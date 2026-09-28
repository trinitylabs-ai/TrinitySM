"""Evaluator policy/contract and isolation regressions; no model calls."""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("score_v2", ROOT / "scripts/score_imo_v2.py")
v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v2)


def test_rule_c_preserves_actual_routine_repair_complexity():
    runner = v2.prepare_runner()
    value = dict(score=5, verdict="substantial_gap", answer_supported=True,
                 dependency_impact="load_bearing", repair_complexity="routine_direct",
                 olympiad_treatment="partial_credit", first_issue="False local step.",
                 summary="Rule C applies.", strengths=["Correct reduction."],
                 errors=[dict(severity="substantial", description="False local step.")])
    result = runner.validate_grade(value)
    assert result["contract_consistent"] and result["repair_complexity"] == "routine_direct"
    value["score"] = 7
    with pytest.raises(ValueError, match="Inconsistent"):
        runner.validate_grade(value)


def test_prompt_is_only_policy_and_mathematical_inputs():
    runner = v2.prepare_runner()
    prompt = runner.grading_prompt(problem="STATEMENT_ONLY", reference="REFERENCE_ONLY",
                                   proof="SUBMISSION_ONLY", grading_policy=runner.STRICT_POLICY)
    assert all(prompt.count(x) == 1 for x in ["STATEMENT_ONLY", "REFERENCE_ONLY", "SUBMISSION_ONLY"])
    assert "Rule A" in prompt and "Rule F" in prompt
    assert "candidate_id" not in prompt and "previous_score" not in prompt
    # Solver prompts and the original grading policy retain their frozen identity.
    old = (ROOT / "docs/public_release/grading/strict_olympiad_policy.txt").read_text().strip()
    assert v2.hashlib.sha256(old.encode()).hexdigest() == "1a8c5d02a7bd84a53ad011cf889ceaaca7ff94166536565bda49082649781ecf"


def test_rule_c_carve_out_allows_recorded_cosmetic_issue_at_seven():
    runner = v2.prepare_runner()
    value = dict(score=7, verdict="pass", answer_supported=True,
                 dependency_impact="none", repair_complexity="none",
                 olympiad_treatment="full_credit", first_issue="No decisive defect.",
                 summary="The needed fact is independently established in the proof.",
                 strengths=["Complete argument."],
                 errors=[dict(severity="cosmetic", description="Dispensable inline remark.")])
    assert runner.validate_grade(value)['full_credit']
    value['errors'][0]['severity'] = 'major'
    with pytest.raises(ValueError, match="Inconsistent"):
        runner.validate_grade(value)


def trace(*kinds):
    return "\n".join(json.dumps(x) for x in [
        *[{"type": "item.completed", "item": {"type": k}} for k in kinds],
        {"type": "turn.completed"}])


def test_trace_rejects_tools_and_incomplete_turns():
    assert v2.validate_trace(trace("reasoning", "agent_message"))["tool_calls"] == 0
    for bad in [trace("command_execution", "agent_message"),
                trace("mcp_tool_call", "agent_message"), trace("reasoning"),
                trace("agent_message") + '\n{"type":"turn.completed"}']:
        with pytest.raises(ValueError, match="isolation"):
            v2.validate_trace(bad)


def test_hash_bound_manifest_rejects_substitution(tmp_path):
    runner = v2.prepare_runner()
    (tmp_path / "problem.json").write_text('{"claim":"A"}')
    (tmp_path / "reference.txt").write_text("B")
    (tmp_path / "proof.md").write_text("C")
    task = dict(problem_number=1, problem_id="p1", candidate_id="a",
                problem_path="problem.json", reference_path="reference.txt", proof_path="proof.md",
                expected_hashes={k + "_sha256": v2.hashlib.sha256(s.encode()).hexdigest()
                                 for k, s in zip(["problem", "reference", "proof"], "ABC")})
    manifest = tmp_path / "tasks.json"
    manifest.write_text(json.dumps(dict(schema="gold-informed-generic-proof-task-manifest-v1", tasks=[task])))
    assert len(runner.generic_proof_task_manifests([manifest])) == 1
    (tmp_path / "proof.md").write_text("CHANGED")
    with pytest.raises(ValueError, match="hash drift"):
        runner.generic_proof_task_manifests([manifest])


def test_response_recovery_selects_first_valid_grade_not_highest(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'scripts'))
    import report_strict_v2 as report
    six = dict(score=6, verdict='minor_gap', answer_supported=True,
               dependency_impact='local', repair_complexity='routine_direct',
               olympiad_treatment='minor_deduction', first_issue='A minor omission.',
               summary='One local omission.', strengths=['Correct central argument.'],
               errors=[dict(severity='minor', description='Minor omission.')])
    seven = {**six, 'score': 7, 'verdict': 'pass', 'dependency_impact': 'none',
             'repair_complexity': 'none', 'olympiad_treatment': 'full_credit', 'errors': []}
    path = tmp_path / 'trace.jsonl'
    events = []
    for attempt, grade in enumerate([six, seven], 1):
        events += [dict(attempt=attempt, returncode=0),
                   dict(type='item.completed', item=dict(type='agent_message', text=json.dumps(grade))),
                   dict(type='turn.completed')]
    path.write_text('\n'.join(map(json.dumps, events)))
    grade, selection = report.first_valid_response(path, v2.prepare_runner())
    assert grade['score'] == 6 and selection['selected_attempt'] == 1
    assert selection['unselected_later_attempts'] == 1
