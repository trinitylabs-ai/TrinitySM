"""Independent validators for generic finite-search results."""

from __future__ import annotations

import itertools
from collections import Counter
from math import prod
from typing import Any

from ..finite_expressions import evaluate_finite_expression


VALIDATOR_VERSION = "finite-search-validator-v1"


def validate_enumeration(arguments: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    count = sum(
        all(
            bool(evaluate_finite_expression(constraint, assignment))
            for constraint in arguments["constraints"]
        )
        for assignment in itertools.product(*arguments["domains"])
    )
    normalized = result.get("normalized_result", {})
    passed = (
        count == normalized.get("count")
        and normalized.get("assignment_space_size")
        == prod(len(domain) for domain in arguments["domains"])
    )
    return {
        "passed": passed,
        "details": {"independent_count": count},
        "version": VALIDATOR_VERSION,
    }


def validate_bounded_integer_solutions(
    arguments: dict[str, Any], result: dict[str, Any]
) -> dict[str, Any]:
    solutions = [
        list(assignment)
        for assignment in itertools.product(*arguments["domains"])
        if all(
            bool(evaluate_finite_expression(constraint, assignment))
            for constraint in arguments["constraints"]
        )
    ]
    normalized = result.get("normalized_result", {})
    retained = solutions[:256]
    passed = (
        normalized.get("count") == len(solutions)
        and normalized.get("solutions") == retained
        and normalized.get("solutions_truncated") == (len(solutions) > 256)
        and normalized.get("assignment_space_size")
        == prod(len(domain) for domain in arguments["domains"])
    )
    return {
        "passed": passed,
        "details": {"independent_solution_count": len(solutions)},
        "version": VALIDATOR_VERSION,
    }


def _independent_integer_ast(value: Any) -> int | bool:
    if isinstance(value, (bool, int)):
        return value
    kind, payload = next(iter(value.items()))
    if kind == "add":
        return sum(int(_independent_integer_ast(item)) for item in payload)
    if kind == "mul":
        result = 1
        for item in payload:
            result *= int(_independent_integer_ast(item))
        return result
    if kind == "sub":
        return int(_independent_integer_ast(payload[0])) - int(
            _independent_integer_ast(payload[1])
        )
    if kind == "pow":
        return int(_independent_integer_ast(payload[0])) ** int(payload[1])
    if kind == "mod":
        return int(_independent_integer_ast(payload[0])) % int(payload[1])
    if kind == "neg":
        return -int(_independent_integer_ast(payload))
    raise ValueError(f"non-integer node in exact expression: {kind}")


def validate_exact_integer_expression(
    arguments: dict[str, Any], result: dict[str, Any]
) -> dict[str, Any]:
    value = _independent_integer_ast(arguments["expression"])
    if isinstance(value, bool):
        return {
            "passed": False,
            "details": {"error": "Boolean result"},
            "version": VALIDATOR_VERSION,
        }
    integer = int(value)
    normalized = result.get("normalized_result", {})
    expected_digit_sum = sum(int(char) for char in str(abs(integer)))
    passed = (
        normalized.get("value") == str(integer)
        and normalized.get("digit_sum") == expected_digit_sum
    )
    if "modulus" in arguments:
        modulus = int(arguments["modulus"])
        passed = (
            passed
            and normalized.get("modulus") == modulus
            and normalized.get("residue") == integer % modulus
        )
    output = str(arguments.get("output", "value"))
    expected_derived = {
        "value": str(integer),
        "digit_sum": str(expected_digit_sum),
        "residue": str(normalized.get("residue")),
    }[output]
    passed = passed and str(result.get("derived_answer")) == expected_derived
    return {
        "passed": passed,
        "details": {"independent_value": str(integer)},
        "version": VALIDATOR_VERSION,
    }


def _trial_factor(value: int) -> dict[int, int]:
    remaining = value
    factors: dict[int, int] = {}
    divisor = 2
    while divisor * divisor <= remaining:
        while remaining % divisor == 0:
            factors[divisor] = factors.get(divisor, 0) + 1
            remaining //= divisor
        divisor = 3 if divisor == 2 else divisor + 2
    if remaining > 1:
        factors[remaining] = factors.get(remaining, 0) + 1
    return factors


def validate_divisor_power_threshold(
    arguments: dict[str, Any], result: dict[str, Any]
) -> dict[str, Any]:
    threshold = int(arguments["threshold"])
    reported = result.get("normalized_result", {})
    found = None
    found_count = None
    for n in range(1, int(arguments["max_n"]) + 1):
        factors = _trial_factor(n)
        count = prod(n * power + 1 for power in factors.values())
        if count >= threshold:
            found = n
            found_count = count
            break
    passed = (
        found is not None
        and reported.get("n") == found
        and reported.get("divisor_count") == found_count
        and reported.get("threshold") == threshold
    )
    return {
        "passed": passed,
        "details": {
            "independent_n": found,
            "independent_divisor_count": found_count,
        },
        "version": VALIDATOR_VERSION,
    }


def validate_residue_dp(arguments: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    modulus = int(arguments["modulus"])
    power = int(arguments.get("power", 1))
    frequency = Counter(
        pow(int(value), power, modulus) for value in arguments["values"]
    )
    distribution = {0: 1}
    for _ in range(int(arguments["variable_count"])):
        updated: Counter[int] = Counter()
        for left, left_count in distribution.items():
            for right, right_count in frequency.items():
                updated[(left + right) % modulus] += left_count * right_count
        distribution = dict(updated)
    exact = distribution.get(int(arguments.get("target", 0)) % modulus, 0)
    output_modulus = arguments.get("output_modulus")
    reported = exact % int(output_modulus) if output_modulus is not None else exact
    normalized = result.get("normalized_result", {})
    return {
        "passed": (
            normalized.get("count") == exact
            and normalized.get("reported_count") == reported
        ),
        "details": {"independent_count": exact, "independent_reported": reported},
        "version": VALIDATOR_VERSION,
    }


def validate_exact_cover(arguments: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    universe_size = int(arguments["universe_size"])
    selection_count = int(arguments["selection_count"])
    objects = [frozenset(map(int, value)) for value in arguments["objects"]]
    count = 0
    universe = frozenset(range(universe_size))
    # Independent combinations are bounded by the argument validator.
    for selected in itertools.combinations(objects, selection_count):
        union: set[int] = set()
        disjoint = True
        for item in selected:
            if union.intersection(item):
                disjoint = False
                break
            union.update(item)
        count += disjoint and frozenset(union) == universe
    return {
        "passed": result.get("normalized_result", {}).get("count") == count,
        "details": {"independent_count": count},
        "version": VALIDATOR_VERSION,
    }
