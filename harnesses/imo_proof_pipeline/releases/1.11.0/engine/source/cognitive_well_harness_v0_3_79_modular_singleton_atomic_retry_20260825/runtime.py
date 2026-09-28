from __future__ import annotations

from experiments.local_math_verifier.timeout_recovery import TimeoutRecoveryFailure

from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import (
    ModelRuntime,
)
from cognitive_well_harness_v0_3_71_modular_shared_lemma_memory_recovery_20260824.runtime import (
    TEXT_MAX_ATTEMPTS,
    ResilientModelRuntime as V071ResilientModelRuntime,
    recovery_profile as v071_recovery_profile,
)


class ResilientModelRuntime(V071ResilientModelRuntime):
    """v0.3.79-only fix for empty text responses at repetition boundaries.

    v0.3.71's text recovery loop did not catch the exception raised by the base
    runtime when a repetition stop contained no final answer.  Preserve the
    original request exactly, then perform the already-specified full-replacement
    attempts only after the original response is rejected.
    """

    def text(self, **kwargs: Any) -> dict[str, Any]:
        base_stage = str(kwargs["stage"])
        original_prompt = str(kwargs["prompt"])
        attempts: list[dict[str, Any]] = []
        partial = ""

        for attempt in range(TEXT_MAX_ATTEMPTS):
            call = dict(kwargs)
            if attempt:
                call["stage"] = f"{base_stage}_replacement_{attempt}"
                call["seed_label"] = (
                    f"v079:{kwargs['seed_label']}:replacement:{attempt}"
                )
                call["prompt"] = (
                    original_prompt.rstrip()
                    + "\n\nTRANSPORT RECOVERY: The preceding response was empty or ended "
                    + "at a repetition or length boundary. Produce a complete replacement "
                    + "from the beginning. Do not continue or reproduce the repeated suffix. "
                    + "Preserve correct task content only.\n\nPRIOR INCOMPLETE RESPONSE:\n"
                    + partial.rstrip()[-12_000:]
                )

            error_text: str | None = None
            try:
                # Bypass the v0.3.71 wrapper so an exception from the nominal call
                # can be caught here and routed to the next replacement attempt.
                generated = ModelRuntime.text(self, **call)
            except TimeoutRecoveryFailure:
                raise
            except Exception as error:
                generated = self.saved_generation(
                    Path(call["destination"]), str(call["stage"])
                )
                error_text = f"{type(error).__name__}: {error}"

            if generated is None:
                text = ""
                metadata: dict[str, Any] = {}
            else:
                text = str(generated.get("text") or "")
                metadata = dict(generated.get("metadata") or {})
            partial = text
            finish = metadata.get("finish_reason")
            accepted = (
                error_text is None
                and bool(text.strip())
                and finish not in {"repetition", "length"}
            )
            attempts.append(
                {
                    "attempt": attempt,
                    "stage": call["stage"],
                    "finish_reason": finish,
                    "empty": not bool(text.strip()),
                    "accepted": accepted,
                    "error": error_text,
                    "repetition_detection_preserved": True,
                }
            )
            if accepted:
                metadata["v079_recovery_attempts"] = attempts
                self._record_recovery(
                    kind="text", stage=base_stage, attempts=attempts, accepted=True
                )
                return {**generated, "metadata": metadata}

        self._record_recovery(
            kind="text", stage=base_stage, attempts=attempts, accepted=False
        )
        raise RuntimeError(f"v0.3.79 text recovery exhausted: {attempts}")


def recovery_profile() -> dict[str, Any]:
    profile = dict(v071_recovery_profile())
    profile.update(
        {
            "text_exception_recovery": "v0.3.79_empty_repetition_fix",
            "text_primary_phase": "original_unchanged",
            "text_recovery_phases": ["replacement_1", "replacement_2"],
        }
    )
    return profile


__all__ = ["ResilientModelRuntime", "recovery_profile"]
