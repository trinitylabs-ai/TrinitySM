from __future__ import annotations

from experiments.local_math_verifier.timeout_recovery import require_valid_fallback

import json
from dataclasses import replace
from pathlib import Path
from typing import Any

from experiments.local_math_verifier.cap_recovery import (
    POLICY_ID, clean_capped_result, policy_manifest, recovery_limit, MAX_RETRY_TOKENS,
)

from experiments.local_math_verifier import runtime as transport
from experiments.local_math_verifier.runtime import HTTPGenerationConfig
from . import HARNESS_VERSION, PARENT_HARNESS_VERSION
from cognitive_well_harness_v0_3_257_v108_third_resolve_raw_t10_bf_temp07_20260904 import (
    pipeline as parent,
)
from cognitive_well_harness_v0_3_36_p4_dual_block_replay_snapshot_20260822.cold_prompts import (
    lazy_phrasing,
)
from cognitive_well_harness_v0_3_37_bf16_gemma_two_block_stage12_20260822.pipeline import (
    nonempty_parser,
)
from cognitive_well_harness_v0_3_37_bf16_gemma_two_block_stage12_20260822.runtime import (
    sha256_text,
)
from cognitive_well_harness_v0_3_47_lazy_in_place_expansion_20260823.run_six_candidate_lazy_test import (
    derived_seed,
)


TERMINAL_STAGE = parent.TERMINAL_STAGE
LAZY_PRIMARY_MAX_TOKENS = 16_384
LAZY_RECOVERY_MAX_TOKENS = MAX_RETRY_TOKENS

v097 = parent.v108.v097
_PARENT_RUNTIME_CONFIG = v097.RuntimeConfig
_PARENT_PHASE_ONE_MANIFEST = v097.phase_one_manifest


def _runtime_config(*args: Any, **kwargs: Any) -> Any:
    kwargs.setdefault("lazy_max_tokens", LAZY_PRIMARY_MAX_TOKENS)
    return _PARENT_RUNTIME_CONFIG(*args, **kwargs)


def _phase_one_manifest(*args: Any, **kwargs: Any) -> dict[str, Any]:
    manifest = _PARENT_PHASE_ONE_MANIFEST(*args, **kwargs)
    manifest["lazy_check"] = {
        **manifest["lazy_check"],
        "max_tokens": LAZY_PRIMARY_MAX_TOKENS,
        "cap_recovery_max_tokens": LAZY_RECOVERY_MAX_TOKENS,
    }
    return manifest


def _fresh_restart_gemma_call(
    *,
    runtime: Any,
    output_dir: Path,
    name: str,
    system_prompt: str,
    user_prompt: str,
    seed: int,
    temperature: float,
    max_tokens: int,
    parser: Any,
) -> dict[str, Any]:
    """Bound cap recovery; retain a clean prefix when the cap contained a loop."""
    output_dir.mkdir(parents=True, exist_ok=True)
    identity = {
        "endpoint": runtime.config.gemma_endpoint.rstrip("/"),
        "model": runtime.config.gemma_model,
        "system_prompt_sha256": sha256_text(system_prompt),
        "user_prompt_sha256": sha256_text(user_prompt),
        "seed": seed,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "cap_recovery_strategy": "fresh_unless_repetition_then_clean_prefix",
    }
    cached = runtime._read_cached(output_dir=output_dir, name=name, identity=identity)
    if cached is not None and parser(str(cached.get("text") or "")).get("valid"):
        return {**cached, "response_source": "saved"}

    errors: list[dict[str, Any]] = []
    for attempt in range(runtime.config.protocol_attempts):
        attempt_seed = (seed + attempt) & 0xFFFFFFFF
        config = HTTPGenerationConfig(
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=0.95,
            top_k=64,
            seed=attempt_seed,
            thinking_token_budget=None,
            reasoning_effort=None,
            timeout_seconds=14_400,
        )
        with runtime._gemma_slots:
            first = transport.run_openai_chat_generation(
                endpoint=runtime.config.gemma_endpoint,
                model=runtime.config.gemma_model,
                prompt=system_prompt,
                user_prompt=user_prompt,
                output_dir=output_dir,
                stage=f"{name}_attempt{attempt + 1}",
                config=config,
            )
        text = str(first["text"]).strip()
        final_metadata = first["metadata"]
        cap_recovery: dict[str, Any] = {
            "triggered": False,
            "strategy": "fresh_unless_repetition_then_clean_prefix",
            "reused_partial_generation": False,
        }
        if first["metadata"].get("finish_reason") == "length":
            cleaned, trimming = clean_capped_result(first)
            reusable = runtime._reusable_http(cleaned) if trimming["detected"] else ""
            recovery_config = replace(
                config,
                max_tokens=recovery_limit(first, max_tokens),
                seed=(attempt_seed + 1_000_003) & 0xFFFFFFFF,
            )
            transport.write_json(output_dir / f"{name}_attempt{attempt + 1}.cap_recovery_input.json", {
                "policy": POLICY_ID, "trimming": trimming,
                "recovery_max_tokens": recovery_config.max_tokens,
                "prior_sha256": sha256_text(reusable),
            })
            with runtime._gemma_slots:
                recovery = transport.run_openai_chat_generation(
                    endpoint=runtime.config.gemma_endpoint,
                    model=runtime.config.gemma_model,
                    prompt=system_prompt,
                    user_prompt=user_prompt,
                    output_dir=output_dir,
                    stage=f"{name}_attempt{attempt + 1}_bounded_cap_recovery",
                    prior_generation=reusable or None,
                    config=recovery_config,
                )
            text = str(recovery["text"]).strip()
            final_metadata = recovery["metadata"]
            cap_recovery = {
                "triggered": True,
                "strategy": "fresh_unless_repetition_then_clean_prefix",
                "reused_partial_generation": bool(reusable),
                "policy": POLICY_ID, "trimming": trimming,
                "primary_max_tokens": max_tokens,
                "recovery_max_tokens": recovery_config.max_tokens,
                "discarded_capped_text_sha256": sha256_text(
                    str(first.get("text") or "")
                ),
                "recovery_text_sha256": sha256_text(text),
                "recovery_metadata": recovery["metadata"],
            }
            if recovery["metadata"].get("finish_reason") == "length":
                errors.append(
                    {"attempt": attempt + 1, "error": "bounded cap recovery exhausted"}
                )
                continue
        try:
            parsed = parser(text)
        except Exception:
            require_valid_fallback(final_metadata, {"valid": False})
            raise
        require_valid_fallback(final_metadata, parsed)
        if not parsed.get("valid"):
            errors.append({"attempt": attempt + 1, "errors": parsed.get("errors", [])})
            continue
        result = runtime._save_cached(
            output_dir=output_dir,
            name=name,
            identity=identity,
            result={
                "text": text,
                "parsed": parsed,
                "generation": first["metadata"],
                "final_generation": final_metadata,
                "cap_recovery": cap_recovery,
                "prior_errors": errors,
                "response_source": "live",
            },
        )
        (output_dir / f"{name}.txt").write_text(text + "\n", encoding="utf-8")
        return result
    raise RuntimeError(f"{name} exhausted protocol attempts: {errors}")


def _run_lazy_check(
    *, runtime: Any, output_dir: Path, row: dict[str, Any]
) -> dict[str, Any]:
    candidate_id = str(row["candidate_id"])
    generated = _fresh_restart_gemma_call(
        runtime=runtime,
        output_dir=output_dir / "candidates" / candidate_id / "lazy_check",
        name="lazy_check",
        system_prompt=lazy_phrasing(str(row["proof"])),
        user_prompt="Scan the submitted proof now.",
        seed=derived_seed(int(row["seed"]), "lazy_check"),
        temperature=0.1,
        max_tokens=runtime.config.lazy_max_tokens,
        parser=nonempty_parser,
    )
    report = str(generated["text"]).strip()
    return {
        **row,
        "lazy_report": report,
        "lazy_report_sha256": sha256_text(report),
        "has_lazy_issues": report != "NO_ISSUES",
        "lazy_generation": generated,
    }


# These symbols are looked up dynamically by v097 when each problem starts.
v097.RuntimeConfig = _runtime_config
v097.phase_one_manifest = _phase_one_manifest
v097.run_lazy_check = _run_lazy_check


def _write_policy_manifest(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "v0258_cap_policy_manifest.json"
    expected = {
        "schema": "cognitive-well-v0258-cap-policy-manifest-v1",
        "harness_version": HARNESS_VERSION,
        "parent_harness_version": PARENT_HARNESS_VERSION,
        "terminal_stage": TERMINAL_STAGE,
        "lazy_check_primary_max_tokens": LAZY_PRIMARY_MAX_TOKENS,
        "lazy_check_cap_recovery_max_tokens": LAZY_RECOVERY_MAX_TOKENS,
        "lazy_check_cap_recovery_strategy": "fresh_unless_repetition_then_clean_prefix",
        "budget_forcing_strategy": "same_trace_semantic_continuation",
        "raw_proof_generation_max_tokens": 65_536,
        "raw_proof_generation_changed": False,
    }
    if path.is_file():
        observed = json.loads(path.read_text(encoding="utf-8"))
        if observed != expected:
            raise ValueError("v0258 cap-policy manifest drift")
        return
    path.write_text(
        json.dumps(expected, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def run_pipeline(**kwargs: Any) -> dict[str, Any]:
    output_dir = Path(kwargs["output_dir"]).resolve()
    _write_policy_manifest(output_dir)
    result = parent.run_pipeline(**kwargs)
    return {
        **result,
        "upgrade_harness_version": HARNESS_VERSION,
        "upgrade_parent_harness_version": PARENT_HARNESS_VERSION,
        "lazy_check_primary_max_tokens": LAZY_PRIMARY_MAX_TOKENS,
        "lazy_check_cap_recovery_max_tokens": LAZY_RECOVERY_MAX_TOKENS,
    }
