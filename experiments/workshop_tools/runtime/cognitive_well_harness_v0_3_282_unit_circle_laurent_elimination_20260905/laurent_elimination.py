from __future__ import annotations

import hashlib
import itertools
import json
from typing import Any, Mapping

import sympy as sp

from .symbol_safety import FreshNames


DOMAIN = sp.QQ_I


def _poly(expression: sp.Expr, symbols: list[sp.Symbol]) -> sp.Poly:
    return sp.Poly(sp.expand(expression), *symbols, extension=sp.I)


def _canonical(expression: sp.Expr, symbols: list[sp.Symbol]) -> sp.Expr:
    polynomial = _poly(expression, symbols)
    if polynomial.is_zero:
        return sp.Integer(0)
    return polynomial.monic().as_expr()


def _key(expression: sp.Expr, symbols: list[sp.Symbol]) -> str:
    return sp.srepr(_canonical(expression, symbols))


def _fraction_numerator(expression: sp.Expr) -> sp.Expr:
    numerator, _ = sp.fraction(sp.cancel(sp.together(expression)))
    return sp.expand(numerator)


def _fraction(expression: sp.Expr) -> tuple[sp.Expr, sp.Expr]:
    numerator, denominator = sp.fraction(sp.cancel(sp.together(expression)))
    return sp.expand(numerator), sp.expand(denominator)


def _profile(expressions: list[sp.Expr], symbols: list[sp.Symbol]) -> dict[str, int]:
    polynomials = [_poly(expression, symbols) for expression in expressions]
    return {
        "symbol_count": len(symbols),
        "maximum_total_degree": max(
            (-1 if polynomial.is_zero else int(polynomial.total_degree())
             for polynomial in polynomials),
            default=-1,
        ),
        "total_monomial_count": sum(len(polynomial.terms()) for polynomial in polynomials),
    }


def detect_unit_circle_candidates(
    generators: Mapping[str, sp.Poly], symbols: list[sp.Symbol]
) -> list[dict[str, Any]]:
    """Return every structural ``x^2+y^2-1`` generator canonically.

    Detection does not greedily consume coordinates.  This matters when malformed
    or redundant input contains overlapping circle generators: the caller can
    enumerate the maximum disjoint sets without depending on mapping order.
    """

    detected: list[dict[str, Any]] = []
    for label, generator in sorted(generators.items()):
        support = sorted(generator.as_expr().free_symbols, key=lambda value: str(value))
        if len(support) != 2:
            continue
        first, second = support
        expected = first**2 + second**2 - 1
        if _key(generator.as_expr(), symbols) != _key(expected, symbols):
            continue
        detected.append(
            {"label": label, "coordinates": (first, second)}
        )
    return sorted(
        detected,
        key=lambda row: (
            tuple(str(value) for value in row["coordinates"]),
            str(row["label"]),
        ),
    )


def enumerate_maximum_disjoint_circle_sets(
    candidates: list[dict[str, Any]],
) -> list[list[dict[str, Any]]]:
    """Enumerate all maximum-cardinality disjoint structural circle sets."""

    disjoint: list[list[dict[str, Any]]] = []
    for mask in range(1, 1 << len(candidates)):
        rows = [
            candidate
            for index, candidate in enumerate(candidates)
            if mask & (1 << index)
        ]
        coordinates = [
            symbol for row in rows for symbol in row["coordinates"]
        ]
        if len(coordinates) == len(set(coordinates)):
            disjoint.append(rows)
    if not disjoint:
        return []
    maximum = max(len(rows) for rows in disjoint)
    return sorted(
        (rows for rows in disjoint if len(rows) == maximum),
        key=lambda rows: tuple(
            (str(row["label"]), *(str(value) for value in row["coordinates"]))
            for row in rows
        ),
    )


def detect_unit_circles(
    generators: Mapping[str, sp.Poly], symbols: list[sp.Symbol]
) -> list[dict[str, Any]]:
    """Backward-compatible helper for inputs with a unique maximum set.

    Ambiguous overlaps fail closed instead of silently depending on generator
    iteration order.  ``transform`` itself enumerates every maximum set.
    """

    sets = enumerate_maximum_disjoint_circle_sets(
        detect_unit_circle_candidates(generators, symbols)
    )
    if len(sets) > 1:
        raise ValueError("unit-circle generators have ambiguous maximum disjoint sets")
    return sets[0] if sets else []


def structural_orientation_plan(validated: Mapping[str, Any]) -> dict[str, Any]:
    """Describe the complete deterministic circle/orientation search space."""

    symbols = [validated["symbol_map"][name] for name in validated["symbols"]]
    candidates = detect_unit_circle_candidates(validated["generators"], symbols)
    circle_sets = enumerate_maximum_disjoint_circle_sets(candidates)
    return {
        "detected_circle_candidates": candidates,
        "circle_sets": circle_sets,
        "circle_set_count": len(circle_sets),
        "maximum_disjoint_circle_count": max(
            (len(rows) for rows in circle_sets), default=0
        ),
        "orientation_attempted_count": sum(2 ** len(rows) for rows in circle_sets),
    }


def _factor_keys(expression: sp.Expr, symbols: list[sp.Symbol]) -> set[str]:
    polynomial = _poly(expression, symbols)
    if polynomial.is_zero:
        raise ValueError("zero cannot be treated as a nonzero guard")
    if polynomial.total_degree() == 0:
        return set()
    _, factors = sp.factor_list(polynomial.as_expr(), *symbols, extension=sp.I)
    return {_key(factor, symbols) for factor, _ in factors}


def _known_nonzero(
    expression: sp.Expr,
    symbols: list[sp.Symbol],
    guard_factor_keys: set[str],
) -> bool:
    return _factor_keys(expression, symbols).issubset(guard_factor_keys)


def _target_numerator(
    target: sp.Expr,
    variable: sp.Symbol,
    coefficient: sp.Expr,
    constant: sp.Expr,
) -> sp.Expr:
    polynomial = sp.Poly(target, variable, domain="EX")
    if polynomial.is_zero:
        return sp.Integer(0)
    degree = int(polynomial.degree())
    return sp.expand(
        sum(
            polynomial.nth(exponent)
            * (-constant) ** exponent
            * coefficient ** (degree - exponent)
            for exponent in range(degree + 1)
        )
    )


def _linear_elimination(
    *,
    generators: Mapping[str, sp.Expr],
    target: sp.Expr,
    symbols: list[sp.Symbol],
    guards: Mapping[str, sp.Expr],
) -> dict[str, Any] | None:
    guard_keys: set[str] = set()
    for expression in guards.values():
        guard_keys.update(_factor_keys(expression, symbols))
    candidates = []
    for variable in symbols:
        independent = []
        linear = []
        rejected = False
        for label, expression in generators.items():
            polynomial = sp.Poly(expression, variable, domain="EX")
            degree = -1 if polynomial.is_zero else int(polynomial.degree())
            if degree <= 0:
                independent.append((label, expression))
            elif degree == 1:
                linear.append(
                    {
                        "label": label,
                        "coefficient": sp.expand(polynomial.nth(1)),
                        "constant": sp.expand(polynomial.nth(0)),
                    }
                )
            else:
                rejected = True
                break
        if rejected or len(linear) < 2:
            continue
        base_symbols = [symbol for symbol in symbols if symbol != variable]
        pivots = [
            row
            for row in linear
            if _known_nonzero(row["coefficient"], base_symbols, guard_keys)
        ]
        if not pivots:
            continue
        pivot_rows = []
        for pivot in pivots:
            compatibility = [
                (
                    f"compat_{pivot['label']}_{row['label']}",
                    sp.expand(
                        pivot["coefficient"] * row["constant"]
                        - row["coefficient"] * pivot["constant"]
                    ),
                )
                for row in linear
                if row["label"] != pivot["label"]
            ]
            derived_generators = [*independent, *compatibility]
            derived_target = _target_numerator(
                target,
                variable,
                pivot["coefficient"],
                pivot["constant"],
            )
            pivot_rows.append(
                {
                    "pivot": pivot,
                    "generators": derived_generators,
                    "target": derived_target,
                    "symbols": base_symbols,
                    "profile": _profile(
                        [*[expression for _, expression in derived_generators], derived_target],
                        base_symbols,
                    ),
                    "linear_rows": linear,
                }
            )
        selected = min(
            pivot_rows,
            key=lambda row: (
                row["profile"]["maximum_total_degree"],
                row["profile"]["total_monomial_count"],
                row["pivot"]["label"],
            ),
        )
        candidates.append(
            {
                "variable": variable,
                **selected,
            }
        )
    if not candidates:
        return None
    return min(
        candidates,
        key=lambda row: (
            row["profile"]["maximum_total_degree"],
            row["profile"]["total_monomial_count"],
            str(row["variable"]),
        ),
    )


def transform(
    validated: Mapping[str, Any],
    *,
    nonzero_guards: Mapping[str, sp.Expr],
) -> dict[str, Any]:
    source_symbols = [validated["symbol_map"][name] for name in validated["symbols"]]
    plan = structural_orientation_plan(validated)
    circle_candidates = plan["detected_circle_candidates"]
    circle_sets = plan["circle_sets"]
    if not circle_sets:
        raise ValueError("no disjoint unit-circle generators were detected")
    rows: list[dict[str, Any]] = []
    outcomes: list[dict[str, Any]] = []
    for set_index, circles in enumerate(circle_sets, start=1):
        circle_labels = {row["label"] for row in circles}
        retained_symbols = [
            symbol
            for symbol in source_symbols
            if all(symbol not in row["coordinates"] for row in circles)
        ]
        for orientation in itertools.product((0, 1), repeat=len(circles)):
            outcome = {
                "circle_set_index": set_index,
                "orientation": orientation,
            }
            try:
                fresh = FreshNames(source_symbols)
                laurent_symbols = [
                    fresh.take(f"unit_{index}")
                    for index in range(1, len(circles) + 1)
                ]
                substitutions: dict[sp.Symbol, sp.Expr] = {}
                inverse_substitutions: dict[sp.Symbol, sp.Expr] = {}
                for circle, odd_index, unit in zip(
                    circles, orientation, laurent_symbols, strict=True
                ):
                    odd = circle["coordinates"][odd_index]
                    even = circle["coordinates"][1 - odd_index]
                    substitutions[odd] = (unit - unit**-1) / (2 * sp.I)
                    substitutions[even] = (unit + unit**-1) / 2
                    inverse_substitutions[unit] = even + sp.I * odd
                for circle in circles:
                    first, second = circle["coordinates"]
                    if sp.cancel(
                        (first**2 + second**2 - 1).subs(substitutions)
                    ) != 0:
                        raise AssertionError("unit-circle Laurent substitution failed")
                new_symbols = [*retained_symbols, *laurent_symbols]
                transformed_generator_fractions = {
                    label: _fraction(generator.as_expr().subs(substitutions))
                    for label, generator in validated["generators"].items()
                    if label not in circle_labels
                }
                transformed_generators = {
                    label: fraction[0]
                    for label, fraction in transformed_generator_fractions.items()
                }
                transformed_target_fraction = _fraction(
                    validated["target"].as_expr().subs(substitutions)
                )
                transformed_target = transformed_target_fraction[0]
                transformed_guard_fractions = {
                    label: _fraction(expression.subs(substitutions))
                    for label, expression in nonzero_guards.items()
                }
                transformed_guards = {
                    label: fraction[0]
                    for label, fraction in transformed_guard_fractions.items()
                }
                transformed_guards.update(
                    {
                        f"unit_guard_{index}": unit
                        for index, unit in enumerate(laurent_symbols, start=1)
                    }
                )
                eliminated = _linear_elimination(
                    generators=transformed_generators,
                    target=transformed_target,
                    symbols=new_symbols,
                    guards=transformed_guards,
                )
                if eliminated is None:
                    pure_profile = _profile(
                        [*transformed_generators.values(), transformed_target],
                        new_symbols,
                    )
                    source_profile = _profile(
                        [
                            *[
                                generator.as_expr()
                                for generator in validated["generators"].values()
                            ],
                            validated["target"].as_expr(),
                        ],
                        source_symbols,
                    )
                    pure_key = (
                        len(new_symbols),
                        len(transformed_generators),
                        pure_profile["maximum_total_degree"],
                        pure_profile["total_monomial_count"],
                    )
                    source_key = (
                        len(source_symbols),
                        len(validated["generators"]),
                        source_profile["maximum_total_degree"],
                        source_profile["total_monomial_count"],
                    )
                    if pure_key >= source_key:
                        outcomes.append(
                            {**outcome, "state": "laurent_only_not_strictly_smaller"}
                        )
                        continue
                    eliminated = {
                        "mode": "laurent_only",
                        "variable": None,
                        "pivot": None,
                        "generators": sorted(transformed_generators.items()),
                        "target": transformed_target,
                        "symbols": new_symbols,
                        "profile": pure_profile,
                        "linear_rows": [],
                    }
                else:
                    eliminated = {"mode": "guarded_linear_elimination", **eliminated}
                row = {
                    **outcome,
                    "circles": circles,
                    "orientation": orientation,
                    "laurent_symbols": laurent_symbols,
                    "substitutions": substitutions,
                    "inverse_substitutions": inverse_substitutions,
                    "transformed_generator_fractions": transformed_generator_fractions,
                    "transformed_generators": transformed_generators,
                    "transformed_target_fraction": transformed_target_fraction,
                    "transformed_target": transformed_target,
                    "transformed_guard_fractions": transformed_guard_fractions,
                    "source_nonzero_guards": dict(nonzero_guards),
                    "transformed_guards": transformed_guards,
                    "elimination": eliminated,
                }
                rows.append(row)
                outcomes.append(
                    {
                        **outcome,
                        "state": "success",
                        "route_mode": eliminated["mode"],
                    }
                )
            except Exception as error:
                outcomes.append(
                    {
                        **outcome,
                        "state": "failed_closed",
                        "error": f"{type(error).__name__}: {error}",
                    }
                )
    if not rows:
        raise ValueError("unit-circle transforms produced no strictly smaller exact route")
    selected = min(
        rows,
        key=lambda row: (
            row["elimination"]["profile"]["symbol_count"],
            len(row["elimination"]["generators"]),
            row["elimination"]["profile"]["maximum_total_degree"],
            row["elimination"]["profile"]["total_monomial_count"],
            row["elimination"]["mode"],
            row["orientation"],
        ),
    )
    return {
        "schema": "cognitive-well-v0282-unit-circle-laurent-elimination-v2",
        "detected_circle_candidates": circle_candidates,
        "circle_sets": circle_sets,
        "detected_circles": selected["circles"],
        "circle_set_count": len(circle_sets),
        "orientation_attempted_count": sum(2 ** len(rows) for rows in circle_sets),
        "orientation_success_count": len(rows),
        "orientation_count": sum(2 ** len(rows) for rows in circle_sets),
        "orientation_outcomes": outcomes,
        "selected": selected,
    }


def _gaussian(value: Any) -> dict[str, int]:
    value = sp.expand(value)
    real, imaginary = value.as_real_imag()
    real = sp.Rational(real)
    imaginary = sp.Rational(imaginary)
    return {
        "real_numerator": int(real.p),
        "real_denominator": int(real.q),
        "imaginary_numerator": int(imaginary.p),
        "imaginary_denominator": int(imaginary.q),
    }


def _payload(expression: sp.Expr, symbols: list[sp.Symbol]) -> dict[str, Any]:
    polynomial = _poly(expression, symbols)
    return {
        "terms": [
            {"powers": list(powers), "coefficient": _gaussian(coefficient)}
            for powers, coefficient in polynomial.terms()
        ],
        "term_count": len(polynomial.terms()),
        "degree": -1 if polynomial.is_zero else int(polynomial.total_degree()),
    }


def principal_identity_certificate(
    *,
    generator: tuple[str, sp.Expr],
    target: sp.Expr,
    symbols: list[sp.Symbol],
    transform_sha256: str,
) -> dict[str, Any]:
    """Build a replayable exact certificate for target in a principal ideal."""
    label, expression = generator
    quotient, remainder = sp.div(
        _poly(target, symbols), _poly(expression, symbols),
        domain=DOMAIN,
    )
    if not remainder.is_zero:
        raise ValueError("principal target division has a nonzero remainder")
    verified = _poly(
        target - quotient.as_expr() * expression, symbols
    ).is_zero
    if not verified:
        raise AssertionError("principal membership certificate failed re-expansion")
    payload = {
        "schema": "cognitive-well-v0282-principal-identity-certificate-v1",
        "coefficient_field": "QQ(i)",
        "transform_sha256": transform_sha256,
        "symbols": [str(symbol) for symbol in symbols],
        "generator_label": label,
        "identity": f"target = quotient * {label}",
        "quotient": _payload(quotient.as_expr(), symbols),
        "remainder_zero": True,
        "reexpansion_zero": True,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["certificate_sha256"] = hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()
    return payload


def full_lift_certificate(
    *,
    validated: Mapping[str, Any],
    transformed: Mapping[str, Any],
    source_arguments_sha256: str,
    guard_program_sha256: str,
    exact_transformation_validation_sha256: str,
    transform_sha256: str,
) -> dict[str, Any]:
    """Replay the complete derived-system implication back to the source.

    The certificate covers the unit-circle parametrization, every Laurent
    denominator clearing, and the guarded linear elimination.  It deliberately
    contains no precomputed target certificate: all identities are rebuilt from
    the supplied validated request and selected deterministic transform.
    """

    selected = transformed["selected"]
    elimination = selected["elimination"]
    source_symbols = [
        validated["symbol_map"][name] for name in validated["symbols"]
    ]
    derived_symbols = list(elimination["symbols"])
    all_derived_symbols = list(derived_symbols)
    if elimination["variable"] is not None:
        all_derived_symbols.append(elimination["variable"])

    def factor_rows(expression: sp.Expr, symbols: list[sp.Symbol]) -> list[dict[str, Any]]:
        polynomial = _poly(expression, symbols)
        if polynomial.is_zero:
            raise ValueError("zero cannot occur in a nonzero-factor certificate")
        if polynomial.total_degree() == 0:
            return []
        _, factors = sp.factor_list(
            polynomial.as_expr(), *symbols, extension=sp.I
        )
        return [
            {
                "key": _key(factor, symbols),
                "expression": sp.sstr(_canonical(factor, symbols)),
                "multiplicity": int(multiplicity),
            }
            for factor, multiplicity in factors
        ]

    unit_guard_keys = {
        _key(unit, all_derived_symbols): label
        for label, unit in selected["transformed_guards"].items()
        if label.startswith("unit_guard_")
    }

    circle_rows = []
    for circle in selected["circles"]:
        first, second = circle["coordinates"]
        substituted = sp.cancel(
            (first**2 + second**2 - 1).subs(selected["substitutions"])
        )
        if substituted != 0:
            raise AssertionError("circle substitution did not replay")
        unit = next(
            value
            for value, expression in selected["inverse_substitutions"].items()
            if expression in {second + sp.I * first, first + sp.I * second}
        )
        # Symbols are algebraic indeterminates, so explicit conjugation is not
        # useful here.  Record and verify the polynomial inverse factor directly.
        odd_index = selected["orientation"][selected["circles"].index(circle)]
        odd = circle["coordinates"][odd_index]
        even = circle["coordinates"][1 - odd_index]
        inverse_factor = even - sp.I * odd
        inverse_identity = sp.expand(
            (even + sp.I * odd) * inverse_factor
            - (first**2 + second**2)
        )
        if inverse_identity != 0:
            raise AssertionError("unit inverse identity did not replay")
        circle_rows.append(
            {
                "label": circle["label"],
                "coordinates": [str(first), str(second)],
                "unit": str(unit),
                "orientation": int(odd_index),
                "substitution_identity_zero": True,
                "source_inverse_identity": (
                    f"{unit} * ({sp.sstr(inverse_factor)}) = "
                    f"{sp.sstr(first**2 + second**2)}"
                ),
                "source_circle_makes_unit_nonzero": True,
            }
        )

    rational_rows = []
    for label, source_polynomial in validated["generators"].items():
        if label in {row["label"] for row in selected["circles"]}:
            continue
        numerator, denominator = selected["transformed_generator_fractions"][label]
        replay = sp.cancel(
            source_polynomial.as_expr().subs(selected["substitutions"])
            - numerator / denominator
        )
        if replay != 0:
            raise AssertionError(f"generator {label} Laurent lift did not replay")
        rational_rows.append(
            {
                "kind": "generator",
                "label": label,
                "numerator": _payload(numerator, all_derived_symbols),
                "denominator": _payload(denominator, all_derived_symbols),
                "denominator_factors": factor_rows(
                    denominator, all_derived_symbols
                ),
                "rational_identity_zero": True,
            }
        )
    target_numerator, target_denominator = selected["transformed_target_fraction"]
    if sp.cancel(
        validated["target"].as_expr().subs(selected["substitutions"])
        - target_numerator / target_denominator
    ) != 0:
        raise AssertionError("target Laurent lift did not replay")
    rational_rows.append(
        {
            "kind": "target",
            "label": "target",
            "numerator": _payload(target_numerator, all_derived_symbols),
            "denominator": _payload(target_denominator, all_derived_symbols),
            "denominator_factors": factor_rows(
                target_denominator, all_derived_symbols
            ),
            "rational_identity_zero": True,
        }
    )
    for row in rational_rows:
        uncovered = [
            factor
            for factor in row["denominator_factors"]
            if factor["key"] not in unit_guard_keys
        ]
        if uncovered:
            raise ValueError(
                f"{row['label']} Laurent denominator has an unguarded factor"
            )
        row["denominator_guard_coverage"] = [
            {
                "factor_key": factor["key"],
                "guard_label": unit_guard_keys[factor["key"]],
            }
            for factor in row["denominator_factors"]
        ]
        row["denominator_factors_all_guarded_nonzero"] = True

    transformed_guard_rows = []
    for label, source_guard in selected["source_nonzero_guards"].items():
        numerator, denominator = selected["transformed_guard_fractions"][label]
        if sp.cancel(
            source_guard.subs(selected["substitutions"])
            - numerator / denominator
        ) != 0:
            raise AssertionError(f"guard {label} Laurent lift did not replay")
        denominator_factors = factor_rows(denominator, all_derived_symbols)
        uncovered = [
            factor
            for factor in denominator_factors
            if factor["key"] not in unit_guard_keys
        ]
        if uncovered:
            raise ValueError(f"guard {label} has an unguarded Laurent denominator")
        transformed_guard_rows.append(
            {
                "label": label,
                "numerator": _payload(numerator, all_derived_symbols),
                "denominator": _payload(denominator, all_derived_symbols),
                "denominator_factors": denominator_factors,
                "denominator_guard_coverage": [
                    {
                        "factor_key": factor["key"],
                        "guard_label": unit_guard_keys[factor["key"]],
                    }
                    for factor in denominator_factors
                ],
                "rational_identity_zero": True,
                "denominator_factors_all_guarded_nonzero": True,
            }
        )

    if elimination["mode"] == "guarded_linear_elimination":
        pivot = elimination["pivot"]
        pivot_expression = sp.expand(
            pivot["coefficient"] * elimination["variable"] + pivot["constant"]
        )
        compatibility_rows = []
        derived_map = dict(elimination["generators"])
        for row in elimination["linear_rows"]:
            if row["label"] == pivot["label"]:
                continue
            label = f"compat_{pivot['label']}_{row['label']}"
            compatibility = derived_map[label]
            identity = sp.expand(
                pivot["coefficient"]
                * (row["coefficient"] * elimination["variable"] + row["constant"])
                - row["coefficient"] * pivot_expression
                - compatibility
            )
            if identity != 0:
                raise AssertionError(f"linear compatibility {label} did not replay")
            compatibility_rows.append(
                {
                    "label": label,
                    "source_linear_generator": row["label"],
                    "identity": (
                        "pivot_coefficient * source_linear_generator - "
                        "source_coefficient * pivot_generator = compatibility"
                    ),
                    "reexpansion_zero": True,
                }
            )

        target_degree = int(
            sp.Poly(
                selected["transformed_target"], elimination["variable"], domain="EX"
            ).degree()
        )
        target_lhs = sp.expand(
            pivot["coefficient"] ** target_degree
            * selected["transformed_target"]
            - elimination["target"]
        )
        quotient, remainder = sp.div(
            sp.Poly(target_lhs, elimination["variable"], domain="EX"),
            sp.Poly(pivot_expression, elimination["variable"], domain="EX"),
        )
        if not remainder.is_zero or sp.expand(
            target_lhs - quotient.as_expr() * pivot_expression
        ) != 0:
            raise AssertionError("linear target lift did not replay")

        guard_factor_owners: dict[str, list[str]] = {}
        for label, expression in selected["transformed_guards"].items():
            if elimination["variable"] in expression.free_symbols:
                continue
            for factor in factor_rows(expression, derived_symbols):
                guard_factor_owners.setdefault(factor["key"], []).append(label)
        pivot_factors = factor_rows(pivot["coefficient"], derived_symbols)
        pivot_coverage = [
            {
                "factor_key": factor["key"],
                "factor_expression": factor["expression"],
                "guard_labels": sorted(guard_factor_owners.get(factor["key"], [])),
            }
            for factor in pivot_factors
        ]
        if any(not row["guard_labels"] for row in pivot_coverage):
            raise ValueError(
                "pivot coefficient has a factor without typed/unit guard coverage"
            )
        linear_payload = {
            "mode": "guarded_linear_elimination",
            "performed": True,
            "variable": str(elimination["variable"]),
            "pivot_label": pivot["label"],
            "pivot_coefficient": _payload(pivot["coefficient"], derived_symbols),
            "pivot_coefficient_expression": sp.sstr(pivot["coefficient"]),
            "pivot_generator_expression": sp.sstr(pivot_expression),
            "pivot_coefficient_guarded_nonzero": True,
            "pivot_factor_guard_coverage": pivot_coverage,
            "compatibility_identities": compatibility_rows,
            "target_identity": (
                "pivot_coefficient^degree * transformed_target - "
                "derived_target = quotient * pivot_generator"
            ),
            "target_degree": target_degree,
            "transformed_candidate_target_expression": sp.sstr(
                selected["transformed_target"]
            ),
            "derived_target_expression": sp.sstr(elimination["target"]),
            "target_quotient": _payload(quotient.as_expr(), all_derived_symbols),
            "target_quotient_expression": sp.sstr(quotient.as_expr()),
            "target_reexpansion_zero": True,
        }
    elif elimination["mode"] == "laurent_only":
        if sp.expand(selected["transformed_target"] - elimination["target"]) != 0:
            raise AssertionError("Laurent-only target identity did not replay")
        linear_payload = {
            "mode": "laurent_only",
            "performed": False,
            "variable": None,
            "pivot_label": None,
            "pivot_coefficient_guarded_nonzero": None,
            "pivot_factor_guard_coverage": [],
            "compatibility_identities": [],
            "target_identity": "transformed_target = derived_target",
            "target_degree": None,
            "transformed_candidate_target_expression": sp.sstr(
                selected["transformed_target"]
            ),
            "derived_target_expression": sp.sstr(elimination["target"]),
            "target_quotient": None,
            "target_quotient_expression": None,
            "target_reexpansion_zero": True,
        }
    else:
        raise ValueError("unknown Laurent elimination mode")

    payload = {
        "schema": "cognitive-well-v0282-full-source-lift-certificate-v1",
        "coefficient_field": "QQ(i)",
        "source_arguments_sha256": source_arguments_sha256,
        "guard_program_sha256": guard_program_sha256,
        "exact_transformation_validation_sha256": (
            exact_transformation_validation_sha256
        ),
        "transform_sha256": transform_sha256,
        "circle_set_index": selected["circle_set_index"],
        "selected_orientation": list(selected["orientation"]),
        "circle_identities": circle_rows,
        "laurent_rational_identities": rational_rows,
        "transformed_source_guard_identities": transformed_guard_rows,
        "linear_elimination": linear_payload,
        "implication_replay": {
            "source_equations_to_derived_equations": True,
            "derived_target_to_source_target_under_recorded_nonzero_guards": True,
            "all_circle_pairs_substituted_simultaneously": True,
        },
        "verified": True,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["certificate_sha256"] = hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()
    return payload


def json_transform(result: Mapping[str, Any]) -> dict[str, Any]:
    selected = result["selected"]
    eliminated = selected["elimination"]
    symbols = list(eliminated["symbols"])
    payload = {
        "schema": result["schema"],
        "detected_circles": [
            {
                "label": row["label"],
                "coordinates": [str(symbol) for symbol in row["coordinates"]],
            }
            for row in result["detected_circles"]
        ],
        "detected_circle_candidates": [
            {
                "label": row["label"],
                "coordinates": [str(symbol) for symbol in row["coordinates"]],
            }
            for row in result["detected_circle_candidates"]
        ],
        "circle_sets": [
            [
                {
                    "label": row["label"],
                    "coordinates": [str(symbol) for symbol in row["coordinates"]],
                }
                for row in rows
            ]
            for rows in result["circle_sets"]
        ],
        "circle_set_count": result["circle_set_count"],
        "orientation_attempted_count": result["orientation_attempted_count"],
        "orientation_success_count": result["orientation_success_count"],
        "orientation_count": result["orientation_count"],
        "orientation_outcomes": [
            {
                **row,
                "orientation": list(row["orientation"]),
            }
            for row in result["orientation_outcomes"]
        ],
        "selected_circle_set_index": selected["circle_set_index"],
        "selected_orientation": list(selected["orientation"]),
        "route_mode": eliminated["mode"],
        "eliminated_variable": (
            None if eliminated["variable"] is None else str(eliminated["variable"])
        ),
        "pivot_label": (
            None if eliminated["pivot"] is None else eliminated["pivot"]["label"]
        ),
        "symbols": [str(symbol) for symbol in symbols],
        "profile": eliminated["profile"],
        "generators": {
            label: _payload(expression, symbols)
            for label, expression in eliminated["generators"]
        },
        "target": _payload(eliminated["target"], symbols),
        "guards": {
            label: _payload(expression, symbols)
            for label, expression in selected["transformed_guards"].items()
            if eliminated["variable"] is None
            or eliminated["variable"] not in expression.free_symbols
        },
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["transform_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return payload
