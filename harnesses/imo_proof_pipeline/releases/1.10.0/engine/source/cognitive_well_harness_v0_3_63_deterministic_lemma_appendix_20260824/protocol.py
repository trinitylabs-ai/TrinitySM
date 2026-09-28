from __future__ import annotations

import re
from typing import Any

from cognitive_well_harness_v0_3_62_dynamic_terminal_composition_20260824.protocol import (
    CASE_HEADING_RE,
    MAXIMUM_REASONING_DIRECTIVE,
)


LOCAL_LABELS = tuple(chr(ord("A") + index) for index in range(26))
LOCAL_LEMMA_REFERENCE_RE = re.compile(r"\bLemma\s+([A-Z])\b", re.IGNORECASE)
INTERNAL_ID_RE = re.compile(r"\bR\d+H\d+\b", re.IGNORECASE)


def label_lemmas(arguments: list[dict[str, str]]) -> list[dict[str, str]]:
    if len(arguments) > len(LOCAL_LABELS):
        raise ValueError("too many arguments for local appendix labels")
    return [
        {"label": LOCAL_LABELS[position], **argument}
        for position, argument in enumerate(arguments)
    ]


def main_proof_prompt(*, problem: str, lemmas: list[dict[str, str]]) -> str:
    statements = "\n\n".join(
        f"Lemma {row['label']}. {row['statement']}" for row in lemmas
    )
    allowed = ", ".join(f"Lemma {row['label']}" for row in lemmas)
    return f"""You are an expert olympiad mathematician composing the main body of one
final proof.
{MAXIMUM_REASONING_DIRECTIVE}

The lemma statements below were loaded dynamically from a prior verification artifact.
Their complete proof bodies are intentionally omitted from this call. After generation,
the harness will append the exact stored proof body of every lemma that your main proof
actually cites.

MAIN-PROOF CONTRACT
1. Produce a clean reader-facing main proof of the exact problem.
2. Re-derive all starting facts needed from the problem itself.
3. You may cite only these local reader-facing lemmas: {allowed}.
4. Cite every listed lemma at the precise point where its hypotheses have been proved
   and its conclusion is needed. State explicitly how the hypotheses are satisfied.
   Do not reproduce or attempt to summarize a lemma's proof in the main body.
5. Read the lemma hypotheses, identify the alternatives needed to apply them, and use
   explicit CASE 1, CASE 2, ... headings. Prove that the cases are exhaustive and
   complete every branch.
6. Do not mention supplied arguments, verification records, internal identifiers,
   candidates, reviewers, dossiers, scores, appendices-to-be-generated, or this
   workflow. The eventual appendix is ordinary reader-facing mathematical text.
7. Avoid unsupported bridge phrases at decisive steps. A lemma citation is valid only
   after its complete hypotheses have been established in the main proof.
8. Return only the main proof and complete answer. If it cannot be completed from the
   problem and the listed statements, state failure and the first remaining gap rather
   than bluffing.

ORIGINAL PROBLEM:
{problem}

DYNAMICALLY LOADED LOCAL LEMMA STATEMENTS:
{statements}
"""


def cited_labels(main_proof: str) -> list[str]:
    seen: list[str] = []
    for match in LOCAL_LEMMA_REFERENCE_RE.finditer(main_proof):
        label = match.group(1).upper()
        if label not in seen:
            seen.append(label)
    return seen


def assemble_used_lemma_appendix(
    *, main_proof: str, lemmas: list[dict[str, str]]
) -> dict[str, Any]:
    allowed = {row["label"]: row for row in lemmas}
    used = cited_labels(main_proof)
    unknown = [label for label in used if label not in allowed]
    selected = [allowed[label] for label in allowed if label in used]
    blocks = []
    for row in selected:
        blocks.append(
            f"### Lemma {row['label']}\n\n"
            f"{row['statement']}\n\n"
            f"**Proof.** {row['proof']}\n\n"
            f"**End of proof of Lemma {row['label']}.**"
        )
    appendix = ""
    if blocks:
        appendix = (
            "\n\n---\n\n## Appendix: proofs of the lemmas cited above\n\n"
            + "\n\n".join(blocks)
        )
    combined = main_proof.rstrip() + appendix + "\n"
    unused = [label for label in allowed if label not in used]
    violations: list[str] = []
    if INTERNAL_ID_RE.search(main_proof):
        violations.append("internal_record_identifier")
    if unknown:
        violations.append("unknown_local_lemma_reference")
    if unused:
        violations.append("not_all_dynamic_lemmas_cited")
    case_heading_count = len(CASE_HEADING_RE.findall(main_proof))
    if case_heading_count < 2:
        violations.append("fewer_than_two_explicit_case_headings")
    return {
        "main_proof": main_proof.rstrip(),
        "appendix": appendix.lstrip("\n"),
        "combined_proof": combined,
        "allowed_labels": list(allowed),
        "used_labels": used,
        "unused_labels": unused,
        "unknown_labels": unknown,
        "appended_labels": [row["label"] for row in selected],
        "case_heading_count": case_heading_count,
        "gate": {"passed": not violations, "violations": violations},
    }

