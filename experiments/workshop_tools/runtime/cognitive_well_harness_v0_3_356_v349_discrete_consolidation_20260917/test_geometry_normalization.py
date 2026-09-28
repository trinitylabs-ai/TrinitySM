"""Syntax recovery cannot manufacture premises or change mathematical expressions."""
import hashlib

import pytest

from . import geometry_normalization as normalization, geometry_program as geometry
from .test_geometry_program import program, BODY, THEOREM


@pytest.mark.parametrize('edit,rule',[
    (lambda b:b.replace('symbols = ', 'symbols '), 'missing_symbols_equals'),
    (lambda b:b.replace('define = ', 'define '), 'missing_field_equals'),
    (lambda b:b.replace('premise = ', 'premise '), 'missing_field_equals'),
    (lambda b:b.replace('target = ', 'target '), 'missing_field_equals'),
    (lambda b:b.replace('define = A :: ', 'define A = '), 'definition_assignment_separator'),
    (lambda b:b.replace('symbols = ', '', 1), 'bare_initial_symbol_list'),
    (lambda b:b.replace('symbols = ', 'symbols='), 'field_separator_whitespace'),
])
def test_syntax_variants_preserve_the_complete_algebraic_system(edit,rule):
    original=program(edit(BODY))
    fixed,record=normalization.normalize(original)
    assert fixed==program(BODY)
    assert record['applied'] and {e['rule'] for e in record['edits']}=={rule}
    assert record['raw_sha256']==hashlib.sha256(original.encode()).hexdigest()
    assert record['normalized_sha256']==hashlib.sha256(fixed.encode()).hexdigest()
    parsed=geometry.parse(original,THEOREM);canonical=geometry.parse(fixed,THEOREM)
    parsed.pop('normalization');canonical.pop('normalization')
    assert parsed==canonical
    compiled=geometry.compile_program(original,THEOREM)
    expected=geometry.compile_program(fixed,THEOREM)
    compiled['report'].pop('normalization');expected['report'].pop('normalization')
    assert compiled==expected
    assert normalization.normalize(original)==(fixed,record)
    twice,second=normalization.normalize(fixed)
    assert twice==fixed and not second['applied'] and not second['edits']
    # The edit ledger alone reproduces the normalized document, including line order.
    lines=original.splitlines()
    for edit in record['edits']:
        assert lines[edit['line']-1]==edit['before']
        lines[edit['line']-1]=edit['after']
    assert '\n'.join(lines)==fixed


def test_retain_alias_preserves_quoted_text_and_binding_prose():
    body='symbols = a, b\nretain condition :: A :: B remains unencoded.\ntarget same :: (eq a a)'
    raw=program(body,bindings='define B = a is explanation, not a program instruction.')
    fixed,record=normalization.normalize(raw)
    assert fixed==raw.replace('retain condition ::','retain = condition ::').replace('target same ::','target = same ::')
    assert len(record['edits'])==2
    parsed=geometry.parse(raw,'A')
    assert parsed['retained']==[{'label':'condition','excerpt':'A','reason':'B remains unencoded.'}]


@pytest.mark.parametrize('body',[
    'symbols = a, b\na, b\ntarget same :: (eq a a)',
    'symbols a, a\ntarget same :: (eq a a)',
    'symbols = a, a\ntarget same :: (eq a a)',
    'a, a\ntarget same :: (eq a a)',
    'symbols = a, b\nassume h :: (eq a b)\ntarget same :: (eq a a)',
    'symbols = a, b\ndefine a :: (add b 1)\ntarget same :: (eq a a)',
    'symbols = a, b\ntarget same :: (eq a a)\ndefine P :: (point 0 0)',
    'symbols = a, b\ntarget same :: (eq a a)\ntarget other :: (eq b b)',
    'symbols = a, b\npremise h :: (eq a b)\ntarget same :: (eq a a)',
])
def test_ambiguous_unknown_duplicate_and_incomplete_records_still_fail(body):
    with pytest.raises(ValueError):geometry.parse(program(body),'a and b are equal')


def test_no_inferred_source_excerpt_or_fixed_expression():
    for expression,quote in [('(eq a b)','a equals b'),
                             ('(eq a 0.5)','a and b are equal')]:
        raw=program('symbols = a, b\npremise relation :: '+expression+' :: '+quote+'\ntarget same :: (eq a a)')
        fixed,_=normalization.normalize(raw)
        assert expression+' :: '+quote in fixed
        with pytest.raises(ValueError):geometry.parse(raw,'a and b are equal')


@pytest.mark.parametrize('raw',[
    '# Decision\n\nNO_TOOL\n\n# Reason\n\nUnavailable.',
    program(BODY)+'\n```geometry-args\na, b\n```',
    program(BODY)+'\n# Geometry Program\n\n```geometry-args\na, b\n```',
    program(BODY.replace('define = A ::','define A ::')).replace('geometry-args','python'),
])
def test_nonprogram_or_ambiguous_container_is_never_rewritten(raw):
    fixed,record=normalization.normalize(raw)
    assert fixed==raw and not record['applied']


def test_normalizer_does_not_make_false_target_or_missing_guard_valid():
    raw=program('symbols = a, b\npremise relation :: (eq a b) :: a and b are equal\ntarget wrong :: (eq a (add b 1))')
    result=geometry.compile_program(raw,'a and b are equal')
    assert result['report']['target_numerator']=='a - b - 1'
    body=BODY.replace('premise = interior :: (inside P A B C) :: lies strictly inside the triangle\n','').replace('define = ','define ')
    with pytest.raises(ValueError,match='unproved construction denominator'):
        geometry.compile_program(program(body),THEOREM)
