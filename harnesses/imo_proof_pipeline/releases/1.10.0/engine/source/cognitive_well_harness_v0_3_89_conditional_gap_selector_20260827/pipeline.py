from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import (
    write_json,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.pipeline import (
    utc_now,
)
from cognitive_well_harness_v0_3_84_trace_resolution_batch_20260827 import (
    pipeline as v084,
)

from . import MODEL


LABELS = ("REAL_GAP", "ROUTINE", "UNSUPPORTED")


GAP_SELECTOR_SYSTEM_PROMPT = r"""You are a conservative olympiad proof-gap
classifier. You receive the original problem, complete submitted proof, and trace
candidates extracted verbatim from a prior reviewer's reasoning.

For every candidate, independently check only whether its stated objection identifies
an unresolved, load-bearing defect in the submitted proof. Assign exactly one label:

- REAL_GAP: the candidate identifies a mathematically genuine missing premise,
  invalid inference, circular step, quantifier failure, or uncovered case that the
  submitted proof itself does not close.
- ROUTINE: the candidate asks only for standard Olympiad-level elaboration, or the
  submitted proof already closes the stated obligation.
- UNSUPPORTED: the objection is false, irrelevant, too vague to verify, or depends on
  a claim not established by the trace candidate.

Judge the objection, not whether you can repair it. A real gap remains REAL_GAP even
when the candidate supplies no repair or supplies a bad repair. Do not solve the
problem, construct a replacement argument, strengthen the candidate, rewrite the
proof, or certify any proposed repair. The original trace packet—not new mathematics
from this call—is what a later resolver will receive.

Classify the proof obligation, not an isolated sentence. A defective justification
is REAL_GAP only when removing it leaves the associated load-bearing claim
unsupported by material already established earlier in the submitted proof. Do not
supply new reasoning to close it. The fact that a missing argument would be short or
routine does not make an unsupported load-bearing claim ROUTINE.

Return compact Markdown in exactly this layout, with one section per supplied gap in
the same order:

## TG1
- Label: REAL_GAP | ROUTINE | UNSUPPORTED
- Reason: one concise explanation tied to the submitted proof

After all sections return:

## Summary
one concise sentence

Do not return JSON, fenced code, a repaired proof, a lemma, or a certified argument.
Do not omit a section.

HIGH-STAKES DELIBERATION REQUIREMENT

Spare no effort. Use the maximum reasoning effort available. Re-check the exact
proof location before assigning the label."""


FORMAT_RETRY_SYSTEM_PROMPT = GAP_SELECTOR_SYSTEM_PROMPT + r"""

FORMAT RETRY

The preceding response was not parseable. Repeat the same classification from
scratch and return only the required two-field Markdown sections and Summary."""


def selector_user_prompt(
    *, problem: str, proof: str, packets: list[dict[str, str]]
) -> str:
    if not problem.strip() or not proof.strip():
        raise ValueError("problem and proof must be nonempty")
    blocks = []
    for packet in packets:
        blocks.append(
            "## "
            + str(packet["gap_id"])
            + "\n- Useful material: "
            + (str(packet.get("useful_material") or "(none)"))
            + "\n- Repair needed: "
            + str(packet["repair_needed"])
            + "\n- Extraction reason: "
            + str(packet["reason"])
        )
    return (
        "# GAP CLASSIFICATION INPUT\n\n"
        "## ORIGINAL PROBLEM\n"
        + problem.strip()
        + "\n\n## SUBMITTED PROOF\n"
        + proof.strip()
        + "\n\n## EXTRACTED TRACE CANDIDATES\n"
        + "\n\n".join(blocks)
        + "\n\nClassify every supplied candidate now.\n"
    )


def parse_gap_selector(
    value: str, packets: list[dict[str, str]]
) -> dict[str, Any]:
    text = value.strip()
    section_re = re.compile(
        r"(?ms)^##\s+(TG[0-9]+)\s*$\n(.*?)(?=^##\s+(?:TG[0-9]+|Summary)\s*$|\Z)"
    )
    decisions: list[dict[str, str]] = []
    for match in section_re.finditer(text):
        gap_id, body = match.group(1), match.group(2).strip()
        label_match = re.search(
            r"(?im)^\s*-\s*(?:\*\*)?Label(?:\*\*)?\s*:\s*`?"
            r"(REAL_GAP|ROUTINE|UNSUPPORTED)`?\s*$",
            body,
        )
        reason_match = re.search(
            r"(?ims)^\s*-\s*(?:\*\*)?Reason(?:\*\*)?\s*:\s*(.*?)\s*$",
            body,
        )
        if not label_match or not reason_match:
            raise ValueError(f"incomplete gap-selector section: {gap_id}")
        reason = reason_match.group(1).strip()
        if not reason:
            raise ValueError(f"empty gap-selector reason: {gap_id}")
        decisions.append(
            {
                "gap_id": gap_id,
                "label": label_match.group(1).upper(),
                "reason": reason,
            }
        )
    summary_match = re.search(r"(?ims)^##\s+Summary\s*$\n(.*?)\s*$", text)
    if not summary_match:
        raise ValueError("gap-selector response lacks Summary")
    expected_ids = [str(packet["gap_id"]) for packet in packets]
    actual_ids = [str(row["gap_id"]) for row in decisions]
    if actual_ids != expected_ids:
        raise ValueError(
            f"gap-selector IDs/order mismatch: expected {expected_ids}, got {actual_ids}"
        )
    if any(row["label"] not in LABELS for row in decisions):
        raise ValueError("gap-selector returned an unknown label")
    return {"decisions": decisions, "summary": summary_match.group(1).strip()}


def run_gap_selector(
    *,
    problem: str,
    proof: str,
    packets: list[dict[str, str]],
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
    if not packets:
        result = {
            "schema": "cognitive-well-v089-gap-selector-result-v1",
            "state": "completed",
            "completed_at": utc_now(),
            "model_call_count": 0,
            "packet_count": 0,
            "real_gap_count": 0,
            "routine_count": 0,
            "unsupported_count": 0,
            "decisions": [],
            "summary": "No trace candidates were extracted.",
            "generation": None,
            "runtime_recovery_events": [],
            "format_retry": False,
        }
        write_json(result_path, result)
        return result

    runtime = v084.runtime_for(endpoint, seed, model)
    user_prompt = selector_user_prompt(problem=problem, proof=proof, packets=packets)
    format_retry = False
    try:
        generated = runtime.text(
            role="gemma",
            prompt=GAP_SELECTOR_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            destination=output_dir / "generation",
            stage="gap_selector",
            temperature=0.1,
            max_tokens=32_768,
            seed_label=seed_label,
            top_p=1.0,
            top_k=-1,
        )
        record = parse_gap_selector(str(generated["text"]), packets)
    except Exception as primary_error:
        format_retry = True
        retry_runtime = v084.runtime_for(endpoint, seed + 1_000_003, model)
        generated = retry_runtime.text(
            role="gemma",
            prompt=FORMAT_RETRY_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            destination=output_dir / "generation",
            stage="gap_selector_format_retry",
            temperature=0.1,
            max_tokens=32_768,
            seed_label=seed_label + ":format_retry",
            top_p=1.0,
            top_k=-1,
        )
        record = parse_gap_selector(str(generated["text"]), packets)
        retry_runtime._recovery_events.append(
            {
                "kind": "format_retry",
                "stage": "gap_selector",
                "accepted": True,
                "prior_error": f"{type(primary_error).__name__}: {primary_error}",
                "attempts": [],
            }
        )
        runtime = retry_runtime

    decisions = list(record["decisions"])
    result = {
        "schema": "cognitive-well-v089-gap-selector-result-v1",
        "state": "completed",
        "completed_at": utc_now(),
        "model_call_count": 1 + int(format_retry),
        "packet_count": len(packets),
        "real_gap_count": sum(row["label"] == "REAL_GAP" for row in decisions),
        "routine_count": sum(row["label"] == "ROUTINE" for row in decisions),
        "unsupported_count": sum(
            row["label"] == "UNSUPPORTED" for row in decisions
        ),
        "decisions": decisions,
        "summary": str(record["summary"]),
        "generation": generated["metadata"],
        "runtime_recovery_events": runtime.recovery_events(),
        "format_retry": format_retry,
    }
    write_json(result_path, result)
    return result


__all__ = [
    "GAP_SELECTOR_SYSTEM_PROMPT",
    "LABELS",
    "parse_gap_selector",
    "run_gap_selector",
    "selector_user_prompt",
]
