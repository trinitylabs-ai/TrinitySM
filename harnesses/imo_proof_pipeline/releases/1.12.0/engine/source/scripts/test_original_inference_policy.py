"""Exercise the restored wire requests without running live inference."""
import io
import json

import pytest

from scripts import run_v263_v290 as runner
from experiments.local_math_verifier.runtime import HTTPGenerationConfig


@pytest.mark.parametrize("model", [runner.GEMMA_MODEL, runner.QWEN_MODEL])
def test_original_requests_have_no_repetition_policy(tmp_path, monkeypatch, model):
    _, pipeline = runner.load_engines()
    from cognitive_well_harness_v0_3_257_v108_third_resolve_raw_t10_bf_temp07_20260904 import budget_forcing as bf
    monkeypatch.setattr(bf, "_ORIGINAL", bf.base._ORIGINAL)
    calls = []

    def respond(request, timeout):
        calls.append(json.loads(request.data))
        assert len(calls) <= 2, "unexpected replacement request"
        return io.BytesIO(json.dumps({
            "id": f"response-{len(calls)}", "usage": {"completion_tokens": 20},
            "choices": [{"finish_reason": "stop", "message": {
                "content": "Complete response.", "reasoning": "Independent reasoning."
            }}],
        }).encode())

    monkeypatch.setattr("urllib.request.urlopen", respond)
    result = bf._call_with_budget_forcing(
        endpoint="http://127.0.0.1:1/v1", model=model, stage="generic_task",
        prompt="Follow the task requirements.", user_prompt="Original task input.",
        config=HTTPGenerationConfig(max_tokens=49152, temperature=0.2, seed=123),
        output_dir=tmp_path,
    )
    assert len(calls) == 2
    assert all(c["seed"] == 123 and c["max_tokens"] == 49152 for c in calls)
    assert all("repetition_detection" not in c for c in calls)
    assert [len(c["messages"]) for c in calls] == [2, 4]
    assert "fresh_retry" not in result["metadata"]
    assert not list(tmp_path.glob("*.fresh_retry"))
    assert pipeline._verify_generation_producer(
        result["metadata"], allowed_root=tmp_path, expected_model=model,
        expected_stage="generic_task", expected_seed=123, expected_cap=49152,
        expected_timeout_sec=7200, expected_system_prompt="Follow the task requirements.",
        expected_user_prompt="Original task input.",
    ) == "Complete response."


@pytest.mark.parametrize("entrypoint", ["worker", "relaunch"])
def test_retired_manifest_cannot_resume_under_changed_policy(tmp_path, monkeypatch, entrypoint):
    runner.write(tmp_path / "manifest.json", {"repetition_fresh_retry": {"enabled": True}})
    monkeypatch.setattr(runner, "load_engines", lambda: pytest.fail("must reject before loading engines"))
    with pytest.raises(ValueError, match="retired repetition fresh-retry policy"):
        if entrypoint == "worker":
            runner._execute_problem(tmp_path, "Example-001", dry_run=False)
        else:
            from scripts.relaunch_v263_v290 import resume_args
            resume_args(tmp_path)
