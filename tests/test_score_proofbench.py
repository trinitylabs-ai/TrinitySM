"""Frozen B.5 adapter regressions, using only local fixtures and a mock Codex."""
import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("score_proofbench", ROOT / "scripts/score_proofbench.py")
b5 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b5)


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


@pytest.fixture
def task(tmp_path):
    proof = tmp_path / "proof.md"
    proof.write_text("  SUBMITTED_PROOF\n", encoding="utf-8")
    manifest = tmp_path / "tasks.json"
    row = dict(problem_id="PB-Basic-029", candidate_id="t10_r01", proof_path="proof.md",
               expected_hashes=dict(proof_sha256=sha("SUBMITTED_PROOF")))
    manifest.write_text(json.dumps(dict(tasks=[row])))
    return manifest, row


@pytest.fixture
def local_runner(monkeypatch):
    runner = b5.prepare_runner()
    data = {"PB-Basic-029": dict(problem="OFFICIAL_PROBLEM", reference="OFFICIAL_SOLUTION",
                               guidelines="OFFICIAL_GUIDELINES")}

    def fixture_rows(path, expected_hash):
        # Explicit dataset mock: production's unmodified hash rejection is tested separately.
        assert expected_hash == b5.DATASET_SHA256
        return data, b5.DATASET_SHA256

    monkeypatch.setattr(runner, "dataset_rows", fixture_rows)
    monkeypatch.setattr(b5, "prepare_runner", lambda: runner)
    return runner


def arguments(task, output, *extra):
    return ["--task-manifest", str(task[0]), "--dataset", "fixture.csv",
            "--output-dir", str(output), *extra]


def test_frozen_prompt_and_portable_defaults():
    runner = b5.prepare_runner()
    template, source = runner.template_and_source()
    assert sha(template) == b5.ARCHIVE_HASHES["references/proof_autograder_prompt.txt"]
    assert source["dataset_sha256"] == b5.DATASET_SHA256
    assert runner.SKILL == b5.ARCHIVE
    args = b5.parser().parse_args(["--task-manifest", "tasks.json", "--dataset", "official.csv",
                                  "--output-dir", "grades"])
    assert (args.model, args.reasoning_effort) == ("gpt-5.6-sol", "xhigh")
    assert str(args.dataset) == "official.csv"
    assert runner.CATEGORIES == {0: "Incorrect", 1: "Partial", 6: "Almost", 7: "Correct"}


@pytest.mark.parametrize("relative", list(b5.ARCHIVE_HASHES))
def test_archive_drift_rejected_before_import(tmp_path, monkeypatch, relative):
    for name in b5.ARCHIVE_HASHES:
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((b5.ARCHIVE / name).read_bytes())
    (tmp_path / relative).write_bytes(b"CHANGED")
    monkeypatch.setattr(b5, "ARCHIVE", tmp_path)
    with pytest.raises(ValueError, match="Archived B.5 scorer changed"):
        b5.prepare_runner()


def test_unpinned_dataset_rejected(tmp_path):
    dataset = tmp_path / "fixture.csv"
    dataset.write_text("Problem ID,Problem,Solution,Grading guidelines\n")
    with pytest.raises(ValueError, match="Dataset hash mismatch"):
        b5.prepare_runner().dataset_rows(dataset, b5.DATASET_SHA256)


@pytest.mark.parametrize("score", [0, 1, 6, 7])
def test_allowed_score_contract(score):
    assert b5.prepare_runner().parse_grade(f"Assessment. <points>{score} out of 7</points>")["score"] == score


@pytest.mark.parametrize("text", ["<points>2 out of 7</points>", "<points>3 out of 7</points>",
                                  "<points>4 out of 7</points>", "<points>5 out of 7</points>",
                                  "<points>7 out of 7</points><points>0 out of 7</points>"])
def test_other_scores_and_ambiguous_response_rejected(text):
    with pytest.raises(ValueError, match="exactly one"):
        b5.prepare_runner().parse_grade(text)


def test_duplicate_tasks_across_manifests_rejected(task, tmp_path):
    second = tmp_path / "second.json"
    second.write_text(task[0].read_text())
    with pytest.raises(ValueError, match="Duplicate explicit task"):
        b5.validate_manifests([task[0], second])


def test_hash_required_and_conflicting_hash_rejected(task):
    manifest, row = task
    row["proof_sha256"] = sha("OTHER")
    manifest.write_text(json.dumps(dict(tasks=[row])))
    with pytest.raises(ValueError, match="Conflicting proof_sha256"):
        b5.validate_manifests([manifest])
    del row["proof_sha256"]
    del row["expected_hashes"]
    manifest.write_text(json.dumps(dict(tasks=[row])))
    with pytest.raises(ValueError, match="requires proof_sha256"):
        b5.validate_manifests([manifest])


def test_changed_proof_fails_before_output_or_model(task, local_runner, tmp_path):
    (tmp_path / "proof.md").write_text("CHANGED")
    output = tmp_path / "grading"
    with pytest.raises(SystemExit) as error:
        b5.main(arguments(task, output, "--dry-run"))
    assert error.value.code == 1
    assert not output.exists()


def test_archived_dry_run_output_contract(task, local_runner, tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Dry run attempted a model call")

    monkeypatch.setattr(local_runner, "execute_model", forbidden)
    output = tmp_path / "grading"
    assert b5.main(arguments(task, output, "--dry-run")) == 0
    summary = json.loads((output / "summary.json").read_text())
    manifest = json.loads((output / "manifest.json").read_text())
    row = summary["rows"][0]
    assert summary["state"] == "dry_run" and summary["total"] == 1
    assert row["state"] == "pending"
    assert row["proof_sha256"] == sha("SUBMITTED_PROOF")
    assert row["result_path"] == str(output / "cases/PB-Basic-029/t10_r01/result.json")
    assert manifest["runner_sha256"] == b5.ARCHIVE_HASHES["scripts/score.py"]
    assert manifest["dataset_sha256"] == b5.DATASET_SHA256
    assert not manifest["pipeline_reviews_supplied"] and not manifest["prior_grades_supplied"]
    prompt = (output / "cases/PB-Basic-029/t10_r01/prompt.txt").read_text()
    expected_task = dict(problem="OFFICIAL_PROBLEM", reference="OFFICIAL_SOLUTION",
                         guidelines="OFFICIAL_GUIDELINES", proof="SUBMITTED_PROOF")
    assert prompt == local_runner.make_prompt(local_runner.template_and_source()[0], expected_task)
    assert all(prompt.count(text) == 1 for text in expected_task.values())
    assert "t10_r01" not in prompt and "proof_sha256" not in prompt
    assert (output / "status.json").is_file() and (output / "report.md").is_file()
    assert (output / "prompt_template.txt").read_bytes() == (b5.ARCHIVE / "references/proof_autograder_prompt.txt").read_bytes()


@pytest.mark.parametrize("tool_use", [False, True])
def test_mock_codex_uses_isolation_and_publishes_native_grade(task, local_runner, tmp_path, monkeypatch, tool_use):
    seen = []

    class FakeProcess:
        returncode = 0

        def __init__(self, command, **kwargs):
            seen.append(command)
            self.command, self.log = command, kwargs["stdout"]
            assert kwargs["start_new_session"]

        def communicate(self, input, timeout):
            assert "SUBMITTED_PROOF" in input and timeout == 1200
            final = Path(self.command[self.command.index("--output-last-message") + 1])
            final.write_text("Correct argument. <points>7 out of 7</points>\n")
            if tool_use:
                self.log.write(json.dumps(dict(type="item.completed", item=dict(type="mcp_tool_call"))) + "\n")
            self.log.write(json.dumps(dict(type="item.completed", item=dict(type="agent_message"))) + "\n")
            self.log.write(json.dumps(dict(type="turn.completed")) + "\n")

    monkeypatch.setattr(b5.shutil, "which", lambda value: "/fake/codex")
    monkeypatch.setattr(local_runner, "subprocess", SimpleNamespace(
        Popen=FakeProcess, PIPE=-1, STDOUT=-2, TimeoutExpired=TimeoutError))
    output = tmp_path / "grading"
    assert b5.main(arguments(task, output, "--workers", "1", "--max-attempts", "1")) == int(tool_use)
    assert len(seen) == 1
    command = seen[0]
    assert all(flag in command for flag in ["--ephemeral", "--ignore-user-config", "--ignore-rules"])
    assert command[command.index("--sandbox") + 1] == "read-only"
    assert command[command.index("--model") + 1] == "gpt-5.6-sol"
    assert 'model_reasoning_effort="xhigh"' in command
    assert "features.shell_tool=false" in command and "project_doc_max_bytes=0" in command
    assert "features.multi_agent=false" in command and 'web_search="disabled"' in command
    assert "model_instructions_file=" + json.dumps(str(b5.ARCHIVE / "references/evaluator_instructions.txt")) in command
    summary = json.loads((output / "summary.json").read_text())
    if tool_use:
        assert summary["state"] == "completed_with_failures" and summary["failed_count"] == 1
        assert summary["rows"][0]["grade"] is None
        assert "isolation violation" in summary["rows"][0]["error"]
        return
    assert summary["state"] == "completed" and summary["completed_count"] == 1
    row = summary["rows"][0]
    assert row["grade"] == dict(score=7, category="Correct")
    assert row["source_artifacts_unchanged"] and row["isolation_verified"]
    case = Path(row["result_path"]).parent
    assert json.loads((case / "isolation_audit.json").read_text())["tool_calls"] == 0
    assert json.loads((case / "result.json").read_text())["grade"]["score"] == 7
    assert (case / "grade.md").is_file()


def test_trace_rejects_tool_use(tmp_path):
    path = tmp_path / "trace.jsonl"
    path.write_text("\n".join(json.dumps(event) for event in [
        dict(type="item.completed", item=dict(type="command_execution")),
        dict(type="item.completed", item=dict(type="agent_message")), dict(type="turn.completed")]))
    with pytest.raises(ValueError, match="isolation violation"):
        b5.prepare_runner().validate_trace(path)
