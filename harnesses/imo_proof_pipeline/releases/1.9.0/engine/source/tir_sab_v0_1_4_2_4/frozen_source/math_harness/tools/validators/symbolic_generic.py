"""Deterministic validators for generic exact operations."""

from __future__ import annotations

import math
from fractions import Fraction
from typing import Any

from ..expressions import symbol_table, to_sympy


VALIDATOR_VERSION = "symbolic-generic-validator-v1"


def validate_symbolic_operation(
    operation: str,
    arguments: dict[str, Any],
    result: dict[str, Any],
) -> dict[str, Any]:
    normalized = result.get("normalized_result", {})
    passed = False
    details: dict[str, Any] = {}
    if operation in {"expand_and_compare", "simplify_identity"}:
        import sympy as sp

        symbols = symbol_table(list(arguments.get("symbols") or []))
        left = to_sympy(arguments["left"], symbols)
        right = to_sympy(arguments["right"], symbols)
        equal = sp.cancel(sp.together(left - right)) == 0
        passed = bool(normalized.get("equal")) == equal
        details["independent_equal"] = equal
    elif operation == "factor_and_reexpand":
        import sympy as sp

        symbols = symbol_table(list(arguments.get("symbols") or []))
        expression = to_sympy(arguments["expression"], symbols)
        independently_factored = sp.factor(expression)
        passed = (
            str(independently_factored) == normalized.get("factorization")
            and sp.expand(independently_factored - expression) == 0
            and normalized.get("matches_original") is True
        )
        details["independent_factorization"] = str(independently_factored)
    elif operation == "solve_and_substitute":
        import sympy as sp

        symbols = symbol_table(list(arguments.get("symbols") or []))
        equations = [to_sympy(value, symbols) for value in arguments["equations"]]
        solve_for = [symbols[str(value)] for value in arguments["solve_for"]]
        independent = sp.solve(equations, solve_for, dict=True)
        canonical = [
            {str(key): str(sp.simplify(value)) for key, value in row.items()}
            for row in independent
        ]
        substitution_valid = all(
            all(sp.simplify(equation.subs(row)) == 0 for equation in equations)
            for row in independent
        )
        passed = canonical == normalized.get("solutions") and substitution_valid
        details["independent_solution_count"] = len(canonical)
    elif operation == "polynomial_root_filter":
        import sympy as sp

        symbols = symbol_table(list(arguments.get("symbols") or []))
        expression = to_sympy(arguments["polynomial"], symbols)
        variable = symbols[str(arguments["variable"])]
        passed = all(
            value == "0" for value in normalized.get("substitution_checks", [])
        ) and all(
            sp.simplify(expression.subs(variable, value)) == 0
            for value in sp.solve(expression, variable)
            if str(sp.simplify(value)) in normalized.get("filtered_roots", [])
        )
    elif operation == "exact_modular_evaluation":
        expected = pow(
            int(arguments["base"]),
            int(arguments["exponent"]),
            int(arguments["modulus"]),
        )
        passed = normalized.get("value") == expected
        details["independent_value"] = expected
    elif operation == "gcd":
        expected = math.gcd(*(int(value) for value in arguments["values"]))
        passed = normalized.get("gcd") == expected
        details["independent_gcd"] = expected
    elif operation == "prime_factorization":
        factors = normalized.get("factors", [])
        reconstructed = int(normalized.get("sign", 1))
        primes_valid = True
        for prime, power in factors:
            if prime < 2 or power < 1:
                primes_valid = False
            for divisor in range(2, int(prime**0.5) + 1):
                if prime % divisor == 0:
                    primes_valid = False
                    break
            reconstructed *= int(prime) ** int(power)
        passed = primes_valid and reconstructed == int(arguments["value"])
        details["reconstructed"] = str(reconstructed)
    elif operation == "determinant":
        matrix = [[Fraction(value) for value in row] for row in arguments["matrix"]]
        determinant_value = Fraction(1)
        sign = 1
        size = len(matrix)
        for column in range(size):
            pivot = next(
                (row for row in range(column, size) if matrix[row][column]),
                None,
            )
            if pivot is None:
                determinant_value = Fraction(0)
                break
            if pivot != column:
                matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
                sign *= -1
            pivot_value = matrix[column][column]
            determinant_value *= pivot_value
            for row in range(column + 1, size):
                factor = matrix[row][column] / pivot_value
                for offset in range(column, size):
                    matrix[row][offset] -= factor * matrix[column][offset]
        determinant_value *= sign
        expected = (
            str(determinant_value.numerator)
            if determinant_value.denominator == 1
            else str(determinant_value)
        )
        passed = normalized.get("determinant") == expected
        details["independent_determinant"] = expected
    else:
        raise ValueError(f"unsupported symbolic validator operation: {operation}")
    return {
        "passed": bool(passed),
        "details": details,
        "version": VALIDATOR_VERSION,
    }


def validate_expand_and_compare(arguments, result):
    return validate_symbolic_operation("expand_and_compare", arguments, result)


def validate_factor_and_reexpand(arguments, result):
    return validate_symbolic_operation("factor_and_reexpand", arguments, result)


def validate_simplify_identity(arguments, result):
    return validate_symbolic_operation("simplify_identity", arguments, result)


def validate_solve_and_substitute(arguments, result):
    return validate_symbolic_operation("solve_and_substitute", arguments, result)


def validate_polynomial_root_filter(arguments, result):
    return validate_symbolic_operation("polynomial_root_filter", arguments, result)


def validate_exact_modular_evaluation(arguments, result):
    return validate_symbolic_operation("exact_modular_evaluation", arguments, result)


def validate_gcd(arguments, result):
    return validate_symbolic_operation("gcd", arguments, result)


def validate_prime_factorization(arguments, result):
    return validate_symbolic_operation("prime_factorization", arguments, result)


def validate_determinant(arguments, result):
    return validate_symbolic_operation("determinant", arguments, result)
