"""Bounded sign parity from strict polynomial facts, with exact identity replay."""
from __future__ import annotations

import sympy as sp

SCHEMA = 'replayed-relative-polynomial-sign-v1'
MAX_FACTS = 128
MAX_FACTORS = 256


def factors(expression, symbols):
    expression = sp.Poly(sp.expand(expression), *symbols, domain=sp.QQ).as_expr()
    coefficient, raw = sp.factor_list(expression, *symbols)
    result = {}
    for factor, exponent in raw:
        exponent = int(exponent)
        poly = sp.Poly(factor, *symbols, domain=sp.QQ)
        coefficient *= poly.LC()**exponent
        result[poly.monic().as_expr()] = exponent
    return coefficient, result


def nonzero_witness(factor, known, symbols):
    for index, (expression, label) in enumerate(known):
        if expression == 0:
            continue
        quotient, remainder = sp.div(expression, factor, *symbols)
        if remainder == 0:
            return {'factor':str(factor), 'source_index':index, 'source':label,
                    'source_expression':str(expression), 'multiplier':str(quotient)}
    return None


def ratio_data(expression, sources, symbols):
    # Replay each small polynomial identity, then combine exponent multisets.
    # Expanding a product of many source facts can be exponentially wasteful.
    def checked(value):
        scalar, row = factors(value, symbols)
        if sp.expand(value-scalar*sp.prod(f**e for f,e in row.items())) != 0:
            raise ValueError('relative sign factor identity failed')
        return scalar, row
    nc, nf = checked(expression)
    dc, df = sp.Integer(1), {}
    for source in sources:
        scalar, row = checked(source)
        if scalar == 0:
            raise ValueError('zero strict sign source')
        dc *= scalar
        for factor, exponent in row.items():
            df[factor] = df.get(factor,0)+exponent
    exponents = {f:nf.get(f,0)-df.get(f,0) for f in set(nf)|set(df)}
    exponents = {f:e for f,e in exponents.items() if e}
    coefficient = nc/dc
    return coefficient, exponents


def replay(expression, symbols, facts, nonzeros, receipt):
    """Check a positive-source product times a nonzero square, without parity search."""
    if receipt.get('schema') != SCHEMA or receipt.get('expression') != str(expression):
        raise ValueError('relative sign receipt target mismatch')
    selected = receipt['positive_source_indices']
    if len(selected) != len(set(selected)) or any(type(i) is not int or not 0<=i<len(facts) or not facts[i][1] for i in selected):
        raise ValueError('relative sign requires strict positive source facts')
    if receipt['strict_sources'] != [{'index':i,'source':facts[i][2],'expression':str(facts[i][0])} for i in selected]:
        raise ValueError('relative sign source binding mismatch')
    product = [facts[i][0] for i in selected]
    coefficient, exponents = ratio_data(expression, product, symbols)
    if coefficient == 0 or any(e%2 for e in exponents.values()):
        raise ValueError('relative sign ratio is not a nonzero signed square')
    expected_factors = [{'factor':str(f), 'exponent':e} for f,e in sorted(exponents.items(),key=lambda row:str(row[0]))]
    if receipt['ratio_coefficient'] != str(coefficient) or receipt['ratio_factors'] != expected_factors:
        raise ValueError('relative sign factorization mismatch')
    sign = 1 if coefficient > 0 else -1
    if type(receipt['sign']) is not int or receipt['sign'] != sign:
        raise ValueError('relative sign mismatch')
    _, query_factors = factors(expression, symbols)
    needed = {str(f):f for f in set(exponents)|set(query_factors)}
    known = list(nonzeros)+[(f,label) for f,strict,label in facts if strict]
    witnesses = receipt['nonzero_proofs']
    if len(witnesses)!=len(needed) or {w['factor'] for w in witnesses}!=set(needed):
        raise ValueError('relative sign missing nonzero witness')
    for witness in witnesses:
        index = witness['source_index']
        if type(index) is not int or not 0<=index<len(known):
            raise ValueError('relative sign unknown nonzero source')
        source = known[index][0]
        factor = needed[witness['factor']]
        quotient, remainder = sp.div(source, factor, *symbols)
        if (source == 0 or remainder != 0 or witness['multiplier'] != str(quotient)
                or witness['source'] != known[index][1] or witness['source_expression'] != str(source)):
            raise ValueError('relative sign invalid nonzero witness')
        if sp.expand(source-quotient*factor) != 0:
            raise ValueError('relative sign nonzero identity failed')
    return sign


def prove(expression, symbols, facts, nonzeros):
    """Return a replayed strict sign or None; never assume an unknown factor sign."""
    expression = sp.expand(expression)
    if expression == 0 or len(facts)>MAX_FACTS:
        return None
    try:
        coefficient, query = factors(expression, symbols)
        source_rows = [(index,*factors(value,symbols))
                       for index,(value,strict,_) in enumerate(facts) if strict]
    except sp.PolynomialError:
        return None
    all_factors = set(query)
    for _,_,row in source_rows:
        all_factors.update(row)
    if len(all_factors)>MAX_FACTORS:
        return None
    names = {f:i for i,f in enumerate(sorted(all_factors,key=str))}
    def bits(row):
        return sum(1<<names[f] for f,e in row.items() if e%2)
    basis = {}
    for index,scalar,row in source_rows:
        if scalar == 0:
            raise ValueError('zero strict sign source')
        mask, parity, used = bits(row), (1 if scalar<0 else 0), 1<<index
        while mask:
            pivot = mask.bit_length()-1
            if pivot not in basis:
                basis[pivot] = (mask,parity,used)
                break
            other,other_parity,other_used = basis[pivot]
            mask ^= other; parity ^= other_parity; used ^= other_used
        if not mask and parity:
            raise ValueError('inconsistent strict sign sources')
    mask, parity, used = bits(query), (1 if coefficient<0 else 0), 0
    while mask:
        pivot = mask.bit_length()-1
        if pivot not in basis:
            return None
        other,other_parity,other_used = basis[pivot]
        mask ^= other; parity ^= other_parity; used ^= other_used
    selected = [i for i in range(len(facts)) if used & (1<<i)]
    product = [facts[i][0] for i in selected]
    scalar, exponents = ratio_data(expression,product,symbols)
    if any(e%2 for e in exponents.values()):
        raise ValueError('relative sign parity identity failed')
    known = list(nonzeros)+[(f,label) for f,strict,label in facts if strict]
    witnesses = [nonzero_witness(f,known,symbols) for f in sorted(set(query)|set(exponents),key=str)]
    if any(w is None for w in witnesses):
        return None
    receipt = {'schema':SCHEMA, 'expression':str(expression), 'sign':-1 if parity else 1,
               'positive_source_indices':selected, 'ratio_coefficient':str(scalar),
               'ratio_factors':[{'factor':str(f),'exponent':e} for f,e in sorted(exponents.items(),key=lambda row:str(row[0]))],
               'nonzero_proofs':witnesses,
               'strict_sources':[{'index':i,'source':facts[i][2],'expression':str(facts[i][0])} for i in selected]}
    replay(expression,symbols,facts,nonzeros,receipt)
    return receipt
