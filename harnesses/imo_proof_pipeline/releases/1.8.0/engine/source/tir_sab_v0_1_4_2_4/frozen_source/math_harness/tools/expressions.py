"""Safe structured mathematical expressions for whitelisted tool operations."""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Any, Mapping


class ExpressionError(ValueError):
    pass


_SYMBOL_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,31}$")


def validate_symbol_name(value: Any) -> str:
    text = str(value)
    if not _SYMBOL_RE.fullmatch(text):
        raise ExpressionError(f"invalid symbol name: {value!r}")
    return text


def validate_expression(
    value: Any,
    *,
    allowed_symbols: set[str] | frozenset[str],
    depth: int = 0,
) -> Any:
    if depth > 32:
        raise ExpressionError("expression nesting exceeds 32")
    if isinstance(value, bool):
        raise ExpressionError("booleans are not mathematical scalars")
    if isinstance(value, int):
        return value
    if not isinstance(value, Mapping) or len(value) != 1:
        raise ExpressionError("expression nodes must be integers or one-key objects")
    kind, payload = next(iter(value.items()))
    if kind == "symbol":
        symbol = validate_symbol_name(payload)
        if symbol not in allowed_symbols:
            raise ExpressionError(f"unregistered symbol: {symbol}")
        return {"symbol": symbol}
    if kind == "rational":
        if (
            not isinstance(payload, list)
            or len(payload) != 2
            or not all(isinstance(item, int) and not isinstance(item, bool) for item in payload)
            or payload[1] == 0
        ):
            raise ExpressionError("rational must be [integer numerator, nonzero denominator]")
        fraction = Fraction(payload[0], payload[1])
        return {"rational": [fraction.numerator, fraction.denominator]}
    if kind in {"add", "mul"}:
        if not isinstance(payload, list) or not 2 <= len(payload) <= 64:
            raise ExpressionError(f"{kind} requires 2 through 64 arguments")
        return {
            kind: [
                validate_expression(
                    item, allowed_symbols=allowed_symbols, depth=depth + 1
                )
                for item in payload
            ]
        }
    if kind in {"sub", "div", "pow"}:
        if not isinstance(payload, list) or len(payload) != 2:
            raise ExpressionError(f"{kind} requires exactly two arguments")
        result = [
            validate_expression(
                item, allowed_symbols=allowed_symbols, depth=depth + 1
            )
            for item in payload
        ]
        if kind == "pow":
            exponent = result[1]
            if not isinstance(exponent, int) or not -64 <= exponent <= 64:
                raise ExpressionError("power exponent must be an integer from -64 to 64")
        return {kind: result}
    if kind in {"neg", "abs"}:
        return {
            kind: validate_expression(
                payload, allowed_symbols=allowed_symbols, depth=depth + 1
            )
        }
    raise ExpressionError(f"unsupported expression node: {kind}")


def to_sympy(value: Any, symbols: Mapping[str, Any]) -> Any:
    import sympy as sp

    normalized = validate_expression(value, allowed_symbols=frozenset(symbols))
    if isinstance(normalized, int):
        return sp.Integer(normalized)
    kind, payload = next(iter(normalized.items()))
    if kind == "symbol":
        return symbols[payload]
    if kind == "rational":
        return sp.Rational(payload[0], payload[1])
    if kind == "add":
        return sp.Add(*(to_sympy(item, symbols) for item in payload))
    if kind == "mul":
        return sp.Mul(*(to_sympy(item, symbols) for item in payload))
    if kind == "sub":
        return to_sympy(payload[0], symbols) - to_sympy(payload[1], symbols)
    if kind == "div":
        return to_sympy(payload[0], symbols) / to_sympy(payload[1], symbols)
    if kind == "pow":
        return to_sympy(payload[0], symbols) ** int(payload[1])
    if kind == "neg":
        return -to_sympy(payload, symbols)
    if kind == "abs":
        return sp.Abs(to_sympy(payload, symbols))
    raise AssertionError(kind)


def symbol_table(names: list[str]) -> dict[str, Any]:
    import sympy as sp

    normalized = [validate_symbol_name(value) for value in names]
    if len(set(normalized)) != len(normalized):
        raise ExpressionError("symbol names must be unique")
    return {name: sp.Symbol(name) for name in normalized}
