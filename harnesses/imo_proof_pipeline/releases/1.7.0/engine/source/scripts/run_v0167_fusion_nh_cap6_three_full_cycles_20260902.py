from __future__ import annotations

import argparse
import concurrent.futures
import json
import math
import re
import sys
import threading
import traceback
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_ROOT = REPO_ROOT / "scripts"
for import_root in (REPO_ROOT, SCRIPTS_ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

import run_v0164_nh_groupwise_multicycle_cleanup_20260902 as nh_runner


HARNESS_VERSION = "v0.3.167-fusion-nh-cap6-three-full-cycles-20260902"
DEFAULT_OUTPUT = (
    REPO_ROOT / "runs/v0167_fusion_nh_cap6_three_full_cycles_20260902"
)
TOTAL_CYCLES = 3
MAX_NH_PACKETS_PER_CALL = 6

# Reuse the already-audited cumulative atomic patch implementation, with the
# requested smaller packet cap and a new version in every stage-input digest.
nh_runner.HARNESS_VERSION = HARNESS_VERSION
nh_runner.MAX_NH_PACKETS_PER_CALL = MAX_NH_PACKETS_PER_CALL

ADDITIONAL_LABEL_A = (
    REPO_ROOT / "runs/v0168_binary_novelty_additional_shard_a_20260902"
)
ADDITIONAL_LABEL_B = (
    REPO_ROOT / "runs/v0168_binary_novelty_additional_shard_b_20260902"
)
DEFAULT_CASES = {
    # The original one-proof-per-problem run.
    "p1:t07_r02": nh_runner.DEFAULT_CASES["p1:t07_r02"],
    "p2:t10_r02": nh_runner.DEFAULT_CASES["p2:t10_r02"],
    "p3:t10_r01": nh_runner.DEFAULT_CASES["p3:t10_r01"],
    "p4:t07_r02": nh_runner.DEFAULT_CASES["p4:t07_r02"],
    "p5:t07_r02": nh_runner.DEFAULT_CASES["p5:t07_r02"],
    # Three additional frozen proofs per problem. Reuse completed labels where
    # available; v0168 produces only the missing label artifacts.
    "p1:t07_r01": ADDITIONAL_LABEL_A / "p1/t07_r01",
    "p1:t10_r01": nh_runner.DEFAULT_CASES["p1:t10_r01"],
    "p1:t10_r02": ADDITIONAL_LABEL_A / "p1/t10_r02",
    "p2:t07_r01": ADDITIONAL_LABEL_A / "p2/t07_r01",
    "p2:t07_r02": ADDITIONAL_LABEL_A / "p2/t07_r02",
    "p2:t10_r01": nh_runner.DEFAULT_CASES["p2:t10_r01"],
    "p3:t07_r01": ADDITIONAL_LABEL_A / "p3/t07_r01",
    "p3:t07_r02": nh_runner.DEFAULT_CASES["p3:t07_r02"],
    "p3:t10_r02": ADDITIONAL_LABEL_A / "p3/t10_r02",
    "p4:t07_r01": ADDITIONAL_LABEL_B / "p4/t07_r01",
    "p4:t10_r01": ADDITIONAL_LABEL_B / "p4/t10_r01",
    "p4:t10_r02": ADDITIONAL_LABEL_B / "p4/t10_r02",
    "p5:t07_r01": ADDITIONAL_LABEL_B / "p5/t07_r01",
    "p5:t10_r01": ADDITIONAL_LABEL_B / "p5/t10_r01",
    "p5:t10_r02": ADDITIONAL_LABEL_B / "p5/t10_r02",
}
DEFAULT_SELECTED_CASE_KEYS = nh_runner.DEFAULT_SELECTED_CASE_KEYS

FUSION_ROOT = (
    REPO_ROOT
    / "runs/v053_fusion_all36_gemma4_bf16_mtp4_t04_gpu0_b4_16k_20260823_1748"
    / "fusion/temperature_0_4/gpu0"
)

# P1's exact-proof Fusion result is ACCEPT_AS_WRITTEN, not a repair packet. It
# therefore remains a deterministic pass-through at the Fusion-resolution step.
FUSION_SOURCES: dict[str, dict[str, str] | None] = {
    "p1:t07_r01": None,
    "p1:t07_r02": None,
    "p1:t10_r01": None,
    "p1:t10_r02": None,
    "p2:t07_r01": {
        "relative_dir": "p2/t07_r01",
        "raw_sha256": "81343a600dbf300ad8844660ac32e7260c0bcb6ce206f8ec8f27931a5d2fb5b0",
        "content_sha256": "80f84a9c8d9df1ad6b6ece17169799d1a278a719074510ef630c63b5103ccbea",
    },
    "p2:t07_r02": {
        "relative_dir": "p2/t07_r02",
        "raw_sha256": "7e403b2f0e864bd778144943497f988699d592b69ddd2ee2252217c71d3f90a5",
        "content_sha256": "ebcd5988b79ce4f1da779f097cb735f1129568c92c6c84fd6b099e638dc03579",
    },
    "p2:t10_r01": {
        "relative_dir": "p2/t10_r01",
        "raw_sha256": "2403040347aa3a14aa7b9bbbe3cc3424d9165ebce00ae84a57f56b90cadc5845",
        "content_sha256": "f4a7ab13661fb92492b344ea1ecbb7eb6ce44c87ba8c03a0d49d88ad82fe76a2",
    },
    "p2:t10_r02": {
        "relative_dir": "p2/t10_r02",
        "raw_sha256": "9655b0ce9d6fe28624869705aa0d43a04277d55b8ea468da8ac9a4c261f40050",
        "content_sha256": "15be4c58250064ebe87859533620a857286429e3516ddbbb2825ba3c8e97d59c",
    },
    "p3:t10_r01": {
        "relative_dir": "p3/t10_r01",
        "raw_sha256": "19061a74118635e32fe43ebd8625dab0932deca0b6e3896f9549c22d0c15831a",
        "content_sha256": "5cb1003776ac382dea06b298e881fb181a955f91ad917daad23f8f208d79f017",
    },
    "p3:t07_r01": {
        "relative_dir": "p3/t07_r01",
        "raw_sha256": "a6ac3615699ac17821a31764edde8d5832e332b11c1c92ade76b9383dff51e50",
        "content_sha256": "ed2d5c5faae754d4ba19c1503b059d7f882e09cf805cb2d54151fcb766afa8ca",
    },
    "p3:t07_r02": {
        "relative_dir": "p3/t07_r02",
        "raw_sha256": "8a7781ef12d574257a2579bc7a0f082eea7ba833de502d1652cbbec1548863a1",
        "content_sha256": "5adfc80943711f955379ba0a4b61f1005b50048d48350cda62fb15bb6ec6616f",
    },
    "p3:t10_r02": {
        "relative_dir": "p3/t10_r02",
        "raw_sha256": "61a2bdf166c62849629dbaa558b95bd9b0240fc7227ccf97d38986edbd7c2026",
        "content_sha256": "11d09fc82fc7faade085681803eaab7af311610ab4e45a7bd2a5d8ed1a52fa86",
    },
    "p4:t07_r01": None,
    "p4:t07_r02": {
        "relative_dir": "p4/t07_r02",
        "raw_sha256": "8f5b4578496e5a61b6c3da0e01517914831846b35aa0a01456a71af650470b1e",
        "content_sha256": "56c156eb7d5e5c09564e2ad930bbfafaaf7602cef31c7a6d95ff229d413eff8f",
    },
    "p4:t10_r01": {
        "relative_dir": "p4/t10_r01",
        "raw_sha256": "4b254df6ff46ce688d8d1faf007f1eaef622961b82f359edb01b12e2f7f00967",
        "content_sha256": "d5a4a4298c768c789ae934a82bfe220ce41e97fedcf6174ac680f0fea09be4b2",
    },
    "p4:t10_r02": {
        "relative_dir": "p4/t10_r02",
        "raw_sha256": "a756fb8153d8ec96d7f457f57a9118e55137a0130f7a47623326c58bcaebedaa",
        "content_sha256": "c7f1adc3078e5bada7c0145a7ffb58f61a7fee53dd8efbad7a1853dedbebb2f9",
    },
    "p5:t07_r01": {
        "relative_dir": "p5/t07_r01",
        "raw_sha256": "ada077971074055bfd22ae68cb7008affa6c76d4b659a97112d9bc19b9ab1aad",
        "content_sha256": "734a929a8e0235acf0a6127bbfb11d64e80d981932cd14603f76244b6e28dbe0",
    },
    "p5:t07_r02": {
        "relative_dir": "p5/t07_r02",
        "raw_sha256": "a3f4b9438d170708ea93226afd27cec9e7da9f52eca0a6f6d4e0e166ecf24c2b",
        "content_sha256": "7573d21885845a620d05a95e1b75e9fbf5e14b70f4c5af1d94eb8635dbef86ad",
    },
    "p5:t10_r01": {
        "relative_dir": "p5/t10_r01",
        "raw_sha256": "78f293746975c90e4b08303d18f606f3a3807b808889c888c35ea94229057a40",
        "content_sha256": "a30b4f9f431e77496a519566c4624b412733394843e75400e3632b8a22875fd8",
    },
    "p5:t10_r02": {
        "relative_dir": "p5/t10_r02",
        "raw_sha256": "5f654d310d757795e7add6d49597457bc665b480fd5b3930e5ad31431a021af8",
        "content_sha256": "2b8b449b94faa215508640db42723e5b6c21d6fa64d3272d85d665cace2fbc15",
    },
}

SYNTHESIS_LEAK_MARKERS = (
    "FUSION_REPAIR_NEEDED",
    "FUSION_ACCEPT_AS_WRITTEN",
    "END_FUSION_",
    "reviewer_1_assessment",
    "reviewer_2_assessment",
    "reviewer_3_assessment",
    "NH suggestion",
    "<!-- CW_BLOCK",
    "START_BLOCK:",
    "END_BLOCK:",
)


def read_fusion(case: dict[str, Any]) -> dict[str, Any] | None:
    spec = FUSION_SOURCES[case["case_key"]]
    if spec is None:
        return None
    source_dir = FUSION_ROOT / spec["relative_dir"]
    raw_path = source_dir / "fusion.raw_response.json"
    source_prompt_path = source_dir / "fusion.user_prompt.txt"
    nh_runner.validate_source_hash(
        raw_path, spec["raw_sha256"], label=f"{case['case_key']} Fusion raw response"
    )
    raw = nh_runner.read_object(raw_path)
    try:
        content = str(raw["choices"][0]["message"]["content"])
    except (KeyError, IndexError, TypeError) as error:
        raise ValueError(f"malformed Fusion raw response: {raw_path}") from error
    if nh_runner.sha256_text(content) != spec["content_sha256"]:
        raise ValueError(f"{case['case_key']} Fusion content hash drift")
    source_prompt = source_prompt_path.read_text(encoding="utf-8")
    original_proof = str(case["proof"]).strip()
    proof_occurrences = source_prompt.count(original_proof)
    if proof_occurrences != 1:
        raise ValueError(
            f"{case['case_key']} Fusion is not exact-proof aligned: "
            f"proof occurrences={proof_occurrences}"
        )
    if "FUSION_REPAIR_NEEDED" not in content:
        raise ValueError(f"{case['case_key']} configured Fusion is not a repair packet")
    return {
        "content": content,
        "content_sha256": spec["content_sha256"],
        "raw_path": str(raw_path.resolve()),
        "raw_sha256": spec["raw_sha256"],
        "source_prompt_path": str(source_prompt_path.resolve()),
        "source_prompt_sha256": nh_runner.file_sha256(source_prompt_path),
        "exact_original_proof_occurrences_in_source_prompt": proof_occurrences,
    }


def load_case(case_key: str) -> dict[str, Any]:
    case = nh_runner.load_case(case_key, DEFAULT_CASES[case_key])
    return {**case, "fusion": read_fusion(case)}


def fusion_resolution_prompt(
    *, problem: str, current_proof: str, fusion: dict[str, Any], cycle: int
) -> str:
    return f"""You are resolving one submitted Olympiad proof in full-cycle {cycle}
of {TOTAL_CYCLES}. Produce one complete, standalone proof suitable for final
submission.

The Fusion diagnostic below was generated for the original submission. It is
UNVERIFIED and can be incomplete, overly broad, or stale after an earlier cycle.
Independently check every diagnosis against the original problem and the CURRENT
PROOF. The current proof is authoritative. Preserve every correct definition,
case condition, derivation, dependency, caveat, and conclusion already present.
Repair only defects that are real and still unresolved. You may restructure the
proof when mathematically necessary, but do not trade rigorous detail for a shorter
or more elegant argument, and do not invent unsupported bridges.

Return only the complete revised proof. Do not mention Fusion, diagnostics,
reviewers, packets, labels, line IDs, scores, or this instruction. Do not use a
Markdown code fence and do not add editorial commentary. No official solution or
gold answer is supplied.

ORIGINAL PROBLEM
{problem}

CURRENT PROOF
{current_proof}

UNVERIFIED FUSION DIAGNOSTIC FOR THE ORIGINAL SUBMISSION
{fusion['content']}
"""


def fusion_prompt_audit(
    *, prompt: str, case: dict[str, Any], proof: str, fusion: dict[str, Any]
) -> dict[str, Any]:
    content = str(fusion["content"])
    return {
        "schema": "cognitive-well-v0167-fusion-prompt-audit-v1",
        "case_key": case["case_key"],
        "current_proof_sha256": nh_runner.sha256_text(proof),
        "fusion_content_sha256": fusion["content_sha256"],
        "current_proof_occurrence_count": prompt.count(proof),
        "fusion_content_occurrence_count": prompt.count(content),
        "current_proof_supplied_exactly_once": prompt.count(proof) == 1,
        "fusion_supplied_exactly_once": prompt.count(content) == 1,
        "fusion_explicitly_unverified": "UNVERIFIED" in prompt,
        "current_proof_declared_authoritative": "current proof is authoritative"
        in prompt.lower(),
        "gold_supplied": False,
        "nh_packets_supplied": False,
    }


def normalize_synthesized_proof(value: str) -> tuple[str, dict[str, Any]]:
    normalized = value.replace("\r\n", "\n").strip()
    stripped_outer_fence = False
    match = re.fullmatch(
        r"```(?:markdown|md|latex|tex)?[ \t]*\n(?P<body>.*)\n```",
        normalized,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if match is not None:
        normalized = match.group("body").strip()
        stripped_outer_fence = True
    if not normalized:
        raise ValueError("Fusion synthesis returned an empty proof")
    word_count = len(re.findall(r"\S+", normalized))
    if word_count < 80:
        raise ValueError(f"Fusion synthesis is implausibly short: {word_count} words")
    leaked = [marker for marker in SYNTHESIS_LEAK_MARKERS if marker in normalized]
    if leaked:
        raise ValueError(f"Fusion synthesis leaked source metadata: {leaked}")
    return normalized + "\n", {
        "line_endings_normalized": value != value.replace("\r\n", "\n"),
        "outer_whitespace_normalized": value != value.strip(),
        "outer_markdown_fence_stripped": stripped_outer_fence,
        "output_word_count": word_count,
        "source_metadata_leak_markers": leaked,
    }


def fusion_stage_digest(
    *, case: dict[str, Any], proof: str, cycle: int, max_tokens: int
) -> str:
    fusion = case["fusion"]
    return nh_runner.stable_digest(
        {
            "harness_version": HARNESS_VERSION,
            "case_key": case["case_key"],
            "cycle": cycle,
            "input_proof_sha256": nh_runner.sha256_text(proof),
            "fusion_content_sha256": (
                fusion["content_sha256"] if fusion is not None else None
            ),
            "max_tokens": max_tokens,
            "operation": "full_proof_synthesis_from_current_proof_and_unverified_fusion",
        }
    )


def run_fusion_stage(
    *,
    runtime: nh_runner.ResilientModelRuntime,
    case: dict[str, Any],
    proof: str,
    cycle: int,
    stage_dir: Path,
    max_tokens: int,
    seed_namespace: str,
    retry_failed: bool,
) -> tuple[str, dict[str, Any]]:
    digest = fusion_stage_digest(
        case=case, proof=proof, cycle=cycle, max_tokens=max_tokens
    )
    summary_path = stage_dir / "summary.json"
    output_path = stage_dir / "proof.md"
    if summary_path.is_file():
        saved = nh_runner.read_object(summary_path)
        if saved.get("input_sha256") != digest:
            raise ValueError(f"refusing Fusion stage reuse after input drift: {stage_dir}")
        failed = str(saved.get("outcome") or "").startswith("FAILED_CLOSED")
        if saved.get("state") == "completed" and not (retry_failed and failed):
            output = output_path.read_bytes().decode("utf-8")
            if nh_runner.sha256_text(output) != saved.get("output_proof_sha256"):
                raise ValueError(f"saved Fusion proof hash drift: {output_path}")
            return output, saved

    stage_dir.mkdir(parents=True, exist_ok=True)
    fusion = case["fusion"]
    nh_runner.write_json(
        stage_dir / "manifest.json",
        {
            "schema": "cognitive-well-v0167-fusion-resolution-manifest-v1",
            "harness_version": HARNESS_VERSION,
            "created_at": nh_runner.utc_now(),
            "input_sha256": digest,
            "case_key": case["case_key"],
            "cycle": cycle,
            "input_proof_sha256": nh_runner.sha256_text(proof),
            "fusion_source": (
                {
                    key: fusion[key]
                    for key in (
                        "raw_path",
                        "raw_sha256",
                        "content_sha256",
                        "source_prompt_path",
                        "source_prompt_sha256",
                        "exact_original_proof_occurrences_in_source_prompt",
                    )
                }
                if fusion is not None
                else None
            ),
            "policy": {
                "fusion_is_unverified": True,
                "current_proof_is_authoritative": True,
                "full_proof_synthesis": fusion is not None,
                "nh_packets_supplied": False,
                "gold_supplied": False,
                "fail_closed_to_input_proof": True,
            },
        },
    )

    if fusion is None:
        output = proof
        summary = {
            "schema": "cognitive-well-v0167-fusion-resolution-summary-v1",
            "state": "completed",
            "outcome": "SKIPPED_NO_REPAIR_FUSION_PACKET",
            "input_sha256": digest,
            "case_key": case["case_key"],
            "cycle": cycle,
            "model_call_performed": False,
            "input_proof_sha256": nh_runner.sha256_text(proof),
            "output_proof_sha256": nh_runner.sha256_text(proof),
            "byte_identical_noop": True,
            "completed_at": nh_runner.utc_now(),
        }
        nh_runner.write_text_exact(output_path, output)
        nh_runner.write_json(summary_path, summary)
        return output, summary

    prompt = fusion_resolution_prompt(
        problem=case["problem"], current_proof=proof, fusion=fusion, cycle=cycle
    )
    audit = fusion_prompt_audit(prompt=prompt, case=case, proof=proof, fusion=fusion)
    if not audit["current_proof_supplied_exactly_once"]:
        raise ValueError(f"current proof inclusion audit failed: {case['case_key']}")
    if not audit["fusion_supplied_exactly_once"]:
        raise ValueError(f"Fusion inclusion audit failed: {case['case_key']}")
    nh_runner.write_text_exact(stage_dir / "prompt.txt", prompt)
    nh_runner.write_json(stage_dir / "prompt_audit.json", audit)
    try:
        generation = runtime.text(
            role="gemma",
            prompt=prompt,
            destination=stage_dir / "model_call",
            stage="fusion_resolution",
            temperature=0.1,
            max_tokens=max_tokens,
            seed_label=(
                f"{seed_namespace}:{case['case_key']}:cycle-{cycle}:fusion-resolution"
            ),
            user_prompt="Return only the complete revised proof now.",
        )
        output, normalization = normalize_synthesized_proof(
            str(generation.get("text") or "")
        )
        outcome = "NO_CHANGE" if output == proof else "SYNTHESIZED"
        summary = {
            "schema": "cognitive-well-v0167-fusion-resolution-summary-v1",
            "state": "completed",
            "outcome": outcome,
            "input_sha256": digest,
            "case_key": case["case_key"],
            "cycle": cycle,
            "model_call_performed": True,
            "input_proof_sha256": nh_runner.sha256_text(proof),
            "output_proof_sha256": nh_runner.sha256_text(output),
            "byte_identical_noop": output == proof,
            "normalization": normalization,
            "generation_metadata": generation.get("metadata"),
            "completed_at": nh_runner.utc_now(),
        }
    except Exception as error:
        output = proof
        summary = {
            "schema": "cognitive-well-v0167-fusion-resolution-summary-v1",
            "state": "completed",
            "outcome": "FAILED_CLOSED_TO_INPUT_PROOF",
            "input_sha256": digest,
            "case_key": case["case_key"],
            "cycle": cycle,
            "model_call_performed": True,
            "input_proof_sha256": nh_runner.sha256_text(proof),
            "output_proof_sha256": nh_runner.sha256_text(proof),
            "byte_identical_noop": True,
            "error": f"{type(error).__name__}: {error}",
            "traceback": traceback.format_exc(),
            "completed_at": nh_runner.utc_now(),
        }
    nh_runner.write_text_exact(output_path, output)
    nh_runner.write_json(summary_path, summary)
    return output, summary


def run_nh_stages(
    *,
    runtime: nh_runner.ResilientModelRuntime,
    case: dict[str, Any],
    proof: str,
    cycle: int,
    destination: Path,
    max_tokens: int,
    seed_namespace: str,
    retry_failed: bool,
    status_callback: Any,
) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
    subpass_rows: list[dict[str, Any]] = []
    group_rows: list[dict[str, Any]] = []
    for group_index, group in enumerate(case["groups"], start=1):
        group_dir = destination / (
            f"group_{group_index:02d}_{group['group_id'].replace('.', '_')}"
        )
        if not group["nh_packets"]:
            status_callback(
                "nh_refinement",
                group_index=group_index,
                batch_index=1,
                batch_count=1,
            )
            proof, row = nh_runner.record_no_evidence_group_pass(
                case=case,
                group=group,
                proof=proof,
                cycle=cycle,
                group_index=group_index,
                stage_dir=group_dir,
                max_tokens=max_tokens,
            )
            subpass_rows.append(row)
            group_rows.append(row)
            continue

        group_input_sha256 = nh_runner.sha256_text(proof)
        batch_rows: list[dict[str, Any]] = []
        batches = nh_runner.split_nh_batches(group)
        for batch in batches:
            batch_index = int(batch["batch_index"])
            status_callback(
                "nh_refinement",
                group_index=group_index,
                batch_index=batch_index,
                batch_count=len(batches),
            )
            batch_dir = (
                group_dir
                if len(batches) == 1
                else group_dir
                / "batches"
                / f"batch_{batch_index:02d}_of_{len(batches):02d}"
            )
            proof, row = nh_runner.run_group_stage(
                runtime=runtime,
                case=case,
                group=batch,
                proof=proof,
                cycle=cycle,
                group_index=group_index,
                stage_dir=batch_dir,
                max_tokens=max_tokens,
                seed_namespace=seed_namespace,
                retry_failed=retry_failed,
            )
            batch_rows.append(row)
            subpass_rows.append(row)

        failed_batch_count = sum(
            str(row["outcome"]).startswith("FAILED_CLOSED") for row in batch_rows
        )
        applied_batch_count = sum(row["outcome"] == "APPLIED" for row in batch_rows)
        if applied_batch_count:
            outcome = "APPLIED"
        elif failed_batch_count == len(batch_rows):
            outcome = "FAILED_CLOSED_TO_INPUT_PROOF"
        else:
            outcome = "NO_CHANGE"
        group_row = {
            "schema": "cognitive-well-v0167-parent-group-summary-v1",
            "state": "completed",
            "outcome": outcome,
            "case_key": case["case_key"],
            "cycle": cycle,
            "group_index": group_index,
            "group_id": group["group_id"],
            "nh_packet_count": len(group["nh_packets"]),
            "batch_count": len(batch_rows),
            "batch_packet_counts": [int(row["nh_packet_count"]) for row in batch_rows],
            "model_call_performed": True,
            "model_call_count": len(batch_rows),
            "applied_batch_count": applied_batch_count,
            "failed_closed_batch_count": failed_batch_count,
            "edit_count": sum(int(row["edit_count"]) for row in batch_rows),
            "input_proof_sha256": group_input_sha256,
            "output_proof_sha256": nh_runner.sha256_text(proof),
            "all_unedited_bytes_preserved": all(
                bool(row["all_unedited_bytes_preserved"]) for row in batch_rows
            ),
            "batches": batch_rows,
            "completed_at": nh_runner.utc_now(),
        }
        if len(batches) > 1:
            nh_runner.write_text_exact(group_dir / "proof.md", proof)
            nh_runner.write_json(group_dir / "summary.json", group_row)
        group_rows.append(group_row)
    nh_runner.write_text_exact(destination / "proof.md", proof)
    nh_runner.write_json(
        destination / "summary.json",
        {
            "schema": "cognitive-well-v0167-nh-cycle-summary-v1",
            "state": "completed",
            "case_key": case["case_key"],
            "cycle": cycle,
            "output_proof_sha256": nh_runner.sha256_text(proof),
            "maximum_nh_packets_per_model_call": MAX_NH_PACKETS_PER_CALL,
            "groups": group_rows,
            "subpass_count": len(subpass_rows),
            "model_call_count": sum(
                row.get("model_call_performed", True) is not False
                for row in subpass_rows
            ),
            "applied_subpass_count": sum(
                row["outcome"] == "APPLIED" for row in subpass_rows
            ),
            "failed_closed_subpass_count": sum(
                str(row["outcome"]).startswith("FAILED_CLOSED")
                for row in subpass_rows
            ),
            "all_unedited_bytes_preserved": all(
                bool(row["all_unedited_bytes_preserved"]) for row in subpass_rows
            ),
            "completed_at": nh_runner.utc_now(),
        },
    )
    return proof, subpass_rows, group_rows


def persist_stable_artifact_audit(
    *, audit_path: Path, audit: dict[str, Any]
) -> dict[str, Any]:
    """Keep an equivalent audit byte-stable across process resumes."""
    if audit_path.is_file():
        existing_audit = nh_runner.read_object(audit_path)
        stable_existing = {
            key: value for key, value in existing_audit.items() if key != "completed_at"
        }
        stable_current = {
            key: value for key, value in audit.items() if key != "completed_at"
        }
        if stable_existing == stable_current:
            return existing_audit
    nh_runner.write_json(audit_path, audit)
    return audit


def run_cycle_cleanup(
    *,
    case: dict[str, Any],
    cycle: int,
    cycle_input_proof: str,
    precleanup_proof: str,
    nh_rows: list[dict[str, Any]],
    fusion_row: dict[str, Any],
    destination: Path,
    gemma_endpoint: str,
    qwen_endpoint: str,
    master_seed: int,
    seed_namespace: str,
) -> tuple[str, dict[str, Any], dict[str, Any]]:
    destination.mkdir(parents=True, exist_ok=True)
    proof_path = destination / "pre_cleanup_proof.md"
    audit_path = destination / "artifact_audit.json"
    nh_runner.write_text_exact(proof_path, precleanup_proof)
    audit = nh_runner.deterministic_artifact_audit(
        original_proof=cycle_input_proof,
        refined_proof=precleanup_proof,
        stage_rows=nh_rows,
    )
    audit.update(
        {
            "schema": "cognitive-well-v0167-cycle-artifact-audit-v1",
            "comparison_scope": "cycle_input_to_post_fusion_post_nh_pre_cleanup",
            "cycle": cycle,
            "fusion_stage_outcome": fusion_row["outcome"],
            "fusion_material_supplied_to_cleanup": False,
            "packet_material_supplied_to_cleanup": False,
            "cleanup_input_is_proof_only": True,
        }
    )
    # The audit payload is deterministic except for its informational timestamp.
    # Preserve the exact existing artifact on resume when all substantive fields
    # match, so downstream cache identities do not drift merely because the driver
    # was restarted.
    audit = persist_stable_artifact_audit(audit_path=audit_path, audit=audit)
    cleanup = nh_runner.run_cleanup_gate(
        problem=case["problem"],
        problem_id=case["problem_id"],
        candidate_id=case["candidate_id"],
        cycle=cycle,
        proof_path=proof_path,
        artifact_audit_path=audit_path,
        output_dir=destination / "gate_v0150",
        gemma_endpoint=gemma_endpoint,
        qwen_endpoint=qwen_endpoint,
        master_seed=master_seed,
        seed_namespace=f"{seed_namespace}:{case['case_key']}:cycle-{cycle}:cleanup",
        force=False,
    )
    output_path = Path(str(cleanup["proof_path"])).resolve()
    output = output_path.read_bytes().decode("utf-8")
    file_audit = {
        "schema": "cognitive-well-v0167-cleanup-file-hash-audit-v1",
        "state": "completed",
        "cycle": cycle,
        "cleanup_summary_recorded_text_sha256": cleanup.get("proof_sha256"),
        "cleanup_output_file_sha256": nh_runner.file_sha256(output_path),
        "cleanup_output_decoded_text_sha256": nh_runner.sha256_text(output),
        "cleanup_output_stripped_text_sha256": nh_runner.sha256_text(output.strip()),
        "recorded_hash_matches_stripped_text": cleanup.get("proof_sha256")
        == nh_runner.sha256_text(output.strip()),
        "note": "v0150 records the stripped proof text hash; v0167 also records the exact file hash.",
        "completed_at": nh_runner.utc_now(),
    }
    nh_runner.write_json(destination / "file_hash_audit.json", file_audit)
    return output, cleanup, audit


def run_case(
    *,
    runtime: nh_runner.ResilientModelRuntime,
    case: dict[str, Any],
    output_root: Path,
    fusion_max_tokens: int,
    nh_max_tokens: int,
    gemma_endpoint: str,
    qwen_endpoint: str,
    master_seed: int,
    seed_namespace: str,
    retry_failed: bool,
) -> dict[str, Any]:
    case_dir = output_root / "cases" / case["problem_key"] / case["candidate_id"]
    case_dir.mkdir(parents=True, exist_ok=True)
    subpasses_per_cycle = sum(
        max(1, math.ceil(len(group["nh_packets"]) / MAX_NH_PACKETS_PER_CALL))
        for group in case["groups"]
    )
    model_nh_calls_per_cycle = sum(
        math.ceil(len(group["nh_packets"]) / MAX_NH_PACKETS_PER_CALL)
        for group in case["groups"]
        if group["nh_packets"]
    )
    scheduled_units = TOTAL_CYCLES * (subpasses_per_cycle + 2)
    completed_units = 0

    nh_runner.write_json(
        case_dir / "manifest.json",
        {
            "schema": "cognitive-well-v0167-case-manifest-v1",
            "harness_version": HARNESS_VERSION,
            "created_at": nh_runner.utc_now(),
            "case_key": case["case_key"],
            "problem_path": case["problem_path"],
            "problem_sha256": case["problem_sha256"],
            "original_proof_path": case["proof_path"],
            "original_proof_sha256": case["proof_sha256"],
            "label_result_path": case["label_result_path"],
            "label_result_sha256": case["label_result_sha256"],
            "fusion_packet_prescreen": case.get("fusion_packet_prescreen"),
            "nh_packet_prescreen": case.get("nh_packet_prescreen"),
            "lemma_index_path": case["lemma_index_path"],
            "lemma_index_sha256": case["lemma_index_sha256"],
            "fusion_source": (
                {
                    key: case["fusion"][key]
                    for key in (
                        "raw_path",
                        "raw_sha256",
                        "content_sha256",
                        "source_prompt_path",
                        "source_prompt_sha256",
                    )
                }
                if case["fusion"] is not None
                else None
            ),
            "cycle_count": TOTAL_CYCLES,
            "cycle_schedule": [
                "fusion_guided_full_proof_resolution",
                "nh_groupwise_cumulative_atomic_refinement",
                "deterministically_triggered_deletion_only_cleanup",
            ],
            "cycle_output_feeds_next_cycle": True,
            "group_count": len(case["groups"]),
            "nh_packet_count_per_cycle": sum(
                len(group["nh_packets"]) for group in case["groups"]
            ),
            "maximum_nh_packets_per_model_call": MAX_NH_PACKETS_PER_CALL,
            "nh_group_subpass_count_per_cycle": subpasses_per_cycle,
            "nh_model_call_count_per_cycle": model_nh_calls_per_cycle,
            "fusion_model_call_count_per_cycle": int(case["fusion"] is not None),
            "cleanup_gate_count_per_cycle": 1,
            "scheduled_units": scheduled_units,
        },
    )

    def status(stage: str, **extra: Any) -> None:
        nh_runner.write_json(
            case_dir / "status.json",
            {
                "state": "running",
                "case_key": case["case_key"],
                "stage": stage,
                "completed_units": completed_units,
                "scheduled_units": scheduled_units,
                "updated_at": nh_runner.utc_now(),
                **extra,
            },
        )

    proof = str(case["proof"])
    cycle_rows: list[dict[str, Any]] = []
    all_fusion_rows: list[dict[str, Any]] = []
    all_nh_rows: list[dict[str, Any]] = []
    cleanup_rows: list[dict[str, Any]] = []

    for cycle in range(1, TOTAL_CYCLES + 1):
        cycle_dir = case_dir / f"cycle_{cycle:02d}"
        cycle_dir.mkdir(parents=True, exist_ok=True)
        cycle_input = proof
        cycle_input_sha256 = nh_runner.sha256_text(cycle_input)
        nh_runner.write_text_exact(cycle_dir / "input_proof.md", cycle_input)

        status("fusion_resolution", cycle=cycle)
        proof, fusion_row = run_fusion_stage(
            runtime=runtime,
            case=case,
            proof=proof,
            cycle=cycle,
            stage_dir=cycle_dir / "01_fusion_resolution",
            max_tokens=fusion_max_tokens,
            seed_namespace=seed_namespace,
            retry_failed=retry_failed,
        )
        completed_units += 1
        all_fusion_rows.append(fusion_row)

        nh_subpass_completed = 0

        def nh_status(stage: str, **extra: Any) -> None:
            nonlocal nh_subpass_completed
            status(
                stage,
                cycle=cycle,
                nh_subpasses_completed_in_cycle=nh_subpass_completed,
                nh_subpasses_per_cycle=subpasses_per_cycle,
                **extra,
            )
            nh_subpass_completed += 1

        proof, cycle_nh_rows, group_rows = run_nh_stages(
            runtime=runtime,
            case=case,
            proof=proof,
            cycle=cycle,
            destination=cycle_dir / "02_nh_refinement",
            max_tokens=nh_max_tokens,
            seed_namespace=seed_namespace,
            retry_failed=retry_failed,
            status_callback=nh_status,
        )
        completed_units += len(cycle_nh_rows)
        all_nh_rows.extend(cycle_nh_rows)

        status("deletion_only_cleanup", cycle=cycle)
        precleanup_sha256 = nh_runner.sha256_text(proof)
        proof, cleanup_row, artifact_audit = run_cycle_cleanup(
            case=case,
            cycle=cycle,
            cycle_input_proof=cycle_input,
            precleanup_proof=proof,
            nh_rows=cycle_nh_rows,
            fusion_row=fusion_row,
            destination=cycle_dir / "03_cleanup",
            gemma_endpoint=gemma_endpoint,
            qwen_endpoint=qwen_endpoint,
            master_seed=master_seed,
            seed_namespace=seed_namespace,
        )
        completed_units += 1
        cleanup_rows.append(cleanup_row)
        nh_runner.write_text_exact(cycle_dir / "output_proof.md", proof)
        cycle_row = {
            "schema": "cognitive-well-v0167-full-cycle-summary-v1",
            "state": "completed",
            "case_key": case["case_key"],
            "cycle": cycle,
            "input_proof_sha256": cycle_input_sha256,
            "fusion_outcome": fusion_row["outcome"],
            "post_fusion_proof_sha256": fusion_row["output_proof_sha256"],
            "nh_subpass_count": len(cycle_nh_rows),
            "nh_model_call_count": sum(
                row.get("model_call_performed", True) is not False
                for row in cycle_nh_rows
            ),
            "nh_applied_subpass_count": sum(
                row["outcome"] == "APPLIED" for row in cycle_nh_rows
            ),
            "nh_failed_closed_subpass_count": sum(
                str(row["outcome"]).startswith("FAILED_CLOSED")
                for row in cycle_nh_rows
            ),
            "post_nh_precleanup_proof_sha256": precleanup_sha256,
            "cleanup_outcome": cleanup_row["outcome"],
            "cleanup_model_call_count": int(cleanup_row.get("model_calls", 0)),
            "cleanup_triggered": artifact_audit["cleanup_triggered"],
            "cleanup_trigger_reasons": artifact_audit["cleanup_trigger_reasons"],
            "output_proof_sha256": nh_runner.sha256_text(proof),
            "output_proof_file_sha256": nh_runner.file_sha256(
                cycle_dir / "output_proof.md"
            ),
            "output_feeds_next_cycle": cycle < TOTAL_CYCLES,
            "groups": group_rows,
            "completed_at": nh_runner.utc_now(),
        }
        nh_runner.write_json(cycle_dir / "summary.json", cycle_row)
        cycle_rows.append(cycle_row)

    final_path = case_dir / "final_proof.md"
    nh_runner.write_text_exact(final_path, proof)
    result = {
        "schema": "cognitive-well-v0167-case-result-v1",
        "harness_version": HARNESS_VERSION,
        "state": "completed",
        "case_key": case["case_key"],
        "cycles": TOTAL_CYCLES,
        "cycle_schedule": "FUSION_RESOLUTION_THEN_NH_CUMULATIVE_THEN_CLEANUP",
        "cycle_output_fed_forward": True,
        "fusion_stage_count": len(all_fusion_rows),
        "fusion_model_call_count": sum(
            row.get("model_call_performed", True) is not False
            for row in all_fusion_rows
        ),
        "fusion_synthesized_count": sum(
            row["outcome"] == "SYNTHESIZED" for row in all_fusion_rows
        ),
        "fusion_failed_closed_count": sum(
            str(row["outcome"]).startswith("FAILED_CLOSED")
            for row in all_fusion_rows
        ),
        "nh_group_subpass_count": len(all_nh_rows),
        "nh_model_call_count": sum(
            row.get("model_call_performed", True) is not False for row in all_nh_rows
        ),
        "nh_applied_subpass_count": sum(
            row["outcome"] == "APPLIED" for row in all_nh_rows
        ),
        "nh_failed_closed_subpass_count": sum(
            str(row["outcome"]).startswith("FAILED_CLOSED") for row in all_nh_rows
        ),
        "all_nh_passes_preserved_unedited_bytes": all(
            bool(row["all_unedited_bytes_preserved"]) for row in all_nh_rows
        ),
        "cleanup_gate_count": len(cleanup_rows),
        "cleanup_model_call_count": sum(
            int(row.get("model_calls", 0)) for row in cleanup_rows
        ),
        "cleanup_accepted_count": sum(
            bool(row.get("cleanup_accepted")) for row in cleanup_rows
        ),
        "total_model_call_count": (
            sum(
                row.get("model_call_performed", True) is not False
                for row in all_fusion_rows
            )
            + sum(
                row.get("model_call_performed", True) is not False
                for row in all_nh_rows
            )
            + sum(int(row.get("model_calls", 0)) for row in cleanup_rows)
        ),
        "original_proof_path": case["proof_path"],
        "original_proof_sha256": case["proof_sha256"],
        "final_proof_path": str(final_path.resolve()),
        "final_proof_sha256": nh_runner.file_sha256(final_path),
        "final_proof_decoded_text_sha256": nh_runner.sha256_text(proof),
        "cycle_summaries": cycle_rows,
        "completed_at": nh_runner.utc_now(),
    }
    nh_runner.write_json(case_dir / "result.json", result)
    nh_runner.write_json(
        case_dir / "status.json",
        {
            "state": "completed",
            "stage": "done",
            "case_key": case["case_key"],
            "completed_units": completed_units,
            "scheduled_units": scheduled_units,
            "final_proof_sha256": result["final_proof_sha256"],
            "updated_at": nh_runner.utc_now(),
        },
    )
    return result


def dry_run(cases: list[dict[str, Any]]) -> dict[str, Any]:
    # Preserve the inherited atomic multi-range patch contract.
    synthetic = "alpha\nbeta\ngamma\ndelta\n"
    edits = nh_runner.normalize_and_validate_edits(
        proof=synthetic,
        record={
            "action": "REPLACE",
            "edits": [
                {"start_line": 2, "end_line": 2, "replacement": "BETA"},
                {"start_line": 4, "end_line": 4, "replacement": "DELTA"},
            ],
            "verification_summary": "contract test",
        },
    )
    patched, atomic_audit = nh_runner.apply_atomic_edits(
        proof=synthetic, edits=edits
    )
    if patched != "alpha\nBETA\ngamma\nDELTA\n":
        raise ValueError("atomic multi-span contract test failed")

    case_rows = []
    for case in cases:
        fusion = case["fusion"]
        if fusion is not None:
            prompt = fusion_resolution_prompt(
                problem=case["problem"],
                current_proof=case["proof"],
                fusion=fusion,
                cycle=1,
            )
            audit = fusion_prompt_audit(
                prompt=prompt,
                case=case,
                proof=case["proof"],
                fusion=fusion,
            )
            if not audit["current_proof_supplied_exactly_once"]:
                raise ValueError(f"Fusion current-proof audit failed: {case['case_key']}")
            if not audit["fusion_supplied_exactly_once"]:
                raise ValueError(f"Fusion content audit failed: {case['case_key']}")
        for group in case["groups"]:
            packets_seen: list[str] = []
            for batch in nh_runner.split_nh_batches(group):
                if len(batch["nh_packets"]) > MAX_NH_PACKETS_PER_CALL:
                    raise ValueError("NH packet cap contract failed")
                prompt_group = {**batch, "_proof_for_audit": case["proof"]}
                prompt = nh_runner.group_patch_prompt(
                    problem=case["problem"],
                    proof=case["proof"],
                    group=prompt_group,
                    cycle=1,
                )
                prompt_check = nh_runner.prompt_audit(prompt, prompt_group)
                if not prompt_check["all_nh_exact_texts_supplied_once"]:
                    raise ValueError(
                        f"NH prompt inclusion failed: {case['case_key']}:"
                        f"{group['group_id']}:{batch['batch_index']}"
                    )
                packets_seen.extend(
                    str(packet["trace_id"]) for packet in batch["nh_packets"]
                )
            expected = [str(packet["trace_id"]) for packet in group["nh_packets"]]
            if packets_seen != expected:
                raise ValueError("NH batching changed packet order or coverage")

        nh_subpasses = sum(
            max(1, math.ceil(len(group["nh_packets"]) / MAX_NH_PACKETS_PER_CALL))
            for group in case["groups"]
        )
        nh_model_calls = sum(
            math.ceil(len(group["nh_packets"]) / MAX_NH_PACKETS_PER_CALL)
            for group in case["groups"]
            if group["nh_packets"]
        )
        case_rows.append(
            {
                "case_key": case["case_key"],
                "fusion_repair_packet_present": fusion is not None,
                "fusion_model_calls_per_cycle": int(fusion is not None),
                "group_count": len(case["groups"]),
                "zero_nh_group_count": sum(
                    not group["nh_packets"] for group in case["groups"]
                ),
                "nh_packet_presentations_per_cycle": sum(
                    len(group["nh_packets"]) for group in case["groups"]
                ),
                "nh_group_subpasses_per_cycle": nh_subpasses,
                "nh_model_calls_per_cycle": nh_model_calls,
                "cleanup_gates_per_cycle": 1,
                "scheduled_units_per_cycle": nh_subpasses + 2,
            }
        )

    return {
        "state": "validated",
        "harness_version": HARNESS_VERSION,
        "cycle_count": TOTAL_CYCLES,
        "cycle_schedule": [
            "fusion_guided_full_proof_resolution",
            "nh_groupwise_cumulative_atomic_refinement",
            "deterministically_triggered_deletion_only_cleanup",
        ],
        "cycle_output_feeds_next_cycle": True,
        "case_count": len(cases),
        "group_count_per_cycle": sum(row["group_count"] for row in case_rows),
        "fusion_stage_count": TOTAL_CYCLES * len(cases),
        "planned_fusion_model_calls": TOTAL_CYCLES
        * sum(row["fusion_model_calls_per_cycle"] for row in case_rows),
        "nh_packet_presentations_per_cycle": sum(
            row["nh_packet_presentations_per_cycle"] for row in case_rows
        ),
        "total_nh_packet_presentations": TOTAL_CYCLES
        * sum(row["nh_packet_presentations_per_cycle"] for row in case_rows),
        "nh_group_subpasses_per_cycle": sum(
            row["nh_group_subpasses_per_cycle"] for row in case_rows
        ),
        "total_nh_group_subpasses": TOTAL_CYCLES
        * sum(row["nh_group_subpasses_per_cycle"] for row in case_rows),
        "planned_nh_model_calls": TOTAL_CYCLES
        * sum(row["nh_model_calls_per_cycle"] for row in case_rows),
        "cleanup_gate_count": TOTAL_CYCLES * len(cases),
        "cleanup_model_calls": "trigger-dependent: 0 to 2 per gate",
        "known_model_calls_excluding_cleanup": TOTAL_CYCLES
        * sum(
            row["fusion_model_calls_per_cycle"] + row["nh_model_calls_per_cycle"]
            for row in case_rows
        ),
        "scheduled_units": TOTAL_CYCLES
        * sum(row["scheduled_units_per_cycle"] for row in case_rows),
        "maximum_nh_packets_per_model_call": MAX_NH_PACKETS_PER_CALL,
        "every_nh_packet_consumed_exactly_once_per_cycle": True,
        "atomic_multi_span_contract": atomic_audit,
        "cases": case_rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run three full cycles of Fusion resolution, capped-6 cumulative NH "
            "refinement, and deletion-only cleanup"
        )
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--gemma-endpoint", default="http://127.0.0.1:8030/v1")
    parser.add_argument("--qwen-endpoint", default="http://127.0.0.1:8027/v1")
    parser.add_argument("--fusion-max-tokens", type=int, default=32_000)
    parser.add_argument("--nh-max-tokens", type=int, default=24_000)
    parser.add_argument("--thinking-token-budget", type=int, default=16_384)
    parser.add_argument("--max-concurrency", type=int, default=4)
    parser.add_argument("--master-seed", type=int, default=20260902)
    parser.add_argument(
        "--seed-namespace", default="v0167:fusion-nh-cap6-three-full-cycles"
    )
    parser.add_argument("--case", action="append", dest="case_keys")
    parser.add_argument("--retry-failed", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.max_concurrency < 1:
        raise ValueError("max concurrency must be positive")
    if args.fusion_max_tokens < 1 or args.nh_max_tokens < 1:
        raise ValueError("token budgets must be positive")
    selected_keys = args.case_keys or list(DEFAULT_SELECTED_CASE_KEYS)
    unknown = sorted(set(selected_keys).difference(DEFAULT_CASES))
    if unknown:
        raise ValueError(f"unknown case keys: {unknown}")
    cases = [load_case(key) for key in selected_keys]
    validation = dry_run(cases)
    if args.dry_run:
        print(json.dumps(validation, ensure_ascii=False, indent=2))
        return

    output_root = args.output_dir.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    nh_runner.write_json(output_root / "preflight.json", validation)
    nh_runner.write_json(
        output_root / "manifest.json",
        {
            "schema": "cognitive-well-v0167-portfolio-manifest-v1",
            "harness_version": HARNESS_VERSION,
            "created_at": nh_runner.utc_now(),
            "implementation_path": str(Path(__file__).resolve()),
            "implementation_sha256": nh_runner.file_sha256(Path(__file__).resolve()),
            "case_keys": selected_keys,
            "cycle_count": TOTAL_CYCLES,
            "cycle_schedule": validation["cycle_schedule"],
            "cycle_output_feeds_next_cycle": True,
            "fusion_stage_count": validation["fusion_stage_count"],
            "planned_fusion_model_calls": validation["planned_fusion_model_calls"],
            "nh_group_subpasses_per_cycle": validation[
                "nh_group_subpasses_per_cycle"
            ],
            "total_nh_group_subpasses": validation["total_nh_group_subpasses"],
            "planned_nh_model_calls": validation["planned_nh_model_calls"],
            "cleanup_gate_count": validation["cleanup_gate_count"],
            "known_model_calls_excluding_cleanup": validation[
                "known_model_calls_excluding_cleanup"
            ],
            "scheduled_units": validation["scheduled_units"],
            "nh_packet_presentations_per_cycle": validation[
                "nh_packet_presentations_per_cycle"
            ],
            "maximum_nh_packets_per_model_call": MAX_NH_PACKETS_PER_CALL,
            "gemma_endpoint": args.gemma_endpoint,
            "qwen_endpoint": args.qwen_endpoint,
            "gemma_model": nh_runner.GEMMA_MODEL,
            "qwen_model": nh_runner.QWEN_MODEL,
            "fusion_max_tokens": args.fusion_max_tokens,
            "nh_max_tokens": args.nh_max_tokens,
            "thinking_token_budget": args.thinking_token_budget,
            "max_concurrency": args.max_concurrency,
            "master_seed": args.master_seed,
            "policy": {
                "fusion_diagnostic_is_unverified": True,
                "fusion_resolution_is_full_proof_synthesis": True,
                "p1_without_repair_fusion_is_deterministic_passthrough": True,
                "packet_selection": "NH_ONLY",
                "all_packet_claims_unverified": True,
                "purpose_only_refinement": False,
                "zero_nh_group": "deterministic_passthrough_without_model_call",
                "large_nh_group_batching": "stable_existing_order_contiguous_chunks",
                "maximum_nh_packets_per_model_call": MAX_NH_PACKETS_PER_CALL,
                "every_nh_packet_consumed_exactly_once_per_cycle": True,
                "nh_edits_are_cumulative": True,
                "nh_sub_batch_edit_set_is_atomic": True,
                "nh_unedited_bytes_are_mechanically_preserved": True,
                "stage_failure_fails_closed_to_input_proof": True,
                "cleanup": "deterministically_triggered_deletion_only_with_independent_preservation_audit",
                "fusion_and_packet_material_supplied_to_cleanup": False,
            },
        },
    )

    runtime = nh_runner.ResilientModelRuntime(
        nh_runner.RuntimeConfig(
            gemma_endpoint=args.gemma_endpoint.rstrip("/"),
            qwen_endpoint=args.qwen_endpoint.rstrip("/"),
            gemma_model=nh_runner.GEMMA_MODEL,
            qwen_model=nh_runner.QWEN_MODEL,
            master_seed=args.master_seed,
            thinking_token_budget=args.thinking_token_budget,
            reasoning_effort="max",
        )
    )
    status_lock = threading.Lock()
    completed_keys: list[str] = []
    failures: list[dict[str, str]] = []

    def root_status(stage: str) -> None:
        with status_lock:
            live_cases = []
            for case in cases:
                path = (
                    output_root
                    / "cases"
                    / case["problem_key"]
                    / case["candidate_id"]
                    / "status.json"
                )
                if path.is_file():
                    try:
                        live_cases.append(nh_runner.read_object(path))
                    except Exception:
                        pass
            nh_runner.write_json(
                output_root / "status.json",
                {
                    "state": "running",
                    "stage": stage,
                    "completed_case_keys": sorted(completed_keys),
                    "completed_case_count": len(completed_keys),
                    "failed_cases": list(failures),
                    "case_count": len(cases),
                    "cycle_count": TOTAL_CYCLES,
                    "scheduled_units": validation["scheduled_units"],
                    "live_cases": live_cases,
                    "updated_at": nh_runner.utc_now(),
                },
            )

    root_status("three_full_cycles")
    results_by_key: dict[str, dict[str, Any]] = {}
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=min(args.max_concurrency, len(cases))
    ) as executor:
        futures = {
            executor.submit(
                run_case,
                runtime=runtime,
                case=case,
                output_root=output_root,
                fusion_max_tokens=args.fusion_max_tokens,
                nh_max_tokens=args.nh_max_tokens,
                gemma_endpoint=args.gemma_endpoint,
                qwen_endpoint=args.qwen_endpoint,
                master_seed=args.master_seed,
                seed_namespace=args.seed_namespace,
                retry_failed=args.retry_failed,
            ): case["case_key"]
            for case in cases
        }
        for future in concurrent.futures.as_completed(futures):
            case_key = futures[future]
            try:
                results_by_key[case_key] = future.result()
                completed_keys.append(case_key)
            except Exception as error:
                failures.append(
                    {
                        "case_key": case_key,
                        "error": f"{type(error).__name__}: {error}",
                        "traceback": traceback.format_exc(),
                    }
                )
            root_status("three_full_cycles")

    ordered_results = [
        results_by_key[key] for key in selected_keys if key in results_by_key
    ]
    result = {
        "schema": "cognitive-well-v0167-portfolio-result-v1",
        "harness_version": HARNESS_VERSION,
        "state": "completed" if not failures else "completed_with_failures",
        "case_count": len(cases),
        "completed_case_count": len(ordered_results),
        "failed_cases": failures,
        "results": ordered_results,
        "fusion_stage_count": sum(
            row["fusion_stage_count"] for row in ordered_results
        ),
        "fusion_model_call_count": sum(
            row["fusion_model_call_count"] for row in ordered_results
        ),
        "nh_group_subpass_count": sum(
            row["nh_group_subpass_count"] for row in ordered_results
        ),
        "nh_model_call_count": sum(
            row["nh_model_call_count"] for row in ordered_results
        ),
        "cleanup_gate_count": sum(row["cleanup_gate_count"] for row in ordered_results),
        "cleanup_model_call_count": sum(
            row["cleanup_model_call_count"] for row in ordered_results
        ),
        "total_model_call_count": sum(
            row["total_model_call_count"] for row in ordered_results
        ),
        "total_fusion_failed_closed": sum(
            row["fusion_failed_closed_count"] for row in ordered_results
        ),
        "total_nh_failed_closed": sum(
            row["nh_failed_closed_subpass_count"] for row in ordered_results
        ),
        "all_nh_passes_preserved_unedited_bytes": all(
            row["all_nh_passes_preserved_unedited_bytes"] for row in ordered_results
        ),
        "completed_at": nh_runner.utc_now(),
    }
    nh_runner.write_json(output_root / "result.json", result)
    nh_runner.write_json(
        output_root / "status.json",
        {
            "state": result["state"],
            "stage": "done",
            "completed_case_keys": [row["case_key"] for row in ordered_results],
            "completed_case_count": len(ordered_results),
            "failed_cases": failures,
            "case_count": len(cases),
            "total_model_call_count": result["total_model_call_count"],
            "updated_at": nh_runner.utc_now(),
        },
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
