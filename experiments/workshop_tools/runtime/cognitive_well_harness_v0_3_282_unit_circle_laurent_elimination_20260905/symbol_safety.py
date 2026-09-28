"""Safe legacy polynomial decoding and deterministic, display-safe fresh names."""
from __future__ import annotations

import ast
import sympy as sp


class FreshNames:
    """Reserve both identifiers and their printed mathematical spellings."""

    def __init__(self, names=()):
        self.identifiers = {str(name) for name in names}
        self.displays = {sp.latex(sp.Symbol(name)) for name in self.identifiers}

    def take(self, preferred):
        candidate = str(preferred)
        index = 0
        while candidate in self.identifiers or sp.latex(sp.Symbol(candidate)) in self.displays:
            index += 1
            candidate = f"{preferred}_cert{index}"
        self.identifiers.add(candidate)
        self.displays.add(sp.latex(sp.Symbol(candidate)))
        return sp.Symbol(candidate)


def parse_polynomial(text, symbols, *, complex_coefficients=True):
    """Decode scalar syntax without eval; reject ambiguous old QQ(i) records.

    Legacy strings use I for the imaginary unit. If a polynomial variable is also
    called I, no decoder can recover which meaning a string intended. Fail closed
    instead of changing its mathematics. Rational source-guard strings have no
    such ambiguity and preserve an original variable named I.
    """
    names = {str(symbol): symbol for symbol in symbols}
    if complex_coefficients:
        if "I" in names:
            raise ValueError("ambiguous legacy QQ(i) symbol I; use a fresh formal variable before certificate generation")
        names["I"] = sp.I
    tree = ast.parse(str(text), mode="eval")
    if sum(1 for _ in ast.walk(tree)) > 500_000:
        raise ValueError("saved polynomial exceeds the AST limit")

    # Long exported sums produce a left-deep Python AST. Traverse explicitly so
    # a valid, bounded certificate cannot exhaust Python's recursion stack.
    pending = [(tree.body, False)]
    values = []
    while pending:
        node, visited = pending.pop()
        if isinstance(node, ast.Constant) and type(node.value) is int:
            values.append(sp.Integer(node.value))
            continue
        if isinstance(node, ast.Name) and node.id in names:
            values.append(names[node.id])
            continue
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            if not visited:
                pending.extend(((node, True), (node.operand, False)))
                continue
            value = values.pop()
            values.append(-value if isinstance(node.op, ast.USub) else value)
            continue
        if isinstance(node, ast.BinOp):
            if not visited:
                pending.extend(((node, True), (node.right, False), (node.left, False)))
                continue
            right, left = values.pop(), values.pop()
            if isinstance(node.op, ast.Add):
                value = left + right
            elif isinstance(node.op, ast.Sub):
                value = left - right
            elif isinstance(node.op, ast.Mult):
                value = left * right
            elif isinstance(node.op, ast.Div) and right.is_Rational and right != 0:
                value = left / right
            elif isinstance(node.op, ast.Pow) and right.is_Integer and 0 <= right <= 1000:
                value = left ** right
            else:
                raise ValueError("unsupported saved polynomial expression")
            values.append(value)
            continue
        raise ValueError("unsupported saved polynomial expression")

    domain = {"extension": sp.I} if complex_coefficients else {"domain": sp.QQ}
    if len(values) != 1:
        raise ValueError("malformed saved polynomial traversal")
    return sp.Poly(values[0], *symbols, **domain).as_expr()
