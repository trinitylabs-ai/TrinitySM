"""Container recovery preserves field values and never repairs mathematical input."""
import pytest

from . import root_normalization as normalization, root_classification as roots
from . import root_workflow as workflow, proof_harness as harness, matched_tools
from .test_root_classification import program, body


@pytest.mark.parametrize('label', ['root-args', 'lisp', ''])
@pytest.mark.parametrize('wrapper', ['', 'real_root_classification', 'root_args', 'root-args'])
@pytest.mark.parametrize('closing_newline', ['', '\n'])
def test_observed_containers_preserve_compiled_math(label, wrapper, closing_newline):
    content = body('(sub (pow z 3) (mul 3 z))', mode='stationary_points')
    canonical = '```root-args\n'+content+'\n```'
    alternate = '\n'.join('  '+line.replace(' = ', ' ') for line in content.splitlines())
    if wrapper:
        alternate = '('+wrapper+'\n'+alternate+closing_newline+')'
    raw = '```'+label+'\n'+alternate+'\n```'
    fixed, record = normalization.normalize(raw)
    assert record['applied'] and record['normalized_program'] == fixed
    assert normalization.normalize(fixed)[0] == fixed
    assert not normalization.normalize(fixed)[1]['applied']
    expected = roots.compile_program(canonical)
    actual = roots.compile_program(raw)
    assert actual['report'].pop('normalization') == record
    assert actual == expected
    expected_result, actual_result = roots.compute(canonical), roots.compute(raw)
    assert actual_result.pop('compilation_sha256') != expected_result.pop('compilation_sha256')
    assert actual_result == expected_result


def test_values_and_bindings_are_retained_verbatim():
    content = ('variable = theta\ndefine = objective :: (div (sub (pow theta 2) 1) (add theta 3))\n'
        'interval = (right_open -2 2)\nmode = roots\nexpression = objective')
    text = program(content, 'Keep these source bindings exactly as written.')
    altered = text.replace('```root-args\n', '```lisp\n(root_args\n').replace(' = ', ' ')
    altered = altered[:-3]+')\n```'
    expected, actual = roots.compile_program(text), roots.compile_program(altered)
    record = actual['report'].pop('normalization')
    assert actual == expected
    assert [line for line in record['normalized_program'].splitlines()[1:-1] if line] == content.splitlines()


def test_canonical_crlf_is_unchanged():
    raw = ('```root-args\n'+body('z')+'\n```').replace('\n', '\r\n')
    fixed, record = normalization.normalize(raw)
    assert fixed == raw and not record['applied']


@pytest.mark.parametrize('content', [
    '(root_args\nvariable = z',
    '(root_args\n'+body('(sub (pow z 2) 1)'),
    '(invented_wrapper\nvariable = z\n)',
    '(root_args\n(root_args\nvariable = z\n)\n)',
    'variable = z\nunknown = z',
    'variable = z\n```\n```root-args\nexpression = z',
    'variable = z\n# extra prose',
])
def test_ambiguous_or_extra_records_are_rejected(content):
    with pytest.raises(ValueError):
        normalization.normalize('```lisp\n'+content+'\n```')


@pytest.mark.parametrize('raw', [
    '```python\nvariable = z\n```',
    'explanation\n```lisp\nvariable = z\n```',
    '```lisp\nvariable = z\n```\nextra explanation',
    '```lisp\nvariable = z',
])
def test_unrecognized_or_incomplete_fence_is_not_guessed(raw):
    with pytest.raises(ValueError):
        normalization.normalize(raw)


@pytest.mark.parametrize('content', [
    body('(sub (pow z 2) 1'),
    body('(sub (pow z 2) 1))'),
    body('(add z unknown)'),
    body('(sin z)'),
    body('z', mode='stationary_points').replace('function =', 'expression ='),
    body('z').replace('interval = (open -2 2)', 'interval = (open 2 -2)'),
    body('z').replace('variable = z', 'variable = z\nvariable = z'),
    body('z').replace('variable = z', 'variable == z'),
    body('z').replace('variable = z', 'variable'),
    body('z').replace('mode = roots', 'mode = roots\ninterval = (open -1 1)'),
])
def test_normalization_never_repairs_invalid_mathematics_or_schema(content):
    with pytest.raises(ValueError):
        roots.compile_program('```lisp\n'+content+'\n```')


def test_cancelled_denominator_domain_is_still_enforced():
    raw = '```lisp\n(root_args\n'+body('(div (mul z (sub z 1)) z)')+'\n)\n```'
    with pytest.raises(ValueError):
        roots.compute(raw)


def test_production_still_requires_bindings_and_preserves_no_tool():
    raw = '```lisp\n'+body('z')+'\n```'
    assert not workflow.inspect(raw, 'source theorem', harness.Config())['parser_valid']
    assert not workflow.inspect(program(body('z'), ''), 'source theorem', harness.Config())['parser_valid']
    assert roots.compile_program('# Decision\nNO_TOOL\n# Reason\nUnsupported task.') == {
        'call_requested': False, 'reason': 'Unsupported task.'}


def test_replay_binds_normalization_provenance():
    raw = program(body('(sub (pow z 2) 1)')).replace('```root-args', '```lisp')
    saved = roots.compute(raw)
    assert workflow.replay(raw, saved, harness.Config()) == saved
    # Even an equivalent container changes the recorded source and requires a
    # fresh compilation/audit; it cannot inherit the old certificate silently.
    with pytest.raises(ValueError, match='replay differs'):
        workflow.replay(raw.replace('```lisp', '```'), saved, harness.Config())


def test_public_tool_uses_same_normalization_and_replay(tmp_path):
    raw = '```lisp\n(root_args\n'+body('(sub (pow z 2) 1)')+')\n```'
    result = matched_tools.run(operation=roots.OPERATION, arguments_markdown=raw, output=tmp_path/'tool')
    assert result['verdict'] == 'ROOT_CLASSIFICATION_VERIFIED'
    assert result['root_compilation']['report']['normalization']['applied']
    assert matched_tools.replay(operation=roots.OPERATION, arguments_markdown=raw, saved_result=result) == result
