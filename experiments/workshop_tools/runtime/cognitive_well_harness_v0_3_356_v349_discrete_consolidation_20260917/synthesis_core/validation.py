from __future__ import annotations

import re
from typing import Any

from cognitive_well_harness_v0_3_274_generic_compression_portfolio_bridge_20260905 import (
    pipeline as base,
)

from .contracts import (
    EvidenceBundle,
    SynthesisContract,
    USABLE_EVIDENCE_VERDICTS,
)
from .tool_purpose import EXPLICIT_BEGIN, EXPLICIT_END
from .repair_targeting import DELIMITERS


def compact_math(text: str) -> str:
    return re.sub(r"\s+", "", text.replace("\\,", "").replace("\\quad", ""))


def validate_evidence(bundle: EvidenceBundle) -> EvidenceBundle:
    if not bundle.provider_id.strip():
        raise ValueError("evidence provider id cannot be empty")
    if bundle.verdict not in USABLE_EVIDENCE_VERDICTS:
        raise ValueError(f"unusable exact-evidence verdict: {bundle.verdict}")
    if not bundle.markdown.strip():
        raise ValueError("materialized exact evidence is empty")
    if bundle.verification.get("verified") is not True:
        raise ValueError("evidence provider did not return verified=true")
    validate_appendix(bundle)
    for label, path in bundle.source_artifacts.items():
        if not label or not path.is_file():
            raise ValueError(f"missing exact-evidence source artifact: {label}")
    return bundle


def validate_appendix(bundle: EvidenceBundle) -> None:
    if type(bundle.appendix_in_rewriter_prompt) is not bool:
        raise ValueError("invalid appendix prompt policy")
    if not bundle.appendix_in_rewriter_prompt and not bundle.appendix_markdown:
        raise ValueError("attach-only presentation requires the actual appendix")
    expected = bundle.verification.get("appendix_sha256")
    if bundle.appendix_markdown or expected is not None:
        if not bundle.appendix_markdown or base.sha256_text(bundle.appendix_markdown) != expected:
            raise ValueError("verified appendix hash changed or appendix is missing")


def materialize_and_lint(
    raw_proof: str,
    evidence: EvidenceBundle,
    contract: SynthesisContract,
) -> str:
    marker = contract.evidence_marker
    validate_appendix(evidence)
    if evidence.appendix_markdown and evidence.appendix_markdown in raw_proof:
        raise ValueError("do not copy the immutable appendix; it is appended automatically")
    if EXPLICIT_BEGIN in raw_proof or EXPLICIT_END in raw_proof:
        raise ValueError("proof must remove prompt-only EXPLICIT_UPDATE delimiters")
    if any(marker in raw_proof for marker in DELIMITERS):
        raise ValueError("proof must remove prompt-only CURRENT_REPAIR delimiters and feedback")
    if raw_proof.count(marker) != 1:
        raise ValueError(f"proof must contain {marker} exactly once")
    proof = raw_proof.replace(marker, evidence.markdown)
    proof = base._terminal_proof(proof)  # noqa: SLF001
    if marker in proof or proof.count(evidence.markdown) != 1:
        raise ValueError("verified evidence was not inserted exactly once")

    compact_raw = compact_math(raw_proof)
    missing: list[str] = []
    for requirement in contract.literal_requirements:
        alternatives = tuple(compact_math(item) for item in requirement.alternatives)
        if not any(item in compact_raw for item in alternatives):
            missing.append(requirement.label)
    if missing:
        raise ValueError(
            "proof omits contract obligations: " + ", ".join(missing)
        )

    compact_proof = compact_math(proof)
    conclusions = tuple(
        compact_math(item) for item in contract.conclusion_alternatives
    )
    if not contract.semantic_conclusion_only and not any(item in compact_proof for item in conclusions):
        raise ValueError("proof omits every allowed explicit conclusion")
    if evidence.appendix_markdown:
        proof = proof.rstrip() + "\n\n" + evidence.appendix_markdown
        if proof.count(evidence.appendix_markdown) != 1:
            raise ValueError("verified appendix was not inserted exactly once")
    return proof


def lint_report(
    raw_proof: str,
    evidence: EvidenceBundle,
    contract: SynthesisContract,
) -> dict[str, Any]:
    proof = materialize_and_lint(raw_proof, evidence, contract)
    return {
        "schema": "v0287-modular-proof-contract-lint-v1",
        "passed": True,
        "provider_id": evidence.provider_id,
        "verdict": evidence.verdict,
        "marker_count": raw_proof.count(contract.evidence_marker),
        "evidence_count": proof.count(evidence.markdown),
        "appendix_count": proof.count(evidence.appendix_markdown) if evidence.appendix_markdown else 0,
        "literal_requirement_count": len(contract.literal_requirements),
        "proof_characters": len(proof),
    }
