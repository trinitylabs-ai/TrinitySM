"""Read-only checkpoint watcher; invoke the existing strict skill per finished proof."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

from . import pipeline
from scripts import run_v097_p145_gold_informed_calibrated_codex_scores_20260827 as scorer


def read_live(path: Path) -> dict | None:
    try:
        return pipeline.read_object(path)
    except (FileNotFoundError, json.JSONDecodeError):
        return None  # Source ledgers are not all written atomically.


def stage_directory(root: Path, candidate: str, checkpoint: str) -> Path:
    lane = root / "lanes" / candidate
    if checkpoint in pipeline.STAGE_ORDER:
        cycle = int(checkpoint.removeprefix("R1-C"))
        return lane / f"{cycle:02d}_r1_cycle_{cycle}"
    # Read-only compatibility for explicitly recorded historical checkpoints.
    # New manifests schedule only R1-C1 through R1-C3.
    if checkpoint not in {"R2", "R3"}:
        raise ValueError(f"unsupported checkpoint: {checkpoint}")
    return lane / {"R2": "05_resolver2", "R3": "06_resolver3"}[checkpoint]


def ready_proof(
    root: Path, candidate: str, checkpoint: str, manifest: dict, prior: dict
) -> dict | None:
    if checkpoint not in manifest.get("stage_order", pipeline.STAGE_ORDER):
        raise ValueError(f"checkpoint is not scheduled by this run: {checkpoint}")
    stage_dir = stage_directory(root, candidate, checkpoint)
    summary = read_live(stage_dir / "summary.json")
    if summary is None or summary.get("state") != "completed":
        return None
    common = dict(
        allowed_root=root, expected_candidates=(candidate,),
        model_timeout_sec=manifest["runtime"]["model_timeout_sec"],
    )
    if checkpoint.startswith("R1-C"):
        return pipeline._terminal_r1_proofs(stage_dir=stage_dir, **common)[0]
    upstream = "R1-C3" if checkpoint == "R2" else "R2"
    if (candidate, upstream) not in prior:
        return None
    common["expected_sources"] = [prior[candidate, upstream]]
    lane = root / "lanes" / candidate
    gate = lane / "04_post_r1_cycle3_audit_ledger"
    seed = manifest["runtime"]["seed_namespace"]
    if checkpoint == "R2":
        result = pipeline._second_checkpoint(
            stage_dir, source_run=gate,
            seed_namespace=f"{seed}:{candidate}:resolver2", **common,
        )
    else:
        result = pipeline._third_checkpoint(
            stage_dir, resolve_run=lane / "05_resolver2", prior_gate_run=gate,
            seed_namespace=f"{seed}:{candidate}:resolver3", **common,
        )
    return result["proofs"][0]


def scoring_command(*, launcher: Path, proof: Path, output: Path, problem_id: str,
                    candidate: str) -> list[str]:
    return [sys.executable, str(launcher), "--proof-task",
            f"{problem_id}:{candidate}={proof}", "--output-dir", str(output),
            "--workers", "1"]


def run(*, root: Path, output: Path, launcher: Path, workers: int = 4,
        poll_seconds: float = 15, resume: bool = False) -> None:
    root, output, launcher = root.resolve(), output.resolve(), launcher.resolve()
    if workers < 1 or poll_seconds <= 0 or not launcher.is_file():
        raise ValueError("invalid watcher configuration")
    if root == output or root in output.parents or output in root.parents:
        raise ValueError("scoring output must be separate from the model run")
    manifest = pipeline.read_object(root / "manifest.json")
    pipeline.configure_problem_binding(
        problem_id=manifest["problem_id"], problem_number=int(manifest.get("problem_number", 5)),
        problem_sha256=manifest["frozen_inputs"]["problem_text_sha256"],
        candidate_ids=tuple(manifest["candidate_ids"]),
    )
    output.mkdir(parents=True, exist_ok=resume)
    candidates = manifest["candidate_ids"]
    checkpoints = manifest["stage_order"]
    problem_id = manifest["problem_id"]
    prior, records, active = {}, {}, {}
    score_manifest = {
        "source_run": str(root), "skill_launcher": str(launcher),
        "candidate_ids": candidates, "checkpoints": checkpoints,
        "model": scorer.MODEL, "reasoning_effort": "xhigh", "policy_mode": "strict",
        "scores_model_visible": False, "workers": workers,
    }
    if resume:
        if pipeline.read_object(output / "manifest.json") != score_manifest:
            raise ValueError("scoring resume changes configuration")
        records = (read_live(output / "status.json") or {}).get("records", {})
        if any(row.get("state") == "running" for row in records.values()):
            raise ValueError("cannot duplicate a previously running grading call")
        for checkpoint in checkpoints:
            for candidate in candidates:
                record = records.get(f"{checkpoint}/{candidate}")
                if not record or record.get("state") != "completed":
                    continue
                proof = ready_proof(root, candidate, checkpoint, manifest, prior)
                if proof is None or proof["proof_sha256"] != record["proof_sha256"]:
                    raise ValueError("previously scored proof changed")
                snapshot = Path(record["submitted_proof"])
                if pipeline.sha256_text(snapshot.read_text().strip()) != record["proof_sha256"]:
                    raise ValueError("previous score snapshot changed")
                prior[candidate, checkpoint] = proof
        if (output / "summary.json").exists():
            index = 1
            while (output / f"prior_completion_{index:02d}.json").exists():
                index += 1
            (output / "summary.json").rename(output / f"prior_completion_{index:02d}.json")
    else:
        pipeline.write_json(output / "manifest.json", score_manifest)
    while True:
        for key, (process, log) in list(active.items()):
            code = process.poll()
            if code is None:
                continue
            log.close()
            del active[key]
            record = records[key]
            summary = read_live(Path(record["output_dir"]) / "summary.json")
            record.update(returncode=code, state="failed")
            if code == 0 and summary and summary.get("state") == "completed":
                if (summary.get("policy_mode") == "strict"
                        and summary.get("reasoning_effort") == "xhigh"
                        and summary.get("model") == scorer.MODEL):
                    record.update(state="completed", policy_sha256=summary["policy_sha256"],
                                  grades=[row["grade"] for row in summary["rows"]])
            print(key, record["state"], flush=True)
        for checkpoint in checkpoints:
            for candidate in candidates:
                key = f"{checkpoint}/{candidate}"
                if key in records or len(active) >= workers:
                    continue
                try:
                    proof = ready_proof(root, candidate, checkpoint, manifest, prior)
                    if proof is None:
                        continue
                    # Bind the exact problem/gold pair used by the bundled scorer.
                    task = scorer.explicit_proof_tasks(
                        [(problem_id, candidate, Path(proof["proof_path"]))],
                        problem_root=scorer.PROBLEM_ROOT, reference_root=scorer.REFERENCE_ROOT,
                    )[0]
                    if (pipeline.sha256_text(task["problem"])
                            != manifest["frozen_inputs"]["problem_text_sha256"]
                            or task["proof_sha256"] != proof["proof_sha256"]):
                        raise ValueError("scorer problem/proof binding mismatch")
                    prior[candidate, checkpoint] = proof
                    job_dir = output / checkpoint / candidate
                    job_dir.mkdir(parents=True, exist_ok=False)
                    snapshot = job_dir / "submitted_proof.md"
                    pipeline._stage_file(Path(proof["proof_path"]), snapshot)
                    if pipeline.sha256_text(snapshot.read_text().strip()) != proof["proof_sha256"]:
                        raise ValueError("scoring snapshot hash drift")
                    score_dir = job_dir / "score"
                    record = {
                        "checkpoint": checkpoint, "candidate_id": candidate,
                        "proof_path": proof["proof_path"], "proof_sha256": proof["proof_sha256"],
                        "submitted_proof": str(snapshot), "output_dir": str(score_dir),
                        "state": "running",
                    }
                    pipeline.write_json(job_dir / "source_binding.json", record)
                    log = (job_dir / "launcher.log").open("w", encoding="utf-8")
                    try:
                        process = subprocess.Popen(scoring_command(
                            launcher=launcher, proof=snapshot, output=score_dir,
                            problem_id=problem_id, candidate=candidate,
                        ), cwd=pipeline.REPO_ROOT, stdout=log, stderr=subprocess.STDOUT)
                    except Exception:
                        log.close()
                        raise
                    records[key] = record
                    active[key] = (process, log)
                    print("Strict scoring launched:", key, flush=True)
                except Exception as error:
                    records[key] = {"state": "failed", "error": f"{type(error).__name__}: {error}"}
                    print("Scoring binding/launch failure:", key, records[key], flush=True)
        source = read_live(root / "status.json") or {}
        source_done = source.get("state") in {"completed", "completed_with_failed_lanes", "failed_closed", "failed"}
        settled = len(records) == len(candidates) * len(checkpoints)
        done = not active and (source_done or settled)
        status = {
            "state": "completed" if done else "running", "source_state": source,
            "active_scores": list(active), "records": records,
            "failed_calls": [key for key, row in records.items() if row["state"] == "failed"],
        }
        temporary = output / "status.json.tmp"
        pipeline.write_json(temporary, status)
        temporary.replace(output / "status.json")
        if done:
            pipeline.write_json(output / "summary.json", status)
            return
        time.sleep(poll_seconds)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--skill-launcher", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    run(root=args.run_root, output=args.output_dir, launcher=args.skill_launcher,
        workers=args.workers, resume=args.resume)


if __name__ == "__main__":
    main()
