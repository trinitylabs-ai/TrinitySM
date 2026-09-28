"""Queue the existing experiment and isolated strict scorer after a prerequisite run."""
from __future__ import annotations

import argparse
import fcntl
from pathlib import Path
import subprocess
import sys
import time

from . import pipeline
from .score_when_ready import read_live

MODULE = "cognitive_well_harness_v0_3_290_p5_iterated_review_fusion_20260906"
TERMINAL_STATES = {"completed", "completed_with_failed_lanes", "failed_closed", "failed"}


def pipeline_finished(root: Path) -> bool:
    state = read_live(root / "status.json") or {}
    if state.get("state") not in TERMINAL_STATES:
        return False
    if state.get("state") == "failed_closed" and state.get("stage") in {"input_binding", "orchestrator"}:
        return False  # Wait for a mechanical repair/resume, not a different experiment.
    summary = read_live(root / "summary.json") or {}
    failures = state.get("lane_failures") or {
        key: row.get("failure") for key, row in summary.get("lanes", {}).items()
        if row.get("failure")
    }
    for failure in failures.values():
        error = str((failure or {}).get("error", ""))
        if not any(kind in error for kind in ("RepairBriefCertificationError", "FusionAcceptanceCertificationError")):
            return False  # An all-lanes timeout is not an experiment conclusion.
    return True


def process_owns_run(pid: int | None, root: Path, *, proc_root: Path = Path("/proc")) -> bool:
    if not pid:
        return False
    try:
        process = proc_root / str(pid)
        command = (process / "cmdline").read_bytes().decode().split("\0")
        output = Path(command[command.index("--output-dir") + 1])
        if not output.is_absolute():
            output = (process / "cwd").resolve() / output
    except (OSError, ValueError, IndexError):
        return False
    return output.resolve() == root.resolve()


def locate_worker(root: Path, module: str, *, proc_root: Path = Path("/proc")) -> int | None:
    """Reattach an explicitly resumed worker by module and exact output root."""
    matches = []
    for process in proc_root.iterdir():
        if not process.name.isdigit():
            continue
        try:
            command = (process / "cmdline").read_bytes().decode().split("\0")
            if command[command.index("-m") + 1] != module:
                continue
        except (OSError, ValueError, IndexError):
            continue
        pid = int(process.name)
        if process_owns_run(pid, root, proc_root=proc_root):
            matches.append(pid)
    if len(matches) > 1:
        raise RuntimeError(f"multiple workers claim {root}: {matches}")
    return matches[0] if matches else None


def frozen_portfolio(source: Path, number: int) -> dict:
    pipeline.configure_source_problem(source, number)
    portfolio = pipeline._lazy_checked_portfolio(source)
    return {
        "problem_id": pipeline.PROBLEM_ID, "problem_sha256": pipeline.EXPECTED_PROBLEM_SHA256,
        "proofs": [{"candidate_id": row["candidate_id"],
                    "proof_path": row["source_proof_path"],
                    "proof_sha256": row["source_proof_sha256"]} for row in portfolio["proofs"]],
    }


def model_command(*, number: int, source: Path, output: Path, runtime: dict,
                  seed_namespace: str) -> list[str]:
    return [sys.executable, "-B", "-m", MODULE,
            "--source-run", str(source), "--output-dir", str(output),
            "--problem-number", str(number), "--input-checkpoint", "lazy_checked",
            "--no-optional-exact-evidence", "--execute-models",
            "--gemma-endpoint", runtime["gemma_endpoint"],
            "--qwen-endpoint", runtime["qwen_endpoint"],
            "--workers-per-endpoint", str(runtime["workers_per_endpoint"]),
            "--resolve-workers", str(runtime["resolve_workers"]),
            "--model-timeout-sec", str(runtime["model_timeout_sec"]),
            "--seed-namespace", f"{seed_namespace}:p{number}"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--after-run", type=Path, required=True)
    parser.add_argument("--after-score-run", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--source-run", type=Path, default=pipeline.DEFAULT_SOURCE_RUN)
    parser.add_argument("--problem-numbers", nargs="+", type=int, required=True)
    parser.add_argument("--skill-launcher", type=Path, required=True)
    parser.add_argument("--seed-namespace", default="v0290r2:lazy_checked")
    args = parser.parse_args()
    output, source = args.output_dir.resolve(), args.source_run.resolve()
    after, after_score = args.after_run.resolve(), args.after_score_run.resolve()
    if len(set(args.problem_numbers)) != len(args.problem_numbers):
        raise ValueError("duplicate queued problem")
    for existing in (source, after, after_score):
        if output == existing or output in existing.parents or existing in output.parents:
            raise ValueError("queue output overlaps an existing run")
    if not args.skill_launcher.is_file():
        raise FileNotFoundError(args.skill_launcher)
    output.mkdir(parents=True, exist_ok=True)
    lock = (output / "queue.lock").open("a")
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    runtime = pipeline.read_object(after / "manifest.json")["runtime"]
    plan = {
        "after_run": str(after), "after_score_run": str(after_score), "source_run": str(source),
        "problem_numbers": args.problem_numbers, "runtime": runtime,
        "input_checkpoint": "lazy_checked", "r1_cycle_count": pipeline.R1_CYCLE_COUNT,
        "pipeline_policy": pipeline.PIPELINE_POLICY,
        "stage_order": list(pipeline.STAGE_ORDER),
        "terminal_checkpoint": pipeline.TERMINAL_CHECKPOINT,
        "enable_exact_evidence": False, "seed_namespace": args.seed_namespace,
        "strict_skill_launcher": str(args.skill_launcher.resolve()),
        "scores_model_visible": False,
        "frozen_inputs": {str(n): frozen_portfolio(source, n) for n in args.problem_numbers},
    }
    manifest_path = output / "manifest.json"
    if manifest_path.exists():
        if pipeline.read_object(manifest_path) != plan:
            raise ValueError("queue resume changes frozen plan/inputs")
    else:
        pipeline.write_json(manifest_path, plan)
    status = read_live(output / "status.json") or {"jobs": {}}

    def publish(state: str, **updates) -> None:
        status.update(state=state, **updates)
        if state != "mechanical_blocker":
            status.pop("error", None)
        temporary = output / "status.json.tmp"
        pipeline.write_json(temporary, status)
        temporary.replace(output / "status.json")

    publish("waiting_for_prerequisite", waiting_for=str(after))
    print("Queue armed; waiting for prerequisite model run and per-proof scoring.", flush=True)
    while not pipeline_finished(after) or not (after_score / "summary.json").is_file():
        time.sleep(15)
    for number in args.problem_numbers:
        key = f"p{number}"
        job_root = output / key
        model_root, score_root = job_root / "model", job_root / "strict_scores"
        if frozen_portfolio(source, number) != plan["frozen_inputs"][str(number)]:
            raise ValueError(f"queued source proof drift: {key}")
        job_root.mkdir(parents=True, exist_ok=True)
        job = status["jobs"].setdefault(key, {})
        for field, worker_root, module in (
            ("model_pid", model_root, MODULE),
            ("score_pid", score_root, MODULE + ".score_when_ready"),
        ):
            if worker_root.exists() and not process_owns_run(job.get(field), worker_root):
                attached = locate_worker(worker_root, module)
                if attached:
                    job[field] = attached
        model_process, score_process = None, None
        resume_reviews = model_root.exists() and not pipeline_finished(model_root) and not process_owns_run(job.get("model_pid"), model_root)
        if not model_root.exists() or resume_reviews:
            command = model_command(number=number, source=source, output=model_root,
                                    runtime=runtime, seed_namespace=args.seed_namespace)
            if resume_reviews:
                source_status = read_live(model_root / "status.json") or {}
                if source_status.get("stage") != "R1-C1":
                    publish("mechanical_blocker", error=f"{key} requires an explicit later-cycle resume")
                    return
                command.append("--resume-fresh-reviews")
            with (job_root / "model.log").open("a", encoding="utf-8") as log:
                model_process = subprocess.Popen(command, cwd=pipeline.REPO_ROOT,
                                                 stdout=log, stderr=subprocess.STDOUT,
                                                 start_new_session=True)
            job["model_pid"] = model_process.pid
            print("Launched", key, "four-proof model experiment", flush=True)
        publish("running", current_problem=number, waiting_for=None)
        while not (model_root / "manifest.json").is_file():
            if model_process and model_process.poll() is not None:
                publish("mechanical_blocker", error=f"{key} failed before input binding")
                return
            time.sleep(1)
        if not score_root.exists() or (not (score_root / "summary.json").exists()
                                      and not process_owns_run(job.get("score_pid"), score_root)):
            command = [sys.executable, "-B", "-m", MODULE + ".score_when_ready",
                       "--run-root", str(model_root), "--output-dir", str(score_root),
                       "--skill-launcher", str(args.skill_launcher.resolve()), "--workers", "4"]
            if score_root.exists():
                command.append("--resume")
            with (job_root / "scoring.log").open("a", encoding="utf-8") as log:
                score_process = subprocess.Popen(command, cwd=pipeline.REPO_ROOT,
                                                 stdout=log, stderr=subprocess.STDOUT,
                                                 start_new_session=True)
            job["score_pid"] = score_process.pid
        while not pipeline_finished(model_root) or not (score_root / "summary.json").is_file():
            job["model_status"] = read_live(model_root / "status.json")
            scores = read_live(score_root / "status.json") or {}
            job["active_scores"] = scores.get("active_scores", [])
            if model_process and model_process.poll() is not None and not pipeline_finished(model_root):
                publish("mechanical_blocker", error=f"{key} needs a model checkpoint repair/resume")
                return
            if score_process and score_process.poll() is not None and not (score_root / "summary.json").is_file():
                publish("mechanical_blocker", error=f"{key} scoring watcher exited early")
                return
            if not process_owns_run(job.get("model_pid"), model_root) and not pipeline_finished(model_root):
                publish("mechanical_blocker", error=f"{key} model worker exited before completion")
                return
            if not process_owns_run(job.get("score_pid"), score_root) and not (score_root / "summary.json").is_file():
                publish("mechanical_blocker", error=f"{key} scoring worker exited before completion")
                return
            publish("running")
            time.sleep(15)
        if model_process:
            model_process.wait()
        if score_process:
            score_process.wait()
        job.update(state="completed", model_status=read_live(model_root / "status.json"),
                   score_summary=str(score_root / "summary.json"))
        print("Finished", key, flush=True)
        publish("running")
    publish("completed", current_problem=None)
    pipeline.write_json(output / "summary.json", status)


if __name__ == "__main__":
    main()
