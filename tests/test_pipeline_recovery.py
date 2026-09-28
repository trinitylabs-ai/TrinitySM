"""Failure recovery contracts, including actual SIGINT/SIGTERM delivery."""
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import pytest
from test_public_reproduction import pipeline, write, ROOT


def frontend(tmp_path, candidate='t07_r01'):
    directory = tmp_path / f'problems/synthetic/01_source/p1/01_raw_lazy_enhanced_resolve/phase_1_raw_lazy/p1/candidates/{candidate}'
    directory.mkdir(parents=True)
    proof = directory / 'draft_proof.md'
    proof.write_text('Completed raw proof.\n')
    row = {'candidate_id': candidate, 'problem_id': 'synthetic',
           'proof_path': str(proof), 'proof_sha256': pipeline.proof_hash(proof)}
    write(directory / 'cold_result.json', row)
    return directory, row


@pytest.mark.parametrize('damage', ['missing', 'truncated', 'hash_mismatch', 'path_escape'])
def test_incomplete_or_invalid_lazy_output_uses_bound_raw_proof(tmp_path, damage):
    directory, raw = frontend(tmp_path)
    checked = directory / 'checked_proof.md'
    checked.write_text('Unusable lazy proof')
    receipt = directory / 'result.json'
    if damage == 'truncated':
        receipt.write_text('{')
    elif damage != 'missing':
        row = {'candidate_id': raw['candidate_id'], 'checked_proof_path': str(checked),
               'checked_proof_sha256': pipeline.proof_hash(checked)}
        if damage == 'hash_mismatch':
            checked.write_text('Changed after receipt')
        else:
            outside = tmp_path / 'unrelated.md'
            outside.write_text(checked.read_text())
            checked.unlink()
            checked.symlink_to(outside)
        write(receipt, row)
    issues = []
    selected = pipeline.collect_lane(tmp_path, 'synthetic', raw['candidate_id'], issues)
    assert selected['selected_stage'] == 'raw'
    assert selected['proof_sha256'] == raw['proof_sha256']
    if damage != 'missing':
        assert issues


def test_failed_core_exports_raw_and_records_unstarted_lanes(tmp_path, monkeypatch):
    run = tmp_path / 'run'
    def core(*args, **kwargs):
        frontend(run)
        write(run / 'manifest.json', {'problems': [{'problem_id': 'synthetic'}, {'problem_id': 'unstarted'}]})
        source = run / 'problems/synthetic/02_r1_cycles'
        source.mkdir()
        (source / 'manifest.json').write_text('{')
        (source / 'score_targets.json').write_text('{')
        write(run / 'problems/synthetic/status.json', {'state': 'failed_closed', 'error': 'worker crashed'})
        return 17
    monkeypatch.setattr(pipeline, 'run_process', core)
    monkeypatch.setattr(pipeline, 'finish_lane', lambda *a: pytest.fail('Started another model stage'))
    assert pipeline.main(['--problem-dir', str(tmp_path), '--output-dir', str(run), '--execute-models']) == 17
    result = pipeline.read(run / 'final_results.json')
    assert result['execution']['returncode'] == 17
    assert result['winner_selection_policy'] is None
    assert result['state'] == 'completed_with_failures'
    assert result['completed_proofs'] == 1 and len(result['lanes']) == 8
    first = result['lanes'][0]
    assert first['state'] == 'failed' and first['proof_available']
    assert first['selected_stage'] == 'raw'
    assert first['interruption']['reason'] == 'worker crashed'
    assert all(not row['proof_available'] for row in result['lanes'][1:])
    assert result['recovery_issues']


def test_raw_file_without_completion_record_is_not_exported(tmp_path):
    directory, raw = frontend(tmp_path)
    (directory / 'cold_result.json').unlink()
    assert pipeline.collect_lane(tmp_path, 'synthetic', raw['candidate_id'], []) is None


@pytest.mark.parametrize('selector', [None, 'legacy', 'qwen'])
def test_launch_exception_still_writes_final_results(tmp_path, monkeypatch, selector):
    identity_path = tmp_path / 'harness_release.json'
    original_identity = None
    expected_policy = None
    if selector is not None:
        release = pipeline.DEFAULT_RELEASE
        identity = {'version': release,
                    'release_sha256': pipeline.sha(pipeline.IMPLEMENTATION / 'releases' / release / 'release.json')}
        if selector == 'qwen':
            identity['final_selector'] = pipeline.selector_policy.binding(release)
        write(identity_path, identity)
        original_identity = identity_path.read_bytes()
        expected_policy = ('qwen_only_full_round_robin_seed_order_ties' if selector == 'qwen'
                           else 'dual_model_full_round_robin_seed_order_ties')
    def core(*args, **kwargs):
        raise OSError('Synthetic process launch failure')
    monkeypatch.setattr(pipeline, 'run_process', core)
    assert pipeline.main(['--problem-dir', str(tmp_path), '--output-dir', str(tmp_path), '--execute-models']) == 1
    result = pipeline.read(tmp_path / 'final_results.json')
    assert result['completed_proofs'] == 0
    assert result['state'] == 'completed_with_failures'
    assert result['winner_selection_policy'] == expected_policy
    assert result['execution']['returncode'] == 1
    assert 'Synthetic process launch failure' in result['execution']['reason']
    assert pipeline.read(tmp_path / 'pipeline_execution.json') == result['execution']
    assert (identity_path.read_bytes() if identity_path.exists() else None) == original_identity


@pytest.mark.parametrize('damage', ['malformed', 'wrong_release'])
def test_finalization_still_rejects_invalid_saved_release(tmp_path, damage):
    identity_path = tmp_path / 'harness_release.json'
    if damage == 'malformed':
        identity_path.write_text('{')
    else:
        write(identity_path, {'version': pipeline.DEFAULT_RELEASE, 'release_sha256': '0' * 64})
    with pytest.raises(ValueError):
        pipeline.finalize(tmp_path, pipeline.DEFAULT_RELEASE, execute=False)
    assert not (tmp_path / 'final_results.json').exists()


def test_collection_rejects_active_native_worker(tmp_path):
    lock_path = tmp_path / 'problems/synthetic/worker.lock'
    lock_path.parent.mkdir(parents=True)
    with lock_path.open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(BlockingIOError):
            pipeline.main(['--collect-only', '--output-dir', str(tmp_path)])
    assert not (tmp_path / 'final_results.json').exists()


@pytest.mark.parametrize('signum', [signal.SIGINT, signal.SIGTERM])
@pytest.mark.parametrize('finalization', [False, True])
def test_actual_signal_stops_process_tree_and_exports_last_completed_proof(tmp_path, signum, finalization):
    output = tmp_path / 'run'
    command = [sys.executable, '-B', str(ROOT / 'tests/pipeline_interruption_driver.py'), str(output)]
    if finalization:
        command.append('--finalization')
    process = subprocess.Popen(command,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    children = {}
    try:
        deadline = time.monotonic() + 10
        while not (output / 'ready.json').is_file():
            assert process.poll() is None, process.communicate()
            assert time.monotonic() < deadline, 'Worker did not become ready'
            time.sleep(0.02)
        children = json.loads((output / 'ready.json').read_text())
        process.send_signal(signum)
        stdout, stderr = process.communicate(timeout=15)
        assert process.returncode == 128 + signum, stdout + stderr
        result = pipeline.read(output / 'final_results.json')
        assert result['execution']['signal'] == signum.name
        assert result['execution']['returncode'] == 128 + signum
        assert result['state'] == 'completed_with_failures'
        assert result['winner_selection_policy'] is None
        assert pipeline.read(output / 'pipeline_execution.json') == result['execution']
        assert result['completed_proofs'] == 1
        row = result['lanes'][0]
        assert row['selected_stage'] == ('refinement_2' if finalization else 'raw')
        assert row['state'] == 'interrupted'
        expected = 'A completed second refinement.\n' if finalization else 'A completed synthetic draft.\n'
        assert (output / row['proof']).read_text() == expected
        for pid in children.values():
            status = Path(f'/proc/{pid}/stat')
            assert not status.exists() or status.read_text().split()[2] == 'Z'
    finally:
        if process.poll() is None:
            process.kill()
            process.communicate(timeout=5)
        for pid in children.values():
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
