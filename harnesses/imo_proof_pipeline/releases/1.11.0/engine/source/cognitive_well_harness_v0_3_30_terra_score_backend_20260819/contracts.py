from __future__ import annotations

from cognitive_well_harness_v0_3_29_scaled_phase1_20260819.contracts import (
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
    TERRA_MODEL,
    TERRA_SUCCESS_CONFIRMATIONS,
    validate_promoted_profile as validate_v0329_profile,
)


HARNESS_VERSION = "full-cold-start-v0.3.30-terra-score-only-grading-over-v0.3.29"
ARTIFACT_SCHEMA_VERSION = "v0.3.30"
PROMOTION_PROFILE = "four-routes-x-four-terra-score-only-grading"
SCORING_BACKEND = "terra"
SCORING_RESULT_KEYS = frozenset({"score"})
VALID_SCORES = frozenset({0, 1, 2, 3, 4, 6, 7})


def validate_promoted_profile() -> None:
    validate_v0329_profile()
    if SCORING_BACKEND != "terra":
        raise RuntimeError("v0.3.30 grading backend must remain Terra")
    if SCORING_RESULT_KEYS != {"score"}:
        raise RuntimeError("v0.3.30 scorer must expose only the normalized score")
