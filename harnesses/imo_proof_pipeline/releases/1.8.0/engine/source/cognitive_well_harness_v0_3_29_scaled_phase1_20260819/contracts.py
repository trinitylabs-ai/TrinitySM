from __future__ import annotations

from cognitive_well_harness_v0_3_28_two_iteration_terra_appendix_20260819.contracts import (
    FINAL_CANDIDATE_FAMILIES,
    FRESH_CANDIDATES_PER_ITERATION,
    GUIDED_CANDIDATES_PER_ITERATION,
    MAX_CHILD_DEPTH,
    MAX_CONJECTURE_ITERATIONS,
    MAX_NEW_CHILDREN_GLOBAL,
    PHASE_ONE_ROUTE_COUNT,
    TERRA_MODEL,
    TERRA_SUCCESS_CONFIRMATIONS,
)


HARNESS_VERSION = (
    "full-cold-start-v0.3.29-scaled-four-route-phase1-over-v0.3.28"
)
ARTIFACT_SCHEMA_VERSION = "v0.3.29"
PROMOTION_PROFILE = "four-routes-x-four-terra-anchor-plus-complement"
PHASE_ONE_WIDTH = 4
PHASE_ONE_CANDIDATE_COUNT = PHASE_ONE_ROUTE_COUNT * PHASE_ONE_WIDTH
PHASE_ONE_FINALISTS_PER_ROUTE = 2
PHASE_ONE_FINALIST_COUNT = PHASE_ONE_ROUTE_COUNT * PHASE_ONE_FINALISTS_PER_ROUTE


def validate_promoted_profile() -> None:
    expected = {
        "phase_one_routes": 4,
        "phase_one_width": 4,
        "phase_one_candidates": 16,
        "phase_one_finalists_per_route": 2,
        "phase_one_finalists": 8,
        "conjecture_iterations": 2,
        "guided_candidates": 3,
        "fresh_candidates": 1,
        "terra_confirmations": 3,
    }
    actual = {
        "phase_one_routes": PHASE_ONE_ROUTE_COUNT,
        "phase_one_width": PHASE_ONE_WIDTH,
        "phase_one_candidates": PHASE_ONE_CANDIDATE_COUNT,
        "phase_one_finalists_per_route": PHASE_ONE_FINALISTS_PER_ROUTE,
        "phase_one_finalists": PHASE_ONE_FINALIST_COUNT,
        "conjecture_iterations": MAX_CONJECTURE_ITERATIONS,
        "guided_candidates": GUIDED_CANDIDATES_PER_ITERATION,
        "fresh_candidates": FRESH_CANDIDATES_PER_ITERATION,
        "terra_confirmations": TERRA_SUCCESS_CONFIRMATIONS,
    }
    if actual != expected:
        raise RuntimeError(f"v0.3.29 promoted profile drift: {actual} != {expected}")
