"""Lossless mathematical presentation of an already checked Laurent witness.

No theorem-specific identities, new ideal search, or model-written multipliers.
Horner rewriting and common-subexpression naming only shorten saved polynomials.
"""
from __future__ import annotations

import json
from pathlib import Path

import sympy as sp

from cognitive_well_harness_v0_3_282_unit_circle_laurent_elimination_20260905.integration import _decode_transform_payload
from cognitive_well_harness_v0_3_282_unit_circle_laurent_elimination_20260905.symbol_safety import FreshNames, parse_polynomial
from . import pipeline
from .certificate import validate_exact_replay
from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906.contracts import EvidenceBundle


_polynomial = parse_polynomial

STATEMENT_END = "\n\nWork over the complex numbers and put "


def audit_statement(markdown, verification):
    """Extract the unchanged statement from this renderer's verified output.

    This is an audit view, never a replacement for the submitted certificate.
    Unknown formats and changed certificates are rejected, not summarized.
    """
    if (verification.get("schema") != "cognitive-well-v0324-lossless-saved-witness-presentation-v1"
            or verification.get("verified") is not True
            or verification.get("horner_and_cse_reexpanded") is not True
            or verification.get("markdown_sha256") != pipeline.base.sha256_text(markdown)):
        raise ValueError("compact audit requires the unchanged verified saved witness")
    if markdown.count(STATEMENT_END) != 1:
        raise ValueError("saved witness has no unique renderer statement boundary")
    statement, _ = markdown.split(STATEMENT_END, 1)
    if (not statement.startswith("## Algebraic lemma\n\nAssume the following equations")
            or statement.count("We will prove that ") != 1):
        raise ValueError("saved witness statement format is unsupported")
    return statement


def _decode(payload, symbols):
    terms = []
    for term in payload["terms"]:
        if len(term["powers"]) != len(symbols):
            raise ValueError("saved polynomial arity mismatch")
        coefficient = term["coefficient"]
        terms.append((sp.Rational(coefficient["real_numerator"], coefficient["real_denominator"])
                  + sp.I * sp.Rational(coefficient["imaginary_numerator"], coefficient["imaginary_denominator"])) * sp.prod(
                      symbol ** power for symbol, power in zip(symbols, term["powers"], strict=True)))
    return sp.expand(sp.Add(*terms))


def _compact(expressions, symbols, *, namespace=None, factor_first=False):
    nested = []
    for index, value in enumerate(expressions, start=1):
        choices = [sp.horner(value, *symbols)]
        if factor_first:
            print(f"Factoring saved polynomial {index}/{len(expressions)} (presentation only).", flush=True)
            choices += [value, sp.factor(value, *symbols, extension=sp.I)]
        nested.append(min(choices, key=lambda item: len(sp.latex(item))))
    if any(sp.expand(old-new) != 0 for old, new in zip(expressions, nested, strict=True)):
        raise ValueError("Horner representation changed a saved polynomial")
    namespace = namespace or FreshNames(symbols)

    def abbreviations():
        index = 0
        while True:
            index += 1
            yield namespace.take(f"w{index}")

    definitions, compact = sp.cse(nested, abbreviations(), order="canonical")
    resolved = {}
    for symbol, expression in definitions:
        resolved[symbol] = expression.xreplace(resolved)
    if any(sp.expand(old-new.xreplace(resolved)) != 0 for old, new in zip(expressions, compact, strict=True)):
        raise ValueError("common-subexpression representation changed a saved polynomial")
    return definitions, compact


def render(context):
    replay = validate_exact_replay(context.replay_exact())
    identity_path = context.source_artifacts["membership_identity"]
    lift_path = context.source_artifacts["source_lift"]
    read = lambda path: json.loads(path.read_text(encoding="utf-8"))
    identity, lift = read(identity_path), read(lift_path)
    transform = read(identity_path.parent / "laurent_transform.json")
    guard_ledger = read(lift_path.parent / "typed_guard_binding.json")
    if pipeline.exact_tools.stable_hash(context.replay_formal_request()) != pipeline.exact_tools.stable_hash(context.arguments):
        raise ValueError("source formalization changed")
    return render_laurent(arguments=context.replay_formal_request(),lift=lift,transform=transform,
                          guard_ledger=guard_ledger,replay=replay,identity=identity)


def render_laurent(*,arguments,lift,transform,guard_ledger,replay,identity=None,radical_identity=None,
                   factor_first=False, table_multipliers=False):
    """Common source-to-Laurent exposition for ordinary or radical witnesses.

    Callers bind the saved lift to the accepted request before presentation.
    The renderer re-expands every newly introduced polynomial abbreviation.
    """
    if (identity is None)==(radical_identity is None):
        raise ValueError("exactly one ordinary or radical witness is required")
    symbols, generators, target, reduced_guards = _decode_transform_payload(transform)
    linear = lift["linear_elimination"]
    all_symbols = symbols + ([sp.Symbol(linear["variable"])] if linear["performed"] else [])
    validated = pipeline.exact_tools.validate_ideal_arguments(arguments)
    source_symbols = list(validated["symbol_map"].values())
    namespace = FreshNames(source_symbols + all_symbols)
    presentation_names = {}

    def ref(label):
        if label not in presentation_names:
            presentation_names[label] = namespace.take(label)
        return sp.latex(presentation_names[label])

    imaginary = ref("i")
    latex = lambda value: sp.latex(value, imaginary_unit=imaginary)
    source_labels = {label: ref(label) for label in validated["generators"]}
    target_name, coefficient_name, remainder_name, quotient_name = (ref(label) for label in ("T", "a", "R", "q"))
    lines = ["## Algebraic lemma", "Assume the following equations and nonzero conditions, in the variables displayed:"]
    lines += [f"\\[{source_labels[label]}={latex(value.as_expr())}=0.\\]"
              for label, value in validated["generators"].items()]
    lines += [f"\\[{ref(f'g_{index}')}={latex(_polynomial(row['expression'], source_symbols, complex_coefficients=False))}\\ne0.\\]"
              for index, row in enumerate(guard_ledger["eligible_records"], start=1)]
    guard_indices = {row["label"]: index for index, row in enumerate(guard_ledger["eligible_records"], start=1)}
    lines.append(f"We will prove that \\({target_name}={latex(validated['target'].as_expr())}=0\\).")
    lines.append(f"Work over the complex numbers and put \\({imaginary}^2=-1\\). For each of the following pairs, the displayed circle equation gives the inverse identity, so the new variable is nonzero:")
    nonzero_units = []
    for row in lift["circle_identities"]:
        if row["orientation"] not in (0, 1) or len(row["coordinates"]) != 2:
            raise ValueError("invalid saved circle coordinates or orientation")
        odd = sp.Symbol(row["coordinates"][row["orientation"]])
        even = sp.Symbol(row["coordinates"][1-row["orientation"]])
        unit = sp.Symbol(row["unit"])
        # Establish unit nonzeroness from an actual source equation, not a
        # symbol-name convention or a persisted boolean assertion.
        scale, remainder = sp.div(validated["generators"][row["label"]].as_expr(),
            even**2 + odd**2 - 1, *source_symbols, domain=sp.QQ)
        if (remainder != 0 or scale == 0 or scale.free_symbols
                or not {odd, even} <= set(source_symbols) or odd == even
                or unit not in symbols or unit in source_symbols):
            raise ValueError("saved unit inverse lacks a matching source circle equation")
        nonzero_units.append(unit)
        lines.append(f"\\[{latex(unit)}={latex(even+sp.I*odd)},\\quad {latex(unit)}({latex(even-sp.I*odd)})={latex(even**2+odd**2)}=1,\\quad {latex(odd)}=\\frac{{{latex(unit)}-{latex(unit)}^{{-1}}}}{{2{imaginary}}},\\quad {latex(even)}=\\frac{{{latex(unit)}+{latex(unit)}^{{-1}}}}{{2}}.\\]")
    numerators = {}
    indices = {}
    lines.append("Substitution and multiplication by the displayed monomial denominators give the following polynomial identities. All denominators are nonzero because they are nonzero constants times powers of the new variables.")
    for index, row in enumerate(lift["laurent_rational_identities"], start=1):
        numerator, denominator = _decode(row["numerator"], all_symbols), _decode(row["denominator"], all_symbols)
        label = row["label"]
        numerators[label], indices[label] = numerator, index
        left = target_name if row["kind"] == "target" else source_labels[label]
        n, h = ref(f"n_{index}"), ref(f"h_{index}")
        lines.append(f"\\[{n}={latex(numerator)},\\qquad {h}={latex(denominator)},\\qquad {h}({left})={n}.\\]")
    lines.append("Consequently all the displayed source numerators vanish. It remains to show that the target numerator vanishes.")
    guard_numerators = {}
    for row in lift["transformed_source_guard_identities"]:
        index = guard_indices[row["label"]]
        numerator, denominator = _decode(row["numerator"], all_symbols), _decode(row["denominator"], all_symbols)
        guard_numerators[row["label"]] = numerator
        b, g = ref(f"b_{index}"), ref(f"g_{index}")
        lines.append(f"\\[{b}={latex(numerator)},\\qquad ({latex(denominator)}){g}={b}\\ne0.\\]")
    if linear["performed"]:
        coefficient = _polynomial(linear["pivot_coefficient_expression"], all_symbols)
        pivot = numerators[linear["pivot_label"]]
        variable = sp.Symbol(linear["variable"])
        if sp.expand(sp.diff(pivot, variable)-coefficient) != 0:
            raise ValueError("saved pivot coefficient mismatch")
        constant, factors = sp.factor_list(coefficient, *symbols, extension=sp.I)
        witnesses = [(ref(f'b_{guard_indices[label]}'), numerator)
                     for label, numerator in guard_numerators.items()]
        witnesses += [(latex(unit), unit) for unit in nonzero_units]
        lines.append(f"Put \\({coefficient_name}={latex(coefficient)}={latex(constant*sp.Mul(*(sp.Pow(f, e, evaluate=False) for f, e in factors), evaluate=False))}\\). Every factor here is nonzero, as witnessed by these exact divisibilities of the nonzero guard numerators or the units established by the inverse identities above:")
        for factor, _ in factors:
            for witness_name, numerator in witnesses:
                quotient, remainder = sp.div(numerator, factor, *all_symbols, extension=sp.I)
                if numerator != 0 and remainder == 0:
                    lines.append(f"\\[{witness_name}=({latex(factor)})({latex(quotient)})\\ne0.\\]")
                    break
            else:
                raise ValueError("pivot factor has no displayed nonzero witness")
    lines.append("The following polynomials therefore vanish:")
    compatibility = {row["label"]: row for row in linear.get("compatibility_identities", [])}
    for index, (label, value) in enumerate(generators, start=1):
        if label in numerators:
            if sp.expand(value-numerators[label]) != 0:
                raise ValueError("saved unchanged generator mismatch")
            expression = ref(f"n_{indices[label]}")
        elif label in compatibility:
            source_label = compatibility[label]["source_linear_generator"]
            source_coefficient = sp.diff(numerators[source_label], variable)
            if sp.expand(value-(coefficient*numerators[source_label]-source_coefficient*pivot)) != 0:
                raise ValueError("saved compatibility identity mismatch")
            source_n = ref(f"n_{indices[source_label]}")
            pivot_n = ref(f"n_{indices[linear['pivot_label']]}")
            expression = f"{coefficient_name} {source_n}-({latex(source_coefficient)}){pivot_n}"
        else:
            raise ValueError("unsupported saved generator derivation")
        lines.append(f"\\[{ref(f'e_{index}')}={expression}=0.\\]")

    radical_abbreviations = 0
    if radical_identity is not None:
        from . import radical_certificate
        # The radical proof may use every retained transformed guard. Establish
        # each from a displayed source-guard numerator or a circle inverse.
        witnesses = list(guard_numerators.values()) + nonzero_units
        for guard in reduced_guards.values():
            if guard == 0 or not any(sp.expand(guard-witness)==0 for witness in witnesses):
                raise ValueError("reduced radical guard lacks a displayed source witness")
        lines.append("Each nonzero condition in the following sublemma is one of the nonzero guard numerators or units just established. Its equations are the vanishing polynomials displayed above.")
        for index in range(1,len(generators)+1):
            ref(f"e_{index}")
        radical_markdown, radical_record = radical_certificate.render(
            radical_certificate.system_payload(symbols,generators,target,reduced_guards),radical_identity,
            namespace=namespace,target_label=presentation_names["R"],
            source_labels=[presentation_names[f"e_{index}"] for index in range(1,len(generators)+1)],
            imaginary_unit=imaginary,factor_first=factor_first,table_multipliers=table_multipliers)
        lines.append(radical_markdown.replace("## Algebraic lemma","### Vanishing of the reduced target",1))
        radical_abbreviations = radical_record["abbreviation_count"]
        multipliers = []
        expressions = []
    else:
        multipliers = [_polynomial(identity["source_multipliers"][label], symbols) for label, _ in generators]
        if sp.expand(target-sum(m*g for m, (_, g) in zip(multipliers, generators, strict=True))) != 0:
            raise ValueError("saved membership identity no longer expands to zero")
        expressions = multipliers + [target]
    if linear["performed"]:
        quotient = _polynomial(linear["target_quotient_expression"], all_symbols)
        if sp.expand(coefficient**linear["target_degree"]*numerators["target"]-target-quotient*pivot) != 0:
            raise ValueError("saved target lift identity mismatch")
        expressions.append(quotient)
    for index in range(1, len(multipliers) + 1):
        ref(f"m_{index}")
    definitions, compact = _compact(expressions, all_symbols, namespace=namespace, factor_first=factor_first)
    if expressions:
        lines.append("For an explicit verification of the remaining algebra, use the following ordered abbreviations. Each right-hand side uses only original variables, the new nonzero variables, or earlier abbreviations:")
    lines += [f"\\[{latex(symbol)}={latex(value)}.\\]" for symbol, value in definitions]
    for index, value in enumerate(compact[:len(multipliers)], start=1):
        lines.append(f"\\[{ref(f'm_{index}')}={latex(value)}.\\]")
    if radical_identity is None:
        lines.append(f"\\[{remainder_name}={latex(compact[len(multipliers)])}.\\]")
        lines.append("Expanding these definitions gives the explicit polynomial identity")
        lines.append(f"\\[{remainder_name}=" + "+".join(f"{ref(f'm_{index}')}{ref(f'e_{index}')}" for index in range(1, len(multipliers)+1)) + "=0.\\]")
    if linear["performed"]:
        lines.append(f"Furthermore, with \\({quotient_name}={latex(compact[-1])}\\), expansion gives")
        target_n, pivot_n = ref(f"n_{indices['target']}"), ref(f"n_{indices[linear['pivot_label']]}")
        lines.append(f"\\[{coefficient_name}^{{{linear['target_degree']}}}{target_n}-{remainder_name}={quotient_name} {pivot_n}=0.\\]")
        lines.append(f"Since \\({coefficient_name}\\ne0\\), the target numerator is zero.")
    else:
        if sp.expand(numerators["target"]-target) != 0:
            raise ValueError("saved uneliminated target mismatch")
        target_n = ref(f"n_{indices['target']}")
        lines.append(f"Here \\({remainder_name}={target_n}\\), so the target numerator is zero.")
    nt, ht = ref(f"n_{indices['target']}"), ref(f"h_{indices['target']}")
    lines.append(f"Finally \\({ht}{target_name}={nt}=0\\) with \\({ht}\\ne0\\), and hence \\({target_name}=0\\), proving the lemma.")
    markdown = "\n\n".join(lines)
    if len(markdown) > (160_000 if table_multipliers else 120_000):
        raise ValueError("saved witness exceeds the fixed presentation budget")
    return markdown, {"verified": True, "schema": "cognitive-well-v0324-lossless-saved-witness-presentation-v1",
                      "exact_replay_sha256": pipeline.exact_tools.stable_hash(replay),
                      "new_ideal_search": False, "horner_and_cse_reexpanded": not table_multipliers,
                      "coefficient_tables_reparsed": table_multipliers,
                      "abbreviation_count": len(definitions)+radical_abbreviations, "markdown_characters": len(markdown),
                      "membership_kind": "guarded_radical" if radical_identity is not None else "ordinary",
                      "factor_first": factor_first,
                      "table_multipliers": table_multipliers,
                      "presentation_names": {key: str(value) for key, value in presentation_names.items()},
                      "target_label_latex": target_name,
                      "markdown_sha256": pipeline.base.sha256_text(markdown)}


class SavedWitnessProvider:
    provider_id = "lossless_saved_laurent_witness_v1"

    def __init__(self, context):
        self.context = context
        self.markdown, self.verification = render(context)

    def materialize(self):
        replay = validate_exact_replay(self.context.replay_exact())
        if pipeline.exact_tools.stable_hash(replay) != self.verification["exact_replay_sha256"]:
            raise ValueError("saved witness changed after presentation")
        if pipeline.base.sha256_text(self.markdown) != self.verification["markdown_sha256"]:
            raise ValueError("saved witness presentation changed after verification")
        return EvidenceBundle(self.provider_id, "VERIFIED_SUPPORT", self.markdown,
                              self.verification, {"operation": replay["operation"],
                              "claim": replay["claim"], "decision": "PROVED"}, self.context.source_artifacts)
