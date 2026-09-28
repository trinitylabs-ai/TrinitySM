"""Generic post-cap recovery: bounded allowance and a clean continuation prefix.

Examines saved output after a length stop. No live stopper, sampling changes,
problem knowledge, model calls or tokenizer calls are involved.
"""
from __future__ import annotations

import hashlib
import re
from typing import Any

POLICY_ID = "cap-recovery-65k-prefix-v1"
MAX_RETRY_TOKENS = 65_536
MIN_REPEATS = 4
MAX_PERIOD_WORDS = 256
MIN_REPEATED_CHARACTERS = 256


def retry_max_tokens(primary_cap: int) -> int:
    if primary_cap < 1:
        raise ValueError("The original output cap must be positive")
    return min(2 * primary_cap, MAX_RETRY_TOKENS)


def recovery_limit(result: dict[str, Any], fallback: int) -> int:
    """Double the physical request that hit its cap (including a BF floor)."""
    cap = result.get("metadata", {}).get("config", {}).get("max_tokens", fallback)
    return retry_max_tokens(int(cap))


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def trim_repeated_suffix(text: str) -> tuple[str, dict[str, Any]]:
    """Find an exact periodic suffix; cut at the newline before its first copy.

    Match whitespace-separated words (not model tokens). Allow one incomplete
    final token at the cap. Require four copies spanning at least 256 characters.
    Earlier repetition followed by substantive new text is not a suffix loop.
    """
    spans = list(re.finditer(r"\S+", text))
    words = [m.group() for m in spans]
    candidates = []
    for omitted in (0, 1):
        end = len(words) - omitted
        for period in range(1, min(MAX_PERIOD_WORDS, end // MIN_REPEATS) + 1):
            if omitted and not (words[end - period].startswith(words[end])
                                and words[end - period] != words[end]):
                continue
            i = end - 1
            while i >= period and words[i] == words[i - period]:
                i -= 1
            start = i - period + 1
            size = end - start
            if size < MIN_REPEATS * period:
                continue
            char_start = spans[start].start()
            if spans[end - 1].end() - char_start < MIN_REPEATED_CHARACTERS:
                continue
            candidates.append((char_start, period, size // period, omitted))
    if not candidates:
        return text, {"detected": False, "policy": POLICY_ID}
    start, period, repeats, omitted = min(candidates)
    boundary = text.rfind("\n", 0, start) + 1
    prefix = text[:boundary]
    return prefix, {
        "detected": True, "policy": POLICY_ID,
        "period_words": period, "complete_repeats": repeats,
        "ignored_partial_tail_tokens": omitted, "repeat_start_char": start,
        "kept_characters": boundary, "removed_characters": len(text) - boundary,
        "original_sha256": _sha(text), "prefix_sha256": _sha(prefix),
        "boundary": "last_complete_newline_before_first_repeated_block",
    }


def clean_capped_result(result: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Retain only output preceding a repetition loop in generation order."""
    audit: dict[str, Any] = {"policy": POLICY_ID, "detected": False}
    if result.get("metadata", {}).get("finish_reason") != "length":
        return result, audit
    saved = result.get("metadata", {}).get("cap_repetition_cleanup")
    if isinstance(saved, dict) and saved.get("detected"):
        return result, saved
    for channel in ("reasoning", "text"):
        text = str(result.get(channel) or "")
        prefix, detail = trim_repeated_suffix(text)
        if detail["detected"]:
            cleaned = {**result, channel: prefix}
            if channel == "reasoning":
                cleaned["text"] = ""  # Final content follows the reasoning loop.
            return cleaned, {**detail, "channel": channel}
    return result, audit


def policy_manifest() -> dict[str, Any]:
    return {
        "policy": POLICY_ID, "retry_cap": "min(2 * primary_cap, 65536)",
        "max_retry_tokens": MAX_RETRY_TOKENS, "min_repeats": MIN_REPEATS,
        "max_period_words": MAX_PERIOD_WORDS,
        "min_repeated_characters": MIN_REPEATED_CHARACTERS,
        "inspection": "post-length-stop, reasoning then final content",
        "retry_input": "original task plus prefix ending at newline before repetition",
        "new_live_repetition_stopper": False,
    }
