from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_2_7_failed_reasoning_memory_20260812 import (
    core as v027_core,
)
from experiments.local_math_verifier.runtime import (
    HTTPGenerationConfig,
    run_openai_chat_generation,
)


def merge_continuation(partial: str, continuation: str) -> str:
    partial = partial.strip()
    continuation = continuation.strip()
    if not partial:
        return continuation
    if not continuation:
        return partial
    prefix = partial[: min(256, len(partial))]
    if len(prefix) >= 64 and continuation.startswith(prefix):
        return continuation
    maximum = min(len(partial), len(continuation), 8_192)
    overlap = 0
    for size in range(maximum, 31, -1):
        if partial[-size:] == continuation[:size]:
            overlap = size
            break
    separator = "" if overlap or partial.endswith((" ", "\n")) else "\n"
    return partial + separator + continuation[overlap:]


def reusable_generation(*, reasoning: str, final: str) -> str:
    chunks: list[str] = []
    if reasoning.strip():
        chunks.append("[Preserved reasoning]\n" + reasoning.strip())
    if final.strip():
        chunks.append("[Preserved final response fragment]\n" + final.strip())
    return "\n\n".join(chunks)


def _saved_recovery(
    *,
    path: Path,
    engine: Any,
    prompt: str,
    seed: int,
    primary_sha256: str,
) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    expected = {
        "prompt_sha256": v027_core.sha256(prompt + v027_core.EXECUTION_DISCIPLINE),
        "seed": seed,
        "model": engine.model,
        "endpoint": engine.endpoint,
        "thinking_token_budget": None,
    }
    if any(value.get(key) != observed for key, observed in expected.items()):
        return None
    recovery = value.get("cap_recovery") or {}
    if (
        recovery.get("triggered") is not True
        or recovery.get("reused_partial_generation") is not True
        or recovery.get("partial_generation_sha256") != primary_sha256
    ):
        return None
    if not str(value.get("final") or "").strip():
        return None
    if value.get("finish_reason") == "length":
        return None
    return value


def cap_recovering_gemma_text(
    self: Any,
    *,
    prompt: str,
    namespace: str,
    index: int = 0,
    temperature: float = 1.0,
    max_tokens: int = 65_536,
) -> dict[str, Any]:
    """Gemma text generation with one continuation-only doubled-cap repair."""

    base_seed = self.seed(namespace, index)
    primary_path = self.raw_dir / f"{namespace}_{index}_attempt1.json"
    primary, response_source = self._load_or_call(
        raw_path=primary_path,
        prompt=prompt,
        seed=base_seed,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    primary_final = str(primary.get("final") or "")
    if primary_final.strip() and primary.get("finish_reason") != "length":
        return primary

    if primary.get("finish_reason") != "length":
        # Preserve the inherited empty-output retry for transport/model anomalies;
        # it is distinct from the cap-exhaustion repair requested here.
        fallback_path = self.raw_dir / f"{namespace}_{index}_attempt2.json"
        fallback, _ = self._load_or_call(
            raw_path=fallback_path,
            prompt=prompt,
            seed=base_seed + 1,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        if str(fallback.get("final") or "").strip() and fallback.get(
            "finish_reason"
        ) != "length":
            return fallback
        raise RuntimeError(
            "Gemma text generation returned no usable final response after retry"
        )

    reusable = reusable_generation(
        reasoning=str(primary.get("reasoning") or ""),
        final=primary_final,
    )
    if not reusable:
        raise RuntimeError(
            "Gemma reached max_tokens without a reusable partial generation"
        )
    primary_sha256 = v027_core.sha256(reusable)
    recovery_seed = (base_seed + 1_000_003) & 0xFFFFFFFF
    recovery_path = self.raw_dir / f"{namespace}_{index}_attempt2.json"
    saved = _saved_recovery(
        path=recovery_path,
        engine=self,
        prompt=prompt,
        seed=recovery_seed,
        primary_sha256=primary_sha256,
    )
    if saved is not None:
        return saved

    result = run_openai_chat_generation(
        endpoint=self.endpoint,
        model=self.model,
        prompt=prompt + v027_core.EXECUTION_DISCIPLINE,
        user_prompt="Execute the requested task now.",
        prior_generation=reusable,
        output_dir=self.raw_dir,
        stage=f"{namespace}_{index}_attempt2_cap_continuation",
        config=HTTPGenerationConfig(
            max_tokens=max_tokens * 2,
            temperature=temperature,
            top_p=0.95,
            top_k=64,
            seed=recovery_seed,
            thinking_token_budget=None,
            reasoning_effort=None,
            timeout_seconds=14_400,
        ),
    )
    if result["metadata"].get("finish_reason") == "length":
        raise RuntimeError(
            "Gemma doubled-cap continuation also reached max_tokens="
            f"{max_tokens * 2}"
        )
    continuation = str(result.get("text") or "").strip()
    merged_final = merge_continuation(primary_final, continuation)
    if not merged_final:
        raise RuntimeError("Gemma cap continuation returned no final proof text")

    recovered = {
        "raw": None,
        "reasoning": "\n\n".join(
            value
            for value in (
                str(primary.get("reasoning") or "").strip(),
                str(result.get("reasoning") or "").strip(),
            )
            if value
        ),
        "final": merged_final,
        "finish_reason": result["metadata"].get("finish_reason"),
        "usage": result["metadata"].get("usage") or {},
        "latency_seconds": (
            float(primary.get("latency_seconds") or 0.0)
            + float(result["metadata"].get("latency_seconds") or 0.0)
        ),
        "seed": recovery_seed,
        "prompt_sha256": v027_core.sha256(
            prompt + v027_core.EXECUTION_DISCIPLINE
        ),
        "message_roles": ["system", "user", "assistant", "user"],
        "thinking_enabled": True,
        "thinking_token_budget": None,
        "model": self.model,
        "endpoint": self.endpoint,
        "response_source": response_source,
        "cap_recovery": {
            "triggered": True,
            "reused_partial_generation": True,
            "primary_max_tokens": max_tokens,
            "recovery_max_tokens": max_tokens * 2,
            "partial_generation_sha256": primary_sha256,
            "partial_final_sha256": v027_core.sha256(primary_final),
            "continuation_sha256": v027_core.sha256(continuation),
            "continuation_generation": result["metadata"],
        },
    }
    v027_core.write_json(recovery_path, recovered)
    return recovered


__all__ = [
    "cap_recovering_gemma_text",
    "merge_continuation",
    "reusable_generation",
]
