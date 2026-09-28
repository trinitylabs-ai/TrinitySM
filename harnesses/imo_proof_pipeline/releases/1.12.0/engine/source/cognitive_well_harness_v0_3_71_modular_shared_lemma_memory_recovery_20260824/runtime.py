from __future__ import annotations

from experiments.local_math_verifier.timeout_recovery import TimeoutRecoveryFailure

import hashlib
import threading
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.contracts import (
    validate_schema,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import (
    ModelRuntime,
    REPETITION_DETECTION,
    parse_json_object,
)


STRUCTURED_RECOVERY_PHASES = ("compact", "repair_1", "repair_2")
TEXT_MAX_ATTEMPTS = 3
COMPACT_INSTRUCTION = (
    "Return exactly one complete compact JSON object on one line. Do not use Markdown "
    "fences or blank lines. Emit every required field, close the object, and stop."
)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _clean_duplicate_wrapper_prefix(value: str) -> tuple[str, str] | None:
    text = value.strip()
    if text.startswith('{"{') and text.endswith("}"):
        return text[2:], "drop_exact_duplicate_wrapper_prefix"
    return None


def _deterministic_structured_candidates(value: str) -> list[tuple[str, str]]:
    """Return transport-only candidates without changing mathematical content."""

    candidates = [(value, "accept_complete_schema_valid_json")]
    duplicate_cleanup = _clean_duplicate_wrapper_prefix(value)
    if duplicate_cleanup is not None:
        candidates.append(duplicate_cleanup)
    return candidates


def recovery_profile() -> dict[str, Any]:
    return {
        "structured_primary_phase": "original_unchanged",
        "structured_recovery_phases": list(STRUCTURED_RECOVERY_PHASES),
        "text_max_attempts": TEXT_MAX_ATTEMPTS,
        "structured_repair_is_full_replacement": True,
        "text_repair_is_full_replacement": True,
        "continuation_or_suffix_splicing": False,
        "deterministic_cleanup": ["drop_exact_duplicate_wrapper_prefix"],
        "gemma_structured_fallback": "one_qwen_full_record_attempt",
        "qwen_structured_fallback": None,
        "schema_validation_after_cleanup": True,
        "empty_text_is_rejected": True,
        "repetition_detection_preserved": True,
        "repetition_detection": dict(REPETITION_DETECTION),
    }


class ResilientModelRuntime(ModelRuntime):
    """Recover transport failures without disabling repetition detection."""

    def __init__(self, config: Any) -> None:
        super().__init__(config)
        self._recovery_lock = threading.Lock()
        self._recovery_events: list[dict[str, Any]] = []

    def _record_recovery(
        self, *, kind: str, stage: str, attempts: list[dict[str, Any]], accepted: bool
    ) -> None:
        with self._recovery_lock:
            self._recovery_events.append(
                {
                    "kind": kind,
                    "stage": stage,
                    "accepted": accepted,
                    "attempts": [dict(row) for row in attempts],
                }
            )

    def recovery_events(self) -> list[dict[str, Any]]:
        with self._recovery_lock:
            return [
                {**event, "attempts": [dict(row) for row in event["attempts"]]}
                for event in self._recovery_events
            ]

    def structured(self, **kwargs: Any) -> tuple[dict[str, Any], dict[str, Any]]:
        base_stage = str(kwargs["stage"])
        original_user = str(kwargs.get("user_prompt", "Return the requested JSON record now."))
        schema = kwargs["schema"]
        attempts: list[dict[str, Any]] = []
        partial = ""
        prior_error = "none"

        # The inherited request is the nominal path. Keep every argument unchanged so
        # adding recovery cannot perturb a previously successful boundary.
        try:
            record, generation = super().structured(**kwargs)
            metadata = dict(generation["metadata"])
            attempts.append(
                {
                    "phase": "original",
                    "stage": base_stage,
                    "status": "accepted",
                    "finish_reason": metadata.get("finish_reason"),
                    "deterministic_cleanup": None,
                    "repetition_detection_preserved": True,
                }
            )
            metadata["v071_recovery_attempts"] = attempts
            self._record_recovery(
                kind="structured", stage=base_stage, attempts=attempts, accepted=True
            )
            return record, {**generation, "metadata": metadata}
        except TimeoutRecoveryFailure:
            raise
        except Exception as error:
            saved = self.saved_generation(Path(kwargs["destination"]), base_stage)
            partial = str(saved["text"]) if saved else ""
            metadata = dict(saved["metadata"]) if saved else {}
            prior_error = f"{type(error).__name__}: {error}"
            if saved is not None:
                cleanup_errors: list[str] = []
                for cleaned_text, cleanup_name in _deterministic_structured_candidates(
                    partial
                ):
                    try:
                        record = parse_json_object(cleaned_text)
                        validate_schema(record, schema)
                        attempts.append(
                            {
                                "phase": "original",
                                "stage": base_stage,
                                "status": "accepted_after_deterministic_cleanup",
                                "finish_reason": metadata.get("finish_reason"),
                                "partial_length": len(partial),
                                "partial_sha256": sha256_text(partial),
                                "deterministic_cleanup": cleanup_name,
                                "repetition_detection_preserved": True,
                            }
                        )
                        metadata["v071_recovery_attempts"] = attempts
                        self._record_recovery(
                            kind="structured",
                            stage=base_stage,
                            attempts=attempts,
                            accepted=True,
                        )
                        return record, {"text": partial, "metadata": metadata}
                    except Exception as cleanup_error:
                        cleanup_errors.append(
                            f"{cleanup_name}: {type(cleanup_error).__name__}: "
                            f"{cleanup_error}"
                        )
                if cleanup_errors:
                    prior_error += "; deterministic cleanup rejected: " + " | ".join(
                        cleanup_errors
                    )
            attempts.append(
                {
                    "phase": "original",
                    "stage": base_stage,
                    "status": "rejected",
                    "finish_reason": metadata.get("finish_reason"),
                    "error": prior_error,
                    "partial_length": len(partial),
                    "partial_sha256": sha256_text(partial) if partial else None,
                    "deterministic_cleanup": None,
                    "repetition_detection_preserved": True,
                }
            )

        for index, phase in enumerate(STRUCTURED_RECOVERY_PHASES):
            call = dict(kwargs)
            call["stage"] = f"{base_stage}_{phase}"
            call["seed_label"] = f"v071:{kwargs['seed_label']}:{phase}"
            if index == 0:
                call["user_prompt"] = original_user.rstrip() + "\n\n" + COMPACT_INSTRUCTION
            else:
                call["user_prompt"] = (
                    original_user.rstrip()
                    + "\n\nTRANSPORT RECOVERY: Regenerate the entire record from scratch. "
                    + "Do not append to the prior response and do not reproduce a repeated "
                    + "suffix. Preserve correct task content only. Prior error: "
                    + prior_error
                    + "\n\nPRIOR INCOMPLETE RESPONSE:\n"
                    + partial.rstrip()[-12_000:]
                    + "\n\n"
                    + COMPACT_INSTRUCTION
                )
            try:
                record, generation = super().structured(**call)
                metadata = dict(generation["metadata"])
                attempts.append(
                    {
                        "phase": phase,
                        "stage": call["stage"],
                        "status": "accepted",
                        "finish_reason": metadata.get("finish_reason"),
                        "deterministic_cleanup": None,
                        "repetition_detection_preserved": True,
                    }
                )
                metadata["v071_recovery_attempts"] = attempts
                self._record_recovery(
                    kind="structured", stage=base_stage, attempts=attempts, accepted=True
                )
                return record, {**generation, "metadata": metadata}
            except TimeoutRecoveryFailure:
                raise
            except Exception as error:
                saved = self.saved_generation(Path(kwargs["destination"]), call["stage"])
                partial = str(saved["text"]) if saved else ""
                metadata = dict(saved["metadata"]) if saved else {}
                prior_error = f"{type(error).__name__}: {error}"
                if saved is not None:
                    cleanup_errors: list[str] = []
                    for (
                        cleaned_text,
                        cleanup_name,
                    ) in _deterministic_structured_candidates(partial):
                        try:
                            record = parse_json_object(cleaned_text)
                            validate_schema(record, schema)
                            attempts.append(
                                {
                                    "phase": phase,
                                    "stage": call["stage"],
                                    "status": "accepted_after_deterministic_cleanup",
                                    "finish_reason": metadata.get("finish_reason"),
                                    "partial_length": len(partial),
                                    "partial_sha256": sha256_text(partial),
                                    "deterministic_cleanup": cleanup_name,
                                    "repetition_detection_preserved": True,
                                }
                            )
                            metadata["v071_recovery_attempts"] = attempts
                            self._record_recovery(
                                kind="structured",
                                stage=base_stage,
                                attempts=attempts,
                                accepted=True,
                            )
                            return record, {"text": partial, "metadata": metadata}
                        except Exception as cleanup_error:
                            cleanup_errors.append(
                                f"{cleanup_name}: {type(cleanup_error).__name__}: "
                                f"{cleanup_error}"
                            )
                    if cleanup_errors:
                        prior_error += (
                            "; deterministic cleanup rejected: "
                            + " | ".join(cleanup_errors)
                        )
                attempts.append(
                    {
                        "phase": phase,
                        "stage": call["stage"],
                        "status": "rejected",
                        "finish_reason": metadata.get("finish_reason"),
                        "error": prior_error,
                        "partial_length": len(partial),
                        "partial_sha256": sha256_text(partial) if partial else None,
                        "deterministic_cleanup": None,
                        "repetition_detection_preserved": True,
                    }
                )
        if str(kwargs["role"]) == "gemma":
            call = dict(kwargs)
            call["role"] = "qwen"
            call["stage"] = f"{base_stage}_qwen_fallback"
            call["seed_label"] = f"v071:{kwargs['seed_label']}:qwen_fallback"
            call["user_prompt"] = (
                original_user.rstrip()
                + "\n\nCROSS-MODEL TRANSPORT RECOVERY: Produce one complete replacement "
                + "record from the task. Do not continue any prior response. The schema "
                + "and task semantics are unchanged.\n\n"
                + COMPACT_INSTRUCTION
            )
            try:
                record, generation = super().structured(**call)
                metadata = dict(generation["metadata"])
                attempts.append(
                    {
                        "phase": "qwen_fallback",
                        "stage": call["stage"],
                        "status": "accepted",
                        "finish_reason": metadata.get("finish_reason"),
                        "deterministic_cleanup": None,
                        "repetition_detection_preserved": True,
                    }
                )
                metadata["v071_recovery_attempts"] = attempts
                self._record_recovery(
                    kind="structured", stage=base_stage, attempts=attempts, accepted=True
                )
                return record, {**generation, "metadata": metadata}
            except TimeoutRecoveryFailure:
                raise
            except Exception as error:
                saved = self.saved_generation(Path(kwargs["destination"]), call["stage"])
                metadata = dict(saved["metadata"]) if saved else {}
                attempts.append(
                    {
                        "phase": "qwen_fallback",
                        "stage": call["stage"],
                        "status": "rejected",
                        "finish_reason": metadata.get("finish_reason"),
                        "error": f"{type(error).__name__}: {error}",
                        "deterministic_cleanup": None,
                        "repetition_detection_preserved": True,
                    }
                )
        self._record_recovery(
            kind="structured", stage=base_stage, attempts=attempts, accepted=False
        )
        raise RuntimeError(f"structured recovery exhausted: {attempts}")

    def text(self, **kwargs: Any) -> dict[str, Any]:
        base_stage = str(kwargs["stage"])
        original_prompt = str(kwargs["prompt"])
        attempts: list[dict[str, Any]] = []
        partial = ""
        for attempt in range(TEXT_MAX_ATTEMPTS):
            call = dict(kwargs)
            if attempt:
                call["stage"] = f"{base_stage}_replacement_{attempt}"
                call["seed_label"] = f"v071:{kwargs['seed_label']}:replacement:{attempt}"
                call["prompt"] = (
                    original_prompt.rstrip()
                    + "\n\nTRANSPORT RECOVERY: The preceding response was empty or ended at "
                    + "a repetition or length boundary. Produce a complete replacement from "
                    + "the beginning. Do not continue or reproduce the repeated suffix. "
                    + "Preserve correct task content only.\n\nPRIOR INCOMPLETE RESPONSE:\n"
                    + partial.rstrip()[-12_000:]
                )
            generated = super().text(**call)
            metadata = dict(generated["metadata"])
            partial = str(generated["text"])
            finish = metadata.get("finish_reason")
            accepted = bool(partial.strip()) and finish not in {"repetition", "length"}
            attempts.append(
                {
                    "attempt": attempt,
                    "stage": call["stage"],
                    "finish_reason": finish,
                    "empty": not bool(partial.strip()),
                    "accepted": accepted,
                    "repetition_detection_preserved": True,
                }
            )
            if accepted:
                metadata["v071_recovery_attempts"] = attempts
                self._record_recovery(
                    kind="text", stage=base_stage, attempts=attempts, accepted=True
                )
                return {**generated, "metadata": metadata}
        self._record_recovery(
            kind="text", stage=base_stage, attempts=attempts, accepted=False
        )
        raise RuntimeError(f"text recovery exhausted: {attempts}")
