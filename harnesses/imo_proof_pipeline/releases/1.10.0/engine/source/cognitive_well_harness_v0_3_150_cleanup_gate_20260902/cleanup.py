from __future__ import annotations

import hashlib
import json
import re
import traceback
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_97_four_proof_raw_lazy_enhanced_pipeline_20260827 import (
    run as v097,
)
from cognitive_well_harness_v0_3_140_clean_dual_trace_fusion_20260901.pipeline import (
    GEMMA_MODEL,
    QWEN_MODEL,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.contracts import (
    validate_schema,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import (
    REPETITION_DETECTION,
    RuntimeConfig,
    parse_json_object,
)
from cognitive_well_harness_v0_3_79_modular_singleton_atomic_retry_20260825.runtime import (
    ResilientModelRuntime,
)
from cognitive_well_harness_v0_3_149_v108_three_cycle_v148_20260902.pipeline import (
    _artifact_metrics,
)
from experiments.local_math_verifier.runtime import (
    HTTPGenerationConfig,
    run_openai_chat_generation,
)

from . import HARNESS_VERSION


CLEANUP_REASONS = {
    "new_exact_duplicate_paragraph",
    "new_repeated_long_span",
    "additional_conclusion_like_ending",
    "additional_lazy_connection_language",
    "proof_word_count_growth_over_75_percent",
}

CLEANUP_PLAN_THINKING_TOKEN_BUDGET = 8_192
CLEANUP_PLAN_MAX_TOKENS = 16_384
PRESERVATION_AUDIT_THINKING_TOKEN_BUDGET = 8_192
PRESERVATION_AUDIT_MAX_TOKENS = 16_384

CLEANUP_PLAN_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["action", "delete_ranges"],
    "properties": {
        "action": {"type": "string", "enum": ["DELETE_REDUNDANCY", "NO_CHANGE"]},
        "delete_ranges": {
            "type": "array",
            "maxItems": 6,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "start_line",
                    "end_line",
                    "kept_start_line",
                    "kept_end_line",
                    "reason",
                ],
                "properties": {
                    "start_line": {"type": "integer", "minimum": 1},
                    "end_line": {"type": "integer", "minimum": 1},
                    "kept_start_line": {"type": "integer", "minimum": 1},
                    "kept_end_line": {"type": "integer", "minimum": 1},
                    "reason": {
                        "type": "string",
                        "enum": [
                            "EXACT_DUPLICATE",
                            "SEMANTIC_DUPLICATE",
                            "REDUNDANT_CONCLUSION",
                            "LAZY_RESTATEMENT",
                        ],
                    },
                },
            },
        },
    },
}

PRESERVATION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "range_verdicts",
        "accepted_range_indices",
        "accepted_subset_verdict",
        "preservation_finding",
    ],
    "properties": {
        "range_verdicts": {
            "type": "array",
            "maxItems": 6,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["range_index", "verdict"],
                "properties": {
                    "range_index": {"type": "integer", "minimum": 1, "maximum": 6},
                    "verdict": {"type": "string", "enum": ["ACCEPT", "REJECT"]},
                },
            },
        },
        "accepted_range_indices": {
            "type": "array",
            "maxItems": 6,
            "items": {"type": "integer", "minimum": 1, "maximum": 6},
        },
        "accepted_subset_verdict": {
            "type": "string",
            "enum": ["ACCEPT", "REJECT"],
        },
        "preservation_finding": {"type": "string"},
    },
}


def _write_json(path: Path, value: Any) -> None:
    v097.write_json(path, value)


def _digest(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def cleanup_plan_runtime(
    *, gemma_endpoint: str, qwen_endpoint: str, master_seed: int
) -> ResilientModelRuntime:
    return ResilientModelRuntime(
        RuntimeConfig(
            gemma_endpoint=gemma_endpoint.rstrip("/"),
            qwen_endpoint=qwen_endpoint.rstrip("/"),
            gemma_model=GEMMA_MODEL,
            qwen_model=QWEN_MODEL,
            master_seed=master_seed,
            thinking_token_budget=CLEANUP_PLAN_THINKING_TOKEN_BUDGET,
            reasoning_effort="max",
        )
    )


def _line_indexed(proof: str) -> str:
    return "\n".join(
        f"L{index:03d}: {line}"
        for index, line in enumerate(proof.splitlines(), start=1)
    )


def _compact_artifact_evidence(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "word_count": metrics["word_count"],
        "exact_duplicate_paragraph_count": metrics[
            "exact_duplicate_paragraph_count"
        ],
        "repeated_12_word_span_count": metrics["repeated_12_word_span_count"],
        "repeated_12_word_spans": metrics["repeated_12_word_spans"],
        "ending_conclusion_like_lines": metrics["ending_conclusion_like_lines"],
        "lazy_connection_counts": metrics["lazy_connection_counts"],
    }


def cleanup_plan_prompt(
    *,
    problem: str,
    proof: str,
    attention_reasons: list[str],
    metrics: dict[str, Any],
) -> str:
    return f"""You are a conservative proof-copy editor, not a proof solver.

Improve the proof's reading flow only by removing redundant language already
present elsewhere in the submitted proof. Smooth flow never overrides mathematical
rigor: do not shorten a derivation merely because it is awkward or verbose.
You may propose deletion of at most six contiguous line ranges. You may not add,
rewrite, correct, strengthen, weaken, or reorder any mathematical content. Every
deleted range must name a disjoint retained line range containing the same
mathematical claim and full derivation. Never remove a useful derivation, definition,
or equation completely. Preserve all assumptions, definitions, equations,
case conditions, dependency links, caveats, unresolved steps, and the final
conclusion. A repeated formula may be deleted only when its retained occurrence is
in the same logical context. If any proposed deletion could change what is proved
or how a later statement is justified, return NO_CHANGE.

The artifact evidence is diagnostic only. It does not establish redundancy.

ORIGINAL PROBLEM
{problem}

CURRENT PROOF WITH IMMUTABLE LINE NUMBERS
{_line_indexed(proof)}

DETERMINISTIC ARTIFACT ATTENTION REASONS
{json.dumps(attention_reasons, ensure_ascii=False)}

DETERMINISTIC ARTIFACT EVIDENCE
{json.dumps(_compact_artifact_evidence(metrics), ensure_ascii=False)}
"""


def preservation_prompt(
    *,
    problem: str,
    before: str,
    after: str,
    plan: dict[str, Any],
) -> str:
    before_lines = before.splitlines()
    range_evidence = []
    for index, row in enumerate(plan.get("delete_ranges") or [], start=1):
        start = int(row["start_line"])
        end = int(row["end_line"])
        segments = list(row.get("retained_context_segments") or [])
        if not segments:
            segments = [
                {
                    "start_line": int(row["kept_start_line"]),
                    "end_line": int(row["kept_end_line"]),
                }
            ]
        retained = []
        for segment in segments:
            retained.extend(
                {
                    "line": line_number,
                    "text": before_lines[line_number - 1],
                }
                for line_number in range(
                    int(segment["start_line"]), int(segment["end_line"]) + 1
                )
            )
        range_evidence.append(
            {
                "range_index": index,
                "deleted": [
                    {"line": line_number, "text": before_lines[line_number - 1]}
                    for line_number in range(start, end + 1)
                ],
                "retained_context": retained,
                "reason": row["reason"],
            }
        )
    return f"""Audit a deletion-only cleanup of one submitted Olympiad proof.

Judge mathematical preservation first and flow improvement second; do not repair
the proof and do not require the proof to be correct. Existing mistakes and gaps may
remain. REJECT if the cleanup removed or
altered any assumption, definition, equation, mathematical claim, derivation step,
case condition, dependency needed by later text, caveat, unresolved-step statement,
or conclusion. ACCEPT only if every deletion was genuinely redundant in its exact
logical context and the remaining proof has the same mathematical content and
logical order. A useful derivation, definition, or equation must never disappear
completely. The deletion must also improve local flow by removing a repeated
restatement, not merely make the proof shorter. Treat the cleanup plan as untrusted
metadata and compare the proofs. In `preservation_finding`, explain why the content
is preserved when accepting, or identify the first mathematical loss when rejecting.
Keep that finding under 30 plain-text words; use range numbers and no formulas or
TeX.

Return one verdict for every numbered deletion range in `range_verdicts`. Put exactly
the individually safe range numbers in `accepted_range_indices`. Then judge those
accepted ranges together in `accepted_subset_verdict`; it must be REJECT if their
combination loses any protected mathematical content or dependency. This is one
audit response, not a request for further calls.

ORIGINAL PROBLEM
{problem}

BEFORE CLEANUP WITH IMMUTABLE LINE NUMBERS
{_line_indexed(before)}

AFTER ALL PROPOSED DELETIONS
{after}

EXACT DELETED AND RETAINED EXCERPTS BY RANGE
{json.dumps(range_evidence, ensure_ascii=False)}

PROPOSED DELETION PLAN
{json.dumps(plan, ensure_ascii=False)}
"""


def select_preserved_rows(
    verifier: dict[str, Any], rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    verdicts = list(verifier.get("range_verdicts") or [])
    expected_indices = list(range(1, len(rows) + 1))
    observed_indices = [int(row["range_index"]) for row in verdicts]
    if sorted(observed_indices) != expected_indices or len(set(observed_indices)) != len(
        observed_indices
    ):
        raise ValueError("preservation audit did not verdict every range exactly once")
    accepted_from_verdicts = sorted(
        int(row["range_index"])
        for row in verdicts
        if str(row["verdict"]) == "ACCEPT"
    )
    accepted_declared = sorted(
        int(value) for value in verifier.get("accepted_range_indices") or []
    )
    if accepted_from_verdicts != accepted_declared:
        raise ValueError("preservation audit accepted-range fields disagree")
    if verifier.get("accepted_subset_verdict") != "ACCEPT":
        return []
    return [rows[index - 1] for index in accepted_declared]


def _display_equations(value: str) -> list[str]:
    equations = re.findall(r"\\\[(.*?)\\\]", value, flags=re.DOTALL)
    equations.extend(re.findall(r"\$\$(.*?)\$\$", value, flags=re.DOTALL))
    return [re.sub(r"\s+", "", equation) for equation in equations]


def deterministic_equation_guard(
    proof: str, rows: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Reject a range if it would remove a non-identically retained display equation."""

    lines = proof.splitlines()
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for row in rows:
        deleted = "\n".join(
            lines[int(row["start_line"]) - 1 : int(row["end_line"])]
        )
        retained_lines: list[str] = []
        for segment in row.get("retained_context_segments") or []:
            retained_lines.extend(
                lines[line_number - 1]
                for line_number in range(
                    int(segment["start_line"]), int(segment["end_line"]) + 1
                )
            )
        retained_equations = set(_display_equations("\n".join(retained_lines)))
        missing = [
            equation
            for equation in _display_equations(deleted)
            if equation not in retained_equations
        ]
        if missing:
            rejected.append(
                {
                    **row,
                    "deterministic_rejection": "display_equation_not_identically_retained",
                    "missing_display_equation_count": len(missing),
                }
            )
        else:
            accepted.append(row)
    return accepted, rejected


def run_compact_preservation_audit(
    *,
    prompt: str,
    destination: Path,
    qwen_endpoint: str,
    seed_label: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Run one compact-output audit with a bounded hidden-reasoning budget."""

    stage = "preservation_audit"
    destination.mkdir(parents=True, exist_ok=True)
    seed = int.from_bytes(hashlib.sha256(seed_label.encode("utf-8")).digest()[:4], "big") or 1
    generation = run_openai_chat_generation(
        endpoint=qwen_endpoint.rstrip("/"),
        model=QWEN_MODEL,
        prompt=prompt,
        output_dir=destination,
        stage=stage,
        user_prompt="Return the compact preservation verdict now.",
        config=HTTPGenerationConfig(
            max_tokens=PRESERVATION_AUDIT_MAX_TOKENS,
            temperature=0.1,
            top_p=1.0,
            top_k=-1,
            seed=seed,
            thinking_enabled=True,
            thinking_token_budget=PRESERVATION_AUDIT_THINKING_TOKEN_BUDGET,
            reasoning_effort="max",
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": stage,
                    "strict": True,
                    "schema": PRESERVATION_SCHEMA,
                },
            },
            repetition_detection=REPETITION_DETECTION,
            timeout_seconds=14_400,
        ),
    )
    record = parse_json_object(str(generation.get("text") or ""))
    validate_schema(record, PRESERVATION_SCHEMA)
    return record, generation


def _tokens(value: str) -> set[str]:
    return set(re.findall(r"[A-Za-z0-9_]+|\\\\[A-Za-z]+", value.lower()))


def validate_cleanup_plan(proof: str, plan: dict[str, Any]) -> list[dict[str, Any]]:
    action = str(plan.get("action") or "")
    rows = [dict(row) for row in plan.get("delete_ranges") or []]
    if action == "NO_CHANGE":
        if rows:
            raise ValueError("NO_CHANGE cleanup plan contains delete ranges")
        return []
    if action != "DELETE_REDUNDANCY" or not rows:
        raise ValueError("cleanup action/range mismatch")

    lines = proof.splitlines()
    line_count = len(lines)
    nonempty = [index for index, line in enumerate(lines, start=1) if line.strip()]
    if not nonempty:
        raise ValueError("cannot clean an empty proof")
    first_nonempty, last_nonempty = nonempty[0], nonempty[-1]
    parsed: list[tuple[dict[str, Any], int, int, int, int]] = []
    previous_end = 0
    for row in sorted(rows, key=lambda value: int(value["start_line"])):
        start = int(row["start_line"])
        end = int(row["end_line"])
        kept_start = int(row["kept_start_line"])
        kept_end = int(row["kept_end_line"])
        if not (1 <= start <= end <= line_count):
            raise ValueError(f"invalid cleanup deletion range {start}-{end}")
        if not (1 <= kept_start <= kept_end <= line_count):
            raise ValueError(f"invalid cleanup retained range {kept_start}-{kept_end}")
        if start <= previous_end:
            raise ValueError("cleanup deletion ranges overlap")
        if start <= first_nonempty <= end or start <= last_nonempty <= end:
            raise ValueError("cleanup may not delete the opening or terminal proof line")
        parsed.append((row, start, end, kept_start, kept_end))
        previous_end = end

    deleted_line_numbers = {
        line_number
        for _, start, end, _, _ in parsed
        for line_number in range(start, end + 1)
    }
    normalized: list[dict[str, Any]] = []
    deleted_line_count = 0
    deleted_word_count = 0
    total_words = max(1, len(re.findall(r"\S+", proof)))
    for row, start, end, kept_start, kept_end in parsed:
        # Some structured outputs use one bracketing retained-context interval.
        # Canonicalize it deterministically to the portions that actually survive
        # every deletion. The preservation verifier still compares the full before
        # and after proofs; this normalization never authorizes extra deletion.
        kept_line_numbers = [
            line_number
            for line_number in range(kept_start, kept_end + 1)
            if line_number not in deleted_line_numbers
        ]
        if not kept_line_numbers:
            raise ValueError("cleanup retained context is entirely deleted")
        retained_segments: list[dict[str, int]] = []
        segment_start = kept_line_numbers[0]
        segment_end = segment_start
        for line_number in kept_line_numbers[1:]:
            if line_number == segment_end + 1:
                segment_end = line_number
            else:
                retained_segments.append(
                    {"start_line": segment_start, "end_line": segment_end}
                )
                segment_start = segment_end = line_number
        retained_segments.append(
            {"start_line": segment_start, "end_line": segment_end}
        )
        deleted = "\n".join(lines[start - 1 : end])
        kept = "\n".join(lines[line_number - 1] for line_number in kept_line_numbers)
        deleted_tokens = _tokens(deleted)
        kept_tokens = _tokens(kept)
        overlap = (
            len(deleted_tokens & kept_tokens) / max(1, len(deleted_tokens))
        )
        if overlap < 0.30:
            raise ValueError(
                f"cleanup retained range lacks deterministic overlap: {overlap:.3f}"
            )
        normalized.append(
            {
                **row,
                "start_line": start,
                "end_line": end,
                "kept_start_line": kept_start,
                "kept_end_line": kept_end,
                "retained_context_segments": retained_segments,
                "deterministic_token_overlap": overlap,
            }
        )
        deleted_line_count += end - start + 1
        deleted_word_count += len(re.findall(r"\S+", deleted))
    if deleted_line_count / max(1, len(nonempty)) > 0.35:
        raise ValueError("cleanup deletes more than 35 percent of nonempty lines")
    if deleted_word_count / total_words > 0.35:
        raise ValueError("cleanup deletes more than 35 percent of proof words")
    return normalized


def apply_deletion_plan(proof: str, rows: list[dict[str, Any]]) -> str:
    if not rows:
        return proof
    deleted = {
        line_number
        for row in rows
        for line_number in range(int(row["start_line"]), int(row["end_line"]) + 1)
    }
    lines = proof.splitlines()
    result = "\n".join(
        line for index, line in enumerate(lines, start=1) if index not in deleted
    ).strip()
    if not result:
        raise ValueError("cleanup produced an empty proof")
    return result


def metric_gate(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    before_lazy = sum(int(value) for value in before["lazy_connection_counts"].values())
    after_lazy = sum(int(value) for value in after["lazy_connection_counts"].values())
    tracked = {
        "exact_duplicate_paragraph_count": (
            int(before["exact_duplicate_paragraph_count"]),
            int(after["exact_duplicate_paragraph_count"]),
        ),
        "repeated_12_word_span_count": (
            int(before["repeated_12_word_span_count"]),
            int(after["repeated_12_word_span_count"]),
        ),
        "ending_conclusion_like_line_count": (
            int(before["ending_conclusion_like_line_count"]),
            int(after["ending_conclusion_like_line_count"]),
        ),
        "lazy_connection_total": (before_lazy, after_lazy),
        "word_count": (int(before["word_count"]), int(after["word_count"])),
    }
    nonworsening = all(after_value <= before_value for before_value, after_value in tracked.values())
    artifact_improved = any(
        after_value < before_value
        for key, (before_value, after_value) in tracked.items()
        if key != "word_count"
    )
    return {
        "tracked": {
            key: {"before": values[0], "after": values[1], "delta": values[1] - values[0]}
            for key, values in tracked.items()
        },
        "all_tracked_metrics_nonworsening": nonworsening,
        "at_least_one_artifact_metric_improved": artifact_improved,
        "accepted": nonworsening and artifact_improved,
    }


def run_cleanup_gate(
    *,
    problem: str,
    problem_id: str,
    candidate_id: str,
    cycle: int,
    proof_path: Path,
    artifact_audit_path: Path,
    output_dir: Path,
    gemma_endpoint: str,
    qwen_endpoint: str,
    master_seed: int,
    seed_namespace: str,
    force: bool = False,
) -> dict[str, Any]:
    destination = output_dir.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    summary_path = destination / "summary.json"
    proof_source = proof_path.resolve()
    audit_source = artifact_audit_path.resolve()
    proof = proof_source.read_text(encoding="utf-8").strip()
    audit = json.loads(audit_source.read_text(encoding="utf-8"))
    attention_reasons = [str(value) for value in audit.get("attention_reasons") or []]
    input_contract = {
        "problem_id": problem_id,
        "candidate_id": candidate_id,
        "cycle": cycle,
        "proof_path": str(proof_source),
        "proof_sha256": v097.sha256_text(proof),
        "artifact_audit_path": str(audit_source),
        "artifact_audit_sha256": v097.file_sha256(audit_source),
        "force": force,
        "gate_version": HARNESS_VERSION,
    }
    input_sha256 = _digest(input_contract)
    if summary_path.is_file():
        saved = json.loads(summary_path.read_text(encoding="utf-8"))
        if saved.get("input_sha256") != input_sha256:
            raise ValueError("refusing to reuse cleanup output after input drift")
        if saved.get("state") == "completed":
            return saved

    _write_json(
        destination / "manifest.json",
        {
            "schema": "cognitive-well-v0150-cleanup-manifest-v1",
            "harness_version": HARNESS_VERSION,
            "created_at": v097.utc_now(),
            "input_sha256": input_sha256,
            "source": input_contract,
            "policy": {
                "solver_internal_same_problem_only": True,
                "external_scores_supplied": False,
                "gold_supplied": False,
                "cross_problem_material_supplied": False,
                "cleanup_operation": "DELETION_ONLY",
                "independent_preservation_audit": True,
                "metric_improvement_required": True,
                "fail_closed_to_original_proof": True,
            },
        },
    )
    _write_json(
        destination / "leak_audit.json",
        {
            "state": "passed",
            "problem_statement_and_current_proof_only": True,
            "gold_supplied": False,
            "codex_grades_supplied": False,
            "external_feedback_supplied": False,
            "cross_problem_information_supplied": False,
            "problem_specific_guidance_supplied": False,
        },
    )

    trigger_reasons = sorted(set(attention_reasons) & CLEANUP_REASONS)
    if not force and not trigger_reasons:
        output_proof_path = destination / "proof.md"
        output_proof_path.write_text(proof + "\n", encoding="utf-8")
        summary = {
            "schema": "cognitive-well-v0150-cleanup-summary-v1",
            "harness_version": HARNESS_VERSION,
            "state": "completed",
            "outcome": "SKIPPED_NO_CLEANUP_TRIGGER",
            "input_sha256": input_sha256,
            "proof_path": str(output_proof_path.resolve()),
            "proof_sha256": v097.sha256_text(proof),
            "cleanup_accepted": False,
            "model_calls": 0,
            "trigger_reasons": trigger_reasons,
            "completed_at": v097.utc_now(),
        }
        _write_json(summary_path, summary)
        return summary

    runtime = cleanup_plan_runtime(
        gemma_endpoint=gemma_endpoint,
        qwen_endpoint=qwen_endpoint,
        master_seed=master_seed,
    )
    before_metrics = _artifact_metrics(proof)
    try:
        plan, plan_generation = runtime.structured(
            role="gemma",
            prompt=cleanup_plan_prompt(
                problem=problem,
                proof=proof,
                attention_reasons=attention_reasons,
                metrics=before_metrics,
            ),
            destination=destination / "01_cleanup_plan",
            stage="cleanup_plan",
            schema=CLEANUP_PLAN_SCHEMA,
            temperature=0.1,
            max_tokens=CLEANUP_PLAN_MAX_TOKENS,
            seed_label=(
                f"{seed_namespace}:{problem_id}:{candidate_id}:cycle-{cycle}:cleanup-plan"
            ),
            user_prompt="Return the deletion-only cleanup plan now.",
        )
        all_rows = validate_cleanup_plan(proof, plan)
        rows, deterministic_rejected_rows = deterministic_equation_guard(
            proof, all_rows
        )
        selected_rows: list[dict[str, Any]] = []
        if not rows:
            proposed = proof
            verifier = {
                "range_verdicts": [],
                "accepted_range_indices": [],
                "accepted_subset_verdict": "ACCEPT",
                "preservation_finding": "No deletion was proposed.",
            }
            verifier_generation: dict[str, Any] | None = None
        else:
            all_deletions_proof = apply_deletion_plan(proof, rows)
            verifier, verifier_generation = run_compact_preservation_audit(
                prompt=preservation_prompt(
                    problem=problem,
                    before=proof,
                    after=all_deletions_proof,
                    plan={**plan, "delete_ranges": rows},
                ),
                destination=destination / "02_preservation_audit",
                qwen_endpoint=qwen_endpoint,
                seed_label=(
                    f"{seed_namespace}:{problem_id}:{candidate_id}:cycle-{cycle}:"
                    "cleanup-audit"
                ),
            )
            selected_rows = select_preserved_rows(verifier, rows)
            proposed = apply_deletion_plan(proof, selected_rows)
        after_metrics = _artifact_metrics(proposed)
        metric_result = metric_gate(before_metrics, after_metrics)
        verifier_accepts = verifier["accepted_subset_verdict"] == "ACCEPT"
        cleanup_accepted = (
            bool(selected_rows) and verifier_accepts and metric_result["accepted"]
        )
        final_proof = proposed if cleanup_accepted else proof
        outcome = (
            "CLEANUP_ACCEPTED"
            if cleanup_accepted
            else ("NO_CHANGE_PROPOSED" if not all_rows else "CLEANUP_REJECTED")
        )
        output_proof_path = destination / "proof.md"
        output_proof_path.write_text(final_proof + "\n", encoding="utf-8")
        _write_json(
            destination / "cleanup_record.json",
            {
                "plan": {**plan, "delete_ranges": all_rows},
                "plan_generation": plan_generation.get("metadata"),
                "deterministic_equation_guard_rejections": deterministic_rejected_rows,
                "selected_delete_ranges": selected_rows,
                "rejected_delete_ranges": [
                    row for row in all_rows if row not in selected_rows
                ],
                "proposed_proof_sha256": v097.sha256_text(proposed),
                "preservation_audit": verifier,
                "preservation_generation": (
                    verifier_generation.get("metadata")
                    if verifier_generation is not None
                    else None
                ),
                "before_metrics": before_metrics,
                "after_metrics": after_metrics,
                "metric_gate": metric_result,
                "cleanup_accepted": cleanup_accepted,
                "fail_closed_to_original": not cleanup_accepted,
            },
        )
        summary = {
            "schema": "cognitive-well-v0150-cleanup-summary-v1",
            "harness_version": HARNESS_VERSION,
            "state": "completed",
            "outcome": outcome,
            "input_sha256": input_sha256,
            "proof_path": str(output_proof_path.resolve()),
            "proof_sha256": v097.sha256_text(final_proof),
            "input_proof_sha256": v097.sha256_text(proof),
            "cleanup_accepted": cleanup_accepted,
            "model_calls": 1 if not rows else 2,
            "trigger_reasons": trigger_reasons,
            "deleted_ranges": selected_rows if cleanup_accepted else [],
            "deterministic_rejected_range_count": len(deterministic_rejected_rows),
            "metric_gate": metric_result,
            "preservation_verdict": verifier["accepted_subset_verdict"],
            "completed_at": v097.utc_now(),
        }
        _write_json(summary_path, summary)
        return summary
    except Exception as error:
        # Cleanup is presentation-only. A transport, parsing, validation, or
        # preservation failure must leave the mathematical proof byte-equivalent.
        output_proof_path = destination / "proof.md"
        output_proof_path.write_text(proof + "\n", encoding="utf-8")
        summary = {
            "schema": "cognitive-well-v0150-cleanup-summary-v1",
            "harness_version": HARNESS_VERSION,
            "state": "completed",
            "outcome": "CLEANUP_FAILED_CLOSED_TO_ORIGINAL",
            "input_sha256": input_sha256,
            "proof_path": str(output_proof_path.resolve()),
            "proof_sha256": v097.sha256_text(proof),
            "input_proof_sha256": v097.sha256_text(proof),
            "cleanup_accepted": False,
            "trigger_reasons": trigger_reasons,
            "error": f"{type(error).__name__}: {error}",
            "traceback": traceback.format_exc(),
            "completed_at": v097.utc_now(),
        }
        _write_json(summary_path, summary)
        return summary


__all__ = [
    "CLEANUP_PLAN_SCHEMA",
    "PRESERVATION_SCHEMA",
    "apply_deletion_plan",
    "cleanup_plan_runtime",
    "cleanup_plan_prompt",
    "deterministic_equation_guard",
    "metric_gate",
    "preservation_prompt",
    "run_cleanup_gate",
    "select_preserved_rows",
    "validate_cleanup_plan",
]
