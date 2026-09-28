#!/usr/bin/env python3
"""Detached saved-lane continuation, selection, isolated grading, and comparison."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import traceback
from recover import read, write, sha, textsha, load

CONTROL = Path(__file__).resolve().parent
CFG = read(CONTROL / 'config.json')
OUT = Path(CFG['output'])
STATE = {}


def now(): return datetime.now(timezone.utc).isoformat()
def event(stage, state, **details):
    STATE.update(stage=stage, state=state, updated_at=now(), **details)
    write(OUT / 'status.json', STATE)
    with (OUT / 'events.jsonl').open('a') as stream:
        stream.write(json.dumps(dict(at=now(), stage=stage, state=state, **details)) + '\n')
    print(now(), stage, state, json.dumps(details), flush=True)


def verify_pins():
    for name, digest in read(CONTROL / 'pins.json').items():
        assert sha(name) == digest, 'Pinned code changed: ' + name


def solver(stage):
    marker = OUT / 'control/stages' / (stage + '.json')
    if marker.exists() and read(marker)['state'] == 'completed': return
    verify_pins(); started = time.monotonic(); event(stage, 'running')
    command = [CFG['solver_python'], '-u', '-B', str(CONTROL / 'recover.py'), '--config', str(CONTROL / 'config.json'), stage]
    proc = subprocess.Popen(command, cwd=CFG['repo'], stdin=subprocess.DEVNULL)
    STATE['child_pid'] = proc.pid; write(OUT / 'status.json', STATE)
    code = proc.wait()
    result = dict(state='completed' if code == 0 else 'failed', exit_code=code,
                  elapsed_seconds=time.monotonic() - started, finished_at=now())
    write(marker, result)
    if code: raise RuntimeError(f'{stage} exited {code}; see controller.log')
    event(stage, 'running', last_stage=result, child_pid=None)


def scoring_engine():
    # This is the same already validated isolated v2 adapter used by the suite.
    helper = load('p4_recovery_scoring_helper', Path(CFG['suite']) / 'control/controller.py')
    return helper, helper.scorer()


def grade(preflight=False):
    c, engine = scoring_engine()
    source = Path(CFG['source']); original = read(source / 'reports/REPORT.json')
    pcopy = OUT / 'grading/inputs/problem.json'; rcopy = OUT / 'grading/inputs/reference.txt'
    c.exact(pcopy, (source / 'grading/inputs/problem.json').read_bytes())
    c.exact(rcopy, (source / 'grading/inputs/reference.txt').read_bytes())
    assert c.textsha(read(pcopy)['claim']) == original['lanes'][0]['grades'][0]['problem_sha256']
    assert c.textsha(rcopy.read_text()) == original['lanes'][0]['grades'][0]['reference_sha256']
    if preflight:
        # Validate a generic task without an inference call or access by the solver.
        row = original['lanes'][0]
        manifest = OUT / 'grading/preflight_task.json'
        write(manifest, {'schema': 'gold-informed-generic-proof-task-manifest-v1', 'tasks': [{
            'problem_number': 4, 'problem_id': 'imo2026_p4', 'candidate_id': 'proof_' + row['proof_sha256'][:32],
            'problem_path': str(pcopy), 'reference_path': str(rcopy), 'proof_path': row['published_proof'],
            'expected_hashes': {k: row['grades'][0][k] for k in ('problem_sha256', 'reference_sha256', 'proof_sha256')}}]})
        task, = engine.generic_proof_task_manifests([manifest])
        prompt = engine.grading_prompt(problem=task['problem'], reference=task['reference'], proof=task['proof'], grading_policy=engine.STRICT_POLICY)
        assert 'grading_key.json' not in prompt and row['candidate_id'] not in prompt
        result = subprocess.run(['codex', 'login', 'status'], stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=30)
        assert result.returncode == 0, 'Grader authentication unavailable'
        write(OUT / 'grading/preflight.json', {'state': 'passed', 'model_calls': 0,
            'grader': c.MODEL, 'policy_sha256': c.POLICY, 'reasoning_effort': 'xhigh',
            'reference_hash_verified': True, 'generic_adapter_verified': True, 'auth_verified': True, 'workers': 12})
        return
    portfolio = read(OUT / 'generation/portfolio.json')
    old = {r['proof_sha256']: r for r in original['lanes']}
    mapping = []; tasks = {}
    for lane in portfolio:
        proof = Path(lane['proof_path']); assert textsha(proof.read_text()) == lane['proof_sha256']
        sid = 'proof_' + lane['proof_sha256'][:32]
        if lane['proof_sha256'] in old:
            prior = old[lane['proof_sha256']]
            for i, result in enumerate(prior['grades'], 1):
                assert result['model'] == c.MODEL and result['policy_sha256'] == c.POLICY and result['reasoning_effort'] == 'xhigh'
                evidence = Path(result['evidence']); assert sha(evidence / 'evidence_hashes.json') == result['evidence_sha256']
                for name, digest in read(evidence / 'evidence_hashes.json').items(): assert sha(evidence / name) == digest
                c.freeze(OUT / 'grades' / f'{sid}_pass{i}.json', result)
            provenance = {'grading': 'reused', 'source_run': original['run_id']}
        else:
            blinded = OUT / 'grading/inputs/proofs' / (sid + '.md')
            c.exact(blinded, (proof.read_text().strip() + '\n').encode())
            tasks[sid] = {'problem_number': 4, 'problem_id': 'imo2026_p4', 'candidate_id': sid,
                'problem_path': str(pcopy), 'reference_path': str(rcopy), 'proof_path': str(blinded),
                'expected_hashes': {'problem_sha256': textsha(read(pcopy)['claim']),
                    'reference_sha256': textsha(rcopy.read_text()), 'proof_sha256': lane['proof_sha256']}}
            provenance = {'grading': 'new_two_independent_passes'}
        mapping.append({**lane, 'submission_id': sid, **provenance})
    manifest = OUT / 'grading/input_manifest.json'
    c.freeze(manifest, {'schema': 'gold-informed-generic-proof-task-manifest-v1', 'tasks': list(tasks.values())})
    c.freeze(OUT / 'grading/grading_key.json', {'lanes': mapping, 'source_run': original['run_id']})
    pending = engine.generic_proof_task_manifests([manifest]) if tasks else []
    problem = {'problem_id': 'imo2026_p4', 'run_id': OUT.name, 'output': str(OUT)}
    with ThreadPoolExecutor(max_workers=12) as pool:
        futures = [pool.submit(c.grade_one, engine, problem, task, repeat) for task in pending for repeat in (1, 2)]
        for future in futures: future.result()
    write(OUT / 'grading/completed.json', {'state': 'completed', 'new_submissions': len(tasks),
        'reused_lanes': sum(r['grading'] == 'reused' for r in mapping), 'passes': 2, 'workers': 12})


def report():
    original = read(Path(CFG['source']) / 'reports/REPORT.json')
    key = read(OUT / 'grading/grading_key.json'); selection = read(OUT / 'generation/selection.json')
    rows = []
    for lane in key['lanes']:
        grades = [read(OUT / 'grades' / f"{lane['submission_id']}_pass{i}.json") for i in (1, 2)]
        before = next(r for r in original['lanes'] if r['candidate_id'] == lane['candidate_id'])
        scores = [g['score'] for g in grades]
        rows.append({**lane, 'scores': scores, 'mean': sum(scores) / 2, 'grades': grades,
            'before_scores': before['scores'], 'before_stage': before['selected_stage'],
            'mean_delta': sum(scores) / 2 - before['mean']})
    winner = selection['summaries']['combined']['winner']; selected = next(r for r in rows if r['candidate_id'] == winner)
    result = {'schema': 'imo2026-b112-p4-saved-lane-recovery-v1', 'quality': 'graded',
        'run_id': OUT.name, 'original_run': original['run_id'], 'problem_id': 'imo2026_p4',
        'release': '1.12.0', 'release_sha256': CFG['release_sha256'],
        'mechanical_adapter': 'acceptance-none-routine-completion-annotation-v1',
        'lanes': rows, 'selection': selection, 'selected_candidate': winner, 'selected_scores': selected['scores'],
        'portfolio_mean': sum(r['mean'] for r in rows) / 4, 'oracle': max(r['mean'] for r in rows),
        'selector_mean': selected['mean'], 'before': {k: original[k] for k in ('portfolio_mean', 'selected_candidate', 'selected_scores')},
        'stage_times': {f.stem: read(f) for f in (CONTROL / 'stages').glob('*.json')},
        'original_artifacts_modified': False, 'fresh_raw_generation': False}
    suite = read(Path(CFG['suite']) / 'control/config.json')
    before_reports = [read(Path(p['output']) / 'reports/REPORT.json') for p in [suite['p1_problem'], *suite['problems']]]
    def metrics(replace):
        portfolios = [rows if replace and r['problem_id'] == 'imo2026_p4' else r['lanes'] for r in before_reports]
        selected_scores = [selected['mean'] if replace and r['problem_id'] == 'imo2026_p4' else r['selected_mean'] for r in before_reports]
        return {'average_mean_of_two_grades': sum(x['mean'] for p in portfolios for x in p) / 24,
                'oracle_at_4_sum_mean_of_two_grades': sum(max(x['mean'] for x in p) for p in portfolios),
                'selector_at_1_sum_mean_of_two_grades': sum(selected_scores)}
    result['six_problem_comparison'] = {'original_fresh_uniform_suite': metrics(False), 'with_explicit_p4_recovery': metrics(True),
        'aggregation': 'mean of the two independent grades per proof; recovery is separately labeled'}
    write(OUT / 'reports/REPORT.json', result)
    lines = ['# P4 saved-lane recovery', '', 'Original frozen B 1.12.0 results are preserved. Only t10_r02 resumes at R2; '
        'the other three lane proofs and matching grades are reused. This is a separately labeled recovery, not a fresh generation.', '',
        '| Lane | Before stage | Before grades | After stage | After grades | Mean change |', '|---|---|---|---|---|---:|']
    for r in rows: lines.append(f"| {r['candidate_id']} | {r['before_stage']} | {r['before_scores']} | {r['selected_stage']} | {r['scores']} | {r['mean_delta']:+g} |")
    lines += ['', f"Cross-lane winner: **{winner}**, grades **{selected['scores']}**.",
        f"Order disagreement: {selection['summaries']['combined']['disagreeing_pairs']}/12.",
        '', '## Six-problem aggregate (mean of two grades)', '', '| Portfolio | Average /7 | Oracle@4 /42 | Selector@1 /42 |', '|---|---:|---:|---:|']
    for label in ('original_fresh_uniform_suite', 'with_explicit_p4_recovery'):
        v = result['six_problem_comparison'][label]
        lines.append(f"| {label} | {v['average_mean_of_two_grades']:.3f} | {v['oracle_at_4_sum_mean_of_two_grades']:g} | {v['selector_at_1_sum_mean_of_two_grades']:g} |")
    lines += ['', 'See REPORT.json for all votes, fallback records, grade provenance, and stage times.', '']
    (OUT / 'reports/REPORT.md').write_text('\n'.join(lines))


def main():
    global STATE
    lock = (CONTROL / 'controller.lock').open('a'); fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    if (OUT / 'status.json').exists() and read(OUT / 'status.json').get('state') == 'completed': return
    verify_pins()
    STATE = dict(run_id=OUT.name, pid=os.getpid(), process_group=os.getpgrp(), started_at=now(),
        waiting_for=Path(CFG['suite']).name, exit_code=None, stages=['r2', 'r3', 'audit', 'vote', 'grading', 'report'])
    event('waiting_for_p6_and_suite_grades', 'waiting')
    while True:
        suite = read(Path(CFG['suite']) / 'status.json')
        if suite['state'] == 'completed': break
        if suite['state'] in ('failed', 'stopped', 'cancelled', 'interrupted'):
            raise RuntimeError('Predecessor suite did not finish: ' + suite['state'])
        STATE.update(predecessor_problem=suite.get('current_problem'), predecessor_updated_at=suite.get('updated_at'))
        write(OUT / 'status.json', STATE); time.sleep(30)
    assert read(Path(CFG['suite']) / 'reports/ALL_SIX.json')['quality'] == 'graded'
    for stage in ('servers', 'r2', 'r3', 'audit', 'vote'): solver(stage)
    event('grading', 'running'); began = time.monotonic(); grade()
    write(CONTROL / 'stages/grading.json', {'state': 'completed', 'elapsed_seconds': time.monotonic() - began, 'exit_code': 0})
    event('report', 'running'); report(); verify_pins()
    event('publication', 'running')
    subprocess.run([sys.executable, '-u', '-B', str(CONTROL / 'publish.py')],
                   cwd=CFG['repo'], stdin=subprocess.DEVNULL, check=True)
    event('complete', 'completed', completed_at=now(), exit_code=0, report=str(OUT / 'reports/REPORT.md'))


if __name__ == '__main__':
    if '--grade-preflight' in sys.argv:
        grade(preflight=True)
    else:
        signal.signal(signal.SIGHUP, signal.SIG_IGN)
        def stop(signum, frame): raise KeyboardInterrupt('Controller stopped')
        signal.signal(signal.SIGTERM, stop)
        try: main()
        except BaseException as exc:
            traceback.print_exc(); event(STATE.get('stage', 'startup'), 'failed', error=f'{type(exc).__name__}: {exc}', exit_code=1); sys.exit(1)
