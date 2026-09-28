from __future__ import annotations

import copy
import hashlib
import json
import re
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable

from cognitive_well_harness_v0_3_325_single_model_problem_pipeline_20260909 import runtime as single_model

from cognitive_well_harness_v0_3_263_v260_unified_recovery_20260905 import (
    pipeline as v263,
)
from cognitive_well_harness_v0_3_266_p5_repair_brief_certification_20260905 import (
    pipeline as brief_stage,
)
from experiments.local_math_verifier import runtime as transport

from . import HARNESS_VERSION


TOKEN_CAPS = (32_768, 49_152, 65_536)
QWEN_MAX_OUTPUT_TOKENS = 49_152
QWEN_TOKEN_POLICY = "qwen-49152-no-cap-retry-v1"
DEFAULT_MODEL_TIMEOUT_SEC = 600
MAX_REWRITE_ROUNDS = 2
MAX_ACCEPTANCE_RECONSIDERATIONS = 2
UNCERTIFIED_SYNTHESIS_POLICY = "synthesize_with_rejected_brief"
QWEN_MODEL = brief_stage.QWEN_MODEL
GEMMA_MODEL = brief_stage.GEMMA_MODEL

stage = v263.parent.parent.parent.v108.v097.enhanced_pipeline

Parser = Callable[[str], dict[str, Any]]
MarkdownCaller = Callable[..., dict[str, Any]]


def token_policy_for(model: str) -> str | None:
    return QWEN_TOKEN_POLICY if model == QWEN_MODEL and not single_model.active() else None


def token_caps_for(model: str, policy: str | None) -> tuple[int, ...]:
    # A missing marker is the historical schedule, retained for artifact replay.
    if policy is None:
        return TOKEN_CAPS
    if policy != QWEN_TOKEN_POLICY or model != QWEN_MODEL:
        raise ValueError("unknown or mismatched model token policy")
    # Preserve bounded parser/transport recovery, but never increase the cap.
    return (QWEN_MAX_OUTPUT_TOKENS,) * len(TOKEN_CAPS)


class RepairBriefCertificationError(RuntimeError):
    """Raised when no certified repair brief exists after the frozen retries."""


class FusionAcceptanceCertificationError(RuntimeError):
    """Raised when an accepting Fusion cannot survive independent audit."""


ACCEPTANCE_CERTIFIER_SYSTEM_PROMPT = r"""You are an independent adversarial certifier of a Fusion Judge's accepting decision for an Olympiad proof.

Read the complete problem and submitted proof. Treat the Fusion record as untrusted. Reconstruct the essential proof route and audit its load-bearing implications in order. Check quantifiers, inequality directions, local-to-global transitions, orbit or iteration claims, boundary cases, and whether every asserted maximum, limit, density, continuity, or connectedness premise was actually established.

Return CERTIFIED only if the submitted proof is literally complete and correct by Olympiad standards, or if an ACCEPT_WITH_ROUTINE_COMPLETION record supplies an exact genuinely routine completion that makes it complete without a new idea. Otherwise return REJECTED at the earliest substantive break. Do not repair the proof and do not use a reference solution.

Return exactly one Markdown document:

# Fusion Acceptance Certification
verdict: CERTIFIED or REJECTED

## Atomic Checks
List the load-bearing checks.

## First Invalid Step
State it, or NONE.

## Missing Obligation
State it, or NONE.

## Counterexample or Failure Witness
State one, or NONE.

## Certification Summary
State the decisive conclusion.

# End Fusion Acceptance Certification

Do not emit JSON."""


FUSION_RECONSIDERATION_SUFFIX = r"""

The prior accepting Fusion decision was rejected by an independent proof-level audit supplied in the user message. Perform a fresh adjudication. Do not preserve the prior verdict by default. If a material defect is validated, output REPAIR_NEEDED with a precise, mathematically viable resolver_brief. Return only one record in the original Fusion protocol."""


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _require_child(root: Path, path: Path, label: str) -> Path:
    root = root.resolve()
    path = path.resolve()
    try:
        path.relative_to(root)
    except ValueError as error:
        raise ValueError(f"{label} escapes {root}: {path}") from error
    return path


def stable_seed(*parts: str) -> int:
    digest = hashlib.sha256(":".join(parts).encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big")


def _parser_feedback(errors: list[str]) -> str:
    if not errors:
        return ""
    compact = " | ".join(" ".join(str(error).split()) for error in errors)
    return (
        "\n\n## Compact parser feedback from the preceding fresh attempt\n"
        f"{compact[:1600]}\n"
        "Return a new complete Markdown document satisfying the exact requested "
        "headings and labels. Do not discuss this feedback."
    )


def default_markdown_call(
    *,
    endpoint: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    output_dir: Path,
    stage_name: str,
    temperature: float,
    seed_key: str,
    reasoning_effort: str | None,
    parser: Parser,
    model_timeout_sec: int = DEFAULT_MODEL_TIMEOUT_SEC,
) -> dict[str, Any]:
    """Run one Markdown logical call under the model-specific cap policy.

    Mandatory same-trace budget forcing is supplied by the imported v0.3.263
    transport. Parser failures receive compact formatting feedback; transport
    failures do not become model feedback. Qwen cap exhaustion is terminal;
    only non-cap failures may receive another fixed-49k attempt.
    """

    if not 30 <= model_timeout_sec <= 14_400:
        raise ValueError("model timeout must be between 30 and 14400 seconds")
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    parser_errors: list[str] = []
    attempts: list[dict[str, Any]] = []
    last_error = "no attempt"
    token_policy = token_policy_for(model)
    token_caps = token_caps_for(model, token_policy)
    for attempt_index, cap in enumerate(token_caps, start=1):
        attempt_dir = output_dir / f"attempt_{attempt_index:02d}_cap_{cap}"
        attempt_dir.mkdir(parents=True, exist_ok=False)
        effective_user_prompt = user_prompt + _parser_feedback(parser_errors)
        stage = f"{stage_name}_cap_{cap}"
        try:
            generated = transport.run_openai_chat_generation(
                endpoint=endpoint.rstrip("/"),
                model=model,
                prompt=system_prompt,
                user_prompt=effective_user_prompt,
                output_dir=attempt_dir,
                stage=stage,
                config=transport.HTTPGenerationConfig(
                    max_tokens=cap,
                    temperature=temperature,
                    top_p=1.0,
                    top_k=-1,
                    seed=stable_seed(seed_key, str(cap)),
                    thinking_token_budget=None,
                    reasoning_effort=reasoning_effort,
                    timeout_seconds=model_timeout_sec,
                ),
            )
        except Exception as error:
            last_error = f"{type(error).__name__}: {error}"
            row = {
                "attempt": attempt_index,
                "cap": cap,
                "state": "transport_failed",
                "error": last_error,
                "parser_feedback_supplied": bool(parser_errors),
                "transport_error_added_to_feedback": False,
                "request_timeout_sec": model_timeout_sec,
            }
            attempts.append(row)
            write_json(attempt_dir / "validation.json", row)
            continue

        metadata = dict(generated.get("metadata") or {})
        text = str(generated.get("text") or "").strip()
        finish_reason = str(metadata.get("finish_reason") or "")
        forcing = metadata.get("v0257_budget_forcing")
        errors: list[str] = []
        parsed: dict[str, Any] = {}
        if finish_reason == "length":
            errors.append(f"canonical response exhausted cap {cap}")
        elif not text:
            errors.append("canonical response was empty")
        else:
            try:
                parsed = parser(text)
            except Exception as error:
                errors.append(f"parser raised {type(error).__name__}: {error}")
            else:
                if not isinstance(parsed, dict) or not parsed.get("valid"):
                    details = parsed.get("errors") if isinstance(parsed, dict) else None
                    errors.extend(str(item) for item in (details or ["parser rejected Markdown"]))
        if single_model.active():
            try:
                single_model.validate_unforced(metadata,text)
            except ValueError as error:
                errors.append(str(error))
        elif not isinstance(forcing, dict):
            errors.append("mandatory budget-forcing metadata is missing")
        else:
            if forcing.get("canonical_artifacts_are_forced_response") is not True:
                errors.append("canonical artifacts are not the forced response")
            if str(forcing.get("forced_text_sha256") or "") != sha256_text(text):
                errors.append("forced-response text hash mismatch")
        budget_path = attempt_dir / f"{stage}.budget_forcing.json"
        if single_model.active():
            policy_path=attempt_dir/f"{stage}.generation_policy.json"
            if not policy_path.is_file() or read_object(policy_path)!=metadata.get("single_model_policy"):
                errors.append("single-model generation policy event is missing or changed")
            if budget_path.exists():
                errors.append("unforced call unexpectedly has a budget-forcing event")
        elif not budget_path.is_file():
            errors.append("mandatory budget-forcing event is missing")
        elif isinstance(forcing, dict):
            budget = read_object(budget_path)
            if budget.get("canonical_artifacts_are_forced_response") is not True:
                errors.append("budget event does not identify the forced response")
            if str(budget.get("forced_text_sha256") or "") != sha256_text(text):
                errors.append("budget event forced-response hash mismatch")
            for name in ("original_config", "forced_config"):
                config = budget.get(name)
                if not isinstance(config, dict) or int(config.get("max_tokens") or 0) != cap:
                    errors.append(f"{name} did not preserve cap {cap}")
        row = {
            "attempt": attempt_index,
            "cap": cap,
            "state": "accepted" if not errors else "rejected",
            "finish_reason": finish_reason,
            "text_sha256": sha256_text(text),
            "parser_feedback_supplied": bool(parser_errors),
            "errors": errors,
            "request_timeout_sec": model_timeout_sec,
        }
        attempts.append(row)
        write_json(attempt_dir / "validation.json", row)
        if not errors:
            final_path = output_dir / f"{stage_name}.final.md"
            final_path.write_text(text + "\n", encoding="utf-8")
            result = {
                "token_policy": token_policy,
                "text": text,
                "parsed": parsed,
                "metadata": metadata,
                "attempts": attempts,
                "attempt_dir": str(attempt_dir),
                "final_path": str(final_path.resolve()),
                "final_sha256": sha256_text(text),
            }
            write_json(output_dir / "call_result.json", result)
            return result
        parser_errors = errors
        last_error = " | ".join(errors)
        if token_policy == QWEN_TOKEN_POLICY and finish_reason == "length":
            write_json(output_dir / "call_failure.json", {
                "state": "output_cap_reached", "token_policy": token_policy,
                "attempts": attempts, "retry_performed_after_cap": False,
            })
            raise RuntimeError(f"{stage_name} reached token cap {cap}; token-cap retries are disabled")
    raise RuntimeError(f"{stage_name} exhausted recovery caps {token_caps}: {last_error}")


def assert_only_resolver_brief_changed(source: str, effective: str) -> None:
    if source == effective:
        return
    source_lines = source.splitlines()
    effective_lines = effective.splitlines()
    if len(source_lines) != len(effective_lines):
        raise RuntimeError("repair rewrite changed Fusion line count")
    differences = [
        (left, right)
        for left, right in zip(source_lines, effective_lines)
        if left != right
    ]
    if (
        len(differences) != 1
        or not differences[0][0].startswith("resolver_brief:")
        or not differences[0][1].startswith("resolver_brief:")
    ):
        raise RuntimeError("effective Fusion changed material outside resolver_brief")


def _public_result(value: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(value)
    result.pop("_v290_effective_result_path", None)
    return result


def _bind_markdown_call(
    value: dict[str, Any], *, call_root: Path, model: str
) -> dict[str, Any]:
    """Bind accepted Markdown to its mandatory forced-response producer."""

    text = str(value.get("text") or "").strip()
    declared_hash = str(value.get("final_sha256") or "")
    if not text or sha256_text(text) != declared_hash:
        raise ValueError("accepted Markdown text/hash mismatch")
    final_path = Path(str(value.get("final_path") or "")).resolve()
    try:
        final_path.relative_to(call_root.resolve())
    except ValueError as error:
        raise ValueError("accepted Markdown path escapes its call root") from error
    if not final_path.is_file():
        raise FileNotFoundError(final_path)
    if sha256_text(final_path.read_text(encoding="utf-8").strip()) != declared_hash:
        raise ValueError("accepted Markdown artifact/hash mismatch")
    forcing = (value.get("metadata") or {}).get("v0257_budget_forcing")
    unforced=single_model.active()
    model=single_model.effective_model(model)
    token_policy = value.get("token_policy")
    if token_policy != token_policy_for(model):
        raise ValueError("accepted Markdown token policy changed")
    token_caps = token_caps_for(model, token_policy)
    if unforced:
        single_model.validate_unforced(value.get("metadata") or {},text)
    elif not isinstance(forcing, dict):
        raise ValueError("accepted Markdown lacks budget-forcing producer metadata")
    if not unforced and forcing.get("canonical_artifacts_are_forced_response") is not True:
        raise ValueError("canonical Markdown is not the forced response")
    forced_hash = declared_hash if unforced else str(forcing.get("forced_text_sha256") or "")
    if forced_hash != declared_hash:
        raise ValueError("forced-response producer hash mismatch")
    attempt_dir = Path(str(value.get("attempt_dir") or "")).resolve()
    try:
        attempt_dir.relative_to(call_root.resolve())
    except ValueError as error:
        raise ValueError("accepted attempt path escapes its call root") from error
    attempts = value.get("attempts")
    if not isinstance(attempts, list) or not attempts:
        raise ValueError("accepted Markdown lacks an attempt ledger")
    accepted_rows = [row for row in attempts if row.get("state") == "accepted"]
    if len(accepted_rows) != 1 or accepted_rows[0] is not attempts[-1]:
        raise ValueError("attempt ledger must end in exactly one accepted attempt")
    cap = int(accepted_rows[0].get("cap") or 0)
    if (not 1 <= len(attempts) <= len(token_caps)
            or cap != token_caps[len(attempts) - 1]
            or attempt_dir.name != f"attempt_{len(attempts):02d}_cap_{cap}"):
        raise ValueError("accepted attempt cap/path does not match the recovery ledger")

    def one_artifact(suffix: str) -> Path:
        paths = sorted(
            path
            for path in attempt_dir.glob(f"*{suffix}")
            if ".pre_budget_forcing." not in path.name
        )
        if len(paths) != 1:
            raise ValueError(
                f"expected one canonical {suffix} producer artifact, found {len(paths)}"
            )
        return paths[0].resolve()

    raw_path = one_artifact(".raw_response.json")
    metadata_path = one_artifact(".metadata.json")
    budget_path = one_artifact(".generation_policy.json" if unforced else ".budget_forcing.json")
    prompt_path = one_artifact(".prompt.txt")
    user_prompt_path = one_artifact(".user_prompt.txt")
    validation_path = attempt_dir / "validation.json"
    if not validation_path.is_file():
        raise FileNotFoundError(validation_path)
    raw = read_object(raw_path)
    choices = raw.get("choices")
    if not isinstance(choices, list) or len(choices) != 1:
        raise ValueError("canonical raw response must contain exactly one choice")
    message = choices[0].get("message") if isinstance(choices[0], dict) else None
    raw_text = str((message or {}).get("content") or "").strip()
    if sha256_text(raw_text) != declared_hash:
        raise ValueError("canonical raw response text/hash mismatch")
    persisted_metadata = read_object(metadata_path)
    persisted_forcing = persisted_metadata.get("v0257_budget_forcing")
    if unforced:
        single_model.validate_unforced(persisted_metadata,raw_text)
        if read_object(budget_path)!=persisted_metadata["single_model_policy"]:
            raise ValueError("unforced producer event mismatch")
    elif not isinstance(persisted_forcing, dict):
        raise ValueError("canonical metadata lacks budget-forcing provenance")
    budget = read_object(budget_path)
    for persisted in (() if unforced else (persisted_forcing, budget)):
        if (
            persisted.get("canonical_artifacts_are_forced_response") is not True
            or str(persisted.get("forced_text_sha256") or "") != declared_hash
        ):
            raise ValueError("persisted budget-forcing producer hash mismatch")
    for name in (() if unforced else ("original_config", "forced_config")):
        config = budget.get(name)
        if not isinstance(config, dict) or int(config.get("max_tokens") or 0) != cap:
            raise ValueError(f"persisted {name} cap mismatch")
    validation = read_object(validation_path)
    if (
        validation.get("state") != "accepted"
        or int(validation.get("cap") or 0) != cap
        or str(validation.get("text_sha256") or "") != declared_hash
    ):
        raise ValueError("accepted validation artifact is inconsistent")
    return {
        "model": model,
        "token_policy": token_policy,
        "call_root": str(call_root.resolve()),
        "attempt_dir": str(attempt_dir),
        "attempt_count": len(attempts),
        "cap": cap,
        "final_path": str(final_path),
        "final_sha256": declared_hash,
        **({"canonical_text_sha256":declared_hash,"producer_policy":single_model.SCHEMA} if unforced
           else {"forced_text_sha256":forced_hash}),
        "raw_response_path": str(raw_path),
        "raw_response_file_sha256": file_sha256(raw_path),
        "metadata_path": str(metadata_path),
        "metadata_file_sha256": file_sha256(metadata_path),
        **({"generation_policy_path":str(budget_path),"generation_policy_file_sha256":file_sha256(budget_path)}
           if unforced else {"budget_forcing_path":str(budget_path),"budget_forcing_file_sha256":file_sha256(budget_path)}),
        "prompt_path": str(prompt_path),
        "prompt_file_sha256": file_sha256(prompt_path),
        "user_prompt_path": str(user_prompt_path),
        "user_prompt_file_sha256": file_sha256(user_prompt_path),
        "validation_path": str(validation_path.resolve()),
        "validation_file_sha256": file_sha256(validation_path),
    }


def verify_producer_binding(
    binding: dict[str, Any],
    *,
    allowed_root: Path,
    expected_model: str | None = None,
    expected_timeout_sec: int | None = None,
    expected_stage: str | None = None,
    expected_seed: int | None = None,
    expected_system_prompt: str | None = None,
    expected_base_user_prompt: str | None = None,
) -> str:
    """Replay the persisted forced-response producer binding without trusting JSON paths."""

    unforced=single_model.active()
    if unforced and binding.get("producer_policy")!=single_model.SCHEMA:
        raise ValueError("explicit unforced producer policy missing")
    if expected_model is not None:
        expected_model=single_model.effective_model(expected_model)

    call_root = Path(str(binding.get("call_root") or "")).resolve()
    _require_child(allowed_root, call_root, "model call root")
    attempt_dir = _require_child(
        call_root, Path(str(binding.get("attempt_dir") or "")), "model attempt"
    )
    cap = int(binding.get("cap") or 0)
    attempt_count = int(binding.get("attempt_count") or 0)
    model = str(binding.get("model") or "")
    if expected_model is not None and model != expected_model:
        raise ValueError("bound model identity changed")
    token_policy = binding.get("token_policy")
    token_caps = token_caps_for(model, token_policy)
    if not 1 <= attempt_count <= len(token_caps):
        raise ValueError("bound model attempt count changed")
    if cap != token_caps[attempt_count - 1] or attempt_dir.name != f"attempt_{attempt_count:02d}_cap_{cap}":
        raise ValueError("bound model attempt cap/path changed")
    attempt_dirs = sorted(
        path.resolve() for path in call_root.glob("attempt_*_cap_*") if path.is_dir()
    )
    if len(attempt_dirs) != attempt_count or attempt_dirs[-1] != attempt_dir:
        raise ValueError("bound model attempt history changed")
    for index, prior_dir in enumerate(attempt_dirs, start=1):
        expected_cap = token_caps[index - 1]
        if prior_dir.name != f"attempt_{index:02d}_cap_{expected_cap}":
            raise ValueError("bound model recovery rung changed")
        prior_validation = read_object(prior_dir / "validation.json")
        if int(prior_validation.get("cap") or 0) != expected_cap:
            raise ValueError("bound model recovery validation cap changed")
        if expected_timeout_sec is not None and int(
            prior_validation.get("request_timeout_sec") or 0
        ) != expected_timeout_sec:
            raise ValueError("bound model request timeout changed")
        state = str(prior_validation.get("state") or "")
        if (token_policy == QWEN_TOKEN_POLICY
                and prior_validation.get("finish_reason") == "length"):
            raise ValueError("capped Qwen response cannot be accepted or retried")
        if index < attempt_count and state == "accepted":
            raise ValueError("accepted model attempt was followed by another rung")
        if index == attempt_count and state != "accepted":
            raise ValueError("bound terminal model attempt is not accepted")
    artifact_fields = (
        ("raw_response_path", "raw_response_file_sha256"),
        ("metadata_path", "metadata_file_sha256"),
        (("generation_policy_path", "generation_policy_file_sha256") if unforced
         else ("budget_forcing_path", "budget_forcing_file_sha256")),
        ("prompt_path", "prompt_file_sha256"),
        ("user_prompt_path", "user_prompt_file_sha256"),
        ("validation_path", "validation_file_sha256"),
    )
    paths: dict[str, Path] = {}
    for path_key, hash_key in artifact_fields:
        path = _require_child(
            attempt_dir, Path(str(binding.get(path_key) or "")), path_key
        )
        if not path.is_file() or file_sha256(path) != str(binding.get(hash_key) or ""):
            raise ValueError(f"bound producer artifact changed: {path_key}")
        paths[path_key] = path
    final_path = _require_child(
        call_root, Path(str(binding.get("final_path") or "")), "accepted Markdown"
    )
    text = final_path.read_text(encoding="utf-8").strip()
    text_hash = sha256_text(text)
    if text_hash != str(binding.get("final_sha256") or ""):
        raise ValueError("bound accepted Markdown changed")
    raw = read_object(paths["raw_response_path"])
    choices = raw.get("choices")
    message = (
        choices[0].get("message")
        if isinstance(choices, list) and len(choices) == 1 and isinstance(choices[0], dict)
        else None
    )
    if sha256_text(str((message or {}).get("content") or "").strip()) != text_hash:
        raise ValueError("bound raw response does not reproduce accepted Markdown")
    metadata = read_object(paths["metadata_path"])
    if metadata.get("model") != model:
        raise ValueError("bound producer metadata model changed")
    config = metadata.get("config")
    if not isinstance(config, dict) or int(config.get("max_tokens") or 0) != cap:
        raise ValueError("bound producer metadata cap changed")
    if expected_timeout_sec is not None and int(config.get("timeout_seconds") or 0) != expected_timeout_sec:
        raise ValueError("bound producer metadata timeout changed")
    if expected_stage is not None and metadata.get("stage") != expected_stage:
        raise ValueError("bound producer metadata stage changed")
    if expected_seed is not None and int(config.get("seed") or -1) != expected_seed:
        raise ValueError("bound producer metadata seed changed")
    prompt_text = paths["prompt_path"].read_text(encoding="utf-8")
    user_prompt_text = paths["user_prompt_path"].read_text(encoding="utf-8")
    if metadata.get("prompt_sha256") != sha256_text(prompt_text):
        raise ValueError("bound producer system prompt identity changed")
    if metadata.get("user_prompt_sha256") != sha256_text(user_prompt_text):
        raise ValueError("bound producer user prompt identity changed")
    if expected_system_prompt is not None and prompt_text != expected_system_prompt:
        raise ValueError("bound producer system prompt content changed")
    if expected_base_user_prompt is not None:
        parser_errors: list[str] = []
        for prior_dir in attempt_dirs[:-1]:
            prior = read_object(prior_dir / "validation.json")
            if prior.get("state") == "rejected":
                errors = prior.get("errors")
                if not isinstance(errors, list) or not all(
                    isinstance(item, str) for item in errors
                ):
                    raise ValueError("bound rejected parser feedback changed")
                parser_errors = list(errors)
            elif prior.get("state") != "transport_failed":
                raise ValueError("bound prior model attempt state changed")
        expected_user_prompt = expected_base_user_prompt + _parser_feedback(parser_errors)
        if user_prompt_text != expected_user_prompt:
            raise ValueError("bound producer user prompt content changed")
    budget = read_object(paths["generation_policy_path" if unforced else "budget_forcing_path"])
    if unforced:
        single_model.validate_unforced(metadata,text)
        if budget!=metadata["single_model_policy"] or binding.get("canonical_text_sha256")!=text_hash:
            raise ValueError("unforced producer event or canonical text changed")
    for event in (() if unforced else (metadata.get("v0257_budget_forcing"), budget)):
        if not isinstance(event, dict) or (
            event.get("canonical_artifacts_are_forced_response") is not True
            or str(event.get("forced_text_sha256") or "") != text_hash
            or event.get("model") != model
        ):
            raise ValueError("bound forced-response event changed")
    for name in (() if unforced else ("original_config", "forced_config")):
        config = budget.get(name)
        if not isinstance(config, dict) or int(config.get("max_tokens") or 0) != cap:
            raise ValueError(f"bound {name} cap changed")
        if expected_timeout_sec is not None and int(
            config.get("timeout_seconds") or 0
        ) != expected_timeout_sec:
            raise ValueError(f"bound {name} timeout changed")
        if expected_seed is not None and int(config.get("seed") or -1) != expected_seed:
            raise ValueError(f"bound {name} seed changed")
    validation = read_object(paths["validation_path"])
    if (
        validation.get("state") != "accepted"
        or int(validation.get("cap") or 0) != cap
        or str(validation.get("text_sha256") or "") != text_hash
    ):
        raise ValueError("bound accepted validation changed")
    return text


def verify_gate_producer_history(
    record: dict[str, Any],
    *,
    allowed_root: Path,
    source_fusion: str,
    effective_fusion: str,
    task: dict[str, Any],
) -> None:
    """Replay every model-produced record in a completed Fusion boundary."""

    if record.get("state") != "completed":
        raise ValueError("Fusion boundary is not completed")
    timeout = int(record.get("model_timeout_sec") or 0)
    if timeout != DEFAULT_MODEL_TIMEOUT_SEC:
        raise ValueError("Fusion boundary timeout policy changed")
    if tuple(record.get("token_caps") or ()) != TOKEN_CAPS:
        raise ValueError("Fusion boundary recovery schedule changed")
    if record.get("qwen_token_policy") not in (None, QWEN_TOKEN_POLICY):
        raise ValueError("Fusion boundary Qwen token policy changed")
    source_fusion = source_fusion.strip()
    effective_fusion = effective_fusion.strip()
    if sha256_text(source_fusion) != str(record.get("source_fusion_sha256") or ""):
        raise ValueError("Fusion boundary source text/hash changed")
    if sha256_text(effective_fusion) != str(
        record.get("effective_fusion_sha256") or ""
    ):
        raise ValueError("Fusion boundary effective text/hash changed")
    problem, proof, task_id, proof_hash = _validate_task_inputs(task)
    cycle_key = str(record.get("cycle_key") or "")
    if not cycle_key:
        raise ValueError("Fusion boundary source identity is incomplete")
    if task_id != str(record.get("task_id") or ""):
        raise ValueError("Fusion boundary task identity changed")
    if sha256_text(problem) != str(record.get("problem_sha256") or ""):
        raise ValueError("Fusion boundary problem changed")
    if proof_hash != str(record.get("proof_sha256") or ""):
        raise ValueError("Fusion boundary proof changed")
    reviewer_hashes = {
        name: sha256_text(str(task.get(name) or "").strip())
        for name in ("reviewer_1", "reviewer_2", "reviewer_3")
    }
    if reviewer_hashes != record.get("reviewer_input_sha256"):
        raise ValueError("Fusion boundary reviewer inputs changed")
    history = record.get("history")
    if not isinstance(history, list) or not history:
        raise ValueError("Fusion boundary producer history is empty")

    def replay_producer(
        row: dict[str, Any],
        *,
        expected_model: str,
        seed_stage: str,
        stage_name: str,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        producer = row.get("producer")
        if not isinstance(producer, dict):
            raise ValueError("Fusion boundary history lacks producer binding")
        if (expected_model == QWEN_MODEL
                and producer.get("token_policy") != record.get("qwen_token_policy")):
            raise ValueError("Fusion boundary/producer Qwen token policy mismatch")
        round_index = int(row.get("round") or 0)
        cap = int(producer.get("cap") or 0)
        expected_seed = stable_seed(
            f"v0290:{cycle_key}:{task_id}:{proof_hash}:{seed_stage}:{round_index}",
            str(cap),
        )
        text = verify_producer_binding(
            producer,
            allowed_root=allowed_root,
            expected_model=expected_model,
            expected_timeout_sec=timeout,
            expected_stage=f"{stage_name}_cap_{cap}",
            expected_seed=expected_seed,
            expected_system_prompt=system_prompt,
            expected_base_user_prompt=user_prompt,
        )
        if sha256_text(text) != str(row.get("text_sha256") or ""):
            raise ValueError("Fusion boundary history text hash changed")
        return text

    def exact_report(
        row: dict[str, Any], *, defect_packet: str, repair_brief: str
    ) -> str | None:
        exact_binding = row.get("exact_evidence")
        if record.get("exact_evidence_enabled") is True and not isinstance(
            exact_binding, dict
        ):
            raise ValueError("repair-brief audit lacks exact-evidence attempt")
        report: str | None = None
        if isinstance(exact_binding, dict):
            from . import exact_evidence

            producer = row.get("producer") or {}
            report = exact_evidence.verify_exact_evidence_binding(
                exact_binding,
                audit_root=Path(str(producer.get("call_root") or "")),
                expected_problem_sha256=sha256_text(problem),
                expected_proof_sha256=proof_hash,
                expected_defect_packet_sha256=str(
                    record.get("defect_packet_sha256") or ""
                ),
                expected_repair_brief_sha256=str(
                    row.get("repair_brief_sha256") or ""
                ),
                expected_problem=problem,
                expected_proof=proof,
                expected_defect_packet=defect_packet,
                expected_repair_brief=repair_brief,
                producer_verifier=verify_producer_binding,
            )
        report_hash = sha256_text(report) if report is not None else None
        if report_hash != row.get("exact_evidence_report_sha256"):
            raise ValueError("repair-brief exact-evidence report changed")
        return report

    schema = str(record.get("schema") or "")
    if schema == "cognitive-well-v0290-repair-brief-gate-v1":
        source_parsed = stage.resolver.parse_fusion(source_fusion)
        if not source_parsed.get("valid") or source_parsed.get("outcome") != "REPAIR_NEEDED":
            raise ValueError("repair gate source Fusion is not REPAIR_NEEDED")
        source_brief = brief_stage.extract_resolver_brief(source_fusion)
        defect_packet = brief_stage.canonical_defect_packet(source_parsed)
        if sha256_text(defect_packet) != str(record.get("defect_packet_sha256") or ""):
            raise ValueError("repair gate canonical defect packet changed")
        if sha256_text(source_brief) != str(
            record.get("source_repair_brief_sha256") or ""
        ):
            raise ValueError("repair gate source brief hash changed")
        rewrite_count = int(record.get("rewrite_count") or 0)
        audit_count = int(record.get("audit_count") or 0)
        if audit_count != rewrite_count + 1 or len(history) != audit_count + rewrite_count:
            raise ValueError("repair-brief audit/rewrite counts changed")
        expected_kinds = ["audit"]
        for _round in range(1, rewrite_count + 1):
            expected_kinds.extend(("rewrite", "audit"))
        if [str(row.get("kind")) for row in history] != expected_kinds:
            raise ValueError("repair-brief audit/rewrite order changed")
        for index, row in enumerate(history):
            expected_round = (index + 1) // 2
            if int(row.get("round") or 0) != expected_round:
                raise ValueError("repair-brief history round changed")
        audits = [row for row in history if row.get("kind") == "audit"]
        if any(row.get("verdict") != "REJECTED" for row in audits[:-1]):
            raise ValueError("repair-brief retry followed a non-rejection")
        disposition = repair_brief_disposition(record)
        if disposition == "CERTIFIED":
            if int(record["certified_round"]) != rewrite_count:
                raise ValueError("repair-brief terminal certification changed")
        elif rewrite_count != MAX_REWRITE_ROUNDS:
            raise ValueError("uncertified synthesis requires the full repair schedule")
        current_fusion = source_fusion
        current_brief = source_brief
        last_audit_text = ""
        for row in history:
            if not isinstance(row, dict):
                raise ValueError("repair gate history row is malformed")
            kind = str(row.get("kind") or "")
            round_index = int(row.get("round") or 0)
            if kind == "audit":
                if sha256_text(current_brief) != str(
                    row.get("repair_brief_sha256") or ""
                ):
                    raise ValueError("repair audit/brief hash chain changed")
                report = exact_report(
                    row, defect_packet=defect_packet, repair_brief=current_brief
                )
                audit_prompt = brief_stage._certifier_user_prompt(
                    problem=problem,
                    proof=proof,
                    defect_packet=defect_packet,
                    repair_brief=current_brief,
                    pass_name=(
                        f"{cycle_key}:original"
                        if round_index == 0
                        else f"{cycle_key}:rewrite:{round_index}"
                    ),
                )
                if report:
                    audit_prompt += f"""

## Independently Verified Optional Exact Evidence

{report}

Use this evidence only for the exact finite/algebraic implication it reports. A
negative search result is not proof outside an exhaustively encoded finite domain.
"""
                text = replay_producer(
                    row,
                    expected_model=QWEN_MODEL,
                    seed_stage="audit",
                    stage_name="audit_repair_brief",
                    system_prompt=brief_stage.CERTIFIER_SYSTEM_PROMPT,
                    user_prompt=audit_prompt,
                )
                parsed = brief_stage.parse_certification_markdown(text)
                if not parsed.get("valid") or parsed.get("verdict") != row.get("verdict"):
                    raise ValueError("repair-brief audit producer parse changed")
                last_audit_text = text
                continue
            if kind != "rewrite" or not last_audit_text:
                raise ValueError("repair rewrite is not preceded by its rejection")
            rewrite_prompt = brief_stage._rewriter_user_prompt(
                problem=problem,
                proof=proof,
                defect_packet=defect_packet,
                rejected_brief=current_brief,
                rejection=last_audit_text,
            )
            text = replay_producer(
                row,
                expected_model=GEMMA_MODEL,
                seed_stage="rewrite",
                stage_name="rewrite_repair_brief",
                system_prompt=brief_stage.REWRITER_SYSTEM_PROMPT,
                user_prompt=rewrite_prompt,
            )
            parsed_rewrite = brief_stage.parse_rewriter_markdown(text)
            new_brief = str(parsed_rewrite.get("repair_brief") or "").strip()
            if not parsed_rewrite.get("valid") or sha256_text(new_brief) != str(
                row.get("repair_brief_sha256") or ""
            ):
                raise ValueError("repair rewrite producer parse changed")
            next_fusion = brief_stage.replace_resolver_brief(current_fusion, new_brief)
            assert_only_resolver_brief_changed(current_fusion, next_fusion)
            current_fusion = next_fusion
            current_brief = brief_stage.extract_resolver_brief(current_fusion)
            if sha256_text(current_brief) != str(
                row.get("repair_brief_sha256") or ""
            ):
                raise ValueError("repair rewrite/brief hash chain changed")
        if current_fusion != effective_fusion:
            raise ValueError("repair gate reconstructed Fusion changed")
        if sha256_text(current_brief) != str(
            record.get("effective_repair_brief_sha256") or ""
        ):
            raise ValueError("repair gate effective brief hash changed")
        return

    if schema != "cognitive-well-v0290-fusion-acceptance-gate-v1":
        raise ValueError("unknown Fusion boundary schema")
    source_parsed = stage.resolver.parse_fusion(source_fusion)
    if not source_parsed.get("valid") or source_parsed.get("outcome") != record.get(
        "source_outcome"
    ):
        raise ValueError("acceptance gate source Fusion outcome changed")
    expected_round = 0
    index = 0
    current_fusion = source_fusion
    terminal_certified = False
    terminal_repair = False
    while index < len(history):
        audit = history[index]
        if audit.get("kind") != "acceptance_audit" or int(
            audit.get("round") or 0
        ) != expected_round:
            raise ValueError("acceptance audit/reconsideration order changed")
        if sha256_text(current_fusion) != str(audit.get("fusion_sha256") or ""):
            raise ValueError("acceptance audit/Fusion hash chain changed")
        audit_text = replay_producer(
            audit,
            expected_model=QWEN_MODEL,
            seed_stage="acceptance_audit",
            stage_name="audit_fusion_acceptance",
            system_prompt=ACCEPTANCE_CERTIFIER_SYSTEM_PROMPT,
            user_prompt=_acceptance_user_prompt(
                problem=problem,
                proof=proof,
                fusion_record=current_fusion,
                pass_name=f"{cycle_key}:acceptance:{expected_round}",
            ),
        )
        parsed_audit = parse_acceptance_certification_markdown(audit_text)
        if not parsed_audit.get("valid") or parsed_audit.get("verdict") != audit.get(
            "verdict"
        ):
            raise ValueError("acceptance audit producer parse changed")
        index += 1
        if audit.get("verdict") == "CERTIFIED":
            terminal_certified = True
            break
        if audit.get("verdict") != "REJECTED" or index >= len(history):
            raise ValueError("acceptance retry did not follow a rejection")
        expected_round += 1
        reconsideration = history[index]
        if reconsideration.get("kind") != "fusion_reconsideration" or int(
            reconsideration.get("round") or 0
        ) != expected_round:
            raise ValueError("Fusion reconsideration order changed")
        current_fusion = replay_producer(
            reconsideration,
            expected_model=GEMMA_MODEL,
            seed_stage="fusion_reconsideration",
            stage_name="reconsider_fusion",
            system_prompt=stage.fusion.SYSTEM_PROMPT + FUSION_RECONSIDERATION_SUFFIX,
            user_prompt=_fusion_reconsideration_user_prompt(
                task=task,
                prior_fusion=current_fusion,
                rejection=audit_text,
            ),
        )
        parsed_reconsideration = stage.resolver.parse_fusion(current_fusion)
        if not parsed_reconsideration.get("valid") or parsed_reconsideration.get(
            "outcome"
        ) != reconsideration.get("outcome"):
            raise ValueError("Fusion reconsideration producer parse changed")
        index += 1
        if reconsideration.get("outcome") == "REPAIR_NEEDED":
            terminal_repair = True
            break
    if index != len(history):
        raise ValueError("Fusion boundary has producers after its terminal route")
    nested = record.get("repair_brief_gate")
    if terminal_repair:
        if not isinstance(nested, dict):
            raise ValueError("reconsidered repair lacks its mandatory brief gate")
        verify_gate_producer_history(
            nested,
            allowed_root=allowed_root,
            source_fusion=current_fusion,
            effective_fusion=effective_fusion,
            task=task,
        )
    elif nested is not None:
        raise ValueError("acceptance route unexpectedly contains a repair gate")
    if terminal_certified:
        if int(record.get("certified_acceptance_round")) != expected_round:
            raise ValueError("acceptance certification round changed")
        if current_fusion != effective_fusion:
            raise ValueError("acceptance gate reconstructed Fusion changed")
    elif not terminal_repair:
        raise ValueError("acceptance boundary has no certified terminal route")
    effective_parsed = stage.resolver.parse_fusion(effective_fusion)
    if not effective_parsed.get("valid") or effective_parsed.get("outcome") != record.get(
        "effective_outcome"
    ):
        raise ValueError("acceptance gate effective Fusion outcome changed")


def _markdown_section(value: str, heading: str, next_heading: str) -> str:
    pattern = re.compile(
        rf"(?ms)^{re.escape(heading)}\s*\n(.*?)\n^{re.escape(next_heading)}\s*$"
    )
    match = pattern.search(value.strip())
    return match.group(1).strip() if match else ""


def parse_acceptance_certification_markdown(value: str) -> dict[str, Any]:
    """Strictly parse the Markdown-only accepting-Fusion audit protocol."""

    text = value.strip()
    errors: list[str] = []
    header = "# Fusion Acceptance Certification"
    footer = "# End Fusion Acceptance Certification"
    if not text.startswith(header):
        errors.append("missing acceptance certification header")
    if not text.endswith(footer):
        errors.append("missing acceptance certification footer")
    matches = re.findall(r"(?im)^\s*verdict:\s*(CERTIFIED|REJECTED)\s*$", text)
    if len(matches) != 1:
        errors.append(f"expected one verdict line, found {len(matches)}")
    headings = (
        "## Atomic Checks",
        "## First Invalid Step",
        "## Missing Obligation",
        "## Counterexample or Failure Witness",
        "## Certification Summary",
        footer,
    )
    for heading in headings:
        if text.count(heading) != 1:
            errors.append(f"expected one {heading}")
    sections: dict[str, str] = {}
    for heading, next_heading in zip(headings, headings[1:]):
        section = _markdown_section(text, heading, next_heading)
        sections[heading] = section
        if not section:
            errors.append(f"empty {heading}")
    verdict = matches[0] if len(matches) == 1 else None
    first_invalid = sections.get("## First Invalid Step", "")
    missing = sections.get("## Missing Obligation", "")
    witness = sections.get("## Counterexample or Failure Witness", "")
    if verdict == "CERTIFIED" and any(
        item.strip().upper() != "NONE" for item in (first_invalid, missing, witness)
    ):
        errors.append("CERTIFIED requires NONE in all three defect fields")
    if verdict == "REJECTED" and first_invalid.strip().upper() == "NONE":
        errors.append("REJECTED requires a first invalid step")
    return {
        "valid": not errors,
        "errors": errors,
        "verdict": verdict,
        "markdown": text,
        "sha256": sha256_text(text),
        "sections": sections,
    }


def _validate_task_inputs(task: dict[str, Any]) -> tuple[str, str, str, str]:
    problem = str(task.get("problem") or "").strip()
    proof = str(task.get("proof") or "").strip()
    task_id = str(task.get("task_id") or "")
    proof_hash = str(task.get("proof_sha256") or sha256_text(proof))
    if not problem or not proof or not task_id:
        raise ValueError("Fusion task is missing problem, proof, or task_id")
    if sha256_text(proof) != proof_hash:
        raise ValueError("Fusion task proof hash drift")
    return problem, proof, task_id, proof_hash


def _acceptance_user_prompt(
    *, problem: str, proof: str, fusion_record: str, pass_name: str
) -> str:
    return f"""Certification pass: {pass_name}

## Problem
{problem}

## Submitted proof
{proof}

## Untrusted accepting Fusion record
{fusion_record}

Audit the proof and accepting decision independently. Do not use a reference solution, hidden score, prior proof, or replacement proof."""


def _acceptance_audit_call(
    *,
    caller: MarkdownCaller,
    destination: Path,
    problem: str,
    proof: str,
    fusion_record: str,
    pass_name: str,
    qwen_endpoint: str,
    seed_key: str,
    model_timeout_sec: int,
) -> dict[str, Any]:
    return caller(
        endpoint=qwen_endpoint,
        model=QWEN_MODEL,
        system_prompt=ACCEPTANCE_CERTIFIER_SYSTEM_PROMPT,
        user_prompt=_acceptance_user_prompt(
            problem=problem,
            proof=proof,
            fusion_record=fusion_record,
            pass_name=pass_name,
        ),
        output_dir=destination,
        stage_name="audit_fusion_acceptance",
        temperature=0.2,
        seed_key=seed_key,
        reasoning_effort=None,
        parser=parse_acceptance_certification_markdown,
        model_timeout_sec=model_timeout_sec,
    )


def _fusion_reconsideration_user_prompt(
    *, task: dict[str, Any], prior_fusion: str, rejection: str
) -> str:
    base = stage.fusion.fusion_user_prompt(
        problem=str(task["problem"]),
        proof=str(task["proof"]),
        reviewer_1=str(task["reviewer_1"]),
        reviewer_2=str(task["reviewer_2"]),
        reviewer_3=str(task["reviewer_3"]),
    )
    return f"""{base}

## PRIOR UNTRUSTED FUSION DECISION
{prior_fusion}

## INDEPENDENT REJECTION OF THAT DECISION
{rejection}

Re-adjudicate from the complete original packet. Return a fresh Fusion record in the exact original protocol. Do not merely paraphrase the rejection."""


def _fusion_reconsideration_call(
    *,
    caller: MarkdownCaller,
    destination: Path,
    task: dict[str, Any],
    prior_fusion: str,
    rejection: str,
    gemma_endpoint: str,
    seed_key: str,
    model_timeout_sec: int,
) -> dict[str, Any]:
    return caller(
        endpoint=gemma_endpoint,
        model=GEMMA_MODEL,
        system_prompt=stage.fusion.SYSTEM_PROMPT + FUSION_RECONSIDERATION_SUFFIX,
        user_prompt=_fusion_reconsideration_user_prompt(
            task=task,
            prior_fusion=prior_fusion,
            rejection=rejection,
        ),
        output_dir=destination,
        stage_name="reconsider_fusion",
        temperature=0.4,
        seed_key=seed_key,
        reasoning_effort="max",
        parser=lambda text: stage.fusion.parse_task_output(text, task),
        model_timeout_sec=model_timeout_sec,
    )


def _audit_call(
    *,
    caller: MarkdownCaller,
    destination: Path,
    problem: str,
    proof: str,
    defect_packet: str,
    repair_brief: str,
    pass_name: str,
    qwen_endpoint: str,
    seed_key: str,
    model_timeout_sec: int,
    exact_evidence_report: str | None = None,
) -> dict[str, Any]:
    user_prompt = brief_stage._certifier_user_prompt(
        problem=problem,
        proof=proof,
        defect_packet=defect_packet,
        repair_brief=repair_brief,
        pass_name=pass_name,
    )
    if exact_evidence_report:
        user_prompt += f"""

## Independently Verified Optional Exact Evidence

{exact_evidence_report}

Use this evidence only for the exact finite/algebraic implication it reports. A
negative search result is not proof outside an exhaustively encoded finite domain.
"""
    return caller(
        endpoint=qwen_endpoint,
        model=QWEN_MODEL,
        system_prompt=brief_stage.CERTIFIER_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        output_dir=destination,
        stage_name="audit_repair_brief",
        temperature=0.2,
        seed_key=seed_key,
        reasoning_effort=None,
        parser=brief_stage.parse_certification_markdown,
        model_timeout_sec=model_timeout_sec,
    )


def _rewrite_call(
    *,
    caller: MarkdownCaller,
    destination: Path,
    problem: str,
    proof: str,
    defect_packet: str,
    rejected_brief: str,
    rejection: str,
    gemma_endpoint: str,
    seed_key: str,
    model_timeout_sec: int,
) -> dict[str, Any]:
    return caller(
        endpoint=gemma_endpoint,
        model=GEMMA_MODEL,
        system_prompt=brief_stage.REWRITER_SYSTEM_PROMPT,
        user_prompt=brief_stage._rewriter_user_prompt(
            problem=problem,
            proof=proof,
            defect_packet=defect_packet,
            rejected_brief=rejected_brief,
            rejection=rejection,
        ),
        output_dir=destination,
        stage_name="rewrite_repair_brief",
        temperature=0.4,
        seed_key=seed_key,
        reasoning_effort="max",
        parser=brief_stage.parse_rewriter_markdown,
        model_timeout_sec=model_timeout_sec,
    )


def repair_brief_disposition(record: dict[str, Any]) -> str:
    """Separate completed audit processing from mathematical certification.

    Only a fully recorded model rejection may continue; transport, parser and
    provenance failures are never converted into advisory mathematical results.
    Legacy certified records remain valid without the newer policy fields.
    """
    if record.get("state") != "completed":
        raise ValueError("repair-brief processing did not complete")
    history = record.get("history") or []
    if not history or history[-1].get("kind") != "audit":
        raise ValueError("repair-brief processing lacks its final audit")
    verdict = history[-1].get("verdict")
    if verdict == "CERTIFIED" and record.get("certified_round") is not None:
        return "CERTIFIED"
    if (verdict == "REJECTED" and record.get("certified_round") is None
            and record.get("synthesis_policy") == UNCERTIFIED_SYNTHESIS_POLICY
            and record.get("certification") == "REJECTED"
            and record.get("rewrite_count") == MAX_REWRITE_ROUNDS
            and record.get("audit_count") == MAX_REWRITE_ROUNDS + 1):
        return "REJECTED"
    raise ValueError("repair-brief terminal certification/disposition changed")


def _write_effective_repair_result(
    *, destination: Path, source_result: dict[str, Any],
    current_final: str, record: dict[str, Any],
) -> dict[str, Any]:
    repair_brief_disposition(record)
    source_final = str(source_result.get("final") or "").strip()
    assert_only_resolver_brief_changed(source_final, current_final)
    effective_parsed = stage.resolver.parse_fusion(current_final)
    if not effective_parsed.get("valid") or effective_parsed.get("outcome") != "REPAIR_NEEDED":
        raise ValueError("effective Fusion is not valid REPAIR_NEEDED")
    effective_result = copy.deepcopy(source_result)
    effective_result["final"] = current_final
    effective_result["final_sha256"] = sha256_text(current_final)
    effective_result["parsed"] = effective_parsed
    effective_result["repair_brief_audit_rewrite"] = record
    effective_path = destination / "effective_fusion_result.json"
    write_json(destination / "result.json", record)
    write_json(effective_path, _public_result(effective_result))
    (destination / "fusion.effective.txt").write_text(current_final + "\n", encoding="utf-8")
    (destination / "repair_brief.effective.txt").write_text(
        brief_stage.extract_resolver_brief(current_final) + "\n", encoding="utf-8"
    )
    effective_result["_v290_effective_result_path"] = str(effective_path.resolve())
    return effective_result


def reuse_rejected_brief(
    *, source_gate: Path, source_result: dict[str, Any], task: dict[str, Any],
    source_case_dir: Path, destination: Path,
) -> dict[str, Any]:
    """Reuse completed rejected audits in a separate output, with no model calls."""
    source_gate = _require_child(source_case_dir, source_gate, "source rejected gate")
    if destination.exists():
        raise FileExistsError(destination)
    record = read_object(source_gate)
    if record.get("state") != "failed_closed" or record.get("certified_round") is not None:
        raise ValueError("source is not a stopped rejected repair-brief gate")
    current_final = str(source_result.get("final") or "").strip()
    for row in record.get("history") or []:
        if row.get("kind") == "rewrite":
            producer = row.get("producer") or {}
            final_path = _require_child(
                source_case_dir, Path(str(producer.get("final_path") or "")), "saved rewrite"
            )
            parsed = brief_stage.parse_rewriter_markdown(final_path.read_text().strip())
            if not parsed.get("valid"):
                raise ValueError("saved rewrite is not valid Markdown")
            current_final = brief_stage.replace_resolver_brief(current_final, parsed["repair_brief"])
    record.update(
        state="completed", certification="REJECTED",
        synthesis_policy=UNCERTIFIED_SYNTHESIS_POLICY,
        resumed_from_rejected_gate={"path": str(source_gate), "file_sha256": file_sha256(source_gate)},
    )
    verify_gate_producer_history(
        record, allowed_root=source_case_dir, source_fusion=str(source_result["final"]),
        effective_fusion=current_final, task=task,
    )
    return _write_effective_repair_result(
        destination=destination, source_result=source_result,
        current_final=current_final, record=record,
    )


def audit_repair_and_reaudit(
    *,
    lane: Path,
    task: dict[str, Any],
    source_result: dict[str, Any],
    qwen_endpoint: str,
    gemma_endpoint: str,
    cycle_key: str,
    model_timeout_sec: int = DEFAULT_MODEL_TIMEOUT_SEC,
    caller: MarkdownCaller = default_markdown_call,
    max_rewrite_rounds: int = MAX_REWRITE_ROUNDS,
    enable_exact_evidence: bool = False,
) -> dict[str, Any]:
    """Audit/repair a brief; final rejection is advisory, not a synthesis veto."""

    parsed = source_result.get("parsed")
    source_final = str(source_result.get("final") or "").strip()
    if not isinstance(parsed, dict) or not parsed.get("valid"):
        raise ValueError("source Fusion result is not valid")
    outcome = str(parsed.get("outcome") or "")
    if outcome != "REPAIR_NEEDED":
        return source_result
    if max_rewrite_rounds < 1:
        raise ValueError("max_rewrite_rounds must be positive")

    destination = lane / "fusion_repair_brief_audit_rewrite"
    destination.mkdir(parents=True, exist_ok=False)
    original_brief = brief_stage.extract_resolver_brief(source_final)
    defect_packet = brief_stage.canonical_defect_packet(parsed)
    (destination / "fusion.original.txt").write_text(source_final + "\n", encoding="utf-8")
    (destination / "repair_brief.original.txt").write_text(
        original_brief + "\n", encoding="utf-8"
    )
    (destination / "defect_packet.canonical.txt").write_text(
        defect_packet + "\n", encoding="utf-8"
    )

    problem, proof, task_id, proof_hash = _validate_task_inputs(task)

    def collect_exact_evidence(
        *, audit_root: Path, pass_name: str, repair_brief: str
    ) -> dict[str, Any] | None:
        if not enable_exact_evidence:
            return None
        from . import exact_evidence

        return exact_evidence.collect_optional_exact_evidence(
            destination=audit_root / "exact_evidence",
            problem=problem,
            proof=proof,
            defect_packet=defect_packet,
            repair_brief=repair_brief,
            pass_name=pass_name,
            qwen_endpoint=qwen_endpoint,
            gemma_endpoint=gemma_endpoint,
            model_timeout_sec=model_timeout_sec,
            caller=caller,
            producer_binder=_bind_markdown_call,
        )

    current_final = source_final
    current_brief = original_brief
    history: list[dict[str, Any]] = []
    audit_root = destination / "audit_00_original"
    exact = collect_exact_evidence(
        audit_root=audit_root,
        pass_name=f"{cycle_key}:original",
        repair_brief=current_brief,
    )
    audit = _audit_call(
        caller=caller,
        destination=audit_root,
        problem=problem,
        proof=proof,
        defect_packet=defect_packet,
        repair_brief=current_brief,
        pass_name=f"{cycle_key}:original",
        qwen_endpoint=qwen_endpoint,
        seed_key=f"v0290:{cycle_key}:{task_id}:{proof_hash}:audit:0",
        model_timeout_sec=model_timeout_sec,
        exact_evidence_report=(exact or {}).get("report"),
    )
    audit_binding = _bind_markdown_call(
        audit, call_root=destination / "audit_00_original", model=QWEN_MODEL
    )
    history.append(
        {
            "kind": "audit",
            "round": 0,
            "verdict": audit["parsed"]["verdict"],
            "text_sha256": audit["final_sha256"],
            "repair_brief_sha256": sha256_text(current_brief),
            "producer": audit_binding,
            "exact_evidence": (exact or {}).get("binding"),
            "exact_evidence_report_sha256": (
                sha256_text(str(exact["report"]))
                if exact is not None and exact.get("report") is not None
                else None
            ),
        }
    )

    certified_round: int | None = 0 if audit["parsed"]["verdict"] == "CERTIFIED" else None
    for repair_round in range(1, max_rewrite_rounds + 1):
        if certified_round is not None:
            break
        rewrite = _rewrite_call(
            caller=caller,
            destination=destination / f"rewrite_{repair_round:02d}",
            problem=problem,
            proof=proof,
            defect_packet=defect_packet,
            rejected_brief=current_brief,
            rejection=str(audit["text"]),
            gemma_endpoint=gemma_endpoint,
            seed_key=(
                f"v0290:{cycle_key}:{task_id}:{proof_hash}:rewrite:{repair_round}"
            ),
            model_timeout_sec=model_timeout_sec,
        )
        rewrite_binding = _bind_markdown_call(
            rewrite,
            call_root=destination / f"rewrite_{repair_round:02d}",
            model=GEMMA_MODEL,
        )
        new_brief = str(rewrite["parsed"]["repair_brief"])
        current_final = brief_stage.replace_resolver_brief(current_final, new_brief)
        current_brief = brief_stage.extract_resolver_brief(current_final)
        history.append(
            {
                "kind": "rewrite",
                "round": repair_round,
                "text_sha256": rewrite["final_sha256"],
                "repair_brief_sha256": sha256_text(current_brief),
                "producer": rewrite_binding,
            }
        )
        audit_root = destination / f"audit_{repair_round:02d}_rewrite"
        exact = collect_exact_evidence(
            audit_root=audit_root,
            pass_name=f"{cycle_key}:rewrite:{repair_round}",
            repair_brief=current_brief,
        )
        audit = _audit_call(
            caller=caller,
            destination=audit_root,
            problem=problem,
            proof=proof,
            defect_packet=defect_packet,
            repair_brief=current_brief,
            pass_name=f"{cycle_key}:rewrite:{repair_round}",
            qwen_endpoint=qwen_endpoint,
            seed_key=(f"v0290:{cycle_key}:{task_id}:{proof_hash}:audit:{repair_round}"),
            model_timeout_sec=model_timeout_sec,
            exact_evidence_report=(exact or {}).get("report"),
        )
        audit_binding = _bind_markdown_call(
            audit,
            call_root=destination / f"audit_{repair_round:02d}_rewrite",
            model=QWEN_MODEL,
        )
        verdict = str(audit["parsed"]["verdict"])
        history.append(
            {
                "kind": "audit",
                "round": repair_round,
                "verdict": verdict,
                "text_sha256": audit["final_sha256"],
                "repair_brief_sha256": sha256_text(current_brief),
                "producer": audit_binding,
                "exact_evidence": (exact or {}).get("binding"),
                "exact_evidence_report_sha256": (
                    sha256_text(str(exact["report"]))
                    if exact is not None and exact.get("report") is not None
                    else None
                ),
            }
        )
        if verdict == "CERTIFIED":
            certified_round = repair_round

    record = {
        "schema": "cognitive-well-v0290-repair-brief-gate-v1",
        "state": "completed",
        "certification": "CERTIFIED" if certified_round is not None else "REJECTED",
        "synthesis_policy": UNCERTIFIED_SYNTHESIS_POLICY,
        "harness_version": HARNESS_VERSION,
        "cycle_key": cycle_key,
        "case_id": task_id.split(".fusion.")[0],
        "task_id": task_id,
        "source_fusion_sha256": sha256_text(source_final),
        "source_repair_brief_sha256": sha256_text(original_brief),
        "effective_fusion_sha256": sha256_text(current_final),
        "effective_repair_brief_sha256": sha256_text(current_brief),
        "certified_round": certified_round,
        "rewrite_count": sum(row["kind"] == "rewrite" for row in history),
        "audit_count": sum(row["kind"] == "audit" for row in history),
        "history": history,
        "model_output_format": "Markdown",
        "model_timeout_sec": model_timeout_sec,
        "token_caps": list(TOKEN_CAPS),
        "qwen_token_policy": token_policy_for(QWEN_MODEL),
        "resolver_packet_mutation": "replace exactly resolver_brief only",
        "exact_evidence_enabled": enable_exact_evidence,
        "problem_sha256": sha256_text(problem),
        "proof_sha256": proof_hash,
        "reviewer_input_sha256": {
            name: sha256_text(str(task.get(name) or "").strip())
            for name in ("reviewer_1", "reviewer_2", "reviewer_3")
        },
        "defect_packet_sha256": sha256_text(defect_packet),
    }
    return _write_effective_repair_result(
        destination=destination, source_result=source_result,
        current_final=current_final, record=record,
    )


def audit_fusion_before_resolver(
    *,
    lane: Path,
    task: dict[str, Any],
    source_result: dict[str, Any],
    qwen_endpoint: str,
    gemma_endpoint: str,
    cycle_key: str,
    model_timeout_sec: int = DEFAULT_MODEL_TIMEOUT_SEC,
    caller: MarkdownCaller = default_markdown_call,
    max_rewrite_rounds: int = MAX_REWRITE_ROUNDS,
    max_acceptance_reconsiderations: int = MAX_ACCEPTANCE_RECONSIDERATIONS,
    enable_exact_evidence: bool = False,
) -> dict[str, Any]:
    """Certify every Fusion decision before it can reach the Resolver.

    A REPAIR_NEEDED record enters the exact v0266/v0268/v0269 brief boundary.
    An accepting record first receives a proof-level Qwen audit. A rejected
    acceptance returns to Gemma Fusion, never directly to the Resolver.
    """

    parsed = source_result.get("parsed")
    source_final = str(source_result.get("final") or "").strip()
    if not isinstance(parsed, dict) or not parsed.get("valid"):
        raise ValueError("source Fusion result is not valid")
    outcome = str(parsed.get("outcome") or "")
    if outcome == "REPAIR_NEEDED":
        return audit_repair_and_reaudit(
            lane=lane,
            task=task,
            source_result=source_result,
            qwen_endpoint=qwen_endpoint,
            gemma_endpoint=gemma_endpoint,
            cycle_key=cycle_key,
            model_timeout_sec=model_timeout_sec,
            caller=caller,
            max_rewrite_rounds=max_rewrite_rounds,
            enable_exact_evidence=enable_exact_evidence,
        )
    accepting_outcomes = {
        "ACCEPT_AS_WRITTEN",
        "ACCEPT_WITH_ROUTINE_COMPLETION",
    }
    if outcome not in accepting_outcomes:
        raise FusionAcceptanceCertificationError(
            f"{cycle_key} Fusion outcome {outcome or 'UNKNOWN'} cannot enter Resolver"
        )
    if max_acceptance_reconsiderations < 1:
        raise ValueError("max_acceptance_reconsiderations must be positive")

    problem, proof, task_id, proof_hash = _validate_task_inputs(task)
    destination = lane / "fusion_acceptance_audit"
    destination.mkdir(parents=True, exist_ok=False)
    (destination / "fusion.original.txt").write_text(
        source_final + "\n", encoding="utf-8"
    )

    current_result = copy.deepcopy(source_result)
    current_final = source_final
    history: list[dict[str, Any]] = []
    certified_round: int | None = None
    final_outcome = outcome
    nested_repair_gate: dict[str, Any] | None = None
    failure: str | None = None

    try:
        for audit_round in range(max_acceptance_reconsiderations + 1):
            audit = _acceptance_audit_call(
                caller=caller,
                destination=destination / f"audit_{audit_round:02d}",
                problem=problem,
                proof=proof,
                fusion_record=current_final,
                pass_name=f"{cycle_key}:acceptance:{audit_round}",
                qwen_endpoint=qwen_endpoint,
                seed_key=(
                    f"v0290:{cycle_key}:{task_id}:{proof_hash}:"
                    f"acceptance_audit:{audit_round}"
                ),
                model_timeout_sec=model_timeout_sec,
            )
            audit_binding = _bind_markdown_call(
                audit,
                call_root=destination / f"audit_{audit_round:02d}",
                model=QWEN_MODEL,
            )
            verdict = str(audit["parsed"]["verdict"])
            history.append(
                {
                    "kind": "acceptance_audit",
                    "round": audit_round,
                    "verdict": verdict,
                    "fusion_sha256": sha256_text(current_final),
                    "text_sha256": audit["final_sha256"],
                    "producer": audit_binding,
                }
            )
            if verdict == "CERTIFIED":
                certified_round = audit_round
                break
            if audit_round >= max_acceptance_reconsiderations:
                break

            reconsideration = _fusion_reconsideration_call(
                caller=caller,
                destination=destination / f"reconsideration_{audit_round + 1:02d}",
                task=task,
                prior_fusion=current_final,
                rejection=str(audit["text"]),
                gemma_endpoint=gemma_endpoint,
                seed_key=(
                    f"v0290:{cycle_key}:{task_id}:{proof_hash}:"
                    f"fusion_reconsideration:{audit_round + 1}"
                ),
                model_timeout_sec=model_timeout_sec,
            )
            reconsideration_binding = _bind_markdown_call(
                reconsideration,
                call_root=destination / f"reconsideration_{audit_round + 1:02d}",
                model=GEMMA_MODEL,
            )
            current_final = str(reconsideration["text"]).strip()
            current_result = copy.deepcopy(source_result)
            current_result["final"] = current_final
            current_result["final_sha256"] = sha256_text(current_final)
            current_result["parsed"] = reconsideration["parsed"]
            final_outcome = str(reconsideration["parsed"].get("outcome") or "")
            history.append(
                {
                    "kind": "fusion_reconsideration",
                    "round": audit_round + 1,
                    "outcome": final_outcome,
                    "text_sha256": reconsideration["final_sha256"],
                    "producer": reconsideration_binding,
                }
            )
            if final_outcome == "REPAIR_NEEDED":
                repaired = audit_repair_and_reaudit(
                    lane=lane,
                    task=task,
                    source_result=current_result,
                    qwen_endpoint=qwen_endpoint,
                    gemma_endpoint=gemma_endpoint,
                    cycle_key=cycle_key,
                    model_timeout_sec=model_timeout_sec,
                    caller=caller,
                    max_rewrite_rounds=max_rewrite_rounds,
                    enable_exact_evidence=enable_exact_evidence,
                )
                current_result = repaired
                current_final = str(repaired["final"]).strip()
                final_outcome = "REPAIR_NEEDED"
                nested_repair_gate = boundary_record_from_effective(repaired)
                break
            if final_outcome not in accepting_outcomes:
                raise FusionAcceptanceCertificationError(
                    f"reconsidered Fusion outcome {final_outcome or 'UNKNOWN'} "
                    "cannot enter Resolver"
                )
    except Exception as error:
        failure = f"{type(error).__name__}: {error}"

    completed = certified_round is not None or nested_repair_gate is not None
    record = {
        "schema": "cognitive-well-v0290-fusion-acceptance-gate-v1",
        "state": "completed" if completed else "failed_closed",
        "harness_version": HARNESS_VERSION,
        "cycle_key": cycle_key,
        "case_id": task_id.split(".fusion.")[0],
        "task_id": task_id,
        "problem_sha256": sha256_text(problem),
        "proof_sha256": proof_hash,
        "reviewer_input_sha256": {
            name: sha256_text(str(task.get(name) or "").strip())
            for name in ("reviewer_1", "reviewer_2", "reviewer_3")
        },
        "source_outcome": outcome,
        "source_fusion_sha256": sha256_text(source_final),
        "effective_outcome": final_outcome,
        "effective_fusion_sha256": sha256_text(current_final),
        "certified_acceptance_round": certified_round,
        "reconsideration_count": sum(
            row["kind"] == "fusion_reconsideration" for row in history
        ),
        "history": history,
        "repair_brief_gate": nested_repair_gate,
        "model_output_format": "Markdown",
        "model_timeout_sec": model_timeout_sec,
        "token_caps": list(TOKEN_CAPS),
        "qwen_token_policy": token_policy_for(QWEN_MODEL),
        "failure": failure,
    }
    write_json(destination / "result.json", record)
    if not completed:
        raise FusionAcceptanceCertificationError(
            failure
            or f"{cycle_key} {record['case_id']} accepting Fusion remained rejected"
        )

    current_result = copy.deepcopy(current_result)
    current_result["fusion_acceptance_audit"] = record
    effective_path = destination / "effective_fusion_result.json"
    write_json(effective_path, _public_result(current_result))
    (destination / "fusion.effective.txt").write_text(
        current_final + "\n", encoding="utf-8"
    )
    current_result["_v290_effective_result_path"] = str(effective_path.resolve())
    return current_result


def boundary_record_from_effective(result: dict[str, Any]) -> dict[str, Any] | None:
    record = result.get("repair_brief_audit_rewrite")
    return dict(record) if isinstance(record, dict) else None


__all__ = [
    "ACCEPTANCE_CERTIFIER_SYSTEM_PROMPT",
    "DEFAULT_MODEL_TIMEOUT_SEC",
    "FusionAcceptanceCertificationError",
    "MAX_ACCEPTANCE_RECONSIDERATIONS",
    "MAX_REWRITE_ROUNDS",
    "RepairBriefCertificationError",
    "TOKEN_CAPS",
    "assert_only_resolver_brief_changed",
    "audit_fusion_before_resolver",
    "audit_repair_and_reaudit",
    "boundary_record_from_effective",
    "default_markdown_call",
    "parse_acceptance_certification_markdown",
    "sha256_text",
]
