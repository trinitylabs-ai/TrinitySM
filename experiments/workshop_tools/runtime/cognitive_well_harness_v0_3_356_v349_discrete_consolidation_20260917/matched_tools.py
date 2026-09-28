"""Deterministic execution after an upstream caller has selected a typed tool.

This module does not detect gaps, choose an operation, read problem/reference
documents, or certify a theorem. The public executor is bounded in a subprocess.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing
from pathlib import Path
import resource

from . import HARNESS_REVISION

SCHEMA = "v0326-matched-exact-computation-v1"
OPERATIONS = ("exact_geometry", "rational_identity", "real_root_classification", "uniform_partition_count", "symbolic_modular_order")
ENGINE_REVISION = "geometry-algebra.1"
CAPABILITIES = {
    "real_root_classification": {
        "detect": "A complete root set or critical-point classification is unproved or may be false.",
        "match": "One real variable with polynomial, rational or single positive square-root expressions on a finite exact interval.",
        "inputs": "The root-args grammar in root_classification.CONTRACT; expression/function and interval, no proposed roots required.",
    },
    "exact_geometry": {
        "detect": "An asserted coordinate, incidence, circle-power, intersection, or fixed-locus fact lacks a derivation or may be false.",
        "match": "A finite chain of planar constructions and exact rational/algebraic expressions encodes the requested local fact.",
        "inputs": "Named scalar parameters, actual construction definitions, domain assumptions, comparisons, and requested outputs; no answer formula is required.",
    },
    "rational_identity": {
        "detect": "A rational identity, linear relation, or parameter-independence claim is an unresolved proof obligation.",
        "match": "Exact rational normalization, differentiation, linear-root derivation, or linear coefficient matching can address the encoded obligation.",
        "inputs": "Scalar definitions, a declared unknown and moving parameter when needed, assumptions, comparisons, and requested outputs.",
    },
}
CONTRACT = """Supply exactly one exact-args Markdown fence. Fields in order:
symbols = comma-separated real scalar identifiers, or NONE
define = unique_name :: expression
assume = unique_label :: comparison
check = unique_label :: comparison
emit = declared_name
Definitions/assumptions are optional; at least one check or emit is required.
Names have no implicit meaning. Every definition must precede assumptions/checks.
Expressions: integer, declared name, (symbol name), (rational int int),
(add e e ...), (mul e e ...), (sub e e), (div e e), (neg e), (pow e integer),
(sqrt nonnegative_exact_constant), (differentiate expression variable).
Comparisons: (eq e e), (ne e e), (gt e e), (ge e e), (lt e e), (le e e).
Roots: (linear_root unknown expression) derives a root of expression=0 when its
numerator is linear in the declared unknown. (coefficient_root unknown parameter
expression) derives a parameter-independent root by setting ALL coefficients of
the numerator in parameter to zero. Only linear equations in the unknown are
supported. Both recheck substitution and record pivot/domain conditions. Neither
claims all roots or covers exceptional zero pivots. Assumptions are not used as
rewrite rules. Arbitrary nonlinear solving or theorem reasoning is unsupported.
Geometry operations (exact_geometry only): (point x y), (vadd P Q), (vsub P Q),
(scale scalar P), (dot P Q), (cross P Q), (norm2 P), (x P), (y P), (midpoint P Q),
(foot P A B), (line_intersection A B C D), (circle A B C),
(circle_center_radius O positive_radius), (center circle), (power circle P),
(second_on_line circle known_point other_line_point),
(second_on_circles circle circle known_point), (invert_point center factor P),
(invert_line center factor A B). Inversion sends X to center +
factor*(X-center)/norm2(X-center); factor must be nonzero. invert_line returns a
circle and requires the line not to pass through the inversion center.
Circles are x^2+y^2+u*x+v*y+w=0. A second intersection must differ from the known
one; tangencies, coincident circles and zero denominators are not silently given
another interpretation. Symbolic construction preconditions remain explicit.
No Python, JSON, file paths, floats, arbitrary functions, or implicit branches.
The output proves at most exact statements in this supplied parameterization,
under ALL reported conditions. It does not check the encoding against a theorem.
A concrete counterexample requires all supplied assumptions and construction
conditions to hold. Unknown signs or symbolic residuals are not counterexamples.
"""


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def envelope(operation, markdown):
    return {"schema": SCHEMA, "engine_revision": ENGINE_REVISION,
            "harness_revision": HARNESS_REVISION, "operation": operation,
            "request_sha256": digest({"operation": operation, "markdown": markdown}),
            "model_calls": 0, "theorem_proved": False, "source_semantics_verified": False,
            "symbolic_premise_consistency_verified": False,
            "scope": "supplied parameterization and comparisons, under all recorded conditions"}


def _compute(operation, markdown):
    if operation in ('uniform_partition_count', 'symbolic_modular_order'):
        from . import discrete_certificates
        compiled = discrete_certificates.compile_program(markdown)
        if compiled.get('operation') != operation:
            raise ValueError('formalization changed the matched operation')
        result = discrete_certificates.compute(markdown)
        return {**envelope(operation, markdown), 'state': 'completed', 'verdict': 'DISCRETE_CERTIFICATE_VERIFIED',
                'usable_evidence': True, 'discrete_compilation': compiled, 'discrete_result': result}
    if operation == 'real_root_classification':
        from . import root_classification
        compiled = root_classification.compile_program(markdown)
        result = root_classification.compute(markdown)
        return {**envelope(operation, markdown), 'state': 'completed', 'verdict': 'ROOT_CLASSIFICATION_VERIFIED',
            'usable_evidence': True, 'root_compilation': compiled, 'root_result': result}
    from .matched_expression import evaluate, parse_program, payload

    program = parse_program(markdown, operation)
    ev, assumptions, checks = evaluate(program, geometry=operation == "exact_geometry")
    conditions = [{key: value for key, value in row.items() if not key.startswith("_")}
                  for row in ev.obligations]
    unresolved = [row for row in assumptions + conditions if row["truth"] is not True]
    concrete = not program["symbols"]
    if any(row["truth"] is False for row in assumptions):
        verdict = "INCONSISTENT_PREMISES"
    elif concrete and not unresolved and any(row["truth"] is False for row in checks):
        verdict = "COUNTEREXAMPLE"
    elif checks and all(row["truth"] is True for row in checks):
        verdict = "CONDITIONAL_IDENTITY" if unresolved else "IDENTITY_VERIFIED"
    elif not checks:
        verdict = "CONDITIONAL_COMPUTATION" if unresolved else "COMPUTED"
    else:
        verdict = "INCONCLUSIVE"
    return {**envelope(operation, markdown), "state": "completed", "verdict": verdict,
            "usable_evidence": verdict not in {"INCONCLUSIVE", "INCONSISTENT_PREMISES"},
            "program_sha256": digest(program), "concrete_instance": concrete,
            "assumptions": assumptions, "construction_conditions": conditions,
            "unresolved_conditions": unresolved, "checks": checks,
            "definitions": {name: payload(ev.env[name]) for name, _ in program["definitions"]},
            "outputs": {name: payload(ev.env[name]) for name in program["emits"]},
            "derivations": ev.derivations,
            "counterexample_replay": verdict == "COUNTEREXAMPLE"}


def _worker(sender, operation, markdown, timeout_seconds, memory_mb):
    try:
        resource.setrlimit(resource.RLIMIT_AS, (memory_mb * 1024**2,) * 2)
        resource.setrlimit(resource.RLIMIT_CPU, (timeout_seconds, timeout_seconds + 1))
        from .matched_expression import DerivationUnavailable, InvalidInstance

        try:
            result = _compute(operation, markdown)
        except InvalidInstance as error:
            result = {**envelope(operation, markdown), "state": "completed", "verdict": "INVALID_INSTANCE",
                      "usable_evidence": False, "reason": str(error)}
        except DerivationUnavailable as error:
            result = {**envelope(operation, markdown), "state": "completed", "verdict": "INCONCLUSIVE",
                      "usable_evidence": False, "reason": str(error)}
        except (ValueError, TypeError, KeyError, RecursionError) as error:
            result = {**envelope(operation, markdown), "state": "failed_closed", "verdict": "INVALID_REQUEST",
                      "usable_evidence": False, "reason": str(error)}
        sender.send(result)
    except BaseException as error:
        try:
            sender.send({**envelope(operation, markdown), "state": "failed_closed", "verdict": "EXECUTION_ERROR",
                         "usable_evidence": False, "reason": type(error).__name__ + ": " + str(error)})
        except (BrokenPipeError, MemoryError, OSError):
            pass
    finally:
        sender.close()


def execute(*, operation, arguments_markdown, timeout_seconds=60, memory_mb=2048):
    """Execute an explicitly matched operation, with no fallback or model calls."""
    if operation not in OPERATIONS:
        raise ValueError("unsupported matched operation: " + str(operation))
    if not isinstance(arguments_markdown, str) or len(arguments_markdown) > 60000:
        raise ValueError("expected at most 60000 characters of Markdown arguments")
    if type(timeout_seconds) is not int or not 1 <= timeout_seconds <= 600:
        raise ValueError("timeout must be an integer in 1..600 seconds")
    if type(memory_mb) is not int or not 256 <= memory_mb <= 8192:
        raise ValueError("memory must be an integer in 256..8192 MiB")
    context = multiprocessing.get_context("spawn")
    receiver, sender = context.Pipe(duplex=False)
    child = context.Process(target=_worker, args=(sender, operation, arguments_markdown, timeout_seconds, memory_mb))
    child.start()
    sender.close()
    try:
        if receiver.poll(timeout_seconds + 2):
            try:
                return receiver.recv()
            except EOFError:
                reason = "bounded worker exited without a result"
        else:
            reason = "bounded worker exceeded its time budget"
        return {**envelope(operation, arguments_markdown), "state": "completed", "verdict": "INCONCLUSIVE",
                "usable_evidence": False, "reason": reason}
    finally:
        receiver.close()
        child.join(timeout=0.2)
        if child.is_alive():
            child.terminate()
            child.join(timeout=1)
        if child.is_alive():
            child.kill()
            child.join(timeout=1)
        child.close()


def replay(*, operation, arguments_markdown, saved_result, **limits):
    """Recompute the bound request; saved booleans/hashes alone are not evidence."""
    if saved_result.get("state") != "completed" or not saved_result.get("usable_evidence"):
        raise ValueError("saved result is not usable exact computation evidence")
    actual = execute(operation=operation, arguments_markdown=arguments_markdown, **limits)
    if actual != saved_result:
        raise ValueError("matched computation replay differs from saved result")
    return actual


def render(result):
    if result.get('verdict') == 'DISCRETE_CERTIFICATE_VERIFIED':
        from . import discrete_certificates
        statement, appendix = discrete_certificates.render(result['discrete_compilation'], result['discrete_result'])
        return statement+'\n\n'+appendix
    if result.get('verdict') == 'ROOT_CLASSIFICATION_VERIFIED':
        from . import root_classification
        statement, appendix = root_classification.render(result['root_compilation'], result['root_result'])
        return statement+'\n\n'+appendix
    lines = ["# Matched exact computation", "", "Verdict: " + result["verdict"],
             "", "Scope: " + result["scope"] + ". Source correspondence and the full theorem are not certified.",
             "", "Request SHA-256: " + result["request_sha256"]]
    if result.get("reason"):
        lines += ["", result["reason"]]
    for title, rows in (("Assumptions", result.get("assumptions", [])),
                        ("Construction conditions (including canceled denominators)", result.get("construction_conditions", [])),
                        ("Checks", result.get("checks", []))):
        if rows:
            lines += ["", "## " + title, ""]
            for row in rows:
                lines.append(f"- {row.get('label', row.get('reason'))}: `{row['residual']} {row['relation']} 0`; exact truth = {row['truth']}")
    if result.get("outputs"):
        lines += ["", "## Outputs", ""]
        lines += [f"- {name}: `{json.dumps(value, sort_keys=True)}`" for name, value in result["outputs"].items()]
    if result.get("derivations"):
        lines += ["", "## Rechecked linear derivations", ""]
        for row in result["derivations"]:
            lines += [f"- {row['kind']}: `{row['unknown']} = {row['candidate']}`; pivot `{row['pivot']}`; all coefficient residuals `{row['coefficient_residuals']}`."]
    return "\n".join(lines) + "\n"


def run(*, operation, arguments_markdown, output, **limits):
    """Persist only the supplied arguments and deterministic result in a fresh directory."""
    root = Path(output)
    root.mkdir(parents=True, exist_ok=False)
    (root / "arguments.md").write_text(arguments_markdown, encoding="utf-8")
    result = execute(operation=operation, arguments_markdown=arguments_markdown, **limits)
    (root / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (root / "result.md").write_text(render(result), encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--operation", required=True, choices=OPERATIONS)
    parser.add_argument("--arguments", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--timeout-seconds", type=int, default=60)
    parser.add_argument("--memory-mb", type=int, default=2048)
    args = parser.parse_args()
    result = run(operation=args.operation, arguments_markdown=args.arguments.read_text(encoding="utf-8"),
                 output=args.output_dir, timeout_seconds=args.timeout_seconds, memory_mb=args.memory_mb)
    print(result["verdict"])
    return int(result["state"] == "failed_closed")


if __name__ == "__main__":
    raise SystemExit(main())
