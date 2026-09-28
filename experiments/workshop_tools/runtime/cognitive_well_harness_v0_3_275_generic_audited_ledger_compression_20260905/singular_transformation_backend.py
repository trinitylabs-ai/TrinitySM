from __future__ import annotations

import hashlib
import json
import os
import re
import resource
import signal
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Mapping

import sympy as sp

from cognitive_well_harness_v0_3_274_generic_compression_portfolio_bridge_20260905 import (
    exact_tools,
)


BACKEND_SCHEMA = "cognitive-well-v0275-singular-transformation-certificate-v1"
BACKEND_NAME = "singular_liftstd_original_generator_certificate"
MAX_STDOUT_BYTES = 64 * 1024 * 1024
MARKER = re.compile(r"^RESULT_([A-Z0-9_]+)=(.*)$")


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def _singular_expression(expression: sp.Expr) -> str:
    return sp.sstr(sp.expand(expression)).replace("**", "^")


def _backend_symbols(symbols: list[sp.Symbol]) -> list[sp.Symbol]:
    """Use delimiter-bearing names so redSB output stays unambiguous."""

    return [sp.Symbol(f"v{index}_") for index in range(len(symbols))]


def _terminate_process_group(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=2)
        return
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait(timeout=5)


def _run_program(
    *, program: str, binary: Path, timeout_sec: int, memory_mb: int
) -> dict[str, Any]:
    """Run one Singular program in a bounded, killable process group."""

    if not 1 <= timeout_sec <= 6_000:
        raise ValueError("Singular timeout must be between 1 and 6000 seconds")
    if not 256 <= memory_mb <= 8192:
        raise ValueError("Singular memory limit must be between 256 and 8192 MB")
    executable = binary.resolve()
    if not executable.is_file():
        raise FileNotFoundError(executable)

    def limit_memory() -> None:
        limit = int(memory_mb) * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (limit, limit))

    started = time.monotonic()
    with tempfile.TemporaryFile(mode="w+b") as output:
        process = subprocess.Popen(
            [str(executable), "-q"],
            stdin=subprocess.PIPE,
            stdout=output,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            preexec_fn=limit_memory,
        )
        timed_out = False
        try:
            process.communicate(program.encode("utf-8"), timeout=timeout_sec)
        except subprocess.TimeoutExpired:
            timed_out = True
            _terminate_process_group(process)
        elapsed = round(time.monotonic() - started, 6)
        output.flush()
        size = output.tell()
        if size > MAX_STDOUT_BYTES:
            raise RuntimeError(
                f"Singular output exceeded {MAX_STDOUT_BYTES} bytes"
            )
        output.seek(0)
        stdout = output.read().decode("utf-8", errors="replace")
    if timed_out:
        return {
            "status": "TIMEOUT",
            "runtime_sec": elapsed,
            "returncode": process.returncode,
            "stdout": stdout,
        }
    singular_error = any(
        line.lstrip().startswith("?") or line.lstrip().startswith("// **")
        for line in stdout.splitlines()
    )
    return {
        "status": (
            "COMPLETED"
            if process.returncode == 0 and not singular_error
            else "ERROR"
        ),
        "runtime_sec": elapsed,
        "returncode": process.returncode,
        "stdout": stdout,
    }


def _markers(stdout: str) -> dict[str, str]:
    rows: dict[str, str] = {}
    for line in stdout.splitlines():
        match = MARKER.fullmatch(line.strip())
        if match is None:
            continue
        key, value = match.groups()
        if key in rows:
            raise ValueError(f"duplicate Singular marker RESULT_{key}")
        rows[key] = value
    return rows


def _parse_compact_monomial(raw: str, symbols: list[sp.Symbol]) -> sp.Expr:
    """Parse Singular redSB's compact monomial syntax, or reject ambiguity.

    With ordinary ring names Singular may serialize ``x^2*y*u^7`` as
    ``x2yu7``.  Tokenization is derived solely from the declared ring symbols
    and their order.  All possible canonical tokenizations are considered and
    accepted only when they produce one exact monomial.
    """

    names = [str(symbol) for symbol in symbols]
    memo: dict[tuple[int, int], tuple[tuple[tuple[int, int], ...], ...]] = {}

    def parse_from(position: int, minimum_index: int) -> tuple[tuple[tuple[int, int], ...], ...]:
        key = (position, minimum_index)
        if key in memo:
            return memo[key]
        if position == len(raw):
            return ((),)
        results: set[tuple[tuple[int, int], ...]] = set()
        for index in range(minimum_index, len(names)):
            name = names[index]
            if not raw.startswith(name, position):
                continue
            exponent_start = position + len(name)
            exponent_choices = [(exponent_start, 1)]
            exponent_end = exponent_start
            while exponent_end < len(raw) and raw[exponent_end].isdigit():
                exponent_end += 1
                exponent = int(raw[exponent_start:exponent_end])
                if exponent >= 2:
                    exponent_choices.append((exponent_end, exponent))
            for next_position, exponent in exponent_choices:
                for suffix in parse_from(next_position, index + 1):
                    results.add(((index, exponent),) + suffix)
                    if len(results) > 1:
                        # More than one exponent vector is an ambiguous exact
                        # serialization; do not guess which one Singular meant.
                        memo[key] = tuple(results)
                        return memo[key]
        memo[key] = tuple(results)
        return memo[key]

    parses = parse_from(0, 0)
    if len(parses) != 1:
        raise ValueError("Singular compact monomial is unknown or ambiguous")
    expression = sp.Integer(1)
    for index, exponent in parses[0]:
        expression *= symbols[index] ** exponent
    return expression


def _parse_compact_polynomial(raw: str, symbols: list[sp.Symbol]) -> sp.Expr:
    compact = "".join(raw.split())
    if compact == "0":
        return sp.Integer(0)
    terms = re.findall(r"[+-]?[^+-]+", compact)
    if not terms or "".join(terms) != compact:
        raise ValueError("Singular compact polynomial has invalid term boundaries")
    expression = sp.Integer(0)
    for term in terms:
        sign = -1 if term.startswith("-") else 1
        body = term[1:] if term[:1] in {"+", "-"} else term
        coefficient_match = re.match(r"^(\d+(?:/\d+)?)", body)
        if coefficient_match is None:
            coefficient = sp.Integer(1)
            monomial = body
        else:
            coefficient = sp.Rational(coefficient_match.group(1))
            monomial = body[coefficient_match.end() :]
        if not monomial:
            expression += sign * coefficient
        else:
            expression += sign * coefficient * _parse_compact_monomial(
                monomial, symbols
            )
    return expression


def _parse_polynomial(raw: str, symbols: list[sp.Symbol]) -> sp.Expr:
    if len(raw) > 8 * 1024 * 1024:
        raise ValueError("Singular multiplier exceeds the parse bound")
    aliases = _backend_symbols(symbols)
    contains_backend_alias = any(str(alias) in raw for alias in aliases)
    if not contains_backend_alias and not any(
        token in raw for token in ("*", "^", "(", ")")
    ) and re.fullmatch(
        r"[A-Za-z0-9_+\-/\s]+", raw
    ):
        expression = _parse_compact_polynomial(raw, symbols)
        return sp.Poly(sp.expand(expression), *symbols, domain=sp.QQ).as_expr()
    names = {str(symbol): symbol for symbol in symbols}
    names.update({str(alias): alias for alias in aliases})
    try:
        expression = sp.sympify(raw.replace("^", "**"), locals=names)
        if not expression.free_symbols.issubset(set(symbols) | set(aliases)):
            if any(token in raw for token in ("*", "^", "(", ")")):
                raise ValueError("Singular polynomial contains an undeclared symbol")
            expression = _parse_compact_polynomial(raw, symbols)
        expression = expression.xreplace(dict(zip(aliases, symbols, strict=True)))
    except (sp.SympifyError, SyntaxError, TypeError):
        expression = _parse_compact_polynomial(raw, symbols)
    return sp.Poly(sp.expand(expression), *symbols, domain=sp.QQ).as_expr()


def _build_program(
    *,
    source_symbols: list[sp.Symbol],
    source_generators: list[tuple[str, sp.Expr]],
    candidate_generators: list[tuple[str, sp.Expr]],
) -> str:
    backend_symbols = _backend_symbols(source_symbols)
    names = [str(symbol) for symbol in backend_symbols]
    to_backend = dict(zip(source_symbols, backend_symbols, strict=True))
    lines = [
        "option(redSB);",
        f"ring R=0,({','.join(names)}),dp;",
    ]
    source_names: list[str] = []
    for index, (_, expression) in enumerate(source_generators, start=1):
        name = f"source_{index}"
        source_names.append(name)
        lines.append(
            f"poly {name}={_singular_expression(expression.xreplace(to_backend))};"
        )
    candidate_names: list[str] = []
    for index, (_, expression) in enumerate(candidate_generators, start=1):
        name = f"candidate_{index}"
        candidate_names.append(name)
        lines.append(
            f"poly {name}={_singular_expression(expression.xreplace(to_backend))};"
        )
    lines.extend(
        [
            f"ideal J={','.join(source_names)};",
            "matrix source_to_std;",
            "int started=timer;",
            "ideal G=liftstd(J,source_to_std);",
            "poly consistency_remainder=reduce(1,G);",
            'print("RESULT_CONSISTENCY_REMAINDER="+string(consistency_remainder));',
            'if (consistency_remainder==0) { print("RESULT_CONSISTENCY=INCONSISTENT"); }',
            'else { print("RESULT_CONSISTENCY=CONSISTENT"); }',
            "int all_proved=1;",
        ]
    )
    for index, name in enumerate(candidate_names, start=1):
        lines.extend(
            [
                f"poly candidate_remainder_{index}=reduce({name},G);",
                f'print("RESULT_GENERATOR_{index}_REMAINDER="+'
                f"string(candidate_remainder_{index}));",
                f'if (candidate_remainder_{index}==0) '
                f'{{ print("RESULT_GENERATOR_{index}=PROVED"); }} '
                f'else {{ print("RESULT_GENERATOR_{index}=NOT_PROVED"); '
                "all_proved=0; }",
            ]
        )
    if candidate_names:
        lines.extend(
            [
                "if (all_proved==1)",
                "{",
                f"  ideal T={','.join(candidate_names)};",
                "  module std_to_candidate=lift(G,T);",
                "  matrix source_to_candidate=source_to_std*std_to_candidate;",
            ]
        )
        for candidate_index in range(1, len(candidate_names) + 1):
            for source_index in range(1, len(source_names) + 1):
                lines.append(
                    "  print(\"RESULT_MULTIPLIER_"
                    f"{candidate_index}_{source_index}=\"+"
                    f"string(source_to_candidate[{source_index},{candidate_index}]));"
                )
        lines.append("}")
    lines.extend(
        [
            'print("RESULT_RUNTIME_TICKS="+string(timer-started));',
            'print("RESULT_DONE=1");',
            "exit;",
        ]
    )
    return "\n".join(lines) + "\n"


def _operation_hash(
    *,
    input_binding: Mapping[str, Any],
    source_generators: list[tuple[str, sp.Expr]],
    candidate_generators: list[tuple[str, sp.Expr]],
    program_sha256: str,
    singular_binary_sha256: str,
) -> str:
    return exact_tools.stable_hash(
        {
            "schema": BACKEND_SCHEMA,
            "backend": BACKEND_NAME,
            "input_binding": dict(input_binding),
            "source_generators": [
                [label, sp.srepr(sp.expand(expression))]
                for label, expression in source_generators
            ],
            "candidate_generators": [
                [label, sp.srepr(sp.expand(expression))]
                for label, expression in candidate_generators
            ],
            "program_sha256": program_sha256,
            "singular_binary_sha256": singular_binary_sha256,
        }
    )


def verify_proved_result(
    *,
    result: Mapping[str, Any],
    source_symbols: list[sp.Symbol],
    source_generators: list[tuple[str, sp.Expr]],
    candidate_generators: list[tuple[str, sp.Expr]],
    binary: Path,
    input_binding: Mapping[str, Any],
    artifact_dir: Path,
) -> dict[str, Any]:
    """Replay every persisted hash and multiplier identity without Singular."""

    if (
        result.get("schema") != BACKEND_SCHEMA
        or result.get("backend") != BACKEND_NAME
        or result.get("status") != "PROVED"
        or result.get("process_status") != "COMPLETED"
        or result.get("source_consistency") != "CONSISTENT"
        or result.get("certificate_reexpanded") is not True
    ):
        raise ValueError("Singular proved-result boundary changed")
    if result.get("input_binding") != dict(input_binding):
        raise ValueError("Singular input binding changed")
    expected_program = (artifact_dir.resolve() / "singular_program.sing").resolve()
    expected_stdout = (artifact_dir.resolve() / "singular_stdout.txt").resolve()
    if Path(str(result.get("program_file"))).resolve() != expected_program or Path(
        str(result.get("stdout_file"))
    ).resolve() != expected_stdout:
        raise ValueError("Singular artifact path changed or escaped")
    program = expected_program.read_text(encoding="utf-8")
    stdout = expected_stdout.read_text(encoding="utf-8")
    expected_program_text = _build_program(
        source_symbols=source_symbols,
        source_generators=source_generators,
        candidate_generators=candidate_generators,
    )
    if program != expected_program_text:
        raise ValueError("Singular persisted program is not the deterministic program")
    program_sha256 = hashlib.sha256(program.encode()).hexdigest()
    stdout_sha256 = hashlib.sha256(stdout.encode()).hexdigest()
    if program_sha256 != result.get("program_sha256"):
        raise ValueError("Singular program hash mismatch")
    if stdout_sha256 != result.get("stdout_sha256"):
        raise ValueError("Singular output hash mismatch")
    if any(
        line.lstrip().startswith("?") or line.lstrip().startswith("// **")
        for line in stdout.splitlines()
    ):
        raise ValueError("Singular output contains a diagnostic")
    executable = binary.resolve()
    if (
        Path(str(result.get("singular_binary"))).resolve() != executable
        or result.get("singular_binary_sha256") != _file_sha256(executable)
    ):
        raise ValueError("Singular binary provenance changed")
    expected_operation_hash = _operation_hash(
        input_binding=input_binding,
        source_generators=source_generators,
        candidate_generators=candidate_generators,
        program_sha256=program_sha256,
        singular_binary_sha256=_file_sha256(executable),
    )
    if result.get("operation_hash") != expected_operation_hash:
        raise ValueError("Singular operation hash mismatch")
    if result.get("source_generator_labels") != [
        label for label, _ in source_generators
    ] or result.get("candidate_generator_labels") != [
        label for label, _ in candidate_generators
    ]:
        raise ValueError("Singular generator-label binding changed")
    markers = _markers(stdout)
    if markers.get("DONE") != "1" or markers.get("CONSISTENCY") != "CONSISTENT":
        raise ValueError("Singular persisted completion/consistency marker changed")
    consistency_remainder = result.get("source_consistency_remainder")
    marker_consistency_remainder = markers.get("CONSISTENCY_REMAINDER")
    if (
        not isinstance(consistency_remainder, str)
        or not isinstance(marker_consistency_remainder, str)
        or _parse_polynomial(consistency_remainder, source_symbols) == 0
        or _parse_polynomial(marker_consistency_remainder, source_symbols)
        != _parse_polynomial(consistency_remainder, source_symbols)
    ):
        raise ValueError("Singular consistency remainder is not nonzero")
    checks = result.get("generator_checks")
    if not isinstance(checks, list) or len(checks) != len(candidate_generators):
        raise ValueError("Singular generator-check ledger changed")
    identity_hashes: list[str] = []
    source_by_label = dict(source_generators)
    for candidate_index, (check, (candidate_label, candidate_expression)) in enumerate(
        zip(checks, candidate_generators, strict=True), start=1
    ):
        if (
            not isinstance(check, Mapping)
            or check.get("label") != candidate_label
            or check.get("decision") != "ACCEPT"
            or check.get("exact_status") != "PROVED"
            or check.get("certificate_reexpanded") is not True
        ):
            raise ValueError("Singular generator check is not proved")
        persisted_remainder = check.get("normal_form_remainder")
        marker_status = markers.get(f"GENERATOR_{candidate_index}")
        marker_remainder = markers.get(f"GENERATOR_{candidate_index}_REMAINDER")
        if (
            marker_status != "PROVED"
            or not isinstance(persisted_remainder, str)
            or not isinstance(marker_remainder, str)
            or _parse_polynomial(persisted_remainder, source_symbols) != 0
            or _parse_polynomial(marker_remainder, source_symbols) != 0
        ):
            raise ValueError("Singular generator status/remainder mismatch")
        identity = check.get("identity")
        if not isinstance(identity, Mapping) or exact_tools.stable_hash(
            identity
        ) != check.get("identity_sha256"):
            raise ValueError("Singular generator identity hash mismatch")
        multipliers = identity.get("source_multipliers")
        if not isinstance(multipliers, Mapping) or set(multipliers) != set(
            source_by_label
        ):
            raise ValueError("Singular source multiplier labels changed")
        expanded = sp.Integer(0)
        for source_label, source_expression in source_generators:
            raw_multiplier = multipliers[source_label]
            if not isinstance(raw_multiplier, str):
                raise ValueError("Singular source multiplier is not serialized")
            source_index = next(
                index
                for index, (label, _) in enumerate(source_generators, start=1)
                if label == source_label
            )
            marker_multiplier = markers.get(
                f"MULTIPLIER_{candidate_index}_{source_index}"
            )
            if (
                not isinstance(marker_multiplier, str)
                or _parse_polynomial(marker_multiplier, source_symbols)
                != _parse_polynomial(raw_multiplier, source_symbols)
            ):
                raise ValueError("Singular multiplier marker changed")
            expanded += _parse_polynomial(
                raw_multiplier, source_symbols
            ) * source_expression
        remainder = sp.Poly(
            sp.expand(candidate_expression - expanded),
            *source_symbols,
            domain=sp.QQ,
        )
        if not remainder.is_zero or identity.get("exact_remainder") != "0":
            raise ValueError("Singular multiplier identity fails exact replay")
        if identity.get("candidate_label") != candidate_label or identity.get(
            "candidate_polynomial"
        ) != sp.sstr(sp.expand(candidate_expression)):
            raise ValueError("Singular candidate polynomial binding changed")
        identity_hashes.append(str(check["identity_sha256"]))
    certificate_payload = {
        "operation_hash": result.get("operation_hash"),
        "source_consistency": "CONSISTENT",
        "source_consistency_remainder": consistency_remainder,
        "generator_identity_sha256": identity_hashes,
    }
    if exact_tools.stable_hash(certificate_payload) != result.get(
        "certificate_sha256"
    ):
        raise ValueError("Singular aggregate certificate hash mismatch")
    return {
        "verified": True,
        "operation_hash": result["operation_hash"],
        "certificate_sha256": result["certificate_sha256"],
        "generator_identity_count": len(identity_hashes),
    }


def verify_closed_result(
    *,
    result: Mapping[str, Any],
    source_symbols: list[sp.Symbol],
    source_generators: list[tuple[str, sp.Expr]],
    candidate_generators: list[tuple[str, sp.Expr]],
    binary: Path,
    input_binding: Mapping[str, Any],
    artifact_dir: Path,
) -> dict[str, Any]:
    """Replay either a proved result or a persisted fail-closed CAS outcome."""

    if result.get("status") == "PROVED":
        return verify_proved_result(
            result=result,
            source_symbols=source_symbols,
            source_generators=source_generators,
            candidate_generators=candidate_generators,
            binary=binary,
            input_binding=input_binding,
            artifact_dir=artifact_dir,
        )
    if result.get("schema") != BACKEND_SCHEMA or result.get("backend") != BACKEND_NAME:
        raise ValueError("Singular closed-result schema changed")
    if result.get("input_binding") != dict(input_binding):
        raise ValueError("Singular input binding changed")
    program_path = (artifact_dir.resolve() / "singular_program.sing").resolve()
    stdout_path = (artifact_dir.resolve() / "singular_stdout.txt").resolve()
    if (
        Path(str(result.get("program_file"))).resolve() != program_path
        or Path(str(result.get("stdout_file"))).resolve() != stdout_path
    ):
        raise ValueError("Singular artifact path changed or escaped")
    program = program_path.read_text(encoding="utf-8")
    stdout = stdout_path.read_text(encoding="utf-8")
    expected_program = _build_program(
        source_symbols=source_symbols,
        source_generators=source_generators,
        candidate_generators=candidate_generators,
    )
    if program != expected_program:
        raise ValueError("Singular persisted program is not the deterministic program")
    program_sha256 = hashlib.sha256(program.encode()).hexdigest()
    stdout_sha256 = hashlib.sha256(stdout.encode()).hexdigest()
    if (
        result.get("program_sha256") != program_sha256
        or result.get("stdout_sha256") != stdout_sha256
    ):
        raise ValueError("Singular persisted artifact hash mismatch")
    executable = binary.resolve()
    binary_sha256 = _file_sha256(executable)
    if (
        Path(str(result.get("singular_binary"))).resolve() != executable
        or result.get("singular_binary_sha256") != binary_sha256
        or result.get("operation_hash")
        != _operation_hash(
            input_binding=input_binding,
            source_generators=source_generators,
            candidate_generators=candidate_generators,
            program_sha256=program_sha256,
            singular_binary_sha256=binary_sha256,
        )
    ):
        raise ValueError("Singular closed-result operation provenance changed")
    if result.get("source_generator_labels") != [
        label for label, _ in source_generators
    ] or result.get("candidate_generator_labels") != [
        label for label, _ in candidate_generators
    ]:
        raise ValueError("Singular generator-label binding changed")
    markers = _markers(stdout)
    status = result.get("status")
    process_status = result.get("process_status")
    diagnostics = any(
        line.lstrip().startswith("?") or line.lstrip().startswith("// **")
        for line in stdout.splitlines()
    )
    if status == "NOT_PROVED":
        if (
            process_status != "COMPLETED"
            or diagnostics
            or markers.get("DONE") != "1"
            or markers.get("CONSISTENCY") != "CONSISTENT"
        ):
            raise ValueError("Singular NOT_PROVED process boundary changed")
        result_consistency = result.get("source_consistency_remainder")
        marker_consistency = markers.get("CONSISTENCY_REMAINDER")
        if (
            not isinstance(result_consistency, str)
            or not isinstance(marker_consistency, str)
            or _parse_polynomial(result_consistency, source_symbols) == 0
            or _parse_polynomial(result_consistency, source_symbols)
            != _parse_polynomial(marker_consistency, source_symbols)
        ):
            raise ValueError("Singular NOT_PROVED consistency remainder changed")
        checks = result.get("generator_checks")
        if not isinstance(checks, list) or len(checks) != len(candidate_generators):
            raise ValueError("Singular NOT_PROVED generator ledger changed")
        rejected = 0
        for index, (check, (label, _)) in enumerate(
            zip(checks, candidate_generators, strict=True), start=1
        ):
            marker_status = markers.get(f"GENERATOR_{index}")
            marker_remainder = markers.get(f"GENERATOR_{index}_REMAINDER")
            if (
                not isinstance(check, Mapping)
                or check.get("label") != label
                or marker_status not in {"PROVED", "NOT_PROVED"}
                or check.get("exact_status") != marker_status
                or not isinstance(marker_remainder, str)
                or not isinstance(check.get("normal_form_remainder"), str)
            ):
                raise ValueError("Singular NOT_PROVED marker ledger changed")
            remainder = _parse_polynomial(marker_remainder, source_symbols)
            persisted = _parse_polynomial(
                str(check["normal_form_remainder"]), source_symbols
            )
            if remainder != persisted or (marker_status == "PROVED") is (remainder != 0):
                raise ValueError("Singular generator status/remainder mismatch")
            expected_decision = "ACCEPT" if marker_status == "PROVED" else "REJECT"
            if (
                check.get("decision") != expected_decision
                or check.get("certificate_reexpanded") is not False
            ):
                raise ValueError("Singular NOT_PROVED decision ledger changed")
            rejected += marker_status == "NOT_PROVED"
        if rejected == 0 or result.get("certificate_reexpanded") is not False:
            raise ValueError("Singular NOT_PROVED result lacks a nonzero remainder")
    elif status == "INCONSISTENT":
        remainder = markers.get("CONSISTENCY_REMAINDER")
        if (
            process_status != "COMPLETED"
            or diagnostics
            or markers.get("DONE") != "1"
            or markers.get("CONSISTENCY") != "INCONSISTENT"
            or not isinstance(remainder, str)
            or _parse_polynomial(remainder, source_symbols) != 0
            or result.get("source_consistency_remainder") != "0"
            or result.get("certificate_reexpanded") is not False
        ):
            raise ValueError("Singular inconsistent-source evidence changed")
    elif status == "INCONCLUSIVE":
        if process_status not in {"TIMEOUT", "ERROR", "COMPLETED"}:
            raise ValueError("Singular inconclusive process status changed")
        if process_status == "ERROR" and not diagnostics and result.get("returncode") == 0:
            raise ValueError("Singular ERROR has no persisted failure evidence")
        if process_status == "COMPLETED" and (
            markers.get("DONE") == "1"
            and markers.get("CONSISTENCY") in {"CONSISTENT", "INCONSISTENT"}
        ):
            raise ValueError("Singular completed outcome was mislabeled inconclusive")
        if result.get("certificate_reexpanded") is not False:
            raise ValueError("Singular inconclusive result became certified")
    else:
        raise ValueError("Singular closed-result status is unsupported")
    return {
        "verified": True,
        "status": status,
        "operation_hash": result["operation_hash"],
        "program_sha256": program_sha256,
        "stdout_sha256": stdout_sha256,
    }


def validate_consequences(
    *,
    source_symbols: list[sp.Symbol],
    source_generators: list[tuple[str, sp.Expr]],
    candidate_generators: list[tuple[str, sp.Expr]],
    binary: Path,
    timeout_sec: int,
    memory_mb: int,
    input_binding: Mapping[str, Any],
    output_dir: Path,
) -> dict[str, Any]:
    """Prove every candidate generator from one localized source ideal.

    Singular computes a standard basis and a lift matrix.  Promotion requires a
    second exact SymPy expansion of every original-generator multiplier identity;
    a bare Singular membership marker is never enough.
    """

    if not source_symbols:
        raise ValueError("Singular transformation validation needs source symbols")
    if not source_generators:
        raise ValueError("Singular transformation validation needs source generators")
    labels = [label for label, _ in source_generators]
    candidate_labels = [label for label, _ in candidate_generators]
    if len(set(labels)) != len(labels) or len(set(candidate_labels)) != len(
        candidate_labels
    ):
        raise ValueError("Singular generator labels must be unique")
    names = [str(symbol) for symbol in source_symbols]
    if len(set(names)) != len(names):
        raise ValueError("Singular symbols must be unique")

    program = _build_program(
        source_symbols=source_symbols,
        source_generators=source_generators,
        candidate_generators=candidate_generators,
    )
    run = _run_program(
        program=program,
        binary=binary,
        timeout_sec=timeout_sec,
        memory_mb=memory_mb,
    )
    artifact_root = output_dir.resolve()
    program_path = artifact_root / "singular_program.sing"
    stdout_path = artifact_root / "singular_stdout.txt"
    _write_text_atomic(program_path, program)
    _write_text_atomic(stdout_path, run["stdout"])
    executable = binary.resolve()
    operation_hash = _operation_hash(
        input_binding=input_binding,
        source_generators=source_generators,
        candidate_generators=candidate_generators,
        program_sha256=hashlib.sha256(program.encode("utf-8")).hexdigest(),
        singular_binary_sha256=_file_sha256(executable),
    )
    base: dict[str, Any] = {
        "schema": BACKEND_SCHEMA,
        "backend": BACKEND_NAME,
        "coefficient_domain": "QQ",
        "monomial_order": "dp",
        "cpu_only": True,
        "timeout_sec": timeout_sec,
        "memory_mb": memory_mb,
        "singular_binary": str(executable),
        "singular_binary_sha256": _file_sha256(executable),
        "program_sha256": hashlib.sha256(program.encode("utf-8")).hexdigest(),
        "program_file": str(program_path),
        "stdout_sha256": hashlib.sha256(run["stdout"].encode("utf-8")).hexdigest(),
        "stdout_file": str(stdout_path),
        "operation_hash": operation_hash,
        "runtime_sec": run["runtime_sec"],
        "process_status": run["status"],
        "returncode": run["returncode"],
        "input_binding": dict(input_binding),
        "source_generator_labels": labels,
        "candidate_generator_labels": candidate_labels,
    }
    if run["status"] != "COMPLETED":
        return {
            **base,
            "status": "INCONCLUSIVE",
            "reason": f"Singular process ended with {run['status']}",
            "source_consistency": "INCONCLUSIVE",
            "generator_checks": [],
            "certificate_reexpanded": False,
        }
    markers = _markers(run["stdout"])
    if markers.get("DONE") != "1":
        return {
            **base,
            "status": "INCONCLUSIVE",
            "reason": "Singular completion marker is missing",
            "source_consistency": "INCONCLUSIVE",
            "generator_checks": [],
            "certificate_reexpanded": False,
        }
    consistency = markers.get("CONSISTENCY")
    consistency_remainder_raw = markers.get("CONSISTENCY_REMAINDER")
    if consistency_remainder_raw is None:
        consistency = None
        consistency_remainder = None
    else:
        consistency_remainder_expression = _parse_polynomial(
            consistency_remainder_raw, source_symbols
        )
        consistency_remainder = sp.sstr(consistency_remainder_expression)
        if (consistency == "CONSISTENT") is (
            consistency_remainder_expression == 0
        ):
            consistency = None
    if consistency != "CONSISTENT":
        return {
            **base,
            "status": "INCONSISTENT" if consistency == "INCONSISTENT" else "INCONCLUSIVE",
            "reason": (
                "localized source ideal contains 1"
                if consistency == "INCONSISTENT"
                else "Singular source-consistency marker is invalid"
            ),
            "source_consistency": consistency or "INCONCLUSIVE",
            "source_consistency_remainder": consistency_remainder,
            "generator_checks": [],
            "certificate_reexpanded": False,
        }

    remainder_rows: list[tuple[str, sp.Expr, str, sp.Expr]] = []
    for candidate_index, (candidate_label, candidate_expression) in enumerate(
        candidate_generators, start=1
    ):
        exact_status = markers.get(f"GENERATOR_{candidate_index}")
        remainder_raw = markers.get(f"GENERATOR_{candidate_index}_REMAINDER")
        if remainder_raw is None:
            raise ValueError(
                f"Singular omitted candidate remainder {candidate_index}"
            )
        candidate_remainder = _parse_polynomial(remainder_raw, source_symbols)
        if exact_status not in {"PROVED", "NOT_PROVED"}:
            raise ValueError(
                f"Singular generator status is invalid for {candidate_label}"
            )
        if (exact_status == "PROVED") is (candidate_remainder != 0):
            raise ValueError(
                f"Singular generator status/remainder mismatch for {candidate_label}"
            )
        remainder_rows.append(
            (candidate_label, candidate_expression, str(exact_status), candidate_remainder)
        )
    if any(status != "PROVED" for _, _, status, _ in remainder_rows):
        checks = [
            {
                "label": candidate_label,
                "exact_status": status,
                "decision": "ACCEPT" if status == "PROVED" else "REJECT",
                "normal_form_remainder": sp.sstr(candidate_remainder),
                "certificate_reexpanded": False,
            }
            for candidate_label, _, status, candidate_remainder in remainder_rows
        ]
        first_rejected = next(
            row[0] for row in remainder_rows if row[2] != "PROVED"
        )
        return {
            **base,
            "status": "NOT_PROVED",
            "reason": f"candidate generator {first_rejected} is not in the localized source ideal",
            "source_consistency": "CONSISTENT",
            "source_consistency_remainder": consistency_remainder,
            "generator_checks": checks,
            "certificate_reexpanded": False,
        }

    checks: list[dict[str, Any]] = []
    for candidate_index, (
        candidate_label,
        candidate_expression,
        _,
        candidate_remainder,
    ) in enumerate(remainder_rows, start=1):
        if candidate_remainder != 0:
            raise ValueError("proved Singular candidate has a nonzero remainder")
        multipliers: dict[str, str] = {}
        expanded = sp.Integer(0)
        for source_index, (source_label, source_expression) in enumerate(
            source_generators, start=1
        ):
            key = f"MULTIPLIER_{candidate_index}_{source_index}"
            if key not in markers:
                raise ValueError(f"Singular lift omitted {key}")
            multiplier = _parse_polynomial(markers[key], source_symbols)
            multipliers[source_label] = sp.sstr(multiplier)
            expanded += multiplier * source_expression
        remainder = sp.Poly(
            sp.expand(candidate_expression - expanded),
            *source_symbols,
            domain=sp.QQ,
        )
        if not remainder.is_zero:
            raise ValueError(
                f"Singular multiplier identity failed exact replay for {candidate_label}"
            )
        identity_payload = {
            "candidate_label": candidate_label,
            "candidate_polynomial": sp.sstr(sp.expand(candidate_expression)),
            "source_multipliers": multipliers,
            "exact_remainder": "0",
        }
        checks.append(
            {
                "label": candidate_label,
                "decision": "ACCEPT",
                "exact_status": "PROVED",
                "normal_form_remainder": "0",
                "certificate_reexpanded": True,
                "identity": identity_payload,
                "identity_sha256": exact_tools.stable_hash(identity_payload),
            }
        )
    certificate_payload = {
        "operation_hash": operation_hash,
        "source_consistency": "CONSISTENT",
        "source_consistency_remainder": consistency_remainder,
        "generator_identity_sha256": [row["identity_sha256"] for row in checks],
    }
    return {
        **base,
        "status": "PROVED",
        "reason": "every candidate generator has an independently re-expanded original-source multiplier identity",
        "source_consistency": "CONSISTENT",
        "source_consistency_remainder": consistency_remainder,
        "generator_checks": checks,
        "certificate_reexpanded": True,
        "certificate_sha256": exact_tools.stable_hash(certificate_payload),
    }
