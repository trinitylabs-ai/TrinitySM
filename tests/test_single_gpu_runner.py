"""Exercise the public single-GPU boundary without model processes or inference."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
from unittest.mock import Mock

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import run_single_gpu as runner
import serve_models


def arguments(**updates):
    values = dict(benchmark='imo-proofbench/basic', problem_id=['PB-Basic-001'],
                  run_id='single_gpu_test_plan', solver_python=Path(sys.executable),
                  gpu=0, broker_port=18890, generation_seed=None)
    values.update(updates)
    return argparse.Namespace(**values)


def test_fresh_plan_and_dry_run_do_not_contact_servers(monkeypatch, capsys):
    monkeypatch.setattr(runner, 'verify_servers', Mock(side_effect=AssertionError('dry run contacted server')))
    monkeypatch.setattr(subprocess, 'Popen', Mock(side_effect=AssertionError('dry run spawned process')))
    assert runner.main(['--run-id', 'single_gpu_test_plan', '--problem-id', 'PB-Basic-001',
                        '--generation-seed', '27', '--dry-run']) == 0
    record = json.loads(capsys.readouterr().out)
    assert not Path(record['directory']).exists()
    assert record['release'] == '1.12.0' and record['problem_count'] == 1
    assert record['proof_concurrency_by_model'] == {'gemma': 8, 'qwen': 12}
    assert record['comparison_concurrency'] == 12 and record['external_grading'] is False
    job = record['jobs'][0]
    assert job['run_id'] == 'single_gpu_test_plan_PB-Basic-001'
    assert not Path(job['output']).exists()
    assert '--raw-seed-offset' in job['command'] and 'workshop-generation:27' in job['command']
    assert record['adapter_sha256']


def test_count_selection_is_repeatable_and_preserves_generation_defaults():
    args = arguments(benchmark='all', problem_id=None, imo_count=2, basic_count=2,
                     advanced_count=2, sample_seed=1729)
    first, second = runner.plan(args), runner.plan(args)
    assert first == second
    assert first['problem_count'] == 6 and first['candidates_per_problem'] == 4
    assert first['sampling']['seed'] == 1729
    assert {b: sum(j['benchmark'] == b for j in first['jobs']) for b in runner.BENCHMARKS} == dict.fromkeys(runner.BENCHMARKS, 2)
    for job in first['jobs']:
        assert '--raw-seed-offset' not in job['command'] and '--seed-namespace' not in job['command']
        assert job['command'][job['command'].index('--release') + 1] == '1.12.0'
        assert '--execute-models' in job['command']


def test_sampling_and_generation_random_seeds_are_drawn_once_independently(monkeypatch):
    draws = []
    def random_seed(bits):
        draws.append(bits)
        return (31, 47)[len(draws) - 1]
    monkeypatch.setattr(runner.secrets, 'randbits', random_seed)
    result = runner.plan(arguments(benchmark='all', problem_id=None, imo_count=2, basic_count=2,
        advanced_count=2, random_sample_seed=True, random_generation_seed=True))
    assert draws == [32, 32]
    assert result['sampling']['seed'] == 31 and result['generation_seed'] == 47
    for job in result['jobs']:
        assert job['command'][job['command'].index('--raw-seed-offset') + 1] == '47'
        assert 'workshop-generation:47' in job['command']


@pytest.mark.parametrize('updates', [
    dict(imo_count=2),  # outside the selected Basic benchmark
    dict(basic_count=2),  # conflicts with explicit problem IDs
    dict(problem_id=None, basic_count=-1),
    dict(problem_id=None, basic_count=31),
    dict(problem_id=None, basic_count=0),
    dict(sample_seed=1),
])
def test_ambiguous_or_impossible_sampling_is_rejected(updates):
    with pytest.raises(ValueError):
        runner.plan(arguments(**updates))


def test_omitted_counts_mean_zero_and_explicit_mixed_selection_still_works():
    selected = runner.plan(arguments(benchmark='all', problem_id=None, imo_count=6))
    assert len(selected['jobs']) == 6 and all(j['benchmark'] == 'imo2026' for j in selected['jobs'])
    ids = ['imo2026_p4', 'PB-Basic-004', 'PB-Advanced-018']
    explicit = runner.plan(arguments(benchmark='all', problem_id=ids))
    assert {j['problem_id'] for j in explicit['jobs']} == set(ids)
    assert 'sampling' not in explicit and 'generation_seed' not in explicit


@pytest.mark.parametrize('updates', [dict(run_id='../outside'), dict(problem_id=['PB-Basic-999']),
                                     dict(gpu=-1), dict(broker_port=8030)])
def test_invalid_plans_are_rejected(updates):
    with pytest.raises(ValueError):
        runner.plan(arguments(**updates))


def test_statement_tampering_and_existing_outputs_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, 'ROOT', tmp_path)
    base = tmp_path / 'benchmarks/imo-proofbench/basic'
    (base / 'problems').mkdir(parents=True)
    proof = base / 'problems/PB-Basic-001.json'
    proof.write_text('changed statement')
    catalog = {'generation_inputs': {'files': [{'problem_id': 'PB-Basic-001',
                'path': 'problems/PB-Basic-001.json', 'sha256': '0' * 64}]}}
    (base / 'catalog.json').write_text(json.dumps(catalog))
    with pytest.raises(ValueError, match='Statement differs'):
        runner.plan(arguments())
    catalog['generation_inputs']['files'][0]['sha256'] = runner.hashlib.sha256(proof.read_bytes()).hexdigest()
    (base / 'catalog.json').write_text(json.dumps(catalog))
    (base / 'results/single_gpu_test_plan_PB-Basic-001').mkdir(parents=True)
    with pytest.raises(ValueError, match='Run already exists'):
        runner.plan(arguments())


def test_unmanaged_servers_are_never_adopted(monkeypatch):
    monkeypatch.setattr(runner.local_servers, 'require_linux', lambda: None)
    monkeypatch.setattr(runner.local_servers, 'read_state', lambda model: None)
    monkeypatch.setattr(runner.local_servers, 'ready', Mock(side_effect=AssertionError('unmanaged server contacted')))
    with pytest.raises(RuntimeError, match='local_servers.py start --single-gpu'):
        runner.verify_servers(0)


def test_original_release_accepts_sleep_flags_with_identical_model_profile(tmp_path):
    release = ROOT / 'harnesses/imo_proof_pipeline/releases/1.12.0'
    spec = importlib.util.spec_from_file_location('sleep_release_test', release / 'launch.py')
    launch = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(launch)
    profile = json.loads((release / 'profile.json').read_text())
    for index, role in enumerate(('gemma', 'qwen')):
        command, env, _ = serve_models.plan(role, tmp_path / 'models', 2, sleep_mode=True, swap_dir=tmp_path / 'swap')
        process = tmp_path / str(1000 + index)
        process.mkdir()
        (process / 'cmdline').write_bytes(('\0'.join(command) + '\0').encode())
        port = 8030 if role == 'gemma' else 8027
        observed = launch.server_settings(f'http://127.0.0.1:{port}/v1', profile['servers'][role], proc=tmp_path)
        assert observed['flags'] == profile['servers'][role]['flags']
        assert '--enable-sleep-mode' in command and env['CUDA_VISIBLE_DEVICES'] == '2'
        assert ('--kv-cache-memory-bytes' in command) == (role == 'gemma')


def test_real_import_hook_survives_worker_pythonpath_reset():
    env = runner.environment({'broker_url': 'http://127.0.0.1:18890'})
    env['PYTHONPATH'] += os.pathsep + str(runner.ENGINE)
    inner = ('from experiments.local_math_verifier import runtime; '
             'assert runtime.run_openai_chat_generation._gpu0_bulk_wrapped; print("child wrapped")')
    outer = ('import os,subprocess,sys; from experiments.local_math_verifier import runtime; '
             'assert runtime.run_openai_chat_generation._gpu0_bulk_wrapped; '
             'env=dict(os.environ, PYTHONPATH=os.environ["GPU0_BULK_ENGINE"]); '
             f'subprocess.run([sys.executable,"-B","-c",{inner!r}],env=env,check=True)')
    result = subprocess.run([sys.executable, '-B', '-c', outer], env=env, cwd=ROOT,
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    assert 'child wrapped' in result.stdout


@pytest.mark.parametrize('failure', [None, 'worker_launch', 'broker_failed'])
def test_runner_tracks_admission_and_cleans_owned_children(tmp_path, monkeypatch, failure):
    record = runner.plan(arguments())
    record['directory'] = str(tmp_path / 'run')
    broker = Mock(pid=1001)
    broker.poll.return_value = None
    child = Mock(pid=1002, returncode=0)
    child.poll.return_value = 0 if failure is None else None
    def popen(command, **kwargs):
        if 'broker.py' in command[3]:
            return broker
        if failure == 'worker_launch':
            raise OSError('worker launch failed')
        assert kwargs['env']['GPU0_BULK_URL'] == record['broker_url']
        return child
    monkeypatch.setattr(subprocess, 'Popen', popen)
    statuses = [{'state': 'ready'}, {'state': 'failed' if failure == 'broker_failed' else 'ready'}]
    monkeypatch.setattr(runner, 'broker_status', Mock(side_effect=statuses))
    prior = signal.getsignal(signal.SIGTERM)
    if failure:
        with pytest.raises((RuntimeError, OSError)):
            runner.Runner().run(record)
    else:
        assert runner.Runner().run(record) == 0
    state = json.loads((tmp_path / 'run/status.json').read_text())
    assert state['state'] == ('failed' if failure else 'completed')
    assert signal.getsignal(signal.SIGTERM) == prior
    assert (tmp_path / 'run/all_problems_admitted.json').exists() == (failure != 'worker_launch')
    broker.terminate.assert_called_once()
    if failure == 'broker_failed':
        child.terminate.assert_called_once()


@pytest.mark.parametrize('recovers', [True, False])
def test_health_pause_recovers_automatically_or_fails_after_grace(tmp_path, monkeypatch, recovers):
    record = runner.plan(arguments())
    record['directory'] = str(tmp_path / 'run')
    broker = Mock(pid=1001)
    broker.poll.return_value = None
    child = Mock(pid=1002, returncode=0)
    child.poll.return_value = None
    monkeypatch.setattr(subprocess, 'Popen', Mock(side_effect=[broker, child]))
    clock = [0]
    states = iter([('ready', 0), ('paused', 1), ('paused', 2),
                   ('ready' if recovers else 'paused', 3 if recovers else 182)])
    def status(_record):
        state, elapsed = next(states)
        clock[0] = elapsed
        if state == 'ready' and elapsed:
            child.poll.return_value = 0
        return {'state': state, 'health_error': 'Timed out'}
    monkeypatch.setattr(runner, 'broker_status', status)
    monkeypatch.setattr(runner.time, 'monotonic', lambda: clock[0])
    monkeypatch.setattr(runner.time, 'sleep', lambda _: None)
    if recovers:
        assert runner.Runner().run(record) == 0
        child.terminate.assert_not_called()
        child.send_signal.assert_not_called()
    else:
        with pytest.raises(RuntimeError, match='did not recover within 180 seconds'):
            runner.Runner().run(record)
        child.terminate.assert_called_once()
    state = json.loads((tmp_path / 'run/status.json').read_text())
    assert state['state'] == ('completed' if recovers else 'failed')
