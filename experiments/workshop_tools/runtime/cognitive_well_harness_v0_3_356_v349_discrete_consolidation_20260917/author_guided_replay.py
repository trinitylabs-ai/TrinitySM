"""Replay the existing certificate-author stage before saved-witness synthesis.

Only model-authored semantic notes condition the rewrite. The immutable algebra
remains the same independently verified saved witness, whether the author's new
compact algebra verifies or not. No prior rewritten proof or grading feedback is
fed into the models.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path
from types import SimpleNamespace

from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906.contracts import SynthesisAdapter
from . import experiment, pipeline, protocol, rewrite
from .saved_witness import SavedWitnessProvider


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_current_context(source):
    """Rebind a completed generic rewrite's original inputs and exact artifacts."""
    result = read(source / "result.json")
    if result.get("state") != "completed":
        raise ValueError("author-guided replay requires a completed source rewrite")
    terminal = Path(result["terminal_proof"]).resolve()
    if source not in terminal.parents or pipeline.base.sha256_text(terminal.read_text().strip()) != result["terminal_proof_sha256"]:
        raise ValueError("source terminal proof binding changed")
    synthesis_root = terminal.parent
    ledger = read(synthesis_root / "01_evidence/source_artifacts.json")
    artifacts = {label: Path(record["path"]) for label, record in ledger.items()}
    if any(pipeline.base.sha256_file(artifacts[label]) != record["sha256"] for label, record in ledger.items()):
        raise ValueError("source certificate artifact changed")
    lock = read(synthesis_root / "protocol_lock.json")["task"]
    theorem, proof = (artifacts[key].read_text().strip() for key in ("original_theorem", "original_proof"))
    if (pipeline.base.sha256_text(theorem) != lock["theorem_sha256"]
            or pipeline.base.sha256_text(proof) != lock["source_proof_sha256"]
            or result["problem_id"] != lock["problem_id"]):
        raise ValueError("original theorem/proof no longer match the completed case")
    selection = read(artifacts["selection"])
    if (selection["selected_route_state_sha256"] != pipeline.base.sha256_file(artifacts["route"])
            or selection["selected_audit_result_sha256"] != pipeline.base.sha256_file(artifacts["semantic_audit_result"])):
        raise ValueError("saved selection binding changed")
    formal = rewrite.acquisition.parse_guarded_formalization(artifacts["formal_request_raw"].read_text().strip())
    tool = read(synthesis_root / "01_evidence/tool_record.json")
    task, context = rewrite.promoted_context(
        problem=SimpleNamespace(problem_id=result["problem_id"], statement=theorem), proof=proof,
        formalization=formal, route=read(artifacts["route"]), route_root=artifacts["route"].parent,
        acquisition_root=artifacts["selection"].parent.parent, audit_root=artifacts["semantic_audit"].parent,
        matcher={"operation": tool["operation"], "claim": tool["claim"]})
    prior_calls = result["prior_model_stages"] + len(read(source / "model_budget.json")["calls"])
    if prior_calls + 7 > 24:
        raise ValueError("author plus three synthesis/audit cycles would exceed the original case budget")
    return task, context, prior_calls


def latest_author_semantics(author_root, *, task, model):
    """Reuse only the latest complete forced response, never select by meaning."""
    stage = pipeline.CERTIFICATE_AUTHOR_STAGE
    attempts = sorted(path for path in author_root.glob("attempt_*")
        if (path / f"{stage}.raw_response.json").is_file()
        and (path / f"{stage}.budget_forcing.json").is_file())
    if not attempts:
        raise ValueError("no completed budget-forced certificate-author response")
    latest = attempts[-1]
    path = latest / f"{stage}.raw_response.json"
    text = read(path)["choices"][0]["message"]["content"].strip()
    sections = protocol.mdp.exact_sections(text, ["Certificate Semantics", "Certificate Program"])
    semantics = protocol._parse_semantics(sections["Certificate Semantics"])
    if semantics["required_conclusion"].replace(" ", "") not in task.theorem.replace(" ", ""):
        raise ValueError("model-authored conclusion is not a literal part of the theorem")
    parts = latest.name.split("_")
    forcing = pipeline.validate_markdown_budget_forcing(
        {"attempt": int(parts[1]), "cap": int(parts[3]), "request_timeout_sec": 600,
         "metadata": {"v0257_budget_forcing": read(latest / f"{stage}.budget_forcing.json")}},
        expected_stage=stage, expected_model=model, canonical_markdown=text)
    return semantics, {"response_path": str(path), "response_sha256": pipeline.base.sha256_file(path),
        "canonical_markdown_sha256": pipeline.base.sha256_text(text),
        "budget_forcing_sha256": pipeline.exact_tools.stable_hash(forcing),
        "selection_policy": "latest_completed_forced_response_no_mathematical_selection"}


def run(source, output, *, master_seed, skill_launcher=None):
    rewrite.assert_generic_boundary()
    source, output = source.resolve(), output.resolve()
    task, context, prior_calls = load_current_context(source)
    provider = SavedWitnessProvider(context)
    # Supply the complete verified mathematical presentation instead of verbose
    # host-ledger serialization. No polynomial or identity is truncated.
    author_task = replace(task, additional_documents={"saved_exact_witness.md": provider.markdown})
    output.mkdir(parents=True, exist_ok=False)
    calls = rewrite.BudgetedCalls(output / "model_budget.json", max_stages=7)
    gemma = pipeline.base.Role("http://127.0.0.1:8030/v1", pipeline.base.DEFAULT_GEMMA_MODEL, 0.2, "max")
    qwen = pipeline.base.Role("http://127.0.0.1:8027/v1", pipeline.base.DEFAULT_QWEN_MODEL, 0.1, None)
    status = {"schema": "generic-author-guided-saved-witness-replay-v1", "state": "running",
        "stage": "certificate_author", "problem_id": task.problem_id, "source_run": str(source),
        "source_result_sha256": pipeline.base.sha256_file(source / "result.json"),
        "source_proof_sha256": pipeline.base.sha256_text(task.source_proof),
        "original_case_model_stages": prior_calls, "maximum_extra_model_stages": 7,
        "master_seed": master_seed, "new_formalization_calls": 0, "new_singular_calls": 0,
        "new_formalization_audits": 0, "prior_grades_or_rewrites_supplied": False,
        "immutable_saved_witness_sha256": provider.verification["markdown_sha256"],
        "manual_mathematical_content": False, "json_model_output": False}
    rewrite.write_record(output / "status.json", status)
    pipeline.base.write_text(output / "saved_lemma.md", provider.markdown)
    rewrite.write_record(output / "saved_lemma_verification.json", provider.verification)
    try:
        try:
            _, record = pipeline.generate_provider(task=author_task, context=context, gemma=gemma,
                output_dir=output / "01_certificate_author", master_seed=master_seed + 1000, model_call=calls)
            rewrite.write_record(output / "01_certificate_author/outcome.json", {"state": "verified", "record": record})
            status["compact_author_algebra_verified"] = True
        except Exception as error:
            rewrite.write_record(output / "01_certificate_author/outcome.json", {
                "state": "not_verified", "error": f"{type(error).__name__}: {error}"})
            status["compact_author_algebra_verified"] = False
        semantics, notes_record = latest_author_semantics(output / "01_certificate_author", task=task, model=gemma.model)
        rewrite.write_record(output / "untrusted_semantic_notes.json", semantics)
        rewrite.write_record(output / "semantic_notes_provenance.json", notes_record)
        status.update(stage="proof_synthesis", model_authored_algebra_used=False,
            mathematical_source="unchanged_verified_saved_witness", semantic_notes_status="untrusted_model_context")
        rewrite.write_record(output / "status.json", status)
        adapter = SynthesisAdapter("generic_author_guided_saved_witness", task, provider,
            pipeline._generic_contract({"semantics": semantics},
                conclusion_label="the target " + provider.verification["target_label_latex"]))
        synthesis = pipeline.synthesis_pipeline.run(adapter=adapter, output_dir=output / "02_synthesis",
            gemma=gemma, qwen=qwen, master_seed=master_seed + 2000,
            model_call=pipeline._with_user_semantics(calls, semantics))
        forcing = pipeline._verify_synthesis_budget_forcing(synthesis_root=output / "02_synthesis",
            synthesis=synthesis, gemma=gemma, qwen=qwen)
        status.update(terminal_proof=synthesis["terminal_proof"], terminal_proof_sha256=synthesis["terminal_proof_sha256"],
            synthesis_result=synthesis, synthesis_budget_forcing=forcing)
        if skill_launcher is not None:
            status.update(stage="independent_strict_score")
            rewrite.write_record(output / "status.json", status)
            import sys
            command = [sys.executable, str(skill_launcher.resolve()), "--proof-task",
                f"{task.problem_id}:author_guided={synthesis['terminal_proof']}",
                "--output-dir", str(output / "strict_score"), "--workers", "1"]
            code = experiment.wait_process(command, output / "strict_score.log", output / "status.json", status,
                timeout_seconds=7800)
            if code != 0:
                raise RuntimeError("isolated strict grading failed")
            score, detail = experiment.score_from_summary(output / "strict_score")
            if detail.get("proof_sha256") != synthesis["terminal_proof_sha256"] or detail.get("problem_id") != task.problem_id:
                raise ValueError("strict score does not bind the synthesized proof")
            status.update(strict_score=score, strict_result=detail)
        status.update(state="completed", stage="finished")
    except Exception as error:
        status.update(state="failed_closed", error=f"{type(error).__name__}: {error}")
    rewrite.write_record(output / "status.json", status)
    rewrite.write_record(output / "result.json", status)
    return status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-run", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--master-seed", type=int, required=True)
    parser.add_argument("--strict-skill-launcher", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.source_run, args.output_dir, master_seed=args.master_seed, skill_launcher=args.strict_skill_launcher)
    print(json.dumps({key: result.get(key) for key in ("state", "stage", "strict_score", "terminal_proof", "error")}), flush=True)
    return 0 if result["state"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
