from __future__ import annotations

import hashlib
import json
import shutil
import sys
import threading
from dataclasses import asdict
from pathlib import Path
from types import ModuleType
from typing import Any, Callable

from experiments.local_math_verifier import runtime as transport


TEXT_CONTINUATION = (
    "Wait. Continue from the viable intermediate reasoning above. Recheck the "
    "original task, use the strongest intermediate result to bridge the major "
    "remaining gap, and emit one complete replacement response in the original "
    "required format. Do not mention this instruction or the earlier draft."
)
STRUCTURED_CONTINUATION = (
    "Wait. Continue from the viable intermediate reasoning above. Recheck every "
    "requirement and bridge the major remaining gap. Emit one complete replacement "
    "JSON object satisfying the original schema exactly. Do not append, comment on, "
    "or mention the earlier draft."
)
TARGET_MODEL_MARKERS = ("gemma", "qwen")
ARTIFACT_SUFFIXES = (
    ".prompt.txt",
    ".user_prompt.txt",
    ".raw_response.json",
    ".reasoning.txt",
    ".metadata.json",
)

_LOCK = threading.Lock()
_ORIGINAL = transport.run_openai_chat_generation
_INSTALLED = False
_EVENTS: list[dict[str, Any]] = []


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def is_target_model(model: str) -> bool:
    normalized = model.casefold()
    return any(marker in normalized for marker in TARGET_MODEL_MARKERS)


def is_structured(config: Any) -> bool:
    return bool(
        getattr(config, "response_format", None)
        or getattr(config, "structured_outputs", None)
    )


def continuation_instruction(config: Any) -> str:
    return STRUCTURED_CONTINUATION if is_structured(config) else TEXT_CONTINUATION


def reusable_generation(result: dict[str, Any]) -> str:
    parts: list[str] = []
    reasoning = str(result.get("reasoning") or "").strip()
    text = str(result.get("text") or "").strip()
    if reasoning:
        parts.append("[Preserved reasoning]\n" + reasoning)
    if text:
        parts.append("[Preserved response]\n" + text)
    if not parts:
        parts.append("[Preserved response]\nThe first response was empty; reconstruct it.")
    return "\n\n".join(parts)


def _read_primary_after_error(output_dir: Path, stage: str) -> dict[str, Any] | None:
    raw_path = output_dir / f"{stage}.raw_response.json"
    metadata_path = output_dir / f"{stage}.metadata.json"
    reasoning_path = output_dir / f"{stage}.reasoning.txt"
    if not raw_path.is_file() or not metadata_path.is_file():
        return None
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    choices = raw.get("choices") or []
    if not choices:
        return None
    message = choices[0].get("message") or {}
    return {
        "text": str(message.get("content") or "").strip(),
        "reasoning": (
            reasoning_path.read_text(encoding="utf-8").strip()
            if reasoning_path.is_file()
            else str(message.get("reasoning_content") or message.get("reasoning") or "").strip()
        ),
        "metadata": json.loads(metadata_path.read_text(encoding="utf-8")),
    }


def _preserve_primary(output_dir: Path, stage: str) -> dict[str, str]:
    paths: dict[str, str] = {}
    for suffix in ARTIFACT_SUFFIXES:
        source = output_dir / f"{stage}{suffix}"
        if not source.is_file():
            continue
        target = output_dir / f"{stage}.pre_budget_forcing{suffix}"
        shutil.copy2(source, target)
        paths[suffix] = str(target.resolve())
    return paths


def _expanded_prior(
    *,
    primary: dict[str, Any],
    prior_generation: str | None,
    prior_instruction: str | None,
) -> str:
    sections: list[str] = []
    if prior_generation is not None:
        sections.append("[Earlier assistant context]\n" + prior_generation.strip())
        if prior_instruction:
            sections.append("[Earlier continuation request]\n" + prior_instruction.strip())
    sections.append(reusable_generation(primary))
    return "\n\n".join(section for section in sections if section.strip())


def _write_event(output_dir: Path, stage: str, event: dict[str, Any]) -> None:
    path = output_dir / f"{stage}.budget_forcing.json"
    path.write_text(
        json.dumps(event, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _call_with_budget_forcing(**kwargs: Any) -> dict[str, Any]:
    model = str(kwargs["model"])
    if not is_target_model(model):
        return _ORIGINAL(**kwargs)

    output_dir = Path(kwargs["output_dir"])
    stage = str(kwargs["stage"])
    primary_error: str | None = None
    try:
        primary = _ORIGINAL(**kwargs)
    except Exception as error:
        primary = _read_primary_after_error(output_dir, stage)
        if primary is None:
            raise
        primary_error = f"{type(error).__name__}: {error}"

    preserved_paths = _preserve_primary(output_dir, stage)
    prior = _expanded_prior(
        primary=primary,
        prior_generation=kwargs.get("prior_generation"),
        prior_instruction=kwargs.get("continuation_instruction"),
    )
    cue = continuation_instruction(kwargs["config"])
    forced_kwargs = dict(kwargs)
    forced_kwargs["prior_generation"] = prior
    forced_kwargs["continuation_instruction"] = cue
    forced = _ORIGINAL(**forced_kwargs)

    primary_metadata = dict(primary.get("metadata") or {})
    forced_metadata = dict(forced.get("metadata") or {})
    event = {
        "schema": "cognitive-well-v0249-all-call-budget-forcing-event-v1",
        "policy": "mandatory_one_semantic_continuation_full_replacement",
        "stage": stage,
        "model": model,
        "structured": is_structured(kwargs["config"]),
        "cue": cue,
        "cue_sha256": _sha256(cue),
        "primary_error_recovered": primary_error,
        "primary_finish_reason": primary_metadata.get("finish_reason"),
        "forced_finish_reason": forced_metadata.get("finish_reason"),
        "primary_text_sha256": _sha256(str(primary.get("text") or "")),
        "primary_reasoning_sha256": _sha256(str(primary.get("reasoning") or "")),
        "forced_text_sha256": _sha256(str(forced.get("text") or "")),
        "forced_reasoning_sha256": _sha256(str(forced.get("reasoning") or "")),
        "preserved_primary_artifacts": preserved_paths,
        "canonical_artifacts_are_forced_response": True,
        "original_config": asdict(kwargs["config"]),
    }
    forced_metadata["v0249_budget_forcing"] = {
        key: value
        for key, value in event.items()
        if key not in {"original_config", "preserved_primary_artifacts"}
    }
    forced["metadata"] = forced_metadata
    transport.write_json(output_dir / f"{stage}.metadata.json", forced_metadata)
    _write_event(output_dir, stage, event)
    with _LOCK:
        _EVENTS.append(dict(event))
    return forced


def _replace_aliases(original: Callable[..., Any], replacement: Callable[..., Any]) -> list[str]:
    replaced: list[str] = []
    for module_name, module in sorted(sys.modules.items()):
        if module is None or not (
            module_name == "experiments.local_math_verifier.runtime"
            or module_name.startswith("cognitive_well_harness_")
        ):
            continue
        # This module intentionally retains the pristine transport in _ORIGINAL;
        # replacing it would make the wrapper recurse into itself.
        if module is sys.modules[__name__]:
            continue
        namespace = vars(module)
        for name, value in list(namespace.items()):
            if value is original:
                namespace[name] = replacement
                replaced.append(f"{module_name}.{name}")
    return replaced


def install() -> list[str]:
    global _INSTALLED
    with _LOCK:
        replaced = _replace_aliases(_ORIGINAL, _call_with_budget_forcing)
        transport.run_openai_chat_generation = _call_with_budget_forcing
        _INSTALLED = True
    return replaced


def audit_loaded_aliases() -> list[str]:
    stale: list[str] = []
    for module_name, module in sorted(sys.modules.items()):
        if module is None or not module_name.startswith("cognitive_well_harness_"):
            continue
        if module is sys.modules[__name__]:
            continue
        for name, value in vars(module).items():
            if value is _ORIGINAL:
                stale.append(f"{module_name}.{name}")
    return stale


def events() -> list[dict[str, Any]]:
    with _LOCK:
        return [dict(event) for event in _EVENTS]


def installed() -> bool:
    return _INSTALLED
