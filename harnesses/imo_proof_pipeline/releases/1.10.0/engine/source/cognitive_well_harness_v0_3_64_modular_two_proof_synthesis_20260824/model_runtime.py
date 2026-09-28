from __future__ import annotations

from experiments.local_math_verifier.timeout_recovery import has_limit_recovery, TimeoutRecoveryFailure

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from experiments.local_math_verifier.runtime import (
    HTTPGenerationConfig,
    run_openai_chat_generation,
)

from .contracts import safe_name, validate_schema


REPETITION_DETECTION = {
    "min_pattern_size": 8,
    "max_pattern_size": 128,
    "min_count": 3,
}


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def escape_raw_json_control_characters(value: str) -> str:
    result: list[str] = []
    in_string = False
    escaped = False
    for character in value:
        if in_string and ord(character) < 0x20:
            replacements = {
                "\b": "\\b",
                "\f": "\\f",
                "\n": "\\n",
                "\r": "\\r",
                "\t": "\\t",
            }
            result.append(replacements.get(character, f"\\u{ord(character):04x}"))
            escaped = False
            continue
        result.append(character)
        if not in_string:
            if character == '"':
                in_string = True
            continue
        if escaped:
            escaped = False
        elif character == "\\":
            escaped = True
        elif character == '"':
            in_string = False
    return "".join(result)


def parse_json_object(value: str) -> dict[str, Any]:
    text = value.strip()
    if text.startswith("```"):
        text = text[3:]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
        if text.endswith("```"):
            text = text[:-3].strip()
    candidates = [text]
    if text.startswith("{{"):
        candidates.append(text[1:])
    for candidate in candidates:
        for repaired in (candidate, escape_raw_json_control_characters(candidate)):
            try:
                parsed = json.loads(repaired)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                return parsed
    raise ValueError("response is not a valid JSON object")


@dataclass(frozen=True)
class RuntimeConfig:
    gemma_endpoint: str
    qwen_endpoint: str
    gemma_model: str = "google/gemma-4-31B-it"
    qwen_model: str = "Qwen/Qwen3.6-27B"
    master_seed: int = 20260824
    thinking_token_budget: int | None = None
    reasoning_effort: str | None = "max"


class ModelRuntime:
    def __init__(self, config: RuntimeConfig) -> None:
        self.config = config

    def stable_seed(self, label: str) -> int:
        material = f"v064:{self.config.master_seed}:{label}".encode("utf-8")
        return int.from_bytes(hashlib.sha256(material).digest()[:4], "big") or 1

    @staticmethod
    def saved_generation(destination: Path, stage: str) -> dict[str, Any] | None:
        raw_path = destination / f"{stage}.raw_response.json"
        metadata_path = destination / f"{stage}.metadata.json"
        if not raw_path.exists() or not metadata_path.exists():
            return None
        response = json.loads(raw_path.read_text(encoding="utf-8"))
        text = str(response["choices"][0]["message"].get("content") or "")
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        return {"text": text, "metadata": metadata}

    def text(
        self,
        *,
        role: str,
        prompt: str,
        destination: Path,
        stage: str,
        temperature: float,
        max_tokens: int,
        seed_label: str,
        user_prompt: str = "Execute the requested mathematical task now.",
        top_p: float | None = None,
        top_k: int | None = None,
    ) -> dict[str, Any]:
        cached = self.saved_generation(destination, stage)
        if cached is not None:
            return cached
        if role == "gemma":
            endpoint = self.config.gemma_endpoint
            model = self.config.gemma_model
            resolved_top_p = 0.95 if top_p is None else top_p
            resolved_top_k = 64 if top_k is None else top_k
        elif role == "qwen":
            endpoint = self.config.qwen_endpoint
            model = self.config.qwen_model
            resolved_top_p = 1.0 if top_p is None else top_p
            resolved_top_k = -1 if top_k is None else top_k
        else:
            raise ValueError(f"unknown model role: {role}")
        destination.mkdir(parents=True, exist_ok=True)
        return run_openai_chat_generation(
            endpoint=endpoint,
            model=model,
            prompt=prompt,
            user_prompt=user_prompt,
            output_dir=destination,
            stage=stage,
            config=HTTPGenerationConfig(
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=resolved_top_p,
                top_k=resolved_top_k,
                seed=self.stable_seed(seed_label),
                thinking_token_budget=self.config.thinking_token_budget,
                reasoning_effort=self.config.reasoning_effort,
                repetition_detection=REPETITION_DETECTION,
                timeout_seconds=14_400,
            ),
        )

    def structured(
        self,
        *,
        role: str,
        prompt: str,
        destination: Path,
        stage: str,
        schema: dict[str, Any],
        temperature: float,
        max_tokens: int,
        seed_label: str,
        user_prompt: str = "Return the requested JSON record now.",
        use_explicit_guided_json: bool = False,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        cached = self.saved_generation(destination, stage)
        if cached is None:
            endpoint = (
                self.config.gemma_endpoint if role == "gemma" else self.config.qwen_endpoint
            )
            model = self.config.gemma_model if role == "gemma" else self.config.qwen_model
            destination.mkdir(parents=True, exist_ok=True)
            schema_name = safe_name(stage)
            cached = run_openai_chat_generation(
                endpoint=endpoint,
                model=model,
                prompt=prompt,
                user_prompt=user_prompt,
                output_dir=destination,
                stage=stage,
                config=HTTPGenerationConfig(
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=1.0,
                    top_k=-1,
                    seed=self.stable_seed(seed_label),
                    thinking_token_budget=self.config.thinking_token_budget,
                    reasoning_effort=self.config.reasoning_effort,
                    response_format=(
                        None
                        if use_explicit_guided_json
                        else {
                            "type": "json_schema",
                            "json_schema": {
                                "name": schema_name,
                                "strict": True,
                                "schema": schema,
                            },
                        }
                    ),
                    structured_outputs=(
                        {
                            "json": schema,
                            "disable_additional_properties": True,
                        }
                        if use_explicit_guided_json
                        else None
                    ),
                    repetition_detection=REPETITION_DETECTION,
                    timeout_seconds=14_400,
                ),
            )
        try:
            record = parse_json_object(str(cached["text"]))
            validate_schema(record, schema)
        except Exception as error:
            if has_limit_recovery(cached["metadata"]):
                raise TimeoutRecoveryFailure("timeout fallback failed schema validation") from error
            raise
        return record, cached
