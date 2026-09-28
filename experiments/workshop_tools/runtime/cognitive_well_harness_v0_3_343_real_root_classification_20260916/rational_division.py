"""Guarded substitution + polynomial division, with an expansion-checked witness.

No Groebner construction, Laurent transformation, numerical sampling, or model
inference is performed here. A nonzero remainder is inconclusive, not disproof.
"""
from __future__ import annotations

import argparse
import json
import resource
import time
from pathlib import Path

import sympy as sp

from cognitive_well_harness_v0_3_274_generic_compression_portfolio_bridge_20260905 import exact_tools
from cognitive_well_harness_v0_3_275_generic_audited_ledger_compression_20260905 import transformation_validation as typed


BACKEND = "guarded_rational_substitution_polynomial_division_v1"
GUARD_PROPAGATION = "retain_checked_substitution_denominator_v1"
MAX_WITNESS_AST_NODES = 200_000


def initial(request):
    validated = exact_tools.validate_ideal_arguments(request["arguments"])
    symbols = list(validated["symbol_map"].values())
    equations = {k: v.as_expr() for k, v in validated["generators"].items()}
    target = validated["target"].as_expr()
    guards = typed.derive_guards(request["guard_program"], request["arguments"])["expressions"]
    return symbols, equations, target, guards


def normalized(expr):
    return sp.fraction(sp.cancel(expr))


def factors(expr, symbols):
    if sp.expand(expr) == 0:
        raise ValueError("zero cannot be canceled as a nonzero expression")
    return {sp.srepr(sp.Poly(f, *symbols, domain=sp.QQ).monic().as_expr())
            for f, _ in sp.factor_list(expr, *symbols)[1]}


def covered(expr, guards, symbols):
    known = set()
    for guard in guards:
        numerator, _ = normalized(guard)
        known.update(factors(numerator, symbols))
    return factors(expr, symbols) <= known


def substitute(equations, target, guards, variable, value, symbols):
    # Establish the pivot denominator from the OLD guards, before using it to
    # justify anything in the new state. It must not depend on the eliminated
    # variable, so its nonzero condition survives the substitution unchanged.
    value_numerator, value_denominator = normalized(value)
    if variable in value_numerator.free_symbols | value_denominator.free_symbols:
        raise ValueError("substitution is self-referential")
    if not covered(value_denominator, guards, symbols):
        raise ValueError("unguarded substitution denominator")
    mapped_guards = [normalized(g.subs(variable, value))[0] for g in guards]
    for g in mapped_guards:
        if sp.expand(g) == 0:
            raise ValueError("substitution conflicts with an asserted nonzero guard")
    # Mapping only numerators can erase a known factor through cancellation:
    # x*y != 0 with x=1/y becomes 1 != 0, but y != 0 is still necessary and
    # already justified. Keep that denominator, without adding a new assumption.
    if not covered(value_denominator, mapped_guards, symbols):
        mapped_guards.append(value_denominator)
    # Every subsequent normalization denominator still needs a checked guard.
    remaining = {}
    for label, equation in equations.items():
        transformed = equation.subs(variable, value)
        numerator, denominator = normalized(transformed)
        if not covered(denominator, mapped_guards, symbols):
            raise ValueError("unguarded equation normalization denominator")
        if sp.cancel(transformed * denominator - numerator) != 0:
            raise ValueError("equation normalization identity failed")
        if numerator != 0:
            remaining[label] = sp.expand(numerator)
    transformed = target.subs(variable, value)
    numerator, denominator = normalized(transformed)
    if not covered(denominator, mapped_guards, symbols):
        raise ValueError("unguarded target normalization denominator")
    if sp.cancel(transformed * denominator - numerator) != 0:
        raise ValueError("target normalization identity failed")
    return remaining, sp.cancel(transformed), mapped_guards


def encode(expr, names):
    return typed._polynomial_ast(sp.expand(expr), names)


def solve(request):
    started = time.monotonic()
    symbols, equations, target, guards = initial(request)
    names = list(request["arguments"]["symbols"])
    source_sizes = {"variables": len(symbols), "generators": len(equations)}
    steps = []
    while True:
        candidates = []
        for index, (label, equation) in enumerate(equations.items()):
            for variable_index, variable in enumerate(symbols):
                if variable not in equation.free_symbols:
                    continue
                polynomial = sp.Poly(equation, variable)
                if polynomial.degree() != 1:
                    continue
                coefficient = polynomial.coeff_monomial(variable)
                if not covered(coefficient, guards, symbols):
                    continue
                value = sp.cancel(-polynomial.coeff_monomial(1) / coefficient)
                # Purely mechanical order, fixed before observing this problem.
                candidates.append((int(sp.count_ops(value)), index, variable_index,
                                   label, variable, value))
        if not candidates:
            break
        _, _, _, label, variable, value = min(candidates)
        numerator, denominator = normalized(value)
        steps.append({"equation": label, "variable": str(variable),
                      "numerator": encode(numerator, names),
                      "denominator": encode(denominator, names)})
        equations, target, guards = substitute(equations, target, guards, variable, value, symbols)
    result = certify_state(request, symbols, equations, target, guards, steps)
    result["elapsed_seconds"] = time.monotonic() - started
    return result


def certify_state(request, symbols, equations, target, guards, steps, *, divisor_labels=None):
    """Export/replay division at an intermediate, guarded substitution state."""
    names = list(request["arguments"]["symbols"])
    source_sizes = {"variables": len(names), "generators": len(request["arguments"]["generators"])}
    numerator, denominator = normalized(target)
    labels = list(equations) if divisor_labels is None else list(divisor_labels)
    if len(labels) != len(equations) or set(labels) != set(equations):
        raise ValueError("division order must contain every current equation exactly once")
    if numerator == 0:
        # SymPy returns an empty quotient list for a zero dividend. The witness
        # must still bind an explicit zero multiplier to every remaining relation.
        quotients, remainder = [sp.Integer(0)] * len(labels), sp.Integer(0)
    elif labels:
        quotients, remainder = sp.reduced(numerator, [equations[label] for label in labels], *symbols, domain=sp.QQ)
    else:
        quotients, remainder = [], sp.expand(numerator)
    certificate = {
        "schema": BACKEND, "request_sha256": exact_tools.stable_hash(request),
        "substitutions": steps, "reduced_equations": {k: encode(v, names) for k, v in equations.items()},
        "target_numerator": encode(numerator, names), "target_denominator": encode(denominator, names),
        "quotients": {k: encode(q, names) for k, q in zip(labels, quotients, strict=True)},
        "remainder": encode(remainder, names),
    }
    checked = replay(request, certificate)
    active = set(numerator.free_symbols)
    for expr in equations.values():
        active.update(expr.free_symbols)
    return {"backend": BACKEND, "verdict": "VERIFIED_SUPPORT" if remainder == 0 else "INCONCLUSIVE",
            "guard_propagation_policy": GUARD_PROPAGATION,
            "verified": remainder == 0, "certificate_verified": checked["certificate_verified"],
            "source_size": source_sizes,
            "reduced_size": {"variables": len(active), "generators": len(equations)},
            "certificate": certificate,
            "groebner_calls": 0, "laurent_calls": 0, "singular_calls": 0,
            "semantic_certification": "NOT_AUDITED", "markdown": checked["markdown"]}


def replay(request, certificate):
    """Check only the supplied witness; no elimination/division search is replayed."""
    if certificate.get("schema") != BACKEND or certificate.get("request_sha256") != exact_tools.stable_hash(request):
        raise ValueError("certificate/request binding mismatch")
    symbols, equations, target, guards = initial(request)
    from cognitive_well_harness_v0_3_282_unit_circle_laurent_elimination_20260905.symbol_safety import FreshNames
    display = FreshNames(symbols)
    target_label = display.take("T")
    source_labels = {key: display.take(key) for key in equations}
    symbol_map = {str(s): s for s in symbols}
    # Generated witnesses can exceed the model-input cap; retain a separate bound.
    decode = lambda node: exact_tools._expression(node, symbol_map,max_ast_nodes=MAX_WITNESS_AST_NODES)
    lines = ["## Conditional algebraic certificate", "Assume the following equations and nonzero conditions:"]
    lines += [f"\\[{sp.latex(source_labels[k])}={sp.latex(v)}=0.\\]" for k, v in equations.items()]
    lines += [f"\\[{sp.latex(g)}\\ne0.\\]" for g in guards]
    lines.append(f"The target is \\({sp.latex(target_label)}={sp.latex(target)}\\).")
    for step in certificate["substitutions"]:
        label, variable = step["equation"], symbol_map[step["variable"]]
        equation = equations[label]
        poly = sp.Poly(equation, variable)
        if poly.degree() != 1:
            raise ValueError("witness pivot is not linear")
        coefficient, constant = poly.coeff_monomial(variable), poly.coeff_monomial(1)
        if not covered(coefficient, guards, symbols):
            raise ValueError("witness cancels an unguarded coefficient")
        numerator, denominator = decode(step["numerator"]), decode(step["denominator"])
        if not covered(denominator, guards, symbols):
            raise ValueError("witness substitution has an unguarded denominator")
        if variable in numerator.free_symbols | denominator.free_symbols:
            raise ValueError("witness substitution is self-referential")
        if sp.expand(coefficient*numerator + constant*denominator) != 0:
            raise ValueError("witness substitution is not implied by its pivot equation")
        value = numerator/denominator
        lines.append(f"The current equation \\({sp.latex(equation)}=0\\), with nonzero "
                     f"coefficient \\({sp.latex(coefficient)}\\), gives \\({sp.latex(variable)}={sp.latex(value)}\\).")
        equations, target, guards = substitute(equations, target, guards, variable, value, symbols)
    if set(certificate["reduced_equations"]) != set(equations) or set(certificate["quotients"]) != set(equations):
        raise ValueError("witness reduced relation labels changed")
    for label, equation in equations.items():
        if sp.expand(decode(certificate["reduced_equations"][label])-equation) != 0:
            raise ValueError("witness reduced equation changed")
    numerator, denominator = decode(certificate["target_numerator"]), decode(certificate["target_denominator"])
    if not covered(denominator, guards, symbols) or sp.cancel(target*denominator-numerator) != 0:
        raise ValueError("witness target normalization changed")
    remainder = decode(certificate["remainder"])
    combination = sum((decode(certificate["quotients"][k])*v for k, v in equations.items()), sp.Integer(0))
    if sp.expand(numerator-combination-remainder) != 0:
        raise ValueError("polynomial division witness failed exact re-expansion")
    lines.append("After these substitutions and denominator clearing, the remaining source equations are:")
    reduced_labels = {key: display.take(f"E_{i}") for i, key in enumerate(equations, 1)}
    numerator_label, denominator_label = display.take("N"), display.take("D")
    lines += [f"\\[{sp.latex(reduced_labels[key])}={sp.latex(value)}=0.\\]" for key, value in equations.items()]
    lines.append(f"The transformed target is \\({sp.latex(numerator_label)}/{sp.latex(denominator_label)}\\), "
                 f"where \\({sp.latex(numerator_label)}={sp.latex(numerator)}\\) and "
                 f"\\({sp.latex(denominator_label)}={sp.latex(denominator)}\\ne0\\). Exact expansion gives")
    rhs = sum((decode(certificate["quotients"][key])*reduced_labels[key]
               for key in equations), sp.Integer(0)) + remainder
    lines.append(f"\\[{sp.latex(numerator_label)}={sp.latex(rhs)}.\\]")
    lines.append(f"The remainder is zero, so the source equations and nonzero conditions imply \\({sp.latex(target_label)}=0\\)."
                 if remainder == 0 else "The remainder is nonzero. This division attempt does not settle whether the target follows.")
    return {"certificate_verified": True, "target_proved": remainder == 0, "markdown": "\n\n".join(lines),
            "guard_propagation_policy": GUARD_PROPAGATION,
            "target_label_latex": sp.latex(target_label)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(4*1024**3,4*1024**3))
    result=solve(json.loads(args.request.read_text()))
    args.output.write_text(json.dumps(result,indent=2)+"\n")


if __name__=="__main__":
    main()
