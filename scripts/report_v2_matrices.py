#!/usr/bin/env python3
"""Summarize category Average and Oracle@4 across independent grading passes."""
import argparse
from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path

METHODS = {'mean': lambda v: sum(v) / len(v), 'lowest': min, 'highest': max}
SETTINGS = {'raw_no_bf': 'Raw without extended reasoning',
            'raw_bf': 'Raw with extended reasoning',
            'full_harness': 'Extended reasoning + full harness'}
LABELS = {'imo-proofbench/basic': 'Basic', 'imo-proofbench/advanced': 'Advanced',
          'imo-proofbench/all': 'All', 'imo2026': 'IMO 2026'}


def build_matrices(manifest, results):
    repeats = manifest.get('repeats', 4)
    if repeats not in [2, 4] or results.get('repeats', repeats) != repeats:
        raise ValueError('Unsupported or mismatched repetition count')
    if results['state'] != 'completed' or results.get('active_batch') is not None:
        raise ValueError('All grading must finish before final matrices are generated')
    units = {u['unit_id']: u for u in manifest['units']}
    rows = {r['unit_id']: r for r in results['rows']}
    if (len(units) != manifest['unique_proofs'] or set(rows) != set(units)
            or len(rows) != len(results['rows'])
            or results['completed_grades'] != manifest['planned_grades']
            or results.get('completed_proofs', results.get('completed_quartets')) != len(units)
            or manifest['planned_grades'] != repeats * len(units)):
        raise ValueError('Incomplete or mismatched result inventory')
    for key in ['model', 'reasoning_effort', 'policy_sha256']:
        if results[key] != manifest[key]:
            raise ValueError(f'Result provenance mismatch: {key}')
    for uid, row in rows.items():
        if (row['problem_id'] != units[uid]['problem_id'] or len(row['scores']) != repeats
                or any(type(x) is not int or not 0 <= x <= 7 for x in row['scores'])):
            raise ValueError(f"Every proof must have {'four' if repeats==4 else 'two'} valid grades")

    groups = defaultdict(lambda: defaultdict(list))
    memberships = set()
    tool_pairs = defaultdict(set)
    for o in manifest['observations']:
        key = (o['benchmark'], o['cohort'], o['problem_id'], o['candidate'])
        if key in memberships:
            raise ValueError('Duplicate candidate membership')
        memberships.add(key)
        if any(o[k] != units[o['unit_id']][k] for k in ['benchmark', 'problem_id']):
            raise ValueError('Observation identity mismatch')
        groups[o['benchmark'], o['cohort']][o['problem_id']].append(rows[o['unit_id']]['scores'])
        if o['cohort'] in ['tool_input', 'tool_rewrite']:
            tool_pairs[o['benchmark'], o['problem_id'], o['candidate']].add(o['cohort'])
    if any(pair != {'tool_input', 'tool_rewrite'} for pair in tool_pairs.values()):
        raise ValueError('Tool comparison is missing its input or rewrite')

    categories = []
    for (benchmark, cohort), problems in sorted(groups.items()):
        categories.append(dict(benchmark=benchmark, cohort=cohort, problems=len(problems),
                               maximum_points=7 * len(problems),
                               repeat_average_points=[sum(sum(v[i] for v in vs)/len(vs) for vs in problems.values()) for i in range(repeats)],
                               repeat_oracle_at_4_points=[sum(max(v[i] for v in vs) for vs in problems.values()) for i in range(repeats)]))
    lookup = {(c['benchmark'], c['cohort']): c for c in categories}
    for setting in SETTINGS:
        both = [lookup.get((benchmark, setting)) for benchmark in ['imo-proofbench/basic', 'imo-proofbench/advanced']]
        if all(both):
            categories.append(dict(benchmark='imo-proofbench/all', cohort=setting,
                                   problems=sum(c['problems'] for c in both),
                                   maximum_points=sum(c['maximum_points'] for c in both),
                                   **{k: [sum(c[k][i] for c in both) for i in range(repeats)]
                                      for k in ['repeat_average_points', 'repeat_oracle_at_4_points']}))
    for c in categories:
        c['summaries'] = {method: dict(average_points=reduce(c['repeat_average_points']),
                                      oracle_at_4_points=reduce(c['repeat_oracle_at_4_points']))
                          for method, reduce in METHODS.items()}
    return dict(schema='workshop-strict-v2-category-matrices-v1', run_id=manifest['run_id'], repeats=repeats,
                results_updated_at=results['updated_at'],
                **{k: results[k] for k in ['model', 'reasoning_effort', 'policy_sha256']},
                definition='For each grading pass, calculate category Average and Oracle@4 first. '
                           f'Then report the mean, minimum and maximum of those {repeats} category totals. '
                           'Combine Basic and Advanced within each pass before summarizing All.',
                categories=categories, consistency=results['overall'],
                metadata_disagreements=results['metadata_disagreements'],
                retries_within_accepted_calls=results['retries_within_accepted_calls'])


def points(value):
    return f'{value:.2f}'.rstrip('0').rstrip('.')


def metric(value, maximum, percentage):
    fraction = f'{points(value)}/{maximum}'
    return f'{100 * value / maximum:.2f}% ({fraction})' if percentage else fraction


def render(data):
    lines = ['# Strict-v2 category matrices: mean, lowest and highest', '',
             f"Evaluator: `{data['model']}` / `{data['reasoning_effort']}`. {data['repeats']} independent grading passes.", '',
             f"Policy SHA-256: `{data['policy_sha256']}`.", '',
             data['definition'], '',
             'Both raw configurations enable native thinking with a 65,536-token initial output limit. '
             'Raw without extended reasoning is a single pass that stops at EOS; '
             'raw with extended reasoning adds forced continuation after the initial answer.', '',
             'Within each pass, Average gives each problem equal weight by averaging its available candidates; '
             'Oracle@4 selects its highest-scoring candidate. Portfolio totals sum these per-problem scores. '
             'Extrema for different metrics or categories may occur in different passes. '
             'These are observed grading extremes, not confidence intervals.', '',
             'IMO-ProofBench percentages are acquired points divided by maximum points. '
             'These strict-v2 scores are distinct from the published IMOBench B.5 scale. '
             'The ablation comparison is retrospective; supplementary cases and tool experiments remain separate.', '',
             '[Consistency and underlying grades](REPORT.md) · [Category CSV](MATRICES.csv) · '
             '[Structured matrices, including each pass\'s category totals](matrices.json)', '']
    lookup = {(c['benchmark'], c['cohort']): c for c in data['categories']}
    for method in METHODS:
        lines += [f"## {method.title()} category result across {data['repeats']} passes", '', '### IMO-ProofBench', '',
                  '| Setting | Category | Average | Oracle@4 |', '|---|---|---:|---:|']
        for setting, label in SETTINGS.items():
            for benchmark in ['imo-proofbench/basic', 'imo-proofbench/advanced', 'imo-proofbench/all']:
                c = lookup.get((benchmark, setting))
                if c:
                    s = c['summaries'][method]
                    cells = [metric(s[k], c['maximum_points'], True) for k in ['average_points', 'oracle_at_4_points']]
                    lines.append(f"| {label} | {LABELS[benchmark]} ({c['problems']}) | {' | '.join(cells)} |")
        lines += ['', '### IMO 2026', '', '| Setting | Average | Oracle@4 |', '|---|---:|---:|']
        for setting, label in SETTINGS.items():
            c = lookup.get(('imo2026', setting))
            if c:
                s = c['summaries'][method]
                cells = [metric(s[k], c['maximum_points'], False) for k in ['average_points', 'oracle_at_4_points']]
                lines.append(f"| {label} | {' | '.join(cells)} |")
        lines += ['', '### Experimental tool calls: tested examples only', '',
                  '| Category | Problems | Average before → after | Oracle@4 before → after |', '|---|---:|---:|---:|']
        for benchmark in ['imo-proofbench/basic', 'imo-proofbench/advanced', 'imo2026']:
            before, after = [lookup.get((benchmark, setting)) for setting in ['tool_input', 'tool_rewrite']]
            if before and after:
                cells = [f"{points(before['summaries'][method][k])} → {points(after['summaries'][method][k])} / {before['maximum_points']}"
                         for k in ['average_points', 'oracle_at_4_points']]
                lines.append(f"| {LABELS[benchmark]} | {before['problems']} | {' | '.join(cells)} |")
        lines += ['', '### Supplementary categories', '',
                  '| Category | Case | Problems | Average | Oracle@4 |', '|---|---|---:|---:|---:|']
        for c in data['categories']:
            if c['cohort'] not in {*SETTINGS, 'tool_input', 'tool_rewrite'}:
                label = {'raw_no_bf_previous_seeds': 'Earlier seeds without extended reasoning',
                         'previous_scored_fallback': 'Earlier scored fallback proofs'}.get(c['cohort'], c['cohort'])
                s = c['summaries'][method]
                cells = [metric(s[k], c['maximum_points'], False) for k in ['average_points', 'oracle_at_4_points']]
                lines.append(f"| {LABELS[c['benchmark']]} | {label} | {c['problems']} | {' | '.join(cells)} |")
        lines.append('')
    c = data['consistency']
    lines += ['## Grading consistency', '',
              '| Complete proofs | Grade agreement | Pairwise agreement | Within one point | Mean range | Mean SD |',
              '|---:|---:|---:|---:|---:|---:|',
              f"| {c['proofs']} | {100*c['exact_agreement']:.2f}% | {100*c['pairwise_agreement']:.2f}% | "
              f"{100*c['within_one_point']:.2f}% | {c['mean_range']:.3f} | {c['mean_population_sd']:.3f} |", '',
              f"Score/metadata disagreements retained: {data['metadata_disagreements']}. "
              f"Retries within accepted calls: {data['retries_within_accepted_calls']}.", '',
              'This measures v2 repeatability, not improvement over v1, which was not repeated in this study.', '']
    return '\n'.join(lines)


def load_manifest(directory):
    manifest = json.loads((directory/'manifest.json').read_text())
    amendment = directory/'two_grade_plan.json'
    if amendment.exists():
        plan = json.loads(amendment.read_text())
        if (plan['original_manifest_sha256'] != hashlib.sha256((directory/'manifest.json').read_bytes()).hexdigest()
                or plan['repeats'] != 2 or plan['selected_repetitions'] != [1, 2]
                or plan['planned_grades'] != 2 * manifest['unique_proofs']):
            raise ValueError('Invalid two-grade protocol amendment')
        manifest.update(repeats=2, planned_grades=plan['planned_grades'])
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--study', type=Path, required=True)
    args = parser.parse_args()
    directory = args.study.resolve()
    manifest = load_manifest(directory)
    results = json.loads((directory/'results.json').read_text())
    data = build_matrices(manifest, results)
    (directory/'matrices.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    (directory/'MATRICES.md').write_text(render(data))
    with (directory/'MATRICES.csv').open('w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['benchmark', 'cohort', 'problems', 'summary', 'average_points', 'oracle_at_4_points', 'maximum_points'])
        for c in data['categories']:
            for method, s in c['summaries'].items():
                writer.writerow([c['benchmark'], c['cohort'], c['problems'], method,
                                 s['average_points'], s['oracle_at_4_points'], c['maximum_points']])
    print('Created category summaries: MATRICES.md, matrices.json and MATRICES.csv')


if __name__ == '__main__':
    main()
