"""CPU-only checks for the process-local refinement BF cue experiment."""

import hashlib
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from types import SimpleNamespace

import pytest

from harnesses.refinement_bf_ablation import policy


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_events(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def fake_module(*, callback=None, fallback=False):
    module = SimpleNamespace(instruction_calls=[], continuation_calls=[])

    def instruction(config):
        module.instruction_calls.append(config)
        # Whitespace deliberately matters to the no-change baseline.
        return "Wait. Original JSON.\n" if config.structured else "Wait. Original text.  "

    def continue_primary(*, primary, kwargs, **optional):
        module.continuation_calls.append((primary, kwargs, optional))
        if callback:
            callback(primary, kwargs, optional)
        cue = module.continuation_instruction(kwargs["config"])
        return {
            "text": "replacement",
            "reasoning": "continued thought",
            "metadata": {
                "finish_reason": "stop",
                "config": {"seed": kwargs["config"].seed, "temperature": 0.4, "max_tokens": 32768},
                "limit_recovery": {"action": "primary_fallback"} if fallback else {},
                "v0257_budget_forcing": {
                    "cue_sha256": digest(cue),
                    "canonical_source": "primary_fallback" if fallback else "forced_response",
                    "canonical_artifacts_are_forced_response": not fallback,
                    "forced_finish_reason": "length" if fallback else "stop",
                },
            },
        }

    module.continuation_instruction = instruction
    module._continue_primary = continue_primary
    return module


def call_args(tmp_path, *, stage="reviewer2", prompt="reviewer 2 system", seed=73):
    return {
        "stage": stage,
        "prompt": prompt,
        "user_prompt": "original problem and proof",
        "model": "Qwen/Qwen3.6-27B",
        "output_dir": tmp_path / stage,
        "config": SimpleNamespace(seed=seed, temperature=0.4, max_tokens=49152, structured=False),
    }


def primary():
    return {
        "text": "primary response",
        "reasoning": "primary thought",
        "metadata": {"finish_reason": "stop"},
    }


@pytest.mark.parametrize("structured", [False, True])
def test_original_is_byte_identical_and_preserves_recovery_arguments(tmp_path, structured):
    module = fake_module()
    original_continue = module._continue_primary
    original_instruction = module.continuation_instruction
    kwargs = call_args(tmp_path)
    kwargs["config"].structured = structured
    kwargs["prior_generation"] = "earlier cap recovery reasoning and response"
    kwargs["continuation_instruction"] = "earlier recovery instruction"
    source = primary()
    route = policy.make_route("reviewer_2", r"reviewer2", kwargs["prompt"])
    events = tmp_path / "events.jsonl"
    with policy.install(module, policy.ORIGINAL, events, routes=[route]):
        result = module._continue_primary(
            primary=source, kwargs=kwargs, primary_error="recovered error", reused_primary=True
        )
    assert module._continue_primary is original_continue
    assert module.continuation_instruction is original_instruction
    passed_primary, passed_kwargs, optional = module.continuation_calls[0]
    assert passed_primary is source
    assert passed_kwargs is kwargs
    assert passed_kwargs["prior_generation"] == "earlier cap recovery reasoning and response"
    assert passed_kwargs["continuation_instruction"] == "earlier recovery instruction"
    assert optional == {"primary_error": "recovered error", "reused_primary": True}
    assert module.instruction_calls == [kwargs["config"]]
    [event] = read_events(events)
    expected = "Wait. Original JSON.\n" if structured else "Wait. Original text.  "
    assert event["cue"] == expected
    assert event["cue_sha256"] == digest(expected)
    assert event["bf_metadata_cue_sha256"] == digest(expected)
    assert event["role"] == "reviewer_2"
    assert event["primary_generation_reused"] is True
    assert event["cue_applied"] is True
    assert event["cue_call_count"] == 1
    assert event["status"] == "returned"
    assert event["response_text_sha256"] == digest(result["text"])


@pytest.mark.parametrize("role", list(policy.ROLE_SPECIFIC_CUES))
def test_each_role_changes_only_instruction(tmp_path, role):
    module = fake_module()
    kwargs = call_args(tmp_path, stage=role, prompt="system for " + role)
    source = primary()
    events = tmp_path / "events.jsonl"
    with policy.install(module, policy.ROLE_SPECIFIC, events, routes=[
        policy.make_route(role, role, kwargs["prompt"])
    ]):
        module._continue_primary(primary=source, kwargs=kwargs)
    assert module.instruction_calls == []
    assert module.continuation_calls[0][0] is source
    assert module.continuation_calls[0][1] is kwargs
    [event] = read_events(events)
    assert event["cue"] == policy.ROLE_SPECIFIC_CUES[role]
    assert event["cue"].startswith("Wait.")
    assert "complete replacement response in the original required format" in event["cue"]
    assert event["cue_sha256"] == event["bf_metadata_cue_sha256"]
    assert event["prompt_sha256"] == digest(kwargs["prompt"])
    assert event["primary_text_sha256"] == digest(source["text"])
    assert event["primary_reasoning_sha256"] == digest(source["reasoning"])
    assert event["config"]["seed"] == 73
    assert event["config"]["temperature"] == 0.4
    assert event["config"]["max_tokens"] == 49152
    assert event["response_config"]["max_tokens"] == 32768
    assert event["model"] == kwargs["model"]
    assert event["artifact_path"] == str(kwargs["output_dir"])
    assert event["canonical_source"] == "forced_response"
    assert event["canonical_artifacts_are_forced_response"] is True
    assert event["elapsed_seconds"] >= 0
    assert event["started_at"] <= event["finished_at"]


@pytest.mark.parametrize("variant", [policy.ORIGINAL, policy.ROLE_SPECIFIC])
def test_explicit_auxiliary_route_uses_generic_cue(tmp_path, variant):
    module = fake_module()
    kwargs = call_args(tmp_path, stage="gap_selector", prompt="gap selector system")
    events = tmp_path / "events.jsonl"
    with policy.install(module, variant, events, routes=[
        policy.make_route(policy.AUXILIARY, r"gap_selector", kwargs["prompt"])
    ]):
        module._continue_primary(primary=primary(), kwargs=kwargs)
    [event] = read_events(events)
    assert event["role"] == policy.AUXILIARY
    assert event["cue"] == "Wait. Original text.  "
    assert module.instruction_calls == [kwargs["config"]]


def test_context_is_thread_local_and_jsonl_events_are_complete(tmp_path):
    roles = list(policy.ROLE_SPECIFIC_CUES)
    barrier = threading.Barrier(len(roles))
    module = fake_module(callback=lambda *args: barrier.wait(timeout=10))
    kwargs = [call_args(tmp_path, stage=role, prompt=role + " prompt", seed=i)
              for i, role in enumerate(roles)]
    routes = [policy.make_route(role, role, args["prompt"]) for role, args in zip(roles, kwargs)]
    events = tmp_path / "events.jsonl"
    with policy.install(module, policy.ROLE_SPECIFIC, events, routes=routes):
        with ThreadPoolExecutor(max_workers=len(roles)) as pool:
            results = list(pool.map(lambda args: module._continue_primary(primary=primary(), kwargs=args), kwargs))
        # Calling the utility outside a wrapped generation must retain original semantics.
        assert module.continuation_instruction(kwargs[0]["config"]) == "Wait. Original text.  "
    assert len(results) == len(roles)
    records = read_events(events)
    assert len(records) == len(roles)
    assert [event["event_index"] for event in records] == list(range(1, len(roles) + 1))
    for event in records:
        assert event["cue"] == policy.ROLE_SPECIFIC_CUES[event["role"]]
        assert event["cue_sha256"] == event["bf_metadata_cue_sha256"]
        assert event["config"]["seed"] == roles.index(event["role"])
    assert len(module.instruction_calls) == 1


@pytest.mark.parametrize("variant", [policy.ORIGINAL, policy.ROLE_SPECIFIC])
@pytest.mark.parametrize("bad", ["unknown_stage", "prefix_only", "wrong_prompt", "ambiguous"])
def test_stage_and_exact_prompt_guard_fails_before_underlying_call(tmp_path, variant, bad):
    module = fake_module()
    kwargs = call_args(tmp_path)
    route = policy.make_route("reviewer_2", r"reviewer2", kwargs["prompt"])
    routes = [route]
    if bad == "unknown_stage":
        kwargs["stage"] = "new_reviewer"
    elif bad == "prefix_only":
        kwargs["stage"] = "reviewer2_unapproved_recovery"
    elif bad == "wrong_prompt":
        kwargs["prompt"] += " changed prompt"
    else:
        routes.append(policy.make_route("reviewer_1", r"reviewer.*", kwargs["prompt"]))
    events = tmp_path / "events.jsonl"
    with pytest.raises(policy.RouteError, match="exactly one route"):
        with policy.install(module, variant, events, routes=routes):
            module._continue_primary(primary=primary(), kwargs=kwargs)
    assert module.continuation_calls == []
    [event] = read_events(events)
    assert event["status"] == "error"
    assert event["error_type"] == "RouteError"
    assert event["cue_applied"] is False
    assert event["cue"] is None


def test_swallowed_guard_is_latched_and_fails_context_exit(tmp_path):
    module = fake_module()
    original_continue = module._continue_primary
    kwargs = call_args(tmp_path)
    route = policy.make_route("reviewer_2", r"reviewer2", kwargs["prompt"])
    with pytest.raises(policy.RouteError):
        with policy.install(module, policy.ROLE_SPECIFIC, tmp_path / "events.jsonl", routes=[route]):
            bad_kwargs = dict(kwargs, stage="unknown")
            with pytest.raises(policy.RouteError):
                module._continue_primary(primary=primary(), kwargs=bad_kwargs)
            # A known later call must not continue the failed experimental arm.
            with pytest.raises(policy.RouteError):
                module._continue_primary(primary=primary(), kwargs=kwargs)
    assert module._continue_primary is original_continue
    assert module.continuation_calls == []
    assert len(read_events(tmp_path / "events.jsonl")) == 2


def test_original_failure_restores_hooks_and_does_not_invent_verdict(tmp_path):
    failure = TimeoutError("local generation timed out")

    def fail(*args):
        raise failure

    module = fake_module(callback=fail)
    original_continue = module._continue_primary
    original_instruction = module.continuation_instruction
    kwargs = call_args(tmp_path)
    events = tmp_path / "events.jsonl"
    with pytest.raises(TimeoutError) as caught:
        with policy.install(module, policy.ROLE_SPECIFIC, events, routes=[
            policy.make_route("reviewer_2", r"reviewer2", kwargs["prompt"])
        ]):
            module._continue_primary(primary=primary(), kwargs=kwargs)
    assert caught.value is failure
    assert module._continue_primary is original_continue
    assert module.continuation_instruction is original_instruction
    [event] = read_events(events)
    assert event["status"] == "error"
    assert event["error_type"] == "TimeoutError"
    assert event["cue_applied"] is False
    assert "canonical_source" not in event
    assert "verdict" not in event


def test_caller_exception_restores_hooks_and_fallback_is_recorded(tmp_path):
    module = fake_module(fallback=True)
    original_continue = module._continue_primary
    original_instruction = module.continuation_instruction
    kwargs = call_args(tmp_path)
    events = tmp_path / "events.jsonl"
    with pytest.raises(ValueError, match="caller failed"):
        with policy.install(module, policy.ROLE_SPECIFIC, events, routes=[
            policy.make_route("reviewer_2", r"reviewer2", kwargs["prompt"])
        ]):
            result = module._continue_primary(primary=primary(), kwargs=kwargs)
            assert result["metadata"]["limit_recovery"]["action"] == "primary_fallback"
            raise ValueError("caller failed")
    assert module._continue_primary is original_continue
    assert module.continuation_instruction is original_instruction
    [event] = read_events(events)
    assert event["canonical_source"] == "primary_fallback"
    assert event["canonical_artifacts_are_forced_response"] is False
    assert event["limit_recovery_action"] == "primary_fallback"
    assert event["forced_finish_reason"] == "length"


def test_route_manifest_serializes_prompt_hash_without_prompt():
    route = policy.make_route("fusion", r"fusion(?:_protocol_repair)?", "exact system")
    assert asdict(route) == {
        "role": "fusion", "stage_pattern": r"fusion(?:_protocol_repair)?",
        "prompt_sha256": digest("exact system"),
    }


@pytest.mark.parametrize("args", [
    ("invented_role", "stage", "prompt"),
    ("resolver", "[", "prompt"),
    ("resolver", "", "prompt"),
    ("resolver", "stage", ""),
])
def test_bad_route_rejected(args):
    with pytest.raises(policy.PolicyError):
        policy.make_route(*args)


def test_nested_install_and_existing_log_are_rejected_without_replacing_hooks(tmp_path):
    module = fake_module()
    original_continue = module._continue_primary
    route = policy.make_route("fusion", "fusion", "prompt")
    events = tmp_path / "events.jsonl"
    with policy.install(module, policy.ORIGINAL, events, routes=[route]):
        active_continue = module._continue_primary
        with pytest.raises(policy.PolicyError, match="already installed"):
            with policy.install(module, policy.ROLE_SPECIFIC, tmp_path / "nested.jsonl", routes=[route]):
                pytest.fail("nested policy must not install")
        assert module._continue_primary is active_continue
    assert module._continue_primary is original_continue
    events.write_text("original evidence\n")
    with pytest.raises(FileExistsError):
        with policy.install(module, policy.ORIGINAL, events, routes=[route]):
            pytest.fail("must not overwrite evidence")
    assert events.read_text() == "original evidence\n"
    assert module._continue_primary is original_continue
    # Failed setup did not leak the installation lock.
    with policy.install(module, policy.ORIGINAL, tmp_path / "new.jsonl", routes=[route]):
        pass
