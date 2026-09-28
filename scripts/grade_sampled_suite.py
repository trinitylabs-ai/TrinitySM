#!/usr/bin/env python3
"""Grade a completed 6+3+3 suite separately from generation, using its saved final proofs."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import urllib.request

import prepare_imo_references
import score_imo_v2
import score_proofbench

ROOT = Path(__file__).resolve().parents[1]
GROUPS = {'imo2026': 6, 'imo-proofbench/basic': 3, 'imo-proofbench/advanced': 3}
CANDIDATES = ('t10_r01', 't10_r02', 't07_r01', 't07_r02')
STAGES = {'raw', 'lazy_checked', 'refinement_1', 'refinement_2', 'refinement_3'}
MODEL = 'gpt-5.6-sol'
EFFORT = 'xhigh'
PROOFBENCH_PASSES = 2


def require(ok, message):
    if not ok:
        raise ValueError(message)


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def text_digest(text):
    return digest(text.strip().encode('utf-8'))


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def identifier(value):
    require(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,127}', value), 'Invalid run/grading ID')
    return value


def inside(path, base):
    path, base = Path(path).absolute(), Path(base).absolute()
    require(path.is_relative_to(base) and path.resolve().is_relative_to(base.resolve()),
            f'Path escapes expected directory: {path}')
    require(not any(p.is_symlink() for p in (path, *path.parents) if p.is_relative_to(base)),
            f'Symlink in artifact path: {path}')
    return path


def checked(path, base, expected=None):
    path = inside(path, base)
    require(path.is_file(), f'Missing input: {path}')
    if expected is not None:
        require(digest(path.read_bytes()) == expected, f'Input hash mismatch: {path}')
    return path


def relative(path):
    return str(Path(path).relative_to(ROOT))


def references(dataset_path, download=False):
    """Preflight both rubrics and reference sources before any paid grading call."""
    score_imo_v2.prepare_runner()
    b5 = score_proofbench.prepare_runner()
    _, source = b5.template_and_source()
    inventory = read(ROOT / 'docs/public_release/grading/imo2026_reference_sources.json')
    if download:
        prepare_imo_references.prepare(inventory, ROOT,
            ROOT / '.workshop/external-references/mechmath-imo2026', download=True)
        if not dataset_path.exists():
            request = urllib.request.Request(source['dataset_url'], headers={'User-Agent': 'ProofWorkshop-grading'})
            with urllib.request.urlopen(request, timeout=60) as response:
                data = response.read()
            require(digest(data) == source['dataset_sha256'], 'Downloaded ProofBench dataset hash mismatch')
            dataset_path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=dataset_path.parent, delete=False) as stream:
                stream.write(data)
                temporary = Path(stream.name)
            temporary.replace(dataset_path)
    require(dataset_path.is_file(), 'ProofBench dataset missing; use --download-references or --dataset PATH')
    dataset, dataset_hash = b5.dataset_rows(dataset_path, source['dataset_sha256'])
    imo = {}
    for row in inventory['references']:
        paths = [ROOT / item['path'] for item in row['local_grading_inputs']]
        path = next((p for p in paths if p.is_file()), None)
        require(path is not None, 'IMO references missing; use --download-references '
                '(see docs/public_release/grading/README.md)')
        checked(path, ROOT)
        require(text_digest(path.read_text(encoding='utf-8')) == row['reference_sha256'],
                f'IMO reference hash mismatch: {path}')
        imo[row['problem_id']] = {'path': str(path), 'sha256': row['reference_sha256']}
    return {'imo': imo, 'dataset': dataset, 'dataset_sha256': dataset_hash,
            'dataset_path': str(dataset_path), 'b5_prompt_sha256': source['prompt_sha256']}


def inspect_suite(run_id):
    """Use the controller's final selection, never choose a checkpoint by a grade."""
    identifier(run_id)
    suite = ROOT / '.workshop/runs' / run_id
    plan_path, status_path = suite / 'plan.json', suite / 'status.json'
    plan, status = read(checked(plan_path, ROOT)), read(checked(status_path, ROOT))
    require(plan.get('schema') == 'workshop-sampled-suite-v1' and plan.get('run_id') == run_id,
            'Not the requested sampled-suite plan')
    require(status.get('state') == 'completed', 'Suite is not completed; finish generation before grading')
    jobs, outcomes = plan['jobs'], status['outcomes']
    require(len(jobs) == 3 and {j['benchmark'] for j in jobs} == set(GROUPS), 'Expected all three benchmarks')
    require(len(outcomes) == 3 and {j['benchmark'] for j in outcomes} == set(GROUPS)
            and all(j['returncode'] == 0 for j in outcomes), 'Generation outcomes are incomplete')
    require(plan.get('problem_count') == 12 and plan.get('candidates_per_problem') == 4, 'Expected 12 problems / 48 lanes')
    sources = {relative(p): digest(p.read_bytes()) for p in (plan_path, status_path)}
    result = []
    for job in jobs:
        benchmark, ids = job['benchmark'], job['problem_ids']
        pattern = r'imo2026_p[1-6]' if benchmark == 'imo2026' else (
            r'PB-Basic-\d{3}' if benchmark.endswith('/basic') else r'PB-Advanced-\d{3}')
        require(len(ids) == GROUPS[benchmark] and len(set(ids)) == len(ids)
                and all(re.fullmatch(pattern, pid) for pid in ids), 'Invalid problem selection')
        experiment = inside(ROOT / 'benchmarks' / benchmark / 'results' / run_id, ROOT)
        run = experiment / 'generation/run'
        inputs = {row['problem_id']: row for row in job['inputs']}
        require(set(inputs) == set(ids) and len(job['inputs']) == len(ids), 'Statement selection differs from plan')
        catalog = checked(ROOT / 'benchmarks' / benchmark / 'catalog.json', ROOT, job['catalog_sha256'])
        catalog_rows = {r['problem_id']: r for r in read(catalog)['generation_inputs']['files']}
        finals_path = checked(run / 'final_results.json', run)
        final = read(finals_path)
        identity_path = checked(experiment / 'experiment.json', experiment)
        completion_path = checked(experiment / 'generation/completion.json', experiment)
        identity, completion = read(identity_path), read(completion_path)
        require(identity.get('run_id') == run_id and identity.get('benchmark') == benchmark
                and identity.get('state') == 'completed', f'Experiment incomplete: {benchmark}')
        require(completion.get('worker_exited') is True and completion.get('returncode') == 0,
                f'Generation worker not finished: {benchmark}')
        require(final.get('state') in {'completed', 'completed_with_fallbacks'}
                and final['execution'].get('state') == 'completed'
                and final['execution'].get('returncode') == 0, f'Final export incomplete: {benchmark}')
        expected = {(pid, cid) for pid in ids for cid in CANDIDATES}
        lanes = final['lanes']
        require(len(lanes) == len(expected) and {(r['problem_id'], r['candidate_id']) for r in lanes} == expected,
                f'Final proof coverage differs from plan: {benchmark}')
        times = {}
        sequence = run / 'problem_sequence.json'
        if sequence.exists():
            checked(sequence, run)
            for p in read(sequence)['problems']:
                elapsed = p.get('elapsed_seconds')
                require(elapsed is None or (isinstance(elapsed, (float, int)) and math.isfinite(elapsed) and elapsed >= 0),
                        'Invalid generation timing')
                times[p['problem_id']] = {'elapsed_seconds': elapsed, 'resumed': bool(p.get('resumed'))}
            sources[relative(sequence)] = digest(sequence.read_bytes())
        rows = []
        for row in lanes:
            pid, cid, stage = row['problem_id'], row['candidate_id'], row.get('selected_stage')
            require(row.get('proof_available') is True and stage in STAGES
                    and row.get('state') == ('completed' if stage == 'refinement_3' else 'completed_with_fallback'),
                    f'Invalid final selection: {pid}/{cid}')
            proof = checked(run / row['proof'], run, row['sha256'])
            producer = checked(run / row['producer'], run)
            receipt = checked(run / row['completion_record'], run)
            require(proof.read_bytes() == producer.read_bytes(), 'Export differs from producer')
            require(proof.read_text(encoding='utf-8').strip()
                    and text_digest(proof.read_text(encoding='utf-8')) == row['proof_sha256'], 'Final proof text hash mismatch')
            item = inputs[pid]
            require(item == catalog_rows[pid], f'Statement metadata changed: {pid}')
            statement = checked(ROOT / 'benchmarks' / benchmark / item['path'],
                                ROOT / 'benchmarks' / benchmark / 'problems', item['sha256'])
            payload = read(statement)
            require(payload.get('problem_id') == pid, 'Statement problem identity mismatch')
            text = str(payload.get('claim') or payload.get('problem') or payload.get('statement') or '').strip()
            require(bool(text), 'Empty problem statement')
            rows.append({'problem_id': pid, 'candidate_id': cid, 'selected_stage': stage,
                         'proof_path': relative(proof), 'proof_sha256': row['proof_sha256'],
                         'proof_file_sha256': row['sha256'], 'problem_path': relative(statement),
                         'problem_sha256': text_digest(text), 'fallback_used': stage != 'refinement_3',
                         **times.get(pid, {'elapsed_seconds': None, 'resumed': False})})
            for path in (proof, producer, receipt, statement):
                sources[relative(path)] = digest(path.read_bytes())
        for path in (catalog, finals_path, identity_path, completion_path):
            sources[relative(path)] = digest(path.read_bytes())
        result.append({'benchmark': benchmark, 'experiment': relative(experiment), 'rows': rows})
    return {'run_id': run_id, 'sample_seed': plan.get('sample_seed'),
            'generation_seed': plan.get('generation_seed'), 'seed_namespace': plan.get('seed_namespace'),
            'jobs': result, 'source_hashes': sources}


def verify_sources(suite):
    for path, expected in suite['source_hashes'].items():
        checked(ROOT / path, ROOT, expected)


def bind_references(suite, refs):
    for job in suite['jobs']:
        for row in job['rows']:
            pid = row['problem_id']
            if job['benchmark'] == 'imo2026':
                row['reference_sha256'] = refs['imo'][pid]['sha256']
            else:
                official = refs['dataset'][pid]
                require(row['problem_sha256'] == text_digest(official['problem']),
                        f'Generated statement differs from the official grading dataset: {pid}')
                row.update(reference_sha256=text_digest(official['reference']),
                           guidelines_sha256=text_digest(official['guidelines']))


def prepare_job(job, refs, grading_id):
    experiment = ROOT / job['experiment']
    work = experiment / 'grading/work' / grading_id
    work.mkdir(parents=True, exist_ok=False)
    tasks = []
    for row in job['rows']:
        pid, cid = row['problem_id'], row['candidate_id']
        inputs = work / 'inputs' / pid
        inputs.mkdir(parents=True, exist_ok=True)
        proof = inputs / (cid + '.md')
        proof.write_bytes((ROOT / row['proof_path']).read_bytes())
        hashes = {key: row[key] for key in ('problem_sha256', 'reference_sha256', 'proof_sha256')}
        task = {'problem_id': pid, 'candidate_id': cid, 'proof_path': str(proof), 'expected_hashes': hashes}
        if job['benchmark'] == 'imo2026':
            statement, reference = inputs / 'problem.json', inputs / 'reference.txt'
            statement.write_bytes((ROOT / row['problem_path']).read_bytes())
            reference.write_text(Path(refs['imo'][pid]['path']).read_text(encoding='utf-8').strip(), encoding='utf-8')
            task.update(problem_number=int(pid.rsplit('p', 1)[1]), problem_path=str(statement), reference_path=str(reference))
        else:
            hashes['guidelines_sha256'] = row['guidelines_sha256']
        tasks.append(task)
    manifest = work / 'tasks.json'
    write(manifest, {'schema': ('gold-informed-generic-proof-task-manifest-v1'
                               if job['benchmark'] == 'imo2026' else 'workshop-b5-final-proof-tasks-v1'), 'tasks': tasks})
    return work, manifest


class Interrupted(Exception):
    pass


def run_command(command, log_path):
    child = None
    def stop(signum, _frame):
        if child is not None and child.poll() is None:
            os.killpg(child.pid, signal.SIGTERM)
        raise Interrupted(f'Stopped by {signal.Signals(signum).name}')
    previous = {s: signal.signal(s, stop) for s in (signal.SIGTERM, signal.SIGINT)}
    try:
        with log_path.open('w') as stream:
            child = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT, cwd=ROOT,
                                     start_new_session=True, env=dict(os.environ, PYTHONUNBUFFERED='1'))
            return child.wait()
    finally:
        for s, handler in previous.items():
            signal.signal(s, handler)
        if child is not None and child.poll() is None:
            os.killpg(child.pid, signal.SIGTERM)
            try:
                child.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()


def validate_grades(job, output, refs):
    summary = read(output / 'summary.json')
    require(summary.get('state') == 'completed', f'Incomplete grading batch: {output}')
    expected = {(r['problem_id'], r['candidate_id']): r for r in job['rows']}
    rows = summary['rows']
    require(len(rows) == len(expected) and {(r['problem_id'], r['candidate_id']) for r in rows} == set(expected),
            'Grading coverage differs from selected final proofs')
    strict = job['benchmark'] == 'imo2026'
    for row in rows:
        bound = expected[row['problem_id'], row['candidate_id']]
        keys = ('problem_sha256', 'reference_sha256', 'proof_sha256') + (() if strict else ('guidelines_sha256',))
        require(all(row.get(k) == bound[k] for k in keys), 'Grade input hash mismatch')
        score = (row.get('grade') or {}).get('score')
        require(row.get('state') == 'completed' and type(score) is int
                and score in (range(8) if strict else (0, 1, 6, 7)), 'Missing or invalid score')
        require(row.get('grader' if strict else 'model') == MODEL and row.get('reasoning_effort') == EFFORT,
                'Grader model/effort differs from the study')
        if strict:
            require(row.get('policy_mode') == 'strict' and row.get('policy_sha256') == score_imo_v2.POLICY_SHA256,
                    'Strict v2 policy mismatch')
            case = output / f"p{int(row['problem_id'].rsplit('p', 1)[1])}" / row['candidate_id']
            saved = read(case / 'summary.json')
            require(saved == row, 'Strict summary differs from per-proof grade')
            audit = read(case / 'isolation_audit.json')
            require(audit.get('tool_calls') == 0 and audit.get('successful_processes_audited') is True,
                    'Strict evaluator isolation was not verified')
        else:
            require(row.get('policy_mode') == 'imobench-proof-autograder-b5-v1'
                    and row.get('prompt_template_sha256') == refs['b5_prompt_sha256']
                    and row.get('dataset_sha256') == refs['dataset_sha256'], 'B.5 grading policy mismatch')
            case = output / 'cases' / row['problem_id'] / row['candidate_id']
            saved = read(case / 'result.json')
            require(all(saved.get(k) == row.get(k) for k in (*keys, 'grade', 'state', 'model', 'policy_mode')),
                    'B.5 summary differs from per-proof grade')
            audit = read(case / 'isolation_audit.json')
            require(audit.get('tool_calls') == 0 and audit.get('completed_turns') == 1,
                    'B.5 evaluator isolation was not verified')
            response = (case / 'grade.md').read_text(encoding='utf-8')
            require(digest(response.encode('utf-8')) == saved.get('response_sha256') == row.get('response_sha256')
                    and re.findall(r'<points>\s*([0167])\s+out\s+of\s+7\s*</points>', response) == [str(score)],
                    'B.5 explanation differs from the reported grade')
    return rows


def metrics(rows):
    groups = {}
    for row in rows:
        groups.setdefault(row['problem_id'], []).append(row)
    problems = []
    for pid, group in sorted(groups.items()):
        require(len(group) == 4 and {r['candidate_id'] for r in group} == set(CANDIDATES), 'Expected four graded lanes')
        scores = [r['grade']['score'] for r in group]
        problems.append({'problem_id': pid, 'scores': {r['candidate_id']: r['grade']['score'] for r in group},
                         'average': sum(scores) / 4, 'oracle_at_4': max(scores),
                         'fully_refined_lanes': sum(r['selected_stage'] == 'refinement_3' for r in group),
                         'fallback_lanes': sum(r['fallback_used'] for r in group),
                         'elapsed_seconds': group[0]['elapsed_seconds'], 'resumed': group[0]['resumed']})
    return {'problems': problems, 'average_points': sum(r['average'] for r in problems),
            'oracle_at_4_points': sum(r['oracle_at_4'] for r in problems), 'maximum_points': 7 * len(problems)}


def mean_grade_metrics(passes):
    """Average repeated grades for each bound proof before choosing the oracle."""
    require(len(passes) in (1, 2), 'Expected one diagnostic pass or two grading passes')
    indexed = []
    for rows in passes:
        by_id = {(row['problem_id'], row['candidate_id']): row for row in rows}
        require(len(by_id) == len(rows), 'Duplicate proof in a grading pass')
        indexed.append(by_id)
    require(all(rows.keys() == indexed[0].keys() for rows in indexed),
            'Grading passes must contain the same proofs')
    averaged = []
    for key, first in indexed[0].items():
        repeats = [rows[key] for rows in indexed]
        for row in repeats:
            require(all(row[field] == first[field] for field in (
                'proof_file_sha256', 'proof_sha256', 'selected_stage')),
                'Repeated grades must bind to the same submitted proof')
        # These transient rows only feed arithmetic; the original grade records,
        # categories and explanations remain unchanged in the published passes.
        averaged.append(dict(first, grade={'score': sum(row['grade']['score'] for row in repeats) / len(repeats)}))
    return metrics(averaged)


def report_text(summary):
    lines = ['# Sampled-suite grading', '', f"Run: `{summary['run_id']}`; grading: `{summary['grading_id']}`.", '',
             f"State: **{summary['state']}**. Grader: {MODEL} / {EFFORT}.",
             f"Sampling seed: {summary['sample_seed']}; generation seed: {summary['generation_seed']}.", '',
             'Separate automated grading, not formal proof verification or an official IMO jury result.',
             'Each lane submits its saved last completed proof; grades never choose the checkpoint.',
             'Oracle@4 is the best of four graded lanes, not a selected single submission.',
             f"Grading passes: IMO {summary.get('imo_passes', 2)}; ProofBench {summary.get('proofbench_passes', 2)} (B.5).",
             'Use the mean of the two grades for each proof, then average the lanes within each problem. '
             'Oracle@4 is the highest mean proof score, not the mean of the two pass oracles. '
             'Problems have equal weight; both original grading passes are retained.',
             *([] if summary.get('imo_passes', 2) == 2 else
               ['IMO is a single-pass diagnostic, not the published two-pass protocol.']),
             'Generation times include the problem\'s refinement attempts and exclude grading.', '',
             '| Set | Aggregation | Average | Oracle@4 |', '|---|---|---:|---:|']
    for job in summary['jobs']:
        if job['state'] != 'completed':
            lines.append(f"| {job['benchmark']} | — | incomplete | incomplete |")
            continue
        m = job['metrics']
        aggregation = 'Mean of 2 grades' if len(job['passes']) == 2 else 'Single-pass diagnostic'
        lines.append(f"| {job['benchmark']} | {aggregation} | {m['average_points']:g}/{m['maximum_points']} | {m['oracle_at_4_points']:g}/{m['maximum_points']} |")
    lines += ['', '| Problem | ' + ' | '.join(CANDIDATES) + ' | Average | Oracle@4 | C3 | Fallback | Generation (min) |',
              '|---|' + '---:|' * 9]
    for job in summary['jobs']:
        if job['state'] != 'completed':
            continue
        for p in job['metrics']['problems']:
            elapsed = 'unavailable' if p['elapsed_seconds'] is None else f"{p['elapsed_seconds'] / 60:.2f}"
            if p['resumed']:
                elapsed += ' (resumed segment)'
            lines.append(f"| {p['problem_id']} | " + ' | '.join(str(p['scores'][c]) for c in CANDIDATES)
                         + f" | {p['average']:g} | {p['oracle_at_4']} | {p['fully_refined_lanes']} | {p['fallback_lanes']} | {elapsed} |")
    lines += ['', 'All pass scores, proof hashes, selected stages and grading failures are retained in `summary.json`.', '']
    return '\n'.join(lines)


def publish_job(job, passes, grading_id):
    experiment = ROOT / job['experiment']
    strict = job['benchmark'] == 'imo2026'
    annotated = []
    evidence = []
    for number, rows in enumerate(passes, 1):
        by_id = {(r['problem_id'], r['candidate_id']): r for r in rows}
        batch = []
        for bound in job['rows']:
            pid, cid = bound['problem_id'], bound['candidate_id']
            native = by_id[pid, cid]
            output = experiment / 'grading/work' / grading_id / f'pass_{number}'
            case = output / (f"p{int(pid.rsplit('p', 1)[1])}" if strict else f'cases/{pid}') / cid
            source = case / ('summary.json' if strict else 'result.json')
            row = dict(bound, grade=native['grade'], model=MODEL, reasoning_effort=EFFORT,
                       policy_mode=native['policy_mode'], pass_number=number,
                       native_result=relative(source), native_result_sha256=digest(source.read_bytes()),
                       isolation_audit_sha256=digest((case / 'isolation_audit.json').read_bytes()))
            for key in ('policy_sha256', 'prompt_template_sha256', 'dataset_sha256', 'response_sha256',
                        'new_model_call', 'failed_attempts', 'errors'):
                if key in native:
                    row[key] = native[key]
            destination = experiment / 'grades' / grading_id / f'pass_{number}' / pid / (cid + '.json')
            if not strict:
                explanation = destination.with_suffix('.md')
                explanation.parent.mkdir(parents=True, exist_ok=True)
                explanation.write_bytes((case / 'grade.md').read_bytes())
                row['explanation'] = relative(explanation)
                evidence.append({'path': str(explanation.relative_to(experiment)),
                                 'sha256': digest(explanation.read_bytes())})
            write(destination, row)
            evidence.append({'path': str(destination.relative_to(experiment)), 'sha256': digest(destination.read_bytes())})
            batch.append(row)
        annotated.append(batch)
    totals = [metrics(rows) for rows in annotated]
    mean_metrics = mean_grade_metrics(annotated)
    for row in job['rows']:
        destination = experiment / 'proofs' / grading_id / row['problem_id'] / (row['candidate_id'] + '.md')
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((ROOT / row['proof_path']).read_bytes())
    result = {'benchmark': job['benchmark'], 'state': 'completed',
              'aggregation': 'mean_of_two_grades_per_proof' if len(annotated) == 2 else 'single_grading_pass',
              'metrics': mean_metrics, 'passes': [{'pass': n + 1, 'metrics': totals[n], 'rows': rows}
                                                     for n, rows in enumerate(annotated)]}
    grade_path = experiment / 'grades' / grading_id / 'summary.json'
    write(grade_path, result)
    manifest_path = experiment / 'manifest.json'
    manifest = read(manifest_path) if manifest_path.exists() else {
        'schema': 'workshop-graded-experiment-v1', 'run_id': experiment.name, 'benchmark': job['benchmark']}
    require(manifest.get('run_id') == experiment.name, 'Existing experiment manifest belongs to another run')
    manifest.setdefault('grading_runs', {})[grading_id] = {
        'grades': str(grade_path.relative_to(experiment)), 'grades_sha256': digest(grade_path.read_bytes()),
        'model': MODEL, 'reasoning_effort': EFFORT, 'grading_evidence': evidence,
        'proofs': [{'problem_id': r['problem_id'], 'candidate_id': r['candidate_id'],
                    'path': f"proofs/{grading_id}/{r['problem_id']}/{r['candidate_id']}.md",
                    'sha256': r['proof_file_sha256'], 'proof_sha256': r['proof_sha256']} for r in job['rows']]}
    write(manifest_path, manifest)
    return result


def refresh_index(job, run_id):
    subprocess.run([sys.executable, '-B', str(ROOT / 'benchmarks/run_experiment.py'),
                    '--benchmark', job['benchmark'], '--run-id', run_id, '--index-only'],
                   check=True, cwd=ROOT)


def execute(suite, refs, grading_id, workers, imo_passes, report_root):
    report_root.mkdir(parents=True, exist_ok=False)
    write(report_root / 'manifest.json', dict(suite, grading_id=grading_id, created_at=now(),
          model=MODEL, reasoning_effort=EFFORT, imo_passes=imo_passes, proofbench_passes=PROOFBENCH_PASSES,
          strict_policy_sha256=score_imo_v2.POLICY_SHA256, b5_prompt_sha256=refs['b5_prompt_sha256'],
          dataset_sha256=refs['dataset_sha256']))
    summary = {k: suite[k] for k in ('run_id', 'sample_seed', 'generation_seed')}
    summary.update(grading_id=grading_id, imo_passes=imo_passes, proofbench_passes=PROOFBENCH_PASSES,
                   state='running', started_at=now(), jobs=[])
    def save():
        write(report_root / 'summary.json', summary)
        (report_root / 'REPORT.md').write_text(report_text(summary), encoding='utf-8')
    save()
    try:
        for job in suite['jobs']:
            verify_sources(suite)
            work, task_manifest = prepare_job(job, refs, grading_id)
            passes, errors = [], []
            count = imo_passes if job['benchmark'] == 'imo2026' else PROOFBENCH_PASSES
            for number in range(1, count + 1):
                output = work / f'pass_{number}'
                command = [sys.executable, '-u', '-B', str(ROOT / 'scripts' /
                    ('score_imo_v2.py' if job['benchmark'] == 'imo2026' else 'score_proofbench.py'))]
                command += ['--generic-task-manifest' if job['benchmark'] == 'imo2026' else '--task-manifest', str(task_manifest),
                            '--output-dir', str(output), '--workers', str(workers), '--reasoning-effort', EFFORT]
                if job['benchmark'] != 'imo2026':
                    command += ['--dataset', refs['dataset_path'], '--model', MODEL]
                log = work / f'pass_{number}.log'
                print(f"{job['benchmark']}: grading pass {number}/{count}; log={log}", flush=True)
                code = run_command(command, log)
                try:
                    require(code == 0, f'Grader exited {code}; see {log}')
                    passes.append(validate_grades(job, output, refs))
                except (ValueError, OSError, KeyError) as error:
                    errors.append({'pass': number, 'error': str(error), 'output': relative(output)})
            verify_sources(suite)
            if errors:
                result = {'benchmark': job['benchmark'], 'state': 'failed', 'errors': errors}
            else:
                result = publish_job(job, passes, grading_id)
            summary['jobs'].append(result)
            save()
            report = ROOT / job['experiment'] / 'reports' / (grading_id + '.md')
            report.parent.mkdir(parents=True, exist_ok=True)
            report.write_text(report_text(dict(summary, state=result['state'], jobs=[result])), encoding='utf-8')
            if result['state'] == 'completed':
                refresh_index(job, suite['run_id'])
            print(f"{job['benchmark']}: {result['state']}", flush=True)
        summary['state'] = 'completed' if all(j['state'] == 'completed' for j in summary['jobs']) else 'failed'
    except Interrupted as error:
        summary.update(state='interrupted', error=str(error))
    except Exception as error:
        summary.update(state='failed', error=f'{type(error).__name__}: {error}')
        raise
    finally:
        summary['finished_at'] = now()
        save()
    print(f"Grading {summary['state']}: {report_root / 'REPORT.md'}", flush=True)
    return 0 if summary['state'] == 'completed' else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--grading-id', default=None, help='Unique repeat ID (default: UTC timestamp)')
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--imo-passes', type=int, choices=(1, 2), default=2,
                        help='Default 2 reports the mean of both grades per proof; 1 is a diagnostic')
    parser.add_argument('--dataset', type=Path, default=ROOT / '.workshop/external-references/proofbench_v2.csv')
    parser.add_argument('--download-references', action='store_true',
                        help='Download hash-pinned evaluator inputs; see grading reference setup documentation')
    parser.add_argument('--dry-run', action='store_true', help='Validate inputs and print plan, without grading/output directories')
    args = parser.parse_args(argv)
    try:
        require(args.workers > 0, 'workers must be positive')
        grading_id = identifier(args.grading_id or datetime.now(timezone.utc).strftime('grading_%Y%m%dT%H%M%S%fZ'))
        suite = inspect_suite(args.run_id)
        report_root = inside(ROOT / 'benchmarks/reports' / (args.run_id + '_grading') / grading_id, ROOT)
        destinations = [report_root]
        for job in suite['jobs']:
            destinations.extend(ROOT / job['experiment'] / sub / grading_id for sub in ('grading/work', 'proofs', 'grades'))
            destinations.append(ROOT / job['experiment'] / 'reports' / (grading_id + '.md'))
            existing = ROOT / job['experiment'] / 'manifest.json'
            if existing.exists():
                checked(existing, ROOT)
                manifest = read(existing)
                require(manifest.get('run_id') == args.run_id and manifest.get('benchmark') == job['benchmark'],
                        'Existing experiment manifest identity differs')
                require(grading_id not in manifest.get('grading_runs', {}), 'Grading ID already recorded in experiment manifest')
        for path in destinations:
            inside(path, ROOT)
            require(not path.exists(), f'Grading ID already exists; choose a new --grading-id: {path}')
        refs = references(args.dataset.expanduser().absolute(), args.download_references)
        bind_references(suite, refs)
        print(f"Run: {args.run_id}\nGrading ID: {grading_id}\nProofs: 48; IMO passes: {args.imo_passes}; B.5 passes: {PROOFBENCH_PASSES}\nReport: {report_root / 'REPORT.md'}", flush=True)
        if args.dry_run:
            print('Preflight passed. No grading calls or result directories created.', flush=True)
            return 0
        require(shutil.which('codex') is not None, 'Authenticated Codex CLI required on this machine; codex was not found')
        return execute(suite, refs, grading_id, args.workers, args.imo_passes, report_root)
    except (ValueError, OSError, KeyError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    raise SystemExit(main())
