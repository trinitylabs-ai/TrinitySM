from __future__ import annotations

from cognitive_well_harness_v0_3_31_external_hypothesis_metadata_20260819.contracts import (
    FINAL_CANDIDATE_FAMILIES,
    FRESH_CANDIDATES_PER_ITERATION,
    GUIDED_CANDIDATES_PER_ITERATION,
    MAX_CHILD_DEPTH,
    MAX_CONJECTURE_ITERATIONS,
    MAX_NEW_CHILDREN_GLOBAL,
    PHASE_ONE_CANDIDATE_COUNT,
    PHASE_ONE_FINALIST_COUNT,
    PHASE_ONE_FINALISTS_PER_ROUTE,
    PHASE_ONE_ROUTE_COUNT,
    PHASE_ONE_WIDTH,
    SCORING_BACKEND,
    SCORING_RESULT_KEYS,
    SIDE_AUDIT_EXTERNAL_FIELDS,
    SIDE_AUDIT_MODEL_FIELDS,
    TERRA_MODEL,
    TERRA_SUCCESS_CONFIRMATIONS,
    VALID_SCORES,
    validate_promoted_profile as validate_v0331_profile,
)


HARNESS_VERSION = "full-cold-start-v0.3.32-clean-terra-metadata-over-v0.3.31"
ARTIFACT_SCHEMA_VERSION = "v0.3.32"
PROMOTION_PROFILE = "four-routes-x-four-clean-terra-routing-metadata"


def validate_promoted_profile() -> None:
    validate_v0331_profile()
    if PHASE_ONE_FINALIST_COUNT != 8:
        raise RuntimeError("v0.3.32 ordinal selector requires exactly eight finalists")
