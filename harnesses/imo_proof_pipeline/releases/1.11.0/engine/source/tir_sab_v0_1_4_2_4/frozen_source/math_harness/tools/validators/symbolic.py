"""Independent exact validators for symbolic backend certificates."""

from __future__ import annotations

from fractions import Fraction
from math import prod
from typing import Any


VALIDATOR_VERSION = "equal-minima-certificate-v1"


def _poly_eval(coefficients: list[int], value: int) -> int:
    result = 0
    for coefficient in coefficients:
        result = result * value + coefficient
    return result


def validate_rational_product_equal_minima(
    arguments: dict[str, Any], result: dict[str, Any]
) -> dict[str, Any]:
    roots = [int(value) for value in arguments["fixed_roots"]]
    normalized = result.get("normalized_result", {})
    coefficients = [int(value) for value in normalized["condition_coefficients"]]
    candidates = [int(value) for value in normalized["candidate_parameters"]]
    admissible = [int(value) for value in normalized["admissible_parameters"]]
    root_sum = sum(roots)
    pair_sum = sum(roots[i] * roots[j] for i in range(3) for j in range(i + 1, 3))
    root_product = prod(roots)
    roots_satisfy = all(_poly_eval(coefficients, value) == 0 for value in candidates)
    filters_valid = True
    independently_admissible: list[int] = []
    for value in candidates:
        uv_sum = Fraction(root_sum + value, 2)
        uv_product = Fraction(pair_sum + root_sum * value, 2) - uv_sum * uv_sum / 2
        # Equivalent direct coefficient expression; equality guards against a
        # backend certificate using a different formula.
        direct = Fraction(-value * value + 2 * root_sum * value + 4 * pair_sum - root_sum * root_sum, 8)
        if uv_product != direct or uv_product * uv_product != root_product * value:
            filters_valid = False
            continue
        discriminant = uv_sum * uv_sum - 4 * uv_product
        if uv_sum > 0 and uv_product > 0 and discriminant > 0:
            independently_admissible.append(value)
    filters_valid = filters_valid and sorted(admissible) == sorted(independently_admissible)
    answer_valid = int(normalized["answer"]) == sum(independently_admissible)
    return {
        "passed": roots_satisfy and filters_valid and answer_valid,
        "details": {
            "candidate_roots_satisfy_condition": roots_satisfy,
            "domain_filter_valid": filters_valid,
            "answer_sum_valid": answer_valid,
            "independently_admissible": independently_admissible,
        },
        "version": VALIDATOR_VERSION,
    }
