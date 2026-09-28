"""Confined patch replay and blinded grading of raw versus repaired proofs."""
import json
from pathlib import Path
import sys
from types import ModuleType

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harnesses.block_local_completion import blocks, report
from test_post_c3_report import experiment as old_experiment

ISSUES = '<ISSUES>\n<ISSUE id="I1" blocks="B0002">Establish the omitted implication.</ISSUE>\n</ISSUES>'


def write(path, value):
    report.write(path, value)
    return path


def proof_hash(data):
    return report.hashlib.sha256(data.decode().strip().encode()).hexdigest()


def bank_artifacts(directory, data):
    directory.mkdir(parents=True, exist_ok=True)
    source = directory / 'source.md'
    source.write_bytes(data)
    bank = blocks.build_blocks(data)
    mapping = write(directory / 'blocks.json', bank)
    rendered = directory / 'rendered.txt'
    rendered.write_bytes(blocks.render_blocks(bank).encode())
    return bank, {'source_path': str(source), 'source_file_sha256': report.sha(source),
                  'blockmap_path': str(mapping), 'blockmap_sha256': report.sha(mapping),
                  'rendered_path': str(rendered), 'rendered_sha256': report.sha(rendered)}


def issue_artifacts(directory, bank, text):
    directory.mkdir(parents=True, exist_ok=True)
    raw = directory / 'issues.txt'
    raw.write_text(text)
    issues = blocks.parse_issues(text, bank)
    parsed = directory / 'issues.json'
    parsed.write_text(json.dumps(issues))
    return issues, {'issues_path': str(parsed), 'issues_file_sha256': report.sha(parsed),
                    'issues_raw_path': str(raw), 'issues_raw_file_sha256': report.sha(raw)}


def patch_artifacts(directory, bank, data, issues, text):
    directory.mkdir(parents=True, exist_ok=True)
    raw = directory / 'patch.txt'
    raw.write_text(text)
    applied = blocks.parse_and_apply(text, bank, data, issues)
    audit = write(directory / 'audit.json', applied['audit'])
    return applied, {'status': applied['status'], 'raw_patch_path': str(raw),
                     'raw_patch_file_sha256': report.sha(raw), 'audit_path': str(audit),
                     'audit_file_sha256': report.sha(audit), 'patches': applied['patches']}


def replacement(text='A locally justified replacement.', block='B0002'):
    return f'<PATCHES>\n<REPLACE blocks="{block}" issues="I1">\n{text}\n</REPLACE>\n</PATCHES>'


@pytest.fixture
def experiment(old_experiment, monkeypatch):
    result = old_experiment
    plan_path = result['plan']
    plan = report.read(plan_path)
    manifest_path = Path(plan['input_manifest_path'])
    bank = report.read(manifest_path)
    bank.update(schema='block-local-inputs-v1', source_arm='raw')
    candidates = bank['problems'][0]['candidates']
    for candidate in candidates:
        data = f"First claim for {candidate['candidate_id']}.\n\nMissing derivation.\n\nFinal conclusion.\n".encode()
        path = Path(candidate['proof_path'])
        path.write_bytes(data)
        candidate.update(proof_file_sha256=report.sha(path), proof_sha256=proof_hash(data), selected_stage='raw')
    write(manifest_path, bank)
    # The input loader is independently covered by its own suite. Verify the
    # fixture's raw snapshot before exercising every report-side provenance link.
    fake_inputs = ModuleType('harnesses.block_local_completion.inputs')
    def verify_manifest(path, expected_sha=None):
        value = report.read(path)
        if expected_sha is not None and report.sha(path) != expected_sha:
            raise ValueError('Input manifest changed')
        for row in value['problems']:
            for candidate in row['candidates']:
                if report.sha(candidate['proof_path']) != candidate['proof_file_sha256']:
                    raise ValueError('Raw input changed')
        return value
    fake_inputs.verify_manifest = verify_manifest
    monkeypatch.setitem(sys.modules, fake_inputs.__name__, fake_inputs)
    import harnesses.block_local_completion as package
    monkeypatch.setattr(package, 'inputs', fake_inputs, raising=False)
    monkeypatch.setattr(report, 'GRADING_ARCHIVE', result['archive'])
    entry = plan['jobs'][0]
    job_path = Path(entry['job_path'])
    job = report.read(job_path)
    job.update(schema='block-local-job-v1', experiment=report.EXPERIMENT,
               strategy='block',
               source_arm='raw', processing_scope=report.SCOPE,
               pipeline_config=dict(report.PIPELINE_CONFIG),
               input_manifest_sha256=report.sha(manifest_path), candidates=candidates)
    job['runtime']['repair_temperature'] = 0.7
    write(job_path, job)
    entry['job_sha256'] = report.sha(job_path)
    plan.update(schema='block-local-plan-v1', experiment=report.EXPERIMENT,
                strategy='block', terminal_stage=report.TERMINAL_STAGES['block'],
                repair_temperature=0.7,
                pipeline_config=dict(report.PIPELINE_CONFIG), refinements_enabled=False,
                source_arm='raw', processing_scope=report.SCOPE, input_manifest_sha256=report.sha(manifest_path))
    write(plan_path, plan)
    summary = report.read(result['summary'])
    summary.update(schema='block-local-result-v1', experiment=report.EXPERIMENT,
                   strategy='block',
                   pipeline_config=dict(report.PIPELINE_CONFIG),
                   source_arm='raw', processing_scope=report.SCOPE,
                   input_manifest_sha256=report.sha(manifest_path), job_sha256=report.sha(job_path), runtime=job['runtime'])
    output = Path(entry['output_dir'])
    for index, (lane, candidate) in enumerate(zip(summary['lanes'], candidates)):
        data = Path(candidate['proof_path']).read_bytes()
        directory = output / 'artifacts' / candidate['candidate_id']
        blockbank, provenance = bank_artifacts(directory / 'original', data)
        lane.update(source_stage='raw', source_proof_path=candidate['proof_path'],
                    source_proof_file_sha256=candidate['proof_file_sha256'], block_provenance=provenance,
                    block_patch={'status': 'not_run'}, adopted_from='original', local_result='invalid_or_failed',
                    phase_elapsed_seconds={'lazy_check': 0.25},
                    operation='failed', failure={'error': 'model failure'})
        final = data
        if index in (0, 2):
            issues, issue_record = issue_artifacts(directory / 'expansion', blockbank, ISSUES)
            text = replacement() if index == 0 else 'CANNOT_REPAIR_LOCALLY'
            applied, patch_record = patch_artifacts(directory / 'expansion', blockbank, data, issues, text)
            lane['block_patch'] = {**issue_record, **patch_record}
            if index == 2:
                lane['local_result'] = 'cannot_repair_locally'
            else:
                final = applied['proof_bytes']
                intermediate = directory / 'intermediate.md'
                intermediate.write_bytes(final)
                fresh, fresh_provenance = bank_artifacts(directory / 'intermediate', final)
                _, audit = issue_artifacts(directory / 'audit', fresh, 'NO_ISSUES')
                lane.update(operation='expanded', failure=None, local_result='patched_audit_passed', adopted_from='expansion',
                    post_expansion={'proof_path': str(intermediate), 'proof_file_sha256': report.sha(intermediate),
                                    'proof_sha256': proof_hash(final), 'block_provenance': fresh_provenance,
                                    'audit': {'status': 'no_issues', **audit}, 'resolve': {'status': 'not_run'}})
        elif index == 1:
            _, issue_record = issue_artifacts(directory / 'scan', blockbank, 'NO_ISSUES')
            lane.update(operation='no_issues', failure=None, local_result='no_issues',
                        block_patch={'status': 'no_issues', **issue_record})
        Path(lane['proof_path']).write_bytes(final)
        lane.update(proof_file_sha256=report.sha(lane['proof_path']), proof_sha256=proof_hash(final), changed=final != data)
    write(result['summary'], summary)
    return result


def grades_for(experiment):
    exported = report.read(report.export_grading(experiment['plan']))
    key = report.read(experiment['plan'].parent / 'grading_key.json')
    kinds = {item['submission_id']: item['kind'] for item in key['mapping']}
    rows = []
    for item in exported['submissions']:
        for index in (1, 2):
            rows.append({'submission_id': item['submission_id'], 'pass_index': index,
                'score': 7 if kinds[item['submission_id']] == 'repaired' else 3,
                'proof_file_sha256': item['proof_file_sha256'], **{key: item[key] for key in report.GRADE_CONFIG}})
    return write(experiment['plan'].parent / 'grades.json', {'schema': 'block-local-grades-v1', 'rows': rows})


def test_authorized_patch_replayed_and_only_changed_final_is_added_to_raw_grading(experiment):
    path = report.export_grading(experiment['plan'])
    value = report.read(path)
    assert len(value['submissions']) == 5  # all four raw proofs plus one repaired
    assert all(item['required_passes'] == [1, 2] for item in value['submissions'])
    for hidden in ('candidate_id', 'kind', 'baseline_scores', 'local_result', 'block_ids'):
        assert hidden not in path.read_text()
    key = report.read(experiment['plan'].parent / 'grading_key.json')
    assert [item['kind'] for item in key['mapping']].count('raw') == 4
    assert [item['kind'] for item in key['mapping']].count('repaired') == 1
    assert report.export_grading(experiment['plan']) == path


def test_grade_import_uses_new_raw_scores_and_reuses_unchanged_finals(experiment):
    grades = grades_for(experiment)
    path = report.write_report(experiment['plan'], grades)
    value = report.read(path.with_suffix('.json'))
    assert value['quality'] == 'graded'
    assert value['problems'][0]['raw_mean'] == 3
    assert value['problems'][0]['repaired_mean'] == 4
    assert value['equal_weight_problem_delta'] == 1
    assert value['required_grade_count'] == 10
    assert value['changed_source_block_count'] == 1
    assert value['local_result_counts']['cannot_repair_locally'] == 1
    assert value['all_portfolio']['same_count'] == 3
    assert value['all_portfolio']['improved_count'] == 1
    assert value['summed_lane_phase_seconds']['lazy_check'] == 1
    assert 'No historical B' in path.read_text()
    assert 'does not establish mathematical correctness' in path.read_text()


def test_self_consistently_rehashed_final_outside_authorized_patch_is_rejected(experiment):
    summary = report.read(experiment['summary'])
    lane = summary['lanes'][0]
    proof = Path(lane['proof_path'])
    proof.write_bytes(proof.read_bytes().replace(b'Final conclusion.', b'Unauthorized different conclusion.'))
    lane.update(proof_file_sha256=report.sha(proof), proof_sha256=proof_hash(proof.read_bytes()))
    write(experiment['summary'], summary)
    with pytest.raises(ValueError, match='audited expansion'):
        report.export_grading(experiment['plan'])
    assert not (experiment['plan'].parent / 'grading').exists()


@pytest.mark.parametrize('target', ['plan', 'job', 'summary'])
def test_experiment_identity_mismatch_is_rejected(experiment, target):
    plan = report.read(experiment['plan'])
    path = {'plan': experiment['plan'], 'job': Path(plan['jobs'][0]['job_path']), 'summary': experiment['summary']}[target]
    value = report.read(path)
    value['experiment'] = 'old_full_rewrite'
    write(path, value)
    if target == 'job':
        plan['jobs'][0]['job_sha256'] = report.sha(path)
        write(experiment['plan'], plan)
    with pytest.raises(ValueError, match='experiment'):
        report.write_report(experiment['plan'])


@pytest.mark.parametrize('field', ['raw_patch_path', 'issues_raw_path', 'issues_path', 'audit_path'])
def test_bound_patch_artifact_mutation_is_rejected(experiment, field):
    patch = report.read(experiment['summary'])['lanes'][0]['block_patch']
    path = Path(patch[field])
    path.write_bytes(path.read_bytes() + b' ')
    with pytest.raises(ValueError, match='artifact hash changed'):
        report.export_grading(experiment['plan'])


def resolve_lane(experiment, *, decline=False):
    summary = report.read(experiment['summary'])
    lane = summary['lanes'][0]
    post = lane['post_expansion']
    intermediate = Path(post['proof_path']).read_bytes()
    bank = report.read(post['block_provenance']['blockmap_path'])
    directory = Path(post['proof_path']).parent
    issues, issue_record = issue_artifacts(directory / 'audit', bank, ISSUES)
    text = 'CANNOT_REPAIR_LOCALLY' if decline else replacement('Resolved local implication.')
    applied, patch_record = patch_artifacts(directory / 'resolve', bank, intermediate, issues, text)
    post.update(audit={'status': 'issues', **issue_record}, resolve=patch_record)
    final = Path(lane['source_proof_path']).read_bytes() if decline else applied['proof_bytes']
    Path(lane['proof_path']).write_bytes(final)
    lane.update(local_result='cannot_repair_locally' if decline else 'resolved',
                adopted_from='original' if decline else 'resolve', operation='failed' if decline else 'expanded',
                failure={'error': 'cannot repair locally'} if decline else None,
                changed=not decline, proof_file_sha256=report.sha(lane['proof_path']), proof_sha256=proof_hash(final))
    write(experiment['summary'], summary)


def test_audit_then_resolve_chain_uses_fresh_intermediate_bank(experiment):
    resolve_lane(experiment)
    path = report.write_report(experiment['plan'])
    value = report.read(path.with_suffix('.json'))
    assert value['local_result_counts']['resolved'] == 1
    assert value['changed_source_block_count'] == 2
    assert value['audit_outcome_counts']['issues'] == 1
    assert value['resolve_outcome_counts']['patched'] == 1


def test_resolve_decline_restores_raw_and_reuses_only_raw_grading(experiment):
    resolve_lane(experiment, decline=True)
    exported = report.read(report.export_grading(experiment['plan']))
    assert len(exported['submissions']) == 4
    report.write_report(experiment['plan'], grades_for(experiment))
    value = report.read(experiment['plan'].parent / 'REPORT.json')
    assert value['equal_weight_problem_delta'] == 0
    assert value['local_result_counts']['cannot_repair_locally'] == 2


def test_failed_resolve_noop_diagnostic_is_replayed_but_original_is_exported(experiment):
    resolve_lane(experiment)
    summary = report.read(experiment['summary'])
    lane = summary['lanes'][0]
    post = lane['post_expansion']
    intermediate = Path(post['proof_path']).read_bytes()
    bank = report.read(post['block_provenance']['blockmap_path'])
    issues = json.loads(Path(post['audit']['issues_path']).read_bytes())
    _, saved = patch_artifacts(Path(post['proof_path']).parent / 'resolve', bank, intermediate, issues,
                               replacement(bank['blocks'][1]['text']))
    saved['status'] = 'failed'
    post['resolve'] = saved
    source = Path(lane['source_proof_path']).read_bytes()
    Path(lane['proof_path']).write_bytes(source)
    lane.update(operation='failed', local_result='invalid_or_failed', adopted_from='original', changed=False,
                failure={'stage': 'resolve', 'error': 'Patch did not repair any bytes'},
                proof_file_sha256=report.sha(lane['proof_path']), proof_sha256=proof_hash(source))
    write(experiment['summary'], summary)
    assert len(report.read(report.export_grading(experiment['plan']))['submissions']) == 4
    Path(saved['audit_path']).write_text('{}')
    with pytest.raises(ValueError, match='artifact hash changed'):
        report.write_report(experiment['plan'])


def test_live_segmentation_failure_preserves_raw_without_fabricated_block_map(experiment):
    summary = report.read(experiment['summary'])
    lane = summary['lanes'][3]
    lane.pop('block_provenance')
    lane['failure'] = {'stage': 'segmentation', 'error': 'Unbalanced source environment'}
    write(experiment['summary'], summary)
    report.write_report(experiment['plan'])
    value = report.read(experiment['plan'].parent / 'REPORT.json')
    assert value['lanes'][3]['patch_provenance']['confinement_check'] == 'unchanged_original_after_segmentation_failure'


@pytest.mark.parametrize('target', ['plan', 'job', 'summary'])
def test_changed_pipeline_limits_are_rejected(experiment, target):
    plan = report.read(experiment['plan'])
    path = {'plan': experiment['plan'], 'job': Path(plan['jobs'][0]['job_path']), 'summary': experiment['summary']}[target]
    value = report.read(path)
    value['pipeline_config']['max_resolve_passes'] = 2
    write(path, value)
    if target == 'job':
        plan['jobs'][0]['job_sha256'] = report.sha(path)
        write(experiment['plan'], plan)
    with pytest.raises(ValueError, match='pipeline configuration'):
        report.write_report(experiment['plan'])


def test_same_problem_id_cannot_attach_reference_to_a_different_statement(experiment):
    rows = report._load(experiment['plan'])[2]
    rows[0]['problem']['claim'] = 'An unrelated problem with a reused IMO identifier.'
    rows[0]['problem']['problem_sha256'] = proof_hash(rows[0]['problem']['claim'].encode())
    with pytest.raises(ValueError, match='canonical grading reference'):
        report._grading_config(rows)


def test_regressions_and_lost_full_credit_are_visible(experiment):
    path = grades_for(experiment)
    value = report.read(path)
    key = report.read(experiment['plan'].parent / 'grading_key.json')
    kinds = {item['submission_id']: item['kind'] for item in key['mapping']}
    for row in value['rows']:
        row['score'] = 3 if kinds[row['submission_id']] == 'repaired' else 7
    write(path, value)
    output = report.write_report(experiment['plan'], path)
    result = report.read(output.with_suffix('.json'))
    assert result['all_portfolio']['worse_count'] == 1
    assert result['all_portfolio']['both_passes_7_retained_count'] == 3
    assert 'worsened 1' in output.read_text()
    assert 'fallback is not counted as mathematical success' in output.read_text()


def test_resolve_cannot_replace_intermediate_outside_recorded_patch(experiment):
    resolve_lane(experiment)
    summary = report.read(experiment['summary'])
    lane = summary['lanes'][0]
    path = Path(lane['proof_path'])
    path.write_bytes(path.read_bytes() + b'Extra unauthorized conclusion.\n')
    lane.update(proof_file_sha256=report.sha(path), proof_sha256=proof_hash(path.read_bytes()))
    write(experiment['summary'], summary)
    with pytest.raises(ValueError, match='authorized resolve'):
        report.export_grading(experiment['plan'])


@pytest.mark.parametrize('change', ['missing', 'duplicate', 'hash', 'model', 'reference', 'bool'])
def test_invalid_grade_contract_is_rejected(experiment, change):
    path = grades_for(experiment)
    value = report.read(path)
    if change == 'missing':
        value['rows'].pop()
    elif change == 'duplicate':
        value['rows'].append(value['rows'][0])
    else:
        key, replacement_value = {'hash': ('proof_file_sha256', '0' * 64), 'model': ('model', 'other'),
                                  'reference': ('reference_sha256', '0' * 64), 'bool': ('score', True)}[change]
        value['rows'][0][key] = replacement_value
    write(path, value)
    with pytest.raises(ValueError):
        report.write_report(experiment['plan'], path)


def make_preflight(experiment):
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
        final = Path(lane['source_proof_path']).read_bytes()
        Path(lane['proof_path']).write_bytes(final)
        lane.update(operation='preflight_only', local_result='preflight_only', adopted_from='original',
                    block_patch={'status': 'not_run'}, changed=False, failure=None,
                    proof_file_sha256=report.sha(lane['proof_path']), proof_sha256=proof_hash(final))
        lane.pop('post_expansion', None)
    write(experiment['summary'], summary)
    return plan_path


def test_preflight_never_reads_grader_configuration(experiment, monkeypatch):
    plan_path = make_preflight(experiment)
    def forbidden(*args, **kwargs):
        raise AssertionError('No grader configuration access in preflight')
    monkeypatch.setattr(report, '_grading_config', forbidden)
    output = report.write_report(plan_path)
    assert report.read(output.with_suffix('.json'))['quality'] == 'not_applicable'
    assert not (plan_path.parent / 'grading').exists()


def test_failed_dry_segmentation_cannot_claim_preflight_passed(experiment):
    make_preflight(experiment)
    summary = report.read(experiment['summary'])
    lane = summary['lanes'][0]
    lane.pop('block_provenance')
    lane.update(operation='failed', local_result='invalid_or_failed', failure={'stage': 'segmentation'})
    write(experiment['summary'], summary)
    with pytest.raises(ValueError, match='Invalid operation'):
        report.write_report(experiment['plan'])
