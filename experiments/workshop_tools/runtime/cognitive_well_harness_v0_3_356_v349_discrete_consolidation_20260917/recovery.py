"""One semantic reassessment and, if needed, one model-authored repair.

Reuse only this case's detector, matcher, and rejected formalization. The model
receives no exact outcome or gold reference. Every repaired request starts new
Laurent/Singular/lift/audit gates. A reassessment that accepts the unchanged input
may replay that same case's existing certificate, never another case's witness.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import pipeline, rewrite

acquisition = rewrite.acquisition

REASSESSMENT_SYSTEM = acquisition.POST_SINGULAR_AUDITOR_SYSTEM.replace(
    "Emit only the required Decision, Checks, and Issues sections.",
    "Emit the required Decision, Checks, and Issues sections, followed by # Reassessment.",
) + """

Reassess one earlier semantic rejection. Treat the earlier audit as untrusted
feedback, not as authority or a request to change your verdict. Inspect the actual
typed expressions, including all recorded divisions, rather than relying on the
earlier label or paraphrase. In Reassessment, briefly explain whether the issue
was valid, mislabeled, or mistaken. If accepting a disputed nonzero condition,
give its derivation from the theorem and account for possible zero cases. Do not
repair the formalization or assume a tool result. Output Markdown only."""


def parse_reassessment(text):
    sections = acquisition.mdp.exact_sections(text, ["Decision", "Checks", "Issues", "Reassessment"])
    rationale = sections["Reassessment"].strip()
    if not rationale or rationale == "NONE" or len(rationale) > 8000:
        raise ValueError("semantic reassessment requires a bounded explicit rationale")
    canonical = "\n\n".join(f"# {name}\n\n{sections[name]}" for name in ("Decision", "Checks", "Issues"))
    return {"audit": acquisition.parse_post_singular_audit(canonical),
            "audit_markdown": canonical, "rationale": rationale}


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def source_binding_paths(source, label):
    root = source / "01_acquisition"
    formal = root / "03_guarded_formalizations" / label
    audit = root / "06_post_singular_audits" / label
    return {"source_result": source / "result.json", "manifest": root / "manifest.json",
        "detection": root / "01_detection/detection.md", "matcher": root / "02_matcher/matcher.md",
        "formalization": formal / "formalization.md", "formalization_raw": formal / "formalization_raw.md",
        "audit": audit / "audit.md", "audit_result": audit / "result.json"}


def eligible_rejections(source):
    root = source / "01_acquisition"
    selected = []
    for label, _ in acquisition.FORMALIZATION_SCHEDULE:
        result_path = root / "06_post_singular_audits" / label / "result.json"
        route_path = root / "05_direct_laurent_routes" / label / "route_state.json"
        if not result_path.is_file() or not route_path.is_file():
            continue
        result, route = read(result_path), read(route_path)
        if result.get("state") != "rejected" or route.get("state") != "singular_proved":
            continue
        audit_path = result_path.parent / "audit.md"
        audit = acquisition.parse_post_singular_audit(audit_path.read_text(encoding="utf-8").strip())
        formal_path = root / "03_guarded_formalizations" / label / "formalization.md"
        formal_text = formal_path.read_text(encoding="utf-8").strip()
        if (audit["accepted"] or audit != result["audit"]
                or result.get("exact_result_supplied") is not False
                or result.get("laurent_outcome_supplied") is not False
                or result.get("formalization_sha256") != pipeline.base.sha256_text(formal_text)):
            raise ValueError("rejected semantic audit failed source binding")
        selected.append(label)
    return selected


def repair_prompt(problem, proof, detection_text, matcher_text, formalization_text, audit_text):
    return f"""# Original Theorem

{problem.statement}

# Original Proof

{proof}

# Frozen Detection

{detection_text}

# Frozen Matcher

{matcher_text}

# Rejected Formalization

{formalization_text}

# Independent Semantic Feedback

{audit_text}

# Repair Task

Repair this formalization against the original theorem and proof. The feedback
may itself contain mistakes or mislabel a record: independently check all affected
definitions, equations, guards, and recorded divisions. Do not change the detected
obligation or assume the desired result. Make only mathematically justified
changes; do not add assumptions merely to make a computation succeed. Return the
complete three-section Markdown formalization, including the full typed Guard
Program and Tool Arguments. No JSON or discussion outside those sections."""


def certify(formalization, root, label):
    """Fresh exact gates with the existing 600/600 limits and no old witness."""
    arguments, guards = formalization["arguments"], formalization["guard_program"]
    engine = acquisition.laurent
    preview = engine.bounded_preview_only(source_arguments=arguments, candidate_arguments=arguments,
        guard_program=guards, output_dir=root / "01_preview", timeout_sec=600, memory_mb=8192)
    expected = {"expected_transform_sha256": str(preview["transform_sha256"]),
                "expected_derived_profile": preview["derived_profile"],
                "expected_structural_preview_sha256": str(preview["preview_file_sha256"])}
    screen = engine.bounded_screen_persisted_preview_target(source_arguments=arguments, candidate_arguments=arguments,
        guard_program=guards, preview_output_dir=root / "01_preview", output_dir=root / "02_target_screen",
        singular_binary=acquisition.SINGULAR_BINARY, timeout_sec=600, memory_mb=8192, **expected)
    route = {"label": label, "state": "singular_not_proved", "preview": preview, "screen": screen}
    if screen["state"] != "proved":
        rewrite.write_record(root / "route_state.json", route)
        return route
    validation = {"decision": "ACCEPT", "identity": True,
        "source_arguments_sha256": pipeline.exact_tools.stable_hash(arguments),
        "candidate_arguments_sha256": pipeline.exact_tools.stable_hash(arguments),
        "guard_program_sha256": pipeline.exact_tools.stable_hash(guards)}
    prepared = engine.bounded_preprocess_only(source_arguments=arguments, candidate_arguments=arguments,
        guard_program=guards, exact_transformation_validation=validation, output_dir=root / "03_laurent_lift",
        timeout_sec=600, memory_mb=8192, **expected)
    replay = engine.verify_exported_membership_identity(output_dir=root / "02_target_screen", result=screen)
    if replay.get("verified") is not True:
        raise ValueError("repaired multiplier identity failed exact replay")
    text = acquisition.render_exact_evidence(root, screen, prepared)
    pipeline.base.write_text(root / "04_exact_evidence.md", text)
    route.update(state="singular_proved", prepared=prepared, identity_replay=replay)
    rewrite.write_record(root / "route_state.json", route)
    return route


def run(source, output, *, master_seed):
    rewrite.assert_generic_boundary()
    source, output = source.resolve(), output.resolve()
    prior = read(source / "result.json")
    if prior.get("state") != "failed_closed" or prior.get("preloaded_certificate") is not False:
        raise ValueError("semantic recovery requires a failed fresh acquisition")
    root = source / "01_acquisition"
    manifest = read(root / "manifest.json")
    if manifest.get("resume_formalizations_root"):
        raise ValueError("recovery must trace to this case's fresh detection")
    problem_file, proof_file = Path(prior["problem_file"]), Path(prior["proof_file"])
    if pipeline.base.sha256_file(problem_file) != prior["problem_file_sha256"] or pipeline.base.sha256_file(proof_file) != prior["input_proof_sha256"]:
        raise ValueError("original theorem or Resolver proof changed")
    problem = acquisition.v0220.load_problem(problem_file)
    proof = proof_file.read_text(encoding="utf-8").strip()
    if (root / "input/original_theorem.md").read_text(encoding="utf-8").strip() != problem.statement.strip() or (root / "input/resolver1_proof.md").read_text(encoding="utf-8").strip() != proof:
        raise ValueError("saved acquisition belongs to a different theorem or proof")
    labels = eligible_rejections(source)
    if not labels:
        raise ValueError("no source-bound rejected formalization is eligible for semantic repair")
    label = labels[0]
    original_calls = len(read(source / "model_budget.json")["calls"])
    remaining = min(9, 24 - original_calls)
    if remaining < 5:
        raise ValueError("insufficient remaining case budget for repair, audit, and synthesis")
    detection_path, matcher_path = root / "01_detection/detection.md", root / "02_matcher/matcher.md"
    detection_text, matcher_text = detection_path.read_text().strip(), matcher_path.read_text().strip()
    detection = acquisition.protocol.parse_detection(detection_text)
    matcher = pipeline.base._parse_matcher(matcher_text, detection["desired_exact_fact"], tuple(manifest["matcher_allowed_operations"]))
    if matcher["operation"] != pipeline.exact_tools.IDEAL_OPERATION:
        raise ValueError("recovery may not change the matched operation")
    formal_path = root / "03_guarded_formalizations" / label / "formalization.md"
    audit_path = root / "06_post_singular_audits" / label / "audit.md"
    binding_paths = source_binding_paths(source, label)
    frozen = {key: pipeline.base.sha256_file(path) for key, path in binding_paths.items()}
    output.mkdir(parents=True, exist_ok=False)
    calls = rewrite.BudgetedCalls(output / "model_budget.json", max_stages=remaining)
    status = {"schema": "generic-bounded-semantic-recovery-v1", "state": "running", "stage": "qwen_semantic_reassessment",
        "problem_id": problem.problem_id, "source_rewrite_run": str(source), "selected_source_label": label,
        "source_hashes": frozen, "selection_policy": "first_rejected_in_frozen_schedule",
        "new_detection_calls": 0, "new_matcher_calls": 0, "maximum_semantic_repairs": 1,
        "maximum_semantic_reassessments": 1,
        "prior_model_stages": original_calls, "maximum_extra_model_stages": remaining,
        "preloaded_certificate": False, "fresh_detection": True, "fresh_detection_origin": str(root)}
    rewrite.write_record(output / "status.json", status)
    destination = output / "01_acquisition"
    for relative, text in (("input/original_theorem.md", problem.statement), ("input/resolver1_proof.md", proof),
                           ("01_detection/detection.md", detection_text), ("02_matcher/matcher.md", matcher_text)):
        pipeline.base.write_text(destination / relative, text)
    gemma = pipeline.base.Role("http://127.0.0.1:8030/v1", pipeline.base.DEFAULT_GEMMA_MODEL, 0.2, "max")
    qwen = pipeline.base.Role("http://127.0.0.1:8027/v1", pipeline.base.DEFAULT_QWEN_MODEL, 0.1, None)
    repaired_label = label + "repair1"
    formal_root = destination / "03_guarded_formalizations" / repaired_label
    try:
        raw_review, review, review_call = calls(role=qwen, system_prompt=REASSESSMENT_SYSTEM,
            user_prompt=acquisition.post_singular_audit_prompt(problem=problem, proof=proof,
                detection_text=detection_text, matcher_text=matcher_text, formalization_text=formal_path.read_text().strip())
                + "\n\n# Earlier Semantic Audit (untrusted)\n\n" + audit_path.read_text().strip(),
            destination=output / "00_reassessment/model", stage="guarded_formalization_semantic_reassessment",
            master_seed=master_seed, parser=parse_reassessment, request_timeout_sec=600)
        pipeline.base.write_text(output / "00_reassessment/reassessment.md", raw_review)
        rewrite.write_record(output / "00_reassessment/result.json", {**review, "call": review_call,
            "source_hashes": frozen, "exact_result_supplied": False, "laurent_outcome_supplied": False})
        if {key: pipeline.base.sha256_file(path) for key, path in binding_paths.items()} != frozen:
            raise ValueError("semantic reassessment inputs changed during generation")
        if review["audit"]["accepted"]:
            original_formal = acquisition.parse_guarded_formalization(formal_path.read_text().strip())
            copied_formal = destination / "03_guarded_formalizations" / label
            pipeline.base.write_text(copied_formal / "formalization.md", formal_path.read_text().strip())
            pipeline.base.write_text(copied_formal / "formalization_raw.md", binding_paths["formalization_raw"].read_text().strip())
            accepted_root = destination / "06_post_singular_audits" / label
            pipeline.base.write_text(accepted_root / "audit.md", review["audit_markdown"])
            rewrite.write_record(accepted_root / "result.json", {"state": "accepted", "audit": review["audit"],
                "reassessment": review["rationale"], "call": review_call,
                "formalization_sha256": pipeline.base.sha256_text(formal_path.read_text().strip()),
                "exact_result_supplied": False, "laurent_outcome_supplied": False})
            original_route_root = root / "05_direct_laurent_routes" / label
            original_route = read(original_route_root / "route_state.json")
            selection = {"selected_label": label, "policy": "one_explicit_semantic_reassessment_of_unchanged_input",
                "selected_route_state_sha256": pipeline.base.sha256_file(original_route_root / "route_state.json"),
                "selected_audit_result_sha256": pipeline.base.sha256_file(accepted_root / "result.json")}
            rewrite.write_record(destination / "07_selection/selection.json", selection)
            status.update(stage="replay_same_case_certificate", reused_case_certificate=True,
                          new_formalization_calls=0, new_singular_calls=0)
            rewrite.write_record(output / "status.json", status)
            result = rewrite.synthesize_promoted(output_dir=output, status=status, calls=calls, gemma=gemma, qwen=qwen,
                master_seed=master_seed, problem=problem, proof=proof, formalization=original_formal,
                route=original_route, route_root=original_route_root, acquisition_root=destination,
                audit_root=accepted_root, matcher=matcher, selection=selection)
            status.update(result, stage="finished")
            rewrite.write_record(output / "status.json", status)
            rewrite.write_record(output / "result.json", status)
            return status
        status.update(stage="model_semantic_repair")
        rewrite.write_record(output / "status.json", status)
        raw, parsed, call = calls(role=gemma, system_prompt=acquisition.FORMALIZER_SYSTEM,
            user_prompt=repair_prompt(problem, proof, detection_text, matcher_text, formal_path.read_text().strip(), raw_review),
            destination=formal_root / "model", stage="guarded_formalization_semantic_repair", master_seed=master_seed + 1,
            parser=acquisition.parse_guarded_formalization, request_timeout_sec=600)
        if {key: pipeline.base.sha256_file(path) for key, path in binding_paths.items()} != frozen:
            raise ValueError("semantic-repair inputs changed during generation")
        canonical = parsed["normalized_markdown"]
        pipeline.base.write_text(formal_root / "formalization_raw.md", raw)
        pipeline.base.write_text(formal_root / "formalization.md", canonical)
        rewrite.write_record(formal_root / "guard_program.json", parsed["guard_program"])
        rewrite.write_record(formal_root / "producer_call.json", call)
        rewrite.write_record(formal_root / "request_profile.json", pipeline.exact_tools.ideal_request_profile(parsed["arguments"]))
        status.update(stage="fresh_exact_validation")
        rewrite.write_record(output / "status.json", status)
        route_root = destination / "05_direct_laurent_routes" / repaired_label
        route = certify(parsed, route_root, repaired_label)
        if route["state"] != "singular_proved":
            raise RuntimeError("model-repaired formalization was not proved by the fresh exact check")
        status.update(stage="independent_semantic_reaudit")
        rewrite.write_record(output / "status.json", status)
        audit_root = destination / "06_post_singular_audits" / repaired_label
        text, audited, audit_call = calls(role=qwen, system_prompt=acquisition.POST_SINGULAR_AUDITOR_SYSTEM,
            user_prompt=acquisition.post_singular_audit_prompt(problem=problem, proof=proof, detection_text=detection_text,
                matcher_text=matcher_text, formalization_text=canonical), destination=audit_root / "model",
            stage="post_singular_guarded_formalization_audit", master_seed=master_seed + 1,
            parser=acquisition.parse_post_singular_audit, request_timeout_sec=600)
        pipeline.base.write_text(audit_root / "audit.md", text)
        rewrite.write_record(audit_root / "result.json", {"state": "accepted" if audited["accepted"] else "rejected",
            "audit": audited, "call": audit_call, "formalization_sha256": pipeline.base.sha256_text(canonical),
            "exact_result_supplied": False, "laurent_outcome_supplied": False})
        if not audited["accepted"]:
            raise RuntimeError("model-repaired formalization was rejected by independent semantic re-audit")
        selection = {"selected_label": repaired_label, "policy": "one_model_repair_then_all_original_gates",
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


def resume_accepted_synthesis(source, output, *, master_seed):
    """Resume a pre-synthesis rendering failure without another semantic vote.

    This narrow mechanical recovery preserves the original failed run and all
    model outputs. It cannot resample a rejected audit or restart failed synthesis.
    """
    from .certificate import validate_markdown_budget_forcing

    rewrite.assert_generic_boundary()
    source, output = source.resolve(), output.resolve()
    prior = read(source / "result.json")
    if (prior.get("state") != "failed_closed" or prior.get("stage") != "verified_certificate_rendering"
            or prior.get("reused_case_certificate") is not True or (source / "02_synthesis").exists()):
        raise ValueError("mechanical resume requires an accepted reassessment stopped before synthesis")
    label = prior["selected_label"]
    origin = Path(prior["source_rewrite_run"])
    bindings = source_binding_paths(origin, label)
    if {key: pipeline.base.sha256_file(path) for key, path in bindings.items()} != prior["source_hashes"]:
        raise ValueError("semantic recovery source binding changed")
    review_text = (source / "00_reassessment/reassessment.md").read_text().strip()
    review, persisted = parse_reassessment(review_text), read(source / "00_reassessment/result.json")
    if (not review["audit"]["accepted"] or any(persisted.get(key) != value for key, value in review.items())
            or persisted.get("source_hashes") != prior["source_hashes"]
            or persisted.get("exact_result_supplied") is not False or persisted.get("laurent_outcome_supplied") is not False):
        raise ValueError("saved reassessment is not a bound exact-blind acceptance")
    validate_markdown_budget_forcing(persisted["call"], expected_stage="guarded_formalization_semantic_reassessment",
        expected_model=pipeline.base.DEFAULT_QWEN_MODEL, canonical_markdown=review_text)
    budget = read(source / "model_budget.json")
    if len(budget["calls"]) != 1 or budget["calls"][0]["stage"] != "guarded_formalization_semantic_reassessment" or budget["calls"][0]["state"] != "completed":
        raise ValueError("mechanical resume may not repeat other model stages")
    consumed = prior["prior_model_stages"] + len(budget["calls"])
    remaining = min(prior["maximum_extra_model_stages"] - len(budget["calls"]), 24 - consumed)
    if remaining < 6:
        raise ValueError("insufficient original budget for three synthesis/audit cycles")
    inputs = read(origin / "result.json")
    problem_file, proof_file = Path(inputs["problem_file"]), Path(inputs["proof_file"])
    if pipeline.base.sha256_file(problem_file) != inputs["problem_file_sha256"] or pipeline.base.sha256_file(proof_file) != inputs["input_proof_sha256"]:
        raise ValueError("original theorem or proof changed")
    problem, proof = acquisition.v0220.load_problem(problem_file), proof_file.read_text().strip()
    acquisition_root = source / "01_acquisition"
    formal_root = acquisition_root / "03_guarded_formalizations" / label
    for name in ("formalization.md", "formalization_raw.md"):
        if (formal_root / name).read_text().strip() != (bindings["formalization"].parent / name).read_text().strip():
            raise ValueError("accepted formalization differs from the original certified input")
    formal = acquisition.parse_guarded_formalization((formal_root / "formalization.md").read_text().strip())
    for relative, key in (("01_detection/detection.md", "detection"), ("02_matcher/matcher.md", "matcher")):
        if (acquisition_root / relative).read_text().strip() != bindings[key].read_text().strip():
            raise ValueError("saved detection or matcher changed")
    detection = acquisition.protocol.parse_detection(bindings["detection"].read_text().strip())
    matcher = pipeline.base._parse_matcher(bindings["matcher"].read_text().strip(), detection["desired_exact_fact"],
        tuple(read(bindings["manifest"])["matcher_allowed_operations"]))
    route_root = origin / "01_acquisition/05_direct_laurent_routes" / label
    audit_root = acquisition_root / "06_post_singular_audits" / label
    selection = read(acquisition_root / "07_selection/selection.json")
    if (selection["selected_label"] != label
            or selection["selected_route_state_sha256"] != pipeline.base.sha256_file(route_root / "route_state.json")
            or selection["selected_audit_result_sha256"] != pipeline.base.sha256_file(audit_root / "result.json")
            or (audit_root / "audit.md").read_text().strip() != review["audit_markdown"].strip()):
        raise ValueError("saved selection or accepted audit changed")
    output.mkdir(parents=True, exist_ok=False)
    status = {**prior, "state": "running", "stage": "verified_certificate_rendering",
        "mechanical_resume_source": str(source), "mechanical_resume_source_sha256": pipeline.base.sha256_file(source / "result.json"),
        "prior_model_stages": consumed, "maximum_extra_model_stages": remaining,
        "new_semantic_reassessments": 0, "new_formalization_calls": 0, "new_singular_calls": 0}
    status.pop("error", None)
    calls = rewrite.BudgetedCalls(output / "model_budget.json", max_stages=remaining)
    try:
        result = rewrite.synthesize_promoted(output_dir=output, status=status, calls=calls,
            gemma=pipeline.base.Role("http://127.0.0.1:8030/v1", pipeline.base.DEFAULT_GEMMA_MODEL, 0.2, "max"),
            qwen=pipeline.base.Role("http://127.0.0.1:8027/v1", pipeline.base.DEFAULT_QWEN_MODEL, 0.1, None),
            master_seed=master_seed, problem=problem, proof=proof, formalization=formal,
            route=read(route_root / "route_state.json"), route_root=route_root,
            acquisition_root=acquisition_root, audit_root=audit_root, matcher=matcher, selection=selection)
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
    parser.add_argument("--resume-accepted-synthesis", action="store_true")
    args = parser.parse_args()
    runner = resume_accepted_synthesis if args.resume_accepted_synthesis else run
    result = runner(args.source_run, args.output_dir, master_seed=args.master_seed)
    print(json.dumps(result), flush=True)
    return 0 if result["state"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
