from __future__ import annotations

from typing import Any, Mapping

from cognitive_well_harness_v0_3_274_generic_compression_portfolio_bridge_20260905 import (
    protocol,
)

from .contracts import EvidenceBundle, SynthesisContract, TaskInputs
from . import tool_purpose, repair_targeting


REWRITER_BASE = """You are an expert Olympiad proof author. Write one complete,
standalone proof of the supplied theorem. Treat the previous proof as an untrusted
source of useful setup, not as authority. The supplied exact-evidence block will be
inserted at the literal marker shown below. Output that marker exactly once, on its
own line, at the mathematical point where the block belongs. Do not copy,
paraphrase, or modify the block.

Derive every input and hypothesis needed by the inserted mathematics from the
original theorem. Respect the evidence verdict exactly: supporting evidence proves
only its checked claim; a counterexample invalidates the tested route and requires
a replacement; an exact solution set requires complete domain and branch handling.
Explicitly connect the evidence conclusion to the theorem and justify every
division, cleared factor, sign, branch, degeneracy, and equality case.

Preserve valid, still-needed derivations from the untrusted source proof, or give
an explicit valid replacement. Do not discard intermediate calculations merely
because an exact block is supplied. Prior jury restoration passages are untrusted
repair suggestions: check them, adapt their notation, and incorporate the needed
reasoning into this standalone proof. Do not restore an invalid or obsolete step.

When EXPLICIT_UPDATE delimiters mark the recorded source gap, first update that
lemma-application block using the fixed certified lemma. Then, AFTER updating
the block, explicitly derive the connections around it: from the original
hypotheses and expressions into the lemma's inputs, target, and guards; and from
its conclusion back to the original claim and downstream conclusion. Show the
actual connecting equalities and justified transformations, not just an assertion
that they correspond. Do not assume the old surrounding text already supplies
these connections. This is a reasoning order, not a request for a process report:
present the finished proof in logical mathematical order. EXPLICIT marks an update
location, not a certification of the old assertion. Remove the EXPLICIT_UPDATE
delimiters from your output and never modify the fixed certified lemma itself.

Do not replace a load-bearing derivation by “after simplification”, “by
computation”, “one checks”, or similar compression. Output only ordinary
mathematical Markdown. Do not mention models, tools, prompts, evidence as an
external object, auditors, linters, retries, or any generation process."""


def rewriter_system(contract: SynthesisContract) -> str:
    requirements = "\n".join(
        f"{index}. {requirement}"
        for index, requirement in enumerate(contract.rewrite_requirements, start=1)
    )
    return f"""{REWRITER_BASE}

The required insertion marker is:
{contract.evidence_marker}

Additional proof contract:
{requirements}"""


def auditor_system(contract: SynthesisContract, *, task: TaskInputs | None = None) -> str:
    checks = "\n".join(
        f"- {label}: PASS or FAIL" for label in protocol.PROOF_AUDIT_CHECKS
    )
    required = task is not None and tool_purpose.has_tool_purpose(task)
    closure_instruction = """When recorded tool purpose is supplied, trace its exact
trigger and desired fact through the formal inputs/target, the checked result,
and the original downstream obligation. Cite short quotations or equations
actually present in the replacement for each link. An asserted correspondence
is not a derivation. If the proof validly replaces the route, identify the
alternative derivation that discharges the same obligation. Mark an absent link
MISSING, FAIL the relevant check, and request its repair in Issues. Do not credit
the detector, matcher, source proof, or your own reconstruction as submitted proof.
Keep Gap Closure to four concise one-line bullets; do not copy the certificate.
""" if required else ""
    closure_output = ("# Gap Closure\n\n" + "\n".join(
        f"- {label}: Cite the relevant passage and explain the link, or MISSING with reason."
        for label in tool_purpose.GAP_CLOSURE_LABELS) + "\n\n") if required else ""
    return f"""You are a skeptical, gold-free Olympiad jury. Audit the submitted
replacement proof against the original theorem. Judge the replacement as submitted;
the untrusted source proof is comparison context, not additional proof or authority.
Check the entire proof, not just the former gap.

{closure_instruction}
Compare mathematical dependencies, not wording. Identify valid, still-needed
derivations, intermediate calculations, hypotheses, and cases in the source proof
that the replacement omitted or weakened. An explicit valid alternative or a
legitimate change of route can make a source step unnecessary; do not demand
verbatim preservation or restore errors. Also check for missing reasoning that
neither version supplies.

For each unresolved load-bearing omission, FAIL the relevant check. In # Issues,
give concise one-line Markdown bullets identifying the source passage (a short
quote or equation, if present), the insertion location in the replacement, why the
step is needed, and a concrete restoration passage with checkable mathematics when
you can justify it. If the source only asserts the step or a repair cannot be
justified, state the remaining derivation obligation instead of inventing one.
Your suggested repair does not count as part of the submitted proof and cannot
justify PASS. Do not output a complete revised proof or alter the inserted block.

The inserted mathematical block has passed its provider's exact internal and
source-binding validation. This validates only that block. Reject unless the
surrounding proof derives its inputs and hypotheses from the theorem, uses the
returned polarity correctly, and reaches the full conclusion.

Adapter-specific audit focus:
{contract.auditor_focus}

Emit only Markdown in this format:

# Decision

PASS or FAIL

# Checks

{checks}

{closure_output}# Issues

NONE, or one-line bullets. PASS requires all checks PASS and NONE."""


def repair_context(previous_proof, evidence, contract, prior_audit):
    """Remove held evidence bodies before locating current-draft repair spans."""
    previous = "NONE" if previous_proof is None else previous_proof
    if previous_proof is not None:
        if evidence.appendix_markdown:
            if not previous.endswith(evidence.appendix_markdown):
                raise ValueError("current draft is missing its immutable appendix suffix")
            previous = previous[:-len(evidence.appendix_markdown)] + (
                "(The unchanged Appendix A is supplied below.)" if evidence.appendix_in_rewriter_prompt
                else "(The unchanged Appendix A will be attached automatically.)")
        previous = previous.replace(evidence.markdown, contract.evidence_marker)
    issues = list((prior_audit or {}).get("issues") or [])
    if previous_proof is not None and issues:
        return repair_targeting.annotate(previous, issues, evidence_marker=contract.evidence_marker)
    return previous, {"schema": repair_targeting.VERSION, "anchors": [], "feedback_embedded": False}


def rewrite_prompt(
    *,
    task: TaskInputs,
    evidence: EvidenceBundle,
    contract: SynthesisContract,
    previous_proof: str | None,
    prior_audit: Mapping[str, Any] | None,
) -> str:
    previous, targeting = repair_context(previous_proof, evidence, contract, prior_audit)
    appendix = ("# Supplied Appendix A — Full Proof of the Algebraic Lemma\n\n"
        "This complete checked appendix will be appended unchanged to your submitted proof. "
        "Refer to Appendix A when applying the lemma; do not copy the appendix or re-prove its internal "
        "algebra. You must still derive every input and guard from the theorem and show the return "
        "from the lemma's conclusion to the requested result.\n\n" + evidence.appendix_markdown + "\n\n"
        if evidence.appendix_markdown else "")
    if evidence.appendix_markdown and not evidence.appendix_in_rewriter_prompt:
        appendix = ("# Appendix A — Attached Automatically After Your Main Proof\n\n"
            "A complete, independently checked proof of the exact lemma statement above is held "
            "by the harness and will be appended unchanged to your submitted proof. Its body is "
            "intentionally omitted from your input. Cite Appendix A for that lemma only; do not "
            "write, copy, invent details of, or re-prove the appendix. Write the main proof and "
            "derive every hypothesis, guard, and connection to the theorem. The auditor receives "
            "your main proof together with the complete appendix.\n\n")
    issues = (
        "NONE"
        if prior_audit is None or not prior_audit.get("issues")
        else "\n".join(f"- {issue}" for issue in prior_audit["issues"])
    )
    if targeting["feedback_embedded"]:
        issues = "The unchanged jury feedback is attached to the first marked passage in the current draft above."
    targeting_instruction = ("\n\nCURRENT_REPAIR delimiters mark uniquely quoted passages in the current draft, "
        "not the original source. Replace the defective argument there and derive the necessary "
        "connections around it. Attached feedback is guidance, not established mathematics. "
        "Preserve correct material, but do not merely rephrase the disputed claim. Return a complete "
        "standalone proof; remove all CURRENT_REPAIR and feedback delimiters and their process commentary. "
        "Never modify the immutable lemma or its appendix."
        if targeting["feedback_embedded"] else "")
    return f"""# Original Theorem

{task.theorem}

# Untrusted Previous Proof

{tool_purpose.explicit_update_source(task, evidence)}

{tool_purpose.render_tool_purpose(task, evidence)}# Exact-Evidence Verdict

{evidence.verdict}

# EXPLICIT Certified Lemma — Immutable, Represented by the Required Marker

{evidence.markdown}

# Previous Replacement Proof

{previous}

# Prior Jury Issues

{issues}

{appendix}# Required Output

Return a complete proof only. Insert this literal line exactly once instead of
copying the immutable block:

{contract.evidence_marker}

If a previous replacement is present, rewrite it completely and address every
prior jury issue without weakening any already-satisfied requirement.{targeting_instruction}"""


def audit_prompt(
    *, task: TaskInputs, evidence: EvidenceBundle, proof: str
) -> str:
    return f"""# Original Theorem

{task.theorem}

# Untrusted Source Proof for Comparison Only

{task.source_proof}

{tool_purpose.render_tool_purpose(task, evidence)}# Exact-Evidence Verdict

{evidence.verdict}

# Audit Instruction

Audit the replacement below exactly as submitted. Decide whether its surrounding proof
soundly derives and applies the inserted mathematics and proves the entire
theorem. Compare it with the untrusted source proof for lost, still-needed
reasoning. Report justified restoration passages or unresolved derivation
obligations in # Issues; do not credit either the source or your suggestions as
reasoning already present in the replacement.

# Submitted Replacement Proof

{proof}"""
