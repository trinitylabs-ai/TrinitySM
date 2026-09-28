from __future__ import annotations

from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.contracts import (  # noqa: F401
    ARMS,
    DIAGNOSTIC_SCHEMA,
    NEGATION_AUDIT_SCHEMA,
    NEGATION_REPAIR_SCHEMA,
    safe_name,
    sha256_text,
    validate_schema,
)
from cognitive_well_harness_v0_3_70_modular_post_v067_compact_json_cleanup_20260824.contracts import (  # noqa: F401
    load_run_input,
)


EXTRACTION_SCHEDULE: tuple[dict[str, Any], ...] = (
    {"round": 1, "temperature": 0.2},
    {"round": 2, "temperature": 0.4},
    {"round": 3, "temperature": 0.8},
)

SYNTHESIS_FAMILIES = (
    "lemma_evidence_only",
    "anchored_refinement",
    "location_aware",
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
    )
    for temperature in (0.2, 0.4)
)

LOCATION_HYPOTHESIS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["hypotheses"],
    "properties": {
        "hypotheses": {
            "type": "array",
            "minItems": 0,
            "maxItems": 3,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "conjecture",
                    "exact_negation",
                    "earliest_unresolved_transition",
                    "local_dependency_map",
                ],
                "properties": {
                    "conjecture": {"type": "string", "minLength": 20},
                    "exact_negation": {"type": "string", "minLength": 20},
                    "earliest_unresolved_transition": {
                        "type": "string",
                        "minLength": 10,
                    },
                    "local_dependency_map": {"type": "string", "minLength": 10},
                },
            },
        }
    },
}

ALIGNMENT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["classification"],
    "properties": {
        "classification": {
            "type": "string",
            "enum": [
                "PROVES_ASSIGNED_CLAIM",
                "PROVES_OPPOSITE_CLAIM",
                "PROVES_NEITHER",
            ],
        }
    },
}

VALIDITY_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["verdict"],
    "properties": {
        "verdict": {"type": "string", "enum": ["PASS", "FAIL", "INCONCLUSIVE"]}
    },
}

SEMANTIC_DEDUP_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["equivalent"],
    "properties": {"equivalent": {"type": "boolean"}},
}


def child_paths(output_dir: Path) -> dict[str, Path]:
    v066 = output_dir / "tree" / "02_v066_compact_json_recovery"
    leaf = v066 / "children" / "03_v072_location_aware_split_verifier"
    return {"v066": v066, "leaf": leaf}


__all__ = [
    "ALIGNMENT_SCHEMA",
    "ARMS",
    "EXTRACTION_SCHEDULE",
    "LOCATION_HYPOTHESIS_SCHEMA",
    "SEMANTIC_DEDUP_SCHEMA",
    "SYNTHESIS_CONFIGURATIONS",
    "SYNTHESIS_FAMILIES",
    "VALIDITY_SCHEMA",
    "child_paths",
    "load_run_input",
]
