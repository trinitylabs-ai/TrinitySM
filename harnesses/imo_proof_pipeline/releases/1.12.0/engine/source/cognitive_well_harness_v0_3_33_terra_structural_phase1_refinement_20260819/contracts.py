from __future__ import annotations

from cognitive_well_harness_v0_3_32_clean_terra_metadata_20260819.contracts import (
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
    validate_promoted_profile as validate_v0332_profile,
)


HARNESS_VERSION = (
    "full-cold-start-v0.3.33-terra-structural-phase1-refinement-"
    "compact-final-score-conditional-semantic-anchor-tiebreak-"
    "seven-independent-binary-complementarity-comparisons-"
    "no-phase1-grade-adapter-"
    "lean-gemma-prompts-over-v0.3.32"
)
ARTIFACT_SCHEMA_VERSION = "v0.3.33"
PROMOTION_PROFILE = (
    "four-routes-x-four-terra-structural-refinement-compact-final-score-"
    "conditional-semantic-anchor-tiebreak-seven-independent-binary-"
    "complementarity-comparisons-no-phase1-grade-adapter-lean-gemma-prompts"
)


def validate_promoted_profile() -> None:
    validate_v0332_profile()
    if PHASE_ONE_CANDIDATE_COUNT != 16:
        raise RuntimeError("v0.3.33 requires the fixed sixteen-proof Phase 1")
