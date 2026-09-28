"""Sampling and fail-safe batch orchestration without servers or model calls."""
import hashlib
import importlib.util
import json
from pathlib import Path
import signal
import sys

import pytest


REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'workshop_sampled_suite', REPO / 'scripts/run_sampled_suite.py')
suite = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(suite)


@pytest.fixture
def catalog_root(tmp_path, monkeypatch):
    """Only statement inputs exist, so accidental solution reads also fail."""
    groups = [('imo2026', 'IMO', 6), ('imo-proofbench/basic', 'Basic', 8),
              ('imo-proofbench/advanced', 'Advanced', 10)]
    for benchmark, prefix, count in groups:
        base = tmp_path / 'benchmarks' / benchmark
        (base / 'problems').mkdir(parents=True)
        rows = []
        for index in range(1, count + 1):
            problem_id = f'{prefix}-{index:03}'
            relative = f'problems/{problem_id}.json'
            content = json.dumps({'problem_id': problem_id,
                                  'statement': f'Synthetic statement {index}.'}).encode()
            (base / relative).write_bytes(content)
            rows.append({'problem_id': problem_id, 'path': relative,
                         'sha256': hashlib.sha256(content).hexdigest()})
        # Selection should depend on IDs, not input catalog ordering.
        (base / 'catalog.json').write_text(json.dumps({
            'generation_inputs': {'files': list(reversed(rows))}}))
    monkeypatch.setattr(suite, 'ROOT', tmp_path)
    return tmp_path


def selection(plan):
    return [(job['benchmark'], job['problem_ids']) for job in plan['jobs']]


def argument(command, flag):
    return command[command.index(flag) + 1]


def dry_plan(capsys, *options):
    assert suite.main(['--run-id', 'test-suite', '--dry-run', *options]) == 0
    return json.loads(capsys.readouterr().out)


def test_selects_all_imo_and_unique_three_per_proofbench_group(catalog_root):
    first = suite.make_plan('first', 1729, None, Path(sys.executable))
    replay = suite.make_plan('second', 1729, None, Path(sys.executable))
    assert selection(first) == selection(replay)
    assert [job['benchmark'] for job in first['jobs']] == [
        'imo2026', 'imo-proofbench/basic', 'imo-proofbench/advanced']
    assert [len(job['problem_ids']) for job in first['jobs']] == [6, 3, 3]
    assert first['jobs'][0]['problem_ids'] == [f'IMO-{i:03}' for i in range(1, 7)]
    assert first['problem_count'] == 12
    assert first['candidates_per_problem'] == 4
    assert first['external_grading'] is False
    for job in first['jobs']:
        assert len(set(job['problem_ids'])) == len(job['problem_ids'])
        forwarded = [job['command'][i + 1] for i, value in enumerate(job['command'])
                     if value == '--problem-id']
        assert forwarded == job['problem_ids']
        assert all(row['problem_id'] in job['problem_ids'] for row in job['inputs'])


@pytest.mark.parametrize('generation_seed', [None, 0, 123456789, 0xFFFFFFFF])
def test_model_seed_preserves_problem_selection_and_reaches_every_job(catalog_root, generation_seed):
    plan = suite.make_plan('test-suite', 0, generation_seed, Path(sys.executable))
    original = suite.make_plan('original', 0, None, Path(sys.executable))
    assert selection(plan) == selection(original)
    offset = 0 if generation_seed is None else generation_seed
    namespace = ('v263-v290:problem-only' if generation_seed is None else
                 f'workshop-generation:{generation_seed}')
    assert plan['generation_seed'] == generation_seed
    assert plan['raw_seed_offset'] == offset
    assert plan['seed_namespace'] == namespace
    for job in plan['jobs']:
        assert argument(job['command'], '--raw-seed-offset') == str(offset)
        assert argument(job['command'], '--seed-namespace') == namespace


def test_sample_seed_changes_only_problem_selection(catalog_root):
    first = suite.make_plan('first', 0, 1729, Path(sys.executable))
    second = suite.make_plan('second', 1, 1729, Path(sys.executable))
    assert first['jobs'][0]['problem_ids'] == second['jobs'][0]['problem_ids']
    assert selection(first) != selection(second)
    for key in ['generation_seed', 'raw_seed_offset', 'seed_namespace']:
        assert first[key] == second[key]


def test_dry_run_preserves_original_seeds_and_creates_nothing_without_venv(
        catalog_root, monkeypatch, capsys):
    files_before = sorted(catalog_root.rglob('*'))
    monkeypatch.setattr(suite.subprocess, 'Popen',
                        lambda *a, **kw: pytest.fail('Dry run started a child'))
    monkeypatch.setattr(suite.secrets, 'randbits',
                        lambda *a: pytest.fail('Default unexpectedly drew randomness'))
    plan = dry_plan(capsys)
    assert plan['sample_seed'] == 0
    assert plan['sample_seed_mode'] == 'fixed'
    assert plan['generation_seed'] is None
    assert plan['generation_seed_mode'] == 'original'
    assert sorted(catalog_root.rglob('*')) == files_before
    assert not (catalog_root / '.venv-solver').exists()


@pytest.mark.parametrize('drawn', [(0, 0), (0xFFFFFFFF, 3456789012)])
def test_random_seeds_are_drawn_once_recorded_and_can_be_replayed(
        catalog_root, monkeypatch, capsys, drawn):
    draws = []
    values = iter(drawn)

    def draw(bits):
        draws.append(bits)
        return next(values)

    monkeypatch.setattr(suite.secrets, 'randbits', draw)
    randomized = dry_plan(capsys, '--random-sample-seed', '--random-generation-seed')
    assert draws == [32, 32]
    assert randomized['sample_seed'] == drawn[0]
    assert randomized['generation_seed'] == drawn[1]
    assert randomized['sample_seed_mode'] == randomized['generation_seed_mode'] == 'random'
    replay = dry_plan(capsys, '--sample-seed', str(drawn[0]),
                      '--generation-seed', str(drawn[1]))
    assert draws == [32, 32]
    for key in ['jobs', 'sample_seed', 'generation_seed', 'raw_seed_offset', 'seed_namespace']:
        assert randomized[key] == replay[key]


@pytest.mark.parametrize('option', ['--random-sample-seed', '--random-generation-seed'])
def test_each_random_option_changes_only_its_own_seed(catalog_root, monkeypatch, capsys, option):
    draws = []
    monkeypatch.setattr(suite.secrets, 'randbits', lambda bits: draws.append(bits) or 12345)
    plan = dry_plan(capsys, option)
    assert draws == [32]
    if option == '--random-sample-seed':
        assert plan['sample_seed'] == 12345
        assert plan['generation_seed'] is None
        assert plan['seed_namespace'] == 'v263-v290:problem-only'
    else:
        assert plan['sample_seed'] == 0
        assert plan['generation_seed'] == 12345


@pytest.mark.parametrize('kind', ['sample', 'generation'])
def test_random_and_explicit_seed_options_conflict_before_execution(monkeypatch, capsys, kind):
    monkeypatch.setattr(suite, 'make_plan', lambda *a: pytest.fail('Planning started'))
    with pytest.raises(SystemExit) as error:
        suite.main(['--run-id', 'test-suite', f'--{kind}-seed', '0', f'--random-{kind}-seed'])
    assert error.value.code == 2
    assert 'not allowed with argument' in capsys.readouterr().err


@pytest.mark.parametrize('kind', ['sample', 'generation'])
@pytest.mark.parametrize('value', ['-1', '4294967296', 'not-a-number'])
def test_invalid_seed_is_rejected_before_execution(monkeypatch, capsys, kind, value):
    monkeypatch.setattr(suite, 'make_plan', lambda *a: pytest.fail('Planning started'))
    with pytest.raises(SystemExit) as error:
        suite.main(['--run-id', 'test-suite', f'--{kind}-seed', value])
    assert error.value.code == 2
    assert 'error:' in capsys.readouterr().err


@pytest.mark.parametrize('existing', [
    '.workshop/runs/test-suite', 'benchmarks/imo2026/results/test-suite',
    'benchmarks/imo-proofbench/basic/results/test-suite',
    'benchmarks/imo-proofbench/advanced/results/test-suite'])
def test_any_existing_destination_is_rejected_before_any_job_runs(
        catalog_root, monkeypatch, capsys, existing):
    occupied = catalog_root / existing
    occupied.mkdir(parents=True)
    evidence = occupied / 'keep.txt'
    evidence.write_text('Existing proof evidence')
    monkeypatch.setattr(suite, 'execute', lambda *a: pytest.fail('Execution started'))
    with pytest.raises(SystemExit) as error:
        suite.main(['--run-id', 'test-suite', '--solver-python', sys.executable])
    assert error.value.code == 2
    assert 'already exists' in capsys.readouterr().err
    assert evidence.read_text() == 'Existing proof evidence'


def test_modified_problem_statement_is_rejected_before_execution(catalog_root, monkeypatch, capsys):
    statement = catalog_root / 'benchmarks/imo2026/problems/IMO-001.json'
    statement.write_text('Changed after catalog hashing')
    monkeypatch.setattr(suite, 'execute', lambda *a: pytest.fail('Execution started'))
    with pytest.raises(SystemExit) as error:
        suite.main(['--run-id', 'test-suite', '--solver-python', sys.executable])
    assert error.value.code == 2
    assert 'Problem input differs from catalog' in capsys.readouterr().err


@pytest.mark.parametrize('second_returncode', [0, 7])
def test_real_children_stream_console_and_persist_sequential_success_or_failure(
        tmp_path, monkeypatch, capsys, second_returncode):
    monkeypatch.setattr(suite, 'ROOT', tmp_path)
    state_dir = tmp_path / 'state'
    observed = tmp_path / 'children.jsonl'
    child = tmp_path / 'stub_child.py'
    child.write_text('''import json, os, pathlib, sys
benchmark, log_path, status_path, observed_path, exit_code = sys.argv[1:]
status = json.loads(pathlib.Path(status_path).read_text())
assert status['active_benchmark'] == benchmark
assert os.environ['HF_HUB_OFFLINE'] == os.environ['TRANSFORMERS_OFFLINE'] == '1'
assert os.environ['PYTHONUNBUFFERED'] == '1'
with open(observed_path, 'a') as record:
    record.write(json.dumps({'benchmark': benchmark, 'prior_outcomes': status['outcomes']}) + '\\n')
log = pathlib.Path(log_path)
log.parent.mkdir(parents=True)
log.write_text('nested progress for ' + benchmark + '\\n')
sys.exit(int(exit_code))
''')
    jobs = []
    for index, returncode in enumerate([0, second_returncode, 0], 1):
        benchmark = f'benchmark-{index}'
        log = tmp_path / benchmark / 'generation/console.log'
        jobs.append({'benchmark': benchmark, 'problem_ids': [f'problem-{index}'],
                     'command': [sys.executable, str(child), benchmark, str(log),
                                 str(state_dir / 'status.json'), str(observed), str(returncode)],
                     'console_log': str(log), 'proofs': str(log.parent / 'proofs'),
                     'final_results': str(log.parent / 'final_results.json')})
    plan = {'jobs': jobs, 'problem_count': 3, 'sample_seed': 0, 'generation_seed': 0}
    handlers = {s: signal.getsignal(s) for s in [signal.SIGINT, signal.SIGTERM]}
    assert suite.execute(plan, state_dir) == second_returncode
    assert json.loads((state_dir / 'plan.json').read_text()) == plan
    status = json.loads((state_dir / 'status.json').read_text())
    expected_count = 2 if second_returncode else 3
    records = [json.loads(line) for line in observed.read_text().splitlines()]
    assert [row['benchmark'] for row in records] == [f'benchmark-{i}' for i in range(1, expected_count + 1)]
    assert [len(row['prior_outcomes']) for row in records] == list(range(expected_count))
    assert [row['returncode'] for row in status['outcomes']] == ([0, 7] if second_returncode else [0, 0, 0])
    assert status['state'] == ('failed' if second_returncode else 'completed')
    assert 'started_at' in status and 'finished_at' in status
    assert 'active_benchmark' not in status
    for signum, handler in handlers.items():
        assert signal.getsignal(signum) == handler
    output = capsys.readouterr().out
    for index in range(1, expected_count + 1):
        assert f'nested progress for benchmark-{index}\n' in output
    if second_returncode:
        assert 'nested progress for benchmark-3' not in output
        assert not (tmp_path / 'benchmark-3').exists()
    else:
        assert 'New proofs are ungraded.' in output


def test_launch_exception_is_recorded_and_signal_handlers_restored(tmp_path, monkeypatch):
    state_dir = tmp_path / 'state'
    plan = {'jobs': [{'benchmark': 'first', 'problem_ids': ['one']}], 'problem_count': 1}
    handlers = {s: signal.getsignal(s) for s in [signal.SIGINT, signal.SIGTERM]}

    def cannot_launch(self, job):
        raise OSError('Synthetic process launch failure')

    monkeypatch.setattr(suite.Runner, 'run', cannot_launch)
    with pytest.raises(OSError, match='Synthetic process launch failure'):
        suite.execute(plan, state_dir)
    status = json.loads((state_dir / 'status.json').read_text())
    assert status['state'] == 'failed'
    assert status['outcomes'] == []
    assert status['error'] == 'OSError: Synthetic process launch failure'
    assert 'finished_at' in status
    for signum, handler in handlers.items():
        assert signal.getsignal(signum) == handler
