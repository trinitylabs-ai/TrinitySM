"""Run-bound label corrections through real frozen parsers, without inference."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from test_public_reproduction import ROOT, load, pipeline, write

policy = pipeline.runtime_policy
ENGINE = ROOT / 'harnesses/imo_proof_pipeline/releases/1.12.0/engine/source'
FUSION = '''FUSION_REPAIR_NEEDED
verdict: REPAIR_NEEDED
reviewer_1_assessment: NO_DEFECT_REPORTED | The reviewer failed to identify the sign error in the slope calculation.
reviewer_2_assessment: NO_DEFECT_REPORTED | The reviewer failed to identify the sign error in the slope calculation.
reviewer_3_assessment: NO_UNCLOSED_OBLIGATION_FOUND | The reviewer failed to identify the sign error in the slope calculation.
decisive_location: The slope calculation in Section 3.
failed_obligation: The claimed positive slope has the wrong sign.
independent_validation: Substituting the given coordinates yields a negative slope.
impact_on_proof: The perpendicularity conclusion is not established.
repair_scope: STRUCTURAL
resolver_brief: Correct the slope signs in the existing coordinate system.
preservable_material: The earlier angle calculation.
END_FUSION_REPAIR_NEEDED'''
LAZY = r'''BEGIN_REPAIR_AUDIT
CONCLUSION_ACTION: PRESERVE
ORIGINAL_CLASSIFICATION: The point $D$ and angle $\theta = \alpha + \pi$ satisfy the required conditions.
REPAIRED_CLASSIFICATION: The point $D$ and angle $\theta = \alpha$ satisfy the required conditions.
CHANGE_BASIS: RIGOROUS_DERIVATION
CHANGE_JUSTIFICATION: The original choice gives D = A; the supplied derivation changes the angle to obtain a distinct point.
END_REPAIR_AUDIT
BEGIN_REPAIRED_PROOF
The submitted proof text is preserved verbatim, including $\theta = \alpha$.
END_REPAIRED_PROOF'''

# Import the same aliases used by generation workers. No model client is called;
# also reject accidental network access in these parser integration tests.
PARSE = '''
import json, socket, sys
def no_network(*args, **kwargs):
    raise AssertionError('Unexpected network request')
socket.socket.connect = no_network
socket.socket.connect_ex = no_network
socket.create_connection = no_network
value = sys.stdin.buffer.read().decode()
try:
    if sys.argv[1] == 'fusion':
        from cognitive_well_harness_v0_3_53_fusion_20260823.run import parse_task_output
        outcomes = ('NO_FIRST_BREAK', 'NO_ADVERSARIAL_BREAK', 'NO_UNCLOSED_OBLIGATION_FOUND')
        if len(sys.argv) > 2:
            outcomes = ('FIRST_BREAK', *outcomes[1:])
        task = {'reviewer_sources': {f'reviewer_{i}': {'outcome': v}
                                    for i, v in enumerate(outcomes, 1)}}
        result = parse_task_output(value, task)
    else:
        from cognitive_well_harness_v0_3_47_lazy_in_place_expansion_20260823.lazy_expansion import parse_lazy_expansion_output
        result = parse_lazy_expansion_output(value)
except ValueError as error:
    result = {'valid': False, 'error': str(error)}
print(json.dumps(result))
'''


def base_environment():
    environment = {k: v for k, v in os.environ.items()
                   if not k.startswith(('GPU0_BULK_', 'WORKSHOP_LABEL_'))}
    environment.update(PYTHONPATH=str(ENGINE), PYTHONDONTWRITEBYTECODE='1')
    return environment


def capture(root):
    write(root / 'harness_release.json', {
        'release_sha256': policy.sha(ENGINE.parents[1] / 'release.json'),
        'label_recovery': policy.binding('1.12.0')})
    policy.prepare(root, ENGINE)
    return policy.environment(root, base_environment())


@pytest.fixture
def bound(tmp_path):
    root = tmp_path / 'run'
    return root, capture(root)


def parse(text, kind, environment, *args):
    result = subprocess.run([sys.executable, '-B', '-c', PARSE, kind, *args],
        input=text, text=True, capture_output=True, env=environment, timeout=20)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


@pytest.mark.parametrize('kind,text', [('fusion', FUSION), ('lazy', LAZY)], ids=['fusion', 'lazy'])
@pytest.mark.parametrize('newline', ['\n', '\r\n'])
def test_explicit_labels_recover_with_original_text_and_hashes(bound, kind, text, newline):
    root, environment = bound
    text = text.replace('\n', newline)
    assert not parse(text, kind, base_environment())['valid']
    result = parse(text, kind, environment)
    assert result['valid']
    receipt = result['mechanical_label_recovery']
    import hashlib
    digest = lambda value: hashlib.sha256(value.encode()).hexdigest()
    assert receipt['original_response_sha256'] == digest(text)
    assert receipt['model_calls'] == 0 and not receipt['mathematical_text_changed']
    normalized = text
    if kind == 'fusion':
        for index, old in ((1, 'NO_DEFECT_REPORTED'), (2, 'NO_DEFECT_REPORTED'),
                           (3, 'NO_UNCLOSED_OBLIGATION_FOUND')):
            normalized = normalized.replace(f'reviewer_{index}_assessment: {old}',
                f'reviewer_{index}_assessment: REVIEWER_MISSED_DEFECT')
        assert result['final'] == text
        assert result['normalized_final'] == normalized.replace('\r\n', '\n')
        assert result['outcome'] == 'REPAIR_NEEDED'
    else:
        normalized = text.replace('CONCLUSION_ACTION: PRESERVE', 'CONCLUSION_ACTION: CHANGE')
        assert result['proof'] == text.split('BEGIN_REPAIRED_PROOF')[1].split('END_REPAIRED_PROOF')[0].strip()
        assert result['raw_sha256'] == digest(text)
        assert result['conclusion_action'] == 'CHANGE'
    assert receipt['normalized_response_sha256'] == digest(normalized)
    assert json.loads((root / 'label_recoveries' / (digest(text.strip()) + '.json')).read_text()) == receipt
    strict = parse(normalized, kind, base_environment())
    assert strict['valid'] and 'mechanical_label_recovery' not in strict


@pytest.mark.parametrize('reason', [
    'The reviewer found no defect.',
    'The reviewer failed to identify the correct slope calculation.',
    'The reviewer may have failed to identify a sign error.',
    'The reviewer failed to identify a possible error, if the coordinates apply.',
])
def test_ambiguous_fusion_remains_invalid(bound, reason):
    text = FUSION.replace('The reviewer failed to identify the sign error in the slope calculation.', reason)
    assert not parse(text, 'fusion', bound[1])['valid']


def test_source_reviewer_semantics_still_enforced(bound):
    result = parse(FUSION, 'fusion', bound[1], 'conflicting-source')
    assert not result['valid']
    assert any('incompatible with source outcome' in error for error in result['errors'])


@pytest.mark.parametrize('text', [
    LAZY.replace('RIGOROUS_DERIVATION', 'NONE'),
    LAZY.replace('RIGOROUS_DERIVATION', 'HEURISTIC'),
    LAZY.replace('The original choice gives D = A; the supplied derivation changes the angle to obtain a distinct point.', 'NONE'),
    LAZY.replace('CONCLUSION_ACTION: PRESERVE', 'CONCLUSION_ACTION: PRESERVE\nCONCLUSION_ACTION: CHANGE'),
])
def test_unjustified_or_ambiguous_lazy_change_remains_invalid(bound, text):
    assert not parse(text, 'lazy', bound[1])['valid']


@pytest.mark.parametrize('kind,text', [('fusion', FUSION), ('lazy', LAZY)], ids=['fusion', 'lazy'])
def test_empty_truncated_and_repeated_outputs_remain_invalid(bound, kind, text):
    for malformed in ('', text.rsplit('\n', 1)[0], text + '\n' + text):
        result = parse(malformed, kind, bound[1])
        assert not result['valid']
        assert 'mechanical_label_recovery' not in result


@pytest.mark.parametrize('single_gpu', [False, True])
def test_policy_survives_nested_workers_resetting_pythonpath(bound, single_gpu):
    root, environment = bound
    if single_gpu:
        adapter = str(ROOT / 'harnesses/single_gpu/client_compat')
        environment.update(GPU0_BULK_URL='http://127.0.0.1:1', GPU0_BULK_ENGINE=str(ENGINE))
        environment['PYTHONPATH'] = adapter + os.pathsep + environment['PYTHONPATH']
    script = '''
import json, os, subprocess, sys
env = dict(os.environ, PYTHONPATH=sys.argv[1])
child = subprocess.run([sys.executable, '-B', '-c', sys.argv[2], 'lazy'],
                       input=sys.stdin.read(), text=True, capture_output=True, env=env)
assert child.returncode == 0, child.stderr
assert json.loads(child.stdout)['valid'], child.stdout
if os.environ.get('GPU0_BULK_URL'):
    assert any(cls.__module__ == 'sitecustomize' for cls in subprocess.Popen.__mro__)
print(child.stdout)
'''
    result = subprocess.run([sys.executable, '-B', '-c', script, str(ENGINE), PARSE],
        input=LAZY, text=True, capture_output=True, env=environment, timeout=20)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)['mechanical_label_recovery']['model_calls'] == 0


def test_legacy_run_is_not_upgraded_or_requeued(tmp_path):
    write(tmp_path / 'harness_release.json', {'release_sha256': 'legacy'})
    environment = dict(base_environment(), WORKSHOP_LABEL_RECOVERY='/unrelated/run.json')
    original = (tmp_path / 'harness_release.json').read_bytes()
    policy.prepare(tmp_path, ENGINE)
    assert policy.saved(tmp_path) is None
    environment = policy.environment(tmp_path, environment)
    assert 'WORKSHOP_LABEL_RECOVERY' not in environment
    assert not parse(LAZY, 'lazy', environment)['valid']
    assert (tmp_path / 'harness_release.json').read_bytes() == original
    assert sorted(p.name for p in tmp_path.iterdir()) == ['harness_release.json']


def test_captured_policy_survives_checkout_changes_and_rejects_tampering(bound, monkeypatch):
    root, environment = bound
    monkeypatch.setattr(policy, 'SOURCES', {name: Path('/missing') for name in policy.SOURCES})
    assert policy.saved(root)
    assert parse(LAZY, 'lazy', policy.environment(root, base_environment()))['valid']
    with (root / 'label_runtime/label_recovery.py').open('a') as handle:
        handle.write('\n# altered snapshot\n')
    with pytest.raises(ValueError, match='Captured label recovery code changed'):
        policy.environment(root, base_environment())
    failed = subprocess.run([sys.executable, '-B', '-c', 'print("should not start")'],
        text=True, capture_output=True, env=environment, timeout=20)
    assert failed.returncode != 0 and 'should not start' not in failed.stdout


@pytest.mark.parametrize('legacy', [False, True])
def test_new_run_and_resume_bind_the_same_snapshot(tmp_path, monkeypatch, legacy):
    monkeypatch.setitem(sys.modules, 'pipeline', pipeline)
    scheduler = load('test_labels_queue', 'harnesses/proof_workshop/problem_queue.py')
    statements, root = tmp_path / 'statements', tmp_path / 'run'
    write(statements / 'synthetic.json', {'problem_id': 'synthetic', 'problem': 'Prove the claim.'})
    monkeypatch.setattr(scheduler, 'run_sequence', lambda *args: 0)
    if legacy:
        monkeypatch.setattr(policy, 'binding', lambda _: None)
    args = ['--release', '1.12.0', '--problem-dir', str(statements),
            '--output-dir', str(root), '--dry-run']
    assert scheduler.main(args) == 0
    identity = (root / 'harness_release.json').read_bytes()
    assert bool(policy.saved(root)) is not legacy
    monkeypatch.setattr(policy, 'binding', lambda _: pytest.fail('Resume used current policy'))
    assert scheduler.main([*args, '--resume']) == 0
    assert (root / 'harness_release.json').read_bytes() == identity


def test_fusion_worker_saves_receipt_without_a_model_repair_call(bound):
    root, environment = bound
    script = '''
import json, sys
from pathlib import Path
from cognitive_well_harness_v0_3_53_fusion_20260823 import run
raw = sys.stdin.read()
calls = []
def generation(**kwargs):
    calls.append(kwargs['stage'])
    assert calls == ['fusion'], 'Unexpected model repair call'
    return {'text': raw, 'reasoning': 'Existing reasoning.',
            'metadata': {'finish_reason': 'stop'}}
run._base.run_openai_chat_generation = generation
task = dict(problem='Prove the claim.', proof='The submitted proof.',
            reviewer_1='No first break.', reviewer_2='No adversarial break.',
            reviewer_3='No unclosed obligation.', model_name='test', endpoint='unused',
            temperature=0.4, gpu=0, problem_number=1, candidate_id='t07_r01', seed=1,
            reviewer_sources={f'reviewer_{i}': {'outcome': v} for i, v in enumerate(
                ('NO_FIRST_BREAK', 'NO_ADVERSARIAL_BREAK', 'NO_UNCLOSED_OBLIGATION_FOUND'), 1)})
output = Path(sys.argv[1])
result = run.run_task(output_dir=output, task=task)
saved = json.loads((run.task_output_dir(output, task) / 'result.json').read_text())
assert saved == result
receipt = saved['parsed']['mechanical_label_recovery']
assert saved['final_normalization']['policy'] == receipt['policy']
assert saved['final_normalization']['model_final_sha256'] == receipt['original_response_sha256']
assert saved['final_sha256'] == receipt['normalized_final_sha256']
assert calls == ['fusion']
'''
    result = subprocess.run([sys.executable, '-B', '-c', script, str(root / 'synthetic-stage')],
        input=FUSION, text=True, capture_output=True, env=environment, timeout=20)
    assert result.returncode == 0, result.stderr


def test_offline_collection_policy_is_scoped_to_its_run(bound):
    root, environment = bound
    script = '''
import importlib.util, sys
spec = importlib.util.spec_from_file_location('policy', sys.argv[1])
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)
from pathlib import Path
root = Path(sys.argv[2])
# Simulate a prior legacy collection importing aliases before policy activation.
from cognitive_well_harness_v0_3_53_fusion_20260823 import run as fusion_run
strict_alias = fusion_run.parse_fusion
with policy.validation(root):
    assert fusion_run.parse_fusion is not strict_alias
    from cognitive_well_harness_v0_3_47_lazy_in_place_expansion_20260823.lazy_expansion import parse_lazy_expansion_output as parse
    value = sys.stdin.read()
    assert parse(value)['valid']
try:
    parse(value)
except ValueError:
    pass
else:
    raise AssertionError('Normalization leaked into legacy collection')
with policy.validation(root):
    assert parse(value)['valid']
assert not (root / 'label_recoveries').exists(), 'Read-only validation wrote receipts'
'''
    result = subprocess.run([sys.executable, '-B', '-c', script,
        str(ROOT / 'harnesses/proof_workshop/runtime_policy.py'), str(root)],
        input=LAZY, text=True, capture_output=True, env=base_environment(), timeout=20)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize('import_when', ['before', 'during'])
def test_collection_leaves_other_engine_modules_strict(bound, import_when):
    from test_voter_prose_recovery import prose
    root, _ = bound
    script = '''
import json, socket, sys
from pathlib import Path
def no_network(*args, **kwargs):
    raise AssertionError('Unexpected network request')
socket.socket.connect = socket.create_connection = no_network
sys.path.insert(0, sys.argv[1])
from test_public_reproduction import pipeline
engine = pipeline.IMPLEMENTATION / 'releases/1.12.0/engine/source'
legacy_engine = pipeline.IMPLEMENTATION / 'releases/1.7.0/engine/source'
sys.path.insert(0, str(legacy_engine))
root = Path(sys.argv[2])
values = json.load(sys.stdin)
def load_legacy():
    from cognitive_well_harness_v0_3_53_fusion_20260823 import protocol
    assert Path(protocol.__file__).resolve().is_relative_to(legacy_engine)
    return protocol, protocol.parse_fusion
if sys.argv[3] == 'before':
    legacy, strict_alias = load_legacy()
voter = pipeline.voter_module('1.12.0')
with pipeline.runtime_policy.validation(root):
    if sys.argv[3] == 'during':
        legacy, strict_alias = load_legacy()
    assert legacy.parse_fusion is strict_alias
    assert not getattr(strict_alias, '_label_recovery_dispatch', False)
    assert not strict_alias(values['fusion'])['valid']
    assert voter.parse(values['comparison'])['winner_label'] == 'A'
    record = pipeline.runtime_policy.saved(root)
    adapter = sys.modules['workshop_label_recovery_' + record['binding']['files']['label_recovery.py']]
    try:
        adapter.patch_module(legacy, engine)
    except ValueError as error:
        assert 'outside the pinned engine' in str(error)
    else:
        raise AssertionError('Patching an unrelated engine bypassed the integrity check')
assert legacy.parse_fusion is strict_alias
try:
    voter.parse(values['comparison'])
except (ValueError, AssertionError):
    pass
else:
    raise AssertionError('Recovery leaked outside the saved run context')
assert not (root / 'label_recoveries').exists()
'''
    result = subprocess.run([sys.executable, '-B', '-c', script,
        str(ROOT / 'tests'), str(root), import_when],
        input=json.dumps(dict(fusion=FUSION, comparison=prose())), text=True,
        capture_output=True, env=base_environment(), timeout=20)
    assert result.returncode == 0, result.stderr
