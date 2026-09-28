#!/usr/bin/env python3
"""Generate four single-pass Gemma drafts with native thinking, without forced continuation or grading."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS = ("imo-proofbench/basic", "imo-proofbench/advanced", "imo2026")
RUNNER = ROOT / "benchmarks/imo-proofbench/basic/results/raw_no_bf/generation/harness_snapshot/run.py"
RUNNER_SHA256 = "282f9b0fc2d01171a89e9a05123ec4eb00222c8ac90a7a827fe1d29cab387aa4"


def load_runner():
    # Reuse the evaluated single-request implementation and its frozen prompts.
    if hashlib.sha256(RUNNER.read_bytes()).hexdigest() != RUNNER_SHA256:
        raise ValueError("The evaluated raw-generation runner changed")
    spec = importlib.util.spec_from_file_location("workshop_raw_no_bf", RUNNER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", choices=BENCHMARKS, default="imo-proofbench/basic")
    parser.add_argument("--problem-id", action="append", default=[])
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--endpoint", default="http://127.0.0.1:8030/v1")
    parser.add_argument("--raw-seed-offset", type=int, default=0)
    parser.add_argument("--max-tokens", type=int, default=65536)
    parser.add_argument("--timeout-sec", type=float, default=14400)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--execute-models", action="store_true",
                        help="Contact the local Gemma server; otherwise only prepare requests")
    args = parser.parse_args(argv)
    args.problem_dir = ROOT / "benchmarks" / args.benchmark / "problems"
    return args


def main(argv=None):
    args = parse_args(argv)
    result = load_runner().run(args)
    print(json.dumps({k: v for k, v in result.items() if k != "rows"}), flush=True)
    return 0 if result["state"] in {"completed", "dry_run"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
