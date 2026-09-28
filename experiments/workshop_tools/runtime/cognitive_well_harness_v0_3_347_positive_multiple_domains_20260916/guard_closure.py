"""Bounded sparse sums, justified by exactly replayed strict product signs."""
from __future__ import annotations

import itertools
import sympy as sp
from . import relative_sign

SCHEMA = 'strict-same-sign-sum-nonzero-v1'
MAX_BASE = 16
MAX_DERIVED = 16
WEIGHTS = (sp.Integer(1), sp.Rational(1, 2), sp.Integer(2))


def canonical(value, symbols):
    return sp.Poly(sp.expand(value), *symbols, domain=sp.QQ).monic().as_expr()


def replay(expression, symbols, facts, nonzeros, receipt):
    if receipt.get('schema') != SCHEMA or receipt.get('expression') != str(expression):
        raise ValueError('sum guard target mismatch')
    names = {str(s): s for s in symbols}
    left = sp.sympify(receipt['left'], locals=names)
    right = sp.sympify(receipt['right'], locals=names)
    weight = sp.Rational(receipt['weight'])
    if weight <= 0:
        raise ValueError('sum guard requires a positive weight')
    sign = relative_sign.replay(sp.expand(left*right), symbols, facts, nonzeros,
                                receipt['strict_product'])
    total = sp.expand(left + sign*weight*right)
    # With left*right of the replayed strict sign, the middle term is positive.
    # Thus total^2 = left^2 + 2*sign*weight*left*right + weight^2*right^2 > 0.
    if sp.expand(total**2-left**2-2*sign*weight*left*right-weight**2*right**2) != 0:
        raise ValueError('sum guard square identity failed')
    quotient, remainder = sp.div(total, expression, *symbols)
    if total == 0 or expression == 0 or remainder != 0:
        raise ValueError('sum guard is not a factor of a proved nonzero sum')
    if receipt['multiplier'] != str(quotient) or sp.expand(total-expression*quotient) != 0:
        raise ValueError('sum guard factor identity failed')
    return True


def derive(base, symbols, facts, nonzeros):
    """Use only current proved guards and current geometric premises.

    Small rational weights and term limits bound discovery. Each accepted factor
    is independently replayed; no unsuccessful sign query becomes an assumption.
    """
    values = sorted({canonical(v, symbols) for v in base if v != 0},
                    key=lambda v:(sp.Poly(v,*symbols).total_degree(),sp.count_ops(v),str(v)))[:MAX_BASE]
    known = set(values)
    found = {}
    for left, right in itertools.combinations(values, 2):
        # Filter cheap candidate sums before invoking exact sign reasoning.
        possibilities = []
        input_terms = len(sp.Poly(left,*symbols).terms()) + len(sp.Poly(right,*symbols).terms())
        for weight in WEIGHTS:
            for sign in (1,-1):
                total = sp.expand(left + sign*weight*right)
                poly = sp.Poly(total,*symbols)
                terms = len(poly.terms())
                if total.free_symbols and terms <= 6 and poly.total_degree() <= 4:
                    possibilities.append((weight,sign,total,input_terms-terms))
        if not possibilities:
            continue
        product = relative_sign.prove(sp.expand(left*right),symbols,facts,nonzeros)
        if product is None:
            continue
        for weight, sign, total, cancellation in possibilities:
            if sign != product['sign']:
                continue
            for factor, _ in sp.factor_list(total,*symbols)[1]:
                factor = canonical(factor,symbols)
                if factor in known:
                    continue
                quotient, remainder = sp.div(total,factor,*symbols)
                assert remainder == 0
                receipt = {'schema':SCHEMA,'expression':str(factor),'left':str(left),
                    'right':str(right),'weight':str(weight),'multiplier':str(quotient),
                    'strict_product':product}
                replay(factor,symbols,facts,nonzeros,receipt)
                rank = (-cancellation,sp.Poly(factor,*symbols).total_degree(),
                        len(sp.Poly(factor,*symbols).terms()),sp.count_ops(factor),str(factor))
                if factor not in found or rank < found[factor][0]:
                    found[factor] = (rank,receipt)
    return [(value,{'expression':str(value),'proof':receipt,
                    'origin':'strict_same_sign_sum','priority':3})
            for value,(_,receipt) in sorted(found.items(),key=lambda row:row[1][0])[:MAX_DERIVED]]
