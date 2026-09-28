"""Prove D != 0 from an exact identity M*D = a*f + b*g > 0.

Only admitted source sign facts supply positivity. Candidate multipliers come
from existing source expressions; their own sign is irrelevant. This bounded
search neither uses equations as domain facts nor admits pending premises.
"""
import sympy as sp

from . import sum_of_squares as codec

POLICY = 'replayed-positive-multiple-nonzero-v1'
MAX_FACTS = 24
MAX_MULTIPLIERS = 16
MAX_TERMS = 128
MAX_DEGREE = 8
WEIGHTS = (sp.Integer(1), sp.Rational(1, 2), sp.Integer(2))


def polynomial(value, symbols):
    result = codec.polynomial(value, symbols)
    if len(result.terms()) > MAX_TERMS or result.total_degree() > MAX_DEGREE:
        raise ValueError('positive multiple polynomial limit')
    return result


def key(poly):
    leading = poly.LC()
    return tuple((powers, coefficient / leading) for powers, coefficient in poly.terms())


def replay(receipt, target, symbols, facts):
    """Check the identity and strict source positivity without repeating search."""
    if (set(receipt) != {'schema', 'symbols', 'target', 'multiplier', 'sources'}
            or receipt['schema'] != POLICY
            or receipt['symbols'] != [str(s) for s in symbols]):
        raise ValueError('positive multiple binding mismatch')
    expected = polynomial(target, symbols)
    if expected.is_zero or polynomial(codec.decode(receipt['target'], symbols), symbols) != expected:
        raise ValueError('positive multiple target mismatch')
    multiplier = polynomial(codec.decode(receipt['multiplier'], symbols), symbols)
    if multiplier.is_zero:
        raise ValueError('zero positive multiple')
    sources = receipt['sources']
    if not isinstance(sources, list) or not 1 <= len(sources) <= 2:
        raise ValueError('positive multiple source count')
    total = sp.Poly(0, *symbols, domain=sp.QQ)
    strict = False
    seen = set()
    for row in sources:
        if set(row) != {'index', 'label', 'expression', 'weight', 'strict'}:
            raise ValueError('invalid positive multiple source')
        index = row['index']
        if type(index) is not int or not 0 <= index < len(facts) or index in seen:
            raise ValueError('positive multiple source index')
        seen.add(index)
        value, is_strict, label = facts[index]
        if type(is_strict) is not bool or row['strict'] is not is_strict or row['label'] != label:
            raise ValueError('positive multiple source binding changed')
        bound = polynomial(value, symbols)
        if polynomial(codec.decode(row['expression'], symbols), symbols) != bound:
            raise ValueError('positive multiple source expression changed')
        weight = codec.rational(row['weight'])
        if weight <= 0:
            raise ValueError('positive multiple weight must be positive')
        total += bound.mul_ground(weight)
        strict = strict or is_strict
    if not strict or total.is_zero:
        raise ValueError('positive multiple requires strict positivity')
    if expected * multiplier != total:
        raise ValueError('positive multiple identity failed')
    return True


class Prover:
    def __init__(self, symbols):
        self.symbols = symbols
        self.signature = None
        self.cache = {}

    def _prepare(self, facts, nonzeros):
        # Admission changes must invalidate both successes and failures.
        signature = (tuple(facts), tuple(nonzeros))
        if signature == self.signature:
            return
        self.signature = signature
        self.cache = {}
        self.rows, self.by_key, self.multipliers = [], {}, []
        for index, (value, strict, label) in enumerate(facts[:MAX_FACTS]):
            try:
                poly = polynomial(value, self.symbols)
            except (ValueError, sp.PolynomialError, sp.CoercionFailed):
                continue
            if poly.is_zero:
                continue
            row = (index, poly, strict, label)
            self.rows.append(row)
            bucket = self.by_key.setdefault(key(poly), [])
            bucket.append(row)
        seen = set()
        candidates = list(nonzeros[:MAX_MULTIPLIERS])
        candidates += [(value, label) for value, strict, label in facts[:MAX_FACTS] if strict]
        for value, _ in candidates:
            try:
                poly = polynomial(value, self.symbols)
            except (ValueError, sp.PolynomialError, sp.CoercionFailed):
                continue
            if poly.is_zero or poly.total_degree() == 0:
                continue
            marker = key(poly)
            if marker in seen:
                continue
            seen.add(marker)
            self.multipliers.append(poly.monic())
            if len(self.multipliers) == MAX_MULTIPLIERS:
                break

    def _receipt(self, target, multiplier, entries, facts):
        receipt = {'schema': POLICY, 'symbols': [str(s) for s in self.symbols],
                   'target': codec.encode(target.as_expr(), self.symbols),
                   'multiplier': codec.encode(multiplier.as_expr(), self.symbols),
                   'sources': [{'index': row[0], 'label': row[3],
                                'expression': codec.encode(row[1].as_expr(), self.symbols),
                                'weight': str(weight), 'strict': row[2]}
                               for row, weight in entries]}
        replay(receipt, target.as_expr(), self.symbols, facts)
        return receipt

    def prove(self, value, facts, nonzeros):
        self._prepare(facts, nonzeros)
        if value in self.cache:
            return self.cache[value]
        try:
            target = polynomial(value, self.symbols)
        except (ValueError, sp.PolynomialError, sp.CoercionFailed):
            return None
        if target.is_zero:
            return None
        result = None
        for multiplier in self.multipliers:
            product = target * multiplier
            if len(product.terms()) > MAX_TERMS or product.total_degree() > MAX_DEGREE:
                continue
            for sign in (1, -1):
                positive = product.mul_ground(sign)
                for first in self.rows:
                    for weight in WEIGHTS:
                        remainder = positive - first[1].mul_ground(weight)
                        if remainder.is_zero:
                            if first[2]:
                                result = self._receipt(target, multiplier.mul_ground(sign), [(first, weight)], facts)
                        else:
                            for second in self.by_key.get(key(remainder), []):
                                ratio = remainder.LC() / second[1].LC()
                                if first[0] != second[0] and ratio > 0 and (first[2] or second[2]):
                                    result = self._receipt(target, multiplier.mul_ground(sign),
                                                           [(first, weight), (second, ratio)], facts)
                                    break
                        if result:
                            break
                    if result:
                        break
                if result:
                    break
            if result:
                break
        if len(self.cache) < 256:
            self.cache[value] = result
        return result
