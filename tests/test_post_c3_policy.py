"""CPU-only checks for independent post-C3 prompts and inherited chat-BF hooks."""

from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import threading
from types import SimpleNamespace

import pytest

from harnesses.post_c3_completion import policy, prompts


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def events(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def route(role, stage, prompt):
    return {"role": role, "stage_pattern": stage, "prompt_sha256": sha(prompt)}


def args(tmp_path, stage="lazy_check", prompt="system including proof", seed=17):
    return {
        "stage": stage, "prompt": prompt, "user_prompt": "original user instruction",
        "model": "google/gemma-4-31B-it", "output_dir": tmp_path / stage,
        "config": SimpleNamespace(seed=seed, temperature=0.1, max_tokens=16384),
        "prior_generation": "existing recovered reasoning and answer",
        "continuation_instruction": "existing recovery instruction",
    }


def source():
    return {"text": "original final answer", "reasoning": "original reasoning",
            "metadata": {"finish_reason": "stop"}}


def module(*, callback=None, cue_calls=1, bad_hash=False, fallback=False):
    bf = SimpleNamespace(calls=[], original_instruction_calls=0, transport_calls=[])

    def instruction(config):
        bf.original_instruction_calls += 1
        return "original generic continuation"

    def original_continue(*, primary, kwargs, **optional):
        bf.calls.append((primary, kwargs, optional))
        if callback:
            callback()
        cue = ""
        for _ in range(cue_calls):
            cue = bf.continuation_instruction(kwargs["config"])
        # This is the inherited function's responsibility, outside the policy.
        bf.transport_calls.append({"prior_reasoning": primary["reasoning"],
                                   "prior_answer": primary["text"], "cue": cue})
        return {"text": "complete replacement", "reasoning": "additional reasoning",
                "metadata": {"finish_reason": "stop", "config": {"seed": 17, "max_tokens": 32768},
                             "limit_recovery": {"action": "primary_fallback"} if fallback else {},
                             "v0257_budget_forcing": {
                                 "cue_sha256": "0" * 64 if bad_hash else sha(cue),
                                 "canonical_source": "primary_fallback" if fallback else "forced_response",
                                 "canonical_artifacts_are_forced_response": not fallback,
                                 "forced_finish_reason": "length" if fallback else "stop"}}}

    bf._continue_primary = original_continue
    bf.continuation_instruction = instruction
    return bf


@pytest.mark.parametrize("role,stage,expected", [
    ("lazy_check", "lazy_check", prompts.LAZY_CONTINUATION),
    ("expansion", "lazy_in_place_resolve", prompts.EXPANSION_CONTINUATION),
])
def test_exact_role_one_original_bf_and_recovery_inputs_unchanged(tmp_path, role, stage, expected):
    bf = module()
    old_continue, old_instruction = bf._continue_primary, bf.continuation_instruction
    kwargs, primary = args(tmp_path, stage=stage), source()
    path = tmp_path / "audit.jsonl"
    with policy.install(bf, path, routes=[route(role, stage, kwargs["prompt"])]):
        result = bf._continue_primary(primary=primary, kwargs=kwargs,
                                      primary_error="recovered timeout", reused_primary=True)
    assert bf._continue_primary is old_continue
    assert bf.continuation_instruction is old_instruction
    assert len(bf.calls) == len(bf.transport_calls) == 1
    passed_primary, passed_kwargs, optional = bf.calls[0]
    assert passed_primary is primary and passed_kwargs is kwargs
    assert passed_kwargs["config"].seed == 17
    assert passed_kwargs["config"].temperature == 0.1
    assert passed_kwargs["config"].max_tokens == 16384
    assert passed_kwargs["prior_generation"] == "existing recovered reasoning and answer"
    assert passed_kwargs["continuation_instruction"] == "existing recovery instruction"
    assert passed_kwargs["user_prompt"] == "original user instruction"
    assert optional == {"primary_error": "recovered timeout", "reused_primary": True}
    assert bf.transport_calls == [{"prior_reasoning": primary["reasoning"],
                                   "prior_answer": primary["text"], "cue": expected}]
    assert bf.original_instruction_calls == 0
    assert result["text"] == "complete replacement"
    [event] = events(path)
    assert event["cue"] == expected
    assert event["cue_sha256"] == event["bf_metadata_cue_sha256"] == sha(expected)
    assert event["cue_call_count"] == 1 and event["cue_applied"] is True
    assert event["role"] == role and event["stage"] == stage
    assert event["primary_text_sha256"] == sha(primary["text"])
    assert event["primary_reasoning_sha256"] == sha(primary["reasoning"])
    assert event["config"]["seed"] == 17 and event["config"]["max_tokens"] == 16384
    assert event["response_config"]["max_tokens"] == 32768
    assert event["primary_generation_reused"] is True
    assert event["canonical_source"] == "forced_response"
    assert event["status"] == "returned" and event["elapsed_seconds"] >= 0


def test_threads_get_their_own_cue_and_audit_record(tmp_path):
    barrier = threading.Barrier(4)
    bf = module(callback=lambda: barrier.wait(timeout=10))
    calls = [args(tmp_path, stage="check" if i % 2 else "expand", prompt=f"prompt {i}", seed=i)
             for i in range(4)]
    routes = [route("lazy_check" if i % 2 else "expansion", call["stage"], call["prompt"])
              for i, call in enumerate(calls)]
    path = tmp_path / "audit.jsonl"
    with policy.install(bf, path, routes=routes):
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(lambda call: bf._continue_primary(primary=source(), kwargs=call), calls))
        assert bf.continuation_instruction(calls[0]["config"]) == "original generic continuation"
    records = events(path)
    assert len(records) == 4
    assert [event["event_index"] for event in records] == [1, 2, 3, 4]
    for event in records:
        assert event["cue"] == policy.CUES[event["role"]]
        assert event["cue_sha256"] == event["bf_metadata_cue_sha256"]
        assert event["prompt_sha256"] == sha(f"prompt {event['config']['seed']}")
    assert bf.original_instruction_calls == 1


def test_identical_lane_routes_are_deduplicated_and_snapshot_is_immutable(tmp_path):
    bf = module()
    kwargs = args(tmp_path)
    routes = [route("lazy_check", "lazy_check", kwargs["prompt"])] * 4
    with policy.install(bf, tmp_path / "audit.jsonl", routes=routes):
        routes[0]["prompt_sha256"] = "0" * 64
        routes.clear()
        bf._continue_primary(primary=source(), kwargs=kwargs)
    assert len(bf.calls) == 1


@pytest.mark.parametrize("bad", ["unknown_stage", "stage_suffix", "wrong_prompt", "ambiguous_role"])
def test_unknown_or_ambiguous_binding_fails_before_original_bf(tmp_path, bad):
    bf = module()
    kwargs = args(tmp_path)
    routes = [route("lazy_check", "lazy_check", kwargs["prompt"])]
    if bad == "unknown_stage":
        kwargs["stage"] = "other"
    elif bad == "stage_suffix":
        kwargs["stage"] = "lazy_check_unregistered_recovery"
    elif bad == "wrong_prompt":
        kwargs["prompt"] += " tampered"
    else:
        routes.append(route("expansion", "lazy_check", kwargs["prompt"]))
    path = tmp_path / "audit.jsonl"
    with pytest.raises(policy.RouteError):
        with policy.install(bf, path, routes=routes):
            bf._continue_primary(primary=source(), kwargs=kwargs)
    assert bf.calls == bf.transport_calls == []
    [event] = events(path)
    assert event["status"] == "error" and event["error_type"] == "RouteError"
    assert event["cue_applied"] is False


def test_swallowed_guard_aborts_later_calls_and_context_exit(tmp_path):
    bf = module()
    old = bf._continue_primary
    kwargs = args(tmp_path)
    with pytest.raises(policy.RouteError):
        with policy.install(bf, tmp_path / "audit.jsonl", routes=[route("lazy_check", "lazy_check", kwargs["prompt"])]):
            with pytest.raises(policy.RouteError):
                bf._continue_primary(primary=source(), kwargs=dict(kwargs, stage="wrong"))
            with pytest.raises(policy.RouteError):
                bf._continue_primary(primary=source(), kwargs=kwargs)
    assert bf.calls == []
    assert bf._continue_primary is old


@pytest.mark.parametrize("settings", [{"cue_calls": 0}, {"cue_calls": 2}, {"bad_hash": True}])
def test_returned_evidence_must_bind_exactly_one_applied_cue(tmp_path, settings):
    bf = module(**settings)
    kwargs = args(tmp_path)
    with pytest.raises(policy.PolicyError, match="exactly one applied"):
        with policy.install(bf, tmp_path / "audit.jsonl", routes=[route("lazy_check", "lazy_check", kwargs["prompt"])]):
            bf._continue_primary(primary=source(), kwargs=kwargs)
    assert len(bf.calls) == 1  # The policy never retries or adds a BF call.


def test_fallback_metadata_is_recorded_without_changing_returned_response(tmp_path):
    bf = module(fallback=True)
    kwargs = args(tmp_path)
    path = tmp_path / "audit.jsonl"
    with policy.install(bf, path, routes=[route("lazy_check", "lazy_check", kwargs["prompt"])]):
        result = bf._continue_primary(primary=source(), kwargs=kwargs)
    [event] = events(path)
    assert result["metadata"]["limit_recovery"]["action"] == "primary_fallback"
    assert event["canonical_source"] == "primary_fallback"
    assert event["canonical_artifacts_are_forced_response"] is False
    assert event["limit_recovery_action"] == "primary_fallback"
    assert event["forced_finish_reason"] == "length"


@pytest.mark.parametrize("error", [TimeoutError("model timeout"), KeyboardInterrupt()])
def test_transport_failure_or_interrupt_is_preserved_and_hooks_restore(tmp_path, error):
    def fail():
        raise error
    bf = module(callback=fail)
    old_continue, old_instruction = bf._continue_primary, bf.continuation_instruction
    kwargs = args(tmp_path)
    path = tmp_path / "audit.jsonl"
    with pytest.raises(type(error)) as caught:
        with policy.install(bf, path, routes=[route("lazy_check", "lazy_check", kwargs["prompt"])]):
            bf._continue_primary(primary=source(), kwargs=kwargs)
    assert caught.value is error
    assert bf._continue_primary is old_continue and bf.continuation_instruction is old_instruction
    [event] = events(path)
    assert event["error_type"] == type(error).__name__ and event["cue_applied"] is False
    assert "canonical_source" not in event


def test_log_is_never_overwritten_and_nested_patch_is_rejected(tmp_path):
    bf, path = module(), tmp_path / "audit.jsonl"
    kwargs = args(tmp_path)
    routes = [route("lazy_check", "lazy_check", kwargs["prompt"])]
    with policy.install(bf, path, routes=routes):
        with pytest.raises(policy.PolicyError, match="already installed"):
            with policy.install(bf, tmp_path / "nested.jsonl", routes=routes):
                pytest.fail("nested install allowed")
    path.write_text("existing evidence\n")
    with pytest.raises(FileExistsError):
        with policy.install(bf, path, routes=routes):
            pytest.fail("existing audit overwritten")
    assert path.read_text() == "existing evidence\n"
    with policy.install(bf, tmp_path / "fresh.jsonl", routes=routes):
        pass


@pytest.mark.parametrize("routes", [[], [{"role": "reviewer"}], [
    {"role": "lazy_check", "stage_pattern": "[", "prompt_sha256": "0" * 64}
], [{"role": "lazy_check", "stage_pattern": "check", "prompt_sha256": "wrong"}]])
def test_malformed_routes_rejected(routes, tmp_path):
    with pytest.raises(policy.PolicyError):
        with policy.install(module(), tmp_path / "audit.jsonl", routes=routes):
            pytest.fail("invalid route accepted")


def test_lazy_prompt_preserves_only_supplied_proof_and_does_not_format_braces():
    proof = "For every x in {1, 2}, P(x).\nHence Q(x)."
    built = prompts.lazy_phrasing(proof)
    assert built == prompts.LAZY_SYSTEM_PROMPT + "\n\nPROOF:\n" + proof + "\n"
    assert built.count(proof) == 1
    assert "NO_ISSUES" in built and "routine omissions" in built
    for bad in ("", "  ", None):
        with pytest.raises(ValueError):
            prompts.lazy_phrasing(bad)
