#!/usr/bin/env python3
"""Publish or verify Qwen-only re-tallies of archived votes, without inference."""
import argparse
from collections import Counter
from fractions import Fraction
import itertools
import json
from pathlib import Path
import re

import export_proofbench_final as proofbench
import verify_latest_selection as imo

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = Path('docs/results/qwen_selection_20260928')
SOURCES = {
    'IMO': ('docs/results/imo2026_b112_selection_20260922',
            '137d738ca3e5468f122618828b464df61c0f04d5fcfea954d2a76a875d0ced59'),
    'ProofBench': ('docs/results/proofbench_b112_final_20260926',
                   '87f2de04e3157ed0a9c790769f6ea5198df8f2bc54c6101a5b87fac4127779a2'),
}


def select(order, votes):
    """Select before accessing grades; ties retain the archived seed order."""
    rows = [v for v in votes if v['model_key'] == 'qwen']
    expected = {(tuple(sorted(pair)), direction) for pair in itertools.combinations(order, 2)
                for direction in ('forward', 'reverse')}
    actual = {(tuple(sorted(v['presentation_order'])), v['order']) for v in rows}
    assert len(rows) == len(actual) == len(expected) and actual == expected
    assert len({v['case_id'] for v in rows}) == len(rows)
    for vote in rows:
        assert vote.get('valid', True) and vote.get('binding_verified', True)
        assert vote['winner_label'] in ('A', 'B')
        assert vote['selected_candidate'] == vote['presentation_order'][vote['winner_label'] == 'B']
    counts = Counter({candidate: 0 for candidate in order})
    counts.update(v['selected_candidate'] for v in rows)
    return dict(selected_candidate=max(order, key=counts.get), votes_received=dict(counts),
                qwen_vote_ids=[v['case_id'] for v in rows], valid_votes=len(rows))


def aggregate(rows):
    return dict(problems=len(rows), available_lanes=sum(p['available_lanes'] for p in rows),
        missing_lanes=sum(4 - p['available_lanes'] for p in rows), score_denominator=7 * len(rows),
        average_score_sum=float(sum(sum(Fraction(sum(l['scores']), 2) for l in p['lanes']
            if l['available']) / p['available_lanes'] for p in rows)),
        selected_score_sum=sum(p['selected_mean'] for p in rows),
        oracle_at_4_score_sum=sum(p['oracle_at_4'] for p in rows),
        previous_selected_score_sum=sum(p['previous_selected_mean'] for p in rows),
        best_or_tied=sum(p['selected_mean'] == p['oracle_at_4'] for p in rows),
        changed_lanes=sum(p['selected_candidate'] != p['previous_selected_candidate'] for p in rows),
        improved_problems=sum(p['selected_mean'] > p['previous_selected_mean'] for p in rows),
        worse_problems=sum(p['selected_mean'] < p['previous_selected_mean'] for p in rows),
        selected_low_over_high=[p['problem_id'] for p in rows if p['selected_mean'] <= 1 and p['oracle_at_4'] >= 6])


def build():
    rows, sources = [], {}
    for benchmark, (relative, digest) in SOURCES.items():
        bundle = ROOT / relative
        assert imo.sha(bundle / 'SCORECARD.json') == digest, 'Archived scorecard changed'
        source = (imo.verify if benchmark == 'IMO' else proofbench.verify)(bundle)
        sources[benchmark] = dict(scorecard=relative + '/SCORECARD.json', sha256=digest,
                                  verified_artifacts=len(source['artifacts']))
        for problem in source['problems']:
            selection = problem if benchmark == 'IMO' else problem['selection']
            order = selection['seed_derived_candidate_order']
            result = select(order, selection['votes'])
            lanes = []
            for lane in problem['lanes']:
                available = lane.get('available', True)
                record = dict(candidate_id=lane['candidate_id'], available=available,
                    scores=lane['scores'], mean=sum(lane['scores']) / 2 if available else None,
                    selected_stage=lane.get('selected_stage', lane.get('stage')))
                if available:
                    record.update(proof=relative + '/' + lane['proof'], proof_sha256=lane['proof_sha256'],
                                  grades=[relative + '/' + g for g in lane['grades']])
                lanes.append(record)
            scores = {lane['candidate_id']: lane['mean'] for lane in lanes if lane['available']}
            assert set(scores) == set(order) and len(order) == len(set(order))
            previous = problem['selected_candidate']
            rows.append(dict(problem_id=problem['problem_id'],
                group='IMO' if benchmark == 'IMO' else problem['problem_id'].split('-')[1],
                source_scorecard=sources[benchmark]['scorecard'], lanes=lanes,
                seed_derived_candidate_order=order, **result, available_lanes=len(scores),
                average=sum(scores.values()) / len(scores), oracle_at_4=max(scores.values()),
                selected_mean=scores[result['selected_candidate']], previous_selected_candidate=previous,
                previous_selected_mean=scores[previous]))
    groups = {name: aggregate([p for p in rows if p['group'] == name or
              (name == 'ProofBench' and p['group'] != 'IMO')]) for name in ('IMO', 'Basic', 'Advanced', 'ProofBench')}
    return dict(schema='qwen-saved-vote-selection-v1', published='2026-09-28',
        method='Re-tally archived Qwen comparisons only; keep archived seed-derived tie order.',
        grading='Mean of two existing grades per available proof; no regrading.',
        missing_policy='Exclude missing lanes from per-problem averages; weight each problem equally.',
        generation_and_r2_r3_audit='Unchanged archived lane finals.',
        additional_model_calls=0, additional_grading_calls=0, sources=sources,
        groups=groups, problems=rows)


def number(value):
    return f'{value:g}'


def imo_section(data):
    lines = ['| Problem | Average | Selector@1 | Oracle@4 |', '|---|---:|---:|---:|']
    for p in data['problems']:
        if p['group'] == 'IMO':
            lines.append('| ' + p['problem_id'].split('_')[-1].upper() + ' | ' +
                         ' | '.join(number(p[k]) for k in ('average', 'selected_mean', 'oracle_at_4')) + ' |')
    g = data['groups']['IMO']
    lines += ['| **Total (of 42)** | ' + ' | '.join('**' + number(g[k]) + '**' for k in
              ('average_score_sum', 'selected_score_sum', 'oracle_at_4_score_sum')) + ' |', '',
              f'[Qwen selections and archived proof grades]({DESTINATION}/README.md)', '']
    return '\n'.join(lines)


def proofbench_section(data):
    lines = ['| Set | Problems | Proofs | Average | Selector@1 | Oracle@4 |', '|---|---:|---:|---:|---:|---:|']
    for name in ('Basic', 'Advanced', 'ProofBench'):
        g = data['groups'][name]
        cells = [f"{100 * g[k] / g['score_denominator']:.2f}%" for k in
                 ('average_score_sum', 'selected_score_sum', 'oracle_at_4_score_sum')]
        lines.append(f"| {'Combined' if name == 'ProofBench' else name} | {g['problems']} | "
                     f"{g['available_lanes']}/{4*g['problems']} | " + ' | '.join(cells) + ' |')
    g = data['groups']['ProofBench']
    assert not g['selected_low_over_high']
    lines += ['', 'Three proofs are missing and are left out of the averages. The selector chose a',
        f"best-scoring proof, or one tied with it, on {g['best_or_tied']} of {g['problems']} problems, and never chose a",
        '0–1 proof when a 6–7 proof was available.', '',
        f'[Qwen selections and comparison with the archived results]({DESTINATION}/README.md) ·',
        f'[SCORECARD.json]({DESTINATION}/SCORECARD.json)']
    return '\n'.join(lines)


def update_readme(text, data):
    for marker, value in [('LATEST SELECTOR RESULTS', imo_section(data)),
                          ('FINAL PROOFBENCH RESULTS', proofbench_section(data) + '\n')]:
        before, rest = text.split('<!-- BEGIN ' + marker + ' -->\n')
        _, after = rest.split('<!-- END ' + marker + ' -->')
        text = before + '<!-- BEGIN ' + marker + ' -->\n' + value + '<!-- END ' + marker + ' -->' + after
    for name in ('Basic', 'Advanced'):
        g = data['groups'][name]
        line = f"| {name} (30) | {100*g['average_score_sum']/210:.2f}% | **{100*g['selected_score_sum']/210:.2f}%** | {100*g['oracle_at_4_score_sum']/210:.2f}% |"
        text, count = re.subn(r'^\| ' + name + r' \(30\) \|.*$', lambda _: line, text, flags=re.M)
        assert count == 1
    return text


def update_release_report(text, data):
    for marker, value in [('QWEN IMO RESULTS', imo_section(data)),
                          ('QWEN PROOFBENCH RESULTS', proofbench_section(data) + '\n')]:
        before, rest = text.split('<!-- BEGIN ' + marker + ' -->\n')
        _, after = rest.split('<!-- END ' + marker + ' -->')
        value = value.replace('(docs/results/', '(results/')
        text = before + '<!-- BEGIN ' + marker + ' -->\n' + value + '<!-- END ' + marker + ' -->' + after
    return text


def report(data):
    lines = ['# Qwen-only selection of archived final proofs', '',
        'Recomputed on September 28, 2026 from the published IMO and ProofBench votes and double grades.',
        'Only Qwen votes count. Each pair is compared in both presentation orders: 12 votes for four lanes,',
        'or 6 for three available lanes. Ties follow the archived seed-derived order, without using grades.',
        'Proofs, R2/R3 audit decisions and grades are unchanged. This is an offline re-tally, not a new generation run.', '',
        '| Set | Previous Selector@1 | Qwen Selector@1 | Best or tied with oracle |', '|---|---:|---:|---:|']
    for name, g in data['groups'].items():
        values = [number(g[k]) + '/42' if name == 'IMO' else f"{100*g[k]/g['score_denominator']:.2f}%"
                  for k in ('previous_selected_score_sum', 'selected_score_sum')]
        lines.append(f"| {name} | {' | '.join(values)} | {g['best_or_tied']}/{g['problems']} |")
    lines += ['', 'Average and Oracle@4 are unchanged. Three missing ProofBench lanes stay excluded.',
        'ProofBench changes 11 selected lanes: three scores improve by 0.5 and none decreases.',
        'The IMO selected lane changes only on P6, with the same mean grade of 3.', '',
        '| Problem | Previous lane | Previous score | Qwen lane | Qwen score | Delta | Votes |',
        '|---|---|---:|---|---:|---:|---:|']
    for p in data['problems']:
        lane = next(l for l in p['lanes'] if l['candidate_id'] == p['selected_candidate'])
        lines.append(f"| {p['problem_id']} | {p['previous_selected_candidate']} | {p['previous_selected_mean']:g} | "
            f"[{p['selected_candidate']}](../../../{lane['proof']}) | {p['selected_mean']:g} | "
            f"{p['selected_mean'] - p['previous_selected_mean']:+g} | {p['valid_votes']} |")
    lines += ['', 'The [scorecard](SCORECARD.json) records every lane score, selected proof hash, grade paths,',
        'Qwen vote IDs, tallies, seed order and source scorecard hashes. Original vote responses remain in',
        'the hash-verified source bundles linked below; the original selections are preserved there.', '',
        *[f"- [{name} original evidence](../../../{path}/README.md)" for name, (path, _) in SOURCES.items()], '',
        'Recompute all selections and verify every source artifact, the derived scorecard and README tables:', '',
        '```bash', 'python3 -B scripts/report_qwen_selection.py --verify', '```', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write', action='store_true')
    mode.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    data = build()
    targets = {ROOT / DESTINATION / 'SCORECARD.json': json.dumps(data, indent=2) + '\n',
               ROOT / DESTINATION / 'README.md': report(data),
               ROOT / 'README.md': update_readme((ROOT / 'README.md').read_text(), data),
               ROOT / 'docs/public_release_report.md': update_release_report(
                   (ROOT / 'docs/public_release_report.md').read_text(), data)}
    for path, value in targets.items():
        if args.write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value)
        else:
            assert path.read_text() == value, 'Published Qwen results differ: ' + str(path)
    print(json.dumps(dict(state='written' if args.write else 'verified', groups=data['groups']), indent=2))


if __name__ == '__main__':
    main()
