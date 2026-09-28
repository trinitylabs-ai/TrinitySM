"""Process-local, prompt-bound continuation cues for the refinement experiment.

This module imports no engine code.  The worker supplies the already loaded BF
module and routes constructed from its actual system prompts.  Only the final
continuation instruction changes; primary outputs, recovery context, transport,
sampling and the inherited full-replacement BF implementation stay untouched.
"""

from __future__ import annotations

import hashlib
import json
import re
import threading
import time
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Any, Iterable, Mapping


ORIGINAL = "original"
ROLE_SPECIFIC = "role_specific"
AUXILIARY = "auxiliary"
POLICY_ID = "refinement-bf-role-cues-v1"

_REPLACEMENT = (
    " Emit one complete replacement response in the original required format. "
    "Do not append to, comment on, or mention the earlier draft or this instruction."
)

ROLE_SPECIFIC_CUES = {
    "reviewer_1": (
        "Wait. Recheck the submitted proof from its hypotheses to its conclusion. "
        "Find the earliest substantive inference that is not justified, and check "
        "whether the proof actually supplies the missing justification later. "
        "Separate a routine omitted step from a gap requiring a new mathematical "
        "idea. Revise unsupported criticism as carefully as unsupported acceptance."
        + _REPLACEMENT
    ),
    "reviewer_2": (
        "Wait. Recheck the strongest concrete attack on the submitted proof. "
        "Verify every proposed counterexample against all hypotheses and check "
        "its calculations. Try to refute your own objection using the proof's "
        "actual argument before retaining it. Distinguish an invalid inference "
        "from a false conclusion, and do not invent a failure witness."
        + _REPLACEMENT
    ),
    "reviewer_3": (
        "Wait. Recheck the proof's decisive missing obligation and the strongest "
        "charitable reading of the argument. Determine whether the gap can be "
        "closed by an explicit routine step using established premises, or instead "
        "needs a new nontrivial lemma or strategy. Do not silently supply that new "
        "idea or accept an unproved premise."
        + _REPLACEMENT
    ),
    "fusion": (
        "Wait. Re-adjudicate the reviewers' strongest claims against the submitted "
        "proof itself. Resolve conflicting diagnoses by checking their mathematical "
        "premises, not by counting reviewers or trusting confidence. Check any "
        "claimed routine completion explicitly. If repair is needed, give a "
        "precise, mathematically viable obligation without assuming the missing "
        "claim or preserving a previous verdict by default."
        + _REPLACEMENT
    ),
    "acceptance": (
        "Wait. Independently recheck the load-bearing implications of the submitted "
        "proof and treat the accepting fusion decision as untrusted. Verify that "
        "any proposed routine completion is explicit, valid and genuinely routine. "
        "Certify only a complete correct argument under the original criteria; "
        "otherwise identify the earliest substantive break without repairing it."
        + _REPLACEMENT
    ),
    "repair_brief_audit": (
        "Wait. Recheck whether the proposed repair brief is mathematically viable "
        "and addresses the actual proof defect. Check its premises, quantifiers "
        "and proposed route for circular reasoning or an unproved replacement "
        "claim. Distinguish a useful repair obligation from a purported solution. "
        "Do not certify the original proof merely because a repair is proposed."
        + _REPLACEMENT
    ),
    "repair_brief_rewrite": (
        "Wait. Recheck the audit's valid objections and revise the repair brief "
        "around the precise unresolved obligation. Preserve the original task "
        "and the brief's required scope. Remove circular steps and unsupported "
        "premises, and make the proposed route mathematically viable without "
        "presenting an unproved claim as an established fact."
        + _REPLACEMENT
    ),
    "resolver": (
        "Wait. Recheck whether the revised proof actually resolves the valid "
        "criticisms and proves the original statement. Preserve sound parts of "
        "the argument, establish the missing implications explicitly, and audit "
        "the resulting proof for circularity, boundary cases and unproved premises. "
        "Return the complete revised proof, not a repair plan or a claim that "
        "the checks have been performed."
        + _REPLACEMENT
    ),
}


class PolicyError(RuntimeError):
    """An experiment policy or evidence invariant failed."""


class RouteError(PolicyError):
    """The BF stage and exact system prompt do not identify one allowed role."""


@dataclass(frozen=True)
class Route:
    role: str
    stage_pattern: str
    prompt_sha256: str


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _validate_route(route: Route) -> None:
    if not isinstance(route, Route):
        raise PolicyError("routes must contain Route instances made by make_route")
    if route.role not in ROLE_SPECIFIC_CUES and route.role != AUXILIARY:
        raise PolicyError("unknown continuation role: " + str(route.role))
    if not isinstance(route.stage_pattern, str) or not route.stage_pattern:
        raise PolicyError("route stage_pattern must be a nonempty regular expression")
    try:
        re.compile(route.stage_pattern)
    except re.error as error:
        raise PolicyError("invalid route stage regular expression") from error
    if not isinstance(route.prompt_sha256, str) or not re.fullmatch(
        r"[0-9a-f]{64}", route.prompt_sha256
    ):
        raise PolicyError("route prompt_sha256 must be a lowercase SHA-256 digest")


def make_route(role: str, stage_pattern: str, system_prompt: str) -> Route:
    """Bind a full-match stage expression to one exact loaded system prompt."""
    if not isinstance(system_prompt, str) or not system_prompt:
        raise PolicyError("route system_prompt must be a nonempty string")
    route = Route(role, stage_pattern, _sha256(system_prompt))
    _validate_route(route)
    return route


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _config_fields(config: Any) -> dict[str, Any]:
    names = (
        "seed", "temperature", "max_tokens", "top_p", "top_k",
        "reasoning_effort", "thinking_token_budget", "timeout_seconds",
    )
    return {
        name: config.get(name) if isinstance(config, Mapping) else getattr(config, name, None)
        for name in names
    }


def _metadata(result: Any) -> Mapping[str, Any]:
    if not isinstance(result, Mapping):
        return {}
    metadata = result.get("metadata")
    return metadata if isinstance(metadata, Mapping) else {}


def _text_hash(result: Any, key: str) -> str:
    value = result.get(key) if isinstance(result, Mapping) else None
    return _sha256(str(value or ""))


_INSTALL_LOCK = threading.Lock()
_INSTALLED_MODULES: set[int] = set()


@contextmanager
def install(bf_module: Any, variant: str, event_path: Path, *, routes: Iterable[Route]):
    """Temporarily wrap only the BF module's two continuation hooks.

    Install after engine initialization.  Concurrent lane calls get independent
    ContextVars and serialized event writes.  Route errors are latched so even a
    frozen caller that catches Exception cannot silently turn them into a lane
    fallback: the error is raised again when this context exits.
    """
    if variant not in (ORIGINAL, ROLE_SPECIFIC):
        raise PolicyError("variant must be original or role_specific")
    bound_routes = tuple(routes)
    if not bound_routes:
        raise PolicyError("at least one explicit route is required")
    for route in bound_routes:
        _validate_route(route)
    original_continue = getattr(bf_module, "_continue_primary", None)
    original_instruction = getattr(bf_module, "continuation_instruction", None)
    if not callable(original_continue) or not callable(original_instruction):
        raise PolicyError("BF module must expose both continuation hooks")

    module_id = id(bf_module)
    with _INSTALL_LOCK:
        if module_id in _INSTALLED_MODULES:
            raise PolicyError("BF cue policy is already installed on this module")
        _INSTALLED_MODULES.add(module_id)

    stream = None
    patched = False
    active = ContextVar("refinement_bf_cue_context", default=None)
    event_lock = threading.Lock()
    failure: list[PolicyError] = []
    event_index = 0

    def latch(error: PolicyError) -> None:
        with event_lock:
            if not failure:
                failure.append(error)

    def record(event: dict[str, Any]) -> None:
        nonlocal event_index
        with event_lock:
            event_index += 1
            event["event_index"] = event_index
            try:
                stream.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
                stream.flush()
            except Exception as error:
                wrapped = PolicyError("could not write the BF cue audit event")
                if not failure:
                    failure.append(wrapped)
                raise wrapped from error

    @wraps(original_instruction)
    def instruction(config: Any) -> str:
        context = active.get()
        if context is None:
            return original_instruction(config)
        role = context["role"]
        cue = (
            original_instruction(config)
            if variant == ORIGINAL or role == AUXILIARY
            else ROLE_SPECIFIC_CUES[role]
        )
        if not isinstance(cue, str) or not cue:
            error = PolicyError("continuation instruction must be a nonempty string")
            latch(error)
            raise error
        context["cue"] = cue
        context["cue_sha256"] = _sha256(cue)
        context["cue_applied"] = True
        context["cue_call_count"] += 1
        return cue

    @wraps(original_continue)
    def continue_primary(*, primary: Any, kwargs: Mapping[str, Any], **optional: Any):
        started = time.monotonic()
        stage = kwargs.get("stage")
        prompt = kwargs.get("prompt")
        event = {
            "schema": POLICY_ID,
            "variant": variant,
            "stage": stage,
            "role": None,
            "prompt_sha256": _sha256(prompt) if isinstance(prompt, str) else None,
            "cue": None,
            "cue_sha256": None,
            "cue_applied": False,
            "cue_call_count": 0,
            "primary_text_sha256": _text_hash(primary, "text"),
            "primary_reasoning_sha256": _text_hash(primary, "reasoning"),
            "primary_finish_reason": _metadata(primary).get("finish_reason"),
            "config": _config_fields(kwargs.get("config")),
            "model": kwargs.get("model"),
            "artifact_path": str(kwargs.get("output_dir", "")),
            "primary_generation_reused": bool(optional.get("reused_primary", False)),
            "started_at": _now(),
            "status": "running",
        }
        token = None
        try:
            with event_lock:
                previous_failure = failure[0] if failure else None
            if previous_failure is not None:
                raise previous_failure
            if not isinstance(stage, str) or not isinstance(prompt, str):
                raise RouteError("BF routing requires string stage and system prompt")
            matches = [
                route for route in bound_routes
                if re.fullmatch(route.stage_pattern, stage)
                and route.prompt_sha256 == event["prompt_sha256"]
            ]
            if len(matches) != 1:
                raise RouteError(
                    "BF stage/prompt must match exactly one route; "
                    f"stage={stage!r}, matching_routes={len(matches)}, "
                    f"prompt_sha256={event['prompt_sha256']}"
                )
            event["role"] = matches[0].role
            token = active.set(event)
            result = original_continue(primary=primary, kwargs=kwargs, **optional)
            metadata = _metadata(result)
            forcing = metadata.get("v0257_budget_forcing")
            forcing = forcing if isinstance(forcing, Mapping) else {}
            recovery = metadata.get("limit_recovery")
            recovery = recovery if isinstance(recovery, Mapping) else {}
            event.update({
                "status": "returned",
                "response_finish_reason": metadata.get("finish_reason"),
                "response_config": _config_fields(metadata.get("config")),
                "response_text_sha256": _text_hash(result, "text"),
                "response_reasoning_sha256": _text_hash(result, "reasoning"),
                "canonical_source": forcing.get("canonical_source"),
                "canonical_artifacts_are_forced_response": forcing.get(
                    "canonical_artifacts_are_forced_response"
                ),
                "limit_recovery_action": recovery.get("action"),
                "bf_metadata_cue_sha256": forcing.get("cue_sha256"),
                "forced_finish_reason": forcing.get("forced_finish_reason"),
            })
            return result
        except BaseException as error:
            event["status"] = "error"
            event["error_type"] = type(error).__name__
            event["error"] = str(error)
            if isinstance(error, PolicyError):
                latch(error)
            raise
        finally:
            if token is not None:
                active.reset(token)
            event["finished_at"] = _now()
            event["elapsed_seconds"] = time.monotonic() - started
            record(event)

    body_error = None
    try:
        path = Path(event_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        stream = path.open("x", encoding="utf-8")
        bf_module.continuation_instruction = instruction
        bf_module._continue_primary = continue_primary
        patched = True
        try:
            yield
        except BaseException as error:
            body_error = error
            raise
        finally:
            if failure and not isinstance(body_error, (PolicyError, KeyboardInterrupt, SystemExit)):
                raise failure[0] from body_error
    finally:
        if patched:
            bf_module._continue_primary = original_continue
            bf_module.continuation_instruction = original_instruction
        if stream is not None:
            stream.close()
        with _INSTALL_LOCK:
            _INSTALLED_MODULES.discard(module_id)
