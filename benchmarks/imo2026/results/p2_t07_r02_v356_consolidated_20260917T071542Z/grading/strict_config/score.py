#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    workspace = Path.cwd().resolve()
    runner = workspace / "scripts/run_gold_informed_calibrated_codex_scores.py"
    if not runner.is_file():
        raise FileNotFoundError(
            "run from the Gemma4 workspace containing "
            "scripts/run_gold_informed_calibrated_codex_scores.py"
        )

    arguments = list(sys.argv[1:])
    has_effort = any(
        argument == "--reasoning-effort"
        or argument.startswith("--reasoning-effort=")
        for argument in arguments
    )
    command = [
        sys.executable,
        "-m",
        "scripts.run_gold_informed_calibrated_codex_scores",
        *arguments,
    ]
    if not has_effort:
        command.extend(("--reasoning-effort", "xhigh"))
    # Keep strict last so a conflicting caller flag cannot weaken this skill.
    command.extend(("--policy-mode", "strict"))
    return subprocess.run(command, cwd=workspace, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
