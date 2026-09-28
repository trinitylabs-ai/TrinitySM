from dataclasses import asdict
from pathlib import Path

import pytest

from . import pipeline, repair_boundary as boundary
from .test_harness import ScriptedCaller, audit_markdown, source_result, task


def reviewer_task():
    return {
        "proof_index": 0, "problem_number": 1, "problem_id": "Example-001",
        "candidate_id": "unit", "problem": "Prove the assertion.",
        "problem_path": "/unused/problem.json", "problem_sha256": "problem-hash",
        "proof": "The submitted proof.", "proof_path": "/unused/proof.md",
        "proof_sha256": "proof-hash", "seed": 123, "temperature": 0.2,
        "temperature_label": "t02", "gpu": 1, "endpoint": "http://unused",
        "task_id": "example.unit.t02", "model_key": "qwen36",
        "model_name": boundary.QWEN_MODEL,
    }


def mock_http(monkeypatch, outputs):
    """Replace physical HTTP only; retain the actual mandatory BF wrapper."""
    calls = []

    def generate(**kwargs):
        index = len(calls)
        assert index < len(outputs), "unexpected retry/model call"
        calls.append(kwargs)
        text, finish = outputs[index]
        root = Path(kwargs["output_dir"])
        root.mkdir(parents=True, exist_ok=True)
        metadata = {
            "model": kwargs["model"], "stage": kwargs["stage"],
            "finish_reason": finish, "config": asdict(kwargs["config"]),
        }
        stage = kwargs['stage']
        for key, suffix, value in [('system_prompt_path', '.prompt.txt', kwargs['prompt']),
                                   ('user_prompt_path', '.user_prompt.txt', kwargs['user_prompt']),
                                   ('reasoning_path', '.reasoning.txt', 'Private analysis.')]:
            path = root / (stage + suffix)
            path.write_text(value)
            metadata[key] = str(path.resolve())
        metadata.update(prompt_sha256=boundary.sha256_text(kwargs['prompt']),
                        user_prompt_sha256=boundary.sha256_text(kwargs['user_prompt']))
        raw_path = root / f'{stage}.raw_response.json'
        boundary.write_json(raw_path, {'choices': [{'message': {'role': 'assistant', 'content': text,
            'reasoning': 'Private analysis.'}, 'finish_reason': finish}]})
        metadata['response_path'] = str(raw_path.resolve())
        boundary.write_json(root / f"{stage}.metadata.json", metadata)
        return {"text": text, "reasoning": "Private analysis.", "metadata": metadata}

    monkeypatch.setattr(pipeline.v263.parent._budget_forcing, "_ORIGINAL", generate)
    return calls


@pytest.mark.parametrize("protocol_repair", [False, True])
def test_reviewer_cap_uses_completed_preforcing_without_retry(tmp_path, monkeypatch, protocol_repair):
    good = "NO_ADVERSARIAL_BREAK"
    outputs = ([("malformed", "stop")] * 2 if protocol_repair else [])
    outputs += [(good, "stop"), (good, "length")]
    calls = mock_http(monkeypatch, outputs)
    reviewer = pipeline.stage.reviewer_2
    old_cap, old_retry = reviewer.MAX_OUTPUT_TOKENS, reviewer.RETRY_ON_OUTPUT_CAP
    with pipeline.runtime_generation_policy(), pipeline.inherited_component_caps():
        result = reviewer.run_task(output_dir=tmp_path, task=reviewer_task())
    assert len(calls) == (4 if protocol_repair else 2)
    assert all(call["config"].max_tokens == 49152 for call in calls)
    assert all(call["config"].temperature == 0.2 for call in calls)
    assert all("clean_" not in call["stage"] for call in calls)
    assert calls[-1].get("continuation_instruction")  # BF still runs.
    assert result['parsed']['valid']
    assert result['final_generation']['v0257_budget_forcing']['canonical_source'] == 'pre_budget_forcing_limit_fallback'
    assert list(tmp_path.rglob("result.json"))
    assert (reviewer.MAX_OUTPUT_TOKENS, reviewer.RETRY_ON_OUTPUT_CAP) == (old_cap, old_retry)


def test_successful_qwen_identity_and_bf_both_use_49k(tmp_path, monkeypatch):
    good = "NO_ADVERSARIAL_BREAK"
    calls = mock_http(monkeypatch, [(good, "stop")] * 2)
    with pipeline.runtime_generation_policy(), pipeline.inherited_component_caps():
        result = pipeline.stage.reviewer_2.run_task(output_dir=tmp_path, task=reviewer_task())
    assert len(calls) == 2
    assert result["identity"]["max_output_tokens"] == 49152
    assert result["identity"]["cap_recovery_max_output_tokens"] is None
    assert result["cap_recovery"] == {"triggered": False, "policy": "stop_on_output_cap"}
    event = boundary.read_object(next(tmp_path.rglob("*.budget_forcing.json")))
    assert event["original_config"]["max_tokens"] == 49152
    assert event["forced_config"]["max_tokens"] == 49152


@pytest.mark.parametrize("prior_parser_failure", [False, True])
def test_boundary_cap_uses_complete_primary_instead_of_parseable_truncation(tmp_path, monkeypatch, prior_parser_failure):
    valid = audit_markdown("CERTIFIED")
    outputs = ([("bad Markdown", "stop")] * 2 if prior_parser_failure else [])
    outputs += [(valid, "stop"), (valid, "length")]
    calls = mock_http(monkeypatch, outputs)
    with pipeline.runtime_generation_policy():
        result = boundary.default_markdown_call(
            endpoint="unused", model=boundary.QWEN_MODEL, system_prompt="system",
            user_prompt="user", output_dir=tmp_path, stage_name="audit",
            temperature=0.2, seed_key="test", reasoning_effort=None,
            parser=boundary.brief_stage.parse_certification_markdown,
        )
    assert len(calls) == (4 if prior_parser_failure else 2)
    assert all(call["config"].max_tokens == 49152 for call in calls)
    assert result['metadata']['v0257_budget_forcing']['canonical_source'] == 'pre_budget_forcing_limit_fallback'
    assert (tmp_path / "audit.final.md").read_text().strip() == valid
    boundary._bind_markdown_call(result, call_root=tmp_path, model=boundary.QWEN_MODEL)


def test_qwen_override_cannot_exceed_49k_and_gemma_is_unchanged(tmp_path, monkeypatch):
    seen = []

    def generate(**kwargs):
        seen.append(kwargs["config"].max_tokens)
        return {"text": "ok", "metadata": {}}

    monkeypatch.setattr(pipeline.transport, "run_openai_chat_generation", generate)
    with pipeline.runtime_generation_policy():
        for model in (boundary.QWEN_MODEL, boundary.GEMMA_MODEL):
            for cap in (4000, 32768, 49152, 65536):
                pipeline.transport.run_openai_chat_generation(
                    model=model, stage="test", config=pipeline.transport.HTTPGenerationConfig(max_tokens=cap),
                )
    assert seen == [49152] * 4 + [32768, 32768, 49152, 65536]


def test_historical_boundary_still_replays_without_relabelling(tmp_path, monkeypatch):
    with monkeypatch.context() as historical:
        historical.setattr(boundary, "token_policy_for", lambda _: None)
        result = boundary.audit_repair_and_reaudit(
            lane=tmp_path, task=task(), source_result=source_result(),
            qwen_endpoint="unused", gemma_endpoint="unused", cycle_key="R1-C1",
            caller=ScriptedCaller([audit_markdown("CERTIFIED")]),
        )
    record = result["repair_brief_audit_rewrite"]
    record.pop("qwen_token_policy")
    record["history"][0]["producer"].pop("token_policy")
    boundary.verify_gate_producer_history(
        record, allowed_root=tmp_path, source_fusion=source_result()["final"],
        effective_fusion=result["final"], task=task(),
    )
    assert record["history"][0]["producer"]["cap"] == 32768


def test_replay_rejects_retry_after_cap(tmp_path):
    for i, state in ((1, "rejected"), (2, "accepted")):
        boundary.write_json(tmp_path / f"attempt_{i:02d}_cap_49152/validation.json", {
            "cap": 49152, "state": state, "finish_reason": "length" if i == 1 else "stop",
        })
    with pytest.raises(ValueError, match="capped Qwen response"):
        boundary.verify_producer_binding({
            "model": boundary.QWEN_MODEL, "token_policy": boundary.QWEN_TOKEN_POLICY,
            "cap": 49152, "attempt_count": 2, "call_root": str(tmp_path),
            "attempt_dir": str(tmp_path / "attempt_02_cap_49152"),
        }, allowed_root=tmp_path, expected_model=boundary.QWEN_MODEL)
