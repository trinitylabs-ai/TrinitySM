"""Ensure mean/min/max describe category totals, not individual proof reductions."""
import copy
import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location('matrices', Path(__file__).resolve().parents[1]/'scripts/report_v2_matrices.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def example():
    units = [dict(unit_id=x, problem_id=p, benchmark='imo2026')
             for x, p in [('a', 'p1'), ('b', 'p1'), ('c', 'p2')]]
    meta = dict(model='test', reasoning_effort='xhigh', policy_sha256='test')
    manifest = dict(**meta, run_id='test', units=units, unique_proofs=3, planned_grades=12,
                    observations=[dict(**u, candidate=u['unit_id'], cohort='full_harness') for u in units])
    results = dict(**meta, state='completed', active_batch=None, updated_at='test',
                   completed_grades=12, completed_quartets=3,
                   rows=[dict(unit_id=u['unit_id'], problem_id=u['problem_id'], scores=v)
                         for u, v in zip(units, [[7, 0, 0, 0], [3, 3, 3, 3], [6, 6, 6, 6]])],
                   overall={}, metadata_disagreements=0, retries_within_accepted_calls=0)
    return manifest, results


def test_summarize_category_metrics_after_each_pass_including_oracle_selection():
    manifest, results = example()
    c = module.build_matrices(manifest, results)['categories'][0]
    assert c['repeat_average_points'] == [11, 7.5, 7.5, 7.5]
    assert c['repeat_oracle_at_4_points'] == [13, 9, 9, 9]
    assert c['summaries']['mean'] == {'average_points': 8.375, 'oracle_at_4_points': 10}
    assert c['summaries']['lowest'] == {'average_points': 7.5, 'oracle_at_4_points': 9}
    assert c['summaries']['highest'] == {'average_points': 11, 'oracle_at_4_points': 13}
    assert c['maximum_points'] == 14


def test_combined_category_sums_within_pass_before_taking_extremes():
    manifest, results = example()
    for i, benchmark in enumerate(['imo-proofbench/basic', 'imo-proofbench/advanced', 'imo2026']):
        manifest['units'][i]['benchmark'] = benchmark
        manifest['observations'][i]['benchmark'] = benchmark
    results['rows'][0]['scores'] = [7, 0, 0, 0]
    results['rows'][1]['scores'] = [0, 7, 0, 0]
    c = next(c for c in module.build_matrices(manifest, results)['categories'] if c['benchmark']=='imo-proofbench/all')
    assert c['repeat_oracle_at_4_points'] == [7, 7, 0, 0]
    assert c['summaries']['highest']['oracle_at_4_points'] == 7  # Not 7+7 from different passes.


def test_incomplete_grades_never_become_final_matrices():
    manifest, results = example()
    for field, value in [('state', 'running'), ('completed_grades', 11), ('active_batch', 'batch')]:
        incomplete = copy.deepcopy(results)
        incomplete[field] = value
        with pytest.raises(ValueError):
            module.build_matrices(manifest, incomplete)
    results['rows'][0]['scores'][0] = None
    with pytest.raises(ValueError, match='four valid grades'):
        module.build_matrices(manifest, results)
