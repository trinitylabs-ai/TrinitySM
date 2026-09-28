from __future__ import annotations

from dataclasses import asdict, replace
import json
from pathlib import Path

import pytest

from experiments.local_math_verifier.runtime import HTTPGenerationConfig
from cognitive_well_harness_v0_3_257_v108_third_resolve_raw_t10_bf_temp07_20260904 import (
    budget_forcing as bf,
)
from cognitive_well_harness_v0_3_257_v108_third_resolve_raw_t10_bf_temp07_20260904 import (
    pipeline,
)
from cognitive_well_harness_v0_3_257_v108_third_resolve_raw_t10_bf_temp07_20260904.run import (
    HANDOFF_MARKER,
    use_v0258_handoff,
)


def _fake_transport(calls: list[dict]):
    def fake(**kwargs):
        calls.append(dict(kwargs))
        output_dir = Path(kwargs["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)
        stage = str(kwargs["stage"])
        forced = kwargs.get("prior_generation") is not None
        text = "forced" if forced else "primary"
        reasoning = f"{text} reasoning"
        raw = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": text,
                        "reasoning_content": reasoning,
                    },
                    "finish_reason": "stop",
                }
            ]
        }
        (output_dir / f"{stage}.prompt.txt").write_text(
            kwargs["prompt"], encoding="utf-8"
        )
        (output_dir / f"{stage}.user_prompt.txt").write_text(
            kwargs.get("user_prompt", ""), encoding="utf-8"
        )
        (output_dir / f"{stage}.raw_response.json").write_text(
            json.dumps(raw), encoding="utf-8"
        )
        (output_dir / f"{stage}.reasoning.txt").write_text(
            reasoning, encoding="utf-8"
        )
        metadata = {
            "finish_reason": "stop",
            "model": kwargs["model"],
            "continuation": forced,
        }
        (output_dir / f"{stage}.metadata.json").write_text(
            json.dumps(metadata), encoding="utf-8"
        )
        return {"text": text, "reasoning": reasoning, "metadata": metadata}

    return fake


def _run_target_call(
    *, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, temperature: float, stage: str
) -> tuple[list[dict], dict]:
    calls: list[dict] = []
    monkeypatch.setattr(bf, "_ORIGINAL", _fake_transport(calls))
    output_dir = tmp_path / "candidate" / "cold_generation"
    if not stage.startswith("cold_draft_attempt"):
        output_dir = tmp_path / "candidate" / "review"
    result = bf._call_with_budget_forcing(
        endpoint="http://127.0.0.1:8030/v1",
        model="google/gemma-4-31B-it",
        prompt="system",
        user_prompt="problem",
        output_dir=output_dir,
        stage=stage,
        config=HTTPGenerationConfig(
            max_tokens=32000,
            temperature=temperature,
            top_p=0.95,
            top_k=64,
            seed=17,
        ),
    )
    return calls, result


def test_raw_t10_primary_stays_1_and_forced_continuation_drops_to_07(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls, result = _run_target_call(
        tmp_path=tmp_path,
        monkeypatch=monkeypatch,
        temperature=1.0,
        stage="cold_draft_attempt1",
    )
    assert [call["config"].temperature for call in calls] == [1.0, 0.7]
    assert calls[0]["config"].max_tokens == calls[1]["config"].max_tokens == 32000
    assert calls[0]["config"].seed == calls[1]["config"].seed == 17
    assert result["text"] == "forced"
    event = json.loads(
        (
            tmp_path
            / "candidate"
            / "cold_generation"
            / "cold_draft_attempt1.budget_forcing.json"
        ).read_text()
    )
    assert event["primary_temperature"] == 1.0
    assert event["forced_temperature"] == 0.7
    assert event["raw_temperature_transition_applied"] is True


def test_saved_primary_runs_only_one_continuation_with_new_timeout(tmp_path, monkeypatch):
    calls=[]
    fake=_fake_transport(calls)
    config=HTTPGenerationConfig(max_tokens=49152,temperature=0.1,top_p=0.95,top_k=64,seed=17,timeout_seconds=600)
    kwargs=dict(endpoint="http://127.0.0.1:8027/v1",model="Qwen/Qwen3.6-27B",prompt="system",
                user_prompt="problem",output_dir=tmp_path/"rewrite",stage="proof_rewrite",config=config)
    primary=fake(**kwargs)
    primary["metadata"]["config"]=asdict(config)
    calls.clear()
    monkeypatch.setattr(bf,"_ORIGINAL",fake)
    result=bf._continue_primary(primary=primary,kwargs={**kwargs,"config":replace(config,timeout_seconds=900)},reused_primary=True)
    assert len(calls)==1
    assert calls[0]["config"].timeout_seconds==900
    assert calls[0]["config"].seed==17 and calls[0]["config"].max_tokens==49152
    assert "primary reasoning" in calls[0]["prior_generation"] and "primary" in calls[0]["prior_generation"]
    assert result["metadata"]["v0257_budget_forcing"]["primary_generation_reused"] is True
    event=json.loads((tmp_path/"rewrite/proof_rewrite.budget_forcing.json").read_text())
    assert event["original_config"]["timeout_seconds"]==600
    assert event["forced_config"]["timeout_seconds"]==900


def test_raw_t07_generation_remains_at_07(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls, _ = _run_target_call(
        tmp_path=tmp_path,
        monkeypatch=monkeypatch,
        temperature=0.7,
        stage="cold_draft_attempt1",
    )
    assert [call["config"].temperature for call in calls] == [0.7, 0.7]


def test_nonraw_t10_call_remains_at_1(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls, _ = _run_target_call(
        tmp_path=tmp_path,
        monkeypatch=monkeypatch,
        temperature=1.0,
        stage="lazy_check_attempt1",
    )
    assert [call["config"].temperature for call in calls] == [1.0, 1.0]


def test_pipeline_manifest_records_temperature_policy_and_third_resolve_boundary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    problem = tmp_path / "problem.json"
    problem.write_text(
        json.dumps({"problem_id": "generic_p4", "claim": "Prove it."}),
        encoding="utf-8",
    )
    received: dict = {}

    def fake_parent(**kwargs):
        received.update(kwargs)
        return {"state": "stopped_at_boundary", "stage": "third_resolve"}

    monkeypatch.setattr(pipeline.v108, "run_pipeline", fake_parent)
    output_dir = tmp_path / "run"
    result = pipeline.run_pipeline(
        problem_file=problem,
        problem_id="generic_p4",
        problem_number=4,
        output_dir=output_dir,
        gemma_endpoint="http://127.0.0.1:8030/v1",
        qwen_endpoint="http://127.0.0.1:8027/v1",
        master_seed=3,
        seed_namespace="test",
    )
    assert received["stop_after"] == "third_resolve"
    assert result["upgrade_harness_version"] == "0.3.257"
    manifest = json.loads(
        (output_dir / "v0257_budget_forcing_manifest.json").read_text()
    )
    transition = manifest["budget_forcing"]["temperature_policy"][
        "raw_generation_primary_temperature_1_0"
    ]
    assert transition == {"primary": 1.0, "continuation": 0.7}


def test_pipeline_rejects_other_terminal_boundaries(tmp_path: Path) -> None:
    problem = tmp_path / "problem.json"
    problem.write_text(json.dumps({"claim": "Prove it."}), encoding="utf-8")
    with pytest.raises(ValueError, match="third_resolve"):
        pipeline.run_pipeline(
            problem_file=problem,
            problem_id="generic_p4",
            problem_number=4,
            output_dir=tmp_path / "run",
            gemma_endpoint="http://127.0.0.1:8030/v1",
            qwen_endpoint="http://127.0.0.1:8027/v1",
            stop_after="proof_synthesis",
        )


def test_run_scoped_v0258_handoff_excludes_p1_and_p2(tmp_path: Path) -> None:
    (tmp_path / HANDOFF_MARKER).write_text("v0258\n", encoding="utf-8")
    assert use_v0258_handoff(output_dir=tmp_path / "p4", problem_number=4)
    assert use_v0258_handoff(output_dir=tmp_path / "p3", problem_number=3)
    assert not use_v0258_handoff(output_dir=tmp_path / "p1", problem_number=1)
    assert not use_v0258_handoff(output_dir=tmp_path / "p2", problem_number=2)
