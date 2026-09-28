from __future__ import annotations

import hashlib
import json
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable, Iterable

from cognitive_well_harness_v0_3_49_reviewer1_temperature_ablation_20260823.protocol import (
    parse_review,
    review_user_prompt,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import (
    RuntimeConfig,
    write_json,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.pipeline import (
    utc_now,
)
from cognitive_well_harness_v0_3_79_modular_singleton_atomic_retry_20260825.runtime import (
    ResilientModelRuntime,
)
from cognitive_well_harness_v0_3_83_batched_dependency_dag_20260826.run_gemma_trace_gap_extractor import (
    COMPACT_TRACE_GAP_SCHEMA,
    TRACE_GAP_SCHEMA,
    TRACE_GAP_SYSTEM_PROMPT,
    compact_trace_gap_user_prompt,
    materialize_compact_record,
    trace_gap_user_prompt,
    validate_source_binding,
)
from cognitive_well_harness_v0_3_83_batched_dependency_dag_20260826.run_reviewer1_thinking_augmentation import (
    reviewer1_system_prompt,
)

from . import HARNESS_VERSION


MODEL = "google/gemma-4-31B-it"
PASS_SENTINELS = {
    "NO_FIRST_BREAK",
    "NO_ADVERSARIAL_BREAK",
    "NO_UNCLOSED_OBLIGATION_FOUND",
    "PROOF_CERTIFIED",
}


TRACE_RESOLUTION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["decisions", "summary"],
    "properties": {
        "decisions": {
            "type": "array",
            "minItems": 0,
            "maxItems": 12,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "gap_id",
                    "decision",
                    "mathematical_status",
                    "source_credit",
                    "reason_code",
                ],
                "properties": {
                    "gap_id": {"type": "string", "pattern": "^(TG|CG)[0-9]+$"},
                    "decision": {
                        "type": "string",
                        "enum": ["USE", "DISCARD", "REPAIR"],
                    },
                    "mathematical_status": {
                        "type": "string",
                        "enum": [
                            "VALID_AND_MISSING",
                            "VALID_BUT_PRESENT_OR_ROUTINE",
                            "INVALID",
                            "INCOMPLETE_BUT_REPAIRABLE",
                            "UNCERTAIN",
                        ],
                    },
                    "source_credit": {
                        "type": "string",
                        "enum": ["TRACE_RECOVERED", "PROVER_NEW", "NO_CREDIT"],
                    },
                    "reason_code": {
                        "type": "string",
                        "enum": [
                            "TRACE_SUPPLIES_VALID_MISSING_ARGUMENT",
                            "TRACE_ONLY_VERIFIES_EXISTING_MATERIAL",
                            "TRACE_ARGUMENT_INVALID",
                            "TRACE_DIAGNOSIS_VALID_REPAIR_NOT_SUPPLIED",
                            "UNCERTAIN",
                        ],
                    },
                },
            },
        },
        "summary": {"type": "string", "minLength": 1},
    },
}


TRACE_RESOLUTION_SYSTEM_PROMPT = r"""You are a conservative olympiad prover acting
as a provenance-aware filter between a reviewer's private reasoning trace and a
submitted proof.

For every source-bound trace item, independently check the original problem, the
complete submitted proof, and the trace record. Classify it exactly once:

- USE: the trace itself contains a valid, non-routine argument missing from the proof.
- DISCARD: the item is false, uncertain, redundant, already explicit in the proof, or
  merely routine elaboration.
- REPAIR: the trace correctly exposes a genuine omission, but its proposed argument is
  invalid or incomplete; you can supply a rigorous localized replacement yourself.

Do not turn a plausible direction into USE. Do not credit the trace with mathematics
that you supplied. USE must have source_credit TRACE_RECOVERED. REPAIR must have
source_credit PROVER_NEW and means a later integration prover—not this record—must
construct the missing argument independently. DISCARD must have source_credit
NO_CREDIT. If uncertain, DISCARD.

Return one decision for every supplied gap_id, in the same order, and only the required
JSON object.

HIGH-STAKES DELIBERATION REQUIREMENT

Spare no effort. Use the maximum reasoning effort available. Re-check every
load-bearing transition before returning the record."""


COMPACT_TRACE_RESOLUTION_SYSTEM_PROMPT = TRACE_RESOLUTION_SYSTEM_PROMPT + r"""

TRANSPORT FALLBACK

Return no JSON and no prose. Return exactly one line per supplied gap, in the supplied
order, using five pipe-delimited fields:

gap_id|decision|mathematical_status|source_credit|reason_code

Use only enum values from the original task. Do not use Markdown fences."""


TRACE_INTEGRATION_SYSTEM_PROMPT = r"""You are a rigorous olympiad proof rewriter.

Rewrite the submitted proof as one complete self-contained solution to the original
problem. You receive a short provenance-resolved packet. USE entries are arguments
recovered from a reviewer trace and independently accepted by a prover. REPAIR entries
are new arguments independently constructed by that prover. Incorporate only those
accepted entries, at their source-bound proof locations, and update every affected
downstream use.

Do not include discarded trace material. Do not invent additional assumptions or
silently strengthen a claim. Preserve correct material, notation, and LaTeX as closely
as possible. Return the complete replacement proof from the beginning. It must not
mention traces, reviewers, decisions, repairs, models, or this workflow. If the
accepted packet cannot be integrated rigorously, retain the strongest correct proof
and state its first unresolved gap. Return only the proof.

HIGH-STAKES DELIBERATION REQUIREMENT

Spare no effort. Use the maximum reasoning effort available. Re-check every
load-bearing transition before returning the proof."""


IMPLICIT_TRACE_RESOLVER_SYSTEM_PROMPT = r"""You are a rigorous olympiad proof
resolver. Rewrite the submitted proof as one complete, self-contained solution to the
original problem.

You receive source-bound candidates extracted from one or more reviewer reasoning
traces. They are untrusted diagnostic material, not established facts. During your
private reasoning, independently evaluate every candidate in the context of the full
proof:

- use a trace argument only if it is mathematically valid, non-routine, missing from
  the submitted proof, and needed by a downstream conclusion;
- ignore false, circular, uncertain, redundant, or merely routine trace material;
- when a trace exposes a genuine gap but does not supply a valid repair, construct a
  rigorous replacement yourself if possible;
- update the affected proof region and every dependent use as one mathematical object.

Do not output a decision table or discuss which candidates you accepted. Return only
the complete replacement proof. It must not mention traces, reviewers, diagnostics,
repairs, models, or this workflow. Preserve correct material, notation, and LaTeX as
closely as possible. If no candidate supplies or exposes a genuine gap requiring a
change, reproduce the submitted proof verbatim. If the theorem cannot be completed,
state the strongest rigorous partial conclusion and its first unresolved gap.

HIGH-STAKES DELIBERATION REQUIREMENT

Spare no effort. Use the maximum reasoning effort available. Do not finalize merely
because a familiar argument or plausible conclusion has been found. Re-check every
load-bearing transition before returning the proof."""


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def parse_review_input(value: str) -> tuple[str, str]:
    problem_header = "## OLYMPIAD PROBLEM"
    proof_header = "## CANDIDATE PROOF"
    allowed_header = "## ALLOWED ESTABLISHED MATERIAL"
    if value.count(problem_header) != 1 or value.count(proof_header) != 1:
        raise ValueError("review prompt does not contain one problem and proof section")
    after_problem = value.split(problem_header, 1)[1]
    problem, after_proof = after_problem.split(proof_header, 1)
    proof = after_proof.split(allowed_header, 1)[0]
    problem, proof = problem.strip(), proof.strip()
    if not problem or not proof:
        raise ValueError("parsed problem or proof is empty")
    return problem, proof


def normalized_reviewer_verdict(value: str) -> str:
    first_line = value.strip().splitlines()[0].strip() if value.strip() else ""
    return "NO_FIRST_BREAK" if first_line in PASS_SENTINELS else "FIRST_BREAK"


def load_corpus(*, root: Path, corpus_path: Path) -> list[dict[str, Any]]:
    payload = json.loads(corpus_path.read_text(encoding="utf-8"))
    seen: set[str] = set()
    rows: list[dict[str, Any]] = []
    for raw in payload.get("cases") or []:
        case_id = str(raw.get("case_id") or "").strip()
        if not case_id or case_id in seen:
            raise ValueError(f"missing or duplicate case_id: {case_id!r}")
        seen.add(case_id)
        paths = {
            key: (root / str(raw[key])).resolve()
            for key in ("user_prompt", "reasoning", "reviewer_final")
        }
        for key, path in paths.items():
            if not path.is_file():
                raise FileNotFoundError(f"{case_id} missing {key}: {path}")
        problem, proof = parse_review_input(
            paths["user_prompt"].read_text(encoding="utf-8")
        )
        reasoning = paths["reasoning"].read_text(encoding="utf-8").strip()
        final = paths["reviewer_final"].read_text(encoding="utf-8").strip()
        if not reasoning or not final:
            raise ValueError(f"{case_id} has empty reasoning or final review")
        collected_cards: list[dict[str, Any]] = []
        trace_lines = reasoning.splitlines()
        proof_lines = [line.strip() for line in proof.splitlines() if line.strip()]
        for index, span in enumerate(raw.get("collected_trace_spans") or [], start=1):
            start, end = int(span["start_line"]), int(span["end_line"])
            if start < 1 or end < start or end > len(trace_lines):
                raise ValueError(
                    f"{case_id} collected span {index} is outside the reasoning trace"
                )
            trace_evidence = "\n".join(trace_lines[start - 1 : end]).strip()
            search = str(span["proof_search"]).strip()
            locations = [line for line in proof_lines if search.lower() in line.lower()]
            if not locations:
                raise ValueError(
                    f"{case_id} collected span {index} proof_search not found: {search!r}"
                )
            collected_cards.append(
                {
                    "gap_id": f"CG{index}",
                    "proof_location": locations[0],
                    "claim": (
                        "Determine whether this collected trace segment contains a valid "
                        "non-routine proof contribution absent from the submitted proof."
                    ),
                    "trace_evidence": trace_evidence,
                    "missing_detail": (
                        "Independently classify the segment as usable, discardable, or "
                        "repairable; no validity label is supplied."
                    ),
                    "later_trace_disposition": (
                        "The segment was retained only as a candidate for this blinded "
                        "resolution experiment."
                    ),
                    "support_origin": "COLLECTED_TRACE_CANDIDATE",
                    "recoverability": "UNKNOWN",
                    "dependency_impact": "UNKNOWN",
                    "report_even_if_final_pass": True,
                    "source_line_range": [start, end],
                }
            )
        rows.append(
            {
                **raw,
                "paths": {key: str(path) for key, path in paths.items()},
                "problem": problem,
                "proof": proof,
                "reasoning": reasoning,
                "reviewer_final_text": final,
                "normalized_source_verdict": normalized_reviewer_verdict(final),
                "proof_sha256": sha256_text(proof),
                "reasoning_sha256": sha256_text(reasoning),
                "collected_trace_cards": collected_cards,
            }
        )
    if not rows:
        raise ValueError("corpus is empty")
    return rows


def resolution_input_gaps(
    *, case: dict[str, Any], extraction: dict[str, Any]
) -> list[dict[str, Any]]:
    model_gaps = [dict(row) for row in extraction.get("gaps") or []]
    collected = [dict(row) for row in case.get("collected_trace_cards") or []]
    # The curated cards guarantee experimental coverage when the generative extractor
    # misses a known trace segment. They carry no expected validity label. Exact trace
    # duplicates are removed so a correctly extracted segment is not voted twice.
    seen_trace = {sha256_text(str(row.get("trace_evidence") or "")) for row in model_gaps}
    merged = list(model_gaps)
    next_id = 1
    for row in collected:
        digest = sha256_text(str(row["trace_evidence"]))
        if digest in seen_trace:
            continue
        while any(str(existing["gap_id"]) == f"CG{next_id}" for existing in merged):
            next_id += 1
        row["gap_id"] = f"CG{next_id}"
        next_id += 1
        merged.append(row)
        seen_trace.add(digest)
    return merged


def runtime_for(
    endpoint: str, seed: int, model: str = MODEL
) -> ResilientModelRuntime:
    return ResilientModelRuntime(
        RuntimeConfig(
            gemma_endpoint=endpoint.rstrip("/"),
            qwen_endpoint=endpoint.rstrip("/"),
            gemma_model=model,
            qwen_model=model,
            master_seed=seed,
        )
    )


def validate_resolution(
    *, record: dict[str, Any], gaps: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    expected = [str(gap["gap_id"]) for gap in gaps]
    actual = [str(row["gap_id"]) for row in record["decisions"]]
    if actual != expected:
        raise ValueError(f"resolution IDs/order changed: expected {expected}, got {actual}")
    decisions: list[dict[str, Any]] = []
    for row in record["decisions"]:
        decision = str(row["decision"])
        credit = str(row["source_credit"])
        expected_credit = {
            "USE": "TRACE_RECOVERED",
            "REPAIR": "PROVER_NEW",
            "DISCARD": "NO_CREDIT",
        }[decision]
        if credit != expected_credit:
            raise ValueError(f"{row['gap_id']} has inconsistent source credit")
        decisions.append(dict(row))
    return decisions


def parse_compact_resolution(
    *, text: str, gaps: list[dict[str, Any]]
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for raw in text.strip().splitlines():
        line = raw.strip()
        if not line or line.startswith("```"):
            continue
        parts = [part.strip() for part in line.split("|")]
        if len(parts) != 5:
            raise ValueError(f"invalid compact resolution line: {line!r}")
        gap_id, decision, status, credit, reason_code = parts
        rows.append(
            {
                "gap_id": gap_id,
                "decision": decision,
                "mathematical_status": status,
                "source_credit": credit,
                "reason_code": reason_code,
            }
        )
    record = {
        "decisions": rows,
        "summary": "Compact transport fallback; see per-gap provenance codes.",
    }
    validate_resolution(record=record, gaps=gaps)
    return record


def trace_resolution_user_prompt(
    *, problem: str, proof: str, gaps: list[dict[str, Any]]
) -> str:
    return (
        "# ORIGINAL PROBLEM\n\n"
        + problem.strip()
        + "\n\n# COMPLETE SUBMITTED PROOF\n\n"
        + proof.strip()
        + "\n\n# SOURCE-BOUND TRACE ITEMS\n\n"
        + json.dumps(gaps, ensure_ascii=False, indent=2)
        + "\n\nClassify every trace item now.\n"
    )


def trace_integration_user_prompt(
    *, problem: str, proof: str, accepted: list[dict[str, Any]], gaps: list[dict[str, Any]]
) -> str:
    gap_by_id = {str(gap["gap_id"]): gap for gap in gaps}
    packet = [
        {
            "gap_id": row["gap_id"],
            "decision": row["decision"],
            "source_credit": row["source_credit"],
            "source_bound_proof_location": gap_by_id[str(row["gap_id"])][
                "proof_location"
            ],
            "resolution_reason_code": row["reason_code"],
            "trace_claim": gap_by_id[str(row["gap_id"])]["claim"],
            "trace_evidence": gap_by_id[str(row["gap_id"])]["trace_evidence"],
            "missing_detail": gap_by_id[str(row["gap_id"])]["missing_detail"],
            "later_trace_disposition": gap_by_id[str(row["gap_id"])][
                "later_trace_disposition"
            ],
        }
        for row in accepted
    ]
    return (
        "# ORIGINAL PROBLEM\n\n"
        + problem.strip()
        + "\n\n# COMPLETE PROOF TO REWRITE\n\n"
        + proof.strip()
        + "\n\n# PROVENANCE-RESOLVED ACCEPTED PACKET\n\n"
        + json.dumps(packet, ensure_ascii=False, indent=2)
        + "\n\nReturn the complete proof now.\n"
    )


def run_trace_extraction(
    *,
    problem: str,
    proof: str,
    reasoning: str,
    reviewer_final: str,
    endpoint: str,
    output_dir: Path,
    seed: int,
    seed_label: str,
    model: str = MODEL,
) -> dict[str, Any]:
    result_path = output_dir / "result.json"
    if result_path.is_file():
        return json.loads(result_path.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)
    normalized = normalized_reviewer_verdict(reviewer_final)
    prompt = trace_gap_user_prompt(
        problem=problem,
        proof=proof,
        reasoning=reasoning,
        reviewer_final=normalized,
    )
    runtime = runtime_for(endpoint, seed, model)
    primary_error: str | None = None
    recovery_mode = "primary"
    try:
        record, generated = runtime.structured(
            role="gemma",
            prompt=TRACE_GAP_SYSTEM_PROMPT,
            user_prompt=prompt,
            destination=output_dir / "generation",
            stage="trace_gap_extraction",
            schema=TRACE_GAP_SCHEMA,
            temperature=0.1,
            max_tokens=12_000,
            seed_label=seed_label,
            use_explicit_guided_json=True,
        )
        gaps = validate_source_binding(
            record=record,
            proof=proof,
            reasoning=reasoning,
            reviewer_final=normalized,
        )
    except Exception as error:
        # Preserve v0.3.83's successful deterministic source-binding recovery. The
        # compact call can only cite immutable proof/trace line IDs, so neither
        # malformed LaTeX serialization nor paraphrased quotations can pass.
        primary_error = f"{type(error).__name__}: {error}"
        recovery_mode = "compact_line_id_retry"
        compact_prompt, proof_lines, trace_lines = compact_trace_gap_user_prompt(
            problem=problem,
            proof=proof,
            reasoning=reasoning,
            reviewer_final=normalized,
        )
        compact, generated = runtime.structured(
            role="gemma",
            prompt=TRACE_GAP_SYSTEM_PROMPT,
            user_prompt=compact_prompt,
            destination=output_dir / "compact_recovery",
            stage="trace_gap_extraction_compact_line_ids",
            schema=COMPACT_TRACE_GAP_SCHEMA,
            temperature=0.1,
            max_tokens=8_000,
            seed_label=seed_label + ":compact_line_ids",
            use_explicit_guided_json=False,
        )
        record = materialize_compact_record(
            compact=compact,
            proof_lines=proof_lines,
            trace_lines=trace_lines,
            reviewer_final=normalized,
        )
        gaps = validate_source_binding(
            record=record,
            proof=proof,
            reasoning=reasoning,
            reviewer_final=normalized,
        )
    result = {
        "schema": "cognitive-well-v084-trace-extraction-result-v1",
        "state": "completed",
        "completed_at": utc_now(),
        "normalized_original_verdict": normalized,
        "gap_count": len(gaps),
        "reportable_gap_count": sum(
            bool(gap["report_even_if_final_pass"]) for gap in gaps
        ),
        "gaps": gaps,
        "summary": record["summary"],
        "recovery_mode": recovery_mode,
        "primary_error": primary_error,
        "generation": generated["metadata"],
        "runtime_recovery_events": runtime.recovery_events(),
    }
    write_json(result_path, result)
    return result


def run_trace_resolution(
    *,
    problem: str,
    proof: str,
    gaps: list[dict[str, Any]],
    endpoint: str,
    output_dir: Path,
    seed: int,
    seed_label: str,
    model: str = MODEL,
) -> dict[str, Any]:
    result_path = output_dir / "result.json"
    if result_path.is_file():
        return json.loads(result_path.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)
    if not gaps:
        result = {
            "schema": "cognitive-well-v084-trace-resolution-result-v1",
            "state": "completed",
            "completed_at": utc_now(),
            "decisions": [],
            "summary": "No trace items were extracted; no proof action is authorized.",
            "generation": None,
            "runtime_recovery_events": [],
        }
        write_json(result_path, result)
        return result
    runtime = runtime_for(endpoint, seed, model)
    user_prompt = trace_resolution_user_prompt(
        problem=problem,
        proof=proof,
        gaps=gaps,
    )
    recovery_mode = "structured_json"
    primary_error: str | None = None
    try:
        record, generated = runtime.structured(
            role="gemma",
            prompt=TRACE_RESOLUTION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            destination=output_dir / "generation",
            stage="trace_resolution",
            schema=TRACE_RESOLUTION_SCHEMA,
            temperature=0.2,
            max_tokens=8_000,
            seed_label=seed_label,
            use_explicit_guided_json=True,
        )
    except Exception as error:
        primary_error = f"{type(error).__name__}: {error}"
        recovery_mode = "pipe_delimited_lines"
        compact_generation = runtime.text(
            role="gemma",
            prompt=COMPACT_TRACE_RESOLUTION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            destination=output_dir / "compact_recovery",
            stage="trace_resolution_compact_lines",
            temperature=0.2,
            max_tokens=2_048,
            seed_label=seed_label + ":compact_lines",
            top_p=1.0,
            top_k=-1,
        )
        record = parse_compact_resolution(
            text=str(compact_generation["text"]),
            gaps=gaps,
        )
        generated = compact_generation
    decisions = validate_resolution(record=record, gaps=gaps)
    result = {
        "schema": "cognitive-well-v084-trace-resolution-result-v1",
        "state": "completed",
        "completed_at": utc_now(),
        "decisions": decisions,
        "summary": record["summary"],
        "recovery_mode": recovery_mode,
        "primary_error": primary_error,
        "generation": generated["metadata"],
        "runtime_recovery_events": runtime.recovery_events(),
    }
    write_json(result_path, result)
    return result


def run_integration(
    *,
    problem: str,
    proof: str,
    gaps: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    endpoint: str,
    output_dir: Path,
    seed: int,
    seed_label: str,
    model: str = MODEL,
) -> dict[str, Any]:
    result_path = output_dir / "result.json"
    if result_path.is_file():
        return json.loads(result_path.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)
    proof_path = output_dir / "complete_proof.md"
    accepted = [row for row in decisions if row["decision"] in {"USE", "REPAIR"}]
    generation: dict[str, Any] | None = None
    recovery: list[dict[str, Any]] = []
    if accepted:
        runtime = runtime_for(endpoint, seed, model)
        generation = runtime.text(
            role="gemma",
            prompt=TRACE_INTEGRATION_SYSTEM_PROMPT,
            user_prompt=trace_integration_user_prompt(
                problem=problem,
                proof=proof,
                accepted=accepted,
                gaps=gaps,
            ),
            destination=output_dir / "generation",
            stage="trace_integration",
            temperature=0.2,
            max_tokens=32_768,
            seed_label=seed_label,
            top_p=1.0,
            top_k=-1,
        )
        replacement = str(generation["text"]).strip()
        if not replacement:
            raise RuntimeError("trace integration produced an empty proof")
        proof_path.write_text(replacement + "\n", encoding="utf-8")
        recovery = runtime.recovery_events()
        action = "REWRITTEN"
    else:
        proof_path.write_text(proof.rstrip() + "\n", encoding="utf-8")
        replacement = proof.strip()
        action = "UNCHANGED_NO_ACCEPTED_TRACE_MATERIAL"
    result = {
        "schema": "cognitive-well-v084-trace-integration-result-v1",
        "state": "completed",
        "completed_at": utc_now(),
        "action": action,
        "accepted_gap_ids": [row["gap_id"] for row in accepted],
        "trace_recovered_count": sum(
            row["decision"] == "USE" for row in accepted
        ),
        "prover_new_count": sum(row["decision"] == "REPAIR" for row in accepted),
        "source_proof_sha256": sha256_text(proof.strip()),
        "output_proof_sha256": sha256_text(replacement),
        "proof_changed": replacement != proof.strip(),
        "proof_path": str(proof_path.resolve()),
        "generation": generation["metadata"] if generation is not None else None,
        "runtime_recovery_events": recovery,
    }
    write_json(result_path, result)
    return result


def _reasoning_from_generation(generated: dict[str, Any], generation_dir: Path) -> str:
    reasoning = str(generated.get("reasoning") or "").strip()
    if reasoning:
        return reasoning
    candidates = sorted(generation_dir.glob("*.reasoning.txt"))
    if not candidates:
        raise RuntimeError("review completed without an observable reasoning trace")
    return "\n\n".join(
        path.read_text(encoding="utf-8").strip() for path in candidates
    ).strip()


def implicit_resolver_user_prompt(
    *, problem: str, proof: str, trace_candidates: list[dict[str, Any]]
) -> str:
    return (
        "# ORIGINAL PROBLEM\n\n"
        + problem.strip()
        + "\n\n# COMPLETE SUBMITTED PROOF\n\n"
        + proof.strip()
        + "\n\n# SOURCE-BOUND TRACE CANDIDATES (UNTRUSTED)\n\n"
        + json.dumps(trace_candidates, ensure_ascii=False, indent=2)
        + "\n\nResolve the proof now and return only the complete proof.\n"
    )


def run_implicit_resolution(
    *,
    problem: str,
    proof: str,
    trace_candidates: list[dict[str, Any]],
    endpoint: str,
    output_dir: Path,
    seed: int,
    seed_label: str,
    model: str = MODEL,
) -> dict[str, Any]:
    result_path = output_dir / "result.json"
    if result_path.is_file():
        return json.loads(result_path.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)
    runtime = runtime_for(endpoint, seed, model)
    generation_dir = output_dir / "generation"
    generated = runtime.text(
        role="gemma",
        prompt=IMPLICIT_TRACE_RESOLVER_SYSTEM_PROMPT,
        user_prompt=implicit_resolver_user_prompt(
            problem=problem,
            proof=proof,
            trace_candidates=trace_candidates,
        ),
        destination=generation_dir,
        stage="implicit_trace_resolution",
        temperature=0.2,
        max_tokens=32_768,
        seed_label=seed_label,
        top_p=1.0,
        top_k=-1,
    )
    replacement = str(generated["text"]).strip()
    if not replacement:
        raise RuntimeError("implicit resolver produced an empty proof")
    reasoning = _reasoning_from_generation(generated, generation_dir)
    proof_path = output_dir / "complete_proof.md"
    proof_path.write_text(replacement + "\n", encoding="utf-8")
    (output_dir / "reasoning.txt").write_text(reasoning + "\n", encoding="utf-8")
    result = {
        "schema": "cognitive-well-v084-implicit-trace-resolution-result-v1",
        "state": "completed",
        "completed_at": utc_now(),
        "trace_candidate_count": len(trace_candidates),
        "source_proof_sha256": sha256_text(proof.strip()),
        "output_proof_sha256": sha256_text(replacement),
        "proof_changed": replacement != proof.strip(),
        "proof_path": str(proof_path.resolve()),
        "reasoning_sha256": sha256_text(reasoning),
        "reasoning_observed": bool(reasoning),
        "generation": generated["metadata"],
        "runtime_recovery_events": runtime.recovery_events(),
    }
    write_json(result_path, result)
    return result


def run_post_review(
    *,
    problem: str,
    proof: str,
    endpoint: str,
    output_dir: Path,
    seed: int,
    seed_label: str,
    model: str = MODEL,
) -> dict[str, Any]:
    result_path = output_dir / "result.json"
    if result_path.is_file():
        return json.loads(result_path.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)
    runtime = runtime_for(endpoint, seed, model)
    system = reviewer1_system_prompt("narrow_terseness")
    user = review_user_prompt(problem=problem, proof=proof)
    generation_dir = output_dir / "generation"
    generated = runtime.text(
        role="gemma",
        prompt=system,
        user_prompt=user,
        destination=generation_dir,
        stage="reviewer1",
        temperature=0.1,
        max_tokens=12_000,
        seed_label=seed_label,
        top_p=1.0,
        top_k=-1,
    )
    final = str(generated["text"]).strip()
    parsed = parse_review(final)
    if not parsed["valid"]:
        repaired = runtime.text(
            role="gemma",
            prompt=system,
            user_prompt=(
                user.rstrip()
                + "\n\nThe preceding response violated the review output protocol. "
                "Repeat the complete audit and return exactly the required FIRST_BREAK "
                "or NO_FIRST_BREAK form.\n"
            ),
            destination=generation_dir,
            stage="reviewer1_protocol_repair",
            temperature=0.1,
            max_tokens=12_000,
            seed_label=seed_label + ":protocol_repair",
            top_p=1.0,
            top_k=-1,
        )
        final = str(repaired["text"]).strip()
        parsed = parse_review(final)
        generated = repaired
    if not parsed["valid"]:
        raise ValueError(f"post-review protocol invalid: {parsed['errors']}")
    reasoning = _reasoning_from_generation(generated, generation_dir)
    (output_dir / "final.txt").write_text(final + "\n", encoding="utf-8")
    (output_dir / "reasoning.txt").write_text(reasoning + "\n", encoding="utf-8")
    result = {
        "schema": "cognitive-well-v084-post-review-result-v1",
        "state": "completed",
        "completed_at": utc_now(),
        "parsed": parsed,
        "final": final,
        "reasoning_sha256": sha256_text(reasoning),
        "generation": generated["metadata"],
        "runtime_recovery_events": runtime.recovery_events(),
    }
    write_json(result_path, result)
    return result


def case_summary(case: dict[str, Any], case_dir: Path) -> dict[str, Any]:
    extraction = json.loads(
        (case_dir / "01_trace_extraction" / "result.json").read_text(encoding="utf-8")
    )
    resolution = json.loads(
        (case_dir / "02_implicit_resolution" / "result.json").read_text(
            encoding="utf-8"
        )
    )
    review = json.loads(
        (case_dir / "04_post_review" / "result.json").read_text(encoding="utf-8")
    )
    post = json.loads(
        (case_dir / "05_post_trace_extraction" / "result.json").read_text(
            encoding="utf-8"
        )
    )
    control_class = str(case["class"])
    no_useful_control = control_class == "NO_USEFUL_TRACE_CONTROL"
    no_hidden_repair_control = control_class == "NO_HIDDEN_REPAIR_CONTROL"
    result = {
        "case_id": case["case_id"],
        "class": control_class,
        "expected_signals": case["expected_signals"],
        "source_verdict": case["normalized_source_verdict"],
        "post_reviewer_outcome": review["parsed"]["outcome"],
        "pre_gap_count": extraction["gap_count"],
        "pre_reportable_gap_count": extraction["reportable_gap_count"],
        "collected_trace_card_count": len(case.get("collected_trace_cards") or []),
        "trace_candidate_count": resolution["trace_candidate_count"],
        "implicit_reasoning_observed": resolution["reasoning_observed"],
        "proof_changed": resolution["proof_changed"],
        "post_gap_count": post["gap_count"],
        "post_reportable_gap_count": post["reportable_gap_count"],
        "reportable_gap_delta": (
            post["reportable_gap_count"] - extraction["reportable_gap_count"]
        ),
        "no_useful_control_preserved": (
            not resolution["proof_changed"] if no_useful_control else None
        ),
        "no_hidden_repair_misattributed": (
            None if no_hidden_repair_control else None
        ),
        "proof_path": resolution["proof_path"],
    }
    write_json(case_dir / "summary.json", result)
    return result


def run_wave(
    *,
    name: str,
    cases: list[dict[str, Any]],
    endpoints: list[str],
    workers_per_endpoint: int,
    task: Callable[[dict[str, Any], str], Any],
) -> dict[str, str]:
    if not endpoints or workers_per_endpoint < 1:
        raise ValueError("at least one endpoint and one worker per endpoint are required")
    errors: dict[str, str] = {}
    assignments = [endpoints[index % len(endpoints)] for index in range(len(cases))]
    with ThreadPoolExecutor(
        max_workers=len(endpoints) * workers_per_endpoint,
        thread_name_prefix=f"v084-{name}",
    ) as pool:
        pending: dict[Future[Any], tuple[dict[str, Any], str]] = {
            pool.submit(task, case, endpoint): (case, endpoint)
            for case, endpoint in zip(cases, assignments, strict=True)
        }
        for future in as_completed(pending):
            case, endpoint = pending[future]
            case_id = str(case["case_id"])
            try:
                future.result()
                print(f"[{utc_now()}] {name}: {case_id} completed on {endpoint}", flush=True)
            except Exception as error:
                errors[case_id] = f"{type(error).__name__}: {error}"
                print(
                    f"[{utc_now()}] {name}: {case_id} failed on {endpoint}: "
                    f"{errors[case_id]}",
                    flush=True,
                )
    return errors


def aggregate_summary(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    cases = list(rows)
    controls = [row for row in cases if row["class"] == "NO_USEFUL_TRACE_CONTROL"]
    hidden_controls = [
        row for row in cases if row["class"] == "NO_HIDDEN_REPAIR_CONTROL"
    ]
    return {
        "schema": "cognitive-well-v084-trace-resolution-batch-summary-v1",
        "state": "completed",
        "completed_at": utc_now(),
        "case_count": len(cases),
        "trace_candidate_total": sum(row["trace_candidate_count"] for row in cases),
        "rewritten_count": sum(row["proof_changed"] for row in cases),
        "post_no_first_break_count": sum(
            row["post_reviewer_outcome"] == "NO_FIRST_BREAK" for row in cases
        ),
        "pre_reportable_gap_total": sum(
            row["pre_reportable_gap_count"] for row in cases
        ),
        "post_reportable_gap_total": sum(
            row["post_reportable_gap_count"] for row in cases
        ),
        "no_useful_controls_preserved": sum(
            row["no_useful_control_preserved"] is True for row in controls
        ),
        "no_useful_control_count": len(controls),
        "hidden_repair_control_count": len(hidden_controls),
        "cases": cases,
    }


__all__ = [
    "MODEL",
    "IMPLICIT_TRACE_RESOLVER_SYSTEM_PROMPT",
    "TRACE_INTEGRATION_SYSTEM_PROMPT",
    "TRACE_RESOLUTION_SCHEMA",
    "TRACE_RESOLUTION_SYSTEM_PROMPT",
    "aggregate_summary",
    "case_summary",
    "load_corpus",
    "normalized_reviewer_verdict",
    "parse_review_input",
    "resolution_input_gaps",
    "run_integration",
    "run_implicit_resolution",
    "run_post_review",
    "run_trace_extraction",
    "run_trace_resolution",
    "run_wave",
    "sha256_text",
    "validate_resolution",
]
