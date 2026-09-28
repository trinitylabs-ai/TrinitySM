"""Published final scores and selections must remain bound to their evidence."""
import copy
import importlib.util
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import report_qwen_selection as qwen
spec = importlib.util.spec_from_file_location('proofbench_final_publication', ROOT / 'scripts/export_proofbench_final.py')
publication = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publication)


def test_final_scores_votes_and_readme():
    d = publication.verify(publication.BUNDLE)
    assert d['completed_judgments'] == 474
    assert len(d['problems']) == 60
    group = d['groups']['Combined']
    assert group['available_lanes'] == 237 and group['missing_lanes'] == 3
    assert group['average_score_sum'] == 246.5
    assert group['oracle_at_4_score_sum'] == 283.5
    assert group['selected_score_sum'] == 276.5
    assert group['score_denominator'] == group['selected_score_denominator'] == 420
    assert d['comparison']['groups']['Combined']['average_score_sum'] == 250.5
    assert d['selection_accuracy']['best_or_tied'] == 50
    assert d['selection_accuracy']['selected_low_over_high'] == []
    assert d['generation_timing'] == publication.generation_timing_annotation()
    assert not d['generation_timing']['comparable_across_problems']
    assert not d['generation_timing']['usable_as_compute_time']
    assert d['recovery_verification'] == publication.recovery_verification()
    assert all('repair_script_sha256' not in (vote['mechanical_recovery'] or {})
               for problem in d['problems'] for vote in problem['selection']['votes'])
    assert sum(len(p['selection']['votes']) for p in d['problems']) == 1404
    partial = next(p for p in d['problems'] if p['problem_id'] == 'PB-Basic-026')
    assert partial['average'] == 1/3
    assert sum(r['available'] for r in partial['lanes']) == 3
    readme = (ROOT / 'README.md').read_text()
    block = readme.split('<!-- BEGIN FINAL PROOFBENCH RESULTS -->\n')[1].split('\n<!-- END FINAL PROOFBENCH RESULTS -->')[0]
    assert block == qwen.proofbench_section(qwen.build())
    assert (publication.BUNDLE / 'README.md').read_text() == publication.markdown(d)


def test_compact_readme_computes_changed_metrics_and_selection_outcomes():
    problems = []
    for pid, values, selected in [('PB-Basic-001', [7, 1, None, 0], 1),
                                  ('PB-Advanced-001', [6, 6, 6, 6], 6)]:
        lanes = [dict(available=value is not None, mean=value, scores=[value, value])
                 for value in values]
        problems.append(dict(problem_id=pid, lanes=lanes, selected_mean=selected,
            selected_candidate='test_selected', oracle_at_4=max(v for v in values if v is not None)))
    d = dict(groups=publication.summaries(problems),
             selection_accuracy=publication.selection_accuracy(problems))
    block = publication.readme_section(d)
    assert '| Basic | 1 | 3/4 | 38.10% | 14.29% | 100.00% |' in block
    assert '| Advanced | 1 | 4/4 | 85.71% | 85.71% | 85.71% |' in block
    assert '| Combined | 2 | 7/8 | 61.90% | 50.00% | 92.86% |' in block
    assert 'One proof is missing and is left out of the averages.' in block
    assert 'on 1 of 2 problems, and chose a\n0–1 proof when a 6–7 proof was available on 1 problem.' in block
    assert 'never chose' not in block


def test_portable_recovery_drops_only_unpublished_script_pin_without_mutating_source():
    receipt = dict(policy='missing-checks-heading-existing-inline-line-citations-v2',
                   winner_label='B', repair_script_sha256='0' * 64, original_response_sha256='1' * 64)
    exported = publication.portable_recovery(receipt)
    assert exported == {key: value for key, value in receipt.items() if key != 'repair_script_sha256'}
    assert receipt['repair_script_sha256'] == '0' * 64


@pytest.mark.parametrize('mutation', ['score', 'winner', 'coverage', 'aggregate', 'response_hash', 'missing_as_zero', 'missing_problem_dropped', 'vote_order', 'previous_denominator', 'normalization', 'timing_as_compute', 'timing_annotation_missing', 'repair_script_pin', 'repair_receipt_hash', 'replay_metadata_missing'])
def test_corrupted_snapshot_rejected(monkeypatch, mutation):
    read = publication.read
    d = copy.deepcopy(read(publication.BUNDLE / 'SCORECARD.json'))
    p = d['problems'][0]
    if mutation == 'score': p['lanes'][0]['scores'][0] = -1
    elif mutation == 'winner': p['selected_candidate'] = 'missing_candidate'
    elif mutation == 'coverage': d['completed_judgments'] += 1
    elif mutation == 'aggregate': d['groups']['Combined']['selected_score_sum'] += 1
    elif mutation == 'response_hash': p['selection']['votes'][0]['response_sha256'] = '0'*64
    elif mutation == 'missing_as_zero':
        partial = next(p for p in d['problems'] if p['problem_id'] == 'PB-Basic-026')
        partial['average'] = 0.25
    elif mutation == 'missing_problem_dropped':
        d['problems'] = [p for p in d['problems'] if p['problem_id'] != 'PB-Basic-026']
    elif mutation == 'vote_order': p['selection']['seed_derived_candidate_order'].reverse()
    elif mutation == 'previous_denominator': d['comparison']['groups']['Combined']['score_denominator'] -= 7
    elif mutation == 'timing_as_compute': d['generation_timing']['usable_as_compute_time'] = True
    elif mutation == 'timing_annotation_missing': d.pop('generation_timing')
    elif mutation == 'replay_metadata_missing': d.pop('recovery_verification')
    elif mutation in ('repair_script_pin', 'repair_receipt_hash'):
        p = next(p for p in d['problems'] if p['problem_id'] == 'PB-Advanced-003')
        repair = next(v['mechanical_recovery'] for v in p['selection']['votes'] if v['mechanical_recovery'])
        repair['repair_script_sha256' if mutation == 'repair_script_pin' else 'copied_evidence_sha256'] = '0' * 64
    else:
        p = next(p for p in d['problems'] if p['problem_id'] == 'PB-Basic-016')
        v = next(v for v in p['selection']['votes'] if v['mechanical_recovery'])
        v['normalized_response'] = v['response']
    monkeypatch.setattr(publication, 'read', lambda path: d if Path(path).name == 'SCORECARD.json' else read(path))
    with pytest.raises(AssertionError):
        publication.verify(publication.BUNDLE)
