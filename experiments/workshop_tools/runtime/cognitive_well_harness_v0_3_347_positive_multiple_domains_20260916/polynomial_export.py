"""Exact QQ(i) polynomials in Singular syntax, independent of SymPy printing.

Singular parses ``x^2/2`` as a power with a number exponent and rejects it.
Emit coefficients separately from monomials and delimit every power. This is
serialization only: no denominator clearing, scaling, or extra assumptions.
"""
from __future__ import annotations

import re

import sympy as sp

POLICY = "exact-qqi-coefficient-monomial-v1"


def _rational(value):
    value = sp.Rational(value)
    return str(value.p) if value.q == 1 else f"({value.p}/{value.q})"


def _coefficient(value):
    real, imaginary = value.as_real_imag()
    if imaginary == 0:
        return f"({_rational(real)})"
    return f"({_rational(real)}+({_rational(imaginary)})*ii)"


def expression(value: sp.Expr) -> str:
    value = sp.sympify(value)
    if value.has(sp.Float):
        raise ValueError("Singular export requires exact coefficients")
    symbols = sorted(value.free_symbols, key=sp.default_sort_key)
    names = [str(symbol) for symbol in symbols]
    if len(set(names)) != len(names) or any(
        name == "ii" or re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", name) is None
        for name in names
    ):
        raise ValueError("Singular export requires distinct safe polynomial symbols")
    if not symbols:
        return _coefficient(sp.QQ_I.to_sympy(sp.QQ_I.convert(value)))
    polynomial = sp.Poly(value, *symbols, domain=sp.QQ_I)
    if polynomial.is_zero:
        return "0"
    terms = []
    for powers, coefficient in polynomial.terms():
        factors = [_coefficient(coefficient)]
        for name, power in zip(names, powers, strict=True):
            if power:
                factors.append(name if power == 1 else f"({name}^{power})")
        terms.append("*".join(factors))
    return "+".join(terms)
