from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import (
    RuntimeConfig,
    write_json,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.pipeline import (
    utc_now,
)
from cognitive_well_harness_v0_3_81_iterative_dual_memory_loop_20260825 import (
    pipeline as v081,
)
from cognitive_well_harness_v0_3_83_batched_dependency_dag_20260826 import (
    pipeline as v083,
)
from cognitive_well_harness_v0_3_96_generic_enhanced_review_fusion_resolver_20260827 import (
    GEMMA_MODEL,
    QWEN_MODEL,
)
from cognitive_well_harness_v0_3_96_generic_enhanced_review_fusion_resolver_20260827 import (
    run as v096,
)

from . import HARNESS_VERSION


def parse_candidate(value: str) -> tuple[str, Path]:
    candidate_id, separator, raw_path = value.partition("=")
    if not separator or not candidate_id.strip() or not raw_path.strip():
        raise argparse.ArgumentTypeError("candidate must have the form ID=PROOF_PATH")
    path = Path(raw_path).expanduser().resolve()
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"proof does not exist: {path}")
    return candidate_id.strip(), path


def packet(result: dict[str, Any]) -> dict[str, Any]:
    value = v081._audit_packet(result)
    if not value.get("outcome"):
        raise ValueError("audit result has no parsed outcome")
    return value


def prepare_seed_state(
    *,
    problem_path: Path,
    problem_id: str,
    candidates: list[tuple[str, Path]],
    output_dir: Path,
    gemma_endpoint: str,
    qwen_endpoint: str,
    workers: int,
    seed_namespace: str,
    allowed_source_root: Path | None = None,
) -> Path:
    if len(candidates) != 2:
        raise ValueError("exactly two candidates are required")
    problem_path = problem_path.resolve()
    if not problem_path.is_file():
        raise FileNotFoundError(problem_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    allowed_source_root = (
        allowed_source_root.resolve()
        if allowed_source_root is not None
        else output_dir.parent.resolve()
    )
    v096.require_within(allowed_source_root, problem_path, "seed-audit problem")
    for candidate_id, proof_path in candidates:
        v096.require_within(
            allowed_source_root,
            proof_path,
            f"seed-audit candidate {candidate_id}",
        )
    cases_manifest_path = output_dir / "cases_manifest.json"
    cases_manifest = {
        "schema": "cognitive-well-v0106-fresh-seed-audit-cases-v1",
        "problem_specific_prompting": False,
        "cases": [
            {
                "case_id": f"{problem_id}.{candidate_id}",
                "mode": "fresh",
                "problem_id": problem_id,
                "candidate_id": candidate_id,
                "problem_path": str(problem_path),
                "proof_path": str(proof_path),
                "proof_index": index,
            }
            for index, (candidate_id, proof_path) in enumerate(candidates)
        ],
    }
    write_json(cases_manifest_path, cases_manifest)
    _, cases = v096.load_cases(
        cases_manifest_path, allowed_input_root=allowed_source_root
    )
    manifest = {
        "schema": "cognitive-well-v0106-fresh-seed-audit-memory-bridge-manifest-v1",
        "harness_version": HARNESS_VERSION,
        "created_at": utc_now(),
        "problem_id": problem_id,
        "problem_path": str(problem_path),
        "candidate_count": len(cases),
        "candidate_ids": [case["candidate_id"] for case in cases],
        "models": {"gemma": GEMMA_MODEL, "qwen": QWEN_MODEL},
        "runtime": {
            "gemma_endpoint": gemma_endpoint,
            "qwen_endpoint": qwen_endpoint,
            "gemma_precision": "BF16",
            "gemma_mtp_speculative_tokens": 4,
            "workers": workers,
        },
        "review_architecture": {
            "reviewer_1": "v0.3.89 conditional trace extraction and selector",
            "reviewer_2": "v0.3.50 Qwen adversarial audit",
            "reviewer_3": "v0.3.92 scope-matched trace extraction and selector",
            "fusion": "v0.3.53 at temperature 0.4",
            "resolver": "not run during seed refresh",
        },
        "problem_specific_prompting": False,
        "gold_or_codex_feedback_supplied": False,
        "source_proofs": [
            {
                "candidate_id": case["candidate_id"],
                "proof_path": case["proof_path"],
                "proof_sha256": case["proof_sha256"],
            }
            for case in cases
        ],
    }
    write_json(output_dir / "manifest.json", manifest)
    write_json(
        output_dir / "status.json",
        {"state": "running", "stage": "fresh_reviews", "updated_at": utc_now()},
    )
    v096.run_fresh_reviews(
        cases=cases,
        output_dir=output_dir,
        gemma_endpoints=[gemma_endpoint],
        qwen_endpoint=qwen_endpoint,
        workers_per_endpoint=workers,
        seed_namespace=seed_namespace,
    )
    write_json(
        output_dir / "status.json",
        {"state": "running", "stage": "reviewer_enhancements", "updated_at": utc_now()},
    )
    v096.run_enhancements(
        cases=cases,
        output_dir=output_dir,
        gemma_endpoints=[gemma_endpoint],
        workers_per_endpoint=workers,
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

    write_json(
        output_dir / "status.json",
        {"state": "running", "stage": "fusion", "updated_at": utc_now()},
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
        name="seed_fusion",
        jobs=[{"job_id": case["case_id"], "case": case} for case in cases],
        max_workers=workers,
        task=fusion_call,
    )

    initial_state = {
        "schema": "cognitive-well-v0106-v083-initial-state-v1",
        "problem_id": problem_id,
        "problem": cases[0]["problem"],
        "candidate_proofs": [
            {
                "candidate_id": case["candidate_id"],
                "role": "anchor" if index == 0 else "supplement",
                "proof_path": case["proof_path"],
                "proof_sha256": case["proof_sha256"],
                "qwen_defect_packet": packet(case["reviews"]["reviewer_2"]),
                "fusion_defect_packet": packet(case["fusion_result"]),
                "seed_audit": {
                    "reviewer_1_outcome": case["reviews"]["reviewer_1"].get(
                        "effective_outcome", case["reviews"]["reviewer_1"]["outcome"]
                    ),
                    "reviewer_2_outcome": case["reviews"]["reviewer_2"]["outcome"],
                    "reviewer_3_outcome": case["reviews"]["reviewer_3"].get(
                        "effective_outcome", case["reviews"]["reviewer_3"]["outcome"]
                    ),
                    "fusion_outcome": case["fusion_result"]["parsed"]["outcome"],
                },
            }
            for index, case in enumerate(cases)
        ],
    }
    initial_state_path = output_dir / "initial_state.json"
    write_json(initial_state_path, initial_state)
    # Exercise the downstream loader before declaring the bridge complete.
    loaded = v083.load_initial_state(initial_state_path)
    summary = {
        "schema": "cognitive-well-v0106-fresh-seed-audit-memory-bridge-summary-v1",
        "harness_version": HARNESS_VERSION,
        "state": "completed",
        "completed_at": utc_now(),
        "initial_state_path": str(initial_state_path.resolve()),
        "validated_candidate_count": len(loaded["candidate_proofs"]),
        "rows": [
            {
                "candidate_id": row["candidate_id"],
                "proof_sha256": row["proof_sha256"],
                **row["seed_audit"],
            }
            for row in initial_state["candidate_proofs"]
        ],
    }
    write_json(output_dir / "summary.json", summary)
    write_json(
        output_dir / "status.json",
        {"state": "completed", "stage": "done", "updated_at": utc_now()},
    )
    return initial_state_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Refresh enhanced audits for two proof seeds and launch v0.3.83"
    )
    parser.add_argument("--problem-path", type=Path, required=True)
    parser.add_argument("--problem-id", required=True)
    parser.add_argument("--candidate", action="append", type=parse_candidate, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--memory-output-dir", type=Path)
    parser.add_argument("--gemma-endpoint", default="http://127.0.0.1:8030/v1")
    parser.add_argument("--qwen-endpoint", default="http://127.0.0.1:8027/v1")
    parser.add_argument("--salvage-verifier-endpoint")
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--master-seed", type=int, default=20260828)
    parser.add_argument("--seed-namespace", default="v0106")
    args = parser.parse_args()
    if len(args.candidate) != 2:
        parser.error("--candidate must be supplied exactly twice")
    gemma_endpoint = args.gemma_endpoint.rstrip("/")
    qwen_endpoint = args.qwen_endpoint.rstrip("/")
    output_dir = args.output_dir.resolve()
    initial_state_path = prepare_seed_state(
        problem_path=args.problem_path,
        problem_id=args.problem_id,
        candidates=args.candidate,
        output_dir=output_dir,
        gemma_endpoint=gemma_endpoint,
        qwen_endpoint=qwen_endpoint,
        workers=args.workers,
        seed_namespace=args.seed_namespace,
    )
    if args.memory_output_dir is None:
        print(json.dumps({"initial_state_path": str(initial_state_path)}, indent=2))
        return
    memory_output_dir = args.memory_output_dir.resolve()
    initial_state = v083.load_initial_state(initial_state_path)
    result = v083.run_pipeline(
        initial_state=initial_state,
        source_run_dir=output_dir,
        output_dir=memory_output_dir,
        runtime_config=RuntimeConfig(
            gemma_endpoint=gemma_endpoint,
            qwen_endpoint=qwen_endpoint,
            master_seed=args.master_seed,
        ),
        salvage_verifier_endpoint=(
            args.salvage_verifier_endpoint or gemma_endpoint
        ).rstrip("/"),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
