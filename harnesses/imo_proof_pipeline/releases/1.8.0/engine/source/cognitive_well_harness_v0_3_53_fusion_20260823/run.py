from __future__ import annotations

from typing import Any

from cognitive_well_harness_v0_3_52_fusion_20260823 import run as _base

from . import HARNESS_VERSION
from .protocol import (
    SYSTEM_PROMPT,
    fusion_user_prompt,
    parse_fusion,
    sha256_text,
    validate_assessment_semantics,
)


_base.HARNESS_VERSION = HARNESS_VERSION
_base.SYSTEM_PROMPT = SYSTEM_PROMPT
_base.fusion_user_prompt = fusion_user_prompt
_base.parse_fusion = parse_fusion
_base.sha256_text = sha256_text
_base.RESULT_SCHEMA = "cognitive-well-v053-fusion-result-v1"
_base.SUMMARY_SCHEMA = "cognitive-well-v053-fusion-summary-v1"
_base.MANIFEST_SCHEMA = "cognitive-well-v053-fusion-manifest-v1"
_base.PERMITTED_RECORD_NAMES = (
    "FUSION_ACCEPT_AS_WRITTEN, FUSION_ACCEPT_WITH_ROUTINE_COMPLETION, "
    "FUSION_REPAIR_NEEDED, or FUSION_INCONCLUSIVE"
)
_base.SEED_POLICY = (
    "reuse matched sha256(v052,fusion,problem,candidate,proof) seeds for paired "
    "v052-v053 prompt comparison"
)


def parse_task_output(value: str, task: dict[str, Any]) -> dict[str, Any]:
    parsed = parse_fusion(value)
    reviewer_sources = task.get("reviewer_sources") or {}
    reviewer_outcomes = {
        name: str((reviewer_sources.get(name) or {}).get("outcome") or "")
        for name in ("reviewer_1", "reviewer_2", "reviewer_3")
    }
    return validate_assessment_semantics(parsed, reviewer_outcomes)


_base.parse_task_output = parse_task_output

MODEL_CONFIGS = _base.MODEL_CONFIGS
REVIEWER_SELECTION = _base.REVIEWER_SELECTION
TEMPERATURES = _base.TEMPERATURES
PER_GPU_BATCH_SIZE = _base.PER_GPU_BATCH_SIZE
load_fusion_rows = _base.load_fusion_rows
build_tasks = _base.build_tasks
task_output_dir = _base.task_output_dir
run_task = _base.run_task
summarize = _base.summarize


def main() -> None:
    _base.main()


if __name__ == "__main__":
    main()
