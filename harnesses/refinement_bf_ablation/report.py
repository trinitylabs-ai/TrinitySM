"""Hash-bound, blinded grading exports and paired descriptive reports."""
from __future__ import annotations

from collections import Counter
import hashlib
import hmac
import json
import math
from pathlib import Path
import re
import secrets

from . import inputs

VARIANTS = ('original', 'role_specific')
STAGES = ('lazy_checked', 'refinement_1', 'refinement_2', 'refinement_3')
PRIMARY = ('Average the two grades for each proof, then average all four lane proofs '
           'within each problem and seed pair. Report role_specific minus original. '
           'Problems are the comparison units; lanes and grading passes are not independent samples.')


def require(value, message):
    if not value:
        raise ValueError(message)


def read(path):
    value = json.loads(Path(path).read_text(encoding='utf-8'))
    require(isinstance(value, dict), f'Expected an object: {path}')
    return value


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def number(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def protocol(problem_id):
    if re.fullmatch(r'imo2026_p[1-6]', problem_id):
        return 'olympiad_strict_scoring_v2'
    if re.fullmatch(r'PB-(Basic|Advanced)-[0-9]+', problem_id):
        return 'imobench-proof-autograder-b5-v1'
    return 'unknown'


def _bound_file(path, root):
    return inputs.safe_file(Path(path), root)


def _load(plan_path):
    plan_path = Path(plan_path).resolve()
    require(plan_path.name not in ('REPORT.md', 'REPORT.json'), 'Plan path overlaps report output')
    plan = read(plan_path)
    require(plan.get('schema') == 'refinement-bf-plan-v1' and type(plan.get('dry_run')) is bool,
            'Unsupported experiment plan')
    manifest_path = Path(plan['input_manifest_path']).resolve()
    bank = inputs.verify_manifest(manifest_path, plan.get('input_manifest_sha256'))
    require(sha(manifest_path) == plan.get('input_manifest_sha256'), 'Input manifest hash missing or changed')
    by_problem = {row['problem']['problem_id']: row for row in bank['problems']}
    pairs = plan.get('pairs')
    require(isinstance(pairs, list) and pairs, 'Plan has no pairs')
    rows, bindings, pair_ids = [], {}, set()
    for pair in pairs:
        pid, seed, pair_id = pair['problem_id'], pair['pair_seed'], pair['pair_id']
        require(pid in by_problem and type(seed) is int and 0 <= seed <= 0xffffffff,
                'Invalid problem or pair seed')
        require(pair_id == f'{pid}__seed{seed}' and pair_id not in pair_ids, 'Duplicate or changed pair identity')
        pair_ids.add(pair_id)
        require(sorted(pair.get('arm_order', [])) == sorted(VARIANTS)
                and set(pair.get('arms', {})) == set(VARIANTS), 'Pair must contain both variants')
        pair_runtime = None
        for variant in VARIANTS:
            arm = pair['arms'][variant]
            job_path = _bound_file(arm['job_path'], plan_path.parent)
            job = read(job_path)
            require(arm.get('job_sha256') == sha(job_path), 'Plan job hash changed')
            output = Path(arm['output_dir']).resolve()
            require(output.is_relative_to(plan_path.parent), 'Arm output escapes experiment')
            require(job.get('schema') == 'refinement-bf-job-v1' and job.get('variant') == variant
                    and job.get('pair_id') == pair_id and job.get('pair_seed') == seed
                    and job.get('dry_run') is plan['dry_run']
                    and Path(job.get('output_dir', '')).resolve() == output,
                    'Arm job differs from plan')
            require(job.get('problem') == by_problem[pid]['problem']
                    and job.get('candidates') == by_problem[pid]['candidates']
                    and Path(job.get('input_manifest_path', '')).resolve() == manifest_path
                    and job.get('input_manifest_sha256') == plan['input_manifest_sha256'],
                    'Arm job differs from frozen inputs')
            if pair_runtime is None:
                pair_runtime = job.get('runtime')
            require(isinstance(pair_runtime, dict) and job.get('runtime') == pair_runtime,
                    'Paired arms changed runtime or seed policy')
            summary_path = _bound_file(output / 'summary.json', output)
            summary = read(summary_path)
            require(summary.get('schema') == 'refinement-bf-arm-v1'
                    and summary.get('variant') == variant and summary.get('pair_id') == pair_id
                    and summary.get('problem_id') == pid and summary.get('pair_seed') == seed
                    and summary.get('job_sha256') == sha(job_path)
                    and summary.get('runtime') == job['runtime']
                    and Path(summary.get('input_manifest_path', '')).resolve() == manifest_path
                    and summary.get('input_manifest_sha256') == plan['input_manifest_sha256'],
                    'Arm summary identity or job hash changed')
            require(summary.get('release_identity', {}).get('release_sha256') == bank['release_sha256'],
                    'Arm summary release differs from input release')
            allowed = ('preflight_passed',) if plan['dry_run'] else ('completed', 'completed_with_fallbacks')
            require(summary.get('state') in allowed, 'Both arms must finish before reporting or grading')
            require(number(summary.get('elapsed_seconds')), 'Invalid arm elapsed time')
            lanes = summary.get('lanes')
            require(isinstance(lanes, list) and [lane.get('candidate_id') for lane in lanes] == list(inputs.CANDIDATES),
                    'Arm summary must contain all four canonical lanes')
            fallbacks = 0
            for lane in lanes:
                cid, stage = lane['candidate_id'], lane.get('selected_stage')
                require(stage in STAGES and number(lane.get('elapsed_seconds')), 'Invalid lane stage or elapsed time')
                proof_path = _bound_file(lane['proof_path'], output)
                require(sha(proof_path) == lane.get('proof_file_sha256')
                        and inputs.text_hash(proof_path) == lane.get('proof_sha256')
                        and proof_path.read_text(encoding='utf-8').strip(), 'Final proof hash changed')
                checkpoints = lane.get('checkpoints')
                require(isinstance(checkpoints, list)
                        and [c.get('stage') for c in checkpoints] == list(STAGES[1:STAGES.index(stage) + 1]),
                        'Selected stage differs from completed checkpoint chain')
                if stage == 'lazy_checked':
                    original = next(c for c in job['candidates'] if c['candidate_id'] == cid)
                    require(lane['proof_file_sha256'] == original['proof_file_sha256'], 'Lazy fallback changed the source proof')
                else:
                    terminal = checkpoints[-1]
                    terminal_path = _bound_file(terminal['proof_path'], output)
                    require(terminal.get('proof_sha256') == lane['proof_sha256']
                            and terminal_path.read_bytes() == proof_path.read_bytes(), 'Selected proof differs from terminal checkpoint')
                if not plan['dry_run'] and stage != 'refinement_3':
                    fallbacks += 1
                    require(isinstance(lane.get('failure'), dict), 'Fallback lacks a failure record')
                    require(lane['failure'].get('stage') == STAGES[STAGES.index(stage) + 1], 'Fallback failure stage changed')
                elif not plan['dry_run']:
                    require(lane.get('failure') is None, 'Completed refinement_3 lane has a failure')
            if not plan['dry_run']:
                require(summary['state'] == ('completed_with_fallbacks' if fallbacks else 'completed'),
                        'Arm completion state disagrees with fallbacks')
            bindings[str(job_path)] = sha(job_path)
            bindings[str(summary_path)] = sha(summary_path)
            rows.append({'pair_id': pair_id, 'pair_seed': seed, 'problem_id': pid,
                         'variant': variant, 'summary': summary, 'job': job})
    return plan_path, plan, bank, rows, bindings


def _export_loaded(plan_path, plan, bank, rows, bindings):
    require(not plan['dry_run'], 'Dry runs have no grading export')
    root, destination = plan_path.parent, plan_path.parent / 'grading'
    key_path, manifest_path = root / 'grading_key.json', destination / 'input_manifest.json'
    if destination.exists() or key_path.exists():
        require(manifest_path.is_file() and key_path.is_file(), 'Incomplete grading export; preserve it for inspection')
        _bound_file(key_path, root)
        _bound_file(manifest_path, destination)
        key, manifest = read(key_path), read(manifest_path)
        require(key.get('plan_sha256') == sha(plan_path) and key.get('source_bindings') == bindings
                and key.get('grading_manifest_sha256') == sha(manifest_path), 'Existing grading export identity changed')
        require(key.get('schema') == 'refinement-bf-grading-key-v1'
                and manifest.get('schema') == 'refinement-bf-blinded-grading-v1', 'Unsupported grading export')
        salt = bytes.fromhex(key['private_id_salt'])
        require(len(salt) == 32, 'Invalid grading identifier salt')
        expected_mapping = []
        for row in rows:
            for lane in row['summary']['lanes']:
                identity = f"{row['pair_id']}:{row['variant']}:{lane['candidate_id']}"
                opaque = 'proof_' + hmac.new(salt, identity.encode(), hashlib.sha256).hexdigest()[:24]
                expected_mapping.append({k: row[k] for k in ('pair_id', 'pair_seed', 'problem_id', 'variant')} |
                    {'submission_id': opaque, 'candidate_id': lane['candidate_id'], 'selected_stage': lane['selected_stage'],
                     'proof_file_sha256': lane['proof_file_sha256']})
        require(key.get('mapping') == expected_mapping, 'Private grading mapping changed')
        expected_submissions = {item['submission_id']: item for item in expected_mapping}
        seen = set()
        for item in manifest.get('submissions', []):
            sid = item['submission_id']
            require(sid in expected_submissions and sid not in seen, 'Grading submission mapping changed')
            seen.add(sid)
            expected = expected_submissions[sid]
            require(item['problem_id'] == expected['problem_id']
                    and item['proof_file_sha256'] == expected['proof_file_sha256']
                    and item['grading_protocol'] == protocol(expected['problem_id'])
                    and item['required_passes'] == [1, 2], 'Grading submission identity changed')
            require(sha(_bound_file(item['proof_path'], destination)) == item['proof_file_sha256'], 'Exported proof changed')
            require(sha(_bound_file(item['problem_path'], destination)) == item['problem_file_sha256'], 'Exported statement changed')
        require(len(manifest.get('submissions', [])) == len(rows) * 4, 'Incomplete grading export')
        return manifest_path
    destination.mkdir()
    salt = secrets.token_bytes(32)
    problems = {row['problem']['problem_id']: row['problem'] for row in bank['problems']}
    problem_paths = {}
    for pid in sorted({row['problem_id'] for row in rows}):
        path = destination / 'problems' / f'{pid}.json'
        inputs.write(path, {'problem_id': pid, 'problem': problems[pid]['claim']})
        problem_paths[pid] = path
    submissions, mapping = [], []
    for row in rows:
        for lane in row['summary']['lanes']:
            identity = f"{row['pair_id']}:{row['variant']}:{lane['candidate_id']}"
            opaque = 'proof_' + hmac.new(salt, identity.encode(), hashlib.sha256).hexdigest()[:24]
            proof_path = destination / 'proofs' / f'{opaque}.md'
            proof_path.parent.mkdir(exist_ok=True)
            proof_path.write_bytes(Path(lane['proof_path']).read_bytes())
            require(sha(proof_path) == lane['proof_file_sha256'], 'Final proof changed during grading export')
            problem_path = problem_paths[row['problem_id']]
            submissions.append({'submission_id': opaque, 'problem_id': row['problem_id'],
                'problem_path': str(problem_path), 'problem_file_sha256': sha(problem_path),
                'proof_path': str(proof_path), 'proof_file_sha256': lane['proof_file_sha256'],
                'required_passes': [1, 2], 'grading_protocol': protocol(row['problem_id'])})
            mapping.append({k: row[k] for k in ('pair_id', 'pair_seed', 'problem_id', 'variant')} |
                           {'submission_id': opaque, 'candidate_id': lane['candidate_id'],
                            'selected_stage': lane['selected_stage'], 'proof_file_sha256': lane['proof_file_sha256']})
    # Random opaque IDs also remove source ordering from the grader's input.
    submissions.sort(key=lambda item: item['submission_id'])
    inputs.write(manifest_path, {'schema': 'refinement-bf-blinded-grading-v1', 'submissions': submissions})
    inputs.write(key_path, {'schema': 'refinement-bf-grading-key-v1', 'plan_sha256': sha(plan_path),
        'private_id_salt': salt.hex(), 'source_bindings': bindings,
        'grading_manifest_sha256': sha(manifest_path), 'mapping': mapping})
    return manifest_path


def export_grading(plan_path: Path) -> Path:
    return _export_loaded(*_load(plan_path))


def _grades(path, manifest):
    value = read(path)
    require(value.get('schema') == 'refinement-bf-grades-v1' and isinstance(value.get('rows'), list),
            'Unsupported grades schema')
    submissions = {row['submission_id']: row for row in manifest['submissions']}
    accepted = {}
    for row in value['rows']:
        require(isinstance(row, dict) and set(row) == {'submission_id', 'pass_index', 'score',
                'proof_file_sha256', 'grader_model', 'protocol'}, 'Unexpected grade fields')
        sid, index = row['submission_id'], row['pass_index']
        require(sid in submissions and type(index) is int and index in (1, 2), 'Unknown submission or grading pass')
        require((sid, index) not in accepted, 'Duplicate submission grade')
        require(type(row['score']) is int and 0 <= row['score'] <= 7, 'Grade must be an integer from 0 to 7')
        require(row['proof_file_sha256'] == submissions[sid]['proof_file_sha256']
                and row['protocol'] == submissions[sid]['grading_protocol'], 'Grade proof hash or protocol mismatch')
        require(isinstance(row['grader_model'], str) and row['grader_model'].strip(), 'Grade lacks a model identity')
        accepted[(sid, index)] = row
    require(set(accepted) == {(sid, index) for sid in submissions for index in (1, 2)},
            'Exactly two grading passes are required for every submitted proof')
    model_policies = {(grading_protocol, index): {
        row['grader_model'] for (sid, p), row in accepted.items()
        if p == index and row['protocol'] == grading_protocol}
        for grading_protocol in {row['protocol'] for row in accepted.values()} for index in (1, 2)}
    require(all(len(models) == 1 for models in model_policies.values()),
            'Within each grading pass, both arms must use the same grader model')
    return accepted


def write_report(plan_path: Path, grades_path: Path | None = None) -> Path:
    plan_path, plan, bank, rows, bindings = _load(plan_path)
    if grades_path is not None:
        require(Path(grades_path).resolve() not in {plan_path.parent / 'REPORT.md', plan_path.parent / 'REPORT.json'},
                'Grade input overlaps report output')
    report = {'schema': 'refinement-bf-report-v1', 'plan_sha256': sha(plan_path),
              'dry_run': plan['dry_run'], 'primary_estimand': PRIMARY, 'arms': [], 'quality': 'pending'}
    lines = ['# Refinement continuation experiment', '', PRIMARY, '',
             'The extended reasoning mechanism, output caps, base prompts, parsers, and seed derivation remain unchanged. '
             'Later proof-dependent seeds may diverge after the arms generate different proofs.', '']
    if plan['dry_run']:
        require(grades_path is None, 'Dry runs cannot import proof grades')
        report.update(quality='not_applicable', state='preflight_passed', model_calls=0)
        lines += ['Dry-run preflight only. No model generation, grading, or quality comparison was performed.']
    else:
        export = _export_loaded(plan_path, plan, bank, rows, bindings)
        manifest = read(export)
        key = read(plan_path.parent / 'grading_key.json')
        grades = _grades(grades_path, manifest) if grades_path is not None else None
        mappings = {(r['pair_id'], r['variant'], r['candidate_id']): r['submission_id'] for r in key['mapping']}
        lines += ['| Pair | Arm | Final stages | Fallback lanes | Wall time (s) | Mean score / 7 |',
                  '|---|---|---|---:|---:|---:|']
        for row in rows:
            summary = row['summary']
            stages = Counter(lane['selected_stage'] for lane in summary['lanes'])
            arm = {k: row[k] for k in ('pair_id', 'pair_seed', 'problem_id', 'variant')}
            arm.update(final_stage_counts=dict(stages),
                completed_checkpoint_counts={stage: sum(any(c['stage'] == stage for c in lane['checkpoints'])
                    for lane in summary['lanes']) for stage in STAGES[1:]},
                fallback_count=sum(lane['selected_stage'] != 'refinement_3' for lane in summary['lanes']),
                elapsed_seconds=summary['elapsed_seconds'], mean_score=None)
            if grades is not None:
                scores = [[grades[(mappings[(row['pair_id'], row['variant'], lane['candidate_id'])], p)]['score']
                           for p in (1, 2)] for lane in summary['lanes']]
                arm.update(mean_score=sum(sum(score) / 2 for score in scores) / 4,
                    both_passes_7_count=sum(score == [7, 7] for score in scores),
                    both_passes_7_rate=sum(score == [7, 7] for score in scores) / 4,
                    grading_pass_7_rates={str(p + 1): sum(score[p] == 7 for score in scores) / 4 for p in (0, 1)},
                    grading_disagreement_count=sum(a != b for a, b in scores),
                    maximum_grading_difference=max(abs(a - b) for a, b in scores))
            report['arms'].append(arm)
            scores_text = 'pending' if arm['mean_score'] is None else f"{arm['mean_score']:.3f}"
            stage_text = ', '.join(f'{stage}: {stages[stage]}' for stage in STAGES if stages[stage])
            lines.append(f"| {row['pair_id']} | {row['variant']} | {stage_text} | {arm['fallback_count']} | "
                         f"{arm['elapsed_seconds']:.1f} | {scores_text} |")
        if grades is None:
            lines += ['', 'Grading pending. No quality gain or loss has been established. '
                      'The blinded export requires two separate 0–7 grading passes for every proof, including fallbacks.']
        else:
            report.update(quality='graded', grades_path=str(Path(grades_path).resolve()),
                          grades_sha256=sha(grades_path), pair_deltas=[])
            by_pair = {}
            for arm in report['arms']:
                by_pair.setdefault(arm['pair_id'], {})[arm['variant']] = arm
            problem_deltas = {}
            lines += ['', '| Pair | Role-specific − original mean score |', '|---|---:|']
            for pair_id, arms in by_pair.items():
                delta = arms['role_specific']['mean_score'] - arms['original']['mean_score']
                pid = arms['original']['problem_id']
                report['pair_deltas'].append({'pair_id': pair_id, 'problem_id': pid, 'delta': delta})
                problem_deltas.setdefault(pid, []).append(delta)
                lines.append(f'| {pair_id} | {delta:+.3f} |')
            report['problem_mean_deltas'] = {pid: sum(values) / len(values) for pid, values in problem_deltas.items()}
            report['mean_problem_delta'] = sum(report['problem_mean_deltas'].values()) / len(problem_deltas)
            lines += ['', f"Distinct problems: {len(problem_deltas)}. Equal-weight mean problem delta: "
                      f"{report['mean_problem_delta']:+.3f}/7. Descriptive comparison only; no independence-based significance claim.", '',
                      '| Pair / arm | Both passes 7/7 | Pass 1 7/7 | Pass 2 7/7 | Grade disagreements | Max difference |',
                      '|---|---:|---:|---:|---:|---:|']
            for arm in report['arms']:
                lines.append(f"| {arm['pair_id']} / {arm['variant']} | {arm['both_passes_7_count']}/4 | "
                    f"{arm['grading_pass_7_rates']['1']:.0%} | {arm['grading_pass_7_rates']['2']:.0%} | "
                    f"{arm['grading_disagreement_count']}/4 | {arm['maximum_grading_difference']} |")
            if any(item['grading_protocol'] == 'unknown' for item in manifest['submissions']):
                lines += ['', 'Some problem IDs have an unknown grading protocol; their scores have no established benchmark-protocol attribution.']
        lines += ['', 'Each arm contains all four final proofs, including fallback proofs. '
                  'Wall time is elapsed arm execution time with concurrent lanes, not a sum of lane durations. '
                  'Token totals, exact physical request counts, and format-failure rates are not reported because they are not fully instrumented.', '',
                  'Share only the grading/ directory with the grader. Keep grading_key.json private until both passes are complete. '
                  'No hosted grading requests are launched by this report.']
    inputs.write(plan_path.parent / 'REPORT.json', report)
    report_path = plan_path.parent / 'REPORT.md'
    report_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return report_path
