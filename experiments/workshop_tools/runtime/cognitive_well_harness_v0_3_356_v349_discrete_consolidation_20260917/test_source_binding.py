"""Exact source references aid transcription, never mathematical acceptance."""
import json

import pytest

from . import source_binding as source, geometry_program as geometry
from .test_geometry_program import program, THEOREM, BODY


def test_inventory_covers_nonwhitespace_exactly_with_bounded_unicode_offsets():
    theorem = '\n  A\u03b1 and B.\r\n\r\n' + ('longword '*400) + '\n' + ('x'*1800)
    record = source.inventory(theorem)
    assert record == source.inventory(theorem)
    assert not record['semantic_units'] and not record['source_semantics_verified']
    covered = set()
    for index, span in enumerate(record['spans'], 1):
        assert span['id'] == f'S{index:04d}'
        assert theorem[span['start']:span['end']] == span['excerpt']
        assert source.sha(span['excerpt']) == span['excerpt_sha256']
        assert 0 < len(span['excerpt']) <= source.MAX_SPAN_CHARS
        covered.update(range(span['start'],span['end']))
        resolved, receipt = source.resolve('@source:'+span['id'],theorem,label='given')
        assert resolved == span['excerpt'] and receipt['theorem_sha256'] == source.sha(theorem)
    assert all(i in covered for i,c in enumerate(theorem) if not c.isspace())
    assert '@source:S0001' in source.render(record)


@pytest.mark.parametrize('opening,closing',list(source.DELIMITERS.items())+[('','')])
def test_literal_and_reference_delimiters_preserve_exact_spelling(opening,closing):
    theorem = r'Assume \(a=b\). Then the conclusion follows.'
    excerpt = r'\(a=b\)'
    result, receipt = source.resolve(opening+excerpt+closing,theorem,label='given')
    assert result == excerpt and receipt['excerpt_sha256'] == source.sha(excerpt)
    result, receipt = source.resolve(opening+'@source:S0001'+closing,theorem,label='given')
    assert result == theorem and receipt['resolution'] == 'source_id'


def test_literal_quotes_belonging_to_original_source_take_precedence():
    theorem = 'The text says "a equals b".'
    resolved, receipt = source.resolve('"a equals b"',theorem,label='given')
    assert resolved == '"a equals b"' and receipt['resolution'] == 'literal'
    resolved, receipt = source.resolve('a\t equals  b',theorem,label='given')
    assert resolved == 'a equals b'


@pytest.mark.parametrize('value',[
    'a equals b', '"a equals b"', '@source:S9999', '@source:../other',
    r'\(a=b\)', 'a=b', '"a and b are equal', '',
])
def test_no_paraphrase_latex_rewrite_unknown_id_or_external_lookup(value):
    with pytest.raises(ValueError,match='source'):
        source.resolve(value,'a and b are equal.',label='given')


def test_id_and_exact_quotation_compile_to_identical_mathematics():
    original = geometry.compile_program(program(BODY),THEOREM)
    with_ids = BODY.replace(':: lies strictly inside the triangle',':: @source:S0001').replace(
        ':: The scalar product equals one.',':: @source:S0001')
    resolved = geometry.compile_program(program(with_ids),THEOREM)
    assert resolved['system'] == original['system']
    for key in ['angle_encodings','construction_obligations','guard_derivations','equations',
                'target_numerator','target_denominator','target_residual']:
        assert resolved['report'][key] == original['report'][key]
    assert not resolved['report']['source_semantics_verified']
    bindings = resolved['report']['source_bindings']
    assert len(bindings)==2 and all(b['resolution']=='source_id' for b in bindings)
    assert all(b['excerpt']==THEOREM and b['theorem_sha256']==source.sha(THEOREM) for b in bindings)
    changed = geometry.compile_program(program(with_ids),THEOREM+' Additional text.')
    assert changed['report']['source_bindings'] != bindings


def test_resolved_source_does_not_fix_false_math_or_missing_domain_condition():
    body = ('symbols = a, b\npremise = given :: (eq a b) :: @source:S0001\n'
            'target = wrong :: (eq a (add b 1))')
    result = geometry.compile_program(program(body),'a and b are equal.')
    assert result['report']['target_numerator']=='a - b - 1'
    assert result['report']['source_semantics']=='MODEL_AUDIT_REQUIRED'
    without_interior = BODY.replace('premise = interior :: (inside P A B C) :: lies strictly inside the triangle\n','')
    with pytest.raises(ValueError,match='unproved construction denominator'):
        geometry.compile_program(program(without_interior),THEOREM)


def test_retain_resolves_same_source_with_binding_receipt():
    body = 'symbols = a\nretain = given :: @source:S0001 :: Retained for the natural proof.\ntarget = same :: (eq a a)'
    parsed = geometry.parse(program(body),'a is real.')
    assert parsed['retained'][0]['excerpt']=='a is real.'
    assert parsed['source_bindings'][0]['submitted']=='@source:S0001'


def test_source_failure_identifies_bad_text_and_gives_mechanical_repair():
    with pytest.raises(ValueError) as error:
        source.resolve('first scalar equals second','The two scalars are equal.',label='given')
    assert 'first scalar equals second' in str(error.value)
    assert '@source:S0001' in str(error.value) and 'Do not paraphrase' in str(error.value)
