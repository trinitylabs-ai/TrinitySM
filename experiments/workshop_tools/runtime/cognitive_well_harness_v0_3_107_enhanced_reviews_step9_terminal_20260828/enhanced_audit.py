from __future__ import annotations

import copy
from collections import Counter
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import (
    write_json,
)
from cognitive_well_harness_v0_3_81_iterative_dual_memory_loop_20260825 import (
    pipeline as v081,
)
from cognitive_well_harness_v0_3_96_generic_enhanced_review_fusion_resolver_20260827 import (
    run as v096,
)


def run_enhanced_review_fusion_dag(
    *,
    run_input: dict[str, Any],
    candidates: list[dict[str, Any]],
    gemma_endpoint: str,
    qwen_endpoint: str,
    output_dir: Path,
    seed_namespace: str,
) -> list[dict[str, Any]]:
    """Run enhanced R1/R3, frozen Qwen R2, then frozen Fusion in batches."""
    problem = str(run_input["problem"])
    problem_id = str(run_input["problem_id"])
    problem_number = v096.problem_number_from(problem_id)
    cases: list[dict[str, Any]] = []
    for proof_index, candidate in enumerate(candidates):
        cases.append(
            {
                "case_id": f"{problem_id}.{candidate['candidate_id']}",
                "mode": "fresh",
                "proof_index": proof_index,
                "problem_number": problem_number,
                "problem_id": problem_id,
                "candidate_id": str(candidate["candidate_id"]),
                "problem_path": "inline:run_input",
                "problem": problem,
                "problem_sha256": v081.sha256_text(problem),
                "proof_path": str(candidate["proof_path"]),
                "proof": str(candidate["proof"]),
                "proof_sha256": str(candidate["proof_sha256"]),
                "reviews": {},
            }
        )

    v096.run_fresh_reviews(
        cases=cases,
        output_dir=output_dir,
        gemma_endpoints=[gemma_endpoint],
        qwen_endpoint=qwen_endpoint,
        workers_per_endpoint=4,
        seed_namespace=seed_namespace,
    )
    v096.run_enhancements(
        cases=cases,
        output_dir=output_dir,
        gemma_endpoints=[gemma_endpoint],
        workers_per_endpoint=4,
        seed_namespace=seed_namespace,
    )
    for case in cases:
        case["fusion_task"] = v096.build_fusion_task(
            case,
            endpoint=gemma_endpoint,
            gpu=0,
            seed_namespace=seed_namespace,
        )
        lane = output_dir / "cases" / case["case_id"]
        lane.mkdir(parents=True, exist_ok=True)
        for role in ("reviewer_1", "reviewer_2", "reviewer_3"):
            (lane / f"effective_{role}.txt").write_text(
                str(case["fusion_task"][role]).strip() + "\n", encoding="utf-8"
            )

    def fusion_call(job: dict[str, Any]) -> None:
        case = job["case"]
        lane = output_dir / "cases" / case["case_id"]
        try:
            result = v096.fusion.run_task(output_dir=lane, task=case["fusion_task"])
        except ValueError:
            result = v096.recover_role_label_only_fusion_result(
                lane, case["fusion_task"]
            )
            if result is None:
                raise
        case["fusion_result"] = result

    v096.run_parallel(
        name="enhanced_fusion",
        jobs=[{"job_id": case["case_id"], "case": case} for case in cases],
        max_workers=4,
        task=fusion_call,
    )

    source_by_id = {str(row["candidate_id"]): row for row in candidates}
    audited: list[dict[str, Any]] = []
    for case in cases:
        candidate_id = str(case["candidate_id"])
        qwen = case["reviews"]["reviewer_2"]
        fused = case["fusion_result"]
        row = {
            **copy.deepcopy(source_by_id[candidate_id]),
            "qwen_defect_packet": v081._audit_packet(qwen),
            "fusion_defect_packet": v081._audit_packet(fused),
            "qwen_final": qwen["final"],
            "fusion_final": fused["final"],
            "qwen_outcome": qwen["parsed"]["outcome"],
            "fusion_outcome": fused["parsed"]["outcome"],
            "review_outcomes": {
                role: case["reviews"][role].get(
                    "effective_outcome", case["reviews"][role]["outcome"]
                )
                for role in ("reviewer_1", "reviewer_2", "reviewer_3")
            },
            "enhanced_review_routes": {
                role: (case["reviews"][role].get("enhancement") or {}).get("route")
                for role in ("reviewer_1", "reviewer_3")
            },
        }
        audited.append(row)

    write_json(
        output_dir / "schedule.json",
        {
            "policy": "enhanced_R1_and_Qwen_R2_concurrent_then_enhanced_R3_then_Fusion",
            "candidate_count": len(candidates),
            "gemma_batch_width": 4,
            "qwen_batch_width": 4,
            "reviewer_1_enhancement": "0.3.89",
            "reviewer_3_enhancement": "0.3.92",
            "problem_specific_prompting": False,
        },
    )
    write_json(
        output_dir / "summary.json",
        {
            "candidate_count": len(audited),
            "reviewer_outcomes": {
                role: dict(Counter(str(row["review_outcomes"][role]) for row in audited))
                for role in ("reviewer_1", "reviewer_2", "reviewer_3")
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
                    "enhanced_review_routes": row["enhanced_review_routes"],
                    "qwen_outcome": row["qwen_outcome"],
                    "fusion_outcome": row["fusion_outcome"],
                }
                for row in audited
            ],
        },
    )
    return audited

