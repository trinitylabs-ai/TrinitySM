"""Deterministic validators for the coverage-experiment task families."""

from __future__ import annotations

from typing import Any, Callable

from ..backends.coverage import (
    exact_coordinate_geometry,
    exact_equation_system,
    exact_finite_state,
    exact_number_theory,
)


VALIDATOR_VERSION = "coverage-exact-recompute-validator-v1"


def _validate(
    execute: Callable[[dict[str, Any]], dict[str, Any]],
    arguments: dict[str, Any],
    result: dict[str, Any],
) -> dict[str, Any]:
    independently_recomputed = execute(dict(arguments))
    expected = independently_recomputed.get("normalized_result")
    observed = result.get("normalized_result")
    expected_answer = independently_recomputed.get("derived_answer")
    observed_answer = result.get("derived_answer")
    return {
        "passed": observed == expected and observed_answer == expected_answer,
        "details": {
            "task": arguments.get("task"),
            "normalized_result_matches": observed == expected,
            "derived_answer_matches": observed_answer == expected_answer,
        },
        "version": VALIDATOR_VERSION,
    }


def validate_exact_equation_system(arguments, result):
    return _validate(exact_equation_system, arguments, result)


def validate_exact_number_theory(arguments, result):
    return _validate(exact_number_theory, arguments, result)


def validate_exact_finite_state(arguments, result):
    return _validate(exact_finite_state, arguments, result)


def validate_exact_coordinate_geometry(arguments, result):
    return _validate(exact_coordinate_geometry, arguments, result)
