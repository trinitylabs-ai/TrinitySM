#!/usr/bin/env python3
"""Resume a study retaining only original grading repetitions 1 and 2."""
import argparse
from collections import Counter
import fcntl
import hashlib
import json
import os
from pathlib import Path
import random
import signal
import subprocess
import sys
import time

import run_v2_consistency as original
from score_v2_consistency_worker import prepare_study_runner

ROOT = original.ROOT
PLAN = 'two_grade_plan.json'


def load_plan(directory):
    study = original.read(directory/'manifest.json')
    plan = original.read(directory/PLAN)
    assert original.digest(directory/'manifest.json') == plan['original_manifest_sha256']
    assert plan['repeats'] == 2 and plan['selected_repetitions'] == [1, 2]
    assert plan['planned_grades'] == study['unique_proofs'] * 2
    study.update(repeats=2, planned_grades=plan['planned_grades'])
    return study


def collect(study):
    found = {}
    for unit in study['units']:
        for repeat in [1, 2]:
            path = original.grade_path(study, unit, repeat)
            if path.exists():
                value = original.read(path)
                original.check_grade(study, unit, repeat, value)
                found[unit['unit_id'], repeat] = value
    return found


def retained_bindings(bindings):
    """Never restore discarded grades from older mixed-repetition batches."""
    return [item for item in bindings if item['repeat'] in [1, 2]]


def consistency(vectors):
    if not vectors:
        return dict(proofs=0)
    assert all(len(v) == 2 and all(type(x) is int and 0 <= x <= 7 for x in v) for v in vectors)
    ranges = [abs(v[0] - v[1]) for v in vectors]
    n = len(vectors)
    agreement = sum(x == 0 for x in ranges) / n
    return dict(proofs=n, exact_agreement=agreement, pairwise_agreement=agreement,
                within_one_point=sum(x <= 1 for x in ranges)/n, mean_range=sum(ranges)/n,
                mean_population_sd=sum(ranges)/(2*n), range_counts=dict(sorted(Counter(ranges).items())),
                crosses_six_threshold=sum(min(v)<6<=max(v) for v in vectors),
                crosses_three_four_boundary=sum(min(v)<=3<max(v) for v in vectors))


def publish(study, directory, found, state=None, active=None, attempts=None, error=None):
    rows, complete = [], []
    for unit in study['units']:
        scores = [found.get((unit['unit_id'], i), {}).get('grade', {}).get('score') for i in [1, 2]]
        if all(x is not None for x in scores):
            complete.append(scores)
        rows.append(dict(unit_id=unit['unit_id'], problem_id=unit['problem_id'], scores=scores,
                         grade_files=[str(original.grade_path(study, unit, i).relative_to(ROOT))
                                      if scores[i-1] is not None else None for i in [1, 2]]))
    result = dict(schema='workshop-v2-pair-results-v1', updated_at=original.now(), repeats=2,
                  state=state or ('completed' if len(found)==study['planned_grades'] else 'running'),
                  completed_grades=len(found), planned_grades=study['planned_grades'],
                  completed_pairs=len(complete), completed_proofs=len(complete),
                  model=study['model'], reasoning_effort=study['reasoning_effort'],
                  policy_sha256=study['policy_sha256'], rows=rows, overall=consistency(complete),
                  metadata_disagreements=sum(not g['grade']['contract_consistent'] for g in found.values()),
                  retries_within_accepted_calls=sum(g.get('response_selection', {}).get('total_attempts', 1)-1 for g in found.values()),
                  active_batch=active, task_attempts=attempts or {}, protocol_amendment=PLAN)
    if error:
        result['pause_reason'] = error
    original.write(directory/'results.json', result)
    c = result['overall']
    lines = ['# Two independent strict-v2 grades per proof', '',
             f"Status: **{result['state']}**; {len(found)}/{study['planned_grades']} grades; "
             f"{len(complete)}/{study['unique_proofs']} complete pairs.", '',
             f"Evaluator: `{study['model']}` / `{study['reasoning_effort']}`. Policy SHA-256: `{study['policy_sha256']}`.", '',
             'The user reduced the repetition target from four to two. Original repetitions 1 and 2 are used, '
             'without selection by score. Repetitions 3 and 4 and their raw outputs were deleted at the user\'s request. '
             'The proof corpus, rubric, model, prompts and isolation requirements are unchanged.', '',
             'Incomplete pairs are excluded from consistency statistics. Category matrices are generated only '
             'when every proof has both grades. For each pass, Average and Oracle@4 are calculated first; '
             'mean, lowest and highest then summarize the two category totals.', '',
             '[Protocol amendment](two_grade_plan.json) · [Retention record](two_grade_retention.json)', '']
    if error:
        lines += [f'Queue pause: {error}', '']
    if c['proofs']:
        lines += ['| Complete proofs | Agreement | Within one point | Mean range | Mean SD |',
                  '|---:|---:|---:|---:|---:|',
                  f"| {c['proofs']} | {100*c['exact_agreement']:.2f}% | {100*c['within_one_point']:.2f}% | "
                  f"{c['mean_range']:.3f} | {c['mean_population_sd']:.3f} |", '']
    lines += [f"Score/metadata disagreements retained: {result['metadata_disagreements']}.", '',
              '## Underlying grades', '', '| Problem | Proof identity | Grade 1 | Grade 2 |', '|---|---|---:|---:|']
    for row in rows:
        cells = ['—' if x is None else f'[{x}]({os.path.relpath(ROOT/p, directory)})'
                 for x, p in zip(row['scores'], row['grade_files'])]
        lines.append(f"| {row['problem_id']} | `{row['unit_id'][:16]}` | {' | '.join(cells)} |")
    (directory/'REPORT.md').write_text('\n'.join(lines)+'\n')
    return result


def usage_limit_error(output):
    for path in output.glob('p*/*/codex.jsonl'):
        for line in path.read_text().splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if event.get('type') not in ['error', 'turn.failed']:
                continue
            message = event.get('message') or event.get('error', {}).get('message', '')
            if "hit your usage limit" in message.lower():
                return message
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--study', type=Path, required=True)
    parser.add_argument('--execute-models', action='store_true')
    parser.add_argument('--workers', type=int, default=8)
    parser.add_argument('--chunk-size', type=int, default=32)
    parser.add_argument('--retry-rounds', type=int, default=3)
    args = parser.parse_args()
    directory = args.study.resolve()
    study = load_plan(directory)
    assert study['policy_sha256'] == original.POLICY_SHA256
    assert args.workers > 0 and args.chunk_size > 0 and args.retry_rounds > 0
    # The original evaluator/policy hashes remain pinned across the operational amendment.
    old_config = original.read(directory/'execution_config.json')
    for name, expected in old_config['source_hashes'].items():
        assert original.digest(ROOT/name) == expected, f'Frozen evaluator changed: {name}'
    runner = prepare_study_runner()
    for u in study['units']:
        for field in ['proof', 'reference']:
            assert hashlib.sha256((ROOT/u[field]).read_text().strip().encode()).hexdigest() == u[field+'_sha256']
        problem = original.read(ROOT/u['problem'])
        statement = (problem.get('claim') or problem.get('problem') or problem.get('statement')).strip()
        assert hashlib.sha256(statement.encode()).hexdigest() == u['problem_sha256']
    work = directory/'work'
    with (work/'coordinator.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        attempt_path = work/'pair_attempts.json'
        attempts = original.read(attempt_path) if attempt_path.exists() else {}
        for benchmark in sorted({u['benchmark'] for u in study['units']}):
            private = ROOT/f"benchmarks/{benchmark}/results/{study['run_id']}/grading/work"
            for binding in sorted(private.glob('*.bindings.json')):
                output = private/binding.name.removesuffix('.bindings.json')
                original.export_batch(study, retained_bindings(original.read(binding)), output, runner)
        found = collect(study)
        publish(study, directory, found, attempts=attempts)
        if not args.execute_models:
            return 0
        files = list(old_config['source_hashes']) + ['scripts/run_v2_pairs.py']
        hashes = {f: original.digest(ROOT/f) for f in files}
        config = dict(original_execution_config_sha256=original.digest(directory/'execution_config.json'),
                      protocol_amendment_sha256=original.digest(directory/PLAN), source_hashes=hashes,
                      workers=args.workers, chunk_size=args.chunk_size, repeats=2,
                      model=study['model'], reasoning_effort=study['reasoning_effort'],
                      policy_sha256=study['policy_sha256'], first_resume_batch_size=1, stop_on_usage_limit=True)
        config_path = directory/'execution_config_pairs.json'
        if config_path.exists():
            assert original.read(config_path) == config, 'Pair execution configuration changed'
        else:
            original.write(config_path, config)
        launcher = Path.home()/'.codex/skills/strict-gold-informed-olympiad-scorer/scripts/score.py'
        if not launcher.is_file():
            launcher = original.ARCHIVE/'score.py'
        assert original.digest(launcher) == '7a4cfb1c678717d045889eb58fd0714a9932c8a2f29902ed210a363a15d8a12a'
        units = list(study['units'])
        random.Random(20260918).shuffle(units)
        first_batch = True
        while len(found) < study['planned_grades']:
            assert hashes == {f: original.digest(ROOT/f) for f in files}, 'Frozen evaluator code changed'
            pending = [(u, i) for u in units for i in [1, 2] if (u['unit_id'], i) not in found
                       and attempts.get(u['unit_id']+f':{i}', 0) < args.retry_rounds]
            if not pending:
                publish(study, directory, found, state='incomplete_after_retries', attempts=attempts)
                return 2
            benchmark = pending[0][0]['benchmark']
            chosen = [(u, i) for u, i in pending if u['benchmark']==benchmark][:(1 if first_batch else args.chunk_size)]
            first_batch = False
            private = original.base_for(study, chosen[0][0])/'grading/work'
            number = len(list(private.glob('pair_batch_*.tasks.json'))) + 1
            name = f'pair_batch_{number:05d}'
            output = private/name
            tasks, bindings = [], []
            for u, i in chosen:
                cid = 'u'+u['unit_id']+f'_g{i}'
                bindings.append(dict(unit_id=u['unit_id'], repeat=i, candidate_id=cid))
                tasks.append(dict(problem_number=u['problem_number'], problem_id=u['problem_id'], candidate_id=cid,
                                  **{k+'_path': str(ROOT/u[k]) for k in ['problem', 'reference', 'proof']},
                                  expected_hashes={k: u[k] for k in ['problem_sha256', 'reference_sha256', 'proof_sha256']}))
                key = u['unit_id']+f':{i}'
                attempts[key] = attempts.get(key, 0) + 1
            manifest = private/(name+'.tasks.json')
            original.write(manifest, dict(schema='gold-informed-generic-proof-task-manifest-v1', tasks=tasks))
            original.write(private/(name+'.bindings.json'), bindings)
            original.write(attempt_path, attempts)
            wrapper = private/'launcher/scripts'
            assert (wrapper/'run_gold_informed_calibrated_codex_scores.py').is_file()
            command = [sys.executable, '-B', str(launcher), '--generic-task-manifest', str(manifest),
                       '--output-dir', str(output), '--workers', str(args.workers), '--reasoning-effort', study['reasoning_effort']]
            quota_error = None
            with (private/(name+'.log')).open('w') as log:
                child = subprocess.Popen(command, cwd=wrapper.parent, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                try:
                    while child.poll() is None:
                        original.export_batch(study, bindings, output, runner)
                        found = collect(study)
                        quota_error = usage_limit_error(output)
                        if quota_error:
                            os.killpg(child.pid, signal.SIGTERM)
                            child.wait()
                            break
                        publish(study, directory, found, active=benchmark+'/'+name, attempts=attempts)
                        print(json.dumps(dict(updated_at=original.now(), completed=len(found), total=study['planned_grades'],
                                              active=benchmark+'/'+name)), flush=True)
                        time.sleep(15)
                except BaseException:
                    if child.poll() is None:
                        os.killpg(child.pid, signal.SIGTERM)
                    child.wait()
                    raise
            original.export_batch(study, bindings, output, runner)
            found = collect(study)
            quota_error = quota_error or usage_limit_error(output)
            if quota_error:
                publish(study, directory, found, state='blocked_usage_limit', attempts=attempts, error=quota_error)
                print('Paused on evaluator usage limit; completed grades preserved.', flush=True)
                return 3
            publish(study, directory, found, attempts=attempts)
        print('Completed two independent grades for every proof.', flush=True)
        return 0


if __name__ == '__main__':
    raise SystemExit(main())
