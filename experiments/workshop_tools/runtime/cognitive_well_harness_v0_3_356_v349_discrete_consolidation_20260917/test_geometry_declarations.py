"""Type-directed elaboration must preserve exact algebra and all obligations."""
import copy
import hashlib

import pytest

from . import geometry_normalization as normalization, geometry_program as geometry
from . import geometry_types, geometry_workflow as workflow
from .test_geometry_program import program


BODY = '''symbols = Q, R, M, t
define = M :: (midpoint Q R)
target = same :: (eq (norm2 (vsub M Q)) (norm2 (vsub M R)))'''
CANONICAL = '''symbols = coordinate_1, coordinate_2, coordinate_3, coordinate_4, t
define = Q :: (point coordinate_1 coordinate_2)
define = R :: (point coordinate_3 coordinate_4)
define = M :: (midpoint Q R)
target = same :: (eq (norm2 (vsub M Q)) (norm2 (vsub M R)))'''


def replay_edits(raw, record):
    lines = raw.splitlines(keepends=True)
    for edit in record['edits']:
        start = edit['line'] - 1
        if 'character_count' in edit:
            text = ''.join(lines)
            offset = len(''.join(lines[:start]))
            end = offset + edit['character_count']
            assert text[offset:end] == edit['before']
            lines = (text[:offset] + edit['after'] + text[end:]).splitlines(keepends=True)
        else:
            ending = '\r\n' if lines[start].endswith('\r\n') else '\n' if lines[start].endswith('\n') else ''
            assert lines[start].rstrip('\r\n') == edit['before']
            lines[start] = edit['after'] + ending
    return ''.join(lines)


def test_redundant_points_lower_to_unrestricted_coordinates_and_same_algebra():
    raw = program(BODY)
    fixed, receipt = normalization.normalize(raw)
    assert fixed == program(CANONICAL)
    assert receipt['raw_sha256'] == hashlib.sha256(raw.encode()).hexdigest()
    assert replay_edits(raw, receipt) == fixed
    detail = receipt['edits'][-1]
    assert detail['redundant_point_declarations'] == ['M']
    assert detail['new_constraints'] == []
    assert detail['original_expressions_unchanged']
    compiled = geometry.compile_program(raw, 'Arbitrary points.')
    explicit = geometry.compile_program(fixed, 'Arbitrary points.')
    compiled['report'].pop('normalization')
    explicit['report'].pop('normalization')
    assert compiled == explicit
    assert compiled['report']['target_identity_checked']
    assert not compiled['report']['source_semantics_verified']
    twice, second = normalization.normalize(fixed)
    assert twice == fixed and not second['applied']


@pytest.mark.parametrize('body', [
    'symbols = Q, R\ntarget = same :: (eq (vsub Q R) (point 0 0))',
    'symbols = Q, R\npremise = distinct :: (ne Q R) :: Points differ.\ntarget = same :: (eq (norm2 (vsub Q R)) (norm2 (vsub R Q)))',
    'symbols = Q, R\ndefine = X :: Q\ntarget = same :: (eq (dot X R) (dot R X))',
    'symbols = q, r\ntarget = same :: (eq (x q) (x r))',
])
def test_types_come_from_operator_uses_not_name_spelling(body):
    fixed, record = normalization.normalize(program(body))
    assert record['applied']
    parsed = geometry.parse(fixed, 'Points differ.')
    geometry_types.validate(parsed)
    assert len(parsed['symbols']) == 4


@pytest.mark.parametrize('body', [
    'symbols = Q, t\ntarget = same :: (eq (add Q t) (x Q))',
    'symbols = Q, R\ndefine = Q :: (point R 0)\ntarget = same :: (eq (dot Q R) 0)',
    'symbols = Q, R\ndefine = Q :: (midpoint Q R)\ntarget = same :: (eq (x Q) 0)',
    'symbols = Q, R, M\ndefine = X :: (midpoint M Q)\ndefine = M :: (midpoint Q R)\ntarget = same :: (eq (x X) 0)',
    'symbols = Q, R\ndefine = M :: (midpoint Q R)\ndefine = M :: (midpoint Q R)\ntarget = same :: (eq (x M) 0)',
    'symbols = q, r\ndefine = q :: (add r 1)\ntarget = same :: (eq q r)',
    'symbols = Q, R\npremise = Q :: (ne Q R) :: Points differ.\ntarget = same :: (eq (x Q) (x R))',
    'symbols = C, P\ntarget = same :: (eq (power C P) 0)',
    'symbols = Q, R\ntarget = same :: (eq (norm (vsub Q R)) 0)',
    'symbols = Q, R\ntarget = same :: (eq (vsub Q R R) (point 0 0))',
    'symbols = Q, R\ntarget = same :: (eq (dot Q R) 0)\ntarget = other :: (eq (dot R Q) 0)',
])
def test_conflicting_circular_unsupported_and_rebinding_programs_still_fail(body):
    raw = program(body)
    fixed, receipt = normalization.normalize(raw)
    assert not any(e['rule'] == 'typed_point_declarations' for e in receipt['edits'])
    with pytest.raises(ValueError):
        geometry_types.validate(geometry.parse(fixed, 'Points differ.'))


def test_unconstrained_names_remain_scalars_and_coordinates_avoid_capture():
    raw = program('symbols = Q, coordinate_1, t\ntarget = same :: (eq (x Q) (add coordinate_1 t))')
    fixed, receipt = normalization.normalize(raw)
    assert receipt['edits'][-1]['point_coordinates'] == {'Q': ['coordinate_2', 'coordinate_3']}
    assert '(add coordinate_1 t)' in fixed
    raw = program('symbols = A, B\ntarget = same :: (eq A B)')
    assert normalization.normalize(raw)[0] == raw


def test_expanded_coordinate_budget_is_not_relaxed():
    names = ['P' + str(i) for i in range(9)]
    body = 'symbols = ' + ', '.join(names) + '\ntarget = same :: (eq (add ' + ' '.join('(x '+n+')' for n in names) + ') 0)'
    raw = program(body)
    assert normalization.normalize(raw)[0] == raw
    with pytest.raises(ValueError):
        geometry_types.validate(geometry.parse(raw, 'Arbitrary points.'))


def test_source_quotes_remain_exact_and_missing_retain_separator_preserves_both_parts():
    body = BODY.replace('target = ', 'retain = condition :: "Points differ." @source:S0001 "Unencoded hypothesis."\ntarget = ')
    raw = program(body)
    fixed, receipt = normalization.normalize(raw)
    assert replay_edits(raw, receipt) == fixed
    assert '"Points differ." @source:S0001 :: "Unencoded hypothesis."' in fixed
    parsed = geometry.parse(raw, 'Points differ.')
    assert parsed['source_bindings'][0]['resolution'] == 'source_id_with_exact_quote'
    assert parsed['retained'][0]['excerpt'] == 'Points differ.'
    with pytest.raises(ValueError, match='source excerpt not found'):
        geometry.parse(raw.replace('"Points differ."', '"Invented quote."'), 'Points differ.')


def test_missing_denominator_guard_still_rejects():
    raw = program('symbols = Q, R, S\ndefine = O :: (center (circle Q R S))\ntarget = same :: (eq (norm2 (vsub O Q)) (norm2 (vsub O R)))')
    with pytest.raises(ValueError, match='unproved construction denominator'):
        geometry.compile_program(raw, 'Arbitrary points.')


def test_false_target_remains_false_and_changed_draft_invalidates_compilation(tmp_path):
    raw = program('symbols = Q, R, t\npremise = parameter :: (eq t 0) :: A parameter vanishes.\ntarget = false_claim :: (eq (norm2 (vsub Q R)) 0)')
    compiled = geometry.compile_program(raw, 'A parameter vanishes.')
    assert compiled['report']['target_numerator'] != '0'
    search = workflow.certificate_search(compiled, tmp_path/'false_target', timeout=3, memory=4096)
    assert not search['exact_verified']
    changed = raw.replace('(norm2 (vsub Q R)) 0', '(norm2 (vsub Q R)) 1')
    assert geometry.compile_program(changed, 'A parameter vanishes.') != compiled


def test_exact_certificate_and_replay_still_bind_to_lowered_system(tmp_path):
    compiled = geometry.compile_program(program(BODY), 'Arbitrary points.')
    result = workflow.certificate_search(compiled, tmp_path/'certificate', timeout=10, memory=4096)
    assert result['exact_verified']
    import json
    from pathlib import Path
    root = Path(result['certificate_root'])
    system = json.loads((root/'system.json').read_text())
    certificate = json.loads((root/'certificate.json').read_text())
    assert workflow.replay_certificate(system, certificate)['verified']
    bad = copy.deepcopy(certificate)
    bad['request_sha256'] = 'tampered'
    with pytest.raises(ValueError):
        workflow.replay_certificate(system, bad)
