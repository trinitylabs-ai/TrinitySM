#!/usr/bin/env python3
"""Verify the published six-problem extended reasoning comparison without models or references."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / 'benchmarks/imo2026/results/refinement_bf_B6_selection_first_20260920_1426'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha(text):
    return hashlib.sha256(text.strip().encode()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def same(value, expected, label):
    require(math.isclose(value, expected, rel_tol=0, abs_tol=1e-12), label)


def verify(root):
    root = root.resolve()
    manifest = read(root / 'manifest.json')
    def artifact(name):
        path = root / name
        require(not Path(name).is_absolute() and path.resolve().is_relative_to(root), 'Artifact escapes archive')
        require(path.is_file() and not path.is_symlink(), f'Missing artifact: {name}')
        return path
    for name, record in manifest['files'].items():
        require(sha(artifact(name)) == record['sha256'], f'File hash mismatch: {name}')
    actual = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()} - {'manifest.json'}
    require(actual == set(manifest['files']), 'Manifest does not cover the exact archive')
    comparison = read(artifact('comparison.json'))
    require(comparison['state'] == 'completed', 'Comparison incomplete')
    require(comparison['run_id'] == manifest['run_id'], 'Run identity mismatch')
    require(not comparison['selection_results_included'] and not comparison['post_selection_recovery_included'],
            'This snapshot must remain the fixed pre-recovery portfolio comparison')
    policy = text_sha(artifact('grading/strict_olympiad_policy_v2.txt').read_text())
    require(policy == comparison['policy_sha256'], 'Rubric mismatch')
    references = {r['problem_id']: r['reference_sha256']
                  for r in read(artifact('grading/reference_sources.json'))['references']}
    rows = comparison['lanes']
    candidates = ['t10_r01', 't10_r02', 't07_r01', 't07_r02']
    expected_keys = {(f'imo2026_p{i}', arm, cid) for i in range(1,7) for arm in ('A','B') for cid in candidates}
    keys = [(r['problem_id'],r['arm'],r['candidate_id']) for r in rows]
    require(len(keys) == 48 and set(keys) == expected_keys, 'Incomplete or duplicated candidate matrix')
    grade_paths = set()
    for row in rows:
        pid = row['problem_id']
        proof = artifact(row['proof_path'])
        require(sha(proof) == row['proof_file_sha256'], 'Submitted proof byte hash mismatch')
        require(text_sha(proof.read_text()) == row['proof_sha256'], 'Submitted proof grading hash mismatch')
        problem = read(artifact(f'problems/{pid}.json'))
        problem_hash = text_sha(problem.get('claim') or problem['problem'])
        require(len(row['scores']) == len(row['grade_paths']) == 2, 'Missing grading pass')
        for repeat, (score, name) in enumerate(zip(row['scores'],row['grade_paths']), 1):
            require(type(score) is int and 0 <= score <= 7, 'Invalid numerical grade')
            grade = read(artifact(name)); grade_paths.add(name)
            for field, value in [('problem_id',pid), ('repeat',repeat), ('proof_sha256',row['proof_sha256']),
                                 ('problem_sha256',problem_hash), ('reference_sha256',references[pid]),
                                 ('policy_sha256',policy), ('model',comparison['model']),
                                 ('reasoning_effort',comparison['reasoning_effort'])]:
                require(grade[field] == value, f'Grade identity mismatch: {name} / {field}')
            require(grade['grade']['score'] == score, 'Score differs from saved judgment')
            require(grade['isolation_audit']['tool_calls'] == 0, 'Grader isolation mismatch')
        same(row['mean_score'],sum(row['scores']) / 2,'Candidate mean mismatch')
    require(len(grade_paths) == 96, 'Expected 96 independent grade records')
    for problem in comparison['problems']:
        pid = problem['problem_id']
        for arm in ('A','B'):
            subset = [r for r in rows if r['problem_id']==pid and r['arm']==arm]
            summary = problem[arm]
            same(summary['mean_score'],sum(sum(r['scores']) for r in subset)/8, 'Problem mean mismatch')
            require(summary['candidate_order'] == candidates, 'Candidate ordering mismatch')
            ordered = [next(r for r in subset if r['candidate_id']==cid) for cid in candidates]
            require(summary['score_vectors'] == {str(i+1):[r['scores'][i] for r in ordered] for i in range(2)},
                    'Per-pass score vector mismatch')
            require(summary['best_score_by_pass'] == [max(r['scores'][i] for r in subset) for i in range(2)],
                    'Problem best score mismatch')
            require(summary['stage_counts'] == dict(Counter(r['selected_stage'] for r in subset)), 'Stage counts mismatch')
        same(problem['delta'],problem['B']['mean_score']-problem['A']['mean_score'],'Problem delta mismatch')
    for arm in ('A','B'):
        subset=[r for r in rows if r['arm']==arm]
        summary=comparison['summary'][arm]
        same(summary['equal_weight_problem_mean'],sum(sum(r['scores']) for r in subset)/48,'Overall mean mismatch')
        best=[sum(max(r['scores'][i] for r in subset if r['problem_id']==f'imo2026_p{p}')
                  for p in range(1,7)) for i in range(2)]
        require(summary['sum_per_problem_best_by_pass'] == best, 'Best-per-problem totals mismatch')
        require(summary['both_passes_7_count'] == sum(r['scores']==[7,7] for r in subset), 'Full-credit count mismatch')
        require(summary['fallback_count'] == sum(bool(r['fallback']) for r in subset), 'Fallback count mismatch')
        require(summary['disagreement_count'] == sum(r['scores'][0]!=r['scores'][1] for r in subset), 'Disagreement count mismatch')
    same(comparison['summary']['mean_delta'],comparison['summary']['B']['equal_weight_problem_mean']-
         comparison['summary']['A']['equal_weight_problem_mean'],'Aggregate delta mismatch')
    require(comparison['B_new_grade_invocations']==comparison['B_grader_process_attempts']==48
            and comparison['retry_errors']==[], 'B grading invocation accounting mismatch')
    print('Verified 48 submitted proofs, 96 grades, all artifact hashes, score matrices and A/B aggregates.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive',type=Path,default=DEFAULT)
    verify(parser.parse_args().archive)


if __name__=='__main__':
    main()
