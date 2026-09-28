"""Report-only baseline binding, changed-proof exports, and grade reuse."""
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harnesses.post_c3_completion import report


def write(path, value):
    report.write(path, value)
    return path


@pytest.fixture
def experiment(tmp_path, monkeypatch):
    root = tmp_path.resolve()
    archive, run = root / 'archive', root / 'run'
    pid, claim = 'imo2026_p2', 'Prove that every real square is nonnegative.'
    problem = {'problem_id': pid, 'problem_number': 2, 'claim': claim,
               'problem_sha256': report.hashlib.sha256(claim.encode()).hexdigest()}
    write(archive / 'problems' / f'{pid}.json', {'problem_id': pid, 'problem': claim})
    rubric = archive / 'grading/strict_olympiad_policy_v2.txt'
    rubric.parent.mkdir(parents=True)
    rubric.write_text('Strict Olympiad rubric fixture.\n')
    config = {'model': 'gpt-5.6-sol', 'reasoning_effort': 'xhigh',
              'policy_sha256': report.text_sha(rubric), 'reference_sha256': 'a' * 64}
    write(archive / 'grading/reference_sources.json', {'references': [{'problem_id': pid, 'reference_sha256': 'a' * 64}]})
    candidates, baseline_lanes = [], []
    baseline_scores = [[7, 7], [3, 5], [6, 6], [2, 2]]
    for index, cid in enumerate(report.CANDIDATES):
        data = f'\r\nSaved B proof for {cid}.\r\n'.encode()
        published = archive / 'proofs/B' / pid / f'{cid}.md'
        published.parent.mkdir(parents=True, exist_ok=True)
        published.write_bytes(data)
        source = run / 'inputs' / pid / f'{cid}.md'
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_bytes(data)
        stage = 'refinement_1' if index == 3 else 'refinement_3'
        candidate = {'candidate_id': cid, 'proof_path': str(source), 'proof_file_sha256': report.sha(source),
                     'proof_sha256': report.text_sha(source), 'selected_stage': stage}
        candidates.append(candidate)
        grade_paths = []
        for repeat, score in enumerate(baseline_scores[index], 1):
            path = archive / 'grades/B' / pid / cid / f'pass_{repeat}.json'
            write(path, {'problem_id': pid, 'repeat': repeat, 'proof_sha256': candidate['proof_sha256'],
                        'problem_sha256': problem['problem_sha256'], **config, 'grade': {'score': score},
                        'errors': [], 'isolation_audit': {'tool_calls': 0}})
            grade_paths.append(str(path.relative_to(archive)))
        baseline_lanes.append({'problem_id': pid, 'arm': 'B', 'candidate_id': cid, 'scores': baseline_scores[index],
            'mean_score': sum(baseline_scores[index]) / 2, 'selected_stage': stage,
            'proof_path': str(published.relative_to(archive)), 'proof_file_sha256': report.sha(published),
            'proof_sha256': report.text_sha(published), 'grade_paths': grade_paths})
    write(archive / 'comparison.json', {'state': 'completed', 'run_id': 'baseline_fixture',
        'selection_results_included': False, 'post_selection_recovery_included': False,
        **config, 'lanes': baseline_lanes})
    archive_manifest = write(archive / 'manifest.json', {'schema': 'refinement-bf-publication-v1',
        'run_id': 'baseline_fixture', 'files': {str(p.relative_to(archive)): {'sha256': report.sha(p)}
        for p in archive.rglob('*') if p.is_file()}})
    bank = {'schema': 'post-c3-inputs-v1', 'source_arm': 'B', 'archive_root': str(archive),
            'archive_manifest_sha256': report.sha(archive_manifest), 'release_sha256': 'b' * 64,
            'problems': [{'problem': problem, 'candidates': candidates}]}
    manifest = write(run / 'inputs/manifest.json', bank)
    # The input module has its own tests. Keep this unit suite focused on the
    # report's complete job/output/archive chain, while checking snapshot hashes.
    def verified_input(path, expected):
        assert report.sha(path) == expected
        value = report.read(path)
        for row in value['problems']:
            for candidate in row['candidates']:
                if report.sha(candidate['proof_path']) != candidate['proof_file_sha256']:
                    raise ValueError('Input proof changed')
        return value
    monkeypatch.setattr(report, 'load_inputs', verified_input)
    output = run / 'jobs' / pid / 'output'
    runtime = {'gemma_endpoint': 'http://127.0.0.1:8030/v1', 'seed': 42}
    job = {'schema': 'post-c3-job-v1', 'source_arm': 'B', 'problem': problem, 'candidates': candidates,
           'dry_run': False, 'runtime': runtime, 'output_dir': str(output),
           'input_manifest_path': str(manifest), 'input_manifest_sha256': report.sha(manifest)}
    job_path = write(run / 'jobs' / pid / 'job.json', job)
    lanes = []
    operations = ('expanded', 'no_issues', 'failed', 'skipped_non_c3')
    for index, candidate in enumerate(candidates):
        cid, operation = candidate['candidate_id'], operations[index]
        path = output / 'proofs' / f'{cid}.md'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'Revised proof.\n' if index == 0 else Path(candidate['proof_path']).read_bytes())
        lanes.append({'candidate_id': cid, 'source_stage': candidate['selected_stage'], 'operation': operation,
            'proof_path': str(path), 'proof_file_sha256': report.sha(path), 'proof_sha256': report.text_sha(path),
            'source_proof_path': candidate['proof_path'], 'source_proof_file_sha256': candidate['proof_file_sha256'],
            'changed': index == 0, 'failure': {'error': 'timeout'} if operation == 'failed' else None, 'elapsed_seconds': 2.0})
    summary = write(output / 'summary.json', {'schema': 'post-c3-result-v1', 'source_arm': 'B', 'problem_id': pid,
        'job_sha256': report.sha(job_path), 'input_manifest_path': str(manifest), 'input_manifest_sha256': report.sha(manifest),
        'runtime': runtime, 'release_identity': {'release_sha256': bank['release_sha256']},
        'dry_run': False, 'state': 'completed_with_fallbacks', 'elapsed_seconds': 10.0, 'lanes': lanes})
    plan_path = write(run / 'plan.json', {'schema': 'post-c3-plan-v1', 'dry_run': False,
        'source_archive': str(archive), 'source_arm': 'B', 'input_manifest_path': str(manifest),
        'input_manifest_sha256': report.sha(manifest), 'jobs': [{'problem_id': pid, 'job_path': str(job_path),
        'job_sha256': report.sha(job_path), 'output_dir': str(output), 'log_path': str(run / 'job.log')}]})
    return {'plan': plan_path, 'archive': archive, 'summary': summary, 'config': config}


def grades_for(experiment):
    plan = experiment['plan']
    exported = report.read(report.export_grading(plan))
    rows = []
    for submission in exported['submissions']:
        for index, score in enumerate((3, 5), 1):
            rows.append({'submission_id': submission['submission_id'], 'pass_index': index, 'score': score,
                'proof_file_sha256': submission['proof_file_sha256'], **experiment['config']})
    return write(plan.parent / 'grades.json', {'schema': 'post-c3-grades-v1', 'rows': rows})


def make_unchanged(experiment):
    path = experiment['summary']
    summary = report.read(path)
    lane = summary['lanes'][0]
    Path(lane['proof_path']).write_bytes(Path(lane['source_proof_path']).read_bytes())
    lane.update(changed=False, proof_file_sha256=report.sha(lane['proof_path']), proof_sha256=report.text_sha(lane['proof_path']))
    write(path, summary)


def all_final_scope(experiment):
    """Upgrade the fixture's contract, including its saved C1 final proof."""
    plan_path = experiment['plan']
    plan = report.read(plan_path)
    plan['processing_scope'] = report.ALL_FINALS
    job_path = Path(plan['jobs'][0]['job_path'])
    job = report.read(job_path)
    job['processing_scope'] = report.ALL_FINALS
    write(job_path, job)
    plan['jobs'][0]['job_sha256'] = report.sha(job_path)
    write(plan_path, plan)
    summary = report.read(experiment['summary'])
    summary.update(processing_scope=report.ALL_FINALS, job_sha256=report.sha(job_path))
    summary['lanes'][3]['operation'] = 'no_issues'
    write(experiment['summary'], summary)


def test_exports_only_changed_proofs_blindly_and_preserves_archive(experiment):
    plan, archive = experiment['plan'], experiment['archive']
    before = {str(p): report.sha(p) for p in archive.rglob('*') if p.is_file()}
    exported = report.export_grading(plan)
    payload = report.read(exported)
    assert len(payload['submissions']) == 1
    task = payload['submissions'][0]
    assert task['required_passes'] == [1, 2]
    assert all(task[key] == value for key, value in experiment['config'].items())
    for forbidden in ('candidate_id', 'source_stage', 'baseline_scores', 'grade_paths', 'source_arm'):
        assert forbidden not in exported.read_text()
    assert not (exported.parent / 'grading_key.json').exists()
    assert (plan.parent / 'grading_key.json').is_file()
    assert report.export_grading(plan) == exported
    assert before == {str(p): report.sha(p) for p in archive.rglob('*') if p.is_file()}


def test_pending_report_reuses_unchanged_fallback_and_skipped_grades(experiment):
    path = report.write_report(experiment['plan'])
    result = report.read(path.with_suffix('.json'))
    assert result['quality'] == 'pending'
    assert result['required_new_grade_count'] == 2
    assert result['reused_baseline_grade_count'] == 6
    assert result['all_portfolio']['same_count'] == 3
    assert result['eligible_c3']['lane_count'] == 3
    assert result['problems'][0]['post_mean'] is None
    assert result['all_portfolio']['both_passes_7_retention_pending'] == 1


def test_new_grades_compute_correct_means_and_retention(experiment):
    grades = grades_for(experiment)
    report.write_report(experiment['plan'], grades)
    result = report.read(experiment['plan'].parent / 'REPORT.json')
    assert result['quality'] == 'graded'
    assert result['problems'][0]['baseline_mean'] == 4.75
    assert result['problems'][0]['post_mean'] == 4.0
    assert result['equal_weight_problem_delta'] == -0.75
    assert result['eligible_c3_equal_weight_problem_delta'] == -1
    assert result['all_portfolio']['worse_count'] == 1
    assert result['all_portfolio']['same_count'] == 3
    assert result['all_portfolio']['both_passes_7_retained_count'] == 0
    assert result['all_portfolio']['both_passes_7_retention_denominator'] == 1
    assert result['grades_sha256'] == report.sha(grades)
    assert (experiment['plan'].parent / 'REPORT.csv').is_file()


def test_identical_expansion_needs_no_new_grades(experiment):
    make_unchanged(experiment)
    exported = report.export_grading(experiment['plan'])
    assert report.read(exported)['submissions'] == []
    report.write_report(experiment['plan'])
    result = report.read(experiment['plan'].parent / 'REPORT.json')
    assert result['quality'] == 'graded'
    assert result['reused_baseline_grade_count'] == 8
    assert result['equal_weight_problem_delta'] == 0
    empty = write(experiment['plan'].parent / 'grades.json', {'schema': 'post-c3-grades-v1', 'rows': []})
    report.write_report(experiment['plan'], empty)


@pytest.mark.parametrize('mutation', ['missing', 'duplicate', 'hash', 'model', 'effort', 'policy', 'reference', 'float', 'bool', 'extra_id'])
def test_malformed_or_mismatched_new_grades_are_rejected(experiment, mutation):
    path = grades_for(experiment)
    value = report.read(path)
    if mutation == 'missing':
        value['rows'].pop()
    elif mutation == 'duplicate':
        value['rows'].append(value['rows'][0])
    else:
        field, replacement = {'hash': ('proof_file_sha256', 'c' * 64), 'model': ('model', 'other'),
            'effort': ('reasoning_effort', 'low'), 'policy': ('policy_sha256', 'c' * 64),
            'reference': ('reference_sha256', 'c' * 64), 'float': ('score', 3.0), 'bool': ('score', True),
            'extra_id': ('submission_id', 'unexpected_unchanged_proof')}[mutation]
        value['rows'][0][field] = replacement
    write(path, value)
    with pytest.raises(ValueError):
        report.write_report(experiment['plan'], path)


@pytest.mark.parametrize('mutation', ['proof', 'job_hash', 'source_stage', 'changed_flag', 'missing_lane', 'unfinished', 'skipped_changed'])
def test_worker_output_provenance_is_enforced(experiment, mutation):
    path = experiment['summary']
    value = report.read(path)
    if mutation == 'proof':
        Path(value['lanes'][0]['proof_path']).write_text('Altered proof')
    elif mutation == 'job_hash':
        value['job_sha256'] = 'c' * 64
    elif mutation == 'source_stage':
        value['lanes'][0]['source_stage'] = 'refinement_2'
    elif mutation == 'changed_flag':
        value['lanes'][0]['changed'] = False
    elif mutation == 'missing_lane':
        value['lanes'].pop()
    elif mutation == 'unfinished':
        value['state'] = 'running'
    elif mutation == 'skipped_changed':
        value['lanes'][0]['source_stage'] = 'refinement_1'
        value['lanes'][0]['operation'] = 'skipped_non_c3'
    write(path, value)
    with pytest.raises(ValueError):
        report.export_grading(experiment['plan'])


@pytest.mark.parametrize('artifact', ['comparison.json', 'grades/B/imo2026_p2/t10_r01/pass_1.json',
    'grading/strict_olympiad_policy_v2.txt', 'grading/reference_sources.json', 'proofs/B/imo2026_p2/t10_r01.md'])
def test_baseline_archive_hashes_are_checked(experiment, artifact):
    path = experiment['archive'] / artifact
    path.write_bytes(path.read_bytes() + b' ')
    with pytest.raises(ValueError, match='archive artifact changed'):
        report.export_grading(experiment['plan'])


def test_private_mapping_cannot_be_swapped(experiment):
    report.export_grading(experiment['plan'])
    path = experiment['plan'].parent / 'grading_key.json'
    value = report.read(path)
    value['mapping'][0]['candidate_id'] = 't07_r02'
    write(path, value)
    with pytest.raises(ValueError, match='mapping changed'):
        report.write_report(experiment['plan'])


def test_new_grades_cannot_be_overwritten_by_report(experiment):
    grades = grades_for(experiment)
    path = experiment['plan'].parent / 'REPORT.json'
    path.write_bytes(grades.read_bytes())
    original = path.read_bytes()
    with pytest.raises(ValueError, match='overlaps report output'):
        report.write_report(experiment['plan'], path)
    assert path.read_bytes() == original


def test_dry_run_never_reads_baseline_grades(experiment, monkeypatch):
    plan_path = experiment['plan']
    plan = report.read(plan_path)
    plan['dry_run'] = True
    entry = plan['jobs'][0]
    job_path = Path(entry['job_path'])
    job = report.read(job_path)
    job['dry_run'] = True
    write(job_path, job)
    entry['job_sha256'] = report.sha(job_path)
    write(plan_path, plan)
    summary = report.read(experiment['summary'])
    summary.update(dry_run=True, state='preflight_passed', job_sha256=report.sha(job_path))
    for lane in summary['lanes']:
        proof = Path(lane['proof_path'])
        proof.write_bytes(Path(lane['source_proof_path']).read_bytes())
        lane.update(operation='preflight_only' if lane['source_stage'] == 'refinement_3' else 'skipped_non_c3', changed=False, failure=None,
                    proof_file_sha256=report.sha(proof), proof_sha256=report.text_sha(proof))
    write(experiment['summary'], summary)
    def forbidden(*args, **kwargs):
        raise AssertionError('Baseline grades must not be inspected in a dry run')
    monkeypatch.setattr(report, '_baseline', forbidden)
    path = report.write_report(plan_path)
    assert report.read(path.with_suffix('.json'))['quality'] == 'not_applicable'
    assert not (plan_path.parent / 'grading').exists()
    with pytest.raises(ValueError, match='Dry runs'):
        report.export_grading(plan_path)


def test_unfinished_generation_does_not_read_baseline_grades(experiment, monkeypatch):
    value = report.read(experiment['summary'])
    value['state'] = 'running'
    write(experiment['summary'], value)
    def forbidden(*args, **kwargs):
        raise AssertionError('Grade access preceded generation completion')
    monkeypatch.setattr(report, '_baseline', forbidden)
    with pytest.raises(ValueError, match='must finish'):
        report.write_report(experiment['plan'])


def test_actual_published_b_baseline_grades_are_bound_without_new_grading():
    from harnesses.post_c3_completion import inputs
    bank = inputs.load_archive(inputs.DEFAULT_ARCHIVE, None, source_arm='B')
    rows = [{'problem_id': row['problem']['problem_id'], 'problem': row['problem'], 'source': candidate}
            for row in bank['problems'] for candidate in row['candidates']]
    baseline = report._baseline(bank, rows)
    assert len(baseline) == 24
    assert sum(len(row['scores']) for row in baseline.values()) == 48
    assert {row['config']['model'] for row in baseline.values()} == {'gpt-5.6-sol'}
    assert {row['config']['reasoning_effort'] for row in baseline.values()} == {'xhigh'}
    assert sum(row['source']['selected_stage'] == 'refinement_3' for row in rows) == 23


def test_all_saved_finals_includes_expanded_c1_and_reports_original_stages(experiment):
    all_final_scope(experiment)
    summary = report.read(experiment['summary'])
    lane = summary['lanes'][3]
    Path(lane['proof_path']).write_text('Completion of the saved C1 final proof.\n')
    lane.update(operation='expanded', changed=True, proof_file_sha256=report.sha(lane['proof_path']),
                proof_sha256=report.text_sha(lane['proof_path']))
    write(experiment['summary'], summary)
    grades = grades_for(experiment)
    exported = report.read(experiment['plan'].parent / 'grading/input_manifest.json')
    assert len(exported['submissions']) == 2
    path = report.write_report(experiment['plan'], grades)
    result = report.read(path.with_suffix('.json'))
    assert result['processing_scope'] == 'all_saved_final_proofs'
    assert result['eligible_final_proof_count'] == result['completion_eligible']['lane_count'] == 4
    assert result['original_c3_source_count'] == result['original_c3']['lane_count'] == 3
    assert result['source_stage_counts'] == {'refinement_3': 3, 'refinement_1': 1}
    assert result['problems'][0]['eligible_final_proof_count'] == 4
    assert result['required_new_grade_count'] == 4
    assert result['reused_baseline_grade_count'] == 4
    assert result['equal_weight_problem_delta'] == -0.25
    assert result['original_c3_equal_weight_problem_delta'] == -1
    assert result['all_portfolio']['improved_count'] == result['all_portfolio']['worse_count'] == 1
    assert result['lanes'][3]['source_stage'] == 'refinement_1'
    assert result['lanes'][3]['eligible_for_completion'] is True
    assert result['lanes'][3]['original_c3'] is False
    assert 'including proofs retained from earlier refinement stages' in path.read_text()


def test_all_saved_finals_rejects_skipping_c1(experiment):
    all_final_scope(experiment)
    summary = report.read(experiment['summary'])
    summary['lanes'][3]['operation'] = 'skipped_non_c3'
    write(experiment['summary'], summary)
    with pytest.raises(ValueError, match='eligible saved final proof was skipped'):
        report.write_report(experiment['plan'])


def test_all_saved_finals_dry_run_preflights_all_four_without_grades(experiment, monkeypatch):
    all_final_scope(experiment)
    plan_path = experiment['plan']
    plan = report.read(plan_path)
    plan['dry_run'] = True
    job_path = Path(plan['jobs'][0]['job_path'])
    job = report.read(job_path)
    job['dry_run'] = True
    write(job_path, job)
    plan['jobs'][0]['job_sha256'] = report.sha(job_path)
    write(plan_path, plan)
    summary = report.read(experiment['summary'])
    summary.update(dry_run=True, state='preflight_passed', job_sha256=report.sha(job_path))
    for lane in summary['lanes']:
        proof = Path(lane['proof_path'])
        proof.write_bytes(Path(lane['source_proof_path']).read_bytes())
        lane.update(operation='preflight_only', changed=False, failure=None,
                    proof_file_sha256=report.sha(proof), proof_sha256=report.text_sha(proof))
    write(experiment['summary'], summary)
    def forbidden(*args, **kwargs):
        raise AssertionError('No baseline grades in a dry run')
    monkeypatch.setattr(report, '_baseline', forbidden)
    result = report.read(report.write_report(plan_path).with_suffix('.json'))
    assert result['eligible_final_proof_count'] == 4
    assert result['original_c3_source_count'] == 3
    assert result['quality'] == 'not_applicable'
    assert not (plan_path.parent / 'grading').exists()


@pytest.mark.parametrize('record, value', [('job', None), ('summary', None),
    ('job', 'c3_only'), ('summary', 'c3_only'), ('plan', 'unknown')])
def test_new_processing_scope_must_match_every_record(experiment, record, value):
    all_final_scope(experiment)
    plan_path = experiment['plan']
    plan = report.read(plan_path)
    job_path = Path(plan['jobs'][0]['job_path'])
    path = {'job': job_path, 'summary': experiment['summary'], 'plan': plan_path}[record]
    changed = report.read(path)
    if value is None:
        changed.pop('processing_scope')
    else:
        changed['processing_scope'] = value
    write(path, changed)
    if record == 'job':
        plan['jobs'][0]['job_sha256'] = report.sha(job_path)
        write(plan_path, plan)
        summary = report.read(experiment['summary'])
        summary['job_sha256'] = report.sha(job_path)
        write(experiment['summary'], summary)
    with pytest.raises(ValueError, match='processing scope'):
        report.write_report(plan_path)


def test_legacy_plan_stays_c3_only_and_is_not_reinterpreted(experiment):
    path = report.write_report(experiment['plan'])
    result = report.read(path.with_suffix('.json'))
    assert result['processing_scope'] == 'c3_only'
    assert result['eligible_final_proof_count'] == 3
    assert result['completion_eligible']['lane_count'] == 3
    assert result['all_portfolio']['lane_count'] == 4
    assert result['lanes'][3]['operation'] == 'skipped_non_c3'
    assert result['lanes'][3]['eligible_for_completion'] is False
    assert 'Legacy C3-only scope' in path.read_text()


def test_legacy_plan_cannot_claim_new_summary_scope(experiment):
    summary = report.read(experiment['summary'])
    summary['processing_scope'] = report.ALL_FINALS
    write(experiment['summary'], summary)
    with pytest.raises(ValueError, match='processing scopes must match'):
        report.write_report(experiment['plan'])
