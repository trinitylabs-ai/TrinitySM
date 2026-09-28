from __future__ import annotations

import argparse
import json
from pathlib import Path

from .pipeline import TERMINAL_STAGE, run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run v0260 with unified guarded v0261/v0262 recoveries"
    )
    parser.add_argument("--problem-file", type=Path, required=True)
    parser.add_argument("--problem-id", required=True)
    parser.add_argument("--problem-number", type=int)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--gemma-endpoint", default="http://127.0.0.1:8030/v1")
    parser.add_argument("--qwen-endpoint", default="http://127.0.0.1:8027/v1")
    parser.add_argument("--salvage-verifier-endpoint")
    parser.add_argument("--gemma-workers", type=int, default=4)
    parser.add_argument("--qwen-workers", type=int, default=4)
    parser.add_argument("--resolve-workers", type=int, default=2)
    parser.add_argument("--seed-workers", type=int, default=2)
    parser.add_argument("--master-seed", type=int, default=20260904)
    parser.add_argument("--seed-namespace", default="v0263")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    result = run_pipeline(
        problem_file=args.problem_file,
        problem_id=args.problem_id,
        problem_number=args.problem_number,
        output_dir=args.output_dir,
        gemma_endpoint=args.gemma_endpoint,
        qwen_endpoint=args.qwen_endpoint,
        salvage_verifier_endpoint=args.salvage_verifier_endpoint,
        gemma_workers=args.gemma_workers,
        qwen_workers=args.qwen_workers,
        resolve_workers=args.resolve_workers,
        seed_workers=args.seed_workers,
        master_seed=args.master_seed,
        seed_namespace=args.seed_namespace,
        stop_after=TERMINAL_STAGE,
        dry_run=args.dry_run,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

