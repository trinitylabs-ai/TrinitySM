from __future__ import annotations

import json
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
from cognitive_well_harness_v0_3_89_conditional_gap_selector_20260827 import (
    pipeline as frozen_v089,
)

from . import MODEL


SCOPE_MATCHING_RULE = r"""Before assigning a label, compare the exact downstream
claim used by the submitted proof with the scope of what its argument actually
establishes. If the argument proves only a local, one-step, eventual, or special-case
statement while the proof requires a global, recursive, from-the-start, or all-case
statement, label the mismatch REAL_GAP unless the submitted proof itself explicitly
supplies the bridge. Do not construct that bridge yourself."""


_INSERTION_POINT = "Return compact Markdown in exactly this layout"
if frozen_v089.GAP_SELECTOR_SYSTEM_PROMPT.count(_INSERTION_POINT) != 1:
    raise RuntimeError("frozen selector insertion point changed")
GAP_SELECTOR_SYSTEM_PROMPT = frozen_v089.GAP_SELECTOR_SYSTEM_PROMPT.replace(
    _INSERTION_POINT,
    SCOPE_MATCHING_RULE + "\n\n" + _INSERTION_POINT,
)
FORMAT_RETRY_SYSTEM_PROMPT = GAP_SELECTOR_SYSTEM_PROMPT + r"""

FORMAT RETRY

The preceding response was not parseable. Repeat the same classification from
scratch and return only the required two-field Markdown sections and Summary."""


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
            "schema": "cognitive-well-v092-gap-selector-result-v1",
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
    user_prompt = frozen_v089.selector_user_prompt(
        problem=problem, proof=proof, packets=packets
    )
    format_retry = False
    try:
        generated = runtime.text(
            role="gemma",
            prompt=GAP_SELECTOR_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            destination=output_dir / "generation",
            stage="scope_matched_gap_selector",
            temperature=0.1,
            max_tokens=32_768,
            seed_label=seed_label,
            top_p=1.0,
            top_k=-1,
        )
        record = frozen_v089.parse_gap_selector(str(generated["text"]), packets)
    except Exception as primary_error:
        format_retry = True
        retry_runtime = v084.runtime_for(endpoint, seed + 1_000_003, model)
        generated = retry_runtime.text(
            role="gemma",
            prompt=FORMAT_RETRY_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            destination=output_dir / "generation",
            stage="scope_matched_gap_selector_format_retry",
            temperature=0.1,
            max_tokens=32_768,
            seed_label=seed_label + ":format_retry",
            top_p=1.0,
            top_k=-1,
        )
        record = frozen_v089.parse_gap_selector(str(generated["text"]), packets)
        retry_runtime._recovery_events.append(
            {
                "kind": "format_retry",
                "stage": "scope_matched_gap_selector",
                "accepted": True,
                "prior_error": f"{type(primary_error).__name__}: {primary_error}",
                "attempts": [],
            }
        )
        runtime = retry_runtime

    decisions = list(record["decisions"])
    result = {
        "schema": "cognitive-well-v092-gap-selector-result-v1",
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
    "SCOPE_MATCHING_RULE",
    "run_gap_selector",
]

