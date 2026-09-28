"""Synthetic geometry only; no benchmark statements, equations or certificates."""
import copy
import json
import sympy as sp
import pytest
from . import geometry_program as geometry, geometry_workflow as workflow
from . import radical_certificate as radical


def program(body, bindings='Use the stated coordinates and constraints.'):
    return '# Decision\n\nCALL_TOOL\n\n# Semantic Bindings\n\n'+bindings+'\n\n# Geometry Program\n\n```geometry-args\n'+body+'\n```'


THEOREM='The point lies strictly inside the triangle. The scalar product equals one.'
BODY='''symbols = x, y, z
define = A :: (point 0 0)
define = B :: (point 5 0)
define = C :: (point 1 3)
define = P :: (point x y)
define = O :: (center (circle A P B))
premise = interior :: (inside P A B C) :: lies strictly inside the triangle
premise = equation :: (eq (mul (add x y) z) 1) :: The scalar product equals one.
target = conclusion :: (eq (norm2 (vsub O A)) (norm2 (vsub O B)))'''


def decode(system):
    return radical.backends.integration._decode_transform_payload(system)


def test_geometry_compilation_derives_construction_domain_and_pivots():
    result=geometry.compile_program(program(BODY),THEOREM)
    assert result==geometry.compile_program(program(BODY),THEOREM)
    assert result['report']['target_identity_checked']
    assert not result['report']['source_semantics_verified']
    assert result['report']['construction_obligations']
    guards=result['report']['guard_derivations']
    assert any(g['expression']=='x + y' for g in guards.values())
    assert decode(result['system'])[2]==0


def test_missing_hypothesis_cannot_justify_circle_denominator():
    body=BODY.replace('premise = interior :: (inside P A B C) :: lies strictly inside the triangle\n','')
    with pytest.raises(ValueError,match='unproved construction denominator'):
        geometry.compile_program(program(body),THEOREM)


def test_nonnegative_never_becomes_nonzero():
    x,y=sp.symbols('x y',real=True);signs=geometry.Signs([x,y])
    signs.fact(x,False,'weak');signs.fact(y,False,'weak_other')
    assert signs.positive(x+y,weak=True)
    assert signs.nonzero(x+y) is None
    assert signs.nonzero(x*x) is None
    signs.fact(y,True,'strict')
    assert signs.nonzero(x+y)
    assert signs.nonzero(x-y) is None


@pytest.mark.parametrize('scale,dx,dy',[(1,0,0),(3,7,-2),(-2,4,9)])
def test_affine_interior_sign_survives_translation_rotation_scaling(scale,dx,dy):
    x,y=sp.symbols('x y',real=True);Point=geometry.syntax.Point
    def transform(a,b):return Point(sp.Integer(dx-scale*b),sp.Integer(dy+scale*a))
    signs=geometry.Signs([x,y]);signs.hulls.append(('inside',Point(x,y),(transform(0,0),transform(5,0),transform(1,3))))
    # Pull back u+v, which is positive on the strict interior of the original triangle.
    expr=sp.expand((y-dy)/scale-(x-dx)/scale)
    assert signs.positive(expr)
    assert signs.positive(-expr) is None


def test_angle_orientation_and_explicit_relaxation():
    theorem='The two angles are equal.'
    body='''symbols = t
define = A :: (point 1 1)
define = B :: (point 0 0)
define = C :: (point 1 0)
define = D :: (point 1 0)
define = E :: (point 0 0)
define = F :: (point 1 1)
premise = angles :: (angle_equal A B C D E F) :: The two angles are equal.
target = trivial :: (eq t t)'''
    result=geometry.compile_program(program(body),theorem)
    assert result['report']['angle_encodings'][0]['method']in {'signed_cotangent','relative_signed_cotangent'}
    relaxed=geometry.compile_program(program(body.replace('(point 1 1)','(point 1 t)',1)),theorem)
    assert relaxed['report']['angle_encodings'][0]['method']=='squared_cosine_necessary_condition'


@pytest.mark.parametrize('edit',[
    lambda body:body.replace('lies strictly inside the triangle','invented missing source'),
    lambda body:body.replace('(point 1 3)','(point 1 0)'),
    lambda body:body.replace('(point x y)',"(__import__ os)"),
    lambda body:body.replace('(point 5 0)','(point 5.0 0)'),
    lambda body:body+'\ntarget = second :: (eq x x)',
])
def test_invalid_source_programs_fail_closed(edit):
    with pytest.raises(ValueError):geometry.compile_program(program(edit(BODY)),THEOREM)


def test_false_identity_and_exact_certificate_tampering(tmp_path):
    theorem='The positive number satisfies the displayed equation.'
    body='''symbols = x, y
premise = positive :: (gt x 0) :: The positive number
premise = relation :: (eq (mul x y) x) :: satisfies the displayed equation
target = desired :: (eq y 1)'''
    result=geometry.compile_program(program(body),theorem)
    search=workflow.certificate_search(result,tmp_path/'good',timeout=20,memory=4096)
    assert search['exact_verified']
    root=__import__('pathlib').Path(search['certificate_root'])
    system=json.loads((root/'system.json').read_text());cert=json.loads((root/'certificate.json').read_text())
    assert workflow.replay_certificate(system,cert)['verified']
    broken=copy.deepcopy(cert)
    if 'multipliers' in broken:
        for multiplier in broken['multipliers']:multiplier['terms']=[]
    else:broken['request_sha256']='tampered'
    with pytest.raises(ValueError):workflow.replay_certificate(system,broken)
    bad=geometry.compile_program(program(body.replace('(eq y 1)','(eq y 2)')),theorem)
    assert not workflow.certificate_search(bad,tmp_path/'bad',timeout=20,memory=4096)['exact_verified']
    unguarded=geometry.compile_program(program(body.replace('premise = positive :: (gt x 0) :: The positive number\n','')),theorem)
    assert not workflow.certificate_search(unguarded,tmp_path/'unguarded',timeout=20,memory=4096)['exact_verified']


def test_bounded_compilation_replays_same_program():
    assert workflow.compile_bounded(program(BODY),THEOREM)==geometry.compile_program(program(BODY),THEOREM)
