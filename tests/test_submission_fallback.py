"""Completed earlier proofs remain final submissions after refinement failures."""
import pytest

from test_public_reproduction import pipeline, write


def saved_portfolio(root, stage):
    pid = 'A'
    write(root / 'manifest.json', {'problems': [{'problem_id': pid}]})
    source = root / 'problems' / pid / '02_r1_cycles'
    write(source / 'manifest.json', {'problem_id': pid, 'candidate_ids': list(pipeline.CANDIDATES)})
    proofs = []
    for candidate in pipeline.CANDIDATES:
        if stage.startswith('refinement_'):
            proof = source / f'{candidate}.md'
        else:
            directory = root / f'problems/A/01_source/p1/01_raw_lazy_enhanced_resolve/phase_1_raw_lazy/p1/candidates/{candidate}'
            directory.mkdir(parents=True)
            proof = directory / ('checked_proof.md' if stage == 'lazy_checked' else 'draft_proof.md')
        proof.write_text(f'Completed {stage} proof for {candidate}.\n')
        row = {'candidate_id': candidate, 'proof_path': str(proof), 'proof_sha256': pipeline.proof_hash(proof)}
        proofs.append(row)
        if stage == 'lazy_checked':
            write(proof.parent / 'result.json', {'problem_id': pid, 'candidate_id': candidate,
                  'checked_proof_path': str(proof), 'checked_proof_sha256': row['proof_sha256']})
        elif stage == 'raw':
            write(proof.parent / 'cold_result.json', dict(row, problem_id=pid))
    if stage.startswith('refinement_'):
        write(source / 'score_targets.json', {'checkpoints': [
            {'checkpoint': 'R1-C' + stage[-1], 'proofs': proofs}]})
    return proofs


@pytest.mark.parametrize('stage', ['refinement_2', 'refinement_1', 'lazy_checked', 'raw'])
def test_successful_submission_uses_exact_last_completed_proof(tmp_path, monkeypatch, stage):
    proofs = saved_portfolio(tmp_path, stage)
    monkeypatch.setattr(pipeline, 'finish_lane', lambda *args: pytest.fail('Fallback collection must not call models'))
    assert pipeline.finalize(tmp_path, '1.7.0', execute=False) == 0
    receipt = pipeline.read(tmp_path / 'final_results.json')
    assert receipt['state'] == 'completed_with_fallbacks'
    assert receipt['execution']['state'] == 'completed' and receipt['execution']['returncode'] == 0
    assert receipt['fully_refined_proofs'] == 0 and receipt['fallback_proofs'] == receipt['completed_proofs'] == 4
    originals = {p['candidate_id']: p for p in proofs}
    for row in receipt['lanes']:
        assert row['selected_stage'] == stage and row['state'] == 'completed_with_fallback'
        assert row['fallback_used'] is True and row['fully_refined'] is False
        assert pipeline.proof_hash(tmp_path / row['proof']) == originals[row['candidate_id']]['proof_sha256']
        assert row['interruption']['stage'] == {'refinement_2': 'refinement_3', 'refinement_1': 'refinement_2',
                                              'lazy_checked': 'refinement_1', 'raw': 'lazy_checked'}[stage]


def test_controller_does_not_retry_c3_after_scheduler_selected_fallback(tmp_path, monkeypatch):
    root = tmp_path / 'run'
    def scheduler(*args, **kwargs):
        saved_portfolio(root, 'refinement_2')
        write(root / 'problem_sequence.json', {'scheduling_policy': pipeline.SCHEDULING_POLICY,
              'state': 'completed_with_fallbacks', 'inference_finished': True,
              'lane_errors': {'A/' + c: 'C3 request timed out' for c in pipeline.CANDIDATES}})
        return 0
    monkeypatch.setattr(pipeline, 'run_process', scheduler)
    monkeypatch.setattr(pipeline, 'finish_lane', lambda *a: pytest.fail('Scheduler already attempted C3'))
    # This fixture records the original four-lane fallback, without the later
    # cross-lane selector's evidence. Keep its release explicit as defaults evolve.
    assert pipeline.main(['--release', '1.7.0', '--problem-dir', str(tmp_path),
                          '--output-dir', str(root), '--execute-models']) == 0
    receipt = pipeline.read(root / 'final_results.json')
    assert receipt['fallback_proofs'] == 4
    assert all('C3 request timed out' in row['interruption']['reason'] for row in receipt['lanes'])


def test_corrupt_latest_proof_falls_back_without_accepting_its_bytes(tmp_path):
    saved_portfolio(tmp_path, 'refinement_1')
    source = tmp_path / 'problems/A/02_r1_cycles'
    target = pipeline.read(source / 'score_targets.json')
    damaged = dict(target['checkpoints'][0]['proofs'][0], proof_sha256='0' * 64)
    target['checkpoints'].append({'checkpoint': 'R1-C2', 'proofs': [damaged]})
    write(source / 'score_targets.json', target)
    assert pipeline.finalize(tmp_path, '1.7.0', execute=False) == 0
    receipt = pipeline.read(tmp_path / 'final_results.json')
    assert all(row['selected_stage'] == 'refinement_1' for row in receipt['lanes'])
    assert any(row.get('recovery_issues') for row in receipt['lanes'])


def test_missing_completed_proofs_is_not_successful_submission(tmp_path):
    write(tmp_path / 'manifest.json', {'problems': [{'problem_id': 'A'}]})
    assert pipeline.finalize(tmp_path, '1.7.0', execute=False) == 1
    receipt = pipeline.read(tmp_path / 'final_results.json')
    assert receipt['completed_proofs'] == 0 and receipt['state'] == 'completed_with_failures'


def test_user_stop_remains_interrupted_even_when_all_lanes_have_fallback(tmp_path):
    saved_portfolio(tmp_path, 'refinement_2')
    assert pipeline.finalize(tmp_path, '1.7.0', execute=False,
                             execution={'state': 'interrupted', 'returncode': 143}) == 1
    receipt = pipeline.read(tmp_path / 'final_results.json')
    assert receipt['execution']['state'] == 'interrupted' and receipt['execution']['returncode'] == 143
    assert receipt['completed_proofs'] == 4 and all(row['state'] == 'interrupted' for row in receipt['lanes'])
