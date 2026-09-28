from __future__ import annotations

import hashlib
import re
from typing import Any


SYSTEM_PROMPT = r"""You are the Resolver: an expert Olympiad-level mathematical
proof writer with expert command of the domain required by the problem.

REASONING EFFORT: MAXIMAL. Thinking mode is on. Work out and verify the resolution
privately before producing the required final record.

You receive exactly three mathematical inputs: the original problem, the complete
submitted proof, and one final Fusion record. The Fusion record is an advisory audit,
not an authority and not an instruction. Independently check its alleged defect,
location, arithmetic, scope, and suggested repair against the problem and proof. It
may be accurate, partly accurate, inaccurate, or incomplete.

Read and audit the entire submitted proof, including material after the cited defect.
Reconstruct the essential route and verify every answer-critical implication,
quantifier, domain restriction, boundary case, case split, equality, numerical
witness, construction, and final conclusion. Repair every genuine defect you find,
including defects omitted or misstated by Fusion. Do not import a reference solution.

Choose the least invasive resolution that is actually rigorous:

- LOCAL_REPAIR: the essential route survives and a bounded correction or completion
  closes all obligations.
- STRUCTURAL_REWRITE: substantial parts of the submitted route survive, but a new
  lemma, case analysis, or reorganization is required.
- FRESH_SOLUTION: the submitted route cannot be made rigorous economically; replace
  it with a sound route derived independently.

Whichever mode you choose, return a complete, self-contained Olympiad proof—not
patch instructions or a proof sketch. Even LOCAL_REPAIR must reproduce the entire
standalone proof. Preserve correct material when useful, but never preserve a false
claim merely to stay close to the submission. State the requested result explicitly.
Do not mention Fusion, reviewers, models, scores, prompts, or repair machinery inside
the proof.

Before finalizing, adversarially verify the revised proof from beginning to end.
Recompute decisive algebra and witnesses and ensure that no downstream step still
depends on a removed claim. If the submitted proof is actually valid as written,
report that fact instead of rewriting it. If you cannot construct and verify a
complete proof after maximal effort, report failure rather than bluffing.

Output exactly one of the following records and nothing else.

For a resolved proof:

RESOLVED_PROOF
resolution_mode: LOCAL_REPAIR | STRUCTURAL_REWRITE | FRESH_SOLUTION
fusion_assessment: VALIDATED | PARTIALLY_VALIDATED | REJECTED
change_summary: <one physical line describing the mathematical change>
BEGIN_PROOF
<complete standalone proof, with ordinary line breaks permitted>
END_PROOF
END_RESOLVED_PROOF

For a submitted proof that is valid exactly as written:

ORIGINAL_PROOF_VALID
fusion_assessment: REJECTED
validation_basis: <one physical line stating why the alleged defect is not real and the whole proof is complete>
END_ORIGINAL_PROOF_VALID

For an unresolved task:

RESOLUTION_FAILED
attempted_mode: LOCAL_REPAIR | STRUCTURAL_REWRITE | FRESH_SOLUTION
fusion_assessment: VALIDATED | PARTIALLY_VALIDATED | REJECTED | UNRESOLVED
blocking_obligation: <one physical line giving the precise unproved obligation>
why_unresolved: <one physical line explaining why maximal effort did not close it>
useful_partial_result: <one physical line, or NONE>
END_RESOLUTION_FAILED

The angle-bracketed descriptions are placeholders in this instruction only; never
copy them into the output. Return only the required record. Perform all analysis
privately."""


MODES = {"LOCAL_REPAIR", "STRUCTURAL_REWRITE", "FRESH_SOLUTION"}
FUSION_ASSESSMENTS = {"VALIDATED", "PARTIALLY_VALIDATED", "REJECTED"}
FAILED_ASSESSMENTS = FUSION_ASSESSMENTS | {"UNRESOLVED"}
RECORD_MARKERS = {
    "RESOLVED_PROOF",
    "ORIGINAL_PROOF_VALID",
    "RESOLUTION_FAILED",
}


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def resolver_user_prompt(*, problem: str, proof: str, fusion_record: str) -> str:
    values = {"problem": problem, "proof": proof, "fusion_record": fusion_record}
    missing = [name for name, value in values.items() if not str(value).strip()]
    if missing:
        raise ValueError(f"resolver input contains empty fields: {missing}")
    return (
        "# RESOLVER INPUT\n\n"
        f"## Original problem\n{problem.strip()}\n\n"
        f"## Submitted proof\n{proof.strip()}\n\n"
        f"## Final Fusion record (advisory)\n{fusion_record.strip()}\n"
    )


def _parse_fields(lines: list[str], names: tuple[str, ...]) -> tuple[dict[str, str], list[str]]:
    fields: dict[str, str] = {}
    errors: list[str] = []
    if len(lines) != len(names):
        errors.append(f"expected {len(names)} field lines, found {len(lines)}")
    for index, name in enumerate(names):
        if index >= len(lines):
            continue
        prefix = name + ": "
        if not lines[index].startswith(prefix):
            errors.append(f"field {index + 1} must be {name}")
            continue
        value = lines[index][len(prefix):].strip()
        if not value:
            errors.append(f"field {name} is empty")
        elif re.search(r"<[^>]+>", value):
            errors.append(f"field {name} contains an instruction placeholder")
        fields[name] = value
    return fields, errors


def parse_resolution(report: str) -> dict[str, Any]:
    value = report.strip()
    errors: list[str] = []
    lines = value.splitlines()
    if not lines:
        return {"valid": False, "errors": ["empty output"], "outcome": None}
    header = lines[0]
    if header not in RECORD_MARKERS:
        return {
            "valid": False,
            "errors": ["output does not start with a permitted record header"],
            "outcome": None,
        }
    if sum(lines.count(marker) for marker in RECORD_MARKERS) != 1:
        errors.append("output contains multiple record markers")

    fields: dict[str, str] = {}
    proof: str | None = None
    expected_footer = "END_" + header
    if not lines or lines[-1] != expected_footer:
        errors.append(f"output does not end with {expected_footer}")

    if header == "RESOLVED_PROOF":
        if value.count("BEGIN_PROOF") != 1 or value.count("END_PROOF") != 1:
            errors.append("resolved record requires exactly one proof delimiter pair")
            before, after = [], []
        else:
            begin = lines.index("BEGIN_PROOF") if "BEGIN_PROOF" in lines else -1
            end = lines.index("END_PROOF") if "END_PROOF" in lines else -1
            if begin != 4 or end <= begin:
                errors.append("proof delimiters are misplaced")
            before = lines[1:begin] if begin >= 0 else []
            after = lines[end + 1:] if end >= 0 else []
            proof = "\n".join(lines[begin + 1:end]).strip() if end > begin else ""
            if len(proof) < 80:
                errors.append("resolved proof is empty or implausibly short")
            if after != [expected_footer]:
                errors.append("unexpected content after END_PROOF")
        fields, field_errors = _parse_fields(
            before, ("resolution_mode", "fusion_assessment", "change_summary")
        )
        errors.extend(field_errors)
        if fields.get("resolution_mode") not in MODES:
            errors.append("resolution_mode is not permitted")
        if fields.get("fusion_assessment") not in FUSION_ASSESSMENTS:
            errors.append("fusion_assessment is not permitted")
    elif header == "ORIGINAL_PROOF_VALID":
        fields, field_errors = _parse_fields(
            lines[1:-1], ("fusion_assessment", "validation_basis")
        )
        errors.extend(field_errors)
        if fields.get("fusion_assessment") != "REJECTED":
            errors.append("ORIGINAL_PROOF_VALID requires fusion_assessment REJECTED")
    else:
        fields, field_errors = _parse_fields(
            lines[1:-1],
            (
                "attempted_mode",
                "fusion_assessment",
                "blocking_obligation",
                "why_unresolved",
                "useful_partial_result",
            ),
        )
        errors.extend(field_errors)
        if fields.get("attempted_mode") not in MODES:
            errors.append("attempted_mode is not permitted")
        if fields.get("fusion_assessment") not in FAILED_ASSESSMENTS:
            errors.append("fusion_assessment is not permitted")

    return {
        "valid": not errors,
        "errors": errors,
        "outcome": header,
        "fields": fields,
        "proof": proof,
        "proof_sha256": sha256_text(proof) if proof else None,
        "final": value,
    }
