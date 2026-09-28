"""A bounded deterministic factor/substitution/cancellation/division portfolio.

This backend accepts an already parsed and semantically accepted polynomial
formalization. Explicit trig syntax, if absent, is NOT reconstructed from symbol
names. Supplied circle equations remain ordinary exact polynomial identities.
No Groebner basis, Laurent transformation, or model calls occur in this backend.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import copy
import json
from pathlib import Path
import resource
import signal
import time

import sympy as sp

from . import backend_comparison as artifacts, rational_division as kernel

SCHEMA = "guarded_composite_identity_v1"
POLICIES = ("target_first", "small_rhs", "lookahead")


@contextmanager
def cpu_slice(seconds):
    def expired(signum, frame):
        raise TimeoutError("bounded simplification step expired")
    old = signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


def normalize_factors(request):
    symbols, equations, target, guards = kernel.initial(request)
    names = request["arguments"]["symbols"]
    result = copy.deepcopy(request)
    trace = []
    for label, equation in equations.items():
        if equation == 0:
            continue
        coefficient, factors = sp.factor_list(equation, *symbols)
        kept, rows = [], []
        for factor, exponent in factors:
            cancelled = kernel.covered(factor, guards, symbols)
            rows.append({"factor": kernel.encode(factor, names), "exponent": int(exponent), "cancelled": cancelled})
            if not cancelled:
                kept.append(factor)
        reduced = sp.expand(sp.prod(kept))
        if not reduced.free_symbols and reduced != 0:
            raise ValueError("source equation is a product of established nonzero factors")
        result["arguments"]["generators"][label] = kernel.encode(reduced, names)
        trace.append({"equation": label, "coefficient": kernel.encode(coefficient, names), "factors": rows})
    return result, trace


def check_preprocessing(request, transformed, trace):
    symbols, equations, target, guards = kernel.initial(request)
    symbol_map = {str(s): s for s in symbols}
    decode = lambda value: kernel.exact_tools._expression(value, symbol_map, max_ast_nodes=kernel.MAX_WITNESS_AST_NODES)
    expected = copy.deepcopy(request)
    seen = set()
    for step in trace:
        label = step["equation"]
        if label in seen or label not in equations:
            raise ValueError("factor trace has duplicate or unknown equation")
        seen.add(label)
        coefficient = decode(step["coefficient"])
        if coefficient == 0 or coefficient.free_symbols:
            raise ValueError("factor coefficient must be a nonzero rational constant")
        product = coefficient
        kept = []
        for row in step["factors"]:
            factor, exponent = decode(row["factor"]), row["exponent"]
            if not isinstance(exponent, int) or isinstance(exponent, bool) or exponent < 1 or exponent > 256:
                raise ValueError("invalid positive factor multiplicity")
            product *= factor**exponent
            if row["cancelled"] is True:
                if not kernel.covered(factor, guards, symbols):
                    raise ValueError("factor trace cancels an unguarded factor")
            else:
                kept.append(factor)
        if sp.expand(product-equations[label]) != 0:
            raise ValueError("factorization identity failed exact expansion")
        expected["arguments"]["generators"][label] = kernel.encode(sp.prod(kept), request["arguments"]["symbols"])
    if expected != transformed:
        raise ValueError("factor-normalized request drift")
    return True


def candidates(symbols, equations, target, guards):
    rows = []
    for equation_index, (label, equation) in enumerate(equations.items()):
        for variable_index, variable in enumerate(symbols):
            if variable not in equation.free_symbols:
                continue
            polynomial = sp.Poly(equation, variable)
            if polynomial.degree() != 1:
                continue
            coefficient = polynomial.coeff_monomial(variable)
            if not kernel.covered(coefficient, guards, symbols):
                continue
            value = sp.cancel(-polynomial.coeff_monomial(1)/coefficient)
            rows.append({"label": label, "variable": variable, "value": value,
                         "key": (int(sp.count_ops(value)), equation_index, variable_index),
                         "target_occurs": variable in target.free_symbols})
    return rows


def choose(policy, rows, symbols, equations, target, guards):
    if policy == "target_first":
        return min(rows, key=lambda row: (not row["target_occurs"], *row["key"])), None
    if policy == "small_rhs":
        return min(rows, key=lambda row: row["key"]), None
    options = []
    for row in sorted(rows, key=lambda row: (not row["target_occurs"], *row["key"]))[:3]:
        state = kernel.substitute(equations, target, guards, row["variable"], row["value"], symbols)
        eqs, result_target, result_guards = state
        size = int(sp.count_ops(result_target)) + sum(int(sp.count_ops(e)) for e in eqs.values())
        options.append(((size, *row["key"]), row, state))
    _, row, state = min(options, key=lambda item: item[0])
    return row, state


def replay(request, certificate):
    if certificate.get("schema") != SCHEMA or certificate.get("request_sha256") != kernel.exact_tools.stable_hash(request):
        raise ValueError("composite certificate/request binding changed")
    transformed = certificate["normalized_request"]
    check_preprocessing(request, transformed, certificate["factor_trace"])
    power = certificate["target_power"]
    if power not in (1, 2) or isinstance(power, bool):
        raise ValueError("unsupported target power")
    powered = copy.deepcopy(transformed)
    symbols, equations, target, guards = kernel.initial(transformed)
    powered["arguments"]["target"] = kernel.encode(target**power, transformed["arguments"]["symbols"])
    checked = kernel.replay(powered, certificate["division_certificate"])
    if checked["target_proved"] is not True:
        raise ValueError("composite certificate does not prove the target")
    original_symbols, original_equations, original_target, original_guards = kernel.initial(request)
    lines = ["## Conditional algebraic lemma", "Assume the following original equations and nonzero conditions:"]
    lines += [f"\\[{sp.latex(expr)}=0.\\]" for expr in original_equations.values()]
    lines += [f"\\[{sp.latex(expr)}\\ne0.\\]" for expr in original_guards]
    lines.append("The following exact factorizations permit cancellation only of established nonzero factors. Over a field, a product of positive powers is zero exactly when the product with those positive multiplicities removed is zero.")
    for label, original in original_equations.items():
        reduced = equations[label]
        if sp.expand(original-reduced) != 0:
            lines.append(f"\\[{sp.latex(original)}={sp.latex(sp.factor(original))}=0\\quad\\Longrightarrow\\quad {sp.latex(reduced)}=0.\\]")
    lines.append(checked["markdown"])
    lines.append(f"This proves \\(({sp.latex(original_target)})^{{{power}}}=0\\). Over the real or complex numbers this implies \\({sp.latex(original_target)}=0\\), as required.")
    markdown = "\n\n".join(lines)
    return {"verified": True, "certificate_verified": True, "target_proved": True,
            "markdown": markdown, "markdown_characters": len(markdown),
            "certificate_sha256": kernel.exact_tools.stable_hash(certificate)}


def solve(request, *, max_checks=36, max_depth=3, stage_seconds=20, event=None):
    started = time.monotonic()
    symbols, original_equations, original_target, original_guards = kernel.initial(request)
    names = request["arguments"]["symbols"]
    status = {"backend": SCHEMA, "state": "running", "verdict": "INCONCLUSIVE", "verified": False,
              "source_size": {"variables": len(symbols), "generators": len(original_equations)},
              "explicit_trig_stage": "NOT_APPLICABLE_ALREADY_POLYNOMIAL_INPUT",
              "model_calls": 0, "singular_calls": 0, "laurent_calls": 0, "groebner_calls": 0,
              "checks": [], "policies": list(POLICIES), "guard_policy": "supplied_guards_only"}

    def report(**changes):
        status.update(changes, elapsed_seconds=round(time.monotonic()-started, 3))
        if event:
            event(copy.deepcopy(status))

    report(stage="factor_and_guard_normalization")
    with cpu_slice(stage_seconds):
        normalized, trace = normalize_factors(request)
        check_preprocessing(request, normalized, trace)
    report(factor_changes=sum(normalized["arguments"]["generators"][label] != value
                              for label, value in request["arguments"]["generators"].items()))
    seen_states = set()
    for policy in POLICIES:
        symbols, equations, target, guards = kernel.initial(normalized)
        steps = []
        for depth in range(max_depth+1):
            if len(status["checks"]) >= max_checks:
                break
            report(stage="polynomial_residual", policy=policy, depth=depth,
                   substitution_count=len(steps), current_size={"variables": len(set().union(target.free_symbols,
                       *(value.free_symbols for value in equations.values()))), "generators": len(equations)})
            # Source relations, including circle identities, are retained. Vary
            # division order without asserting any new equation or branch.
            divisor_orders = [list(equations), sorted(equations, key=lambda label: (sp.count_ops(equations[label]), label))]
            for divisor_order in divisor_orders:
                for power in (1, 2):
                    key = (sp.srepr(target), tuple((label, sp.srepr(equations[label])) for label in divisor_order), power)
                    if key in seen_states or len(status["checks"]) >= max_checks:
                        continue
                    seen_states.add(key)
                    row = {"policy": policy, "depth": depth, "target_power": power, "divisor_order": divisor_order}
                    status["checks"].append(row)
                    report()
                    try:
                        with cpu_slice(stage_seconds):
                            numerator, denominator = kernel.normalized(target)
                            numerator = sp.expand(numerator**power)
                            if len(sp.Poly(numerator, *symbols).terms()) > 3000:
                                row.update(outcome="TERM_BUDGET")
                                continue
                            _, remainder = sp.reduced(numerator, [equations[label] for label in divisor_order],
                                                       *symbols, domain=sp.QQ) if divisor_order else ([], numerator)
                            row.update(outcome="ZERO" if remainder == 0 else "NONZERO",
                                       remainder_terms=len(sp.Poly(remainder, *symbols).terms()))
                            if remainder == 0:
                                powered = copy.deepcopy(normalized)
                                powered["arguments"]["target"] = kernel.encode(original_target**power, names)
                                result = kernel.certify_state(powered, symbols, equations, target**power, guards,
                                                              steps, divisor_labels=divisor_order)
                                certificate = {"schema": SCHEMA, "request_sha256": kernel.exact_tools.stable_hash(request),
                                    "normalized_request": normalized, "factor_trace": trace, "target_power": power,
                                    "division_certificate": result["certificate"]}
                                checked = replay(request, certificate)
                                report(state="completed", stage="verified", verdict="VERIFIED_SUPPORT", verified=True,
                                       certificate=certificate, presentation=checked)
                                return status
                    except TimeoutError:
                        row.update(outcome="TIMEOUT")
                    report()
            if depth == max_depth:
                break
            try:
                report(stage="guarded_substitution", policy=policy, depth=depth)
                with cpu_slice(stage_seconds):
                    options = candidates(symbols, equations, target, guards)
                    if not options:
                        break
                    row, next_state = choose(policy, options, symbols, equations, target, guards)
                    numerator, denominator = kernel.normalized(row["value"])
                    next_state = next_state or kernel.substitute(equations, target, guards, row["variable"], row["value"], symbols)
                    steps.append({"equation": row["label"], "variable": str(row["variable"]),
                                  "numerator": kernel.encode(numerator, names), "denominator": kernel.encode(denominator, names)})
                    equations, target, guards = next_state
            except TimeoutError:
                report(last_timeout="guarded_substitution")
                break
    report(state="completed", stage="inconclusive", fallback_recommended="existing_guarded_radical_then_laurent_cascade")
    return status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--stage-seconds", type=int, default=20)
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (4*1024**3, 4*1024**3))
    request, admission = artifacts.accepted_request(args.request)
    args.output.mkdir(parents=True, exist_ok=False)
    artifacts.write(args.output / "request.json", request)
    manifest = {"admission": admission, "request_path": str(args.request.resolve()),
                "model_calls": 0, "started": time.time(), "backend": SCHEMA,
                "max_checks": 36, "max_depth": 3, "stage_seconds": args.stage_seconds}
    artifacts.write(args.output / "manifest.json", manifest)
    try:
        result = solve(request, stage_seconds=args.stage_seconds,
                       event=lambda value: artifacts.write(args.output / "status.json", value))
    except Exception as error:
        result = {"state": "failed_closed", "verified": False, "error": f"{type(error).__name__}: {error}"}
    if result.get("verified"):
        artifacts.write(args.output / "certificate.json", result["certificate"])
        from .rewrite import pipeline
        pipeline.base.write_text(args.output / "lemma.md", result["presentation"]["markdown"])
    artifacts.write(args.output / "status.json", result)
    artifacts.write(args.output / "result.json", result)
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
