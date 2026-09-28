"""Matched snapshots, ordered execution, and fail-closed paired orchestration."""
import importlib.util
from pathlib import Path
import signal
import sys
from types import ModuleType

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harnesses.block_local_completion import inputs, paired_runner, runner

_spec = importlib.util.spec_from_file_location('_block_raw_fixture', Path(__file__).with_name('test_block_local_runner.py'))
_fixtures = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fixtures)


@pytest.fixture
def source_run(tmp_path):
    return _fixtures.source_run.__wrapped__(tmp_path)


def args_for(source, output, live=False):
    args = runner.parser().parse_args(['run', '--source-run', str(source), '--problem-id', 'imo2026_p2',
        '--problem-id', 'imo2026_p3', '--seed', '17', '--output-dir', str(output)]
        + (['--execute-models'] if live else []))
    return args


def plan_for(source, tmp_path, live=False):
    return paired_runner.create_plan(args_for(source, tmp_path.resolve() / 'paired', live))


def fake_reports(monkeypatch, events):
    module = ModuleType('harnesses.block_local_completion.paired_report')
    module.export_grading = lambda path: events.append('export')
    module.write_report = lambda path: events.append('report')
    monkeypatch.setitem(sys.modules, module.__name__, module)


def test_all_conditions_frozen_with_same_raw_bytes_seed_and_batch(source_run, tmp_path):
    args = args_for(source_run, tmp_path.resolve() / 'paired')
    original_args = vars(args).copy()
    path = paired_runner.create_plan(args)
    assert vars(args) == original_args
    plan = inputs.read(path)
    assert plan['schema'] == 'block-local-paired-plan-v1'
    assert plan['repair_temperatures'] == [0.7, 0.4, 0.4]
    assert plan['seed'] == 17 and plan['problem_count'] == 2 and plan['raw_candidates'] == 8
    banks, jobs = [], []
    for label, temperature, strategy in paired_runner.ARMS:
        child = inputs.read(path.parent / label / 'plan.json')
        assert child['repair_temperature'] == temperature
        assert child['strategy'] == strategy
        assert child['pipeline_config'] == runner.strategy_config(strategy)
        assert child['terminal_stage'] == runner.TERMINAL_STAGES[strategy]
        banks.append(inputs.verify_manifest(child['input_manifest_path']))
        jobs.append([inputs.read(j['job_path']) for j in child['jobs']])
        assert all(j['runtime']['workers'] == 4 and j['runtime']['repair_temperature'] == temperature
                   for j in jobs[-1])
    for index in (1, 2):
        assert paired_runner._bank_identity(banks[0]) == paired_runner._bank_identity(banks[index])
        assert [paired_runner._job_identity(j) for j in jobs[0]] == [paired_runner._job_identity(j) for j in jobs[index]]
    proof_bytes = [[Path(c['proof_path']).read_bytes() for row in b['problems'] for c in row['candidates']]
                   for b in banks]
    assert proof_bytes[0] == proof_bytes[1] == proof_bytes[2]
    assert not (path.parent / 'paired_status.json').exists()
    with pytest.raises(ValueError, match='fresh'):
        paired_runner.create_plan(args)


def test_native_source_drift_between_freezes_rejected(source_run, tmp_path, monkeypatch):
    create = runner.create_plan
    def drifting(args):
        path = create(args)
        if args.repair_temperature == 0.7:
            manifest = inputs.read(source_run / 'manifest.json')
            manifest['seed_namespace'] = 'changed_between_arms'
            inputs.write(source_run / 'manifest.json', manifest)
        return path
    monkeypatch.setattr(runner, 'create_plan', drifting)
    with pytest.raises(ValueError, match='changed'):
        plan_for(source_run, tmp_path)
    assert not (tmp_path / 'paired/pair_plan.json').exists()


@pytest.mark.parametrize('what', ['provenance', 'runtime'])
def test_individually_hashbound_but_mismatched_arms_rejected(source_run, tmp_path, monkeypatch, what):
    create = runner.create_plan
    def mismatched(args):
        path = create(args)
        if args.strategy == 'original':
            plan = inputs.read(path)
            if what == 'provenance':
                bank = inputs.read(plan['input_manifest_path'])
                bank['problems'][0]['provenance']['source_seed_namespace'] = 'other'
                inputs.write(plan['input_manifest_path'], bank)
                plan['input_manifest_sha256'] = inputs.digest(plan['input_manifest_path'])
            for entry in plan['jobs']:
                job = inputs.read(entry['job_path'])
                job['input_manifest_sha256'] = plan['input_manifest_sha256']
                if what == 'runtime':
                    job['runtime']['qwen_endpoint'] = 'http://127.0.0.1:9999/v1'
                inputs.write(entry['job_path'], job)
                entry['job_sha256'] = inputs.digest(entry['job_path'])
            inputs.write(path, plan)
        return path
    monkeypatch.setattr(runner, 'create_plan', mismatched)
    with pytest.raises(ValueError, match='different raw|differ beyond'):
        plan_for(source_run, tmp_path)


@pytest.mark.parametrize('live', [False, True])
def test_sequential_all_problems_then_second_arm_and_deferred_reporting(source_run, tmp_path, monkeypatch, live):
    path = plan_for(source_run, tmp_path, live)
    events = []
    fake_reports(monkeypatch, events)
    def child_run(child_path, *, defer_reporting=False):
        assert defer_reporting is True
        assert all((path.parent / label / 'plan.json').exists() for label, _, _ in paired_runner.ARMS)
        plan = inputs.read(child_path)
        events.extend(f"{child_path.parent.name}:{job['problem_id']}" for job in plan['jobs'])
        status = {'state': 'completed' if live else 'preflight_passed'}
        inputs.write(child_path.parent / 'status.json', status)
        return status
    monkeypatch.setattr(runner, 'run_plan', child_run)
    status = paired_runner.run_plan(path)
    assert events == ['t07:imo2026_p2', 't07:imo2026_p3', 't04:imo2026_p2', 't04:imo2026_p3',
                      'original_t04:imo2026_p2', 'original_t04:imo2026_p3'] + (
        ['export', 'report'] if live else ['report'])
    assert status['state'] == ('completed' if live else 'preflight_passed')
    assert [row['label'] for row in status['outcomes']] == ['t07', 't04', 'original_t04']
    assert [row['strategy'] for row in status['outcomes']] == ['block', 'block', 'original']
    assert all(row['status_sha256'] for row in status['outcomes'])
    assert 'active' not in inputs.read(path.parent / 'paired_status.json')
    with pytest.raises(ValueError, match='already started'):
        paired_runner.run_plan(path)


@pytest.mark.parametrize('error', [runner.Interrupted(signal.SIGTERM), KeyboardInterrupt(), ValueError('worker failed')])
def test_interruption_or_failure_prevents_second_arm(source_run, tmp_path, monkeypatch, error):
    path = plan_for(source_run, tmp_path)
    calls = []
    fake_reports(monkeypatch, calls)
    def fail(child_path, *, defer_reporting=False):
        calls.append(child_path.parent.name)
        raise error
    monkeypatch.setattr(runner, 'run_plan', fail)
    before = {sig: signal.getsignal(sig) for sig in (signal.SIGINT, signal.SIGTERM)}
    with pytest.raises(type(error)):
        paired_runner.run_plan(path)
    assert calls == ['t07']
    status = inputs.read(path.parent / 'paired_status.json')
    assert status['state'] == ('interrupted' if isinstance(error, KeyboardInterrupt) else 'failed')
    assert len(status['outcomes']) == 1 and 'active' not in status
    assert {sig: signal.getsignal(sig) for sig in before} == before


@pytest.mark.parametrize('target', ['parent', 'child', 'code'])
def test_revalidates_frozen_plans_and_code_before_second_arm(source_run, tmp_path, monkeypatch, target):
    path = plan_for(source_run, tmp_path)
    calls = []
    fake_reports(monkeypatch, calls)
    verify = inputs.verify_sources
    def child_run(child_path, *, defer_reporting=False):
        calls.append(child_path.parent.name)
        if target == 'code':
            hashes = inputs.read(path)['code_hashes']
            def altered(mapping):
                if mapping == hashes:
                    raise ValueError('Code changed')
                return verify(mapping)
            monkeypatch.setattr(inputs, 'verify_sources', altered)
        else:
            changed = path if target == 'parent' else path.parent / 'original_t04/plan.json'
            data = inputs.read(changed)
            data['seed'] = 23
            inputs.write(changed, data)
        return {'state': 'preflight_passed'}
    monkeypatch.setattr(runner, 'run_plan', child_run)
    with pytest.raises(ValueError, match='changed'):
        paired_runner.run_plan(path)
    assert calls == ['t07']
    assert inputs.read(path.parent / 'paired_status.json')['state'] == 'failed'


def test_reject_child_already_run_before_parent(source_run, tmp_path, monkeypatch):
    path = plan_for(source_run, tmp_path)
    inputs.write(path.parent / 'original_t04/status.json', {'state': 'preflight_passed'})
    monkeypatch.setattr(runner, 'run_plan', lambda *a, **k: pytest.fail('Must not run a child'))
    with pytest.raises(ValueError, match='child arm already started'):
        paired_runner.run_plan(path)


@pytest.mark.parametrize('field,value', [
    ('strategy', 'block'),
    ('pipeline_config', {'neighbor_blocks': 1, 'max_audit_passes': 1, 'max_resolve_passes': 1}),
    ('terminal_stage', 'block_audit_or_one_resolve'),
])
def test_original_condition_cannot_silently_enable_block_pipeline(source_run, tmp_path, field, value):
    path = plan_for(source_run, tmp_path)
    plan = inputs.read(path)
    arm = plan['arms'][2]
    child = inputs.read(arm['plan_path'])
    child[field] = value
    inputs.write(arm['plan_path'], child)
    arm['plan_sha256'] = inputs.digest(arm['plan_path'])
    with pytest.raises(ValueError, match='configuration changed'):
        paired_runner.verify_pair(plan)


@pytest.mark.parametrize('label', ['t04', 'original_t04'])
def test_failure_in_later_condition_stops_remaining_work(source_run, tmp_path, monkeypatch, label):
    path = plan_for(source_run, tmp_path)
    calls = []
    fake_reports(monkeypatch, calls)
    def child_run(child_path, *, defer_reporting=False):
        calls.append(child_path.parent.name)
        if child_path.parent.name == label:
            raise runner.Interrupted(signal.SIGTERM)
        return {'state': 'preflight_passed'}
    monkeypatch.setattr(runner, 'run_plan', child_run)
    with pytest.raises(runner.Interrupted):
        paired_runner.run_plan(path)
    expected = ['t07', 't04'] if label == 't04' else ['t07', 't04', 'original_t04']
    assert calls == expected
    assert inputs.read(path.parent / 'paired_status.json')['state'] == 'interrupted'
