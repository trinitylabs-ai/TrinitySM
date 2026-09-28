"""Active two-grade study and pass-first measurement regressions without model calls."""
import importlib
from pathlib import Path

import pytest


@pytest.fixture
def study(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'scripts'))
    return importlib.import_module('run_v2_pairs')


def test_agreement_counts_one_pair_per_proof_and_population_sd(study):
    result=study.consistency([[7,7],[3,4],[1,5]])
    assert result['proofs']==3
    assert result['exact_agreement']==pytest.approx(1/3)
    assert result['pairwise_agreement']==pytest.approx(1/3)
    assert result['within_one_point']==pytest.approx(2/3)
    assert result['mean_range']==pytest.approx(5/3)
    assert result['mean_population_sd']==pytest.approx(5/6)
    assert result['crosses_three_four_boundary']==2
    assert result['crosses_six_threshold']==0


def test_incomplete_pair_is_not_zero_filled(study):
    assert study.consistency([])=={'proofs':0}
    with pytest.raises(AssertionError):study.consistency([[7]])
    with pytest.raises(AssertionError):study.consistency([[7,7,7,7]])


def test_semantic_metadata_disagreement_is_retained(study):
    runner=study.prepare_study_runner()
    grade=dict(score=4,verdict='pass',answer_supported=True,dependency_impact='load_bearing',
               repair_complexity='new_idea',olympiad_treatment='full_credit',first_issue='Central gap.',
               summary='Contradictory metadata.',strengths=[],errors=[])
    result=runner.validate_grade(grade)
    assert result['score']==4 and result['contract_consistent'] is False
    with pytest.raises(ValueError):runner.validate_grade({'score':4})


def test_category_metrics_are_computed_within_each_of_two_passes(study,tmp_path):
    matrices=importlib.import_module('report_v2_matrices')
    units=[dict(unit_id=x,problem_id='p1',benchmark='imo2026') for x in ['a','b']]
    manifest=dict(units=units,run_id='test_only',unique_proofs=2,planned_grades=4,repeats=2,
                  policy_sha256=study.original.POLICY_SHA256,
                  model='gpt-5.6-sol',reasoning_effort='xhigh',
                  observations=[dict(**u,cohort='full_harness',candidate=u['unit_id']) for u in units])
    found={(u['unit_id'],i+1):dict(grade=dict(score=score,contract_consistent=True))
           for u,scores in zip(units,[[7,0],[3,3]]) for i,score in enumerate(scores)}
    result=study.publish(manifest,tmp_path,found)
    cohort=matrices.build_matrices(manifest,result)['categories'][0]
    assert cohort['repeat_oracle_at_4_points']==[7,3]
    assert cohort['summaries']['mean']=={'oracle_at_4_points':5,'average_points':3.25}
    found.pop(('a',2));result=study.publish(manifest,tmp_path,found)
    assert result['completed_pairs']==1
    with pytest.raises(ValueError,match='All grading must finish'):
        matrices.build_matrices(manifest,result)


def test_effective_inventory_has_two_calls_per_unique_input(study):
    directory=study.ROOT/'benchmarks/reports/strict_v2_consistency_20260918T064715Z'
    manifest=study.load_plan(directory)
    assert manifest['unique_proofs']==749
    assert manifest['repeats']==2
    assert manifest['planned_grades']==1498
    assert manifest['previous_grades_reused'] is False
    assert manifest['cohort_counts']['raw_no_bf']==264
    assert manifest['cohort_counts']['raw_bf']==263
    assert manifest['cohort_counts']['full_harness']==263
    assert len(manifest['newly_included_finals'])==6
    assert len({u['unit_id'] for u in manifest['units']})==749
