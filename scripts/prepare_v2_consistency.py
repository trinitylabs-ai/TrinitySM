#!/usr/bin/env python3
"""Freeze the release ablation cohorts for four independent strict-v2 grades.

Historical artifacts are read from --source-root, never modified. The output
contains portable mathematical inputs, hashes and provenance, without logs or
earlier grades in the evaluator's task manifests.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from score_imo_v2 import ROOT, POLICY_SHA256


def read(path):
    return json.loads(path.read_text())


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def prepare(source, ablation, run_id):
    group = ROOT / 'benchmarks/reports' / run_id
    if group.exists():
        raise ValueError('Choose a new study ID')
    group.mkdir(parents=True)
    (group / '.gitignore').write_text('work/\n')
    core = read(ROOT / 'docs/public_release/score_snapshot.json')
    advanced = read(source / 'benchmarks/reports/advanced_best_score_percentage_20260917T214759Z.json')
    adv_raw = [x for x in advanced['evidence'] if x['checkpoint'] == 'raw']
    assert len(adv_raw) == 119
    refs = {}
    for x in adv_raw:
        grade = read(Path(x['grade']))
        ref = Path(x['grade']).parent / 'reference.md'
        assert sha(ref.read_text().strip()) == grade['reference_sha256']
        if x['problem_id'] in refs:
            assert refs[x['problem_id']].read_text().strip() == ref.read_text().strip()
        refs[x['problem_id']] = ref
    for n in range(1, 31):
        pid = f'PB-Basic-{n:03d}'
        refs[pid] = ROOT / f'benchmarks/imo-proofbench/basic/results/pipeline_final/grading/problems/{pid}/reference.md'
    for n in range(1, 7):
        pid = f'imo2026_p{n}'
        refs[pid] = ROOT / f'benchmarks/imo2026/results/review_fusion/grading/problems/{pid}/reference.txt'
    units, observations, omissions = {}, [], []

    def add(pid, candidate, cohort, proof_path, expected, source_kind):
        benchmark = ('imo2026' if pid.startswith('imo2026') else
                     'imo-proofbench/basic' if 'Basic' in pid else 'imo-proofbench/advanced')
        problem_path = ROOT / f'benchmarks/{benchmark}/problems/{pid}.json'
        payload = read(problem_path)
        problem = (payload.get('claim') or payload.get('problem') or payload.get('statement')).strip()
        reference = refs[pid].read_text().strip()
        proof = proof_path.read_text().strip()
        assert proof and sha(proof) == expected, (pid, candidate, cohort, 'proof hash')
        hashes = dict(problem_sha256=sha(problem), reference_sha256=sha(reference), proof_sha256=sha(proof))
        identity = sha(json.dumps(hashes, sort_keys=True))
        base = ROOT / f'benchmarks/{benchmark}/results/{run_id}'
        if identity not in units:
            dest = base / f'proofs/{identity}.md'
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(proof)
            ref_dest = base / f'grading/inputs/{pid}/reference.md'
            ref_dest.parent.mkdir(parents=True, exist_ok=True)
            ref_dest.write_text(reference)
            (base / 'grading/.gitignore').write_text('work/\n')
            units[identity] = dict(unit_id=identity, problem_id=pid, benchmark=benchmark,
                                   problem_number=int(pid[-1:] if pid.startswith('imo2026') else pid[-3:]),
                                   problem=str(problem_path.relative_to(ROOT)),
                                   reference=str(ref_dest.relative_to(ROOT)), proof=str(dest.relative_to(ROOT)),
                                   **hashes)
        provenance_root = ROOT if proof_path.is_relative_to(ROOT) else source
        observations.append(dict(problem_id=pid, candidate=candidate, benchmark=benchmark,
                                 cohort=cohort, unit_id=identity, source_kind=source_kind,
                                 source_proof=str(proof_path.relative_to(provenance_root))))

    # Existing Basic no-BF drafts; two seed mismatches are retained separately.
    archive = ROOT / 'benchmarks/imo-proofbench/basic/results/raw_no_bf'
    for x in read(archive / 'manifest.json')['rows']:
        cohort = 'raw_no_bf_previous_seeds' if x['problem_id'] in {'PB-Basic-009', 'PB-Basic-026'} else 'raw_no_bf'
        add(x['problem_id'], x['candidate_id'], cohort, archive / x['proof'], x['proof_sha256'], 'archived_no_bf')
    # Completed fresh no-BF run: all Advanced, all IMO, and two seed-matched Basic problems.
    fresh = []
    for p in sorted((ablation / 'problems').glob('*/summary.json')):
        d = read(p)
        assert d['state'] == 'completed' and d['budget_forcing'] is False
        for x in d['rows']:
            assert x['state'] == 'completed' and x['finish_reason'] == 'stop' and not x['truncated']
            assert x['generation_requests'] == 1 and x['continuation_requests'] == 0
            add(x['problem_id'], x['candidate_id'], 'raw_no_bf', Path(x['proof_path']), x['proof_sha256'], 'fresh_no_bf')
            fresh.append({k: x[k] for k in ['problem_id', 'candidate_id', 'seed', 'temperature', 'model',
                                          'budget_forcing', 'generation_requests', 'continuation_requests',
                                          'finish_reason', 'truncated', 'proof_sha256', 'started_at', 'completed_at',
                                          'usage', 'request_sha256']})
    assert len(fresh) == 152
    write(group / 'fresh_generation.json', fresh)
    # Raw BF arms, before lazy checking or refinement.
    archive = ROOT / 'benchmarks/imo-proofbench/basic/results/pipeline_raw_bf'
    for x in read(archive / 'manifest.json')['rows']:
        add(x['problem_id'], x['candidate_id'], 'raw_bf', archive / x['proof'], x['proof_sha256'], 'archived_raw_bf')
    for x in adv_raw:
        add(x['problem_id'], x['candidate'], 'raw_bf', Path(x['proof']), x['proof_sha256'], 'selected_pipeline_raw')
    imo_root = source / 'runs/v0257_v108_six_problem_bf_temp_transition_20260904'
    for n in range(1, 7):
        for candidate in ['t07_r01', 't07_r02', 't10_r01', 't10_r02']:
            p = imo_root / f'p{n}/01_raw_lazy_enhanced_resolve/phase_1_raw_lazy/p{n}/candidates/{candidate}/draft_proof.md'
            result = read(p.with_name('cold_result.json'))
            expected = result.get('proof_sha256') or sha(p.read_text().strip())
            add(f'imo2026_p{n}', candidate, 'raw_bf', p, expected, 'recorded_imo_raw_bf')
    # Current full-harness cohort, including the six previously ungraded finals.
    upgraded = []
    for x in core['lanes']:
        if not x.get('included'):
            omissions.append(dict(problem_id=x['problem_id'], candidate=x['candidate'],
                                  cohorts=['raw_bf', 'full_harness'], reason='No generated proof'))
            continue
        b = x['baseline']; old = ROOT / 'docs/public_release' / b['proof']
        replacement = None
        if x['benchmark'] == 'Advanced' and x['c3_generation_state'] == 'completed' and b['checkpoint'] != 'R1-C3':
            pattern = f"advanced{x['problem_id'][-3:]}_c3_{x['candidate'].replace('_', '')}_*/generation/run/score_targets.json"
            for targets in sorted((source / 'benchmarks/imo-proofbench/advanced/results').glob(pattern)):
                for stage in read(targets).get('checkpoints', []):
                    if stage['checkpoint'] == 'R1-C3':
                        replacement = next((p for p in stage['proofs'] if p['candidate_id'] == x['candidate']), replacement)
            assert replacement, (x['problem_id'], x['candidate'], 'missing completed final')
        if replacement and replacement['proof_sha256'] != b['proof_sha256']:
            add(x['problem_id'], x['candidate'], 'previous_scored_fallback', old, b['proof_sha256'], 'release_selected_fallback')
            add(x['problem_id'], x['candidate'], 'full_harness', Path(replacement['proof_path']), replacement['proof_sha256'], 'completed_final_previously_ungraded')
            upgraded.append(dict(problem_id=x['problem_id'], candidate=x['candidate']))
        else:
            add(x['problem_id'], x['candidate'], 'full_harness', old, b['proof_sha256'], 'release_selected_final')
    # Retained tool examples, including their actual input proof where distinct.
    for x in read(ROOT / 'experiments/workshop_tools/score_snapshot.json')['records']:
        for which, cohort in [('input', 'tool_input'), ('rewrite', 'tool_rewrite')]:
            b = x[which]
            add(x['problem_id'], x['candidate'], cohort, ROOT / b['proof'], b['proof_sha256'], 'retained_tool_example')
    assert len(upgraded) == 6
    assert len({(o['problem_id'], o['candidate'], o['cohort']) for o in observations}) == len(observations)
    manifest = dict(schema='workshop-v2-consistency-study-v1', run_id=run_id,
                    policy_sha256=POLICY_SHA256, model='gpt-5.6-sol', reasoning_effort='xhigh', repeats=4,
                    previous_grades_reused=False, model_inputs='Frozen policy, one statement, one reference, one proof only.',
                    identical_inputs='Four calls per unique statement/reference/proof triple; shared across cohort memberships.',
                    units=list(units.values()), observations=observations, omissions=omissions,
                    newly_included_finals=upgraded,
                    cohort_counts=dict(Counter(o['cohort'] for o in observations)),
                    unique_proofs=len(units), planned_grades=4*len(units))
    write(group / 'manifest.json', manifest)
    for benchmark in ['imo-proofbench/basic', 'imo-proofbench/advanced', 'imo2026']:
        base = ROOT / f'benchmarks/{benchmark}/results/{run_id}'
        write(base / 'manifest.json', dict(schema='workshop-v2-consistency-benchmark-v1', run_id=run_id,
                                         study=str((group/'manifest.json').relative_to(ROOT)),
                                         units=[u for u in units.values() if u['benchmark'] == benchmark]))
    print(json.dumps({k:manifest[k] for k in ['cohort_counts', 'unique_proofs', 'planned_grades', 'omissions']}, indent=2))
    print(group)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-root', type=Path, required=True)
    p.add_argument('--ablation-run', type=Path, required=True)
    p.add_argument('--run-id', required=True)
    a = p.parse_args()
    prepare(a.source_root.resolve(), a.ablation_run.resolve(), a.run_id)
