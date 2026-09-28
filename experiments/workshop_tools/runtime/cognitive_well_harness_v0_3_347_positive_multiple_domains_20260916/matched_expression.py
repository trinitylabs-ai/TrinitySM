"""Closed exact-expression language for explicitly selected computations.

No source documents, file paths, example catalog, or model calls are accepted by
this module. Names have no mathematical meaning beyond their typed definitions.
"""
from __future__ import annotations

from dataclasses import dataclass
import re

import sympy as sp

IDENT = re.compile(r"[A-Za-z][A-Za-z0-9_]{0,47}\Z")
MAX_CHARS = 60000
MAX_NODES = 12000
MAX_EXPANDED_OPERATIONS = 12000


def names(value):
    result = [] if value == "NONE" else [s.strip() for s in value.split(",")]
    if len(result) > 24 or len(result) != len(set(result)) or any(not IDENT.fullmatch(s) for s in result):
        raise ValueError("expected at most 24 unique identifiers, or NONE")
    return result


def expression(value):
    """Parse prefix forms without eval, sympify(string), or executable input."""
    tokens = re.findall(r"\(|\)|[^\s()]+", value)
    if not tokens or len(tokens) > MAX_NODES:
        raise ValueError("expression token limit or empty expression")
    index = 0

    def read(depth=0):
        nonlocal index
        if depth > 48 or index >= len(tokens):
            raise ValueError("expression depth limit or incomplete expression")
        token = tokens[index]
        index += 1
        if token == "(":
            result = []
            while index < len(tokens) and tokens[index] != ")":
                result.append(read(depth + 1))
            if index == len(tokens) or not result or not isinstance(result[0], str):
                raise ValueError("unclosed expression or missing operator")
            index += 1
            return result
        if token == ")":
            raise ValueError("unexpected closing parenthesis")
        if re.fullmatch(r"-?[0-9]{1,19}", token):
            result = int(token)
            if abs(result) > 10**18:
                raise ValueError("integer literal limit")
            return result
        if not IDENT.fullmatch(token):
            raise ValueError("only integer literals and identifiers are accepted")
        return token

    result = read()
    if index != len(tokens):
        raise ValueError("trailing expression tokens")
    return result


def fields(markdown, fence="exact-args"):
    if not isinstance(markdown, str) or len(markdown) > MAX_CHARS:
        raise ValueError("request must be bounded Markdown text")
    match = re.fullmatch(r"```" + re.escape(fence) + r"\r?\n(.*?)\r?\n```", markdown.strip(), re.S)
    if match is None:
        raise ValueError("expected exactly one " + fence + " Markdown fence")
    result = []
    for line in match[1].splitlines():
        if not line.strip():
            continue
        key, sep, body = line.partition(" = ")
        if not sep or not IDENT.fullmatch(key) or not body.strip():
            raise ValueError("expected field = value")
        result.append((key, body.strip()))
    if len(result) > 160:
        raise ValueError("request exceeds 160 fields")
    return result


def labeled(body):
    parts = body.split(" :: ")
    if len(parts) != 2 or not IDENT.fullmatch(parts[0]):
        raise ValueError("expected identifier :: expression")
    return parts[0], expression(parts[1])


def parse_program(markdown, operation):
    rows = fields(markdown)
    if not rows or rows[0][0] != "symbols":
        raise ValueError("symbols must be the first field")
    if operation not in {"exact_geometry", "rational_identity"}:
        raise ValueError("unsupported matched computation")
    program = {"symbols": names(rows[0][1]), "definitions": [], "assumptions": [],
               "checks": [], "emits": []}
    taken, declared, phase = set(program["symbols"]), set(program["symbols"]), 0
    phases = {"define": 1, "assume": 2, "check": 3, "emit": 4}
    for key, body in rows[1:]:
        if key not in phases or phases[key] < phase:
            raise ValueError("unknown field or fields out of order: " + key)
        phase = phases[key]
        if key == "emit":
            if body not in declared or body in program["emits"]:
                raise ValueError("emit requires a unique declared name")
            program["emits"].append(body)
        else:
            label, node = labeled(body)
            if label in taken:
                raise ValueError("duplicate symbol or label: " + label)
            taken.add(label)
            dest = {"define": "definitions", "assume": "assumptions", "check": "checks"}[key]
            program[dest].append((label, node))
            if key == "define":
                declared.add(label)
    if not program["checks"] and not program["emits"]:
        raise ValueError("at least one check or emit is required")
    return program


@dataclass(frozen=True)
class Point:
    x: sp.Expr
    y: sp.Expr


@dataclass(frozen=True)
class Circle:
    # x^2 + y^2 + u*x + v*y + w = 0
    u: sp.Expr
    v: sp.Expr
    w: sp.Expr


@dataclass(frozen=True)
class Predicate:
    relation: str
    residual: sp.Expr
    truth: bool | None


class InvalidInstance(ValueError):
    """An explicitly evaluated instance violates a construction precondition."""


class DerivationUnavailable(ValueError):
    """The bounded linear derivation could not supply a checked candidate."""


def clean(value):
    result = sp.cancel(value)
    if result.has(sp.zoo, sp.nan, sp.oo, -sp.oo) or result.is_real is False:
        raise InvalidInstance("nonfinite or nonreal expression")
    if sp.count_ops(result) > MAX_EXPANDED_OPERATIONS:
        raise ValueError("expanded expression size limit")
    return result


def predicate(relation, residual):
    residual = clean(residual)
    if not residual.free_symbols:
        residual = sp.simplify(residual)
    zero = residual.is_zero
    truth = {"eq": zero, "ne": None if zero is None else not zero,
             "gt": residual.is_positive, "ge": residual.is_nonnegative,
             "lt": residual.is_negative, "le": residual.is_nonpositive}[relation]
    return Predicate(relation, residual, truth)


def payload(value):
    if isinstance(value, Point):
        return {"type": "point", "x": str(value.x), "y": str(value.y)}
    if isinstance(value, Circle):
        return {"type": "circle", "u": str(value.u), "v": str(value.v), "w": str(value.w)}
    if isinstance(value, Predicate):
        return {"relation": value.relation, "residual": str(value.residual), "truth": value.truth}
    return {"type": "scalar", "expression": str(value)}


class Evaluator:
    clean = staticmethod(clean)
    predicate = staticmethod(predicate)

    def __init__(self, symbols=(), assignment=None, *, geometry=True):
        self.env = {name: sp.Symbol(name, real=True) for name in symbols}
        if assignment is not None:
            if set(assignment) != set(symbols):
                raise ValueError("assignment must cover precisely the declared symbols")
            self.env.update(assignment)
        self.geometry = geometry
        self.obligations = []
        self.derivations = []
        self.nodes = 0

    @staticmethod
    def scalar(value):
        if not isinstance(value, sp.Expr):
            raise ValueError("expected an exact scalar")
        return value

    @staticmethod
    def point(value):
        if not isinstance(value, Point):
            raise ValueError("expected a point/vector")
        return value

    @staticmethod
    def circle(value):
        if not isinstance(value, Circle):
            raise ValueError("expected a circle")
        return value

    def require(self, relation, residual, reason):
        pred = self.predicate(relation, residual)
        if pred.truth is False:
            raise InvalidInstance(reason + ": " + str(pred.residual) + " " + relation + " 0 is false")
        row = {**payload(pred), "reason": reason, "_predicate": pred}
        if row not in self.obligations:
            self.obligations.append(row)
        return row

    def divide(self, numerator, denominator, reason="division denominator"):
        self.require("ne", denominator, reason)
        return self.clean(numerator / denominator)

    @classmethod
    def plus(cls, a, b):
        return Point(cls.clean(a.x + b.x), cls.clean(a.y + b.y))

    @classmethod
    def minus(cls, a, b):
        return Point(cls.clean(a.x - b.x), cls.clean(a.y - b.y))

    @classmethod
    def scale(cls, k, a):
        return Point(cls.clean(k * a.x), cls.clean(k * a.y))

    @classmethod
    def dot(cls, a, b):
        return cls.clean(a.x * b.x + a.y * b.y)

    @classmethod
    def cross(cls, a, b):
        return cls.clean(a.x * b.y - a.y * b.x)

    def power(self, circle, point):
        return self.clean(self.dot(point, point) + circle.u * point.x + circle.v * point.y + circle.w)

    def second(self, circle, known, through):
        self.require("eq", self.power(circle, known), "known point must lie on circle")
        direction = self.minus(through, known)
        norm = self.dot(direction, direction)
        coefficient = self.clean(2 * self.dot(known, direction) + circle.u * direction.x + circle.v * direction.y)
        parameter = self.divide(-coefficient, norm, "line needs distinct defining points")
        self.require("ne", parameter, "second intersection must differ from known point (no tangency)")
        result = self.plus(known, self.scale(parameter, direction))
        # Verify the construction algebra; do not turn its desired consequence
        # into an additional assumption. Membership follows from known's power.
        if self.predicate("eq", self.power(circle, result) - self.power(circle, known)).truth is not True:
            raise RuntimeError("second intersection construction failed exact replay")
        return result

    def root(self, op, raw, depth):
        count = 2 if op == "linear_root" else 3
        if len(raw) != count or any(not isinstance(s, str) or not isinstance(self.env.get(s), sp.Symbol) for s in raw[:-1]):
            raise ValueError(op + " requires declared symbolic names followed by a scalar expression")
        variable = self.env[raw[0]]
        parameter = None if count == 2 else self.env[raw[1]]
        if variable == parameter:
            raise ValueError("root unknown and coefficient parameter must differ")
        value = self.scalar(self.decode(raw[-1], depth + 1))
        numerator, denominator = sp.fraction(self.clean(value))
        try:
            equations = [numerator] if parameter is None else sp.Poly(numerator, parameter).all_coeffs()
            polynomials = [sp.Poly(e, variable) for e in equations]
        except sp.PolynomialError as error:
            raise ValueError("root requires polynomial numerators in the selected variables") from error
        if any(p.degree() > 1 for p in polynomials):
            raise DerivationUnavailable("only equations linear in the selected unknown are supported")
        pivot = next((p for p in polynomials if p.degree() == 1), None)
        if pivot is None:
            raise DerivationUnavailable("no linear pivot; no candidate root was derived")
        coefficient = pivot.nth(1)
        candidate = self.divide(-pivot.nth(0), coefficient, "linear root pivot (exceptional zero-pivot cases remain)")
        if parameter is not None and parameter in candidate.free_symbols:
            raise DerivationUnavailable("coefficient root still depends on the coefficient parameter")
        residuals = [self.clean(e.subs(variable, candidate)) for e in equations]
        if any(self.predicate("eq", r).truth is not True for r in residuals):
            raise DerivationUnavailable("linear candidate does not annihilate every coefficient")
        self.require("ne", self.clean(denominator.subs(variable, candidate)), "derived root must be in the original rational expression domain")
        # Preserve even denominators that canceled inside the scoped expression.
        # Previously defined expressions retain their original obligations too.
        for row in list(self.obligations):
            # The exact objects are maintained separately; displayed strings are
            # never parsed back into executable or symbolic input.
            pred = row["_predicate"]
            if variable in pred.residual.free_symbols:
                self.require(pred.relation, self.clean(pred.residual.subs(variable, candidate)), "derived root: " + row["reason"])
        self.derivations.append({"kind": op, "unknown": str(variable),
            "coefficient_parameter": None if parameter is None else str(parameter),
            "source_expression": str(value), "candidate": str(candidate),
            "pivot": str(coefficient), "coefficient_residuals": [str(r) for r in residuals],
            "substitution_verified": True, "scope": "candidate under recorded conditions; no completeness or exceptional-branch claim"})
        return candidate

    def decode(self, node, depth=0):
        self.nodes += 1
        if self.nodes > MAX_NODES or depth > 48:
            raise ValueError("AST evaluation size/depth limit")
        if type(node) is int:
            return sp.Integer(node)
        if isinstance(node, str):
            if node not in self.env:
                raise ValueError("unknown or forward-referenced name: " + node)
            return self.env[node]
        if not isinstance(node, list) or not node:
            raise ValueError("invalid expression")
        op, raw = node[0], node[1:]
        if op in {"linear_root", "coefficient_root"}:
            return self.root(op, raw, depth)
        if op == "symbol" and len(raw) == 1 and isinstance(raw[0], str):
            return self.decode(raw[0], depth + 1)
        if op == "differentiate":
            if len(raw) != 2 or not isinstance(raw[1], str) or not isinstance(self.env.get(raw[1]), sp.Symbol):
                raise ValueError("differentiate needs an expression and a declared symbolic variable")
            return self.clean(sp.diff(self.scalar(self.decode(raw[0], depth + 1)), self.env[raw[1]]))
        args = [self.decode(arg, depth + 1) for arg in raw]
        if op in {"add", "mul"} and 2 <= len(args) <= 64:
            args = [self.scalar(arg) for arg in args]
            return self.clean(sp.Add(*args) if op == "add" else sp.Mul(*args))
        if op in {"sub", "div", "rational", "pow", "eq", "ne", "gt", "ge", "lt", "le"} and len(args) == 2:
            if self.geometry and op in {"eq", "ne"} and all(isinstance(a, Point) for a in args):
                difference = self.minus(*args)
                return self.predicate(op, self.dot(difference, difference))
            a, b = map(self.scalar, args)
            if op in {"eq", "ne", "gt", "ge", "lt", "le"}:
                return self.predicate(op, a - b)
            if op == "sub":
                return self.clean(a - b)
            if op == "rational" and (not a.is_Integer or not b.is_Integer):
                raise ValueError("rational requires two integer literals")
            if op in {"div", "rational"}:
                return self.divide(a, b)
            if not b.is_Integer or not -16 <= b <= 32:
                raise ValueError("power exponent must be an integer in -16..32")
            if b < 0:
                self.require("ne", a, "negative power base")
            return self.clean(a**b)
        if op in {"neg", "sqrt"} and len(args) == 1:
            a = self.scalar(args[0])
            if op == "neg":
                return self.clean(-a)
            if a.free_symbols or a.is_nonnegative is not True:
                raise ValueError("sqrt requires a proven nonnegative exact constant")
            return self.clean(sp.sqrt(a))
        if not self.geometry:
            raise ValueError("unsupported scalar operation or arity: " + str(op))
        if op == "point" and len(args) == 2:
            return Point(*map(self.scalar, args))
        if op in {"vadd", "vsub", "dot", "cross", "midpoint"} and len(args) == 2:
            a, b = map(self.point, args)
            if op == "midpoint":
                return self.scale(sp.Rational(1, 2), self.plus(a, b))
            return {"vadd": self.plus, "vsub": self.minus, "dot": self.dot, "cross": self.cross}[op](a, b)
        if op == "scale" and len(args) == 2:
            return self.scale(self.scalar(args[0]), self.point(args[1]))
        if op in {"x", "y", "norm2"} and len(args) == 1:
            a = self.point(args[0])
            return self.dot(a, a) if op == "norm2" else getattr(a, op)
        if op == "foot" and len(args) == 3:
            p, a, b = map(self.point, args)
            direction = self.minus(b, a)
            t = self.divide(self.dot(self.minus(p, a), direction), self.dot(direction, direction), "foot needs distinct line points")
            return self.plus(a, self.scale(t, direction))
        if op == "line_intersection" and len(args) == 4:
            a, b, c, d = map(self.point, args)
            v, w = self.minus(b, a), self.minus(d, c)
            t = self.divide(self.cross(self.minus(c, a), w), self.cross(v, w), "lines must have a unique intersection")
            return self.plus(a, self.scale(t, v))
        if op == "circle" and len(args) == 3:
            a, b, c = map(self.point, args)
            v, w = self.minus(b, a), self.minus(c, a)
            r, s = self.dot(a, a) - self.dot(b, b), self.dot(a, a) - self.dot(c, c)
            determinant = self.cross(v, w)
            u = self.divide(r * w.y - s * v.y, determinant, "circle needs noncollinear defining points")
            vcoef = self.divide(v.x * s - w.x * r, determinant, "circle needs noncollinear defining points")
            return Circle(u, vcoef, self.clean(-self.dot(a, a) - u * a.x - vcoef * a.y))
        if op == "circle_center_radius" and len(args) == 2:
            center, radius = self.point(args[0]), self.scalar(args[1])
            self.require("gt", radius, "circle radius must be positive")
            return Circle(-2 * center.x, -2 * center.y, self.clean(self.dot(center, center) - radius**2))
        if op == "center" and len(args) == 1:
            c = self.circle(args[0])
            return Point(self.clean(-c.u / 2), self.clean(-c.v / 2))
        if op == "power" and len(args) == 2:
            return self.power(self.circle(args[0]), self.point(args[1]))
        if op == "second_on_line" and len(args) == 3:
            return self.second(self.circle(args[0]), self.point(args[1]), self.point(args[2]))
        if op == "second_on_circles" and len(args) == 3:
            c, d, p = self.circle(args[0]), self.circle(args[1]), self.point(args[2])
            self.require("eq", self.power(d, p), "known point must lie on second circle")
            direction = Point(self.clean(c.v - d.v), self.clean(d.u - c.u))
            result = self.second(c, p, self.plus(p, direction))
            if self.predicate("eq", self.power(d, result) - self.power(d, p)).truth is not True:
                raise RuntimeError("second circle construction failed exact replay")
            return result
        if op == "invert_point" and len(args) == 3:
            center, factor, point = self.point(args[0]), self.scalar(args[1]), self.point(args[2])
            self.require("ne", factor, "inversion factor must be nonzero")
            displacement = self.minus(point, center)
            t = self.divide(factor, self.dot(displacement, displacement), "point must differ from inversion center")
            return self.plus(center, self.scale(t, displacement))
        if op == "invert_line" and len(args) == 4:
            center, factor = self.point(args[0]), self.scalar(args[1])
            a, b = self.point(args[2]), self.point(args[3])
            self.require("ne", factor, "inversion factor must be nonzero")
            direction = self.minus(b, a)
            t = self.divide(factor, self.cross(direction, self.minus(center, a)),
                            "inverted line must be defined and must not pass through inversion center")
            # Substitute X = center + factor*(Y-center)/|Y-center|^2
            # into cross(B-A, X-A)=0 and normalize the quadratic coefficient.
            return Circle(self.clean(-2 * center.x - t * direction.y),
                          self.clean(-2 * center.y + t * direction.x),
                          self.clean(self.dot(center, center) - t * self.cross(direction, center)))
        raise ValueError("unsupported operation or arity: " + str(op))


def evaluate(program, assignment=None, *, geometry=True):
    ev = Evaluator(program["symbols"], assignment, geometry=geometry)
    for label, node in program["definitions"]:
        value = ev.decode(node)
        if isinstance(value, Predicate):
            raise ValueError("definitions must be scalars, points, or circles")
        ev.env[label] = value
    assumptions, checks = [], []
    for dest, rows in ((assumptions, program["assumptions"]), (checks, program["checks"])):
        for label, node in rows:
            value = ev.decode(node)
            if not isinstance(value, Predicate):
                raise ValueError("assume/check requires a comparison predicate")
            dest.append({"label": label, **payload(value)})
    return ev, assumptions, checks
