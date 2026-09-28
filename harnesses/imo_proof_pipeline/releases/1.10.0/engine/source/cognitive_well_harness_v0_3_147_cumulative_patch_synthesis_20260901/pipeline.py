from __future__ import annotations

from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_143_separate_tracing_memory_20260901.pipeline import (
    apply_localized_patch,
    fusion_only_patch_prompt,
    parse_localized_patch_markdown,
    proof_line_blocks,
    run as run_base,
    trace_batch_patch_prompt,
)

from . import HARNESS_VERSION


def run(*, source_run: Path, output_dir: Path) -> dict[str, Any]:
    return run_base(
        source_run=source_run,
        output_dir=output_dir,
        visible_fusion_transport="fixed_header_markdown",
        harness_version=HARNESS_VERSION,
        inline_trace_annotations=True,
        iterative_synthesis_batch_size=4,
        fusion_only_first_synthesis=True,
        localized_patch_synthesis=True,
    )


__all__ = [
    "apply_localized_patch",
    "fusion_only_patch_prompt",
    "parse_localized_patch_markdown",
    "proof_line_blocks",
    "run",
    "trace_batch_patch_prompt",
]
