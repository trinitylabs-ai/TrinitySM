import json
from pathlib import Path
import threading

import pytest

from harnesses.post_resolver_audit import live
from post_resolver_audit_replay import response


def prepare(tmp_path, cid='lane', identical=False):
    raw = tmp_path / (cid + '.r2.md'); raw.write_text('An incomplete calculation.\n')
    new = tmp_path / (cid + '.r3.md'); new.write_text(raw.read_text() if identical else 'The missing calculation is supplied.\n')
    pair = {'problem_id': 'P', 'candidate_id': cid, 'problem': 'Prove the implication.',
            'baseline_path': str(raw), 'candidate_path': str(new),
            'baseline_proof_sha256': live.digest(raw.read_bytes().strip()),
            'candidate_proof_sha256': live.digest(new.read_bytes().strip()),
            'grade': 'SECRET_GRADE', 'reference_solution': 'SECRET_REFERENCE'}
    runtime = {'seed_namespace': 'test:17', 'gemma_endpoint': 'http://127.0.0.1:8030/v1',
               'qwen_endpoint': 'http://127.0.0.1:8027/v1', 'model_timeout_sec': 600}
    root = tmp_path / 'audit' / cid
    case, tasks = live.prepare(root, pair, runtime, 'a' * 64)
    return root, pair, runtime, case, tasks


def selected(root, pair):
    return live.collect(root, Path(pair['baseline_path']).read_bytes(),
                        Path(pair['candidate_path']).read_bytes(), 'a' * 64)


@pytest.mark.parametrize('mode,expected', [('accept', live.ACCEPT), ('veto', live.KEEP),
                                         ('invalid', live.KEEP), ('failed', live.KEEP)])
def test_real_bindings_and_four_approval_policy(tmp_path, mode, expected):
    root, pair, runtime, case, tasks = prepare(tmp_path)
    calls = []
    def caller(**kwargs):
        calls.append(kwargs)
        if mode == 'failed' and len(calls) == 1:
            raise TimeoutError('scripted timeout')
        return response(kwargs, live.KEEP if mode == 'veto' and len(calls) == 1 else live.ACCEPT,
                        invalid=mode == 'invalid' and len(calls) == 1)
    for task in tasks:
        live.execute_task(root, task, caller)
    assert selected(root, pair)['decision'] == expected
    assert len(calls) == 4
    assert len({c['seed_key'] for c in calls}) == 1
    assert all(c['temperature'] == 0.2 for c in calls)
    assert all('SECRET' not in c['user_prompt'] for c in calls)
    forward, reverse = calls[0]['user_prompt'], calls[1]['user_prompt']
    assert forward.index('# Baseline proof') < forward.index('# Candidate proof')
    assert reverse.index('# Candidate proof') < reverse.index('# Baseline proof')
    for task in tasks:
        live.execute_task(root, task, lambda **_: pytest.fail('Completed audit must not rerun'))
    assert selected(root, pair)['decision'] == expected
    # Re-preparing the same run is idempotent; changing its seed is refused.
    live.prepare(root, pair, runtime, 'a' * 64)
    with pytest.raises(ValueError, match='changed'):
        live.prepare(root, pair, {**runtime, 'seed_namespace': 'different'}, 'a' * 64)


def test_interrupted_call_not_repeated_and_collector_never_trusts_forged_selection(tmp_path):
    root, pair, _, _, tasks = prepare(tmp_path)
    folder = root / 'cases' / tasks[0]['case_id'] / 'audit'
    folder.mkdir(parents=True)
    live.execute_task(root, tasks[0], lambda **_: pytest.fail('Interrupted request must not repeat'))
    for task in tasks[1:]:
        live.execute_task(root, task, lambda **kw: response(kw))
    live.write(root / 'selection.json', {'decision': live.ACCEPT})
    assert selected(root, pair)['decision'] == live.KEEP


def test_tampering_after_acceptance_forces_r2(tmp_path):
    root, pair, _, case, tasks = prepare(tmp_path)
    for task in tasks:
        live.execute_task(root, task, lambda **kw: response(kw))
    assert selected(root, pair)['decision'] == live.ACCEPT
    call_path = root / 'cases' / tasks[0]['case_id'] / 'audit/call_result.json'
    call = live.read(call_path); call['text'] += ' altered'; live.write(call_path, call)
    assert selected(root, pair)['decision'] == live.KEEP
    Path(pair['candidate_path']).write_text('A different proof.')
    with pytest.raises(ValueError, match='different proofs'):
        selected(root, pair)


def test_identical_proofs_skip_all_calls(tmp_path):
    root, pair, _, _, tasks = prepare(tmp_path, identical=True)
    assert tasks == []
    assert selected(root, pair)['state'] == 'identical_no_calls'


@pytest.mark.parametrize('lane_count,peak_per_model', [(4, 8), (6, 12), (8, 12)])
def test_twelve_slots_per_model_without_extra_calls(tmp_path, lane_count, peak_per_model):
    roots = [prepare(tmp_path, f'lane{i}')[0] for i in range(lane_count)]
    job = tmp_path / 'audit/job.json'; live.write(job, {'lane_roots': list(map(str, roots))})
    barrier, lock = threading.Barrier(2 * peak_per_model, timeout=10), threading.Lock()
    active = peak = count = 0
    model_active = {m: 0 for m in live.MODELS.values()}
    model_peak = dict(model_active)
    def caller(**kwargs):
        nonlocal active, peak, count
        model = kwargs['model']
        with lock:
            active += 1; count += 1; peak = max(peak, active)
            first_wave = count <= 2 * peak_per_model
            model_active[model] += 1
            model_peak[model] = max(model_peak[model], model_active[model])
        if first_wave:
            barrier.wait()
        result = response(kwargs)
        with lock:
            active -= 1
            model_active[model] -= 1
        return result
    report = live.run_job(job, caller)
    assert peak == 2 * peak_per_model and count == 4 * lane_count and report['completed_calls'] == 4 * lane_count
    assert model_peak == {model: peak_per_model for model in live.MODELS.values()}
    assert report['workers_per_model'] == {'gemma': 12, 'qwen': 12}
    assert report['max_concurrency_per_model'] == {'gemma': peak_per_model, 'qwen': peak_per_model}
    assert report['workers_total'] == 24
    assert report['max_concurrency_observed'] == 2 * peak_per_model
    assert report['active_calls'] == 0 and set(report['active_per_model'].values()) == {0}
    assert all(r['decision'] == live.ACCEPT for r in report['selections'])
    live.run_job(job, lambda **_: pytest.fail('Completed calls must not rerun'))


def test_identical_lane_leaves_only_twelve_calls_and_six_gemma_slots(tmp_path):
    roots = [prepare(tmp_path, f'lane{i}', identical=i == 3)[0] for i in range(4)]
    job = tmp_path / 'audit/job.json'; live.write(job, {'lane_roots': list(map(str, roots))})
    barrier, lock = threading.Barrier(12, timeout=10), threading.Lock()
    calls = []
    def caller(**kwargs):
        with lock:
            calls.append(kwargs['model'])
            first_wave = len(calls) <= 12
        if first_wave:
            barrier.wait()
        return response(kwargs)
    report = live.run_job(job, caller)
    assert len(calls) == report['total_calls'] == 12
    assert report['max_concurrency_observed'] == 12
    assert report['max_concurrency_per_model'] == {'gemma': 6, 'qwen': 6}
    assert all(row['decision'] == live.ACCEPT for row in report['selections'])
