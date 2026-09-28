from __future__ import annotations

import concurrent.futures
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import write_json

from .runtime import ResilientModelRuntime
from .split_verifier import split_certify


def evaluate_candidate(
    *,
    verifier_runtime: ResilientModelRuntime,
    problem: str,
    candidate: dict[str, Any],
    gate_policy: dict[str, Any],
    output_dir: Path,
) -> dict[str, Any]:
    candidate_id = str(candidate["candidate_id"])
    structural = candidate["assembly"]["structural_gate"]
    certification = None
    required = bool(gate_policy["require_qwen_certification"])
    if structural["passed"] and required:
        certification = split_certify(
            runtime=verifier_runtime,
            problem=problem,
            assigned_claim=problem,
            proof=str(candidate["proof"]),
            output_dir=output_dir / candidate_id,
            seed_label=f"final_gate:{candidate_id}",
        )
    mathematical_pass = (
        bool(certification and certification["assigned_claim_certified"])
        if required
        else True
    )
    result = {
        "candidate_id": candidate_id,
        "structural_gate": structural,
        "split_verifier_required": required,
        "split_verifier": certification,
        "passed": bool(structural["passed"] and mathematical_pass),
    }
    write_json(output_dir / candidate_id / "gate_result.json", result)
    return result


def evaluate_all(
    *,
    verifier_runtime: ResilientModelRuntime,
    problem: str,
    candidates: list[dict[str, Any]],
    gate_policy: dict[str, Any],
    output_dir: Path,
) -> list[dict[str, Any]]:
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        return list(
            executor.map(
                lambda candidate: evaluate_candidate(
                    verifier_runtime=verifier_runtime,
                    problem=problem,
                    candidate=candidate,
                    gate_policy=gate_policy,
                    output_dir=output_dir,
                ),
                candidates,
            )
        )
