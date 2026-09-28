"""Replay confined edits before exporting a blinded raw-versus-repaired study."""
from __future__ import annotations

from collections import Counter
import csv
import hashlib
import hmac
import json
from pathlib import Path
import secrets

from harnesses.post_c3_completion.report import file, number, read, require, sha, write, _mean, _metrics
from . import PIPELINE_CONFIG, TERMINAL_STAGES, strategy_config

EXPERIMENT = 'block_local_completion_v1'
SCOPE = 'all_saved_raw_proofs'
CANDIDATES = ('t10_r01', 't10_r02', 't07_r01', 't07_r02')
GRADING_ARCHIVE = Path(__file__).resolve().parents[2] / 'benchmarks/imo2026/results/refinement_bf_B6_selection_first_20260920_1426'
GRADE_CONFIG = ('model', 'reasoning_effort', 'policy_sha256', 'reference_sha256')
LIMITATION = ('Reapplying the saved patches verifies that edits are confined to their authorized block ranges. '
              'This does not establish mathematical correctness. The Qwen audit is an automated model judgment, '
              'not a formal proof check. A resolved proof is not audited again.')
ORIGINAL_LIMITATION = ('The original strategy returns a complete proof in the frozen repair envelope. '
    'The saved response and parsed proof are hash-bound and checked against that format; edits are not confined to blocks. '
    'No separate audit or resolve is run, and format checks do not establish mathematical correctness.')
PRIMARY = ('Average the two grades per proof, then all four lanes per problem; give each problem equal weight. '
           'Compare the repaired portfolio with its saved raw proofs. Lanes and grading passes are not independent problems.')


def _text(path):
    return Path(path).read_bytes().decode('utf-8')


def _artifact(record, name, root, bindings):
    path = file(record[name], root)
    expected = record.get(name.replace('_path', '_file_sha256'))
    if expected is None:
        expected = record.get(name.replace('_path', '_sha256'))
    require(sha(path) == expected, f'Patch artifact hash changed: {name}')
    bindings[str(path)] = expected
    return path


def _bank(record, expected, root, bindings):
    from . import blocks
    source = _artifact(record, 'source_path', root, bindings)
    require(source.read_bytes() == expected, 'Patch source differs from frozen source or preceding patch')
    bank_path = _artifact(record, 'blockmap_path', root, bindings)
    bank = read(bank_path)
    require(bank == blocks.build_blocks(expected), 'Block map differs from deterministic source map')
    rendered = _artifact(record, 'rendered_path', root, bindings)
    require(rendered.read_bytes() == blocks.render_blocks(bank).encode('utf-8'), 'Rendered block view changed')
    return bank


def _issues(record, bank, root, bindings, *, required):
    from . import blocks
    if 'issues_raw_path' not in record:
        require(not required and 'issues_path' not in record, 'Missing authorized issue document')
        return None
    raw = _artifact(record, 'issues_raw_path', root, bindings)
    saved = _artifact(record, 'issues_path', root, bindings)
    parsed = blocks.parse_issues(_text(raw), bank)
    require(json.loads(saved.read_bytes()) == parsed, 'Authorized issues differ from saved model issue document')
    return parsed


def _patch(record, bank, original, issues, root, bindings, *, failed_diagnostic=False):
    from . import blocks
    require(issues, 'A patch has no authorized issues')
    raw = _artifact(record, 'raw_patch_path', root, bindings)
    result = blocks.parse_and_apply(_text(raw), bank, original, issues)
    audit_path = _artifact(record, 'audit_path', root, bindings)
    require(read(audit_path) == result['audit'], 'Saved patch audit differs from deterministic reapplication')
    require(record.get('status') == result['status'] or (failed_diagnostic and record.get('status') == 'failed'),
            'Saved patch status differs from response')
    if 'patches' in record:
        require(record['patches'] == result['patches'], 'Saved replacement ranges changed')
    changed_ids = {block_id for patch in result['patches']
                   if patch['original_sha256'] != patch['replacement_sha256'] for block_id in patch['block_ids']}
    return result, len(changed_ids)


def _lane_provenance(lane, source, final, output, bindings, dry_run):
    patch = lane.get('block_patch', {})
    operation, local = lane['operation'], lane.get('local_result')
    result = {'local_result': local, 'adopted_from': lane.get('adopted_from'),
              'expansion_changed_block_count': 0, 'resolve_changed_block_count': 0,
              'audit_outcome': 'not_run', 'resolve_outcome': 'not_run'}
    if 'block_provenance' not in lane:
        require(not dry_run and operation == 'failed' and local == 'invalid_or_failed'
                and lane.get('failure', {}).get('stage') == 'segmentation'
                and lane.get('adopted_from') == 'original' and final == source,
                'Missing block provenance for an adopted or preflight proof')
        result['confinement_check'] = 'unchanged_original_after_segmentation_failure'
        return result
    bank = _bank(lane['block_provenance'], source, output, bindings)
    if dry_run:
        require(operation == 'preflight_only' and local == 'preflight_only'
                and patch.get('status') == 'not_run' and final == source, 'Dry-run patch state changed')
        return result
    issues = _issues(patch, bank, output, bindings, required=operation in ('no_issues', 'expanded') or local == 'cannot_repair_locally')
    if operation == 'no_issues':
        require(issues == [] and local == 'no_issues' and final == source
                and lane.get('adopted_from') == 'original', 'NO_ISSUES result changed the raw proof')
        return result
    if patch.get('status') not in ('patched', 'cannot_repair_locally'):
        require(operation == 'failed' and local == 'invalid_or_failed'
                and lane.get('adopted_from') == 'original' and final == source, 'Unproven expansion was adopted')
        return result
    expanded, result['expansion_changed_block_count'] = _patch(patch, bank, source, issues, output, bindings)
    if expanded['status'] == 'cannot_repair_locally':
        require(operation == 'failed' and local == 'cannot_repair_locally'
                and lane.get('adopted_from') == 'original' and final == source, 'Declined local repair was adopted')
        return result
    intermediate = expanded['proof_bytes']
    if intermediate == source:
        require(operation == 'expanded' and local == 'unchanged_patch_audit_skipped' and final == source,
                'Unchanged patch result changed')
        return result
    post = lane.get('post_expansion')
    require(isinstance(post, dict), 'Changed expansion lacks audit/resolve provenance')
    intermediate_path = _artifact(post, 'proof_path', output, bindings)
    require(intermediate_path.read_bytes() == intermediate, 'Intermediate proof differs from authorized expansion')
    next_bank = _bank(post['block_provenance'], intermediate, output, bindings)
    audit, resolve = post.get('audit', {}), post.get('resolve', {})
    result.update(audit_outcome=audit.get('status'), resolve_outcome=resolve.get('status', 'not_run'))
    if audit.get('status') in ('not_run', 'failed'):
        require(operation == 'failed' and local == 'invalid_or_failed' and final == source
                and lane.get('adopted_from') == 'original', 'Unaudited changed expansion was adopted')
        return result
    audit_issues = _issues(audit, next_bank, output, bindings, required=True)
    if audit.get('status') == 'no_issues':
        require(audit_issues == [] and resolve.get('status', 'not_run') == 'not_run'
                and operation == 'expanded' and local == 'patched_audit_passed'
                and lane.get('adopted_from') == 'expansion' and final == intermediate,
                'Final proof differs from the audited expansion')
        return result
    require(audit.get('status') == 'issues' and audit_issues, 'Invalid structured audit outcome')
    if resolve.get('status') in ('patched', 'cannot_repair_locally'):
        resolved, result['resolve_changed_block_count'] = _patch(resolve, next_bank, intermediate, audit_issues, output, bindings)
        if resolved['status'] == 'patched':
            require(operation == 'expanded' and local == 'resolved' and lane.get('adopted_from') == 'resolve'
                    and final == resolved['proof_bytes'] and final != intermediate,
                    'Final proof differs from authorized resolve patches')
        else:
            require(operation == 'failed' and local == 'cannot_repair_locally'
                    and lane.get('adopted_from') == 'original' and final == source, 'Declined resolve was adopted')
    else:
        if 'audit_path' in resolve:
            _, result['resolve_changed_block_count'] = _patch(
                resolve, next_bank, intermediate, audit_issues, output, bindings, failed_diagnostic=True)
        require(operation == 'failed' and local == 'invalid_or_failed'
                and lane.get('adopted_from') == 'original' and final == source, 'Failed resolve did not restore original raw proof')
    return result


def _original_provenance(lane, source, final, output, bindings, dry_run):
    record = lane.get('original_provenance')
    require(isinstance(record, dict), 'Missing original strategy provenance')
    saved_source = _artifact(record, 'source_path', output, bindings)
    require(saved_source.read_bytes() == source, 'Original strategy source snapshot changed')
    result = {'local_result': lane.get('local_result'), 'adopted_from': lane.get('adopted_from'),
        'expansion_changed_block_count': 0, 'resolve_changed_block_count': 0,
        'audit_outcome': 'not_applicable', 'resolve_outcome': 'not_applicable',
        'edit_confinement_checked': False, 'confinement_check': 'not_applicable_full_proof_expansion'}
    operation = lane['operation']
    if dry_run:
        require(operation == 'preflight_only' and lane.get('local_result') == 'preflight_only'
                and final == source, 'Original dry-run proof changed')
        return result
    lazy = None
    if 'lazy_report_path' in record:
        lazy = _text(_artifact(record, 'lazy_report_path', output, bindings)).strip()
        require(bool(lazy), 'Empty original lazy report')
    if operation == 'no_issues':
        require(lazy == 'NO_ISSUES' and lane.get('local_result') == 'no_issues'
                and lane.get('adopted_from') == 'original' and final == source, 'Original NO_ISSUES result changed')
    elif operation == 'expanded':
        require(lazy and lazy != 'NO_ISSUES' and lane.get('local_result') == 'original_expanded'
                and lane.get('adopted_from') == 'expansion', 'Original expansion lacks a lazy issue report')
        response = _artifact(record, 'expansion_response_path', output, bindings)
        parsed_path = _artifact(record, 'parsed_proof_path', output, bindings)
        from harnesses.refinement_bf_ablation import worker as frozen
        import sys
        frozen.load_release()
        frontend = frozen.load_backend().v108.v097
        module = sys.modules[frontend.run_lazy_resolve.__module__]
        parsed = module.expansion_parser(_text(response))
        require(parsed.get('valid') is True and isinstance(parsed.get('proof'), str), 'Invalid original repair envelope')
        expected = (parsed['proof'].strip() + '\n').encode('utf-8')
        require(parsed_path.read_bytes() == expected == final
                and record.get('conclusion_action') == parsed.get('conclusion_action'),
                'Original final proof differs from the parsed repair envelope')
    else:
        require(operation == 'failed' and lane.get('local_result') == 'invalid_or_failed'
                and lane.get('adopted_from') == 'original' and final == source, 'Original failed repair changed raw proof')
    return result


def _load(plan_path):
    from . import inputs
    plan_path = Path(plan_path).resolve()
    require(plan_path.name not in ('REPORT.json', 'REPORT.md', 'REPORT.csv'), 'Plan overlaps report output')
    plan = read(plan_path)
    require(plan.get('schema') == 'block-local-plan-v1' and plan.get('experiment') == EXPERIMENT
            and plan.get('processing_scope') == SCOPE and plan.get('source_arm') == 'raw'
            and type(plan.get('dry_run')) is bool, 'Unsupported block-local experiment plan')
    strategy = plan.get('strategy')
    config = strategy_config(strategy)
    require(plan.get('pipeline_config') == config
            and all(type(value) is int for value in plan['pipeline_config'].values())
            and plan.get('refinements_enabled') is False and plan.get('terminal_stage') == TERMINAL_STAGES[strategy],
            'Plan pipeline configuration changed')
    require(type(plan.get('repair_temperature')) in (int, float)
            and plan['repair_temperature'] in ((0.7, 0.4) if strategy == 'block' else (0.4,)), 'Invalid plan repair temperature')
    manifest_path = Path(plan['input_manifest_path']).resolve()
    require(sha(manifest_path) == plan['input_manifest_sha256'], 'Input manifest hash changed')
    bank = inputs.verify_manifest(manifest_path)
    require(bank.get('schema') == 'block-local-inputs-v1' and bank.get('source_arm') == 'raw', 'Expected saved raw proofs')
    problems = {row['problem']['problem_id']: row for row in bank['problems']}
    jobs = plan.get('jobs')
    require(isinstance(jobs, list) and len(jobs) == len(problems)
            and {entry.get('problem_id') for entry in jobs} == set(problems), 'Incomplete or duplicated job plan')
    rows, bindings, timings = [], {str(plan_path): sha(plan_path), str(manifest_path): sha(manifest_path)}, {}
    for entry in jobs:
        pid, frozen = entry['problem_id'], problems[entry['problem_id']]
        job_path = file(entry['job_path'], plan_path.parent)
        require(sha(job_path) == entry['job_sha256'], 'Job hash changed')
        job = read(job_path)
        require(job.get('runtime', {}).get('repair_temperature') == plan['repair_temperature'],
                'Worker repair temperature differs from plan')
        output = Path(entry['output_dir']).resolve()
        require(output.is_relative_to(plan_path.parent), 'Worker output escapes experiment')
        summary_path = file(output / 'summary.json', output)
        summary = read(summary_path)
        for record, schema in ((job, 'block-local-job-v1'), (summary, 'block-local-result-v1')):
            require(record.get('schema') == schema and record.get('experiment') == EXPERIMENT
                    and record.get('processing_scope') == SCOPE and record.get('source_arm') == 'raw'
                    and record.get('dry_run') is plan['dry_run'], 'Plan/job/result experiment or processing scope mismatch')
            require(record.get('strategy') == strategy and record.get('pipeline_config') == config
                    and all(type(value) is int for value in record['pipeline_config'].values()),
                    'Worker pipeline configuration changed')
            require(Path(record.get('input_manifest_path', '')).resolve() == manifest_path
                    and record.get('input_manifest_sha256') == plan['input_manifest_sha256'], 'Worker input identity changed')
        require(job.get('problem') == frozen['problem'] and job.get('candidates') == frozen['candidates']
                and Path(job.get('output_dir', '')).resolve() == output, 'Job differs from frozen raw inputs')
        require(summary.get('problem_id') == pid and summary.get('job_sha256') == sha(job_path)
                and summary.get('runtime') == job.get('runtime')
                and summary.get('release_identity', {}).get('release_sha256') == bank['release_sha256'], 'Worker identity changed')
        allowed = ('preflight_passed',) if plan['dry_run'] else ('completed', 'completed_with_fallbacks')
        require(summary.get('state') in allowed, 'Finish all generation before reading grading configuration')
        require(number(summary.get('elapsed_seconds')), 'Invalid elapsed time')
        lanes = summary.get('lanes')
        require(isinstance(lanes, list) and [lane.get('candidate_id') for lane in lanes] == list(CANDIDATES), 'Expected all four raw lanes')
        failed = 0
        for lane, candidate in zip(lanes, frozen['candidates']):
            source_path = file(candidate['proof_path'], manifest_path.parent)
            source, final_path = source_path.read_bytes(), file(lane['proof_path'], output)
            final = final_path.read_bytes()
            require(sha(source_path) == candidate['proof_file_sha256'] == lane.get('source_proof_file_sha256')
                    and sha(final_path) == lane.get('proof_file_sha256')
                    and hashlib.sha256(final_path.read_text(encoding='utf-8').strip().encode()).hexdigest() == lane.get('proof_sha256'),
                    'Source or result proof hash changed')
            require(lane.get('source_stage') == candidate.get('selected_stage') == 'raw'
                    and type(lane.get('changed')) is bool and lane['changed'] == (source != final)
                    and number(lane.get('elapsed_seconds')), 'Source stage, changed flag, or time changed')
            phase_times = lane.get('phase_elapsed_seconds', {})
            require(isinstance(phase_times, dict) and set(phase_times) <= {'lazy_check', 'expansion', 'audit', 'resolve'}
                    and all(number(value) for value in phase_times.values()), 'Invalid phase elapsed time')
            operation = lane.get('operation')
            require(operation in (('preflight_only',) if plan['dry_run'] else ('expanded', 'no_issues', 'failed')), 'Invalid operation')
            if operation != 'expanded':
                require(final == source, 'An unsuccessful operation altered its original proof')
            if operation == 'failed':
                failed += 1
                require(isinstance(lane.get('failure'), dict), 'Failure metadata missing')
            else:
                require(lane.get('failure') is None, 'Successful operation contains failure metadata')
            if strategy == 'original':
                require(set(phase_times) <= {'lazy_check', 'expansion'}, 'Original strategy unexpectedly ran audit or resolve')
            provenance = (_lane_provenance if strategy == 'block' else _original_provenance)(
                lane, source, final, output, bindings, plan['dry_run'])
            rows.append({'problem_id': pid, 'problem': frozen['problem'], 'candidate': candidate,
                         'lane': lane, 'patch_provenance': provenance})
            bindings[str(source_path)], bindings[str(final_path)] = sha(source_path), sha(final_path)
        if not plan['dry_run']:
            require(summary['state'] == ('completed_with_fallbacks' if failed else 'completed'), 'Failure state mismatch')
        bindings[str(job_path)], bindings[str(summary_path)] = sha(job_path), sha(summary_path)
        timings[pid] = summary['elapsed_seconds']
    return plan_path, plan, rows, bindings, timings


def _grading_config(rows):
    """Extract grading configuration, without reusing old scores or opening reference answers."""
    root = GRADING_ARCHIVE.resolve()
    manifest_path = file(root / 'manifest.json', root)
    manifest = read(manifest_path)
    bindings = {str(manifest_path): sha(manifest_path)}
    def artifact(name):
        path = file(root / name, root)
        require(name in manifest['files'] and sha(path) == manifest['files'][name]['sha256'], 'Grading configuration artifact changed')
        bindings[str(path)] = sha(path)
        return path
    comparison = read(artifact('comparison.json'))
    rubric = artifact('grading/strict_olympiad_policy_v2.txt')
    policy_hash = hashlib.sha256(_text(rubric).strip().encode()).hexdigest()
    require(comparison.get('model') == 'gpt-5.6-sol' and comparison.get('reasoning_effort') == 'xhigh'
            and comparison.get('policy_sha256') == policy_hash, 'Unexpected default grading configuration')
    refs = read(artifact('grading/reference_sources.json'))['references']
    ref_hashes = {row['problem_id']: row['reference_sha256'] for row in refs}
    require(len(ref_hashes) == len(refs), 'Duplicate reference metadata')
    for row in rows:
        pid = row['problem_id']
        canonical = read(artifact(f'problems/{pid}.json'))
        claim = canonical.get('claim', canonical.get('problem'))
        require(canonical.get('problem_id') == pid and isinstance(claim, str)
                and hashlib.sha256(claim.strip().encode()).hexdigest() == row['problem']['problem_sha256']
                and claim.strip() == row['problem']['claim'].strip(),
                'Raw problem statement does not match the canonical grading reference')
        require(pid in ref_hashes and isinstance(ref_hashes[pid], str) and len(ref_hashes[pid]) == 64,
                'Missing canonical grading reference hash')
    return ({row['problem_id']: {'model': 'gpt-5.6-sol', 'reasoning_effort': 'xhigh',
             'policy_sha256': policy_hash, 'reference_sha256': ref_hashes[row['problem_id']]}
             for row in rows}, bindings)


def _mapping(rows, salt):
    mapping = []
    for row in rows:
        for kind in ('raw', 'repaired') if row['lane']['changed'] else ('raw',):
            pid, cid = row['problem_id'], row['candidate']['candidate_id']
            opaque = 'proof_' + hmac.new(salt, f'{pid}:{cid}:{kind}'.encode(), hashlib.sha256).hexdigest()[:24]
            proof = row['candidate'] if kind == 'raw' else row['lane']
            mapping.append({'submission_id': opaque, 'problem_id': pid, 'candidate_id': cid, 'kind': kind,
                            'proof_file_sha256': proof['proof_file_sha256']})
    return mapping


def _export(loaded):
    plan_path, plan, rows, bindings, _ = loaded
    require(not plan['dry_run'], 'Dry runs have no grading export')
    configs, config_bindings = _grading_config(rows)
    all_bindings = {**bindings, **config_bindings}
    root, folder = plan_path.parent, plan_path.parent / 'grading'
    key_path, manifest_path = root / 'grading_key.json', folder / 'input_manifest.json'
    if folder.exists() or key_path.exists():
        key, manifest = read(file(key_path, root)), read(file(manifest_path, folder))
        require(key.get('experiment') == EXPERIMENT and key.get('source_bindings') == all_bindings
                and key.get('grading_manifest_sha256') == sha(manifest_path), 'Existing export identity changed')
        salt = bytes.fromhex(key['private_id_salt'])
        require(len(salt) == 32 and key.get('mapping') == _mapping(rows, salt), 'Private grading mapping changed')
        expected = {item['submission_id']: item for item in key['mapping']}
        submissions = manifest.get('submissions', [])
        require(manifest.get('schema') == 'block-local-blinded-grading-v1' and len(submissions) == len(expected)
                and {item.get('submission_id') for item in submissions} == set(expected), 'Grading submission set changed')
        for item in submissions:
            target = expected[item['submission_id']]
            require(item['problem_id'] == target['problem_id'] and item['proof_file_sha256'] == target['proof_file_sha256']
                    and all(item.get(key) == value for key, value in configs[target['problem_id']].items())
                    and item.get('required_passes') == [1, 2], 'Grading task identity changed')
            require(sha(file(item['proof_path'], folder)) == item['proof_file_sha256']
                    and sha(file(item['problem_path'], folder)) == item['problem_file_sha256'], 'Exported proof or statement changed')
        return manifest_path, key, configs
    folder.mkdir()
    salt = secrets.token_bytes(32)
    mapping = _mapping(rows, salt)
    by_id = {(row['problem_id'], row['candidate']['candidate_id']): row for row in rows}
    submissions = []
    for item in mapping:
        row = by_id[(item['problem_id'], item['candidate_id'])]
        source = row['candidate'] if item['kind'] == 'raw' else row['lane']
        proof_path = folder / 'proofs' / (item['submission_id'] + '.md')
        proof_path.parent.mkdir(exist_ok=True)
        proof_path.write_bytes(Path(source['proof_path']).read_bytes())
        require(sha(proof_path) == item['proof_file_sha256'], 'Proof changed during grading export')
        problem_path = folder / 'problems' / (item['problem_id'] + '.json')
        write(problem_path, {'problem_id': item['problem_id'], 'problem': row['problem']['claim']})
        submissions.append({'submission_id': item['submission_id'], 'problem_id': item['problem_id'],
            'proof_path': str(proof_path), 'proof_file_sha256': item['proof_file_sha256'],
            'problem_path': str(problem_path), 'problem_file_sha256': sha(problem_path),
            'grading_protocol': 'olympiad_strict_scoring_v2', 'required_passes': [1, 2], **configs[item['problem_id']]})
    write(manifest_path, {'schema': 'block-local-blinded-grading-v1',
                         'submissions': sorted(submissions, key=lambda item: item['submission_id'])})
    key = {'schema': 'block-local-grading-key-v1', 'experiment': EXPERIMENT, 'source_bindings': all_bindings,
           'private_id_salt': salt.hex(), 'mapping': mapping, 'grading_manifest_sha256': sha(manifest_path)}
    write(key_path, key)
    return manifest_path, key, configs


def export_grading(plan_path: Path) -> Path:
    return _export(_load(plan_path))[0]


def _grades(path, manifest, *, schema='block-local-grades-v1'):
    if path is None:
        return None
    value = read(path)
    require(value.get('schema') == schema and isinstance(value.get('rows'), list), 'Unsupported grade schema')
    expected = {item['submission_id']: item for item in manifest['submissions']}
    result = {}
    for row in value['rows']:
        require(set(row) == {'submission_id', 'pass_index', 'score', 'proof_file_sha256', *GRADE_CONFIG}, 'Unexpected grade fields')
        sid, index = row['submission_id'], row['pass_index']
        require(sid in expected and type(index) is int and index in (1, 2) and (sid, index) not in result, 'Duplicate or unknown grade')
        require(type(row['score']) is int and 0 <= row['score'] <= 7
                and all(row[key] == expected[sid][key] for key in ('proof_file_sha256', *GRADE_CONFIG)), 'Grade score or configuration changed')
        result[(sid, index)] = row['score']
    require(set(result) == {(sid, index) for sid in expected for index in (1, 2)}, 'Exactly two grades are required for every exported proof')
    return result


def write_report(plan_path: Path, grades_path: Path | None = None) -> Path:
    loaded = _load(plan_path)
    plan_path, plan, rows, bindings, timings = loaded
    root = plan_path.parent
    if grades_path is not None:
        require(Path(grades_path).resolve() not in {root / f'REPORT.{ext}' for ext in ('md', 'json', 'csv')}, 'Grade input overlaps report output')
    limitation = LIMITATION if plan['strategy'] == 'block' else ORIGINAL_LIMITATION
    result = {'schema': 'block-local-report-v1', 'experiment': EXPERIMENT, 'processing_scope': SCOPE,
              'strategy': plan['strategy'], 'repair_temperature': plan['repair_temperature'],
              'source_arm': 'raw', 'dry_run': plan['dry_run'], 'plan_sha256': sha(plan_path),
              'primary_estimand': PRIMARY, 'limitation': limitation, 'lanes': [], 'problem_elapsed_seconds': timings}
    lines = ['# ' + ('Block-local completion' if plan['strategy'] == 'block' else 'Original lazy-check and expansion')
             + ' of saved raw proofs', '', PRIMARY, '', limitation, '']
    if plan['dry_run']:
        require(grades_path is None, 'Dry runs cannot import grades')
        result.update(quality='not_applicable', model_calls=0)
        lines.append('Preflight only. No inference, grading configuration inspection, or grading was performed.')
    else:
        export, key, configs = _export(loaded)
        grades = _grades(grades_path, read(export))
        mapping = {(item['problem_id'], item['candidate_id'], item['kind']): item['submission_id'] for item in key['mapping']}
        for row in rows:
            pid, cid, lane = row['problem_id'], row['candidate']['candidate_id'], row['lane']
            raw_sid = mapping[(pid, cid, 'raw')]
            final_sid = mapping[(pid, cid, 'repaired')] if lane['changed'] else raw_sid
            before = None if grades is None else [grades[(raw_sid, index)] for index in (1, 2)]
            after = None if grades is None else [grades[(final_sid, index)] for index in (1, 2)]
            result['lanes'].append({'problem_id': pid, 'candidate_id': cid, 'operation': lane['operation'],
                'changed': lane['changed'], 'baseline_scores': before, 'post_scores': after,
                'baseline_mean': None if before is None else _mean(before), 'post_mean': None if after is None else _mean(after),
                'delta': None if after is None else _mean(after) - _mean(before),
                'grading_source': 'paired_raw_and_repaired_grades' if lane['changed'] else 'paired_raw_grades_reused_for_identical_final',
                'elapsed_seconds': lane['elapsed_seconds'], 'failure': lane.get('failure'),
                'phase_elapsed_seconds': lane.get('phase_elapsed_seconds', {}),
                'patch_provenance': row['patch_provenance']})
        problems = []
        for pid in timings:
            subset = [lane for lane in result['lanes'] if lane['problem_id'] == pid]
            before, after = _mean([lane['baseline_mean'] for lane in subset]), _mean([lane['post_mean'] for lane in subset])
            problems.append({'problem_id': pid, 'raw_mean': before, 'repaired_mean': after,
                             'delta': None if after is None else after - before, 'elapsed_seconds': timings[pid]})
        result.update(quality='pending' if grades is None else 'graded', problems=problems,
            changed_proof_count=sum(row['lane']['changed'] for row in rows), raw_proof_count=len(rows),
            required_grade_count=2 * len(key['mapping']), grading_config=configs,
            local_result_counts=dict(Counter(row['patch_provenance']['local_result'] for row in rows)),
            audit_outcome_counts=dict(Counter(row['patch_provenance']['audit_outcome'] for row in rows)),
            resolve_outcome_counts=dict(Counter(row['patch_provenance']['resolve_outcome'] for row in rows)),
            changed_source_block_count=sum(row['patch_provenance']['expansion_changed_block_count'] + row['patch_provenance']['resolve_changed_block_count'] for row in rows),
            changed_block_count_definition=('Source blocks covered by byte-changing patch ranges, counted separately for expansion and resolve; includes diagnostic patches later discarded.'
                if plan['strategy'] == 'block' else 'Not applicable: original expansion returns the entire proof without block restrictions.'),
            summed_lane_phase_seconds={phase: sum(row['lane'].get('phase_elapsed_seconds', {}).get(phase, 0)
                for row in rows) for phase in ('lazy_check', 'expansion', 'audit', 'resolve')
                if any(phase in row['lane'].get('phase_elapsed_seconds', {}) for row in rows)},
            phase_time_definition='Sum of measured lane durations per phase, including failed calls; parallel lane times do not equal end-to-end wall time.',
            equal_weight_problem_delta=_mean([problem['delta'] for problem in problems]))
        if grades is not None:
            result.update(all_portfolio=_metrics(result['lanes']), grades_path=str(Path(grades_path).resolve()), grades_sha256=sha(grades_path))
            result['all_portfolio'].update(raw_grading_disagreement_count=sum(lane['baseline_scores'][0] != lane['baseline_scores'][1]
                for lane in result['lanes']),
                raw_both_passes_7_count=sum(lane['baseline_scores'] == [7, 7] for lane in result['lanes']))
        lines += [f"Raw proofs: {len(rows)}; changed final proofs: {result['changed_proof_count']}; "
                  f"required grading passes: {result['required_grade_count']}.", '',
                  'Every raw proof needs two new grades. An unchanged final proof reuses its own paired raw grades. '
                  'No historical B or other proof grades are reused.', '',
                  '| Problem | Raw mean / 7 | Repaired mean / 7 | Delta | Wall time (s) |', '|---|---:|---:|---:|---:|']
        for problem in problems:
            values = ['pending' if problem[key] is None else f"{problem[key]:.3f}" for key in ('raw_mean', 'repaired_mean', 'delta')]
            lines.append(f"| {problem['problem_id']} | {' | '.join(values)} | {problem['elapsed_seconds']:.1f} |")
        lines += ['', 'Local outcomes: ' + ', '.join(f'{name}: {count}' for name, count in result['local_result_counts'].items()),
                  'Audit outcomes: ' + ', '.join(f'{name}: {count}' for name, count in result['audit_outcome_counts'].items()),
                  'Resolve outcomes: ' + ', '.join(f'{name}: {count}' for name, count in result['resolve_outcome_counts'].items()), '',
                  'Changed block count: ' + str(result['changed_source_block_count']) + '. ' + result['changed_block_count_definition'], '',
                  'Grading pending; no quality gain or loss is established.' if grades is None else
                  f"Equal-weight mean problem delta: {result['equal_weight_problem_delta']:+.3f}/7. Descriptive comparison only.", '',
                  'Keep grading_key.json private. The grading export contains no reference answers or source/final labels. No hosted grader is launched.']
        if result['summed_lane_phase_seconds']:
            lines += ['', 'Measured phase times (summed over lanes): ' + ', '.join(
                f'{phase}: {seconds:.1f}s' for phase, seconds in result['summed_lane_phase_seconds'].items()) + '.',
                result['phase_time_definition']]
        if grades is not None:
            metrics = result['all_portfolio']
            lines += ['', f"Proof means: improved {metrics['improved_count']}; worsened {metrics['worse_count']}; "
                      f"unchanged {metrics['same_count']}.",
                      'Raw proofs scoring 7/7 on both passes retained that result: '
                      f"{metrics['both_passes_7_retained_count']}/{metrics['both_passes_7_retention_denominator']}.",
                      f"Two-pass score disagreements: raw {metrics['raw_grading_disagreement_count']}; "
                      f"repaired {metrics['grading_disagreement_count']}."]
        lines += ['', 'Failed or declined repairs preserve the raw proof; fallback is not counted as mathematical success.']
    for name, expected in bindings.items():
        require(sha(file(name, Path(name).parent)) == expected, 'Artifact changed during report generation')
    write(root / 'REPORT.json', result)
    output = root / 'REPORT.md'
    output.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    with (root / 'REPORT.csv').open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=['problem_id', 'candidate_id', 'operation', 'changed', 'baseline_mean', 'post_mean', 'delta', 'grading_source'], extrasaction='ignore')
        writer.writeheader()
        writer.writerows(result['lanes'])
    return output
