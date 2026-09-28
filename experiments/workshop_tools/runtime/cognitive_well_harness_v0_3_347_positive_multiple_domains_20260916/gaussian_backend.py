from __future__ import annotations

import hashlib
import json
import os
import resource
import subprocess
import time
from pathlib import Path
from typing import Any, Mapping

import sympy as sp

from .polynomial_export import expression as _expression

MAX_BACKEND_OUTPUT_BYTES = 8 * 1024 * 1024


def _backend_symbols(symbols: list[sp.Symbol]) -> list[sp.Symbol]:
    return [sp.Symbol(f"v{index}_") for index in range(len(symbols))]


def _backend_expression(
    expression: sp.Expr, symbols: list[sp.Symbol], aliases: list[sp.Symbol]
) -> str:
    mapped = expression.xreplace(dict(zip(symbols, aliases, strict=True)))
    return _expression(mapped)


def _parse_backend_polynomial(
    raw: str, symbols: list[sp.Symbol], aliases: list[sp.Symbol]
) -> sp.Expr:
    locals_map = {str(alias): alias for alias in aliases}
    locals_map["ii"] = sp.I
    expression = sp.sympify(raw.replace("^", "**"), locals=locals_map)
    allowed = set(aliases)
    if not expression.free_symbols.issubset(allowed):
        raise ValueError("Gaussian Singular output contains an undeclared symbol")
    expression = expression.xreplace(dict(zip(aliases, symbols, strict=True)))
    return sp.Poly(sp.expand(expression), *symbols, extension=sp.I).as_expr()


def _ordinary_program(
    *, symbols: list[sp.Symbol], generators: list[tuple[str, sp.Expr]], target: sp.Expr
) -> tuple[str, list[sp.Symbol]]:
    aliases = _backend_symbols(symbols)
    lines = [
        "option(redSB);",
        f"ring R=(0,ii),({','.join(str(alias) for alias in aliases)}),dp;",
        "minpoly=ii^2+1;",
    ]
    generator_names = []
    for index, (_, expression) in enumerate(generators, start=1):
        name = f"g{index}"
        generator_names.append(name)
        lines.append(
            f"poly {name}={_backend_expression(expression, symbols, aliases)};"
        )
    lines.extend(
        [
            f"poly target={_backend_expression(target, symbols, aliases)};",
            f"ideal J={','.join(generator_names)};",
            "matrix source_to_std;",
            "int started=timer;",
            "ideal G=liftstd(J,source_to_std);",
            "poly consistency_remainder=reduce(1,G);",
            'print("RESULT_CONSISTENCY_REMAINDER="+string(consistency_remainder));',
            "poly remainder=reduce(target,G);",
            'print("RESULT_REMAINDER="+string(remainder));',
            'print("RESULT_GB_SECONDS="+string(timer-started));',
            'print("RESULT_GB_SIZE="+string(size(G)));',
            'if (remainder==0) { print("RESULT_ORDINARY=PROVED");',
            "  module std_to_target=lift(G,target);",
            "  matrix source_to_target=source_to_std*std_to_target;",
        ]
    )
    for index in range(1, len(generator_names) + 1):
        lines.append(
            f'  print("RESULT_MULTIPLIER_{index}="+'
            f"string(source_to_target[{index},1]));"
        )
    lines.extend(
        [
            '} else { print("RESULT_ORDINARY=NONZERO");',
            '  print("RESULT_REMAINDER_TERMS="+string(size(remainder)));',
            '  print("RESULT_REMAINDER_DEGREE="+string(deg(remainder))); }',
            'print("RESULT_DONE=1");',
            "exit;",
        ]
    )
    return "\n".join(lines) + "\n", aliases


def _ordinary_certificate_check(
    *,
    symbols: list[sp.Symbol],
    generators: list[tuple[str, sp.Expr]],
    target: sp.Expr,
    binary: Path,
    timeout_sec: int,
    memory_mb: int | None,
) -> dict[str, Any]:
    program, aliases = _ordinary_program(
        symbols=symbols, generators=generators, target=target
    )
    result = _run(program, binary, timeout_sec, memory_mb=memory_mb)
    result["program"] = program
    result["program_sha256"] = hashlib.sha256(program.encode()).hexdigest()
    result["output_sha256"] = hashlib.sha256(result["output"].encode()).hexdigest()
    result.update(
        {
            "method": "gaussian_ordinary_original_generator_lift",
            "generator_labels": [label for label, _ in generators],
            "guard_count": 0,
        }
    )
    markers = result.get("markers", {})
    if (
        result.get("status") != "COMPLETED"
        or markers.get("RESULT_DONE") != "1"
        or "RESULT_REMAINDER" not in markers
        or "RESULT_CONSISTENCY_REMAINDER" not in markers
    ):
        result.update(
            certificate_reexpanded=False,
            membership_certificate=None,
        )
        return result
    try:
        consistency = _parse_backend_polynomial(
            markers["RESULT_CONSISTENCY_REMAINDER"], symbols, aliases
        )
        remainder = _parse_backend_polynomial(
            markers["RESULT_REMAINDER"], symbols, aliases
        )
    except Exception as error:
        result.update(
            status="ERROR",
            certificate_reexpanded=False,
            membership_certificate=None,
            certificate_error=f"invalid Singular remainder: {type(error).__name__}: {error}",
        )
        return result
    result["consistency_remainder"] = sp.sstr(consistency)
    result["normal_form_remainder"] = sp.sstr(remainder)
    if markers.get("RESULT_ORDINARY") != "PROVED" or remainder != 0:
        result.update(certificate_reexpanded=False, membership_certificate=None)
        return result
    if consistency == 0:
        result.update(
            status="ERROR",
            certificate_reexpanded=False,
            membership_certificate=None,
            certificate_error="derived ideal is inconsistent",
        )
        return result
    multipliers: dict[str, str] = {}
    expanded = sp.Integer(0)
    for index, (label, generator) in enumerate(generators, start=1):
        raw = markers.get(f"RESULT_MULTIPLIER_{index}")
        if not isinstance(raw, str):
            result.update(
                status="ERROR",
                certificate_reexpanded=False,
                membership_certificate=None,
                certificate_error=f"missing multiplier for {label}",
            )
            return result
        try:
            multiplier = _parse_backend_polynomial(raw, symbols, aliases)
        except Exception as error:
            result.update(
                status="ERROR",
                certificate_reexpanded=False,
                membership_certificate=None,
                certificate_error=(
                    f"invalid multiplier for {label}: {type(error).__name__}: {error}"
                ),
            )
            return result
        multipliers[label] = sp.sstr(multiplier)
        expanded += multiplier * generator
    exact_remainder = sp.Poly(
        sp.expand(target - expanded), *symbols, extension=sp.I
    )
    if not exact_remainder.is_zero:
        result.update(
            status="ERROR",
            certificate_reexpanded=False,
            membership_certificate=None,
            certificate_error="original-generator multiplier identity failed replay",
        )
        return result
    certificate = {
        "coefficient_field": "QQ(i)",
        "generator_labels": [label for label, _ in generators],
        "source_multipliers": multipliers,
        "target_expression": sp.sstr(sp.expand(target)),
        "exact_remainder": "0",
        "reexpansion_zero": True,
    }
    canonical = json.dumps(certificate, sort_keys=True, separators=(",", ":"))
    certificate["certificate_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    result.update(
        certificate_reexpanded=True,
        membership_certificate=certificate,
    )
    return result


def _markers(output: str) -> dict[str, str]:
    markers: dict[str, str] = {}
    for line in output.splitlines():
        if not line.startswith("RESULT_") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key in markers:
            raise ValueError(f"duplicate Singular result marker: {key}")
        markers[key] = value
    return markers


def _singular_diagnostic(output: str) -> bool:
    lines = output.splitlines()
    # The relocatable Debian Singular bundle may omit its optional
    # p_Procs_FieldIndep acceleration module.  Singular explicitly reports that
    # it remains correct (only slower), then emits the ordinary result markers.
    # Ignore only that exact three-line advisory; every other Singular warning
    # or diagnostic remains fail-closed.
    optional_module_advisory = (
        "// ** Could not find dynamic library: p_Procs_FieldIndep.so (path )",
        "// ** Singular will work properly, but much slower.",
        "// ** See the INSTALL section in the Singular manual for details.",
    )
    stripped = [line.strip() for line in lines]
    for advisory in optional_module_advisory:
        if stripped.count(advisory) > 1:
            return True
    remaining = [line for line in stripped if line not in optional_module_advisory]
    return any(
        line.startswith("?") or line.startswith("// **") for line in remaining
    )


def _singular_environment(binary: Path) -> dict[str, str]:
    """Bind a relocatable Singular installation's libraries and modules."""

    environment = dict(os.environ)
    installation_root = binary.resolve().parents[2]
    library_dir = installation_root / "usr/lib/x86_64-linux-gnu"
    module_paths = (
        installation_root / "usr/share/singular/LIB",
        installation_root / "usr/libexec/x86_64-linux-gnu/singular/MOD",
    )
    process_module_dir = module_paths[1]
    if library_dir.is_dir():
        prior = environment.get("LD_LIBRARY_PATH", "")
        environment["LD_LIBRARY_PATH"] = os.pathsep.join(
            [str(library_dir), *([prior] if prior else [])]
        )
    existing_modules = [str(path) for path in module_paths if path.is_dir()]
    prior = environment.get("SINGULARPATH", "")
    if prior:
        existing_modules.append(prior)
    if existing_modules:
        environment["SINGULARPATH"] = os.pathsep.join(existing_modules)
    if process_module_dir.is_dir():
        # Relocated Debian Singular builds otherwise retain the compiled `/usr`
        # ProcDir and silently miss the bundled p_Procs acceleration modules.
        environment["SINGULAR_PROCS_DIR"] = str(process_module_dir)
    return environment


def _run(
    program: str, binary: Path, timeout_sec: int, memory_mb: int | None = None
) -> dict[str, Any]:
    started = time.monotonic()
    def limit_memory() -> None:
        if memory_mb is None:
            return
        limit = memory_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (limit, limit))

    try:
        completed = subprocess.run(
            [str(binary), "-q"],
            input=program,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout_sec,
            check=False,
            preexec_fn=limit_memory,
            env=_singular_environment(binary),
        )
    except subprocess.TimeoutExpired as error:
        output = error.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        if len(output.encode("utf-8")) > MAX_BACKEND_OUTPUT_BYTES:
            output = output[:MAX_BACKEND_OUTPUT_BYTES]
        try:
            markers = _markers(output)
        except ValueError:
            markers = {}
        return {
            "status": "TIMEOUT",
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "markers": markers,
            "output": output,
        }
    output = completed.stdout
    oversized = len(output.encode("utf-8")) > MAX_BACKEND_OUTPUT_BYTES
    if oversized:
        output = output[:MAX_BACKEND_OUTPUT_BYTES]
    singular_error = oversized or _singular_diagnostic(output)
    try:
        markers = {} if singular_error else _markers(output)
    except ValueError:
        singular_error = True
        markers = {}
    return {
        "status": (
            "COMPLETED"
            if completed.returncode == 0 and not singular_error
            else "ERROR"
        ),
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "returncode": completed.returncode,
        # Singular can exit 0 after a parse/runtime error and continue to later
        # statements.  Such downstream markers are not valid certificates.
        "markers": markers,
        "output": output,
        "output_truncated": oversized,
    }


def check(
    *,
    symbols: list[sp.Symbol],
    generators: list[tuple[str, sp.Expr]],
    target: sp.Expr,
    guards: Mapping[str, sp.Expr],
    binary: Path,
    timeout_sec: int,
    radical: bool,
    memory_mb: int | None = None,
) -> dict[str, Any]:
    if not radical:
        return _ordinary_certificate_check(
            symbols=symbols,
            generators=generators,
            target=target,
            binary=binary,
            timeout_sec=timeout_sec,
            memory_mb=memory_mb,
        )
    base_names = [str(symbol) for symbol in symbols]
    auxiliary = ["proof_inv", "guard_inv"] if radical else []
    lines = [
        "option(redSB);",
        f"ring R=(0,ii),({','.join(base_names + auxiliary)}),dp;",
        "minpoly=ii^2+1;",
    ]
    generator_names = []
    for index, (_, expression) in enumerate(generators, start=1):
        name = f"g{index}"
        generator_names.append(name)
        lines.append(f"poly {name}={_expression(expression)};")
    lines.append(f"poly target={_expression(target)};")
    if radical:
        guard_product = sp.prod(guards.values())
        lines.append(f"poly guard={_expression(guard_product)};")
        ideal_terms = [*generator_names, "1-guard_inv*guard", "1-proof_inv*target"]
    else:
        ideal_terms = generator_names
    lines.extend(
        [
            f"ideal J={','.join(ideal_terms)};",
            "int started=timer;",
            "ideal G=slimgb(J);",
            'print("RESULT_GB_SECONDS="+string(timer-started));',
            'print("RESULT_GB_SIZE="+string(size(G)));',
        ]
    )
    if radical:
        lines.append(
            'if (reduce(1,G)==0) { print("RESULT_RADICAL=PROVED"); } '
            'else { print("RESULT_RADICAL=NOT_PROVED"); }'
        )
    else:
        lines.append(
            'poly remainder=reduce(target,G); '
            'if (remainder==0) { print("RESULT_ORDINARY=PROVED"); } '
            'else { print("RESULT_ORDINARY=NONZERO"); '
            'print("RESULT_REMAINDER_TERMS="+string(size(remainder))); '
            'print("RESULT_REMAINDER_DEGREE="+string(deg(remainder))); }'
        )
    lines.append("exit;")
    result = _run(
        "\n".join(lines) + "\n", binary, timeout_sec, memory_mb=memory_mb
    )
    result.update(
        {
            "method": "gaussian_guarded_rabinowitsch" if radical else "gaussian_ordinary",
            "generator_labels": [label for label, _ in generators],
            "guard_count": len(guards),
        }
    )
    return result


def check_principal_radical(
    *,
    symbols: list[sp.Symbol],
    generator: tuple[str, sp.Expr],
    target: sp.Expr,
    guards: Mapping[str, sp.Expr],
    binary: Path,
    timeout_sec: int,
    memory_mb: int | None = None,
) -> dict[str, Any]:
    """Decide guarded radical membership for a principal ideal exactly.

    First remove from the generator every factor made invertible by any guard.
    In characteristic zero, dividing the result by the gcd of it and all of its
    partial derivatives produces its square-free part.  Membership in the
    radical of the resulting principal ideal is then ordinary divisibility.
    """
    base_names = [str(symbol) for symbol in symbols]
    label, expression = generator
    lines = [
        "option(redSB);",
        f"ring R=(0,ii),({','.join(base_names)}),dp;",
        "minpoly=ii^2+1;",
        f"poly principal={_expression(expression)};",
        f"poly target={_expression(target)};",
    ]
    guard_names = []
    for index, guard in enumerate(guards.values(), start=1):
        name = f"guard{index}"
        guard_names.append(name)
        lines.append(f"poly {name}={_expression(guard)};")
    lines.extend(
        [
            "int started=timer;",
            "poly saturated=principal;",
            "poly common;",
            "int changed=1;",
            "while (changed==1)",
            "{",
            "  changed=0;",
        ]
    )
    for name in guard_names:
        lines.extend(
            [
                f"  common=gcd(saturated,{name});",
                "  if (deg(common)>0)",
                "  {",
                "    saturated=saturated/common;",
                "    changed=1;",
                "  }",
            ]
        )
    lines.extend(
        [
            "}",
            "poly repeated=saturated;",
        ]
    )
    for symbol in base_names:
        lines.append(f"repeated=gcd(repeated,diff(saturated,{symbol}));")
    lines.extend(
        [
            "poly squarefree=saturated/repeated;",
            "ideal K=squarefree;",
            "ideal G=std(K);",
            "poly remainder=reduce(target,G);",
            'print("RESULT_PRINCIPAL_SECONDS="+string(timer-started));',
            'print("RESULT_SATURATED_DEGREE="+string(deg(saturated)));',
            'print("RESULT_SQUAREFREE_DEGREE="+string(deg(squarefree)));',
            'if (remainder==0) { print("RESULT_PRINCIPAL_RADICAL=PROVED"); } '
            'else { print("RESULT_PRINCIPAL_RADICAL=NOT_PROVED"); '
            'print("RESULT_REMAINDER_TERMS="+string(size(remainder))); '
            'print("RESULT_REMAINDER_DEGREE="+string(deg(remainder))); }',
            "exit;",
        ]
    )
    result = _run(
        "\n".join(lines) + "\n", binary, timeout_sec, memory_mb=memory_mb
    )
    result.update(
        {
            "method": "gaussian_guard_localized_principal_radical",
            "generator_labels": [label],
            "guard_count": len(guards),
        }
    )
    return result
