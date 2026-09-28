from __future__ import annotations

import json
import re
import sys
import threading
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Callable

from experiments.local_math_verifier import runtime as transport
from cognitive_well_harness_v0_3_249_v108_third_resolve_all_call_budget_forcing_20260904 import (
    budget_forcing as base,
)


TEXT_CONTINUATION = base.TEXT_CONTINUATION
STRUCTURED_CONTINUATION = base.STRUCTURED_CONTINUATION
TARGET_MODEL_MARKERS = base.TARGET_MODEL_MARKERS
RAW_PRIMARY_TEMPERATURE = 1.0
RAW_FORCED_TEMPERATURE = 0.7
RAW_STAGE_PATTERN = re.compile(r"cold_draft_attempt[0-9]+\Z")

_LOCK = threading.Lock()
_ORIGINAL = base._ORIGINAL
_INSTALLED = False
_EVENTS: list[dict[str, Any]] = []


def is_target_model(model: str) -> bool:
    return base.is_target_model(model)


def is_structured(config: Any) -> bool:
    return base.is_structured(config)


def continuation_instruction(config: Any) -> str:
    return base.continuation_instruction(config)


def is_raw_temperature_transition(
    *, output_dir: Path, stage: str, config: Any
) -> bool:
    """Identify only the initial raw proof-generation calls sampled at t=1.0."""
    temperature = float(getattr(config, "temperature", 0.0))
    return (
        output_dir.name == "cold_generation"
        and RAW_STAGE_PATTERN.fullmatch(stage) is not None
        and abs(temperature - RAW_PRIMARY_TEMPERATURE) < 1e-12
    )


def continuation_config(*, output_dir: Path, stage: str, config: Any) -> Any:
    if not is_raw_temperature_transition(
        output_dir=output_dir, stage=stage, config=config
    ):
        return config
    return replace(config, temperature=RAW_FORCED_TEMPERATURE)


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
        primary = base._read_primary_after_error(output_dir, stage)
        if primary is None:
            raise
        primary_error = f"{type(error).__name__}: {error}"

    return _continue_primary(primary=primary, kwargs=kwargs, primary_error=primary_error)


def _continue_primary(*, primary: dict[str, Any], kwargs: dict[str, Any],
                      primary_error: str | None = None, reused_primary: bool = False) -> dict[str, Any]:
    """Finish one mandatory continuation, including a caller-validated saved primary."""
    model = str(kwargs["model"])
    output_dir = Path(kwargs["output_dir"])
    stage = str(kwargs["stage"])
    preserved_paths = base._preserve_primary(output_dir, stage)
    prior = base._expanded_prior(
        primary=primary,
        prior_generation=kwargs.get("prior_generation"),
        prior_instruction=kwargs.get("continuation_instruction"),
    )
    cue = continuation_instruction(kwargs["config"])
    forced_config = continuation_config(
        output_dir=output_dir,
        stage=stage,
        config=kwargs["config"],
    )
    forced_kwargs = dict(kwargs)
    forced_kwargs["config"] = forced_config
    forced_kwargs["prior_generation"] = prior
    forced_kwargs["continuation_instruction"] = cue
    forced = _ORIGINAL(**forced_kwargs)

    primary_metadata = dict(primary.get("metadata") or {})
    forced_metadata = dict(forced.get("metadata") or {})
    primary_temperature = float(getattr(kwargs["config"], "temperature", 0.0))
    forced_temperature = float(getattr(forced_config, "temperature", 0.0))
    event = {
        "schema": "cognitive-well-v0257-all-call-budget-forcing-event-v1",
        "policy": "mandatory_one_semantic_continuation_full_replacement",
        "stage": stage,
        "model": model,
        "structured": is_structured(kwargs["config"]),
        "cue": cue,
        "cue_sha256": base._sha256(cue),
        "primary_error_recovered": primary_error,
        "primary_finish_reason": primary_metadata.get("finish_reason"),
        "forced_finish_reason": forced_metadata.get("finish_reason"),
        "primary_temperature": primary_temperature,
        "forced_temperature": forced_temperature,
        "raw_temperature_transition_applied": (
            abs(primary_temperature - forced_temperature) > 1e-12
        ),
        "primary_text_sha256": base._sha256(str(primary.get("text") or "")),
        "primary_reasoning_sha256": base._sha256(str(primary.get("reasoning") or "")),
        "forced_text_sha256": base._sha256(str(forced.get("text") or "")),
        "forced_reasoning_sha256": base._sha256(str(forced.get("reasoning") or "")),
        "preserved_primary_artifacts": preserved_paths,
        "canonical_artifacts_are_forced_response": True,
        "original_config": dict(primary_metadata["config"]) if reused_primary else asdict(kwargs["config"]),
        "forced_config": asdict(forced_config),
    }
    if reused_primary:
        event["primary_generation_reused"] = True
    forced_metadata["v0257_budget_forcing"] = {
        key: value
        for key, value in event.items()
        if key
        not in {"original_config", "forced_config", "preserved_primary_artifacts"}
    }
    forced["metadata"] = forced_metadata
    transport.write_json(output_dir / f"{stage}.metadata.json", forced_metadata)
    (output_dir / f"{stage}.budget_forcing.json").write_text(
        json.dumps(event, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    with _LOCK:
        _EVENTS.append(dict(event))
    return forced


def _replace_aliases(
    original: Callable[..., Any], replacement: Callable[..., Any]
) -> list[str]:
    replaced: list[str] = []
    excluded = {__name__, base.__name__}
    for module_name, module in sorted(sys.modules.items()):
        if module is None or module_name in excluded:
            continue
        if not (
            module_name == "experiments.local_math_verifier.runtime"
            or module_name.startswith("cognitive_well_harness_")
        ):
            continue
        for name, value in list(vars(module).items()):
            if value is original:
                vars(module)[name] = replacement
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
    excluded = {__name__, base.__name__}
    for module_name, module in sorted(sys.modules.items()):
        if (
            module is None
            or module_name in excluded
            or not module_name.startswith("cognitive_well_harness_")
        ):
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
