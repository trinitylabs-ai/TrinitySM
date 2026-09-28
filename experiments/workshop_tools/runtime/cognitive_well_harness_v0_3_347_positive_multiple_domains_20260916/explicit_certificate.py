"""Verify model-written polynomial derivations by expansion, without ideal search."""
from __future__ import annotations

from typing import Any, Mapping

from cognitive_well_harness_v0_3_274_generic_compression_portfolio_bridge_20260905 import exact_tools


def verify(program: Mapping[str, Any], validated: Mapping[str, Any], guards: Mapping[str, Any]) -> dict[str, Any]:
    sp = exact_tools.require_sympy()
    names = list(validated["symbols"])
    variables = list(validated["symbol_map"].values())
    sources = {label: validated["generators"][label].as_expr() for label in program["relations"]}
    target = validated["target"].as_expr()
    if set(names) & (set(sources) | set(guards) | {"T", "C1"}):
        raise ValueError("certificate reference names collide with source variables")
    aliases = {**validated["symbol_map"], **guards, "T": target}
    display = {name: sp.Symbol(name) for name in aliases}
    definitions = []
    for row in program["definitions"]:
        label = row["label"]
        if label in aliases or label in sources or label.startswith("Z") or label == "C1":
            raise ValueError("definition label collides with a frozen or derived reference")
        value = exact_tools._expression(row["value"], aliases)
        sp.Poly(value, *variables, domain=sp.QQ)
        expression = exact_tools._expression(row["value"], display)
        aliases[label] = value
        display[label] = sp.Symbol(label)
        definitions.append((label, expression))

    # Only explicit disjoint-circle equations are available for cheap reduction.
    # Polynomial division returns the actual quotients, which are displayed below.
    circle_labels, circle_polynomials = [], []
    for label, value in sources.items():
        active = sorted(value.free_symbols, key=str)
        if len(active) != 2:
            continue
        poly = sp.Poly(value, *active, domain=sp.QQ)
        coef = poly.coeff_monomial(active[0] ** 2)
        if coef and sp.expand(value - coef * (active[0]**2 + active[1]**2 - 1)) == 0:
            circle_labels.append(label)
            circle_polynomials.append(value)

    def divide(residual: Any, label: str) -> tuple[Any, list[Any]]:
        expanded = sp.Poly(sp.expand(residual), *variables, domain=sp.QQ).as_expr()
        if circle_polynomials:
            quotients, remainder = sp.reduced(expanded, circle_polynomials, *variables, domain=sp.QQ)
        else:
            quotients, remainder = [], expanded
        if sp.expand(remainder) != 0:
            polynomial = sp.Poly(remainder, *variables, domain=sp.QQ)
            raise ValueError(f"{label} identity has nonzero exact remainder ({len(polynomial.terms())} terms)")
        return expanded, quotients

    factors = {}
    for label, guard in guards.items():
        if sp.expand(guard) == 0:
            raise ValueError("frozen guard is zero")
        for factor, _ in sp.factor_list(guard, *variables)[1]:
            key = sp.srepr(sp.Poly(factor, *variables, domain=sp.QQ).monic().as_expr())
            factors.setdefault(key, []).append(label)

    def scale_coverage(scale: Any) -> list[dict[str, Any]]:
        if sp.expand(scale) == 0:
            raise ValueError("zero derivation has zero cancellation scale")
        coverage = []
        for factor, exponent in sp.factor_list(scale, *variables)[1]:
            key = sp.srepr(sp.Poly(factor, *variables, domain=sp.QQ).monic().as_expr())
            if key not in factors:
                raise ValueError(f"cancellation scale has unguarded factor {factor}")
            coverage.append({"factor": str(factor), "exponent": exponent, "guards": factors[key]})
        return coverage

    lines = ["## Algebraic lemma", "Put \\[T=" + sp.latex(target) + ".\\]",
             "Assume the following polynomial equations and nonzero conditions:"]
    lines += [f"\\[{sp.latex(sp.Symbol(label))}={sp.latex(value)}=0.\\]" for label, value in sources.items()]
    lines += [f"\\[{sp.latex(sp.Symbol(label))}={sp.latex(value)}\\ne0.\\]" for label, value in guards.items()]
    if definitions:
        lines.append("Use the following abbreviations, in the order displayed:")
        lines += [f"\\[{sp.latex(sp.Symbol(label))}={sp.latex(value)}.\\]" for label, value in definitions]

    def correction(quotients: list[Any]) -> Any:
        return sum((q * sp.Symbol(label) for label, q in zip(circle_labels, quotients, strict=True)), sp.Integer(0))

    records = []
    for row in program["identities"]:
        left = exact_tools._expression(row["left"], aliases)
        right = exact_tools._expression(row["right"], aliases)
        _, quotients = divide(left - right, row["label"])
        shown_left = exact_tools._expression(row["left"], display)
        shown_right = exact_tools._expression(row["right"], display)
        lines.append(f"\\[\\bigl({sp.latex(shown_left)}\\bigr)-\\bigl({sp.latex(shown_right)}\\bigr)={sp.latex(correction(quotients))}.\\]")
        records.append({"label": row["label"], "exact_expansion_zero": True})

    references = {**sources}
    zero_rows = list(program["zeros"])
    if not zero_rows or zero_rows[-1]["label"] != "C1":
        raise ValueError("certificate needs an explicit zero derivation ending in C1")
    for index, row in enumerate(zero_rows):
        label = row["label"]
        expected = "C1" if index == len(zero_rows)-1 else f"Z{index+1}"
        if label != expected:
            raise ValueError("zero derivations must be Z1, Z2, ... followed by C1")
        value = exact_tools._expression(row["value"], aliases)
        scale = exact_tools._expression(row["scale"], aliases)
        if label == "C1" and sp.expand(value - target) != 0:
            raise ValueError("C1 must be exactly the frozen formal target")
        coverage = scale_coverage(scale)
        refs = {key: sp.Dummy(key) for key in references}
        symbolic_combination = exact_tools._expression(row["combination"], {**aliases, **refs})
        if sp.expand(symbolic_combination.xreplace({symbol: sp.Integer(0) for symbol in refs.values()})) != 0:
            raise ValueError(f"{label} combination is not zero from previous equations")
        combination = symbolic_combination.xreplace({symbol: references[key] for key, symbol in refs.items()})
        _, quotients = divide(scale * value - combination, label)
        shown_value = exact_tools._expression(row["value"], display)
        shown_scale = exact_tools._expression(row["scale"], display)
        shown_combination = exact_tools._expression(row["combination"], {**display, **{key: sp.Symbol(key) for key in references}})
        rhs = shown_combination + correction(quotients)
        rendered_label = sp.latex(sp.Symbol(label))
        lines += [f"Define \\({rendered_label}={sp.latex(shown_value)}\\). Expanding the displayed definitions gives the polynomial identity",
                  f"\\[\\bigl({sp.latex(shown_scale)}\\bigr){rendered_label}={sp.latex(rhs)}.\\]"]
        if coverage:
            used = sorted({g for item in coverage for g in item["guards"]})
            lines.append("The factor on the left is nonzero by " + ", ".join(used) + ".")
        else:
            lines.append("The constant factor on the left is nonzero.")
        lines.append(f"The right-hand side vanishes by the source equations and the preceding zero identities, so \\({rendered_label}=0\\).")
        references[label] = value
        records.append({"label": label, "exact_expansion_zero": True, "guard_factor_coverage": coverage,
                        "circle_quotients": [str(q) for q in quotients]})
    lines.append("Since \\(C_1=T\\), the lemma proves \\(T=0\\) under exactly the stated equations and nonzero conditions.")
    markdown = "\n\n".join(lines)
    if len(markdown) > 120_000:
        raise ValueError("explicit certificate is too long; use shorter algebraic definitions")
    return {"markdown": markdown, "checks": records, "groebner_search_performed": False,
            "verified": True, "source_relations": list(sources)}
