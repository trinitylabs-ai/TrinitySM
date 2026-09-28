"""Offline end-to-end checks for the paired experiment and source snapshots."""
import hashlib
import json
from pathlib import Path
import signal
import subprocess
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harnesses.refinement_bf_ablation import inputs, runner


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


@pytest.fixture
def source(tmp_path):
    root = tmp_path.resolve() / 'source'
    pid, number, claim = 'imo2026_p2', 2, 'Prove that x² ≥ 0 for every real number x.'
    inputs.write(root / 'harness_release.json', {'version': '1.7.0', 'release_sha256': inputs.digest(inputs.RELEASE / 'release.json')})
    inputs.write(root / 'manifest.json', {'schema': 'v263_lazy_refined_to_v290_r1c2_queue_v1',
        'dry_run': False, 'seed_namespace': 'source-seed',
        'problems': [{'problem_id': pid, 'problem_number': number, 'problem': claim}]})
    inputs.write(root / f'inputs/{pid}.json', {'problem_id': pid, 'problem': claim})
    phase = root / f'problems/{pid}/01_source/p{number}/01_raw_lazy_enhanced_resolve'
    inputs.write(phase / 'summary.json', {'state': 'completed', 'terminal_checkpoint': 'lazy_checked',
        'problem_id': pid, 'candidate_ids': list(inputs.CANDIDATES)})
    statement = phase / 'input/problem.json'
    inputs.write(statement, {'problem_id': pid, 'problem_number': number, 'claim': claim})
    cases = []
    for cid in inputs.CANDIDATES:
        directory = phase / f'phase_1_raw_lazy/p{number}/candidates/{cid}'
        directory.mkdir(parents=True)
        proof = directory / 'checked_proof.md'
        proof.write_bytes(f'\r\nProof for {cid}: a real square is nonnegative.\r\n'.encode())
        inputs.write(directory / 'result.json', {'candidate_id': cid, 'checked_proof_path': str(proof),
                                                'checked_proof_sha256': inputs.text_hash(proof)})
        cases.append({'candidate_id': cid, 'case_id': f'{pid}.{cid}', 'problem_id': pid,
                      'proof_path': str(proof), 'problem_path': str(statement)})
    original = phase / 'phase_2_v096_cases.json'
    inputs.write(original, {'cases': cases})
    inputs.write(phase / 'phase_2_v096/manifest.json', {'source_manifest_path': str(original),
        'source_manifest_sha256': inputs.digest(original),
        'cases': [{**case, 'proof_sha256': inputs.text_hash(case['proof_path']), 'problem_sha256': sha(claim)} for case in cases]})
    return root


def args(source, output, *extra):
    return runner.parser().parse_args(['run', '--source-run', str(source), '--problem-id', 'imo2026_p2',
                                      '--output-dir', str(output), *extra])


def test_both_arms_share_proofs_seed_policy_and_differ_only_cue_variant(source, tmp_path):
    original = {str(p): inputs.digest(p) for p in source.rglob('*') if p.is_file()}
    plan_path = runner.create_plan(args(source, tmp_path.resolve() / 'experiment', '--pair-seed', '10', '--pair-seed', '11'))
    plan = inputs.read(plan_path)
    assert plan['dry_run'] is True
    assert len(plan['pairs']) == 2
    assert plan['pairs'][0]['arm_order'] == list(reversed(plan['pairs'][1]['arm_order']))
    for pair in plan['pairs']:
        left, right = [inputs.read(pair['arms'][variant]['job_path']) for variant in runner.VARIANTS]
        assert left['variant'] != right['variant']
        for field in ('output_dir', 'variant'):
            left.pop(field)
            right.pop(field)
        assert left == right
        assert 'original' not in left['runtime']['seed_namespace']
        assert left['dry_run'] is True
    inputs.verify_sources(original)
    frozen = inputs.verify_manifest(plan['input_manifest_path'], plan['input_manifest_sha256'])
    for item in frozen['problems'][0]['candidates']:
        assert Path(item['proof_path']).read_bytes().startswith(b'\r\n')
    with pytest.raises(ValueError, match='fresh'):
        runner.create_plan(args(source, tmp_path.resolve() / 'experiment'))


def test_reject_drift_in_native_proof_before_snapshot(source):
    proof = next(source.rglob('checked_proof.md'))
    proof.write_text('A different proof')
    with pytest.raises(ValueError, match='completed producer'):
        inputs.load_sources([source], ['imo2026_p2'])


def test_reject_statement_and_missing_lane(source):
    queue = source / 'manifest.json'
    record = inputs.read(queue)
    record['problems'][0]['problem'] = 'A different task'
    inputs.write(queue, record)
    with pytest.raises(ValueError, match='Frozen statement'):
        inputs.load_sources([source], ['imo2026_p2'])


def test_snapshot_independent_of_source_and_protected_from_drift(source, tmp_path):
    bank = inputs.load_sources([source], ['imo2026_p2'])
    path = inputs.snapshot_inputs(bank, tmp_path.resolve() / 'snapshots')
    expected = inputs.digest(path)
    frozen = inputs.verify_manifest(path, expected)
    original = next(source.rglob('checked_proof.md'))
    original.write_text('Later original source change')
    inputs.verify_manifest(path, expected)
    target = Path(frozen['problems'][0]['candidates'][0]['proof_path'])
    target.write_text('Modified experiment input')
    with pytest.raises(ValueError, match='binding changed'):
        inputs.verify_manifest(path, expected)


def test_live_requires_explicit_opt_in(source, tmp_path):
    path = runner.create_plan(args(source, tmp_path.resolve() / 'live', '--execute-models'))
    plan = inputs.read(path)
    assert plan['dry_run'] is False
    assert all(inputs.read(arm['job_path'])['dry_run'] is False for pair in plan['pairs'] for arm in pair['arms'].values())


def test_refuse_source_output_overlap(source):
    with pytest.raises(ValueError, match='separate'):
        runner.create_plan(args(source, source / 'experiment'))


def test_offline_cli_runs_real_frozen_engine_in_two_fresh_processes(source, tmp_path):
    output = tmp_path.resolve() / 'offline'
    command = [sys.executable, '-B', str(runner.ROOT / 'scripts/run_refinement_bf_ablation.py'), 'run',
               '--source-run', str(source), '--problem-id', 'imo2026_p2', '--output-dir', str(output)]
    result = subprocess.run(command, cwd=runner.ROOT, text=True, capture_output=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    status = inputs.read(output / 'status.json')
    assert status['state'] == 'preflight_passed'
    assert len(status['outcomes']) == 2
    plan = inputs.read(output / 'plan.json')
    for arm in plan['pairs'][0]['arms'].values():
        summary = inputs.read(Path(arm['output_dir']) / 'summary.json')
        assert summary['state'] == 'preflight_passed'
        assert summary['model_calls'] == 0
        assert len(summary['lanes']) == 4
    assert (output / 'REPORT.md').exists()
    assert not (output / 'grading').exists()


def test_stop_child_reaps_owned_process_group(monkeypatch):
    signals, waits = [], []
    monkeypatch.setattr(runner.os, 'killpg', lambda pid, sig: signals.append((pid, sig)))
    def wait(timeout=None):
        waits.append(timeout)
        if timeout is not None:
            raise subprocess.TimeoutExpired('fixture', timeout)
        return -9
    child = SimpleNamespace(pid=123456, poll=lambda: None, wait=wait)
    runner.stop_child(child)
    assert signals == [(123456, signal.SIGTERM), (123456, signal.SIGKILL)]
    assert waits == [10, None]


def test_interruption_terminates_child_and_records_status(source, tmp_path, monkeypatch):
    plan = runner.create_plan(args(source, tmp_path.resolve() / 'interrupted'))
    stopped = []
    class Child:
        pid = 123456
        def __init__(self, *args, **kwargs):
            assert kwargs['start_new_session'] is True
        def wait(self, timeout=None):
            raise runner.Interrupted(signal.SIGTERM)
    monkeypatch.setattr(runner.subprocess, 'Popen', Child)
    monkeypatch.setattr(runner, 'stop_child', lambda child: stopped.append(child.pid))
    with pytest.raises(runner.Interrupted):
        runner.run_plan(plan)
    assert stopped == [123456]
    assert inputs.read(plan.parent / 'status.json')['state'] == 'interrupted'
