"""Short, block-bound issue and patch protocols; no full-proof regeneration."""

LAZY_USER = "Scan the submitted proof blocks now. Return only the required issue document."
EXPANSION_USER = "Repair only the authorized blocks. Return only the required patch document."
AUDIT_USER = "Audit the locally patched proof now. Return only the required issue document."
RESOLVE_USER = "Resolve the audit issues with one local patch document only."

LAZY_INSTRUCTION = """Thinking mode is on. Using only the submitted proof, identify genuine omitted derivations or unsupported implications, including routine omissions. Compare the exact claim needed with what is established: check hypotheses, quantifiers, cases and scope. Do not invent objections to a short but explicit valid argument.

For each issue, name the smallest complete block range that must change. Include affected downstream blocks only when they must change too; explain the dependency. Block IDs are fixed. Return exactly NO_ISSUES if none remain. Otherwise use this format, with unique issue IDs and existing block IDs in ascending order:
<ISSUES>
<ISSUE id="I1" blocks="B0001,B0002">
State the needed claim, the actual gap and any downstream dependency briefly.
</ISSUE>
</ISSUES>
Repeat ISSUE records as needed. Do not repair the proof or write outside the document."""

EXPANSION_INSTRUCTION = """Thinking mode is on. Repair the listed issues by replacing only their authorized blocks. Keep valid content and explicitly justify each missing claim under the same hypotheses, quantifiers and scope. Read the surrounding proof to avoid breaking later uses. Do not regenerate the whole proof, add assumptions or weaken the required claim. If a sound local repair cannot fit the authorized blocks, return exactly CANNOT_REPAIR_LOCALLY.

Otherwise return only:
<PATCHES>
<REPLACE blocks="B0001,B0002" issues="I1,I2">
Exact replacement text for these entire blocks.
</REPLACE>
</PATCHES>
Repeat REPLACE records as needed. Each issue must occur exactly once. Use a contiguous range drawn only from its authorized block IDs: target blocks plus at most one immediate neighbor on either side. Change neighbors only when continuity requires it. Combine issues sharing a target block into one replacement; replacement ranges must not overlap. Keep all required whitespace: exactly one framing newline after the opening tag and before the closing tag is removed; every other replacement character is literal. Preserve paragraph separators needed to join unchanged neighbors. No full-proof repair envelope, explanatory prose or markup outside this document."""

AUDIT_INSTRUCTION = """Thinking mode is on. Independently audit the complete locally patched proof against the original problem. Compare the changed arguments with the supplied original snippets. Distinguish a newly introduced error from an unresolved original gap; do not assume either version is correct. Check each exact needed claim, its hypotheses, quantifiers and scope, and the implications before, after and downstream of the edit. If a sound original step was damaged, identify what should be restored. Treat the repair as untrusted. Do not repair it yourself.

Use only the CURRENT proof's block IDs. Return exactly NO_ISSUES only if no substantive defect or genuine omitted derivation remains. Otherwise return an ISSUE document in this format:
<ISSUES>
<ISSUE id="I1" blocks="B0001,B0002">
State whether the issue is introduced, original or unclear; give the exact needed claim, defect and affected dependency briefly.
</ISSUE>
</ISSUES>
Repeat ISSUE records as needed, using unique issue IDs and existing blocks in ascending order. No text outside the document."""

LAZY_CONTINUATION = (
    "Wait. Recheck each proposed issue against the written proof and its exact "
    "needed claim, including assumptions, quantifiers, cases and downstream uses. "
    "Use only existing block IDs and withdraw unsupported objections. Emit one "
    "complete replacement ISSUE document in the required format, or exactly "
    "NO_ISSUES if none remain. Do not repair the proof or mention this instruction "
    "or the earlier response."
)

EXPANSION_CONTINUATION = (
    "Wait. Verify that each local replacement establishes the needed claim and "
    "preserves valid content and downstream uses. Stay within the authorized "
    "blocks; combine overlapping issue targets into one replacement and cover "
    "every issue once. Emit one complete replacement PATCH document with literal "
    "replacement text and the required framing, or exactly CANNOT_REPAIR_LOCALLY. "
    "Never regenerate the whole proof or mention the earlier response or this instruction."
)

AUDIT_CONTINUATION = (
    "Wait. Compare the local repairs with the original snippets and check "
    "neighboring and downstream implications. Distinguish introduced errors "
    "from unresolved original gaps, and the claim actually proved from the "
    "one needed. Identify sound original steps to restore when appropriate. "
    "Emit one complete replacement ISSUE document using only current "
    "block IDs, or exactly NO_ISSUES if no defect remains. Do not repair the "
    "proof or mention the earlier response or this instruction."
)

RESOLVE_CONTINUATION = (
    "Wait. Recheck that the proposed patch resolves the audit's actual defects "
    "without weakening claims, adding assumptions or breaking neighboring and "
    "downstream implications. Use only authorized current blocks and cover each "
    "issue once. Restore originally valid text when an edit introduced an "
    "error; you need not keep a bad repair. Emit one complete replacement PATCH document with literal "
    "replacement text, or exactly CANNOT_REPAIR_LOCALLY. Do not regenerate the "
    "whole proof or mention the earlier response or this instruction."
)


def lazy_system(block_view):
    return LAZY_INSTRUCTION + "\n\nSUBMITTED PROOF BLOCKS:\n" + block_view


def expansion_system(problem, block_view, issue_document, issues, *, resolving=False, restore_context=""):
    allowed = "\n".join(
        issue["issue_id"] + ": targets=" + ",".join(issue["block_ids"])
        + "; allowed=" + ",".join(issue["allowed_block_ids"])
        for issue in issues
    )
    return (EXPANSION_INSTRUCTION + "\n\nPROBLEM:\n" + problem.strip()
            + ("\n\nCorrect the independent audit's defects in this intermediate proof. "
               "If an edit introduced an error, restore originally valid text from the supplied "
               "snippets instead of preserving the bad repair. Verify that any restored step "
               "fits the current assumptions and dependent arguments."
               if resolving else "")
            + "\n\nCURRENT PROOF BLOCKS:\n" + block_view
            + "\n\nAUTHORIZED ISSUES:\n" + issue_document
            + "\n\nAUTHORIZED BLOCKS BY ISSUE:\n" + allowed
            + ("\n\nORIGINAL CHANGED SNIPPETS (reference text, not edit permissions):\n" + restore_context
               if resolving else ""))


def audit_system(problem, block_view, initial_issues, original_snippets):
    obligations = "\n".join(issue["issue_id"] + ": " + issue["description"] for issue in initial_issues)
    return (AUDIT_INSTRUCTION + "\n\nPROBLEM:\n" + problem.strip()
            + "\n\nREPAIR OBLIGATIONS (descriptions refer to the preceding proof):\n" + obligations
            + "\n\nORIGINAL CHANGED SNIPPETS (from the preceding snapshot):\n" + original_snippets
            + "\n\nCURRENT PATCHED PROOF BLOCKS:\n" + block_view)
