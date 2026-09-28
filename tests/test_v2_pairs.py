"""Retain original grades 1 and 2; exclude discarded grades even during recovery."""
import importlib
import json
from pathlib import Path

import pytest


@pytest.fixture
def pairs(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'scripts'))
    return importlib.import_module('run_v2_pairs')


def test_pair_agreement_and_population_sd(pairs):
    c = pairs.consistency([[7, 7], [3, 4], [1, 5]])
    assert c['exact_agreement'] == pytest.approx(1/3)
    assert c['pairwise_agreement'] == pytest.approx(1/3)
    assert c['within_one_point'] == pytest.approx(2/3)
    assert c['mean_range'] == pytest.approx(5/3)
    assert c['mean_population_sd'] == pytest.approx(5/6)
    with pytest.raises(AssertionError):
        pairs.consistency([[7]])


def test_select_original_first_two_without_reading_discarded_grades(pairs, monkeypatch, tmp_path):
    for i, score in enumerate([0, 1, 7, 7], 1):
        (tmp_path/f'g{i}.json').write_text(json.dumps({'score': score}))
    monkeypatch.setattr(pairs.original, 'grade_path', lambda study, unit, repeat: tmp_path/f'g{repeat}.json')
    checked = []
    monkeypatch.setattr(pairs.original, 'check_grade', lambda study, unit, repeat, value: checked.append(repeat))
    assert pairs.collect({'units': [{'unit_id': 'a'}]}) == {('a', 1): {'score': 0}, ('a', 2): {'score': 1}}
    assert checked == [1, 2]


def test_recovery_excludes_repetitions_three_and_four(pairs):
    bindings = [dict(unit_id='a', repeat=i, candidate_id=f'a_g{i}') for i in [1, 2, 3, 4]]
    assert pairs.retained_bindings(bindings) == bindings[:2]


def test_quota_detection_uses_error_events_not_proof_content(pairs, tmp_path):
    case = tmp_path/'p1/candidate'
    case.mkdir(parents=True)
    log = case/'codex.jsonl'
    log.write_text(json.dumps({'type': 'item.completed', 'message': "You've hit your usage limit."})+'\n')
    assert pairs.usage_limit_error(tmp_path) is None
    with log.open('a') as f:
        f.write(json.dumps({'type': 'turn.failed', 'error': {'message': "You've hit your usage limit. Try later."}})+'\n')
        f.write('{incomplete')
    assert 'usage limit' in pairs.usage_limit_error(tmp_path)


def test_two_pass_category_summaries_do_not_average_individual_extremes(pairs):
    matrices = importlib.import_module('report_v2_matrices')
    units = [dict(unit_id=x, problem_id='p1', benchmark='imo2026') for x in ['a', 'b']]
    meta = dict(model='test', reasoning_effort='xhigh', policy_sha256='test')
    manifest = dict(**meta, run_id='test', units=units, unique_proofs=2, planned_grades=4, repeats=2,
                    observations=[dict(**u, candidate=u['unit_id'], cohort='full_harness') for u in units])
    results = dict(**meta, state='completed', active_batch=None, updated_at='test', repeats=2,
                   completed_grades=4, completed_proofs=2,
                   rows=[dict(unit_id=u['unit_id'], problem_id='p1', scores=v)
                         for u, v in zip(units, [[7, 0], [3, 3]])],
                   overall=pairs.consistency([[7, 0], [3, 3]]), metadata_disagreements=0,
                   retries_within_accepted_calls=0)
    data = matrices.build_matrices(manifest, results)
    c = data['categories'][0]
    assert c['repeat_average_points'] == [5, 1.5]
    assert c['repeat_oracle_at_4_points'] == [7, 3]
    assert c['summaries']['mean'] == {'average_points': 3.25, 'oracle_at_4_points': 5}
    assert c['summaries']['lowest']['oracle_at_4_points'] == 3
    assert c['summaries']['highest']['oracle_at_4_points'] == 7
    text = matrices.render(data)
    assert '2 independent grading passes' in text and 'across 2 passes' in text
    assert 'four passes' not in text.lower()
