"""Exact, bounded univariate root isolation and derivative sign classification.

The expression grammar is closed. Algebraic coefficients and a single positive
variable-dependent square root are supported. Original division domains survive
cancellation. No problem identifiers, source formulas, or model calls occur here.
"""
from functools import lru_cache
import hashlib
import json
import math
import re

import sympy as sp

from . import matched_expression as syntax, root_normalization

OPERATION = 'real_root_classification'
POLICY = 'exact-univariate-positive-radical-sign-cells-v1'
MAX_DEGREE = 24
MAX_FIELD_DEGREE = 8
MAX_OPERATIONS = 2000
CONTRACT = '''Return exactly # Decision, # Semantic Bindings, # Root Program.
Decision is CALL_TOOL, or use # Decision NO_TOOL and # Reason.
Bind the exact function/expression, variable, interval and domain to the matcher's
Immutable Claim and the original source. Never assume that an asserted root set
or critical-point count is correct. The tool COMPUTES the complete set.
Root Program contains exactly one root-args fence, with fields in this order:
```root-args
variable = one real identifier
define = unique_name :: expression
interval = (open lower upper)
mode = stationary_points
function = expression
```
Use plain field = value lines, with no enclosing operation-name wrapper.
Definitions are optional. Endpoints must be finite exact real algebraic constants.
Interval kinds: open, closed, left_open, right_open (the named side is open).
For stationary_points, supply the original function; the tool differentiates it
and classifies all stationary points by derivative signs. Alternatively use
mode = roots and expression = expression to classify all zeros and their left/
right signs. In roots mode signs are signs of the supplied expression, not of an
unspecified underlying function. Do not encode only one proposed solution.
Expressions: integer literals, declared names, (rational int int), (add ...),
(mul ...), (sub a b), (div a b), (neg a), (pow a integer), (sqrt a).
Constant algebraic square roots are supported. At most ONE distinct square root
depending on the variable is supported, with a rational-function radicand.
The variable radicand must be strictly positive throughout the requested interval.
All original denominators must be nonzero throughout that interval. Excluded
open endpoints may be singular. A domain with an interior singularity is rejected;
split it into separately justified intervals rather than silently discarding it.
No free parameters, trigonometric/transcendental functions, floats, Python or JSON.
Polynomial degree is bounded at 24; coefficient field degree at 8, with combined
degree at most 64. Resource exhaustion or unresolved exact signs is inconclusive.
All results concern the supplied expression and interval. Source correspondence
and the surrounding proof require independent audits; no theorem is certified by
the root computation alone.'''


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def _sqrt_bounds(a, b, bits):
    if a < 0:
        raise ValueError('interval square root has an unresolved negative argument')
    scale = 2**bits
    lo = math.isqrt(int(sp.numer(a))*scale*scale//int(sp.denom(a)))
    hi = math.isqrt(int(sp.numer(b))*scale*scale//int(sp.denom(b)))
    if sp.Rational(hi, scale)**2 != b:
        hi += 1
    return sp.Rational(lo, scale), sp.Rational(hi, scale)


def _mul(a, b):
    products = [x*y for x in a for y in b]
    return min(products), max(products)


def enclosure(value, variable=None, bounds=None, bits=64):
    if value == variable:
        return bounds
    if value.is_Rational:
        return value, value
    if isinstance(value, sp.CRootOf):
        interval = value._get_interval()
        for extra in (8, 32, 64, 128, 256):
            interval = interval.refine_size(sp.Rational(1, 2**(bits+extra)))
            lo, hi = sp.Rational(interval.a), sp.Rational(interval.b)
            a, b = sp.floor(lo*2**bits), sp.floor(hi*2**bits)
            if a == b:
                return a/sp.Integer(2**bits), (a+1)/sp.Integer(2**bits)
        raise ValueError('could not bound algebraic root on a canonical dyadic grid')
    if value.is_Add:
        rows = [enclosure(v, variable, bounds, bits) for v in value.args]
        return sum(a for a, _ in rows), sum(b for _, b in rows)
    if value.is_Mul:
        out = (sp.Integer(1), sp.Integer(1))
        for v in value.args:
            out = _mul(out, enclosure(v, variable, bounds, bits))
        return out
    if value.is_Pow:
        a, b = enclosure(value.base, variable, bounds, bits)
        exponent = value.exp
        if exponent == sp.Rational(1, 2):
            return _sqrt_bounds(a, b, bits)
        if exponent.is_Integer and abs(exponent) <= 128:
            exponent = int(exponent)
            if exponent < 0:
                if a <= 0 <= b:
                    raise ValueError('interval denominator encloses zero')
                a, b, exponent = 1/b, 1/a, -exponent
            if exponent == 0:
                return sp.Integer(1), sp.Integer(1)
            vals = [a**exponent, b**exponent]
            if exponent % 2 == 0 and a <= 0 <= b:
                vals.append(sp.Integer(0))
            return min(vals), max(vals)
    raise ValueError('unsupported exact interval expression: '+str(value))


def exact_sign(value):
    if value == 0:
        return 0
    for bits in (32, 64, 128, 256, 512, 1024):
        try:
            lo, hi = enclosure(value, bits=bits)
        except ValueError:
            continue
        if lo > 0:
            return 1
        if hi < 0:
            return -1
        if lo == hi == 0:
            return 0
    # Equality is never inferred from a small numerical residual.
    if sp.polys.numberfields.to_number_field(value).as_expr() == 0:
        return 0
    raise ValueError('exact algebraic sign could not be resolved within the bound')


def compare(a, b):
    return 0 if a == b else exact_sign(a-b)


class Program:
    def __init__(self, text):
        self.bindings = ''
        self.call_requested = True
        if text.strip().startswith('```'):
            fence = text.strip()
        else:
            parts = re.split(r'^# (Decision|Semantic Bindings|Root Program|Reason)\s*$', text.strip(), flags=re.M)
            if parts[0].strip() or len(parts) not in (5, 7):
                raise ValueError('expected Decision, Semantic Bindings, Root Program sections')
            headings, bodies = parts[1::2], parts[2::2]
            values = dict(zip(headings, (v.strip() for v in bodies)))
            if headings == ['Decision', 'Reason'] and values['Decision'] == 'NO_TOOL' and values['Reason']:
                self.call_requested = False
                self.reason = values['Reason']
                return
            if headings != ['Decision', 'Semantic Bindings', 'Root Program'] or values['Decision'] != 'CALL_TOOL' or not values['Semantic Bindings']:
                raise ValueError('invalid root formalization headings or decision')
            fence = values['Root Program']
            self.bindings = values['Semantic Bindings']
        fence, self.normalization = root_normalization.normalize(fence)
        rows = syntax.fields(fence, 'root-args')
        if not rows or rows[0][0] != 'variable' or not syntax.IDENT.fullmatch(rows[0][1]):
            raise ValueError('one declared variable must be the first field')
        self.x = sp.Symbol(rows[0][1], real=True)
        self.y = sp.Dummy('positive_radical', real=True)
        self.env = {str(self.x): self.x}
        self.radicand = None
        self.domains = []
        index = 1
        while index < len(rows) and rows[index][0] == 'define':
            name, node = syntax.labeled(rows[index][1])
            if name in self.env:
                raise ValueError('duplicate definition')
            self.env[name] = self.decode(node)
            index += 1
        if [k for k, _ in rows[index:]] not in (['interval', 'mode', 'function'], ['interval', 'mode', 'expression']):
            raise ValueError('expected interval, mode and function/expression fields')
        interval = syntax.expression(rows[index][1])
        if not isinstance(interval, list) or len(interval) != 3 or interval[0] not in {'open', 'closed', 'left_open', 'right_open'}:
            raise ValueError('invalid interval constructor')
        self.left, self.right = [self.decode(v) for v in interval[1:]]
        if self.left.free_symbols or self.right.free_symbols or compare(self.left, self.right) >= 0:
            raise ValueError('finite exact constant endpoints must be strictly ordered')
        self.left_open = interval[0] in {'open', 'left_open'}
        self.right_open = interval[0] in {'open', 'right_open'}
        self.mode = rows[index+1][1]
        expected = {'roots': 'expression', 'stationary_points': 'function'}
        if self.mode not in expected or rows[index+2][0] != expected[self.mode]:
            raise ValueError('mode roots needs expression; stationary_points needs function')
        self.function = self.decode(syntax.expression(rows[index+2][1]))
        self.target = self.function
        if self.mode == 'stationary_points':
            self.target = sp.diff(self.function, self.x)
            if self.y in self.function.free_symbols:
                self.target += sp.diff(self.function, self.y)*sp.diff(self.radicand, self.x)/(2*self.y)
                self.domains.append(self.y)
        self.target = self.reduce(self.target)
        self.domains.append(sp.fraction(self.target)[1])
        self.polynomial(self.target)  # Validate degree/field budgets before audit.

    def decode(self, node):
        if isinstance(node, int):
            return sp.Integer(node)
        if isinstance(node, str):
            if node not in self.env:
                raise ValueError('undeclared identifier: '+node)
            return self.env[node]
        op, args = node[0], node[1:]
        if op == 'rational' and len(args) == 2 and all(type(v) is int for v in args):
            if args[1] == 0:
                raise ValueError('zero rational denominator')
            return sp.Rational(*args)
        if op == 'pow' and len(args) == 2 and type(args[1]) is int and abs(args[1]) <= 24:
            base = self.decode(args[0])
            if args[1] < 0:
                self.domains.append(base)
            result = base**args[1]
        else:
            values = [self.decode(a) for a in args]
            if op == 'add' and len(values) >= 2:
                result = sum(values)
            elif op == 'mul' and len(values) >= 2:
                result = sp.prod(values)
            elif op == 'sub' and len(values) == 2:
                result = values[0]-values[1]
            elif op == 'neg' and len(values) == 1:
                result = -values[0]
            elif op == 'div' and len(values) == 2:
                self.domains.append(values[1])
                if values[1] == 0:
                    raise ValueError('zero division denominator')
                result = values[0]/values[1]
            elif op == 'sqrt' and len(values) == 1:
                value = sp.cancel(values[0])
                if not value.free_symbols:
                    if exact_sign(value) < 0:
                        raise ValueError('nonreal constant square root')
                    result = sp.sqrt(value)
                else:
                    if self.y in value.free_symbols or not value.free_symbols <= {self.x}:
                        raise ValueError('nested variable radicals are unsupported')
                    if self.radicand is not None and sp.cancel(value-self.radicand) != 0:
                        raise ValueError('only one distinct variable radicand is supported')
                    self.radicand = value
                    result = self.y
            else:
                raise ValueError('unsupported root expression operation or arity: '+op)
        if sp.count_ops(result) > MAX_OPERATIONS:
            raise ValueError('root expression size limit')
        return self.reduce(result)

    def reduce(self, expr):
        return sp.cancel(expr)

    def coefficients(self, expr):
        n, _ = sp.fraction(sp.cancel(expr))
        if self.y not in n.free_symbols:
            return n, sp.Integer(0)
        n = sp.rem(n, self.y**2-self.radicand, self.y)
        return sp.cancel(n.coeff(self.y, 0)), sp.cancel(n.coeff(self.y, 1))

    def polynomial(self, expr):
        a, b = self.coefficients(expr)
        value = a if b == 0 else a*a-b*b*self.radicand
        value = sp.fraction(sp.cancel(value))[0]
        poly = sp.Poly(value, self.x, extension=True)
        field_degree = int(poly.domain.ext.minpoly.degree()) if poly.domain.is_AlgebraicField else 1
        if not (poly.domain.is_QQ or poly.domain.is_ZZ or poly.domain.is_AlgebraicField):
            raise ValueError('nonalgebraic coefficient field')
        degree = max(0, poly.degree()) if not poly.is_zero else 0
        if degree > MAX_DEGREE or field_degree > MAX_FIELD_DEGREE or degree*field_degree > 64:
            raise ValueError('root polynomial degree or algebraic-field budget exceeded')
        if not poly.is_zero and max(len(str(c)) for c in poly.all_coeffs()) > 10000:
            raise ValueError('root coefficient size limit')
        return poly

    def actual(self, expr):
        return expr if self.radicand is None else expr.xreplace({self.y: sp.sqrt(self.radicand)})

    def report(self):
        if not self.call_requested:
            return {'call_requested': False, 'reason': self.reason}
        p = self.polynomial(self.target)
        return {'call_requested': True, 'bindings': self.bindings, 'report': {
            'schema': POLICY, 'variable': str(self.x), 'mode': self.mode,
            'function_or_expression': str(self.actual(self.function)),
            'classified_expression': str(self.actual(self.target)),
            'interval': {'left': str(self.left), 'right': str(self.right), 'left_open': self.left_open, 'right_open': self.right_open},
            'variable_radicand': str(self.radicand) if self.radicand is not None else None,
            'original_nonzero_domains': [str(self.actual(v)) for v in self.domains],
            'elimination_polynomial': str(p.as_expr()), 'eliminant_is_candidate_superset': True,
            'source_semantics_verified': False, 'semantics': 'MODEL_AUDIT_REQUIRED',
            'strict_positive_variable_radicand_required': True,
            **({'normalization': self.normalization} if self.normalization['applied'] else {})}}

    def inside(self, root):
        a, b = compare(root, self.left), compare(root, self.right)
        return (a > 0 or a == 0 and not self.left_open) and (b < 0 or b == 0 and not self.right_open)

    @lru_cache(maxsize=256)
    def roots_of_poly(self, expression):
        p = sp.Poly(expression, self.x, extension=True)
        if p.is_zero:
            raise ValueError('identically zero polynomial has a continuum of roots')
        return tuple(r for r, _ in p.real_roots(multiple=False, radicals=False))

    def rational_sign_at(self, expression, root):
        numerator, denominator = sp.fraction(sp.cancel(expression))
        if numerator == 0:
            return 0
        if self.x in numerator.free_symbols and any(compare(root, q) == 0 for q in self.roots_of_poly(numerator)):
            return 0
        return exact_sign(expression.subs(self.x, root))

    def roots(self, expression, record=False):
        poly = self.polynomial(expression)
        if poly.is_zero:
            if sp.cancel(expression) == 0:
                raise ValueError('expression is identically zero; isolated-root classification is inapplicable')
            raise ValueError('degenerate radical eliminant; a separate branch proof is required')
        a, b = self.coefficients(expression)
        accepted, rejected, candidates = [], [], []
        for root in self.roots_of_poly(poly.as_expr()):
            if not self.inside(root):
                continue
            candidates.append(root)
            sa = self.rational_sign_at(a, root) if b != 0 else 0
            sb = self.rational_sign_at(b, root) if b != 0 else 0
            # On R>0, A+B*sqrt(R)=0 iff its norm vanishes and signs oppose
            # (or both coefficients vanish). Squaring alone never admits a root.
            valid = b == 0 or (sa == sb == 0) or sa*sb == -1
            row = {'root': encode_root(root), 'coefficient_signs': [sa, sb], 'accepted_original_branch': valid}
            (accepted if valid else rejected).append((root, row))
        return [r for r, _ in accepted], {'polynomial': str(poly.as_expr()), 'polynomial_coefficients': [str(c) for c in poly.all_coeffs()],
            'coefficient_domain': str(poly.domain), 'candidates_in_interval': len(candidates),
            'branch_checks': [row for _, row in accepted+rejected], 'complete_real_root_isolation': True}

    def rational_between(self, left, right):
        for bits in (8, 16, 32, 64, 128, 256):
            _, a = enclosure(left, bits=bits)
            b, _ = enclosure(right, bits=bits)
            if a < b:
                return (a+b)/2
        raise ValueError('could not separate adjacent roots exactly within the bound')

    def solve(self):
        if not self.call_requested:
            raise ValueError('NO_TOOL has no root computation')
        mid = self.rational_between(self.left, self.right)
        domain_proofs = []
        if self.radicand is not None:
            numerator, denominator = sp.fraction(self.radicand)
            for value in (numerator, denominator):
                p = self.polynomial(value)
                if p.is_zero or any(self.inside(r) for r in self.roots_of_poly(p.as_expr())):
                    raise ValueError('variable radicand is not strictly positive and defined throughout the interval')
            sign = exact_sign(self.radicand.subs(self.x, mid))
            if sign != 1:
                raise ValueError('variable radicand is not positive on the interval')
            domain_proofs.append({'condition': str(self.radicand)+' > 0', 'sample': str(mid), 'sign': sign, 'no_numerator_or_denominator_zeros_in_interval': True})
        for value in dict.fromkeys(self.domains):
            roots, proof = self.roots(value)
            if roots:
                raise ValueError('original denominator vanishes in requested interval: '+str(self.actual(value)))
            sign = exact_sign(self.actual(value).subs(self.x, mid))
            if sign == 0:
                raise ValueError('zero original denominator')
            domain_proofs.append({'condition': str(self.actual(value))+' != 0', 'sample': str(mid), 'sign': sign, 'isolation': proof})
        roots, isolation = self.roots(self.target)
        interior = [r for r in roots if compare(r, self.left) > 0 and compare(r, self.right) < 0]
        boundaries = [self.left, *interior, self.right]
        cells = []
        for left, right in zip(boundaries, boundaries[1:]):
            sample = self.rational_between(left, right)
            sign = exact_sign(self.actual(self.target).subs(self.x, sample))
            if sign == 0:
                raise ValueError('zero sign-cell sample contradicts complete root isolation')
            cells.append({'left': encode_root(left), 'right': encode_root(right), 'sample': str(sample), 'sign': sign})
        classified = []
        for root in roots:
            at_left, at_right = compare(root, self.left) == 0, compare(root, self.right) == 0
            index = next((i for i, r in enumerate(interior) if compare(r, root) == 0), None)
            left_sign = None if at_left else cells[-1]['sign'] if at_right else cells[index]['sign']
            right_sign = None if at_right else cells[0]['sign'] if at_left else cells[index+1]['sign']
            classification = 'boundary_root' if at_left or at_right else 'negative_to_positive' if (left_sign, right_sign) == (-1, 1) else 'positive_to_negative' if (left_sign, right_sign) == (1, -1) else 'no_sign_change'
            if self.mode == 'stationary_points':
                classification = {'negative_to_positive': 'local_minimum', 'positive_to_negative': 'local_maximum', 'no_sign_change': 'stationary_no_extremum', 'boundary_root': 'boundary_stationary_point'}[classification]
            classified.append({'root': encode_root(root), 'left_sign': left_sign, 'right_sign': right_sign, 'classification': classification})
        return {'schema': POLICY, 'verified': True, 'scope': 'complete roots and sign cells of the supplied expression on the supplied interval',
            'mode': self.mode, 'compilation_sha256': digest(self.report()), 'domain_proofs': domain_proofs,
            'root_isolation': isolation, 'roots': classified, 'sign_cells': cells,
            'root_count': len(roots), 'numerical_tolerance_used': False, 'source_semantics_verified': False}


def encode_root(root):
    record = {'exact': str(root)}
    if isinstance(root, sp.CRootOf):
        # A fixed dyadic enclosure is deterministic even if SymPy's cache has
        # already refined the internal isolating interval in another call.
        for bits in (40, 64, 96, 128, 256):
            lo, hi = enclosure(root, bits=bits)
            if root.poly.count_roots(lo, hi) == 1:
                record.update(polynomial=str(root.poly.as_expr()), index=int(root.index),
                    isolating_interval=[str(lo), str(hi)], sturm_root_count=1)
                break
        else:
            raise ValueError('could not encode a canonical isolating interval')
    return record


def compile_program(text, theorem=''):
    return Program(text).report()


def compute(text):
    return Program(text).solve()


def render(compiled, result):
    report = compiled['report']
    lines = ['## Exact root-classification lemma', '',
        'For the supplied expression `'+report['classified_expression']+'` in `'+report['variable']+'`,',
        'on interval `'+json.dumps(report['interval'], separators=(',', ':'))+'`, the complete root count is **'+str(result['root_count'])+'**.', '']
    for row in result['roots']:
        lines.append('- `'+row['root']['exact']+'`: '+row['classification']+'; signs '+str(row['left_sign'])+' → '+str(row['right_sign'])+'.')
    statement = '\n'.join(lines)
    appendix = '# Appendix A — Exact root isolation and sign classification\n\n'
    appendix += ('The polynomial below is an elimination superset. Exact real-root isolation covers all its real roots. '
        'Each candidate is checked against the positive square-root branch. Original denominators and the radicand domain '
        'are checked before classification. On each remaining interval the continuous expression has no zero or pole, '
        'so its sign equals the exact sign at the recorded rational sample. In stationary-points mode the expression is '
        'the derivative of the supplied function; its sign changes determine the listed local extrema.\n\n')
    appendix += 'The expression classified is `'+report['classified_expression']+'`.\n\n'
    if report['mode'] == 'stationary_points':
        appendix += 'It is the derivative of `'+report['function_or_expression']+'`.\n\n'
    appendix += 'The elimination polynomial is `'+result['root_isolation']['polynomial']+'`, over `'+result['root_isolation']['coefficient_domain']+'`.\n\n'
    appendix += 'A `CRootOf(P,k)` denotes the root of the indicated polynomial with zero-based index k in the exact root ordering. Each recorded rational isolating interval below contains exactly one root of its polynomial, checked by a Sturm root count.\n\n'
    appendix += '| Candidate root | Rational isolating interval | Signs of A, B in A+B√R | Original branch |\n| --- | --- | --- | --- |\n'
    for row in result['root_isolation']['branch_checks']:
        r = row['root']
        appendix += '| `'+r['exact']+'` | `'+str(r.get('isolating_interval', [r['exact'], r['exact']]))+'` | '+str(row['coefficient_signs'])+' | '+('accepted' if row['accepted_original_branch'] else 'rejected')+' |\n'
    appendix += '\nOriginal-domain checks (each condition has no zero in the specified interval):\n\n'
    for row in result['domain_proofs']:
        appendix += '- `'+row['condition']+'`; exact sign '+str(row['sign'])+' at rational sample `'+row['sample']+'`.\n'
    appendix += '\nThe accepted roots divide the interval into the following zero-free, pole-free open cells:\n\n'
    for row in result['sign_cells']:
        appendix += '- Between `'+row['left']['exact']+'` and `'+row['right']['exact']+'`, sample `'+row['sample']+'` has exact sign '+str(row['sign'])+'.\n'
    appendix += '\n'+statement+'\n\nThese computations classify the supplied expression; the source correspondence and its use in the full proof are separately audited.'
    return statement.strip(), appendix.strip()
