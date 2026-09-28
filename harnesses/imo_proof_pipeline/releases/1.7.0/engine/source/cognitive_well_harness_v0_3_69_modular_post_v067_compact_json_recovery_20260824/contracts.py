from __future__ import annotations

from pathlib import Path

from cognitive_well_harness_v0_3_66_modular_six_to_two_proof_selection_20260824.contracts import (
    INPUT_SCHEMA,
    load_run_input,
)


def child_paths(output_dir: Path) -> dict[str, Path]:
    v066 = output_dir / "tree" / "02_v066_compact_json_recovery"
    v065 = v066 / "children" / "03_v065_two_path_hypothesis_extraction"
    return {"v066": v066, "v065": v065}


__all__ = ["INPUT_SCHEMA", "child_paths", "load_run_input"]

