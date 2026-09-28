"""Byte preservation and fail-closed authorization for block-local proof edits."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harnesses.block_local_completion.blocks import build_blocks, render_blocks, parse_issues, parse_and_apply


def issue_text(*records):
    return '<ISSUES>\n' + '\n'.join(
        f'<ISSUE id="{iid}" blocks="{ids}">\n{description}\n</ISSUE>'
        for iid, ids, description in records) + '\n</ISSUES>'


def patch_text(*records):
    return '<PATCHES>\n' + '\n'.join(
        f'<REPLACE blocks="{ids}" issues="{issues}">\n{replacement}\n</REPLACE>'
        for ids, issues, replacement in records) + '\n</PATCHES>'


@pytest.fixture
def source():
    return b'First paragraph.\n\nSecond paragraph.\n\nThird paragraph.\n\nFourth paragraph.\n\nFifth paragraph.\n'


def issues_for(bank, *records):
    return parse_issues(issue_text(*[(iid, ids, 'Needed claim; missing justification; used in next implication.')
                                   for iid, ids in records]), bank)


def assert_unchanged_ranges(result, original):
    final = result['proof_bytes']
    for span in result['audit']['unchanged_ranges']:
        before = original[span['start']:span['end']]
        after = final[span['result_start']:span['result_end']]
        assert before == after
        assert hashlib.sha256(before).hexdigest() == span['sha256']


def test_block_offsets_are_bytes_and_paragraph_separators_remain_unowned():
    data = '\r\n  Α πρώτη.\r\n\r\n두 번째 $x$.\r\n \t\r\n尾。\r\n\r\n'.encode()
    bank = build_blocks(data)
    assert bank == build_blocks(data)
    assert [b['block_id'] for b in bank['blocks']] == ['B0001', 'B0002', 'B0003']
    assert bank['blocks'][0]['start'] == 2
    assert bank['blocks'][0]['text'] == '  Α πρώτη.'
    for block in bank['blocks']:
        assert data[block['start']:block['end']] == block['text'].encode()
        assert hashlib.sha256(data[block['start']:block['end']]).hexdigest() == block['sha256']
    assert data[bank['blocks'][0]['end']:bank['blocks'][1]['start']] == b'\r\n\r\n'


@pytest.mark.parametrize('protected', [
    '$$\na+b\n\n=c\n$$',
    '\\[\na+b\n\n=c\n\\]',
    '\\begin{align*}\na+b\n\n&=c\n\\end{align*}',
    '\\[\n\\begin{aligned}\na+b\n\n&=c\n\\end{aligned}\n\\]',
    '```python\nprint("$$")\n\nprint("\\\\begin{unclosed}")\n```',
    '~~~~\n<code>\n\n$$ not math\n~~~~',
    '\\begin{verbatim}\n$ unclosed literal\n\n\\[\n\\end{verbatim}',
    '\\(\nx+y\n\n=z\n\\)', '$x\n\n+y$',
])
def test_blank_lines_inside_balanced_structures_never_split(protected):
    data = ('Before.\n\n' + protected + '\n\nAfter.\n').encode()
    bank = build_blocks(data)
    assert len(bank['blocks']) == 3
    assert bank['blocks'][1]['text'] == protected


@pytest.mark.parametrize('text', [
    '$$\nx\n\nunfinished', '\\[ x', '\\begin{align}\nx', '```python\nx',
    '\\end{align}', '\\begin{align}\nx\n\\end{equation}',
    '\\[\\begin{aligned}x\\]\\end{aligned}', '\\begin{align', '$x', '\\(x', '\\]',
])
def test_unmatched_or_crossed_structures_fail_before_editing(text):
    with pytest.raises(ValueError):
        build_blocks(text.encode())


def test_escaped_math_comments_and_inline_code_do_not_open_structures():
    data = b'Cost \\$5. Escaped \\\\[. `% $$ \\begin{bad}`\n% $$ ignored\n\nNext paragraph.'
    assert len(build_blocks(data)['blocks']) == 2


@pytest.mark.parametrize('data', [b'', b'\r\n \t\n', b'\xffbad'])
def test_empty_or_non_utf8_proofs_are_rejected(data):
    with pytest.raises(ValueError):
        build_blocks(data)


def test_render_shows_stable_ids_with_source_hash(source):
    bank = build_blocks(source)
    rendered = render_blocks(bank)
    assert f'SOURCE_SHA256: {bank["source_sha256"]}' in rendered
    assert '<BLOCK id="B0001">\nFirst paragraph.\n</BLOCK>' in rendered


def test_issue_permissions_are_exactly_target_plus_one_neighbor(source):
    bank = build_blocks(source)
    issues = issues_for(bank, ('I1', 'B0001'), ('I2', 'B0003'), ('I3', 'B0005'))
    assert issues[0]['allowed_block_ids'] == ['B0001', 'B0002']
    assert issues[1]['allowed_block_ids'] == ['B0002', 'B0003', 'B0004']
    assert issues[2]['allowed_block_ids'] == ['B0004', 'B0005']
    assert parse_issues('NO_ISSUES', bank) == parse_issues('NO_ISSUES\n', bank) == []


def test_neighbor_only_fix_is_allowed_without_replacing_target(source):
    bank = build_blocks(source)
    issues = issues_for(bank, ('I1', 'B0003'))
    replacement = 'Second paragraph with the required connection.'
    result = parse_and_apply(patch_text(('B0002', 'I1', replacement)), bank, source, issues)
    assert result['status'] == 'patched'
    assert result['proof_bytes'] == source.replace(b'Second paragraph.', replacement.encode())
    assert result['patches'][0]['allowed_block_ids'] == ['B0002', 'B0003', 'B0004']
    assert result['patches'][0]['changed'] is True
    assert_unchanged_ranges(result, source)


@pytest.mark.parametrize('blocks', ['B0001', 'B0005', 'B0001,B0002,B0003,B0004,B0005'])
def test_two_away_or_unrestricted_whole_proof_edit_is_forbidden(source, blocks):
    bank = build_blocks(source)
    issues = issues_for(bank, ('I1', 'B0003'))
    with pytest.raises(ValueError, match='one-neighbor'):
        parse_and_apply(patch_text((blocks, 'I1', 'Unauthorized proof rewrite.')), bank, source, issues)


def test_raw_replacement_math_and_crlf_survive_without_json_or_whitespace_rewrite():
    source = 'α.\r\n\r\nβ.\r\n\r\nγ.\r\n'.encode()
    bank = build_blocks(source)
    replacement = '\n  β: $\\frac{1}{2} < 1$ & "exact".\r\nSecond line.\n'
    result = parse_and_apply(patch_text(('B0002', 'I1', replacement)), bank, source, issues_for(bank, ('I1', 'B0002')))
    assert result['proof_bytes'] == source[:bank['blocks'][1]['start']] + replacement.encode() + source[bank['blocks'][1]['end']:]
    assert result['patches'][0]['replacement_text'] == replacement
    assert_unchanged_ranges(result, source)


def test_contiguous_range_can_include_existing_separators(source):
    bank = build_blocks(source)
    issues = issues_for(bank, ('I1', 'B0002'))
    result = parse_and_apply(patch_text(('B0001,B0002,B0003', 'I1', 'Three connected paragraphs.')), bank, source, issues)
    assert result['proof_bytes'] == b'Three connected paragraphs.\n\nFourth paragraph.\n\nFifth paragraph.\n'
    assert_unchanged_ranges(result, source)


def test_multiple_patches_apply_atomically_in_source_order(source):
    bank = build_blocks(source)
    issues = issues_for(bank, ('I1', 'B0001'), ('I2', 'B0005'))
    result = parse_and_apply(patch_text(('B0005', 'I2', 'Last repaired.'), ('B0001', 'I1', 'First repaired.')), bank, source, issues)
    assert [p['block_ids'] for p in result['patches']] == [['B0001'], ['B0005']]
    assert result['proof_bytes'] == source.replace(b'First paragraph.', b'First repaired.').replace(b'Fifth paragraph.', b'Last repaired.')
    assert_unchanged_ranges(result, source)
    json.dumps({key: value for key, value in result.items() if key != 'proof_bytes'})


def test_identical_replacement_is_recorded_as_unchanged(source):
    bank = build_blocks(source)
    result = parse_and_apply(patch_text(('B0002', 'I1', 'Second paragraph.')), bank, source, issues_for(bank, ('I1', 'B0002')))
    assert result['proof_bytes'] == source and result['audit']['changed'] is False
    assert result['patches'][0]['changed'] is False and result['patches'][0]['changed_byte_window'] is None


def test_issues_with_shared_target_require_one_combined_replacement(source):
    bank = build_blocks(source)
    issues = issues_for(bank, ('I1', 'B0002'), ('I2', 'B0002,B0003'))
    with pytest.raises(ValueError, match='combined'):
        parse_and_apply(patch_text(('B0001', 'I1', 'First repaired.'), ('B0004', 'I2', 'Fourth repaired.')), bank, source, issues)
    result = parse_and_apply(patch_text(('B0002,B0003', 'I1,I2', 'Both obligations addressed.')), bank, source, issues)
    assert result['status'] == 'patched'


@pytest.mark.parametrize('response', [
    'Some prose\nNO_ISSUES', 'NO_ISSUES\n\n', '<ISSUES>\n</ISSUES>',
    '<ISSUES>\n<ISSUE id="I1" blocks="B9999">Gap.</ISSUE>\n</ISSUES>',
    '<ISSUES>\n<ISSUE id="I1" blocks="B0001,B0001">Gap.</ISSUE>\n</ISSUES>',
    '<ISSUES>\n<ISSUE id="I1" blocks="B0002,B0001">Gap.</ISSUE>\n</ISSUES>',
    '<ISSUES>\n<ISSUE id="I1" blocks="B0001"> </ISSUE>\n</ISSUES>',
    '<ISSUES>\n<ISSUE id="I1" blocks="B0001">Gap.\n</ISSUES>',
    '<ISSUES>\n<ISSUE id="I1" blocks="B0001">Gap.</ISSUE>\n<ISSUE id="I1" blocks="B0002">Gap.</ISSUE>\n</ISSUES>',
])
def test_malformed_unknown_or_repeated_issues_rejected(source, response):
    with pytest.raises(ValueError):
        parse_issues(response, build_blocks(source))


@pytest.mark.parametrize('response', [
    '<PATCHES>\n<REPLACE blocks="B0002" issues="I1">inline proof</REPLACE>\n</PATCHES>',
    '<PATCHES>\n<REPLACE blocks="B0002" issues="I1">\n\n</REPLACE>\n</PATCHES>',
    '<PATCHES>\n<REPLACE blocks="B0002" issues="I1">\nProof.\n</PATCHES>',
    '<PATCHES>\n<REPLACE blocks="B0002" issues="I999">\nProof.\n</REPLACE>\n</PATCHES>',
    '<PATCHES>\n<REPLACE blocks="B0002,B0002" issues="I1">\nProof.\n</REPLACE>\n</PATCHES>',
    '<PATCHES>\n<REPLACE blocks="B0001,B0003" issues="I1">\nProof.\n</REPLACE>\n</PATCHES>',
    '<PATCHES>\n<REPLACE blocks="B0003,B0002" issues="I1">\nProof.\n</REPLACE>\n</PATCHES>',
    '<PATCHES>\n<REPLACE blocks="B0002" issues="I1">\n$$ unclosed\n</REPLACE>\n</PATCHES>',
])
def test_invalid_patch_response_is_rejected_without_modifying_original(source, response):
    original = bytes(source)
    bank = build_blocks(source)
    saved = deepcopy(bank)
    with pytest.raises(ValueError):
        parse_and_apply(response, bank, source, issues_for(bank, ('I1', 'B0002')))
    assert source == original and bank == saved


def test_missing_repeated_and_overlapping_issue_edits_fail_atomically(source):
    bank = build_blocks(source)
    issues = issues_for(bank, ('I1', 'B0002'), ('I2', 'B0003'))
    cases = [
        patch_text(('B0002', 'I1', 'Only one addressed.')),
        patch_text(('B0001', 'I1', 'First.'), ('B0002', 'I1,I2', 'Repeated issue.')),
        patch_text(('B0002', 'I1', 'First.'), ('B0002,B0003', 'I2', 'Overlap.')),
    ]
    for text in cases:
        with pytest.raises(ValueError):
            parse_and_apply(text, bank, source, issues)
    assert source.startswith(b'First paragraph.')


def test_stale_source_altered_bank_and_forged_neighborhood_fail(source):
    bank = build_blocks(source)
    issues = issues_for(bank, ('I1', 'B0003'))
    text = patch_text(('B0003', 'I1', 'Repaired.'))
    with pytest.raises(ValueError, match='Stale'):
        parse_and_apply(text, bank, source + b' changed', issues)
    altered = deepcopy(bank)
    altered['blocks'][0]['start'] += 1
    with pytest.raises(ValueError, match='Stale'):
        parse_and_apply(text, altered, source, issues)
    issues[0]['allowed_block_ids'].append('B0005')
    with pytest.raises(ValueError, match='permission changed'):
        parse_and_apply(text, bank, source, issues)


def test_cannot_repair_locally_is_an_explicit_unchanged_result(source):
    bank = build_blocks(source)
    result = parse_and_apply('CANNOT_REPAIR_LOCALLY', bank, source, issues_for(bank, ('I1', 'B0003')))
    assert result['status'] == 'cannot_repair_locally'
    assert result['proof_bytes'] == source and result['patches'] == []
    assert result['audit']['changed'] is False
    assert_unchanged_ranges(result, source)


def test_second_stage_must_bind_to_fresh_intermediate_snapshot(source):
    bank = build_blocks(source)
    first = parse_and_apply(patch_text(('B0002', 'I1', 'A longer first local repair.')), bank, source,
                            issues_for(bank, ('I1', 'B0002')))
    with pytest.raises(ValueError, match='Stale'):
        parse_and_apply('CANNOT_REPAIR_LOCALLY', bank, first['proof_bytes'], issues_for(bank, ('I1', 'B0002')))
    second_bank = build_blocks(first['proof_bytes'])
    with pytest.raises(ValueError, match='different proof snapshot'):
        parse_and_apply('CANNOT_REPAIR_LOCALLY', second_bank, first['proof_bytes'], issues_for(bank, ('I1', 'B0002')))
    second = parse_and_apply(patch_text(('B0003', 'I1', 'Audit follow-up repair.')), second_bank, first['proof_bytes'],
                             issues_for(second_bank, ('I1', 'B0003')))
    assert b'A longer first local repair.' in second['proof_bytes']
    assert b'Audit follow-up repair.' in second['proof_bytes']
    assert_unchanged_ranges(second, first['proof_bytes'])


def test_separate_patches_cannot_wrap_untouched_blocks_in_math(source):
    bank = build_blocks(source)
    issues = issues_for(bank, ('I1', 'B0001'), ('I2', 'B0005'))
    with pytest.raises(ValueError, match='Unmatched'):
        parse_and_apply(patch_text(('B0001', 'I1', '$$ opens'), ('B0005', 'I2', 'closes $$')), bank, source, issues)


def test_overlapping_neighbor_permissions_do_not_force_unrelated_issues_to_merge(source):
    bank = build_blocks(source)
    issues = issues_for(bank, ('I1', 'B0002'), ('I2', 'B0004'))
    result = parse_and_apply(patch_text(('B0001', 'I1', 'First connection.'), ('B0005', 'I2', 'Last connection.')),
                             bank, source, issues)
    assert len(result['patches']) == 2
    assert_unchanged_ranges(result, source)
