from __future__ import annotations

import concurrent.futures
from pathlib import Path
from typing import Any

from .lemma_proving import compact_certify
from .model_runtime import ModelRuntime, write_json


def evaluate_candidate(
    *,
    runtime: ModelRuntime,
    problem: str,
    candidate: dict[str, Any],
    gate_policy: dict[str, Any],
    output_dir: Path,
) -> dict[str, Any]:
    candidate_id = str(candidate["candidate_id"])
    structural = candidate["assembly"]["structural_gate"]
    certification: dict[str, Any] | None = None
    if structural["passed"] and gate_policy["require_qwen_certification"]:
        certification = compact_certify(
            runtime=runtime,
            problem=problem,
            claim=problem,
            proof=str(candidate["proof"]),
            output_dir=output_dir / candidate_id,
            stage_prefix="final_proof",
            seed_label=f"final_gate:{candidate_id}",
        )
    mathematical_pass = (
        certification is not None and certification["certified"]
        if gate_policy["require_qwen_certification"]
        else True
    )
    result = {
        "candidate_id": candidate_id,
        "structural_gate": structural,
        "qwen_certification_required": gate_policy["require_qwen_certification"],
        "qwen_certification": certification,
        "passed": bool(structural["passed"] and mathematical_pass),
    }
    write_json(output_dir / candidate_id / "gate_result.json", result)
    return result


def evaluate_all(
    *,
    runtime: ModelRuntime,
    problem: str,
    candidates: list[dict[str, Any]],
    gate_policy: dict[str, Any],
    output_dir: Path,
) -> list[dict[str, Any]]:
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        return list(
            executor.map(
                lambda candidate: evaluate_candidate(
                    runtime=runtime,
                    problem=problem,
                    candidate=candidate,
                    gate_policy=gate_policy,
                    output_dir=output_dir,
                ),
                candidates,
            )
        )

