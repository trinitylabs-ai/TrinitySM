import fcntl
from types import SimpleNamespace
import shlex

import pytest

from scripts import relaunch_v263_v290 as restart


def queue(tmp_path):
    rows = [{"problem_id": f"Example-{i}", "problem_number": i} for i in (1, 2)]
    restart.runner.write(tmp_path / "manifest.json", {"problems": rows})
    first = tmp_path / "problems/Example-1"
    restart.runner.write(first / "summary.json", {"state": "completed"})
    second = tmp_path / "problems/Example-2"
    restart.runner.write(second / "01_source/p2/01_raw_lazy_enhanced_resolve/summary.json",
                         {"state": "completed", "terminal_checkpoint": "lazy_checked"})
    restart.runner.write(second / "02_r1_cycles/status.json", {"state": "running"})
    restart.runner.write(second / "execution_policy.json", {"old_policy": True})
    return second


def test_preserves_partial_work_and_skips_completed_problems(tmp_path):
    second = queue(tmp_path)
    plan = restart.restart_plan(tmp_path)
    assert plan["problem_id"] == "Example-2"
    assert plan["archive_partial_backend"] is True
    with restart.stopped_queue(tmp_path):
        backup = restart.preserve_partial(plan)
    assert restart.runner.read(backup / "02_r1_cycles/status.json") == {"state": "running"}
    assert restart.runner.read(backup / "execution_policy.json") == {"old_policy": True}
    assert (second / "01_source/p2/01_raw_lazy_enhanced_resolve/summary.json").is_file()
    assert not (second / "02_r1_cycles").exists()
    assert restart.restart_plan(tmp_path)["archive_partial_backend"] is False


@pytest.mark.parametrize("worker", [False, True])
def test_refuses_live_queue_or_orphan_worker_without_moving_files(tmp_path, worker):
    second = queue(tmp_path)
    path = second / "worker.lock" if worker else tmp_path / "queue.lock"
    with path.open("a") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(RuntimeError, match="still running"):
            with restart.stopped_queue(tmp_path):
                pytest.fail("should not get the lock")
    assert (second / "02_r1_cycles/status.json").is_file()
    assert not list(second.glob("restart_backup.*"))


def test_no_archive_of_completed_backend_without_outer_summary(tmp_path):
    second = queue(tmp_path)
    restart.runner.write(second / "02_r1_cycles/summary.json", {"state": "completed_with_failed_lanes"})
    assert restart.restart_plan(tmp_path)["archive_partial_backend"] is False


def test_requires_real_checkpoint_before_preserving_partial_cycle(tmp_path):
    second = queue(tmp_path)
    restart.runner.write(second / "01_source/p2/01_raw_lazy_enhanced_resolve/summary.json", {"state": "running"})
    with pytest.raises(RuntimeError, match="No completed lazy-checked checkpoint"):
        restart.restart_plan(tmp_path)
    assert (second / "02_r1_cycles/status.json").is_file()


def test_check_only_does_not_move_work_or_launch(tmp_path, monkeypatch):
    second = queue(tmp_path)
    monkeypatch.setattr(restart, "resume_args", lambda _: None)
    monkeypatch.setattr(restart, "launch_tmux", lambda *_: pytest.fail("launched tmux"))
    monkeypatch.setattr(restart.sys, "argv", ["restart", "--output-dir", str(tmp_path), "--check"])
    assert restart.main() == 0
    assert (second / "02_r1_cycles/status.json").is_file()
    assert not list(second.glob("restart_backup.*"))


def test_finished_queue_is_noop(tmp_path):
    second = queue(tmp_path)
    restart.runner.write(second / "summary.json", {"state": "completed_with_failed_lanes"})
    assert restart.restart_plan(tmp_path) is None


@pytest.mark.parametrize("session_exists", [False, True])
def test_tmux_launch_uses_correct_python_and_quotes_paths(tmp_path, monkeypatch, session_exists):
    calls = []

    def run(command, **kwargs):
        calls.append(command)
        return SimpleNamespace(returncode=0 if session_exists else 1)

    monkeypatch.setattr(restart.shutil, "which", lambda _: "/usr/bin/tmux")
    monkeypatch.setattr(restart, "MODEL_PYTHON", restart.Path(restart.__file__))
    monkeypatch.setattr(restart.subprocess, "run", run)
    root = tmp_path / "directory with spaces"
    restart.launch_tmux(root, "test-session")
    assert calls[1][1] == ("new-window" if session_exists else "new-session")
    child = shlex.split(calls[1][-1].removesuffix("; exec bash"))
    assert child[child.index("--output-dir") + 1] == str(root)
    assert child[-1] == "--foreground"
