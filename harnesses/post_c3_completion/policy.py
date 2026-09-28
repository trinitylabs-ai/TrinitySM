"""Independent, process-local cue routing around the original frozen chat BF.

No engine imports, token-budget changes, new BF loop, or native-prefix transport
are introduced here.  The worker installs this once around each completed batch
of exact prompt bindings, and joins its lane threads before leaving the context.
"""
from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
from functools import wraps
import hashlib
import json
from pathlib import Path
import re
import threading
import time
from typing import Mapping

from .prompts import EXPANSION_CONTINUATION, LAZY_CONTINUATION

POLICY_ID = "post-c3-completion-chat-bf-v1"
CUES = {"lazy_check": LAZY_CONTINUATION, "expansion": EXPANSION_CONTINUATION}
_INSTALL_LOCK = threading.Lock()
_INSTALLED = set()


class PolicyError(RuntimeError):
    """The experimental BF policy or its audit evidence is inconsistent."""


class RouteError(PolicyError):
    """A stage and exact system prompt do not identify one permitted role."""


def _sha(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _now():
    return datetime.now(timezone.utc).isoformat()


def _config(value):
    return {name: value.get(name) if isinstance(value, Mapping) else getattr(value, name, None)
            for name in ("seed", "temperature", "max_tokens", "top_p", "top_k",
                         "reasoning_effort", "thinking_token_budget", "timeout_seconds")}


def _metadata(value):
    result = value.get("metadata") if isinstance(value, Mapping) else None
    return result if isinstance(result, Mapping) else {}


def _hash_field(value, field):
    return _sha(str(value.get(field) or "")) if isinstance(value, Mapping) else _sha("")


def _routes(routes):
    bound = []
    for route in routes:
        if not isinstance(route, Mapping) or set(route) != {"role", "stage_pattern", "prompt_sha256"}:
            raise PolicyError("routes require role, stage_pattern and prompt_sha256 only")
        role, pattern, sha = (route[key] for key in ("role", "stage_pattern", "prompt_sha256"))
        if role not in CUES or not isinstance(pattern, str) or not pattern:
            raise PolicyError("unknown role or empty stage pattern")
        if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha):
            raise PolicyError("prompt_sha256 must be an exact lowercase SHA-256 digest")
        try:
            re.compile(pattern)
        except re.error as error:
            raise PolicyError("invalid stage pattern") from error
        entry = (role, pattern, sha)
        # Identical proof texts can legitimately produce identical lane routes.
        if entry not in bound:
            bound.append(entry)
    if not bound:
        raise PolicyError("at least one exact prompt route is required")
    return tuple(bound)


@contextmanager
def install(bf_module, event_path, *, routes):
    """Override only the instruction used by one original _continue_primary.

    Routes are snapshotted on entry. Unknown/ambiguous routes are fatal, including
    when inherited recovery code catches their exception; the first policy error
    is latched and raised again on context exit. Out-of-context utility calls keep
    the original continuation instruction.
    """
    bound = _routes(routes)
    original_continue = getattr(bf_module, "_continue_primary", None)
    original_instruction = getattr(bf_module, "continuation_instruction", None)
    if not callable(original_continue) or not callable(original_instruction):
        raise PolicyError("expected the two original BF continuation hooks")
    module_id = id(bf_module)
    with _INSTALL_LOCK:
        if module_id in _INSTALLED:
            raise PolicyError("BF policy already installed on this module")
        _INSTALLED.add(module_id)

    active = ContextVar("post_c3_bf_role", default=None)
    lock, failures = threading.Lock(), []
    stream, patched, body_error, sequence = None, False, None, 0

    def latch(error):
        with lock:
            if not failures:
                failures.append(error)

    def record(event):
        nonlocal sequence
        with lock:
            sequence += 1
            event["event_index"] = sequence
            try:
                stream.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
                stream.flush()
            except Exception as error:
                failure = PolicyError("could not persist BF continuation audit")
                if not failures:
                    failures.append(failure)
                raise failure from error

    @wraps(original_instruction)
    def instruction(config):
        event = active.get()
        if event is None:
            return original_instruction(config)
        cue = CUES[event["role"]]
        event.update(cue=cue, cue_sha256=_sha(cue), cue_applied=True)
        event["cue_call_count"] += 1
        return cue

    @wraps(original_continue)
    def continue_primary(*, primary, kwargs, **optional):
        began, token = time.monotonic(), None
        stage, prompt = kwargs.get("stage"), kwargs.get("prompt")
        event = {
            "schema": POLICY_ID, "stage": stage, "role": None,
            "prompt_sha256": _sha(prompt) if isinstance(prompt, str) else None,
            "cue": None, "cue_sha256": None, "cue_applied": False, "cue_call_count": 0,
            "config": _config(kwargs.get("config")), "model": kwargs.get("model"),
            "artifact_path": str(kwargs.get("output_dir", "")),
            "primary_text_sha256": _hash_field(primary, "text"),
            "primary_reasoning_sha256": _hash_field(primary, "reasoning"),
            "primary_finish_reason": _metadata(primary).get("finish_reason"),
            "primary_generation_reused": bool(optional.get("reused_primary", False)),
            "started_at": _now(), "status": "running",
        }
        try:
            with lock:
                previous = failures[0] if failures else None
            if previous is not None:
                raise previous
            if not isinstance(stage, str) or not isinstance(prompt, str):
                raise RouteError("BF routing requires a string stage and system prompt")
            matches = [role for role, pattern, sha in bound
                       if re.fullmatch(pattern, stage) and sha == event["prompt_sha256"]]
            if len(matches) != 1:
                raise RouteError(f"BF stage/prompt must match exactly one route: {stage!r}; matches={len(matches)}")
            event["role"] = matches[0]
            token = active.set(event)
            # One inherited call performs the existing preserved-reasoning-and-
            # response chat continuation; no second loop or transport is added.
            result = original_continue(primary=primary, kwargs=kwargs, **optional)
            metadata = _metadata(result)
            bf = metadata.get("v0257_budget_forcing")
            if (event["cue_call_count"] != 1 or not isinstance(bf, Mapping)
                    or bf.get("cue_sha256") != event["cue_sha256"]):
                raise PolicyError("returned BF evidence does not bind to exactly one applied role cue")
            recovery = metadata.get("limit_recovery") or {}
            event.update(
                status="returned", response_config=_config(metadata.get("config")),
                response_finish_reason=metadata.get("finish_reason"),
                response_text_sha256=_hash_field(result, "text"),
                response_reasoning_sha256=_hash_field(result, "reasoning"),
                bf_metadata_cue_sha256=bf.get("cue_sha256"),
                canonical_source=bf.get("canonical_source"),
                canonical_artifacts_are_forced_response=bf.get("canonical_artifacts_are_forced_response"),
                forced_finish_reason=bf.get("forced_finish_reason"),
                limit_recovery_action=recovery.get("action") if isinstance(recovery, Mapping) else None,
            )
            return result
        except BaseException as error:
            event.update(status="error", error_type=type(error).__name__, error=str(error))
            if isinstance(error, PolicyError):
                latch(error)
            raise
        finally:
            if token is not None:
                active.reset(token)
            event.update(finished_at=_now(), elapsed_seconds=time.monotonic() - began)
            record(event)

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
            if failures and not isinstance(body_error, (PolicyError, KeyboardInterrupt, SystemExit)):
                raise failures[0] from body_error
    finally:
        if patched:
            bf_module._continue_primary = original_continue
            bf_module.continuation_instruction = original_instruction
        try:
            if stream is not None:
                stream.close()
        finally:
            with _INSTALL_LOCK:
                _INSTALLED.discard(module_id)
