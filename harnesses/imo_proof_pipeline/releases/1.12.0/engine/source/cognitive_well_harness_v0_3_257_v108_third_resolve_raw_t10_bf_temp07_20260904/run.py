from __future__ import annotations

import argparse
import json
from pathlib import Path

from .pipeline import TERMINAL_STAGE, run_pipeline as run_v0257_pipeline


HANDOFF_MARKER = "USE_V0258_AFTER_P1_P2"


def handoff_version(*, output_dir: Path, problem_number: int | None) -> str | None:
    marker = output_dir.parent / HANDOFF_MARKER
    if problem_number in {None, 1, 2} or not marker.is_file():
        return None
    value = marker.read_text(encoding="utf-8").strip()
    return value if value in {"v0258", "v0260"} else None


def use_v0258_handoff(*, output_dir: Path, problem_number: int | None) -> bool:
    return handoff_version(output_dir=output_dir, problem_number=problem_number) in {
        "v0258",
        "v0260",
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run v108 through third resolve with mandatory Gemma/Qwen budget "
            "forcing and a 1.0-to-0.7 raw-generation continuation transition"
        )
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
    parser.add_argument("--seed-namespace", default="v0257")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    selected_pipeline = run_v0257_pipeline
    selected_handoff = handoff_version(
        output_dir=args.output_dir, problem_number=args.problem_number
    )
    if selected_handoff == "v0258":
        from cognitive_well_harness_v0_3_258_v108_third_resolve_lazy16k_20260904.pipeline import (
            run_pipeline as selected_pipeline,
        )
    elif selected_handoff == "v0260":
        from cognitive_well_harness_v0_3_260_v258_bf32k_floor_20260905.pipeline import (
            run_pipeline as selected_pipeline,
        )
    result = selected_pipeline(
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
