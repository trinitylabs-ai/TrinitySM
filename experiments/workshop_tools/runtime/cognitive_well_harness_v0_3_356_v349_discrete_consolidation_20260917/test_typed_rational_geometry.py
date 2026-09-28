"""Generic compiler regressions, with no benchmark-specific mathematics."""
import pytest
import sympy as sp
from . import geometry_program as geometry, rational_geometry
from .test_geometry_program import program, decode


@pytest.mark.parametrize('bad', [
    '(gt A 0)', '(circle A A)', '(mystery A)', '(dot A missing)',
    '(scale A 2)', '(eq A 0)', '(norm A)',
])
def test_entire_program_is_typed_before_symbolic_work(monkeypatch, bad):
    raw = program('symbols = x\ndefine = costly :: (pow (add x 1) 32)\n'
                  'define = A :: (point x 0)\n'
                  'premise = condition :: '+bad+' :: The condition holds.\n'
                  'target = conclusion :: (eq x x)')
    monkeypatch.setattr(geometry.GeometryEvaluator,'decode',
                        lambda *a, **k: pytest.fail('symbolic evaluation before type check'))
    with pytest.raises(ValueError,match='geometry type check'):
        geometry.compile_program(raw,'The condition holds.')


def test_point_equality_is_exact_squared_distance_over_real_coordinates():
    raw = program('symbols = x, y\ndefine = A :: (point x y)\n'
                  'define = B :: (point 2 3)\n'
                  'premise = distinct :: (ne A B) :: The points differ.\n'
                  'target = same :: (eq A B)')
    compiled = geometry.compile_program(raw,'The points differ.')
    symbols,_,target,_ = decode(compiled['system'])
    x,y = symbols
    assert sp.expand(target - (x-2)**2 - (y-3)**2) == 0
    assert target.subs({x:2,y:3}) == 0
    assert target.subs({x:2,y:4}) == 1


@pytest.mark.parametrize('relation', ['ne', 'gt', 'ge', 'lt', 'le'])
def test_rational_comparison_requires_independent_denominator(relation):
    body = ('symbols = x, d\n'
            'premise = relation :: ('+relation+' (div x d) 0) :: The condition holds.\n'
            'target = identity :: (eq x x)')
    with pytest.raises(ValueError,match='unproved source comparison domain'):
        geometry.compile_program(program(body),'The condition holds.')
    body=body.replace('premise = relation','premise = guard :: (ne d 0) :: The condition holds.\npremise = relation')
    compiled=geometry.compile_program(program(body),'The condition holds.')
    assert compiled['report']['rational_premise_encodings'][0]['denominator_proof']


@pytest.mark.parametrize('defined', [False, True])
def test_canceled_division_cannot_prove_its_own_original_domain(defined):
    expression = '(mul (div d d) d)'
    definitions = 'define = hidden :: '+expression+'\ndefine = alias :: hidden\n' if defined else ''
    raw = program('symbols = d\n'+definitions+'premise = positive :: (gt '+
                  ('alias' if defined else expression)+' 0) :: The condition holds.\n'
                  'target = identity :: (eq d d)')
    with pytest.raises(ValueError,match='unproved source comparison domain'):
        geometry.compile_program(raw,'The condition holds.')


def test_rational_guards_cannot_bootstrap_each_other():
    raw = program('''symbols = x, y
premise = first :: (ne (div x y) 0) :: The condition holds.
premise = second :: (ne (div y x) 0) :: The condition holds.
target = identity :: (eq x x)''')
    with pytest.raises(ValueError,match='unproved source comparison domain'):
        geometry.compile_program(raw,'The condition holds.')


@pytest.mark.parametrize('relation', ['gt','ge','lt','le'])
def test_ordered_rational_comparison_handles_negative_denominator(relation):
    raw = program('''symbols = x, d
premise = guard :: (ne d 0) :: The condition holds.
premise = comparison :: (REL (div x d) 2) :: The condition holds.
target = identity :: (eq x x)'''.replace('REL',relation))
    compiled = geometry.compile_program(raw,'The condition holds.')
    row = compiled['report']['rational_premise_encodings'][0]
    # Multiplying by d would reverse an ordering at negative d. The encoded
    # residual instead equals the original residual times strictly positive d^2.
    assert row['polynomial_comparison'] == '-2*d**2 + d*x'
    for x in (-7,0,5):
        for d in (-3,2):
            assert sp.sign(sp.Rational(x,d)-2) == sp.sign((x-2*d)*d)


def test_rational_field_reduction_matches_independent_symbolic_algebra():
    a,b,c = sp.symbols('a b c',real=True)
    expressions = [((a+b)**6-(a-b)**6)/(a*b),
                   (a/b+b/c)/(1/b+1/c),
                   ((a+b)/(a-b))**3 - 1]
    for expr in expressions:
        result = rational_geometry.clean(expr)
        assert sp.cancel(result-expr) == 0


def test_rational_guard_may_follow_comparison():
    lines = ['symbols = x, d',
             'premise = comparison :: (ne (div x d) 0) :: The condition holds.',
             'premise = guard :: (ne d 0) :: The condition holds.',
             'target = identity :: (eq x x)']
    a=geometry.compile_program(program('\n'.join(lines)),'The condition holds.')
    lines[1],lines[2]=lines[2],lines[1]
    b=geometry.compile_program(program('\n'.join(lines)),'The condition holds.')
    assert a['system'] == b['system']


def test_intermediate_budget_can_use_checked_auxiliary_fallback(monkeypatch):
    monkeypatch.setattr(rational_geometry,'MAX_INTERMEDIATE_PRODUCTS',2000)
    raw=program('''symbols = a, b, c
define = H :: (pow (add a b c) 12)
define = K :: (pow H 2)
target = identity :: (eq K (pow H 2))''')
    with pytest.raises(ValueError,match='rational intermediate size limit'):
        geometry._compile_program(raw,'An arbitrary identity.')
    compiled=geometry.compile_program(raw,'An arbitrary identity.')
    report=compiled['report']['auxiliary_compilation']
    assert report['trigger'] == 'rational intermediate size limit'
    assert report['definitions'] and report['equations_excluded_from_guard_prover']
    _,_,target,_=decode(compiled['system'])
    assert target == 0


def test_provably_positive_symbolic_circle_radius_remains_supported():
    raw=program('''symbols = x
define = C :: (circle_center_radius (point 0 0) (add (pow x 2) 1))
target = identity :: (eq (power C (point 0 0)) (neg (pow (add (pow x 2) 1) 2)))''')
    compiled=geometry.compile_program(raw,'An arbitrary circle identity.')
    assert compiled['report']['target_numerator'] == '0'
    assert any(o['reason']=='circle radius must be positive'
               for o in compiled['report']['construction_obligations'])
