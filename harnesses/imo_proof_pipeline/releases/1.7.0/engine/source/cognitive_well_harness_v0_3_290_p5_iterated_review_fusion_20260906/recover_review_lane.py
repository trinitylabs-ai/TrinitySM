"""Recover a timed-out R1 review lane without touching other running lanes."""
from __future__ import annotations

import argparse
import fcntl
from pathlib import Path

from . import pipeline as p
from .score_when_ready import read_live, stage_directory


def recovery_inputs(root: Path, candidate: str) -> tuple[dict, int, dict, Path]:
    manifest = p.read_object(root / "manifest.json")
    if candidate not in manifest["candidate_ids"]:
        raise ValueError("candidate is not in the frozen portfolio")
    p.configure_problem_binding(
        problem_id=manifest["problem_id"], problem_number=int(manifest.get("problem_number", 5)),
        problem_sha256=manifest["frozen_inputs"]["problem_text_sha256"],
        candidate_ids=tuple(manifest["candidate_ids"]),
    )
    failure = p.read_object(root / "lanes" / candidate / "failure.json")
    checkpoint = str(failure.get("stage", ""))
    if (failure.get("state") != "failed_closed" or checkpoint not in {"R1-C1", "R1-C2", "R1-C3"}
            or "fresh_reviewer_2 failures:" not in failure.get("error", "")
            or "TimeoutError:" not in failure.get("error", "")):
        raise ValueError("recovery is restricted to a recorded Reviewer2 timeout")
    outer = read_live(root / "status.json") or {}
    # The parent may still list the failed lane until its cycle barrier clears.
    if outer.get("stage") == checkpoint and candidate in outer.get("active_lanes", []):
        raise ValueError("wait for the parent to leave the failed cycle")
    cycle = int(checkpoint[-1])
    partial = stage_directory(root, candidate, checkpoint)
    if (p.read_object(partial / "status.json").get("stage") != "fresh_reviews"
            or any((partial / "cases").glob("*/fusion*"))):
        raise ValueError("recovery must not repeat Fusion or its gate")
    for later in range(cycle + 1, 4):
        if stage_directory(root, candidate, f"R1-C{later}").exists():
            raise ValueError("failed lane has later cycle work")
    if (root / "lanes" / candidate / "04_post_r1_cycle3_audit_ledger").exists():
        raise ValueError("failed lane has downstream work")
    problem = p._require_child(root, Path(manifest["frozen_inputs"]["problem_path"]), "problem")
    if p.file_sha256(problem) != manifest["frozen_inputs"]["problem_file_sha256"]:
        raise ValueError("problem file drift")
    proof, = [r for r in manifest["frozen_inputs"]["lanes"] if r["candidate_id"] == candidate]
    p._proof_identity(proof, allowed_root=root, label="recovery baseline")
    for prior in range(1, cycle):
        proof = p._terminal_r1_proofs(
            stage_dir=stage_directory(root, candidate, f"R1-C{prior}"), allowed_root=root,
            expected_candidates=(candidate,), model_timeout_sec=manifest["runtime"]["model_timeout_sec"],
        )[0]
    return manifest, cycle, proof, problem


def recover(*, root: Path, candidate: str) -> None:
    root = root.resolve()
    manifest, first, proof, problem = recovery_inputs(root, candidate)
    lane = root / "lanes" / candidate
    lock = (lane / "review_recovery.lock").open("a")
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    journal = p._unused_resume_path(lane / "mechanical_review_recovery")
    journal.mkdir()
    for name in ("failure.json", "status.json"):
        if (lane / name).is_file():
            (lane / name).rename(journal / name)
    runtime = manifest["runtime"]
    p.write_json(journal / "manifest.json", {
        "source_manifest_sha256": p.file_sha256(root / "manifest.json"),
        "candidate_id": candidate, "first_cycle": first, "runtime": runtime,
        "reviewer2_http_timeout_floor_sec": 2400, "enable_exact_evidence": False,
        "model_prompts_seeds_temperatures_token_caps_changed": False,
        "other_lanes_touched": False, "portfolio_reconciliation_required": True,
        "terminal_checkpoint": p.TERMINAL_CHECKPOINT,
    })
    checkpoints = []
    with p.runtime_generation_policy(model_timeout_sec=runtime["model_timeout_sec"]), p.inherited_component_caps():
        for cycle in range(first, 4):
            key = f"R1-C{cycle}"
            p.write_json(journal / "status.json", {"state": "running", "stage": key})
            try:
                with p.mandatory_repair_boundary(
                    qwen_endpoint=runtime["qwen_endpoint"], gemma_endpoint=runtime["gemma_endpoint"],
                    cycle_key=key, model_timeout_sec=runtime["model_timeout_sec"], enable_exact_evidence=False,
                ):
                    _, proof = p.run_r1_cycle_lane(
                        output_dir=root, candidate_id=candidate, cycle=cycle, source_proof=proof,
                        problem_path=problem, gemma_endpoint=runtime["gemma_endpoint"],
                        qwen_endpoint=runtime["qwen_endpoint"], seed_namespace=runtime["seed_namespace"],
                        model_timeout_sec=runtime["model_timeout_sec"],
                    )
            except Exception as error:
                failure = {"state": "failed_closed", "stage": key, "error": f"{type(error).__name__}: {error}"}
                p.write_json(lane / "failure.json", failure)
                p.write_json(journal / "status.json", failure)
                raise
            checkpoints.append({"checkpoint": key, "proof": proof})
            p.write_json(journal / "checkpoints.json", {"checkpoints": checkpoints})
            print(candidate, key, "completed", flush=True)
    p.write_json(lane / "status.json", {"state": "completed", "stage": p.TERMINAL_CHECKPOINT})
    p.write_json(journal / "status.json", {"state": "completed", "stage": "awaiting_portfolio_reconciliation"})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--execute-models", action="store_true", required=True)
    args = parser.parse_args()
    recover(root=args.run_root, candidate=args.candidate)


if __name__ == "__main__":
    main()
