"""Bounded, generic counting and integer-polynomial congruence certificates.

No problem identities, source formulas, references, or model calls occur here.
The source interpretation of every conditional result requires a separate audit.
"""
import hashlib
import json
import math
import re

import sympy as sp

from . import matched_expression as syntax

OPERATIONS = ('uniform_partition_count', 'symbolic_modular_order')
POLICY = 'checked-discrete-certificates-v1'
COMMON = '''Return exactly # Decision, # Semantic Bindings, # Discrete Program.
Decision is CALL_TOOL; alternatively return # Decision NO_TOOL and # Reason.
Explain how the chosen parameters, all hypotheses, and the resulting conditional
lemma correspond to the matcher's Immutable Claim and the original theorem.
The submitted proof is untrusted. Invented assumptions are forbidden. A tool
lemma may supply the missing step; the surrounding proof remains your responsibility.
Discrete Program contains one Markdown fence as described below. No code or JSON.
'''
CONTRACTS = {
    'uniform_partition_count': COMMON + '''Use one partition-args fence:
population = positive integer N
block_size = positive integer K dividing N
total = nonnegative
These are plain field = value lines, without an operation wrapper.
The total field may alternatively be an exact nonnegative integer literal;
its sign is checked and the declared value is retained in the compilation.
The population consists of N labeled real weights of nonnegative total.
The tool counts partitions into N/K unordered disjoint K-subsets, checks uniform
incidence, and proves a lower bound on the number of K-subsets of nonnegative sum.
It requires 1 <= K <= N <= 200 and K dividing N; otherwise it rejects the request.
It does not prove that an equality construction exists. A zero-total normalization
is permitted when justified from the original problem. Explain that normalization.
''',
    'symbolic_modular_order': COMMON + '''Use one modular-args fence, in this order:
symbols = comma-separated integer identifiers, or NONE
modulus = polynomial expression
assume = modulus_ge_2
residue = integer R between -8 and 8
unit = unique_label :: polynomial base :: polynomial inverse
check = unique_label :: declared unit label :: polynomial offset
Repeat unit and check lines as needed, with all units before all checks.
At least one unit and check are required. At most 8 symbols and 8 units/checks.
Expressions use integer literals, declared names, (add ...), (mul ...), (sub a b),
(neg a), (pow a nonnegative_integer). No division, floats or variable exponents.
Maximum total polynomial degree 16, 1024 terms, integer coefficients only.
The tool requires exact Z[symbols] certificates M | (base*inverse-1) and
M | (base^R+offset), using inverse^(-R) when R < 0. It returns congruences for
ALL positive exponents n congruent to R modulo phi(M), hence infinitely many n,
conditionally on the integer substitutions and M >= 2. Each check means
M divides base^n + offset. Phi is Euler's totient; its value need not be computed.
You must derive the modulus, inverse, residue, and target correspondence yourself.
Explain why M >= 2 follows, or exactly which source-justified case assumes it.
The tool does not infer eventual constancy of a sequence, growth, or a contradiction.
'''
}


def contract(operation):
    return CONTRACTS[operation]


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def _sections(text):
    if not isinstance(text, str) or len(text) > 30000:
        raise ValueError('expected at most 30000 characters of Markdown')
    text = text.strip()
    if text.startswith('```'):
        return text, ''
    chunks = re.split(r'^# ([^\n]+)\n', text, flags=re.M)
    if chunks[0].strip() or len(chunks) % 2 != 1:
        raise ValueError('invalid section structure')
    keys, values = chunks[1::2], [v.strip() for v in chunks[2::2]]
    if keys == ['Decision', 'Reason'] and values[0] == 'NO_TOOL' and values[1]:
        return None, values[1]
    if keys != ['Decision', 'Semantic Bindings', 'Discrete Program'] or values[0] != 'CALL_TOOL' or not values[1]:
        raise ValueError('expected Decision, Semantic Bindings, Discrete Program')
    return values[2], values[1]


def integer(text, lower, upper):
    if not re.fullmatch(r'-?[0-9]{1,4}', text):
        raise ValueError('expected a bounded integer literal')
    number = int(text)
    if not lower <= number <= upper:
        raise ValueError('integer outside supported range')
    return number


def polynomial(node, symbols):
    if type(node) is int:
        value = sp.Integer(node)
    elif isinstance(node, str):
        if node not in symbols:
            raise ValueError('undeclared integer symbol: '+node)
        value = symbols[node]
    elif isinstance(node, list) and node:
        op, args = node[0], node[1:]
        if op == 'pow' and len(args) == 2 and type(args[1]) is int and 0 <= args[1] <= 16:
            value = polynomial(args[0], symbols)**args[1]
        elif op in ('add', 'mul') and 2 <= len(args) <= 16:
            values = [polynomial(a, symbols) for a in args]
            value = sum(values) if op == 'add' else sp.prod(values)
        elif op == 'sub' and len(args) == 2:
            value = polynomial(args[0], symbols)-polynomial(args[1], symbols)
        elif op == 'neg' and len(args) == 1:
            value = -polynomial(args[0], symbols)
        else:
            raise ValueError('unsupported polynomial operator or arity')
    else:
        raise ValueError('invalid polynomial expression')
    poly = sp.Poly(value, *list(symbols.values()) or [sp.Symbol('_constant')], domain=sp.ZZ)
    if poly.total_degree() > 16 or len(poly.terms()) > 1024 or any(abs(int(c)).bit_length() > 512 for c in poly.coeffs()):
        raise ValueError('polynomial size limit exceeded')
    return poly.as_expr()


def compile_program(text, theorem=''):
    fence, bindings = _sections(text)
    if fence is None:
        return {'call_requested': False, 'reason': bindings}
    if fence.startswith('```partition-args\n'):
        operation = OPERATIONS[0]
        rows = syntax.fields(fence, 'partition-args')
        if [k for k, _ in rows] != ['population', 'block_size', 'total']:
            raise ValueError('expected population, block_size, total')
        total = rows[2][1]
        if total != 'nonnegative':
            if not re.fullmatch(r'-?[0-9]{1,19}', total) or int(total) < 0:
                raise ValueError('total must be nonnegative or an exact nonnegative integer')
        n, k = integer(rows[0][1], 1, 200), integer(rows[1][1], 1, 200)
        if k > n or n % k:
            raise ValueError('block size must divide population')
        program = {'population': n, 'block_size': k, 'total': 'nonnegative'}
        if total != 'nonnegative':
            program.update(declared_total=int(total), total_derivation='exact_integer_sign_check')
        scope = 'N labeled real weights with nonnegative total; all unordered K-subsets'
    elif fence.startswith('```modular-args\n'):
        operation = OPERATIONS[1]
        rows = syntax.fields(fence, 'modular-args')
        if [k for k, _ in rows[:4]] != ['symbols', 'modulus', 'assume', 'residue'] or rows[2][1] != 'modulus_ge_2':
            raise ValueError('expected symbols, modulus, assume = modulus_ge_2, residue')
        names = syntax.names(rows[0][1])
        if len(names) > 8:
            raise ValueError('at most 8 symbols')
        symbols = {name: sp.Symbol(name, integer=True) for name in names}
        modulus = syntax.expression(rows[1][1])
        m = polynomial(modulus, symbols)
        if m == 0 or (not m.free_symbols and m < 2):
            raise ValueError('modulus must admit the required domain M >= 2')
        units, checks, used, phase = [], [], set(names), 'unit'
        for key, body in rows[4:]:
            parts = body.split(' :: ')
            if len(parts) != 3 or not syntax.IDENT.fullmatch(parts[0]) or parts[0] in used:
                raise ValueError('expected unique_label :: value :: value')
            used.add(parts[0])
            if key == 'unit' and phase == 'unit':
                base, inverse = syntax.expression(parts[1]), syntax.expression(parts[2])
                polynomial(base, symbols); polynomial(inverse, symbols)
                units.append({'label': parts[0], 'base': base, 'inverse': inverse})
            elif key == 'check' and parts[1] in {r['label'] for r in units}:
                phase = 'check'
                offset = syntax.expression(parts[2]); polynomial(offset, symbols)
                checks.append({'label': parts[0], 'unit': parts[1], 'offset': offset})
            else:
                raise ValueError('unknown field, unit, or invalid field ordering')
        if not 1 <= len(units) <= 8 or not 1 <= len(checks) <= 8:
            raise ValueError('require 1..8 units and checks')
        program = {'symbols': names, 'modulus': modulus, 'assumption': 'modulus_ge_2',
                   'residue': integer(rows[3][1], -8, 8), 'units': units, 'checks': checks}
        scope = 'integer substitutions satisfying M >= 2; positive n congruent to R modulo phi(M)'
    else:
        raise ValueError('expected partition-args or modular-args fence')
    return {'call_requested': True, 'operation': operation, 'program': program,
            'bindings': bindings, 'report': {'operation': operation, 'program': program,
                                           'scope': scope, 'source_semantics_verified': False}}


def quotient(numerator, modulus, symbols):
    variables = list(symbols.values()) or [sp.Symbol('_constant')]
    p, m = (sp.Poly(e, *variables, domain=sp.ZZ) for e in (numerator, modulus))
    if p.total_degree() > 128 or len(p.terms()) > 8192:
        raise ValueError('expanded certificate limit exceeded')
    q, remainder = sp.div(p, m, domain=sp.QQ)
    if not remainder.is_zero or any(c.q != 1 for c in q.coeffs()):
        raise ValueError('no integer-polynomial divisibility certificate for '+str(p.as_expr()))
    if sp.expand(p.as_expr()-q.as_expr()*m.as_expr()) != 0:
        raise ValueError('polynomial certificate expansion failed')
    return str(q.as_expr())


def compute(text):
    compiled = compile_program(text)
    if not compiled['call_requested']:
        raise ValueError('no computation requested')
    p = compiled['program']
    result = {'policy': POLICY, 'operation': compiled['operation'], 'verified': True,
              'compilation_sha256': digest(compiled), 'source_semantics_verified': False,
              'numerical_sampling_used': False, 'conditional': True}
    if compiled['operation'] == OPERATIONS[0]:
        n, k = p['population'], p['block_size']
        q = n//k
        partitions = math.factorial(n)//(math.factorial(k)**q*math.factorial(q))
        incidence = math.factorial(n-k)//(math.factorial(k)**(q-1)*math.factorial(q-1))
        assert partitions*q == math.comb(n, k)*incidence
        assert partitions == math.comb(n-1, k-1)*incidence
        result.update(partitions=partitions, fixed_block_incidence=incidence,
                      lower_bound=math.comb(n-1, k-1), blocks_per_partition=q)
    else:
        symbols = {name: sp.Symbol(name, integer=True) for name in p['symbols']}
        m = polynomial(p['modulus'], symbols)
        units, checks = {}, []
        for row in p['units']:
            a, b = polynomial(row['base'], symbols), polynomial(row['inverse'], symbols)
            units[row['label']] = {'base': str(a), 'inverse': str(b),
                                   'quotient': quotient(a*b-1, m, symbols)}
        for row in p['checks']:
            unit = next(u for u in p['units'] if u['label'] == row['unit'])
            expression = unit['base'] if p['residue'] >= 0 else unit['inverse']
            offset = polynomial(row['offset'], symbols)
            residual = polynomial(expression, symbols)**abs(p['residue'])+offset
            checks.append({'label': row['label'], 'unit': row['unit'], 'offset': str(offset),
                           'quotient': quotient(residual, m, symbols)})
        result.update(modulus=str(m), residue=p['residue'], units=units, checks=checks,
                      exponent_period='phi(M)', exponent_domain='positive integers', infinitely_many_exponents=True)
    return result


def replay(text, saved):
    actual = compute(text)
    if actual != saved:
        raise ValueError('discrete certificate replay differs')
    return actual


def render(compiled, result):
    if result['compilation_sha256'] != digest(compiled) or not result['verified']:
        raise ValueError('unbound discrete certificate')
    p = compiled['program']
    if compiled['operation'] == OPERATIONS[0]:
        n, k, q = p['population'], p['block_size'], result['blocks_per_partition']
        statement = (f'For any {n} labeled real numbers with nonnegative total sum, '
                     f'at least {result["lower_bound"]} of their unordered {k}-subsets have nonnegative sum.')
        appendix = (f'## Checked counting lemma D\n\n{statement}\n\n'
                    f'Partition the labels into {q} unordered blocks of size {k}. '
                    'Every partition has at least one block of nonnegative sum: otherwise the total would be negative. '
                    f'The number of partitions is T = {n}! / (({k}!)^{q} {q}!) = {result["partitions"]}. '
                    f'A fixed block occurs in U = {n-k}! / (({k}!)^{q-1} {q-1}!) = {result["fixed_block_incidence"]} partitions. '
                    'These formulas follow by ordering all labels, then dividing by the permutations within each block and of the blocks. '
                    'Count incidences between partitions and their nonnegative blocks. If A is the number of nonnegative blocks, '
                    f'then A U >= T, hence A >= T/U = {result["lower_bound"]}. '
                    'Labels distinguish equal weights. Blocks of sum zero qualify.\n')
    else:
        terms = [f"({result['units'][c['unit']]['base']})^n + ({c['offset']})" for c in result['checks']]
        statement = (f"For integer values of {', '.join(p['symbols']) or 'the constants'}, let M = {result['modulus']} >= 2. "
                     f"For every positive integer n congruent to {p['residue']} modulo phi(M), M divides each of "
                     + '; '.join(terms) + '. There are infinitely many such positive exponents.')
        lines = ['## Checked modular-order lemma D', statement,
                 'The following are exact integer-polynomial identities; all displayed quotient polynomials have integer coefficients.']
        for label, u in result['units'].items():
            lines.append(f"For {label}: ({u['base']})({u['inverse']}) - 1 = M ({u['quotient']}). Thus the base is a unit modulo M and the second factor is its inverse.")
        for c in result['checks']:
            u = result['units'][c['unit']]
            base = u['base'] if p['residue'] >= 0 else u['inverse']
            lines.append(f"For {c['label']}: ({base})^{abs(p['residue'])} + ({c['offset']}) = M ({c['quotient']}).")
        lines += ['Multiplication by a unit permutes the phi(M) invertible residue classes modulo M. Multiplying all classes before and after this permutation and canceling their invertible product gives a^phi(M) = 1 modulo M. This proves the exponent-period rule used here.',
                  'Consequently a^n equals a^R modulo M for n congruent to R modulo phi(M), interpreting negative powers by the verified inverse. The checked identities prove every displayed divisibility claim.',
                  'Since phi(M) is a positive integer, n = R + t phi(M) is positive for all sufficiently large positive integers t and supplies infinitely many exponents. All statements remain conditional on the stated integer domain and M >= 2.']
        appendix = '\n\n'.join(lines)+'\n'
    return statement, appendix
