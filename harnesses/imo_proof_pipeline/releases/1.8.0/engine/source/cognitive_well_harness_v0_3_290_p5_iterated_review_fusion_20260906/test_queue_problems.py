from pathlib import Path
from types import SimpleNamespace

import pytest

from . import pipeline, queue_problems as queue


def test_queue_waits_for_completion_and_does_not_skip_mechanical_failures(tmp_path):
    assert not queue.pipeline_finished(tmp_path)
    pipeline.write_json(tmp_path / "status.json", {"state": "running", "stage": "R1-C3"})
    assert not queue.pipeline_finished(tmp_path)
    pipeline.write_json(tmp_path / "status.json", {"state": "failed_closed", "stage": "orchestrator"})
    assert not queue.pipeline_finished(tmp_path)
    pipeline.write_json(tmp_path / "status.json", {"state": "completed_with_failed_lanes"})
    assert queue.pipeline_finished(tmp_path)


def test_queued_command_uses_requested_problem_no_tools_and_same_runtime():
    runtime = {"gemma_endpoint": "http://gemma", "qwen_endpoint": "http://qwen",
               "workers_per_endpoint": 4, "resolve_workers": 2, "model_timeout_sec": 600}
    command = queue.model_command(number=4, source=Path("/saved"), output=Path("/new"),
                                  runtime=runtime, seed_namespace="queue_test")
    assert command[command.index("--problem-number") + 1] == "4"
    assert command[command.index("--input-checkpoint") + 1] == "lazy_checked"
    assert command[command.index("--seed-namespace") + 1] == "queue_test:p4"
    assert "--no-optional-exact-evidence" in command
    assert "--execute-models" in command
    assert "--reference-root" not in command
    assert "--strict-score" not in command


def test_worker_reattachment_matches_module_and_output_not_input(tmp_path):
    proc = tmp_path / "proc"
    proc.mkdir()
    model = tmp_path / "model"
    score = tmp_path / "scores"
    for pid, module, arguments in (
        (101, queue.MODULE, ["--output-dir", "model"]),
        (102, queue.MODULE + ".score_when_ready", ["--run-root", str(model), "--output-dir", str(score)]),
    ):
        directory = proc / str(pid)
        directory.mkdir()
        (directory / "cwd").symlink_to(tmp_path, target_is_directory=True)
        (directory / "cmdline").write_bytes("\0".join(["python", "-m", module, *arguments, ""]).encode())
    assert queue.locate_worker(model, queue.MODULE, proc_root=proc) == 101
    assert queue.locate_worker(score, queue.MODULE + ".score_when_ready", proc_root=proc) == 102
    assert not queue.process_owns_run(102, model, proc_root=proc)
    assert queue.locate_worker(model, queue.MODULE + ".score_when_ready", proc_root=proc) is None
    duplicate = proc / "103"
    duplicate.mkdir()
    (duplicate / "cwd").symlink_to(tmp_path, target_is_directory=True)
    (duplicate / "cmdline").write_bytes((proc / "101/cmdline").read_bytes())
    with pytest.raises(RuntimeError, match="multiple workers"):
        queue.locate_worker(model, queue.MODULE, proc_root=proc)


def test_queue_children_are_detached_from_supervisor(tmp_path, monkeypatch):
    source, after, after_score, output = [tmp_path / name for name in ("source", "after", "after_score", "queue")]
    source.mkdir()
    runtime = {"gemma_endpoint": "http://gemma", "qwen_endpoint": "http://qwen",
               "workers_per_endpoint": 4, "resolve_workers": 2, "model_timeout_sec": 600}
    pipeline.write_json(after / "manifest.json", {"runtime": runtime})
    pipeline.write_json(after / "status.json", {"state": "completed"})
    pipeline.write_json(after_score / "summary.json", {"state": "completed"})
    launcher = tmp_path / "score.py"
    launcher.write_text("# test launcher\n")
    calls = []
    def spawn(command, **kwargs):
        assert kwargs["start_new_session"] is True
        calls.append(command)
        destination = Path(command[command.index("--output-dir") + 1])
        pipeline.write_json(destination / "manifest.json", {})
        pipeline.write_json(destination / "status.json", {"state": "completed"})
        pipeline.write_json(destination / "summary.json", {"state": "completed"})
        return SimpleNamespace(pid=100000 + len(calls), poll=lambda: 0, wait=lambda: 0)
    monkeypatch.setattr(queue.subprocess, "Popen", spawn)
    monkeypatch.setattr(queue, "frozen_portfolio", lambda *_: {"frozen": True})
    monkeypatch.setattr(queue.sys, "argv", ["queue", "--after-run", str(after), "--after-score-run", str(after_score),
                                           "--output-dir", str(output), "--source-run", str(source),
                                           "--problem-numbers", "1", "--skill-launcher", str(launcher)])
    queue.main()
    assert len(calls) == 2
    assert pipeline.read_object(output / "status.json")["state"] == "completed"
