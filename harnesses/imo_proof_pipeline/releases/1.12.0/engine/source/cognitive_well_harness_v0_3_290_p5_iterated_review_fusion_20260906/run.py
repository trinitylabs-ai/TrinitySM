from __future__ import annotations

import argparse
import json
from pathlib import Path

from .pipeline import (
    DEFAULT_GEMMA_ENDPOINT,
    DEFAULT_MODEL_TIMEOUT_SEC,
    DEFAULT_QWEN_ENDPOINT,
    DEFAULT_SEED_NAMESPACE,
    DEFAULT_SOURCE_RUN,
    run_pipeline,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run three fresh Reviewer/Fusion/Resolver-1 cycles with a "
            "mandatory repair-brief audit/repair/re-audit boundary; end at R1-C3"
        )
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--source-run", type=Path, default=DEFAULT_SOURCE_RUN)
    parser.add_argument("--problem-number", type=int, default=5)
    parser.add_argument("--problem-id", help="Explicit dataset ID for a saved lazy_checked portfolio")
    parser.add_argument(
        "--input-checkpoint", choices=("resolver1", "lazy_checked"),
        default="resolver1",
        help="Saved proof checkpoint used for the first fresh review cycle",
    )
    parser.add_argument("--gemma-endpoint", default=DEFAULT_GEMMA_ENDPOINT)
    parser.add_argument("--qwen-endpoint", default=DEFAULT_QWEN_ENDPOINT)
    parser.add_argument("--workers-per-endpoint", type=int, default=4)
    parser.add_argument("--resolve-workers", type=int, default=2)
    parser.add_argument("--seed-namespace", default=DEFAULT_SEED_NAMESPACE)
    parser.add_argument("--optional-exact-evidence", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--resume-after-cycle", type=int, choices=(1, 2, 3), default=0)
    parser.add_argument("--resume-fresh-reviews", action="store_true")
    parser.add_argument(
        "--model-timeout-sec", type=int, default=DEFAULT_MODEL_TIMEOUT_SEC
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--execute-models", action="store_true")
    args = parser.parse_args()
    result = run_pipeline(
        output_dir=args.output_dir,
        source_run=args.source_run,
        input_checkpoint=args.input_checkpoint,
        gemma_endpoint=args.gemma_endpoint,
        qwen_endpoint=args.qwen_endpoint,
        workers_per_endpoint=args.workers_per_endpoint,
        resolve_workers=args.resolve_workers,
        seed_namespace=args.seed_namespace,
        model_timeout_sec=args.model_timeout_sec,
        dry_run=args.dry_run,
        authorize_model_calls=args.execute_models,
        enable_exact_evidence=args.optional_exact_evidence,
        resume_after_cycle=args.resume_after_cycle,
        problem_number=args.problem_number,
        resume_fresh_reviews=args.resume_fresh_reviews,
        source_problem_id=args.problem_id,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
