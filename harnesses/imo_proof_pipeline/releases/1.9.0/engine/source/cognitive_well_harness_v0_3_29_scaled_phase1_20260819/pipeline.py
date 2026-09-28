from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_28_two_iteration_terra_appendix_20260819 import (
    pipeline as base_pipeline,
)

from .contracts import (
    ARTIFACT_SCHEMA_VERSION,
    HARNESS_VERSION,
    PHASE_ONE_WIDTH,
    PROMOTION_PROFILE,
    validate_promoted_profile,
)


BASE_PACKAGE = (
    Path(__file__).resolve().parents[1]
    / "cognitive_well_harness_v0_3_28_two_iteration_terra_appendix_20260819"
)
PINNED_BASE_FILES = (
    "__init__.py",
    "contracts.py",
    "pipeline.py",
    "prompts.py",
    "run.py",
    "terra_runtime.py",
    "verification.py",
    "schemas/gemma_body.schema.json",
    "schemas/gemma_child.schema.json",
    "schemas/gemma_exact_negation_repair.schema.json",
    "schemas/terra_child_gate.schema.json",
    "schemas/terra_exact_negation_gate.schema.json",
    "schemas/terra_global.schema.json",
    "schemas/terra_paired.schema.json",
    "schemas/terra_phase_one_diversity.schema.json",
    "schemas/terra_phase_one_score.schema.json",
    "schemas/terra_side.schema.json",
)
EXPECTED_BASE_IMPLEMENTATION_SHA256 = (
    "fd4612aeadcb19aba9df53bdc723b3cf376f80fc138964e9cfa94812b20bbc37"
)


def base_implementation_sha256() -> str:
    digest = hashlib.sha256()
    for relative in PINNED_BASE_FILES:
        path = BASE_PACKAGE / relative
        if not path.is_file():
            raise RuntimeError(f"missing pinned v0.3.28 implementation file: {path}")
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def assert_frozen_base() -> dict[str, Any]:
    observed = base_implementation_sha256()
    if observed != EXPECTED_BASE_IMPLEMENTATION_SHA256:
        raise RuntimeError(
            "v0.3.29 frozen v0.3.28 implementation changed: "
            f"expected {EXPECTED_BASE_IMPLEMENTATION_SHA256}, observed {observed}"
        )
    return {
        "package": BASE_PACKAGE.name,
        "sha256": observed,
        "files": list(PINNED_BASE_FILES),
    }


def run_harness(**kwargs: Any) -> dict[str, Any]:
    """Run the promoted profile through the frozen v0.3.28 implementation."""

    validate_promoted_profile()
    frozen_base = assert_frozen_base()
    requested_width = int(kwargs.pop("phase_one_width", PHASE_ONE_WIDTH))
    if requested_width != PHASE_ONE_WIDTH:
        raise ValueError("v0.3.29 fixes Phase-1 width at four candidates per route")
    forbidden = {
        "harness_version",
        "artifact_schema_version",
        "promotion_profile",
        "promotion_base",
    } & set(kwargs)
    if forbidden:
        raise ValueError(
            "promoted identity fields are not caller-configurable: "
            + ", ".join(sorted(forbidden))
        )
    return base_pipeline.run_harness(
        **kwargs,
        phase_one_width=PHASE_ONE_WIDTH,
        harness_version=HARNESS_VERSION,
        artifact_schema_version=ARTIFACT_SCHEMA_VERSION,
        promotion_profile=PROMOTION_PROFILE,
        promotion_base=frozen_base,
    )
