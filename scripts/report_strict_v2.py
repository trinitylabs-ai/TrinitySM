#!/usr/bin/env python3
"""Publish or verify the separate v2 audit without changing v1 matrices."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from score_imo_v2 import POLICY_SHA256, ROOT, prepare_runner, validate_trace

DEFAULT_RUN = ROOT / "benchmarks/imo2026/results/strict_v2_20260918T061000Z"
ORDER = ["t07_r01", "t07_r02", "t10_r01", "t10_r02"]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def first_valid_response(path, runner):
    """Select chronologically, including responses rejected by the old validator.

    Do not make new calls or select by numerical score. Preserve the native batch
    artifacts and disclose any automatic retry or contract-only recovery.
    """
    attempts = []
    for line in path.read_text(encoding='utf-8').splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            event = {}
        if 'attempt' in event and 'returncode' in event:
            attempts.append(dict(header=event, lines=[]))
        elif attempts:
            attempts[-1]['lines'].append(line)
    rejected = 0
    process_failures = []
    for attempt in attempts:
        if attempt['header']['returncode'] != 0:
            rejected += 1
            process_failures.append(dict(attempt=attempt['header']['attempt'],
                                         returncode=attempt['header']['returncode'],
                                         reason='model_capacity' if any('Selected model is at capacity.' in line
                                                                       for line in attempt['lines']) else 'process_failure'))
            continue
        try:
            validate_trace('\n'.join(attempt['lines']))
            messages = []
            for line in attempt['lines']:
                try:
                    event = json.loads(line)
                except ValueError:
                    continue
                if event.get('type') == 'item.completed' and event.get('item', {}).get('type') == 'agent_message':
                    messages.append(event['item']['text'])
            assert len(messages) == 1, 'Expected one completed grade message'
            grade = runner.validate_grade(json.loads(messages[0]))
        except (ValueError, AssertionError, KeyError):
            rejected += 1
            continue
        return grade, dict(selected_attempt=attempt['header']['attempt'], total_attempts=len(attempts),
                           rejected_attempts_before_selection=rejected,
                           failed_process_attempts=process_failures,
                           unselected_later_attempts=len(attempts) - attempt['header']['attempt'])
    raise ValueError('No valid isolated response; this proof remains ungraded')


def report(rows, run):
    def link(path):
        return Path(os.path.relpath(ROOT / path, run / "reports")).as_posix()

    lines = ["# IMO 2026: separate strict-v2 audit", "",
             "The submitted mathematics is unchanged. V2 uses Rules A--F with the agreed",
             "clarifications. The original v1 scores remain in the release matrices.", "",
             "Evaluator: `gpt-5.6-sol`, `xhigh`; independent calls by submitted proof,",
             "four workers, with retries disclosed below. Each selected response passed",
             "the zero-tool-call isolation audit.",
             "V2 policy SHA-256: `" + POLICY_SHA256 + "`.", "",
             "Single grades under each policy do not separate policy effects from grader",
             "variation. These are local strict grades, not official IMO jury scores.", "",
             "## Core proofs: v1 → v2", "",
             "| Problem | t07_r01 | t07_r02 | t10_r01 | t10_r02 | Average | Oracle@4 |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    totals = [0, 0, 0, 0]
    for n in range(1, 7):
        rs = sorted([r for r in rows if r['group'] == 'core' and r['problem_id'] == f'imo2026_p{n}'],
                    key=lambda r: ORDER.index(r['candidate']))
        assert len(rs) == 4
        before = [r['v1_score'] for r in rs]
        after = [r['grade']['score'] for r in rs]
        stats = [sum(before)/4, sum(after)/4, max(before), max(after)]
        totals = [a+b for a, b in zip(totals, stats)]
        lines.append(f"| P{n} | " + " | ".join(f"{a} → {b}" for a, b in zip(before, after)) +
                     f" | {stats[0]:.2f} → {stats[1]:.2f} | {stats[2]} → {stats[3]} |")
    lines += [f"| Total /42 | — | — | — | — | {totals[0]:.2f} → {totals[1]:.2f} | {totals[2]} → {totals[3]} |",
              "", "Each per-problem score is out of 7. Average is the mean of the four",
              "fixed submissions; Oracle@4 is their maximum. Totals sum across six problems.",
              "", "## P2 experimental rewrites", "",
              "These three rewrites are reported separately from the 24 core proofs.", "",
              "| Candidate | Same rewrite: v1 → v2 | V2 input → rewrite |",
              "|---|---:|---:|"]
    for r in rows:
        if r['group'] != 'tool_rewrite':
            continue
        base = next(x for x in rows if x['group'] == 'core' and x['problem_id'] == r['problem_id'] and x['candidate'] == r['candidate'])
        lines.append(f"| {r['candidate']} | {r['v1_score']} → {r['grade']['score']} | {base['grade']['score']} → {r['grade']['score']} |")
    lines += ["", "## Individual assessments", "",
              "Every v2 score and verdict follows. For scores below 7, the first issue is",
              "the evaluator's recorded assessment, not an additional human adjudication.", ""]
    for r in rows:
        g = r['grade']
        lines += [f"### {r['problem_id']} · {r['candidate']} · {r['group']}", "",
                  f"**{r['v1_score']} → {g['score']}/7; {g['verdict']}.** " +
                  f"[Submitted proof]({link(r['proof'])}) · [V2 grade]({link(r['v2_grade'])}) · " +
                  f"[V1 grade]({link(r['v1_grade'])})", ""]
        if g['score'] < 7:
            lines += [g['first_issue'], ""]
    lines += ["## Execution", "",
              f"Published grades: {len(rows)}. Unrecovered failed cases: 0. " +
              f"Native scorer failures recovered from existing responses: {sum(r['native_scorer_failed'] for r in rows)}.", "",
              f"Automatic extra attempts: {sum(r['response_selection']['total_attempts'] - 1 for r in rows)}. " +
              f"Invalid attempts preceding a selected response: {sum(r['response_selection']['rejected_attempts_before_selection'] for r in rows)}. " +
              f"Unselected later attempts: {sum(r['response_selection']['unselected_later_attempts'] for r in rows)}.", "",
              f"Provider-capacity failures successfully retried: {sum(f['reason'] == 'model_capacity' for r in rows for f in r['response_selection']['failed_process_attempts'])}.", "",
              "Responses are selected chronologically, using the first valid isolated",
              "response under the corrected v2 contract. The initial validator rejected",
              "full-credit Rule C exceptions that listed cosmetic issues; these",
              "responses are recovered without another model call. Native artifacts are",
              "preserved, and no response is selected by its numerical score.", "",
              "Problem, reference, proof, prompt and policy identities are recorded in the",
              "published grades. Runtime logs and machine-local paths are excluded.", ""]
    return "\n".join(lines)


def validate_rows(rows, manifest, runner):
    assert len(rows) == len(manifest['records']) == 27, "Incomplete audit"
    expected = {(r['problem_id'], r['grader_candidate']): r for r in manifest['records']}
    assert len(expected) == 27
    assert {(r['problem_id'], r['grader_candidate']) for r in rows} == set(expected)
    for r in rows:
        e = expected[r['problem_id'], r['grader_candidate']]
        for key in ['problem_sha256', 'reference_sha256', 'proof_sha256', 'v1_score', 'v1_grade', 'proof', 'group', 'candidate']:
            assert r[key] == e[key], f"Changed binding: {key}"
        assert sha(ROOT / r['proof']) == r['proof_sha256'], "Changed submitted proof"
        old = read(ROOT / r['v1_grade'])
        assert old['grade']['score'] == r['v1_score'] and old['proof_sha256'] == r['proof_sha256']
        assert r['policy_sha256'] == POLICY_SHA256
        assert r['grader'] == 'gpt-5.6-sol' and r['reasoning_effort'] == 'xhigh'
        assert r['isolation_audit']['tool_calls'] == 0 and r['isolation_audit']['successful_processes_audited']
        original = {k:v for k,v in r['grade'].items() if k not in {'contract_consistent', 'full_credit'}}
        assert runner.validate_grade(original) == r['grade']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, default=DEFAULT_RUN)
    parser.add_argument('--work-results', type=Path)
    parser.add_argument('--publish', action='store_true', help='Export completed private results; default verifies existing exports')
    args = parser.parse_args()
    run = args.run.resolve()
    manifest = read(run / 'manifest.json')
    runner = prepare_runner()
    tasks = runner.generic_proof_task_manifests([run / 'grading/tasks.json'])
    lookup = {(t['problem_id'], t['candidate_id']): t for t in tasks}
    if args.publish:
        work = args.work_results or run / 'grading/work/results'
        status = read(work / 'summary.json')
        assert status['state'] in {'completed', 'failed'}, 'Audit is not terminal'
        rows = []
        for e in manifest['records']:
            task = lookup[e['problem_id'], e['grader_candidate']]
            case = work / f"p{task['problem_number']}" / e['grader_candidate']
            result = read(case / 'summary.json')
            meta = read(case / 'manifest.json')
            assert result['state'] in {'completed', 'failed'}
            for key in ['problem_sha256', 'reference_sha256', 'proof_sha256']:
                assert result[key] == e[key]
            prompt = runner.grading_prompt(problem=task['problem'], reference=task['reference'],
                                           proof=task['proof'], grading_policy=runner.STRICT_POLICY)
            assert hashlib.sha256(prompt.encode()).hexdigest() == meta['prompt_sha256']
            target = run / 'grades' / e['problem_id'] / (e['grader_candidate'] + '.json')
            grade, selection = first_valid_response(case / 'codex.jsonl', runner)
            rows.append({**e, 'v2_grade': str(target.relative_to(ROOT)),
                         **{k:result[k] for k in ['grader', 'reasoning_effort', 'policy_sha256', 'completed_at']},
                         'grade': grade, 'response_selection': selection,
                         'native_scorer_failed': result['state'] == 'failed',
                         'prompt_sha256': meta['prompt_sha256'],
                         'isolation_audit': dict(tool_calls=0, successful_processes_audited=True),
                         'native_rejection_count': len(result['errors'])})
        validate_rows(rows, manifest, runner)
        for row in rows:
            write(ROOT / row['v2_grade'], row)
        artifacts = {r['v2_grade']: sha(ROOT / r['v2_grade']) for r in rows}
        snapshot = dict(schema='workshop-strict-v2-results-v1', policy_sha256=POLICY_SHA256,
                        rows=rows, artifacts=artifacts)
        write(run / 'score_snapshot.json', snapshot)
        (run / 'reports').mkdir(exist_ok=True)
        (run / 'reports/comparison.md').write_text(report(rows, run), encoding='utf-8')
    snapshot = read(run / 'score_snapshot.json')
    rows = snapshot['rows']
    validate_rows(rows, manifest, runner)
    assert set(snapshot['artifacts']) == {r['v2_grade'] for r in rows}
    for row in rows:
        assert read(ROOT / row['v2_grade']) == row, 'Snapshot differs from published grade'
        task = lookup[row['problem_id'], row['grader_candidate']]
        for key in ['problem_sha256', 'reference_sha256', 'proof_sha256']:
            assert row[key] == task[key], f'Published input differs from task: {key}'
        prompt = runner.grading_prompt(problem=task['problem'], reference=task['reference'],
                                       proof=task['proof'], grading_policy=runner.STRICT_POLICY)
        assert hashlib.sha256(prompt.encode()).hexdigest() == row['prompt_sha256']
    for path, digest in snapshot['artifacts'].items():
        assert sha(ROOT / path) == digest
    assert (run / 'reports/comparison.md').read_text() == report(rows, run)
    print(f"Verified {len(rows)} strict-v2 grades, frozen inputs, v1 comparisons, isolation records, and report.")
    print(run / 'reports/comparison.md')


if __name__ == '__main__':
    main()
