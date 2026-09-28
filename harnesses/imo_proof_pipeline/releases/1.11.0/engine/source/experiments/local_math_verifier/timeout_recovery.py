"""Recorded timeout recovery; never treat an incomplete stream as a final answer."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import time
from typing import Any

from .cap_recovery import trim_repeated_suffix


POLICY_ID = "timeout-600s-prefix-or-primary-v1"
WALL_TIMEOUT_SECONDS = 600
MAX_REPETITION_RETRIES = 1
CONTINUATION = (
    "Continue from the preserved output above and complete the original task. "
    "Return one complete response in the originally required format."
)


class GenerationTimeout(TimeoutError):
    def __init__(self, partial: dict[str, Any], evidence: dict[str, Any]):
        super().__init__(f"generation exceeded {evidence['wall_timeout_seconds']} seconds")
        self.partial = partial
        self.evidence = evidence


class TimeoutRecoveryFailure(RuntimeError):
    """Terminal for this call: inherited generic retries must not restart it."""


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _trim_char_loop(text: str) -> tuple[str, dict[str, Any]]:
    # Character periods also catch unseparated loops such as token ID 0 ('!').
    original_length = len(text)
    text = text.rstrip()
    candidates = []
    for period in range(1, min(512, len(text) // 8) + 1):
        i = len(text) - 1
        while i >= period and text[i] == text[i - period]:
            i -= 1
        start = i - period + 1
        count = len(text) - start
        if count >= max(128, period * 8):
            candidates.append((start, period, count // period))
    if not candidates:
        return text, {"detected": False}
    start, period, repeats = min(candidates)
    boundary = text.rfind("\n", 0, start) + 1
    return text[:boundary], {"detected": True, "detector": "character_period",
        "period_characters": period, "complete_repeats": repeats,
        "repeat_start_char": start, "kept_characters": boundary,
        "removed_characters": original_length - boundary}


def trim_loop(text: str) -> tuple[str, dict[str, Any]]:
    word_prefix, word = trim_repeated_suffix(text)
    char_prefix, char = _trim_char_loop(text)
    detected = [(word_prefix, word), (char_prefix, char)]
    detected = [item for item in detected if item[1]["detected"]]
    if not detected:
        return text, {"detected": False, "policy": POLICY_ID}
    prefix, detail = min(detected, key=lambda item: item[1]["repeat_start_char"])
    return prefix, {**detail, "policy": POLICY_ID, "original_sha256": sha(text),
                    "prefix_sha256": sha(prefix),
                    "boundary": "last_newline_before_repetition_start"}


def clean_timeout_result(result: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    for channel in ("reasoning", "text"):
        prefix, detail = trim_loop(str(result.get(channel) or ""))
        if detail["detected"]:
            cleaned = {**result, channel: prefix}
            if channel == "reasoning":
                cleaned["text"] = ""
            return cleaned, {**detail, "channel": channel}
    return result, {"detected": False, "policy": POLICY_ID}


def reusable(result: dict[str, Any]) -> str:
    parts = []
    for key, label in (("reasoning", "Preserved reasoning"), ("text", "Preserved response")):
        text = str(result.get(key) or "").rstrip()
        if text:
            parts.append(f"[{label}]\n{text}")
    return "\n\n".join(parts)


def read_stream(response: Any, *, request: dict[str, Any], output_dir: Path,
                stage: str, started: float, wall_timeout: float) -> dict[str, Any]:
    """Save every delta, imposing a wall deadline even while tokens keep arriving."""
    reasoning, content, token_ids = [], [], []
    finish = None
    response_id = None
    usage: dict[str, Any] = {}
    stream_path = output_dir / f"{stage}.stream.jsonl"
    timed_out = False
    with stream_path.open("w", encoding="utf-8") as journal:
        try:
            while True:
                remaining = wall_timeout - (time.monotonic() - started)
                if remaining <= 0:
                    raise TimeoutError("wall deadline reached")
                try:
                    response.fp.raw._sock.settimeout(remaining)
                except AttributeError:
                    pass  # In-memory offline transport fixtures.
                line = response.readline()
                if not line:
                    break
                if not line.startswith(b"data: "):
                    continue
                payload = line[6:].strip()
                if payload == b"[DONE]":
                    break
                event = json.loads(payload)
                journal.write(json.dumps(event, ensure_ascii=False) + "\n")
                journal.flush()
                if "error" in event:
                    raise RuntimeError(f"stream server error: {event['error']}")
                response_id = event.get("id", response_id)
                if event.get("usage"):
                    usage = event["usage"]
                for choice in event.get("choices", []):
                    if choice.get("index", 0) != 0:
                        raise ValueError("expected a single generation choice")
                    delta = choice.get("delta") or {}
                    reasoning.append(delta.get("reasoning") or delta.get("reasoning_content") or "")
                    content.append(delta.get("content") or "")
                    token_ids.extend(choice.get("token_ids") or [])
                    finish = choice.get("finish_reason") or finish
        except TimeoutError:
            timed_out = True
    raw = {"id": response_id, "object": "chat.completion", "model": request["model"],
           "choices": [{"index": 0, "message": {"role": "assistant",
               "content": "".join(content), "reasoning": "".join(reasoning)},
               "finish_reason": finish, "token_ids": token_ids}], "usage": usage}
    if timed_out:
        partial = {"text": "".join(content), "reasoning": "".join(reasoning),
                   "metadata": {"finish_reason": "timeout", "usage": usage},
                   "token_ids": token_ids}
        partial_path = output_dir / f"{stage}.timeout.partial.json"
        partial_path.write_text(json.dumps(raw, ensure_ascii=False, indent=2) + "\n")
        evidence = {"policy": POLICY_ID, "state": "timeout", "wall_timeout_seconds": wall_timeout,
                    "elapsed_seconds": time.monotonic() - started, "stream_path": str(stream_path.resolve()),
                    "partial_path": str(partial_path.resolve()), "partial_sha256": hashlib.sha256(partial_path.read_bytes()).hexdigest(),
                    "observed_tokens": len(token_ids)}
        (output_dir / f"{stage}.timeout.json").write_text(json.dumps(evidence, indent=2) + "\n")
        raise GenerationTimeout(partial, evidence)
    if finish is None:
        raise RuntimeError("stream ended without a terminal finish reason")
    return raw


def primary_eligible(primary: dict[str, Any] | None) -> bool:
    if not primary or primary.get("metadata", {}).get("finish_reason") != "stop":
        return False
    if not str(primary.get("text") or "").strip():
        return False
    return not clean_timeout_result(primary)[1]["detected"]


def is_primary_fallback(metadata: dict[str, Any]) -> bool:
    from .limit_recovery import FALLBACK_SOURCE
    return (metadata.get("v0257_budget_forcing") or {}).get("canonical_source") == FALLBACK_SOURCE


def has_limit_recovery(metadata: dict[str, Any]) -> bool:
    return is_primary_fallback(metadata) or bool(metadata.get("limit_retry"))


def require_valid_fallback(metadata: dict[str, Any], parsed: dict[str, Any]) -> None:
    if has_limit_recovery(metadata) and not parsed.get("valid"):
        raise TimeoutRecoveryFailure("limit recovery response failed the existing stage validator")


def canonical_hash(event: dict[str, Any]) -> str:
    from .limit_recovery import FALLBACK_SOURCE
    key = "canonical_text_sha256" if event.get("canonical_source") == FALLBACK_SOURCE else "forced_text_sha256"
    return str(event.get(key) or "")


def canonical_allowed(event: dict[str, Any]) -> bool:
    from . import limit_recovery as limits
    if event.get("canonical_artifacts_are_forced_response") is True:
        return True
    recovery = event.get("limit_recovery") or {}
    return (event.get("canonical_artifacts_are_forced_response") is False
            and event.get("canonical_source") == limits.FALLBACK_SOURCE
            and recovery.get("policy") == limits.POLICY_ID
            and recovery.get("phase") == "budget_forcing"
            and recovery.get("action") == "primary_fallback"
            and recovery.get("repetition_detected") is False
            and event.get("primary_finish_reason") == "stop"
            and bool(event.get("canonical_text_sha256"))
            and event.get("canonical_text_sha256") == event.get("primary_text_sha256"))


def verify_fallback_artifacts(metadata: dict[str, Any], directory: Path, stage: str) -> None:
    from . import limit_recovery as limits
    limits.verify_retry(metadata, directory)
    event = metadata.get("v0257_budget_forcing") or {}
    if not is_primary_fallback(metadata):
        return
    if not canonical_allowed(event):
        raise ValueError("invalid limit fallback policy event")
    recovery = event["limit_recovery"]
    partial = limits.read_evidence(recovery["evidence"], directory)
    if clean_timeout_result(partial)[1]["detected"]:
        raise ValueError("primary fallback followed repetition at a limit")
    primary = json.loads((directory / f"{stage}.pre_budget_forcing.raw_response.json").read_text())
    choice, msg = primary["choices"][0], primary["choices"][0]["message"]
    if (choice.get("finish_reason") != "stop" or sha(str(msg.get("content") or "").strip()) != canonical_hash(event)
            or clean_timeout_result({"text": msg.get("content", ""), "reasoning": msg.get("reasoning_content") or msg.get("reasoning", "")})[1]["detected"]):
        raise ValueError("limit fallback does not match a completed nonrepetitive preserved primary")


def policy_manifest() -> dict[str, Any]:
    from .limit_recovery import policy_manifest as manifest
    return manifest()
