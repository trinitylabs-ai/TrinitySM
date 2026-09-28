from __future__ import annotations

import concurrent.futures
import copy
import json
import traceback
from collections import Counter
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import (
    RuntimeConfig,
    write_json,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.pipeline import (
    utc_now,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.synthesis import (
    assemble_proof,
    cited_labels,
)
from cognitive_well_harness_v0_3_72_modular_location_aware_split_verifier_20260824.split_verifier import (
    make_gemma_verifier_runtime,
)
from cognitive_well_harness_v0_3_79_modular_singleton_atomic_retry_20260825.runtime import (
    ResilientModelRuntime,
    recovery_profile,
)
from cognitive_well_harness_v0_3_81_iterative_dual_memory_loop_20260825 import (
    pipeline as v081,
)

from . import HARNESS_VERSION
from .contracts import (
    AUDIT_ANCHOR_SCHEMA,
    CONTEXT_CERTIFIED,
    LITERAL_AUDIT_SCHEMA,
    MAX_CONTEXTUAL_REWRITES,
    MEMORY_DISPOSITION_SCHEMA,
    MEMORY_TIERS,
    PROVISIONAL,
    QWEN_REPAIR_SPEC_SCHEMA,
    STRICT_FUSION_OUTCOME,
    STRICT_REVIEW_OUTCOMES,
)
from .prompts import (
    audit_anchor_extraction_prompt,
    contextual_rewrite_prompt,
    iterative_extraction_prompt,
    literal_anchor_audit_prompt,
    memory_disposition_prompt,
    qwen_repair_spec_prompt,
    synthesis_prompt,
)


ITERATION_COUNT = 2
EXTRACTION_SCHEDULE = v081.EXTRACTION_SCHEDULE
SYNTHESIS_CONFIGS = v081.SYNTHESIS_CONFIGS


def _status(output_dir: Path, stage: str, **values: Any) -> None:
    write_json(
        output_dir / "status.json",
        {"state": "running", "stage": stage, **values, "updated_at": utc_now()},
    )


def with_memory_tier(row: dict[str, Any], tier: str) -> dict[str, Any]:
    if tier not in MEMORY_TIERS:
        raise ValueError(f"unknown memory tier: {tier}")
    return {**copy.deepcopy(row), "memory_tier": tier}


def combined_memory(
    context_certified: list[dict[str, Any]], provisional: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    rows = [with_memory_tier(row, CONTEXT_CERTIFIED) for row in context_certified]
    rows.extend(with_memory_tier(row, PROVISIONAL) for row in provisional)
    seen: set[str] = set()
    for row in rows:
        lemma_id = str(row["lemma_id"])
        if lemma_id in seen:
            raise ValueError(f"lemma exists in both memory tiers: {lemma_id}")
        seen.add(lemma_id)
    return rows


def partition_preliminary_memory(
    *,
    previous_context_certified: list[dict[str, Any]],
    preliminary_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    context_ids = {str(row["lemma_id"]) for row in previous_context_certified}
    context: list[dict[str, Any]] = []
    provisional: list[dict[str, Any]] = []
    for row in preliminary_rows:
        lemma_id = str(row["lemma_id"])
        if lemma_id in context_ids or row.get("memory_tier") == CONTEXT_CERTIFIED:
            context.append(with_memory_tier(row, CONTEXT_CERTIFIED))
        else:
            provisional.append(with_memory_tier(row, PROVISIONAL))
    return context, provisional


def label_memory(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    labeled = v081.label_verified_lemmas(rows)
    return [
        {**label, "memory_tier": rows[index].get("memory_tier", PROVISIONAL)}
        for index, label in enumerate(labeled)
    ]


def _extract_one(
    *,
    runtime: ResilientModelRuntime,
    problem: str,
    candidate_proofs: list[dict[str, Any]],
    context_certified_memory: list[dict[str, Any]],
    provisional_memory: list[dict[str, Any]],
    failed_memory: list[dict[str, Any]],
    iteration: int,
    config: dict[str, Any],
    output_dir: Path,
) -> dict[str, Any]:
    round_number = int(config["round"])
    temperature = float(config["temperature"])
    destination = output_dir / f"round_{round_number}"
    generated = runtime.text(
        role="gemma",
        prompt=iterative_extraction_prompt(
            problem=problem,
            candidate_proofs=candidate_proofs,
            context_certified_memory=context_certified_memory,
            provisional_memory=provisional_memory,
            failed_memory=failed_memory,
        ),
        destination=destination,
        stage="hypothesis_document",
        temperature=temperature,
        max_tokens=32_768,
        seed_label=f"v082:i{iteration}:extraction:r{round_number}",
    )
    document = str(generated["text"]).strip()
    record = v081.deterministic_location_record(document)
    parser_generation: dict[str, Any] | None = None
    attempts: list[dict[str, Any]] = []
    if record is not None:
        v081.validate_schema(record, v081.LOCATION_HYPOTHESIS_SCHEMA)
        parser_generation = {"metadata": {"source": "deterministic_section_parser"}}
        attempts.append({"attempt": 0, "stage": "deterministic", "status": "accepted"})
    for attempt in range(v081.PARSER_MAX_ATTEMPTS) if record is None else ():
        try:
            record, parser_generation = runtime.structured(
                role="gemma",
                prompt=v081.location_hypothesis_parser_prompt(document),
                destination=destination,
                stage=f"location_parser_{attempt}",
                schema=v081.LOCATION_HYPOTHESIS_SCHEMA,
                temperature=v081.PARSER_TEMPERATURE,
                max_tokens=8_192,
                seed_label=f"v082:i{iteration}:r{round_number}:parser:{attempt}",
            )
            attempts.append({"attempt": attempt, "stage": "model", "status": "accepted"})
            break
        except Exception as error:
            attempts.append(
                {
                    "attempt": attempt,
                    "stage": "model",
                    "status": "rejected",
                    "error": f"{type(error).__name__}: {error}",
                }
            )
            record = None
            parser_generation = None
    if record is None or parser_generation is None:
        raise RuntimeError(f"hypothesis parser exhausted: {attempts}")
    result = {
        "iteration": iteration,
        "round": round_number,
        "temperature": temperature,
        "document": document,
        "record": record,
        "parser_attempts": attempts,
        "document_generation": generated["metadata"],
        "parser_generation": parser_generation["metadata"],
    }
    write_json(destination / "result.json", result)
    return result


def run_extraction(
    *,
    runtime: ResilientModelRuntime,
    problem: str,
    candidate_proofs: list[dict[str, Any]],
    context_certified_memory: list[dict[str, Any]],
    provisional_memory: list[dict[str, Any]],
    failed_memory: list[dict[str, Any]],
    iteration: int,
    output_dir: Path,
) -> list[dict[str, Any]]:
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        return list(
            executor.map(
                lambda config: _extract_one(
                    runtime=runtime,
                    problem=problem,
                    candidate_proofs=candidate_proofs,
                    context_certified_memory=context_certified_memory,
                    provisional_memory=provisional_memory,
                    failed_memory=failed_memory,
                    iteration=iteration,
                    config=config,
                    output_dir=output_dir,
                ),
                EXTRACTION_SCHEDULE,
            )
        )


def run_synthesis(
    *,
    runtime: ResilientModelRuntime,
    problem: str,
    candidate_proofs: list[dict[str, Any]],
    context_certified_memory: list[dict[str, Any]],
    provisional_memory: list[dict[str, Any]],
    iteration: int,
    output_dir: Path,
) -> list[dict[str, Any]]:
    memory = combined_memory(context_certified_memory, provisional_memory)
    lemmas = label_memory(memory)

    def generate(config: dict[str, Any]) -> dict[str, Any]:
        candidate_id = str(config["candidate_id"])
        mode = str(config["mode"])
        anchor_index = config["anchor"]
        anchor = (
            str(candidate_proofs[int(anchor_index)]["proof"])
            if anchor_index is not None
            else None
        )
        destination = output_dir / "candidates" / candidate_id
        generated = runtime.text(
            role="gemma",
            prompt=synthesis_prompt(
                mode=mode, problem=problem, lemmas=lemmas, anchor_proof=anchor
            ),
            destination=destination,
            stage="main_proof",
            temperature=0.4,
            max_tokens=32_768,
            seed_label=f"v082:i{iteration}:synthesis:{candidate_id}",
        )
        main_proof = str(generated["text"]).strip()
        assembled = assemble_proof(
            main_proof=main_proof,
            lemmas=lemmas,
            gate_policy={
                "require_all_verified_lemmas": False,
                "minimum_cited_lemmas": 0,
                "minimum_case_headings": 0,
            },
        )
        if not assembled["structural_gate"]["passed"]:
            raise RuntimeError(
                f"synthesis structural gate failed for {candidate_id}: "
                f"{assembled['structural_gate']['violations']}"
            )
        proof = str(assembled["combined_proof"]).strip()
        main_path = destination / "main_proof.md"
        proof_path = destination / "proof_with_appendix.md"
        main_path.parent.mkdir(parents=True, exist_ok=True)
        main_path.write_text(main_proof + "\n", encoding="utf-8")
        proof_path.write_text(proof + "\n", encoding="utf-8")
        tier_by_label = {str(row["label"]): str(row["memory_tier"]) for row in lemmas}
        dependencies = [
            {"label": label, "memory_tier": tier_by_label[label]}
            for label in assembled["used_labels"]
        ]
        result = {
            "iteration": iteration,
            "candidate_id": candidate_id,
            "mode": mode,
            "temperature": 0.4,
            "anchor_candidate_id": (
                candidate_proofs[int(anchor_index)]["candidate_id"]
                if anchor_index is not None
                else None
            ),
            "proof": proof,
            "proof_path": str(proof_path.resolve()),
            "proof_sha256": v081.sha256_text(proof),
            "generation": generated["metadata"],
            "assembly": assembled,
            "memory_dependencies": dependencies,
        }
        write_json(destination / "result.json", result)
        return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        rows = list(executor.map(generate, SYNTHESIS_CONFIGS))
    write_json(
        output_dir / "summary.json",
        {
            "iteration": iteration,
            "candidate_count": len(rows),
            "temperature": 0.4,
            "modes": dict(Counter(str(row["mode"]) for row in rows)),
            "context_certified_memory_count": len(context_certified_memory),
            "provisional_memory_count": len(provisional_memory),
        },
    )
    return rows


def rebind_memory_dependencies(
    *,
    candidates: list[dict[str, Any]],
    context_certified: list[dict[str, Any]],
    provisional: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Recompute proof-to-memory citations after any complete proof replacement."""
    labeled = label_memory(combined_memory(context_certified, provisional))
    tier_by_label = {str(row["label"]): str(row["memory_tier"]) for row in labeled}
    rebound: list[dict[str, Any]] = []
    for source in candidates:
        row = copy.deepcopy(source)
        mentioned = cited_labels(str(row["proof"]))
        used = [label for label in mentioned if label in tier_by_label]
        assembly = copy.deepcopy(row.get("assembly") or {})
        assembly["used_labels"] = used
        assembly["unknown_labels"] = [
            label for label in mentioned if label not in tier_by_label
        ]
        row["assembly"] = assembly
        row["memory_dependencies"] = [
            {"label": label, "memory_tier": tier_by_label[label]} for label in used
        ]
        row["dependency_rebound_after_full_rewrite"] = True
        rebound.append(row)
    return rebound


def strict_whole_proof_pass(candidate: dict[str, Any]) -> bool:
    reviews = dict(candidate.get("review_outcomes") or {})
    return all(reviews.get(name) == outcome for name, outcome in STRICT_REVIEW_OUTCOMES.items()) and str(
        candidate.get("fusion_outcome")
    ) == STRICT_FUSION_OUTCOME


def validate_anchor_records(proof: str, anchors: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for index, anchor in enumerate(anchors, start=1):
        anchor_id = str(anchor.get("anchor_id") or "")
        quote = str(anchor.get("exact_quote") or "")
        if anchor_id in seen:
            errors.append(f"duplicate_anchor_id:{anchor_id}")
        seen.add(anchor_id)
        if quote not in proof:
            errors.append(f"quote_not_literal:{anchor_id or index}")
    return errors


def run_dynamic_literal_audit(
    *,
    runtime: ResilientModelRuntime,
    problem: str,
    proof: str,
    candidate_id: str,
    attempt: int,
    output_dir: Path,
) -> dict[str, Any]:
    destination = output_dir / f"attempt_{attempt}"
    base_prompt = audit_anchor_extraction_prompt(problem=problem, proof=proof)
    anchor_attempts: list[dict[str, Any]] = []
    anchors: list[dict[str, Any]] = []
    extraction_errors: list[str] = []
    anchor_generation: dict[str, Any] | None = None
    for wave in (0, 1):
        retry_directive = ""
        if wave:
            retry_directive = f"""

EXACT-QUOTE CONTRACT RETRY
The preceding record failed deterministic substring binding: {extraction_errors}
Copy every exact_quote as a contiguous byte-for-byte substring of COMPLETE PROOF,
including its original LaTeX delimiters, backslashes, spacing, and punctuation.
Do not replace LaTeX with Unicode, remove dollar signs, normalize whitespace, insert
ellipses, or paraphrase. Shorten a quote if necessary. Return the full JSON record.
"""
        anchor_record, generated = v081._structured_with_v081_transport_waves(
            runtime=runtime,
            role="gemma",
            prompt=base_prompt + retry_directive,
            destination=(
                destination / "01_anchor_extraction"
                if wave == 0
                else destination / "01_anchor_extraction_exact_retry"
            ),
            stage="audit_anchors" if wave == 0 else "audit_anchors_exact_retry",
            schema=AUDIT_ANCHOR_SCHEMA,
            temperature=0.1,
            max_tokens=8_192,
            seed_label=f"v082:literal:{candidate_id}:{attempt}:anchors:{wave}",
        )
        anchors = list(anchor_record["anchors"])
        extraction_errors = validate_anchor_records(proof, anchors)
        anchor_generation = generated
        anchor_attempts.append(
            {
                "wave": wave,
                "anchor_count": len(anchors),
                "deterministic_errors": extraction_errors,
                "generation": generated["metadata"],
            }
        )
        if not extraction_errors:
            break
    if extraction_errors:
        literal = {
            "verdict": "LITERAL_FAILURE",
            "earliest_failed_anchor_id": "ANCHOR_EXTRACTION_INVALID",
            "exact_location": "dynamic audit-anchor extraction",
            "failed_obligation": "Every exact_quote must occur literally in the audited proof.",
            "verification": " | ".join(extraction_errors),
        }
        literal_generation: dict[str, Any] = {
            "metadata": {"source": "deterministic_anchor_validation"}
        }
    else:
        literal, literal_generation = v081._structured_with_v081_transport_waves(
            runtime=runtime,
            role="qwen",
            prompt=literal_anchor_audit_prompt(
                problem=problem, proof=proof, anchors=anchors
            ),
            destination=destination / "02_literal_verification",
            stage="literal_audit",
            schema=LITERAL_AUDIT_SCHEMA,
            temperature=0.1,
            max_tokens=16_384,
            seed_label=f"v082:literal:{candidate_id}:{attempt}:verify",
        )
    result = {
        "proof_sha256": v081.sha256_text(proof),
        "anchors": anchors,
        "anchor_extraction_errors": extraction_errors,
        "anchor_extraction_attempts": anchor_attempts,
        "audit_status": (
            "AUDIT_UNAVAILABLE" if extraction_errors else "COMPLETED"
        ),
        "eligible_for_defect_routing": not extraction_errors,
        "literal_audit": literal,
        "literal_pass": literal["verdict"] == "PASS" and not extraction_errors,
        "anchor_generation": (
            anchor_generation["metadata"] if anchor_generation is not None else None
        ),
        "literal_generation": literal_generation["metadata"],
    }
    write_json(destination / "result.json", result)
    return result


def attach_dynamic_literal_audits(
    *,
    runtime: ResilientModelRuntime,
    problem: str,
    candidates: list[dict[str, Any]],
    output_dir: Path,
) -> list[dict[str, Any]]:
    """Generate proof-specific audit anchors for every current proof body."""

    def audit(source: dict[str, Any]) -> dict[str, Any]:
        row = copy.deepcopy(source)
        literal = run_dynamic_literal_audit(
            runtime=runtime,
            problem=problem,
            proof=str(row["proof"]),
            candidate_id=str(row["candidate_id"]),
            attempt=0,
            output_dir=output_dir / v081._safe_component(str(row["candidate_id"])),
        )
        row["dynamic_literal_audit"] = literal
        return row

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        rows = list(executor.map(audit, candidates))
    write_json(
        output_dir / "summary.json",
        {
            "candidate_count": len(rows),
            "literal_pass_count": sum(
                bool(row["dynamic_literal_audit"]["literal_pass"]) for row in rows
            ),
            "proof_hash_bound_anchors": True,
            "static_problem_specific_checklist": False,
        },
    )
    return rows


def _candidate_reports_defect(candidate: dict[str, Any]) -> bool:
    literal = dict(candidate.get("dynamic_literal_audit") or {})
    reviewer_defect = (
        not strict_whole_proof_pass(candidate)
        if candidate.get("review_outcomes")
        else v081._audit_reports_defect(candidate)
    )
    literal_defect = (
        str(literal.get("audit_status") or "COMPLETED") == "COMPLETED"
        and not bool(literal.get("literal_pass", True))
    )
    return reviewer_defect or literal_defect


def _candidate_defect_events(
    candidate: dict[str, Any],
) -> list[tuple[str, dict[str, Any]]]:
    events = list(v081._defect_events(candidate))
    literal = dict(candidate.get("dynamic_literal_audit") or {})
    if (
        literal
        and str(literal.get("audit_status") or "COMPLETED") == "COMPLETED"
        and not bool(literal.get("literal_pass"))
    ):
        events.append(("dynamic_literal_qwen", dict(literal.get("literal_audit") or {})))
    return events


def run_attribution_and_quarantine(
    *,
    runtime: ResilientModelRuntime,
    problem: str,
    candidates: list[dict[str, Any]],
    memory: list[dict[str, Any]],
    iteration: int,
    output_dir: Path,
) -> tuple[
    list[dict[str, Any]],
    dict[str, list[dict[str, Any]]],
    dict[str, dict[str, Any]],
    dict[str, Any],
]:
    """Associate audit failures with memory entries; never repair lemmas in isolation."""
    output_dir.mkdir(parents=True, exist_ok=True)
    labeled = label_memory(memory)
    by_label = {
        str(label_row["label"]): memory[index]
        for index, label_row in enumerate(labeled)
    }
    candidate_by_id = {str(row["candidate_id"]): row for row in candidates}
    jobs: list[tuple[dict[str, Any], str, dict[str, Any], str, dict[str, Any], int]] = []
    for candidate in candidates:
        if not _candidate_reports_defect(candidate):
            continue
        for label in candidate.get("assembly", {}).get("used_labels", []):
            label_text = str(label)
            lemma = by_label.get(label_text)
            if lemma is None:
                continue
            for source, packet in _candidate_defect_events(candidate):
                for call_index in (1, 2):
                    jobs.append(
                        (candidate, label_text, lemma, source, packet, call_index)
                    )

    def attribute(
        job: tuple[
            dict[str, Any], str, dict[str, Any], str, dict[str, Any], int
        ]
    ) -> dict[str, Any]:
        candidate, label, lemma, source, packet, call_index = job
        candidate_id = str(candidate["candidate_id"])
        destination = (
            output_dir
            / "01_attribution"
            / v081._safe_component(candidate_id)
            / f"lemma_{v081._safe_component(label)}"
            / v081._safe_component(source)
        )
        try:
            record, generation = v081._structured_with_v081_transport_waves(
                runtime=runtime,
                role="qwen",
                prompt=v081.lemma_defect_attribution_prompt(
                    problem=problem,
                    lemma={"label": label, **lemma},
                    refined_proof=str(candidate["proof"]),
                    audit_source=source,
                    defect_packet=packet,
                ),
                destination=destination,
                stage=f"attribution_{call_index}",
                schema=v081.LEMMA_ATTRIBUTION_SCHEMA,
                temperature=0.1,
                max_tokens=16_384,
                seed_label=(
                    f"v082:i{iteration}:attribution:{candidate_id}:"
                    f"{lemma['lemma_id']}:{source}:{call_index}"
                ),
            )
            transport_failure = None
        except RuntimeError as error:
            transport_failure = f"{type(error).__name__}: {error}"
            record = {
                "stored_body_contains_same_obligation": False,
                "stored_body_obligation_status": "NOT_PRESENT_OR_DIFFERENT",
                "classification": "UNRELATED_OR_UNCERTAIN",
                "failed_obligation": "No attribution vote survived transport recovery.",
                "evidence": transport_failure,
            }
            generation = {
                "metadata": {
                    "transport_failure": transport_failure,
                    "conservative_fallback": "UNRELATED_OR_UNCERTAIN",
                }
            }
        result = {
            "candidate_id": candidate_id,
            "label": label,
            "lemma_id": str(lemma["lemma_id"]),
            "audit_source": source,
            "call_index": call_index,
            **record,
            "transport_failure": transport_failure,
            "generation": generation["metadata"],
        }
        write_json(destination / f"attribution_{call_index}_result.json", result)
        return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        attribution_rows = list(executor.map(attribute, jobs))
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for row in attribution_rows:
        grouped.setdefault(
            (str(row["candidate_id"]), str(row["label"]), str(row["audit_source"])),
            [],
        ).append(row)

    replay_jobs: list[
        tuple[dict[str, Any], str, dict[str, Any], str, dict[str, Any], int]
    ] = []
    for (candidate_id, label, source), rows in grouped.items():
        if len(rows) != 2 or not all(
            bool(row.get("stored_body_contains_same_obligation")) for row in rows
        ):
            continue
        packet = next(
            packet
            for event_source, packet in _candidate_defect_events(
                candidate_by_id[candidate_id]
            )
            if event_source == source
        )
        for call_index in (1, 2):
            replay_jobs.append(
                (
                    candidate_by_id[candidate_id],
                    label,
                    by_label[label],
                    source,
                    packet,
                    call_index,
                )
            )

    def replay(
        job: tuple[
            dict[str, Any], str, dict[str, Any], str, dict[str, Any], int
        ]
    ) -> dict[str, Any]:
        candidate, label, lemma, source, packet, call_index = job
        candidate_id = str(candidate["candidate_id"])
        destination = (
            output_dir
            / "02_body_replay"
            / v081._safe_component(candidate_id)
            / f"lemma_{v081._safe_component(label)}"
            / v081._safe_component(source)
        )
        try:
            record, generation = v081._structured_with_v081_transport_waves(
                runtime=runtime,
                role="qwen",
                prompt=v081.lemma_body_replay_prompt(
                    problem=problem,
                    lemma={"label": label, **lemma},
                    audit_source=source,
                    defect_packet=packet,
                ),
                destination=destination,
                stage=f"body_replay_{call_index}",
                schema=v081.LEMMA_BODY_REPLAY_SCHEMA,
                temperature=0.1,
                max_tokens=16_384,
                seed_label=(
                    f"v082:i{iteration}:body_replay:{candidate_id}:"
                    f"{lemma['lemma_id']}:{source}:{call_index}"
                ),
            )
            transport_failure = None
        except RuntimeError as error:
            transport_failure = f"{type(error).__name__}: {error}"
            record = {
                "same_obligation": False,
                "verdict": "UNCERTAIN",
                "first_break": "No stored-body replay survived transport recovery.",
                "verification": transport_failure,
            }
            generation = {
                "metadata": {
                    "transport_failure": transport_failure,
                    "conservative_fallback": "UNCERTAIN",
                }
            }
        result = {
            "candidate_id": candidate_id,
            "label": label,
            "lemma_id": str(lemma["lemma_id"]),
            "audit_source": source,
            "call_index": call_index,
            **record,
            "transport_failure": transport_failure,
            "generation": generation["metadata"],
        }
        write_json(destination / f"body_replay_{call_index}_result.json", result)
        return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        replay_rows = list(executor.map(replay, replay_jobs))
    replay_grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for row in replay_rows:
        replay_grouped.setdefault(
            (str(row["candidate_id"]), str(row["label"]), str(row["audit_source"])),
            [],
        ).append(row)

    decisions: list[dict[str, Any]] = []
    challenges_by_lemma: dict[str, list[dict[str, Any]]] = {}
    for key, attributions in grouped.items():
        candidate_id, label, source = key
        attributions.sort(key=lambda row: int(row["call_index"]))
        replay_audits = replay_grouped.get(key, [])
        replay_audits.sort(key=lambda row: int(row["call_index"]))
        association = v081.attribution_consensus(attributions)
        body = v081.body_replay_consensus(replay_audits)
        statement_defect = bool(
            association["quarantine"]
            and association["scope"] == "LEMMA_STATEMENT_DEFECT"
        )
        quarantine = statement_defect or bool(body["confirmed_body_defect"])
        scope = (
            "LEMMA_STATEMENT_DEFECT"
            if statement_defect
            else "LEMMA_BODY_DEFECT"
            if body["confirmed_body_defect"]
            else "NO_LEMMA_QUARANTINE"
        )
        packet = next(
            packet
            for event_source, packet in _candidate_defect_events(
                candidate_by_id[candidate_id]
            )
            if event_source == source
        )
        decision = {
            "candidate_id": candidate_id,
            "label": label,
            "lemma_id": str(by_label[label]["lemma_id"]),
            "audit_source": source,
            "attributions": attributions,
            "body_replay_audits": replay_audits,
            "consensus": {
                "quarantine": quarantine,
                "scope": scope,
                "attribution": association,
                "body_replay": body,
            },
            "defect_packet": packet,
        }
        decisions.append(decision)
        if quarantine:
            challenges_by_lemma.setdefault(str(by_label[label]["lemma_id"]), []).append(
                decision
            )

    quarantined_ids = set(challenges_by_lemma)
    quarantined_by_label = {
        label: lemma
        for label, lemma in by_label.items()
        if str(lemma["lemma_id"]) in quarantined_ids
    }
    tainted = v081._taint_dependent_candidates(
        candidates=candidates, quarantined_by_label=quarantined_by_label
    )
    summary = {
        "attribution_job_count": len(attribution_rows),
        "body_replay_job_count": len(replay_rows),
        "quarantined_lemma_ids": sorted(quarantined_ids),
        "quarantined_labels": sorted(quarantined_by_label),
        "isolated_lemma_revision_calls": 0,
        "policy": "source-isolated association and replay before contextual repair",
        "lineages": decisions,
    }
    write_json(output_dir / "summary.json", summary)
    return tainted, challenges_by_lemma, quarantined_by_label, summary


def candidate_requires_contextual_repair(candidate: dict[str, Any]) -> bool:
    return bool(candidate.get("memory_invalidation")) or _candidate_reports_defect(
        candidate
    )


def _separate_feedback_packets(candidate: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    literal = dict(candidate.get("dynamic_literal_audit") or {})
    literal_completed = (
        str(literal.get("audit_status") or "COMPLETED") == "COMPLETED"
    )
    qwen_packet = {
        "reviewer_2_qwen": dict(candidate.get("qwen_defect_packet") or {}),
        "dynamic_literal_qwen": (
            dict(literal.get("literal_audit") or {}) if literal_completed else {}
        ),
        "dynamic_literal_audit_status": str(
            literal.get("audit_status") or "NOT_RUN"
        ),
        "memory_invalidation": list(candidate.get("memory_invalidation") or []),
    }
    fusion_packet = {
        "fusion": dict(candidate.get("fusion_defect_packet") or {}),
        "memory_invalidation": list(candidate.get("memory_invalidation") or []),
    }
    return qwen_packet, fusion_packet


def _candidate_implicated_lemmas(
    *,
    candidate: dict[str, Any],
    memory_by_id: dict[str, dict[str, Any]],
    challenges_by_lemma: dict[str, list[dict[str, Any]]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    candidate_id = str(candidate["candidate_id"])
    implicated_ids = {
        str(row["lemma_id"]) for row in candidate.get("memory_invalidation", [])
    }
    replay_records: list[dict[str, Any]] = []
    for lemma_id, challenges in challenges_by_lemma.items():
        related = [
            row for row in challenges if str(row["candidate_id"]) == candidate_id
        ]
        if related:
            implicated_ids.add(lemma_id)
        for row in related:
            replay_records.extend(copy.deepcopy(row.get("body_replay_audits") or []))
    implicated = [
        copy.deepcopy(memory_by_id[lemma_id])
        for lemma_id in sorted(implicated_ids)
        if lemma_id in memory_by_id
    ]
    return implicated, replay_records


def _rewrite_candidate_record(
    *,
    source: dict[str, Any],
    proof: str,
    proof_path: Path,
    generation: dict[str, Any],
    attempt: int,
) -> dict[str, Any]:
    row = copy.deepcopy(source)
    used_labels = cited_labels(proof)
    assembly = copy.deepcopy(row.get("assembly") or {})
    assembly["used_labels"] = used_labels
    row.update(
        {
            "pre_contextual_repair_proof": str(source["proof"]),
            "pre_contextual_repair_proof_sha256": str(source["proof_sha256"]),
            "proof": proof,
            "proof_path": str(proof_path.resolve()),
            "proof_sha256": v081.sha256_text(proof),
            "assembly": assembly,
            "contextual_repair_attempt": attempt,
            "contextual_repair_generation": generation,
        }
    )
    return row


def run_contextual_repair_candidate(
    *,
    runtime: ResilientModelRuntime,
    problem_id: str,
    problem: str,
    candidate: dict[str, Any],
    implicated_lemmas: list[dict[str, Any]],
    body_replay_records: list[dict[str, Any]],
    iteration: int,
    output_dir: Path,
) -> dict[str, Any]:
    """Repair and re-audit a complete proof, with one bounded second rewrite."""
    candidate_id = str(candidate["candidate_id"])
    destination = output_dir / v081._safe_component(candidate_id)
    qwen_packet, fusion_packet = _separate_feedback_packets(candidate)
    repair_spec, specification_generation = v081._structured_with_v081_transport_waves(
        runtime=runtime,
        role="qwen",
        prompt=qwen_repair_spec_prompt(
            problem=problem,
            proof=str(candidate["proof"]),
            implicated_lemmas=implicated_lemmas,
            qwen_packet=qwen_packet,
            fusion_packet=fusion_packet,
            body_replay_records=body_replay_records,
        ),
        destination=destination / "01_qwen_repair_specification",
        stage="repair_specification",
        schema=QWEN_REPAIR_SPEC_SCHEMA,
        temperature=0.1,
        max_tokens=16_384,
        seed_label=f"v082:i{iteration}:context_spec:{candidate_id}",
    )
    if repair_spec["lemma_interface_action"] == "NO_SUPPORTED_REPAIR":
        result = {
            **candidate,
            "contextual_repair_status": "NO_SUPPORTED_REPAIR",
            "contextual_repair_specification": repair_spec,
            "contextual_repair_specification_generation": specification_generation[
                "metadata"
            ],
            "contextual_repair_attempts": [],
        }
        write_json(destination / "result.json", result)
        return result

    attempts: list[dict[str, Any]] = []
    prior_feedback: dict[str, Any] | None = None
    accepted: dict[str, Any] | None = None
    audit_unavailable = False
    for attempt in range(1, MAX_CONTEXTUAL_REWRITES + 1):
        attempt_dir = destination / f"02_rewrite_attempt_{attempt}"
        generated = runtime.text(
            role="gemma",
            prompt=contextual_rewrite_prompt(
                problem=problem,
                proof=str(candidate["proof"]),
                implicated_lemmas=implicated_lemmas,
                repair_spec=repair_spec,
                qwen_packet=qwen_packet,
                fusion_packet=fusion_packet,
                prior_attempt_feedback=prior_feedback,
            ),
            destination=attempt_dir / "generation",
            stage="complete_replacement_proof",
            temperature=0.4,
            max_tokens=32_768,
            seed_label=f"v082:i{iteration}:context_rewrite:{candidate_id}:{attempt}",
        )
        proof = str(generated["text"]).strip()
        proof_path = attempt_dir / "complete_replacement_proof.md"
        proof_path.parent.mkdir(parents=True, exist_ok=True)
        proof_path.write_text(proof + "\n", encoding="utf-8")
        replacement = _rewrite_candidate_record(
            source=candidate,
            proof=proof,
            proof_path=proof_path,
            generation=generated["metadata"],
            attempt=attempt,
        )
        audited = v081.run_review_fusion(
            run_input={"problem_id": problem_id, "problem": problem},
            candidates=[replacement],
            gemma_endpoint=runtime.config.gemma_endpoint,
            qwen_endpoint=runtime.config.qwen_endpoint,
            output_dir=attempt_dir / "03_full_proof_review_fusion",
        )[0]
        literal = run_dynamic_literal_audit(
            runtime=runtime,
            problem=problem,
            proof=proof,
            candidate_id=candidate_id,
            attempt=attempt,
            output_dir=attempt_dir / "04_dynamic_literal_gate",
        )
        audited["dynamic_literal_audit"] = literal
        reviewer_pass = strict_whole_proof_pass(audited)
        full_pass = reviewer_pass and bool(literal["literal_pass"])
        attempt_record = {
            "attempt": attempt,
            "proof_path": str(proof_path.resolve()),
            "proof_sha256": audited["proof_sha256"],
            "review_outcomes": audited["review_outcomes"],
            "qwen_outcome": audited["qwen_outcome"],
            "fusion_outcome": audited["fusion_outcome"],
            "reviewer_fusion_pass": reviewer_pass,
            "literal_pass": literal["literal_pass"],
            "literal_audit_status": literal.get("audit_status", "COMPLETED"),
            "accepted": full_pass,
        }
        attempts.append(attempt_record)
        if full_pass:
            accepted = audited
            break
        if (
            reviewer_pass
            and str(literal.get("audit_status") or "COMPLETED")
            == "AUDIT_UNAVAILABLE"
        ):
            audit_unavailable = True
            break
        prior_feedback = {
            "reviewer_2_qwen": audited["qwen_defect_packet"],
            "fusion": audited["fusion_defect_packet"],
            "dynamic_literal": (
                literal["literal_audit"]
                if str(literal.get("audit_status") or "COMPLETED") == "COMPLETED"
                else {}
            ),
        }

    result = {
        **(accepted if accepted is not None else candidate),
        "contextual_repair_status": (
            "ACCEPTED"
            if accepted is not None
            else "AUDIT_UNAVAILABLE"
            if audit_unavailable
            else "FAILED"
        ),
        "contextual_repair_specification": repair_spec,
        "contextual_repair_specification_generation": specification_generation[
            "metadata"
        ],
        "contextual_repair_attempts": attempts,
        "contextual_repair_implicated_lemma_ids": [
            str(row["lemma_id"]) for row in implicated_lemmas
        ],
    }
    if accepted is not None and result.get("memory_invalidation"):
        result["resolved_memory_invalidation"] = result.pop("memory_invalidation")
    write_json(destination / "result.json", result)
    return result


def validate_memory_disposition(
    *,
    disposition: dict[str, Any],
    proof: str,
    quarantined_ids: set[str],
) -> list[str]:
    errors: list[str] = []
    decision = str(disposition.get("decision"))
    supersedes = {str(value) for value in disposition.get("supersedes_lemma_ids", [])}
    statement = str(disposition.get("statement_exact_quote") or "")
    lemma_proof = str(disposition.get("proof_exact_quote") or "")
    if decision == "NO_REUSABLE_LEMMA":
        if statement or lemma_proof:
            errors.append("no_reusable_lemma_must_have_empty_quotes")
        if supersedes:
            errors.append("no_reusable_lemma_must_not_supersede")
        return errors
    if decision != "EXACT_SELF_CONTAINED_REVISION":
        return ["unknown_decision"]
    if not supersedes:
        errors.append("missing_superseded_lemma")
    if not supersedes.issubset(quarantined_ids):
        errors.append("supersedes_nonquarantined_lemma")
    if not statement or statement not in proof:
        errors.append("statement_is_not_an_exact_proof_quote")
    if not lemma_proof or lemma_proof not in proof:
        errors.append("lemma_proof_is_not_an_exact_proof_quote")
    return errors


def commit_contextual_memory_transaction(
    *,
    context_certified: list[dict[str, Any]],
    provisional: list[dict[str, Any]],
    failed_memory: list[dict[str, Any]],
    quarantined_ids: set[str],
    challenges_by_lemma: dict[str, list[dict[str, Any]]],
    accepted_revisions: list[dict[str, Any]],
    iteration: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """Pure atomic memory commit: revoke first, then insert only accepted exact excerpts."""
    old_memory = combined_memory(context_certified, provisional)
    old_by_id = {str(row["lemma_id"]): row for row in old_memory}
    new_context = [
        with_memory_tier(row, CONTEXT_CERTIFIED)
        for row in context_certified
        if str(row["lemma_id"]) not in quarantined_ids
    ]
    new_provisional = [
        with_memory_tier(row, PROVISIONAL)
        for row in provisional
        if str(row["lemma_id"]) not in quarantined_ids
    ]
    exact_keys = {
        (v081.normalized(str(row["statement"])), v081.normalized(str(row["proof"])))
        for row in new_context
    }
    inserted: list[str] = []
    superseded: set[str] = set()
    for revision in accepted_revisions:
        requested = {str(value) for value in revision["supersedes_lemma_ids"]}
        if requested.intersection(superseded):
            continue
        key = (
            v081.normalized(str(revision["statement"])),
            v081.normalized(str(revision["proof"])),
        )
        if key in exact_keys:
            superseded.update(requested)
            continue
        row = with_memory_tier(revision, CONTEXT_CERTIFIED)
        new_context.append(row)
        exact_keys.add(key)
        inserted.append(str(row["lemma_id"]))
        superseded.update(requested)

    failure_additions: list[dict[str, Any]] = []
    for lemma_id in sorted(quarantined_ids):
        old = old_by_id.get(lemma_id)
        challenges = challenges_by_lemma.get(lemma_id, [])
        if old is None or not challenges:
            continue
        failure_additions.append(
            v081._memory_failure_record(
                old_lemma=old,
                challenges=challenges,
                iteration=iteration,
                status="PROOF_INVALIDATED",
                resolved_by_certification=lemma_id in superseded,
            )
        )
    new_failed, failure_audit = v081._insert_failed_exact(
        failed_memory, failure_additions
    )
    summary = {
        "quarantined_lemma_ids": sorted(quarantined_ids),
        "inserted_context_certified_lemma_ids": inserted,
        "superseded_lemma_ids": sorted(superseded),
        "context_certified_count": len(new_context),
        "provisional_count": len(new_provisional),
        "failed_count": len(new_failed),
        "failed_insertion_audit": failure_audit,
    }
    return new_context, new_provisional, new_failed, summary


def run_contextual_memory_feedback(
    *,
    runtime: ResilientModelRuntime,
    problem_id: str,
    problem: str,
    candidates: list[dict[str, Any]],
    context_certified: list[dict[str, Any]],
    provisional: list[dict[str, Any]],
    failed_memory: list[dict[str, Any]],
    iteration: int,
    output_dir: Path,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, Any],
]:
    """Attribute, quarantine, contextually repair, and atomically update memory."""
    memory = combined_memory(context_certified, provisional)
    tainted, challenges, quarantined_by_label, attribution = (
        run_attribution_and_quarantine(
            runtime=runtime,
            problem=problem,
            candidates=candidates,
            memory=memory,
            iteration=iteration,
            output_dir=output_dir / "01_attribution_and_quarantine",
        )
    )
    memory_by_id = {str(row["lemma_id"]): row for row in memory}

    def repair(source: dict[str, Any]) -> dict[str, Any]:
        if not candidate_requires_contextual_repair(source):
            return {**copy.deepcopy(source), "contextual_repair_status": "NOT_REQUIRED"}
        implicated, replay = _candidate_implicated_lemmas(
            candidate=source,
            memory_by_id=memory_by_id,
            challenges_by_lemma=challenges,
        )
        return run_contextual_repair_candidate(
            runtime=runtime,
            problem_id=problem_id,
            problem=problem,
            candidate=source,
            implicated_lemmas=implicated,
            body_replay_records=replay,
            iteration=iteration,
            output_dir=output_dir / "02_contextual_full_proof_repair",
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        repaired_candidates = list(executor.map(repair, tainted))

    quarantined_ids = {str(row["lemma_id"]) for row in quarantined_by_label.values()}
    accepted_revisions: list[dict[str, Any]] = []
    disposition_audit: list[dict[str, Any]] = []
    claimed_supersessions: set[str] = set()
    for candidate in repaired_candidates:
        if candidate.get("contextual_repair_status") != "ACCEPTED":
            continue
        implicated_ids = {
            str(value)
            for value in candidate.get("contextual_repair_implicated_lemma_ids", [])
        }.intersection(quarantined_ids)
        if not implicated_ids:
            continue
        candidate_id = str(candidate["candidate_id"])
        destination = (
            output_dir
            / "03_atomic_memory_disposition"
            / v081._safe_component(candidate_id)
        )
        disposition, generation = v081._structured_with_v081_transport_waves(
            runtime=runtime,
            role="qwen",
            prompt=memory_disposition_prompt(
                proof=str(candidate["proof"]),
                quarantined_lemmas=[
                    {
                        "lemma_id": lemma_id,
                        "statement": memory_by_id[lemma_id]["statement"],
                        "earliest_unresolved_transition": memory_by_id[lemma_id][
                            "earliest_unresolved_transition"
                        ],
                        "local_dependency_map": memory_by_id[lemma_id][
                            "local_dependency_map"
                        ],
                    }
                    for lemma_id in sorted(implicated_ids)
                ],
            ),
            destination=destination,
            stage="exact_memory_disposition",
            schema=MEMORY_DISPOSITION_SCHEMA,
            temperature=0.1,
            max_tokens=8_192,
            seed_label=f"v082:i{iteration}:memory_disposition:{candidate_id}",
        )
        errors = validate_memory_disposition(
            disposition=disposition,
            proof=str(candidate["proof"]),
            quarantined_ids=implicated_ids,
        )
        requested = {
            str(value) for value in disposition.get("supersedes_lemma_ids", [])
        }
        if requested.intersection(claimed_supersessions):
            errors.append("supersession_already_claimed_by_prior_accepted_revision")
        accepted = (
            disposition["decision"] == "EXACT_SELF_CONTAINED_REVISION"
            and not errors
        )
        audit_row = {
            "candidate_id": candidate_id,
            "proof_sha256": candidate["proof_sha256"],
            "disposition": disposition,
            "deterministic_errors": errors,
            "accepted_into_context_memory": accepted,
            "generation": generation["metadata"],
        }
        disposition_audit.append(audit_row)
        write_json(destination / "result.json", audit_row)
        if not accepted:
            continue
        statement = str(disposition["statement_exact_quote"])
        lemma_proof = str(disposition["proof_exact_quote"])
        digest = v081.sha256_text(statement + "\n\n" + lemma_proof)[:16]
        accepted_revisions.append(
            {
                "lemma_id": f"CTX_I{iteration}_{digest}",
                "statement": statement,
                "proof": lemma_proof,
                "earliest_unresolved_transition": str(
                    disposition["earliest_unresolved_transition"]
                ),
                "local_dependency_map": str(disposition["local_dependency_map"]),
                "direction": "positive",
                "context_certified": True,
                "source_candidate_id": candidate_id,
                "source_full_proof_sha256": str(candidate["proof_sha256"]),
                "supersedes_lemma_ids": sorted(requested),
                "memory_revision_iteration": iteration,
                "self_containment_reason": str(disposition["self_containment_reason"]),
            }
        )
        claimed_supersessions.update(requested)

    new_context, new_provisional, new_failed, transaction = (
        commit_contextual_memory_transaction(
            context_certified=context_certified,
            provisional=provisional,
            failed_memory=failed_memory,
            quarantined_ids=quarantined_ids,
            challenges_by_lemma=challenges,
            accepted_revisions=accepted_revisions,
            iteration=iteration,
        )
    )
    summary = {
        "attribution": attribution,
        "contextual_repair_outcomes": dict(
            Counter(
                str(row.get("contextual_repair_status"))
                for row in repaired_candidates
            )
        ),
        "contextual_rewrite_limit": MAX_CONTEXTUAL_REWRITES,
        "memory_dispositions": disposition_audit,
        "transaction": transaction,
        "accepted_proof_without_reusable_lemma_is_allowed": True,
    }
    write_json(output_dir / "summary.json", summary)
    write_json(
        output_dir / "04_memory_snapshot.json",
        {
            "context_certified": new_context,
            "provisional": new_provisional,
            "failed": new_failed,
        },
    )
    return new_context, new_provisional, new_failed, repaired_candidates, summary


def run_contextual_repairs_without_commit(
    *,
    runtime: ResilientModelRuntime,
    problem_id: str,
    problem: str,
    candidates: list[dict[str, Any]],
    context_certified: list[dict[str, Any]],
    provisional: list[dict[str, Any]],
    failed_memory: list[dict[str, Any]],
    iteration: int,
    output_dir: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run step 9 through contextual repair, stopping before memory disposition."""
    memory = combined_memory(context_certified, provisional)
    tainted, challenges, quarantined_by_label, attribution = (
        run_attribution_and_quarantine(
            runtime=runtime,
            problem=problem,
            candidates=candidates,
            memory=memory,
            iteration=iteration,
            output_dir=output_dir / "01_attribution_and_quarantine",
        )
    )
    memory_by_id = {str(row["lemma_id"]): row for row in memory}

    def repair(source: dict[str, Any]) -> dict[str, Any]:
        if not candidate_requires_contextual_repair(source):
            return {**copy.deepcopy(source), "contextual_repair_status": "NOT_REQUIRED"}
        implicated, replay = _candidate_implicated_lemmas(
            candidate=source,
            memory_by_id=memory_by_id,
            challenges_by_lemma=challenges,
        )
        return run_contextual_repair_candidate(
            runtime=runtime,
            problem_id=problem_id,
            problem=problem,
            candidate=source,
            implicated_lemmas=implicated,
            body_replay_records=replay,
            iteration=iteration,
            output_dir=output_dir / "02_contextual_full_proof_repair",
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        repaired = list(executor.map(repair, tainted))
    summary = {
        "stopping_boundary": "after_step_9_before_atomic_memory_transaction",
        "attribution": attribution,
        "contextual_repair_outcomes": dict(
            Counter(str(row.get("contextual_repair_status")) for row in repaired)
        ),
        "contextual_rewrite_limit": MAX_CONTEXTUAL_REWRITES,
        "initial_context_certified_count": len(context_certified),
        "initial_provisional_count": len(provisional),
        "initial_failed_count": len(failed_memory),
        "memory_disposition_calls": 0,
        "memory_commit_performed": False,
        "selection_performed": False,
    }
    write_json(output_dir / "summary.json", summary)
    write_json(
        output_dir / "unchanged_memory_snapshot.json",
        {
            "context_certified": context_certified,
            "provisional": provisional,
            "failed": failed_memory,
        },
    )
    return repaired, summary


novelty_gate = v081.novelty_gate


def load_initial_state(source: Path) -> dict[str, Any]:
    """Load a problem-agnostic two-proof seed packet.

    ``source`` may be the JSON file itself or a directory containing
    ``initial_state.json``. Proof bodies may be inline or referenced by a path
    relative to that JSON file.
    """
    input_path = source if source.is_file() else source / "initial_state.json"
    if not input_path.is_file():
        raise FileNotFoundError(
            f"expected a generic two-proof input packet at {input_path}"
        )
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("initial state must be a JSON object")
    problem = str(payload.get("problem") or "").strip()
    if not problem:
        raise ValueError("initial state requires a nonempty problem")
    raw_proofs = payload.get("candidate_proofs")
    if not isinstance(raw_proofs, list) or len(raw_proofs) != 2:
        raise ValueError("initial state requires exactly two candidate_proofs")
    candidates: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_proofs):
        if not isinstance(raw, dict):
            raise ValueError(f"candidate_proofs[{index}] must be an object")
        proof_path_value = raw.get("proof_path")
        if raw.get("proof"):
            proof = str(raw["proof"]).strip()
            proof_path = (
                (input_path.parent / str(proof_path_value)).resolve()
                if proof_path_value
                else None
            )
        elif proof_path_value:
            proof_path = (input_path.parent / str(proof_path_value)).resolve()
            proof = proof_path.read_text(encoding="utf-8").strip()
        else:
            raise ValueError(
                f"candidate_proofs[{index}] requires proof or proof_path"
            )
        if not proof:
            raise ValueError(f"candidate_proofs[{index}] has an empty proof")
        digest = v081.sha256_text(proof)
        supplied_digest = str(raw.get("proof_sha256") or "")
        if supplied_digest and supplied_digest != digest:
            raise ValueError(f"proof hash mismatch for candidate_proofs[{index}]")
        for packet_name in ("qwen_defect_packet", "fusion_defect_packet"):
            if not isinstance(raw.get(packet_name), dict):
                raise ValueError(
                    f"candidate_proofs[{index}] requires object field {packet_name}"
                )
        candidates.append(
            {
                **copy.deepcopy(raw),
                "candidate_id": str(raw.get("candidate_id") or f"seed_{index + 1}"),
                "role": str(raw.get("role") or ("anchor" if index == 0 else "supplement")),
                "proof": proof,
                "proof_path": (
                    str(proof_path) if proof_path is not None else f"inline:{input_path}#{index}"
                ),
                "proof_sha256": digest,
                "qwen_defect_packet": dict(raw["qwen_defect_packet"]),
                "fusion_defect_packet": dict(raw["fusion_defect_packet"]),
            }
        )
    problem_id = str(payload.get("problem_id") or "").strip()
    if not problem_id:
        problem_id = f"generic_{v081.sha256_text(problem)[:12]}"
    return {
        "problem_id": problem_id,
        "problem": problem,
        "candidate_proofs": candidates,
    }


def build_manifest(
    *,
    initial_state: dict[str, Any],
    source_run_dir: Path,
    runtime_config: RuntimeConfig,
    salvage_verifier_endpoint: str,
) -> dict[str, Any]:
    return {
        "schema": "cognitive-well-v082-contextual-surgical-memory-manifest-v1",
        "harness_version": HARNESS_VERSION,
        "created_at": utc_now(),
        "problem_id": initial_state["problem_id"],
        "problem_sha256": v081.sha256_text(str(initial_state["problem"])),
        "source_run_dir": str(source_run_dir.resolve()),
        "iteration_count": ITERATION_COUNT,
        "flow": [
            "three_unconditional_location_aware_hypothesis_extractions",
            "exact_novelty_plus_unanimous_failed_semantic_comparison",
            "paired_proving_split_verification_salvage_and_atomic_child_retry",
            "insert_new_results_into_provisional_memory_only",
            "six_t0.4_tier_labeled_synthesis_modes",
            "three_reviews_fusion_and_full_replacement_refinement",
            "fresh_three_reviews_and_fusion",
            "dynamic_proof_specific_literal_anchor_audit",
            "source_isolated_defect_attribution_and_stored_body_replay",
            "contextual_whole_proof_repair_with_at_most_two_rewrites",
            "fresh_full_review_fusion_and_dynamic_literal_gate",
            "atomic_proof_and_context_memory_commit_or_rollback",
            "six_to_two_selection",
        ],
        "memory": {
            "context_certified": (
                "reusable only after a whole repaired proof passes every final gate "
                "and an exact self-contained lemma statement/body are copied verbatim"
            ),
            "provisional": (
                "paired-proof and split-verifier pass; supplied as untrusted evidence"
            ),
            "failed": "never visible to synthesis",
            "dedup": "exact_only_for_active_memory",
            "semantic_dedup": "failed-memory comparison only; two unanimous Qwen calls",
        },
        "hypothesis_extraction": {
            "model": runtime_config.gemma_model,
            "schedule": list(EXTRACTION_SCHEDULE),
            "max_tokens": 32_768,
            "routing_fields": [
                "earliest_unresolved_transition",
                "local_dependency_map",
            ],
        },
        "synthesis": {
            "model": runtime_config.gemma_model,
            "temperature": 0.4,
            "max_tokens": 32_768,
            "candidate_configs": list(SYNTHESIS_CONFIGS),
        },
        "full_proof_audit": {
            "reviewer_1": "Gemma_t0.4_earliest_break",
            "reviewer_2": "Qwen_t0.2_adversarial",
            "reviewer_3": "Gemma_t0.2_charitable",
            "fusion": "Gemma_t0.4_downstream_adjudication",
            "qwen_and_fusion_packets": "separate_provenance_not_independent_votes",
        },
        "dynamic_literal_audit": {
            "anchor_extractor": "Gemma_t0.1_nonjudging_max_24",
            "literal_verifier": "Qwen_t0.1",
            "anchor_binding": "exact_quote_plus_proof_sha256",
            "anchors_regenerated_after_every_rewrite": True,
            "static_problem_specific_checklist": False,
        },
        "contextual_repair": {
            "repair_spec": "Qwen_t0.1",
            "complete_rewrite": "Gemma_t0.4_max_32768",
            "maximum_rewrites": MAX_CONTEXTUAL_REWRITES,
            "isolated_lemma_repair": False,
            "atomic_memory_update": True,
        },
        "preliminary_split_verifier": {
            "model": runtime_config.gemma_model,
            "endpoint": salvage_verifier_endpoint.rstrip("/"),
            "durable_memory_authority": False,
        },
        "runtime": {
            "gemma_endpoint": runtime_config.gemma_endpoint,
            "qwen_endpoint": runtime_config.qwen_endpoint,
            "gemma_model": runtime_config.gemma_model,
            "qwen_model": runtime_config.qwen_model,
            "master_seed": runtime_config.master_seed,
            "gemma_dtype": "bfloat16",
            "gemma_mtp_speculative_tokens": 4,
            "recovery_profile": recovery_profile(),
        },
        "problem_specific_prompt_logic": False,
        "reference_solution_access": False,
        "gold_score_access": False,
        "final_split_verifier_gate": "not_requested",
    }


def run_pipeline(
    *,
    initial_state: dict[str, Any],
    source_run_dir: Path,
    output_dir: Path,
    runtime_config: RuntimeConfig,
    salvage_verifier_endpoint: str,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        output_dir / "manifest.json",
        build_manifest(
            initial_state=initial_state,
            source_run_dir=source_run_dir,
            runtime_config=runtime_config,
            salvage_verifier_endpoint=salvage_verifier_endpoint,
        ),
    )
    write_json(output_dir / "initial_state.json", initial_state)
    runtime = ResilientModelRuntime(runtime_config)
    verifier_runtime = make_gemma_verifier_runtime(
        RuntimeConfig(
            gemma_endpoint=salvage_verifier_endpoint.rstrip("/"),
            qwen_endpoint=salvage_verifier_endpoint.rstrip("/"),
            gemma_model=runtime_config.gemma_model,
            qwen_model=runtime_config.gemma_model,
            master_seed=runtime_config.master_seed,
        )
    )
    problem_id = str(initial_state["problem_id"])
    problem = str(initial_state["problem"])
    run_input = {"problem_id": problem_id, "problem": problem}
    current_proofs = list(initial_state["candidate_proofs"])
    context_certified: list[dict[str, Any]] = []
    provisional: list[dict[str, Any]] = []
    failed_memory: list[dict[str, Any]] = []
    iteration_summaries: list[dict[str, Any]] = []
    try:
        for iteration in range(1, ITERATION_COUNT + 1):
            iteration_dir = output_dir / f"iteration_{iteration}"
            _status(output_dir, "hypothesis_extraction", iteration=iteration)
            extracted = run_extraction(
                runtime=runtime,
                problem=problem,
                candidate_proofs=current_proofs,
                context_certified_memory=context_certified,
                provisional_memory=provisional,
                failed_memory=failed_memory,
                iteration=iteration,
                output_dir=iteration_dir / "01_hypothesis_extraction",
            )

            _status(output_dir, "novelty_gate", iteration=iteration)
            accepted, novelty_audit = v081.novelty_gate(
                runtime=runtime,
                extraction_results=extracted,
                certified_memory=combined_memory(context_certified, provisional),
                failed_memory=failed_memory,
                iteration=iteration,
                output_dir=iteration_dir / "02_novelty_gate",
            )

            _status(output_dir, "preliminary_certification", iteration=iteration)
            preliminary, failed_memory, certification = (
                v081.run_certification_and_memory(
                    proof_runtime=runtime,
                    verifier_runtime=verifier_runtime,
                    runtime_config=runtime_config,
                    salvage_verifier_endpoint=salvage_verifier_endpoint,
                    problem=problem,
                    candidate_proofs=current_proofs,
                    accepted_hypotheses=accepted,
                    certified_memory=combined_memory(context_certified, provisional),
                    failed_memory=failed_memory,
                    iteration=iteration,
                    output_dir=iteration_dir / "03_preliminary_certification",
                )
            )
            context_certified, provisional = partition_preliminary_memory(
                previous_context_certified=context_certified,
                preliminary_rows=preliminary,
            )

            _status(output_dir, "six_candidate_synthesis", iteration=iteration)
            synthesized = run_synthesis(
                runtime=runtime,
                problem=problem,
                candidate_proofs=current_proofs,
                context_certified_memory=context_certified,
                provisional_memory=provisional,
                iteration=iteration,
                output_dir=iteration_dir / "04_synthesis",
            )
            _status(output_dir, "pre_refinement_full_audit", iteration=iteration)
            pre_audited = v081.run_review_fusion(
                run_input=run_input,
                candidates=synthesized,
                gemma_endpoint=runtime_config.gemma_endpoint,
                qwen_endpoint=runtime_config.qwen_endpoint,
                output_dir=iteration_dir / "05_pre_refinement_audit",
            )
            _status(output_dir, "high_stakes_refinement", iteration=iteration)
            refined = v081.run_refinement(
                runtime=runtime,
                problem=problem,
                audited_candidates=pre_audited,
                iteration=iteration,
                output_dir=iteration_dir / "06_refinement",
            )
            refined = rebind_memory_dependencies(
                candidates=refined,
                context_certified=context_certified,
                provisional=provisional,
            )
            _status(output_dir, "post_refinement_full_audit", iteration=iteration)
            post_audited = v081.run_review_fusion(
                run_input=run_input,
                candidates=refined,
                gemma_endpoint=runtime_config.gemma_endpoint,
                qwen_endpoint=runtime_config.qwen_endpoint,
                output_dir=iteration_dir / "07_post_refinement_audit",
            )
            _status(output_dir, "dynamic_literal_audit", iteration=iteration)
            literal_audited = attach_dynamic_literal_audits(
                runtime=runtime,
                problem=problem,
                candidates=post_audited,
                output_dir=iteration_dir / "08_dynamic_literal_audit",
            )
            _status(output_dir, "contextual_memory_feedback", iteration=iteration)
            (
                context_certified,
                provisional,
                failed_memory,
                final_candidates,
                contextual_feedback,
            ) = run_contextual_memory_feedback(
                runtime=runtime,
                problem_id=problem_id,
                problem=problem,
                candidates=literal_audited,
                context_certified=context_certified,
                provisional=provisional,
                failed_memory=failed_memory,
                iteration=iteration,
                output_dir=iteration_dir / "09_contextual_memory_feedback",
            )
            _status(output_dir, "six_to_two_selection", iteration=iteration)
            current_proofs, selection = v081.run_selection(
                runtime=runtime,
                problem=problem,
                post_audited_candidates=final_candidates,
                output_dir=iteration_dir / "10_selection",
            )
            iteration_summary = {
                "iteration": iteration,
                "extracted_hypothesis_count": sum(
                    len(row["record"]["hypotheses"]) for row in extracted
                ),
                "novelty_accepted_count": len(accepted),
                "novelty_rejected_count": len(novelty_audit) - len(accepted),
                "certification": certification,
                "context_certified_memory_count": len(context_certified),
                "provisional_memory_count": len(provisional),
                "failed_memory_count": len(failed_memory),
                "pre_fusion_outcomes": dict(
                    Counter(str(row["fusion_outcome"]) for row in pre_audited)
                ),
                "post_fusion_outcomes": dict(
                    Counter(str(row["fusion_outcome"]) for row in post_audited)
                ),
                "dynamic_literal_outcomes": dict(
                    Counter(
                        str(row["dynamic_literal_audit"]["literal_audit"]["verdict"])
                        for row in literal_audited
                    )
                ),
                "contextual_feedback": contextual_feedback,
                "selection": selection,
            }
            write_json(iteration_dir / "summary.json", iteration_summary)
            write_json(
                iteration_dir / "memory_snapshot.json",
                {
                    "context_certified": context_certified,
                    "provisional": provisional,
                    "failed": failed_memory,
                },
            )
            iteration_summaries.append(iteration_summary)

        summary = {
            "schema": "cognitive-well-v082-contextual-surgical-memory-summary-v1",
            "harness_version": HARNESS_VERSION,
            "state": "completed",
            "completed_at": utc_now(),
            "iteration_count": ITERATION_COUNT,
            "context_certified_memory_count": len(context_certified),
            "provisional_memory_count": len(provisional),
            "failed_memory_count": len(failed_memory),
            "final_selected_proofs": [
                {
                    "candidate_id": row["candidate_id"],
                    "role": row["role"],
                    "proof_path": row["proof_path"],
                    "proof_sha256": row["proof_sha256"],
                    "qwen_outcome": row["qwen_outcome"],
                    "fusion_outcome": row["fusion_outcome"],
                    "contextual_repair_status": row.get("contextual_repair_status"),
                }
                for row in current_proofs
            ],
            "iterations": iteration_summaries,
            "proof_runtime_recovery_events": runtime.recovery_events(),
            "verifier_runtime_recovery_events": verifier_runtime.recovery_events(),
        }
        write_json(
            output_dir / "final_context_certified_memory.json",
            {"context_certified": context_certified},
        )
        write_json(
            output_dir / "final_provisional_memory.json",
            {"provisional": provisional},
        )
        write_json(
            output_dir / "final_failed_memory.json", {"failed": failed_memory}
        )
        write_json(output_dir / "summary.json", summary)
        write_json(
            output_dir / "status.json",
            {
                "state": "completed",
                "stage": "two_iteration_contextual_loop_complete",
                "context_certified_memory_count": len(context_certified),
                "provisional_memory_count": len(provisional),
                "failed_memory_count": len(failed_memory),
                "updated_at": utc_now(),
            },
        )
        return summary
    except Exception as error:
        write_json(
            output_dir / "status.json",
            {
                "state": "failed",
                "stage": "exception",
                "error": f"{type(error).__name__}: {error}",
                "traceback": traceback.format_exc(),
                "updated_at": utc_now(),
            },
        )
        raise
