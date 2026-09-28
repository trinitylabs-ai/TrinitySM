#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import traceback
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.run_v0183_gemma_bridge_certificate_portfolio_20260904 as v0183


HARNESS_VERSION = "v0.3.184-gemma-s1-exact-bridge-budget-forcing-20260904"
DEFAULT_SOURCE_CALL_DIR = (
    ROOT
    / "runs/v0183_gemma_bridge_certificate_pilot_20260904"
    / "search_precise/model_call"
)
DEFAULT_OUTPUT = ROOT / "runs/v0184_gemma_s1_bridge_budget_forcing_20260904"
MODEL_ID = "google/gemma-4-31B-it"
FORCING_CUE = "Wait"
MAX_TOKENS_PER_CONTINUATION = 32_000
DEFAULT_STEPS = 2


def utc_now() -> str:
    return v0183.utc_now()


def write_json(path: Path, value: Any) -> None:
    v0183.write_json(path, value)


def write_text(path: Path, value: str) -> None:
    v0183.write_text(path, value)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalize_nonempty(value: str, label: str) -> str:
    normalized = value.replace("\r\n", "\n").strip()
    if not normalized:
        raise ValueError(f"empty {label}")
    return normalized


def gemma_reasoning_prefix(system_prompt: str, user_prompt: str) -> str:
    """Render the canonical simple system/user Gemma4 thinking prefix.

    The deployed canonical template emits exactly this prefix for one string
    system message, one string user message, and thinking enabled.  Ending
    inside the thought channel is essential: chat-level
    ``continue_final_message`` closes that channel before generation.
    """

    system = normalize_nonempty(system_prompt, "system prompt")
    user = normalize_nonempty(user_prompt, "user prompt")
    return (
        "<bos><|turn>system\n<|think|>\n"
        + system
        + "<turn|>\n<|turn>user\n"
        + user
        + "<turn|>\n<|turn>model\n<|channel>thought\n"
    )


def forced_reasoning_prompt(
    system_prompt: str,
    user_prompt: str,
    accumulated_reasoning: str,
    cue: str = FORCING_CUE,
) -> str:
    reasoning = normalize_nonempty(accumulated_reasoning, "accumulated reasoning")
    forcing_cue = normalize_nonempty(cue, "forcing cue")
    return gemma_reasoning_prefix(system_prompt, user_prompt) + reasoning + "\n" + forcing_cue


def build_completion_request(
    *,
    model: str,
    raw_prompt: str,
    max_tokens: int,
    seed: int,
    temperature: float,
    top_p: float,
    top_k: int,
) -> dict[str, Any]:
    if max_tokens <= 0:
        raise ValueError("max_tokens must be positive")
    return {
        "model": model,
        "prompt": raw_prompt,
        "add_special_tokens": False,
        "skip_special_tokens": False,
        "spaces_between_special_tokens": False,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
        "seed": seed,
    }


def parse_raw_continuation(value: str) -> dict[str, Any]:
    """Split output generated from inside Gemma's open thought channel."""

    normalized = value.replace("\r\n", "\n")
    turn_closed = "<turn|>" in normalized
    if "<channel|>" not in normalized:
        return {
            "reasoning": normalized.strip(),
            "content": "",
            "thought_channel_closed": False,
            "turn_closed": turn_closed,
        }
    reasoning, remainder = normalized.split("<channel|>", 1)
    content = remainder.split("<turn|>", 1)[0].strip()
    return {
        "reasoning": reasoning.strip(),
        "content": content,
        "thought_channel_closed": True,
        "turn_closed": turn_closed,
    }


def append_forced_reasoning(
    accumulated_reasoning: str,
    new_reasoning: str,
    cue: str = FORCING_CUE,
) -> str:
    prior = normalize_nonempty(accumulated_reasoning, "accumulated reasoning")
    forcing_cue = normalize_nonempty(cue, "forcing cue")
    continuation = new_reasoning.replace("\r\n", "\n").strip()
    result = prior + "\n" + forcing_cue
    if continuation:
        result += "\n" + continuation
    return result


def parse_bridge_claim(value: str) -> dict[str, Any]:
    if not value.strip():
        return {"status": "NO_VISIBLE_ANSWER"}
    try:
        return v0183.parse_bridge_output(value)
    except Exception as error:
        return {
            "status": "MALFORMED",
            "error": f"{type(error).__name__}: {error}",
        }


def http_post_json(url: str, body: dict[str, Any], timeout_seconds: int) -> dict[str, Any]:
    payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        headers={"Authorization": "Bearer EMPTY", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            response_bytes = response.read()
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {error.code}: {detail}") from error
    value = json.loads(response_bytes.decode("utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("endpoint returned a non-object response")
    return value


def extract_completion(raw: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
    choices = raw.get("choices") or []
    if len(choices) != 1:
        raise RuntimeError(f"expected one completion choice, got {len(choices)}")
    choice = choices[0]
    text = str(choice.get("text") or "")
    finish_reason = str(choice.get("finish_reason") or "")
    usage = dict(raw.get("usage") or {})
    return text, finish_reason, usage


def load_source_call(source_call_dir: Path) -> dict[str, Any]:
    system_prompt = normalize_nonempty(
        (source_call_dir / "gemma_bridge_search.prompt.txt").read_text(encoding="utf-8"),
        "source system prompt",
    )
    user_prompt = normalize_nonempty(
        (source_call_dir / "gemma_bridge_search.user_prompt.txt").read_text(encoding="utf-8"),
        "source user prompt",
    )
    reasoning = normalize_nonempty(
        (source_call_dir / "gemma_bridge_search.reasoning.txt").read_text(encoding="utf-8"),
        "source reasoning",
    )
    raw = json.loads(
        (source_call_dir / "gemma_bridge_search.raw_response.json").read_text(
            encoding="utf-8"
        )
    )
    metadata = json.loads(
        (source_call_dir / "gemma_bridge_search.metadata.json").read_text(
            encoding="utf-8"
        )
    )
    choices = raw.get("choices") or []
    if len(choices) != 1:
        raise ValueError("source call must have exactly one choice")
    message = choices[0].get("message") or {}
    raw_reasoning = str(message.get("reasoning") or message.get("reasoning_content") or "").strip()
    if raw_reasoning != reasoning:
        raise ValueError("source reasoning artifact does not match raw response")
    content = str(message.get("content") or "").strip()
    config = dict(metadata.get("config") or {})
    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "reasoning": reasoning,
        "content": content,
        "model": str(raw.get("model") or MODEL_ID),
        "seed": int(config.get("seed") or 0),
        "temperature": float(config.get("temperature") or 0.0),
        "top_p": float(config.get("top_p") or 1.0),
        "top_k": int(config.get("top_k") or -1),
        "finish_reason": str(choices[0].get("finish_reason") or ""),
        "usage": dict(raw.get("usage") or {}),
    }


def run_forcing_step(
    *,
    endpoint: str,
    destination: Path,
    step: int,
    source: dict[str, Any],
    accumulated_reasoning: str,
    max_tokens: int,
    temperature: float,
    top_p: float,
    top_k: int,
    timeout_seconds: int,
    cue: str = FORCING_CUE,
) -> dict[str, Any]:
    step_dir = destination / f"s1_{step}"
    raw_prompt = forced_reasoning_prompt(
        source["system_prompt"], source["user_prompt"], accumulated_reasoning, cue
    )
    request_body = build_completion_request(
        model=source["model"],
        raw_prompt=raw_prompt,
        max_tokens=max_tokens,
        seed=int(source["seed"]),
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
    )
    write_json(step_dir / "request.json", request_body)
    started = time.perf_counter()
    raw = http_post_json(
        endpoint.rstrip("/") + "/completions",
        request_body,
        timeout_seconds,
    )
    elapsed = time.perf_counter() - started
    write_json(step_dir / "raw_response.json", raw)
    completion, finish_reason, usage = extract_completion(raw)
    parsed = parse_raw_continuation(completion)
    new_reasoning = str(parsed["reasoning"])
    content = str(parsed["content"])
    next_accumulated = append_forced_reasoning(accumulated_reasoning, new_reasoning, cue)
    write_text(step_dir / "raw_continuation.txt", completion)
    write_text(step_dir / "new_reasoning.txt", new_reasoning + ("\n" if new_reasoning else ""))
    write_text(step_dir / "accumulated_reasoning.txt", next_accumulated + "\n")
    write_text(step_dir / "bridge.txt", content + ("\n" if content else ""))
    summary = {
        "step": step,
        "forcing_cue": cue,
        "continuation_method": "raw_completion_inside_open_thought_channel",
        "new_user_turn_added": False,
        "prior_visible_answer_included": False,
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
        "max_tokens": max_tokens,
        "finish_reason": finish_reason,
        "usage": usage,
        "latency_seconds": elapsed,
        "raw_prompt_sha256": sha256_text(raw_prompt),
        "prior_reasoning_sha256": sha256_text(accumulated_reasoning),
        "new_reasoning_sha256": sha256_text(new_reasoning),
        "new_reasoning_characters": len(new_reasoning),
        "accumulated_reasoning_characters": len(next_accumulated),
        "thought_channel_closed": bool(parsed["thought_channel_closed"]),
        "turn_closed": bool(parsed["turn_closed"]),
        "visible_answer_characters": len(content),
        "bridge_parse": parse_bridge_claim(content),
    }
    write_json(step_dir / "summary.json", summary)
    return {**summary, "accumulated_reasoning": next_accumulated, "content": content}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Continue a Gemma bridge trace with exact s1-style budget forcing"
    )
    parser.add_argument("--source-call-dir", type=Path, default=DEFAULT_SOURCE_CALL_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--endpoint", default="http://127.0.0.1:8030/v1")
    parser.add_argument("--steps", type=int, default=DEFAULT_STEPS)
    parser.add_argument("--max-tokens", type=int, default=MAX_TOKENS_PER_CONTINUATION)
    parser.add_argument("--temperature", type=float)
    parser.add_argument("--top-p", type=float)
    parser.add_argument("--top-k", type=int)
    parser.add_argument("--timeout-seconds", type=int, default=14_400)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.steps <= 8:
        raise ValueError("--steps must be between 1 and 8")
    if args.max_tokens <= 0:
        raise ValueError("--max-tokens must be positive")

    source_call_dir = args.source_call_dir.resolve()
    source = load_source_call(source_call_dir)
    temperature = source["temperature"] if args.temperature is None else args.temperature
    top_p = source["top_p"] if args.top_p is None else args.top_p
    top_k = source["top_k"] if args.top_k is None else args.top_k
    preflight = {
        "schema": "cognitive-well-v0184-gemma-s1-preflight-v1",
        "state": "validated",
        "harness_version": HARNESS_VERSION,
        "source_call_dir": str(source_call_dir),
        "source_system_prompt_sha256": sha256_text(source["system_prompt"]),
        "source_user_prompt_sha256": sha256_text(source["user_prompt"]),
        "source_reasoning_sha256": sha256_text(source["reasoning"]),
        "source_reasoning_characters": len(source["reasoning"]),
        "source_visible_answer": source["content"],
        "source_finish_reason": source["finish_reason"],
        "source_usage": source["usage"],
        "model": source["model"],
        "endpoint": args.endpoint,
        "steps": args.steps,
        "max_tokens_per_continuation": args.max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
        "forcing_cue": FORCING_CUE,
        "thinking_token_budget": None,
        "reasoning_effort": "unbounded_by_s1_continuation",
        "exact_same_turn_continuation": True,
        "proof_rewrite_performed": False,
    }
    if args.dry_run:
        print(json.dumps(preflight, ensure_ascii=False, indent=2))
        return 0

    destination = args.output_dir.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    write_json(destination / "manifest.json", {**preflight, "created_at": utc_now()})
    write_json(
        destination / "status.json",
        {"state": "running", "stage": "s1_1", "updated_at": utc_now()},
    )
    write_text(destination / "control_bridge.txt", source["content"] + "\n")
    try:
        accumulated = source["reasoning"]
        rows: list[dict[str, Any]] = []
        for step in range(1, args.steps + 1):
            write_json(
                destination / "status.json",
                {"state": "running", "stage": f"s1_{step}", "updated_at": utc_now()},
            )
            row = run_forcing_step(
                endpoint=args.endpoint,
                destination=destination,
                step=step,
                source=source,
                accumulated_reasoning=accumulated,
                max_tokens=args.max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                timeout_seconds=args.timeout_seconds,
            )
            accumulated = row.pop("accumulated_reasoning")
            row.pop("content")
            rows.append(row)
        result = {
            "schema": "cognitive-well-v0184-gemma-s1-result-v1",
            "state": "completed",
            "harness_version": HARNESS_VERSION,
            "control": {
                "bridge_parse": parse_bridge_claim(source["content"]),
                "finish_reason": source["finish_reason"],
                "usage": source["usage"],
            },
            "forcing_steps": rows,
            "proof_rewrite_performed": False,
            "completed_at": utc_now(),
        }
        write_json(destination / "result.json", result)
        write_json(
            destination / "status.json",
            {"state": "completed", "stage": f"s1_{args.steps}_done", "updated_at": utc_now()},
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as error:
        write_json(
            destination / "status.json",
            {
                "state": "failed_closed",
                "stage": "mechanical_failure",
                "error": f"{type(error).__name__}: {error}",
                "traceback": traceback.format_exc(),
                "updated_at": utc_now(),
            },
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
