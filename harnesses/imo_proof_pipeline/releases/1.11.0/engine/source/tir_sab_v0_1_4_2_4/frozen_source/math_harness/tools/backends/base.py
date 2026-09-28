"""Shared backend result helpers."""

from __future__ import annotations

from typing import Any


def exact_value_latex(value: Any) -> str:
    """Render exact values with positive terms before subtractive terms."""

    import sympy as sp

    numerator, denominator = sp.fraction(
        sp.together(sp.cancel(sp.simplify(value)))
    )

    def render_sum(expression: Any) -> str:
        if not expression.is_Add:
            return sp.latex(expression)
        terms = list(expression.as_ordered_terms())
        positive = [
            term for term in terms if not term.could_extract_minus_sign()
        ]
        negative = [
            -term for term in terms if term.could_extract_minus_sign()
        ]
        pieces: list[str] = []
        for term in positive:
            rendered = sp.latex(term)
            pieces.append(rendered if not pieces else f"+{rendered}")
        for term in negative:
            rendered = sp.latex(term)
            pieces.append(f"-{rendered}")
        return "".join(pieces) or "0"

    numerator_latex = render_sum(numerator)
    if denominator == 1:
        return numerator_latex
    return rf"\frac{{{numerator_latex}}}{{{render_sum(denominator)}}}"


def backend_result(
    *,
    normalized_result: dict[str, Any],
    certificate: dict[str, Any],
    checked_claim: str,
    derived_answer: str | None = None,
    counterexample: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "normalized_result": normalized_result,
        "certificate": certificate,
        "checked_claim": checked_claim,
        "derived_answer": derived_answer,
        "counterexample": counterexample,
    }
