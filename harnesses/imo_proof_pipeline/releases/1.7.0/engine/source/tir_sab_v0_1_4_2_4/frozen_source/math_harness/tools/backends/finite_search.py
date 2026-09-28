"""Generic deterministic finite enumeration, residue DP, and exact cover."""

from __future__ import annotations

import itertools
from collections import Counter
from functools import lru_cache
from math import prod
from typing import Any

from ..finite_expressions import evaluate_finite_expression
from .base import backend_result


def enumerate_finite_assignments(arguments: dict[str, Any]) -> dict[str, Any]:
    domains = arguments["domains"]
    constraints = arguments["constraints"]
    count = 0
    examples: list[list[int]] = []
    for assignment in itertools.product(*domains):
        if all(
            bool(evaluate_finite_expression(constraint, assignment))
            for constraint in constraints
        ):
            count += 1
            if len(examples) < 16:
                examples.append(list(assignment))
    return backend_result(
        normalized_result={
            "count": count,
            "assignment_space_size": prod(len(domain) for domain in domains),
            "variable_count": len(domains),
        },
        certificate={"first_solutions": examples},
        checked_claim="Exhaustive finite enumeration has the reported solution count.",
        derived_answer=str(count),
    )


def bounded_integer_solutions(arguments: dict[str, Any]) -> dict[str, Any]:
    """Enumerate a bounded integer system and retain its exact solutions."""

    domains = arguments["domains"]
    constraints = arguments["constraints"]
    solutions = [
        list(assignment)
        for assignment in itertools.product(*domains)
        if all(
            bool(evaluate_finite_expression(constraint, assignment))
            for constraint in constraints
        )
    ]
    retained = solutions[:256]
    return backend_result(
        normalized_result={
            "count": len(solutions),
            "solutions": retained,
            "solutions_truncated": len(solutions) > len(retained),
            "assignment_space_size": prod(len(domain) for domain in domains),
            "variable_count": len(domains),
        },
        certificate={"enumeration_order": "lexicographic_domain_product"},
        checked_claim=(
            "Exhaustive bounded integer enumeration has exactly the listed "
            "solutions (unless explicitly marked truncated)."
        ),
        # A list of assignments has no dataset-independent textual answer
        # format. Keep the exact solutions in normalized_result for refiners,
        # but do not create an automatic boxed repair candidate.
        derived_answer=None,
    )


def exact_integer_expression(arguments: dict[str, Any]) -> dict[str, Any]:
    """Evaluate a safe, variable-free integer expression exactly."""

    value = evaluate_finite_expression(arguments["expression"], ())
    if isinstance(value, bool):
        raise ValueError("exact integer expression must not be Boolean")
    integer = int(value)
    modulus = arguments.get("modulus")
    normalized = {
        "value": str(integer),
        "digit_sum": sum(int(char) for char in str(abs(integer))),
    }
    if modulus is not None:
        normalized["residue"] = integer % int(modulus)
        normalized["modulus"] = int(modulus)
    output = str(arguments.get("output", "value"))
    derived = normalized[output]
    return backend_result(
        normalized_result=normalized,
        certificate={"evaluation": "safe_integer_ast"},
        checked_claim="The structured integer expression has the reported exact value.",
        derived_answer=str(derived),
    )


def divisor_power_threshold(arguments: dict[str, Any]) -> dict[str, Any]:
    """Find the first n for which n**n has at least a target divisor count."""

    threshold = int(arguments["threshold"])
    max_n = int(arguments["max_n"])
    for n in range(1, max_n + 1):
        remaining = n
        factors: dict[int, int] = {}
        for prime in (2, 3):
            while remaining % prime == 0:
                factors[prime] = factors.get(prime, 0) + 1
                remaining //= prime
        divisor = 5
        step = 2
        while divisor * divisor <= remaining:
            while remaining % divisor == 0:
                factors[divisor] = factors.get(divisor, 0) + 1
                remaining //= divisor
            divisor += step
            step = 6 - step
        if remaining > 1:
            factors[remaining] = factors.get(remaining, 0) + 1
        divisor_count = prod(n * int(power) + 1 for power in factors.values())
        if divisor_count >= threshold:
            return backend_result(
                normalized_result={
                    "n": n,
                    "divisor_count": divisor_count,
                    "threshold": threshold,
                    "factorization": [
                        [int(prime), int(power)]
                        for prime, power in sorted(factors.items())
                    ],
                },
                certificate={"checked_range": [1, n]},
                checked_claim=(
                    "This is the smallest positive n whose n-th power has at "
                    "least the requested number of divisors."
                ),
                derived_answer=str(n),
            )
    raise ValueError("no qualifying n was found within max_n")


def modular_tuple_enumeration(arguments: dict[str, Any]) -> dict[str, Any]:
    return enumerate_finite_assignments(arguments)


def bitmask_dynamic_program(arguments: dict[str, Any]) -> dict[str, Any]:
    variable_count = int(arguments["variable_count"])
    values = [int(value) for value in arguments["values"]]
    power = int(arguments.get("power", 1))
    modulus = int(arguments["modulus"])
    target = int(arguments.get("target", 0)) % modulus
    output_modulus = arguments.get("output_modulus")
    frequencies = Counter(pow(value, power, modulus) for value in values)
    distribution = [0] * modulus
    distribution[0] = 1
    for _ in range(variable_count):
        updated = [0] * modulus
        for residue, count in enumerate(distribution):
            if not count:
                continue
            for delta, frequency in frequencies.items():
                updated[(residue + delta) % modulus] += count * frequency
        distribution = updated
    exact_count = distribution[target]
    reported = (
        exact_count % int(output_modulus)
        if output_modulus is not None
        else exact_count
    )
    return backend_result(
        normalized_result={
            "count": exact_count,
            "reported_count": reported,
            "target": target,
            "modulus": modulus,
            "distinct_transformed_residues": len(frequencies),
        },
        certificate={
            "residue_frequencies": [
                [residue, frequency]
                for residue, frequency in sorted(frequencies.items())
            ],
            "variable_count": variable_count,
            "power": power,
            "value_count": len(values),
            "output_modulus": output_modulus,
        },
        checked_claim="Exact residue-distribution convolution has the reported count.",
        derived_answer=str(reported),
    )


def exact_cover_count(arguments: dict[str, Any]) -> dict[str, Any]:
    universe_size = int(arguments["universe_size"])
    selection_count = int(arguments["selection_count"])
    masks = tuple(
        sum(1 << int(index) for index in cells) for cells in arguments["objects"]
    )
    full = (1 << universe_size) - 1
    by_element: list[list[int]] = [[] for _ in range(universe_size)]
    for mask in masks:
        remaining = mask
        while remaining:
            bit = remaining & -remaining
            by_element[bit.bit_length() - 1].append(mask)
            remaining ^= bit
    calls = 0

    @lru_cache(maxsize=None)
    def count(covered: int, used: int) -> int:
        nonlocal calls
        calls += 1
        if covered == full:
            return int(used == selection_count)
        if used == selection_count:
            return 0
        missing = full ^ covered
        first = (missing & -missing).bit_length() - 1
        return sum(
            count(covered | mask, used + 1)
            for mask in by_element[first]
            if not mask & covered
        )

    total = count(0, 0)
    return backend_result(
        normalized_result={
            "count": total,
            "universe_size": universe_size,
            "object_count": len(masks),
            "selection_count": selection_count,
        },
        certificate={"state_count": calls, "cache_hits": count.cache_info().hits},
        checked_claim="The exact-cover instance has the reported number of covers.",
        derived_answer=str(total),
    )
