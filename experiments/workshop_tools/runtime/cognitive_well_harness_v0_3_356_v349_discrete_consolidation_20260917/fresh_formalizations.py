"""Fresh samples only for parser-failed arms, retaining this case's tool request.

The old drafts and parser feedback are never supplied to the new first prompt.
Successful arms and any running exact computations are read-only and untouched.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from . import pipeline, rewrite

acquisition = rewrite.acquisition


def load_source(source, *, require_failed_arms=True):
    root = source / "01_acquisition"
    manifest = acquisition._read_json(root / "manifest.json")
    problem = acquisition.v0220.load_problem(Path(manifest["problem_file"]))
    proof = (root / "input/resolver1_proof.md").read_text(encoding="utf-8").strip()
    if (pipeline.base.sha256_file(problem.source_path) != manifest["problem_file_sha256"]
            or pipeline.base.sha256_text(proof) != manifest["resolver1_proof_sha256"]
            or (root / "input/original_theorem.md").read_text(encoding="utf-8").strip() != problem.statement):
        raise ValueError("source theorem/proof binding mismatch")
    detection = acquisition.protocol.parse_detection((root / "01_detection/detection.md").read_text(encoding="utf-8").strip())
    matcher = acquisition.base._parse_matcher((root / "02_matcher/matcher.md").read_text(encoding="utf-8").strip(),
        detection["desired_exact_fact"], tuple(manifest["matcher_allowed_operations"]))
    if not detection["call_requested"] or not matcher["call_requested"] or matcher["operation"] != pipeline.exact_tools.IDEAL_OPERATION:
        raise ValueError("source does not request the supported exact operation")
    schedule = [(label, temperature) for label, temperature in acquisition.FORMALIZATION_SCHEDULE
        if (root / "03_guarded_formalizations" / label / "failure.json").is_file()
        and not (root / "03_guarded_formalizations" / label / "formalization_raw.md").is_file()]
    if require_failed_arms and not schedule:
        raise ValueError("no parser-failed arms eligible for fresh generation")
    return root, manifest, problem, proof, detection, matcher, schedule


def run(source, output, *, master_seed):
    rewrite.assert_generic_boundary()
    source, output = source.resolve(), output.resolve()
    root, manifest, problem, proof, detection, matcher, schedule = load_source(source)
    output.mkdir(parents=True, exist_ok=False)
    prompt = acquisition.formalization_prompt(problem, proof, detection, matcher)
    binding_paths = {"theorem": root / "input/original_theorem.md", "proof": root / "input/resolver1_proof.md",
                     "detection": root / "01_detection/detection.md", "matcher": root / "02_matcher/matcher.md"}
    binding = {label: pipeline.base.sha256_file(path) for label, path in binding_paths.items()}
    prior_stages = len(acquisition._read_json(source / "model_budget.json")["calls"])
    if prior_stages + len(schedule) > 24:
        raise ValueError("fresh samples would exceed the case model-stage budget")
    calls = rewrite.BudgetedCalls(output / "model_budget.json", max_stages=len(schedule))
    status = {"schema": "generic-fresh-parser-failed-arms-v1", "state": "running", "source_run": str(source),
              "source_bindings": binding, "master_seed": master_seed, "prior_model_stages": prior_stages,
              "fresh_schedule": [{"label": label, "temperature": temperature} for label, temperature in schedule],
              "rejected_drafts_supplied": False, "prior_parser_feedback_supplied": False,
              "detection_and_matching_reused": True, "successful_arms_untouched": True,
              "prompt_sha256": pipeline.base.sha256_text(prompt), "rows": []}
    rewrite.write_record(output / "status.json", status)
    pipeline.base.write_text(output / "fresh_prompt.md", prompt)

    def formalize(label, temperature):
        target = output / "03_guarded_formalizations" / label
        role = pipeline.base.Role(manifest["roles"]["formalizer"]["endpoint"],
            manifest["roles"]["formalizer"]["model"], temperature, manifest["roles"]["formalizer"]["reasoning_effort"])
        try:
            raw, parsed, call = calls(role=role, system_prompt=acquisition.FORMALIZER_SYSTEM, user_prompt=prompt,
                destination=target / "model", stage="guarded_polynomial_formalization",
                master_seed=pipeline.base.stable_seed(master_seed, f"formalizer:{label}"),
                parser=acquisition.parse_guarded_formalization, request_timeout_sec=600)
            canonical = parsed["normalized_markdown"]
            profile = pipeline.exact_tools.ideal_request_profile(parsed["arguments"])
            pipeline.base.write_text(target / "formalization_raw.md", raw)
            pipeline.base.write_text(target / "formalization.md", canonical)
            rewrite.write_record(target / "guard_program.json", parsed["guard_program"])
            rewrite.write_record(target / "surface_normalization.json", parsed["surface_normalization"])
            rewrite.write_record(target / "request_profile.json", profile)
            rewrite.write_record(target / "producer_call.json", call)
            return {"label": label, "temperature": temperature, "state": "compiled", "request_profile": profile}
        except Exception as error:
            result = {"label": label, "temperature": temperature, "state": "compiler_failed",
                      "error": f"{type(error).__name__}: {error}"}
            rewrite.write_record(target / "failure.json", result)
            return result

    with ThreadPoolExecutor(max_workers=len(schedule)) as executor:
        futures = [executor.submit(formalize, label, temperature) for label, temperature in schedule]
        for future in as_completed(futures):
            status["rows"].append(future.result())
            status["rows"].sort(key=lambda row: next(i for i, pair in enumerate(schedule) if pair[0] == row["label"]))
            rewrite.write_record(output / "status.json", status)
    if binding != {label: pipeline.base.sha256_file(path) for label, path in binding_paths.items()}:
        raise ValueError("source inputs changed during fresh generation")
    status.update(state="completed", compiled_labels=[row["label"] for row in status["rows"] if row["state"] == "compiled"])
    rewrite.write_record(output / "status.json", status)
    rewrite.write_record(output / "result.json", status)
    return status


def resume_checks(source, fresh_root, output, *, master_seed):
    """Continue every compiled fresh arm through the existing exact/synthesis path."""
    rewrite.assert_generic_boundary()
    source, fresh_root, output = source.resolve(), fresh_root.resolve(), output.resolve()
    root, manifest, problem, proof, _, _, _ = load_source(source, require_failed_arms=False)
    if acquisition._read_json(source / "result.json").get("state") != "failed_closed":
        raise ValueError("fresh-arm continuation requires a stopped original case")
    fresh = acquisition._read_json(fresh_root / "result.json")
    original_stages = len(acquisition._read_json(source / "model_budget.json")["calls"])
    fresh_stages = len(acquisition._read_json(fresh_root / "model_budget.json")["calls"])
    if fresh.get("prior_model_stages") != original_stages:
        raise ValueError("fresh portfolio ancestor budget changed")
    prior_stages = original_stages + fresh_stages
    if prior_stages >= 24:
        raise ValueError("the original case model-stage budget is exhausted")
    # Run the existing strict loader before creating any live run directory.
    _, _, _, _, rows, binding = acquisition.load_resumed_formalizations(
        resume_root=root, problem=problem, proof=proof,
        allowed_matcher_operations=tuple(manifest["matcher_allowed_operations"]),
        fresh_portfolio_root=fresh_root)
    output.mkdir(parents=True, exist_ok=False)
    calls = rewrite.BudgetedCalls(output / "model_budget.json", max_stages=24-prior_stages)
    gemma = pipeline.base.Role(manifest["roles"]["formalizer"]["endpoint"],
        manifest["roles"]["formalizer"]["model"], 0.2, "max")
    qwen = pipeline.base.Role(manifest["roles"]["post_singular_auditor"]["endpoint"],
        manifest["roles"]["post_singular_auditor"]["model"], 0.1, None)
    status = {"schema": "generic-fresh-arm-exact-continuation-v1", "state": "running",
        "stage": "resumed_exact_checks", "problem_id": problem.problem_id, "source_run": str(source),
        "fresh_portfolio_root": str(fresh_root), "compiled_labels": [row["label"] for row in rows],
        "prior_model_stages": prior_stages, "maximum_extra_model_stages": 24-prior_stages,
        "new_detection_calls": 0, "new_matcher_calls": 0, "new_formalization_calls": 0,
        "laurent_preprocess_timeout_sec": 600, "singular_timeout_sec": 600,
        "fresh_detection": False, "fresh_detection_origin": str(root), "preloaded_certificate": False,
        "resume_binding_sha256": binding["binding_sha256"]}
    rewrite.write_record(output / "status.json", status)
    def synthesize(**promoted):
        return rewrite.synthesize_promoted(output_dir=output, status=status, calls=calls,
            gemma=gemma, qwen=qwen, master_seed=master_seed, **promoted)
    try:
        result = acquisition.run_after_resolver1(problem_file=problem.source_path,
            proof_file=root / "input/resolver1_proof.md", output_dir=output / "01_acquisition",
            detector=qwen, compiler=gemma, auditor=qwen, rewriter=gemma, master_seed=master_seed,
            resume_formalizations_root=root, resume_fresh_portfolio_root=fresh_root,
            excluded_matcher_operations=tuple(manifest["matcher_excluded_operations"]),
            laurent_preprocess_timeout_sec=600, singular_timeout_sec=600,
            on_promoted=synthesize, model_call=calls, compiler_model_call=calls)
        status.update(result, stage="finished")
    except Exception as error:
        status.update(state="failed_closed", stage="finished", error=f"{type(error).__name__}: {error}")
    rewrite.write_record(output / "status.json", status)
    rewrite.write_record(output / "result.json", status)
    return status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-run", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--master-seed", type=int, required=True)
    parser.add_argument("--resume-checks-from", type=Path)
    args = parser.parse_args()
    if args.resume_checks_from:
        result = resume_checks(args.source_run, args.resume_checks_from, args.output_dir, master_seed=args.master_seed)
        print(result["state"], result.get("error", ""), flush=True)
    else:
        result = run(args.source_run, args.output_dir, master_seed=args.master_seed)
        print("Fresh parser-valid labels:", result["compiled_labels"], flush=True)


if __name__ == "__main__":
    main()
