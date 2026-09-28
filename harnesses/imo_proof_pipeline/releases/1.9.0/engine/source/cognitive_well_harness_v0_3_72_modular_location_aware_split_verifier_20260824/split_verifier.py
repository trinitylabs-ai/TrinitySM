from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.contracts import validate_schema
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import (
    RuntimeConfig,
    parse_json_object,
    write_json,
)

from .contracts import ALIGNMENT_SCHEMA, VALIDITY_SCHEMA
from .prompts import (
    ALIGNMENT_PROMPT,
    PROMPT_REVISION,
    VALIDITY_PROMPT,
    alignment_user_prompt,
    validity_user_prompt,
)
from .runtime import ResilientModelRuntime


VERIFIER_TEMPERATURE = 0.1
VERIFIER_MAX_TOKENS = 32_768


def make_gemma_verifier_runtime(config: RuntimeConfig) -> ResilientModelRuntime:
    """Pin both recovery roles to Gemma so fallback cannot change verifier models."""
    return ResilientModelRuntime(
        RuntimeConfig(
            gemma_endpoint=config.gemma_endpoint,
            qwen_endpoint=config.gemma_endpoint,
            gemma_model=config.gemma_model,
            qwen_model=config.gemma_model,
            master_seed=config.master_seed,
        )
    )


def formal_negation(claim: str) -> str:
    return f"It is not the case that the following statement holds: ({claim})"


def _cleanup_saved(
    *,
    runtime: ResilientModelRuntime,
    destination: Path,
    stage: str,
    schema: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]] | None:
    saved = runtime.saved_generation(destination, stage)
    if saved is None:
        return None
    partial = str(saved["text"]).rstrip()
    try:
        record = parse_json_object(partial + "}")
        validate_schema(record, schema)
        metadata = dict(saved["metadata"])
        metadata["v072_deterministic_cleanup"] = "append_one_missing_closing_brace"
        return record, {"text": partial + "}", "metadata": metadata}
    except (ValueError, KeyError):
        pass
    decoder = json.JSONDecoder()
    records: dict[str, dict[str, Any]] = {}
    for offset, character in enumerate(partial):
        if character != "{":
            continue
        try:
            candidate, _ = decoder.raw_decode(partial, offset)
            validate_schema(candidate, schema)
        except (json.JSONDecodeError, ValueError, KeyError, TypeError):
            continue
        canonical = json.dumps(candidate, sort_keys=True, separators=(",", ":"))
        records[canonical] = candidate
    if len(records) != 1:
        return None
    record = next(iter(records.values()))
    metadata = dict(saved["metadata"])
    metadata["v072_deterministic_cleanup"] = (
        "extract_unique_embedded_schema_valid_json_object"
    )
    return record, {"text": json.dumps(record), "metadata": metadata}


def structured_with_cleanup(
    *,
    runtime: ResilientModelRuntime,
    destination: Path,
    stage: str,
    schema: dict[str, Any],
    **kwargs: Any,
) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        return runtime.structured(
            destination=destination,
            stage=stage,
            schema=schema,
            **kwargs,
        )
    except Exception:
        repaired = _cleanup_saved(
            runtime=runtime,
            destination=destination,
            stage=stage,
            schema=schema,
        )
        if repaired is not None:
            return repaired
        raise


def split_certify(
    *,
    runtime: ResilientModelRuntime,
    problem: str,
    assigned_claim: str,
    proof: str,
    output_dir: Path,
    seed_label: str,
) -> dict[str, Any]:
    """Two alignment calls plus one validity call; the harness computes the result."""
    opposite_claim = formal_negation(assigned_claim)
    request = alignment_user_prompt(
        problem=problem,
        assigned_claim=assigned_claim,
        opposite_claim=opposite_claim,
        proof=proof,
    )

    def align(number: int) -> tuple[dict[str, Any], dict[str, Any]]:
        return structured_with_cleanup(
            runtime=runtime,
            role="gemma",
            prompt=ALIGNMENT_PROMPT,
            user_prompt=request,
            destination=output_dir / f"alignment_{number}",
            stage="claim_alignment",
            schema=ALIGNMENT_SCHEMA,
            temperature=VERIFIER_TEMPERATURE,
            max_tokens=VERIFIER_MAX_TOKENS,
            seed_label=f"v072:{seed_label}:alignment:{number}",
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        outputs = list(executor.map(align, (1, 2)))
    classifications = [str(row[0]["classification"]) for row in outputs]
    unanimous = classifications[0] if len(set(classifications)) == 1 else None
    routed_target = None
    routed_claim = None
    if unanimous == "PROVES_ASSIGNED_CLAIM":
        routed_target = "assigned_claim"
        routed_claim = assigned_claim
    elif unanimous == "PROVES_OPPOSITE_CLAIM":
        routed_target = "opposite_claim"
        routed_claim = opposite_claim

    validity = None
    validity_generation = None
    if routed_claim is not None:
        validity, validity_generation = structured_with_cleanup(
            runtime=runtime,
            role="gemma",
            prompt=VALIDITY_PROMPT,
            user_prompt=validity_user_prompt(
                problem=problem,
                target_claim=routed_claim,
                proof=proof,
            ),
            destination=output_dir / "mathematical_validity",
            stage="mathematical_validity",
            schema=VALIDITY_SCHEMA,
            temperature=VERIFIER_TEMPERATURE,
            max_tokens=VERIFIER_MAX_TOKENS,
            seed_label=f"v072:{seed_label}:mathematical_validity",
        )
    validity_pass = bool(validity is not None and validity["verdict"] == "PASS")
    certified = routed_claim is not None and validity_pass
    result = {
        "prompt_revision": PROMPT_REVISION,
        "model": runtime.config.gemma_model,
        "temperature": VERIFIER_TEMPERATURE,
        "max_tokens": VERIFIER_MAX_TOKENS,
        "reasoning_effort": "max",
        "alignment_results": [row[0] for row in outputs],
        "alignment_deterministic_cleanups": [
            row[1].get("metadata", {}).get("v072_deterministic_cleanup")
            for row in outputs
        ],
        "unanimous_classification": unanimous,
        "routed_target": routed_target,
        "routed_claim": routed_claim,
        "mathematical_validity_result": validity,
        "mathematical_validity_deterministic_cleanup": (
            validity_generation.get("metadata", {}).get("v072_deterministic_cleanup")
            if validity_generation is not None
            else None
        ),
        "mathematical_validity_pass": validity_pass,
        "certified": certified,
        "assigned_claim_certified": bool(certified and routed_target == "assigned_claim"),
        "opposite_claim_salvaged": bool(certified and routed_target == "opposite_claim"),
        "harness_computes_certification": True,
    }
    write_json(output_dir / "summary.json", result)
    return result
