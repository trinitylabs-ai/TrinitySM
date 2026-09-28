"""Each candidate independently contributes its last completed submission."""
from test_public_reproduction import pipeline, write
from test_submission_fallback import saved_portfolio


def test_mixed_portfolio_submits_c3_c2_c1_and_lazy_independently(tmp_path, monkeypatch):
    c3, c2, c1, lazy = pipeline.CANDIDATES
    proofs = {p['candidate_id']: p for p in saved_portfolio(tmp_path, 'refinement_2')}
    source = tmp_path / 'problems/A/02_r1_cycles'
    first = source / 'first-pass.md'
    first.write_text('Completed C1 only.\n')
    write(source / 'score_targets.json', {'checkpoints': [
        {'checkpoint': 'R1-C2', 'proofs': [proofs[c3], proofs[c2]]},
        {'checkpoint': 'R1-C1', 'proofs': [{'candidate_id': c1, 'proof_path': str(first),
                                          'proof_sha256': pipeline.proof_hash(first)}]}]})
    directory = tmp_path / f'problems/A/01_source/p1/01_raw_lazy_enhanced_resolve/phase_1_raw_lazy/p1/candidates/{lazy}'
    directory.mkdir(parents=True)
    checked = directory / 'checked_proof.md'
    checked.write_text('Completed lazy check only.\n')
    write(directory / 'result.json', {'problem_id': 'A', 'candidate_id': lazy,
          'checked_proof_path': str(checked), 'checked_proof_sha256': pipeline.proof_hash(checked)})
    calls = []
    def finish(root, source, candidate, *args):
        calls.append(candidate)
        if candidate == c2:
            raise RuntimeError('C3 timeout for this candidate')
        assert candidate == c3
        proof = root / 'finalization/A' / candidate / 'proof.md'
        proof.parent.mkdir(parents=True)
        proof.write_text('Completed C3 only.\n')
        return {'candidate_id': candidate, 'proof_path': str(proof), 'proof_sha256': pipeline.proof_hash(proof)}
    monkeypatch.setattr(pipeline, 'finish_lane', finish)
    assert pipeline.finalize(tmp_path, '1.7.0') == 0
    assert set(calls) == {c3, c2}
    result = pipeline.read(tmp_path / 'final_results.json')
    assert result['completed_proofs'] == 4 and result['fully_refined_proofs'] == 1
    assert result['fallback_proofs'] == 3 and result['state'] == 'completed_with_fallbacks'
    rows = {row['candidate_id']: row for row in result['lanes']}
    expected = {c3: 'refinement_3', c2: 'refinement_2', c1: 'refinement_1', lazy: 'lazy_checked'}
    assert {c: row['selected_stage'] for c, row in rows.items()} == expected
    for row in rows.values():
        assert (tmp_path / row['proof']).read_bytes() == (tmp_path / row['producer']).read_bytes()
    assert 'C3 timeout' in rows[c2]['interruption']['reason']
