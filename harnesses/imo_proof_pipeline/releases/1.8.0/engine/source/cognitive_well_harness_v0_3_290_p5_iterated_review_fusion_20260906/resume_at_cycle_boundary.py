"""Switch optional evidence off after the current cycle, retaining completed work."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

from . import pipeline
from .score_when_ready import read_live, stage_directory


def cycle_settled(root: Path, candidates: list[str], cycle: int) -> bool:
    for candidate in candidates:
        summary = read_live(stage_directory(root, candidate, f"R1-C{cycle}") / "summary.json") or {}
        if summary.get("state") == "completed":
            continue
        failure = read_live(root / "lanes" / candidate / "failure.json") or {}
        if failure.get("state") != "failed_closed" or failure.get("stage") != f"R1-C{cycle}":
            return False
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--pid", type=int, required=True)
    parser.add_argument("--cycle", type=int, choices=(1, 2, 3), required=True)
    args = parser.parse_args()
    root = args.run_root.resolve()
    manifest = pipeline.read_object(root / "manifest.json")
    proc = Path(f"/proc/{args.pid}")
    original_cmd = (proc / "cmdline").read_bytes()
    module = "cognitive_well_harness_v0_3_290_p5_iterated_review_fusion_20260906"
    parts = original_cmd.decode().split("\0")
    if module not in parts or "--output-dir" not in parts:
        raise ValueError("replacement PID is not the requested harness")
    bound_root = Path(parts[parts.index("--output-dir") + 1])
    if not bound_root.is_absolute():
        bound_root = (proc / "cwd").resolve() / bound_root
    if bound_root.resolve() != root:
        raise ValueError("replacement PID belongs to another run")
    print("Waiting for cycle", args.cycle, "to settle; optional evidence will be off after resume.", flush=True)
    while not cycle_settled(root, manifest["candidate_ids"], args.cycle):
        if not proc.exists():
            raise RuntimeError("original process exited before the checkpoint settled")
        time.sleep(0.5)
    if proc.exists():
        if (proc / "cmdline").read_bytes() != original_cmd:
            raise ValueError("replacement process identity changed")
        os.kill(args.pid, signal.SIGSTOP)
        try:
            # Never discard a completed later checkpoint. A just-started later
            # cycle may have unfinished requests; keep its artifacts separately.
            archive = root / f"interrupted_before_resume_after_cycle_{args.cycle}"
            moved = []
            for candidate in manifest["candidate_ids"]:
                for cycle in range(args.cycle + 1, pipeline.R1_CYCLE_COUNT + 1):
                    stage = stage_directory(root, candidate, f"R1-C{cycle}")
                    if not stage.exists():
                        continue
                    if (read_live(stage / "summary.json") or {}).get("state") == "completed":
                        raise ValueError("a later cycle is already complete; refusing earlier resume")
                    destination = archive / candidate / stage.name
                    if destination.exists():
                        raise FileExistsError(destination)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    stage.rename(destination)
                    moved.append({"from": str(stage), "to": str(destination)})
            pipeline.write_json(root / "optional_evidence_disable_transition.json", {
                "previous_pid": args.pid, "resume_after_cycle": args.cycle,
                "enable_exact_evidence": False, "preserved_incomplete_stages": moved,
                "completed_proofs_reused": True,
            })
            os.kill(args.pid, signal.SIGTERM)
        finally:
            if proc.exists():
                os.kill(args.pid, signal.SIGCONT)
        for _ in range(100):
            if not proc.exists():
                break
            time.sleep(0.1)
        else:
            raise RuntimeError("original process did not terminate; refusing duplicate run")
    runtime = manifest["runtime"]
    command = [sys.executable, "-B", "-m", module,
               "--output-dir", str(root), "--source-run", manifest["source_run"],
               "--problem-number", str(manifest.get("problem_number", 5)),
               "--input-checkpoint", manifest["input_checkpoint"],
               "--gemma-endpoint", runtime["gemma_endpoint"],
               "--qwen-endpoint", runtime["qwen_endpoint"],
               "--workers-per-endpoint", str(runtime["workers_per_endpoint"]),
               "--resolve-workers", str(runtime["resolve_workers"]),
               "--seed-namespace", runtime["seed_namespace"],
               "--model-timeout-sec", str(runtime["model_timeout_sec"]),
               "--resume-after-cycle", str(args.cycle),
               "--no-optional-exact-evidence", "--execute-models"]
    print("Resuming with optional exact evidence disabled.", flush=True)
    raise SystemExit(subprocess.run(command, cwd=pipeline.REPO_ROOT, check=False).returncode)


if __name__ == "__main__":
    main()
