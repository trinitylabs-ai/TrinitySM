from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_49_reviewer1_temperature_ablation_20260823.protocol import (
    parse_review as parse_reviewer_1,
)
from cognitive_well_harness_v0_3_51_reviewer3_certifier_20260823.protocol import (
    parse_review as parse_reviewer_3,
)
from cognitive_well_harness_v0_3_53_fusion_20260823 import run as fusion
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import (
    write_json,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.pipeline import (
    utc_now,
)
from cognitive_well_harness_v0_3_85_nvfp4_single_trace_resolver_20260827.pipeline import (
    sha256_text,
)


NO_DEFECT_OUTCOMES = {
    "NO_FIRST_BREAK",
    "NO_ADVERSARIAL_BREAK",
    "NO_UNCLOSED_OBLIGATION_FOUND",
    "PROOF_CERTIFIED",
}
DEFECT_OUTCOMES = {
    "FIRST_BREAK",
    "ADVERSARIAL_BREAK",
    "CERTIFICATION_FAILURE",
}


def canonical_role_label(
    *, source_outcome: str, model_label: str, reason: str
) -> str | None:
    """Return a label-only repair when the preserved reason makes it unambiguous."""
    reason_lower = reason.lower()
    if source_outcome in NO_DEFECT_OUTCOMES:
        if model_label not in {
            "DEFECT_VALIDATED",
            "DEFECT_REJECTED",
            "DEFECT_UNRESOLVED",
        }:
            return None
        if any(
            marker in reason_lower
            for marker in ("missed", "failed to identify", "did not identify", "overlook")
        ):
            return "REVIEWER_MISSED_DEFECT"
        return None
    if source_outcome in DEFECT_OUTCOMES:
        if model_label not in {"NO_DEFECT_REPORTED", "REVIEWER_MISSED_DEFECT"}:
            return None
        if any(
            marker in reason_lower
            for marker in (
                "correctly identified the gap",
                "correctly identified the break",
                "correctly identified the defect",
            )
        ):
            return "DEFECT_VALIDATED"
        if any(
            marker in reason_lower
            for marker in (
                "does not invalidate",
                "doesn't invalidate",
                "does not constitute a defect",
                "is not a defect",
                "is not a material defect",
            )
        ):
            return "DEFECT_REJECTED"
    return None


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def reviewer_1_failure_record(packet: dict[str, str]) -> str:
    record = (
        "FIRST_BREAK\n"
        f"location: {packet['useful_material'] or packet['repair_needed']}\n"
        f"claim: {packet['repair_needed']}\n"
        f"established_before: {packet['useful_material'] or 'The preceding submitted proof.'}\n"
        f"missing_or_invalid_link: {packet['repair_needed']}\n"
        f"why_not_follow: {packet['selector_reason']}\n"
        f"minimum_requirement: {packet['repair_needed']}\n"
        "END_FIRST_BREAK"
    )
    parsed = parse_reviewer_1(record)
    if not parsed["valid"] or parsed["outcome"] != "FIRST_BREAK":
        raise ValueError(f"invalid adapted Reviewer 1 record: {parsed['errors']}")
    return record


def reviewer_3_failure_record(packet: dict[str, str]) -> str:
    record = (
        "CERTIFICATION_FAILURE\n"
        f"critical_obligation: {packet['repair_needed']}\n"
        f"candidate_support: {packet['useful_material']}\n"
        "attempted_completion: The stored Reviewer 3 reasoning considered the "
        "candidate support quoted above but did not establish the required obligation.\n"
        f"why_completion_fails: {packet['selector_reason']}\n"
        "impact_on_conclusion: The selected REAL_GAP is a load-bearing obligation; "
        "the submitted proof cannot be certified while it remains unproved.\n"
        "repair_scope: STRUCTURAL\n"
        f"minimum_required_lemma: {packet['repair_needed']}\n"
        "END_CERTIFICATION_FAILURE"
    )
    parsed = parse_reviewer_3(record)
    if not parsed["valid"] or parsed["outcome"] != "CERTIFICATION_FAILURE":
        raise ValueError(f"invalid enhanced Reviewer 3 record: {parsed['errors']}")
    return record


def recover_role_label_only_fusion_result(
    output_dir: Path, task: dict[str, Any]
) -> dict[str, Any] | None:
    """Recover only deterministic reviewer-role label inconsistencies."""
    destination = fusion.task_output_dir(output_dir, task)
    result_path = destination / "result.json"
    if result_path.is_file():
        return None
    candidates = [
        destination / "fusion_protocol_repair.raw_response.json",
        destination / "fusion.raw_response.json",
    ]
    raw_path = next((path for path in candidates if path.is_file()), None)
    if raw_path is None:
        return None
    payload = load_json(raw_path)
    original = str(payload["choices"][0]["message"].get("content") or "").strip()
    normalized = original
    changes: list[dict[str, str]] = []
    for index, role in enumerate(("reviewer_1", "reviewer_2", "reviewer_3"), start=1):
        source_outcome = str(task["reviewer_sources"][role]["outcome"])
        if source_outcome in NO_DEFECT_OUTCOMES:
            pattern = re.compile(
                rf"(?m)^reviewer_{index}_assessment: "
                r"(DEFECT_VALIDATED|DEFECT_REJECTED|DEFECT_UNRESOLVED) \| ([^\n]+)$"
            )
            match = pattern.search(normalized)
            if match is None:
                continue
        elif source_outcome in DEFECT_OUTCOMES:
            pattern = re.compile(
                rf"(?m)^reviewer_{index}_assessment: "
                r"(NO_DEFECT_REPORTED|REVIEWER_MISSED_DEFECT) \| ([^\n]+)$"
            )
            match = pattern.search(normalized)
            if match is None:
                continue
        else:
            continue
        reason = match.group(2)
        new_label = canonical_role_label(
            source_outcome=source_outcome,
            model_label=match.group(1),
            reason=reason,
        )
        if new_label is None:
            continue
        replacement = f"reviewer_{index}_assessment: {new_label} | {reason}"
        normalized = normalized[: match.start()] + replacement + normalized[match.end() :]
        changes.append(
            {
                "role": role,
                "source_outcome": source_outcome,
                "old_label": match.group(1),
                "new_label": new_label,
                "reason_preserved": reason,
            }
        )
    if not changes:
        return None
    parsed = fusion.parse_task_output(normalized, task)
    if not parsed["valid"]:
        raise ValueError(f"role-label-only recovery did not validate: {parsed['errors']}")
    user_prompt = fusion.fusion_user_prompt(
        problem=task["problem"],
        proof=task["proof"],
        reviewer_1=task["reviewer_1"],
        reviewer_2=task["reviewer_2"],
        reviewer_3=task["reviewer_3"],
    )
    base = fusion._base
    identity = {
        **base.public_task(task),
        "model": task["model_name"],
        "system_prompt_sha256": sha256_text(fusion.SYSTEM_PROMPT),
        "user_prompt_sha256": sha256_text(user_prompt),
        "max_output_tokens": base.MAX_OUTPUT_TOKENS,
        "cap_recovery_max_output_tokens": base.CAP_RECOVERY_MAX_OUTPUT_TOKENS,
        "top_p": base.TOP_P,
        "top_k": base.TOP_K,
        "thinking_enabled": True,
        "reasoning_effort": base.REASONING_EFFORT,
    }
    generation = load_json(destination / "fusion.metadata.json")
    final_generation_path = destination / "fusion_protocol_repair.metadata.json"
    final_generation = (
        load_json(final_generation_path) if final_generation_path.is_file() else generation
    )
    reasoning_parts = []
    for name in ("fusion.reasoning.txt", "fusion_protocol_repair.reasoning.txt"):
        path = destination / name
        if path.is_file() and path.read_text(encoding="utf-8").strip():
            reasoning_parts.append(path.read_text(encoding="utf-8").strip())
    reasoning = "\n\n[CONTINUATION]\n\n".join(reasoning_parts)
    result = {
        "schema": base.RESULT_SCHEMA,
        "identity": identity,
        "task": base.public_task(task),
        "final": normalized,
        "final_sha256": sha256_text(normalized),
        "final_normalization": {
            "applied": True,
            "model_final_sha256": sha256_text(original),
            "policy": "v0.3.93 deterministic reviewer-role label normalization",
        },
        "parsed": parsed,
        "thinking_requested": True,
        "thinking_observed": bool(reasoning),
        "reasoning_sha256": sha256_text(reasoning),
        "generation": generation,
        "final_generation": final_generation,
        "recovery": {
            "triggered": True,
            "v093_role_label_only": {
                "source_response_path": str(raw_path.resolve()),
                "source_response_sha256": sha256_text(
                    raw_path.read_text(encoding="utf-8")
                ),
                "changes": changes,
                "mathematical_fields_modified": False,
            },
        },
        "response_source": "deterministic_role_label_recovery",
        "completed_at": utc_now(),
    }
    write_json(result_path, result)
    (destination / "final.txt").write_text(normalized + "\n", encoding="utf-8")
    return result
