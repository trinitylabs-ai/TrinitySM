"""Generic proof + theorem -> exact-tool-assisted rewritten proof and provenance.

This entry point performs fresh acquisition. It never imports a problem adapter,
a prior packaging run, or a gold reference. Unsupported tool routes fail closed.
"""
from __future__ import annotations

import argparse
import json
import sys
import threading
from pathlib import Path

from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906.contracts import SynthesisAdapter, SynthesisContract, TaskInputs
from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906.tool_purpose import DETECTION_DOCUMENT, MATCHER_DOCUMENT
from cognitive_well_harness_v0_3_309_guarded_formalization_direct_laurent_20260906 import pipeline as acquisition
from cognitive_well_harness_v0_3_309_guarded_formalization_direct_laurent_20260906.resume_first_promoted_synthesis import _verify_prepared_route
from . import pipeline
from .certificate import GenericCertificateContext
from .saved_witness import SavedWitnessProvider


def write_record(path, record):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def assert_generic_boundary():
    forbidden = ("experiments.legacy_problem_specific_adapters", "cognitive_well_harness_v0_3_285_human_readable_t10_certificate_20260905")
    loaded = [name for name in sys.modules if any(name == item or name.startswith(item + ".") for item in forbidden)]
    if loaded:
        raise ValueError("generic worker imported legacy mathematical adapters: " + ", ".join(loaded))


class BudgetedCalls:
    """Bound logical calls and prompt size without changing any model decision."""

    def __init__(self, output, *, max_stages=24):
        self.output, self.max_stages = output, max_stages
        self.records, self.lock = [], threading.Lock()

    def __call__(self, **kwargs):
        with self.lock:
            if len(self.records) >= self.max_stages:
                raise RuntimeError("fixed model-stage budget exhausted")
            record = {"stage": kwargs["stage"], "destination": str(kwargs["destination"]),
                      "state": "running", "prompt_characters": len(kwargs["system_prompt"]) + len(kwargs["user_prompt"])}
            self.records.append(record)
            self._save()
        try:
            result = pipeline._mandatory_budget_forced_model_call(
                **kwargs, token_caps=(32768, 49152), prompt_character_limit=180_000,
                feedback_history_limit=1,
            )
            with self.lock:
                record.update(state="completed", attempt=result[2]["attempt"], cap=result[2]["cap"])
            return result
        except Exception as error:
            with self.lock:
                record.update(state="failed", error=f"{type(error).__name__}: {error}")
            raise
        finally:
            with self.lock:
                self._save()

    def _save(self):
        write_record(self.output, {"max_model_stages": self.max_stages,
            "token_caps": [32768, 49152], "thinking_token_budget": 16384,
            "prompt_character_limit": 180_000, "parser_feedback_responses_kept": 1,
            "calls": self.records})


def promoted_context(*, problem, proof, formalization, route, route_root, acquisition_root, audit_root, matcher, **unused):
    """Bind only this fresh proof's exact and independently audited artifacts."""
    audit = json.loads((audit_root / "result.json").read_text(encoding="utf-8"))
    parsed_audit = acquisition.parse_post_singular_audit((audit_root / "audit.md").read_text(encoding="utf-8").strip())
    label = route["label"]
    formal_root = acquisition_root / "03_guarded_formalizations" / label
    formal_text = (formal_root / "formalization.md").read_text(encoding="utf-8").strip()
    if (not parsed_audit["accepted"] or audit["audit"] != parsed_audit
            or audit.get("exact_result_supplied") is not False
            or audit.get("laurent_outcome_supplied") is not False
            or audit["formalization_sha256"] != pipeline.base.sha256_text(formal_text)):
        raise ValueError("semantic audit does not bind this formalization")
    evidence = _verify_prepared_route(route_root, route, formalization)
    artifacts = {
        "original_theorem": acquisition_root / "input/original_theorem.md",
        "original_proof": acquisition_root / "input/resolver1_proof.md",
        "tool_detection": acquisition_root / "01_detection/detection.md",
        "tool_matcher": acquisition_root / "02_matcher/matcher.md",
        "formal_request": formal_root / "formalization.md",
        "formal_request_raw": formal_root / "formalization_raw.md",
        "exact_result": route_root / "04_exact_evidence.md",
        "semantic_audit": audit_root / "audit.md",
        "semantic_audit_result": audit_root / "result.json",
        "membership_identity": route_root / "02_target_screen/derived_identity_certificate.json",
        "source_lift": route_root / "03_laurent_lift/full_source_lift_certificate.json",
        "route": route_root / "route_state.json",
        "selection": acquisition_root / "07_selection/selection.json",
    }
    for directory in ("02_target_screen", "03_laurent_lift"):
        for index, path in enumerate(sorted(item for item in (route_root / directory).rglob("*") if item.is_file())):
            artifacts[f"saved_{directory}_{index}"] = path
    hashes = {key: pipeline.base.sha256_file(path) for key, path in artifacts.items()}
    if artifacts["original_theorem"].read_text(encoding="utf-8").strip() != problem.statement.strip() or artifacts["original_proof"].read_text(encoding="utf-8").strip() != proof.strip():
        raise ValueError("fresh theorem/proof input binding changed")
    guard_program = formalization["guard_program"]
    guards = dict(guard_program["source_nonzero"])
    for key, division in guard_program["provenance_divisions"].items():
        guard_label = f"denominator_{key}"
        if guard_label in guards:
            raise ValueError("typed guard labels collide")
        guards[guard_label] = division["denominator"]
    replay = {"schema": "generic-fresh-certificate-replay-v1", "verified": True,
              "operation": matcher["operation"], "claim": matcher["claim"], "verdict": "VERIFIED_SUPPORT",
              "source_artifact_sha256": hashes,
              "source_arguments_sha256": pipeline.exact_tools.stable_hash(formalization["arguments"])}

    def replay_exact():
        if {key: pipeline.base.sha256_file(path) for key, path in artifacts.items()} != hashes:
            raise ValueError("fresh certificate source artifact drift")
        return dict(replay)

    def replay_formal():
        parsed = acquisition.parse_guarded_formalization(artifacts["formal_request_raw"].read_text(encoding="utf-8").strip())
        if parsed["arguments"] != formalization["arguments"] or parsed["guard_program"] != guard_program:
            raise ValueError("fresh formalization parser replay drift")
        return parsed["arguments"]

    context = GenericCertificateContext(
        certificate_id="fresh_" + hashes["formal_request"][:16], theorem=problem.statement,
        arguments=formalization["arguments"], typed_guards=guards, replay_exact=replay_exact,
        replay_formal_request=replay_formal, formal_request_markdown=formal_text,
        exact_result_markdown=evidence, source_artifacts=artifacts,
    )
    return TaskInputs(problem.problem_id, problem.statement, proof, {
        DETECTION_DOCUMENT: artifacts["tool_detection"].read_text(encoding="utf-8").strip(),
        MATCHER_DOCUMENT: artifacts["tool_matcher"].read_text(encoding="utf-8").strip(),
    }), context


def synthesis_contract(bindings, target_label):
    """Case-independent instructions; bindings and labels belong in user evidence.

    Keep the arguments for callers, but never interpolate their contents into
    the system prompt. The appendix path supplies the accepted formalization.
    """
    return SynthesisContract(
        evidence_marker="[[VERIFIED_EXACT_EVIDENCE]]",
        rewrite_requirements=(
            "Define every formal symbol and derive every source equation from the theorem.",
            "Justify every nonzero guard before division, including boundary and degenerate cases.",
            "Translate the inserted lemma's conclusion into the original theorem conclusion; show every load-bearing intermediate calculation.",
            "Write a complete standalone proof, ending with the full theorem conclusion.",
        ),
        literal_requirements=(), conclusion_alternatives=(), semantic_conclusion_only=True,
        auditor_focus="Check the full theorem conclusion semantically, not by literal matching. Independently verify all symbol meanings, source equations, guard justifications, and the final implication. Reject any unsupported decisive simplification.",
        max_cycles=3,
    )


def synthesize_promoted(*, output_dir, status, calls, gemma, qwen, master_seed, **promoted):
    status.update(stage="verified_certificate_rendering", selected_label=promoted["route"]["label"])
    write_record(output_dir / "status.json", status)
    task, context = promoted_context(**promoted)
    provider = SavedWitnessProvider(context)
    pipeline.base.write_text(output_dir / "saved_lemma.md", provider.markdown)
    write_record(output_dir / "saved_lemma_verification.json", provider.verification)
    adapter = SynthesisAdapter("generic_fresh_saved_witness", task, provider,
        synthesis_contract(promoted["formalization"]["bindings"], provider.verification["target_label_latex"]))
    status.update(stage="proof_synthesis")
    write_record(output_dir / "status.json", status)
    result = pipeline.synthesis_pipeline.run(adapter=adapter, output_dir=output_dir / "02_synthesis",
        gemma=gemma, qwen=qwen, master_seed=master_seed + 2000,
        model_call=pipeline._with_user_semantics(calls, promoted["formalization"]["bindings"]))
    forcing = pipeline._verify_synthesis_budget_forcing(synthesis_root=output_dir / "02_synthesis",
        synthesis=result, gemma=gemma, qwen=qwen)
    return {"state": "completed", "problem_id": task.problem_id, "synthesis_result": result,
            "synthesis_budget_forcing": forcing, "terminal_proof": result["terminal_proof"],
            "terminal_proof_sha256": result["terminal_proof_sha256"]}


def run(*, problem_file, proof_file, output_dir, gemma, qwen, master_seed, excluded_operations=()):
    assert_generic_boundary()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=False)
    calls = BudgetedCalls(output_dir / "model_budget.json")
    status = {"schema": "generic-tool-proof-rewrite-v1", "state": "running", "stage": "fresh_detection",
              "problem_file": str(problem_file.resolve()), "proof_file": str(proof_file.resolve()),
              "problem_file_sha256": pipeline.base.sha256_file(problem_file),
              "input_proof_sha256": pipeline.base.sha256_file(proof_file), "preloaded_certificate": False}
    write_record(output_dir / "status.json", status)

    def synthesize(**promoted):
        return synthesize_promoted(output_dir=output_dir, status=status, calls=calls,
            gemma=gemma, qwen=qwen, master_seed=master_seed, **promoted)

    try:
        result = acquisition.run_after_resolver1(
            problem_file=problem_file, proof_file=proof_file, output_dir=output_dir / "01_acquisition",
            detector=qwen, compiler=gemma, auditor=qwen, rewriter=gemma, master_seed=master_seed,
            excluded_matcher_operations=tuple(excluded_operations), on_promoted=synthesize,
            model_call=calls, compiler_model_call=calls,
        )
        assert_generic_boundary()
        status.update(result, stage="finished")
    except Exception as error:
        status.update(state="failed_closed", stage="finished", error=f"{type(error).__name__}: {error}")
    write_record(output_dir / "status.json", status)
    write_record(output_dir / "result.json", status)
    return status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--problem-file", type=Path, required=True)
    parser.add_argument("--proof-file", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--master-seed", type=int, required=True)
    parser.add_argument("--exclude-operation", action="append", default=[])
    args = parser.parse_args()
    result = run(problem_file=args.problem_file, proof_file=args.proof_file, output_dir=args.output_dir,
        master_seed=args.master_seed, excluded_operations=args.exclude_operation,
        gemma=pipeline.base.Role("http://127.0.0.1:8030/v1", pipeline.base.DEFAULT_GEMMA_MODEL, 0.2, "max"),
        qwen=pipeline.base.Role("http://127.0.0.1:8027/v1", pipeline.base.DEFAULT_QWEN_MODEL, 0.1, None))
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return 0 if result["state"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
