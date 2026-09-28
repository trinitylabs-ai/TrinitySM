from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import traceback
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from cognitive_well_harness_v0_2_7_failed_reasoning_memory_20260812 import (
    prompts as v027_prompts,
)
from cognitive_well_harness_v0_2_7_failed_reasoning_memory_20260812.core import (
    utc_now,
    write_json,
)
from experiments.local_math_verifier.runtime import (
    HTTPGenerationConfig,
    run_openai_chat_generation,
)

from . import HARNESS_VERSION
from .protocol import (
    HYPOTHESIS_SCHEMA,
    NEGATION_AUDIT_SCHEMA,
    NEGATION_REPAIR_SCHEMA,
    PROOF_AUDIT_SCHEMA,
    REPETITION_DETECTION,
    final_repair_prompt,
    lemma_repair_prompt,
    lemma_solver_prompt,
    negation_audit_prompt,
    normalize_hypothesis_record,
    parse_json_object,
    proof_audit_prompt,
    qwen_negation_verifier_system_prompt,
    qwen_verifier_system_prompt,
    synthesis_prompt,
)


GEMMA_MODEL = "google/gemma-4-31B-it"
GEMMA_REVISION = "842da3794eaa0b77d5f08bae87a17459d91ff475"
QWEN_MODEL = "Qwen/Qwen3.6-27B"
QWEN_REVISION = "6a9e13bd6fc8f0983b9b99948120bc37f49c13e9"
PROBLEM_PATH = Path("math_harness_inputs/imo2026_p4_p2_v0313_20260815/imo2026_p5.json")
FUSION_RUN = Path("runs/v053_fusion_all36_gemma4_bf16_mtp4_t04_gpu0_b4_16k_20260823_1748")
RESOLVER_RUN = Path("runs/v054_resolver_repair29_gemma4_bf16_mtp4_t020406_gpu0_b4_32k_20260823_1815")
TRACKS = (
    ("p5.t10_r03", "t10_r03", "anchor"),
    ("p5.t07_r01", "t07_r01", "supplement"),
)


def stable_seed(label: str) -> int:
    return int.from_bytes(hashlib.sha256(f"v057:{label}".encode()).digest()[:4], "big") or 1


def load_inputs() -> tuple[str, list[dict[str, str]]]:
    problem = str(json.loads(PROBLEM_PATH.read_text(encoding="utf-8"))["claim"])
    seeds: list[dict[str, str]] = []
    for track_id, candidate_id, role in TRACKS:
        resolver_path = RESOLVER_RUN / "resolver" / "temperature_0_4" / "gpu0" / "p5" / candidate_id / "result.json"
        fusion_path = FUSION_RUN / "fusion" / "temperature_0_4" / "gpu0" / "p5" / candidate_id / "result.json"
        resolver = json.loads(resolver_path.read_text(encoding="utf-8"))
        fusion = json.loads(fusion_path.read_text(encoding="utf-8"))
        proof = str((resolver.get("parsed") or {}).get("proof") or "").strip()
        dossier = str(fusion.get("final") or "").strip()
        if not proof or not dossier:
            raise ValueError(f"missing selected-track material for {track_id}")
        seeds.append(
            {
                "solution_id": track_id,
                "role": role,
                "proof": proof,
                "proof_sha256": hashlib.sha256(proof.encode()).hexdigest(),
                "fusion_dossier": dossier,
                "fusion_dossier_sha256": hashlib.sha256(dossier.encode()).hexdigest(),
                "resolver_result_path": str(resolver_path.resolve()),
                "fusion_result_path": str(fusion_path.resolve()),
            }
        )
    return problem, seeds


def validate_schema(record: dict[str, Any], schema: dict[str, Any]) -> None:
    errors = sorted(Draft202012Validator(schema).iter_errors(record), key=lambda row: list(row.path))
    if errors:
        location = ".".join(str(part) for part in errors[0].absolute_path) or "<root>"
        raise ValueError(f"schema error at {location}: {errors[0].message}")


def saved_generation(destination: Path, stage: str) -> dict[str, Any] | None:
    response_path = destination / f"{stage}.raw_response.json"
    metadata_path = destination / f"{stage}.metadata.json"
    if not response_path.exists() or not metadata_path.exists():
        return None
    response = json.loads(response_path.read_text(encoding="utf-8"))
    text = str(response["choices"][0]["message"].get("content") or "")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    return {"text": text, "metadata": metadata}


def gemma_text(
    *, endpoint: str, prompt: str, destination: Path, stage: str, seed_label: str, temperature: float, max_tokens: int
) -> dict[str, Any]:
    destination.mkdir(parents=True, exist_ok=True)
    return run_openai_chat_generation(
        endpoint=endpoint,
        model=GEMMA_MODEL,
        prompt=prompt,
        user_prompt="Execute the requested mathematical task now.",
        output_dir=destination,
        stage=stage,
        config=HTTPGenerationConfig(
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=0.95,
            top_k=64,
            seed=stable_seed(seed_label),
            thinking_token_budget=None,
            reasoning_effort="max",
            repetition_detection=REPETITION_DETECTION,
            timeout_seconds=14_400,
        ),
    )


def json_call(
    *,
    endpoint: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    destination: Path,
    stage: str,
    seed_label: str,
    schema: dict[str, Any],
    max_tokens: int,
    temperature: float = 0.2,
) -> tuple[dict[str, Any], dict[str, Any]]:
    destination.mkdir(parents=True, exist_ok=True)
    generated = run_openai_chat_generation(
        endpoint=endpoint,
        model=model,
        prompt=system_prompt,
        user_prompt=user_prompt,
        output_dir=destination,
        stage=stage,
        config=HTTPGenerationConfig(
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=1.0,
            top_k=-1,
            seed=stable_seed(seed_label),
            thinking_token_budget=None,
            reasoning_effort="max",
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": stage,
                    "strict": True,
                    "schema": schema,
                },
            },
            repetition_detection=REPETITION_DETECTION,
            timeout_seconds=14_400,
        ),
    )
    record = parse_json_object(str(generated["text"]))
    validate_schema(record, schema)
    return record, generated


def extract_hypotheses(
    *, arm: str, problem: str, seeds: list[dict[str, str]], gemma_endpoint: str, output_dir: Path
) -> dict[str, Any]:
    result_path = output_dir / "result.json"
    if result_path.exists():
        return json.loads(result_path.read_text(encoding="utf-8"))
    packets: list[dict[str, Any]] = []
    for seed in seeds:
        packet: dict[str, Any] = {
            "solution_id": seed["solution_id"],
            "role": seed["role"],
            "proof": seed["proof"],
        }
        if arm == "diagnostic":
            packet["fusion_dossier"] = {
                "status": "NONAUTHORITATIVE_DIAGNOSTIC",
                "instruction": "Recheck every assertion; use only to locate promising material or gaps.",
                "final_structured_record": seed["fusion_dossier"],
            }
        packets.append(packet)
    document_prompt = v027_prompts.conjecture_extractor(problem, packets, [], [], [])
    generated = saved_generation(output_dir, "hypothesis_extraction_document")
    if generated is None:
        generated = gemma_text(
            endpoint=gemma_endpoint,
            prompt=document_prompt,
            destination=output_dir,
            stage="hypothesis_extraction_document",
            seed_label="hypothesis_extraction_document",
            temperature=1.0,
            max_tokens=32_768,
        )
    document = str(generated["text"]).strip()
    parsed_generation = saved_generation(output_dir, "hypothesis_extraction_parser")
    if parsed_generation is None:
        record, parsed_generation = json_call(
            endpoint=gemma_endpoint,
            model=GEMMA_MODEL,
            system_prompt=v027_prompts.conjecture_parser(document),
            user_prompt="Parse the supplied hypothesis document now.",
            destination=output_dir,
            stage="hypothesis_extraction_parser",
            seed_label="hypothesis_extraction_parser",
            schema=HYPOTHESIS_SCHEMA,
            max_tokens=16_384,
            temperature=0.1,
        )
    else:
        record = normalize_hypothesis_record(
            parse_json_object(str(parsed_generation["text"]))
        )
        validate_schema(record, HYPOTHESIS_SCHEMA)
    if len(record["conjectures"]) != len(record["negations"]):
        raise ValueError("conjecture and negation counts differ")
    result = {
        "arm": arm,
        "dossier_exposed": arm == "diagnostic",
        "seed_packets": packets,
        "document": document,
        "record": record,
        "document_generation": generated["metadata"],
        "parser_generation": parsed_generation["metadata"],
    }
    write_json(output_dir / "result.json", result)
    return result


def audit_negation(
    *, problem: str, claim: str, negation: str, qwen_endpoint: str, destination: Path, stage: str, seed_label: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    return json_call(
        endpoint=qwen_endpoint,
        model=QWEN_MODEL,
        system_prompt=qwen_negation_verifier_system_prompt(),
        user_prompt=negation_audit_prompt(problem=problem, claim=claim, proposed_negation=negation),
        destination=destination,
        stage=stage,
        seed_label=seed_label,
        schema=NEGATION_AUDIT_SCHEMA,
        max_tokens=8_192,
    )


def validate_and_repair_negations(
    *, hypotheses: dict[str, Any], problem: str, gemma_endpoint: str, qwen_endpoint: str, output_dir: Path
) -> list[dict[str, str]]:
    pairs: list[dict[str, str]] = []
    for index, (claim, negation) in enumerate(zip(hypotheses["conjectures"], hypotheses["negations"]), start=1):
        destination = output_dir / f"h{index}"
        audit, _ = audit_negation(
            problem=problem, claim=claim, negation=negation, qwen_endpoint=qwen_endpoint,
            destination=destination, stage="negation_audit_0", seed_label=f"h{index}:negation:audit0",
        )
        final_negation = negation
        if not audit["valid_exact_negation"]:
            repair, _ = json_call(
                endpoint=gemma_endpoint,
                model=GEMMA_MODEL,
                system_prompt="You are an olympiad logician. Repair only the exact negation. Return JSON only.",
                user_prompt=(
                    f"PROBLEM:\n{problem}\n\nCLAIM:\n{claim}\n\nINVALID NEGATION:\n{negation}"
                    f"\n\nQWEN ISSUE:\n{audit['first_issue']}"
                ),
                destination=destination,
                stage="negation_repair",
                seed_label=f"h{index}:negation:repair",
                schema=NEGATION_REPAIR_SCHEMA,
                max_tokens=8_192,
                temperature=0.1,
            )
            final_negation = str(repair["exact_negation"])
            audit, _ = audit_negation(
                problem=problem, claim=claim, negation=final_negation, qwen_endpoint=qwen_endpoint,
                destination=destination, stage="negation_audit_1", seed_label=f"h{index}:negation:audit1",
            )
        if not audit["valid_exact_negation"]:
            raise RuntimeError(f"Qwen could not certify exact negation for H{index}: {audit['first_issue']}")
        pair = {"claim_id": f"H{index}", "positive": claim, "negative": final_negation}
        write_json(destination / "result.json", {**pair, "audit": audit})
        pairs.append(pair)
    return pairs


def qwen_audit(
    *, problem: str, claim: str, proof: str, qwen_endpoint: str, destination: Path, stage: str, seed_label: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    record, generated = json_call(
        endpoint=qwen_endpoint,
        model=QWEN_MODEL,
        system_prompt=qwen_verifier_system_prompt(),
        user_prompt=proof_audit_prompt(problem=problem, claim=claim, proof=proof),
        destination=destination,
        stage=stage,
        seed_label=seed_label,
        schema=PROOF_AUDIT_SCHEMA,
        max_tokens=16_384,
    )
    if record["verdict"] == "PASS" and (
        record["earliest_break"] is not None
        or record["exact_claim_reached"] is not True
        or record["missing_obligations"]
    ):
        raise ValueError("Qwen PASS record is internally inconsistent")
    if record["verdict"] == "FAIL" and not record["earliest_break"]:
        raise ValueError("Qwen FAIL record omitted the earliest break")
    return record, generated


def prove_side(
    *, pair: dict[str, str], side: str, problem: str, gemma_endpoint: str, qwen_endpoint: str, output_dir: Path
) -> dict[str, Any]:
    claim = pair[side]
    destination = output_dir / pair["claim_id"] / side
    generated = gemma_text(
        endpoint=gemma_endpoint,
        prompt=lemma_solver_prompt(problem=problem, claim=claim),
        destination=destination,
        stage="proof_0",
        seed_label=f"{pair['claim_id']}:{side}:proof0",
        temperature=0.6,
        max_tokens=32_768,
    )
    proof = str(generated["text"]).strip()
    audit, audit_generation = qwen_audit(
        problem=problem, claim=claim, proof=proof, qwen_endpoint=qwen_endpoint,
        destination=destination, stage="audit_0", seed_label=f"{pair['claim_id']}:{side}:audit0",
    )
    repair_invoked = audit["verdict"] != "PASS"
    if repair_invoked:
        repaired = gemma_text(
            endpoint=gemma_endpoint,
            prompt=lemma_repair_prompt(problem=problem, claim=claim, proof=proof, audit=audit),
            destination=destination,
            stage="proof_1_repair",
            seed_label=f"{pair['claim_id']}:{side}:proof1",
            temperature=0.2,
            max_tokens=32_768,
        )
        proof = str(repaired["text"]).strip()
        audit, audit_generation = qwen_audit(
            problem=problem, claim=claim, proof=proof, qwen_endpoint=qwen_endpoint,
            destination=destination, stage="audit_1", seed_label=f"{pair['claim_id']}:{side}:audit1",
        )
    result = {
        "claim_id": pair["claim_id"],
        "side": side,
        "claim": claim,
        "proof": proof,
        "audit": audit,
        "repair_invoked": repair_invoked,
        "certified": audit["verdict"] == "PASS",
        "generation": generated["metadata"],
        "audit_generation": audit_generation["metadata"],
    }
    write_json(destination / "result.json", result)
    (destination / "proof.md").write_text(proof + "\n", encoding="utf-8")
    return result


def prove_pairs(
    *, pairs: list[dict[str, str]], problem: str, gemma_endpoint: str, qwen_endpoint: str, output_dir: Path
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    jobs = [(pair, side) for pair in pairs for side in ("positive", "negative")]
    results: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(
                prove_side, pair=pair, side=side, problem=problem,
                gemma_endpoint=gemma_endpoint, qwen_endpoint=qwen_endpoint, output_dir=output_dir,
            )
            for pair, side in jobs
        ]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    verified: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    by_pair: dict[str, dict[str, dict[str, Any]]] = {}
    for result in results:
        by_pair.setdefault(result["claim_id"], {})[result["side"]] = result
    for pair in pairs:
        sides = by_pair[pair["claim_id"]]
        certified = [side for side in ("positive", "negative") if sides[side]["certified"]]
        if len(certified) == 1:
            side = certified[0]
            verified.append(
                {
                    "lemma_id": pair["claim_id"],
                    "direction": side,
                    "statement": pair[side],
                    "proof": sides[side]["proof"],
                    "qwen_audit": sides[side]["audit"],
                }
            )
        else:
            unresolved.append(
                {
                    "claim_id": pair["claim_id"],
                    "status": "conflict" if len(certified) == 2 else "unresolved",
                    "positive_audit": sides["positive"]["audit"],
                    "negative_audit": sides["negative"]["audit"],
                }
            )
    write_json(output_dir / "summary.json", {"verified": verified, "unresolved": unresolved})
    return verified, unresolved


def synthesize_one(
    *, family: str, problem: str, seeds: list[dict[str, str]], verified: list[dict[str, Any]], unresolved: list[dict[str, Any]], gemma_endpoint: str, qwen_endpoint: str, output_dir: Path
) -> dict[str, Any]:
    destination = output_dir / family
    seed_packet = [{"solution_id": row["solution_id"], "role": row["role"], "proof": row["proof"]} for row in seeds]
    generated = gemma_text(
        endpoint=gemma_endpoint,
        prompt=synthesis_prompt(family=family, problem=problem, seeds=seed_packet, verified=verified, unresolved=unresolved),
        destination=destination,
        stage="proof_0",
        seed_label=f"terminal:{family}:proof0",
        temperature=0.4,
        max_tokens=32_768,
    )
    proof = str(generated["text"]).strip()
    audit, audit_generation = qwen_audit(
        problem=problem, claim=problem, proof=proof, qwen_endpoint=qwen_endpoint,
        destination=destination, stage="audit_0", seed_label=f"terminal:{family}:audit0",
    )
    repair_invoked = audit["verdict"] != "PASS"
    if repair_invoked:
        repaired = gemma_text(
            endpoint=gemma_endpoint,
            prompt=final_repair_prompt(problem=problem, proof=proof, audit=audit),
            destination=destination,
            stage="proof_1_repair",
            seed_label=f"terminal:{family}:proof1",
            temperature=0.2,
            max_tokens=32_768,
        )
        proof = str(repaired["text"]).strip()
        audit, audit_generation = qwen_audit(
            problem=problem, claim=problem, proof=proof, qwen_endpoint=qwen_endpoint,
            destination=destination, stage="audit_1", seed_label=f"terminal:{family}:audit1",
        )
    result = {
        "family": family,
        "proof": proof,
        "proof_sha256": hashlib.sha256(proof.encode()).hexdigest(),
        "qwen_audit": audit,
        "qwen_certified": audit["verdict"] == "PASS",
        "repair_invoked": repair_invoked,
        "generation": generated["metadata"],
        "audit_generation": audit_generation["metadata"],
    }
    write_json(destination / "result.json", result)
    (destination / "proof.md").write_text(proof + "\n", encoding="utf-8")
    return result


def status(output_dir: Path, **values: Any) -> None:
    write_json(output_dir / "status.json", {**values, "updated_at": utc_now()})


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one Terra-free cross-model v0.3.30-topology replay arm")
    parser.add_argument("--arm", choices=("original", "diagnostic"), required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--gemma-endpoint", default="http://127.0.0.1:8020/v1")
    parser.add_argument("--qwen-endpoint", default="http://127.0.0.1:8027/v1")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    problem, seeds = load_inputs()
    manifest = {
        "schema": "cognitive-well-v0.3.57-v030-cross-model-arm-manifest-v1",
        "created_at": utc_now(),
        "harness_version": HARNESS_VERSION,
        "arm": args.arm,
        "base_topology": "v0.3.30 Phase 2: joint hypothesis extraction -> lemma proof -> refinement/synthesis",
        "constructive_model": {"model": GEMMA_MODEL, "revision": GEMMA_REVISION, "dtype": "bfloat16", "mtp": 4, "endpoint": args.gemma_endpoint},
        "verifier_model": {"model": QWEN_MODEL, "revision": QWEN_REVISION, "dtype": "bfloat16", "role": "non-scoring proof verifier", "endpoint": args.qwen_endpoint},
        "terra_calls": 0,
        "intermediate_numeric_scores": False,
        "final_codex_evaluation_in_pipeline": False,
        "fusion_dossier_exposed": args.arm == "diagnostic",
        "fusion_dossier_scope": "initial joint hypothesis extraction only" if args.arm == "diagnostic" else "not exposed",
        "repetition_detection": REPETITION_DETECTION,
        "seed_proofs": [{key: row[key] for key in ("solution_id", "role", "proof_sha256", "fusion_dossier_sha256", "resolver_result_path", "fusion_result_path")} for row in seeds],
        "problem_path": str(PROBLEM_PATH.resolve()),
        "problem_sha256": hashlib.sha256(problem.encode()).hexdigest(),
        "gold_or_reference_accessed": False,
    }
    write_json(args.output_dir / "manifest.json", manifest)
    try:
        status(args.output_dir, state="running", stage="hypothesis_extraction", arm=args.arm)
        extraction = extract_hypotheses(
            arm=args.arm, problem=problem, seeds=seeds, gemma_endpoint=args.gemma_endpoint,
            output_dir=args.output_dir / "hypothesis_extraction",
        )
        status(args.output_dir, state="running", stage="exact_negation_validation", arm=args.arm)
        pairs = validate_and_repair_negations(
            hypotheses=extraction["record"], problem=problem, gemma_endpoint=args.gemma_endpoint,
            qwen_endpoint=args.qwen_endpoint, output_dir=args.output_dir / "negation_validation",
        )
        status(args.output_dir, state="running", stage="lemma_proof_and_qwen_audit", arm=args.arm, hypothesis_count=len(pairs))
        verified, unresolved = prove_pairs(
            pairs=pairs, problem=problem, gemma_endpoint=args.gemma_endpoint,
            qwen_endpoint=args.qwen_endpoint, output_dir=args.output_dir / "lemma_verification",
        )
        status(args.output_dir, state="running", stage="terminal_synthesis", arm=args.arm, verified_lemma_count=len(verified), unresolved_count=len(unresolved))
        families = ("anchor_plus_evidence", "independent_reconstruction")
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(
                    synthesize_one, family=family, problem=problem, seeds=seeds,
                    verified=verified, unresolved=unresolved, gemma_endpoint=args.gemma_endpoint,
                    qwen_endpoint=args.qwen_endpoint, output_dir=args.output_dir / "terminal",
                )
                for family in families
            ]
            terminal = [future.result() for future in futures]
        terminal.sort(key=lambda row: families.index(row["family"]))
        summary = {
            "schema": "cognitive-well-v0.3.57-v030-cross-model-arm-summary-v1",
            "state": "completed",
            "arm": args.arm,
            "hypothesis_count": len(pairs),
            "verified_lemma_count": len(verified),
            "unresolved_count": len(unresolved),
            "terminal_candidates": [
                {key: row[key] for key in ("family", "proof_sha256", "qwen_certified", "repair_invoked", "qwen_audit")}
                for row in terminal
            ],
            "terra_calls": 0,
            "completed_at": utc_now(),
        }
        write_json(args.output_dir / "summary.json", summary)
        status(args.output_dir, state="completed", stage="terminal_synthesis", arm=args.arm, hypothesis_count=len(pairs), verified_lemma_count=len(verified), terminal_candidate_count=2)
    except Exception as error:
        status(args.output_dir, state="failed", stage="exception", arm=args.arm, error=f"{type(error).__name__}: {error}", traceback=traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
