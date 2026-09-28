from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def render_template(template: str, **values: str) -> str:
    declared = set(re.findall(r"\{\{([A-Z][A-Z0-9_]*)\}\}", template))
    supplied = {key.upper() for key in values}
    missing = declared - supplied
    extra = supplied - declared
    if missing:
        raise ValueError(f"prompt template has unresolved placeholders: {sorted(missing)}")
    if extra:
        raise ValueError(f"prompt template does not declare placeholders: {sorted(extra)}")
    rendered = template
    for key, value in values.items():
        marker = "{{" + key.upper() + "}}"
        rendered = rendered.replace(marker, value)
    return rendered


def prepare_new_output_dir(path: Path) -> None:
    if path.exists() and any(path.iterdir()):
        raise FileExistsError(f"refusing to reuse nonempty output directory: {path}")
    path.mkdir(parents=True, exist_ok=True)


def resolve_llama_binary(explicit: str | None = None) -> str:
    if explicit:
        candidate = Path(explicit).expanduser()
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate.resolve())
        found = shutil.which(explicit)
        if found:
            return found
        raise FileNotFoundError(f"llama runtime is not executable: {explicit}")
    for name in ("llama-cli", "llama-completion"):
        found = shutil.which(name)
        if found:
            return found
    raise FileNotFoundError("neither llama-cli nor llama-completion is on PATH")


def runtime_help(binary: str) -> str:
    completed = subprocess.run(
        [binary, "--help"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return completed.stdout


def runtime_version(binary: str) -> str:
    completed = subprocess.run(
        [binary, "--version"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return completed.stdout.strip()


@dataclass(frozen=True)
class GenerationConfig:
    ctx_size: int
    predict: int
    threads: int
    gpu_layers: int
    batch_size: int
    ubatch_size: int
    temperature: float = 0.2
    seed: int = 20260820
    reasoning_budget: int | None = None
    cuda_visible_devices: str | None = None


@dataclass(frozen=True)
class HTTPGenerationConfig:
    max_tokens: int
    temperature: float = 0.7
    top_p: float = 0.95
    top_k: int = 64
    min_p: float | None = None
    presence_penalty: float | None = None
    repetition_penalty: float | None = None
    repetition_detection: dict[str, int] | None = None
    seed: int = 20260820
    thinking_token_budget: int | None = 3_000
    reasoning_effort: str | None = None
    thinking_enabled: bool = True
    response_format: dict[str, Any] | None = None
    structured_outputs: dict[str, Any] | None = None
    timeout_seconds: int | None = 7_200


def require_loopback_endpoint(endpoint: str) -> str:
    normalized = endpoint.rstrip("/")
    parsed = urllib.parse.urlparse(normalized)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("OpenAI-compatible endpoint must use http or https")
    if parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("this experiment permits only a loopback Gemma endpoint")
    if not parsed.path.endswith("/v1"):
        raise ValueError("OpenAI-compatible endpoint must end in /v1")
    return normalized


def openai_chat_request(
    *,
    model: str,
    prompt: str,
    config: HTTPGenerationConfig,
    user_prompt: str = "Execute the requested task now.",
    prior_generation: str | None = None,
    continuation_instruction: str | None = None,
) -> dict[str, Any]:
    messages: list[dict[str, str]] = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": user_prompt},
    ]
    if prior_generation is not None:
        if not prior_generation.strip():
            raise ValueError("a continuation requires a nonempty prior generation")
        messages.extend(
            [
                {"role": "assistant", "content": prior_generation},
                {
                    "role": "user",
                    "content": continuation_instruction
                    or (
                        "The preceding assistant response reached its output-token "
                        "cap. Continue exactly where it stopped. Do not restart or "
                        "repeat completed material; output only the missing continuation."
                    ),
                },
            ]
        )
    request: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": config.temperature,
        "top_p": config.top_p,
        "max_tokens": config.max_tokens,
        "seed": config.seed,
        "top_k": config.top_k,
        "chat_template_kwargs": {"enable_thinking": config.thinking_enabled},
    }
    if config.thinking_enabled and config.thinking_token_budget is not None:
        request["thinking_token_budget"] = config.thinking_token_budget
    if config.thinking_enabled and config.reasoning_effort is not None:
        request["reasoning_effort"] = config.reasoning_effort
    if config.min_p is not None:
        request["min_p"] = config.min_p
    if config.presence_penalty is not None:
        request["presence_penalty"] = config.presence_penalty
    if config.repetition_penalty is not None:
        request["repetition_penalty"] = config.repetition_penalty
    if config.repetition_detection is not None:
        request["repetition_detection"] = dict(config.repetition_detection)
    if config.response_format is not None:
        request["response_format"] = config.response_format
    if config.structured_outputs is not None:
        request["structured_outputs"] = config.structured_outputs
    return request


def run_openai_chat_generation(
    *,
    endpoint: str,
    model: str,
    prompt: str,
    output_dir: Path,
    stage: str,
    config: HTTPGenerationConfig,
    user_prompt: str = "Execute the requested task now.",
    prior_generation: str | None = None,
    continuation_instruction: str | None = None,
) -> dict[str, Any]:
    endpoint = require_loopback_endpoint(endpoint)
    prompt_path = output_dir / f"{stage}.prompt.txt"
    user_prompt_path = output_dir / f"{stage}.user_prompt.txt"
    response_path = output_dir / f"{stage}.raw_response.json"
    reasoning_path = output_dir / f"{stage}.reasoning.txt"
    metadata_path = output_dir / f"{stage}.metadata.json"
    prompt_path.write_text(prompt, encoding="utf-8")
    user_prompt_path.write_text(user_prompt, encoding="utf-8")
    request_body = openai_chat_request(
        model=model,
        prompt=prompt,
        config=config,
        user_prompt=user_prompt,
        prior_generation=prior_generation,
        continuation_instruction=continuation_instruction,
    )
    request_bytes = json.dumps(request_body, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        endpoint + "/chat/completions",
        data=request_bytes,
        headers={
            "Authorization": "Bearer EMPTY",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    started_at = utc_now()
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=config.timeout_seconds) as response:
            response_bytes = response.read()
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{stage} HTTP {error.code}: {detail}") from error
    raw = json.loads(response_bytes.decode("utf-8"))
    response_path.write_text(
        json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    choices = raw.get("choices") or []
    if not choices:
        raise RuntimeError(f"{stage} returned no choices")
    choice = choices[0]
    message = choice.get("message") or {}
    text = str(message.get("content") or "").strip()
    reasoning = str(
        message.get("reasoning_content") or message.get("reasoning") or ""
    ).strip()
    reasoning_path.write_text(reasoning + ("\n" if reasoning else ""), encoding="utf-8")
    finish_reason = choice.get("finish_reason")
    metadata = {
        "stage": stage,
        "started_at": started_at,
        "completed_at": utc_now(),
        "latency_seconds": time.perf_counter() - started,
        "transport": "openai-compatible-loopback-http",
        "endpoint": endpoint,
        "model": model,
        "prompt_sha256": sha256_text(prompt),
        "user_prompt_sha256": sha256_text(user_prompt),
        "request_sha256": sha256_text(request_bytes.decode("utf-8")),
        "response_id": raw.get("id"),
        "finish_reason": finish_reason,
        "usage": raw.get("usage") or {},
        "config": asdict(config),
        "message_roles": [
            str(message["role"]) for message in request_body["messages"]
        ],
        "continuation": prior_generation is not None,
        "prior_generation_sha256": (
            sha256_text(prior_generation) if prior_generation is not None else None
        ),
        "system_prompt_path": str(prompt_path.resolve()),
        "user_prompt_path": str(user_prompt_path.resolve()),
        "thinking_enabled": config.thinking_enabled,
        "response_path": str(response_path.resolve()),
        "reasoning_path": str(reasoning_path.resolve()),
    }
    write_json(metadata_path, metadata)
    if not text and finish_reason != "length":
        raise RuntimeError(f"{stage} returned empty final content")
    return {"text": text, "reasoning": reasoning, "metadata": metadata}


def llama_command(
    *,
    binary: str,
    model: Path,
    prompt_path: Path,
    config: GenerationConfig,
    help_text: str,
    output_path: Path | None = None,
) -> list[str]:
    command = [
        binary,
        "--model",
        str(model),
        "--file",
        str(prompt_path),
        "--ctx-size",
        str(config.ctx_size),
        "--n-predict",
        str(config.predict),
        "--threads",
        str(config.threads),
        "--n-gpu-layers",
        str(config.gpu_layers),
        "--batch-size",
        str(config.batch_size),
        "--ubatch-size",
        str(config.ubatch_size),
        "--temp",
        str(config.temperature),
        "--seed",
        str(config.seed),
    ]
    if "--no-display-prompt" in help_text:
        command.append("--no-display-prompt")
    if "--simple-io" in help_text:
        command.append("--simple-io")
    if "--single-turn" in help_text:
        command.append("--single-turn")
    if "--conversation" in help_text:
        command.append("--conversation")
    if config.reasoning_budget is not None and "--reasoning-budget" in help_text:
        command.extend(["--reasoning-budget", str(config.reasoning_budget)])
    if output_path is not None and "--output" in help_text:
        command.extend(["--output", str(output_path)])
    return command


def extract_llama_assistant_text(transcript: str) -> str:
    matches = list(re.finditer(r"(?:^|\n)Assistant:\s*", transcript))
    if not matches:
        return transcript.strip()
    return transcript[matches[-1].end() :].strip()


def extract_final_after_reasoning(text: str) -> str:
    marker = "[End thinking]"
    if marker not in text:
        return text.strip()
    return text.rsplit(marker, 1)[1].strip()


def run_llama_generation(
    *,
    binary: str,
    model: Path,
    prompt: str,
    output_dir: Path,
    stage: str,
    config: GenerationConfig,
    detect_token_cap: bool = False,
) -> dict[str, Any]:
    if not model.is_file() or model.stat().st_size == 0:
        raise FileNotFoundError(f"model is missing or empty: {model}")
    help_text = runtime_help(binary)
    prompt_path = output_dir / f"{stage}.prompt.txt"
    stdout_path = output_dir / f"{stage}.stdout.txt"
    log_path = output_dir / f"{stage}.log"
    transcript_path = output_dir / f"{stage}.transcript.txt"
    metadata_path = output_dir / f"{stage}.metadata.json"
    prompt_path.write_text(prompt, encoding="utf-8")
    command = llama_command(
        binary=binary,
        model=model,
        prompt_path=prompt_path,
        config=config,
        help_text=help_text,
        output_path=transcript_path,
    )
    # llama-cli does not expose an OpenAI-style finish_reason. Its INFO timing
    # line does expose the exact number of predicted tokens without the very
    # large per-token DEBUG stream. Opt in only for callers that need a cap
    # signal so existing experiments retain byte-for-byte command identities.
    if detect_token_cap:
        command.extend(["--log-verbosity", "3"])
    started_at = utc_now()
    environment = None
    if config.cuda_visible_devices is not None:
        environment = dict(os.environ)
        environment["CUDA_VISIBLE_DEVICES"] = config.cuda_visible_devices
    completed = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=environment,
        check=False,
    )
    stdout_path.write_text(completed.stdout, encoding="utf-8")
    log_path.write_text(completed.stderr, encoding="utf-8")
    diagnostic_stream = completed.stdout + "\n" + completed.stderr
    predicted_counts = [
        int(value)
        for value in re.findall(
            r"(?<!prompt )eval time\s*=.*?/\s*(\d+)\s+tokens",
            diagnostic_stream,
        )
    ]
    reached_prediction_cap = bool(
        detect_token_cap
        and (
            re.search(
                r"(?:^|\s)n_remain(?:ing)?\s*[:=]\s*0(?:\s|$)",
                diagnostic_stream,
            )
            or re.search(r"stopped by limit", diagnostic_stream, re.IGNORECASE)
            or re.search(
                r'"finish_reason"\s*:\s*"length"', diagnostic_stream
            )
            or (predicted_counts and predicted_counts[-1] >= config.predict)
        )
        and "[end of text]" not in diagnostic_stream
    )
    metadata = {
        "stage": stage,
        "started_at": started_at,
        "completed_at": utc_now(),
        "returncode": completed.returncode,
        "runtime_binary": binary,
        "runtime_version": runtime_version(binary),
        "model_path": str(model.resolve()),
        "model_size_bytes": model.stat().st_size,
        "prompt_sha256": sha256_text(prompt),
        "config": asdict(config),
        "command": command,
        "cuda_visible_devices": config.cuda_visible_devices,
        "stdout_path": str(stdout_path.resolve()),
        "log_path": str(log_path.resolve()),
        "transcript_path": str(transcript_path.resolve()),
        "finish_reason": "length" if reached_prediction_cap else "stop",
        "token_cap_detection_enabled": detect_token_cap,
        "prediction_cap_reached": reached_prediction_cap,
        "predicted_tokens_observed": (
            predicted_counts[-1] if predicted_counts else None
        ),
    }
    write_json(metadata_path, metadata)
    if completed.returncode != 0:
        raise RuntimeError(
            f"{stage} failed with return code {completed.returncode}; see {log_path}"
        )
    raw_response = (
        transcript_path.read_text(encoding="utf-8")
        if transcript_path.is_file() and transcript_path.stat().st_size > 0
        else completed.stdout
    )
    response = extract_llama_assistant_text(raw_response)
    if not response:
        raise RuntimeError(f"{stage} returned an empty response")
    return {"text": response, "metadata": metadata}
