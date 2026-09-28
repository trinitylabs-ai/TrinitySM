"""Resume a mechanically interrupted, saved proved route before semantic audit.

No detection, matching, formalization, Laurent search, or Singular is repeated.
The unchanged certificate must replay before the existing audit/synthesis gates.
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from . import fresh_formalizations, pipeline, rewrite

acquisition = rewrite.acquisition


def eligible_routes(source):
    root = source / "01_acquisition"
    eligible = []
    for label, _ in acquisition.FORMALIZATION_SCHEDULE:
        route_root = root / "05_direct_laurent_routes" / label
        path = route_root / "route_state.json"
        if not path.is_file():
            continue
        route = acquisition._read_json(path)
        if (route.get("state") == "exact_failed_closed"
                and route.get("screen", {}).get("state") == "proved"
                and (route_root / "03_laurent_lift/prepared.json").is_file()
                and not (root / "06_post_singular_audits" / label).exists()):
            eligible.append(label)
    return eligible


def run(source, output, *, master_seed):
    rewrite.assert_generic_boundary()
    source, output = source.resolve(), output.resolve()
    prior = acquisition._read_json(source / "result.json")
    if prior.get("state") != "failed_closed":
        raise ValueError("source must be a stopped case, not a live worker")
    root, manifest, problem, proof, detection, matcher, _ = fresh_formalizations.load_source(source, require_failed_arms=False)
    labels = eligible_routes(source)
    if not labels:
        raise ValueError("no saved proved pre-audit route is eligible")
    label = labels[0]
    original_calls = len(acquisition._read_json(source / "model_budget.json")["calls"])
    remaining = 24-original_calls
    if remaining < 3:
        raise ValueError("insufficient remaining stage budget for audit and synthesis")
    output.mkdir(parents=True, exist_ok=False)
    destination = output / "01_acquisition"
    selected_source = root / "05_direct_laurent_routes" / label
    source_paths = [root / "input/original_theorem.md", root / "input/resolver1_proof.md",
        root / "01_detection/detection.md", root / "02_matcher/matcher.md",
        *sorted(p for p in (root / "03_guarded_formalizations" / label).rglob("*") if p.is_file()),
        *sorted(p for p in selected_source.rglob("*") if p.is_file())]
    frozen = {str(p.relative_to(root)): pipeline.base.sha256_file(p) for p in source_paths}
    for relative in ("input", "01_detection", "02_matcher", f"03_guarded_formalizations/{label}", f"05_direct_laurent_routes/{label}"):
        shutil.copytree(root / relative, destination / relative)
    rewrite.write_record(destination / "manifest.json", {**manifest, "state": "running", "mechanical_resume_source": str(source)})
    calls = rewrite.BudgetedCalls(output / "model_budget.json", max_stages=remaining)
    status = {"schema": "generic-saved-proved-route-resume-v1", "state": "running", "stage": "saved_identity_replay",
        "problem_id": problem.problem_id, "source_rewrite_run": str(source), "source_artifact_sha256": frozen,
        "selected_label": label, "selection_policy": "first_saved_proved_pre_audit_failure_in_frozen_schedule",
        "prior_model_stages": original_calls, "maximum_extra_model_stages": remaining,
        "fresh_detection": True, "fresh_detection_origin": str(root), "new_detection_calls": 0,
        "new_formalization_calls": 0, "new_singular_calls": 0, "preloaded_certificate": False,
        "reused_case_certificate": True, "problem_file": str(problem.source_path),
        "proof_file": prior["proof_file"], "problem_file_sha256": prior["problem_file_sha256"],
        "input_proof_sha256": prior["input_proof_sha256"]}
    rewrite.write_record(output / "status.json", status)
    try:
        formal_root = destination / "03_guarded_formalizations" / label
        parsed = acquisition.parse_guarded_formalization((formal_root / "formalization_raw.md").read_text().strip())
        canonical = (formal_root / "formalization.md").read_text().strip()
        if parsed["normalized_markdown"] != canonical:
            raise ValueError("saved formalization canonical binding changed")
        route_root = destination / "05_direct_laurent_routes" / label
        route = acquisition._read_json(route_root / "route_state.json")
        prepared_path = route_root / "03_laurent_lift/prepared.json"
        prepared = {**acquisition._read_json(prepared_path), "prepared_file_sha256": pipeline.base.sha256_file(prepared_path)}
        replay = acquisition.laurent.verify_exported_membership_identity(output_dir=route_root / "02_target_screen", result=route["screen"])
        route.update(state="singular_proved", prepared=prepared, identity_replay=replay)
        route.pop("error", None)
        pipeline.base.write_text(route_root / "04_exact_evidence.md", acquisition.render_exact_evidence(route_root, route["screen"], prepared))
        rewrite._verify_prepared_route(route_root, route, parsed)
        rewrite.write_record(route_root / "route_state.json", route)
        if frozen != {str(p.relative_to(root)): pipeline.base.sha256_file(p) for p in source_paths}:
            raise ValueError("original saved artifacts changed during replay")
        qwen = pipeline.base.Role(manifest["roles"]["post_singular_auditor"]["endpoint"], manifest["roles"]["post_singular_auditor"]["model"], 0.1, None)
        gemma = pipeline.base.Role(manifest["roles"]["formalizer"]["endpoint"], manifest["roles"]["formalizer"]["model"], 0.2, "max")
        status.update(stage="independent_semantic_audit")
        rewrite.write_record(output / "status.json", status)
        audit_root = destination / "06_post_singular_audits" / label
        text, audit, call = calls(role=qwen, system_prompt=acquisition.POST_SINGULAR_AUDITOR_SYSTEM,
            user_prompt=acquisition.post_singular_audit_prompt(problem=problem, proof=proof,
                detection_text=(destination / "01_detection/detection.md").read_text().strip(),
                matcher_text=(destination / "02_matcher/matcher.md").read_text().strip(), formalization_text=canonical),
            destination=audit_root / "model", stage="post_singular_guarded_formalization_audit",
            master_seed=master_seed, parser=acquisition.parse_post_singular_audit, request_timeout_sec=600)
        pipeline.base.write_text(audit_root / "audit.md", text)
        rewrite.write_record(audit_root / "result.json", {"state": "accepted" if audit["accepted"] else "rejected",
            "audit": audit, "call": call, "formalization_sha256": pipeline.base.sha256_text(canonical),
            "exact_result_supplied": False, "laurent_outcome_supplied": False})
        if not audit["accepted"]:
            raise RuntimeError("independent semantic audit rejected the unchanged formalization")
        selection = {"selected_label": label, "policy": status["selection_policy"],
            "selected_route_state_sha256": pipeline.base.sha256_file(route_root / "route_state.json"),
            "selected_audit_result_sha256": pipeline.base.sha256_file(audit_root / "result.json")}
        rewrite.write_record(destination / "07_selection/selection.json", selection)
        result = rewrite.synthesize_promoted(output_dir=output, status=status, calls=calls, gemma=gemma, qwen=qwen,
            master_seed=master_seed, problem=problem, proof=proof, formalization=parsed, route=route,
            route_root=route_root, acquisition_root=destination, audit_root=audit_root, matcher=matcher, selection=selection)
        status.update(result, stage="finished")
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
    args = parser.parse_args()
    result = run(args.source_run, args.output_dir, master_seed=args.master_seed)
    print(result["state"], result.get("error", ""), flush=True)


if __name__ == "__main__":
    main()
