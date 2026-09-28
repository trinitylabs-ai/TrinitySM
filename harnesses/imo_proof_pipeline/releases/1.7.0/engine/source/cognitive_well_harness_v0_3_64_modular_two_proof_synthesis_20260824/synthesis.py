from __future__ import annotations

import concurrent.futures
import re
from pathlib import Path
from typing import Any

from .contracts import SYNTHESIS_CONFIGURATIONS, sha256_text
from .model_runtime import ModelRuntime, write_json
from .prompts import synthesis_prompt


LOCAL_LABELS = tuple(chr(ord("A") + index) for index in range(26))
LOCAL_LEMMA_REFERENCE_RE = re.compile(r"\bLemma\s+([A-Z])\b", re.IGNORECASE)
INTERNAL_ID_RE = re.compile(r"\bR\d+H\d+\b", re.IGNORECASE)
CASE_HEADING_RE = re.compile(r"(?im)^\s*(?:#{1,6}\s*)?(?:\*\*)?CASE\s+\d+\b")


def label_verified_lemmas(verified: list[dict[str, Any]]) -> list[dict[str, str]]:
    if len(verified) > len(LOCAL_LABELS):
        raise ValueError("too many verified lemmas for local labels")
    return [
        {
            "label": LOCAL_LABELS[index],
            "source_lemma_id": str(row["lemma_id"]),
            "statement": str(row["statement"]),
            "proof": str(row["proof"]),
        }
        for index, row in enumerate(verified)
    ]


def cited_labels(main_proof: str) -> list[str]:
    seen: list[str] = []
    for match in LOCAL_LEMMA_REFERENCE_RE.finditer(main_proof):
        label = match.group(1).upper()
        if label not in seen:
            seen.append(label)
    return seen


def assemble_proof(
    *,
    main_proof: str,
    lemmas: list[dict[str, str]],
    gate_policy: dict[str, Any],
) -> dict[str, Any]:
    allowed = {row["label"]: row for row in lemmas}
    used = cited_labels(main_proof)
    unknown = [label for label in used if label not in allowed]
    selected = [row for row in lemmas if row["label"] in used]
    unused = [label for label in allowed if label not in used]

    blocks = [
        f"### Lemma {row['label']}\n\n"
        f"{row['statement']}\n\n"
        f"**Proof.** {row['proof']}\n\n"
        f"**End of proof of Lemma {row['label']}.**"
        for row in selected
    ]
    appendix = ""
    if blocks:
        appendix = (
            "\n\n---\n\n## Appendix: proofs of cited lemmas\n\n"
            + "\n\n".join(blocks)
        )
    combined = main_proof.rstrip() + appendix + "\n"

    violations: list[str] = []
    if not main_proof.strip():
        violations.append("empty_main_proof")
    if INTERNAL_ID_RE.search(main_proof):
        violations.append("internal_lemma_identifier_exposed")
    if unknown:
        violations.append("unknown_local_lemma_reference")
    if gate_policy["require_all_verified_lemmas"] and unused:
        violations.append("not_all_verified_lemmas_cited")
    if len(selected) < int(gate_policy["minimum_cited_lemmas"]):
        violations.append("too_few_certified_lemmas_cited")
    case_heading_count = len(CASE_HEADING_RE.findall(main_proof))
    if case_heading_count < int(gate_policy["minimum_case_headings"]):
        violations.append("too_few_explicit_case_headings")

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
        "structural_gate": {"passed": not violations, "violations": violations},
    }


def generate_one(
    *,
    runtime: ModelRuntime,
    problem: str,
    lemmas: list[dict[str, str]],
    anchor_proof: str,
    synthesis_instructions: str,
    gate_policy: dict[str, Any],
    config: dict[str, Any],
    output_dir: Path,
) -> dict[str, Any]:
    candidate_id = str(config["candidate_id"])
    destination = output_dir / candidate_id
    prompt = synthesis_prompt(
        family=str(config["family"]),
        problem=problem,
        lemmas=lemmas,
        anchor_proof=(
            anchor_proof if config["family"] == "anchored_refinement" else None
        ),
        synthesis_instructions=synthesis_instructions,
        require_all_lemmas=bool(gate_policy["require_all_verified_lemmas"]),
        minimum_case_headings=int(gate_policy["minimum_case_headings"]),
    )
    generated = runtime.text(
        role="gemma",
        prompt=prompt,
        destination=destination,
        stage="main_proof",
        temperature=float(config["temperature"]),
        max_tokens=32_768,
        seed_label=f"synthesis:{candidate_id}",
    )
    main_proof = str(generated["text"]).strip()
    assembly = assemble_proof(
        main_proof=main_proof,
        lemmas=lemmas,
        gate_policy=gate_policy,
    )
    combined = str(assembly["combined_proof"]).strip()
    result = {
        **config,
        "main_proof_sha256": sha256_text(main_proof),
        "proof_sha256": sha256_text(combined),
        "assembly": {
            key: assembly[key]
            for key in (
                "allowed_labels",
                "used_labels",
                "unused_labels",
                "unknown_labels",
                "appended_labels",
                "case_heading_count",
                "structural_gate",
            )
        },
        "generation": generated["metadata"],
    }
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "main_proof.md").write_text(main_proof + "\n", encoding="utf-8")
    (destination / "proof_with_appendix.md").write_text(
        combined + "\n",
        encoding="utf-8",
    )
    write_json(destination / "synthesis_result.json", result)
    return {**result, "proof": combined}


def generate_arm_samples(
    *,
    runtime: ModelRuntime,
    arm: str,
    problem: str,
    verified: list[dict[str, Any]],
    anchor_proof: str,
    synthesis_instructions: str,
    gate_policy: dict[str, Any],
    output_dir: Path,
) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    lemmas = label_verified_lemmas(verified)
    configurations = tuple(
        row for row in SYNTHESIS_CONFIGURATIONS if row["arm"] == arm
    )
    if len(configurations) != 4:
        raise RuntimeError(f"arm {arm!r} must have exactly four synthesis samples")
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        candidates = list(
            executor.map(
                lambda config: generate_one(
                    runtime=runtime,
                    problem=problem,
                    lemmas=lemmas,
                    anchor_proof=anchor_proof,
                    synthesis_instructions=synthesis_instructions,
                    gate_policy=gate_policy,
                    config=config,
                    output_dir=output_dir,
                ),
                configurations,
            )
        )
    return lemmas, candidates
