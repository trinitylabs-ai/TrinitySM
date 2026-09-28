from __future__ import annotations

import hashlib
import json
import multiprocessing
import os
import queue as queue_module
import resource
import signal
import shutil
import threading
from pathlib import Path
from typing import Any, Mapping

import sympy as sp

from cognitive_well_harness_v0_3_274_generic_compression_portfolio_bridge_20260905 import (
    exact_tools,
)
from cognitive_well_harness_v0_3_275_generic_audited_ledger_compression_20260905 import (
    transformation_validation,
)

from . import gaussian_backend, laurent_elimination
from .symbol_safety import parse_polynomial


class LaurentInapplicableError(ValueError):
    """A structural preview proved that no valid smaller Laurent route exists."""


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json_nodes(value: Any) -> int:
    if isinstance(value, Mapping):
        return 1 + sum(_json_nodes(key) + _json_nodes(item) for key, item in value.items())
    if isinstance(value, list):
        return 1 + sum(_json_nodes(item) for item in value)
    return 1


def _derived_profile(
    *, transform_payload: Mapping[str, Any], eliminated: Mapping[str, Any]
) -> dict[str, Any]:
    return {
        "solver_symbol_count": eliminated["profile"]["symbol_count"],
        "solver_generator_count": len(eliminated["generators"]),
        "maximum_total_degree": eliminated["profile"]["maximum_total_degree"],
        "total_monomial_count": eliminated["profile"]["total_monomial_count"],
        "argument_ast_nodes": _json_nodes(
            {
                "generators": transform_payload["generators"],
                "target": transform_payload["target"],
            }
        ),
        "canonical_argument_hash": transform_payload["transform_sha256"],
    }


def _mathematical_appendix(
    *,
    transformed: Mapping[str, Any],
    guard_ledger: Mapping[str, Any],
    lift: Mapping[str, Any],
    identity: Mapping[str, Any] | None,
) -> str:
    """Render exact machine-derived mathematics for the synthesis models."""

    selected = transformed["selected"]
    eliminated = selected["elimination"]
    lines = [
        "# Deterministic Laurent Certificate Appendix",
        "",
        "## Simultaneous Unit-Circle Substitutions",
        "",
    ]
    for circle, odd_index, unit in zip(
        selected["circles"],
        selected["orientation"],
        selected["laurent_symbols"],
        strict=True,
    ):
        odd = circle["coordinates"][odd_index]
        even = circle["coordinates"][1 - odd_index]
        lines.extend(
            [
                f"- `{circle['label']}`: `{odd} = ({unit} - {unit}^(-1))/(2*i)`, "
                f"`{even} = ({unit} + {unit}^(-1))/2`.",
                f"  Inverse on the source circle: `{unit} = {even} + i*{odd}` and "
                f"`{unit}^(-1) = {even} - i*{odd}`.",
            ]
        )
    lines.extend(["", "## Typed Nonzero Guards", ""])
    if guard_ledger["eligible_records"]:
        for row in guard_ledger["eligible_records"]:
            lines.append(
                f"- `{row['label']}`: `{row['expression']} != 0`; provenance: "
                + ", ".join(f"`{source}`" for source in row["sources"])
                + "."
            )
    else:
        lines.append("- No source guard was eligible; only the algebraic unit guards are used.")
    lines.extend(["", "## Deterministic Post-Laurent Reduction", ""])
    linear = lift["linear_elimination"]
    if linear["performed"]:
        lines.append(
            f"- Eliminate `{linear['variable']}` using pivot `{linear['pivot_label']}`."
        )
        for row in linear["pivot_factor_guard_coverage"]:
            lines.append(
                f"- Pivot factor `{row['factor_expression']}` is nonzero by "
                + ", ".join(f"`{label}`" for label in row["guard_labels"])
                + "."
            )
        for row in linear["compatibility_identities"]:
            lines.append(
                f"- `{row['label']}` is exact: pivot coefficient times "
                f"`{row['source_linear_generator']}` minus its coefficient times "
                "the pivot equals the compatibility generator."
            )
    else:
        lines.append(
            "- No guarded linear elimination is used; the simultaneous Laurent "
            "substitution and exact denominator clearing are already strictly smaller."
        )
    lines.extend(["", "## Derived Exact Ideal-Membership Problem", ""])
    lines.append(
        "- Symbols: " + ", ".join(f"`{symbol}`" for symbol in eliminated["symbols"]) + "."
    )
    for label, expression in eliminated["generators"]:
        lines.append(f"- `{label} = {str(expression)}`.")
    lines.append(f"- Derived target: `{str(eliminated['target'])}`.")
    if linear["performed"]:
        lines.append(
            f"- Exact candidate-target lift: `({linear['pivot_coefficient_expression']})^"
            f"{linear['target_degree']} * ({linear['transformed_candidate_target_expression']}) "
            f"- ({linear['derived_target_expression']}) = "
            f"({linear['target_quotient_expression']}) * "
            f"({linear['pivot_generator_expression']})`."
        )
    else:
        lines.append(
            f"- Exact candidate-target lift: `({linear['transformed_candidate_target_expression']}) "
            f"= ({linear['derived_target_expression']})`."
        )
    lines.extend(["", "## Exported Membership Identity", ""])
    if identity is None:
        lines.append("- No replayable membership identity was exported; promotion is forbidden.")
    else:
        lines.append(
            f"- Exact identity over `QQ(i)`: the derived target equals the sum "
            f"of {len(identity['generator_labels'])} generator multiples."
        )
        for label in identity["generator_labels"]:
            lines.append(
                f"- Multiplier for `{label}`: `{identity['source_multipliers'][label]}`."
            )
    lines.extend(
        [
            "",
            "Every displayed Laurent/elimination expression is generated from and "
            "re-expanded against the hash-bound candidate request. The separate exact "
            "transformation certificate binds the accepted source request to that "
            "candidate. No model-authored certificate text is used.",
        ]
    )
    return "\n".join(lines) + "\n"


def _eligible_guards(
    *,
    source_arguments: Mapping[str, Any],
    candidate_arguments: Mapping[str, Any],
    guard_program: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Derive guards only from typed provenance and classify their scope."""

    derived = transformation_validation.derive_guards(
        guard_program, source_arguments
    )
    source = exact_tools.validate_ideal_arguments(source_arguments)
    candidate = exact_tools.validate_ideal_arguments(candidate_arguments)
    candidate_names = set(candidate["symbols"])
    eligible: dict[str, Any] = {}
    excluded: list[dict[str, Any]] = []
    for row, expression in zip(
        derived["records"], derived["expressions"], strict=True
    ):
        names = {str(symbol) for symbol in expression.free_symbols}
        if names <= candidate_names:
            eligible[str(row["label"])] = expression
        else:
            excluded.append(
                {
                    **row,
                    "reason": "guard refers to a symbol absent from the candidate",
                    "absent_symbols": sorted(names - candidate_names),
                }
            )
    ledger = {
        "schema": "cognitive-well-v0282-typed-guard-binding-v1",
        "source_symbols": list(source["symbols"]),
        "candidate_symbols": list(candidate["symbols"]),
        "guard_program_sha256": exact_tools.stable_hash(guard_program),
        "derived_guard_count": len(derived["records"]),
        "eligible_guard_count": len(eligible),
        "eligible_records": [
            row
            for row in derived["records"]
            if row["label"] in eligible
        ],
        "excluded_records": excluded,
        "typed_division_count": len(guard_program["provenance_divisions"]),
        "source_nonzero_count": len(guard_program["source_nonzero"]),
    }
    return eligible, ledger


def preview_only(
    *,
    source_arguments: Mapping[str, Any],
    candidate_arguments: Mapping[str, Any],
    guard_program: Mapping[str, Any],
    output_dir: Path,
) -> dict[str, Any]:
    """Build a structural Laurent preview with no source-equivalence claim.

    A preview is useful only for deterministic queue ordering.  It is deliberately
    missing a source-to-candidate validation certificate and is never promotable.
    """

    source_sha = exact_tools.stable_hash(source_arguments)
    candidate_sha = exact_tools.stable_hash(candidate_arguments)
    guard_sha = exact_tools.stable_hash(guard_program)
    destination = output_dir.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    candidate = exact_tools.validate_ideal_arguments(candidate_arguments)
    guards, guard_ledger = _eligible_guards(
        source_arguments=source_arguments,
        candidate_arguments=candidate_arguments,
        guard_program=guard_program,
    )
    _write_json(destination / "typed_guard_binding.json", guard_ledger)
    transformed = laurent_elimination.transform(candidate, nonzero_guards=guards)
    transform_payload = laurent_elimination.json_transform(transformed)
    _write_json(destination / "laurent_transform.json", transform_payload)
    selected = transformed["selected"]
    eliminated = selected["elimination"]
    artifacts = {
        name: _sha256_file(destination / name)
        for name in ("typed_guard_binding.json", "laurent_transform.json")
    }
    persisted = {
        "schema": "cognitive-well-v0282-generic-laurent-structural-preview-v1",
        "state": "structural_preview_unvalidated",
        "cpu_only": True,
        "model_calls": 0,
        "problem_specific_rules": 0,
        "preloaded_certificate_used": False,
        "source_equivalence_status": "unchecked",
        "promotable": False,
        "source_arguments_sha256": source_sha,
        "candidate_arguments_sha256": candidate_sha,
        "guard_program_sha256": guard_sha,
        "exact_transformation_validation_sha256": None,
        "transform_sha256": transform_payload["transform_sha256"],
        "detected_circle_count": len(transformed["detected_circles"]),
        "detected_circle_candidate_count": len(
            transformed["detected_circle_candidates"]
        ),
        "circle_set_count": transformed["circle_set_count"],
        "orientation_attempted_count": transformed["orientation_attempted_count"],
        "orientation_success_count": transformed["orientation_success_count"],
        "selected_circle_set_index": selected["circle_set_index"],
        "selected_orientation": list(selected["orientation"]),
        "derived_profile": _derived_profile(
            transform_payload=transform_payload, eliminated=eliminated
        ),
        "artifact_sha256": artifacts,
    }
    _write_json(destination / "preview.json", persisted)
    return {
        **persisted,
        "preview_file_sha256": _sha256_file(destination / "preview.json"),
    }


def preprocess_only(
    *,
    source_arguments: Mapping[str, Any],
    candidate_arguments: Mapping[str, Any],
    guard_program: Mapping[str, Any],
    exact_transformation_validation: Mapping[str, Any],
    output_dir: Path,
    expected_transform_sha256: str | None = None,
    expected_derived_profile: Mapping[str, Any] | None = None,
    expected_structural_preview_sha256: str | None = None,
) -> dict[str, Any]:
    """Prepare and certify a Laurent descendant without executing the target."""

    if exact_transformation_validation.get("decision") != "ACCEPT":
        raise ValueError("Laurent preprocessing requires exact transformation ACCEPT")
    source_sha = exact_tools.stable_hash(source_arguments)
    candidate_sha = exact_tools.stable_hash(candidate_arguments)
    guard_sha = exact_tools.stable_hash(guard_program)
    validation_sha = exact_tools.stable_hash(exact_transformation_validation)
    for field, value in {
        "source_arguments_sha256": source_sha,
        "candidate_arguments_sha256": candidate_sha,
        "guard_program_sha256": guard_sha,
    }.items():
        if exact_transformation_validation.get(field) != value:
            raise ValueError(f"exact transformation validation lost {field}")
    destination = output_dir.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    candidate = exact_tools.validate_ideal_arguments(candidate_arguments)
    guards, guard_ledger = _eligible_guards(
        source_arguments=source_arguments,
        candidate_arguments=candidate_arguments,
        guard_program=guard_program,
    )
    _write_json(destination / "typed_guard_binding.json", guard_ledger)
    transformed = laurent_elimination.transform(candidate, nonzero_guards=guards)
    transform_payload = laurent_elimination.json_transform(transformed)
    if (
        expected_transform_sha256 is not None
        and transform_payload["transform_sha256"] != expected_transform_sha256
    ):
        raise ValueError("certified Laurent transform does not match structural preview")
    _write_json(destination / "laurent_transform.json", transform_payload)
    lift = laurent_elimination.full_lift_certificate(
        validated=candidate,
        transformed=transformed,
        source_arguments_sha256=source_sha,
        guard_program_sha256=guard_sha,
        exact_transformation_validation_sha256=validation_sha,
        transform_sha256=transform_payload["transform_sha256"],
    )
    _write_json(destination / "full_source_lift_certificate.json", lift)
    selected = transformed["selected"]
    eliminated = selected["elimination"]
    derived_profile = _derived_profile(
        transform_payload=transform_payload, eliminated=eliminated
    )
    if (
        expected_derived_profile is not None
        and dict(expected_derived_profile) != derived_profile
    ):
        raise ValueError("certified Laurent profile does not match structural preview")
    artifacts = {
        name: _sha256_file(destination / name)
        for name in (
            "typed_guard_binding.json",
            "laurent_transform.json",
            "full_source_lift_certificate.json",
        )
    }
    persisted = {
        "schema": "cognitive-well-v0282-generic-laurent-preprocessing-prepared-v1",
        "state": "prepared",
        "cpu_only": True,
        "model_calls": 0,
        "problem_specific_rules": 0,
        "preloaded_certificate_used": False,
        "source_arguments_sha256": source_sha,
        "candidate_arguments_sha256": candidate_sha,
        "guard_program_sha256": guard_sha,
        "exact_transformation_validation_sha256": validation_sha,
        "transform_sha256": transform_payload["transform_sha256"],
        "full_source_lift_certificate_sha256": lift["certificate_sha256"],
        "detected_circle_count": len(transformed["detected_circles"]),
        "detected_circle_candidate_count": len(
            transformed["detected_circle_candidates"]
        ),
        "circle_set_count": transformed["circle_set_count"],
        "orientation_attempted_count": transformed["orientation_attempted_count"],
        "orientation_success_count": transformed["orientation_success_count"],
        "selected_circle_set_index": selected["circle_set_index"],
        "selected_orientation": list(selected["orientation"]),
        "derived_profile": derived_profile,
        "matched_structural_preview": expected_transform_sha256 is not None,
        "expected_preview_transform_sha256": expected_transform_sha256,
        "expected_preview_derived_profile": (
            None
            if expected_derived_profile is None
            else dict(expected_derived_profile)
        ),
        "structural_preview_file_sha256": expected_structural_preview_sha256,
        "artifact_sha256": artifacts,
    }
    _write_json(destination / "prepared.json", persisted)
    return {
        **persisted,
        "prepared_file_sha256": _sha256_file(destination / "prepared.json"),
        "_runtime": {
            "transformed": transformed,
            "filtered_guards": {
                label: expression
                for label, expression in selected["transformed_guards"].items()
                if eliminated["variable"] not in expression.free_symbols
            },
        },
    }


def _bounded_worker(
    queue: Any,
    mode: str,
    kwargs: dict[str, Any],
    memory_mb: int,
) -> None:
    try:
        os.setsid()
        limit = memory_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
        function = (
            preview_only
            if mode == "preview"
            else preprocess_only
            if mode == "prepare"
            else screen_persisted_preview_target
            if mode == "screen_persisted"
            else screen_preview_target
            if mode == "screen"
            else preprocess_and_execute
        )
        function(**kwargs)
        queue.put(
            {
                "ok": True,
                "result_file": (
                    "preview.json"
                    if mode == "preview"
                    else "prepared.json"
                    if mode == "prepare"
                    else "result.json"
                ),
            }
        )
    except BaseException as error:  # child must report fail-closed, including MemoryError
        queue.put(
            {
                "ok": False,
                "error_type": type(error).__name__,
                "error": f"{type(error).__name__}: {error}",
            }
        )


def _bounded(
    *,
    mode: str,
    output_dir: Path,
    timeout_sec: int,
    memory_mb: int,
    kwargs: dict[str, Any],
) -> dict[str, Any]:
    """Run SymPy preprocessing in a bounded child and atomically promote output."""

    destination = output_dir.resolve()
    if destination.exists():
        raise FileExistsError(destination)
    partial = destination.with_name(
        f".{destination.name}.partial-{os.getpid()}"
    )
    if partial.exists():
        raise FileExistsError(partial)
    child_kwargs = {**kwargs, "output_dir": partial}
    # A fork from a ThreadPoolExecutor worker inherits the executor's shutdown
    # bookkeeping: even a successful child can then exit 1 on Python shutdown.
    # Spawn gives threaded callers a clean interpreter without changing the math.
    context = multiprocessing.get_context(
        "spawn" if threading.current_thread() is not threading.main_thread() else "fork"
    )
    queue = context.Queue()
    process = context.Process(
        target=_bounded_worker,
        args=(queue, mode, child_kwargs, memory_mb),
    )
    process.start()
    process.join(timeout_sec)
    if process.is_alive():
        group_signal_sent = False
        try:
            os.killpg(process.pid, signal.SIGTERM)
            group_signal_sent = True
        except ProcessLookupError:
            pass
        if not group_signal_sent and process.is_alive():
            process.terminate()
        process.join(5)
        if process.is_alive():
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                process.kill()
            process.join(5)
        if partial.exists():
            shutil.rmtree(partial)
        raise TimeoutError(
            f"Laurent {mode} exceeded the {timeout_sec}-second exact-work limit"
        )
    try:
        message = queue.get(timeout=5)
    except queue_module.Empty:
        message = None
    if not isinstance(message, Mapping) or message.get("ok") is not True:
        if partial.exists():
            shutil.rmtree(partial)
        detail = (
            message.get("error")
            if isinstance(message, Mapping)
            else f"child exited {process.exitcode} without a result"
        )
        if (
            mode == "preview"
            and isinstance(message, Mapping)
            and message.get("error_type") == "ValueError"
        ):
            raise LaurentInapplicableError(str(detail))
        raise RuntimeError(f"Laurent {mode} failed closed: {detail}")
    if process.exitcode != 0:
        if partial.exists():
            shutil.rmtree(partial)
        raise RuntimeError(f"Laurent {mode} child exited {process.exitcode}")
    partial.replace(destination)
    result_file = destination / str(message["result_file"])
    result = json.loads(result_file.read_text(encoding="utf-8"))
    if not isinstance(result, dict):
        raise ValueError("bounded Laurent result is not a JSON object")
    result[
        "preview_file_sha256"
        if mode == "preview"
        else "prepared_file_sha256"
        if mode == "prepare"
        else "result_file_sha256"
    ] = _sha256_file(result_file)
    return result


def bounded_preview_only(
    *,
    source_arguments: Mapping[str, Any],
    candidate_arguments: Mapping[str, Any],
    guard_program: Mapping[str, Any],
    output_dir: Path,
    timeout_sec: int,
    memory_mb: int,
) -> dict[str, Any]:
    return _bounded(
        mode="preview",
        output_dir=output_dir,
        timeout_sec=timeout_sec,
        memory_mb=memory_mb,
        kwargs={
            "source_arguments": source_arguments,
            "candidate_arguments": candidate_arguments,
            "guard_program": guard_program,
        },
    )


def bounded_preprocess_only(
    *,
    source_arguments: Mapping[str, Any],
    candidate_arguments: Mapping[str, Any],
    guard_program: Mapping[str, Any],
    exact_transformation_validation: Mapping[str, Any],
    output_dir: Path,
    timeout_sec: int,
    memory_mb: int,
    expected_transform_sha256: str | None = None,
    expected_derived_profile: Mapping[str, Any] | None = None,
    expected_structural_preview_sha256: str | None = None,
) -> dict[str, Any]:
    return _bounded(
        mode="prepare",
        output_dir=output_dir,
        timeout_sec=timeout_sec,
        memory_mb=memory_mb,
        kwargs={
            "source_arguments": source_arguments,
            "candidate_arguments": candidate_arguments,
            "guard_program": guard_program,
            "exact_transformation_validation": exact_transformation_validation,
            "expected_transform_sha256": expected_transform_sha256,
            "expected_derived_profile": expected_derived_profile,
            "expected_structural_preview_sha256": (
                expected_structural_preview_sha256
            ),
        },
    )


def _execute_transformed_target(
    *,
    transformed: Mapping[str, Any],
    singular_binary: Path,
    timeout_sec: int,
    memory_mb: int,
) -> dict[str, Any]:
    selected = transformed["selected"]
    eliminated = selected["elimination"]
    filtered_guards = {
        label: expression
        for label, expression in selected["transformed_guards"].items()
        if eliminated["variable"] is None
        or eliminated["variable"] not in expression.free_symbols
    }
    return gaussian_backend.check(
        symbols=list(eliminated["symbols"]),
        generators=list(eliminated["generators"]),
        target=eliminated["target"],
        guards=filtered_guards,
        binary=singular_binary.resolve(),
        timeout_sec=timeout_sec,
        memory_mb=memory_mb,
        radical=False,
    )


def _persist_membership_identity(
    *,
    exact_result: Mapping[str, Any],
    transform_sha256: str,
    destination: Path,
) -> tuple[bool, dict[str, Any] | None]:
    backend_proved = (
        exact_result.get("status") == "COMPLETED"
        and exact_result.get("markers", {}).get("RESULT_ORDINARY") == "PROVED"
    )
    identity = None
    backend_identity = exact_result.get("membership_certificate")
    if (
        backend_proved
        and exact_result.get("certificate_reexpanded") is True
        and isinstance(backend_identity, Mapping)
    ):
        identity_payload = {
            "schema": "cognitive-well-v0282-gaussian-membership-identity-v1",
            "transform_sha256": transform_sha256,
            "gaussian_certificate_sha256": backend_identity.get(
                "certificate_sha256"
            ),
            "coefficient_field": backend_identity.get("coefficient_field"),
            "generator_labels": list(backend_identity.get("generator_labels", [])),
            "source_multipliers": dict(
                backend_identity.get("source_multipliers", {})
            ),
            "target_expression": backend_identity.get("target_expression"),
            "exact_remainder": backend_identity.get("exact_remainder"),
            "reexpansion_zero": backend_identity.get("reexpansion_zero"),
        }
        identity = {
            **identity_payload,
            "certificate_sha256": exact_tools.stable_hash(identity_payload),
        }
        _write_json(destination / "derived_identity_certificate.json", identity)
    return backend_proved, identity


def screen_preview_target(
    *,
    source_arguments: Mapping[str, Any],
    candidate_arguments: Mapping[str, Any],
    guard_program: Mapping[str, Any],
    output_dir: Path,
    singular_binary: Path,
    timeout_sec: int,
    memory_mb: int,
    expected_transform_sha256: str,
    expected_derived_profile: Mapping[str, Any],
    expected_structural_preview_sha256: str,
) -> dict[str, Any]:
    """Screen the reduced Laurent target before any source-link certificate.

    A positive result proves membership only in the recomputed transformed ideal.
    It is explicitly nonpromotable until the separate source-to-compression and
    compression-to-Laurent lift certificates are established.
    """

    if not singular_binary.resolve().is_file():
        raise FileNotFoundError(singular_binary)
    source_sha = exact_tools.stable_hash(source_arguments)
    candidate_sha = exact_tools.stable_hash(candidate_arguments)
    guard_sha = exact_tools.stable_hash(guard_program)
    destination = output_dir.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    candidate = exact_tools.validate_ideal_arguments(candidate_arguments)
    guards, guard_ledger = _eligible_guards(
        source_arguments=source_arguments,
        candidate_arguments=candidate_arguments,
        guard_program=guard_program,
    )
    _write_json(destination / "typed_guard_binding.json", guard_ledger)
    transformed = laurent_elimination.transform(candidate, nonzero_guards=guards)
    transform_payload = laurent_elimination.json_transform(transformed)
    if transform_payload["transform_sha256"] != expected_transform_sha256:
        raise ValueError("screened Laurent transform differs from structural preview")
    _write_json(destination / "laurent_transform.json", transform_payload)
    selected = transformed["selected"]
    eliminated = selected["elimination"]
    derived_profile = _derived_profile(
        transform_payload=transform_payload, eliminated=eliminated
    )
    if dict(expected_derived_profile) != derived_profile:
        raise ValueError("screened Laurent profile differs from structural preview")
    exact_result = _execute_transformed_target(
        transformed=transformed,
        singular_binary=singular_binary,
        timeout_sec=timeout_sec,
        memory_mb=memory_mb,
    )
    _write_json(destination / "exact_result.json", exact_result)
    backend_proved, identity = _persist_membership_identity(
        exact_result=exact_result,
        transform_sha256=transform_payload["transform_sha256"],
        destination=destination,
    )
    proved = backend_proved and identity is not None
    artifact_names = [
        "typed_guard_binding.json",
        "laurent_transform.json",
        "exact_result.json",
    ]
    if identity is not None:
        artifact_names.append("derived_identity_certificate.json")
    artifacts = {
        name: _sha256_file(destination / name) for name in artifact_names
    }
    result = {
        "schema": "cognitive-well-v0282-laurent-target-screen-v1",
        "state": (
            "proved"
            if proved
            else "uncertified_backend_proof"
            if backend_proved
            else "not_proved"
        ),
        "cpu_only": True,
        "model_calls": 0,
        "problem_specific_rules": 0,
        "preloaded_certificate_used": False,
        "source_equivalence_status": "unchecked",
        "promotable": False,
        "source_arguments_sha256": source_sha,
        "candidate_arguments_sha256": candidate_sha,
        "guard_program_sha256": guard_sha,
        "exact_transformation_validation_sha256": None,
        "transform_sha256": transform_payload["transform_sha256"],
        "derived_profile": derived_profile,
        "structural_preview_file_sha256": expected_structural_preview_sha256,
        "exact_status": exact_result.get("markers", {}).get(
            "RESULT_ORDINARY", exact_result.get("status")
        ),
        "backend_proved": backend_proved,
        "membership_certificate_scope": "all_transformed_original_generators",
        "membership_certificate_exported": identity is not None,
        "membership_certificate_reexpanded": (
            identity is not None and identity.get("reexpansion_zero") is True
        ),
        "derived_identity_certificate_sha256": (
            None if identity is None else identity["certificate_sha256"]
        ),
        # This is a target screen, not proof evidence about the source request.
        "validation_status": "screen_only",
        "evidence_status": "nonpromotable",
        "timeout_sec": timeout_sec,
        "memory_mb": memory_mb,
        "artifact_sha256": artifacts,
    }
    _write_json(destination / "result.json", result)
    return {
        **result,
        "result_file_sha256": _sha256_file(destination / "result.json"),
    }


def _decode_transform_payload(
    transform: Mapping[str, Any],
) -> tuple[list[sp.Symbol], list[tuple[str, sp.Expr]], sp.Expr, dict[str, sp.Expr]]:
    symbol_names = transform.get("symbols")
    if (
        not isinstance(symbol_names, list)
        or not symbol_names
        or any(not isinstance(name, str) or not name for name in symbol_names)
        or len(symbol_names) != len(set(symbol_names))
    ):
        raise ValueError("persisted Laurent symbol list is malformed")
    symbols = list(sp.symbols(" ".join(symbol_names), seq=True))

    def decode(payload: Mapping[str, Any]) -> sp.Expr:
        terms = payload.get("terms")
        if not isinstance(terms, list):
            raise ValueError("persisted Laurent polynomial payload is malformed")
        expression = sp.Integer(0)
        for term in terms:
            if not isinstance(term, Mapping):
                raise ValueError("persisted Laurent term is malformed")
            powers = term.get("powers")
            coefficient = term.get("coefficient")
            if (
                not isinstance(powers, list)
                or len(powers) != len(symbols)
                or not isinstance(coefficient, Mapping)
            ):
                raise ValueError("persisted Laurent polynomial arity changed")
            value = sp.Rational(
                int(coefficient["real_numerator"]),
                int(coefficient["real_denominator"]),
            ) + sp.I * sp.Rational(
                int(coefficient["imaginary_numerator"]),
                int(coefficient["imaginary_denominator"]),
            )
            expression += value * sp.prod(
                symbol ** int(power)
                for symbol, power in zip(symbols, powers, strict=True)
            )
        return sp.Poly(sp.expand(expression), *symbols, extension=sp.I).as_expr()

    generator_payloads = transform.get("generators")
    guard_payloads = transform.get("guards")
    target_payload = transform.get("target")
    if not isinstance(generator_payloads, Mapping) or not generator_payloads:
        raise ValueError("persisted Laurent generators are missing")
    if not isinstance(guard_payloads, Mapping) or not isinstance(target_payload, Mapping):
        raise ValueError("persisted Laurent target or guards are malformed")
    generators = [
        (str(label), decode(payload))
        for label, payload in generator_payloads.items()
        if isinstance(payload, Mapping)
    ]
    guards = {
        str(label): decode(payload)
        for label, payload in guard_payloads.items()
        if isinstance(payload, Mapping)
    }
    if len(generators) != len(generator_payloads) or len(guards) != len(guard_payloads):
        raise ValueError("persisted Laurent polynomial payload is malformed")
    return symbols, generators, decode(target_payload), guards


def screen_persisted_preview_target(
    *,
    source_arguments: Mapping[str, Any],
    candidate_arguments: Mapping[str, Any],
    guard_program: Mapping[str, Any],
    preview_output_dir: Path,
    output_dir: Path,
    singular_binary: Path,
    timeout_sec: int,
    memory_mb: int,
    expected_transform_sha256: str,
    expected_derived_profile: Mapping[str, Any],
    expected_structural_preview_sha256: str,
) -> dict[str, Any]:
    """Run Singular directly on a hash-bound persisted Laurent preview.

    This deliberately avoids recomputing the symbolic Laurent transform.  A
    successful target screen remains nonpromotable until preprocess_only later
    replays the transform and proves the full source lift.
    """

    if not singular_binary.resolve().is_file():
        raise FileNotFoundError(singular_binary)
    preview_root = preview_output_dir.resolve()
    preview_path = preview_root / "preview.json"
    transform_path = preview_root / "laurent_transform.json"
    guard_binding_path = preview_root / "typed_guard_binding.json"
    if _sha256_file(preview_path) != expected_structural_preview_sha256:
        raise ValueError("persisted Laurent preview file hash changed")
    preview = json.loads(preview_path.read_text(encoding="utf-8"))
    if preview.get("state") != "structural_preview_unvalidated":
        raise ValueError("persisted Laurent preview has an invalid state")
    if preview.get("promotable") is not False:
        raise ValueError("persisted Laurent preview crossed the promotion boundary")
    source_sha = exact_tools.stable_hash(source_arguments)
    candidate_sha = exact_tools.stable_hash(candidate_arguments)
    guard_sha = exact_tools.stable_hash(guard_program)
    if (
        preview.get("source_arguments_sha256") != source_sha
        or preview.get("candidate_arguments_sha256") != candidate_sha
        or preview.get("guard_program_sha256") != guard_sha
    ):
        raise ValueError("persisted Laurent preview input binding changed")
    if preview.get("transform_sha256") != expected_transform_sha256:
        raise ValueError("persisted Laurent preview transform binding changed")
    if preview.get("derived_profile") != dict(expected_derived_profile):
        raise ValueError("persisted Laurent preview profile changed")
    artifacts = preview.get("artifact_sha256")
    if not isinstance(artifacts, Mapping):
        raise ValueError("persisted Laurent preview artifact ledger is missing")
    if artifacts.get("laurent_transform.json") != _sha256_file(transform_path):
        raise ValueError("persisted Laurent transform file hash changed")
    if artifacts.get("typed_guard_binding.json") != _sha256_file(guard_binding_path):
        raise ValueError("persisted Laurent guard-binding file hash changed")
    transform = json.loads(transform_path.read_text(encoding="utf-8"))
    transform_payload = dict(transform)
    internal_transform_sha = transform_payload.pop("transform_sha256", None)
    if (
        exact_tools.stable_hash(transform_payload) != internal_transform_sha
        or internal_transform_sha != expected_transform_sha256
    ):
        raise ValueError("persisted Laurent transform internal hash changed")

    destination = output_dir.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(transform_path, destination / "laurent_transform.json")
    shutil.copyfile(guard_binding_path, destination / "typed_guard_binding.json")
    symbols, generators, target, guards = _decode_transform_payload(transform)
    exact_result = gaussian_backend.check(
        symbols=symbols,
        generators=generators,
        target=target,
        guards=guards,
        binary=singular_binary.resolve(),
        timeout_sec=timeout_sec,
        memory_mb=memory_mb,
        radical=False,
    )
    _write_json(destination / "exact_result.json", exact_result)
    backend_proved, identity = _persist_membership_identity(
        exact_result=exact_result,
        transform_sha256=expected_transform_sha256,
        destination=destination,
    )
    proved = backend_proved and identity is not None
    artifact_names = [
        "typed_guard_binding.json",
        "laurent_transform.json",
        "exact_result.json",
    ]
    if identity is not None:
        artifact_names.append("derived_identity_certificate.json")
    result = {
        "schema": "cognitive-well-v0314-persisted-laurent-target-screen-v1",
        "state": (
            "proved"
            if proved
            else "uncertified_backend_proof"
            if backend_proved
            else "not_proved"
        ),
        "cpu_only": True,
        "model_calls": 0,
        "problem_specific_rules": 0,
        "preloaded_certificate_used": False,
        "source_equivalence_status": "unchecked",
        "promotable": False,
        "persisted_preview_verified": True,
        "transform_recomputed_before_screen": False,
        "source_arguments_sha256": source_sha,
        "candidate_arguments_sha256": candidate_sha,
        "guard_program_sha256": guard_sha,
        "exact_transformation_validation_sha256": None,
        "transform_sha256": expected_transform_sha256,
        "derived_profile": dict(expected_derived_profile),
        "structural_preview_file_sha256": expected_structural_preview_sha256,
        "exact_status": exact_result.get("markers", {}).get(
            "RESULT_ORDINARY", exact_result.get("status")
        ),
        "backend_proved": backend_proved,
        "membership_certificate_scope": "all_transformed_original_generators",
        "membership_certificate_exported": identity is not None,
        "membership_certificate_reexpanded": (
            identity is not None and identity.get("reexpansion_zero") is True
        ),
        "derived_identity_certificate_sha256": (
            None if identity is None else identity["certificate_sha256"]
        ),
        "validation_status": "screen_only",
        "evidence_status": "nonpromotable",
        "timeout_sec": timeout_sec,
        "memory_mb": memory_mb,
        "artifact_sha256": {
            name: _sha256_file(destination / name) for name in artifact_names
        },
    }
    _write_json(destination / "result.json", result)
    return {**result, "result_file_sha256": _sha256_file(destination / "result.json")}


def bounded_screen_persisted_preview_target(
    *,
    source_arguments: Mapping[str, Any],
    candidate_arguments: Mapping[str, Any],
    guard_program: Mapping[str, Any],
    preview_output_dir: Path,
    output_dir: Path,
    singular_binary: Path,
    timeout_sec: int,
    memory_mb: int,
    expected_transform_sha256: str,
    expected_derived_profile: Mapping[str, Any],
    expected_structural_preview_sha256: str,
) -> dict[str, Any]:
    return _bounded(
        mode="screen_persisted",
        output_dir=output_dir,
        timeout_sec=timeout_sec + 30,
        memory_mb=memory_mb,
        kwargs={
            "source_arguments": source_arguments,
            "candidate_arguments": candidate_arguments,
            "guard_program": guard_program,
            "preview_output_dir": preview_output_dir,
            "singular_binary": singular_binary,
            "timeout_sec": timeout_sec,
            "memory_mb": memory_mb,
            "expected_transform_sha256": expected_transform_sha256,
            "expected_derived_profile": dict(expected_derived_profile),
            "expected_structural_preview_sha256": expected_structural_preview_sha256,
        },
    )


def bounded_screen_preview_target(
    *,
    source_arguments: Mapping[str, Any],
    candidate_arguments: Mapping[str, Any],
    guard_program: Mapping[str, Any],
    output_dir: Path,
    singular_binary: Path,
    timeout_sec: int,
    memory_mb: int,
    expected_transform_sha256: str,
    expected_derived_profile: Mapping[str, Any],
    expected_structural_preview_sha256: str,
) -> dict[str, Any]:
    return _bounded(
        mode="screen",
        output_dir=output_dir,
        timeout_sec=timeout_sec,
        memory_mb=memory_mb,
        kwargs={
            "source_arguments": source_arguments,
            "candidate_arguments": candidate_arguments,
            "guard_program": guard_program,
            "singular_binary": singular_binary,
            "timeout_sec": timeout_sec,
            "memory_mb": memory_mb,
            "expected_transform_sha256": expected_transform_sha256,
            "expected_derived_profile": dict(expected_derived_profile),
            "expected_structural_preview_sha256": (
                expected_structural_preview_sha256
            ),
        },
    )


def preprocess_and_execute(
    *,
    source_arguments: Mapping[str, Any],
    candidate_arguments: Mapping[str, Any],
    guard_program: Mapping[str, Any],
    exact_transformation_validation: Mapping[str, Any],
    output_dir: Path,
    singular_binary: Path,
    timeout_sec: int,
    memory_mb: int,
    expected_transform_sha256: str | None = None,
    expected_derived_profile: Mapping[str, Any] | None = None,
    expected_structural_preview_sha256: str | None = None,
    expected_certified_preparation_sha256: str | None = None,
) -> dict[str, Any]:
    """Run generic Laurent preprocessing followed by exact ideal membership."""

    if exact_transformation_validation.get("decision") != "ACCEPT":
        raise ValueError("Laurent preprocessing requires exact transformation ACCEPT")
    source_sha = exact_tools.stable_hash(source_arguments)
    candidate_sha = exact_tools.stable_hash(candidate_arguments)
    guard_sha = exact_tools.stable_hash(guard_program)
    validation_sha = exact_tools.stable_hash(exact_transformation_validation)
    expected = {
        "source_arguments_sha256": source_sha,
        "candidate_arguments_sha256": candidate_sha,
        "guard_program_sha256": guard_sha,
    }
    for field, value in expected.items():
        if exact_transformation_validation.get(field) != value:
            raise ValueError(f"exact transformation validation lost {field}")
    if not singular_binary.resolve().is_file():
        raise FileNotFoundError(singular_binary)
    destination = output_dir.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    candidate = exact_tools.validate_ideal_arguments(candidate_arguments)
    guards, guard_ledger = _eligible_guards(
        source_arguments=source_arguments,
        candidate_arguments=candidate_arguments,
        guard_program=guard_program,
    )
    _write_json(destination / "typed_guard_binding.json", guard_ledger)
    transformed = laurent_elimination.transform(
        candidate, nonzero_guards=guards
    )
    transform_payload = laurent_elimination.json_transform(transformed)
    if (
        expected_transform_sha256 is not None
        and transform_payload["transform_sha256"] != expected_transform_sha256
    ):
        raise ValueError("recomputed Laurent transform hash changed before execution")
    _write_json(destination / "laurent_transform.json", transform_payload)
    lift = laurent_elimination.full_lift_certificate(
        validated=candidate,
        transformed=transformed,
        source_arguments_sha256=source_sha,
        guard_program_sha256=guard_sha,
        exact_transformation_validation_sha256=validation_sha,
        transform_sha256=transform_payload["transform_sha256"],
    )
    _write_json(destination / "full_source_lift_certificate.json", lift)

    selected = transformed["selected"]
    eliminated = selected["elimination"]
    derived_profile = _derived_profile(
        transform_payload=transform_payload, eliminated=eliminated
    )
    if (
        expected_derived_profile is not None
        and dict(expected_derived_profile) != derived_profile
    ):
        raise ValueError("executed Laurent profile does not match certified preview")
    filtered_guards = {
        label: expression
        for label, expression in selected["transformed_guards"].items()
        if eliminated["variable"] is None
        or eliminated["variable"] not in expression.free_symbols
    }
    exact_result = gaussian_backend.check(
        symbols=list(eliminated["symbols"]),
        generators=list(eliminated["generators"]),
        target=eliminated["target"],
        guards=filtered_guards,
        binary=singular_binary.resolve(),
        timeout_sec=timeout_sec,
        memory_mb=memory_mb,
        radical=False,
    )
    _write_json(destination / "exact_result.json", exact_result)
    backend_proved = (
        exact_result.get("status") == "COMPLETED"
        and exact_result.get("markers", {}).get("RESULT_ORDINARY") == "PROVED"
    )
    identity = None
    backend_identity = exact_result.get("membership_certificate")
    if (
        backend_proved
        and exact_result.get("certificate_reexpanded") is True
        and isinstance(backend_identity, Mapping)
    ):
        identity_payload = {
            "schema": "cognitive-well-v0282-gaussian-membership-identity-v1",
            "transform_sha256": transform_payload["transform_sha256"],
            "gaussian_certificate_sha256": backend_identity.get(
                "certificate_sha256"
            ),
            "coefficient_field": backend_identity.get("coefficient_field"),
            "generator_labels": list(backend_identity.get("generator_labels", [])),
            "source_multipliers": dict(
                backend_identity.get("source_multipliers", {})
            ),
            "target_expression": backend_identity.get("target_expression"),
            "exact_remainder": backend_identity.get("exact_remainder"),
            "reexpansion_zero": backend_identity.get("reexpansion_zero"),
        }
        identity = {
            **identity_payload,
            "certificate_sha256": exact_tools.stable_hash(identity_payload),
        }
        _write_json(destination / "derived_identity_certificate.json", identity)
    # A marker alone is never promotable.  The backend must export original-
    # generator multipliers and independently re-expand the exact QQ(i) identity.
    proved = backend_proved and identity is not None
    appendix = _mathematical_appendix(
        transformed=transformed,
        guard_ledger=guard_ledger,
        lift=lift,
        identity=identity,
    )
    appendix_path = destination / "mathematical_certificate_appendix.md"
    appendix_path.write_text(appendix, encoding="utf-8")
    artifact_hashes = {
        name: _sha256_file(destination / name)
        for name in (
            "typed_guard_binding.json",
            "laurent_transform.json",
            "full_source_lift_certificate.json",
            "exact_result.json",
            "mathematical_certificate_appendix.md",
        )
    }
    if identity is not None:
        artifact_hashes["derived_identity_certificate.json"] = _sha256_file(
            destination / "derived_identity_certificate.json"
        )
    result = {
        "schema": "cognitive-well-v0282-generic-laurent-preprocessing-result-v1",
        "state": (
            "proved"
            if proved
            else "uncertified_backend_proof"
            if backend_proved
            else "not_proved"
        ),
        "cpu_only": True,
        "model_calls": 0,
        "problem_specific_rules": 0,
        "preloaded_certificate_used": False,
        "source_arguments_sha256": source_sha,
        "candidate_arguments_sha256": candidate_sha,
        "guard_program_sha256": guard_sha,
        "exact_transformation_validation_sha256": validation_sha,
        "transform_sha256": transform_payload["transform_sha256"],
        "full_source_lift_certificate_sha256": lift["certificate_sha256"],
        "derived_identity_certificate_sha256": (
            None if identity is None else identity["certificate_sha256"]
        ),
        "detected_circle_count": len(transformed["detected_circles"]),
        "detected_circle_candidate_count": len(
            transformed["detected_circle_candidates"]
        ),
        "circle_set_count": transformed["circle_set_count"],
        "orientation_attempted_count": transformed[
            "orientation_attempted_count"
        ],
        "orientation_success_count": transformed["orientation_success_count"],
        "selected_circle_set_index": selected["circle_set_index"],
        "selected_orientation": list(selected["orientation"]),
        "derived_profile": derived_profile,
        "matched_certified_preview": expected_transform_sha256 is not None,
        "expected_preview_transform_sha256": expected_transform_sha256,
        "expected_preview_derived_profile": (
            None
            if expected_derived_profile is None
            else dict(expected_derived_profile)
        ),
        "structural_preview_file_sha256": expected_structural_preview_sha256,
        "certified_preparation_file_sha256": (
            expected_certified_preparation_sha256
        ),
        "exact_status": exact_result.get("markers", {}).get(
            "RESULT_ORDINARY", exact_result.get("status")
        ),
        "backend_proved": backend_proved,
        "membership_certificate_scope": "all_transformed_original_generators",
        "membership_certificate_exported": identity is not None,
        "membership_certificate_reexpanded": (
            identity is not None and identity.get("reexpansion_zero") is True
        ),
        "validation_status": "passed" if proved and lift["verified"] else "failed",
        "evidence_status": "verified" if proved and lift["verified"] else "absent",
        "timeout_sec": timeout_sec,
        "memory_mb": memory_mb,
        "artifact_sha256": artifact_hashes,
        "mathematical_certificate_appendix": appendix,
        "mathematical_certificate_appendix_sha256": hashlib.sha256(
            appendix.encode("utf-8")
        ).hexdigest(),
    }
    _write_json(destination / "result.json", result)
    result["result_file_sha256"] = _sha256_file(destination / "result.json")
    return result


def bounded_preprocess_and_execute(
    *,
    source_arguments: Mapping[str, Any],
    candidate_arguments: Mapping[str, Any],
    guard_program: Mapping[str, Any],
    exact_transformation_validation: Mapping[str, Any],
    output_dir: Path,
    singular_binary: Path,
    timeout_sec: int,
    memory_mb: int,
    expected_transform_sha256: str | None = None,
    expected_derived_profile: Mapping[str, Any] | None = None,
    expected_structural_preview_sha256: str | None = None,
    expected_certified_preparation_sha256: str | None = None,
) -> dict[str, Any]:
    return _bounded(
        mode="execute",
        output_dir=output_dir,
        timeout_sec=timeout_sec,
        memory_mb=memory_mb,
        kwargs={
            "source_arguments": source_arguments,
            "candidate_arguments": candidate_arguments,
            "guard_program": guard_program,
            "exact_transformation_validation": exact_transformation_validation,
            "singular_binary": singular_binary,
            "timeout_sec": timeout_sec,
            "memory_mb": memory_mb,
            "expected_transform_sha256": expected_transform_sha256,
            "expected_derived_profile": expected_derived_profile,
            "expected_structural_preview_sha256": (
                expected_structural_preview_sha256
            ),
            "expected_certified_preparation_sha256": (
                expected_certified_preparation_sha256
            ),
        },
    )


def render_evidence(result: Mapping[str, Any]) -> str:
    header = "\n".join(
        [
            "# Exact Tool Evidence",
            "",
            "- Route: deterministic unit-circle Laurent preprocessing",
            f"- Exact result: `{result['exact_status']}`",
            f"- Validation: `{result['validation_status']}`",
            f"- Evidence: `{result['evidence_status']}`",
            f"- Unit-circle pairs transformed simultaneously: {result['detected_circle_count']}",
            f"- Orientations attempted: {result['orientation_attempted_count']}",
            f"- Orientations yielding guarded elimination: {result['orientation_success_count']}",
            f"- Selected orientation: {result['selected_orientation']}",
            f"- Source arguments SHA-256: `{result['source_arguments_sha256']}`",
            f"- Candidate arguments SHA-256: `{result['candidate_arguments_sha256']}`",
            f"- Typed guard program SHA-256: `{result['guard_program_sha256']}`",
            f"- Laurent transform SHA-256: `{result['transform_sha256']}`",
            f"- Full source-lift certificate SHA-256: `{result['full_source_lift_certificate_sha256']}`",
            "- CPU only: yes",
            "- Preloaded certificate: none",
        ]
    ) + "\n"
    appendix = str(result.get("mathematical_certificate_appendix") or "")
    if hashlib.sha256(appendix.encode("utf-8")).hexdigest() != result.get(
        "mathematical_certificate_appendix_sha256"
    ):
        raise ValueError("mathematical certificate appendix hash mismatch")
    return header + "\n" + appendix


def verify_exported_membership_identity(
    *, output_dir: Path, result: Mapping[str, Any]
) -> dict[str, Any]:
    """Replay the persisted general QQ(i) identity without invoking Singular."""

    root = output_dir.resolve()
    transform = json.loads(
        (root / "laurent_transform.json").read_text(encoding="utf-8")
    )
    transform_payload = dict(transform)
    transform_sha = transform_payload.pop("transform_sha256", None)
    if exact_tools.stable_hash(transform_payload) != transform_sha or result.get(
        "transform_sha256"
    ) != transform_sha:
        raise ValueError("Laurent transform hash failed identity replay")
    symbol_names = list(transform["symbols"])
    if not symbol_names or len(symbol_names) != len(set(symbol_names)):
        raise ValueError("Laurent transform symbols are malformed")
    symbols = list(sp.symbols(" ".join(symbol_names), seq=True))

    def decode_polynomial(payload: Mapping[str, Any]) -> sp.Expr:
        terms = payload.get("terms")
        if not isinstance(terms, list):
            raise ValueError("Laurent polynomial payload is malformed")
        expression = sp.Integer(0)
        for term in terms:
            if not isinstance(term, Mapping) or not isinstance(term.get("powers"), list):
                raise ValueError("Laurent polynomial term is malformed")
            powers = term["powers"]
            coefficient = term.get("coefficient")
            if len(powers) != len(symbols) or not isinstance(coefficient, Mapping):
                raise ValueError("Laurent polynomial arity changed")
            value = sp.Rational(
                int(coefficient["real_numerator"]),
                int(coefficient["real_denominator"]),
            ) + sp.I * sp.Rational(
                int(coefficient["imaginary_numerator"]),
                int(coefficient["imaginary_denominator"]),
            )
            expression += value * sp.prod(
                symbol ** int(power)
                for symbol, power in zip(symbols, powers, strict=True)
            )
        return sp.Poly(sp.expand(expression), *symbols, extension=sp.I).as_expr()

    generator_payloads = transform.get("generators")
    if not isinstance(generator_payloads, Mapping) or not generator_payloads:
        raise ValueError("Laurent transform generators are missing")
    generators = {
        str(label): decode_polynomial(payload)
        for label, payload in generator_payloads.items()
        if isinstance(payload, Mapping)
    }
    if len(generators) != len(generator_payloads):
        raise ValueError("Laurent transform generator payload is malformed")
    target = decode_polynomial(transform["target"])
    identity = json.loads(
        (root / "derived_identity_certificate.json").read_text(encoding="utf-8")
    )
    identity_payload = dict(identity)
    identity_sha = identity_payload.pop("certificate_sha256", None)
    if exact_tools.stable_hash(identity_payload) != identity_sha or result.get(
        "derived_identity_certificate_sha256"
    ) != identity_sha:
        raise ValueError("Laurent membership identity hash failed replay")
    labels = list(generators)
    multipliers = identity.get("source_multipliers")
    if (
        identity.get("schema")
        != "cognitive-well-v0282-gaussian-membership-identity-v1"
        or identity.get("generator_labels") != labels
        or not isinstance(multipliers, Mapping)
        or list(multipliers) != labels
        or identity.get("reexpansion_zero") is not True
        or identity.get("exact_remainder") != "0"
    ):
        raise ValueError("Laurent membership identity structure changed")
    expanded = sp.Integer(0)
    for label, generator in generators.items():
        multiplier = parse_polynomial(str(multipliers[label]), symbols)
        if not multiplier.free_symbols.issubset(set(symbols)):
            raise ValueError("Laurent multiplier contains an undeclared symbol")
        expanded += multiplier * generator
    if sp.Poly(sp.expand(target - expanded), *symbols, extension=sp.I).is_zero is not True:
        raise ValueError("Laurent original-generator identity does not re-expand")
    identity_target = parse_polynomial(str(identity["target_expression"]), symbols)
    if sp.expand(identity_target - target) != 0:
        raise ValueError("Laurent identity target expression changed")
    exact_result = json.loads(
        (root / "exact_result.json").read_text(encoding="utf-8")
    )
    backend_identity = exact_result.get("membership_certificate")
    if (
        exact_result.get("status") != "COMPLETED"
        or exact_result.get("markers", {}).get("RESULT_ORDINARY") != "PROVED"
        or exact_result.get("certificate_reexpanded") is not True
        or not isinstance(backend_identity, Mapping)
        or backend_identity.get("certificate_sha256")
        != identity.get("gaussian_certificate_sha256")
        or result.get("membership_certificate_exported") is not True
        or result.get("membership_certificate_reexpanded") is not True
    ):
        raise ValueError("Laurent backend membership certificate changed")
    return {
        "verified": True,
        "transform_sha256": transform_sha,
        "identity_sha256": identity_sha,
        "generator_count": len(labels),
        "reexpansion_zero": True,
    }


def verify_persisted_laurent_outcome(
    *, output_dir: Path, result: Mapping[str, Any]
) -> dict[str, Any]:
    """Bind a Laurent target outcome, including a closed non-proof outcome."""

    root = output_dir.resolve()
    artifact_hashes = result.get("artifact_sha256")
    if not isinstance(artifact_hashes, Mapping):
        raise ValueError("Laurent outcome artifact ledger is missing")
    for relative, digest in artifact_hashes.items():
        artifact = (root / str(relative)).resolve()
        if root not in artifact.parents or not artifact.is_file():
            raise ValueError("Laurent outcome artifact escaped its root")
        if _sha256_file(artifact) != digest:
            raise ValueError(f"Laurent outcome artifact hash changed: {relative}")
    exact_result = json.loads(
        (root / "exact_result.json").read_text(encoding="utf-8")
    )
    program = exact_result.get("program")
    output = exact_result.get("output")
    if (
        not isinstance(program, str)
        or not isinstance(output, str)
        or hashlib.sha256(program.encode()).hexdigest()
        != exact_result.get("program_sha256")
        or hashlib.sha256(output.encode()).hexdigest()
        != exact_result.get("output_sha256")
        or len(output.encode("utf-8")) > gaussian_backend.MAX_BACKEND_OUTPUT_BYTES
        or gaussian_backend._singular_diagnostic(output)
    ):
        raise ValueError("Laurent Singular program/output binding changed")
    try:
        parsed_markers = gaussian_backend._markers(output)
    except ValueError as error:
        raise ValueError("Laurent Singular markers are not unique") from error
    if parsed_markers != exact_result.get("markers"):
        raise ValueError("Laurent Singular marker ledger changed")
    if result.get("state") == "proved":
        identity = verify_exported_membership_identity(
            output_dir=root, result=result
        )
        return {"verified": True, "affirmative": True, "identity": identity}
    if (
        parsed_markers.get("RESULT_ORDINARY") == "PROVED"
        or result.get("validation_status") == "passed"
        or result.get("evidence_status") == "verified"
        or result.get("membership_certificate_exported") is True
    ):
        raise ValueError("closed Laurent non-proof outcome became affirmative")
    remainder_text = exact_result.get("normal_form_remainder")
    if parsed_markers.get("RESULT_ORDINARY") == "NONZERO":
        if not isinstance(remainder_text, str):
            raise ValueError("Laurent non-proof remainder is missing")
        names = json.loads(
            (root / "laurent_transform.json").read_text(encoding="utf-8")
        )["symbols"]
        symbols = list(sp.symbols(" ".join(names), seq=True))
        remainder = sp.sympify(
            remainder_text, locals={str(symbol): symbol for symbol in symbols}
        )
        if remainder == 0 or not remainder.free_symbols.issubset(set(symbols)):
            raise ValueError("Laurent non-proof remainder is not a bound nonzero polynomial")
    return {
        "verified": True,
        "affirmative": False,
        "status": result.get("state"),
        "exact_status": result.get("exact_status"),
    }
