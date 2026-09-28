"""Export only changed proofs for blinded grading; reuse bound baseline grades."""
from __future__ import annotations

from collections import Counter
import csv
import hashlib
import hmac
import json
import math
from pathlib import Path
import re
import secrets

CANDIDATES = ('t10_r01', 't10_r02', 't07_r01', 't07_r02')
OPERATIONS = ('no_issues', 'expanded', 'failed', 'skipped_non_c3', 'preflight_only')
PROTOCOL = 'olympiad_strict_scoring_v2'
GRADE_CONFIG = ('model', 'reasoning_effort', 'policy_sha256', 'reference_sha256')
ALL_FINALS = 'all_saved_final_proofs'
LEGACY_C3_ONLY = 'c3_only'
PRIMARY = ('Average two grades per proof, then all four final lane proofs per problem, '
           'with equal weight across problems. Compare completion results with the saved B portfolio. '
           'Lanes and grading passes are not independent problem samples.')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    value = json.loads(Path(path).read_text(encoding='utf-8'))
    require(isinstance(value, dict), f'Expected an object: {path}')
    return value


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    temporary.replace(path)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def text_sha(path):
    return hashlib.sha256(Path(path).read_text(encoding='utf-8').strip().encode()).hexdigest()


def file(path, root):
    path, root = Path(path).absolute(), Path(root).resolve()
    require(path.is_file() and not path.is_symlink()
            and all(not p.is_symlink() for p in path.parents if str(p) not in ('/tmp', '/var'))
            and path.resolve().is_relative_to(root), f'Missing, symlinked, or escaping artifact: {path}')
    return path.resolve()


def number(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def load_inputs(path, expected_sha):
    from .inputs import verify_manifest
    require(sha(path) == expected_sha, 'Input manifest hash changed')
    return verify_manifest(path)


def _load(plan_path):
    plan_path = Path(plan_path).resolve()
    require(plan_path.name not in ('REPORT.md', 'REPORT.json', 'REPORT.csv'), 'Plan overlaps report output')
    plan = read(plan_path)
    require(plan.get('schema') == 'post-c3-plan-v1' and type(plan.get('dry_run')) is bool
            and plan.get('source_arm') == 'B', 'Unsupported post-C3 plan')
    scope = plan.get('processing_scope', LEGACY_C3_ONLY)
    require(scope in (ALL_FINALS, LEGACY_C3_ONLY), 'Unsupported processing scope')

    def validate_scope(record):
        observed = record.get('processing_scope') if 'processing_scope' in plan else record.get('processing_scope', LEGACY_C3_ONLY)
        require(observed == scope, 'Plan, job, and summary processing scopes must match')

    manifest_path = Path(plan['input_manifest_path']).resolve()
    bank = load_inputs(manifest_path, plan.get('input_manifest_sha256'))
    archive = Path(plan['source_archive']).resolve()
    require(bank.get('source_arm') == 'B' and Path(bank['archive_root']).resolve() == archive,
            'Source archive or baseline arm changed')
    require(sha(file(archive / 'manifest.json', archive)) == bank['archive_manifest_sha256'],
            'Source archive manifest changed')
    by_problem = {row['problem']['problem_id']: row for row in bank['problems']}
    jobs = plan.get('jobs')
    require(isinstance(jobs, list) and jobs and len(jobs) == len(by_problem), 'Incomplete post-C3 job plan')
    require({job.get('problem_id') for job in jobs} == set(by_problem), 'Duplicate or changed job problems')
    rows, bindings = [], {}
    for entry in jobs:
        pid = entry['problem_id']
        source = by_problem[pid]
        job_path = file(entry['job_path'], plan_path.parent)
        require(sha(job_path) == entry.get('job_sha256'), 'Plan job hash changed')
        job = read(job_path)
        validate_scope(job)
        output = Path(entry['output_dir']).resolve()
        require(output.is_relative_to(plan_path.parent), 'Job output escapes experiment')
        require(job.get('schema') == 'post-c3-job-v1' and job.get('source_arm') == 'B' and job.get('problem') == source['problem']
                and job.get('candidates') == source['candidates'] and job.get('dry_run') is plan['dry_run']
                and Path(job.get('output_dir', '')).resolve() == output
                and Path(job.get('input_manifest_path', '')).resolve() == manifest_path
                and job.get('input_manifest_sha256') == plan['input_manifest_sha256'],
                'Job differs from its plan or frozen inputs')
        summary_path = file(output / 'summary.json', output)
        summary = read(summary_path)
        validate_scope(summary)
        require(summary.get('schema') == 'post-c3-result-v1' and summary.get('source_arm') == 'B'
                and summary.get('problem_id') == pid and summary.get('dry_run') is plan['dry_run']
                and summary.get('job_sha256') == sha(job_path) and summary.get('runtime') == job.get('runtime')
                and Path(summary.get('input_manifest_path', '')).resolve() == manifest_path
                and summary.get('input_manifest_sha256') == plan['input_manifest_sha256'],
                'Result identity, job, or input hash changed')
        require(summary.get('release_identity', {}).get('release_sha256') == bank['release_sha256'],
                'Worker release identity changed')
        states = ('preflight_passed',) if plan['dry_run'] else ('completed', 'completed_with_fallbacks')
        require(summary.get('state') in states, 'All generation jobs must finish before reading baseline grades')
        require(number(summary.get('elapsed_seconds')), 'Invalid problem elapsed time')
        lanes = summary.get('lanes')
        require(isinstance(lanes, list) and [lane.get('candidate_id') for lane in lanes] == list(CANDIDATES),
                'Result must contain all four canonical lanes')
        failures = 0
        for lane, candidate in zip(lanes, source['candidates']):
            operation = lane.get('operation')
            require(operation in OPERATIONS and type(lane.get('changed')) is bool
                    and lane.get('source_stage') == candidate['selected_stage']
                    and number(lane.get('elapsed_seconds')), 'Invalid lane operation or source stage')
            proof = file(lane['proof_path'], output)
            require(sha(proof) == lane.get('proof_file_sha256') and text_sha(proof) == lane.get('proof_sha256')
                    and proof.read_text(encoding='utf-8').strip(), 'Final proof hash changed')
            original_path = Path(lane['source_proof_path']).absolute()
            original_root = output if original_path.resolve().is_relative_to(output) else manifest_path.parent
            original = file(original_path, original_root)
            require(sha(original) == lane.get('source_proof_file_sha256') == candidate['proof_file_sha256'],
                    'Source proof identity changed')
            changed = proof.read_bytes() != original.read_bytes()
            require(lane['changed'] is changed, 'Changed-proof flag differs from proof bytes')
            eligible = scope == ALL_FINALS or candidate['selected_stage'] == 'refinement_3'
            if plan['dry_run']:
                expected_operation = 'preflight_only' if eligible else 'skipped_non_c3'
                require(operation == expected_operation and not changed, 'Dry run altered a proof or skipped eligibility')
            else:
                require(operation != 'preflight_only', 'Live result contains a preflight lane')
                if not eligible:
                    require(operation == 'skipped_non_c3', 'A non-C3 source was processed under the legacy C3-only scope')
                else:
                    require(operation != 'skipped_non_c3', 'An eligible saved final proof was skipped')
                if operation != 'expanded':
                    require(not changed, 'Unexpanded proof changed')
                if operation == 'failed':
                    failures += 1
                    require(isinstance(lane.get('failure'), dict), 'Failed lane lacks failure metadata')
                else:
                    require(lane.get('failure') is None, 'Successful lane has failure metadata')
            rows.append({'problem_id': pid, 'problem': source['problem'], 'source': candidate,
                         'lane': lane, 'eligible_for_completion': eligible})
        if not plan['dry_run']:
            require(summary['state'] == ('completed_with_fallbacks' if failures else 'completed'),
                    'Completion state disagrees with failed lanes')
        bindings[str(job_path)] = sha(job_path)
        bindings[str(summary_path)] = sha(summary_path)
    return plan_path, plan, bank, rows, bindings


def _baseline(bank, rows):
    """This is called only after _load has checked every completed worker."""
    archive = Path(bank['archive_root']).resolve()
    manifest_path = file(archive / 'manifest.json', archive)
    require(sha(manifest_path) == bank['archive_manifest_sha256'], 'Archive manifest changed')
    manifest = read(manifest_path)
    require(manifest.get('schema') == 'refinement-bf-publication-v1', 'Unsupported baseline archive')

    def artifact(name):
        require(isinstance(name, str) and not Path(name).is_absolute(), 'Invalid archive artifact path')
        path = file(archive / name, archive)
        require(name in manifest['files'] and sha(path) == manifest['files'][name]['sha256'],
                f'Baseline archive artifact changed: {name}')
        return path

    comparison = read(artifact('comparison.json'))
    require(comparison.get('state') == 'completed' and comparison.get('run_id') == manifest.get('run_id')
            and comparison.get('selection_results_included') is False
            and comparison.get('post_selection_recovery_included') is False, 'Baseline comparison identity changed')
    policy_hash = text_sha(artifact('grading/strict_olympiad_policy_v2.txt'))
    require(policy_hash == comparison.get('policy_sha256'), 'Baseline rubric hash changed')
    reference_rows = read(artifact('grading/reference_sources.json'))['references']
    references = {row['problem_id']: row['reference_sha256'] for row in reference_rows}
    require(len(references) == len(reference_rows), 'Duplicate baseline reference metadata')
    selected = {(row['problem_id'], row['source']['candidate_id']): row for row in rows}
    baseline_rows = [row for row in comparison['lanes'] if row.get('arm') == 'B'
                     and (row.get('problem_id'), row.get('candidate_id')) in selected]
    require(len(baseline_rows) == len(selected)
            and len({(row['problem_id'], row['candidate_id']) for row in baseline_rows}) == len(selected),
            'Missing or duplicate B baseline lanes')
    result, grade_paths = {}, set()
    for baseline in baseline_rows:
        pid, cid = baseline['problem_id'], baseline['candidate_id']
        row, source = selected[(pid, cid)], selected[(pid, cid)]['source']
        proof = artifact(baseline['proof_path'])
        require(sha(proof) == baseline['proof_file_sha256'] == source['proof_file_sha256']
                and text_sha(proof) == baseline['proof_sha256'] == source['proof_sha256']
                and baseline['selected_stage'] == source['selected_stage'], 'Baseline proof or selected stage changed')
        statement = read(artifact(f'problems/{pid}.json'))
        claim = statement.get('claim', statement.get('problem'))
        require(statement.get('problem_id', pid) == pid and isinstance(claim, str)
                and claim.strip() == row['problem']['claim'].strip(), 'Baseline problem changed')
        scores = baseline.get('scores')
        require(isinstance(scores, list) and len(scores) == len(baseline.get('grade_paths', [])) == 2
                and all(type(score) is int and 0 <= score <= 7 for score in scores), 'Invalid baseline scores')
        config = {'model': comparison['model'], 'reasoning_effort': comparison['reasoning_effort'],
                  'policy_sha256': policy_hash, 'reference_sha256': references[pid]}
        require(all(isinstance(value, str) and value for value in config.values())
                and all(re.fullmatch('[0-9a-f]{64}', config[key]) for key in ('policy_sha256', 'reference_sha256')),
                'Invalid baseline grading configuration')
        for index, name in enumerate(baseline['grade_paths'], 1):
            require(name not in grade_paths, 'Baseline grade record reused for different proofs')
            grade_paths.add(name)
            grade = read(artifact(name))
            expected = {'problem_id': pid, 'repeat': index, 'proof_sha256': source['proof_sha256'],
                        'problem_sha256': row['problem']['problem_sha256'], **config}
            require(all(grade.get(key) == value for key, value in expected.items()), 'Baseline grading identity changed')
            require(type(grade.get('grade', {}).get('score')) is int and grade['grade']['score'] == scores[index - 1]
                    and grade.get('errors') == [] and grade.get('isolation_audit', {}).get('tool_calls') == 0,
                    'Baseline score or grader isolation record changed')
        require(math.isclose(baseline['mean_score'], sum(scores) / 2, rel_tol=0, abs_tol=1e-12), 'Baseline mean changed')
        result[(pid, cid)] = {'scores': scores, 'grade_paths': baseline['grade_paths'], 'config': config}
    return result


def _mapping(rows, salt):
    result = []
    for row in rows:
        if not row['lane']['changed']:
            continue
        pid, cid = row['problem_id'], row['source']['candidate_id']
        opaque = 'proof_' + hmac.new(salt, f'{pid}:{cid}'.encode(), hashlib.sha256).hexdigest()[:24]
        result.append({'submission_id': opaque, 'problem_id': pid, 'candidate_id': cid,
                       'source_stage': row['source']['selected_stage'],
                       'proof_file_sha256': row['lane']['proof_file_sha256']})
    return result


def _export(plan_path, plan, bank, rows, bindings, baseline):
    require(not plan['dry_run'], 'Dry runs have no grading export')
    root, directory = plan_path.parent, plan_path.parent / 'grading'
    manifest_path, key_path = directory / 'input_manifest.json', root / 'grading_key.json'
    if directory.exists() or key_path.exists():
        key = read(file(key_path, root))
        require(key.get('schema') == 'post-c3-grading-key-v1' and key.get('plan_sha256') == sha(plan_path)
                and key.get('source_bindings') == bindings
                and key.get('archive_manifest_sha256') == bank['archive_manifest_sha256'], 'Existing grading export identity changed')
        salt = bytes.fromhex(key['private_id_salt'])
        require(len(salt) == 32 and key.get('mapping') == _mapping(rows, salt), 'Private grading mapping changed')
        exported = read(file(manifest_path, directory))
        require(key.get('grading_manifest_sha256') == sha(manifest_path)
                and exported.get('schema') == 'post-c3-blinded-grading-v1', 'Grading manifest changed')
        expected = {row['submission_id']: row for row in key['mapping']}
        submissions = exported.get('submissions')
        require(isinstance(submissions, list) and len(submissions) == len(expected)
                and {item.get('submission_id') for item in submissions} == set(expected), 'Changed-proof export is incomplete')
        for item in submissions:
            mapping = expected[item['submission_id']]
            config = baseline[(mapping['problem_id'], mapping['candidate_id'])]['config']
            require(item['problem_id'] == mapping['problem_id']
                    and item['proof_file_sha256'] == mapping['proof_file_sha256']
                    and all(item.get(key) == value for key, value in config.items())
                    and item.get('grading_protocol') == PROTOCOL and item.get('required_passes') == [1, 2],
                    'Exported grading task changed')
            require(sha(file(item['proof_path'], directory)) == item['proof_file_sha256'], 'Exported proof changed')
            require(sha(file(item['problem_path'], directory)) == item['problem_file_sha256'], 'Exported statement changed')
        return manifest_path
    directory.mkdir()
    salt = secrets.token_bytes(32)
    mapping = _mapping(rows, salt)
    by_identity = {(row['problem_id'], row['source']['candidate_id']): row for row in rows}
    submissions = []
    for record in mapping:
        row = by_identity[(record['problem_id'], record['candidate_id'])]
        proof_path = directory / 'proofs' / (record['submission_id'] + '.md')
        proof_path.parent.mkdir(exist_ok=True)
        proof_path.write_bytes(Path(row['lane']['proof_path']).read_bytes())
        require(sha(proof_path) == record['proof_file_sha256'], 'Proof changed during export')
        problem_path = directory / 'problems' / (record['problem_id'] + '.json')
        write(problem_path, {'problem_id': record['problem_id'], 'problem': row['problem']['claim']})
        submissions.append({'submission_id': record['submission_id'], 'problem_id': record['problem_id'],
            'proof_path': str(proof_path), 'proof_file_sha256': record['proof_file_sha256'],
            'problem_path': str(problem_path), 'problem_file_sha256': sha(problem_path),
            'grading_protocol': PROTOCOL, 'required_passes': [1, 2],
            **baseline[(record['problem_id'], record['candidate_id'])]['config']})
    submissions.sort(key=lambda item: item['submission_id'])
    write(manifest_path, {'schema': 'post-c3-blinded-grading-v1', 'submissions': submissions})
    write(key_path, {'schema': 'post-c3-grading-key-v1', 'plan_sha256': sha(plan_path),
        'archive_manifest_sha256': bank['archive_manifest_sha256'], 'source_bindings': bindings,
        'private_id_salt': salt.hex(), 'mapping': mapping, 'grading_manifest_sha256': sha(manifest_path)})
    return manifest_path


def export_grading(plan_path: Path) -> Path:
    loaded = _load(plan_path)
    require(not loaded[1]['dry_run'], 'Dry runs have no grading export')
    return _export(*loaded, _baseline(loaded[2], loaded[3]))


def _grades(path, exported):
    if path is None:
        return None
    supplied = read(path)
    require(supplied.get('schema') == 'post-c3-grades-v1' and isinstance(supplied.get('rows'), list), 'Unsupported grading file')
    expected = {item['submission_id']: item for item in exported['submissions']}
    accepted = {}
    for grade in supplied['rows']:
        require(isinstance(grade, dict) and set(grade) == {'submission_id', 'pass_index', 'score',
                'proof_file_sha256', *GRADE_CONFIG}, 'Unexpected grade fields')
        sid, index = grade['submission_id'], grade['pass_index']
        require(sid in expected and type(index) is int and index in (1, 2) and (sid, index) not in accepted,
                'Unexpected or duplicate grading pass')
        require(type(grade['score']) is int and 0 <= grade['score'] <= 7, 'Grade must be an integer from 0 to 7')
        require(all(grade.get(key) == expected[sid][key] for key in ('proof_file_sha256', *GRADE_CONFIG)),
                'Grade proof hash or baseline grading configuration changed')
        accepted[(sid, index)] = grade['score']
    require(set(accepted) == {(sid, index) for sid in expected for index in (1, 2)},
            'Exactly two grades are required for every changed proof; unchanged proofs must not be rescored')
    return accepted


def _mean(values):
    return sum(values) / len(values) if values and all(v is not None for v in values) else None


def _metrics(lanes):
    known = [lane for lane in lanes if lane['post_scores'] is not None]
    full = [lane for lane in lanes if lane['baseline_scores'] == [7, 7]]
    known_full = [lane for lane in full if lane['post_scores'] is not None]
    return {'lane_count': len(lanes), 'graded_lane_count': len(known),
            'improved_count': sum(lane['delta'] > 0 for lane in known),
            'worse_count': sum(lane['delta'] < 0 for lane in known),
            'same_count': sum(lane['delta'] == 0 for lane in known),
            'baseline_both_passes_7_count': len(full),
            'both_passes_7_retained_count': sum(lane['post_scores'] == [7, 7] for lane in known_full),
            'both_passes_7_retention_denominator': len(known_full),
            'both_passes_7_retention_pending': len(full) - len(known_full),
            'post_both_passes_7_count': sum(lane['post_scores'] == [7, 7] for lane in known),
            'grading_disagreement_count': sum(lane['post_scores'][0] != lane['post_scores'][1] for lane in known)}


def write_report(plan_path: Path, grades_path: Path | None = None) -> Path:
    plan_path, plan, bank, rows, bindings = _load(plan_path)
    root = plan_path.parent
    if grades_path is not None:
        require(Path(grades_path).resolve() not in {root / f'REPORT.{ext}' for ext in ('md', 'json', 'csv')},
                'Grade input overlaps report output')
    scope = plan.get('processing_scope', LEGACY_C3_ONLY)
    report = {'schema': 'post-c3-report-v1', 'plan_sha256': sha(plan_path), 'dry_run': plan['dry_run'],
              'source_arm': 'B', 'source_archive': str(Path(bank['archive_root']).resolve()),
              'archive_manifest_sha256': bank['archive_manifest_sha256'], 'primary_estimand': PRIMARY,
              'processing_scope': scope, 'eligible_final_proof_count': sum(row['eligible_for_completion'] for row in rows),
              'original_c3_source_count': sum(row['source']['selected_stage'] == 'refinement_3' for row in rows),
              'source_stage_counts': dict(Counter(row['source']['selected_stage'] for row in rows)),
              'eligible_c3_field_note': 'Legacy eligible_c3 fields describe the original-C3 subgroup, not current processing eligibility.'}
    scope_text = ('Every saved final proof is eligible, including proofs retained from earlier refinement stages.'
                  if scope == ALL_FINALS else
                  'Legacy C3-only scope: only original C3 proofs were processed; earlier-stage final proofs were skipped.')
    lines = ['# Final-proof completion experiment', '', PRIMARY, '', scope_text, '']
    if plan['dry_run']:
        require(grades_path is None, 'Dry runs cannot import grades')
        report.update(quality='not_applicable', state='preflight_passed', model_calls=0, lanes=[])
        lines += ['Preflight only. No generation, baseline-grade inspection, new grading, or quality comparison was performed.']
    else:
        baseline = _baseline(bank, rows)
        export = _export(plan_path, plan, bank, rows, bindings, baseline)
        exported, key = read(export), read(root / 'grading_key.json')
        grades = _grades(grades_path, exported)
        mappings = {(item['problem_id'], item['candidate_id']): item['submission_id'] for item in key['mapping']}
        records = []
        for row in rows:
            identity = (row['problem_id'], row['source']['candidate_id'])
            saved, lane = baseline[identity], row['lane']
            if not lane['changed']:
                scores, source = list(saved['scores']), 'baseline_reused_identical_bytes'
            elif grades is None:
                scores, source = None, 'pending_new_grades'
            else:
                scores = [grades[(mappings[identity], index)] for index in (1, 2)]
                source = 'new_two_pass_grades'
            before, after = _mean(saved['scores']), _mean(scores) if scores is not None else None
            records.append({'problem_id': identity[0], 'candidate_id': identity[1],
                'source_stage': row['source']['selected_stage'], 'operation': lane['operation'],
                'eligible_c3': row['source']['selected_stage'] == 'refinement_3', 'changed': lane['changed'],
                'original_c3': row['source']['selected_stage'] == 'refinement_3',
                'eligible_for_completion': row['eligible_for_completion'],
                'baseline_scores': saved['scores'], 'post_scores': scores,
                'baseline_mean': before, 'post_mean': after, 'delta': None if after is None else after - before,
                'grading_source': source, 'baseline_grade_paths': saved['grade_paths'], 'grading_config': saved['config'],
                'source_proof_file_sha256': row['source']['proof_file_sha256'],
                'proof_file_sha256': lane['proof_file_sha256'], 'elapsed_seconds': lane['elapsed_seconds'],
                'failure': lane.get('failure')})
        problems = []
        for entry in plan['jobs']:
            pid = entry['problem_id']
            subset = [record for record in records if record['problem_id'] == pid]
            eligible = [record for record in subset if record['eligible_c3']]
            elapsed = read(Path(entry['output_dir']) / 'summary.json')['elapsed_seconds']
            before, after = _mean([record['baseline_mean'] for record in subset]), _mean([record['post_mean'] for record in subset])
            eligible_before = _mean([record['baseline_mean'] for record in eligible])
            eligible_after = _mean([record['post_mean'] for record in eligible])
            problems.append({'problem_id': pid, 'baseline_mean': before, 'post_mean': after,
                'delta': None if after is None else after - before, 'eligible_c3_count': len(eligible),
                'original_c3_count': len(eligible),
                'eligible_final_proof_count': sum(record['eligible_for_completion'] for record in subset),
                'source_stage_counts': dict(Counter(record['source_stage'] for record in subset)),
                'eligible_c3_baseline_mean': eligible_before, 'eligible_c3_post_mean': eligible_after,
                'eligible_c3_delta': None if eligible_after is None else eligible_after - eligible_before,
                'operation_counts': dict(Counter(record['operation'] for record in subset)), 'elapsed_seconds': elapsed})
        complete = all(record['post_scores'] is not None for record in records)
        report.update(quality='graded' if complete else 'pending', lanes=records, problems=problems,
            changed_proof_count=len(mappings), required_new_grade_count=2 * len(mappings),
            reused_baseline_grade_count=2 * sum(not row['changed'] for row in records),
            all_portfolio=_metrics(records), eligible_c3=_metrics([row for row in records if row['eligible_c3']]),
            original_c3=_metrics([row for row in records if row['original_c3']]),
            completion_eligible=_metrics([row for row in records if row['eligible_for_completion']]),
            equal_weight_problem_delta=_mean([p['delta'] for p in problems]),
            eligible_c3_equal_weight_problem_delta=_mean([p['eligible_c3_delta'] for p in problems if p['eligible_c3_count']]),
            original_c3_equal_weight_problem_delta=_mean([p['eligible_c3_delta'] for p in problems if p['eligible_c3_count']]),
            operation_counts=dict(Counter(row['operation'] for row in records)))
        if grades_path is not None:
            report.update(grades_path=str(Path(grades_path).resolve()), grades_sha256=sha(grades_path))
        lines += [f"Changed proofs requiring new grades: {len(mappings)} ({2 * len(mappings)} grading passes). "
                  f"Unchanged proofs reuse {report['reused_baseline_grade_count']} saved B grades.", '',
                  '| Problem | Saved B mean / 7 | Completion mean / 7 | Delta | Eligible final proofs | Original C3 proofs | Operations | Wall time (s) |',
                  '|---|---:|---:|---:|---:|---:|---|---:|']
        for problem in problems:
            after = 'pending' if problem['post_mean'] is None else f"{problem['post_mean']:.3f}"
            delta = 'pending' if problem['delta'] is None else f"{problem['delta']:+.3f}"
            operations = ', '.join(f'{name}: {count}' for name, count in problem['operation_counts'].items())
            lines.append(f"| {problem['problem_id']} | {problem['baseline_mean']:.3f} | {after} | {delta} | "
                         f"{problem['eligible_final_proof_count']}/4 | {problem['original_c3_count']}/4 | "
                         f"{operations} | {problem['elapsed_seconds']:.1f} |")
        lines += ['', '| Portfolio | Known grades / lanes | Improved | Worse | Same | Both-pass 7/7 retained | Pending 7/7 retention |',
                  '|---|---:|---:|---:|---:|---:|---:|']
        for label, field in [('All four lanes per problem', 'all_portfolio'),
                             ('Eligible for completion under recorded scope', 'completion_eligible'),
                             ('Originally completed C3 subgroup', 'original_c3')]:
            metrics = report[field]
            lines.append(f"| {label} | {metrics['graded_lane_count']}/{metrics['lane_count']} | {metrics['improved_count']} | "
                f"{metrics['worse_count']} | {metrics['same_count']} | {metrics['both_passes_7_retained_count']}/"
                f"{metrics['both_passes_7_retention_denominator']} | {metrics['both_passes_7_retention_pending']} |")
        if complete:
            lines += ['', f"Equal-weight mean problem delta: {report['equal_weight_problem_delta']:+.3f}/7. "
                      'This is a descriptive comparison, not a significance claim.']
        else:
            lines += ['', 'New grading is pending. Unchanged-proof scores are known, but no overall quality gain or loss has been established.']
        lines += ['', 'The saved B proofs are never rescored. Identical proofs and failed-operation fallbacks reuse '
                  'their original two grades. '
                  + ('Legacy skipped non-C3 proofs also reuse their original grades. ' if scope == LEGACY_C3_ONLY else '')
                  + 'A valid repair envelope does not verify mathematical correctness.', '',
                  'The grading export includes no reference solutions or baseline scores. Keep grading_key.json private. '
                  'No hosted grader is launched. Token totals and exact model-call counts are not inferred from elapsed time.']
    write(root / 'REPORT.json', report)
    report_path = root / 'REPORT.md'
    report_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    with (root / 'REPORT.csv').open('w', encoding='utf-8', newline='') as handle:
        fields = ['problem_id', 'candidate_id', 'source_stage', 'eligible_for_completion', 'original_c3',
                  'operation', 'changed', 'baseline_mean', 'post_mean', 'delta', 'grading_source']
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(report.get('lanes', []))
    return report_path
