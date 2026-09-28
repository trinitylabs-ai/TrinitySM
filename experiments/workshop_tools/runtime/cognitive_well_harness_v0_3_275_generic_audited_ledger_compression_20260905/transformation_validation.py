from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Mapping

import scripts.v0236_markdown_protocol as mdp
import scripts.run_v0221_gemma_constrained_tool_router_budget_20260904 as v0221
from cognitive_well_harness_v0_3_274_generic_compression_portfolio_bridge_20260905 import (
    exact_tools,
    protocol,
)

from . import singular_transformation_backend


GUARD_LABEL = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,63}$")
GUARD_FIELD = re.compile(r"^([a-z][a-z0-9_]*) = (.+)$")


def _render_ast(node: Any) -> str:
    if isinstance(node, int):
        return str(node)
    if not isinstance(node, Mapping) or len(node) != 1:
        raise ValueError("cannot render malformed guard AST")
    head, value = next(iter(node.items()))
    if head == "symbol":
        return f"(symbol {value})"
    if head == "rational":
        return f"(rational {value[0]} {value[1]})"
    if isinstance(value, list):
        return "(" + head + " " + " ".join(_render_ast(item) if isinstance(item, Mapping) else str(item) for item in value) + ")"
    return f"({head} {_render_ast(value)})"


def parse_guard_program(section: str) -> dict[str, Any]:
    """Parse typed division provenance and explicit source nonzero facts."""
    if section.strip() == "NONE":
        return {"provenance_divisions": {}, "source_nonzero": {}}
    body = mdp.fenced_body(
        "# Guard Program\n\n" + section.strip(), "guard-args", "Guard Program"
    )
    fields: dict[str, list[str]] = {}
    for line_number, line in enumerate(body.splitlines(), start=1):
        match = GUARD_FIELD.fullmatch(line)
        if match is None:
            raise ValueError(f"invalid guard-args line {line_number}")
        key, value = match.groups()
        fields.setdefault(key, []).append(value)
    if not set(fields) <= {"provenance_division", "source_nonzero"}:
        raise ValueError("guard program contains unsupported fields")
    divisions: dict[str, dict[str, Any]] = {}
    for raw in fields.get("provenance_division", []):
        parts = raw.split(" :: ")
        if len(parts) != 3:
            raise ValueError(
                "provenance division must use "
                "'label :: numerator :: denominator'"
            )
        label, numerator, denominator = parts
        if GUARD_LABEL.fullmatch(label) is None or label in divisions:
            raise ValueError("provenance division labels must be unique identifiers")
        divisions[label] = {
            "numerator": mdp.expression_ast(
                protocol._parse_sexpr_with_diagnostics(  # noqa: SLF001
                    numerator, field=f"provenance division {label} numerator"
                )
            ),
            "denominator": mdp.expression_ast(
                protocol._parse_sexpr_with_diagnostics(  # noqa: SLF001
                    denominator, field=f"provenance division {label} denominator"
                )
            ),
        }
    nonzero: dict[str, Any] = {}
    for raw in fields.get("source_nonzero", []):
        if " :: " not in raw:
            raise ValueError("source nonzero fact must use 'label :: expression'")
        label, expression = raw.split(" :: ", 1)
        if GUARD_LABEL.fullmatch(label) is None or label in nonzero:
            raise ValueError("source nonzero labels must be unique identifiers")
        nonzero[label] = mdp.expression_ast(
            protocol._parse_sexpr_with_diagnostics(  # noqa: SLF001
                expression, field=f"source nonzero {label}"
            )
        )
    if set(divisions) & set(nonzero):
        raise ValueError("guard program labels must be unique across all fields")
    if not divisions and not nonzero:
        raise ValueError("guard program fence is empty; use NONE")
    return {"provenance_divisions": divisions, "source_nonzero": nonzero}


def render_guard_program(program: Mapping[str, Any]) -> str:
    if not program["provenance_divisions"] and not program["source_nonzero"]:
        return "NONE"
    lines = []
    for label, row in program["provenance_divisions"].items():
        lines.append(
            "provenance_division = "
            f"{label} :: {_render_ast(row['numerator'])} :: "
            f"{_render_ast(row['denominator'])}"
        )
    for label, expression in program["source_nonzero"].items():
        lines.append(
            f"source_nonzero = {label} :: {_render_ast(expression)}"
        )
    return "```guard-args\n" + "\n".join(lines) + "\n```"


def _canonical(expression: Any, symbols: list[Any]) -> Any:
    symbolic = exact_tools.require_sympy()
    polynomial = symbolic.Poly(
        symbolic.expand(expression), *symbols, domain=symbolic.QQ
    )
    if polynomial.is_zero:
        return symbolic.Integer(0)
    return polynomial.monic().as_expr()


def derive_guards(
    program: Mapping[str, Any], source_arguments: Mapping[str, Any]
) -> dict[str, Any]:
    """Derive square-free guard factors deterministically from typed records."""
    symbolic = exact_tools.require_sympy()
    validated = exact_tools.validate_ideal_arguments(source_arguments)
    names = list(validated["symbols"])
    symbols = [validated["symbol_map"][name] for name in names]
    symbol_map = validated["symbol_map"]
    rows: dict[str, dict[str, Any]] = {}

    def add(expression: Any, source: str) -> None:
        polynomial = symbolic.Poly(
            symbolic.expand(expression), *symbols, domain=symbolic.QQ
        )
        if polynomial.is_zero:
            raise ValueError(f"zero cannot be a nonzero guard ({source})")
        if polynomial.total_degree() == 0:
            return
        _, factors = symbolic.factor_list(polynomial.as_expr(), *symbols)
        for factor, _ in factors:
            canonical = _canonical(factor, symbols)
            key = symbolic.srepr(canonical)
            rows.setdefault(
                key,
                {"expression": canonical, "sources": []},
            )["sources"].append(source)

    for label, row in program["provenance_divisions"].items():
        # Validate the numerator too, even though only the denominator creates
        # a guard.  This rejects undeclared symbols and unsafe AST operations.
        exact_tools._expression(row["numerator"], symbol_map)  # noqa: SLF001
        denominator = exact_tools._expression(  # noqa: SLF001
            row["denominator"], symbol_map
        )
        add(denominator, f"provenance_division.{label}.denominator")
    for label, node in program["source_nonzero"].items():
        add(
            exact_tools._expression(node, symbol_map),  # noqa: SLF001
            f"source_nonzero.{label}",
        )

    ordered = sorted(
        rows.values(), key=lambda row: symbolic.srepr(row["expression"])
    )
    return {
        "expressions": [row["expression"] for row in ordered],
        "records": [
            {
                "label": f"G{index}",
                "expression": symbolic.sstr(row["expression"]),
                "sources": sorted(set(row["sources"])),
            }
            for index, row in enumerate(ordered, start=1)
        ],
    }


def _polynomial_ast(expression: Any, names: list[str]) -> Any:
    symbolic = exact_tools.require_sympy()
    symbols = [symbolic.Symbol(name) for name in names]
    polynomial = symbolic.Poly(
        symbolic.expand(expression), *symbols, domain=symbolic.QQ
    )
    terms: list[Any] = []
    for powers, coefficient in polynomial.terms():
        value = symbolic.Rational(coefficient)
        factors: list[Any] = []
        if value != 1 or not any(powers):
            factors.append(
                int(value.p)
                if value.q == 1
                else {"rational": [int(value.p), int(value.q)]}
            )
        for name, power in zip(names, powers, strict=True):
            if power == 0:
                continue
            symbol: Any = {"symbol": name}
            factors.append(symbol if power == 1 else {"pow": [symbol, power]})
        terms.append(factors[0] if len(factors) == 1 else {"mul": factors})
    if not terms:
        return 0
    return terms[0] if len(terms) == 1 else {"add": terms}


def _embedded_polynomial(
    expression: Any, source_symbols: list[Any]
) -> Any:
    symbolic = exact_tools.require_sympy()
    return symbolic.Poly(
        symbolic.expand(expression), *source_symbols, domain=symbolic.QQ
    )


def _localized_singular_inputs(
    *,
    source: Mapping[str, Any],
    candidate: Mapping[str, Any],
    guards: Mapping[str, Any],
) -> dict[str, Any]:
    symbolic = exact_tools.require_sympy()
    source_names = list(source["symbols"])
    source_symbols = [source["symbol_map"][name] for name in source_names]
    execution_names = list(source_names)
    generator_nodes = {
        label: _polynomial_ast(polynomial.as_expr(), source_names)
        for label, polynomial in source["generators"].items()
    }
    if guards["expressions"]:
        auxiliary = "guard_inverse"
        suffix = 1
        while auxiliary in execution_names:
            suffix += 1
            auxiliary = f"guard_inverse_{suffix}"
        execution_names.append(auxiliary)
        guard_product = symbolic.prod(guards["expressions"])
        generator_nodes["D_guard_localization"] = _polynomial_ast(
            1 - symbolic.Symbol(auxiliary) * guard_product,
            execution_names,
        )
        generator_nodes.update(
            {
                label: _polynomial_ast(polynomial.as_expr(), execution_names)
                for label, polynomial in source["generators"].items()
            }
        )
    execution_symbol_map = {
        name: symbolic.Symbol(name) for name in execution_names
    }
    return {
        "source_symbols": [execution_symbol_map[name] for name in execution_names],
        "source_generators": [
            (
                label,
                exact_tools._expression(node, execution_symbol_map),  # noqa: SLF001
            )
            for label, node in generator_nodes.items()
        ],
        "candidate_generators": [
            (
                label,
                symbolic.Poly(
                    polynomial.as_expr(),
                    *source_symbols,
                    domain=symbolic.QQ,
                ).as_expr(),
            )
            for label, polynomial in candidate["generators"].items()
        ],
    }


def _validate_ideal_transformation(
    *,
    source_arguments: Mapping[str, Any],
    candidate_arguments: Mapping[str, Any],
    guard_program: Mapping[str, Any],
    timeout_sec: int,
    memory_mb: int,
    singular_binary: Path,
    artifact_dir: Path,
) -> dict[str, Any]:
    """Exact source-to-candidate validation for polynomial-ideal reductions."""
    symbolic = exact_tools.require_sympy()
    source = exact_tools.validate_ideal_arguments(source_arguments)
    candidate = exact_tools.validate_ideal_arguments(candidate_arguments)
    source_names = list(source["symbols"])
    candidate_names = list(candidate["symbols"])
    new_symbols = sorted(set(candidate_names) - set(source_names))
    guards = derive_guards(guard_program, source_arguments)
    base = {
        "schema": "cognitive-well-v0275-exact-transformation-validation-v1",
        "method": "guard_localized_singular_original_generator_lift",
        "source_arguments_sha256": exact_tools.stable_hash(source_arguments),
        "candidate_arguments_sha256": exact_tools.stable_hash(candidate_arguments),
        "guard_program_sha256": exact_tools.stable_hash(guard_program),
        "source_symbol_count": len(source_names),
        "candidate_symbol_count": len(candidate_names),
        "derived_guard_count": len(guards["expressions"]),
        "derived_guards": guards["records"],
        "new_candidate_symbols": new_symbols,
    }
    if new_symbols:
        return {
            **base,
            "decision": "REJECT",
            "reason": "new candidate symbols require typed source bindings",
            "target_correspondence": "NOT_CHECKED",
            "generator_checks": [],
        }

    source_symbols = [source["symbol_map"][name] for name in source_names]
    source_target = _embedded_polynomial(source["target"].as_expr(), source_symbols)
    candidate_target = _embedded_polynomial(
        candidate["target"].as_expr(), source_symbols
    )
    target_matches = (
        source_target.is_zero and candidate_target.is_zero
    ) or (
        not source_target.is_zero
        and not candidate_target.is_zero
        and source_target.monic() == candidate_target.monic()
    )
    if not target_matches:
        return {
            **base,
            "decision": "REJECT",
            "reason": "candidate target is not a nonzero rational multiple of the source target",
            "target_correspondence": "REJECT",
            "generator_checks": [],
        }

    singular_inputs = _localized_singular_inputs(
        source=source, candidate=candidate, guards=guards
    )
    backend = singular_transformation_backend.validate_consequences(
        source_symbols=singular_inputs["source_symbols"],
        source_generators=singular_inputs["source_generators"],
        candidate_generators=singular_inputs["candidate_generators"],
        binary=singular_binary,
        timeout_sec=timeout_sec,
        memory_mb=memory_mb,
        input_binding={
            "operation": exact_tools.IDEAL_OPERATION,
            "source_arguments_sha256": base["source_arguments_sha256"],
            "candidate_arguments_sha256": base["candidate_arguments_sha256"],
            "guard_program_sha256": base["guard_program_sha256"],
            "target_correspondence": "ACCEPT",
        },
        output_dir=artifact_dir,
    )
    backend_status = backend["status"]
    if backend_status == "INCONSISTENT":
        return {
            **base,
            "decision": "REJECT",
            "reason": "derived guards are inconsistent with the source equations",
            "target_correspondence": "ACCEPT",
            "source_localization_consistency": "REJECT",
            "generator_checks": [],
            "singular_backend": backend,
        }
    if backend_status == "INCONCLUSIVE":
        return {
            **base,
            "decision": "INCONCLUSIVE",
            "reason": "bounded Singular source-to-candidate validation was inconclusive",
            "target_correspondence": "ACCEPT",
            "source_localization_consistency": "INCONCLUSIVE",
            "generator_checks": [],
            "singular_backend": backend,
        }
    if backend_status != "PROVED":
        return {
            **base,
            "decision": "REJECT",
            "reason": backend["reason"],
            "target_correspondence": "ACCEPT",
            "source_localization_consistency": "ACCEPT",
            "generator_checks": backend["generator_checks"],
            "singular_backend": backend,
        }
    return {
        **base,
        "decision": "ACCEPT",
        "reason": (
            "every candidate generator has a bounded Singular lift whose "
            "original-source multiplier identity re-expands exactly"
        ),
        "target_correspondence": "ACCEPT",
        "source_localization_consistency": "ACCEPT",
        "generator_checks": backend["generator_checks"],
        "singular_backend": backend,
    }


def _guard_program_is_empty(program: Mapping[str, Any]) -> bool:
    """Require the exact parsed guard-program shape for non-ideal operations."""

    if set(program) != {"provenance_divisions", "source_nonzero"}:
        raise ValueError("guard program has unexpected fields")
    divisions = program["provenance_divisions"]
    source_nonzero = program["source_nonzero"]
    if not isinstance(divisions, Mapping) or not isinstance(source_nonzero, Mapping):
        raise ValueError("guard program fields must be mappings")
    return not divisions and not source_nonzero


def _validate_legacy_transformation(
    *,
    operation: str,
    source_arguments: Mapping[str, Any],
    candidate_arguments: Mapping[str, Any],
    guard_program: Mapping[str, Any],
) -> dict[str, Any]:
    """Fail closed unless a legacy request is canonically identical.

    The frozen operation validators establish that both requests are safe and
    well-typed.  They do not provide source-to-candidate equivalence theorems for
    constraint deletion, domain changes, variable elimination, or branch changes.
    Consequently canonical identity is the only generic exact contract available
    here.  A non-identical request is recorded as INCONCLUSIVE rather than being
    misrouted through the polynomial-ideal validator.
    """

    if operation not in exact_tools.LEGACY_OPERATIONS:
        raise ValueError(f"operation is not exposed: {operation}")
    source = v0221.validate_operation_arguments(operation, source_arguments)
    candidate = v0221.validate_operation_arguments(operation, candidate_arguments)
    source_hash = exact_tools.stable_hash(source)
    candidate_hash = exact_tools.stable_hash(candidate)
    guards_empty = _guard_program_is_empty(guard_program)
    base = {
        "schema": "cognitive-well-v0275-exact-transformation-validation-v2",
        "operation": operation,
        "method": "validated_canonical_argument_identity",
        "source_arguments_validated": True,
        "candidate_arguments_validated": True,
        "source_arguments_sha256": source_hash,
        "candidate_arguments_sha256": candidate_hash,
        "guard_program_empty": guards_empty,
        "derived_guard_count": 0,
        "derived_guards": [],
        "generator_checks": [],
    }
    if not guards_empty:
        return {
            **base,
            "decision": "INCONCLUSIVE",
            "reason": (
                "the declared operation has no exact guard-derivation contract; "
                "nonempty guards cannot be certified generically"
            ),
            "target_correspondence": "NOT_CHECKED",
        }
    if source_hash == candidate_hash:
        return {
            **base,
            "decision": "ACCEPT",
            "reason": (
                "source and candidate arguments are identical after the frozen "
                "operation validator"
            ),
            "target_correspondence": "ACCEPT",
        }
    return {
        **base,
        "decision": "INCONCLUSIVE",
        "reason": (
            "the declared operation has no sound generic exact transformation "
            "contract for non-identical validated arguments"
        ),
        "target_correspondence": "NOT_CHECKED",
    }


def validate_transformation(
    *,
    source_arguments: Mapping[str, Any],
    candidate_arguments: Mapping[str, Any],
    guard_program: Mapping[str, Any],
    timeout_sec: int,
    memory_mb: int,
    operation: str = exact_tools.IDEAL_OPERATION,
    singular_binary: Path | None = None,
    artifact_dir: Path | None = None,
) -> dict[str, Any]:
    """Dispatch exact transformation validation by the declared operation.

    Polynomial ideal membership retains the guarded consequence checker.  Every
    legacy operation is first passed through its frozen argument validator and is
    accepted only under the exact canonical-identity contract.  Unsupported
    non-identity transformations remain explicitly fail closed.
    """

    if operation == exact_tools.IDEAL_OPERATION:
        if singular_binary is None:
            singular_binary = (
                Path(__file__).resolve().parents[1]
                / ".tools/singular-4.2.1/singular"
            )
        if artifact_dir is None:
            raise ValueError(
                "ideal transformation validation requires a persistent artifact directory"
            )
        result = _validate_ideal_transformation(
            source_arguments=source_arguments,
            candidate_arguments=candidate_arguments,
            guard_program=guard_program,
            timeout_sec=timeout_sec,
            memory_mb=memory_mb,
            singular_binary=singular_binary.resolve(),
            artifact_dir=artifact_dir.resolve(),
        )
        return {**result, "operation": operation}
    return _validate_legacy_transformation(
        operation=operation,
        source_arguments=source_arguments,
        candidate_arguments=candidate_arguments,
        guard_program=guard_program,
    )


def verify_singular_certificate(
    *,
    source_arguments: Mapping[str, Any],
    candidate_arguments: Mapping[str, Any],
    guard_program: Mapping[str, Any],
    validation: Mapping[str, Any],
    singular_binary: Path,
    artifact_dir: Path,
) -> dict[str, Any]:
    """Replay a promoted ideal transformation certificate without rerunning CAS."""

    source = exact_tools.validate_ideal_arguments(source_arguments)
    candidate = exact_tools.validate_ideal_arguments(candidate_arguments)
    guards = derive_guards(guard_program, source_arguments)
    source_names = list(source["symbols"])
    candidate_names = list(candidate["symbols"])
    source_symbols = [source["symbol_map"][name] for name in source_names]
    source_target = _embedded_polynomial(source["target"].as_expr(), source_symbols)
    candidate_target = _embedded_polynomial(
        candidate["target"].as_expr(), source_symbols
    )
    target_matches = (
        source_target.is_zero and candidate_target.is_zero
    ) or (
        not source_target.is_zero
        and not candidate_target.is_zero
        and source_target.monic() == candidate_target.monic()
    )
    expected_top = {
        "schema": "cognitive-well-v0275-exact-transformation-validation-v1",
        "method": "guard_localized_singular_original_generator_lift",
        "operation": exact_tools.IDEAL_OPERATION,
        "decision": "ACCEPT",
        "source_arguments_sha256": exact_tools.stable_hash(source_arguments),
        "candidate_arguments_sha256": exact_tools.stable_hash(candidate_arguments),
        "guard_program_sha256": exact_tools.stable_hash(guard_program),
        "source_symbol_count": len(source_names),
        "candidate_symbol_count": len(candidate_names),
        "derived_guard_count": len(guards["expressions"]),
        "derived_guards": guards["records"],
        "new_candidate_symbols": sorted(set(candidate_names) - set(source_names)),
        "target_correspondence": "ACCEPT",
        "source_localization_consistency": "ACCEPT",
    }
    for field, expected in expected_top.items():
        if validation.get(field) != expected:
            raise ValueError(f"Singular transformation binding changed: {field}")
    if expected_top["new_candidate_symbols"] or not target_matches:
        raise ValueError("Singular transformation is not replayably eligible")
    backend = validation.get("singular_backend")
    if not isinstance(backend, Mapping):
        raise ValueError("Singular transformation backend result is missing")
    singular_inputs = _localized_singular_inputs(
        source=source, candidate=candidate, guards=guards
    )
    input_binding = {
        "operation": exact_tools.IDEAL_OPERATION,
        "source_arguments_sha256": expected_top["source_arguments_sha256"],
        "candidate_arguments_sha256": expected_top["candidate_arguments_sha256"],
        "guard_program_sha256": expected_top["guard_program_sha256"],
        "target_correspondence": "ACCEPT",
    }
    replay = singular_transformation_backend.verify_proved_result(
        result=backend,
        source_symbols=singular_inputs["source_symbols"],
        source_generators=singular_inputs["source_generators"],
        candidate_generators=singular_inputs["candidate_generators"],
        binary=singular_binary.resolve(),
        input_binding=input_binding,
        artifact_dir=artifact_dir.resolve(),
    )
    if validation.get("generator_checks") != backend.get("generator_checks"):
        raise ValueError("Singular top-level generator ledger changed")
    return {
        "verified": True,
        "validation_sha256": exact_tools.stable_hash(validation),
        "backend_operation_hash": replay["operation_hash"],
        "backend_certificate_sha256": replay["certificate_sha256"],
        "generator_identity_count": replay["generator_identity_count"],
    }


def verify_singular_outcome(
    *,
    source_arguments: Mapping[str, Any],
    candidate_arguments: Mapping[str, Any],
    guard_program: Mapping[str, Any],
    validation: Mapping[str, Any],
    singular_binary: Path,
    artifact_dir: Path,
) -> dict[str, Any]:
    """Replay any persisted ideal exact-validation terminal outcome."""

    source = exact_tools.validate_ideal_arguments(source_arguments)
    candidate = exact_tools.validate_ideal_arguments(candidate_arguments)
    guards = derive_guards(guard_program, source_arguments)
    source_names = list(source["symbols"])
    candidate_names = list(candidate["symbols"])
    new_symbols = sorted(set(candidate_names) - set(source_names))
    source_symbols = [source["symbol_map"][name] for name in source_names]
    source_target = _embedded_polynomial(source["target"].as_expr(), source_symbols)
    if new_symbols:
        target_matches = False
    else:
        candidate_target = _embedded_polynomial(
            candidate["target"].as_expr(), source_symbols
        )
        target_matches = (
            source_target.is_zero and candidate_target.is_zero
        ) or (
            not source_target.is_zero
            and not candidate_target.is_zero
            and source_target.monic() == candidate_target.monic()
        )
    backend = validation.get("singular_backend")
    if not isinstance(backend, Mapping):
        base = {
            "schema": "cognitive-well-v0275-exact-transformation-validation-v1",
            "method": "guard_localized_singular_original_generator_lift",
            "operation": exact_tools.IDEAL_OPERATION,
            "source_arguments_sha256": exact_tools.stable_hash(source_arguments),
            "candidate_arguments_sha256": exact_tools.stable_hash(candidate_arguments),
            "guard_program_sha256": exact_tools.stable_hash(guard_program),
            "source_symbol_count": len(source_names),
            "candidate_symbol_count": len(candidate_names),
            "derived_guard_count": len(guards["expressions"]),
            "derived_guards": guards["records"],
            "new_candidate_symbols": new_symbols,
        }
        if new_symbols:
            expected = {
                **base,
                "decision": "REJECT",
                "reason": "new candidate symbols require typed source bindings",
                "target_correspondence": "NOT_CHECKED",
                "generator_checks": [],
            }
        elif not target_matches:
            expected = {
                **base,
                "decision": "REJECT",
                "reason": "candidate target is not a nonzero rational multiple of the source target",
                "target_correspondence": "REJECT",
                "generator_checks": [],
            }
        else:
            raise ValueError("eligible Singular transformation backend result is missing")
        if dict(validation) != expected:
            raise ValueError("deterministic pre-Singular rejection changed")
        return {
            "verified": True,
            "status": "PRE_SINGULAR_REJECT",
            "validation_sha256": exact_tools.stable_hash(validation),
        }
    if backend.get("status") == "PROVED":
        return verify_singular_certificate(
            source_arguments=source_arguments,
            candidate_arguments=candidate_arguments,
            guard_program=guard_program,
            validation=validation,
            singular_binary=singular_binary,
            artifact_dir=artifact_dir,
        )
    if not target_matches or new_symbols:
        raise ValueError("Singular closed outcome is not replayably eligible")
    status = str(backend.get("status"))
    expected_decision = {
        "NOT_PROVED": "REJECT",
        "INCONSISTENT": "REJECT",
        "INCONCLUSIVE": "INCONCLUSIVE",
    }.get(status)
    expected_consistency = {
        "NOT_PROVED": "ACCEPT",
        "INCONSISTENT": "REJECT",
        "INCONCLUSIVE": "INCONCLUSIVE",
    }.get(status)
    if expected_decision is None:
        raise ValueError("unsupported Singular exact-validation outcome")
    expected_fields = {
        "schema": "cognitive-well-v0275-exact-transformation-validation-v1",
        "method": "guard_localized_singular_original_generator_lift",
        "operation": exact_tools.IDEAL_OPERATION,
        "decision": expected_decision,
        "source_arguments_sha256": exact_tools.stable_hash(source_arguments),
        "candidate_arguments_sha256": exact_tools.stable_hash(candidate_arguments),
        "guard_program_sha256": exact_tools.stable_hash(guard_program),
        "source_symbol_count": len(source_names),
        "candidate_symbol_count": len(candidate_names),
        "derived_guard_count": len(guards["expressions"]),
        "derived_guards": guards["records"],
        "new_candidate_symbols": [],
        "target_correspondence": "ACCEPT",
        "source_localization_consistency": expected_consistency,
        "generator_checks": backend.get("generator_checks"),
    }
    for field, expected in expected_fields.items():
        if validation.get(field) != expected:
            raise ValueError(f"Singular closed transformation changed: {field}")
    singular_inputs = _localized_singular_inputs(
        source=source, candidate=candidate, guards=guards
    )
    input_binding = {
        "operation": exact_tools.IDEAL_OPERATION,
        "source_arguments_sha256": expected_fields["source_arguments_sha256"],
        "candidate_arguments_sha256": expected_fields["candidate_arguments_sha256"],
        "guard_program_sha256": expected_fields["guard_program_sha256"],
        "target_correspondence": "ACCEPT",
    }
    replay = singular_transformation_backend.verify_closed_result(
        result=backend,
        source_symbols=singular_inputs["source_symbols"],
        source_generators=singular_inputs["source_generators"],
        candidate_generators=singular_inputs["candidate_generators"],
        binary=singular_binary.resolve(),
        input_binding=input_binding,
        artifact_dir=artifact_dir.resolve(),
    )
    return {
        "verified": True,
        "status": replay["status"],
        "validation_sha256": exact_tools.stable_hash(validation),
        "backend_operation_hash": replay["operation_hash"],
    }
