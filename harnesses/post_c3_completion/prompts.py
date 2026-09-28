"""Proof-only completion check and local-repair instructions for saved C3 proofs.

The expansion system prompt and repair-envelope parser remain owned by the
frozen frontend.  EXPANSION_GUIDANCE is appended to its existing user message.
"""

LAZY_SYSTEM_PROMPT = """Thinking mode is on. Using only the submitted proof, scan for genuine omitted derivations and unsupported implications, including routine omissions and phrases such as 'it is clear', 'one can show', or 'by a standard argument'.

At each suspected gap, compare the exact claim needed there with what the written argument actually establishes. Check assumptions, quantifiers, cases and scope; a weaker claim or an added assumption does not fill the gap. A short but explicit valid derivation is not an omission.

List each genuine issue briefly, identifying its location, the needed claim and what is missing or insufficient. Do not repair the proof or invent an objection. Output exactly NO_ISSUES only if no such issue remains."""


def lazy_phrasing(proof: str) -> str:
    """Keep the original proof-only system-message placement."""
    if not isinstance(proof, str) or not proof.strip():
        raise ValueError("lazy check requires a nonempty proof")
    return LAZY_SYSTEM_PROMPT + "\n\nPROOF:\n" + proof + "\n"


LAZY_CONTINUATION = (
    "Wait. Recheck each suspected gap against the submitted proof. Compare the "
    "exact needed claim with what the written argument establishes, including "
    "assumptions, quantifiers, cases and scope. Look for genuine omitted "
    "derivations even when routine, and withdraw objections contradicted by "
    "the text. Emit one complete replacement issue report, or exactly NO_ISSUES "
    "only if none remain. Do not repair the proof or mention the earlier response "
    "or this instruction."
)

EXPANSION_GUIDANCE = (
    "For each repaired gap, explicitly state and justify the exact claim "
    "established by the inserted argument, then check that it implies the claim "
    "needed there with the same hypotheses, quantifiers and scope. Do not "
    "substitute a weaker statement or add assumptions. Make local edits and "
    "preserve valid content; keep the required repair envelope unchanged."
)

EXPANSION_CONTINUATION = (
    "Wait. Audit each proposed local repair: explicitly state and justify what "
    "the inserted argument proves, then compare it with the exact claim needed "
    "at that point. Check hypotheses, quantifiers, cases and scope; do not add "
    "assumptions or substitute a weaker conclusion. Preserve valid content. "
    "Emit one complete replacement repair envelope in the original required "
    "format, including the full repaired proof. Do not append commentary or "
    "mention the earlier response or this instruction."
)
