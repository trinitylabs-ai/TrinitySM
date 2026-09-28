"""Whitelisted exact symbolic operations.

SymPy is imported lazily so routing and schema tests remain usable in minimal
environments. A missing dependency becomes ``unknown`` at the executor layer.
"""

from __future__ import annotations

from typing import Any

from .base import backend_result


def rational_product_equal_minima(arguments: dict[str, Any]) -> dict[str, Any]:
    """Solve the equal-positive-minima condition for Π(x-r_i)(x-k)/x.

    If the same minimum value ``M`` occurs at positive ``u`` and ``v``, then
    ``P(x)-M*x`` is the monic quartic ``(x-u)^2(x-v)^2``. Coefficient matching
    gives a polynomial condition on ``k``; domain filtering removes solutions
    whose paired stationary points are not both positive.
    """

    import sympy as sp

    roots = [sp.Integer(value) for value in arguments["fixed_roots"]]
    if len(roots) != 3 or len(set(roots)) != 3 or any(value <= 0 for value in roots):
        raise ValueError("fixed_roots must contain three distinct positive integers")
    variable = str(arguments.get("variable", "k"))
    if not variable.isidentifier():
        raise ValueError("variable must be an identifier")
    k = sp.symbols(variable, real=True)
    z = sp.symbols("z", real=True)
    root_sum = sum(roots)
    pair_sum = sum(roots[i] * roots[j] for i in range(3) for j in range(i + 1, 3))
    root_product = sp.prod(roots)
    uv_sum = (root_sum + k) / 2
    uv_product = sp.simplify((pair_sum + root_sum * k - uv_sum**2) / 2)
    condition = sp.factor(sp.together(uv_product**2 - root_product * k))
    numerator = sp.Poly(sp.fraction(condition)[0], k)
    factorization = sp.factor(numerator.as_expr())
    candidate_roots = sorted(
        {
            sp.simplify(value)
            for value in sp.solve(numerator.as_expr(), k)
            if value.is_real is True and value > 0
        },
        key=sp.default_sort_key,
    )
    admissible: list[Any] = []
    stationary_pairs: dict[str, list[str]] = {}
    for candidate in candidate_roots:
        sum_value = sp.simplify(uv_sum.subs(k, candidate))
        product_value = sp.simplify(uv_product.subs(k, candidate))
        pair = sp.solve(z**2 - sum_value * z + product_value, z)
        stationary_pairs[str(candidate)] = [str(sp.simplify(item)) for item in pair]
        if (
            len(pair) == 2
            and all(item.is_real is True and item > 0 for item in pair)
            and pair[0] != pair[1]
        ):
            admissible.append(candidate)
    answer = sp.simplify(sum(admissible))
    checked = (
        "Find positive parameter values for which the rational product with "
        f"fixed roots {[int(value) for value in roots]} attains its positive-domain "
        "minimum at two distinct points."
    )
    return backend_result(
        normalized_result={
            "condition_coefficients": [int(value) for value in numerator.all_coeffs()],
            "factorization": str(factorization),
            "candidate_parameters": [str(value) for value in candidate_roots],
            "admissible_parameters": [str(value) for value in admissible],
            "stationary_pairs": stationary_pairs,
            "answer": str(answer),
        },
        certificate={
            "fixed_roots": [int(value) for value in roots],
            "root_sum": str(root_sum),
            "pair_sum": str(pair_sum),
            "root_product": str(root_product),
            "uv_sum": str(uv_sum),
            "uv_product": str(uv_product),
        },
        checked_claim=checked,
        derived_answer=str(answer),
    )
