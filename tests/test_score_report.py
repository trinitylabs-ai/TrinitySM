"""Offline regression checks for fallback selection and benchmark arithmetic."""
import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "workshop_score_report", ROOT / "docs/public_release/verify_scores.py")
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)


@pytest.mark.parametrize("checkpoint", report.CHECKPOINT_PRIORITY)
def test_fallback_uses_latest_graded_checkpoint_even_when_score_is_zero(checkpoint):
    candidates = {name: {"scored": False} for name in report.CHECKPOINT_PRIORITY}
    candidates[checkpoint] = {"scored": True, "score": 0}
    for name in report.CHECKPOINT_PRIORITY[report.CHECKPOINT_PRIORITY.index(checkpoint) + 1:]:
        candidates[name] = {"scored": True, "score": 7}
    assert report.first_scored_checkpoint(candidates) == checkpoint


def test_missing_grades_do_not_become_zero_score_selections():
    assert report.first_scored_checkpoint({"raw": {"scored": False}}) is None


def test_completed_final_proof_cannot_fall_back_to_an_earlier_grade(monkeypatch):
    original = report.read
    def changed(name):
        value = original(name)
        if str(name) == "score_snapshot.json":
            row = next(r for r in value['lanes'] if r.get('c3_generation_state') == 'completed')
            row['baseline']['checkpoint'] = 'R1-C2'
        return value
    monkeypatch.setattr(report, "read", changed)
    with pytest.raises(AssertionError, match="Completed Refinement 3 requires"):
        report.main()


def test_final_refinement_binding_rejects_a_different_proof(monkeypatch):
    original = report.read
    def changed(name):
        value = original(name)
        if str(name) == "score_snapshot.json":
            row = next(r for r in value['lanes'] if 'final_refinement_provenance' in r)
            row['final_refinement_provenance']['proof_sha256'] = '0' * 64
        return value
    monkeypatch.setattr(report, "read", changed)
    with pytest.raises(AssertionError, match="Final proof binding mismatch"):
        report.main()


def row(problem, score):
    result = {"problem_id": problem, "benchmark": "Advanced", "included": score is not None}
    if score is not None:
        result.update(baseline={"score": score}, with_tools={"score": 7})
    return result


def test_problem_weighting_with_one_missing_lane_and_separate_tool_scores():
    rows = [row("a", score) for score in (7, 7, 7, None)]
    rows += [row("b", score) for score in (0, 0, 0, 0)]
    summary = report.compute(rows, "Advanced")
    assert summary["scored_lanes"] == 7
    assert summary["maximum_points"] == 14
    assert summary["before_average_points"] == 7
    assert summary["before_average_percent"] == 50
    assert summary["before_best_points"] == 7
    assert summary["including_tools_average_percent"] == 100
    table = report.table([summary])
    assert "50.00% (7/14)" in table
    assert "100.00%" not in table
    assert "Scored lanes" not in table
    tool_table = report.table([summary], mode="with_tools")
    assert "100.00% (14/14)" in tool_table
    assert "50.00%" not in tool_table
    comparison = report.table([summary], mode="comparison")
    assert "| Set | Grading scheme | Average | Oracle@4 |" in comparison
    assert "50.00% (7/14) → 100.00% (14/14) | 50.00% (7/14) → 100.00% (14/14)" in comparison


def test_problem_without_any_grade_cannot_silently_disappear_from_denominator():
    with pytest.raises(AssertionError, match="no eligible grade"):
        report.compute([row("a", 7), row("b", None)], "Advanced")


def test_ablation_rejects_a_grade_with_a_different_evaluation_identity(monkeypatch):
    original = report.read
    def changed(name):
        value = original(name)
        if str(name).startswith("evidence/grades/"):
            value["reference_sha256"] = "0" * 64
        return value
    monkeypatch.setattr(report, "read", changed)
    with pytest.raises(AssertionError, match="grading identity mismatch"):
        report.verify_ablation(report.read("score_snapshot.json"))


def test_ablation_rejects_changed_submitted_proofs(monkeypatch):
    original = report.sha
    monkeypatch.setattr(report, "sha", lambda path: "0" * 64
                        if "raw_no_bf/proofs/" in path.as_posix() else original(path))
    with pytest.raises(AssertionError, match="artifact hash mismatch"):
        report.verify_ablation(report.read("score_snapshot.json"))


def test_saved_evidence_and_all_published_matrices(capsys):
    report.main()
    output = capsys.readouterr().out
    assert "263 scored selections" in output
    assert "240 raw ablation grades" in output
    assert "62.14% (130.5/210) | 73.33% (154/210)" in output
    assert "23.69% (49.75/210) | 30.95% (65/210)" in output
    assert "25.36% (53.25/210) | 38.57% (81/210)" in output
    assert "67.86% (142.5/210) | 80.95% (170/210)" in output
    assert "| Extended reasoning + full harness | IMOBench B.5 | 80.00% (168/210) | 84.76% (178/210)" in output
    assert "80.00% (168/210)" in output
    assert "39.29% (82.5/210)" in output
    assert "59.64% (250.5/420)" in output
    assert "48.10% (101/210)" in output
    assert "66.43% (279/420)" in output
    for problem in range(1, 7):
        assert f"| P{problem} | Strict v2 (pass 1) |" in output
    imo = output.split("\nIMO 2026\n", 1)[1].split(
        "\nIMO-ProofBench tool examples (actual input → rewrite)\n", 1)[0]
    assert "| P1 | Strict v2 (pass 1) | 7/7 | 7/7 |" in imo
    assert "| P3 | Strict v2 (pass 1) | 1.75/7 | 2/7 |" in imo
    assert "| IMO 2026 (6) | Strict v2 (pass 1) | 24/42 | 29/42 |" in imo
    assert "Other pass (**pass 2**): **24.50/42 Average, 29/42 Oracle@4**" in imo
    assert "%" not in imo
    assert "| Basic-008 (t10_r01) | real_root_classification | 1/7 → 6/7 | +5 |" in output
    assert "| Basic-009 (t07_r01) | uniform_partition_count | 1/7 → 7/7 | +6 |" in output
    assert "Advanced-009" not in output
    assert "| Advanced-020 (t10_r02) | symbolic_modular_order | 0/7 → 0/7 | +0 |" in output
    imo_tools = output.split("\nIMO 2026 tool examples (actual input → rewrite)\n", 1)[1]
    assert "| P2 (t07_r02) | exact_geometry | 3/7 → 5/7 | +2 |" in imo_tools
    assert "%" not in imo_tools
    assert "P1" not in imo_tools and "Average" not in imo_tools
    assert "Scored lanes" not in output
    assert "| Raw without extended reasoning | Strict v2 (pass 1) | 18.75/42 | 21/42 |" in output
    assert "| Raw with extended reasoning | Strict v2 (pass 1) | 19/42 | 21/42 |" in output
    assert "| Extended reasoning + full harness | Strict v2 (pass 1) | 24/42 | 29/42 |" in output


def test_lower_pass_tie_selects_first_pass_for_every_problem():
    rows = [dict(problem_id=pid, benchmark='IMO 2026', included=True,
                 baseline={'scores': scores}, with_tools={'scores': scores})
            for pid, scores in [('imo2026_p1', [7, 0]), ('imo2026_p2', [0, 7])]]
    total = report.compute_v2_lower_pass(rows, 'IMO 2026')
    assert total['selected_repeat'] == 1
    assert total['before_average_points'] == total['before_best_points'] == 7
    assert [report.compute_v2_lower_pass(rows, pid)['before_average_points']
            for pid in ['imo2026_p1', 'imo2026_p2']] == [7, 0]
    rows[1]['baseline']['scores'] = [0]
    with pytest.raises(AssertionError):
        report.compute_v2_lower_pass(rows, 'IMO 2026')


@pytest.mark.parametrize('lower_repeat', [1, 2])
def test_lower_average_pass_keeps_its_oracle_and_problem_values(lower_repeat):
    samples = [('imo2026_p1', values) for values in ([0, 4], [0, 4], [0, 4], [7, 4])]
    samples.append(('imo2026_p2', [2, 0]))
    rows = []
    for pid, scores in samples:
        if lower_repeat == 2:
            scores = scores[::-1]
        rows.append(dict(problem_id=pid, benchmark='IMO 2026', included=True,
                         baseline={'scores': scores}, with_tools={'scores': scores}))
    total = report.compute_v2_lower_pass(rows, 'IMO 2026')
    assert total['selected_repeat'] == lower_repeat
    assert total['before_average_points'] == 3.75
    # The other pass has a lower Oracle total (4), but must not supply this cell.
    assert total['before_best_points'] == 9
    problems = [report.compute_v2_lower_pass(rows, pid) for pid in ['imo2026_p1', 'imo2026_p2']]
    assert problems[1]['before_average_points'] == 2  # Other pass gives zero.
    for key in ['before_average_points', 'before_best_points',
                'including_tools_average_points', 'including_tools_best_points']:
        assert sum(problem[key] for problem in problems) == total[key]


def test_v2_reporting_rejects_reordered_grading_passes(monkeypatch):
    original = report.read
    def changed(name):
        value = original(name)
        if str(name).startswith('evidence/v2_grades/'):
            value['repeat'] = 3 - value['repeat']
        return value
    monkeypatch.setattr(report, 'read', changed)
    with pytest.raises(AssertionError, match='repetition mismatch'):
        report.verify_imo_v2(report.read('score_snapshot.json'))


def test_v2_reporting_rejects_changed_reference_identity(monkeypatch):
    original = report.read
    def changed(name):
        value = original(name)
        if str(name).startswith('evidence/v2_grades/'):
            value['reference_sha256'] = '0' * 64
        return value
    monkeypatch.setattr(report, 'read', changed)
    with pytest.raises(AssertionError, match='reference_sha256 mismatch'):
        report.verify_imo_v2(report.read('score_snapshot.json'))


def test_proofbench_reporting_stays_b5_and_v2_results_are_removed():
    snapshot = report.read('score_snapshot.json')
    for old, current in zip(snapshot['historical_single_grade_summary'][:3], snapshot['summary'][:3]):
        assert old == current
    assert snapshot['grading_schemes']['strict-v2']['benchmarks'] == ['IMO 2026']
    for subset in ('basic', 'advanced'):
        base = ROOT / f'benchmarks/imo-proofbench/{subset}/results/strict_v2_consistency_20260918T064715Z'
        assert not (base / 'grades').exists()
        assert not (base / 'grading/work').exists()
        assert (base / 'proofs').is_dir()
    results = report.json.loads((ROOT / 'benchmarks/reports/strict_v2_consistency_20260918T064715Z/results.json').read_text())
    assert results['scope'] == 'imo2026_only'
    assert all(row['problem_id'].startswith('imo2026_p') for row in results['rows'])


def test_proofbench_ablation_rejects_strict_v2_grades(monkeypatch):
    original = report.read
    def changed(name):
        value = original(name)
        if str(name).startswith('evidence/b5_grades/'):
            value['policy_mode'] = 'strict-v2'
        return value
    monkeypatch.setattr(report, 'read', changed)
    with pytest.raises(AssertionError, match='requires B.5'):
        report.verify_proofbench_ablation(report.read('score_snapshot.json'))


def test_basic_no_bf_replacements_must_match_the_bf_request_seeds(monkeypatch):
    original = report.read
    def changed(name):
        value = original(name)
        if str(name) == 'proofbench_no_bf_generation.json':
            row = next(r for r in value['records'] if r['problem_id'] == 'PB-Basic-009')
            row['request']['seed'] += 1
        return value
    monkeypatch.setattr(report, 'read', changed)
    with pytest.raises(AssertionError, match='request seed mismatch'):
        report.verify_proofbench_ablation(report.read('score_snapshot.json'))


def test_tool_comparison_rejects_substituting_the_later_core_input(monkeypatch):
    original = report.json.loads
    def changed(text, **kwargs):
        data = original(text, **kwargs)
        if isinstance(data, dict) and data.get("schema") == "workshop-tools-submitted-proof-comparison-v1":
            row = next(r for r in data["records"] if r["problem_id"] == "PB-Basic-008")
            row["input"] = dict(row["rewrite"])
        return data
    monkeypatch.setattr(report.json, "loads", changed)
    with pytest.raises(AssertionError, match="input/rewrite binding mismatch"):
        report.verify_tool_examples(report.read("score_snapshot.json"))
