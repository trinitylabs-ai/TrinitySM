from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Any

from . import HARNESS_VERSION, PARENT_HARNESS_VERSION

# Importing v0263 installs the v0260 32k-floor mandatory budget-forcing
# transport and the guarded Resolver parser compatibility.
from cognitive_well_harness_v0_3_263_v260_unified_recovery_20260905 import (  # noqa: E402
    pipeline as v263,
)
from experiments.local_math_verifier import runtime as transport  # noqa: E402


resolver = v263.resolver
REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE_RUN = (
    REPO_ROOT / "runs/v0264_p5_resolver1_v263_recycle_bf32_48_64_20260905"
)
DEFAULT_OUTPUT_DIR = (
    REPO_ROOT / "runs/v0266_p5_t10_r01_repair_brief_certified_bf32_20260905"
)
DEFAULT_QWEN_ENDPOINT = "http://127.0.0.1:8027/v1"
DEFAULT_GEMMA_ENDPOINT = "http://127.0.0.1:8030/v1"
QWEN_MODEL = "Qwen/Qwen3.6-27B"
GEMMA_MODEL = "google/gemma-4-31B-it"
PROBLEM_ID = "imo2026_p5"
CANDIDATE_ID = "t10_r01"
CASE_ID = f"{PROBLEM_ID}.{CANDIDATE_ID}"
SOURCE_STAGE = Path("01_v263_review_fusion_resolver")
MAX_OUTPUT_TOKENS = 32_768
TOP_P = 1.0
TOP_K = -1
REASONING_EFFORT = "max"
SEED_NAMESPACE = "v0266:p5:t10_r01:repair_brief_certification"

EXPECTED_PROBLEM_SHA256 = (
    "f298ac63a0c7bbca176888c0ed48a1da2fedb09f7609c042dfbb9540bde8231e"
)
EXPECTED_PROOF_SHA256 = (
    "99f6145c16b387196178029323489f257854c98c14ec099d68fa8bfbc8105bb1"
)


CERTIFIER_SYSTEM_PROMPT = r"""You are an independent adversarial certifier of a proposed repair brief for an Olympiad proof. The brief is untrusted even when it was produced by another reviewer or Fusion model.

Do not write a replacement proof and do not defer to labels such as "minimum_required_lemma". Decompose the brief into atomic mathematical implications. For every implication, identify the exact premises available in the submitted proof or problem, audit quantifier scope and variable binding, check inequality direction, distinguish local from global conclusions, and actively try to falsify it. A proposed lemma phrased as an instruction to "show" or "prove" must itself be mathematically viable.

Return CERTIFIED only when every asserted step is supported and completing the brief would close the stated failed obligation. Otherwise return REJECTED and identify the earliest decisive defect. Be skeptical and concise.

Return exactly one concise Markdown document with this structure:

# Repair Brief Certification
verdict: CERTIFIED or REJECTED

## Atomic Checks
For each atomic claim, give its claim, exact premises, status (SUPPORTED, UNSUPPORTED, or FALSE), and a concise audit.

## First Invalid Step
State the first invalid step, or NONE if certified.

## Missing Obligation
State the missing obligation, or NONE if certified.

## Counterexample or Failure Witness
Give a witness, or NONE if certified.

## Certification Summary
Give the decisive conclusion.

# End Repair Brief Certification

Do not emit JSON. Do not repeat premises or sections."""


REWRITER_SYSTEM_PROMPT = r"""You synthesize a mathematically sound repair brief for an Olympiad proof after an adversarial certifier rejected the previous brief. Produce a repair plan, not a full replacement proof.

Work only from the problem, submitted proof, Fusion defect certificate, and independent rejection supplied by the user. Do not use or assume a reference solution. Recheck any premise taken from the submitted proof. The new brief must close the failed obligation, preserve correct material when useful, explicitly bridge local-to-global steps, and avoid the rejected shortcut. Do not merely restate the failed obligation. Every proposed lemma must be true and sufficiently precise for a Resolver to prove it.

Return exactly one concise Markdown document with this structure:

# Repair Brief Candidate

## Target Obligation
State it once.

## Verified Premises
List only premises you rechecked.

## Repair Brief
Give one self-contained repair plan. This section is the exact text sent onward if certified.

## Derivation Checklist
List the indispensable logical bridges.

## Forbidden Shortcuts
List invalid shortcuts the Resolver must avoid.

## Completion Criterion
State what must be established for the repair to close the gap.

# End Repair Brief Candidate

Do not emit JSON. Do not repeat sections."""


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _single(paths: list[Path], label: str) -> Path:
    if len(paths) != 1:
        raise ValueError(f"expected one {label}, found {len(paths)}")
    return paths[0].resolve()


def _seed(stage: str) -> int:
    digest = hashlib.sha256(f"{SEED_NAMESPACE}:{stage}".encode()).digest()
    return int.from_bytes(digest[:4], "big")


def extract_resolver_brief(fusion_record: str) -> str:
    matches = [
        line[len("resolver_brief:") :].strip()
        for line in fusion_record.strip().splitlines()
        if line.startswith("resolver_brief:")
    ]
    if len(matches) != 1 or not matches[0]:
        raise ValueError("expected exactly one nonempty resolver_brief")
    return matches[0]


def replace_resolver_brief(fusion_record: str, new_brief: str) -> str:
    one_line = " ".join(new_brief.split())
    if not one_line:
        raise ValueError("replacement resolver_brief is empty")
    old = "resolver_brief: " + extract_resolver_brief(fusion_record)
    lines = fusion_record.strip().splitlines()
    changed = [
        f"resolver_brief: {one_line}" if line == old else line for line in lines
    ]
    if changed == lines or sum(line.startswith("resolver_brief:") for line in changed) != 1:
        raise RuntimeError("failed to replace exactly one resolver_brief line")
    return "\n".join(changed)


def canonical_defect_packet(parsed_fusion: dict[str, Any]) -> str:
    fields = parsed_fusion.get("fields")
    if not isinstance(fields, dict):
        raise ValueError("parsed Fusion fields are missing")
    names = (
        "decisive_location",
        "failed_obligation",
        "independent_validation",
        "impact_on_proof",
        "repair_scope",
    )
    values = []
    for name in names:
        value = str(fields.get(name) or "").strip()
        if not value:
            raise ValueError(f"Fusion field is empty: {name}")
        values.append(f"{name}: {value}")
    packet = "\n".join(values)
    if "resolver_brief:" in packet or "reviewer_" in packet:
        raise RuntimeError("canonical defect packet contains excluded Fusion material")
    return packet


def _load_inputs(source_run: Path, output_dir: Path) -> dict[str, Any]:
    source_run = source_run.resolve()
    lane = source_run / SOURCE_STAGE / "cases" / CASE_ID
    fusion_result_path = _single(
        list((lane / "fusion").rglob("result.json")), "Fusion result"
    )
    source_resolver_result_path = _single(
        list((lane / "resolver").rglob("result.json")), "Resolver result"
    )
    problem_path = (source_run / "input/problem.json").resolve()
    proof_path = (
        source_run / "input/resolver1_proofs" / f"{CANDIDATE_ID}.md"
    ).resolve()
    problem = str(_read_json(problem_path).get("claim") or "").strip()
    proof = proof_path.read_text(encoding="utf-8").strip()
    fusion_result = _read_json(fusion_result_path)
    fusion_record = str(fusion_result.get("final") or "").strip()
    parsed_fusion = resolver.parse_fusion(fusion_record)
    if not parsed_fusion.get("valid") or parsed_fusion.get("outcome") != "REPAIR_NEEDED":
        raise ValueError("source Fusion is not one valid REPAIR_NEEDED record")
    defect_packet = canonical_defect_packet(parsed_fusion)
    if _sha256_text(problem) != EXPECTED_PROBLEM_SHA256:
        raise ValueError("problem hash drift")
    if _sha256_text(proof) != EXPECTED_PROOF_SHA256:
        raise ValueError("proof hash drift")
    source_resolver = _read_json(source_resolver_result_path)
    source_task = source_resolver.get("task")
    if not isinstance(source_task, dict):
        raise ValueError("source Resolver task is missing")

    input_dir = output_dir / "input"
    input_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(problem_path, input_dir / "problem.json")
    (input_dir / "resolver1_proof.md").write_text(proof + "\n", encoding="utf-8")
    (input_dir / "fusion.original.txt").write_text(
        fusion_record + "\n", encoding="utf-8"
    )
    (input_dir / "defect_packet.canonical.txt").write_text(
        defect_packet + "\n", encoding="utf-8"
    )
    return {
        "problem": problem,
        "proof": proof,
        "fusion_record": fusion_record,
        "defect_packet": defect_packet,
        "original_brief": extract_resolver_brief(fusion_record),
        "source_resolver_seed": int(source_task["seed"]),
        "problem_path": str(problem_path),
        "proof_path": str(proof_path),
        "fusion_result_path": str(fusion_result_path),
        "source_resolver_result_path": str(source_resolver_result_path),
    }


def _certifier_user_prompt(
    *, problem: str, proof: str, defect_packet: str, repair_brief: str, pass_name: str
) -> str:
    return f"""Certification pass: {pass_name}

## Problem
{problem}

## Submitted proof
{proof}

## Canonical Fusion defect certificate
{defect_packet}

## Untrusted repair brief to certify
{repair_brief}

Audit the untrusted brief independently. The original proof and Fusion record may themselves contain errors; only use premises you explicitly revalidate. Do not use a reference solution or generate a replacement proof."""


def _rewriter_user_prompt(
    *, problem: str, proof: str, defect_packet: str, rejected_brief: str,
    rejection: str
) -> str:
    return f"""## Problem
{problem}

## Submitted proof
{proof}

## Canonical Fusion defect certificate
{defect_packet}

## Rejected repair brief
{rejected_brief}

## Independent adversarial rejection
{rejection}

Synthesize one corrected, self-contained repair brief. It must give the Resolver a viable derivation route rather than repeat the obligation, and it must not rely on the rejected inference."""


def parse_certification_markdown(value: str) -> dict[str, Any]:
    text = value.strip()
    errors: list[str] = []
    if not text.startswith("# Repair Brief Certification"):
        errors.append("missing certification header")
    if not text.endswith("# End Repair Brief Certification"):
        errors.append("missing certification footer")
    matches = re.findall(
        r"(?im)^\s*verdict:\s*(CERTIFIED|REJECTED)\s*$", text
    )
    if len(matches) != 1:
        errors.append(f"expected one verdict line, found {len(matches)}")
    required = (
        "## Atomic Checks",
        "## First Invalid Step",
        "## Missing Obligation",
        "## Counterexample or Failure Witness",
        "## Certification Summary",
    )
    for heading in required:
        if text.count(heading) != 1:
            errors.append(f"expected one {heading}")
    return {
        "valid": not errors,
        "errors": errors,
        "verdict": matches[0] if len(matches) == 1 else None,
        "markdown": text,
        "sha256": _sha256_text(text),
    }


def _markdown_section(value: str, heading: str, next_heading: str) -> str:
    pattern = re.compile(
        rf"(?ms)^{re.escape(heading)}\s*\n(.*?)\n^{re.escape(next_heading)}\s*$"
    )
    match = pattern.search(value.strip())
    return match.group(1).strip() if match else ""


def parse_rewriter_markdown(value: str) -> dict[str, Any]:
    text = value.strip()
    errors: list[str] = []
    if not text.startswith("# Repair Brief Candidate"):
        errors.append("missing rewrite header")
    if not text.endswith("# End Repair Brief Candidate"):
        errors.append("missing rewrite footer")
    headings = (
        "## Target Obligation",
        "## Verified Premises",
        "## Repair Brief",
        "## Derivation Checklist",
        "## Forbidden Shortcuts",
        "## Completion Criterion",
        "# End Repair Brief Candidate",
    )
    for heading in headings:
        if text.count(heading) != 1:
            errors.append(f"expected one {heading}")
    repair_brief = _markdown_section(
        text, "## Repair Brief", "## Derivation Checklist"
    )
    if not repair_brief:
        errors.append("empty Repair Brief section")
    return {
        "valid": not errors,
        "errors": errors,
        "repair_brief": " ".join(repair_brief.split()),
        "markdown": text,
        "sha256": _sha256_text(text),
    }


def _run_markdown_call(
    *, endpoint: str, model: str, system_prompt: str, user_prompt: str,
    output_dir: Path, stage: str, temperature: float, seed: int,
    reasoning_effort: str | None
) -> tuple[str, dict[str, Any]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    generated = transport.run_openai_chat_generation(
        endpoint=endpoint.rstrip("/"),
        model=model,
        prompt=system_prompt,
        user_prompt=user_prompt,
        output_dir=output_dir,
        stage=stage,
        config=transport.HTTPGenerationConfig(
            max_tokens=MAX_OUTPUT_TOKENS,
            temperature=temperature,
            top_p=TOP_P,
            top_k=TOP_K,
            seed=seed,
            thinking_token_budget=None,
            reasoning_effort=reasoning_effort,
            timeout_seconds=14_400,
        ),
    )
    metadata = dict(generated.get("metadata") or {})
    if str(metadata.get("finish_reason") or "") == "length":
        raise RuntimeError(f"{stage} exhausted the hard 32k cap")
    text = str(generated.get("text") or "").strip()
    if not text:
        raise ValueError(f"{stage} returned empty Markdown")
    budget_path = output_dir / f"{stage}.budget_forcing.json"
    budget = _read_json(budget_path)
    for key in ("original_config", "forced_config"):
        config = budget.get(key)
        if isinstance(config, dict) and int(config.get("max_tokens") or 0) != MAX_OUTPUT_TOKENS:
            raise RuntimeError(f"{stage} {key} escaped the 32k cap")
    if budget.get("structured") is not False:
        raise RuntimeError(f"{stage} unexpectedly used structured decoding")
    (output_dir / f"{stage}.final.md").write_text(text + "\n", encoding="utf-8")
    return text, metadata


def _run_resolver(
    *, inputs: dict[str, Any], fusion_record: str, endpoint: str,
    output_dir: Path
) -> dict[str, Any]:
    stage = "resolver_certified_brief"
    destination = output_dir / "04_resolver"
    destination.mkdir(parents=True, exist_ok=True)
    user_prompt = resolver.resolver_user_prompt(
        problem=inputs["problem"],
        proof=inputs["proof"],
        fusion_record=fusion_record,
    )
    generated = transport.run_openai_chat_generation(
        endpoint=endpoint.rstrip("/"),
        model=GEMMA_MODEL,
        prompt=resolver.SYSTEM_PROMPT,
        user_prompt=user_prompt,
        output_dir=destination,
        stage=stage,
        config=transport.HTTPGenerationConfig(
            max_tokens=MAX_OUTPUT_TOKENS,
            temperature=0.4,
            top_p=TOP_P,
            top_k=TOP_K,
            seed=int(inputs["source_resolver_seed"]),
            thinking_token_budget=None,
            reasoning_effort=REASONING_EFFORT,
            timeout_seconds=14_400,
        ),
    )
    metadata = dict(generated.get("metadata") or {})
    if str(metadata.get("finish_reason") or "") == "length":
        raise RuntimeError("Resolver exhausted the hard 32k cap")
    final = str(generated.get("text") or "").strip()
    with v263.resolver_fusion_context("REPAIR_NEEDED"):
        parsed = resolver.parse_resolution(final)
    if not parsed.get("valid"):
        raise ValueError(f"invalid Resolver protocol: {parsed.get('errors')}")
    (destination / "final.txt").write_text(final + "\n", encoding="utf-8")
    proof_path: str | None = None
    if parsed.get("outcome") == "RESOLVED_PROOF":
        resolved = str(parsed.get("proof") or "").strip()
        path = destination / "resolved_proof.md"
        path.write_text(resolved + "\n", encoding="utf-8")
        proof_path = str(path.resolve())
    budget = _read_json(destination / f"{stage}.budget_forcing.json")
    for key in ("original_config", "forced_config"):
        config = budget.get(key)
        if isinstance(config, dict) and int(config.get("max_tokens") or 0) != MAX_OUTPUT_TOKENS:
            raise RuntimeError(f"Resolver {key} escaped the 32k cap")
    return {
        "outcome": parsed.get("outcome"),
        "parsed": parsed,
        "final": final,
        "resolved_proof_path": proof_path,
        "resolved_proof_sha256": (
            _sha256_text(str(parsed.get("proof") or "").strip())
            if parsed.get("outcome") == "RESOLVED_PROOF"
            else None
        ),
        "metadata": metadata,
    }


def run_pipeline(
    *, source_run: Path, output_dir: Path, qwen_endpoint: str,
    gemma_endpoint: str, dry_run: bool
) -> dict[str, Any]:
    source_run = source_run.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    inputs = _load_inputs(source_run, output_dir)
    manifest = {
        "schema": "cognitive-well-v0266-p5-repair-brief-certification-manifest-v1",
        "harness_version": HARNESS_VERSION,
        "parent_harness_version": PARENT_HARNESS_VERSION,
        "case_id": CASE_ID,
        "source_run": str(source_run),
        "source_artifacts": {
            key: inputs[key]
            for key in (
                "problem_path", "proof_path", "fusion_result_path",
                "source_resolver_result_path"
            )
        },
        "source_hashes": {
            "problem": _sha256_text(inputs["problem"]),
            "proof": _sha256_text(inputs["proof"]),
            "fusion_record": _sha256_text(inputs["fusion_record"]),
            "canonical_defect_packet": _sha256_text(inputs["defect_packet"]),
            "original_brief": _sha256_text(inputs["original_brief"]),
        },
        "call_sequence": [
            "qwen_original_brief_certification",
            "gemma_conditional_brief_rewrite",
            "qwen_fresh_recertification",
            "gemma_v263_resolver_if_certified",
        ],
        "hard_cap_per_physical_call": MAX_OUTPUT_TOKENS,
        "model_output_format": "plain_markdown",
        "json_schema_or_structured_decoding": False,
        "budget_forcing": {
            "mandatory_same_trace_continuation_replacement": True,
            "primary_cap": MAX_OUTPUT_TOKENS,
            "replacement_cap": MAX_OUTPUT_TOKENS,
            "higher_cap_recovery": False,
        },
        "models": {"certifier": QWEN_MODEL, "rewriter_resolver": GEMMA_MODEL},
        "sampling_contract": {
            "qwen_certifier": {
                "temperature": 0.2,
                "reasoning_effort": None,
                "source": "v0264 adversarial Reviewer 2",
            },
            "gemma_rewriter": {"temperature": 0.4, "reasoning_effort": "max"},
            "gemma_resolver": {"temperature": 0.4, "reasoning_effort": "max"},
        },
        "endpoints": {
            "qwen": qwen_endpoint.rstrip("/"),
            "gemma": gemma_endpoint.rstrip("/"),
        },
        "generation_inputs_exclude": [
            "reference_solution", "gold_score", "Codex_feedback",
            "v0139_proof", "v0264_resolved_proof", "v0265_resolved_proof"
        ],
    }
    _write_json(output_dir / "manifest.json", manifest)
    if dry_run:
        summary = {
            "schema": "cognitive-well-v0266-p5-repair-brief-certification-summary-v1",
            "state": "dry_run_completed",
            "case_id": CASE_ID,
            "model_calls_performed": 0,
        }
        _write_json(output_dir / "summary.json", summary)
        return summary

    _write_json(output_dir / "status.json", {"state": "running", "stage": "certify_original"})
    first_prompt = _certifier_user_prompt(
        problem=inputs["problem"], proof=inputs["proof"],
        defect_packet=inputs["defect_packet"], repair_brief=inputs["original_brief"],
        pass_name="original_fusion_brief"
    )
    first_text, first_meta = _run_markdown_call(
        endpoint=qwen_endpoint, model=QWEN_MODEL,
        system_prompt=CERTIFIER_SYSTEM_PROMPT, user_prompt=first_prompt,
        output_dir=output_dir / "01_certify_original", stage="certify_original_brief",
        temperature=0.2, seed=_seed("certify_original"), reasoning_effort=None
    )
    first = parse_certification_markdown(first_text)
    _write_json(output_dir / "01_certify_original/certify_original_brief.parsed.json", first)
    if not first["valid"]:
        raise ValueError(f"invalid certification Markdown: {first['errors']}")

    selected_brief = inputs["original_brief"]
    rewrite: dict[str, Any] | None = None
    rewrite_meta: dict[str, Any] | None = None
    second: dict[str, Any] | None = None
    second_meta: dict[str, Any] | None = None
    if first.get("verdict") == "REJECTED":
        _write_json(output_dir / "status.json", {"state": "running", "stage": "rewrite"})
        rewrite_prompt = _rewriter_user_prompt(
            problem=inputs["problem"], proof=inputs["proof"],
            defect_packet=inputs["defect_packet"], rejected_brief=inputs["original_brief"],
            rejection=str(first["markdown"])
        )
        rewrite_text, rewrite_meta = _run_markdown_call(
            endpoint=gemma_endpoint, model=GEMMA_MODEL,
            system_prompt=REWRITER_SYSTEM_PROMPT, user_prompt=rewrite_prompt,
            output_dir=output_dir / "02_rewrite", stage="rewrite_repair_brief",
            temperature=0.4, seed=_seed("rewrite"), reasoning_effort=REASONING_EFFORT
        )
        rewrite = parse_rewriter_markdown(rewrite_text)
        _write_json(output_dir / "02_rewrite/rewrite_repair_brief.parsed.json", rewrite)
        if not rewrite["valid"]:
            raise ValueError(f"invalid rewrite Markdown: {rewrite['errors']}")
        selected_brief = str(rewrite["repair_brief"])
        _write_json(output_dir / "status.json", {"state": "running", "stage": "recertify"})
        second_prompt = _certifier_user_prompt(
            problem=inputs["problem"], proof=inputs["proof"],
            defect_packet=inputs["defect_packet"], repair_brief=selected_brief,
            pass_name="fresh_recertification_of_rewritten_brief"
        )
        second_text, second_meta = _run_markdown_call(
            endpoint=qwen_endpoint, model=QWEN_MODEL,
            system_prompt=CERTIFIER_SYSTEM_PROMPT, user_prompt=second_prompt,
            output_dir=output_dir / "03_recertify", stage="recertify_rewritten_brief",
            temperature=0.2, seed=_seed("recertify_fresh"), reasoning_effort=None
        )
        second = parse_certification_markdown(second_text)
        _write_json(output_dir / "03_recertify/recertify_rewritten_brief.parsed.json", second)
        if not second["valid"]:
            raise ValueError(f"invalid recertification Markdown: {second['errors']}")

    final_certification = second if second is not None else first
    certified = final_certification.get("verdict") == "CERTIFIED"
    resolver_result: dict[str, Any] | None = None
    rectified_record: str | None = None
    if certified:
        rectified_record = replace_resolver_brief(inputs["fusion_record"], selected_brief)
        (output_dir / "input/fusion.certified_rectified.txt").write_text(
            rectified_record + "\n", encoding="utf-8"
        )
        _write_json(output_dir / "status.json", {"state": "running", "stage": "resolver"})
        resolver_result = _run_resolver(
            inputs=inputs, fusion_record=rectified_record,
            endpoint=gemma_endpoint, output_dir=output_dir
        )

    logical_calls = 1 + (2 if rewrite is not None else 0) + (1 if resolver_result else 0)
    summary = {
        "schema": "cognitive-well-v0266-p5-repair-brief-certification-summary-v1",
        "state": "completed",
        "case_id": CASE_ID,
        "original_brief_verdict": first.get("verdict"),
        "rewrite_performed": rewrite is not None,
        "rewritten_brief_verdict": second.get("verdict") if second else None,
        "certified_brief_available": certified,
        "resolver_performed": resolver_result is not None,
        "resolver_outcome": (resolver_result or {}).get("outcome"),
        "resolved_proof_path": (resolver_result or {}).get("resolved_proof_path"),
        "resolved_proof_sha256": (resolver_result or {}).get("resolved_proof_sha256"),
        "logical_model_calls": logical_calls,
        "expected_physical_model_calls_with_budget_forcing": 2 * logical_calls,
        "hard_cap_per_physical_call": MAX_OUTPUT_TOKENS,
        "selected_brief": selected_brief if certified else None,
        "selected_brief_sha256": _sha256_text(selected_brief) if certified else None,
        "rectified_fusion_record_sha256": (
            _sha256_text(rectified_record) if rectified_record else None
        ),
        "first_certification": first,
        "rewrite": rewrite,
        "second_certification": second,
        "generation_metadata": {
            "first_certification": first_meta,
            "rewrite": rewrite_meta,
            "second_certification": second_meta,
            "resolver": (resolver_result or {}).get("metadata"),
        },
    }
    _write_json(output_dir / "summary.json", summary)
    _write_json(output_dir / "status.json", {"state": "completed", "stage": "done"})
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Certify and rectify the P5 t10_r01 Fusion repair brief"
    )
    parser.add_argument("--source-run", type=Path, default=DEFAULT_SOURCE_RUN)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--qwen-endpoint", default=DEFAULT_QWEN_ENDPOINT)
    parser.add_argument("--gemma-endpoint", default=DEFAULT_GEMMA_ENDPOINT)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--execute-models", action="store_true")
    args = parser.parse_args()
    if args.dry_run == args.execute_models:
        parser.error("select exactly one of --dry-run or --execute-models")
    result = run_pipeline(
        source_run=args.source_run,
        output_dir=args.output_dir,
        qwen_endpoint=args.qwen_endpoint,
        gemma_endpoint=args.gemma_endpoint,
        dry_run=args.dry_run,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


__all__ = [
    "MAX_OUTPUT_TOKENS", "canonical_defect_packet", "extract_resolver_brief",
    "parse_certification_markdown", "parse_rewriter_markdown",
    "replace_resolver_brief", "run_pipeline"
]
