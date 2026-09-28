#!/usr/bin/env python3
"""Statement-only queue: v263 raw/lazy/refinement -> cleaned v290 R1-C2.

No model calls without --execute-models. Each problem has its own process.
This is orchestration only; prompts, parsing, sampling and recovery are inherited.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import re
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen


REPO = Path(__file__).resolve().parents[1]
SCHEMA = "v263_lazy_refined_to_v290_r1c2_queue_v1"
GEMMA_MODEL = "google/gemma-4-31B-it"
QWEN_MODEL = "Qwen/Qwen3.6-27B"
STAGES = ["raw_generation", "lazy_check", "conditional_in_place_expansion",
          "R1-C1", "R1-C2"]
TERMINAL_STATES = {"completed", "completed_with_failed_lanes", "dry_run_completed"}


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def report(message: str) -> None:
    print(f"{datetime.now(timezone.utc).isoformat(timespec='seconds')} {message}", flush=True)


def collect_problems(directory: Path, selected: list[str] | None, limit: int | None) -> list[dict]:
    """Allow only ID and statement. Reject, never silently discard, extra fields."""
    if not directory.is_dir():
        raise ValueError(f"problem directory not found: {directory}")
    records = []
    for path in sorted(directory.glob("*.json")):
        payload = read(path)
        if not isinstance(payload, dict) or set(payload) not in (
            {"problem_id", "problem"}, {"problem_id", "claim"},
        ):
            raise ValueError(f"problem-only input requires exactly ID and statement: {path}")
        problem_id = payload["problem_id"]
        statement = payload.get("problem", payload.get("claim"))
        if not isinstance(problem_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", problem_id):
            raise ValueError(f"unsafe or empty problem ID: {path}")
        if not isinstance(statement, str) or not statement.strip():
            raise ValueError(f"empty or non-text statement: {path}")
        records.append({"problem_id": problem_id, "problem": statement})
    records.sort(key=lambda row: row["problem_id"])
    ids = [row["problem_id"] for row in records]
    if not ids or len(set(ids)) != len(ids):
        raise ValueError("problem directory is empty or has duplicate IDs")
    # Assign before selection so running one selected problem preserves its seed.
    records = [{**row, "problem_number": index} for index, row in enumerate(records, 1)]
    if selected:
        unknown = set(selected) - set(ids)
        if unknown:
            raise ValueError(f"unknown problem IDs: {sorted(unknown)}")
        records = [row for row in records if row["problem_id"] in selected]
    if limit is not None:
        if limit < 1:
            raise ValueError("--limit must be positive")
        records = records[:limit]
    return records


def freeze_queue(args) -> dict:
    rows = collect_problems(args.problem_dir, args.problem_id, args.limit)
    manifest = {
        "schema": SCHEMA, "problem_dir": str(args.problem_dir.resolve()),
        "output_dir": str(args.output_dir.resolve()), "problems": rows,
        "gemma_endpoint": args.gemma_endpoint.rstrip("/"),
        "qwen_endpoint": args.qwen_endpoint.rstrip("/"),
        "gemma_model": GEMMA_MODEL, "qwen_model": QWEN_MODEL,
        "seed_namespace": args.seed_namespace, "model_timeout_sec": args.model_timeout_sec,
        "dry_run": args.dry_run, "stage_order": STAGES, "terminal_checkpoint": "R1-C2",
        "frontend": "0.3.263", "backend": "0.3.290+goldfree.1",
        "budget_forcing": True, "raw_bf_temperature_transition": "1.0 -> 0.7",
        "workers_per_endpoint": 4, "optional_exact_evidence": False,
        "model_output": "Markdown", "strict_scoring_inside_pipeline": False,
        "reference_inputs_allowed": False,
        "refinement_bf": refinement_policy_manifest(),
    }
    offset = getattr(args, "raw_seed_offset", 0)
    if not isinstance(offset, int) or not 0 <= offset <= 0xFFFFFFFF:
        raise ValueError("raw seed offset must be a uint32")
    if offset:
        manifest["raw_seed_offset"] = offset
    if not manifest["gemma_endpoint"] or not manifest["qwen_endpoint"] or (
        manifest["gemma_endpoint"] == manifest["qwen_endpoint"]
    ):
        raise ValueError("distinct Gemma and Qwen endpoints are required")
    if args.model_timeout_sec < 1:
        raise ValueError("model timeout must be positive")
    path = args.output_dir / "manifest.json"
    if args.resume:
        if read(path) != manifest:
            raise ValueError("resume changes frozen inputs or configuration; use the original arguments")
    else:
        if path.exists():
            raise FileExistsError(path)
        write(path, manifest)
    for row in rows:
        snapshot = args.output_dir / "inputs" / f"{row['problem_id']}.json"
        expected = {key: row[key] for key in ("problem_id", "problem")}
        if args.resume:
            if read(snapshot) != expected:
                raise ValueError(f"frozen problem snapshot changed: {snapshot}")
        else:
            write(snapshot, expected)
    return manifest


def refinement_policy(backend, directory):
    from experiments.local_math_verifier.refinement_bf import refinement_policy as installed
    return installed(backend, directory)


def refinement_policy_manifest():
    return read(REPO / "experiments/local_math_verifier/refinement_bf_manifest.json")


def check_servers(manifest: dict) -> None:
    for role in ("gemma", "qwen"):
        endpoint = manifest[f"{role}_endpoint"]
        with urlopen(endpoint + "/models", timeout=10) as response:
            served = {row["id"] for row in json.load(response)["data"]}
        if manifest[f"{role}_model"] not in served:
            raise ValueError(f"{role} endpoint serves {sorted(served)}, expected {manifest[f'{role}_model']}")


def load_engines():
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    # v290 first preserves the unwrapped transport before importing v263. The
    # alternative v325 single-model policy is imported but NEVER installed.
    from cognitive_well_harness_v0_3_290_p5_iterated_review_fusion_20260906 import pipeline as backend
    frontend = backend.v108.v097
    if backend.single_model.active():
        raise RuntimeError("this launcher requires the original dual-model budget-forcing policy")
    if backend.v263.parent.BUDGET_FORCING_MIN_MAX_TOKENS != 32768:
        raise RuntimeError("v263 budget-forcing policy drift")
    if frontend.RuntimeConfig().lazy_max_tokens != 16384 or frontend.BASELINE_MAX_TOKENS != 65536:
        raise RuntimeError("v263 raw/lazy primary cap drift")
    return frontend, backend


def execute_problem(output_dir: Path, problem_id: str, *, dry_run: bool) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9_-]+", problem_id):
        raise ValueError("unsafe worker problem ID")
    root = output_dir / "problems" / problem_id
    root.mkdir(parents=True, exist_ok=True)
    # A detached/orphaned worker must not be duplicated by a restarted queue.
    with (root / "worker.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return _execute_problem(output_dir, problem_id, dry_run=dry_run)


def _execute_problem(output_dir: Path, problem_id: str, *, dry_run: bool) -> dict:
    manifest = read(output_dir / "manifest.json")
    if manifest.get("repetition_fresh_retry"):
        raise ValueError("This run used the retired repetition fresh-retry policy; use a new output directory")
    if manifest["schema"] != SCHEMA or manifest["dry_run"] != dry_run:
        raise ValueError("worker mode does not match the frozen queue")
    row = next(row for row in manifest["problems"] if row["problem_id"] == problem_id)
    snapshot = output_dir / "inputs" / f"{problem_id}.json"
    if read(snapshot) != {key: row[key] for key in ("problem_id", "problem")}:
        raise ValueError("worker problem snapshot drift")
    frontend, backend = load_engines()
    from experiments.local_math_verifier.cap_recovery import policy_manifest
    from experiments.local_math_verifier.timeout_recovery import policy_manifest as timeout_manifest
    root = output_dir / "problems" / problem_id
    root.mkdir(parents=True, exist_ok=True)
    source = root / "01_source"
    phase = source / f"p{row['problem_number']}" / "01_raw_lazy_enhanced_resolve"
    downstream = root / "02_r1_cycles"
    write(root / "execution_policy.json", {
        "launcher_sha256": digest(Path(__file__)), "stage_order": STAGES,
        "frontend_budget_forcing": True, "frontend_model": GEMMA_MODEL,
        "raw_bf_temperature_transition": "1.0 -> 0.7",
        "raw_candidate_specs": list(frontend.raw_candidate_specs(manifest.get("raw_seed_offset", 0))),
        "raw_seed_offset": manifest.get("raw_seed_offset", 0),
        "raw_primary_max_tokens": frontend.BASELINE_MAX_TOKENS,
        "lazy_primary_max_tokens": frontend.RuntimeConfig().lazy_max_tokens,
        "bf_continuation_cap_floor": 32768,
        "cap_recovery": timeout_manifest(),
        "timeout_recovery": timeout_manifest(),
        "qwen_token_policy": backend.repair_boundary.QWEN_TOKEN_POLICY,
        "qwen_max_output_tokens": backend.repair_boundary.QWEN_MAX_OUTPUT_TOKENS,
        "qwen_retry_on_output_cap": True,
        "limit_recovery": backend.repair_boundary.limit_policy.policy_manifest(),
        "qwen_mandatory_budget_forcing": True,
        "frontend_reviews_fusion_resolver_executed": False,
        "refinement_bf": refinement_policy_manifest(),
        "frontend_lane_failure_policy": "retain_actual_checkpoint_continue_survivors",
    })
    if not dry_run:
        check_servers(manifest)
    try:
        write(root / "status.json", {"state": "running", "stage": "v263_raw_lazy_refinement"})
        saved = read(phase / "summary.json") if (phase / "summary.json").is_file() else {}
        if (saved.get("state"), saved.get("terminal_checkpoint")) not in {
            ("completed", "lazy_checked"), ("completed_with_failed_lanes", "frontend_terminal")
        }:
            frontend.run(
                problem_file=snapshot, output_dir=phase,
                problem_id=problem_id, problem_number=row["problem_number"],
                gpu0_gemma_endpoint=manifest["gemma_endpoint"],
                gpu1_qwen_endpoint=manifest["qwen_endpoint"],
                seed_namespace=f"{manifest['seed_namespace']}:{problem_id}:raw",
                dry_run=dry_run, stop_after_lazy=True, continue_failed_lanes=True,
                raw_seed_offset=manifest.get("raw_seed_offset", 0),
            )
        if dry_run:
            # No invented proof artifacts and no backend model calls in a dry run.
            result = {"state": "dry_run_completed", "problem_id": problem_id,
                      "model_calls_performed": 0, "stage_order": STAGES,
                      "backend_handoff": "planned; requires four actual lazy-refined proofs"}
        else:
            normalized = read(phase / "input/problem.json")
            if normalized.get("claim") != row["problem"].strip():
                raise ValueError("frontend statement does not match the frozen problem-only input")
            backend.configure_source_problem(source, row["problem_number"], expected_problem_id=problem_id)
            backend._lazy_checked_portfolio(source)  # Validate all real source hashes, even on resume.
            if downstream.exists():
                final = read(downstream / "summary.json") if (downstream / "summary.json").is_file() else {}
                if final.get("state") not in {"completed", "completed_with_failed_lanes"}:
                    raise RuntimeError(
                        "v290 has partial work; use its explicit cycle-boundary/fresh-review recovery "
                        "with --problem-id before resuming the queue. No Fusion/rewrite is repeated."
                    )
                result = final
            else:
                write(root / "status.json", {"state": "running", "stage": "v290_R1_C1_to_C2"})
                with refinement_policy(backend, root / "refinement_bf"):
                    result = backend.run_pipeline(
                        output_dir=downstream, source_run=source, input_checkpoint="lazy_checked",
                        source_problem_id=problem_id, problem_number=row["problem_number"],
                        gemma_endpoint=manifest["gemma_endpoint"], qwen_endpoint=manifest["qwen_endpoint"],
                        workers_per_endpoint=4, resolve_workers=2,
                        seed_namespace=f"{manifest['seed_namespace']}:{problem_id}:r1",
                        model_timeout_sec=manifest["model_timeout_sec"],
                        authorize_model_calls=True, enable_exact_evidence=False,
                    )
        write(root / "summary.json", result)
        write(root / "status.json", {"state": result["state"], "stage": "done"})
        return result
    except Exception as error:
        write(root / "status.json", {"state": "failed_closed", "error": str(error),
                                     "traceback": traceback.format_exc()})
        raise


def progress(output_dir: Path, row: dict) -> str:
    root = output_dir / "problems" / row["problem_id"]
    paths = [root / "02_r1_cycles/status.json",
             root / f"01_source/p{row['problem_number']}/01_raw_lazy_enhanced_resolve/status.json",
             root / "status.json"]
    for path in paths:
        if path.is_file():
            try:
                return json.dumps(read(path), ensure_ascii=False)
            except (OSError, ValueError):
                pass  # A legacy status file can be in the middle of a write.
    return "initializing"


def validate_failed_portfolio(root: Path, problem_id: str) -> dict:
    """Bind the saved proofs before explicitly leaving an exhausted problem closed."""
    summary = read(root / "summary.json")
    candidates = {"t10_r01", "t10_r02", "t07_r01", "t07_r02"}
    if (summary.get("problem_id") != problem_id or summary.get("state") != "failed_closed"
            or summary.get("completed_lane_count") != 0 or summary.get("failed_lane_count") != 4
            or set(summary.get("lanes", {})) != candidates):
        raise ValueError(f"Not an exhausted four-lane portfolio: {problem_id}")
    for candidate, lane in summary["lanes"].items():
        if lane.get("state") != "failed_closed" or read(root / "02_r1_cycles/lanes" / candidate / "failure.json").get("state") != "failed_closed":
            raise ValueError(f"Lane is not closed: {problem_id}/{candidate}")
        if lane["current_proof"] is None:
            failure = lane.get("failure") or {}
            if lane["checkpoints"] or failure.get("checkpoint") != "no_proof" or failure.get("proof_path") is not None:
                raise ValueError(f"Invalid proof-less terminal lane: {problem_id}/{candidate}")
            continue
        proof, checkpoint = lane["current_proof"], lane["checkpoints"][-1]
        path = Path(proof["proof_path"]).resolve()
        if not path.is_relative_to(root.resolve()):
            raise ValueError(f"Proof outside problem directory: {path}")
        text = path.read_text(encoding="utf-8").strip()
        if not text or hashlib.sha256(text.encode()).hexdigest() != proof["proof_sha256"] or proof["proof_sha256"] != checkpoint["proof_sha256"]:
            raise ValueError(f"Saved proof hash mismatch: {path}")
    return summary


def run_queue(args) -> int:
    args.output_dir = args.output_dir.resolve()
    if not args.resume:
        args.output_dir.mkdir(parents=True, exist_ok=False)
    with (args.output_dir / "queue.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        manifest = freeze_queue(args)
        skipped = set(getattr(args, "skip_failed_problem", None) or [])
        if skipped and (not args.resume or not skipped <= {row["problem_id"] for row in manifest["problems"]}):
            raise ValueError("Failed-problem skips require resume and IDs in the frozen queue")
        for problem_id in skipped:
            validate_failed_portfolio(args.output_dir / "problems" / problem_id, problem_id)
        for index, row in enumerate(manifest["problems"], 1):
            problem_id = row["problem_id"]
            root = args.output_dir / "problems" / problem_id
            prior = read(root / "summary.json") if (root / "summary.json").is_file() else {}
            if problem_id in skipped:
                report(f"{problem_id}: preserving failed portfolio and saved proofs; continuing remaining queue")
                continue
            if prior.get("state") in TERMINAL_STATES:
                report(f"{problem_id}: already {prior['state']}; skipping model execution")
                continue
            root.mkdir(parents=True, exist_ok=True)
            write(args.output_dir / "status.json", {"state": "running", "problem_id": problem_id,
                                                   "index": index, "total": len(manifest["problems"])})
            command = [sys.executable, "-B", str(Path(__file__).resolve()),
                       "--output-dir", str(args.output_dir), "--_worker", problem_id,
                       "--dry-run" if args.dry_run else "--execute-models"]
            report(f"{problem_id}: starting {index}/{len(manifest['problems'])}; log={root / 'worker.log'}")
            with (root / "worker.log").open("a", encoding="utf-8") as log:
                child = subprocess.Popen(command, cwd=REPO, stdout=log, stderr=subprocess.STDOUT)
                try:
                    while True:
                        try:
                            code = child.wait(timeout=60)
                            break
                        except subprocess.TimeoutExpired:
                            report(f"{problem_id}: {progress(args.output_dir, row)}")
                except BaseException:
                    child.terminate()
                    try:
                        child.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        child.kill()
                        child.wait()
                    raise
            if code:
                write(args.output_dir / "status.json", {"state": "paused_on_failure", "problem_id": problem_id,
                                                       "returncode": code, "log": str(root / "worker.log")})
                report(f"{problem_id}: paused; inspect {root / 'worker.log'} (exit {code})")
                return 1
            report(f"{problem_id}: {read(root / 'summary.json')['state']}")
        results = [read(args.output_dir / "problems" / row["problem_id"] / "summary.json")
                   for row in manifest["problems"]]
        failed_lanes = sum(result.get("failed_lane_count", 0) for result in results)
        state = ("dry_run_completed" if args.dry_run else
                 "completed_with_failed_lanes" if failed_lanes else "completed")
        write(args.output_dir / "status.json", {"state": state, "problem_count": len(results),
                                               "failed_lane_count": failed_lanes})
        report(f"Queue {state}: {len(manifest['problems'])} problems")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--problem-dir", type=Path)
    parser.add_argument("--problem-id", action="append", help="Optional ID filter; repeat to select several")
    parser.add_argument("--limit", type=int, help="Run only the first N selected problems")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--gemma-endpoint", default="http://127.0.0.1:8030/v1")
    parser.add_argument("--qwen-endpoint", default="http://127.0.0.1:8027/v1")
    parser.add_argument("--model-timeout-sec", type=int, default=600)
    parser.add_argument("--seed-namespace", default="v263-v290:problem-only")
    parser.add_argument("--raw-seed-offset", type=int, default=0, help="Recorded uint32 offset for fresh raw portfolio random streams; zero preserves baseline seeds")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--skip-failed-problem", action="append", help="On resume, preserve an exhausted problem and continue; repeat for each ID")
    parser.add_argument("--_worker", help=argparse.SUPPRESS)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--execute-models", action="store_true")
    args = parser.parse_args()
    if args._worker:
        result = execute_problem(args.output_dir.resolve(), args._worker, dry_run=args.dry_run)
        return 0 if result["state"] in TERMINAL_STATES else 1
    if args.problem_dir is None:
        parser.error("--problem-dir is required")
    return run_queue(args)


if __name__ == "__main__":
    raise SystemExit(main())
