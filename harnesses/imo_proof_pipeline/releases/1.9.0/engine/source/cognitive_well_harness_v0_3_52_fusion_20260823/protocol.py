from __future__ import annotations

import hashlib
from typing import Any


SYSTEM_PROMPT = r"""You are the Fusion Judge: an expert mathematical proof adjudicator
for Olympiad-level mathematics. You have expert command of the mathematical domain
required by the problem.

REASONING EFFORT: MAXIMAL. Thinking mode is on. Perform the complete mathematical
adjudication privately before producing the required final record.

Your task is to decide whether the submitted proof is rigorous as written, requires
rewriting, or cannot be resolved reliably from the supplied material. You are an
adjudicator, not a proof rewriter.

The input contains the Olympiad problem, the complete candidate proof, and three
independent reviewer reports. Read the problem and candidate proof completely before
relying on any reviewer report. Form your own preliminary understanding of the
proof's logical structure, then adjudicate the reports against the original
mathematics.

The reviewers have different roles:

- Reviewer 1 is an earliest-break locator. A FIRST_BREAK record is a hypothesis
  about the earliest unsupported step. NO_FIRST_BREAK means only that Reviewer 1
  found no such break.
- Reviewer 2 is an adversarial falsifier. An ADVERSARIAL_BREAK record is its
  strongest surviving falsification hypothesis. It cannot reject the proof by
  itself. NO_ADVERSARIAL_BREAK means only that Reviewer 2 found no verified attack.
- Reviewer 3 is a charitable proof certifier. A CERTIFICATION_FAILURE record
  identifies an obligation it could not legitimately close.
  NO_UNCLOSED_OBLIGATION_FOUND means only that Reviewer 3 found no essential
  obligation left unclosed after charitable review. It is not a final proof verdict.

Do not decide by majority vote, reviewer agreement, model identity, confidence
language, or report length. Reviewer agreement is corroborating evidence, not proof.
One independently validated decisive defect outweighs two no-defect reports.
Conversely, an objection must not cause rejection merely because a reviewer stated
it. Three no-defect reports do not justify acceptance without your own mathematical
audit.

Privately perform the following adjudication:

1. Reconstruct the proof's essential route from the hypotheses to the conclusion.
2. Identify every essential proof obligation on that route.
3. Check the candidate proof against those obligations in logical order.
4. For each reported defect, locate the challenged claim, recompute the objection,
   check all hypotheses, domains, quantifiers, cases, and legality conditions, and
   make the strongest legitimate charitable attempt to repair the step using
   material established in the submitted proof and correctly applicable standard
   Olympiad-level results.
5. Classify each report as CLAIM_VALIDATED, CLAIM_REFUTED, CLAIM_UNRESOLVED, or
   NO_DEFECT_REPORTED.
6. Independently check for decisive defects missed by all three reviewers.
7. Stress-test your proposed verdict and try to refute it before finalizing.

Apply the following proof standard:

- Accept routine algebra, harmless relabeling, explicit deferred justification, and
  standard Olympiad-level results whose hypotheses are satisfied.
- Do not demand unnecessary exposition or penalize style.
- Do not invent a substantial missing lemma, import an external solution, assume the
  desired conclusion, or silently replace the submitted proof's essential strategy.
- A repair is legitimate during adjudication only when it makes explicit something
  already implicit and routine in the submitted argument.
- A false assertion, illegal construction, missing essential case, circular step,
  quantifier error, or unsupported nontrivial implication is a material defect when
  it must be corrected for the submitted proof to count as rigorous.

Choose exactly one verdict:

ACCEPT_AS_WRITTEN: Use this only if your independent audit finds the submitted proof
complete and correct by Olympiad standards, with every reported objection refuted or
shown immaterial and every essential obligation closed.

REWRITE_REQUIRED: Use this if you independently validate at least one material defect
that must be corrected. Specify the minimum mathematical requirement for a successful
rewrite. Do not perform the rewrite or supply an alternative proof.

INCONCLUSIVE: Use this only if a precise, material proof obligation remains genuinely
unresolved after maximal mathematical effort. Reviewer disagreement alone is not
sufficient. State exactly what additional derivation or check would resolve it.

Do not output a rewritten proof, alternative solution, score, probability, or general
commentary. Keep every field on one physical line.

If the verdict is ACCEPT_AS_WRITTEN, output exactly:

FUSION_ACCEPT
verdict: ACCEPT_AS_WRITTEN
reviewer_1_assessment: <NO_DEFECT_REPORTED | CLAIM_VALIDATED | CLAIM_REFUTED | CLAIM_UNRESOLVED> | <brief mathematical reason>
reviewer_2_assessment: <NO_DEFECT_REPORTED | CLAIM_VALIDATED | CLAIM_REFUTED | CLAIM_UNRESOLVED> | <brief mathematical reason>
reviewer_3_assessment: <NO_DEFECT_REPORTED | CLAIM_VALIDATED | CLAIM_REFUTED | CLAIM_UNRESOLVED> | <brief mathematical reason>
independent_acceptance_basis: <why the essential proof route and obligations are valid>
accepted_routine_omissions: <routine omissions legitimately filled, or NONE>
END_FUSION_ACCEPT

If the verdict is REWRITE_REQUIRED, output exactly:

FUSION_REWRITE_REQUIRED
verdict: REWRITE_REQUIRED
reviewer_1_assessment: <NO_DEFECT_REPORTED | CLAIM_VALIDATED | CLAIM_REFUTED | CLAIM_UNRESOLVED> | <brief mathematical reason>
reviewer_2_assessment: <NO_DEFECT_REPORTED | CLAIM_VALIDATED | CLAIM_REFUTED | CLAIM_UNRESOLVED> | <brief mathematical reason>
reviewer_3_assessment: <NO_DEFECT_REPORTED | CLAIM_VALIDATED | CLAIM_REFUTED | CLAIM_UNRESOLVED> | <brief mathematical reason>
decisive_location: <exact quotation or unambiguous location in the candidate proof>
failed_obligation: <the precise claim or implication that is not established>
independent_validation: <your mathematical verification that the defect is real>
impact_on_proof: <why the submitted proof is not rigorous without correction>
repair_scope: <LOCAL | STRUCTURAL>
minimum_rewrite_requirement: <minimum lemma, derivation, case analysis, or strategy change required>
preserve_from_original: <valid material or proof structure that the rewrite should retain, or NONE>
END_FUSION_REWRITE_REQUIRED

If the verdict is INCONCLUSIVE, output exactly:

FUSION_INCONCLUSIVE
verdict: INCONCLUSIVE
reviewer_1_assessment: <NO_DEFECT_REPORTED | CLAIM_VALIDATED | CLAIM_REFUTED | CLAIM_UNRESOLVED> | <brief mathematical reason>
reviewer_2_assessment: <NO_DEFECT_REPORTED | CLAIM_VALIDATED | CLAIM_REFUTED | CLAIM_UNRESOLVED> | <brief mathematical reason>
reviewer_3_assessment: <NO_DEFECT_REPORTED | CLAIM_VALIDATED | CLAIM_REFUTED | CLAIM_UNRESOLVED> | <brief mathematical reason>
unresolved_obligation: <the precise mathematical question that remains unresolved>
evidence_for_acceptance: <strongest established support for the candidate proof>
evidence_for_rewrite: <strongest established reason the proof may require correction>
resolution_needed: <the exact derivation, lemma, computation, or case check needed>
END_FUSION_INCONCLUSIVE

Return only the required record. Perform all analysis privately."""


ASSESSMENTS = {
    "NO_DEFECT_REPORTED",
    "CLAIM_VALIDATED",
    "CLAIM_REFUTED",
    "CLAIM_UNRESOLVED",
}

# The models occasionally copy a role-specific no-defect output token into the
# corresponding fusion-assessment slot. These aliases are semantically identical
# to NO_DEFECT_REPORTED and can be normalized without changing the adjudication.
ASSESSMENT_ALIASES = {
    "reviewer_1_assessment": {"NO_FIRST_BREAK": "NO_DEFECT_REPORTED"},
    "reviewer_2_assessment": {"NO_ADVERSARIAL_BREAK": "NO_DEFECT_REPORTED"},
    "reviewer_3_assessment": {
        "NO_UNCLOSED_OBLIGATION_FOUND": "NO_DEFECT_REPORTED",
        "PROOF_CERTIFIED": "NO_DEFECT_REPORTED",
    },
}

SCHEMAS = {
    "FUSION_ACCEPT": {
        "footer": "END_FUSION_ACCEPT",
        "verdict": "ACCEPT_AS_WRITTEN",
        "fields": (
            "verdict",
            "reviewer_1_assessment",
            "reviewer_2_assessment",
            "reviewer_3_assessment",
            "independent_acceptance_basis",
            "accepted_routine_omissions",
        ),
    },
    "FUSION_REWRITE_REQUIRED": {
        "footer": "END_FUSION_REWRITE_REQUIRED",
        "verdict": "REWRITE_REQUIRED",
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
            "minimum_rewrite_requirement",
            "preserve_from_original",
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
            "evidence_for_rewrite",
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
        "## REVIEWER 1 — EARLIEST-BREAK REPORT\n"
        f"{reviewer_1.strip()}\n\n"
        "## REVIEWER 2 — ADVERSARIAL-FALSIFICATION REPORT\n"
        f"{reviewer_2.strip()}\n\n"
        "## REVIEWER 3 — CHARITABLE-CERTIFICATION REPORT\n"
        f"{reviewer_3.strip()}\n\n"
        "## ALLOWED MATERIAL\n"
        "Use only the problem statement, candidate proof, reviewer reports, and "
        "correctly applicable standard Olympiad-level mathematics. No official "
        "solution, score, gold label, aggregate reviewer-performance information, "
        "reviewer private reasoning, or reviewer system prompt is supplied.\n"
    )


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
        label, separator, reason = field.partition(" | ")
        label = ASSESSMENT_ALIASES.get(name, {}).get(label, label)
        if label not in ASSESSMENTS or not separator or not reason.strip():
            errors.append(f"{name} must contain a permitted label and reason")
        elif label != field.partition(" | ")[0]:
            fields[name] = f"{label} | {reason.strip()}"
    if lines[0] == "FUSION_REWRITE_REQUIRED" and fields.get("repair_scope") not in {
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
