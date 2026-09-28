"""Conservative, exact normalization of closed numeric inline mathematics.

No model calls, symbolic simplification, prose rewriting, eval, or user-code
execution. Unsupported expressions remain opaque and cannot establish a match.
"""
from __future__ import annotations

import ast
from fractions import Fraction
from math import comb
import re


POLICY = "closed-numeric-classification-v1"
MAX_CHARS = 512
MAX_BITS = 4096
_INTEGER = r"[+-]?\d{1,64}"
_BINOM = re.compile(r"\\(?:binom|tbinom|dbinom)\s*\{\s*(" + _INTEGER + r")\s*\}\s*\{\s*(" + _INTEGER + r")\s*\}")
_FRAC = re.compile(r"\\(?:frac|tfrac|dfrac)\s*\{\s*(" + _INTEGER + r")\s*\}\s*\{\s*(" + _INTEGER + r")\s*\}")
_INLINE = re.compile(r"(?<![\\$])\$(?!\$)([^$\n]+)\$(?!\$)|\\\(([^\n]*?)\\\)")


def _bounded(value: Fraction) -> Fraction:
    if max(value.numerator.bit_length(), value.denominator.bit_length()) > MAX_BITS:
        raise ValueError("numeric expression exceeds size bound")
    return value


def _evaluate(node: ast.AST, depth: int = 0) -> Fraction:
    if depth > 16:
        raise ValueError("numeric expression exceeds depth bound")
    child = lambda item: _evaluate(item, depth + 1)
    if isinstance(node, ast.Constant) and type(node.value) is int:
        return _bounded(Fraction(node.value))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = child(node.operand)
        return value if isinstance(node.op, ast.UAdd) else -value
    if isinstance(node, ast.BinOp):
        left, right = child(node.left), child(node.right)
        if isinstance(node.op, ast.Add):
            return _bounded(left + right)
        if isinstance(node.op, ast.Sub):
            return _bounded(left - right)
        if isinstance(node.op, ast.Mult):
            return _bounded(left * right)
        if isinstance(node.op, ast.Div):
            return _bounded(left / right)
        if isinstance(node.op, ast.Pow) and right.denominator == 1 and abs(right) <= 64:
            if left == right == 0:
                raise ValueError("zero to the zeroth power requires a convention")
            return _bounded(left ** int(right))
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id == "comb" and len(node.args) == 2 and not node.keywords):
        n, k = (child(arg) for arg in node.args)
        if n.denominator == k.denominator == 1 and 0 <= k <= n <= 1024:
            return _bounded(Fraction(comb(int(n), int(k))))
    raise ValueError("not allowlisted closed arithmetic")


def exact_numeric_value(expression: str) -> Fraction:
    if not expression.strip() or len(expression) > MAX_CHARS:
        raise ValueError("empty or oversized expression")
    text = _BINOM.sub(lambda m: f"comb({m[1]},{m[2]})", expression)
    text = _FRAC.sub(lambda m: f"({m[1]}/{m[2]})", text)
    text = re.sub(r"\\(?:times|cdot)(?![A-Za-z])", "*", text)
    text = text.replace("−", "-").replace("×", "*").replace("÷", "/")
    text = text.replace("^", "**").replace("{", "(").replace("}", ")").strip()
    # Reject Python-specific literal forms, strings, attributes and comparisons.
    if (not re.fullmatch(r"[0-9comb(),+*/\s.-]+", text) or "." in text
            or re.search(r"\b0[bo]", text)):
        raise ValueError("unsupported arithmetic notation")
    if re.search(r"\d{65}", text):
        raise ValueError("integer literal exceeds size bound")
    nesting = 0
    for character in text:
        if character == "(":
            nesting += 1
            if nesting > 32:
                raise ValueError("numeric expression exceeds nesting bound")
        elif character == ")":
            nesting -= 1
    parsed = ast.parse(text, mode="eval")
    if sum(1 for _ in ast.walk(parsed)) > 128:
        raise ValueError("numeric expression exceeds node bound")
    return _evaluate(parsed.body)


def _canonicalize(value: str) -> tuple[str, list[dict[str, str]]]:
    steps = []

    def replace(match: re.Match[str]) -> str:
        # Never merge into a word/number or remove grouping next to math syntax.
        unsafe_boundary = r"[\w$+*/^=<>\\{}()\[\]|−-]"
        if ((match.start() and re.match(unsafe_boundary, value[match.start() - 1]))
                or (match.end() < len(value) and re.match(unsafe_boundary, value[match.end()]))):
            return match[0]
        expression = match[1] if match[1] is not None else match[2]
        try:
            terms = [exact_numeric_value(term) for term in expression.split("=")]
            if not all(term == terms[0] for term in terms):
                return match[0]  # A printed equality is not trusted as a certificate.
        except (ValueError, SyntaxError, ArithmeticError, RecursionError):
            return match[0]
        canonical = str(terms[0])
        steps.append({"source": match[0], "exact_value": canonical})
        return canonical

    canonical = _INLINE.sub(replace, value)
    # Preserve case as well as qualifiers: distinct mathematical symbols must not
    # become equal via this additional acceptance path. Legacy matching is separate.
    return re.sub(r"\s+", " ", canonical).strip(), steps


def numeric_classification_equivalence(original: str, repaired: str) -> dict | None:
    left, left_steps = _canonicalize(original)
    right, right_steps = _canonicalize(repaired)
    if left != right or not (left_steps or right_steps):
        return None
    return {"policy": POLICY, "canonical_classification": left,
            "original_steps": left_steps, "repaired_steps": right_steps}
