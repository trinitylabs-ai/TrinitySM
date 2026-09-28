from __future__ import annotations

from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_72_modular_location_aware_split_verifier_20260824.contracts import (  # noqa: F401
    ALIGNMENT_SCHEMA,
    ARMS,
    EXTRACTION_SCHEDULE,
    LOCATION_HYPOTHESIS_SCHEMA,
    SYNTHESIS_CONFIGURATIONS as V072_SYNTHESIS_CONFIGURATIONS,
    SYNTHESIS_FAMILIES as V072_SYNTHESIS_FAMILIES,
    VALIDITY_SCHEMA,
    load_run_input,
    safe_name,
    sha256_text,
    validate_schema,
)
from cognitive_well_harness_v0_3_63_deterministic_lemma_appendix_20260824.run import (
    CONFIGURATIONS as V063_EXPERIMENT_CONFIGURATIONS,
)
from cognitive_well_harness_v0_3_63_deterministic_lemma_appendix_20260824.run_failure_guided_salvage_surgical import (
    SALVAGE_SCHEMA as V063_FAILURE_SALVAGE_SCHEMA,
)


MAX_FAILURE_SALVAGE_CASES = 3

FAILURE_SALVAGE_SCHEMA: dict[str, Any] = V063_FAILURE_SALVAGE_SCHEMA

STATEMENT_ONLY_CONFIGURATIONS: tuple[dict[str, Any], ...] = tuple(
    dict(row) for row in V063_EXPERIMENT_CONFIGURATIONS
)


def child_paths(output_dir: Path) -> dict[str, Path]:
    v066 = output_dir / "tree" / "02_v066_compact_json_recovery"
    leaf = v066 / "children" / "03_v078_failure_salvage_statement_only"
    return {"v066": v066, "leaf": leaf}


__all__ = [
    "ALIGNMENT_SCHEMA",
    "ARMS",
    "EXTRACTION_SCHEDULE",
    "FAILURE_SALVAGE_SCHEMA",
    "LOCATION_HYPOTHESIS_SCHEMA",
    "MAX_FAILURE_SALVAGE_CASES",
    "STATEMENT_ONLY_CONFIGURATIONS",
    "VALIDITY_SCHEMA",
    "V072_SYNTHESIS_CONFIGURATIONS",
    "V072_SYNTHESIS_FAMILIES",
    "child_paths",
    "load_run_input",
    "safe_name",
    "sha256_text",
    "validate_schema",
]
