from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Any


NO_OBJECTIONS = "NO OBJECTIONS"
SCORING_RE = re.compile(
    r"(?i)(?:FINAL[_ ]GRADE|FINAL[_ ]VERDICT|\bscore(?:d|s|ing)?\b|"
    r"\bgrad(?:e|ed|es|ing)\b|\b[0-7]\s*/\s*7\b|\\boxed\s*\{\s*(?:correct|incorrect))"
)
OBJECTION_RE = re.compile(
    r"(?m)^- Objection ID: ([OG]\d+)\n"
    r"  - Severity: (LOCAL|SUBSTANTIVE|FATAL)\n"
    r"  - Claim challenged: (.+)\n"
    r"  - Analysis: (.+)\n"
    r"  - Required resolution: (.+)$"
)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def review_source(*, problem: str, proof: str) -> str:
    """The only source shown to OPC/GPT-OSS; deliberately contains no rubric."""

    return (
        "# MATHEMATICAL REVIEW SOURCE\n\n"
        f"## Problem\n{problem.strip()}\n\n"
        f"## Submitted proof\n{proof.strip()}\n"
    )


def independent_review_prompt(*, role: str, source: str) -> str:
    if role == "opc":
        identity = "an independent local mathematical critic"
        heading = "# LOCAL CRITIC"
        end = "END LOCAL CRITIC"
        prefix = "O"
        focus = (
            "Check individual implications, computations, constructions, edge cases, "
            "and omitted justifications. Identify concrete defects, not style issues."
        )
    elif role == "gptoss":
        identity = "an independent whole-proof adversarial reviewer"
        heading = "# WHOLE-PROOF REVIEW"
        end = "END WHOLE-PROOF REVIEW"
        prefix = "G"
        focus = (
            "Test the global strategy, both directions, quantifiers, exhaustiveness, "
            "and whether the claimed conclusion actually follows."
        )
    else:
        raise ValueError(f"unknown reviewer role: {role}")

    return f"""Act as {identity}. Work closed-book and independently. {focus}
Do not rewrite the proof and do not silently repair it. Do not assign or discuss a
score, grade, verdict, or correctness label. Your only job is to produce your
designated review block.

After any model-native reasoning, the final response must use exactly this format:

{heading}
- Objection ID: {prefix}1
  - Severity: SUBSTANTIVE
  - Claim challenged: one specific submitted claim
  - Analysis: a concise reproducible mathematical objection
  - Required resolution: the exact obligation a rewriter must discharge
[repeat consecutively as {prefix}2, {prefix}3, ...]
{end}

If there is no concrete objection, use exactly:

{heading}
{NO_OBJECTIONS}
{end}

For each item, replace SUBSTANTIVE with exactly one chosen severity word: LOCAL,
SUBSTANTIVE, or FATAL. Never copy a list of alternatives into that field. Do not emit
any score or verdict. Do not add text after the end marker. Keep the final block under
1,200 words.

{source.strip()}
"""


def _gptoss_final(report: str) -> tuple[str, str]:
    value = report.strip()
    marker = "[End thinking]"
    if value.startswith("[Start thinking]"):
        if value.count(marker) != 1:
            raise ValueError("GPT-OSS output lacks one exact reasoning boundary")
        reasoning, final = value.split(marker, 1)
        reasoning = (reasoning.strip() + "\n" + marker).strip()
        final = final.strip()
        if not final:
            raise ValueError("GPT-OSS final review is empty")
        return reasoning, final
    # Some llama.cpp templates suppress the exposed reasoning wrapper. The
    # complete response is then already the final review block.
    return "", value


def canonicalize_component_review(*, role: str, report: str) -> str:
    """Package only structured objections the reviewer actually emitted.

    OPC-R1 can repeat otherwise well-formed review blocks inside its native
    reasoning trace. This normalization does not infer severity or generate
    criticism: it selects the first emitted record for each role-specific ID,
    orders those records numerically, and wraps them in one designated block.
    Malformed placeholder records are deliberately excluded.
    """

    if role not in {"opc", "gptoss"}:
        raise ValueError(f"unknown reviewer role: {role}")
    prefix = "O" if role == "opc" else "G"
    heading = "# LOCAL CRITIC" if role == "opc" else "# WHOLE-PROOF REVIEW"
    end = "END LOCAL CRITIC" if role == "opc" else "END WHOLE-PROOF REVIEW"
    records: dict[int, str] = {}
    for match in OBJECTION_RE.finditer(report):
        objection_id = match.group(1)
        if not objection_id.startswith(prefix):
            continue
        number = int(objection_id[1:])
        records.setdefault(number, match.group(0).strip())
    if records:
        ordered = [records[number] for number in sorted(records)]
        # Renumber gaps caused by malformed emitted records. This changes only
        # protocol identity, never reviewer mathematics or severity.
        normalized = []
        for index, record in enumerate(ordered, 1):
            normalized.append(
                re.sub(
                    rf"(?m)^- Objection ID: {prefix}\d+$",
                    f"- Objection ID: {prefix}{index}",
                    record,
                    count=1,
                )
            )
        return heading + "\n" + "\n".join(normalized) + "\n" + end
    if re.search(r"(?m)^NO OBJECTIONS$", report):
        return f"{heading}\n{NO_OBJECTIONS}\n{end}"
    return report.strip()


def parse_component_review(*, role: str, report: str) -> dict[str, Any]:
    if role not in {"opc", "gptoss"}:
        raise ValueError(f"unknown reviewer role: {role}")
    reasoning, final = _gptoss_final(report) if role == "gptoss" else ("", report.strip())
    heading = "# LOCAL CRITIC" if role == "opc" else "# WHOLE-PROOF REVIEW"
    end = "END LOCAL CRITIC" if role == "opc" else "END WHOLE-PROOF REVIEW"
    prefix = "O" if role == "opc" else "G"
    errors: list[str] = []
    if not final.startswith(heading + "\n"):
        errors.append(f"final review does not start with {heading}")
    if not final.endswith("\n" + end):
        errors.append(f"final review does not end with {end}")
    if SCORING_RE.search(final):
        errors.append("review contains forbidden scoring/verdict language")

    objections = [
        {
            "id": match.group(1),
            "severity": match.group(2),
            "claim": match.group(3).strip(),
            "analysis": match.group(4).strip(),
            "required_resolution": match.group(5).strip(),
        }
        for match in OBJECTION_RE.finditer(final)
    ]
    expected_ids = [f"{prefix}{index}" for index in range(1, len(objections) + 1)]
    observed_ids = [row["id"] for row in objections]
    if observed_ids != expected_ids:
        errors.append("objection IDs are not consecutive or use the wrong role prefix")
    has_none = f"\n{NO_OBJECTIONS}\n" in final
    if objections and has_none:
        errors.append("review both lists objections and says NO OBJECTIONS")
    if not objections and not has_none:
        errors.append("review contains neither structured objections nor NO OBJECTIONS")

    return {
        "valid": not errors,
        "errors": errors,
        "reasoning": reasoning,
        "final": final,
        "objections": objections,
    }


@dataclass(frozen=True)
class TwoBlockMaterials:
    problem: str
    candidate_proof: str
    opc_final: str
    gptoss_final: str
    objections: tuple[dict[str, str], ...]

    def validate(self) -> None:
        if not all(
            value.strip()
            for value in (
                self.problem,
                self.candidate_proof,
                self.opc_final,
                self.gptoss_final,
            )
        ):
            raise ValueError("two-block materials contain an empty field")


FUSION_SYSTEM_PROMPT = r"""You are Gemma4 acting as the review-fusion adjudicator for an olympiad proof.
You receive exactly two final review blocks: OPC local criticism and GPT-OSS
whole-proof criticism. Neither critic is authoritative. Reproduce each objection
against the problem and submitted proof, then explicitly accept or reject it.

You must disposition every supplied objection exactly once. A rejection must give a
direct mathematical reason showing why the submitted proof already closes the issue;
"the critic is wrong" is not a resolution. An acceptance must become a concrete
rewrite obligation. Independently audit the proof for defects missed by both critics
and add those as obligations I1, I2, ... when needed.

Every ledger resolution must be self-contained. Cross-references such as "see O2",

Problem-neutral conservative gate: every critic-labeled SUBSTANTIVE or FATAL
objection must create a rewrite obligation, even when you judge the objection itself
unsupported. In that case mark it REJECTED, explain the mathematical reason, and use
the obligation to require the rewritten proof to make the contested inference
self-contained. The fusion stage is not permitted to erase a serious critic concern;
the proof rewriter is the stage that must close it in the submitted mathematics.

Substantive-objection gate: if either critic supplied any SUBSTANTIVE or FATAL
objection, the pre-rewrite proof is INCOMPLETE/INCORRECT, its score is at most 3, and
at least one corresponding rewrite obligation is mandatory. Thus 7/7 is possible
only when no critic supplied a serious objection, the independent audit finds no gap,
and there are no rewrite obligations. A genuinely local accepted slip may receive 6.
Never assign 5.

Output exactly this structure:

# GEMMA REVIEW FUSION
## VALID CORE
[concise description]
## OBJECTION LEDGER
- Objection ID: O1
  - Severity: LOCAL|SUBSTANTIVE|FATAL
  - Disposition: ACCEPTED|REJECTED
  - Mathematical resolution: concrete adjudication
  - Rewrite obligation: R1|NONE
[one entry for every supplied O/G objection, in input order]
[or exactly `NO CRITIC OBJECTIONS` when none were supplied]
## INDEPENDENT AUDIT
[direct audit; state NO ADDITIONAL DEFECTS or identify each new obligation I1, I2, ...]
## REWRITE HANDOFF
- Obligation ID: R1
  - Severity: LOCAL|SUBSTANTIVE|FATAL
  - Required repair: exact mathematical obligation
[then any I obligations; or exactly `NO REWRITE OBLIGATIONS`]
## FINAL ASSESSMENT
- FINAL VERDICT: CORRECT|INCORRECT
- FINAL_GRADE: N/7
- Accepted objection IDs: comma-separated IDs or NONE
- Rewrite obligation IDs: comma-separated IDs or NONE

Emit no text after the last line."""


def fusion_user_prompt(materials: TwoBlockMaterials) -> str:
    materials.validate()
    return (
        "# TWO-BLOCK FUSION INPUT\n\n"
        f"## Problem\n{materials.problem.strip()}\n\n"
        f"## Candidate proof\n{materials.candidate_proof.strip()}\n\n"
        "## Block 1 — OPC final local-critic report\n"
        f"{materials.opc_final.strip()}\n\n"
        "## Block 2 — GPT-OSS final whole-proof report\n"
        f"{materials.gptoss_final.strip()}\n"
    )


LEDGER_RE = re.compile(
    r"(?m)^- Objection ID: ([OG]\d+)\n"
    r"  - Severity: (LOCAL|SUBSTANTIVE|FATAL)\n"
    r"  - Disposition: (ACCEPTED|REJECTED)\n"
    r"  - Mathematical resolution: (.+)\n"
    r"  - Rewrite obligation: (R\d+|NONE)$"
)
OBLIGATION_RE = re.compile(
    r"(?m)^- Obligation ID: ([RI]\d+)\n"
    r"  - Severity: (LOCAL|SUBSTANTIVE|FATAL)\n"
    r"  - Required repair: (.+)$"
)


def _csv(value: str | None) -> list[str]:
    if not value or value.strip() == "NONE":
        return []
    return [item.strip() for item in value.split(",")]


def parse_fusion_output(
    report: str, *, required_objections: tuple[dict[str, str], ...]
) -> dict[str, Any]:
    value = report.strip()
    errors: list[str] = []
    required_ids = [row["id"] for row in required_objections]
    required_severity = {row["id"]: row["severity"] for row in required_objections}
    if not value.startswith("# GEMMA REVIEW FUSION\n"):
        errors.append("fusion output has the wrong first heading")
    for heading in (
        "## VALID CORE",
        "## OBJECTION LEDGER",
        "## INDEPENDENT AUDIT",
        "## REWRITE HANDOFF",
        "## FINAL ASSESSMENT",
    ):
        if value.count(heading) != 1:
            errors.append(f"{heading} section count is not one")

    ledger = [
        {
            "id": match.group(1),
            "severity": match.group(2),
            "disposition": match.group(3),
            "resolution": match.group(4).strip(),
            "obligation": match.group(5),
        }
        for match in LEDGER_RE.finditer(value)
    ]
    if [row["id"] for row in ledger] != required_ids:
        errors.append("ledger does not disposition every critic objection exactly once in order")
    for row in ledger:
        if required_severity.get(row["id"]) != row["severity"]:
            errors.append(f"fusion changed severity for {row['id']}")
        if len(row["resolution"].split()) < 5:
            errors.append(f"{row['id']} lacks a substantive mathematical resolution")
        if row["disposition"] == "ACCEPTED" and row["obligation"] == "NONE":
            errors.append(f"accepted objection {row['id']} lacks a rewrite obligation")
        if row["severity"] in {"SUBSTANTIVE", "FATAL"} and row["obligation"] == "NONE":
            errors.append(
                f"serious critic objection {row['id']} lacks a conservative rewrite obligation"
            )
    if not required_ids and "NO CRITIC OBJECTIONS" not in value:
        errors.append("empty critic ledger lacks NO CRITIC OBJECTIONS")

    obligations = [
        {
            "id": match.group(1),
            "severity": match.group(2),
            "required_repair": match.group(3).strip(),
        }
        for match in OBLIGATION_RE.finditer(value)
    ]
    obligation_ids = [row["id"] for row in obligations]
    if len(obligation_ids) != len(set(obligation_ids)):
        errors.append("rewrite obligation IDs are duplicated")
    for row in ledger:
        if row["obligation"] != "NONE" and row["obligation"] not in obligation_ids:
            errors.append(f"ledger obligation {row['obligation']} is absent from handoff")

    verdict_match = re.search(r"(?m)^- FINAL VERDICT: (CORRECT|INCORRECT)$", value)
    grade_match = re.search(r"(?m)^- FINAL_GRADE: ([0-7])/7$", value)
    accepted_match = re.search(r"(?m)^- Accepted objection IDs: (.+)$", value)
    obligation_match = re.search(r"(?m)^- Rewrite obligation IDs: (.+)$", value)
    if not all((verdict_match, grade_match, accepted_match, obligation_match)):
        errors.append("fusion lacks an exact final assessment")
    if obligation_match and value.splitlines()[-1] != obligation_match.group(0):
        errors.append("content appears after rewrite obligation IDs")

    score = int(grade_match.group(1)) if grade_match else None
    verdict = verdict_match.group(1) if verdict_match else None
    accepted_ids = _csv(accepted_match.group(1) if accepted_match else None)
    declared_obligations = _csv(obligation_match.group(1) if obligation_match else None)
    actual_accepted = [row["id"] for row in ledger if row["disposition"] == "ACCEPTED"]
    if accepted_ids != actual_accepted:
        errors.append("declared accepted IDs do not match the ledger")
    if declared_obligations != obligation_ids:
        errors.append("declared rewrite obligations do not match the handoff")
    accepted_substantive = [
        row["id"]
        for row in ledger
        if row["disposition"] == "ACCEPTED" and row["severity"] in {"SUBSTANTIVE", "FATAL"}
    ]
    mandatory_substantive = [
        row["id"] for row in ledger if row["severity"] in {"SUBSTANTIVE", "FATAL"}
    ]
    if score == 5:
        errors.append("fusion used the disallowed score 5")
    if mandatory_substantive and score is not None and score > 3:
        errors.append("any critic substantive/fatal objection must cap the score at 3")
    if score == 7 and (mandatory_substantive or obligation_ids):
        errors.append("7/7 is forbidden while a substantive objection or obligation remains")
    if score == 7 and verdict != "CORRECT":
        errors.append("7/7 must use verdict CORRECT")
    if obligations and verdict != "INCORRECT":
        errors.append("a proof with rewrite obligations must use verdict INCORRECT")

    return {
        "valid": not errors,
        "errors": errors,
        "score": score,
        "verdict": verdict,
        "ledger": ledger,
        "accepted_objection_ids": accepted_ids,
        "accepted_substantive_objection_ids": accepted_substantive,
        "mandatory_substantive_objection_ids": mandatory_substantive,
        "obligations": obligations,
        "rewrite_obligation_ids": declared_obligations,
    }


REWRITER_SYSTEM_PROMPT = r"""You are Gemma4 rewriting an olympiad proof after a two-block review fusion.
Return only one complete, self-contained, reviewer-ready proof. Do not mention the
critics, review process, scores, grades, ledgers, or rewriting.

Treat the fusion as advisory, but independently verify every adjudication. You must
substantively discharge every accepted critic objection and every rewrite obligation
inside the mathematics of the returned proof. Do not merely delete the challenged
sentence, restate the desired conclusion, or call an argument standard. Supply the
missing lemma, invariant, construction, case analysis, or replacement strategy. If a
suggested repair is false or insufficient, discard it and solve the underlying
obligation correctly. Recheck both directions, boundary cases, and all quantifiers.

Even when the handoff has no obligation, preserve the correct mathematical content
while improving explicitness. Finish with the exact requested answer in \boxed{} when
the problem asks for one. Output the proof only."""


def rewriter_user_prompt(
    *, materials: TwoBlockMaterials, fusion_report: str, stage: int
) -> str:
    materials.validate()
    return (
        f"# STAGE {stage} PROOF REWRITE INPUT\n\n"
        f"## Problem\n{materials.problem.strip()}\n\n"
        f"## Current proof\n{materials.candidate_proof.strip()}\n\n"
        f"## Gemma review fusion and mandatory resolution handoff\n{fusion_report.strip()}\n"
    )
