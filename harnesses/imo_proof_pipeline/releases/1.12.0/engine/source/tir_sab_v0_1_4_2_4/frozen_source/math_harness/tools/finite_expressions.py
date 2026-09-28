"""Safe Boolean/integer expressions for finite exhaustive searches."""

from __future__ import annotations

from typing import Any, Mapping, Sequence


class FiniteExpressionError(ValueError):
    pass


def validate_finite_expression(
    value: Any,
    *,
    variable_count: int,
    depth: int = 0,
) -> Any:
    if depth > 32:
        raise FiniteExpressionError("finite expression nesting exceeds 32")
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if not isinstance(value, Mapping) or len(value) != 1:
        raise FiniteExpressionError("finite expression must be scalar or one-key object")
    kind, payload = next(iter(value.items()))
    if kind == "var":
        if not isinstance(payload, int) or not 0 <= payload < variable_count:
            raise FiniteExpressionError("variable index is out of range")
        return {"var": payload}
    if kind in {"add", "mul", "and", "or"}:
        if not isinstance(payload, list) or not 2 <= len(payload) <= 64:
            raise FiniteExpressionError(f"{kind} requires 2 through 64 arguments")
        return {
            kind: [
                validate_finite_expression(
                    item, variable_count=variable_count, depth=depth + 1
                )
                for item in payload
            ]
        }
    if kind in {"sub", "mod", "eq", "ne", "lt", "le", "gt", "ge", "pow"}:
        if not isinstance(payload, list) or len(payload) != 2:
            raise FiniteExpressionError(f"{kind} requires two arguments")
        result = [
            validate_finite_expression(
                item, variable_count=variable_count, depth=depth + 1
            )
            for item in payload
        ]
        if kind == "pow" and (
            not isinstance(result[1], int) or not 0 <= result[1] <= 16
        ):
            raise FiniteExpressionError("finite power must be an integer from 0 to 16")
        if kind == "mod" and (
            not isinstance(result[1], int) or not 2 <= result[1] <= 10**9
        ):
            raise FiniteExpressionError("modulus must be a fixed integer")
        return {kind: result}
    if kind in {"neg", "not"}:
        return {
            kind: validate_finite_expression(
                payload, variable_count=variable_count, depth=depth + 1
            )
        }
    raise FiniteExpressionError(f"unsupported finite expression node: {kind}")


def evaluate_finite_expression(value: Any, assignment: Sequence[int]) -> int | bool:
    if isinstance(value, (bool, int)):
        return value
    kind, payload = next(iter(value.items()))
    if kind == "var":
        return int(assignment[payload])
    if kind == "add":
        return sum(int(evaluate_finite_expression(item, assignment)) for item in payload)
    if kind == "mul":
        result = 1
        for item in payload:
            result *= int(evaluate_finite_expression(item, assignment))
        return result
    if kind == "sub":
        return int(evaluate_finite_expression(payload[0], assignment)) - int(
            evaluate_finite_expression(payload[1], assignment)
        )
    if kind == "pow":
        return int(evaluate_finite_expression(payload[0], assignment)) ** int(payload[1])
    if kind == "mod":
        return int(evaluate_finite_expression(payload[0], assignment)) % int(payload[1])
    if kind == "neg":
        return -int(evaluate_finite_expression(payload, assignment))
    if kind == "not":
        return not bool(evaluate_finite_expression(payload, assignment))
    if kind == "and":
        return all(bool(evaluate_finite_expression(item, assignment)) for item in payload)
    if kind == "or":
        return any(bool(evaluate_finite_expression(item, assignment)) for item in payload)
    left = evaluate_finite_expression(payload[0], assignment)
    right = evaluate_finite_expression(payload[1], assignment)
    return {
        "eq": left == right,
        "ne": left != right,
        "lt": left < right,
        "le": left <= right,
        "gt": left > right,
        "ge": left >= right,
    }[kind]
