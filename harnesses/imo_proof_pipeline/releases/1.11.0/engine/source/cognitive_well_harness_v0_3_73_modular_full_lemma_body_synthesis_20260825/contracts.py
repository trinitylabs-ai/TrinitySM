from __future__ import annotations

from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_72_modular_location_aware_split_verifier_20260824.contracts import (  # noqa: F401
    ALIGNMENT_SCHEMA,
    ARMS,
    EXTRACTION_SCHEDULE,
    LOCATION_HYPOTHESIS_SCHEMA,
    SEMANTIC_DEDUP_SCHEMA,
    VALIDITY_SCHEMA,
    load_run_input,
    safe_name,
    sha256_text,
    validate_schema,
)


SYNTHESIS_TEMPERATURES = (0.2, 0.4, 0.6)

SYNTHESIS_FAMILIES = (
    "lemma_evidence_only",
    "anchored_refinement",
    "location_aware",
    "full_lemma_body",
)

SYNTHESIS_CONFIGURATIONS: tuple[dict[str, Any], ...] = tuple(
    {
        "candidate_id": f"{arm}_{short}_t{str(temperature).replace('.', '')}",
        "arm": arm,
        "family": family,
        "temperature": temperature,
        "replicate": 1,
    }
    for arm in ARMS
    for family, short in (
        ("lemma_evidence_only", "evidence"),
        ("anchored_refinement", "anchored"),
        ("location_aware", "location"),
        ("full_lemma_body", "full_body"),
    )
    for temperature in SYNTHESIS_TEMPERATURES
)


def child_paths(output_dir: Path) -> dict[str, Path]:
    v066 = output_dir / "tree" / "02_v066_compact_json_recovery"
    leaf = v066 / "children" / "03_v073_full_lemma_body_synthesis"
    return {"v066": v066, "leaf": leaf}


__all__ = [
    "ALIGNMENT_SCHEMA",
    "ARMS",
    "EXTRACTION_SCHEDULE",
    "LOCATION_HYPOTHESIS_SCHEMA",
    "SEMANTIC_DEDUP_SCHEMA",
    "SYNTHESIS_CONFIGURATIONS",
    "SYNTHESIS_FAMILIES",
    "SYNTHESIS_TEMPERATURES",
    "VALIDITY_SCHEMA",
    "child_paths",
    "load_run_input",
]
