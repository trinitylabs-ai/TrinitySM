"""Disjoint follow-up selection and waiting without launching GPU processes."""
import argparse
import fcntl
import json
from pathlib import Path
import shutil
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import run_next_single_gpu as followup


@pytest.fixture
def prior(tmp_path, monkeypatch):
    original = followup.ROOT
    for benchmark in followup.runner.BENCHMARKS:
        source = original / 'benchmarks' / benchmark
        target = tmp_path / 'benchmarks' / benchmark
        shutil.copytree(source / 'problems', target / 'problems')
        shutil.copyfile(source / 'catalog.json', target / 'catalog.json')
    monkeypatch.setattr(followup, 'ROOT', tmp_path)
    monkeypatch.setattr(followup.runner, 'ROOT', tmp_path)
    adapter = tmp_path / 'harnesses/single_gpu'
    shutil.copytree(original / 'harnesses/single_gpu', adapter)
    monkeypatch.setattr(followup.runner, 'ADAPTER', adapter)
    plan = followup.runner.plan(argparse.Namespace(benchmark='all', problem_id=None,
        imo_count=2, basic_count=2, advanced_count=2, sample_seed=42,
        generation_seed=None, gpu=0, broker_port=18890,
        run_id='first', solver_python=Path(sys.executable)))
    directory = tmp_path / '.workshop/single_gpu/first'
    directory.mkdir(parents=True)
    (directory / 'plan.json').write_text(json.dumps(plan))
    status = dict(state='completed_with_failures', jobs=[
        dict(problem_id=job['problem_id'], returncode=1 if i == 0 else 0)
        for i, job in enumerate(plan['jobs'])])
    (directory / 'status.json').write_text(json.dumps(status))
    return tmp_path, plan, status


def options(*extra):
    return ['--after-run', 'first', '--run-id', 'second', *extra]


def read_plan(prior, capsys):
    assert followup.main(options('--dry-run')) == 0
    return json.loads(capsys.readouterr().out)


def test_disjoint_repeatable_plan_keeps_generation_defaults(prior, capsys, monkeypatch):
    monkeypatch.setattr(followup.os, 'execv', lambda *a: pytest.fail('dry-run launched a process'))
    record = read_plan(prior, capsys)
    assert record == read_plan(prior, capsys)
    old = {j['problem_id'] for j in prior[1]['jobs']}
    assert len(record['selected_problems']) == 6
    assert not old.intersection(record['selected_problems'])
    native = record['native_plan']
    for group in followup.runner.BENCHMARKS:
        assert sum(j['benchmark'] == group for j in native['jobs']) == 2
    assert record['generation_seed'] is None
    assert '--generation-seed' not in record['argv']
    assert all('--raw-seed-offset' not in j['command'] for j in native['jobs'])
    assert not (prior[0] / '.workshop/runs').exists()
    assert not Path(native['directory']).exists()


def test_original_problem_failure_does_not_prevent_followup_after_all_exit(prior, capsys):
    record = read_plan(prior, capsys)
    assert followup.previous_finished(record)
    status = prior[2]
    status['jobs'][1]['returncode'] = None
    Path(record['previous_plan']).with_name('status.json').write_text(json.dumps(status))
    with pytest.raises(ValueError, match='every problem exited'):
        followup.previous_finished(record)


def test_active_run_requires_wait_and_wait_execs_existing_runner(prior, monkeypatch, capsys):
    status_path = prior[0] / '.workshop/single_gpu/first/status.json'
    status_path.write_text(json.dumps(dict(state='running', jobs=[])))
    launched = []
    monkeypatch.setattr(followup.os, 'execv', lambda *a: launched.append(a))
    with pytest.raises(SystemExit):
        followup.main(options())
    assert not launched and not (prior[0] / '.workshop/runs').exists()
    waited = []
    def finish(seconds):
        waited.append(seconds)
        status_path.write_text(json.dumps(prior[2]))
    monkeypatch.setattr(followup.time, 'sleep', finish)
    followup.main(options('--wait'))
    assert waited == [15] and len(launched) == 1
    command = launched[0][1]
    assert command[3] == str(prior[0] / 'scripts/run_single_gpu.py')
    assert command.count('--problem-id') == 6 and '--execute-models' not in command
    assert (prior[0] / '.workshop/runs/second.followup.json').exists()
    with pytest.raises(SystemExit):
        followup.main(options())
    assert len(launched) == 1


def test_cleanup_lock_must_be_released(prior, capsys):
    record = read_plan(prior, capsys)
    lock = prior[0] / '.workshop/servers/single_gpu_run.lock'
    lock.parent.mkdir(parents=True)
    with lock.open('w') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        assert not followup.previous_finished(record)
    assert followup.previous_finished(record)


def test_changed_previous_plan_is_rejected(prior, capsys):
    record = read_plan(prior, capsys)
    Path(record['previous_plan']).write_text('{}')
    with pytest.raises(ValueError, match='changed while waiting'):
        followup.previous_finished(record)


@pytest.mark.parametrize('state', ['failed', 'interrupted', 'unknown'])
def test_aborted_or_unrecognized_runner_state_is_not_silently_advanced(prior, capsys, state):
    record = read_plan(prior, capsys)
    status = dict(prior[2], state=state)
    Path(record['previous_plan']).with_name('status.json').write_text(json.dumps(status))
    with pytest.raises(ValueError):
        followup.previous_finished(record)


@pytest.mark.parametrize('extra', [
    ('--imo-count', '5'), ('--basic-count', '-1'),
    ('--imo-count', '0', '--basic-count', '0', '--advanced-count', '0'),
    ('--run-id', 'first'), ('--after-run', '../outside'),
])
def test_invalid_or_impossible_selection_is_rejected(prior, extra):
    with pytest.raises(SystemExit):
        followup.main(options('--dry-run', *extra))


def test_custom_counts_and_explicit_generation_seed(prior, capsys):
    assert followup.main(options('--dry-run', '--imo-count', '0', '--basic-count', '4',
        '--advanced-count', '1', '--generation-seed', '17')) == 0
    record = json.loads(capsys.readouterr().out)
    assert len(record['selected_problems']) == 5
    assert record['generation_seed'] == 17 and '17' in record['argv']
