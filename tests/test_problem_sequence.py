"""Problem-boundary scheduling, failure and resume checks without model calls."""
from collections import Counter
import signal
import subprocess
import sys

import pytest

from test_public_reproduction import ROOT, load, pipeline, write


def save_checkpoint(root, problem, stage, candidates=pipeline.CANDIDATES):
    source = root / 'problems' / problem / '02_r1_cycles'
    write(source / 'manifest.json', {'problem_id': problem, 'runtime': {},
                                    'candidate_ids': list(pipeline.CANDIDATES)})
    proofs = []
    for candidate in candidates:
        proof = source / f'{candidate}.{stage}.md'
        proof.write_text(f'Completed {stage} proof for {problem}/{candidate}.\n')
        proofs.append({'candidate_id': candidate, 'proof_path': str(proof),
                       'proof_sha256': pipeline.proof_hash(proof)})
    write(source / 'score_targets.json', {'checkpoints': [{'checkpoint': stage, 'proofs': proofs}]})


def save_frontend(root, problem, stage):
    for candidate in pipeline.CANDIDATES:
        directory = root / f'problems/{problem}/01_source/p1/01_raw_lazy_enhanced_resolve/phase_1_raw_lazy/p1/candidates/{candidate}'
        directory.mkdir(parents=True)
        lazy = stage == 'lazy_checked'
        proof = directory / ('checked_proof.md' if lazy else 'draft_proof.md')
        proof.write_text(f'Completed {stage} proof for {candidate}.\n')
        prefix = 'checked_proof' if lazy else 'proof'
        write(directory / ('result.json' if lazy else 'cold_result.json'),
              {'candidate_id': candidate, 'problem_id': problem,
               prefix + '_path': str(proof), prefix + '_sha256': pipeline.proof_hash(proof)})


@pytest.fixture
def sequence(tmp_path, monkeypatch):
    monkeypatch.setitem(sys.modules, 'pipeline', pipeline)
    scheduler = load('test_problem_sequence_scheduler', 'harnesses/proof_workshop/problem_queue.py')
    engine = scheduler.verified_engine('1.7.0')
    monkeypatch.setattr(scheduler, 'verified_engine', lambda _: engine)
    monkeypatch.setattr(engine[1], 'server_settings', lambda *a: {})
    statements = tmp_path / 'statements'
    for problem in ('A', 'B'):
        write(statements / f'{problem}.json', {'problem_id': problem, 'problem': f'Prove {problem}.'})
    run = tmp_path / 'run'
    arguments = ['--problem-dir', str(statements), '--output-dir', str(run),
                 '--seed-namespace', 'sequence:test', '--raw-seed-offset', '17', '--execute-models']
    events = []

    def worker(queue, root, row, *, dry_run):
        assert not dry_run
        problem = row['problem_id']
        events.append((problem, 'C2'))
        source = root / 'problems' / problem / '02_r1_cycles'
        write(source.parent / 'summary.json', {'state': 'completed', 'failed_lane_count': 0})
        save_checkpoint(root, problem, 'R1-C2')
        return 0

    def finish(root, source, candidate, problem, release, python):
        marker = root / 'finalization' / problem / candidate / 'status.json'
        if marker.exists():
            return
        events.append((problem, candidate))
        output = marker.parent
        output.mkdir(parents=True, exist_ok=True)
        saved = next(p for p in pipeline.read(source / 'score_targets.json')['checkpoints'][0]['proofs']
                     if p['candidate_id'] == candidate)
        proof = output / 'proof.md'
        proof.write_text(f'Completed C3 proof for {problem}/{candidate}.\n')
        staged = output / 'input.md'
        staged.write_bytes(pipeline.Path(saved['proof_path']).read_bytes())
        write(output / 'continuation.json', {
            'source_manifest_sha256': pipeline.sha(source / 'manifest.json'),
            'release_sha256': pipeline.read(root / 'harness_release.json')['release_sha256'],
            'driver_sha256': pipeline.sha(pipeline.IMPLEMENTATION / 'tools/continue_r1.py'),
            'problem_id': problem, 'candidate_id': candidate, 'source_proof': saved,
            'input_proof': {'candidate_id': candidate, 'proof_path': str(staged),
                            'proof_sha256': pipeline.proof_hash(staged)},
            'runtime': {}, 'target_checkpoint': 'R1-C3'})
        write(output / 'terminal_proof.json', {'candidate_id': candidate, 'proof_path': str(proof),
                                             'proof_sha256': pipeline.proof_hash(proof)})
        write(marker, {'state': 'completed'})

    monkeypatch.setattr(scheduler, 'run_worker', worker)
    monkeypatch.setattr(pipeline, 'finish_lane', finish)
    return scheduler, run, arguments, events


def test_finishes_all_c3_lanes_before_next_problem_and_preserves_native_identity(sequence):
    scheduler, root, arguments, events = sequence
    assert scheduler.main(arguments) == 0
    assert events[0] == ('A', 'C2')
    assert set(events[1:5]) == {('A', c) for c in pipeline.CANDIDATES}
    assert events[5] == ('B', 'C2')
    assert set(events[6:]) == {('B', c) for c in pipeline.CANDIDATES}
    manifest = pipeline.read(root / 'manifest.json')
    assert [(r['problem_id'], r['problem_number']) for r in manifest['problems']] == [('A', 1), ('B', 2)]
    assert manifest['seed_namespace'] == 'sequence:test' and manifest['raw_seed_offset'] == 17
    assert manifest['terminal_checkpoint'] == 'R1-C2'
    record = pipeline.read(root / 'problem_sequence.json')
    assert record['completed_problems'] == ['A', 'B'] and record['state'] == 'completed'
    assert record['scheduling_policy'] == pipeline.SCHEDULING_POLICY
    assert record['inference_finished'] is True
    assert record['attempted_problems'] == ['A', 'B']
    for problem in record['problems']:
        assert problem['started_at'] <= problem['completed_at']
        assert problem['elapsed_seconds'] >= 0 and problem['resumed'] is False
        assert all(lane['selected_stage'] == 'refinement_3' for lane in problem['lanes'])


def test_new_release_audits_after_all_c3_lanes_before_next_problem(sequence, monkeypatch):
    scheduler, root, arguments, events = sequence
    def audit(run_root, problem, release, python):
        assert release == '1.10.0'
        assert all((problem, candidate) in events for candidate in pipeline.CANDIDATES)
        events.append((problem, 'AUDIT'))
    monkeypatch.setattr(pipeline, 'run_post_resolver_audit', audit)
    assert scheduler.main(['--release', '1.10.0', *arguments]) == 0
    assert events.index(('A', 'AUDIT')) < events.index(('B', 'C2'))
    assert events[-1] == ('B', 'AUDIT')


def test_c3_failure_keeps_c2_and_continues_next_problem(sequence, monkeypatch):
    scheduler, root, arguments, events = sequence
    original = pipeline.finish_lane
    def finish(*args):
        if args[3] == 'A' and args[2] == pipeline.CANDIDATES[0]:
            raise RuntimeError('Synthetic C3 timeout')
        return original(*args)
    monkeypatch.setattr(pipeline, 'finish_lane', finish)
    assert scheduler.main(arguments) == 0
    assert any(problem == 'B' for problem, _ in events)
    record = pipeline.read(root / 'problem_sequence.json')
    assert record['state'] == 'completed_with_fallbacks' and record['inference_finished']
    assert 'Synthetic C3 timeout' in record['lane_errors']['A/' + pipeline.CANDIDATES[0]]
    lane = record['problems'][0]['lanes'][0]
    assert lane['proof_available'] and lane['selected_stage'] == 'refinement_2'


@pytest.mark.parametrize('stage', ['refinement_1', 'lazy_checked', 'raw'])
def test_worker_failure_without_c2_collects_saved_proofs_then_continues(sequence, monkeypatch, stage):
    scheduler, root, arguments, events = sequence
    original = scheduler.run_worker
    def worker(queue, output, row, **kwargs):
        if row['problem_id'] != 'A':
            return original(queue, output, row, **kwargs)
        if stage == 'refinement_1':
            save_checkpoint(output, 'A', 'R1-C1')
        else:
            save_frontend(output, 'A', stage)
        return 17
    monkeypatch.setattr(scheduler, 'run_worker', worker)
    assert scheduler.main(arguments) == 0
    assert not any(problem == 'A' for problem, _ in events)
    assert any(problem == 'B' for problem, _ in events)
    record = pipeline.read(root / 'problem_sequence.json')
    assert record['state'] == 'completed_with_fallbacks' and record['inference_finished']
    assert {lane['selected_stage'] for lane in record['problems'][0]['lanes']} == {stage}
    assert len(record['lane_errors']) == 4


def test_partial_worker_failure_still_finishes_valid_c2_lanes(sequence, monkeypatch):
    scheduler, root, arguments, events = sequence
    original = scheduler.run_worker
    healthy = pipeline.CANDIDATES[0]
    def worker(queue, output, row, **kwargs):
        if row['problem_id'] != 'A':
            return original(queue, output, row, **kwargs)
        save_checkpoint(output, 'A', 'R1-C1')
        target = output / 'problems/A/02_r1_cycles/score_targets.json'
        first = pipeline.read(target)['checkpoints'][0]
        save_checkpoint(output, 'A', 'R1-C2', [healthy])
        second = pipeline.read(target)['checkpoints'][0]
        write(target, {'checkpoints': [second, first]})
        return 17
    monkeypatch.setattr(scheduler, 'run_worker', worker)
    assert scheduler.main(arguments) == 0
    assert [event for event in events if event[0] == 'A'] == [('A', healthy)]
    record = pipeline.read(root / 'problem_sequence.json')
    a = record['problems'][0]
    assert a['worker_returncode'] == 17 and '17' in a['worker_error']
    selected = {lane['candidate_id']: lane['selected_stage'] for lane in a['lanes']}
    assert selected[healthy] == 'refinement_3'
    assert {stage for candidate, stage in selected.items() if candidate != healthy} == {'refinement_1'}
    assert f'A/{healthy}' not in record['lane_errors']
    assert len(record['lane_errors']) == 3
    assert any(problem == 'B' for problem, _ in events)


def test_corrupt_c2_is_not_sent_to_c3_and_other_lane_errors_accumulate(sequence, monkeypatch):
    scheduler, root, arguments, events = sequence
    original_worker = scheduler.run_worker
    original_finish = pipeline.finish_lane
    corrupt = pipeline.CANDIDATES[0]
    def worker(queue, output, row, **kwargs):
        result = original_worker(queue, output, row, **kwargs)
        if row['problem_id'] == 'A':
            save_frontend(output, 'A', 'lazy_checked')
            (output / f'problems/A/02_r1_cycles/{corrupt}.R1-C2.md').write_text('Tampered proof.\n')
        return result
    def finish(*args):
        if args[3] == 'B' and args[2] == pipeline.CANDIDATES[1]:
            raise RuntimeError('B C3 timeout')
        return original_finish(*args)
    monkeypatch.setattr(scheduler, 'run_worker', worker)
    monkeypatch.setattr(pipeline, 'finish_lane', finish)
    assert scheduler.main(arguments) == 0
    assert ('A', corrupt) not in events
    record = pipeline.read(root / 'problem_sequence.json')
    assert record['problems'][0]['lanes'][0]['selected_stage'] == 'lazy_checked'
    assert set(record['lane_errors']) == {f'A/{corrupt}', 'B/' + pipeline.CANDIDATES[1]}


def test_missing_proofs_fail_after_attempting_remaining_problems(sequence, monkeypatch):
    scheduler, root, arguments, events = sequence
    original = scheduler.run_worker
    monkeypatch.setattr(scheduler, 'run_worker',
                        lambda queue, output, row, **kw: 17 if row['problem_id'] == 'A'
                        else original(queue, output, row, **kw))
    assert scheduler.main(arguments) == 1
    assert any(problem == 'B' for problem, _ in events)
    record = pipeline.read(root / 'problem_sequence.json')
    assert record['state'] == 'failed' and record['inference_finished']
    assert record['completed_problems'] == ['B']
    assert record['problems'][0]['state'] == 'missing_proofs'
    assert all(not lane['proof_available'] for lane in record['problems'][0]['lanes'])


@pytest.mark.parametrize('code', [-signal.SIGINT, -signal.SIGTERM, -signal.SIGKILL, 130, 143])
def test_signalled_worker_stops_the_queue(sequence, monkeypatch, code):
    scheduler, root, arguments, events = sequence
    monkeypatch.setattr(scheduler, 'run_worker', lambda *a, **kw: code)
    assert scheduler.main(arguments) == (128 - code if code < 0 else code)
    assert events == []
    record = pipeline.read(root / 'problem_sequence.json')
    assert record['state'] == 'interrupted' and not record['inference_finished']
    assert record['attempted_problems'] == ['A']


@pytest.mark.parametrize('code', [-signal.SIGTERM, 130, 143])
def test_signalled_c3_stops_before_next_problem(sequence, monkeypatch, code):
    scheduler, root, arguments, events = sequence
    monkeypatch.setattr(pipeline, 'finish_lane',
                        lambda *a: (_ for _ in ()).throw(subprocess.CalledProcessError(code, ['synthetic'])))
    assert scheduler.main(arguments) == (128 - code if code < 0 else code)
    assert events == [('A', 'C2')]
    record = pipeline.read(root / 'problem_sequence.json')
    assert record['state'] == 'interrupted' and not record['inference_finished']


@pytest.mark.parametrize('boundary', ['C2', 'C3'])
def test_resume_reuses_completed_work_and_finishes_c3_before_advancing(sequence, monkeypatch, boundary):
    scheduler, root, arguments, events = sequence
    original = scheduler.finish_problem
    def interrupt(*args):
        if boundary == 'C3':
            original(*args)
        raise KeyboardInterrupt('Synthetic boundary stop')
    monkeypatch.setattr(scheduler, 'finish_problem', interrupt)
    with pytest.raises(KeyboardInterrupt):
        scheduler.main(arguments)
    identity = (root / 'harness_release.json').read_bytes()
    manifest = (root / 'manifest.json').read_bytes()
    monkeypatch.setattr(scheduler, 'finish_problem', original)
    assert scheduler.main([*arguments, '--resume']) == 0
    counts = Counter(events)
    assert counts == Counter({(p, c): 1 for p in ('A', 'B') for c in ('C2', *pipeline.CANDIDATES)})
    assert all(p == 'A' for p, _ in events[:5])
    assert (root / 'harness_release.json').read_bytes() == identity
    assert (root / 'manifest.json').read_bytes() == manifest
    assert all(row['resumed'] for row in pipeline.read(root / 'problem_sequence.json')['problems'])


def test_resume_rejects_changed_seeds_before_any_worker(sequence):
    scheduler, root, arguments, events = sequence
    assert scheduler.main(arguments) == 0
    before = list(events)
    changed = list(arguments)
    changed[changed.index('--raw-seed-offset') + 1] = '18'
    with pytest.raises(ValueError, match='Resume changes'):
        scheduler.main([*changed, '--resume'])
    assert events == before


def test_selected_problem_keeps_original_ordinal(sequence):
    scheduler, root, arguments, events = sequence
    assert scheduler.main([*arguments, '--problem-id', 'B']) == 0
    assert pipeline.read(root / 'manifest.json')['problems'][0]['problem_number'] == 2
    assert all(problem == 'B' for problem, _ in events)


@pytest.mark.parametrize('resume,modified', [(True, False), (False, False), (True, True)])
def test_resumed_export_archives_only_receipt_bound_earlier_proof(tmp_path, monkeypatch, resume, modified):
    source = tmp_path / 'problems/A/02_r1_cycles'
    candidate = pipeline.CANDIDATES[0]
    write(source / 'manifest.json', {'problem_id': 'A', 'candidate_ids': [candidate]})
    old = source / 'proof.md'
    old.write_text('Completed C2 proof.\n')
    write(source / 'score_targets.json', {'checkpoints': [{'checkpoint': 'R1-C2', 'proofs': [{
        'candidate_id': candidate, 'proof_path': str(old), 'proof_sha256': pipeline.proof_hash(old)}]}]})
    assert pipeline.finalize(tmp_path, '1.7.0', execute=False,
                             execution={'state': 'interrupted', 'returncode': 143}) == 1
    destination = tmp_path / 'proofs/A' / (candidate + '.md')
    earlier_receipt = (tmp_path / 'final_results.json').read_bytes()
    if modified:
        destination.write_text('User modification.\n')
    prior_bytes = destination.read_bytes()
    def finish(*args):
        proof = tmp_path / 'finalization/A' / candidate / 'proof.md'
        proof.parent.mkdir(parents=True)
        proof.write_text('Completed C3 proof.\n')
        return {'candidate_id': candidate, 'proof_path': str(proof), 'proof_sha256': pipeline.proof_hash(proof)}
    monkeypatch.setattr(pipeline, 'finish_lane', finish)
    result = pipeline.finalize(tmp_path, '1.7.0', allow_export_advance=resume)
    if resume and not modified:
        assert result == 0
        assert destination.read_text() == 'Completed C3 proof.\n'
        archived = list((tmp_path / 'proof_history/A' / candidate).glob('*.md'))
        assert len(archived) == 1 and archived[0].read_bytes() == prior_bytes
        receipts = list((tmp_path / 'proof_history').glob('final_results.*.json'))
        assert len(receipts) == 1 and receipts[0].read_bytes() == earlier_receipt
    else:
        assert result == 1 and destination.read_bytes() == prior_bytes
        assert not (tmp_path / 'proof_history').exists()

@pytest.mark.parametrize('failed_vote', [False, True])
def test_voter_follows_audit_before_next_problem_and_records_failure(sequence, monkeypatch, failed_vote):
    scheduler, root, arguments, events = sequence
    def audit(run_root, problem, release, python):
        events.append((problem,'AUDIT'))
    def vote(run_root, problem, release, **kwargs):
        assert kwargs['execute'] and (problem,'AUDIT') in events
        events.append((problem,'VOTE'))
        return {'state':'incomplete' if failed_vote and problem=='A' else 'completed'}
    monkeypatch.setattr(pipeline,'run_post_resolver_audit',audit)
    monkeypatch.setattr(pipeline,'cross_lane_selection',vote)
    assert scheduler.main(['--release','1.11.0',*arguments]) == (1 if failed_vote else 0)
    assert events.index(('A','AUDIT')) < events.index(('A','VOTE')) < events.index(('B','C2'))
    assert events[-1] == ('B','VOTE')
    record=pipeline.read(root/'problem_sequence.json')
    assert record['problems'][0]['cross_lane_voter']['state']==('incomplete' if failed_vote else 'completed')
