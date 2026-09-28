"""Replay saved audits without making model calls or changing source artifacts."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from statistics import mean

from .validation import ACCEPT, KEEP, VERSION, select_candidate, validate_audit
from .bindings import verify_audit_binding

STRATEGIES = {"gemma": ("gemma",), "qwen": ("qwen",), "both": ("gemma", "qwen")}


def read(path):
    return json.loads(Path(path).read_text())


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def replay(roots, output):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    status = {"state": "running", "new_model_calls": 0, "validator_version": VERSION}
    write(output / 'status.json', status)
    try:
        cases, votes, provenance = [], [], {}

        def bound(path, expected=None):
            path = Path(path).resolve()
            actual = digest(path)
            if expected is not None and actual != expected:
                raise ValueError('Hash mismatch: ' + str(path))
            provenance[str(path)] = actual
            return path

        # Selection is completed before loading any evaluation labels or grades.
        for root in map(Path, roots):
            root = root.resolve()
            manifest = read(bound(root / 'manifest.json'))
            plan = read(bound(root / 'audit_plan.json'))
            source_cases = {case['case_id']: case for case in manifest['cases']}
            for case in source_cases.values():
                for name, expected in case['files'].items():
                    bound(root / 'model_inputs' / case['case_id'] / name, expected)
                assert case['files']['baseline.md'] == case['baseline_sha256']
                assert case['files']['candidate.md'] == case['candidate_sha256']
                assert case['identical'] == (case['baseline_sha256'] == case['candidate_sha256'])
            root_votes = []
            for task in plan['audits']:
                case = source_cases[task['original_case_id']]
                assert task['changes'] == case['changes']
                for role in ('baseline', 'candidate'):
                    assert task[role + '_sha256'] == case[role + '_sha256']
                for name, expected in task['files'].items():
                    bound(root / 'model_inputs' / task['case_id'] / name, expected)
                folder = root / 'cases' / task['case_id']
                original = read(bound(folder / 'result.json'))
                call = read(bound(folder / 'audit/call_result.json'))
                binding = verify_audit_binding(root, task, original, call)
                provenance.update(binding['source_hashes'])
                parsed = validate_audit(call['text'], task)
                assert parsed['response_sha256'] == call['final_sha256'] == original['audit_sha256']
                vote = {**parsed, **{k: task[k] for k in ('case_id', 'original_case_id', 'problem_id', 'model_key', 'order')},
                        'source_root': str(root), 'response_path': str(folder / 'audit/call_result.json')}
                root_votes.append(vote)
            votes.extend(root_votes)
            for case in source_cases.values():
                audits = [vote for vote in root_votes if vote['original_case_id'] == case['case_id']]
                strategies = {}
                for name, models in STRATEGIES.items():
                    chosen = [vote for vote in audits if vote['model_key'] in models]
                    validated = select_candidate(case['case_id'], chosen, models)
                    raw_accept = (len(chosen) == 2 * len(models) and
                                  {(v['model_key'], v['order']) for v in chosen} ==
                                  {(m, o) for m in models for o in ('forward', 'reverse')} and
                                  all(v['model_decision'] == ACCEPT for v in chosen))
                    decisions = {'raw': ACCEPT if raw_accept else KEEP,
                                 'validated': validated['decision'] if not case['identical'] else KEEP}
                    strategies[name] = {**decisions, 'validation': validated}
                    for mode, decision in decisions.items():
                        role = 'candidate' if decision == ACCEPT else 'baseline'
                        source = root / 'model_inputs' / case['case_id'] / (role + '.md')
                        target = output / 'selected_proofs' / name / mode / (case['case_id'] + '.md')
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(source.read_bytes())
                        assert digest(target) == case[role + '_sha256']
                cases.append({**case, 'source_root': str(root), 'strategies': strategies})
        assert len({(case['problem_id'], case['case_id']) for case in cases}) == len(cases)
        write(output / 'SELECTIONS.json', {'cases': cases, 'votes': votes, 'grade_access': False})

        # Reporting only: attach hash-verified, previously completed two-pass grades.
        for case in cases:
            labels = read(bound(Path(case['source_root']) / 'evaluation_only/labels.json'))['rows']
            label = next(row for row in labels if row['case_id'] == case['case_id'])
            for role in ('r2', 'final'):
                bound(label[role + '_grades_path'], label[role + '_grades_sha256'])
            bound(label['baseline_path'], case['baseline_sha256'])
            bound(label['candidate_path'], case['candidate_sha256'])
            case['candidate_id'] = label['candidate_id']
            case['r2_scores'], case['r3_scores'] = label['r2_scores'], label['final_scores']
            case['delta'] = mean(case['r3_scores']) - mean(case['r2_scores'])
            for values in case['strategies'].values():
                for mode in ('raw', 'validated'):
                    values[mode + '_scores'] = case['r3_scores'] if values[mode] == ACCEPT else case['r2_scores']
        summary = {}
        for problem in sorted({case['problem_id'] for case in cases}) + ['all']:
            group = [case for case in cases if problem == 'all' or case['problem_id'] == problem]
            summary[problem] = {'r2_mean': mean(mean(c['r2_scores']) for c in group),
                                'r3_mean': mean(mean(c['r3_scores']) for c in group), 'strategies': {}}
            for name in STRATEGIES:
                summary[problem]['strategies'][name] = {}
                for mode in ('raw', 'validated'):
                    summary[problem]['strategies'][name][mode] = {
                        'mean': mean(mean(c['strategies'][name][mode + '_scores']) for c in group),
                        'avoided_declines': sum(c['delta'] < 0 and c['strategies'][name][mode] == KEEP for c in group),
                        'accepted_gains': sum(c['delta'] > 0 and c['strategies'][name][mode] == ACCEPT for c in group),
                        'adopted_r3': sum(c['strategies'][name][mode] == ACCEPT for c in group),
                    }
        for path, expected in list(provenance.items()):
            assert digest(path) == expected, 'Source changed during replay: ' + path
        report = {'quality': 'evaluated_existing_two_pass_grades', 'validator_version': VERSION,
                  'finished_at': datetime.now(timezone.utc).isoformat(), 'new_model_calls': 0,
                  'source_runs': list(map(str, roots)), 'summary': summary, 'rows': cases, 'votes': votes,
                  'invalid_audits': sum(not v['valid'] for v in votes), 'source_hashes': provenance}
        write(output / 'REPORT.json', report)
        lines = ['# Mechanical validation replay', '',
                 'Saved responses only; zero new model calls. Selection precedes loading evaluation grades.',
                 'Each model must approve in both orders; the combined strategy requires all four valid approvals.', '',
                 '| Auditor | Before validation | After validation | Declines prevented after | Gains retained after |',
                 '|---|---:|---:|---:|---:|']
        for name, values in summary['all']['strategies'].items():
            before, after = values['raw'], values['validated']
            lines.append(f"| {name} | {before['mean']:.5f} | {after['mean']:.5f} | {after['avoided_declines']} | {after['accepted_gains']} |")
        lines += ['', '| Problem | Lane | R2 | R3 | Gemma validated | Qwen validated | Both validated |',
                  '|---|---|---|---|---|---|---|']
        for case in sorted(cases, key=lambda c: (c['problem_id'], c['candidate_id'])):
            selected = [str(case['strategies'][name]['validated_scores']) for name in STRATEGIES]
            lines.append(f"| {case['problem_id']} | {case['candidate_id']} | {case['r2_scores']} | {case['r3_scores']} | " + ' | '.join(selected) + ' |')
        lines += ['', 'Invalid audit records (retained as evidence; no mathematical repair):', '']
        for vote in votes:
            if not vote['valid']:
                case = next(c for c in cases if c['case_id'] == vote['original_case_id'])
                lines.append(f"- {case['problem_id']} {case['candidate_id']} {vote['model_key']} {vote['order']}: " + '; '.join(vote['errors']))
        lines += ['', 'Model-echoed hashes are diagnostic only; actual proof and request/response bindings are verified in code.',
                  'Grade agreement on this small retrospective sample is not a formal proof of correctness.', '']
        (output / 'REPORT.md').write_text('\n'.join(lines))
        write(output / 'status.json', {**status, 'state': 'completed', 'exit_code': 0,
                                      'report': str(output / 'REPORT.md')})
        return report
    except BaseException as error:
        write(output / 'status.json', {**status, 'state': 'failed', 'exit_code': 1, 'error': str(error)})
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-run', type=Path, action='append', required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    report = replay(args.source_run, args.output_dir)
    print(json.dumps(report['summary']['all'], indent=2))


if __name__ == '__main__':
    main()
