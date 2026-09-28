"""Prompt-only repair locations from uniquely matching model quotations.

No mathematical rewriting, fuzzy matching, inferred location, or model call.
The caller removes immutable evidence/appendix bodies before calling this code.
"""
from __future__ import annotations

import hashlib
import re

BEGIN = "[[CURRENT_REPAIR_BEGIN]]"
END = "[[CURRENT_REPAIR_END]]"
FEEDBACK_BEGIN = "[[CURRENT_REPAIR_FEEDBACK_BEGIN]]"
FEEDBACK_END = "[[CURRENT_REPAIR_FEEDBACK_END]]"
DELIMITERS = (BEGIN, END, FEEDBACK_BEGIN, FEEDBACK_END)
VERSION = "unique-current-draft-quotation-v1"
QUOTES = re.compile(r'"([^"\n]+)"|“([^”\n]+)”')


def annotate(proof, issues, *, evidence_marker):
    if any(marker in proof for marker in DELIMITERS):
        raise ValueError("current draft already contains prompt-only repair markers")
    record = {"schema": VERSION, "draft_sha256": hashlib.sha256(proof.encode()).hexdigest(),
              "anchors": [], "unmatched": [], "feedback_embedded": False}
    candidates = {}
    for index, issue in enumerate(issues, 1):
        for match in QUOTES.finditer(issue):
            original = next(group for group in match.groups() if group is not None)
            quote = original
            # An edge ellipsis denotes an omitted prefix/suffix, not a wildcard.
            # Interior omissions and whitespace/LaTeX differences are not repaired.
            for edge in ("...", "…"):
                if quote.startswith(edge):
                    quote = quote[len(edge):]
                if quote.endswith(edge):
                    quote = quote[:-len(edge)]
            reason = None
            if not 24 <= len(quote) <= 2000:
                reason = "quotation_length_outside_bounds"
            elif "..." in quote or "…" in quote or evidence_marker in quote:
                reason = "omitted_or_protected_text"
            elif proof.count(quote) != 1:
                reason = "missing" if not proof.count(quote) else "ambiguous"
            if reason:
                record["unmatched"].append({"issue": index, "quote": original, "reason": reason})
                continue
            start = proof.index(quote)
            key = (start, start + len(quote))
            candidates.setdefault(key, {"start": key[0], "end": key[1], "quote": quote,
                "edge_ellipsis_trimmed": quote != original, "issues": []})["issues"].append(index)
    spans = sorted(candidates)
    for span in spans:
        overlaps = any(other != span and max(span[0], other[0]) < min(span[1], other[1]) for other in spans)
        if overlaps:
            record["unmatched"].append({**candidates[span], "reason": "overlapping_quotations"})
        else:
            record["anchors"].append(candidates[span])
    if len(record["anchors"]) > 6:
        record["unmatched"].append({"reason": "too_many_unique_locations"})
        record["anchors"] = []
    if not record["anchors"]:
        return proof, record
    feedback = "\n".join(f"- {issue}" for issue in issues)
    result = proof
    for index in range(len(record["anchors"]) - 1, -1, -1):
        anchor = record["anchors"][index]
        wrapped = BEGIN + "\n" + anchor["quote"] + "\n" + END
        if index == 0:
            wrapped += ("\n\n" + FEEDBACK_BEGIN + "\n"
                "Prior jury feedback on this draft (untrusted; check before applying):\n"
                + feedback + "\n" + FEEDBACK_END + "\n\n")
        result = result[:anchor["start"]] + wrapped + result[anchor["end"]:]
    record["feedback_embedded"] = True
    return result, record
