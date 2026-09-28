"""Blinded, deduplicated grading for two block-repair arms and an original control."""
from __future__ import annotations

import csv
import hashlib
import hmac
import json
from pathlib import Path
import secrets

from . import report

ARMS = (('t07', 0.7, 'block'), ('t04', 0.4, 'block'), ('original_t04', 0.4, 'original'))
MEANS = ('raw_mean', 't07_mean', 't04_mean', 'original_t04_mean')
CONTRASTS = ('delta_t04_minus_t07', 'delta_t04_minus_original_t04')
PRIMARY = ('Use two grades per unique proof and average four lanes per problem, with equal problem weight. '
           'Compare raw, block repair at 0.7 and 0.4, and original expansion at 0.4. '
           'Identical proof bytes for the same problem and grading configuration share grades. '
           'Lanes and grading passes are not independent problems.')


def _job_identity(job):
    value = {key: item for key, item in job.items() if key not in ('output_dir', 'input_manifest_path',
        'input_manifest_sha256', 'strategy', 'pipeline_config')}
    value['runtime'] = {key: item for key, item in job['runtime'].items() if key != 'repair_temperature'}
    value['candidates'] = [{key: item for key, item in candidate.items() if key != 'proof_path'}
                           for candidate in job['candidates']]
    return value


def _load(path):
    path = Path(path).absolute()
    path = report.file(path, path.parent)
    report.require(path.name not in ('REPORT.json', 'REPORT.md', 'REPORT.csv'), 'Pair plan overlaps report output')
    plan = report.read(path)
    report.require(plan.get('schema') == 'block-local-paired-plan-v1'
        and plan.get('experiment') == report.EXPERIMENT and type(plan.get('dry_run')) is bool
        and plan.get('source_arm') == 'raw' and plan.get('processing_scope') == report.SCOPE
        and type(plan.get('seed')) is int and 0 <= plan['seed'] <= 0xffffffff
        and plan.get('repair_temperatures') == [0.7, 0.4, 0.4], 'Unsupported paired strategy plan')
    arms = plan.get('arms')
    report.require(isinstance(arms, list) and len(arms) == 3
        and [(arm.get('label'), arm.get('repair_temperature'), arm.get('strategy')) for arm in arms] == list(ARMS),
        'Expected sequential block 0.7, block 0.4, and original 0.4 arms')
    loaded, identities, child_paths = {}, {}, []
    for arm in arms:
        label, temperature, strategy = arm['label'], arm['repair_temperature'], arm['strategy']
        child_path = report.file(arm['plan_path'], path.parent)
        report.require(report.sha(child_path) == arm.get('plan_sha256'), 'Paired child plan hash changed')
        child_paths.append(child_path)
        child = report._load(child_path)
        child_plan = child[1]
        report.require(child_plan.get('seed') == plan['seed'] and child_plan.get('dry_run') is plan['dry_run']
            and child_plan.get('repair_temperature') == temperature and child_plan.get('strategy') == strategy,
            'Paired seed, mode, strategy, or repair temperature changed')
        jobs = []
        for entry in child_plan['jobs']:
            job = report.read(entry['job_path'])
            runtime = job.get('runtime', {})
            report.require(type(runtime.get('repair_temperature')) in (int, float)
                and runtime['repair_temperature'] == temperature and runtime.get('workers') == 4,
                'Paired worker temperature or batch size changed')
            jobs.append(_job_identity(job))
        identities[label] = jobs
        loaded[label] = child
    for index, child_path in enumerate(child_paths):
        for other in child_paths[index + 1:]:
            report.require(not child_path.parent.is_relative_to(other.parent)
                and not other.parent.is_relative_to(child_path.parent), 'Paired arm output directories overlap')
    before = loaded['t07'][1]
    for label, _, _ in ARMS[1:]:
        report.require(identities['t07'] == identities[label], 'Paired raw inputs or runtime settings differ beyond intended strategy settings')
        after = loaded[label][1]
        for key in ('source_arm', 'processing_scope', 'bf_mode',
                    'refinements_enabled', 'git_commit', 'code_hashes', 'source_runs', 'version', 'problem_count', 'raw_candidates'):
            report.require(before.get(key) == after.get(key), f'Paired plan configuration changed: {key}')
    if 'code_hashes' in plan:
        report.require(plan['code_hashes'] == before.get('code_hashes'), 'Paired code identity changed')
    return path, plan, loaded


def _signature(item):
    return (item['problem_id'], item['proof_file_sha256'], *(item[key] for key in report.GRADE_CONFIG))


def _opaque(signature, salt):
    payload = json.dumps(signature, ensure_ascii=False, separators=(',', ':')).encode()
    return 'proof_' + hmac.new(salt, payload, hashlib.sha256).hexdigest()[:24]


def _export(loaded):
    path, plan, children = loaded
    report.require(not plan['dry_run'], 'Dry runs have no paired grading export')
    # All three arms must be complete before the first grading metadata access.
    bindings = {str(path): report.sha(path)}
    submissions, mapping_sources, configs = {}, [], {}
    for label, _, _ in ARMS:
        child = children[label]
        manifest_path, _, _ = report._export(child)
        key_path = child[0].parent / 'grading_key.json'
        bindings.update(child[3])
        bindings.update(report.read(key_path)['source_bindings'])
        bindings[str(manifest_path)], bindings[str(key_path)] = report.sha(manifest_path), report.sha(key_path)
        for item in report.read(manifest_path)['submissions']:
            pid = item['problem_id']
            config = tuple(item[key] for key in report.GRADE_CONFIG)
            report.require(pid not in configs or configs[pid] == config, 'Paired grader configurations differ')
            configs[pid] = config
            signature = _signature(item)
            for name, expected in (('proof_path', item['proof_file_sha256']), ('problem_path', item['problem_file_sha256'])):
                source = report.file(item[name], manifest_path.parent)
                report.require(report.sha(source) == expected, 'Child grading snapshot changed')
                bindings[str(source)] = expected
            if signature in submissions:
                report.require(submissions[signature]['problem_file_sha256'] == item['problem_file_sha256'],
                    'Identical grading identifier has differing problem statements')
            submissions.setdefault(signature, item)
            mapping_sources.append((label, item['submission_id'], signature))
    root, folder = path.parent, path.parent / 'grading'
    manifest_path, key_path = folder / 'input_manifest.json', root / 'grading_key.json'
    existing = folder.exists() or key_path.exists()
    if existing:
        key = report.read(report.file(key_path, root))
        report.require(key.get('schema') == 'block-local-paired-grading-key-v1'
            and key.get('source_bindings') == bindings, 'Existing paired grading identity changed')
        salt = bytes.fromhex(key['private_id_salt'])
        report.require(len(salt) == 32, 'Invalid private grading salt')
    else:
        salt = secrets.token_bytes(32)
        folder.mkdir()
    mapping = [{'arm': label, 'child_submission_id': sid, 'submission_id': _opaque(signature, salt)}
               for label, sid, signature in mapping_sources]
    exported = []
    for signature, item in submissions.items():
        sid = _opaque(signature, salt)
        proof_path = folder / 'proofs' / (sid + '.md')
        problem_path = folder / 'problems' / (item['problem_id'] + '.json')
        if not existing:
            proof_path.parent.mkdir(exist_ok=True)
            problem_path.parent.mkdir(exist_ok=True)
            proof_path.write_bytes(Path(item['proof_path']).read_bytes())
            problem_path.write_bytes(Path(item['problem_path']).read_bytes())
        report.require(report.sha(report.file(proof_path, folder)) == item['proof_file_sha256']
            and report.sha(report.file(problem_path, folder)) == item['problem_file_sha256'], 'Paired grading snapshot changed')
        exported.append({**item, 'submission_id': sid, 'proof_path': str(proof_path), 'problem_path': str(problem_path)})
    manifest = {'schema': 'block-local-paired-blinded-grading-v1',
                'submissions': sorted(exported, key=lambda item: item['submission_id'])}
    if existing:
        report.require(key.get('mapping') == mapping and key.get('grading_manifest_sha256') == report.sha(manifest_path)
            and report.read(manifest_path) == manifest, 'Existing paired grading export changed')
    else:
        report.write(manifest_path, manifest)
        key = {'schema': 'block-local-paired-grading-key-v1', 'experiment': report.EXPERIMENT,
               'private_id_salt': salt.hex(), 'source_bindings': bindings, 'mapping': mapping,
               'grading_manifest_sha256': report.sha(manifest_path)}
        report.write(key_path, key)
    for source, expected in bindings.items():
        report.require(report.sha(source) == expected, 'Source changed during paired export')
    return manifest_path, key


def export_grading(pair_plan_path: Path) -> Path:
    return _export(_load(pair_plan_path))[0]


def write_report(pair_plan_path: Path, grades_path: Path | None = None) -> Path:
    loaded = _load(pair_plan_path)
    path, plan, children = loaded
    root = path.parent
    result = {'schema': 'block-local-paired-report-v1', 'experiment': report.EXPERIMENT,
              'plan_sha256': report.sha(path), 'dry_run': plan['dry_run'], 'primary_estimand': PRIMARY,
              'repair_temperatures': [0.7, 0.4, 0.4], 'problems': [], 'lanes': []}
    lines = ['# Paired raw-proof repair strategies', '', PRIMARY, '']
    if plan['dry_run']:
        report.require(grades_path is None, 'Dry runs cannot import paired grades')
        result.update(quality='not_applicable', model_calls=0)
        lines.append('All three arms passed offline preflight. No grading configuration was read and no model was called.')
    else:
        manifest_path, key = _export(loaded)
        manifest = report.read(manifest_path)
        forbidden = [root / f'REPORT.{ext}' for ext in ('json', 'md', 'csv')]
        forbidden += [child[0].parent / f'REPORT.{ext}' for child in children.values() for ext in ('json', 'md', 'csv')]
        if grades_path is not None:
            grades_path = Path(grades_path).resolve()
            report.require(grades_path not in forbidden and not grades_path.is_relative_to(root / 'paired_import'),
                           'Grade input overlaps generated paired report artifacts')
        grade_sha = report.sha(grades_path) if grades_path is not None else None
        grades = report._grades(grades_path, manifest, schema='block-local-paired-grades-v1')
        imported = {}
        if grades is not None:
            digest = grade_sha
            report.require(report.sha(grades_path) == digest, 'Paired grade input changed during import')
            result.update(grades_path=str(grades_path), grades_sha256=digest)
            tasks = {item['submission_id']: item for item in manifest['submissions']}
            for label, _, _ in ARMS:
                rows = []
                for item in key['mapping']:
                    if item['arm'] != label:
                        continue
                    sid = item['submission_id']
                    for index in (1, 2):
                        rows.append({'submission_id': item['child_submission_id'], 'pass_index': index,
                            'score': grades[(sid, index)], 'proof_file_sha256': tasks[sid]['proof_file_sha256'],
                            **{name: tasks[sid][name] for name in report.GRADE_CONFIG}})
                target = root / 'paired_import' / digest / (label + '.json')
                value = {'schema': 'block-local-grades-v1', 'rows': rows}
                if target.exists():
                    report.require(report.read(target) == value, 'Imported child grades changed')
                else:
                    report.write(target, value)
                imported[label] = target
        child_results = {}
        for label, _, _ in ARMS:
            child_report = report.write_report(children[label][0], imported.get(label))
            child_results[label] = report.read(child_report.with_suffix('.json'))
        portfolios = {label: {(lane['problem_id'], lane['candidate_id']): lane
            for lane in child_results[label]['lanes']} for label, _, _ in ARMS}
        first = portfolios['t07']
        report.require(all(portfolio.keys() == first.keys() for portfolio in portfolios.values()), 'Paired result portfolio differs')
        for identity, before in first.items():
            report.require(all(before['baseline_scores'] == portfolio[identity]['baseline_scores']
                for portfolio in portfolios.values()), 'Paired raw grades differ')
            means = {label + '_mean': portfolio[identity]['post_mean'] for label, portfolio in portfolios.items()}
            result['lanes'].append({'problem_id': identity[0], 'candidate_id': identity[1],
                'raw_mean': before['baseline_mean'], **means,
                'delta_t04_minus_t07': None if grades is None else means['t04_mean'] - means['t07_mean'],
                'delta_t04_minus_original_t04': None if grades is None else means['t04_mean'] - means['original_t04_mean']})
        for pid in dict.fromkeys(lane['problem_id'] for lane in result['lanes']):
            subset = [lane for lane in result['lanes'] if lane['problem_id'] == pid]
            report.require(len(subset) == 4, 'Paired problem is missing a lane')
            result['problems'].append({'problem_id': pid, **{name: report._mean([lane[name] for lane in subset])
                for name in (*MEANS, *CONTRASTS)}})
        result.update(quality='pending' if grades is None else 'graded', unique_proof_count=len(manifest['submissions']),
            required_grade_count=2 * len(manifest['submissions']),
            child_submission_count=len(key['mapping']), deduplicated_submission_count=len(key['mapping']) - len(manifest['submissions']),
            equal_weight_problem_deltas={name: report._mean([row[name] for row in result['problems']]) for name in CONTRASTS},
            arm_metrics={label: child_results[label].get('all_portfolio') for label, _, _ in ARMS})
        result['equal_weight_problem_means'] = {name: report._mean([row[name] for row in result['problems']])
            for name in MEANS}
        if grades is not None:
            result['contrast_counts'] = {contrast: {name: sum(test(row[contrast]) for row in result['lanes'])
                for name, test in (('improved', lambda x: x > 0), ('worsened', lambda x: x < 0), ('unchanged', lambda x: x == 0))}
                for contrast in CONTRASTS}
        lines += [f"Unique proofs: {result['unique_proof_count']}; required grading passes: {result['required_grade_count']}.", '',
                  '| Problem | Raw / 7 | Block 0.7 / 7 | Block 0.4 / 7 | Original 0.4 / 7 | Block 0.4 − 0.7 | Block − original at 0.4 |',
                  '|---|---:|---:|---:|---:|---:|---:|']
        for row in result['problems']:
            cells = ['pending' if row[name] is None else f'{row[name]:.3f}'
                     for name in (*MEANS, *CONTRASTS)]
            lines.append(f"| {row['problem_id']} | {' | '.join(cells)} |")
        if grades is not None:
            for contrast, description in zip(CONTRASTS, ('Block 0.4 versus block 0.7', 'Block versus original at 0.4')):
                lines += ['', description + ' proof means: ' + ', '.join(
                    f'{name} {count}' for name, count in result['contrast_counts'][contrast].items()) + '.',
                    f"Equal-weight mean problem delta: {result['equal_weight_problem_deltas'][contrast]:+.3f}/7."]
            for label, temperature, strategy in ARMS:
                metrics = result['arm_metrics'][label]
                lines.append(f"{strategy.capitalize()} {temperature} versus raw: improved {metrics['improved_count']}; "
                    f"worsened {metrics['worse_count']}; unchanged {metrics['same_count']}; "
                    f"both-pass full-credit retention {metrics['both_passes_7_retained_count']}/"
                    f"{metrics['both_passes_7_retention_denominator']}.")
        else:
            lines += ['', 'Grading pending; no quality gain or loss is established.']
        lines += ['', 'Runs used a fixed order: block 0.7, block 0.4, then original 0.4; this is a descriptive paired comparison.',
                  'The original control uses the original lazy-check/whole-proof expansion workflow without audit/resolve. '
                  'The block-versus-original contrast includes those added stages and does not isolate block editing at matched compute.',
                  'Child reports retain raw-to-final regressions, full-credit retention, fallback outcomes and timing.',
                  'Only the parent grading directory is intended for the grader; keep every grading_key.json private.',
                  'Edit-confinement checks apply only to the block arms. ' + report.LIMITATION]
        for source, expected in key['source_bindings'].items():
            report.require(report.sha(source) == expected, 'Source changed during paired reporting')
        if grades_path is not None:
            report.require(report.sha(grades_path) == grade_sha, 'Paired grade input changed during reporting')
    report.write(root / 'REPORT.json', result)
    output = root / 'REPORT.md'
    output.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    with (root / 'REPORT.csv').open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=['problem_id', 'candidate_id', *MEANS, *CONTRASTS])
        writer.writeheader()
        writer.writerows(result['lanes'])
    return output
