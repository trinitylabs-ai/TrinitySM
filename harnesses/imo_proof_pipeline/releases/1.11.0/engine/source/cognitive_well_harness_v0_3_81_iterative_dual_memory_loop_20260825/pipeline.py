from __future__ import annotations

import concurrent.futures
import copy
import json
import re
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
)
from cognitive_well_harness_v0_3_66_modular_six_to_two_proof_selection_20260824 import (
    pipeline as v066,
)
from cognitive_well_harness_v0_3_67_modular_six_track_generation_review_resolution_20260824 import (
    pipeline as v067,
)
from cognitive_well_harness_v0_3_72_modular_location_aware_split_verifier_20260824.contracts import (
    LOCATION_HYPOTHESIS_SCHEMA,
    validate_schema,
)
from cognitive_well_harness_v0_3_72_modular_location_aware_split_verifier_20260824.extraction import (
    PARSER_MAX_ATTEMPTS,
    PARSER_TEMPERATURE,
    deterministic_location_record,
)
from cognitive_well_harness_v0_3_72_modular_location_aware_split_verifier_20260824.lemma_proving import (
    prove_pairs,
    validate_and_repair_negations,
)
from cognitive_well_harness_v0_3_72_modular_location_aware_split_verifier_20260824.memory import (
    normalized,
)
from cognitive_well_harness_v0_3_72_modular_location_aware_split_verifier_20260824.prompts import (
    location_hypothesis_parser_prompt,
)
from cognitive_well_harness_v0_3_72_modular_location_aware_split_verifier_20260824.split_verifier import (
    formal_negation,
    make_gemma_verifier_runtime,
)
from cognitive_well_harness_v0_3_73_modular_full_lemma_body_synthesis_20260825.synthesis import (
    label_verified_lemmas,
)
from cognitive_well_harness_v0_3_78_modular_failure_salvage_statement_only_20260825.memory import (
    extend_shared_verified_exact,
)
from cognitive_well_harness_v0_3_78_modular_failure_salvage_statement_only_20260825.contracts import (
    FAILURE_SALVAGE_SCHEMA,
)
from cognitive_well_harness_v0_3_78_modular_failure_salvage_statement_only_20260825.prompts import (
    FAILURE_SALVAGE_SYSTEM_PROMPT,
    failure_salvage_user_prompt,
)
from cognitive_well_harness_v0_3_78_modular_failure_salvage_statement_only_20260825.salvage import (
    _salvage_one,
    failure_card_for_pair,
    select_failure_cards,
)
from cognitive_well_harness_v0_3_79_modular_singleton_atomic_retry_20260825.full_pipeline import (
    child_paths as v079_child_paths,
)
from cognitive_well_harness_v0_3_79_modular_singleton_atomic_retry_20260825.retry import (
    read_json,
    run_atomic_retry,
)
from cognitive_well_harness_v0_3_79_modular_singleton_atomic_retry_20260825.run_enriched_high_stakes_resolver_2 import (
    FUSION_FIELDS,
    QWEN_FIELDS,
    one_result_path,
    parsed_fields,
    sha256_text,
)
from cognitive_well_harness_v0_3_79_modular_singleton_atomic_retry_20260825.run_gemma_repair_qwen_rejected_full_body_4 import (
    GEMMA_MODEL,
    QWEN_MODEL,
)
from cognitive_well_harness_v0_3_79_modular_singleton_atomic_retry_20260825.runtime import (
    ResilientModelRuntime,
    recovery_profile,
)

from . import HARNESS_VERSION
from .prompts import (
    FAILED_COMPARATOR_PROMPT,
    failed_comparator_user_prompt,
    iterative_extraction_prompt,
    lemma_body_replay_prompt,
    lemma_defect_attribution_prompt,
    lemma_revision_prompt,
    refinement_prompt,
    synthesis_prompt,
)


ITERATION_COUNT = 2
EXTRACTION_SCHEDULE: tuple[dict[str, Any], ...] = (
    {"round": 1, "temperature": 0.2},
    {"round": 2, "temperature": 0.4},
    {"round": 3, "temperature": 0.8},
)
SYNTHESIS_CONFIGS: tuple[dict[str, Any], ...] = (
    {"candidate_id": "statement_only", "mode": "statement_only", "anchor": None},
    {"candidate_id": "evidence_only", "mode": "evidence_only", "anchor": None},
    {"candidate_id": "anchored_a", "mode": "anchored", "anchor": 0},
    {"candidate_id": "anchored_b", "mode": "anchored", "anchor": 1},
    {"candidate_id": "location_aware", "mode": "location_aware", "anchor": None},
    {
        "candidate_id": "evidence_location",
        "mode": "evidence_location",
        "anchor": None,
    },
)
FAILED_COMPARATOR_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["classification", "matched_failed_id"],
    "properties": {
        "classification": {
            "type": "string",
            "enum": [
                "SAME_FAILED_HYPOTHESIS",
                "STRICT_REPAIR_OR_NARROWING",
                "DISTINCT_OR_UNCERTAIN",
            ],
        },
        "matched_failed_id": {"type": "string", "minLength": 1},
    },
}
LEMMA_ATTRIBUTION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "stored_body_contains_same_obligation",
        "stored_body_obligation_status",
        "classification",
        "failed_obligation",
        "evidence",
    ],
    "properties": {
        "stored_body_contains_same_obligation": {"type": "boolean"},
        "stored_body_obligation_status": {
            "type": "string",
            "enum": ["DISCHARGED", "UNRESOLVED", "NOT_PRESENT_OR_DIFFERENT"],
        },
        "classification": {
            "type": "string",
            "enum": [
                "LEMMA_BODY_DEFECT",
                "LEMMA_STATEMENT_DEFECT",
                "APPLICATION_ONLY",
                "UNRELATED_OR_UNCERTAIN",
            ],
        },
        "failed_obligation": {"type": "string", "minLength": 1},
        "evidence": {"type": "string", "minLength": 1},
    },
}
LEMMA_BODY_REPLAY_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "same_obligation",
        "verdict",
        "first_break",
        "verification",
    ],
    "properties": {
        "same_obligation": {"type": "boolean"},
        "verdict": {
            "type": "string",
            "enum": [
                "STORED_BODY_FAIL",
                "STORED_BODY_PASS",
                "NOT_SAME_OBLIGATION",
                "UNCERTAIN",
            ],
        },
        "first_break": {"type": "string", "minLength": 1},
        "verification": {"type": "string", "minLength": 1},
    },
}
LEMMA_REVISION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "decision",
        "revised_statement",
        "exact_negation",
        "earliest_unresolved_transition",
        "local_dependency_map",
        "repair_rationale",
    ],
    "properties": {
        "decision": {
            "type": "string",
            "enum": [
                "REPAIR_SAME_STATEMENT",
                "NARROW_STATEMENT",
                "CANNOT_REPAIR",
            ],
        },
        "revised_statement": {"type": "string", "minLength": 20},
        "exact_negation": {"type": "string", "minLength": 20},
        "earliest_unresolved_transition": {"type": "string", "minLength": 10},
        "local_dependency_map": {"type": "string", "minLength": 10},
        "repair_rationale": {"type": "string", "minLength": 10},
    },
}


def _status(output_dir: Path, stage: str, **values: Any) -> None:
    write_json(
        output_dir / "status.json",
        {
            "state": "running",
            "stage": stage,
            **values,
            "updated_at": utc_now(),
        },
    )


def _failure_exact_key(row: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        normalized(str(row["hypothesis"])),
        normalized(str(row["exact_negation"])),
        normalized(str(row["earliest_unresolved_transition"])),
        normalized(str(row["local_dependency_map"])),
    )


def _hypothesis_exact_key(row: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        normalized(str(row["conjecture"])),
        normalized(str(row["exact_negation"])),
        normalized(str(row["earliest_unresolved_transition"])),
        normalized(str(row["local_dependency_map"])),
    )


def _compact_packet(result: dict[str, Any], names: tuple[str, ...]) -> dict[str, Any]:
    fields = dict(result.get("parsed", {}).get("fields", {}))
    return {
        "outcome": result.get("parsed", {}).get("outcome"),
        **{name: fields.get(name) for name in names if fields.get(name)},
    }


def load_initial_state(source_run_dir: Path) -> dict[str, Any]:
    leaf_dir = v079_child_paths(source_run_dir)["leaf"]
    run_input = read_json(leaf_dir.parent.parent / "selected_pair_input.json")
    review_root = source_run_dir / "three_review_fusion_recheck_repaired_4"
    summary = read_json(review_root / "summary.json")
    selected = [
        row for row in summary["candidates"] if row["fusion_outcome"] == "REPAIR_NEEDED"
    ]
    if len(selected) != 2:
        raise RuntimeError(f"expected two audited source proofs, got {len(selected)}")
    proofs: list[dict[str, Any]] = []
    for index, source in enumerate(selected):
        candidate_id = str(source["candidate_id"])
        proof_path = Path(str(source["proof_path"]))
        proof = proof_path.read_text(encoding="utf-8").strip()
        if sha256_text(proof) != str(source["proof_sha256"]):
            raise RuntimeError(f"source proof hash mismatch for {candidate_id}")
        qwen_path = one_result_path(review_root / "reviewer_2", candidate_id)
        fusion_path = one_result_path(review_root / "fusion_stage", candidate_id)
        qwen_packet = parsed_fields(qwen_path, QWEN_FIELDS)
        qwen_packet["outcome"] = str(
            read_json(qwen_path)["parsed"]["outcome"]
        )
        fusion_packet = parsed_fields(fusion_path, FUSION_FIELDS)
        fusion_packet["outcome"] = str(
            read_json(fusion_path)["parsed"]["outcome"]
        )
        proofs.append(
            {
                "candidate_id": candidate_id,
                "role": "anchor" if index == 0 else "supplement",
                "proof": proof,
                "proof_path": str(proof_path.resolve()),
                "proof_sha256": str(source["proof_sha256"]),
                "qwen_defect_packet": qwen_packet,
                "fusion_defect_packet": fusion_packet,
                "qwen_result_path": str(qwen_path.resolve()),
                "fusion_result_path": str(fusion_path.resolve()),
            }
        )
    return {
        "problem_id": str(run_input["problem_id"]),
        "problem": str(run_input["problem"]),
        "candidate_proofs": proofs,
        "synthesis_instructions": str(run_input.get("synthesis_instructions") or ""),
        "gate": dict(run_input.get("gate") or {}),
    }


def _extract_one(
    *,
    runtime: ResilientModelRuntime,
    problem: str,
    candidate_proofs: list[dict[str, Any]],
    certified_memory: list[dict[str, Any]],
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
            certified_memory=certified_memory,
            failed_memory=failed_memory,
        ),
        destination=destination,
        stage="hypothesis_document",
        temperature=temperature,
        max_tokens=32_768,
        seed_label=f"v081:i{iteration}:extraction:r{round_number}",
    )
    document = str(generated["text"]).strip()
    record = deterministic_location_record(document)
    parser_generation: dict[str, Any] | None = None
    attempts: list[dict[str, Any]] = []
    if record is not None:
        validate_schema(record, LOCATION_HYPOTHESIS_SCHEMA)
        parser_generation = {"metadata": {"source": "deterministic_section_parser"}}
        attempts.append({"attempt": 0, "stage": "deterministic", "status": "accepted"})
    for attempt in range(PARSER_MAX_ATTEMPTS) if record is None else ():
        try:
            record, parser_generation = runtime.structured(
                role="gemma",
                prompt=location_hypothesis_parser_prompt(document),
                destination=destination,
                stage=f"location_parser_{attempt}",
                schema=LOCATION_HYPOTHESIS_SCHEMA,
                temperature=PARSER_TEMPERATURE,
                max_tokens=8_192,
                seed_label=f"v081:i{iteration}:r{round_number}:parser:{attempt}",
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
    certified_memory: list[dict[str, Any]],
    failed_memory: list[dict[str, Any]],
    iteration: int,
    output_dir: Path,
) -> list[dict[str, Any]]:
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        results = list(
            executor.map(
                lambda config: _extract_one(
                    runtime=runtime,
                    problem=problem,
                    candidate_proofs=candidate_proofs,
                    certified_memory=certified_memory,
                    failed_memory=failed_memory,
                    iteration=iteration,
                    config=config,
                    output_dir=output_dir,
                ),
                EXTRACTION_SCHEDULE,
            )
        )
    return results


def _semantic_compare(
    *,
    runtime: ResilientModelRuntime,
    candidate: dict[str, str],
    failed_memory: list[dict[str, Any]],
    iteration: int,
    candidate_index: int,
    output_dir: Path,
) -> dict[str, Any]:
    user_prompt = failed_comparator_user_prompt(
        candidate=candidate, failed_memory=failed_memory
    )

    def compare(number: int) -> dict[str, Any]:
        record, generation = runtime.structured(
            role="qwen",
            prompt=FAILED_COMPARATOR_PROMPT,
            user_prompt=user_prompt,
            destination=output_dir / f"comparison_{number}",
            stage="failed_semantic_comparison",
            schema=FAILED_COMPARATOR_SCHEMA,
            temperature=0.1,
            max_tokens=16_384,
            seed_label=f"v081:i{iteration}:failed_compare:{candidate_index}:{number}",
        )
        return {"record": record, "generation": generation["metadata"]}

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        calls = list(executor.map(compare, (1, 2)))
    classifications = [row["record"]["classification"] for row in calls]
    reject = classifications == ["SAME_FAILED_HYPOTHESIS"] * 2
    return {
        "calls": calls,
        "unanimous_semantic_duplicate": reject,
        "decision": "reject_semantic_failed_duplicate" if reject else "allow",
    }


def novelty_gate(
    *,
    runtime: ResilientModelRuntime,
    extraction_results: list[dict[str, Any]],
    certified_memory: list[dict[str, Any]],
    failed_memory: list[dict[str, Any]],
    iteration: int,
    output_dir: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    candidates: list[dict[str, Any]] = []
    for extraction in extraction_results:
        for hypothesis_index, hypothesis in enumerate(
            extraction["record"]["hypotheses"], start=1
        ):
            candidates.append(
                {
                    **hypothesis,
                    "source_round": extraction["round"],
                    "source_temperature": extraction["temperature"],
                    "source_hypothesis_index": hypothesis_index,
                }
            )
    certified_statements = {normalized(str(row["statement"])) for row in certified_memory}
    failed_exact = {
        _failure_exact_key(row): row
        for row in failed_memory
        if not row.get("resolved_by_certification")
    }
    active_failed_memory = [
        row for row in failed_memory if not row.get("resolved_by_certification")
    ]
    accepted: list[dict[str, Any]] = []
    audit: list[dict[str, Any]] = []
    for index, candidate in enumerate(candidates, start=1):
        if normalized(str(candidate["conjecture"])) in certified_statements:
            audit.append({"candidate": candidate, "decision": "reject_exact_certified_statement"})
            continue
        exact_failure = failed_exact.get(_hypothesis_exact_key(candidate))
        if exact_failure is not None:
            audit.append(
                {
                    "candidate": candidate,
                    "decision": "reject_exact_failed_duplicate",
                    "matched_failed_id": exact_failure["failed_id"],
                }
            )
            continue
        semantic = None
        if active_failed_memory:
            semantic = _semantic_compare(
                runtime=runtime,
                candidate=candidate,
                failed_memory=active_failed_memory,
                iteration=iteration,
                candidate_index=index,
                output_dir=output_dir / f"candidate_{index}",
            )
            if semantic["unanimous_semantic_duplicate"]:
                audit.append({"candidate": candidate, **semantic})
                continue
        accepted.append(candidate)
        audit.append({"candidate": candidate, "decision": "accepted", "semantic": semantic})
    write_json(output_dir / "audit.json", audit)
    return accepted, audit


def _decisive_failure(card: dict[str, Any]) -> str:
    payload = card["failure_card"]
    parts: list[str] = []
    for side in ("positive_signal", "negative_signal"):
        signal = payload.get(side) or {}
        for key in ("earliest_break", "summary"):
            if signal.get(key):
                parts.append(str(signal[key]))
    return " | ".join(parts) or str(payload["status"])


def _failed_record_from_card(
    *, card: dict[str, Any], pair: dict[str, str], iteration: int
) -> dict[str, Any]:
    return {
        "failed_id": f"I{iteration}:{pair['claim_id']}",
        "iteration": iteration,
        "source_claim_id": pair["claim_id"],
        "status": card["status"],
        "hypothesis": pair["positive"],
        "exact_negation": pair["negative"],
        "earliest_unresolved_transition": pair["earliest_unresolved_transition"],
        "local_dependency_map": pair["local_dependency_map"],
        "decisive_failure": _decisive_failure(card),
        "resolved_by_certification": False,
    }


def _insert_failed_exact(
    existing: list[dict[str, Any]], additions: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    memory = copy.deepcopy(existing)
    keys = {_failure_exact_key(row): row for row in memory}
    audit: list[dict[str, Any]] = []
    for row in additions:
        key = _failure_exact_key(row)
        if key in keys:
            keys[key].setdefault("repeat_sources", []).append(row["failed_id"])
            audit.append(
                {
                    "failed_id": row["failed_id"],
                    "decision": "rejected_exact_duplicate",
                    "kept_failed_id": keys[key]["failed_id"],
                }
            )
            continue
        memory.append(row)
        keys[key] = row
        audit.append({"failed_id": row["failed_id"], "decision": "inserted"})
    return memory, audit


def _recover_one_salvage_transport(
    *,
    runtime: ResilientModelRuntime,
    problem: str,
    candidate_proofs: list[dict[str, str]],
    selected_case: dict[str, Any],
    output_dir: Path,
) -> dict[str, Any]:
    """Retry only a structurally malformed salvage record without changing its task.

    The nominal v0.3.63 request has already exhausted its original/compact/repair
    boundary. This extension keeps its system prompt, user prompt, schema, Gemma
    model, temperature, token ceiling, and repetition detector. Both runtime roles
    are pinned to Gemma so transport recovery cannot silently switch models.
    """
    case_name = str(selected_case["case_name"])
    destination = output_dir / case_name
    failure_card = dict(selected_case["failure_card"])
    user_prompt = failure_salvage_user_prompt(
        problem=problem,
        candidate_proofs=candidate_proofs,
        failure_card=failure_card,
    )
    pinned = ResilientModelRuntime(
        RuntimeConfig(
            gemma_endpoint=runtime.config.gemma_endpoint,
            qwen_endpoint=runtime.config.gemma_endpoint,
            gemma_model=runtime.config.gemma_model,
            qwen_model=runtime.config.gemma_model,
            master_seed=runtime.config.master_seed,
        )
    )
    wave_failures: list[str] = []
    record = None
    generation = None
    for wave in range(1, 4):
        try:
            record, generation = pinned.structured(
                role="gemma",
                prompt=FAILURE_SALVAGE_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                destination=destination,
                stage=f"failure_guided_salvage_v081_transport_retry_w{wave}",
                schema=FAILURE_SALVAGE_SCHEMA,
                temperature=0.4,
                max_tokens=32_768,
                seed_label=(
                    "v081:salvage_transport_retry:"
                    + case_name
                    + f":wave:{wave}:"
                    + sha256_text(user_prompt)[:16]
                ),
            )
            break
        except RuntimeError as error:
            wave_failures.append(f"wave_{wave}: {error}")
    if record is None or generation is None:
        raise RuntimeError(
            "v0.3.81 scoped salvage transport recovery exhausted: "
            + " | ".join(wave_failures)
        )
    source = {
        key: selected_case[key]
        for key in ("source_claim_id", "source_arm", "source_round")
    }
    result = {
        "schema": "cognitive-well-failure-guided-salvage-surgical-v1",
        "case_name": case_name,
        "source": source,
        "failure_card": failure_card,
        "record": record,
        "generation": {
            **generation["metadata"],
            "v081_scoped_transport_recovery": True,
            "model_pinned_to_gemma": True,
            "failed_prior_waves": wave_failures,
        },
    }
    write_json(destination / "result.json", result)
    return result


def run_failure_guided_salvage_resilient(
    *,
    runtime: ResilientModelRuntime,
    verifier_runtime: ResilientModelRuntime,
    problem: str,
    candidate_proofs: list[dict[str, str]],
    failure_cards: list[dict[str, Any]],
    output_dir: Path,
    limit: int,
) -> dict[str, Any]:
    """Run all selected cards, recovering a malformed record per case."""
    selected = select_failure_cards(failure_cards, limit=limit)
    if not selected:
        result = {
            "selected_failure_count": 0,
            "selected_failures": [],
            "generated_hypothesis_count": 0,
            "verified": [],
            "unresolved": [],
            "cases": [],
            "provenance": {},
        }
        write_json(output_dir / "summary.json", result)
        return result

    def generate_case(selected_case: dict[str, Any]) -> dict[str, Any]:
        case_name = str(selected_case["case_name"])
        result_path = output_dir / "hypothesis_salvage" / case_name / "result.json"
        if result_path.is_file():
            return read_json(result_path)
        try:
            return _salvage_one(
                runtime=runtime,
                problem=problem,
                candidate_proofs=candidate_proofs,
                selected_case=selected_case,
                output_dir=output_dir / "hypothesis_salvage",
            )
        except RuntimeError as error:
            if not str(error).startswith("structured salvage recovery exhausted:"):
                raise
            return _recover_one_salvage_transport(
                runtime=runtime,
                problem=problem,
                candidate_proofs=candidate_proofs,
                selected_case=selected_case,
                output_dir=output_dir / "hypothesis_salvage",
            )

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(selected)) as executor:
        cases = list(executor.map(generate_case, selected))

    pairs: list[dict[str, str]] = []
    provenance: dict[str, dict[str, Any]] = {}
    for case in cases:
        source = case["source"]
        status = str(case["failure_card"]["status"])
        for hypothesis_index, hypothesis in enumerate(
            case["record"]["hypotheses"], start=1
        ):
            if case["case_name"] == status.lower():
                claim_prefix = status
            else:
                source_fragment = re.sub(
                    r"[^A-Za-z0-9_]+", "_", str(source["source_claim_id"])
                ).strip("_")
                claim_prefix = f"{status}_{source_fragment}"
            claim_id = f"{claim_prefix}_H{hypothesis_index}"
            pairs.append(
                {
                    "claim_id": claim_id,
                    "positive": str(hypothesis["statement"]),
                    "negative": str(hypothesis["exact_negation"]),
                    "earliest_unresolved_transition": str(
                        hypothesis["earliest_unresolved_transition"]
                    ),
                    "local_dependency_map": str(hypothesis["local_dependency_map"]),
                }
            )
            provenance[claim_id] = {
                "case_name": case["case_name"],
                "source_claim_id": source["source_claim_id"],
                "source_status": status,
                "source_arm": source["source_arm"],
                "source_round": source["source_round"],
                "salvage_decision": case["record"]["decision"],
                "relation_to_failed_hypothesis": hypothesis[
                    "relation_to_failed_hypothesis"
                ],
            }
    verified, unresolved = prove_pairs(
        runtime=runtime,
        verifier_runtime=verifier_runtime,
        problem=problem,
        pairs=pairs,
        output_dir=output_dir / "atomic_proof_generation",
    )
    for row in verified:
        row["failure_salvage_provenance"] = provenance[row["lemma_id"]]
    result = {
        "selected_failure_count": len(selected),
        "selected_failures": selected,
        "generated_hypothesis_count": len(pairs),
        "verified": verified,
        "unresolved": unresolved,
        "cases": cases,
        "provenance": provenance,
        "v081_scoped_transport_recovery_cases": [
            row["case_name"]
            for row in cases
            if row.get("generation", {}).get("v081_scoped_transport_recovery")
        ],
    }
    write_json(output_dir / "summary.json", result)
    return result


def run_certification_and_memory(
    *,
    proof_runtime: ResilientModelRuntime,
    verifier_runtime: ResilientModelRuntime,
    runtime_config: RuntimeConfig,
    salvage_verifier_endpoint: str,
    problem: str,
    candidate_proofs: list[dict[str, Any]],
    accepted_hypotheses: list[dict[str, Any]],
    certified_memory: list[dict[str, Any]],
    failed_memory: list[dict[str, Any]],
    iteration: int,
    output_dir: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    record = {
        "hypotheses": [
            {
                key: row[key]
                for key in (
                    "conjecture",
                    "exact_negation",
                    "earliest_unresolved_transition",
                    "local_dependency_map",
                )
            }
            for row in accepted_hypotheses
        ]
    }
    pairs = validate_and_repair_negations(
        runtime=proof_runtime,
        problem=problem,
        hypotheses=record,
        arm=f"iteration_{iteration}",
        round_number=iteration,
        output_dir=output_dir / "negation_validation",
    )
    initial_verified, initial_unresolved = prove_pairs(
        runtime=proof_runtime,
        verifier_runtime=verifier_runtime,
        problem=problem,
        pairs=pairs,
        output_dir=output_dir / "initial_lemma_proving",
    )
    pair_by_id = {row["claim_id"]: row for row in pairs}
    failure_cards: list[dict[str, Any]] = []
    failed_additions: list[dict[str, Any]] = []
    for pair in pairs:
        pair_dir = output_dir / "initial_lemma_proving" / pair["claim_id"]
        wrapper = failure_card_for_pair(
            pair=pair,
            positive=read_json(pair_dir / "positive" / "result.json"),
            negative=read_json(pair_dir / "negative" / "result.json"),
            source_arm=f"iteration_{iteration}",
            round_number=iteration,
        )
        if wrapper is not None:
            failure_cards.append(wrapper)
            failed_additions.append(
                _failed_record_from_card(card=wrapper, pair=pair, iteration=iteration)
            )

    memory_after_initial, initial_insert_audit = extend_shared_verified_exact(
        existing_verified=certified_memory,
        salvage_verified=initial_verified,
        output_dir=output_dir / "initial_exact_memory_insertion",
    )
    salvage = run_failure_guided_salvage_resilient(
        runtime=proof_runtime,
        verifier_runtime=verifier_runtime,
        problem=problem,
        candidate_proofs=[
            {
                "candidate_id": row["candidate_id"],
                "role": row["role"],
                "proof": row["proof"],
            }
            for row in candidate_proofs
        ],
        failure_cards=failure_cards,
        output_dir=output_dir / "failure_guided_salvage",
        limit=len(failure_cards),
    )
    memory_after_salvage, salvage_insert_audit = extend_shared_verified_exact(
        existing_verified=memory_after_initial,
        salvage_verified=list(salvage["verified"]),
        output_dir=output_dir / "salvage_exact_memory_insertion",
    )
    write_json(
        output_dir / "shared_lemma_memory.json",
        {"verified": memory_after_salvage, "unresolved": initial_unresolved + salvage["unresolved"]},
    )
    iteration_input = {
        "problem_id": "iterative_problem",
        "problem": problem,
        "candidate_proofs": [
            {
                "candidate_id": row["candidate_id"],
                "role": row["role"],
                "proof": row["proof"],
            }
            for row in candidate_proofs
        ],
    }
    input_path = output_dir / "iteration_input.json"
    write_json(input_path, iteration_input)
    retry = run_atomic_retry(
        source_run_dir=output_dir,
        input_path=input_path,
        output_dir=output_dir / "atomic_child_retry",
        runtime_config=runtime_config,
        salvage_verifier_endpoint=salvage_verifier_endpoint,
    )
    final_memory_payload = read_json(
        output_dir / "atomic_child_retry" / "augmented_shared_lemma_memory.json"
    )
    final_certified = list(final_memory_payload["verified"])

    # Persist every failed atomic child. Parent cards above remain the main reusable
    # failure context; child records prevent the next iteration from regenerating the
    # same decomposition verbatim.
    salvage_verified = {row["lemma_id"]: row for row in salvage["verified"]}
    salvage_unresolved = {row["claim_id"]: row for row in salvage["unresolved"]}
    for claim_id, provenance in salvage["provenance"].items():
        case = next(row for row in salvage["cases"] if row["case_name"] == provenance["case_name"])
        index_match = re.search(r"_H([1-9][0-9]*)$", claim_id)
        if index_match is None:
            continue
        hypothesis = case["record"]["hypotheses"][int(index_match.group(1)) - 1]
        verified_row = salvage_verified.get(claim_id)
        if verified_row is not None and verified_row["direction"] == "positive":
            continue
        unresolved = salvage_unresolved.get(claim_id)
        status = (
            "REFUTED"
            if verified_row is not None
            else "VERIFIER_CONFLICT"
            if unresolved and unresolved["status"] == "logical_conflict"
            else "PROOF_FAILED"
        )
        failed_additions.append(
            {
                "failed_id": f"I{iteration}:SALVAGE:{claim_id}",
                "iteration": iteration,
                "source_claim_id": claim_id,
                "status": status,
                "hypothesis": str(hypothesis["statement"]),
                "exact_negation": str(hypothesis["exact_negation"]),
                "earliest_unresolved_transition": str(hypothesis["earliest_unresolved_transition"]),
                "local_dependency_map": str(hypothesis["local_dependency_map"]),
                "decisive_failure": str(unresolved or status),
                "parent_failed_id": f"I{iteration}:{provenance['source_claim_id']}",
                "resolved_by_certification": False,
            }
        )

    final_failed, failed_insert_audit = _insert_failed_exact(
        failed_memory, failed_additions
    )
    certified_statements = {normalized(str(row["statement"])) for row in final_certified}
    for row in final_failed:
        if normalized(str(row["hypothesis"])) in certified_statements:
            row["resolved_by_certification"] = True
            row["resolved_iteration"] = iteration
    result = {
        "accepted_hypothesis_count": len(accepted_hypotheses),
        "pair_count": len(pairs),
        "initial_verified_count": len(initial_verified),
        "initial_unresolved_count": len(initial_unresolved),
        "salvage_failure_count": len(failure_cards),
        "salvage_generated_count": salvage["generated_hypothesis_count"],
        "salvage_verified_count": len(salvage["verified"]),
        "retry_verified_count": retry["verified_count"],
        "certified_memory_count": len(final_certified),
        "failed_memory_count": len(final_failed),
        "initial_insert_audit": initial_insert_audit,
        "salvage_insert_audit": salvage_insert_audit,
        "failed_insert_audit": failed_insert_audit,
    }
    write_json(output_dir / "certification_summary.json", result)
    write_json(output_dir / "certified_memory.json", {"verified": final_certified})
    write_json(output_dir / "failed_memory.json", {"failed": final_failed})
    return final_certified, final_failed, result


def run_synthesis(
    *,
    runtime: ResilientModelRuntime,
    problem: str,
    candidate_proofs: list[dict[str, Any]],
    certified_memory: list[dict[str, Any]],
    iteration: int,
    output_dir: Path,
) -> list[dict[str, Any]]:
    """Generate the frozen six-candidate mix, all at Gemma temperature 0.4."""
    lemmas = label_verified_lemmas(certified_memory)

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
                mode=mode,
                problem=problem,
                lemmas=lemmas,
                anchor_proof=anchor,
            ),
            destination=destination,
            stage="main_proof",
            temperature=0.4,
            max_tokens=32_768,
            seed_label=f"v081:i{iteration}:synthesis:{candidate_id}",
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
            "proof_sha256": sha256_text(proof),
            "generation": generated["metadata"],
            "assembly": assembled,
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
            "modes": dict(Counter(row["mode"] for row in rows)),
            "candidates": [
                {
                    key: row[key]
                    for key in (
                        "candidate_id",
                        "mode",
                        "anchor_candidate_id",
                        "proof_path",
                        "proof_sha256",
                    )
                }
                for row in rows
            ],
        },
    )
    return rows


def _audit_packet(result: dict[str, Any]) -> dict[str, Any]:
    parsed = dict(result.get("parsed") or {})
    fields = dict(parsed.get("fields") or {})
    return {"outcome": parsed.get("outcome"), **fields}


def run_review_fusion(
    *,
    run_input: dict[str, Any],
    candidates: list[dict[str, Any]],
    gemma_endpoint: str,
    qwen_endpoint: str,
    output_dir: Path,
) -> list[dict[str, Any]]:
    """Run the frozen three reviews and revised Fusion on every proof."""
    proof_rows: list[dict[str, Any]] = []
    for proof_index, candidate in enumerate(candidates):
        proof_rows.append(
            {
                "proof_index": proof_index,
                "problem_number": v067.problem_number_for_artifacts(run_input),
                "problem_id": run_input["problem_id"],
                "candidate_id": candidate["candidate_id"],
                "problem": run_input["problem"],
                "problem_sha256": sha256_text(str(run_input["problem"])),
                "proof": candidate["proof"],
                "proof_path": candidate["proof_path"],
                "proof_sha256": candidate["proof_sha256"],
                "source_temperature": 0.4,
            }
        )

    review_results: dict[str, dict[str, dict[str, Any]]] = {}
    for reviewer_name, module in (
        ("reviewer_1", v067.reviewer_1),
        ("reviewer_2", v067.reviewer_2),
        ("reviewer_3", v067.reviewer_3),
    ):
        tasks = [
            v067.build_review_task(
                run_input=run_input,
                row=row,
                reviewer_name=reviewer_name,
                gemma_endpoint=gemma_endpoint,
                qwen_endpoint=qwen_endpoint,
            )
            for row in proof_rows
        ]
        results = v067._parallel_stage(
            output_dir=output_dir,
            stage=reviewer_name,
            rows=tasks,
            identity=lambda row: str(row["candidate_id"]),
            worker=lambda task, module=module: module.run_task(
                output_dir=output_dir / reviewer_name,
                task=task,
            ),
        )
        review_results[reviewer_name] = {
            str(result["task"]["candidate_id"]): result for result in results
        }

    fusion_tasks: list[dict[str, Any]] = []
    for row in proof_rows:
        candidate_id = str(row["candidate_id"])
        fusion_tasks.append(
            v067.build_fusion_task(
                run_input=run_input,
                row=row,
                reviews={
                    name: review_results[name][candidate_id]
                    for name in ("reviewer_1", "reviewer_2", "reviewer_3")
                },
                gemma_endpoint=gemma_endpoint,
            )
        )
    fusion_rows = v067._parallel_stage(
        output_dir=output_dir,
        stage="fusion",
        rows=fusion_tasks,
        identity=lambda row: str(row["candidate_id"]),
        worker=lambda task: v067.fusion.run_task(
            output_dir=output_dir / "fusion_stage", task=task
        ),
    )
    fusion_results = {
        str(result["task"]["candidate_id"]): result for result in fusion_rows
    }
    by_id = {str(row["candidate_id"]): row for row in candidates}
    audited: list[dict[str, Any]] = []
    for row in proof_rows:
        candidate_id = str(row["candidate_id"])
        source = by_id[candidate_id]
        qwen_result = review_results["reviewer_2"][candidate_id]
        fusion_result = fusion_results[candidate_id]
        audited.append(
            {
                **source,
                "qwen_defect_packet": _audit_packet(qwen_result),
                "fusion_defect_packet": _audit_packet(fusion_result),
                "qwen_final": qwen_result["final"],
                "fusion_final": fusion_result["final"],
                "qwen_outcome": qwen_result["parsed"]["outcome"],
                "fusion_outcome": fusion_result["parsed"]["outcome"],
                "review_outcomes": {
                    name: review_results[name][candidate_id]["parsed"]["outcome"]
                    for name in ("reviewer_1", "reviewer_2", "reviewer_3")
                },
            }
        )
    write_json(
        output_dir / "summary.json",
        {
            "candidate_count": len(audited),
            "reviewer_outcomes": {
                name: dict(
                    Counter(
                        str(result["parsed"]["outcome"])
                        for result in review_results[name].values()
                    )
                )
                for name in ("reviewer_1", "reviewer_2", "reviewer_3")
            },
            "fusion_outcomes": dict(
                Counter(str(row["fusion_outcome"]) for row in audited)
            ),
            "candidates": [
                {
                    "candidate_id": row["candidate_id"],
                    "proof_path": row["proof_path"],
                    "proof_sha256": row["proof_sha256"],
                    "review_outcomes": row["review_outcomes"],
                    "qwen_outcome": row["qwen_outcome"],
                    "fusion_outcome": row["fusion_outcome"],
                }
                for row in audited
            ],
        },
    )
    return audited


def run_refinement(
    *,
    runtime: ResilientModelRuntime,
    problem: str,
    audited_candidates: list[dict[str, Any]],
    iteration: int,
    output_dir: Path,
) -> list[dict[str, Any]]:
    """One full-replacement, high-stakes Gemma refinement for every candidate."""

    def refine(candidate: dict[str, Any]) -> dict[str, Any]:
        candidate_id = str(candidate["candidate_id"])
        destination = output_dir / "candidates" / candidate_id
        generated = runtime.text(
            role="gemma",
            prompt=refinement_prompt(
                problem=problem,
                proof=str(candidate["proof"]),
                qwen_packet=dict(candidate["qwen_defect_packet"]),
                fusion_packet=dict(candidate["fusion_defect_packet"]),
            ),
            destination=destination,
            stage="refined_proof",
            temperature=0.4,
            max_tokens=32_768,
            seed_label=f"v081:i{iteration}:refinement:{candidate_id}",
        )
        proof = str(generated["text"]).strip()
        proof_path = destination / "refined_proof.md"
        proof_path.parent.mkdir(parents=True, exist_ok=True)
        proof_path.write_text(proof + "\n", encoding="utf-8")
        result = {
            **candidate,
            "pre_refinement_proof": candidate["proof"],
            "pre_refinement_proof_path": candidate["proof_path"],
            "pre_refinement_proof_sha256": candidate["proof_sha256"],
            "proof": proof,
            "proof_path": str(proof_path.resolve()),
            "proof_sha256": sha256_text(proof),
            "refinement_temperature": 0.4,
            "refinement_generation": generated["metadata"],
        }
        write_json(destination / "result.json", result)
        return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        rows = list(executor.map(refine, audited_candidates))
    write_json(
        output_dir / "summary.json",
        {
            "candidate_count": len(rows),
            "temperature": 0.4,
            "candidates": [
                {
                    "candidate_id": row["candidate_id"],
                    "proof_path": row["proof_path"],
                    "proof_sha256": row["proof_sha256"],
                    "pre_refinement_proof_sha256": row[
                        "pre_refinement_proof_sha256"
                    ],
                }
                for row in rows
            ],
        },
    )
    return rows


LEMMA_SCOPE_CLASSIFICATIONS = frozenset(
    {"LEMMA_BODY_DEFECT", "LEMMA_STATEMENT_DEFECT"}
)


def attribution_consensus(attributions: list[dict[str, Any]]) -> dict[str, Any]:
    """Require two independent Qwen calls to implicate the lemma itself."""
    reported_classifications = [str(row["classification"]) for row in attributions]
    classifications = [
        "LEMMA_BODY_DEFECT"
        if bool(row.get("stored_body_contains_same_obligation"))
        and str(row.get("stored_body_obligation_status")) == "UNRESOLVED"
        else str(row["classification"])
        for row in attributions
    ]
    quarantine = (
        len(classifications) == 2
        and all(value in LEMMA_SCOPE_CLASSIFICATIONS for value in classifications)
    )
    if not quarantine:
        scope = "NO_LEMMA_QUARANTINE"
    elif "LEMMA_STATEMENT_DEFECT" in classifications:
        scope = "LEMMA_STATEMENT_DEFECT"
    else:
        scope = "LEMMA_BODY_DEFECT"
    return {
        "quarantine": quarantine,
        "scope": scope,
        "classifications": classifications,
        "reported_classifications": reported_classifications,
    }


def body_replay_consensus(audits: list[dict[str, Any]]) -> dict[str, Any]:
    verdicts = [str(row["verdict"]) for row in audits]
    same = [bool(row["same_obligation"]) for row in audits]
    confirmed_body_defect = (
        len(audits) == 2
        and all(same)
        and all(verdict == "STORED_BODY_FAIL" for verdict in verdicts)
    )
    return {
        "confirmed_body_defect": confirmed_body_defect,
        "same_obligation": same,
        "verdicts": verdicts,
    }


def _audit_reports_defect(candidate: dict[str, Any]) -> bool:
    return (
        str(candidate.get("qwen_outcome")) != "NO_ADVERSARIAL_BREAK"
        or str(candidate.get("fusion_outcome")) != "ACCEPT_AS_WRITTEN"
    )


def _defect_events(candidate: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    events: list[tuple[str, dict[str, Any]]] = []
    if str(candidate.get("qwen_outcome")) != "NO_ADVERSARIAL_BREAK":
        events.append(("qwen", dict(candidate.get("qwen_defect_packet") or {})))
    if str(candidate.get("fusion_outcome")) != "ACCEPT_AS_WRITTEN":
        events.append(("fusion", dict(candidate.get("fusion_defect_packet") or {})))
    return events


def _safe_component(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")
    return cleaned[:120] or "unnamed"


def _structured_with_v081_transport_waves(
    *,
    runtime: ResilientModelRuntime,
    role: str,
    prompt: str,
    destination: Path,
    stage: str,
    schema: dict[str, Any],
    temperature: float,
    max_tokens: int,
    seed_label: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Add bounded fresh requests only after nominal structured recovery exhausts."""
    failures: list[str] = []
    for wave in range(0, 4):
        wave_stage = stage if wave == 0 else f"{stage}_v081_transport_w{wave}"
        wave_seed = seed_label if wave == 0 else f"{seed_label}:transport:{wave}"
        try:
            record, generation = runtime.structured(
                role=role,
                prompt=prompt,
                destination=destination,
                stage=wave_stage,
                schema=schema,
                temperature=temperature,
                max_tokens=max_tokens,
                seed_label=wave_seed,
            )
            metadata = dict(generation["metadata"])
            metadata["v081_transport_waves"] = {
                "accepted_wave": wave,
                "prior_failures": failures,
                "mathematical_request_unchanged": True,
                "repetition_detection_preserved": True,
            }
            return record, {**generation, "metadata": metadata}
        except RuntimeError as error:
            failures.append(f"wave_{wave}: {error}")
    raise RuntimeError(
        f"v0.3.81 structured transport waves exhausted for {stage}: {failures}"
    )


def _memory_failure_record(
    *,
    old_lemma: dict[str, Any],
    challenges: list[dict[str, Any]],
    iteration: int,
    status: str,
    resolved_by_certification: bool,
) -> dict[str, Any]:
    obligations: list[str] = []
    for challenge in challenges:
        for attribution in challenge["attributions"]:
            obligation = str(attribution["failed_obligation"])
            if obligation not in obligations:
                obligations.append(obligation)
    old_id = str(old_lemma["lemma_id"])
    return {
        "failed_id": f"I{iteration}:MEMORY_REVOKED:{old_id}",
        "iteration": iteration,
        "source_claim_id": old_id,
        "status": status,
        "hypothesis": str(old_lemma["statement"]),
        "exact_negation": formal_negation(str(old_lemma["statement"])),
        "earliest_unresolved_transition": str(
            old_lemma["earliest_unresolved_transition"]
        ),
        "local_dependency_map": str(old_lemma["local_dependency_map"]),
        "decisive_failure": " | ".join(obligations)
        or "The stored proof certification was invalidated by a confirmed lemma-level defect.",
        "resolved_by_certification": resolved_by_certification,
        "tombstoned_proof_sha256": sha256_text(str(old_lemma["proof"])),
        "memory_feedback": True,
    }


def _taint_dependent_candidates(
    *,
    candidates: list[dict[str, Any]],
    quarantined_by_label: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    updated: list[dict[str, Any]] = []
    for source in candidates:
        row = copy.deepcopy(source)
        used = set(str(label) for label in row.get("assembly", {}).get("used_labels", []))
        affected = [
            {
                "label": label,
                "lemma_id": str(quarantined_by_label[label]["lemma_id"]),
                "old_proof_sha256": sha256_text(
                    str(quarantined_by_label[label]["proof"])
                ),
                "reason": "cited lemma was quarantined after a confirmed lemma-level defect",
            }
            for label in sorted(used.intersection(quarantined_by_label))
        ]
        if affected:
            row["memory_invalidation"] = affected
            row["fusion_outcome_before_memory_feedback"] = row.get("fusion_outcome")
            row["fusion_outcome"] = "REPAIR_NEEDED"
            row["fusion_defect_packet"] = {
                **dict(row.get("fusion_defect_packet") or {}),
                "memory_invalidation": affected,
            }
            row["fusion_final"] = (
                str(row.get("fusion_final") or "").rstrip()
                + "\n\nMEMORY INVALIDATION NOTICE\n"
                + json.dumps(affected, ensure_ascii=False, indent=2)
            )
        updated.append(row)
    return updated


def run_memory_feedback(
    *,
    runtime: ResilientModelRuntime,
    verifier_runtime: ResilientModelRuntime,
    problem: str,
    post_audited_candidates: list[dict[str, Any]],
    certified_memory: list[dict[str, Any]],
    failed_memory: list[dict[str, Any]],
    iteration: int,
    output_dir: Path,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, Any],
]:
    """Close the audit-to-memory loop before selecting the next two proofs.

    A proof-level defect only challenges a cited lemma. Two fresh Qwen attribution
    calls must independently agree that the defect belongs to the lemma statement or
    stored proof body before the old certification is quarantined.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    labeled = label_verified_lemmas(certified_memory)
    by_label = {
        str(label_row["label"]): certified_memory[index]
        for index, label_row in enumerate(labeled)
    }
    attribution_jobs: list[
        tuple[dict[str, Any], str, dict[str, Any], str, dict[str, Any], int]
    ] = []
    for candidate in post_audited_candidates:
        if not _audit_reports_defect(candidate):
            continue
        for label in candidate.get("assembly", {}).get("used_labels", []):
            label_text = str(label)
            lemma = by_label.get(label_text)
            if lemma is None:
                continue
            for audit_source, defect_packet in _defect_events(candidate):
                for call_index in (1, 2):
                    attribution_jobs.append(
                        (
                            candidate,
                            label_text,
                            lemma,
                            audit_source,
                            defect_packet,
                            call_index,
                        )
                    )

    def attribute(
        job: tuple[
            dict[str, Any], str, dict[str, Any], str, dict[str, Any], int
        ]
    ) -> dict[str, Any]:
        candidate, label, lemma, audit_source, defect_packet, call_index = job
        candidate_id = str(candidate["candidate_id"])
        destination = (
            output_dir
            / "01_attribution"
            / _safe_component(candidate_id)
            / f"lemma_{_safe_component(label)}"
            / _safe_component(audit_source)
        )
        prompt = lemma_defect_attribution_prompt(
            problem=problem,
            lemma={"label": label, **lemma},
            refined_proof=str(candidate["proof"]),
            audit_source=audit_source,
            defect_packet=defect_packet,
        )
        try:
            record, generation = _structured_with_v081_transport_waves(
                runtime=runtime,
                role="qwen",
                prompt=prompt,
                destination=destination,
                stage=f"attribution_{call_index}",
                schema=LEMMA_ATTRIBUTION_SCHEMA,
                temperature=0.1,
                max_tokens=16_384,
                seed_label=(
                    f"v081:i{iteration}:memory_attribution:{candidate_id}:"
                    f"{lemma['lemma_id']}:{audit_source}:{call_index}"
                ),
            )
            transport_failure = None
        except RuntimeError as error:
            transport_failure = f"{type(error).__name__}: {error}"
            record = {
                "stored_body_contains_same_obligation": False,
                "stored_body_obligation_status": "NOT_PRESENT_OR_DIFFERENT",
                "classification": "UNRELATED_OR_UNCERTAIN",
                "failed_obligation": (
                    "No attribution vote was accepted after bounded structured "
                    "transport recovery."
                ),
                "evidence": transport_failure,
            }
            generation = {
                "metadata": {
                    "transport_failure": transport_failure,
                    "accepted_as_mathematical_vote": False,
                    "conservative_fallback": "UNRELATED_OR_UNCERTAIN",
                }
            }
        result = {
            "candidate_id": candidate_id,
            "label": label,
            "lemma_id": str(lemma["lemma_id"]),
            "audit_source": audit_source,
            "call_index": call_index,
            **record,
            "transport_failure": transport_failure,
            "generation": generation["metadata"],
        }
        write_json(destination / f"attribution_{call_index}_result.json", result)
        return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        attribution_rows = list(executor.map(attribute, attribution_jobs))

    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for row in attribution_rows:
        grouped.setdefault(
            (
                str(row["candidate_id"]),
                str(row["label"]),
                str(row["audit_source"]),
            ),
            [],
        ).append(row)

    candidate_by_id = {
        str(row["candidate_id"]): row for row in post_audited_candidates
    }
    body_replay_jobs: list[
        tuple[dict[str, Any], str, dict[str, Any], str, dict[str, Any], int]
    ] = []
    for (candidate_id, label, audit_source), rows in grouped.items():
        if len(rows) != 2 or not all(
            bool(row.get("stored_body_contains_same_obligation")) for row in rows
        ):
            continue
        candidate = candidate_by_id[candidate_id]
        defect_packet = dict(
            candidate.get(
                "qwen_defect_packet"
                if audit_source == "qwen"
                else "fusion_defect_packet"
            )
            or {}
        )
        for call_index in (1, 2):
            body_replay_jobs.append(
                (
                    candidate,
                    label,
                    by_label[label],
                    audit_source,
                    defect_packet,
                    call_index,
                )
            )

    def audit_stored_body(
        job: tuple[
            dict[str, Any], str, dict[str, Any], str, dict[str, Any], int
        ]
    ) -> dict[str, Any]:
        candidate, label, lemma, audit_source, defect_packet, call_index = job
        candidate_id = str(candidate["candidate_id"])
        destination = (
            output_dir
            / "02_body_replay"
            / _safe_component(candidate_id)
            / f"lemma_{_safe_component(label)}"
            / _safe_component(audit_source)
        )
        prompt = lemma_body_replay_prompt(
            problem=problem,
            lemma={"label": label, **lemma},
            audit_source=audit_source,
            defect_packet=defect_packet,
        )
        try:
            record, generation = _structured_with_v081_transport_waves(
                runtime=runtime,
                role="qwen",
                prompt=prompt,
                destination=destination,
                stage=f"body_replay_{call_index}",
                schema=LEMMA_BODY_REPLAY_SCHEMA,
                temperature=0.1,
                max_tokens=16_384,
                seed_label=(
                    f"v081:i{iteration}:body_replay:{candidate_id}:"
                    f"{lemma['lemma_id']}:{audit_source}:{call_index}"
                ),
            )
            transport_failure = None
        except RuntimeError as error:
            transport_failure = f"{type(error).__name__}: {error}"
            record = {
                "same_obligation": False,
                "verdict": "UNCERTAIN",
                "first_break": (
                    "No stored-body replay was accepted after bounded structured "
                    "transport recovery."
                ),
                "verification": transport_failure,
            }
            generation = {
                "metadata": {
                    "transport_failure": transport_failure,
                    "accepted_as_mathematical_vote": False,
                    "conservative_fallback": "UNCERTAIN",
                }
            }
        result = {
            "candidate_id": candidate_id,
            "label": label,
            "lemma_id": str(lemma["lemma_id"]),
            "audit_source": audit_source,
            "call_index": call_index,
            **record,
            "transport_failure": transport_failure,
            "generation": generation["metadata"],
        }
        write_json(destination / f"body_replay_{call_index}_result.json", result)
        return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        body_replay_rows = list(executor.map(audit_stored_body, body_replay_jobs))
    body_grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for row in body_replay_rows:
        body_grouped.setdefault(
            (
                str(row["candidate_id"]),
                str(row["label"]),
                str(row["audit_source"]),
            ),
            [],
        ).append(row)

    lineage_decisions: list[dict[str, Any]] = []
    challenges_by_lemma: dict[str, list[dict[str, Any]]] = {}
    for (candidate_id, label, audit_source), rows in grouped.items():
        rows.sort(key=lambda row: int(row["call_index"]))
        attribution_decision = attribution_consensus(rows)
        replay_rows = body_grouped.get((candidate_id, label, audit_source), [])
        replay_rows.sort(key=lambda row: int(row["call_index"]))
        replay_decision = body_replay_consensus(replay_rows)
        statement_defect = (
            attribution_decision["quarantine"]
            and attribution_decision["scope"] == "LEMMA_STATEMENT_DEFECT"
        )
        quarantine = bool(
            statement_defect or replay_decision["confirmed_body_defect"]
        )
        consensus = {
            "quarantine": quarantine,
            "scope": (
                "LEMMA_STATEMENT_DEFECT"
                if statement_defect
                else "LEMMA_BODY_DEFECT"
                if replay_decision["confirmed_body_defect"]
                else "NO_LEMMA_QUARANTINE"
            ),
            "attribution": attribution_decision,
            "body_replay": replay_decision,
        }
        decision = {
            "candidate_id": candidate_id,
            "label": label,
            "lemma_id": str(by_label[label]["lemma_id"]),
            "audit_source": audit_source,
            "attributions": rows,
            "body_replay_audits": replay_rows,
            "consensus": consensus,
        }
        lineage_decisions.append(decision)
        if not consensus["quarantine"]:
            continue
        candidate = candidate_by_id[candidate_id]
        defect_packet = dict(
            candidate.get(
                "qwen_defect_packet"
                if audit_source == "qwen"
                else "fusion_defect_packet"
            )
            or {}
        )
        challenges_by_lemma.setdefault(str(by_label[label]["lemma_id"]), []).append(
            {
                **decision,
                "defect_source": audit_source,
                "defect_packet": defect_packet,
                "refined_proof": str(candidate["proof"]),
                "refined_proof_sha256": str(candidate["proof_sha256"]),
            }
        )
    write_json(
        output_dir / "01_attribution" / "summary.json",
        {
            "policy": (
                "source_isolated_two_call_association_then_two_call_stored_body_replay"
            ),
            "attribution_job_count": len(attribution_rows),
            "body_replay_job_count": len(body_replay_rows),
            "lineages": lineage_decisions,
        },
    )

    old_by_id = {str(row["lemma_id"]): row for row in certified_memory}
    quarantined_ids = set(challenges_by_lemma)
    quarantined_by_label = {
        label: lemma
        for label, lemma in by_label.items()
        if str(lemma["lemma_id"]) in quarantined_ids
    }

    pinned_gemma = ResilientModelRuntime(
        RuntimeConfig(
            gemma_endpoint=runtime.config.gemma_endpoint,
            qwen_endpoint=runtime.config.gemma_endpoint,
            gemma_model=runtime.config.gemma_model,
            qwen_model=runtime.config.gemma_model,
            master_seed=runtime.config.master_seed,
        )
    )

    def revise(lemma_id: str) -> dict[str, Any]:
        lemma = old_by_id[lemma_id]
        destination = output_dir / "03_revision" / _safe_component(lemma_id)
        record, generation = pinned_gemma.structured(
            role="gemma",
            prompt=lemma_revision_prompt(
                problem=problem,
                lemma=lemma,
                challenges=challenges_by_lemma[lemma_id],
            ),
            destination=destination,
            stage="revision",
            schema=LEMMA_REVISION_SCHEMA,
            temperature=0.4,
            max_tokens=32_768,
            seed_label=f"v081:i{iteration}:memory_revision:{lemma_id}",
        )
        result = {
            "old_lemma_id": lemma_id,
            **record,
            "generation": generation["metadata"],
        }
        write_json(destination / "result.json", result)
        return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        revision_rows = list(executor.map(revise, sorted(quarantined_ids)))

    pairs: list[dict[str, str]] = []
    revision_by_claim: dict[str, dict[str, Any]] = {}
    revision_errors: dict[str, str] = {}
    for revision in revision_rows:
        old_id = str(revision["old_lemma_id"])
        if revision["decision"] == "CANNOT_REPAIR":
            continue
        try:
            validated = validate_and_repair_negations(
                runtime=runtime,
                problem=problem,
                hypotheses={
                    "hypotheses": [
                        {
                            "conjecture": str(revision["revised_statement"]),
                            "exact_negation": str(revision["exact_negation"]),
                            "earliest_unresolved_transition": str(
                                revision["earliest_unresolved_transition"]
                            ),
                            "local_dependency_map": str(
                                revision["local_dependency_map"]
                            ),
                        }
                    ]
                },
                arm=f"memory_feedback_{_safe_component(old_id)}",
                round_number=iteration,
                output_dir=output_dir / "04_fresh_certification" / "negation",
            )
            pair = validated[0]
            pairs.append(pair)
            revision_by_claim[str(pair["claim_id"])] = revision
        except Exception as error:
            revision_errors[old_id] = f"{type(error).__name__}: {error}"

    verified: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    if pairs:
        verified, unresolved = prove_pairs(
            runtime=runtime,
            verifier_runtime=verifier_runtime,
            problem=problem,
            pairs=pairs,
            output_dir=output_dir / "04_fresh_certification" / "proofs",
        )
    write_json(
        output_dir / "04_fresh_certification" / "summary.json",
        {
            "pairs": pairs,
            "verified": verified,
            "unresolved": unresolved,
            "negation_validation_errors": revision_errors,
        },
    )

    verified_by_old: dict[str, dict[str, Any]] = {}
    for row in verified:
        revision = revision_by_claim.get(str(row["lemma_id"]))
        if revision is not None:
            verified_by_old[str(revision["old_lemma_id"])] = row

    active = [
        copy.deepcopy(row)
        for row in certified_memory
        if str(row["lemma_id"]) not in quarantined_ids
    ]
    new_positive: list[dict[str, Any]] = []
    failure_additions: list[dict[str, Any]] = []
    archive: list[dict[str, Any]] = []
    for old_id in sorted(quarantined_ids):
        old = old_by_id[old_id]
        revision = next(row for row in revision_rows if row["old_lemma_id"] == old_id)
        certified = verified_by_old.get(old_id)
        positive = certified is not None and certified.get("direction") == "positive"
        same_statement = positive and normalized(str(certified["statement"])) == normalized(
            str(old["statement"])
        )
        if positive:
            replacement = copy.deepcopy(certified)
            replacement["supersedes_lemma_id"] = old_id
            replacement["memory_revision_iteration"] = iteration
            replacement["memory_revision_decision"] = revision["decision"]
            replacement["quarantined_proof_sha256"] = sha256_text(str(old["proof"]))
            new_positive.append(replacement)
            disposition = "superseded_by_fresh_certification"
        else:
            disposition = "revoked_after_failed_recertification"

        statement_scope = any(
            challenge["consensus"]["scope"] == "LEMMA_STATEMENT_DEFECT"
            for challenge in challenges_by_lemma[old_id]
        )
        status = "TOO_BROAD" if statement_scope else "PROOF_INVALIDATED"
        revision_matches_old = normalized(str(revision["revised_statement"])) == normalized(
            str(old["statement"])
        )
        if (
            certified is not None
            and certified.get("direction") == "negative"
            and revision_matches_old
        ):
            status = "REFUTED"
        failure_additions.append(
            _memory_failure_record(
                old_lemma=old,
                challenges=challenges_by_lemma[old_id],
                iteration=iteration,
                status=status,
                resolved_by_certification=bool(same_statement),
            )
        )
        if (
            certified is not None
            and certified.get("direction") == "negative"
            and not revision_matches_old
        ):
            failure_additions.append(
                {
                    "failed_id": f"I{iteration}:MEMORY_REVISION_REFUTED:{old_id}",
                    "iteration": iteration,
                    "source_claim_id": str(certified["lemma_id"]),
                    "status": "REFUTED",
                    "hypothesis": str(revision["revised_statement"]),
                    "exact_negation": str(certified["statement"]),
                    "earliest_unresolved_transition": str(
                        revision["earliest_unresolved_transition"]
                    ),
                    "local_dependency_map": str(revision["local_dependency_map"]),
                    "decisive_failure": "Fresh paired certification established the negative polarity.",
                    "resolved_by_certification": False,
                    "memory_feedback": True,
                }
            )
        archive.append(
            {
                "old_lemma": old,
                "old_proof_sha256": sha256_text(str(old["proof"])),
                "challenges": challenges_by_lemma[old_id],
                "revision": revision,
                "fresh_certification": certified,
                "disposition": disposition,
            }
        )

    active, insertion_audit = extend_shared_verified_exact(
        existing_verified=active,
        salvage_verified=new_positive,
        output_dir=output_dir / "05_memory_update" / "certified_insertion",
    )
    updated_failed, failed_insertion_audit = _insert_failed_exact(
        failed_memory, failure_additions
    )
    active_statements = {normalized(str(row["statement"])) for row in active}
    for row in updated_failed:
        if normalized(str(row["hypothesis"])) in active_statements:
            row["resolved_by_certification"] = True
            row.setdefault("resolved_iteration", iteration)
    tainted = _taint_dependent_candidates(
        candidates=post_audited_candidates,
        quarantined_by_label=quarantined_by_label,
    )
    write_json(output_dir / "05_memory_update" / "revoked_lemma_archive.json", archive)
    write_json(output_dir / "05_memory_update" / "certified_memory.json", {"verified": active})
    write_json(output_dir / "05_memory_update" / "failed_memory.json", {"failed": updated_failed})
    write_json(output_dir / "05_memory_update" / "tainted_candidates.json", tainted)
    summary = {
        "attribution_job_count": len(attribution_rows),
        "body_replay_job_count": len(body_replay_rows),
        "attribution_event_count": len(lineage_decisions),
        "quarantined_lemma_ids": sorted(quarantined_ids),
        "quarantined_labels": sorted(quarantined_by_label),
        "revision_count": len(revision_rows),
        "fresh_pair_count": len(pairs),
        "fresh_verified_count": len(verified),
        "fresh_positive_insert_count": len(new_positive),
        "certified_memory_count": len(active),
        "failed_memory_count": len(updated_failed),
        "tainted_candidate_ids": [
            str(row["candidate_id"]) for row in tainted if row.get("memory_invalidation")
        ],
        "certified_insertion_audit": insertion_audit,
        "failed_insertion_audit": failed_insertion_audit,
    }
    write_json(output_dir / "summary.json", summary)
    return active, updated_failed, tainted, summary


def run_selection(
    *,
    runtime: ResilientModelRuntime,
    problem: str,
    post_audited_candidates: list[dict[str, Any]],
    output_dir: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Use v0.3.66 evidence extraction and all-15-pair selection."""
    tracks = [
        {
            "track_id": str(row["candidate_id"]),
            # Both slots deliberately contain the refined proof: the selector may
            # choose a version label, but cannot silently revert the refinement.
            "original_proof": str(row["proof"]),
            "fusion_diagnostic": str(row["fusion_final"]),
            "resolver_change_record": json.dumps(
                {
                    "qwen_defect_packet": row["qwen_defect_packet"],
                    "fusion_defect_packet": row["fusion_defect_packet"],
                },
                ensure_ascii=False,
                indent=2,
            ),
            "resolved_proof": str(row["proof"]),
        }
        for row in post_audited_candidates
    ]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        track_results = list(
            executor.map(
                lambda track: v066.audit_track(
                    runtime=runtime,
                    problem=problem,
                    track=track,
                    output_dir=output_dir,
                ),
                tracks,
            )
        )
    order = {track["track_id"]: index for index, track in enumerate(tracks)}
    track_results.sort(key=lambda row: order[str(row["track_id"])])
    selection_result = v066.select_pair_and_roles(
        runtime=runtime,
        problem=problem,
        track_results=track_results,
        output_dir=output_dir,
    )
    selection = selection_result["selection"]
    by_id = {
        str(row["candidate_id"]): row for row in post_audited_candidates
    }
    chosen: list[dict[str, Any]] = []
    for role in ("anchor", "supplement"):
        selected = selection[role]
        candidate_id = str(selected["track_id"])
        row = by_id[candidate_id]
        selected_path = output_dir / "selected_proofs" / f"{role}.md"
        selected_path.parent.mkdir(parents=True, exist_ok=True)
        selected_path.write_text(str(row["proof"]).strip() + "\n", encoding="utf-8")
        chosen.append(
            {
                **row,
                "role": role,
                "selected_version_label": selected["version"],
                "selected_proof_path": str(selected_path.resolve()),
                "selection_reason": selected.get("selection_reason"),
            }
        )
    summary = {
        "selection": selection,
        "selected": [
            {
                "candidate_id": row["candidate_id"],
                "role": row["role"],
                "proof_path": row["selected_proof_path"],
                "proof_sha256": row["proof_sha256"],
                "qwen_outcome": row["qwen_outcome"],
                "fusion_outcome": row["fusion_outcome"],
            }
            for row in chosen
        ],
    }
    write_json(output_dir / "summary.json", summary)
    return chosen, summary


def build_manifest(
    *,
    initial_state: dict[str, Any],
    source_run_dir: Path,
    runtime_config: RuntimeConfig,
    salvage_verifier_endpoint: str,
) -> dict[str, Any]:
    return {
        "schema": "cognitive-well-v081-iterative-dual-memory-loop-manifest-v1",
        "harness_version": HARNESS_VERSION,
        "created_at": utc_now(),
        "problem_id": initial_state["problem_id"],
        "problem_sha256": sha256_text(str(initial_state["problem"])),
        "source_run_dir": str(source_run_dir.resolve()),
        "source_proofs": [
            {
                "candidate_id": row["candidate_id"],
                "role": row["role"],
                "proof_path": row["proof_path"],
                "proof_sha256": row["proof_sha256"],
                "qwen_result_path": row["qwen_result_path"],
                "fusion_result_path": row["fusion_result_path"],
            }
            for row in initial_state["candidate_proofs"]
        ],
        "iteration_count": ITERATION_COUNT,
        "iteration_flow": [
            "three_unconditional_hypothesis_extractions",
            "exact_novelty_gate_plus_unanimous_failed_semantic_comparison",
            "negation_validation_and_paired_certification",
            "failure_salvage_then_one_singleton_atomic_child_retry",
            "exact_only_certified_memory_insertion_and_failed_memory_update",
            "six_proof_synthesis_candidates",
            "three_reviews_and_revised_fusion",
            "one_high_stakes_full_replacement_refinement",
            "fresh_three_reviews_and_revised_fusion",
            "audit_attribution_quarantine_revision_and_fresh_recertification",
            "dependent_proof_invalidation_and_closed_loop_memory_update",
            "six_to_two_distinct_portfolio_selection",
        ],
        "hypothesis_extraction": {
            "model": runtime_config.gemma_model,
            "endpoint": runtime_config.gemma_endpoint,
            "schedule": list(EXTRACTION_SCHEDULE),
            "reasoning_effort": "max",
            "max_tokens": 32_768,
        },
        "failed_memory": {
            "statuses": [
                "REFUTED",
                "PROOF_FAILED",
                "VERIFIER_CONFLICT",
                "TOO_BROAD",
                "PROOF_INVALIDATED",
            ],
            "exact_duplicate_gate": "deterministic",
            "semantic_comparator": {
                "model": runtime_config.qwen_model,
                "calls": 2,
                "temperature": 0.1,
                "rejection_rule": "unanimous_SAME_FAILED_HYPOTHESIS_only",
            },
            "visible_to_synthesis": False,
        },
        "certified_memory": {
            "insertion_dedup": "exact_only",
            "semantic_dedup_model_calls": 0,
            "cumulative_across_iterations": True,
        },
        "synthesis": {
            "model": runtime_config.gemma_model,
            "temperature": 0.4,
            "max_tokens": 32_768,
            "candidate_configs": list(SYNTHESIS_CONFIGS),
        },
        "review_and_refinement": {
            "reviewer_1": "Gemma4-31B_t0.4_earliest_break",
            "reviewer_2": "Qwen3.6-27B_t0.2_adversarial",
            "reviewer_3": "Gemma4-31B_t0.2_charitable",
            "fusion": "Gemma4-31B_t0.4_revised_fusion",
            "refinement": "Gemma4-31B_t0.4_high_stakes_full_replacement",
            "packets_kept_separate": True,
        },
        "audit_to_memory_feedback": {
            "trigger": "qwen_or_fusion_reports_defect",
            "attribution_model": runtime_config.qwen_model,
            "defect_packets": "source_isolated_never_mixed",
            "attribution_calls_per_candidate_lemma_defect_source": 2,
            "stored_body_replay_calls_after_unanimous_association": 2,
            "quarantine_rule": (
                "unanimous_statement_defect_or_unanimous_stored_body_replay_fail"
            ),
            "revision_model": runtime_config.gemma_model,
            "revision_temperature": 0.4,
            "recertification": "fresh_positive_and_negative_proofs_plus_split_verifier",
            "old_proof_policy": "tombstone_and_invalidate_dependent_syntheses",
        },
        "split_verifier": {
            "model": runtime_config.gemma_model,
            "endpoint": salvage_verifier_endpoint.rstrip("/"),
            "alignment_calls": 2,
            "alignment_rule": "unanimous",
            "validity_calls_after_alignment": 1,
            "temperature": 0.1,
            "max_tokens": 32_768,
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
    run_input = {
        "problem_id": initial_state["problem_id"],
        "problem": initial_state["problem"],
    }
    problem = str(initial_state["problem"])
    current_proofs = list(initial_state["candidate_proofs"])
    certified_memory: list[dict[str, Any]] = []
    failed_memory: list[dict[str, Any]] = []
    iteration_summaries: list[dict[str, Any]] = []
    try:
        for iteration in range(1, ITERATION_COUNT + 1):
            iteration_dir = output_dir / f"iteration_{iteration}"

            _status(output_dir, "hypothesis_extraction", iteration=iteration)
            extraction_results = run_extraction(
                runtime=runtime,
                problem=problem,
                candidate_proofs=current_proofs,
                certified_memory=certified_memory,
                failed_memory=failed_memory,
                iteration=iteration,
                output_dir=iteration_dir / "01_hypothesis_extraction",
            )

            _status(output_dir, "novelty_gate", iteration=iteration)
            accepted, novelty_audit = novelty_gate(
                runtime=runtime,
                extraction_results=extraction_results,
                certified_memory=certified_memory,
                failed_memory=failed_memory,
                iteration=iteration,
                output_dir=iteration_dir / "02_novelty_gate",
            )

            _status(
                output_dir,
                "hypothesis_certification_and_salvage",
                iteration=iteration,
                accepted_hypothesis_count=len(accepted),
            )
            certified_memory, failed_memory, certification = (
                run_certification_and_memory(
                    proof_runtime=runtime,
                    verifier_runtime=verifier_runtime,
                    runtime_config=runtime_config,
                    salvage_verifier_endpoint=salvage_verifier_endpoint,
                    problem=problem,
                    candidate_proofs=current_proofs,
                    accepted_hypotheses=accepted,
                    certified_memory=certified_memory,
                    failed_memory=failed_memory,
                    iteration=iteration,
                    output_dir=iteration_dir / "03_certification_salvage_memory",
                )
            )

            _status(
                output_dir,
                "six_candidate_synthesis",
                iteration=iteration,
                certified_memory_count=len(certified_memory),
                failed_memory_count=len(failed_memory),
            )
            synthesized = run_synthesis(
                runtime=runtime,
                problem=problem,
                candidate_proofs=current_proofs,
                certified_memory=certified_memory,
                iteration=iteration,
                output_dir=iteration_dir / "04_synthesis",
            )

            _status(output_dir, "pre_refinement_reviews_and_fusion", iteration=iteration)
            pre_audited = run_review_fusion(
                run_input=run_input,
                candidates=synthesized,
                gemma_endpoint=runtime_config.gemma_endpoint,
                qwen_endpoint=runtime_config.qwen_endpoint,
                output_dir=iteration_dir / "05_pre_refinement_audit",
            )

            _status(output_dir, "high_stakes_refinement", iteration=iteration)
            refined = run_refinement(
                runtime=runtime,
                problem=problem,
                audited_candidates=pre_audited,
                iteration=iteration,
                output_dir=iteration_dir / "06_refinement",
            )

            _status(output_dir, "post_refinement_reviews_and_fusion", iteration=iteration)
            post_audited = run_review_fusion(
                run_input=run_input,
                candidates=refined,
                gemma_endpoint=runtime_config.gemma_endpoint,
                qwen_endpoint=runtime_config.qwen_endpoint,
                output_dir=iteration_dir / "07_post_refinement_audit",
            )

            _status(output_dir, "audit_to_memory_feedback", iteration=iteration)
            certified_memory, failed_memory, post_audited, memory_feedback = (
                run_memory_feedback(
                    runtime=runtime,
                    verifier_runtime=verifier_runtime,
                    problem=problem,
                    post_audited_candidates=post_audited,
                    certified_memory=certified_memory,
                    failed_memory=failed_memory,
                    iteration=iteration,
                    output_dir=iteration_dir / "08_memory_feedback",
                )
            )

            _status(output_dir, "six_to_two_selection", iteration=iteration)
            current_proofs, selection = run_selection(
                runtime=runtime,
                problem=problem,
                post_audited_candidates=post_audited,
                output_dir=iteration_dir / "09_selection",
            )
            iteration_summary = {
                "iteration": iteration,
                "extracted_hypothesis_count": sum(
                    len(row["record"]["hypotheses"])
                    for row in extraction_results
                ),
                "novelty_accepted_count": len(accepted),
                "novelty_rejected_count": len(novelty_audit) - len(accepted),
                "certification": certification,
                "certified_memory_count": len(certified_memory),
                "failed_memory_count": len(failed_memory),
                "pre_fusion_outcomes": dict(
                    Counter(str(row["fusion_outcome"]) for row in pre_audited)
                ),
                "post_fusion_outcomes": dict(
                    Counter(str(row["fusion_outcome"]) for row in post_audited)
                ),
                "memory_feedback": memory_feedback,
                "selection": selection,
            }
            write_json(iteration_dir / "summary.json", iteration_summary)
            write_json(
                iteration_dir / "memory_snapshot.json",
                {"certified": certified_memory, "failed": failed_memory},
            )
            iteration_summaries.append(iteration_summary)

        summary = {
            "schema": "cognitive-well-v081-iterative-dual-memory-loop-summary-v1",
            "harness_version": HARNESS_VERSION,
            "state": "completed",
            "completed_at": utc_now(),
            "iteration_count": ITERATION_COUNT,
            "certified_memory_count": len(certified_memory),
            "failed_memory_count": len(failed_memory),
            "final_certified_memory_path": str(
                (output_dir / "final_certified_memory.json").resolve()
            ),
            "final_failed_memory_path": str(
                (output_dir / "final_failed_memory.json").resolve()
            ),
            "final_selected_proofs": [
                {
                    "candidate_id": row["candidate_id"],
                    "role": row["role"],
                    "proof_path": row["proof_path"],
                    "proof_sha256": row["proof_sha256"],
                    "qwen_outcome": row["qwen_outcome"],
                    "fusion_outcome": row["fusion_outcome"],
                }
                for row in current_proofs
            ],
            "iterations": iteration_summaries,
            "proof_runtime_recovery_events": runtime.recovery_events(),
            "verifier_runtime_recovery_events": verifier_runtime.recovery_events(),
        }
        write_json(
            output_dir / "final_certified_memory.json",
            {"verified": certified_memory},
        )
        write_json(
            output_dir / "final_failed_memory.json", {"failed": failed_memory}
        )
        write_json(output_dir / "summary.json", summary)
        write_json(
            output_dir / "status.json",
            {
                "state": "completed",
                "stage": "two_iteration_loop_complete",
                "certified_memory_count": len(certified_memory),
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
