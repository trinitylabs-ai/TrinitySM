from __future__ import annotations

from cognitive_well_harness_v0_3_30_terra_score_backend_20260819.contracts import (
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
    TERRA_MODEL,
    TERRA_SUCCESS_CONFIRMATIONS,
    VALID_SCORES,
    validate_promoted_profile as validate_v0330_profile,
)


HARNESS_VERSION = (
    "full-cold-start-v0.3.31-external-hypothesis-audit-metadata-over-v0.3.30"
)
ARTIFACT_SCHEMA_VERSION = "v0.3.31"
PROMOTION_PROFILE = (
    "four-routes-x-four-terra-score-only-grading-external-hypothesis-metadata"
)
SIDE_AUDIT_EXTERNAL_FIELDS = frozenset({"claim_id", "audited_side"})
SIDE_AUDIT_MODEL_FIELDS = frozenset(
    {
        "verdict",
        "exact_claim_reached",
        "first_break",
        "missing_obligations",
        "counterexample_or_failure_witness",
        "external_information_used",
    }
)


def validate_promoted_profile() -> None:
    validate_v0330_profile()
    if SIDE_AUDIT_EXTERNAL_FIELDS & SIDE_AUDIT_MODEL_FIELDS:
        raise RuntimeError("external hypothesis metadata leaked into model fields")
    if SIDE_AUDIT_EXTERNAL_FIELDS != {"claim_id", "audited_side"}:
        raise RuntimeError("v0.3.31 external hypothesis metadata contract drifted")
