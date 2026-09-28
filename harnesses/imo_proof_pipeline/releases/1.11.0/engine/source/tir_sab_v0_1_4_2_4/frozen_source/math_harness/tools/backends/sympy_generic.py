"""Generic exact SymPy operations over safe structured expressions."""

from __future__ import annotations

import math
from typing import Any

from ..expressions import symbol_table, to_sympy
from .base import backend_result


def _expressions(arguments: dict[str, Any], *fields: str):
    symbols = symbol_table(list(arguments.get("symbols") or []))
    return symbols, [to_sympy(arguments[field], symbols) for field in fields]


def expand_and_compare(arguments: dict[str, Any]) -> dict[str, Any]:
    import sympy as sp

    _, (left, right) = _expressions(arguments, "left", "right")
    left_expanded = sp.expand(left)
    right_expanded = sp.expand(right)
    difference = sp.expand(left_expanded - right_expanded)
    equal = difference == 0
    return backend_result(
        normalized_result={
            "equal": equal,
            "left_expanded": str(left_expanded),
            "right_expanded": str(right_expanded),
            "difference": str(difference),
        },
        certificate={"method": "independent_expansion"},
        checked_claim="The two structured expressions are algebraically equal.",
        derived_answer=None,
    )


def factor_and_reexpand(arguments: dict[str, Any]) -> dict[str, Any]:
    import sympy as sp

    _, (expression,) = _expressions(arguments, "expression")
    factored = sp.factor(expression)
    reexpanded = sp.expand(factored)
    return backend_result(
        normalized_result={
            "factorization": str(factored),
            "reexpanded": str(reexpanded),
            "matches_original": sp.expand(expression - reexpanded) == 0,
        },
        certificate={"original_expanded": str(sp.expand(expression))},
        checked_claim="The exact factorization re-expands to the original expression.",
    )


def simplify_identity(arguments: dict[str, Any]) -> dict[str, Any]:
    import sympy as sp

    _, (left, right) = _expressions(arguments, "left", "right")
    difference = sp.cancel(sp.together(left - right))
    return backend_result(
        normalized_result={
            "equal": difference == 0,
            "simplified_difference": str(difference),
        },
        certificate={"method": "together_then_cancel"},
        checked_claim="The two exact rational expressions define the same identity.",
    )


def solve_and_substitute(arguments: dict[str, Any]) -> dict[str, Any]:
    import sympy as sp

    symbols = symbol_table(list(arguments.get("symbols") or []))
    solve_for_names = list(arguments.get("solve_for") or [])
    solve_for = [symbols[str(name)] for name in solve_for_names]
    equations = [to_sympy(value, symbols) for value in arguments["equations"]]
    raw = sp.solve(equations, solve_for, dict=True)
    solutions: list[dict[str, str]] = []
    substitution_checks: list[list[str]] = []
    for solution in raw:
        solutions.append(
            {str(symbol): str(sp.simplify(value)) for symbol, value in solution.items()}
        )
        substitution_checks.append(
            [str(sp.simplify(equation.subs(solution))) for equation in equations]
        )
    return backend_result(
        normalized_result={
            "solutions": solutions,
            "solution_count": len(solutions),
            "substitution_checks": substitution_checks,
        },
        certificate={"solve_for": solve_for_names},
        checked_claim="The listed exact solutions satisfy every original equation.",
    )


def polynomial_root_filter(arguments: dict[str, Any]) -> dict[str, Any]:
    import sympy as sp

    symbols, (expression,) = _expressions(arguments, "polynomial")
    variable = symbols[str(arguments["variable"])]
    roots = sp.solve(expression, variable)
    domain = str(arguments.get("domain", "real"))
    filtered = []
    for value in roots:
        keep = value.is_real is True if domain in {"real", "positive", "nonnegative"} else True
        if domain == "positive":
            keep = keep and value > 0
        elif domain == "nonnegative":
            keep = keep and value >= 0
        elif domain == "integer":
            keep = value.is_integer is True
        if keep:
            filtered.append(value)
    return backend_result(
        normalized_result={
            "all_roots": [str(sp.simplify(value)) for value in roots],
            "filtered_roots": [str(sp.simplify(value)) for value in filtered],
            "domain": domain,
            "substitution_checks": [
                str(sp.simplify(expression.subs(variable, value))) for value in filtered
            ],
        },
        certificate={"variable": str(variable)},
        checked_claim=f"The filtered roots satisfy the polynomial and domain {domain}.",
    )


def exact_modular_evaluation(arguments: dict[str, Any]) -> dict[str, Any]:
    base = int(arguments["base"])
    exponent = int(arguments["exponent"])
    modulus = int(arguments["modulus"])
    if exponent < 0 or exponent.bit_length() > 1_000_000:
        raise ValueError("exponent must be a bounded nonnegative integer")
    if not 2 <= modulus <= 10**12:
        raise ValueError("modulus must be between 2 and 10^12")
    value = pow(base, exponent, modulus)
    return backend_result(
        normalized_result={"value": value, "modulus": modulus},
        certificate={"base": base, "exponent": str(exponent)},
        checked_claim="The exact modular exponentiation has the reported residue.",
        derived_answer=str(value),
    )


def exact_gcd(arguments: dict[str, Any]) -> dict[str, Any]:
    values = [int(value) for value in arguments["values"]]
    if not 2 <= len(values) <= 1024:
        raise ValueError("gcd requires 2 through 1024 integers")
    value = math.gcd(*values)
    return backend_result(
        normalized_result={"gcd": value},
        certificate={"values": values},
        checked_claim="The reported integer is the greatest common divisor.",
        derived_answer=str(value),
    )


def prime_factorization(arguments: dict[str, Any]) -> dict[str, Any]:
    import sympy as sp

    value = int(arguments["value"])
    if value == 0 or abs(value).bit_length() > 4096:
        raise ValueError("factorization requires a nonzero integer of at most 4096 bits")
    factors = sp.factorint(abs(value))
    return backend_result(
        normalized_result={
            "sign": -1 if value < 0 else 1,
            "factors": [[int(prime), int(power)] for prime, power in sorted(factors.items())],
        },
        certificate={"value": str(value)},
        checked_claim="The reported primes and exponents multiply to the input integer.",
    )


def determinant(arguments: dict[str, Any]) -> dict[str, Any]:
    import sympy as sp

    matrix = arguments["matrix"]
    if (
        not isinstance(matrix, list)
        or not matrix
        or len(matrix) > 64
        or any(not isinstance(row, list) or len(row) != len(matrix) for row in matrix)
        or any(not isinstance(value, int) for row in matrix for value in row)
    ):
        raise ValueError("matrix must be a square integer matrix of size 1 through 64")
    value = sp.det(sp.Matrix(matrix))
    return backend_result(
        normalized_result={"determinant": str(value)},
        certificate={"matrix": matrix},
        checked_claim="The exact determinant has the reported value.",
        derived_answer=str(value),
    )
