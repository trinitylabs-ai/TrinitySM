"""Deterministic change coverage; all mathematical judgments remain model-owned."""
from __future__ import annotations

from difflib import SequenceMatcher
import re

from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906 import tool_purpose
from . import pipeline


INSTRUCTION = """Additional required audit section: insert # Change Review immediately
before # Issues. Review every supplied change ID exactly once, in its supplied
order, using one Markdown bullet per ID:
- C001: JUSTIFIED | A concise mathematical reason grounded in the submitted proof.
Use JUSTIFIED, INVALID, or UNRESOLVED after the ID. These are judgment options,
not a requested verdict. Derive the changed equations from their definitions and
preceding steps; similarity of wording does not justify them. A valid alternative
derivation or legitimate change of route is allowed. Neither version is assumed
correct. Do not repair an equation mentally and credit the repaired version as
submitted. INVALID or UNRESOLVED requires overall FAIL and a corresponding Issue;
even all JUSTIFIED does not establish the rest of the proof. Keep reviewing the
whole proof and its lemma connections. The change list is mechanically generated,
not an assessment of mathematical correctness. Output Markdown only.
"""


def detect(original, proof, evidence, marker):
    if not marker or marker in original or marker in proof or proof.count(evidence) != 1:
        raise ValueError("change detection requires a unique frozen certificate insertion")
    raw = proof.replace(evidence, marker, 1)
    old, new = original.strip().splitlines(), raw.strip().splitlines()
    rows = []
    for kind, a0, a1, b0, b1 in SequenceMatcher(None, old, new, autojunk=False).get_opcodes():
        if kind == "equal":
            continue
        rows.append({"id": f"C{len(rows)+1:03d}", "kind": kind,
            "old_start": a0 + 1, "old_end": a1, "new_start": b0 + 1, "new_end": b1,
            "old": "\n".join(old[a0:a1]), "new": "\n".join(new[b0:b1]),
            "old_preceding": old[a0-1] if a0 else "",
            "old_following": old[a1] if a1 < len(old) else "",
            "new_preceding": new[b0-1] if b0 else "",
            "new_following": new[b1] if b1 < len(new) else ""})
    return rows


def _fence(text):
    longest = max((len(match.group()) for match in re.finditer(r"`+", text)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}text\n{text}\n{fence}"


def render(rows):
    parts = ["# Deterministically Detected Changes",
        "These are contiguous changed line blocks, not correctness labels. The immutable certificate is represented by its insertion marker. Line numbers for the rewrite refer to that marker-only view. Empty old or new text means an insertion or deletion. Review every ID; assess the new proof, not whether it copies the old one."]
    for row in rows:
        parts.append(f"## {row['id']} — {row['kind']}")
        for side in ("old", "new"):
            parts.append(f"{side.title()} changed lines {row[side+'_start']}–{row[side+'_end']}:\n\n" + _fence(row[side]))
        for label, old_key, new_key in (("Preceding context", "old_preceding", "new_preceding"),
                ("Following context", "old_following", "new_following")):
            if row[old_key] == row[new_key]:
                if row[old_key]:
                    parts.append(f"{label} (unchanged):\n\n" + _fence(row[old_key]))
            else:
                for side, key in (("old", old_key), ("new", new_key)):
                    if row[key]:
                        parts.append(f"{label} ({side}):\n\n" + _fence(row[key]))
    if not rows:
        parts.append("NONE")
    return "\n\n".join(parts)


def parse(markdown, rows, *, require_gap_closure):
    names = ["Decision", "Checks"] + (["Gap Closure"] if require_gap_closure else []) + ["Change Review", "Issues"]
    sections = pipeline.base.protocol.mdp.exact_sections(markdown, names)
    original = "\n\n".join(f"# {name}\n\n{sections[name]}" for name in names if name != "Change Review")
    audit = tool_purpose.parse_proof_audit(original, require_gap_closure=require_gap_closure)
    lines = sections["Change Review"].splitlines() if rows else []
    if not rows and sections["Change Review"] != "NONE":
        raise ValueError("an empty change list requires Change Review NONE")
    if len(lines) != len(rows):
        raise ValueError("every change ID must be reviewed exactly once")
    reviews = {}
    for row, line in zip(rows, lines, strict=True):
        match = re.fullmatch(r"- " + re.escape(row["id"]) + r": (JUSTIFIED|INVALID|UNRESOLVED) \| (.+)", line)
        if not match or not match[2].strip():
            raise ValueError("missing, duplicate, unordered, or malformed change review")
        status, reason = match.groups()
        if status != "JUSTIFIED":
            if audit["passed"] or not any(row["id"] in issue for issue in audit["issues"]):
                raise ValueError("non-justified change requires FAIL and an Issue citing its ID")
        reviews[row["id"]] = {"status": status, "reason": reason}
    return {**audit, "change_reviews": reviews, "change_coverage_complete": True}
