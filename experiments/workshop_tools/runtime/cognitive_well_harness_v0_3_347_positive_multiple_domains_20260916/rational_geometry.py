"""Exact rational arithmetic without global symbolic assumption queries.

Geometry coordinates live in a rational function field over real symbols.
Original division obligations remain in the evaluator, even after cancellation.
No mathematical source data or assignments are used here.
"""
from functools import lru_cache
import sympy as sp
from sympy.polys.fields import field
from . import matched_expression as syntax

MAX_INTERMEDIATE_PRODUCTS = 25000


def bounded_fraction(value, domain):
    """Bound sparse polynomial work *before* fraction multiplication/GCD.

    This is a conservative resource gate, never an algebraic assertion. Rejected
    expressions may simplify to something small; they need a smaller encoding.
    """
    mapping = dict(zip(domain.symbols, domain.gens))

    def combine(a, b, addition=False):
        if addition and a.denom == b.denom:
            work = len(a.numer) + len(b.numer)
        elif addition:
            work = len(a.numer)*len(b.denom) + len(b.numer)*len(a.denom) + len(a.denom)*len(b.denom)
        else:
            work = len(a.numer)*len(b.numer) + len(a.denom)*len(b.denom)
        if work > MAX_INTERMEDIATE_PRODUCTS:
            raise ValueError('rational intermediate size limit')
        return a+b if addition else a*b

    def visit(expr):
        if expr in mapping:
            return mapping[expr]
        if expr.is_Add or expr.is_Mul:
            values = [visit(arg) for arg in expr.args]
            while len(values) > 1:
                values = [combine(values[i],values[i+1],expr.is_Add) if i+1 < len(values)
                          else values[i] for i in range(0,len(values),2)]
            return values[0]
        if expr.is_Pow and expr.exp.is_Integer:
            base = visit(expr.base)
            exponent = int(expr.exp)
            if exponent < 0:
                base = domain.one/base
                exponent = -exponent
            result = domain.one
            while exponent:
                if exponent & 1:
                    result = combine(result,base)
                exponent >>= 1
                if exponent:
                    base = combine(base,base)
            return result
        return domain.from_expr(expr)

    return visit(value)

@lru_cache(maxsize=64)
def rational_field(symbols):
    return field(symbols, sp.QQ)[0]


def clean(value):
    value = sp.sympify(value)
    symbols = tuple(sorted(value.free_symbols, key=str))
    if not symbols:
        return syntax.clean(value)
    if not all(s.is_real is True for s in symbols):
        return syntax.clean(value)
    try:
        fraction = bounded_fraction(value,rational_field(symbols))
    except ValueError as error:
        if str(error) == 'rational intermediate size limit':
            raise
        # Preserve the existing exact-constant and unsupported-expression rules.
        return syntax.clean(value)
    result = fraction.as_expr()
    if sp.count_ops(result) > syntax.MAX_EXPANDED_OPERATIONS:
        raise ValueError('expanded expression size limit')
    return result


def predicate(relation, residual):
    residual = clean(residual)
    if not residual.free_symbols:
        return syntax.predicate(relation, residual)
    # A symbolic rational function's sign is established by the checked guard
    # prover. Querying SymPy's assumptions here can dominate construction time.
    return syntax.Predicate(relation, residual, None)
