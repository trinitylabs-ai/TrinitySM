#!/usr/bin/env python3
"""Restart a stopped statement-only queue in tmux, preserving partial work."""
from __future__ import annotations

import argparse
from contextlib import ExitStack, contextmanager
import fcntl
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from scripts import run_v263_v290 as runner

DEFAULT_RUN = REPO / "runs/basic002_030_v263_v290_run01"
MODEL_PYTHON = Path("/home/user/miniconda3/envs/math/bin/python")


def resume_args(root: Path) -> argparse.Namespace:
    manifest = runner.read(root / "manifest.json")
    if manifest.get("repetition_fresh_retry"):
        raise ValueError("This run used the retired repetition fresh-retry policy; use a new output directory")
    if (manifest.get("schema") != runner.SCHEMA or manifest.get("dry_run") is not False
            or Path(manifest["output_dir"]).resolve() != root):
        raise ValueError("not an existing live-mode v263/v290 queue at this path")
    ids = [row["problem_id"] for row in manifest["problems"]]
    if not ids or any(not re.fullmatch(r"[A-Za-z0-9_-]+", pid) for pid in ids):
        raise ValueError("invalid frozen problem IDs")
    return argparse.Namespace(
        problem_dir=Path(manifest["problem_dir"]), problem_id=ids, limit=None,
        output_dir=root, gemma_endpoint=manifest["gemma_endpoint"],
        qwen_endpoint=manifest["qwen_endpoint"], model_timeout_sec=manifest["model_timeout_sec"],
        seed_namespace=manifest["seed_namespace"], dry_run=False, resume=True,
        raw_seed_offset=manifest.get("raw_seed_offset", 0),
    )


@contextmanager
def stopped_queue(root: Path):
    """Hold queue and existing worker locks before inspecting/moving artifacts."""
    with ExitStack() as stack:
        paths = [root / "queue.lock", *sorted((root / "problems").glob("*/worker.lock"))]
        for path in paths:
            handle = stack.enter_context(path.open("a"))
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise RuntimeError("The queue or a worker is still running. Stop it before relaunching.") from error
        yield


def restart_plan(root: Path) -> dict | None:
    manifest = runner.read(root / "manifest.json")
    for row in manifest["problems"]:
        problem_root = root / "problems" / row["problem_id"]
        summary = problem_root / "summary.json"
        if summary.is_file() and runner.read(summary).get("state") in runner.TERMINAL_STATES:
            continue
        downstream = problem_root / "02_r1_cycles"
        archive = False
        if downstream.exists():
            if downstream.is_symlink() or downstream.resolve().parent != problem_root.resolve():
                raise ValueError("refusing to archive a redirected backend directory")
            terminal = downstream / "summary.json"
            archive = not (terminal.is_file() and runner.read(terminal).get("state") in runner.TERMINAL_STATES)
        if archive:
            checkpoint = problem_root / f"01_source/p{row['problem_number']}/01_raw_lazy_enhanced_resolve/summary.json"
            saved = runner.read(checkpoint) if checkpoint.is_file() else {}
            if saved.get("state") != "completed" or saved.get("terminal_checkpoint") != "lazy_checked":
                raise RuntimeError("No completed lazy-checked checkpoint; refusing to move partial work.")
        return {"problem_id": row["problem_id"], "archive_partial_backend": archive,
                "problem_root": str(problem_root), "backend": str(downstream)}
    return None


def preserve_partial(plan: dict) -> Path | None:
    if not plan["archive_partial_backend"]:
        return None
    root = Path(plan["problem_root"])
    backup = Path(tempfile.mkdtemp(prefix="restart_backup.", dir=root))
    for name in ("execution_policy.json", "status.json"):
        if (root / name).is_file():
            shutil.copy2(root / name, backup / name)
    Path(plan["backend"]).rename(backup / "02_r1_cycles")
    runner.write(backup / "restart_record.json", {
        **plan, "backup": str(backup), "restart_checkpoint": "lazy_checked",
        "incomplete_backend_cycles_will_repeat": True, "source_proofs_preserved": True,
    })
    return backup


def launch_tmux(root: Path, session: str) -> None:
    if shutil.which("tmux") is None or not MODEL_PYTHON.is_file():
        raise RuntimeError("tmux or the configured math Python environment is unavailable")
    command = shlex.join([str(MODEL_PYTHON), "-u", "-B", str(Path(__file__).resolve()),
                          "--output-dir", str(root), "--foreground"])
    # Keep the pane available for inspecting any startup error or final result.
    command += "; exec bash"
    exists = subprocess.run(["tmux", "has-session", "-t", f"={session}"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
    tmux_args = (["new-window", "-d", "-t", f"={session}", "-n", "resume"] if exists
                 else ["new-session", "-d", "-s", session, "-n", "resume"])
    subprocess.run(["tmux", *tmux_args, command], cwd=REPO, check=True)
    print(f"Restart launched in tmux. View it: tmux attach -t {session}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--tmux-session", default="proofbench-basic")
    parser.add_argument("--check", action="store_true", help="show the restart point without moving files or launching")
    parser.add_argument("--foreground", action="store_true", help=argparse.SUPPRESS)
    options = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", options.tmux_session):
        parser.error("invalid tmux session name")
    root = options.output_dir.resolve()
    try:
        args = resume_args(root)
        with stopped_queue(root):
            plan = restart_plan(root)
            if plan is None:
                print("All queued problems are already completed; nothing to relaunch.")
                return 0
            print(f"Resume at {plan['problem_id']}; restart incomplete cycles from saved lazy-checked proofs: "
                  f"{plan['archive_partial_backend']}", flush=True)
            if options.check:
                return 0
            if options.foreground:
                runner.freeze_queue(args)  # Validate all frozen inputs before moving anything.
                backup = preserve_partial(plan)
                if backup:
                    print(f"Interrupted work preserved in {backup}", flush=True)
        if options.foreground:
            return runner.run_queue(args)  # Reacquires queue.lock; never allows duplicate inference.
        launch_tmux(root, options.tmux_session)
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Cannot relaunch: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
