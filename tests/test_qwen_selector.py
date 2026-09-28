"""Qwen-only execution, captured policy and legacy replay; no model calls."""
import json
import os
from pathlib import Path
import subprocess
import sys
import threading

import pytest

from cross_lane_replay import response, sample
from test_public_reproduction import ROOT, pipeline, write
from test_stage_label_recovery import ENGINE, base_environment, capture

policy = pipeline.selector_policy


def setup(root, n=4):
    capture(root)
    identity = pipeline.read(root / 'harness_release.json')
    identity['final_selector'] = policy.binding('1.12.0')
    write(root / 'harness_release.json', identity)
    policy.prepare(root, ENGINE)
    voter = policy.module(root)
    candidates = []
    for i in range(n):
        proof = root / f'lane{i}.md'
        proof.write_text(f'Proof {i}.\n')
        candidates.append(dict(candidate_id=f'lane{i}', proof_path=str(proof),
            proof_sha256=voter.digest(proof.read_bytes().strip()), selected_stage='refinement_2',
            grade='DO_NOT_PASS_GRADE'))
    runtime = dict(raw_seed_offset=0, seed_namespace=voter.DEFAULT_NAMESPACE, model_timeout_sec=600,
        gemma_endpoint='http://127.0.0.1:8030/v1', qwen_endpoint='http://127.0.0.1:8027/v1')
    directory = root / 'cross_lane_voter/P/portfolio'
    voter.prepare(directory, 'P', 'Prove X.', candidates, runtime, identity['release_sha256'])
    expected = dict(problem_id='P', problem='Prove X.', candidates=candidates, runtime=runtime,
                    release_sha256=identity['release_sha256'])
    return voter, directory, expected


@pytest.mark.parametrize('n', [1, 2, 3, 4])
def test_only_qwen_executes_with_complete_pairs_and_no_duplicate_resume(tmp_path, n):
    voter, directory, expected = setup(tmp_path, n)
    cfg, manifest, tasks = voter.verify(directory, expected=expected)
    assert set(cfg['auditors']) == {'qwen'}
    assert len(tasks) == n * (n - 1)
    assert manifest['comparison_runtime']['workers_per_model'] == {'qwen': 12}
    assert manifest['comparison_runtime']['calls_per_model'] == len(tasks)
    assert 'DO_NOT_PASS_GRADE' not in ''.join(p.read_text() for p in directory.rglob('*.md'))
    calls = []
    result = voter.run(directory, lambda **kw: calls.append(kw) or response(kw))
    assert len(calls) == len(tasks)
    assert all('qwen' in call['model'].lower() for call in calls)
    assert result['voting_models'] == ['qwen'] and 'gemma' not in result['summaries']
    summary = result['summaries']['qwen']
    assert summary == result['summaries']['combined']
    assert summary['winner'] == manifest['seed_derived_candidate_order'][0]
    assert summary['complete'] and summary['expected_calls'] == len(tasks)
    assert set(summary['votes'].values()) == {n - 1}
    voter.run(directory, lambda **kw: pytest.fail('Resume repeated inference'))
    assert voter.collect(directory, expected=expected)['state'] == 'completed'


def test_qwen_keeps_existing_inputs_seeds_and_audit_remains_dual_model(tmp_path):
    voter, directory, expected = setup(tmp_path)
    legacy = pipeline.voter_module('1.12.0')
    legacy.prepare(tmp_path / 'legacy', **expected)
    _, _, old_tasks = legacy.verify(tmp_path / 'legacy')
    assert len(old_tasks) == 24
    assert voter.verify(directory)[2] == [t for t in old_tasks if t['model_key'] == 'qwen']
    for name in ('AUDIT_PROMPT.md', 'BF_CUE.md', 'timeout_policy.json'):
        assert (directory / name).read_bytes() == (tmp_path / 'legacy' / name).read_bytes()
    assert set(legacy.MODELS) == set(pipeline.audit_module('1.12.0').MODELS) == {'gemma', 'qwen'}
    assert voter.parse(sample().replace('Winner: A', 'Winner: Proof A'))['winner_label'] == 'A'


def test_qwen_uses_twelve_workers(tmp_path):
    voter, directory, _ = setup(tmp_path)
    barrier = threading.Barrier(12, timeout=10)
    def call(**kw):
        barrier.wait()
        return response(kw)
    result = voter.run(directory, call)
    assert result['observed_runtime']['max_concurrency_per_model'] == {'qwen': 12}
    assert result['observed_runtime']['max_concurrency_observed'] == 12


def test_failed_vote_has_no_winner_and_is_not_repeated(tmp_path):
    voter, directory, _ = setup(tmp_path, 2)
    task = voter.verify(directory)[2][0]
    write(directory / 'cases' / task['case_id'] / 'call_started.json', {})
    result = voter.run(directory, lambda **kw: response(kw))
    assert result['state'] == 'incomplete'
    assert result['summaries']['qwen']['valid_calls'] == 1
    assert result['summaries']['combined']['winner'] is None
    voter.run(directory, lambda **kw: pytest.fail('Repeated interrupted inference'))


def test_tampered_vote_or_duplicate_cannot_complete_selection(tmp_path):
    voter, directory, _ = setup(tmp_path, 2)
    result = voter.run(directory, lambda **kw: response(kw))
    manifest = voter.verify(directory)[1]
    assert voter.summarize(manifest, [result['vote_table'][0]] * 2)['state'] == 'incomplete'
    task = voter.verify(directory)[2][0]
    path = directory / 'cases' / task['case_id'] / 'audit/call_result.json'
    value = pipeline.read(path)
    value['text'] += 'forged'
    write(path, value)
    assert voter.collect(directory)['summaries']['qwen']['winner'] is None


@pytest.mark.parametrize('tamper', ['code', 'recovery', 'identity', 'engine'])
def test_policy_binding_rejects_tampering(tmp_path, tamper):
    setup(tmp_path, 1)
    if tamper in ('code', 'recovery'):
        name = 'selector.py' if tamper == 'code' else 'comparison_recovery.py'
        with (tmp_path / 'selector_runtime' / name).open('a') as handle:
            handle.write('\n# changed\n')
    elif tamper == 'identity':
        identity = pipeline.read(tmp_path / 'harness_release.json')
        del identity['final_selector']
        write(tmp_path / 'harness_release.json', identity)
    else:
        identity = pipeline.read(tmp_path / 'harness_release.json')
        identity['release_sha256'] = '0' * 64
        write(tmp_path / 'harness_release.json', identity)
    with pytest.raises(ValueError):
        policy.module(tmp_path)


def test_captured_policy_survives_checkout_change_and_legacy_has_none(tmp_path, monkeypatch):
    voter, _, _ = setup(tmp_path / 'new', 1)
    monkeypatch.setattr(policy, 'binding', lambda *_: pytest.fail('Current policy used on replay'))
    assert policy.module(tmp_path / 'new') is voter
    write(tmp_path / 'old/harness_release.json', {})
    assert policy.module(tmp_path / 'old') is None


@pytest.mark.parametrize('veto', [False, True])
def test_full_pipeline_exports_qwen_choice_after_dual_model_r2_r3_audit(tmp_path, veto):
    result = subprocess.run([sys.executable, '-B', str(ROOT / 'tests/pipeline_regression_driver.py'),
        str(tmp_path / 'run'), 'CERTIFIED', '--selection-upgrade-b', '--voter-b', '--qwen-selector',
        *(['--audit-veto'] if veto else [])], cwd=ROOT, text=True, capture_output=True, timeout=90)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize('single_gpu', [False, True])
def test_captured_worker_uses_correct_transport_and_label_recovery(tmp_path, single_gpu):
    from test_voter_prose_recovery import prose
    _, directory, _ = setup(tmp_path)
    environment = pipeline.runtime_policy.environment(tmp_path, base_environment())
    environment['PYTHONPATH'] += os.pathsep + str(ROOT / 'tests')
    if single_gpu:
        environment.update(GPU0_BULK_URL='http://127.0.0.1:1', GPU0_BULK_ENGINE=str(ENGINE))
        environment['PYTHONPATH'] = str(ROOT / 'harnesses/single_gpu/client_compat') + os.pathsep + environment['PYTHONPATH']
    script = '''
import json, os, runpy, socket, sys
from types import SimpleNamespace
def forbidden(*a, **kw):
    raise AssertionError('Unexpected network request')
socket.socket.connect = socket.create_connection = forbidden
from experiments.local_math_verifier.cross_lane_voter import live, timeout_adapter, mechanical_recovery
from experiments.local_math_verifier.post_resolver_audit import live as audit
from cross_lane_replay import response, sample
single_gpu = bool(os.environ.get('GPU0_BULK_URL'))
tickets = []
if single_gpu:
    import client
    def api(path, body=None):
        if path == '/enqueue':
            tickets.append(body)
        return {'state': 'granted'}
    client.api = api
def main():
    assert set(live.MODELS) == {'qwen'} and set(audit.MODELS) == {'gemma', 'qwen'}
    assert live.parse(sys.stdin.read())['mechanical_recovery']
    bf = SimpleNamespace(_timeout_call=forbidden, _ORIGINAL=forbidden)
    with timeout_adapter.install(bf, lambda **kw: response(kw), live.parse,
                                 mechanical_recovery.restore_checks_label) as caller:
        assert bool(getattr(caller, '_gpu0_bulk_wrapped', False)) == single_gpu
        result = live.run(sys.argv[-1], caller)
    assert result['state'] == 'completed', result
    if single_gpu:
        assert len(tickets) == 12 and {t['role'] for t in tickets} == {'qwen'}
    print(json.dumps({'state': result['state'], 'calls': result['summaries']['qwen']['valid_calls']}))
    return 0
live.main = main
entry = sys.argv[1]
sys.argv = sys.argv[1:]
runpy.run_path(entry, run_name='__main__')
'''
    result = subprocess.run([sys.executable, '-B', '-c', script,
        str(tmp_path / 'selector_runtime/selector.py'), '--run-root', str(tmp_path), '--root', str(directory)],
        cwd=ENGINE, env=environment, input=prose(), text=True, capture_output=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout) == {'state': 'completed', 'calls': 12}
