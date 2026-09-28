from __future__ import annotations

import hashlib
import json
import multiprocessing
import resource
import time
from pathlib import Path
from typing import Any, Mapping

try:
    import sympy as sp
except ModuleNotFoundError:  # Routing/dry-run remains available outside the math env.
    sp = None  # type: ignore[assignment]

import scripts.run_v0220_gemma_global_tool_budget_20260904 as v0220
import scripts.run_v0221_gemma_constrained_tool_router_budget_20260904 as v0221
import scripts.v0236_markdown_protocol as mdp
from tir_sab_v0_1_4_2_4.frozen_source.math_harness.tools.schemas import (
    operation_hash as registry_operation_hash,
)


IDEAL_OPERATION = "polynomial_ideal_membership"
LEGACY_OPERATIONS = tuple(v0221.EXPOSED_OPERATIONS)
EXPOSED_OPERATIONS = LEGACY_OPERATIONS + (IDEAL_OPERATION,)

MAX_SYMBOLS = 16
MAX_GENERATORS = 12
MAX_AST_NODES = 20_000
MAX_EXPONENT = 32
MAX_CERTIFICATE_EXPONENT = 1_000_000
MAX_INTEGER_ABS = 10**18
DEFAULT_IDEAL_TIMEOUT_SEC = 900
MAX_IDEAL_TIMEOUT_SEC = 3_600
DEFAULT_IDEAL_MEMORY_MB = 4_096
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CERTIFICATE_CACHE_DIR = ROOT / "runs/_v0274_exact_certificate_cache"
EXACT_CACHE_SCHEMA = "cognitive-well-v0274-exact-certificate-cache-v1"


def stable_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def require_sympy() -> Any:
    if sp is None:
        raise RuntimeError(
            "polynomial_ideal_membership requires the existing SymPy math environment"
        )
    return sp


def _ast_size(node: Any) -> int:
    if isinstance(node, (int, str)):
        return 1
    if isinstance(node, list):
        return 1 + sum(_ast_size(value) for value in node)
    if isinstance(node, Mapping):
        return 1 + sum(_ast_size(key) + _ast_size(value) for key, value in node.items())
    raise ValueError("unsupported AST value")


def _expression(node: Any, symbols: Mapping[str, sp.Symbol], *, max_ast_nodes: int | None = None) -> sp.Expr:
    symbolic = require_sympy()
    limit = MAX_AST_NODES if max_ast_nodes is None else max_ast_nodes
    if _ast_size(node) > limit:
        raise ValueError("expression AST exceeds the node limit")
    if isinstance(node, bool):
        raise ValueError("Boolean leaves are not polynomials")
    if isinstance(node, int):
        if abs(node) > MAX_INTEGER_ABS:
            raise ValueError("integer leaf exceeds the magnitude limit")
        return symbolic.Integer(node)
    if not isinstance(node, Mapping) or len(node) != 1:
        raise ValueError("expression must use the safe one-key AST")
    head, value = next(iter(node.items()))
    if head == "symbol":
        name = str(value)
        if name not in symbols:
            raise ValueError(f"expression uses undeclared symbol {name!r}")
        return symbols[name]
    if head == "rational":
        if (
            not isinstance(value, list)
            or len(value) != 2
            or any(isinstance(item, bool) or not isinstance(item, int) for item in value)
            or value[1] == 0
            or any(abs(item) > MAX_INTEGER_ABS for item in value)
        ):
            raise ValueError("malformed rational leaf")
        return symbolic.Rational(value[0], value[1])
    if head in {"add", "mul"}:
        if not isinstance(value, list) or len(value) < 2:
            raise ValueError(f"{head} requires at least two operands")
        parts = [_expression(item, symbols, max_ast_nodes=limit) for item in value]
        return symbolic.Add(*parts) if head == "add" else symbolic.Mul(*parts)
    if head in {"sub", "pow"}:
        if not isinstance(value, list) or len(value) != 2:
            raise ValueError(f"{head} requires exactly two operands")
        left = _expression(value[0], symbols, max_ast_nodes=limit)
        if head == "sub":
            return left - _expression(value[1], symbols, max_ast_nodes=limit)
        exponent = value[1]
        if isinstance(exponent, bool) or not isinstance(exponent, int):
            raise ValueError("polynomial exponent must be an integer")
        if not 0 <= exponent <= MAX_EXPONENT:
            raise ValueError("polynomial exponent is outside the allowed range")
        return left**exponent
    if head == "neg":
        return -_expression(value, symbols, max_ast_nodes=limit)
    raise ValueError(f"operation {head!r} is not polynomial-safe")


def validate_ideal_arguments(arguments: Mapping[str, Any]) -> dict[str, Any]:
    symbolic = require_sympy()
    if set(arguments) != {"symbols", "generators", "target"}:
        raise ValueError("ideal-membership arguments have unexpected fields")
    names = list(arguments["symbols"])
    if not 1 <= len(names) <= MAX_SYMBOLS:
        raise ValueError(f"ideal-membership symbols must be unique and bounded: expected 1..{MAX_SYMBOLS} symbols, received {len(names)}")
    if len(names) != len(set(names)):
        raise ValueError("ideal-membership symbols must be unique and bounded: duplicate symbol names")
    if any(not isinstance(name, str) or not name.isidentifier() for name in names):
        raise ValueError("invalid ideal-membership symbol")
    raw_generators = arguments["generators"]
    if not isinstance(raw_generators, Mapping):
        raise ValueError("ideal-membership generators must be a bounded mapping")
    if not 1 <= len(raw_generators) <= MAX_GENERATORS:
        raise ValueError(f"ideal-membership generators must be a bounded mapping: expected 1..{MAX_GENERATORS} generators, received {len(raw_generators)}")
    labels = list(raw_generators)
    if any(not isinstance(label, str) or not label.startswith("D") for label in labels):
        raise ValueError("invalid ideal-membership generator label")
    symbol_map = {name: symbolic.Symbol(name) for name in names}
    generators = {
        label: symbolic.Poly(
            symbolic.expand(_expression(raw_generators[label], symbol_map)),
            *symbol_map.values(),
        )
        for label in labels
    }
    target = symbolic.Poly(
        symbolic.expand(_expression(arguments["target"], symbol_map)),
        *symbol_map.values(),
    )
    return {
        "symbols": names,
        "symbol_map": symbol_map,
        "generators": generators,
        "target": target,
    }


def _term_payload(expression: sp.Expr, names: list[str]) -> list[dict[str, Any]]:
    """Serialize a QQ polynomial without reparsing executable expression text."""

    symbolic = require_sympy()
    symbols = [symbolic.Symbol(name) for name in names]
    polynomial = symbolic.Poly(symbolic.expand(expression), *symbols, domain=symbolic.QQ)
    rows: list[dict[str, Any]] = []
    for powers, coefficient in polynomial.terms():
        rational = symbolic.Rational(coefficient)
        rows.append(
            {
                "powers": list(powers),
                "numerator": int(rational.p),
                "denominator": int(rational.q),
            }
        )
    return rows


def _expression_from_terms(
    rows: Any, names: list[str], symbol_map: Mapping[str, sp.Symbol]
) -> sp.Expr:
    symbolic = require_sympy()
    if not isinstance(rows, list):
        raise ValueError("cached polynomial terms must be a list")
    expression = symbolic.Integer(0)
    for row in rows:
        if not isinstance(row, Mapping) or set(row) != {
            "powers",
            "numerator",
            "denominator",
        }:
            raise ValueError("malformed cached polynomial term")
        powers = row["powers"]
        numerator = row["numerator"]
        denominator = row["denominator"]
        if (
            not isinstance(powers, list)
            or len(powers) != len(names)
            or any(isinstance(power, bool) or not isinstance(power, int) for power in powers)
            or any(power < 0 or power > MAX_CERTIFICATE_EXPONENT for power in powers)
            or isinstance(numerator, bool)
            or not isinstance(numerator, int)
            or isinstance(denominator, bool)
            or not isinstance(denominator, int)
            or denominator == 0
        ):
            raise ValueError("malformed cached polynomial coefficient")
        term = symbolic.Rational(numerator, denominator)
        for name, power in zip(names, powers, strict=True):
            term *= symbol_map[name] ** power
        expression += term
    return symbolic.expand(expression)


def _reexpand_machine_certificate(
    arguments: Mapping[str, Any], machine: Mapping[str, Any]
) -> dict[str, Any]:
    """Replay an ideal-membership certificate from safe polynomial terms."""

    symbolic = require_sympy()
    validated = validate_ideal_arguments(arguments)
    names: list[str] = validated["symbols"]
    generators: Mapping[str, sp.Poly] = validated["generators"]
    if set(machine) != set(generators):
        raise ValueError("multiplier labels do not match the ideal request")
    multipliers = {
        label: _expression_from_terms(machine[label], names, validated["symbol_map"])
        for label in generators
    }
    remainder = symbolic.Poly(
        symbolic.expand(
            validated["target"].as_expr()
            - sum(
                multipliers[label] * generators[label].as_expr()
                for label in generators
            )
        ),
        *validated["symbol_map"].values(),
    )
    if not remainder.is_zero:
        raise ValueError("ideal-membership certificate has nonzero exact remainder")
    return {
        "status": "PROVED",
        "exact_remainder": "0",
        "machine_certificate_sha256": stable_hash(machine),
        "multipliers": {
            label: symbolic.sstr(value) for label, value in multipliers.items()
        },
    }


def _lossless_reduction(validated: Mapping[str, Any]) -> dict[str, Any]:
    """Remove only mechanically provable algebraic redundancy.

    This deliberately does not perform heuristic equation selection. Semantic
    elimination and invariant choice belong to the audited compiler stage.
    """

    generators: Mapping[str, sp.Poly] = validated["generators"]
    target: sp.Poly = validated["target"]
    retained: dict[str, sp.Poly] = {}
    canonical_to_label: dict[str, str] = {}
    removals: dict[str, dict[str, Any]] = {}
    for label, polynomial in generators.items():
        if polynomial.is_zero:
            removals[label] = {"reason": "zero_generator", "representative": None}
            continue
        monic = polynomial.monic()
        key = symbolic_key = require_sympy().srepr(monic.as_expr())
        if key in canonical_to_label:
            representative = canonical_to_label[key]
            representative_poly = retained[representative]
            ratio = require_sympy().Rational(polynomial.LC(), representative_poly.LC())
            removals[label] = {
                "reason": "rationally_proportional_generator",
                "representative": representative,
                "ratio_to_representative": require_sympy().sstr(ratio),
            }
            continue
        canonical_to_label[symbolic_key] = label
        retained[label] = polynomial

    active = set(target.as_expr().free_symbols)
    for polynomial in retained.values():
        active.update(polynomial.as_expr().free_symbols)
    names = list(validated["symbols"])
    active_names = [name for name in names if validated["symbol_map"][name] in active]
    # SymPy's old polynomial ring requires at least one generator. A constant-only
    # system can safely retain one declared dummy symbol.
    if not active_names:
        active_names = names[:1]
    return {
        "original_symbol_count": len(names),
        "solver_symbol_count": len(active_names),
        "unused_symbols_removed": [name for name in names if name not in active_names],
        "original_generator_count": len(generators),
        "solver_generator_count": len(retained),
        "generator_removals": removals,
        "active_symbol_names": active_names,
        "retained_generators": retained,
    }


def ideal_request_profile(arguments: Mapping[str, Any]) -> dict[str, Any]:
    """Return deterministic pre-solve size and safe-reduction statistics."""

    validated = validate_ideal_arguments(arguments)
    reduction = _lossless_reduction(validated)
    retained: Mapping[str, sp.Poly] = reduction["retained_generators"]
    target: sp.Poly = validated["target"]
    polynomials = [target, *retained.values()]
    monomial_counts = [len(polynomial.terms()) for polynomial in polynomials]
    total_degrees = [int(polynomial.total_degree()) for polynomial in polynomials]
    return {
        key: value
        for key, value in reduction.items()
        if key not in {"active_symbol_names", "retained_generators"}
    } | {
        "maximum_total_degree": max(total_degrees, default=0),
        "total_monomial_count": sum(monomial_counts),
        "argument_ast_nodes": _ast_size(arguments),
        "canonical_argument_hash": stable_hash(arguments),
    }


def _cache_key(arguments: Mapping[str, Any]) -> str:
    return stable_hash(
        {
            "schema": EXACT_CACHE_SCHEMA,
            "operation": IDEAL_OPERATION,
            "backend": "sympy_agca_submodule_syzygy",
            "coefficient_domain": "QQ",
            "monomial_order": "lex",
            "arguments": arguments,
        }
    )


def _execute_ideal_membership_unbounded(arguments: Mapping[str, Any]) -> dict[str, Any]:
    symbolic = require_sympy()
    validated = validate_ideal_arguments(arguments)
    names = validated["symbols"]
    symbol_map = validated["symbol_map"]
    generators: Mapping[str, sp.Poly] = validated["generators"]
    target: sp.Poly = validated["target"]
    reduction = _lossless_reduction(validated)
    active_names: list[str] = reduction["active_symbol_names"]
    retained: Mapping[str, sp.Poly] = reduction["retained_generators"]
    active_symbols = [symbol_map[name] for name in active_names]
    started = time.perf_counter()
    if target.is_zero:
        multipliers = {label: symbolic.Integer(0) for label in generators}
        elapsed = time.perf_counter() - started
        return {
            "operation": IDEAL_OPERATION,
            "status": "PROVED",
            "validation_status": "passed",
            "evidence_status": "verified",
            "reason": "target is the zero polynomial",
            "symbols": names,
            "target": symbolic.sstr(target.as_expr()),
            "generators": {
                label: symbolic.sstr(value.as_expr()) for label, value in generators.items()
            },
            "multipliers": {label: "0" for label in generators},
            "identity": "R = "
            + " + ".join(f"P{label[1:]}*{label}" for label in generators),
            "remainder": "0",
            "runtime_sec": elapsed,
            "operation_hash": stable_hash(arguments),
            "backend": "sympy_agca_submodule_syzygy",
            "coefficient_domain": "QQ",
            "monomial_order": "lex",
            "lossless_reduction": ideal_request_profile(arguments),
            "_machine_certificate": {
                label: _term_payload(value, names) for label, value in multipliers.items()
            },
        }
    if not retained:
        return {
            "operation": IDEAL_OPERATION,
            "status": "NOT_PROVED",
            "validation_status": "passed",
            "evidence_status": "verified",
            "reason": "no nonzero generators remain after lossless reduction",
            "symbols": names,
            "target": symbolic.sstr(target.as_expr()),
            "generators": {
                label: symbolic.sstr(value.as_expr()) for label, value in generators.items()
            },
            "multipliers": {},
            "remainder": "unavailable",
            "runtime_sec": time.perf_counter() - started,
            "operation_hash": stable_hash(arguments),
            "backend": "sympy_agca_submodule_syzygy",
            "coefficient_domain": "QQ",
            "monomial_order": "lex",
            "lossless_reduction": ideal_request_profile(arguments),
        }
    ring = symbolic.QQ.old_poly_ring(*active_symbols, order="lex")
    module = ring.free_module(1).submodule(
        *([generator.as_expr()] for generator in retained.values()), order="lex"
    )
    try:
        representation = module.in_terms_of_generators([target.as_expr()])
    except (IndexError, ValueError) as error:
        return {
            "operation": IDEAL_OPERATION,
            "status": "NOT_PROVED",
            "validation_status": "passed",
            "evidence_status": "verified",
            "reason": f"no original-generator representation found: {type(error).__name__}",
            "symbols": names,
            "target": symbolic.sstr(target.as_expr()),
            "generators": {
                label: symbolic.sstr(value.as_expr()) for label, value in generators.items()
            },
            "multipliers": {},
            "remainder": "unavailable",
            "runtime_sec": time.perf_counter() - started,
            "operation_hash": stable_hash(arguments),
            "backend": "sympy_agca_submodule_syzygy",
            "coefficient_domain": "QQ",
            "monomial_order": "lex",
            "lossless_reduction": ideal_request_profile(arguments),
        }
    retained_multipliers = {
        label: symbolic.expand(ring.to_sympy(value))
        for label, value in zip(retained, representation, strict=True)
    }
    multipliers = {
        label: retained_multipliers.get(label, symbolic.Integer(0)) for label in generators
    }
    remainder = symbolic.Poly(
        symbolic.expand(
            target.as_expr()
            - sum(
                multipliers[label] * generators[label].as_expr()
                for label in generators
            )
        ),
        *symbol_map.values(),
    )
    elapsed = time.perf_counter() - started
    verified = remainder.is_zero
    return {
        "operation": IDEAL_OPERATION,
        "status": "PROVED" if verified else "BACKEND_MISMATCH",
        "validation_status": "passed" if verified else "failed",
        "evidence_status": "verified" if verified else "rejected",
        "reason": (
            "target equals the displayed original-generator combination over QQ"
            if verified
            else "independent exact expansion found a nonzero remainder"
        ),
        "symbols": names,
        "target": symbolic.sstr(target.as_expr()),
        "generators": {
            label: symbolic.sstr(value.as_expr()) for label, value in generators.items()
        },
        "multipliers": {label: symbolic.sstr(value) for label, value in multipliers.items()},
        "identity": "R = "
        + " + ".join(f"P{label[1:]}*{label}" for label in generators),
        "remainder": symbolic.sstr(remainder.as_expr()),
        "runtime_sec": elapsed,
        "operation_hash": stable_hash(arguments),
        "backend": "sympy_agca_submodule_syzygy",
        "coefficient_domain": "QQ",
        "monomial_order": "lex",
        "lossless_reduction": ideal_request_profile(arguments),
        "_machine_certificate": {
            label: _term_payload(value, names) for label, value in multipliers.items()
        },
    }


def _ideal_worker(connection: Any, arguments: Mapping[str, Any], memory_mb: int) -> None:
    try:
        memory_bytes = int(memory_mb) * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
        connection.send(("ok", _execute_ideal_membership_unbounded(arguments)))
    except BaseException as error:
        connection.send(("error", f"{type(error).__name__}: {error}"))
    finally:
        connection.close()


def _verify_cached_certificate(
    arguments: Mapping[str, Any], envelope: Mapping[str, Any], expected_key: str
) -> dict[str, Any]:
    if envelope.get("schema") != EXACT_CACHE_SCHEMA:
        raise ValueError("cache schema mismatch")
    if envelope.get("cache_key") != expected_key:
        raise ValueError("cache key mismatch")
    result = envelope.get("result")
    machine = envelope.get("machine_certificate")
    if not isinstance(result, Mapping) or result.get("status") != "PROVED":
        raise ValueError("cache does not contain a proved result")
    if not isinstance(machine, Mapping):
        raise ValueError("cache lacks a safe machine certificate")
    replay = _reexpand_machine_certificate(arguments, machine)
    replayed = dict(result)
    replayed["validation_status"] = "passed"
    replayed["evidence_status"] = "verified"
    replayed["remainder"] = "0"
    replayed["certificate_reexpanded"] = True
    replayed["machine_certificate_sha256"] = replay[
        "machine_certificate_sha256"
    ]
    replayed["cache"] = {
        "status": "verified_hit",
        "cache_key": expected_key,
        "certificate_reexpanded": True,
    }
    replayed["_machine_certificate"] = dict(machine)
    return replayed


def _write_verified_cache(
    path: Path,
    *,
    key: str,
    result: Mapping[str, Any],
    machine_certificate: Mapping[str, Any],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    envelope = {
        "schema": EXACT_CACHE_SCHEMA,
        "cache_key": key,
        "result": dict(result),
        "machine_certificate": dict(machine_certificate),
    }
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(envelope, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def execute_ideal_membership(
    arguments: Mapping[str, Any],
    *,
    timeout_sec: int = DEFAULT_IDEAL_TIMEOUT_SEC,
    memory_mb: int = DEFAULT_IDEAL_MEMORY_MB,
    cache_dir: Path | None = DEFAULT_CERTIFICATE_CACHE_DIR,
) -> dict[str, Any]:
    require_sympy()
    validate_ideal_arguments(arguments)
    if not 1 <= timeout_sec <= MAX_IDEAL_TIMEOUT_SEC:
        raise ValueError(
            f"ideal-membership timeout must be between 1 and {MAX_IDEAL_TIMEOUT_SEC} seconds"
        )
    if not 256 <= memory_mb <= 8192:
        raise ValueError("ideal-membership memory limit must be between 256 and 8192 MB")
    key = _cache_key(arguments)
    cache_path = None if cache_dir is None else Path(cache_dir).resolve() / f"{key}.json"
    invalid_cache_reason: str | None = None
    if cache_path is not None and cache_path.is_file():
        try:
            envelope = json.loads(cache_path.read_text(encoding="utf-8"))
            return _verify_cached_certificate(arguments, envelope, key)
        except Exception as error:
            invalid_cache_reason = f"{type(error).__name__}: {error}"
    context = multiprocessing.get_context("fork")
    receiving, sending = context.Pipe(duplex=False)
    process = context.Process(
        target=_ideal_worker,
        args=(sending, dict(arguments), memory_mb),
        daemon=True,
    )
    process.start()
    sending.close()
    try:
        if not receiving.poll(timeout_sec):
            process.terminate()
            process.join(timeout=5)
            raise TimeoutError(
                f"polynomial_ideal_membership exceeded {timeout_sec} seconds"
            )
        status, payload = receiving.recv()
    finally:
        receiving.close()
    process.join(timeout=5)
    if process.is_alive():
        process.terminate()
        process.join(timeout=5)
    if status != "ok":
        raise RuntimeError(f"polynomial_ideal_membership failed closed: {payload}")
    if not isinstance(payload, dict):
        raise RuntimeError("polynomial_ideal_membership returned a malformed result")
    machine_certificate = payload.pop("_machine_certificate", None)
    if payload.get("status") == "PROVED":
        if not isinstance(machine_certificate, Mapping):
            raise RuntimeError("proved ideal membership lacks a machine certificate")
        replay = _reexpand_machine_certificate(arguments, machine_certificate)
        if replay["multipliers"] != payload.get("multipliers"):
            raise RuntimeError("displayed and machine multipliers disagree")
        payload["certificate_reexpanded"] = True
        payload["machine_certificate_sha256"] = replay[
            "machine_certificate_sha256"
        ]
    else:
        payload["certificate_reexpanded"] = False
        if payload.get("status") == "NOT_PROVED":
            # This backend outcome is not a non-membership certificate.  The
            # computation was valid, but it supplies no proof evidence for the
            # requested ideal-membership claim.
            payload["evidence_status"] = "absent"
    payload["cache"] = {
        "status": "miss" if invalid_cache_reason is None else "invalid_entry_recomputed",
        "cache_key": key,
        "certificate_reexpanded": payload.get("certificate_reexpanded") is True,
        "invalid_entry_reason": invalid_cache_reason,
    }
    if (
        cache_path is not None
        and payload.get("status") == "PROVED"
        and payload.get("validation_status") == "passed"
        and isinstance(machine_certificate, Mapping)
    ):
        _write_verified_cache(
            cache_path,
            key=key,
            result=payload,
            machine_certificate=machine_certificate,
        )
        payload["cache"]["stored"] = True
        payload["cache"]["path"] = str(cache_path)
    if isinstance(machine_certificate, Mapping):
        payload["_machine_certificate"] = dict(machine_certificate)
    return payload


def execute(
    *,
    operation: str,
    arguments: Mapping[str, Any],
    claim: str,
    problem: v0220.Problem,
    run_id: str,
    exact_tool_timeout_sec: int = DEFAULT_IDEAL_TIMEOUT_SEC,
    exact_tool_memory_mb: int = DEFAULT_IDEAL_MEMORY_MB,
    certificate_cache_dir: Path | None = DEFAULT_CERTIFICATE_CACHE_DIR,
) -> dict[str, Any]:
    if operation == IDEAL_OPERATION:
        result = execute_ideal_membership(
            arguments,
            timeout_sec=exact_tool_timeout_sec,
            memory_mb=exact_tool_memory_mb,
            cache_dir=certificate_cache_dir,
        )
        machine_certificate = result.pop("_machine_certificate", None)
        return {
            "event_index": 1,
            "claim_id": "post_resolver_gap_1",
            "claim": claim,
            "operation": operation,
            "arguments": dict(arguments),
            "validation_status": result["validation_status"],
            "evidence_status": result["evidence_status"],
            "normalized_result": result,
            "certificate": {
                "kind": "original_generator_multiplier_identity",
                "multipliers": result.get("multipliers") or {},
                "identity": result.get("identity"),
                "exact_remainder": result.get("remainder"),
                "machine_multipliers": machine_certificate,
                "machine_certificate_sha256": result.get(
                    "machine_certificate_sha256"
                ),
                "certificate_reexpanded": result.get(
                    "certificate_reexpanded", False
                ),
            },
            "counterexample": None,
            "operation_hash": result["operation_hash"],
            "executor_code_hash": hashlib.sha256(
                execute_ideal_membership.__code__.co_code
            ).hexdigest(),
            "validator_code_hash": hashlib.sha256(
                validate_ideal_arguments.__code__.co_code
            ).hexdigest(),
        }
    if operation not in LEGACY_OPERATIONS:
        raise ValueError(f"operation is not exposed: {operation}")
    registry = v0221.build_registry((operation,))
    execution = v0220.execute_model_call(
        parsed={
            "valid": True,
            "call": {"operation": operation, "claim": claim, "arguments": dict(arguments)},
            "call_sha256": stable_hash(
                {"operation": operation, "claim": claim, "arguments": arguments}
            ),
        },
        problem=problem,
        run_id=run_id,
        event_index=1,
        registry=registry,
        timeout_sec=120,
        memory_mb=2048,
    )
    result = execution["execution"]
    return {
        "event_index": 1,
        "claim_id": "post_resolver_gap_1",
        "claim": claim,
        "operation": operation,
        "arguments": dict(arguments),
        "validation_status": str(result.get("validation_status") or "unknown"),
        "evidence_status": str(result.get("evidence_status") or "unknown"),
        "normalized_result": result.get("normalized_result"),
        "certificate": result.get("certificate"),
        "counterexample": result.get("counterexample"),
        "operation_hash": result.get("operation_hash"),
        "executor_code_hash": result.get("executor_code_hash"),
        "validator_code_hash": result.get("validator_code_hash"),
    }


def verify_target_evidence_event(
    event: Mapping[str, Any], *, full_legacy_replay: bool = False
) -> dict[str, Any]:
    """Independently decide whether an event is usable exact target evidence.

    Validator/evidence transport statuses alone are insufficient for operations
    with a one-sided prover.  In particular, ideal-membership ``NOT_PROVED``
    means only that this backend did not find a representation; it is neither a
    membership proof nor an exact non-membership certificate.
    """

    operation = str(event.get("operation") or "")
    if operation not in EXPOSED_OPERATIONS:
        raise ValueError("target event uses an unexposed operation")
    arguments = event.get("arguments")
    normalized = event.get("normalized_result")
    certificate = event.get("certificate")
    if not isinstance(arguments, Mapping):
        raise ValueError("target event arguments are missing")
    if not isinstance(normalized, Mapping):
        raise ValueError("target event normalized result is missing")
    if not isinstance(certificate, Mapping):
        raise ValueError("target event certificate is missing")
    if event.get("validation_status") != "passed":
        raise ValueError("target event did not pass independent validation")
    if event.get("evidence_status") != "verified":
        raise ValueError("target event does not contain verified proof evidence")

    if operation == IDEAL_OPERATION:
        if normalized.get("operation") != IDEAL_OPERATION:
            raise ValueError("ideal target result operation changed")
        if normalized.get("status") != "PROVED":
            raise ValueError("ideal target result is not an affirmative proof")
        if (
            normalized.get("validation_status") != "passed"
            or normalized.get("evidence_status") != "verified"
            or normalized.get("remainder") != "0"
            or normalized.get("certificate_reexpanded") is not True
        ):
            raise ValueError("ideal target result lacks re-expanded zero evidence")
        if (
            certificate.get("kind")
            != "original_generator_multiplier_identity"
            or certificate.get("exact_remainder") != "0"
            or certificate.get("certificate_reexpanded") is not True
        ):
            raise ValueError("ideal target event certificate is incomplete")
        machine = certificate.get("machine_multipliers")
        if not isinstance(machine, Mapping):
            raise ValueError("ideal target event lacks safe machine multipliers")
        replay = _reexpand_machine_certificate(arguments, machine)
        if (
            replay["multipliers"] != normalized.get("multipliers")
            or replay["multipliers"] != certificate.get("multipliers")
            or replay["machine_certificate_sha256"]
            != normalized.get("machine_certificate_sha256")
            or replay["machine_certificate_sha256"]
            != certificate.get("machine_certificate_sha256")
            or event.get("operation_hash") != stable_hash(arguments)
            or normalized.get("operation_hash") != stable_hash(arguments)
        ):
            raise ValueError("ideal target certificate binding changed")
        return {
            "usable": True,
            "operation": operation,
            "evidence_semantics": "affirmative_membership_proof",
            "status": "PROVED",
            "certificate_reexpanded": True,
            "exact_remainder": "0",
            "arguments_sha256": stable_hash(arguments),
            "machine_certificate_sha256": replay[
                "machine_certificate_sha256"
            ],
        }

    validated_arguments = v0221.validate_operation_arguments(operation, arguments)
    capability = v0221.build_registry((operation,)).get(operation)
    replayed_validation = capability.validate(
        dict(validated_arguments),
        {
            "normalized_result": dict(normalized),
            "certificate": dict(certificate),
        },
    )
    if replayed_validation.get("passed") is not True:
        raise ValueError("legacy target result failed operation-specific replay")
    expected_operation_hash = registry_operation_hash(
        {
            "operation": operation,
            "arguments": dict(validated_arguments),
            "assumptions": [],
            "backend_capability": capability.backend_capability,
            "validator": capability.validator_name,
        },
        backend_version=capability.backend_version,
        validator_version=capability.validator_version,
    )
    if event.get("operation_hash") != expected_operation_hash:
        raise ValueError("legacy target operation hash changed")
    if full_legacy_replay:
        replayed = execute(
            operation=operation,
            arguments=validated_arguments,
            claim=str(event.get("claim") or ""),
            problem=v0220.Problem(
                problem_id="target_evidence_replay",
                statement="deterministic target-evidence replay",
                source_path=Path(__file__).resolve(),
            ),
            run_id="target-evidence-replay",
            certificate_cache_dir=None,
        )
        for field in (
            "validation_status",
            "evidence_status",
            "normalized_result",
            "certificate",
            "counterexample",
            "operation_hash",
            "executor_code_hash",
            "validator_code_hash",
        ):
            if event.get(field) != replayed.get(field):
                raise ValueError(
                    f"legacy target event differs from bounded replay: {field}"
                )
    return {
        "usable": True,
        "operation": operation,
        "evidence_semantics": "independently_replayed_exact_result",
        "status": "VERIFIED",
        "certificate_reexpanded": None,
        "arguments_sha256": stable_hash(validated_arguments),
        "operation_hash": expected_operation_hash,
        "validator_version": capability.validator_version,
    }


def render_event(event: Mapping[str, Any]) -> str:
    result = event.get("normalized_result")
    certificate = event.get("certificate")
    counterexample = event.get("counterexample")
    visible_certificate = (
        {
            key: value
            for key, value in certificate.items()
            if key != "machine_multipliers"
        }
        if isinstance(certificate, Mapping)
        else certificate
    )
    result_lines = "\n".join(
        f"- {path}: {value}" for path, value in mdp.flatten_facts(result, "result")
    ) or "NONE"
    certificate_lines = "\n".join(
        f"- {path}: {value}"
        for path, value in mdp.flatten_facts(
            visible_certificate, "certificate"
        )
    ) or "NONE"
    counterexample_lines = (
        "NONE"
        if counterexample is None
        else "\n".join(
            f"- {path}: {value}"
            for path, value in mdp.flatten_facts(counterexample, "counterexample")
        )
    )
    return "\n".join(
        (
            "# Exact Tool Result",
            "",
            f"- Operation: {event['operation']}",
            f"- Requested fact: {event['claim']}",
            f"- Validation status: {event['validation_status']}",
            f"- Evidence status: {event['evidence_status']}",
            f"- Operation hash: {event['operation_hash']}",
            "",
            "## Normalized Result",
            "",
            result_lines,
            "",
            "## Exact Certificate",
            "",
            certificate_lines,
            "",
            "## Counterexample",
            "",
            counterexample_lines,
        )
    )
