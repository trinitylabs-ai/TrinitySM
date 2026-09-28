"""Bounded rational square certificates, independently checked by expansion.

This module proves nonnegativity only. Strictness requires a separate source-
bound proof that at least one square's form is nonzero.
"""
import re
import sympy as sp

SCHEMA = 'exact-rational-sum-of-squares-v1'
MAX_SYMBOLS = 16
MAX_TERMS = 256
MAX_DEGREE = 16
MAX_SQUARES = 32


def polynomial(value, symbols):
    if not symbols or len(symbols) > MAX_SYMBOLS or any(s.is_real is not True for s in symbols):
        raise ValueError('square certificate requires bounded real symbols')
    p = sp.Poly(value, *symbols, domain=sp.QQ)
    if len(p.terms()) > MAX_TERMS or p.total_degree() > MAX_DEGREE:
        raise ValueError('square certificate polynomial limit')
    return p


def encode(value, symbols):
    return [{'powers': list(powers), 'coefficient': str(coefficient)}
            for powers, coefficient in polynomial(value, symbols).terms()]


def rational(value):
    if not isinstance(value, str) or len(value) > 2048 or not re.fullmatch(r'-?\d+(?:/[1-9]\d*)?', value):
        raise ValueError('invalid rational certificate coefficient')
    return sp.Rational(value)


def decode(terms, symbols):
    if not isinstance(terms, list) or not 1 <= len(terms) <= MAX_TERMS:
        raise ValueError('invalid certificate term list')
    seen = set()
    result = sp.Integer(0)
    for term in terms:
        if set(term) != {'powers', 'coefficient'}:
            raise ValueError('invalid certificate term')
        powers = term['powers']
        if (not isinstance(powers, list) or len(powers) != len(symbols)
                or any(type(n) is not int or n < 0 for n in powers) or sum(powers) > MAX_DEGREE
                or tuple(powers) in seen):
            raise ValueError('invalid certificate powers')
        seen.add(tuple(powers))
        result += rational(term['coefficient']) * sp.prod(s**n for s, n in zip(symbols, powers))
    return polynomial(result, symbols).as_expr()


def certificate(target, squares, symbols):
    result = {'schema': SCHEMA, 'symbols': [str(s) for s in symbols],
              'target': encode(target, symbols),
              'squares': [{'weight': str(weight), 'form': encode(form, symbols)} for weight, form in squares]}
    replay(result, target, symbols)
    return result


def replay(receipt, target, symbols):
    """Check a supplied identity without rerunning its discovery algorithm."""
    if (set(receipt) != {'schema', 'symbols', 'target', 'squares'} or receipt['schema'] != SCHEMA
            or receipt['symbols'] != [str(s) for s in symbols]):
        raise ValueError('square certificate binding mismatch')
    expected = polynomial(target, symbols)
    if polynomial(decode(receipt['target'], symbols), symbols) != expected:
        raise ValueError('square certificate target mismatch')
    entries = receipt['squares']
    if not isinstance(entries, list) or not 1 <= len(entries) <= MAX_SQUARES:
        raise ValueError('square certificate size limit')
    total, forms = sp.Integer(0), []
    for item in entries:
        if set(item) != {'weight', 'form'}:
            raise ValueError('invalid square entry')
        weight = rational(item['weight'])
        if weight <= 0:
            raise ValueError('square weight must be positive')
        form = decode(item['form'], symbols)
        total += weight * form**2
        forms.append(form)
    if polynomial(total, symbols) != expected:
        raise ValueError('square certificate identity failed')
    return forms


def quadratic(value, symbols):
    """Exact square completion for globally nonnegative rational quadratics."""
    try:
        initial = polynomial(value, symbols)
        if initial.total_degree() > 2 or initial.is_zero:
            return None
        remainder, squares = initial.as_expr(), []
        for symbol in symbols:
            p = sp.Poly(remainder, symbol)
            pivot = p.coeff_monomial(symbol**2)
            if pivot == 0:
                continue
            if not pivot.is_Rational or pivot < 0:
                return None
            form = symbol + p.coeff_monomial(symbol)/(2*pivot)
            squares.append((pivot, form))
            remainder = polynomial(remainder-pivot*form**2, symbols).as_expr()
        if remainder.free_symbols or remainder < 0:
            return None
        if remainder > 0:
            squares.append((remainder, sp.Integer(1)))
        return certificate(initial.as_expr(), squares, symbols) if squares else None
    except (ValueError, sp.PolynomialError, sp.polys.polyerrors.CoercionFailed):
        return None


def rational_norm(components, symbols):
    """Preserve a polynomial square numerator of a rational vector norm.

    No component denominator is assumed nonzero here. This emits a polynomial
    identity only; the compiler retains every original construction obligation.
    """
    try:
        if not 1 <= len(components) <= MAX_SQUARES:
            return None
        parts = [sp.fraction(sp.cancel(v)) for v in components]
        denominator = sp.Poly(1, *symbols, domain=sp.QQ)
        for numerator, divisor in parts:
            polynomial(numerator, symbols)
            denominator = denominator.lcm(polynomial(divisor, symbols))
            polynomial(denominator.as_expr(), symbols)
        forms = []
        for numerator, divisor in parts:
            factor = denominator.exquo(polynomial(divisor, symbols))
            forms.append(polynomial(numerator*factor.as_expr(), symbols).as_expr())
        target = polynomial(sum(v**2 for v in forms), symbols).as_expr()
        if target == 0:
            return None
        return certificate(target, [(sp.Integer(1), v) for v in forms if v != 0], symbols)
    except (ValueError, sp.PolynomialError, sp.polys.polyerrors.CoercionFailed):
        return None
