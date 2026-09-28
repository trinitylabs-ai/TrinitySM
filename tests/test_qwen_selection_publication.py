"""Recount archived votes without changing grade or missing-lane semantics."""
import copy
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import report_qwen_selection as publication


@pytest.fixture(scope='module')
def data():
    return publication.build()


def test_scores_coverage_and_published_outputs(data):
    assert {name: group['selected_score_sum'] for name, group in data['groups'].items()} == {
        'IMO': 29, 'Basic': 173, 'Advanced': 105, 'ProofBench': 278}
    assert data['groups']['ProofBench']['available_lanes'] == 237
    assert data['groups']['ProofBench']['missing_lanes'] == 3
    assert data['groups']['ProofBench']['best_or_tied'] == 52
    assert data['groups']['ProofBench']['average_score_sum'] == 246.5
    assert data['groups']['ProofBench']['oracle_at_4_score_sum'] == 283.5
    assert data['groups']['ProofBench']['worse_problems'] == 0
    assert sum(p['valid_votes'] for p in data['problems']) == 774
    assert sum(2 * p['available_lanes'] for p in data['problems']) == 522
    root = ROOT / publication.DESTINATION
    assert json.loads((root / 'SCORECARD.json').read_text()) == data
    assert (root / 'README.md').read_text() == publication.report(data)
    readme = (ROOT / 'README.md').read_text()
    assert publication.update_readme(readme, data) == readme
    assert '| Basic (30) | 78.13% | **82.38%** | 82.62% |' in readme
    assert '| Advanced (30) | 39.25% | **50.00%** | 52.38% |' in readme
    report = (ROOT / 'docs/public_release_report.md').read_text()
    assert publication.update_release_report(report, data) == report
    assert '**12 votes**' in report and '**R2/R3 audit still uses Gemma and Qwen**' in report
    assert '24-call' not in report


def test_seeded_ties_can_choose_a_lower_grade(data):
    problem = next(p for p in data['problems'] if p['problem_id'] == 'PB-Advanced-008')
    assert problem['selected_mean'] == 6.5 and problem['oracle_at_4'] == 7
    tied = [cid for cid in problem['seed_derived_candidate_order']
            if problem['votes_received'][cid] == max(problem['votes_received'].values())]
    assert len(tied) > 1 and problem['selected_candidate'] == tied[0]


@pytest.mark.parametrize('mutation', ['missing', 'duplicate', 'invalid'])
def test_missing_duplicate_or_invalid_qwen_vote_rejects_publication(mutation):
    relative, _ = publication.SOURCES['IMO']
    problem = json.loads((ROOT / relative / 'SCORECARD.json').read_text())['problems'][0]
    votes = [copy.deepcopy(v) for v in problem['votes'] if v['model_key'] == 'qwen']
    if mutation == 'missing':
        votes.pop()
    elif mutation == 'duplicate':
        votes[-1] = copy.deepcopy(votes[0])
    else:
        votes[0]['valid'] = False
    with pytest.raises(AssertionError):
        publication.select(problem['seed_derived_candidate_order'], votes)
