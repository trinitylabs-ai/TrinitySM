#!/usr/bin/env python3
"""Grade any completed single-GPU problem selection and compare saved baselines.

Generation is performed separately by run_single_gpu.py. This adapter reuses
the existing isolated Codex CLI graders without running or changing inference.
"""
import argparse
from datetime import datetime, timezone
import importlib.util
import math
from pathlib import Path
import shutil

import grade_sampled_suite as grading

ROOT = Path(__file__).resolve().parents[1]
STUDY = 'docs/reproduction/single_gpu_baselines.json'
QWEN_POLICY = 'qwen_only_full_round_robin_seed_order_ties'
LEGACY_POLICY = 'dual_model_full_round_robin_seed_order_ties'
POLICY_LABELS = {QWEN_POLICY: 'Qwen-only', LEGACY_POLICY: 'Gemma+Qwen'}


def verify_recovered_selection(run, pid, claim, runtime, final, selection, bound):
    """Read-only verification of a format-only recovery; never erase exit 1."""
    sequence = grading.read(bound(run / 'problem_sequence.json', run))
    execution = grading.read(bound(run / 'pipeline_execution.json', run))
    grading.require(execution == final['execution'] and sequence.get('inference_finished') is True
                    and sequence.get('state') == 'failed' and sequence.get('returncode') == 1
                    and len(sequence.get('problems', [])) == 1, f'Unfinished recovery source: {pid}')
    problem = sequence['problems'][0]
    grading.require(problem.get('problem_id') == pid and problem.get('state') == 'missing_proofs'
                    and type(problem.get('worker_returncode')) is int
                    and problem['worker_returncode'] in (0, 1), f'Interrupted or invalid worker: {pid}')
    original = problem['cross_lane_voter']
    grading.require(original.get('state') == 'incomplete'
                    and original.get('artifact_directory') == selection.get('artifact_directory'),
                    f'Selection recovery changed its source: {pid}')
    old_lanes = problem['lanes']
    grading.require(len(old_lanes) == 4 and {x['candidate_id'] for x in old_lanes} == set(grading.CANDIDATES),
                    f'Original portfolio is incomplete: {pid}')
    candidates = []
    for lane in final['lanes']:
        old = next(x for x in old_lanes if x['candidate_id'] == lane['candidate_id'])
        grading.require(old.get('proof_available') is True
                        and old.get('selected_stage') == lane['selected_stage']
                        and old.get('proof_sha256') == lane['proof_sha256']
                        and Path(old['proof_path']) == run / lane['producer']
                        and Path(old['completion_record']) == run / lane['completion_record'],
                        f'Recovery changed a lane final: {pid}/{lane["candidate_id"]}')
        candidates.append(dict(candidate_id=lane['candidate_id'], selected_stage=lane['selected_stage'],
                               proof_path=str(run / lane['proof']), proof_sha256=lane['proof_sha256']))
    # Only the verified read-only collector is used: prepare/run/report would
    # mutate the generation archive and must never be called by this adapter.
    path = Path(__file__).resolve().parents[1] / 'harnesses/proof_workshop/pipeline.py'
    spec = importlib.util.spec_from_file_location('grading_selection_reader', path)
    pipeline = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pipeline)
    voter = pipeline.voter_module(final['implementation_release'])
    directory = grading.inside(run / selection['artifact_directory'], run / 'cross_lane_voter' / pid)
    expected = dict(problem_id=pid, problem=claim, candidates=candidates,
                    runtime=runtime['parameters'], release_sha256=runtime['release_sha256'])
    cfg, manifest, tasks = voter.verify(directory, expected=expected)
    bound(directory / 'config.json', directory)
    for name, digest in cfg['pins'].items():
        bound(directory / name, directory, digest)
    fresh = voter.collect(directory, expected=expected)
    grading.require(fresh['state'] == 'completed' and fresh['summaries']['combined']['valid_calls'] == 24
                    and all(selection.get(k) == v for k, v in fresh.items())
                    and fresh['summaries']['combined']['winner'] == selection['selected_candidate'],
                    f'Recovered selection does not match bound responses: {pid}')
    old_votes = original['vote_table']
    grading.require(len(old_votes) == 24 and {v['case_id'] for v in old_votes} == {t['case_id'] for t in tasks}
                    and voter.summarize(manifest, old_votes)['summaries'] == original['summaries'],
                    f'Original vote accounting differs: {pid}')
    repaired = []
    for task, vote in zip(tasks, fresh['vote_table']):
        folder = directory / 'cases' / task['case_id']
        result = grading.read(bound(folder / 'result.json', directory))
        call = grading.read(bound(folder / 'audit/call_result.json', directory))
        evidence = voter.verify_audit_binding(directory, task, result, call)
        for filename, digest in evidence['source_hashes'].items():
            bound(Path(filename), directory, digest)
        old = next(v for v in old_votes if v['case_id'] == task['case_id'])
        grading.require(all(old.get(k) == task[k] for k in
                        ('original_case_id', 'problem_id', 'model_key', 'order', 'presentation_order')),
                        f'Original vote identity differs: {pid}/{task["case_id"]}')
        repair = vote.get('mechanical_recovery')
        if repair:
            grading.require(old.get('valid') is False and old.get('selected_candidate') is None
                            and old.get('error') == 'ValueError: Expected exactly one unambiguous Winner: A or B'
                            and repair['policy'] == 'explicit-winner-proof-prefix-v1'
                            and repair['model_calls'] == 0 and repair['new_mathematical_text'] is False,
                            f'Failure is not an explicit winner-prefix recovery: {pid}/{task["case_id"]}')
            repaired.append(dict(case_id=task['case_id'], **repair))
        else:
            grading.require(old == vote, f'Recovery changed an originally valid vote: {pid}/{task["case_id"]}')
    grading.require(repaired, f'No verified format recovery: {pid}')
    return dict(policy='verified-explicit-winner-prefix-selection-v1', original_returncode=1,
                original_execution_state=execution['state'], model_calls=0, cases=repaired,
                original_worker_returncode=problem['worker_returncode'], original_worker_error=problem.get('worker_error'),
                original_combined=original['summaries']['combined'], recovered_combined=fresh['summaries']['combined'])


def inspect_run(run_id, allow_recovered_selection=False):
    grading.identifier(run_id)
    sources = {}

    def bound(path, base=ROOT, expected=None):
        path = grading.checked(path, base, expected)
        sources[str(path.relative_to(ROOT))] = grading.digest(path.read_bytes())
        return path

    study = grading.read(bound(ROOT / STUDY))
    baseline_policy = study.get('winner_selection_policy', LEGACY_POLICY)
    grading.require(baseline_policy in POLICY_LABELS, 'Unknown baseline selection policy')
    baseline = {}
    for record in study['baselines']:
        document = grading.read(bound(ROOT / record['path'], ROOT, record['sha256']))
        for problem in document['problems']:
            baseline[problem['problem_id']] = problem
    scheduler = ROOT / '.workshop/single_gpu' / run_id
    plan = grading.read(bound(scheduler / 'plan.json'))
    status = grading.read(bound(scheduler / 'status.json'))
    jobs = plan['jobs']
    expected = {(p['benchmark'], p['problem_id']) for p in jobs}
    grading.require(plan.get('schema') == 'workshop-single-gpu-run-v1' and plan.get('run_id') == run_id
                    and plan.get('release') == study['release']
                    and plan.get('release_sha256') == study['release_sha256']
                    and plan.get('candidates_per_problem') == 4 and plan.get('problem_count') == len(jobs),
                    'Scheduler plan differs from the reproduction study')
    grading.require(jobs and len(expected) == len(jobs) and len({p for _, p in expected}) == len(jobs)
                    and all(b in grading.GROUPS for b, _ in expected), 'Invalid or duplicate problem selection')
    outcomes = status.get('jobs', [])
    codes = [j.get('returncode') for j in outcomes]
    terminal = (status.get('state') == 'completed' and all(type(c) is int and c == 0 for c in codes))
    if allow_recovered_selection and status.get('state') == 'completed_with_failures':
        terminal = any(c == 1 for c in codes) and all(type(c) is int and c in (0, 1) for c in codes)
    grading.require(terminal and len(outcomes) == len(jobs)
                    and {j['problem_id'] for j in status['jobs']} == {p for _, p in expected},
                    'Generation is incomplete or failed; inspect scheduler status and retain failures')
    results = []
    for job in plan['jobs']:
        benchmark, pid = job['benchmark'], job['problem_id']
        child_id = run_id + '_' + pid
        base = ROOT / 'benchmarks' / benchmark
        experiment = base / 'results' / child_id
        run = experiment / 'generation/run'
        grading.require(job['run_id'] == child_id and Path(job['output']) == experiment
                        and Path(job['final_results']) == run / 'final_results.json',
                        'Scheduler output identity differs; grade the original unmoved run')
        outcome = next(x for x in status['jobs'] if x['problem_id'] == pid)
        recovered = outcome['returncode'] == 1
        grading.require(outcome['final_results'] == job['final_results'], 'Outcome belongs to another run')
        catalog = grading.read(bound(base / 'catalog.json'))
        inputs = [x for x in catalog['generation_inputs']['files'] if x['problem_id'] == pid]
        grading.require(len(inputs) == 1 and inputs[0]['sha256'] == job['input_sha256'], 'Statement binding differs')
        statement = bound(base / inputs[0]['path'], base / 'problems', job['input_sha256'])
        payload = grading.read(statement)
        claim = str(payload.get('claim') or payload.get('problem') or payload.get('statement') or '').strip()
        grading.require(payload.get('problem_id') == pid and bool(claim), 'Invalid problem statement')
        identity = grading.read(bound(experiment / 'experiment.json', experiment))
        completion = grading.read(bound(experiment / 'generation/completion.json', experiment))
        runtime = grading.read(bound(run / 'harness_release.json', run))
        final = grading.read(bound(run / 'final_results.json', run))
        selection_policy = QWEN_POLICY if runtime.get('final_selector') else LEGACY_POLICY
        grading.require(final.get('winner_selection_policy', selection_policy) == selection_policy,
                        f'Selection policy differs from the saved run identity: {pid}')
        grading.require(identity.get('run_id') == child_id and identity.get('benchmark') == benchmark
                        and identity.get('state') == ('failed_or_interrupted' if recovered else 'completed')
                        and completion.get('worker_exited') is True
                        and completion.get('returncode') == outcome['returncode'], f'Unfinished experiment: {pid}')
        parameters = dict(study['generation_parameters'])
        for key in parameters:
            flag = '--' + key.replace('_', '-')
            if flag in job['command']:
                value = job['command'][job['command'].index(flag) + 1]
                parameters[key] = value if key == 'seed_namespace' else int(value)
        grading.require(runtime.get('release_sha256') == study['release_sha256']
                        and all(runtime['parameters'].get(k) == v for k, v in parameters.items()),
                        f'Release or generation seed/settings differ: {pid}')
        grading.require(final.get('implementation_release') == study['release']
                        and final.get('implementation_sha256') == study['release_sha256']
                        and final.get('state') in (('completed_with_failures',) if recovered else ('completed', 'completed_with_fallbacks'))
                        and final['execution'].get('state') == ('failed' if recovered else 'completed')
                        and final['execution'].get('returncode') == outcome['returncode'], f'Incomplete final export: {pid}')
        elapsed = completion.get('wall_seconds')
        grading.require(type(elapsed) in (int, float) and math.isfinite(elapsed) and elapsed >= 0,
                        f'Invalid generation wall time: {pid}')
        lanes = final['lanes']
        grading.require(len(lanes) == 4 and {(x['problem_id'], x['candidate_id']) for x in lanes}
                        == {(pid, cid) for cid in grading.CANDIDATES}, f'Missing or duplicate lanes: {pid}')
        rows = []
        for lane in lanes:
            stage = lane.get('selected_stage')
            grading.require(lane.get('proof_available') is True and stage in grading.STAGES
                            and lane.get('state') == ('completed' if stage == 'refinement_3' else
                                                     'failed' if recovered else 'completed_with_fallback'),
                            f'No eligible final proof: {pid}/{lane["candidate_id"]}')
            proof = bound(run / lane['proof'], run, lane['sha256'])
            producer = bound(run / lane['producer'], run)
            bound(run / lane['completion_record'], run)
            grading.require(proof.read_bytes() == producer.read_bytes() and bool(proof.read_text().strip())
                            and grading.text_digest(proof.read_text()) == lane['proof_sha256'], 'Final proof binding differs')
            rows.append(dict(problem_id=pid, candidate_id=lane['candidate_id'], selected_stage=stage,
                proof_path=str(proof.relative_to(ROOT)), proof_sha256=lane['proof_sha256'], proof_file_sha256=lane['sha256'],
                problem_path=str(statement.relative_to(ROOT)), problem_sha256=grading.text_digest(claim),
                fallback_used=stage != 'refinement_3', elapsed_seconds=elapsed, resumed=False))
        selections = final.get('problem_selections', [])
        grading.require(len(selections) == 1 and selections[0].get('problem_id') == pid
                        and selections[0].get('state') == 'completed', f'Incomplete selector: {pid}')
        selection = selections[0]
        winner = selection['selected_candidate']
        selected = [row for row in rows if row['candidate_id'] == winner]
        grading.require(len(selected) == 1, 'Selector winner is not an available lane')
        chosen = bound(run / selection['proof'], run, selection['sha256'])
        grading.require(grading.digest(chosen.read_bytes()) == selected[0]['proof_file_sha256'],
                        'Selected proof differs from its lane')
        recovery = verify_recovered_selection(run, pid, claim, runtime, final, selection, bound) if recovered else None
        old = baseline[pid]
        grading.require(len(old['lanes']) == 4 and all(len(x['scores']) == 2 for x in old['lanes'] if x.get('available', True)),
                        'Available baseline lanes lack two grades')
        results.append(dict(benchmark=benchmark, experiment=str(experiment.relative_to(ROOT)), run_id=child_id,
                            problem_id=pid, selected_candidate=winner, rows=rows, baseline=old,
                            original_returncode=outcome['returncode'], selection_recovery=recovery,
                            baseline_selection_policy=baseline_policy, selection_policy=selection_policy,
                            generation_parameters=parameters,
                            matches_baseline_generation_parameters=parameters == study['generation_parameters']))
    return dict(run_id=run_id, sample_seed=plan.get('sampling', {}).get('seed'), generation_seed=plan.get('generation_seed'),
                original_generation_state=status['state'], allow_recovered_selection=allow_recovered_selection,
                baseline_selection_policy=baseline_policy,
                jobs=results, source_hashes=sources)


def compare(job, result):
    indexed = [{r['candidate_id']: r for r in p['rows']} for p in result['passes']]
    grading.require(len(indexed) == 2, 'Expected two fresh grading passes')
    old = {r['candidate_id']: r for r in job['baseline']['lanes']}
    rows = []
    for row in job['rows']:
        cid = row['candidate_id']
        scores = [p[cid]['grade']['score'] for p in indexed]
        prior = old[cid]['scores'] if old[cid].get('available', True) else None
        rows.append(dict(candidate_id=cid, previous_scores=prior, scores=scores,
            previous_mean=sum(prior) / 2 if prior else None, mean=sum(scores) / 2,
            delta=(sum(scores) - sum(prior)) / 2 if prior else None,
            same_proof_text=row['proof_sha256'] == old[cid].get('proof_sha256') if prior else None,
            previous_stage=old[cid].get('stage', old[cid].get('selected_stage')),
            selected_stage=row['selected_stage'], fallback_used=row['fallback_used']))
    before = {r['candidate_id']: r['previous_mean'] for r in rows if r['previous_mean'] is not None}
    after = {r['candidate_id']: r['mean'] for r in rows}
    def metrics(scores, winner):
        return dict(average=sum(scores.values()) / len(scores), oracle_at_4=max(scores.values()), selector_at_1=scores[winner])
    previous = metrics(before, job['baseline']['selected_candidate'])
    current = metrics(after, job['selected_candidate'])
    baseline_policy = job.get('baseline_selection_policy', LEGACY_POLICY)
    selection_policy = job.get('selection_policy', LEGACY_POLICY)
    return dict(problem_id=job['problem_id'], benchmark=job['benchmark'], lanes=rows,
        previous_selected_candidate=job['baseline']['selected_candidate'], selected_candidate=job['selected_candidate'],
        previous=previous, current=current, delta={k: current[k] - previous[k] for k in current},
        baseline_selection_policy=baseline_policy, selection_policy=selection_policy,
        matches_baseline_selection_policy=baseline_policy == selection_policy,
        previous_available_lanes=len(before), available_lanes=len(after),
        generation_parameters=job['generation_parameters'],
        original_returncode=job['original_returncode'], selection_recovery=job['selection_recovery'],
        matches_baseline_generation_parameters=job['matches_baseline_generation_parameters'],
        elapsed_seconds=job['rows'][0]['elapsed_seconds'])


def report(summary):
    lines = ['# Single-GPU grading and baseline comparison', '',
        f"Run: `{summary['run_id']}`. Grading: `{summary['grading_id']}`. State: **{summary['state']}**.", '',
        'Two fresh grades per final proof; existing baseline grades are reused unchanged.',
        f"Baseline selector: **{POLICY_LABELS[summary.get('baseline_selection_policy', LEGACY_POLICY)]}**.",
        'Reported scores are per-proof means, then per-problem lane averages / oracle / saved selector winner.',
        'Selection policies are shown for both sides. A difference between policies can change Selector@1 '
        'without any change in proofs or grades; it is not a reproduction performance gain.',
        'Separate automated grading is not mathematical verification. A sampled run is a diagnostic, not a general performance guarantee.',
        'Missing baseline lanes are excluded from its lane average, not scored as zero. Unequal lane counts are shown.',
        'Matching seeds and inference budgets do not make GPU scheduling, hardware or evaluator sampling identical.',
        'Generation time is elapsed wall time including scheduler waits; it is not active GPU compute time.', '',
        f"Original generation state: **{summary['original_generation_state']}**.",
        'Grading completion does not change the original generation outcome.', '']
    for recovery in summary['selection_recoveries']:
        lines += [f"- {recovery['problem_id']}: original exit 1 retained; saved selection recovered offline "
                  f"by verifying {len(recovery['cases'])} explicit Winner: Proof A/B response(s). "
                  'No additional model calls. This is not a clean end-to-end generation pass.']
    lines += ['',
        '| Problem | Average old → new | Oracle old → new | Selector old → new | Selector policy old → new | Lanes old → new | Same seed/budget | Time (min) |',
        '|---|---:|---:|---:|---|---:|---|---:|']
    for problem in summary['comparisons']:
        cells = [f"{problem['previous'][k]:g} → {problem['current'][k]:g}" for k in ('average', 'oracle_at_4', 'selector_at_1')]
        lines.append(f"| {problem['problem_id']} | " + ' | '.join(cells)
                     + f" | {POLICY_LABELS[problem.get('baseline_selection_policy', LEGACY_POLICY)]} → "
                     + POLICY_LABELS[problem.get('selection_policy', LEGACY_POLICY)]
                     + f" | {problem['previous_available_lanes']} → {problem['available_lanes']} | "
                     + f"{problem['matches_baseline_generation_parameters']} | {problem['elapsed_seconds']/60:.2f} |")
    lines += ['', '| Problem / lane | Old grades | New grades | Mean delta | Final stage | Same proof text |',
              '|---|---|---|---:|---|---|']
    for problem in summary['comparisons']:
        for lane in problem['lanes']:
            delta = 'unavailable' if lane['delta'] is None else f"{lane['delta']:+g}"
            lines.append(f"| {problem['problem_id']} / {lane['candidate_id']} | {lane['previous_scores']} | {lane['scores']} | "
                         f"{delta} | {lane['selected_stage']} | {lane['same_proof_text']} |")
    lines += ['', 'All job states and errors are retained in `summary.json`. An incomplete run is not reported as reproduced.', '']
    return '\n'.join(lines)


def execute(suite, refs, grading_id, workers, destination):
    destination.mkdir(parents=True, exist_ok=False)
    grading.write(destination / 'manifest.json', dict(suite, grading_id=grading_id, model=grading.MODEL,
                  reasoning_effort=grading.EFFORT, passes=2))
    summary = dict(run_id=suite['run_id'], grading_id=grading_id, state='running', jobs=[], comparisons=[],
                   baseline_selection_policy=suite.get('baseline_selection_policy', LEGACY_POLICY),
                   original_generation_state=suite['original_generation_state'],
                   selection_recoveries=[dict(problem_id=j['problem_id'], **j['selection_recovery'])
                                         for j in suite['jobs'] if j['selection_recovery']])
    def save():
        grading.write(destination / 'summary.json', summary)
        (destination / 'REPORT.md').write_text(report(summary))
    save()
    try:
        for job in suite['jobs']:
            grading.verify_sources(suite)
            child = dict(suite, run_id=job['run_id'], jobs=[job])
            folder = destination / job['problem_id']
            code = grading.execute(child, refs, grading_id, workers, 2, folder)
            saved = grading.read(folder / 'summary.json')
            summary['jobs'].append(dict(problem_id=job['problem_id'], returncode=code, state=saved['state']))
            if code == 0:
                summary['comparisons'].append(compare(job, saved['jobs'][0]))
            save()
            if saved['state'] == 'interrupted':
                summary['state'] = 'interrupted'
                return 1
        summary['state'] = 'completed' if len(summary['comparisons']) == len(suite['jobs']) else 'failed'
        return 0 if summary['state'] == 'completed' else 1
    except BaseException as error:
        summary.update(state='failed', error=f'{type(error).__name__}: {error}')
        raise
    finally:
        save()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--grading-id', default=None)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--dataset', type=Path, default=ROOT / '.workshop/external-references/proofbench_v2.csv')
    parser.add_argument('--download-references', action='store_true')
    parser.add_argument('--allow-recovered-selection', action='store_true',
                        help='Accept a verified offline Winner: Proof A/B selection recovery; retain original failures')
    parser.add_argument('--dry-run', action='store_true', help='Validate completed proofs and references without grading calls')
    args = parser.parse_args(argv)
    try:
        grading.require(args.workers > 0, 'workers must be positive')
        grading_id = grading.identifier(args.grading_id or datetime.now(timezone.utc).strftime('grading_%Y%m%dT%H%M%S%fZ'))
        suite = inspect_run(args.run_id, args.allow_recovered_selection)
        destination = grading.inside(ROOT / 'benchmarks/reports' / (args.run_id + '_reproduction') / grading_id, ROOT)
        paths = [destination]
        for job in suite['jobs']:
            experiment = ROOT / job['experiment']
            paths += [experiment / part / grading_id for part in ('grading/work', 'grades', 'proofs')]
            paths.append(experiment / 'reports' / (grading_id + '.md'))
            manifest = experiment / 'manifest.json'
            if manifest.exists():
                saved = grading.read(grading.checked(manifest, ROOT))
                grading.require(saved.get('run_id') == job['run_id'] and saved.get('benchmark') == job['benchmark']
                                and grading_id not in saved.get('grading_runs', {}), 'Existing grading manifest conflicts')
        for path in paths:
            grading.inside(path, ROOT)
            grading.require(not path.exists(), f'Grading output exists; retain it and choose a fresh grading ID: {path}')
        refs = grading.references(args.dataset.expanduser().absolute(), args.download_references)
        grading.bind_references(suite, refs)
        grading.verify_sources(suite)
        proofs = sum(len(j['rows']) for j in suite['jobs'])
        print(f"Run: {args.run_id}\nProofs: {proofs}; fresh judgments: {2 * proofs}\nReport: {destination / 'REPORT.md'}", flush=True)
        for job in suite['jobs']:
            if job['selection_recovery']:
                print(f"{job['problem_id']}: verified offline selection recovery; original generation exit 1 retained.", flush=True)
        if args.dry_run:
            print('Preflight passed. No grading calls or grading result directories created.')
            return 0
        grading.require(shutil.which('codex') is not None, 'Authenticated Codex CLI is required for grading')
        return execute(suite, refs, grading_id, args.workers, destination)
    except (ValueError, OSError, KeyError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    raise SystemExit(main())
