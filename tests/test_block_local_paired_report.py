"""Paired temperature grading deduplicates exact proof bytes without mixing inputs."""
import json
from pathlib import Path
import shutil

import pytest

from harnesses.block_local_completion import paired_report, report
from test_block_local_report import (experiment as single_experiment, old_experiment,
    bank_artifacts, issue_artifacts, patch_artifacts, replacement, proof_hash, write, make_preflight, ISSUES)


def rebind(pair, label):
    path = pair[label]['plan']
    plan = report.read(path)
    manifest = Path(plan['input_manifest_path'])
    job_path = Path(plan['jobs'][0]['job_path'])
    job = report.read(job_path)
    job['input_manifest_sha256'] = report.sha(manifest)
    write(job_path, job)
    summary = report.read(pair[label]['summary'])
    summary.update(job_sha256=report.sha(job_path), input_manifest_sha256=report.sha(manifest), runtime=job['runtime'])
    write(pair[label]['summary'], summary)
    plan['jobs'][0]['job_sha256'] = report.sha(job_path)
    plan['input_manifest_sha256'] = report.sha(manifest)
    write(path, plan)
    parent = report.read(pair['plan'])
    next(arm for arm in parent['arms'] if arm['label'] == label)['plan_sha256'] = report.sha(path)
    write(pair['plan'], parent)


@pytest.fixture
def pair(single_experiment):
    old = single_experiment['plan'].parent
    root = old.parent / 'paired'
    root.mkdir()
    arms, result = [], {'plan': root / 'pair_plan.json'}
    for label, temperature, strategy in paired_report.ARMS:
        target = root / label
        shutil.copytree(old, target)
        for path in target.rglob('*.json'):
            text = path.read_text()
            if str(old) in text:
                path.write_text(text.replace(str(old), str(target)))
        plan_path = target / 'plan.json'
        plan = report.read(plan_path)
        plan.update(seed=42, repair_temperature=temperature, strategy=strategy,
                    pipeline_config=report.strategy_config(strategy), terminal_stage=report.TERMINAL_STAGES[strategy])
        write(plan_path, plan)
        job_path = Path(plan['jobs'][0]['job_path'])
        job = report.read(job_path)
        job.update(strategy=strategy, pipeline_config=report.strategy_config(strategy))
        job['runtime'].update(repair_temperature=temperature, workers=4)
        write(job_path, job)
        summary = Path(plan['jobs'][0]['output_dir']) / 'summary.json'
        value = report.read(summary)
        value.update(strategy=strategy, pipeline_config=report.strategy_config(strategy))
        if strategy == 'original':
            value['state'] = 'completed'
            for lane in value['lanes']:
                source = Path(lane['source_proof_path']).read_bytes()
                Path(lane['proof_path']).write_bytes(source)
                record = lane.pop('block_provenance')
                lazy_path = Path(record['source_path']).parent / 'original_lazy.txt'
                lazy_path.write_text('NO_ISSUES')
                lane.update(operation='no_issues', local_result='no_issues', failure=None,
                    changed=False, adopted_from='original', proof_file_sha256=report.sha(lane['proof_path']),
                    proof_sha256=proof_hash(source), original_provenance={
                        'source_path': record['source_path'], 'source_file_sha256': record['source_file_sha256'],
                        'lazy_report_path': str(lazy_path), 'lazy_report_file_sha256': report.sha(lazy_path)})
                lane.pop('block_patch', None)
                lane.pop('post_expansion', None)
        write(summary, value)
        result[label] = {'plan': plan_path, 'summary': summary}
        arms.append({'label': label, 'repair_temperature': temperature, 'strategy': strategy, 'plan_path': str(plan_path),
                     'plan_sha256': report.sha(plan_path)})
    write(result['plan'], {'schema': 'block-local-paired-plan-v1', 'experiment': report.EXPERIMENT,
        'source_arm': 'raw', 'processing_scope': report.SCOPE, 'seed': 42, 'dry_run': False,
        'repair_temperatures': [0.7, 0.4, 0.4], 'arms': arms})
    for label, _, _ in paired_report.ARMS:
        rebind(result, label)
    return result


def change_second_repair(pair):
    summary = report.read(pair['t04']['summary'])
    lane = summary['lanes'][0]
    data = Path(lane['source_proof_path']).read_bytes()
    bank = report.read(lane['block_provenance']['blockmap_path'])
    directory = Path(lane['block_provenance']['source_path']).parent.parent
    issues, issue_record = issue_artifacts(directory / 'changed-expansion', bank, ISSUES)
    applied, patch_record = patch_artifacts(directory / 'changed-expansion', bank, data, issues,
                                           replacement('A different valid-looking local repair.'))
    lane['block_patch'] = {**issue_record, **patch_record}
    final = applied['proof_bytes']
    fresh, provenance = bank_artifacts(directory / 'changed-intermediate', final)
    _, audit = issue_artifacts(directory / 'changed-audit', fresh, 'NO_ISSUES')
    lane['post_expansion'] = {'proof_path': provenance['source_path'], 'proof_file_sha256': provenance['source_file_sha256'],
        'proof_sha256': proof_hash(final), 'block_provenance': provenance,
        'audit': {'status': 'no_issues', **audit}, 'resolve': {'status': 'not_run'}}
    Path(lane['proof_path']).write_bytes(final)
    lane.update(proof_file_sha256=report.sha(lane['proof_path']), proof_sha256=proof_hash(final))
    write(pair['t04']['summary'], summary)


def grades_for(pair):
    path = paired_report.export_grading(pair['plan'])
    parent_key = report.read(path.parent.parent / 'grading_key.json')
    kinds = {}
    for label, _, _ in paired_report.ARMS:
        child_key = report.read(pair[label]['plan'].parent / 'grading_key.json')
        for item in child_key['mapping']:
            kinds[(label, item['submission_id'])] = item['kind']
    scores = {}
    for item in parent_key['mapping']:
        kind = kinds[(item['arm'], item['child_submission_id'])]
        scores[item['submission_id']] = 3 if kind == 'raw' else 5 if item['arm'] == 't07' else 7
    rows = []
    for item in report.read(path)['submissions']:
        for index in (1, 2):
            rows.append({'submission_id': item['submission_id'], 'pass_index': index,
                'score': scores[item['submission_id']], 'proof_file_sha256': item['proof_file_sha256'],
                **{key: item[key] for key in report.GRADE_CONFIG}})
    return write(pair['plan'].parent / 'grades.json', {'schema': 'block-local-paired-grades-v1', 'rows': rows})


def test_deduplicates_raw_and_identical_finals_across_all_three_arms(pair):
    path = paired_report.export_grading(pair['plan'])
    assert len(report.read(path)['submissions']) == 5  # four raw and one shared repaired proof
    assert paired_report.export_grading(pair['plan']) == path
    key = report.read(path.parent.parent / 'grading_key.json')
    assert len(key['mapping']) == 14
    for hidden in ('t07', 't04', 'original_t04', 'raw_mean', 'candidate_id', 'child_submission_id', 'repair_temperature'):
        assert hidden not in path.read_text()


def test_distinct_repairs_are_graded_separately_but_raw_is_graded_once(pair):
    change_second_repair(pair)
    grades = grades_for(pair)
    output = paired_report.write_report(pair['plan'], grades)
    value = report.read(output.with_suffix('.json'))
    assert value['quality'] == 'graded'
    assert value['required_grade_count'] == 12
    assert value['problems'][0] == {'problem_id': 'imo2026_p2', 'raw_mean': 3, 't07_mean': 3.5,
                                    't04_mean': 4, 'original_t04_mean': 3,
                                    'delta_t04_minus_t07': 0.5, 'delta_t04_minus_original_t04': 1}
    assert value['contrast_counts']['delta_t04_minus_t07'] == {'improved': 1, 'worsened': 0, 'unchanged': 3}
    for label, _, _ in paired_report.ARMS:
        child = report.read(pair[label]['plan'].parent / 'REPORT.json')
        assert child['quality'] == 'graded' and child['problems'][0]['raw_mean'] == 3


@pytest.mark.parametrize('change', ['schema', 'order', 'child_hash', 'runtime', 'temperature', 'source'])
def test_pair_identity_changes_fail_before_grading_configuration(pair, monkeypatch, change):
    parent = report.read(pair['plan'])
    if change == 'schema':
        parent['schema'] = 'other-plan'
    elif change == 'order':
        parent['arms'].reverse()
    elif change == 'child_hash':
        parent['arms'][1]['plan_sha256'] = '0' * 64
    else:
        plan = report.read(pair['t04']['plan'])
        job_path = Path(plan['jobs'][0]['job_path'])
        job = report.read(job_path)
        if change == 'runtime':
            job['runtime']['seed'] = 43
        elif change == 'temperature':
            job['runtime']['repair_temperature'] = 0.7
        else:
            manifest = Path(plan['input_manifest_path'])
            bank = report.read(manifest)
            bank['problems'][0]['problem']['claim'] += ' Different statement.'
            bank['problems'][0]['problem']['problem_sha256'] = proof_hash(bank['problems'][0]['problem']['claim'].encode())
            job['problem'] = bank['problems'][0]['problem']
            write(manifest, bank)
        write(job_path, job)
        rebind(pair, 't04')
        parent = report.read(pair['plan'])
    write(pair['plan'], parent)
    monkeypatch.setattr(report, '_grading_config', lambda *a: pytest.fail('No grading config before pair validation'))
    with pytest.raises(ValueError):
        paired_report.export_grading(pair['plan'])


def test_waits_for_all_three_arms_before_any_grading_access(pair, monkeypatch):
    summary = report.read(pair['original_t04']['summary'])
    summary['state'] = 'running'
    write(pair['original_t04']['summary'], summary)
    monkeypatch.setattr(report, '_grading_config', lambda *a: pytest.fail('Third arm is not finished'))
    with pytest.raises(ValueError, match='Finish all generation'):
        paired_report.export_grading(pair['plan'])


def test_dry_pair_never_reads_grading_config(pair, monkeypatch):
    parent = report.read(pair['plan'])
    parent['dry_run'] = True
    write(pair['plan'], parent)
    for label, _, _ in paired_report.ARMS:
        make_preflight(pair[label])
        rebind(pair, label)
    monkeypatch.setattr(report, '_grading_config', lambda *a: pytest.fail('Dry run must not read grading config'))
    output = paired_report.write_report(pair['plan'])
    assert report.read(output.with_suffix('.json'))['quality'] == 'not_applicable'
    assert not (pair['plan'].parent / 'grading').exists()


@pytest.mark.parametrize('change', ['missing', 'schema', 'config', 'proof_hash'])
def test_invalid_paired_grades_are_rejected(pair, change):
    path = grades_for(pair)
    value = report.read(path)
    if change == 'missing':
        value['rows'].pop()
    elif change == 'schema':
        value['schema'] = 'block-local-grades-v1'
    else:
        value['rows'][0]['model' if change == 'config' else 'proof_file_sha256'] = 'wrong'
    write(path, value)
    with pytest.raises(ValueError):
        paired_report.write_report(pair['plan'], path)


def test_changed_exported_snapshot_is_rejected(pair):
    path = paired_report.export_grading(pair['plan'])
    item = report.read(path)['submissions'][0]
    Path(item['proof_path']).write_bytes(b'Tampered proof.')
    with pytest.raises(ValueError, match='snapshot changed'):
        paired_report.write_report(pair['plan'])


def original_expansion(pair):
    summary = report.read(pair['original_t04']['summary'])
    lane = summary['lanes'][0]
    record = lane['original_provenance']
    directory = Path(record['source_path']).parent
    lazy = Path(record['lazy_report_path'])
    lazy.write_text('The conclusion needs a missing derivation.')
    proof = b'A completely rewritten proof, unconstrained by the source blocks.\n'
    response = directory / 'original_expansion.txt'
    response.write_text('BEGIN_REPAIR_AUDIT\nCONCLUSION_ACTION: PRESERVE\nORIGINAL_CLASSIFICATION: implication holds\n'
        'REPAIRED_CLASSIFICATION: implication holds\nCHANGE_BASIS: NONE\nCHANGE_JUSTIFICATION: NONE\nEND_REPAIR_AUDIT\n'
        'BEGIN_REPAIRED_PROOF\n' + proof.decode() + 'END_REPAIRED_PROOF')
    parsed = directory / 'parsed_proof.md'
    parsed.write_bytes(proof)
    record.update(lazy_report_file_sha256=report.sha(lazy), expansion_response_path=str(response),
        expansion_response_file_sha256=report.sha(response), parsed_proof_path=str(parsed),
        parsed_proof_file_sha256=report.sha(parsed), conclusion_action='PRESERVE')
    Path(lane['proof_path']).write_bytes(proof)
    lane.update(operation='expanded', local_result='original_expanded', adopted_from='expansion', changed=True,
        proof_file_sha256=report.sha(lane['proof_path']), proof_sha256=proof_hash(proof))
    write(pair['original_t04']['summary'], summary)


def test_original_control_replays_full_proof_envelope_without_claiming_confinement(pair):
    original_expansion(pair)
    path = paired_report.write_report(pair['plan'])
    child = report.read(pair['original_t04']['plan'].parent / 'REPORT.json')
    assert child['strategy'] == 'original'
    assert child['lanes'][0]['patch_provenance']['edit_confinement_checked'] is False
    assert 'not confined to blocks' in child['limitation']
    assert report.read(path.with_suffix('.json'))['unique_proof_count'] == 6


@pytest.mark.parametrize('mutation', ['envelope', 'final'])
def test_original_envelope_or_proof_mismatch_is_rejected(pair, mutation):
    original_expansion(pair)
    summary = report.read(pair['original_t04']['summary'])
    lane = summary['lanes'][0]
    if mutation == 'envelope':
        record = lane['original_provenance']
        path = Path(record['expansion_response_path'])
        path.write_text('A full proof without required markers.')
        record['expansion_response_file_sha256'] = report.sha(path)
    else:
        path = Path(lane['proof_path'])
        path.write_bytes(b'A proof not present in the saved response.\n')
        lane.update(proof_file_sha256=report.sha(path), proof_sha256=proof_hash(path.read_bytes()))
    write(pair['original_t04']['summary'], summary)
    with pytest.raises(ValueError, match='repair envelope'):
        paired_report.export_grading(pair['plan'])


def test_original_control_failure_keeps_raw_grades_without_confinement_claim(pair):
    summary = report.read(pair['original_t04']['summary'])
    lane = summary['lanes'][0]
    lane.update(operation='failed', local_result='invalid_or_failed', failure={'stage': 'expansion', 'error': 'bad envelope'})
    summary['state'] = 'completed_with_fallbacks'
    write(pair['original_t04']['summary'], summary)
    output = paired_report.write_report(pair['plan'], grades_for(pair))
    assert report.read(output.with_suffix('.json'))['unique_proof_count'] == 5
    child = report.read(pair['original_t04']['plan'].parent / 'REPORT.json')
    assert child['all_portfolio']['same_count'] == 4
    assert child['lanes'][0]['grading_source'] == 'paired_raw_grades_reused_for_identical_final'
