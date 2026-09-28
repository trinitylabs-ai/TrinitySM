"""Source-bound Cartesian programs and bounded, exact positivity derivations.

No theorem catalog, saved encoding, model, filesystem, or certificate search is
used by this compiler. Source quotations are provenance, not semantic proof.
"""
from __future__ import annotations

import itertools
import re
import sympy as sp
from . import matched_expression as syntax
from . import radical_certificate as radical
from . import geometry_normalization, source_binding, relative_sign, guard_closure, sum_of_squares, auxiliary_geometry, rational_geometry
from . import geometry_types, positive_multiple

VERSION = 'geometry-program-v1'
CONTRACT = r'''Return exactly # Decision, # Semantic Bindings, # Geometry Program.
Decision is CALL_TOOL; alternatively return # Decision NO_TOOL and # Reason.
Semantic Bindings must derive coordinates/normalization, every premise, the
target correspondence and all domain conditions from the theorem. The submitted
proof is untrusted. Inventory every hypothesis: encode it or explicitly retain
it with an explanation of why a weaker algebraic implication suffices. Do not
assert the target, introduce extra assumptions, or assume a construction valid.

Geometry Program contains exactly one geometry-args fence. Its line grammar is:
symbols = comma-separated real coordinate/parameter names (1..16)
define = unique_name :: expression
premise = unique_label :: predicate :: source ID or exact theorem excerpt
retain = unique_label :: source ID or exact theorem excerpt :: explanation
target = unique_label :: (eq expression expression)

The symbols field lists free REAL SCALARS, not every named geometric object.
For free points use coordinate scalars and explicit point definitions, e.g.
symbols = ax, ay, bx, by
define = A :: (point ax ay)
define = B :: (point bx by)
define = M :: (midpoint A B)
Do not put A, B or M in that symbols list or define any name twice. Every point
argument must be a point expression or a previously defined point, not a scalar.
Keep the total number of free coordinate scalars within the 16-symbol limit.
Each free point consumes two coordinate scalars. Reuse actual constructions
instead of giving every constructed point independent coordinates. Do not drop
domain conditions or fix arbitrary coordinates merely to fit this budget.

A premise may append a fourth field containing an explanation. It is preserved
as untrusted audit context and never adds an equation, sign fact or guard.

A retain line may instead use four fields: label :: description :: source ::
explanation. The optional description is preserved as untrusted audit context.
Neither retain form adds an equation, sign fact or nonzero guard.
Use the literal separators, for example:
retain = condition :: @source:S0001 :: Explain why retaining this suffices.

Declare symbols first, then all definitions, then premises/retained hypotheses,
then exactly one target last. In every source slot, prefer an @source:S0001-style
ID from the Exact Source Spans supplied below. The compiler resolves that ID to
unchanged original theorem text; it does not infer that the premise follows.
Reuse a span for several premises when needed, explaining each correspondence.
Literal excerpts are also accepted: copy exact original text, including its
actual LaTeX spelling. Matching outer quotation marks are allowed. Do not
paraphrase a shared clause into separate quotations. Neither an ID nor an exact
quotation proves a premise; every correspondence still needs independent audit.
No JSON, Python, decimal floats or file paths in the Geometry Program.
Scalar expressions use integer literals, declared names, (add ...), (mul ...),
(sub x y), (div x y), (rational integer integer), (neg x), (pow x integer).
Geometry expressions: (point x y), (vadd P Q), (vsub P Q), (scale k P),
(dot P Q), (cross P Q), (norm2 P), (x P), (y P), (midpoint P Q),
(foot P A B), (line_intersection A B C D), (circle A B C), (center circle),
(power circle P). A point expression may be nested in any point operand.
Points and scalars are distinct types. eq and ne also accept two points, with
the exact meaning that their squared distance is zero or nonzero, respectively.
All ordered comparisons require scalar operands. Operators have exactly the
arities displayed here; extra operands or unknown operators are rejected.
norm2 is squared Euclidean length. Ordinary norm is unsupported; replacing it
with norm2 changes the value and is not a valid syntax repair.
Predicates: (eq x y), (gt x y), (ge x y), (lt x y), (le x y), (ne x y),
(inside P A B C) for STRICT interior of a nondegenerate triangle, and
(angle_equal A B C D E F) for the ordinary angles ABC and DEF.
Only equality is supported as a target. Rational premises require independently
proved original denominator conditions before their sign facts can be used.
The target must express the stated conclusion, with all parameters and their
dependencies justified. An arbitrary stronger claim or guessed object is not a
replacement for an existential or fixed-object conclusion. Retain the original
quantifiers and explain the correspondence in Semantic Bindings.
Use actual coordinate variables for freely located points and derive constructions
with the geometry operators. Avoid independent sine/cosine variables for Cartesian
constructions. Similarity normalization must be justified for the actual claim.
If nested rational constructions exceed the algebra budget, use a smaller,
equivalent encoding. Additional coordinate variables with source-justified
defining equalities are allowed within the 16-symbol limit; account for every
original domain and exceptional branch. Such equalities are unaudited premises,
not automatically trusted construction facts. Size-limit rejection supplies no
mathematical conclusion and never licenses dropping a hypothesis or guard.

The compiler derives dot/cross equations, interior consequences, construction
denominators and the polynomial numerator of the target. It searches bounded
positive sums/products, factors, affine functions on triangle interiors, and
linear-equation pivots for provable nonzero guards. Unsupported denominators
reject the draft. It never assumes a proposed guard merely to make algebra work.
Angle equality first tries a bounded exact calculation to establish the sign of
the cross-product product from strict source facts and proved nonzero conditions.
If that fails, it tries the existing individual-sign positivity search.
It factors polynomials over the rationals and solves sign parity relations,
then independently replays a positive-source product times a nonzero rational
square. This proves relative orientation without assuming either absolute sign.
Successful replay enables a relative signed cotangent equation, with both angle
cross products proved nonzero. If neither sign method succeeds, the compiler
uses a weaker squared-cosine equation and records the relaxation. Failure of a
certificate search is inconclusive. Source semantics still need model audit.
'''


def polynomial(expr, symbols):
    return sp.Poly(sp.expand(expr), *symbols, domain=sp.QQ).as_expr()


class GeometryEvaluator(syntax.Evaluator):
    """Keep exact squared-length components before rational expansion."""
    clean = staticmethod(rational_geometry.clean)
    predicate = staticmethod(rational_geometry.predicate)
    def __init__(self, symbols):
        super().__init__(symbols)
        self.square_norms = []
        self.accessed_obligations = []
        self.definition_obligations = {}

    def require(self, relation, residual, reason):
        row = super().require(relation, residual, reason)
        if row not in self.accessed_obligations:
            self.accessed_obligations.append(row)
        return row

    def decode(self, node, depth=0):
        if isinstance(node, str):
            for row in self.definition_obligations.get(node, []):
                if row not in self.accessed_obligations:
                    self.accessed_obligations.append(row)
        if isinstance(node, list) and node and node[0] == 'norm':
            raise ValueError('unsupported ordinary norm: Euclidean length may require '
                             'square roots; norm2 is squared length and is not interchangeable')
        return super().decode(node, depth)

    def dot(self, a, b):
        value = super().dot(a, b)
        if a == b and len(self.square_norms) < 128:
            components = (a.x, a.y)
            if components not in self.square_norms:
                self.square_norms.append(components)
        return value


class AuxiliaryGeometryEvaluator(auxiliary_geometry.AuxiliaryMixin, GeometryEvaluator):
    pass


class Signs:
    """Derivations checked with exact identities; strictness is tracked explicitly."""
    def __init__(self, symbols):
        self.symbols = symbols
        self.facts = []
        self.hulls = []
        self.nonzeros = []
        self.memo = {}
        self._polynomials = {}
        self.steps = 0
        self.square_certificates = {}
        self.quadratic_certificates = {}
        self.positive_multiple_prover = positive_multiple.Prover(symbols)

    def add_norm(self, components):
        receipt = sum_of_squares.rational_norm(components, self.symbols)
        if receipt is not None:
            value = sum_of_squares.decode(receipt['target'], self.symbols)
            if value not in self.square_certificates:
                self.square_certificates[value] = receipt
                self.memo.clear()

    def source_nonzero(self, expr):
        direct = self.direct_source_nonzero(expr)
        if direct:return direct
        coefficient, factors = sp.factor_list(expr, *self.symbols)
        if coefficient and factors:
            proofs = [self.direct_source_nonzero(factor) for factor, _ in factors]
            if all(proofs):
                return {'rule':'product_of_nonzero_sources', 'expression':str(expr),
                        'coefficient':str(coefficient),
                        'factors':[{'expression':str(f), 'exponent':int(n), 'proof':p}
                                   for (f,n),p in zip(factors,proofs)]}
        return None

    def direct_source_nonzero(self, expr):
        expr = polynomial(expr, self.symbols)
        if expr == 0:
            return None
        if not expr.free_symbols:
            return {'rule':'nonzero_constant', 'expression':str(expr)}
        for fact,label in self.nonzeros+[(f,label) for f,strict,label in self.facts if strict]:
            if sp.rem(sp.Poly(fact,*self.symbols), sp.Poly(expr,*self.symbols)).is_zero:
                return {'rule':'factor_of_nonzero_source', 'source':label, 'expression':str(expr), 'multiple':str(sp.cancel(fact/expr))}
        return None

    def rational_multiple(self, numerator, denominator):
        """Same exact constant-ratio check, without repeated rational cancellation."""
        try:
            for value in (numerator, denominator):
                if value not in self._polynomials:
                    self._polynomials[value] = sp.Poly(value, *self.symbols, domain=sp.QQ)
            top, bottom = self._polynomials[numerator], self._polynomials[denominator]
        except (sp.PolynomialError, sp.polys.polyerrors.CoercionFailed):
            ratio = sp.cancel(numerator/denominator)
            return ratio if ratio.is_Rational else None
        if bottom.is_zero:
            return None
        if top.is_zero:
            return sp.Integer(0)
        ratio = top.LC()/bottom.LC()
        return ratio if top == bottom.mul_ground(ratio) else None

    def fact(self, expr, strict, source):
        expr = polynomial(expr, self.symbols)
        if not expr.free_symbols and (expr < 0 or (strict and expr == 0)):
            raise ValueError('false constant premise')
        self.facts.append((expr, strict, source))
        self.memo.clear()

    def positive(self, expr, *, weak=False, depth=0, trail=frozenset()):
        expr = sp.cancel(expr)
        key = (expr, weak)
        if key in self.memo:
            return self.memo[key]
        self.steps += 1
        if depth > 5 or self.steps > 4000 or key in trail:
            return None
        trail = trail | {key}
        def child(value, weak=False):
            return self.positive(value, weak=weak, depth=depth+1, trail=trail)
        def done(rule, **details):
            record = {'rule': rule, 'expression': str(expr), 'strict': not weak, **details}
            self.memo[key] = record
            return record
        if not expr.free_symbols:
            if expr.is_positive or (weak and expr.is_nonnegative):
                return done('exact_constant')
            return None
        for fact, strict, source in self.facts:
            if fact == 0:
                continue
            ratio = self.rational_multiple(expr, fact)
            if ratio is not None and ratio > 0 and (weak or strict):
                assert sp.expand(expr-ratio*fact) == 0
                return done('positive_multiple_of_source', source=source, factor=str(ratio))
        receipt = self.square_certificates.get(expr)
        if receipt is None:
            if expr not in self.quadratic_certificates:
                self.quadratic_certificates[expr] = sum_of_squares.quadratic(expr, self.symbols)
            receipt = self.quadratic_certificates[expr]
        if receipt is not None:
            forms = sum_of_squares.replay(receipt, expr, self.symbols)
            if weak:
                return done('checked_sum_of_squares', identity=receipt, nonzero_term=None)
            for index, form in enumerate(forms):
                proof = self.source_nonzero(form) or child(form) or child(-form)
                if proof:
                    return done('checked_sum_of_squares', identity=receipt,
                                nonzero_term={'index':index, 'expression':str(form), 'proof':proof})
        coefficient, factors = sp.factor_list(expr, *self.symbols)
        if factors and not (coefficient == 1 and len(factors) == 1 and factors[0] == (expr, 1)):
            sign = 1 if coefficient > 0 else -1
            records = []
            possible = True
            for factor, exponent in factors:
                if exponent % 2 == 0 and weak:
                    records.append({'rule': 'even_power_nonnegative', 'expression': str(factor), 'exponent': int(exponent)})
                    continue
                record = child(factor, weak=weak)
                if record:
                    records.append(record)
                else:
                    record = child(-factor, weak=weak)
                    if not record:
                        possible = False
                        break
                    if exponent % 2:
                        sign *= -1
                    records.append(record)
            if possible and sign == 1:
                return done('product', factors=records)
        # Positive sums do not inherit nonzero from merely nonnegative terms.
        if expr.is_Add and len(expr.args) <= 12:
            records = [child(term, weak=True) for term in expr.args]
            if all(records) and (weak or any(child(term) for term in expr.args)):
                return done('sum', terms=records,
                            positive_term=next((str(t) for t in expr.args if child(t)), None))
        # Any affine functional of a strict convex combination is positive if
        # its vertex values are nonnegative and one is positive. The barycentric
        # identity is re-expanded, including its orientation-independent weights.
        for label, point, vertices in self.hulls:
            if not isinstance(point.x, sp.Symbol) or not isinstance(point.y, sp.Symbol) or point.x == point.y:
                continue
            coords = (point.x, point.y)
            if any(set(coords) & (v.x.free_symbols | v.y.free_symbols) for v in vertices):
                continue
            if not (set(coords) & expr.free_symbols):
                continue
            try:
                if sp.Poly(expr, *coords).total_degree() > 1:
                    continue
            except sp.PolynomialError:
                continue
            values = [sp.expand(expr.subs({point.x:v.x, point.y:v.y}, simultaneous=True)) for v in vertices]
            records = [child(v, weak=True) for v in values]
            strict_values = [child(v) for v in values] if all(records) else []
            if not all(records) or not (weak or any(strict_values)):
                continue
            a,b,c = vertices
            cross, sub = syntax.Evaluator.cross, syntax.Evaluator.minus
            area = cross(sub(b,a), sub(c,a))
            numerators = [cross(sub(b,point),sub(c,point)), cross(sub(c,point),sub(a,point)), cross(sub(a,point),sub(b,point))]
            if sp.expand(area*expr-sum(n*v for n,v in zip(numerators,values))) != 0:
                raise ValueError('affine interior identity failed')
            return done('strict_interior_affine', source=label, area=str(area),
                        weight_numerators=list(map(str,numerators)), vertex_values=list(map(str,values)),
                        vertex_proofs=records, strict_vertex=next((i for i,p in enumerate(strict_values) if p),None))
        # Small positive combinations cover useful cancellation between signed
        # area polynomials without admitting arbitrary invented inequalities.
        if depth == 0:
            for fact, strict, source in self.facts[:24]:
                for coefficient in (sp.Integer(1), sp.Rational(1,2), sp.Integer(2)):
                    remainder = sp.expand(expr-coefficient*fact)
                    square_receipt = self.square_certificates.get(remainder)
                    if square_receipt is None:
                        if remainder not in self.quadratic_certificates:
                            self.quadratic_certificates[remainder] = sum_of_squares.quadratic(remainder,self.symbols)
                        square_receipt = self.quadratic_certificates[remainder]
                    if square_receipt is not None:
                        sum_of_squares.replay(square_receipt,remainder,self.symbols)
                        remainder_proof = child(remainder) if not (weak or strict) else None
                        if weak or strict or remainder_proof:
                            assert sp.expand(expr-coefficient*fact-remainder) == 0
                            return done('source_plus_checked_squares',source=source,
                                        source_expression=str(fact),coefficient=str(coefficient),
                                        remainder_identity=square_receipt,remainder_strict=remainder_proof)
                    for other, other_strict, other_source in self.facts[:24]:
                        if other == 0:continue
                        ratio=self.rational_multiple(remainder,other)
                        if ratio is not None and ratio >= 0 and (weak or strict or (ratio>0 and other_strict)):
                            assert sp.expand(expr-coefficient*fact-ratio*other)==0
                            return done('positive_combination', source=source, coefficient=str(coefficient),
                                        other_source=other_source,other_coefficient=str(ratio))
        self.memo[key]=None
        return None

    def nonzero(self, expr):
        expr = polynomial(expr, self.symbols)
        if expr == 0:return None
        source = self.source_nonzero(expr)
        if source:return source
        coefficient,factors=sp.factor_list(expr,*self.symbols)
        if factors and not (len(factors)==1 and factors[0]==(expr,1)):
            proofs=[self.nonzero(factor) for factor,_ in factors]
            if all(proofs):
                return {'rule':'product_of_proved_nonzero_factors','expression':str(expr),
                        'coefficient':str(coefficient),
                        'factors':[{'expression':str(f),'exponent':int(n),'proof':proof}
                                   for (f,n),proof in zip(factors,proofs)]}
        for value,negative in ((expr,False),(-expr,True)):
            record = self.positive(value)
            if record:
                return {'rule':'signed_implies_nonzero','negative':negative,'proof':record,'expression':str(expr)}
        for value, receipt in self.square_certificates.items():
            quotient, remainder = sp.div(sp.Poly(value,*self.symbols), sp.Poly(expr,*self.symbols))
            if remainder.is_zero:
                record = self.positive(value)
                if record:
                    assert sp.expand(expr*quotient.as_expr()-value) == 0
                    return {'rule':'factor_of_positive_square_sum', 'expression':str(expr),
                            'multiple':str(quotient.as_expr()), 'proof':record}
        receipt = self.positive_multiple_prover.prove(expr, self.facts, self.nonzeros)
        if receipt is not None:
            positive_multiple.replay(receipt, expr, self.symbols, self.facts)
            return {'rule':'factor_of_positive_multiple', 'expression':str(expr),
                    'identity':receipt}
        return None


def parse(text, theorem):
    text, normalization = geometry_normalization.normalize(text)
    sections = re.split(r'^# ([^\n]+)\n', text.strip(), flags=re.M)
    if sections[0] or len(sections) < 5:
        raise ValueError('expected named Markdown sections')
    names = sections[1::2]
    if len(names) != len(set(names)):
        raise ValueError('duplicate section')
    parts = dict(zip(names,(p.strip() for p in sections[2::2])))
    if parts.get('Decision') == 'NO_TOOL' and set(parts) == {'Decision','Reason'} and parts['Reason']:
        return {'call_requested':False,'reason':parts['Reason'],'normalization':normalization}
    if names != ['Decision','Semantic Bindings','Geometry Program'] or parts['Decision'] != 'CALL_TOOL' or not parts['Semantic Bindings']:
        raise ValueError('expected Decision, Semantic Bindings, Geometry Program')
    rows = syntax.fields(parts['Geometry Program'], fence='geometry-args')
    if not rows or rows[0][0] != 'symbols' or rows[-1][0] != 'target':
        raise ValueError('symbols first and target last required')
    symbols = syntax.names(rows[0][1])
    if not symbols or len(symbols) > 16:
        raise ValueError('require 1..16 symbols')
    taken = set(symbols)
    definitions, premises, retained, target = [], [], [], None
    source_bindings = []
    phase = 0
    for key,body in rows[1:]:
        allowed = {'define':0,'premise':1,'retain':1,'target':2}
        if key not in allowed or allowed[key] < phase:
            raise ValueError('unknown or misplaced field: '+key)
        phase = allowed[key]
        fields = body.split(' :: ')
        arities = {'define':{2}, 'premise':{3,4}, 'retain':{3,4}, 'target':{2,3}}[key]
        if len(fields) not in arities or not all(fields):
            raise ValueError(f'{key} field requires {" or ".join(map(str, sorted(arities)))} nonempty ::-separated parts; got {len(fields)}')
        if not syntax.IDENT.fullmatch(fields[0]):
            raise ValueError('invalid field label: '+fields[0])
        if fields[0] in taken:
            hint = ('; symbols lists free scalar coordinates only. Constructed '
                    'point names belong only in define. Free points need two '
                    'coordinates each, within the 16-scalar limit.'
                    if key == 'define' and fields[0] in symbols else '')
            raise ValueError('duplicate symbol or field label: '+fields[0]+hint)
        label = fields[0];taken.add(label)
        if key in {'premise','retain'}:
            source_index = 2 if key == 'premise' or len(fields) == 4 else 1
            quote = fields[source_index]
            quote, binding = source_binding.resolve(quote, theorem, label=label)
            if key == 'premise' and len(fields) == 4:
                binding['untrusted_explanation'] = fields[3]
            source_bindings.append(binding)
            fields[source_index] = quote
        elif key == 'target' and len(fields) == 3:
            # Optional provenance is checked and recorded, never an assumption.
            _, binding = source_binding.resolve(fields[2], theorem, label=label)
            source_bindings.append(binding)
        if key == 'define':definitions.append((label,syntax.expression(fields[1])))
        elif key == 'premise':premises.append((label,syntax.expression(fields[1]),fields[2]))
        elif key == 'retain':
            row = {'label':label,'excerpt':fields[source_index],'reason':fields[-1]}
            if len(fields) == 4:
                row['description'] = fields[1]
            retained.append(row)
        else:
            if target is not None:raise ValueError('exactly one target required')
            target = (label,syntax.expression(fields[1]))
    if len(premises)>32:
        raise ValueError('premise budget exceeded')
    return {'call_requested':True,'bindings':parts['Semantic Bindings'],'symbols':symbols,
            'normalization':normalization, 'source_bindings':source_bindings,
            'definitions':definitions,'premises':premises,'retained':retained,'target':target}


def compile_program(text, theorem):
    # Preserve successful direct compilations exactly. Only an expression-size
    # overflow enables the alternate representation, under the same bounds.
    try:
        return _compile_program(text,theorem)
    except ValueError as error:
        if str(error) not in {'expanded expression size limit', 'rational intermediate size limit'}:
            raise
        trigger = str(error)
    try:
        result = _compile_program(text,theorem,auxiliary=True)
        result['report']['auxiliary_compilation']['trigger'] = trigger
        return result
    except ValueError as error:
        raise ValueError('auxiliary fallback after '+trigger+': '+str(error)) from error


def _compile_program(text, theorem, *, auxiliary=False):
    parsed = parse(text,theorem)
    if not parsed['call_requested']:
        return parsed
    geometry_types.validate(parsed)
    ev = AuxiliaryGeometryEvaluator(parsed['symbols']) if auxiliary else GeometryEvaluator(parsed['symbols'])
    if auxiliary:
        reserved = set(parsed['symbols']) | {label for label,_ in parsed['definitions']}
        reserved |= {label for label,_,_ in parsed['premises']} | {r['label'] for r in parsed['retained']}
        reserved.add(parsed['target'][0])
        ev.initialize_auxiliaries(reserved)
    symbols = list(ev.env.values())
    for label,node in parsed['definitions']:
        ev.accessed_obligations = []
        value = ev.decode(node)
        if isinstance(value,syntax.Predicate):raise ValueError('predicate used as definition')
        if auxiliary:
            value = ev.bind_definition(value)
        ev.env[label] = value
        ev.definition_obligations[label] = list(ev.accessed_obligations)
    if auxiliary:
        # Freeze the symbol list before source sign facts are processed. No
        # auxiliary is introduced by a premise, target, or guard proof.
        ev.auxiliary_enabled = False
        symbols = list(ev.algebra_symbols)
    signs = Signs(symbols)
    for components in ev.square_norms:
        signs.add_norm(components)
    equations = list(ev.auxiliary_equations) if auxiliary else []
    angle_rows, coverage = [], []
    rational_premises = []
    pending_signs = []
    cross, sub, dot = ev.cross, ev.minus, ev.dot
    for label,node,quote in parsed['premises']:
        if not isinstance(node,list):raise ValueError('premise requires a predicate')
        op = node[0]
        coverage.append({'label':label,'operator':op,'excerpt':quote})
        if op == 'inside' and len(node)==5:
            p,a,b,c = [ev.point(ev.decode(x)) for x in node[1:]]
            area = polynomial(cross(sub(b,a),sub(c,a)),symbols)
            if area == 0:raise ValueError('degenerate interior triangle')
            signs.hulls.append((label,p,(a,b,c)))
            signs.nonzeros.append((area,label))
            for i,(u,v) in enumerate(((a,b),(b,c),(c,a))):
                edge = cross(sub(v,u),sub(p,u))
                signs.fact(area*edge,True,label+':oriented_halfplane_'+str(i))
                signs.nonzeros.append((edge,label))
        elif op == 'angle_equal' and len(node)==7:
            angle_rows.append((label,[ev.point(ev.decode(x)) for x in node[1:]]))
        else:
            ev.accessed_obligations = []
            pred = ev.decode(node)
            if not isinstance(pred,syntax.Predicate):raise ValueError('source requires a comparison')
            if pred.relation == 'eq':
                n,d = sp.fraction(sp.cancel(pred.residual))
                n,d = polynomial(n,symbols),polynomial(d,symbols)
                if d.free_symbols:
                    # Equality clearing adds no sign fact or nonzero assumption.
                    # Signs never reads these equations, so this premise cannot
                    # supply its own denominator proof. Admission is gated below.
                    if sp.cancel(pred.residual*d-n) != 0:
                        raise ValueError('rational premise identity replay failed')
                    rational_premises.append({'label':label,'residual':str(pred.residual),
                        'numerator':str(n),'denominator':str(d),'identity_checked':True,
                        '_denominator':d})
                    value = n
                else:
                    value = polynomial(pred.residual,symbols)
            else:
                n,d = sp.fraction(pred.residual)
                n,d = polynomial(n,symbols),polynomial(d,symbols)
                # n/d has the sign of n*d on its original domain, regardless
                # of the denominator's sign. Nonzero needs only n != 0.
                value = (n if pred.relation == 'ne' else polynomial(n*d,symbols)) if d.free_symbols else polynomial(pred.residual,symbols)
                if d.free_symbols:
                    if rational_geometry.clean(pred.residual*d-n) != 0:
                        raise ValueError('rational premise identity replay failed')
                    rational_premises.append({'label':label,'relation':pred.relation,
                        'residual':str(pred.residual),'numerator':str(n),
                        'denominator':str(d),'identity_checked':True,'_denominator':d,
                        'polynomial_comparison':str(value)})
                    ev.require('ne',d,'rational premise denominator: '+label)
            if pred.relation=='eq':equations.append((label,value))
            else:
                pending_signs.append((label,pred.relation,value,list(ev.accessed_obligations)))
    # A sign premise may be used only after its complete original domain is
    # established from already admitted facts. This includes canceled divisions
    # and transitive definition dependencies. Unadmitted premises cannot prove
    # their own domains, nor can two such premises bootstrap each other.
    while pending_signs:
        progress = False
        for row in list(pending_signs):
            label,relation,value,domains = row
            valid = True
            for item in domains:
                p = item['_predicate']
                if p.truth is True:
                    continue
                n,d = sp.fraction(p.residual)
                if p.relation == 'ne':
                    valid = bool(signs.nonzero(n) and signs.nonzero(d))
                elif p.relation == 'eq':
                    valid = n == 0 and bool(signs.nonzero(d))
                else:
                    valid = bool(signs.nonzero(d) and signs.positive(n*d)) if p.relation == 'gt' else False
                if not valid:
                    break
            if not valid:
                continue
            if relation == 'ne':
                if value == 0:raise ValueError('zero nonzero premise')
                signs.nonzeros.append((value,label))
            else:
                signs.fact(-value if relation in {'lt','le'} else value,relation in {'gt','lt'},label)
            pending_signs.remove(row)
            progress = True
        if not progress:
            raise ValueError('unproved source comparison domain: '+', '.join(row[0] for row in pending_signs))
    angle_report=[]
    for label,(a,b,c,d,e,f) in angle_rows:
        u,v,w,z = sub(a,b),sub(c,b),sub(d,e),sub(f,e)
        c1,c2 = cross(u,v),cross(w,z)
        relative = relative_sign.prove(sp.expand(c1*c2),symbols,signs.facts,signs.nonzeros)
        if relative is not None:
            equation=dot(u,v)*c2-relative['sign']*dot(w,z)*c1
            method='relative_signed_cotangent';proofs=[relative]
        else:
            orient=[]
            for value in (c1,c2):
                pos,neg = signs.positive(value),signs.positive(-value)
                orient.append((1,pos) if pos else (-1,neg) if neg else (0,None))
            if all(x[0] for x in orient):
                equation=dot(u,v)*orient[1][0]*c2-dot(w,z)*orient[0][0]*c1
                method='signed_cotangent';proofs=[x[1] for x in orient]
            else:
                equation=dot(u,v)**2*dot(w,w)*dot(z,z)-dot(w,z)**2*dot(u,u)*dot(v,v)
                method='squared_cosine_necessary_condition';proofs=[]
        equations.append((label,polynomial(equation,symbols)))
        angle_report.append({'label':label,'method':method,'orientation_proofs':proofs})
    target_label,node = parsed['target']
    pred=ev.decode(node)
    for components in ev.square_norms:
        signs.add_norm(components)
    if not isinstance(pred,syntax.Predicate) or pred.relation!='eq':raise ValueError('target must be an equality')
    numerator,denominator=sp.fraction(sp.cancel(pred.residual))
    numerator,denominator=polynomial(numerator,symbols),polynomial(denominator,symbols)
    assert sp.cancel(pred.residual*denominator-numerator)==0
    obligations=[]
    for row in rational_premises:
        d = row.pop('_denominator')
        proof = signs.nonzero(d)
        if not proof:
            raise ValueError('unproved rational premise denominator: '+row['label']+' :: '+str(d))
        row['denominator_proof'] = proof
        obligations.append({'reason':'rational premise denominator: '+row['label'],
                            'expression':str(d),'proof':proof})
    for item in ev.obligations:
        p=item['_predicate']
        if p.truth is True:continue
        if p.relation=='eq':
            if p.residual != 0:raise ValueError('construction equality must be independently established: '+item['reason'])
            continue
        if p.relation == 'gt':
            n,d = sp.fraction(p.residual)
            denominator_proof = signs.nonzero(d)
            positive_proof = signs.positive(n*d)
            if not denominator_proof or not positive_proof:
                raise ValueError('unproved positive construction condition: '+item['reason'])
            obligations.append({'reason':item['reason'],'expression':str(p.residual),
                'proof':{'rule':'positive_rational','denominator':denominator_proof,
                         'positive_product':positive_proof}})
            continue
        if p.relation!='ne':raise ValueError('unsupported construction sign obligation')
        n,d=sp.fraction(p.residual)
        for value in (n,d):
            proof=signs.nonzero(value)
            if not proof:raise ValueError('unproved construction denominator: '+str(value))
            obligations.append({'reason':item['reason'],'expression':str(value),'proof':proof})
    proof=signs.nonzero(denominator)
    if not proof:raise ValueError('unproved target denominator')
    obligations.append({'reason':'target denominator','expression':str(denominator),'proof':proof})
    primitive=[]
    for label,equation in equations:
        if equation!=0:
            value=sp.Poly(equation,*symbols,domain=sp.QQ).primitive()[1].as_expr()
            if not value.free_symbols:raise ValueError('inconsistent constant equation')
            primitive.append((label,value))
    if not primitive:
        # Native certificate payload requires at least one source generator.
        primitive=[('identity',sp.Integer(0))]
    candidates={}
    def candidate(value,origin,priority):
        for factor,_ in sp.factor_list(value,*symbols)[1]:
            factor=sp.Poly(factor,*symbols,domain=sp.QQ).monic().as_expr()
            if factor in candidates or len(candidates)>=48:continue
            proof=signs.nonzero(factor)
            if proof:candidates[factor]={'expression':str(factor),'proof':proof,'origin':origin,'priority':priority}
    # Linear pivots are chosen by algebraic structure; no source names have meaning.
    for label,value in primitive:
        for symbol in symbols:
            p=sp.Poly(value,symbol)
            if p.degree()==1:candidate(p.coeff_monomial(symbol),label+':linear_pivot',0)
    for value,label in signs.nonzeros:candidate(value,label,1)
    for value,strict,label in signs.facts:
        if strict:candidate(value,label,2)
    candidates=sorted(candidates.items(),key=lambda x:(x[1]['priority'],sp.Poly(x[0],*symbols).total_degree(),sp.count_ops(x[0]),str(x[0])))[:16]
    candidates += guard_closure.derive([value for value,_ in candidates],symbols,signs.facts,signs.nonzeros)
    guards={f'G{i+1}':value for i,(value,_) in enumerate(candidates)}
    system=radical.system_payload(symbols,primitive,numerator,guards)
    report={'schema':VERSION,'coverage':coverage,'retained':parsed['retained'],
            'normalization':parsed['normalization'],
            'source_bindings':parsed['source_bindings'],
            'definitions':{k:syntax.payload(ev.env[k]) for k,_ in parsed['definitions']},
            'angle_encodings':angle_report,'construction_obligations':obligations,
            'rational_premise_encodings':rational_premises,
            'guard_derivations':{f'G{i+1}':row for i,(_,row) in enumerate(candidates)},
            'equations':{k:str(v) for k,v in primitive},'target_numerator':str(numerator),
            'target_denominator':str(denominator),'target_residual':str(pred.residual),
            'target_identity_checked':True,'source_semantics_verified':False,
            'source_semantics':'MODEL_AUDIT_REQUIRED','guard_search_steps':signs.steps}
    if auxiliary:
        report['auxiliary_compilation'] = ev.auxiliary_report()
    return {'call_requested':True,'bindings':parsed['bindings'],'system':system,'report':report}


def guard_subsets(system):
    """All singletons and pairs in the bounded pool, ordered by polynomial cost."""
    labels=list(system['guards'])
    symbols,equations,_,guards=radical.backends.integration._decode_transform_payload(system)
    pivot_factors=set()
    for _,equation in equations:
        for symbol in symbols:
            poly=sp.Poly(equation,symbol)
            if poly.degree()==1:
                for factor,_ in sp.factor_list(poly.coeff_monomial(symbol),*symbols)[1]:
                    pivot_factors.add(guard_closure.canonical(factor,symbols))
    pivots={label for label,value in guards.items()
            if guard_closure.canonical(value,symbols) in pivot_factors}
    def cost(label):
        value=system['guards'][label]
        return (value['degree'],value['term_count'],labels.index(label))
    singles=sorted(labels,key=lambda label:(label not in pivots,cost(label)))
    pairs=sorted(itertools.combinations(labels,2),
        key=lambda pair:(not any(x in pivots for x in pair),
                         sum(cost(x)[0] for x in pair),sum(cost(x)[1] for x in pair),
                         tuple(labels.index(x) for x in pair)))
    subsets=[(),*[(x,) for x in singles],*pairs,tuple(labels)]
    unique=[]
    for subset in subsets:
        if subset not in unique:unique.append(subset)
    return unique
