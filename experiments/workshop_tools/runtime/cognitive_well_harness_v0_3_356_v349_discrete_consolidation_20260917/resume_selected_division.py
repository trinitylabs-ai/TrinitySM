"""Resume a selected division certificate stopped before its first rewrite call.

Reuse frozen model decisions, semantic admission, seed and model configuration.
Only replay the saved certificate; never repeat formalization or solver search.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, replace
from pathlib import Path

from . import proof_harness as harness, algebra_workflow as workflow
from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906 import tool_purpose


def run(source, output, *, proof_rewriter=None):
    source, output = source.resolve(), output.resolve()
    harness.rewrite.assert_generic_boundary()
    manifest = harness.resume.read(source / "manifest.json")
    if manifest.get("schema") != harness.SCHEMA:
        raise ValueError("source is not a packaged proof harness")
    saved_config = harness.Config.from_saved(manifest["config"])
    config = saved_config if proof_rewriter is None else replace(saved_config, proof_rewriter=proof_rewriter)
    config.validate()
    selected = harness.resume.read(source / "selection.json")
    request_path = Path(selected["request_path"]).resolve()
    sample = request_path.parents[4]
    if sample.parent != source / "02_formalizations":
        raise ValueError("selected request is outside the saved portfolio")
    state = harness.resume.read(sample / "status.json")
    expected = sample / "cycles" / f"cycle_{state['cycle']:02d}" / "03_execution/04_tool/request.json"
    if request_path != expected or state.get("state") != "failed_closed":
        raise ValueError("selected request is not the stopped sample checkpoint")
    old_root = request_path.parent / "division_rewrite"
    stopped = harness.resume.read(old_root / "02_synthesis/manifest.json")
    if (stopped.get("state") != "failed_closed" or stopped.get("cycles") != []
            or not stopped.get("error", "").startswith("ValueError: explicit update requires one unique ")
            or state.get("error") != stopped["error"]
            or any(old_root.rglob("*.prompt.txt"))):
        raise ValueError("recovery requires a source-anchor failure before any rewrite call")
    documents = harness.input_context.load_saved(source, manifest)
    _, admission, task, _, _, _ = workflow.source_context(request_path, documents)
    problem = harness.acquisition.v0220.load_problem(source / "input/problem.json")
    if (task.source_proof.strip() != (source / "input/source_proof.md").read_text().strip()
            or task.theorem.strip() != problem.statement.strip() or task.problem_id != problem.problem_id):
        raise ValueError("selected request binds another problem or proof")
    result_path = request_path.parent / "division/result.json"
    provider = workflow.DivisionProvider(request_path, result_path)
    # Fail before any inference if the generic locator still cannot find the span.
    marked = tool_purpose.explicit_update_source(task, provider.materialize())
    paths = [source / "manifest.json", source / "selection.json", sample / "status.json",
             old_root / "02_synthesis/manifest.json",
             *(source / name for name in manifest["input_artifacts"]),
             *provider.bundle.source_artifacts.values()]
    frozen = {str(path): harness.base.sha256_file(path) for path in paths}
    output.mkdir(parents=True, exist_ok=False)
    status = {"schema": "generic-selected-division-synthesis-resume-v1", "state": "running",
        "stage": "proof_synthesis", "source_run": str(source), "source_artifacts": frozen,
        "master_seed": state["master_seed"], "config": asdict(config), "admission": admission,
        "source_config": manifest["config"],
        "model_role_override": {} if proof_rewriter is None else {
            "proof_rewriter": {"from": saved_config.proof_rewriter, "to": config.proof_rewriter}},
        "proof_rewriter_model": config.proof_writer().model,
        "proof_rewriter_temperature": config.proof_writer().temperature,
        "new_detection_calls": 0, "new_matcher_calls": 0, "new_formalization_calls": 0,
        "new_semantic_audit_calls": 0, "new_solver_searches": 0, "certificate_replayed": True,
        "explicit_update_source_policy": tool_purpose.EXPLICIT_SOURCE_POLICY,
        "marked_source_sha256": harness.base.sha256_text(marked),
        "selected": {"request_path": str(request_path), "state": "running"}}
    harness.rewrite.write_record(output / "manifest.json", status)
    harness.rewrite.write_record(output / "status.json", status)
    try:
        result = workflow.rewrite_division(request_path, result_path, output / "division_rewrite",
            config=config, seed=state["master_seed"], documents=documents)
        if {path: harness.base.sha256_file(Path(path)) for path in frozen} != frozen:
            raise ValueError("frozen recovery inputs changed")
        status["selected"].update(state=result["state"], result=result)
    except Exception as error:
        status.update(error=f"{type(error).__name__}: {error}")
        status["selected"].update(state="failed_closed", result={"state": "failed_closed"})
    status["stage"] = "finished"
    return harness.publish(output, status)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-run", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--execute-models", action="store_true", required=True)
    parser.add_argument("--proof-rewriter", choices=("gemma", "qwen"),
        help="Explicitly override only the saved proof-writing model for every synthesis cycle")
    args = parser.parse_args()
    result = run(args.source_run, args.output_dir, proof_rewriter=args.proof_rewriter)
    print(f"{result['state']}: {result.get('outcome')}", flush=True)
    return int(result["state"] == "failed_closed")


if __name__ == "__main__":
    raise SystemExit(main())
