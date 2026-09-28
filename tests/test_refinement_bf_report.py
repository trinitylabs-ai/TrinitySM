"""Blinding, fallback inclusion, and paired grading integrity checks."""
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harnesses.refinement_bf_ablation import inputs, report


def write(path, value):
    inputs.write(path, value)
    return path


@pytest.fixture
def plan_path(tmp_path):
    root = tmp_path.resolve()
    pid, pair_id = 'imo2026_p2', 'imo2026_p2__seed42'
    claim = 'Prove that every square is nonnegative.'
    problem = {'problem_id': pid, 'problem_number': 2, 'claim': claim,
               'problem_sha256': report.hashlib.sha256(claim.encode()).hexdigest()}
    candidates = []
    for cid in inputs.CANDIDATES:
        path = root / 'inputs' / pid / f'{cid}.md'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(f'\r\nInitial proof {cid}.\r\n'.encode())
        candidates.append({'candidate_id': cid, 'proof_path': str(path),
            'proof_file_sha256': report.sha(path), 'proof_sha256': inputs.text_hash(path)})
    manifest = write(root / 'inputs/manifest.json', {'schema': inputs.SCHEMA,
        'release_sha256': report.sha(inputs.RELEASE / 'release.json'),
        'problems': [{'problem': problem, 'candidates': candidates}], 'source_hashes': {}})
    pair = {'problem_id': pid, 'pair_id': pair_id, 'pair_seed': 42,
            'arm_order': ['role_specific', 'original'], 'arms': {}}
    for variant in report.VARIANTS:
        output = root / 'arms' / variant
        runtime = {'seed_namespace': 'paired:42', 'workers': 4}
        job = {'schema': 'refinement-bf-job-v1', 'variant': variant, 'pair_id': pair_id,
               'pair_seed': 42, 'problem': problem, 'candidates': candidates, 'runtime': runtime,
               'dry_run': False, 'output_dir': str(output), 'input_manifest_path': str(manifest),
               'input_manifest_sha256': report.sha(manifest)}
        job_path = write(root / 'jobs' / f'{variant}.json', job)
        pair['arms'][variant] = {'job_path': str(job_path), 'job_sha256': report.sha(job_path),
            'output_dir': str(output), 'log_path': str(root / (variant + '.log'))}
        lanes = []
        for index, candidate in enumerate(candidates):
            cid = candidate['candidate_id']
            stage = ('lazy_checked' if variant == 'original' else 'refinement_2') if index == 0 else 'refinement_3'
            path = output / 'proofs' / f'{cid}.md'
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(Path(candidate['proof_path']).read_bytes() if stage == 'lazy_checked'
                             else f'Final proof for lane {index}.\n'.encode())
            stages = report.STAGES[1:report.STAGES.index(stage) + 1]
            checkpoints = [{'stage': s, 'proof_path': str(path), 'proof_sha256': inputs.text_hash(path)} for s in stages]
            failure = None if stage == 'refinement_3' else {'stage': report.STAGES[report.STAGES.index(stage) + 1], 'error': 'timeout'}
            lanes.append({'candidate_id': cid, 'selected_stage': stage, 'proof_path': str(path),
                          'proof_file_sha256': report.sha(path), 'proof_sha256': inputs.text_hash(path),
                          'checkpoints': checkpoints, 'failure': failure, 'elapsed_seconds': 5.0})
        write(output / 'summary.json', {'schema': 'refinement-bf-arm-v1', 'variant': variant,
            'problem_id': pid, 'pair_id': pair_id, 'pair_seed': 42, 'state': 'completed_with_fallbacks',
            'job_sha256': report.sha(job_path), 'runtime': runtime, 'input_manifest_path': str(manifest),
            'input_manifest_sha256': report.sha(manifest), 'elapsed_seconds': 20.0, 'lanes': lanes,
            'release_identity': {'release_sha256': report.sha(inputs.RELEASE / 'release.json')}})
    return write(root / 'plan.json', {'schema': 'refinement-bf-plan-v1', 'dry_run': False,
        'input_manifest_path': str(manifest), 'input_manifest_sha256': report.sha(manifest), 'pairs': [pair]})


def make_grades(plan_path):
    exported = report.export_grading(plan_path)
    submissions = report.read(exported)['submissions']
    mapping = {row['submission_id']: row for row in report.read(plan_path.parent / 'grading_key.json')['mapping']}
    rows = []
    for submission in submissions:
        variant = mapping[submission['submission_id']]['variant']
        for index in (1, 2):
            rows.append({'submission_id': submission['submission_id'], 'pass_index': index,
                'score': 7 if variant == 'role_specific' else (3 if index == 1 else 5),
                'proof_file_sha256': submission['proof_file_sha256'], 'grader_model': 'same-grader',
                'protocol': submission['grading_protocol']})
    return write(plan_path.parent / 'grades.json', {'schema': 'refinement-bf-grades-v1', 'rows': rows})


def test_blinded_export_includes_every_fallback_and_is_idempotent(plan_path):
    path = report.export_grading(plan_path)
    original = path.read_bytes()
    manifest = report.read(path)
    assert len(manifest['submissions']) == 8
    assert [row['submission_id'] for row in manifest['submissions']] == sorted(row['submission_id'] for row in manifest['submissions'])
    text = path.read_text()
    for hidden in ('role_specific', 'candidate_id', 'selected_stage', 'pair_seed', 'variant'):
        assert hidden not in text
    assert not (path.parent / 'grading_key.json').exists()
    key = report.read(plan_path.parent / 'grading_key.json')
    assert {row['selected_stage'] for row in key['mapping']} == {'lazy_checked', 'refinement_2', 'refinement_3'}
    assert all(row['required_passes'] == [1, 2] for row in manifest['submissions'])
    assert report.export_grading(plan_path).read_bytes() == original


def test_pending_report_makes_no_quality_claim(plan_path):
    path = report.write_report(plan_path)
    result = report.read(path.with_suffix('.json'))
    assert result['quality'] == 'pending'
    assert all(arm['fallback_count'] == 1 for arm in result['arms'])
    assert 'No quality gain or loss' in path.read_text()
    assert all(arm['elapsed_seconds'] == 20 for arm in result['arms'])


def test_paired_report_averages_both_passes_and_all_four_lanes(plan_path):
    grades = make_grades(plan_path)
    report.write_report(plan_path, grades)
    result = report.read(plan_path.parent / 'REPORT.json')
    arms = {row['variant']: row for row in result['arms']}
    assert arms['original']['mean_score'] == 4
    assert arms['role_specific']['mean_score'] == 7
    assert result['mean_problem_delta'] == 3
    assert arms['original']['grading_disagreement_count'] == 4
    assert arms['role_specific']['both_passes_7_rate'] == 1
    assert result['grades_sha256'] == report.sha(grades)


@pytest.mark.parametrize('mutation', ['missing', 'duplicate', 'hash', 'protocol', 'float', 'bool', 'model'])
def test_bad_grades_are_rejected(plan_path, mutation):
    path = make_grades(plan_path)
    value = report.read(path)
    if mutation == 'missing':
        value['rows'].pop()
    elif mutation == 'duplicate':
        value['rows'].append(value['rows'][0])
    else:
        field, changed = {'hash': ('proof_file_sha256', '0' * 64), 'protocol': ('protocol', 'wrong'),
                          'float': ('score', 3.5), 'bool': ('score', True), 'model': ('grader_model', 'other')}[mutation]
        value['rows'][0][field] = changed
    write(path, value)
    with pytest.raises(ValueError):
        report.write_report(plan_path, path)


@pytest.mark.parametrize('mutation', ['proof', 'summary_job', 'job', 'input', 'missing_lane', 'unfinished'])
def test_changed_provenance_is_rejected(plan_path, mutation):
    plan = report.read(plan_path)
    arm = plan['pairs'][0]['arms']['original']
    summary_path = Path(arm['output_dir']) / 'summary.json'
    summary = report.read(summary_path)
    if mutation == 'proof':
        Path(summary['lanes'][0]['proof_path']).write_text('Changed proof')
    elif mutation == 'job':
        job = report.read(arm['job_path'])
        job['pair_seed'] = 43
        write(Path(arm['job_path']), job)
    elif mutation == 'input':
        Path(plan['input_manifest_path']).write_text('{}')
    else:
        if mutation == 'summary_job':
            summary['job_sha256'] = '0' * 64
        elif mutation == 'missing_lane':
            summary['lanes'].pop()
        elif mutation == 'unfinished':
            summary['state'] = 'running'
        write(summary_path, summary)
    with pytest.raises(ValueError):
        report.export_grading(plan_path)


def test_private_mapping_cannot_be_swapped(plan_path):
    report.export_grading(plan_path)
    path = plan_path.parent / 'grading_key.json'
    value = report.read(path)
    value['mapping'][0]['variant'] = 'role_specific'
    write(path, value)
    with pytest.raises(ValueError, match='mapping changed'):
        report.write_report(plan_path)


def test_modified_exported_proof_is_rejected(plan_path):
    path = report.export_grading(plan_path)
    proof = Path(report.read(path)['submissions'][0]['proof_path'])
    proof.write_text('Changed exported proof')
    with pytest.raises(ValueError, match='Exported proof changed'):
        report.write_report(plan_path)


def test_grade_input_cannot_be_overwritten_by_report(plan_path):
    grades = make_grades(plan_path)
    path = plan_path.parent / 'REPORT.json'
    original = grades.read_bytes()
    path.write_bytes(original)
    with pytest.raises(ValueError, match='overlaps report output'):
        report.write_report(plan_path, path)
    assert path.read_bytes() == original


@pytest.mark.parametrize('pid, expected', [('imo2026_p2', 'olympiad_strict_scoring_v2'),
    ('PB-Basic-001', 'imobench-proof-autograder-b5-v1'), ('PB-Advanced-009', 'imobench-proof-autograder-b5-v1'),
    ('custom_problem', 'unknown')])
def test_protocol_assignment_is_explicit(pid, expected):
    assert report.protocol(pid) == expected


def test_dry_run_report_has_no_export_or_quality(plan_path):
    plan = report.read(plan_path)
    plan['dry_run'] = True
    manifest = report.read(plan['input_manifest_path'])
    candidates = manifest['problems'][0]['candidates']
    for arm in plan['pairs'][0]['arms'].values():
        job_path = Path(arm['job_path'])
        job = report.read(job_path)
        job['dry_run'] = True
        write(job_path, job)
        arm['job_sha256'] = report.sha(job_path)
        summary_path = Path(arm['output_dir']) / 'summary.json'
        summary = report.read(summary_path)
        summary.update(state='preflight_passed', job_sha256=report.sha(job_path))
        for lane, candidate in zip(summary['lanes'], candidates):
            Path(lane['proof_path']).write_bytes(Path(candidate['proof_path']).read_bytes())
            lane.update(selected_stage='lazy_checked', checkpoints=[], failure=None,
                        proof_file_sha256=candidate['proof_file_sha256'], proof_sha256=candidate['proof_sha256'])
        write(summary_path, summary)
    write(plan_path, plan)
    path = report.write_report(plan_path)
    assert report.read(path.with_suffix('.json'))['quality'] == 'not_applicable'
    assert not (plan_path.parent / 'grading').exists()
    with pytest.raises(ValueError, match='Dry runs'):
        report.export_grading(plan_path)
