"""Synthesize from a lossless rendering when compact-certificate authorship fails.

Reuse only the author's untrusted semantic notes, never its rejected algebra.
The mathematical evidence is the independently checked saved witness itself.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import traceback

from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906.contracts import SynthesisAdapter
from . import pipeline, protocol
from .resume_saved import load_context
from .saved_witness import SavedWitnessProvider


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection-run", type=Path, required=True)
    parser.add_argument("--previous-packaging-run", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--master-seed", type=int, required=True)
    args = parser.parse_args()
    previous = args.previous_packaging_run.resolve()
    prior_manifest = json.loads((previous / "manifest.json").read_text(encoding="utf-8"))
    if prior_manifest.get("state") != "failed_closed":
        raise ValueError("fallback is allowed only after the compact author run failed closed")
    stage = pipeline.CERTIFICATE_AUTHOR_STAGE
    attempts = sorted(path for path in (previous / "01_certificate_author").glob("attempt_*")
                      if (path / f"{stage}.raw_response.json").is_file()
                      and (path / f"{stage}.budget_forcing.json").is_file())
    if not attempts:
        raise ValueError("no prior model-authored semantic record")
    latest = attempts[-1]
    response_path = latest / f"{stage}.raw_response.json"
    response = json.loads(response_path.read_text(encoding="utf-8"))
    text = response["choices"][0]["message"]["content"].strip()
    sections = protocol.mdp.exact_sections(text, ["Certificate Semantics", "Certificate Program"])
    semantics = protocol._parse_semantics(sections["Certificate Semantics"])
    task, context = load_context(args.selection_run)
    if semantics["required_conclusion"].replace(" ", "") not in task.theorem.replace(" ", ""):
        raise ValueError("model-authored conclusion is not the saved theorem conclusion")
    role_record = prior_manifest["certificate_author"]
    metadata = json.loads((latest / f"{stage}.metadata.json").read_text(encoding="utf-8"))
    forcing = json.loads((latest / f"{stage}.budget_forcing.json").read_text(encoding="utf-8"))
    parts = latest.name.split("_")
    pipeline.validate_markdown_budget_forcing(
        {"attempt": int(parts[1]), "cap": int(parts[3]), "request_timeout_sec": 600,
         "metadata": {"v0257_budget_forcing": forcing}},
        expected_stage=stage, expected_model=role_record["model"], canonical_markdown=text,
    )
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    manifest = {
        "schema": "cognitive-well-v0324-saved-witness-synthesis-v1",
        "state": "running", "problem_id": task.problem_id,
        "previous_packaging_run": str(previous),
        "untrusted_semantic_notes_source_sha256": pipeline.base.sha256_file(response_path),
        "untrusted_semantic_notes_source": str(response_path),
        "semantic_note_reuse_policy": "latest_completed_budget_forced_author_response_no_mathematical_selection",
        "rejected_model_algebra_used": False,
        "mathematical_source": "already_certified_saved_witness",
        "new_author_calls": 0, "new_formalization_calls": 0, "new_singular_calls": 0,
        "manual_mathematical_content": False,
    }
    pipeline.base.write_json(output / "manifest.json", manifest)
    try:
        print("Rendering and exactly checking the saved witness presentation.", flush=True)
        provider = SavedWitnessProvider(context)
        pipeline.base.write_text(output / "saved_lemma.md", provider.markdown)
        pipeline.base.write_json(output / "saved_lemma_verification.json", provider.verification)
        pipeline.base.write_json(output / "untrusted_semantic_notes.json", semantics)
        print(f"Saved lemma ready: {provider.verification['markdown_characters']} characters. Starting whole-proof synthesis.", flush=True)
        gemma = pipeline.base.Role(**role_record)
        qwen = pipeline.base.Role(**prior_manifest["proof_auditor"])
        adapter = SynthesisAdapter("generic_saved_witness_" + context.certificate_id,
                                  task, provider, pipeline._generic_contract({"semantics": semantics}, conclusion_label="the target T"))
        synthesis = pipeline.synthesis_pipeline.run(
            adapter=adapter, output_dir=output / "02_proof_synthesis", gemma=gemma, qwen=qwen,
            master_seed=args.master_seed,
            model_call=pipeline._with_user_semantics(pipeline._mandatory_budget_forced_model_call, semantics))
        records = pipeline._verify_synthesis_budget_forcing(
            synthesis_root=output / "02_proof_synthesis", synthesis=synthesis, gemma=gemma, qwen=qwen)
        result = {**manifest, "state": "completed", "synthesis_result": synthesis,
                  "synthesis_budget_forcing": records,
                  "terminal_proof": synthesis["terminal_proof"],
                  "terminal_proof_sha256": synthesis["terminal_proof_sha256"]}
        pipeline.base.write_json(output / "result.json", result)
        pipeline.base.write_json(output / "manifest.json", result)
        print(f"Proof ready: {result['terminal_proof']}", flush=True)
    except Exception as error:
        failure = {**manifest, "state": "failed_closed", "error": f"{type(error).__name__}: {error}",
                   "traceback": traceback.format_exc()}
        pipeline.base.write_json(output / "manifest.json", failure)
        pipeline.base.write_json(output / "failure.json", failure)
        raise


if __name__ == "__main__":
    main()
