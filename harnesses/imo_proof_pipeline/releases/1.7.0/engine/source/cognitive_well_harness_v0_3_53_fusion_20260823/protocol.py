from __future__ import annotations

import hashlib
from typing import Any


SYSTEM_PROMPT = r"""You are the Fusion Judge: an expert mathematical proof adjudicator
for Olympiad-level mathematics. You have expert command of the mathematical domain
required by the problem.

REASONING EFFORT: MAXIMAL. Thinking mode is on. Perform the complete mathematical
adjudication privately before producing the required final record.

You adjudicate a submitted proof; you do not rewrite it. The input contains the
Olympiad problem, the complete candidate proof, and three independent final reviewer
records. Read the problem and proof completely before relying on any report.

First perform a blind audit without using the reviewer reports. Reconstruct the
essential route, list its proof obligations, and check them in logical order. In
particular, recompute displayed equalities and numerical witnesses; check domains,
quantifiers, boundary cases, exhaustive relabeling or case choices, and the legality
and count of constructed objects or moves. Only then inspect and adjudicate the three
reviewer records.

The reviewers have different roles:

- Reviewer 1 is an earliest-break locator. FIRST_BREAK submits a defect hypothesis.
  NO_FIRST_BREAK means only that Reviewer 1 found no break.
- Reviewer 2 is an adversarial falsifier. ADVERSARIAL_BREAK submits its strongest
  surviving falsification hypothesis; it cannot reject the proof by itself.
  NO_ADVERSARIAL_BREAK means only that it found no verified attack.
- Reviewer 3 is a charitable proof certifier. CERTIFICATION_FAILURE submits an
  unclosed-obligation hypothesis. NO_UNCLOSED_OBLIGATION_FOUND means only that it
  found no essential obligation unclosed after charitable review.

Do not decide by vote, agreement, model identity, confidence language, or report
length. One independently verified defect can outweigh two no-defect reports. Three
no-defect reports cannot justify acceptance without your blind audit. Conversely, a
submitted objection cannot affect the verdict unless you validate its exact claim,
witness, hypotheses, arithmetic, and implication for the proof.

Use input-aware reviewer-assessment labels:

- If a reviewer submitted FIRST_BREAK, ADVERSARIAL_BREAK, or CERTIFICATION_FAILURE,
  use exactly one of DEFECT_VALIDATED, DEFECT_REJECTED, or DEFECT_UNRESOLVED.
- If a reviewer submitted NO_FIRST_BREAK, NO_ADVERSARIAL_BREAK, or
  NO_UNCLOSED_OBLIGATION_FOUND, use exactly NO_DEFECT_REPORTED when your audit found
  no defect missed by that reviewer, or REVIEWER_MISSED_DEFECT when your audit found
  a specific defect that reviewer missed.
- Never describe a no-defect report as though it had asserted a claim that you
  refuted. Judge the record that was actually submitted.

Apply this proof standard:

- Accept correctly applicable standard Olympiad results and harmless exposition
  choices.
- Do not demand unnecessary detail or penalize style.
- Do not invent a substantial lemma, import an external solution, assume the desired
  conclusion, or silently replace the proof's essential strategy.
- A routine completion must be unique or canonical from established material and
  require no new idea, nontrivial lemma, missing essential case, quantifier change,
  or strategy change. Permitted examples are an explicit harmless relabeling, one
  standard lemma invocation with already-verified hypotheses, or an isolated local
  algebra/transcription correction whose intended valid statement follows
  immediately and leaves every downstream inference intact.
- A false assertion, illegal construction, missing essential case, circular step,
  quantifier error, unsupported nontrivial implication, or non-canonical repair is a
  material defect and requires Resolver work.

Choose exactly one verdict:

ACCEPT_AS_WRITTEN: The submitted text is literally complete and correct by Olympiad
standards. No mathematical correction or completion is needed. All submitted defect
hypotheses are rejected, all no-defect reports missed nothing, and your blind audit
finds no defect.

ACCEPT_WITH_ROUTINE_COMPLETION: The conclusion and essential proof strategy are
correct, but the text needs one or more precisely stated routine completions under
the strict criteria above. State the exact local completion and verify that it closes
the proof. Do not use this verdict to excuse a new idea, a nontrivial missing lemma,
an essential missing case, or a structural change.

REPAIR_NEEDED: At least one independently validated material defect must be corrected
by the separate Resolver. Specify a Resolver brief, but do not perform the repair or
supply replacement proof text.

INCONCLUSIVE: A precise material obligation remains genuinely unresolved after
maximal effort. Reviewer disagreement alone is insufficient. State exactly what
would resolve it.

Stress-test your intended verdict before finalizing. Do not output a rewritten proof,
alternative solution, score, probability, private reasoning, or general commentary.
Keep every field on one physical line.

If the verdict is ACCEPT_AS_WRITTEN, output exactly:

FUSION_ACCEPT_AS_WRITTEN
verdict: ACCEPT_AS_WRITTEN
reviewer_1_assessment: <permitted input-aware label> | <brief mathematical reason>
reviewer_2_assessment: <permitted input-aware label> | <brief mathematical reason>
reviewer_3_assessment: <permitted input-aware label> | <brief mathematical reason>
independent_acceptance_basis: <why the essential proof route and obligations are valid>
literal_completeness_check: <why no mathematical correction or completion is needed>
END_FUSION_ACCEPT_AS_WRITTEN

If the verdict is ACCEPT_WITH_ROUTINE_COMPLETION, output exactly:

FUSION_ACCEPT_WITH_ROUTINE_COMPLETION
verdict: ACCEPT_WITH_ROUTINE_COMPLETION
reviewer_1_assessment: <permitted input-aware label> | <brief mathematical reason>
reviewer_2_assessment: <permitted input-aware label> | <brief mathematical reason>
reviewer_3_assessment: <permitted input-aware label> | <brief mathematical reason>
completion_location: <exact quotation or unambiguous local location>
routine_completion: <the exact local correction, relabeling, or standard justification>
why_routine: <why it is canonical and introduces no new idea, lemma, case, or strategy>
validation_after_completion: <why all downstream steps and the conclusion remain valid>
END_FUSION_ACCEPT_WITH_ROUTINE_COMPLETION

If the verdict is REPAIR_NEEDED, output exactly:

FUSION_REPAIR_NEEDED
verdict: REPAIR_NEEDED
reviewer_1_assessment: <permitted input-aware label> | <brief mathematical reason>
reviewer_2_assessment: <permitted input-aware label> | <brief mathematical reason>
reviewer_3_assessment: <permitted input-aware label> | <brief mathematical reason>
decisive_location: <exact quotation or unambiguous location in the candidate proof>
failed_obligation: <the precise claim or implication that is not established>
independent_validation: <your mathematical verification that the defect is real>
impact_on_proof: <why the submitted proof is not rigorous without Resolver work>
repair_scope: <LOCAL | STRUCTURAL>
resolver_brief: <minimum lemma, derivation, case analysis, or strategy change required>
preservable_material: <valid material or proof structure the Resolver may retain, or NONE>
END_FUSION_REPAIR_NEEDED

If the verdict is INCONCLUSIVE, output exactly:

FUSION_INCONCLUSIVE
verdict: INCONCLUSIVE
reviewer_1_assessment: <permitted input-aware label> | <brief mathematical reason>
reviewer_2_assessment: <permitted input-aware label> | <brief mathematical reason>
reviewer_3_assessment: <permitted input-aware label> | <brief mathematical reason>
unresolved_obligation: <the precise mathematical question that remains unresolved>
evidence_for_acceptance: <strongest established support for the candidate proof>
evidence_for_repair: <strongest established reason the proof may require Resolver work>
resolution_needed: <the exact derivation, lemma, computation, or case check needed>
END_FUSION_INCONCLUSIVE

Return only the required record. Perform all analysis privately."""


ASSESSMENTS = {
    "DEFECT_VALIDATED",
    "DEFECT_REJECTED",
    "DEFECT_UNRESOLVED",
    "NO_DEFECT_REPORTED",
    "REVIEWER_MISSED_DEFECT",
}

ASSESSMENT_ALIASES = {
    "reviewer_1_assessment": {"NO_FIRST_BREAK": "NO_DEFECT_REPORTED"},
    "reviewer_2_assessment": {"NO_ADVERSARIAL_BREAK": "NO_DEFECT_REPORTED"},
    "reviewer_3_assessment": {
        "NO_UNCLOSED_OBLIGATION_FOUND": "NO_DEFECT_REPORTED",
        "PROOF_CERTIFIED": "NO_DEFECT_REPORTED",
    },
}

DEFECT_SOURCE_OUTCOMES = {
    "FIRST_BREAK",
    "ADVERSARIAL_BREAK",
    "CERTIFICATION_FAILURE",
}
NO_DEFECT_SOURCE_OUTCOMES = {
    "NO_FIRST_BREAK",
    "NO_ADVERSARIAL_BREAK",
    "NO_UNCLOSED_OBLIGATION_FOUND",
    "PROOF_CERTIFIED",
}
DEFECT_ASSESSMENTS = {
    "DEFECT_VALIDATED",
    "DEFECT_REJECTED",
    "DEFECT_UNRESOLVED",
}
NO_DEFECT_ASSESSMENTS = {
    "NO_DEFECT_REPORTED",
    "REVIEWER_MISSED_DEFECT",
}

SCHEMAS = {
    "FUSION_ACCEPT_AS_WRITTEN": {
        "footer": "END_FUSION_ACCEPT_AS_WRITTEN",
        "verdict": "ACCEPT_AS_WRITTEN",
        "fields": (
            "verdict",
            "reviewer_1_assessment",
            "reviewer_2_assessment",
            "reviewer_3_assessment",
            "independent_acceptance_basis",
            "literal_completeness_check",
        ),
    },
    "FUSION_ACCEPT_WITH_ROUTINE_COMPLETION": {
        "footer": "END_FUSION_ACCEPT_WITH_ROUTINE_COMPLETION",
        "verdict": "ACCEPT_WITH_ROUTINE_COMPLETION",
        "fields": (
            "verdict",
            "reviewer_1_assessment",
            "reviewer_2_assessment",
            "reviewer_3_assessment",
            "completion_location",
            "routine_completion",
            "why_routine",
            "validation_after_completion",
        ),
    },
    "FUSION_REPAIR_NEEDED": {
        "footer": "END_FUSION_REPAIR_NEEDED",
        "verdict": "REPAIR_NEEDED",
        "fields": (
            "verdict",
            "reviewer_1_assessment",
            "reviewer_2_assessment",
            "reviewer_3_assessment",
            "decisive_location",
            "failed_obligation",
            "independent_validation",
            "impact_on_proof",
            "repair_scope",
            "resolver_brief",
            "preservable_material",
        ),
    },
    "FUSION_INCONCLUSIVE": {
        "footer": "END_FUSION_INCONCLUSIVE",
        "verdict": "INCONCLUSIVE",
        "fields": (
            "verdict",
            "reviewer_1_assessment",
            "reviewer_2_assessment",
            "reviewer_3_assessment",
            "unresolved_obligation",
            "evidence_for_acceptance",
            "evidence_for_repair",
            "resolution_needed",
        ),
    },
}


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def fusion_user_prompt(
    *,
    problem: str,
    proof: str,
    reviewer_1: str,
    reviewer_2: str,
    reviewer_3: str,
) -> str:
    values = (problem, proof, reviewer_1, reviewer_2, reviewer_3)
    if any(not value.strip() for value in values):
        raise ValueError("all fusion inputs must be nonempty")
    return (
        "# FUSION INPUT\n\n"
        "## OLYMPIAD PROBLEM\n"
        f"{problem.strip()}\n\n"
        "## CANDIDATE PROOF\n"
        f"{proof.strip()}\n\n"
        "## REVIEWER 1 — EARLIEST-BREAK RECORD\n"
        f"{reviewer_1.strip()}\n\n"
        "## REVIEWER 2 — ADVERSARIAL-FALSIFICATION RECORD\n"
        f"{reviewer_2.strip()}\n\n"
        "## REVIEWER 3 — CHARITABLE-CERTIFICATION RECORD\n"
        f"{reviewer_3.strip()}\n\n"
        "## ALLOWED MATERIAL\n"
        "Use only the problem statement, candidate proof, reviewer records, and "
        "correctly applicable standard Olympiad-level mathematics. No official "
        "solution, score, gold label, aggregate reviewer-performance information, "
        "reviewer private reasoning, raw response, or reviewer system prompt is "
        "supplied.\n"
    )


def _assessment_labels(fields: dict[str, str]) -> list[str]:
    return [
        fields.get(f"reviewer_{reviewer}_assessment", "").partition(" | ")[0]
        for reviewer in (1, 2, 3)
    ]


def parse_fusion(value: str) -> dict[str, Any]:
    text = value.strip()
    lines = text.splitlines()
    if len(lines) < 3 or lines[0] not in SCHEMAS:
        return {
            "valid": False,
            "errors": ["output does not start with a permitted fusion record"],
            "outcome": None,
            "fields": None,
            "final": text,
            "normalized_final": None,
        }
    schema = SCHEMAS[lines[0]]
    errors: list[str] = []
    if lines[-1] != schema["footer"]:
        errors.append(f"record must end with {schema['footer']}")
    body = lines[1:-1]
    expected = schema["fields"]
    if len(body) != len(expected):
        errors.append(f"expected {len(expected)} fields, found {len(body)}")
    fields: dict[str, str] = {}
    for index, name in enumerate(expected):
        if index >= len(body):
            break
        prefix = name + ": "
        if not body[index].startswith(prefix):
            errors.append(f"field {index + 1} must be {name}")
            continue
        field = body[index][len(prefix):].strip()
        fields[name] = field
        if not field or (field.startswith("<") and field.endswith(">")):
            errors.append(f"{name} was empty or a placeholder")
    if fields.get("verdict") != schema["verdict"]:
        errors.append(f"verdict must be {schema['verdict']}")
    for reviewer in (1, 2, 3):
        name = f"reviewer_{reviewer}_assessment"
        field = fields.get(name, "")
        original_label, separator, reason = field.partition(" | ")
        label = ASSESSMENT_ALIASES.get(name, {}).get(original_label, original_label)
        if label not in ASSESSMENTS or not separator or not reason.strip():
            errors.append(f"{name} must contain a permitted label and reason")
        elif label != original_label:
            fields[name] = f"{label} | {reason.strip()}"
    labels = _assessment_labels(fields)
    verdict = str(schema["verdict"])
    real_findings = {"DEFECT_VALIDATED", "REVIEWER_MISSED_DEFECT"}
    if verdict == "ACCEPT_AS_WRITTEN" and any(
        label in real_findings | {"DEFECT_UNRESOLVED"} for label in labels
    ):
        errors.append("ACCEPT_AS_WRITTEN cannot contain a validated, missed, or unresolved defect")
    if verdict in {"ACCEPT_WITH_ROUTINE_COMPLETION", "REPAIR_NEEDED"} and not any(
        label in real_findings for label in labels
    ):
        errors.append(f"{verdict} requires at least one validated or independently missed defect")
    if verdict == "ACCEPT_WITH_ROUTINE_COMPLETION" and "DEFECT_UNRESOLVED" in labels:
        errors.append("routine completion cannot contain an unresolved defect")
    if verdict == "INCONCLUSIVE" and "DEFECT_UNRESOLVED" not in labels:
        errors.append("INCONCLUSIVE requires at least one unresolved submitted defect")
    if lines[0] == "FUSION_REPAIR_NEEDED" and fields.get("repair_scope") not in {
        "LOCAL",
        "STRUCTURAL",
    }:
        errors.append("repair_scope must be LOCAL or STRUCTURAL")
    normalized_final = None
    if not errors:
        normalized_final = "\n".join(
            [lines[0]]
            + [f"{name}: {fields[name]}" for name in expected]
            + [str(schema["footer"])]
        )
    return {
        "valid": not errors,
        "errors": errors,
        "outcome": schema["verdict"] if not errors else None,
        "fields": fields,
        "final": text,
        "normalized_final": normalized_final,
    }


def validate_assessment_semantics(
    parsed: dict[str, Any], reviewer_outcomes: dict[str, str]
) -> dict[str, Any]:
    if not parsed.get("valid"):
        return parsed
    errors: list[str] = []
    fields = dict(parsed["fields"])
    for reviewer in (1, 2, 3):
        name = f"reviewer_{reviewer}"
        field_name = f"{name}_assessment"
        source_outcome = reviewer_outcomes.get(name)
        label = fields[field_name].partition(" | ")[0]
        if source_outcome in DEFECT_SOURCE_OUTCOMES:
            allowed = DEFECT_ASSESSMENTS
        elif source_outcome in NO_DEFECT_SOURCE_OUTCOMES:
            allowed = NO_DEFECT_ASSESSMENTS
        else:
            errors.append(f"unknown {name} source outcome: {source_outcome}")
            continue
        if label not in allowed:
            errors.append(
                f"{field_name} label {label} is incompatible with source outcome "
                f"{source_outcome}; allowed: {sorted(allowed)}"
            )
    if not errors:
        return parsed
    return {
        **parsed,
        "valid": False,
        "errors": list(parsed.get("errors") or []) + errors,
        "outcome": None,
        "normalized_final": None,
    }
