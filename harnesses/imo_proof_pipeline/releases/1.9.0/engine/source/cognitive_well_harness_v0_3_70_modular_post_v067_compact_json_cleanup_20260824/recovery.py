from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Callable

from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.contracts import (
    validate_schema,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import (
    ModelRuntime,
    REPETITION_DETECTION,
    RuntimeConfig,
    parse_json_object,
)
from cognitive_well_harness_v0_3_66_modular_six_to_two_proof_selection_20260824 import (
    pipeline as frozen_v066,
)


RECOVERY_PHASES = ("compact", "repair_1", "repair_2")

COMPACT_INSTRUCTION = """

OUTPUT TRANSPORT CONTRACT:
Return the entire requested record as exactly one compact JSON object on one line.
Do not use Markdown fences. Do not pretty-print. Do not insert blank lines. Emit every
required field exactly once, close all arrays and objects, and stop immediately after
the final `}`. The mathematical and semantic requirements in the task are unchanged.
""".strip()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _saved_failure(
    runtime: ModelRuntime,
    *,
    output_dir: Path,
    stage: str,
) -> tuple[str, dict[str, Any] | None]:
    saved = runtime.saved_generation(output_dir, stage)
    if saved is None:
        return "", None
    return str(saved["text"]), dict(saved["metadata"])


def _repair_prompt(
    *,
    original_user_prompt: str,
    partial: str,
    required_fields: list[str],
    prior_error: str,
) -> str:
    clipped = partial[-12_000:]
    return (
        original_user_prompt.rstrip()
        + "\n\nRECOVERY TASK:\n"
        + "The preceding draft entered a whitespace/repetition loop or failed strict "
        + "validation. Do not append to it and do not reproduce its trailing whitespace. "
        + "Reconstruct the complete record from the task and return a full replacement "
        + "as one compact JSON object on one line. Preserve useful mathematical content "
        + "from the draft only when it is correct. Required top-level fields: "
        + ", ".join(required_fields)
        + ". Prior validation error: "
        + prior_error
        + "\n\nINCOMPLETE DRAFT FOR RECOVERY:\n"
        + clipped
        + "\n\n"
        + COMPACT_INSTRUCTION
    )


def _clean_duplicate_wrapper_prefix(value: str) -> tuple[str, str] | None:
    """Repair only the observed `{"{` transport prefix; do not infer JSON content."""
    text = value.strip()
    if text.startswith('{"{') and text.endswith("}"):
        return text[2:], "drop_exact_duplicate_wrapper_prefix"
    return None


def structured_with_compact_cleanup(
    *,
    runtime: ModelRuntime,
    prompt: str,
    user_prompt: str,
    output_dir: Path,
    stage_prefix: str,
    schema: dict[str, Any],
    max_tokens: int,
    seed_label: str,
    validator: Callable[[dict[str, Any]], None],
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    attempts: list[dict[str, Any]] = []
    previous_partial = ""
    previous_error = "none"
    required_fields = [str(value) for value in schema.get("required", [])]

    for phase_index, phase in enumerate(RECOVERY_PHASES):
        stage = f"{stage_prefix}_{phase}"
        phase_prompt = (
            user_prompt.rstrip() + "\n\n" + COMPACT_INSTRUCTION
            if phase == "compact"
            else _repair_prompt(
                original_user_prompt=user_prompt,
                partial=previous_partial,
                required_fields=required_fields,
                prior_error=previous_error,
            )
        )
        try:
            record, generation = runtime.structured(
                role="gemma",
                prompt=prompt,
                user_prompt=phase_prompt,
                destination=output_dir,
                stage=stage,
                schema=schema,
                temperature=frozen_v066.TEMPERATURE,
                max_tokens=max_tokens,
                seed_label=f"v070:{seed_label}:{phase_index}:{phase}",
            )
            validator(record)
            attempts.append(
                {
                    "phase": phase,
                    "stage": stage,
                    "status": "accepted",
                    "finish_reason": generation["metadata"].get("finish_reason"),
                    "deterministic_cleanup": None,
                    "repetition_detection_preserved": True,
                }
            )
            return record, generation, attempts
        except Exception as error:
            previous_partial, metadata = _saved_failure(
                runtime, output_dir=output_dir, stage=stage
            )
            previous_error = f"{type(error).__name__}: {error}"
            finish_reason = metadata.get("finish_reason") if metadata else None

            cleanup = _clean_duplicate_wrapper_prefix(previous_partial)
            if cleanup is not None and metadata is not None:
                cleaned_text, cleanup_name = cleanup
                try:
                    record = parse_json_object(cleaned_text)
                    validate_schema(record, schema)
                    validator(record)
                    generation = {"text": previous_partial, "metadata": metadata}
                    attempts.append(
                        {
                            "phase": phase,
                            "stage": stage,
                            "status": "accepted_after_deterministic_cleanup",
                            "finish_reason": finish_reason,
                            "initial_error": previous_error,
                            "partial_length": len(previous_partial),
                            "partial_sha256": sha256_text(previous_partial),
                            "deterministic_cleanup": cleanup_name,
                            "repetition_recovery_triggered": finish_reason
                            == "repetition",
                            "repetition_detection_preserved": True,
                        }
                    )
                    return record, generation, attempts
                except Exception as cleanup_error:
                    previous_error += (
                        "; deterministic cleanup rejected: "
                        + f"{type(cleanup_error).__name__}: {cleanup_error}"
                    )

            attempts.append(
                {
                    "phase": phase,
                    "stage": stage,
                    "status": "rejected",
                    "finish_reason": finish_reason,
                    "error": previous_error,
                    "partial_length": len(previous_partial),
                    "partial_sha256": (
                        sha256_text(previous_partial) if previous_partial else None
                    ),
                    "deterministic_cleanup": None,
                    "repetition_recovery_triggered": finish_reason == "repetition",
                    "repetition_detection_preserved": True,
                }
            )
    raise RuntimeError(f"compact structured recovery exhausted phases: {attempts}")


def run_recovered_v066(
    *,
    run_input: dict[str, Any],
    input_path: Path,
    output_dir: Path,
    runtime_config: RuntimeConfig,
    batch_size: int,
) -> dict[str, Any]:
    original = frozen_v066.structured_with_attempts
    try:
        frozen_v066.structured_with_attempts = structured_with_compact_cleanup
        return frozen_v066.run_pipeline(
            run_input=run_input,
            input_path=input_path,
            output_dir=output_dir,
            runtime_config=runtime_config,
            batch_size=batch_size,
        )
    finally:
        frozen_v066.structured_with_attempts = original


def recovery_profile() -> dict[str, Any]:
    return {
        "phases": list(RECOVERY_PHASES),
        "compact_full_record_first": True,
        "repair_regenerates_entire_record": True,
        "raw_suffix_splicing": False,
        "deterministic_cleanup": ["drop_exact_duplicate_wrapper_prefix"],
        "cleanup_requires_schema_and_semantic_validation": True,
        "strict_schema_validation_after_every_phase": True,
        "semantic_validation_after_every_phase": True,
        "repetition_detection_preserved": True,
        "repetition_detection": dict(REPETITION_DETECTION),
    }

