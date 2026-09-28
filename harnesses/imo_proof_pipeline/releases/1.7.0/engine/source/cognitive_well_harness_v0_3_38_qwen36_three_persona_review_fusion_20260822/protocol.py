from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Any


NO_OBJECTIONS = "NO OBJECTIONS"
ROLE_ORDER = ("thinkprm", "opc", "gptoss")
ROLE_SPECS = {
    "thinkprm": {
        "label": "THINKPRM",
        "heading": "# THINKPRM PROCESS REVIEW",
        "end": "END THINKPRM PROCESS REVIEW",
        "prefix": "T",
        "identity": "a ThinkPRM-style proof-process reviewer",
        "focus": (
            "Read the proof sequentially. Verify each inference against its stated "
            "prerequisites, locate the earliest unsupported transition, and trace how "
            "that break affects all downstream claims. Focus on step-level proof integrity."
        ),
    },
    "opc": {
        "label": "OPC",
        "heading": "# OPC LOCAL-CRITIC REVIEW",
        "end": "END OPC LOCAL-CRITIC REVIEW",
        "prefix": "O",
        "identity": "an OPC-style local mathematical critic",
        "focus": (
            "Stress-test individual lemmas, implications, equations, constructions, "
            "case splits, edge conditions, and quantifier scope. Make each objection "
            "locally reproducible from a specific submitted claim."
        ),
    },
    "gptoss": {
        "label": "GPT-OSS",
        "heading": "# GPT-OSS WHOLE-PROOF REVIEW",
        "end": "END GPT-OSS WHOLE-PROOF REVIEW",
        "prefix": "G",
        "identity": "a GPT-OSS-style whole-proof adversarial reviewer",
        "focus": (
            "Attack the end-to-end strategy. Test necessity and sufficiency, "
            "exhaustiveness, hidden assumptions, invariants, termination, and plausible "
            "counterexamples. Check that the announced conclusion really follows."
        ),
    },
}

SCORING_RE = re.compile(
    r"(?i)(?:FINAL[_ ]GRADE|FINAL[_ ]VERDICT|\bscore(?:d|s|ing)?\b|"
    r"\bgrad(?:e|ed|es|ing)\b|\b[0-7]\s*/\s*7\b|\\boxed\s*\{\s*(?:correct|incorrect))"
)
OBJECTION_RE = re.compile(
    r"(?m)^- Objection ID: ([TOG]\d+)\n"
    r"  - Severity: (LOCAL|SUBSTANTIVE|FATAL)\n"
    r"  - Claim challenged: (.+)\n"
    r"  - Analysis: (.+)\n"
    r"  - Required resolution: (.+)$"
)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def review_source(*, problem: str, proof: str) -> str:
    return (
        "# MATHEMATICAL REVIEW SOURCE\n\n"
        f"## Problem\n{problem.strip()}\n\n"
        f"## Submitted proof\n{proof.strip()}\n"
    )


def independent_review_prompt(*, role: str, source: str) -> str:
    try:
        spec = ROLE_SPECS[role]
    except KeyError as error:
        raise ValueError(f"unknown reviewer role: {role}") from error
    return f"""You are Qwen3.6 acting only as {spec['identity']}. Thinking mode is on.
Work closed-book and independently; you cannot see any other review. {spec['focus']}

Do not rewrite or silently repair the proof. Do not assign or discuss a score, grade,
verdict, or correctness label. Produce only your designated review block after your
private model-native reasoning. Each objection must identify an exact mathematical
obligation, not a style preference.

Your final response must use exactly this format:

{spec['heading']}
- Objection ID: {spec['prefix']}1
  - Severity: SUBSTANTIVE
  - Claim challenged: one specific submitted claim
  - Analysis: a concise reproducible mathematical objection on one line
  - Required resolution: the exact obligation a rewriter must discharge on one line
[repeat consecutively as {spec['prefix']}2, {spec['prefix']}3, ...]
{spec['end']}

If there is no concrete objection, use exactly:

{spec['heading']}
{NO_OBJECTIONS}
{spec['end']}

For every item, replace SUBSTANTIVE with exactly one severity: LOCAL, SUBSTANTIVE,
or FATAL. Keep each field on one physical line. Do not add text after the end marker.
Keep the final block under 1,500 words.

{source.strip()}
"""


def parse_component_review(*, role: str, report: str) -> dict[str, Any]:
    try:
        spec = ROLE_SPECS[role]
    except KeyError as error:
        raise ValueError(f"unknown reviewer role: {role}") from error
    value = report.strip()
    errors: list[str] = []
    if not value.startswith(spec["heading"] + "\n"):
        errors.append(f"review does not start with {spec['heading']}")
    if not value.endswith("\n" + spec["end"]):
        errors.append(f"review does not end with {spec['end']}")
    if SCORING_RE.search(value):
        errors.append("review contains forbidden scoring or verdict language")

    objections = [
        {
            "id": match.group(1),
            "role": role,
            "source_role": spec["label"],
            "severity": match.group(2),
            "claim": match.group(3).strip(),
            "analysis": match.group(4).strip(),
            "required_resolution": match.group(5).strip(),
        }
        for match in OBJECTION_RE.finditer(value)
        if match.group(1).startswith(spec["prefix"])
    ]
    expected_ids = [f"{spec['prefix']}{index}" for index in range(1, len(objections) + 1)]
    if [row["id"] for row in objections] != expected_ids:
        errors.append("objection IDs are not consecutive or use the wrong prefix")
    has_none = f"\n{NO_OBJECTIONS}\n" in value
    if objections and has_none:
        errors.append("review both lists objections and says NO OBJECTIONS")
    if not objections and not has_none:
        errors.append("review contains neither structured objections nor NO OBJECTIONS")
    return {"valid": not errors, "errors": errors, "objections": objections, "final": value}


@dataclass(frozen=True)
class ThreePersonaMaterials:
    problem: str
    candidate_proof: str
    thinkprm_final: str
    opc_final: str
    gptoss_final: str
    objections: tuple[dict[str, str], ...]

    def validate(self) -> None:
        fields = (
            self.problem,
            self.candidate_proof,
            self.thinkprm_final,
            self.opc_final,
            self.gptoss_final,
        )
        if not all(value.strip() for value in fields):
            raise ValueError("three-persona materials contain an empty field")


FUSION_SYSTEM_PROMPT = r"""You are Qwen3.6 acting as a fresh review-fusion adjudicator.
Thinking mode is on. You receive three final review blocks produced independently by
Qwen3.6 under three different responsibilities: ThinkPRM proof-process review, OPC
local criticism, and GPT-OSS whole-proof adversarial review. You do not receive their
private reasoning traces. No review is authoritative and majority vote is forbidden.

Reproduce every supplied objection directly against the original problem and proof.
Disposition every objection exactly once. REJECTED means you can give a concrete,
self-contained mathematical reason the submitted proof already closes that exact
issue; merely saying the reviewer is mistaken is invalid. ACCEPTED objections must
become explicit rewrite obligations. Independently audit the proof and add missed
defects as I1, I2, ... obligations.

Conservative substantive-objection gate: every reviewer-labeled SUBSTANTIVE or FATAL
objection must create a rewrite obligation, even if its diagnosis is rejected. In a
rejected case the obligation requires Gemma to make the contested inference explicit
and self-contained. Fusion cannot erase a serious critic concern. Every accepted
LOCAL objection must also create an obligation. Only a rejected LOCAL objection may
use NONE.

Do not score the proof and do not rewrite it. Produce a precise feedback object for
Gemma4. Use exactly this structure and no text after the final line:

# QWEN THREE-PERSONA REVIEW FUSION
## VALID CORE
[concise independently verified content]
## OBJECTION LEDGER
- Objection ID: T1
  - Source role: THINKPRM
  - Severity: LOCAL|SUBSTANTIVE|FATAL
  - Disposition: ACCEPTED|REJECTED
  - Mathematical adjudication: a concrete self-contained adjudication on one line
  - Rewrite obligation: R1|NONE
[one entry for every supplied T/O/G objection, in input order]
[or exactly `NO CRITIC OBJECTIONS` if none exist]
## INDEPENDENT AUDIT
[state NO ADDITIONAL DEFECTS, or explain new defects represented by I obligations]
## REWRITE HANDOFF
- Obligation ID: R1
  - Source objection IDs: T1
  - Severity: LOCAL|SUBSTANTIVE|FATAL
  - Required repair: exact mathematical work Gemma must put in the proof on one line
[then additional R or I obligations; use INDEPENDENT for an I source]
[or exactly `NO REWRITE OBLIGATIONS`]
## COMPLETION GATE
- Supplied objection IDs: T1, O1, G1|NONE
- Dispositioned objection IDs: T1, O1, G1|NONE
- Mandatory serious objection IDs: T1, G1|NONE
- Rewrite obligation IDs: R1, R2, I1|NONE"""


def fusion_user_prompt(materials: ThreePersonaMaterials) -> str:
    materials.validate()
    return (
        "# THREE-PERSONA FUSION INPUT\n\n"
        f"## Problem\n{materials.problem.strip()}\n\n"
        f"## Candidate proof\n{materials.candidate_proof.strip()}\n\n"
        "## Block 1 — ThinkPRM-style process review\n"
        f"{materials.thinkprm_final.strip()}\n\n"
        "## Block 2 — OPC-style local-critic review\n"
        f"{materials.opc_final.strip()}\n\n"
        "## Block 3 — GPT-OSS-style whole-proof adversarial review\n"
        f"{materials.gptoss_final.strip()}\n"
    )


LEDGER_RE = re.compile(
    r"(?m)^- Objection ID: ([TOG]\d+)\n"
    r"  - Source role: (THINKPRM|OPC|GPT-OSS)\n"
    r"  - Severity: (LOCAL|SUBSTANTIVE|FATAL)\n"
    r"  - Disposition: (ACCEPTED|REJECTED)\n"
    r"  - Mathematical adjudication: (.+)\n"
    r"  - Rewrite obligation: (R\d+|NONE)$"
)
OBLIGATION_RE = re.compile(
    r"(?m)^- Obligation ID: ([RI]\d+)\n"
    r"  - Source objection IDs: (.+)\n"
    r"  - Severity: (LOCAL|SUBSTANTIVE|FATAL)\n"
    r"  - Required repair: (.+)$"
)


def _csv(value: str | None) -> list[str]:
    if value is None or value.strip() == "NONE":
        return []
    return [item.strip() for item in value.split(",")]


def parse_fusion_output(
    report: str, *, required_objections: tuple[dict[str, str], ...]
) -> dict[str, Any]:
    value = report.strip()
    errors: list[str] = []
    required_ids = [row["id"] for row in required_objections]
    required_severity = {row["id"]: row["severity"] for row in required_objections}
    required_roles = {row["id"]: row["source_role"] for row in required_objections}
    if not value.startswith("# QWEN THREE-PERSONA REVIEW FUSION\n"):
        errors.append("fusion output has the wrong first heading")
    for heading in (
        "## VALID CORE",
        "## OBJECTION LEDGER",
        "## INDEPENDENT AUDIT",
        "## REWRITE HANDOFF",
        "## COMPLETION GATE",
    ):
        if value.count(heading) != 1:
            errors.append(f"{heading} section count is not one")

    ledger = [
        {
            "id": match.group(1),
            "source_role": match.group(2),
            "severity": match.group(3),
            "disposition": match.group(4),
            "adjudication": match.group(5).strip(),
            "obligation": match.group(6),
        }
        for match in LEDGER_RE.finditer(value)
    ]
    if [row["id"] for row in ledger] != required_ids:
        errors.append("ledger does not disposition every supplied objection once in order")
    for row in ledger:
        if required_severity.get(row["id"]) != row["severity"]:
            errors.append(f"fusion changed severity for {row['id']}")
        if required_roles.get(row["id"]) != row["source_role"]:
            errors.append(f"fusion changed source role for {row['id']}")
        if len(row["adjudication"].split()) < 5:
            errors.append(f"{row['id']} lacks substantive mathematical adjudication")
        if row["disposition"] == "ACCEPTED" and row["obligation"] == "NONE":
            errors.append(f"accepted objection {row['id']} lacks an obligation")
        if row["severity"] in {"SUBSTANTIVE", "FATAL"} and row["obligation"] == "NONE":
            errors.append(f"serious objection {row['id']} lacks a conservative obligation")
    if not required_ids and "NO CRITIC OBJECTIONS" not in value:
        errors.append("empty ledger lacks NO CRITIC OBJECTIONS")

    obligations = [
        {
            "id": match.group(1),
            "source_objection_ids": _csv(match.group(2)) if match.group(2) != "INDEPENDENT" else [],
            "independent": match.group(2) == "INDEPENDENT",
            "severity": match.group(3),
            "required_repair": match.group(4).strip(),
        }
        for match in OBLIGATION_RE.finditer(value)
    ]
    obligation_ids = [row["id"] for row in obligations]
    if len(obligation_ids) != len(set(obligation_ids)):
        errors.append("rewrite obligation IDs are duplicated")
    for row in ledger:
        if row["obligation"] != "NONE" and row["obligation"] not in obligation_ids:
            errors.append(f"ledger obligation {row['obligation']} is absent from handoff")
    for row in obligations:
        if not row["independent"] and any(item not in required_ids for item in row["source_objection_ids"]):
            errors.append(f"obligation {row['id']} cites an unknown objection")

    supplied_match = re.search(r"(?m)^- Supplied objection IDs: (.+)$", value)
    dispositioned_match = re.search(r"(?m)^- Dispositioned objection IDs: (.+)$", value)
    serious_match = re.search(r"(?m)^- Mandatory serious objection IDs: (.+)$", value)
    obligations_match = re.search(r"(?m)^- Rewrite obligation IDs: (.+)$", value)
    if not all((supplied_match, dispositioned_match, serious_match, obligations_match)):
        errors.append("fusion lacks an exact completion gate")
    elif value.splitlines()[-1] != obligations_match.group(0):
        errors.append("content appears after the completion gate")
    supplied = _csv(supplied_match.group(1) if supplied_match else None)
    dispositioned = _csv(dispositioned_match.group(1) if dispositioned_match else None)
    serious = _csv(serious_match.group(1) if serious_match else None)
    declared_obligations = _csv(obligations_match.group(1) if obligations_match else None)
    required_serious = [
        row["id"] for row in required_objections if row["severity"] in {"SUBSTANTIVE", "FATAL"}
    ]
    if supplied != required_ids:
        errors.append("declared supplied IDs do not match the inputs")
    if dispositioned != required_ids:
        errors.append("declared dispositioned IDs do not match the ledger")
    if serious != required_serious:
        errors.append("declared serious IDs do not match reviewer severities")
    if declared_obligations != obligation_ids:
        errors.append("declared rewrite obligations do not match the handoff")
    return {
        "valid": not errors,
        "errors": errors,
        "ledger": ledger,
        "obligations": obligations,
        "supplied_objection_ids": required_ids,
        "mandatory_serious_objection_ids": required_serious,
        "rewrite_obligation_ids": obligation_ids,
    }


REWRITER_SYSTEM_PROMPT = r"""You are Gemma4 rewriting an olympiad proof from a
Qwen3.6 three-persona review fusion. Thinking mode is on. Return only one complete,
self-contained, reviewer-ready proof. Do not mention reviewers, fusion, feedback,
scores, grades, ledgers, personas, or rewriting.

Independently verify the fused adjudication. You must substantively discharge every
rewrite obligation in the mathematics of the returned proof. Do not merely delete a
challenged sentence, restate the goal, or call an argument standard. Supply the
missing lemma, invariant, predecessor/backward-induction argument, construction,
case analysis, obstruction, or replacement strategy actually required. If suggested
feedback is false or insufficient, solve the underlying obligation correctly.

Explicit objection-resolution gate: before finalizing, check internally that every
listed R/I obligation is resolved by an identifiable passage of the rewritten proof.
Recheck both directions, all quantifiers, boundary cases, invariants, and finite
termination. Output the proof only."""


def rewriter_user_prompt(*, materials: ThreePersonaMaterials, fusion_report: str) -> str:
    materials.validate()
    return (
        "# PROOF REWRITE INPUT\n\n"
        f"## Problem\n{materials.problem.strip()}\n\n"
        f"## Proof to replace\n{materials.candidate_proof.strip()}\n\n"
        "## Qwen3.6 fused repair feedback\n"
        f"{fusion_report.strip()}\n\n"
        "Return only the complete replacement proof."
    )


def nonempty_parser(value: str) -> dict[str, Any]:
    text = value.strip()
    return {"valid": bool(text), "errors": [] if text else ["empty response"]}

