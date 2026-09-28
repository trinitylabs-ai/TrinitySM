"""Isolated raw-proof block repair, one Qwen audit, and one conditional resolve."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import sys
import time
from urllib.parse import urlsplit

from harnesses.post_c3_completion import worker as legacy
from . import blocks, policy, prompts
from . import strategy_config

frozen = legacy.frozen
IntegrityError = legacy.IntegrityError
require = legacy.require
CANDIDATES = legacy.CANDIDATES
EXPERIMENT = "block_local_completion_v1"
PIPELINE_CONFIG = {"neighbor_blocks": 1, "max_audit_passes": 1, "max_resolve_passes": 1}
STAGES = {
    "lazy_check": r"lazy_check_attempt[0-9]+(?:_cap_continuation)?",
    "expansion": r"lazy_in_place_resolve_attempt[0-9]+(?:_cap_continuation)?",
    "audit": r"post_block_audit_cap_[0-9]+",
    "resolve": r"post_block_resolve_attempt[0-9]+(?:_cap_continuation)?",
}


def validate_job(path, *, strategy="block"):
    from . import inputs
    path = frozen.checked_path(str(Path(path).absolute()))
    raw = path.read_bytes()
    job = json.loads(raw)
    require(isinstance(job, dict) and job.get("schema") == "block-local-job-v1"
            and job.get("experiment") == EXPERIMENT, "Expected an independent block-local job")
    require(job.get("source_arm") == "raw"
            and job.get("processing_scope") == "all_saved_raw_proofs", "Only saved raw proofs are supported")
    require(job.get("strategy") == strategy, "Worker strategy differs from job")
    require(job.get("pipeline_config") == strategy_config(strategy)
            and all(type(v) is int for v in job["pipeline_config"].values()), "Unexpected block/audit/resolve policy")
    require(type(job.get("dry_run")) is bool, "Job must specify dry_run")
    manifest = frozen.checked_path(job.get("input_manifest_path"))
    bank = inputs.verify_manifest(manifest, expected_sha=job.get("input_manifest_sha256"))
    problem, candidates = job.get("problem"), job.get("candidates")
    matching = [row for row in bank["problems"] if row["problem"] == problem]
    require(bank.get("source_arm") == "raw" and len(matching) == 1
            and matching[0]["candidates"] == candidates, "Job differs from bound raw inputs")
    require([c["candidate_id"] for c in candidates] == list(CANDIDATES)
            and all(c["selected_stage"] == "raw" for c in candidates), "Expected four raw lanes")
    runtime = job.get("runtime")
    require(isinstance(runtime, dict) and set(runtime) == {
        "gemma_endpoint", "qwen_endpoint", "workers", "model_timeout_sec", "seed_namespace", "repair_temperature"
    }, "Unexpected runtime fields")
    require(type(runtime["workers"]) is int and runtime["workers"] == 4
            and type(runtime["model_timeout_sec"]) is int and runtime["model_timeout_sec"] == 14400,
            "Keep four workers and the original request deadline")
    require(type(runtime["repair_temperature"]) is float and runtime["repair_temperature"] in (0.7, 0.4),
            "Repair temperature must be 0.7 or 0.4")
    require(isinstance(runtime["seed_namespace"], str) and runtime["seed_namespace"].strip(), "Missing seed namespace")
    require(strategy != "original" or runtime["repair_temperature"] == 0.4,
            "The original-harness control requires repair temperature 0.4")
    for role in ("gemma", "qwen"):
        endpoint = urlsplit(runtime[role + "_endpoint"])
        require(endpoint.scheme == "http" and endpoint.hostname in ("127.0.0.1", "localhost", "::1")
                and endpoint.path.rstrip("/") == "/v1" and not endpoint.query
                and not endpoint.fragment and not endpoint.username, "Expected a loopback /v1 endpoint")
    require(runtime["gemma_endpoint"].rstrip("/") != runtime["qwen_endpoint"].rstrip("/"), "Model endpoints must differ")
    output = frozen.checked_path(job.get("output_dir"))
    require(not output.exists() and not output.is_relative_to(frozen.RELEASE.parent)
            and not frozen.RELEASE.is_relative_to(output), "Use a fresh output outside frozen releases")
    require(not output.is_relative_to(manifest.parent) and not manifest.parent.is_relative_to(output),
            "Output overlaps the bound input snapshot")
    sources = {str(path): frozen.digest(raw), str(manifest): job["input_manifest_sha256"]}
    for candidate in candidates:
        proof_path = frozen.checked_path(candidate["proof_path"])
        data = frozen.read_bound(proof_path, candidate["proof_file_sha256"])
        require(frozen.text_digest(data) == candidate["proof_sha256"], "Raw proof text hash changed")
        sources[str(proof_path)] = frozen.digest(data)
    return job, sources


def _text(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")
    return str(path), frozen.digest(path.read_bytes())


def _json(path, value):
    frozen.write(path, value)
    return str(path), frozen.digest(path.read_bytes())


def _snapshot(data, source_path, directory):
    """Freeze exact bytes and a reproducible block table, without normalization."""
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_bytes(data)
    bank = blocks.build_blocks(data)
    require(bank["source_sha256"] == frozen.digest(data), "Block table lost its source binding")
    view = blocks.render_blocks(bank)
    bank_path, bank_hash = _json(directory / "blockmap.json", bank)
    view_path, view_hash = _text(directory / "blocks.txt", view)
    provenance = {"source_path": str(source_path), "source_file_sha256": frozen.digest(data),
                  "blockmap_path": bank_path, "blockmap_sha256": bank_hash,
                  "rendered_path": view_path, "rendered_sha256": view_hash}
    return {"data": data, "bank": bank, "view": view, "provenance": provenance}


def _verify_snapshot(snapshot):
    p = snapshot["provenance"]
    for key, hash_key in (("source_path", "source_file_sha256"), ("blockmap_path", "blockmap_sha256"),
                          ("rendered_path", "rendered_sha256")):
        try:
            frozen.read_bound(p[key], p[hash_key])
        except Exception as error:
            raise IntegrityError(str(error)) from error
    require(snapshot["bank"]["source_sha256"] == frozen.digest(snapshot["data"]), "In-memory block source drift")


def _issue_parser(bank):
    def parse(text):
        try:
            return {"valid": True, "issues": blocks.parse_issues(text, bank)}
        except ValueError as error:
            return {"valid": False, "errors": [str(error)]}
    return parse


def _patch_parser(snapshot, issues):
    def parse(text):
        try:
            result = blocks.parse_and_apply(text, snapshot["bank"], snapshot["data"], issues)
            return {"valid": True, **{k: v for k, v in result.items() if k != "proof_bytes"}}
        except ValueError as error:
            return {"valid": False, "errors": [str(error)]}
    return parse


def _issue_artifacts(directory, text, bank):
    issues = blocks.parse_issues(text, bank)
    raw_path, raw_hash = _text(directory / "issues.raw.txt", text)
    issues_path, issues_hash = _json(directory / "issues.json", issues)
    return issues, {"status": "issues" if issues else "no_issues",
                    "issues_path": issues_path, "issues_file_sha256": issues_hash,
                    "issues_raw_path": raw_path, "issues_raw_file_sha256": raw_hash}


def _patch_artifacts(directory, text, snapshot, issues):
    _verify_snapshot(snapshot)
    result = blocks.parse_and_apply(text, snapshot["bank"], snapshot["data"], issues)
    raw_path, raw_hash = _text(directory / "patch.raw.txt", text)
    audit_path, audit_hash = _json(directory / "patch_audit.json", result["audit"])
    return result, {"status": result["status"], "raw_patch_path": raw_path,
                    "raw_patch_file_sha256": raw_hash, "audit_path": audit_path,
                    "audit_file_sha256": audit_hash, "patches": result.get("patches", [])}


def _original_snippets(snapshot, patches):
    return "\n\n".join(
        "Edit " + str(index) + " (original block range " + ",".join(patch["block_ids"]) + "):\n"
        + snapshot["data"][patch["start"]:patch["end"]].decode("utf-8")
        for index, patch in enumerate(patches, 1) if patch.get("changed", True)
    )


def run(job_path, *, execute_models=False):
    job, sources = validate_job(job_path)
    require(job["dry_run"] != bool(execute_models), "Live jobs require --execute-models; dry runs must omit it")
    launcher, release_manifest, profile = frozen.load_release()
    backend = frozen.load_backend()
    frontend, boundary = backend.v108.v097, backend.repair_boundary
    runtime = frontend.GPU0FourSlotStageRuntime(frontend.RuntimeConfig(gemma_endpoint=job["runtime"]["gemma_endpoint"]))
    require((runtime.config.lazy_max_tokens, runtime.config.solver_max_tokens, runtime.config.protocol_attempts)
            == (16384, 65536, 2), "Frozen Gemma settings changed")
    require(boundary.QWEN_MAX_OUTPUT_TOKENS == 49152, "Frozen Qwen cap changed")
    bf = backend.v263.parent._budget_forcing
    require(bf.is_target_model(boundary.QWEN_MODEL), "Original chat BF does not support the pinned Qwen model")
    servers = {} if job["dry_run"] else {role: launcher.server_settings(job["runtime"][role + "_endpoint"],
        profile["servers"][role]) for role in ("gemma", "qwen")}
    legacy.verify_sources(sources)
    output = frozen.checked_path(job["output_dir"])
    output.mkdir(parents=True, exist_ok=False)
    began, problem = time.monotonic(), job["problem"]
    summary = {"schema": "block-local-result-v1", "experiment": EXPERIMENT,
        "strategy": "block",
        "processing_scope": job["processing_scope"], "pipeline_config": PIPELINE_CONFIG,
        "problem_id": problem["problem_id"], "source_arm": "raw", "dry_run": job["dry_run"],
        "job_sha256": sources[str(frozen.checked_path(str(Path(job_path).absolute())))],
        "input_manifest_path": job["input_manifest_path"], "input_manifest_sha256": job["input_manifest_sha256"],
        "runtime": job["runtime"], "release_identity": {"release": release_manifest["version"],
            "release_sha256": frozen.digest((frozen.RELEASE / "release.json").read_bytes()), "verified_servers": servers},
        "state": "running", "started_at": legacy.now(), "elapsed_seconds": 0.0, "lanes": [],
        "grading_performed": False, "mathematically_verified": False,
        "pipeline": "raw_block_lazy_patch_qwen_audit_conditional_gemma_resolve_once",
        "budget_forcing": "original_chat_reasoning_and_response_full_replacement"}
    lanes, snapshots, intermediate, issues, audit_issues, timings = {}, {}, {}, {}, {}, {}

    def update():
        summary["lanes"] = legacy.export_lanes(output, lanes)
        frozen.write(output / "status.json", summary)

    def failure(cid, phase, error, *, cannot=False):
        lane = lanes[cid]
        lane.update(operation="failed", local_result="cannot_repair_locally" if cannot else "invalid_or_failed",
            adopted_from="original", _proof_bytes=lane["_original_bytes"], failure={"stage": phase,
                "error_type": "CANNOT_REPAIR_LOCALLY" if cannot else type(error).__name__,
                "status": "CANNOT_REPAIR_LOCALLY" if cannot else "failed", "error": str(error), "at": legacy.now()})
        if phase == "lazy_check":
            lane["block_patch"]["status"] = "failed"
        elif phase == "expansion" and not cannot:
            lane["block_patch"]["status"] = "failed"
        elif phase in ("audit", "resolve"):
            target = lane["post_expansion"][phase]
            if not cannot:
                target["status"] = "failed"
        print(f"{legacy.now()} {cid}: {phase} failed; retaining original raw proof", flush=True)

    def call_gemma(cid, phase, system, parser):
        name = {"lazy_check": "lazy_check", "expansion": "lazy_in_place_resolve", "resolve": "post_block_resolve"}[phase]
        return runtime.gemma_call(output_dir=output / "run/candidates" / cid / name, name=name,
            system_prompt=system, user_prompt={"lazy_check": prompts.LAZY_USER, "expansion": prompts.EXPANSION_USER,
                                             "resolve": prompts.RESOLVE_USER}[phase],
            seed=lanes[cid]["seeds"][phase],
            temperature=0.1 if phase == "lazy_check" else job["runtime"]["repair_temperature"],
            max_tokens=16384 if phase == "lazy_check" else 65536, parser=parser)

    def batch(phase, ids, systems, task, accept):
        if not ids:
            return
        summary["stage"] = phase
        update()
        routes = legacy.unique_routes(legacy.route(phase, STAGES[phase], systems[cid]) for cid in ids)
        frozen.write(output / (phase + "_routes.json"), routes)
        user = {"lazy_check": prompts.LAZY_USER, "expansion": prompts.EXPANSION_USER,
                "audit": prompts.AUDIT_USER, "resolve": prompts.RESOLVE_USER}[phase]
        for cid in ids:
            lanes[cid][phase + "_prompt"] = legacy.record_prompts(output, cid, phase, systems[cid], user, policy.CUES[phase])
        def execute(cid):
            timings[cid] = time.monotonic()
            legacy.verify_sources(sources)
            _verify_snapshot(intermediate[cid] if phase in ("audit", "resolve") else snapshots[cid])
            value = task(cid)
            legacy.verify_sources(sources)
            return value
        def done(cid, value):
            elapsed = time.monotonic() - timings[cid]
            lanes[cid]["elapsed_seconds"] += elapsed
            lanes[cid]["phase_elapsed_seconds"][phase] = elapsed
            if "error" in value:
                failure(cid, phase, value["error"])
            else:
                accept(cid, value)
            update()
        with policy.install(bf, output / (phase + "_continuations.jsonl"), routes=routes):
            legacy.run_batch(ids, execute, done, policy_error=policy.PolicyError)

    try:
        frozen.write(output / "job.json", job)
        frozen.write(output / "input/problem.json", {"problem_id": problem["problem_id"], "claim": problem["claim"]})
        for candidate in job["candidates"]:
            cid = candidate["candidate_id"]
            data = frozen.read_bound(candidate["proof_path"], candidate["proof_file_sha256"])
            seed = legacy.seed_for(job["runtime"]["seed_namespace"], cid)
            audit_key = str(legacy.stage_seed(seed, "post_block_audit"))
            lanes[cid] = {"candidate_id": cid, "source_stage": "raw", "source_proof_path": candidate["proof_path"],
                "source_proof_file_sha256": candidate["proof_file_sha256"], "operation": "preflight_only",
                "local_result": "preflight_only", "adopted_from": "original", "failure": None,
                "elapsed_seconds": 0.0, "phase_elapsed_seconds": {}, "_proof_bytes": data, "_original_bytes": data,
                "block_patch": {"status": "not_run"}, "post_expansion": {"audit": {"status": "not_run"},
                                                                           "resolve": {"status": "not_run"}},
                "seeds": {"candidate": seed, "lazy_check": legacy.stage_seed(seed, "lazy_check"),
                    "expansion": legacy.stage_seed(seed, "lazy_in_place_resolve"),
                    "audit_seed_key": audit_key, "audit": boundary.stable_seed(audit_key, "49152"),
                    "resolve": legacy.stage_seed(seed, "post_block_resolve")}}
            try:
                snapshots[cid] = _snapshot(data, output / "input" / (cid + ".md"), output / "blocks" / cid)
                lanes[cid]["block_provenance"] = snapshots[cid]["provenance"]
            except ValueError as error:
                failure(cid, "segmentation", error)
        lazy_ids = [cid for cid in CANDIDATES if lanes[cid]["failure"] is None]
        lazy_systems = {cid: prompts.lazy_system(snapshots[cid]["view"]) for cid in lazy_ids}
        if job["dry_run"]:
            if any(lane["failure"] for lane in lanes.values()):
                update()
                raise ValueError("Raw proof segmentation failed; preflight is not ready for model execution")
            for cid in lazy_ids:
                lanes[cid]["lazy_check_prompt"] = legacy.record_prompts(output, cid, "lazy_check", lazy_systems[cid],
                    prompts.LAZY_USER, prompts.LAZY_CONTINUATION)
            summary.update(state="preflight_passed", model_calls=0)
        else:
            def check(cid):
                generated = call_gemma(cid, "lazy_check", lazy_systems[cid], _issue_parser(snapshots[cid]["bank"]))
                parsed, artifact = _issue_artifacts(output / "blocks" / cid, generated["text"], snapshots[cid]["bank"])
                return {"generated": generated, "issues": parsed, "artifact": artifact}
            def checked(cid, result):
                lane = lanes[cid]
                issues[cid] = result["issues"]
                lane["block_patch"].update(result["artifact"])
                lane.update(native_lazy_generation=result["generated"], lazy_report=result["generated"]["text"],
                    lazy_report_sha256=frozen.digest(result["generated"]["text"].encode()), has_lazy_issues=bool(issues[cid]))
                if not issues[cid]:
                    lane.update(operation="no_issues", local_result="no_issues")
            batch("lazy_check", lazy_ids, lazy_systems, check, checked)

            patch_ids = [cid for cid in lazy_ids if issues.get(cid)]
            patch_systems = {cid: prompts.expansion_system(problem["claim"], snapshots[cid]["view"],
                lanes[cid]["lazy_report"], issues[cid]) for cid in patch_ids}
            def patch(cid):
                generated = call_gemma(cid, "expansion", patch_systems[cid], _patch_parser(snapshots[cid], issues[cid]))
                result, artifact = _patch_artifacts(output / "blocks" / cid, generated["text"], snapshots[cid], issues[cid])
                return {"generated": generated, "result": result, "artifact": artifact}
            def patched(cid, value):
                lane, result = lanes[cid], value["result"]
                lane["block_patch"].update(value["artifact"])
                lane["native_expansion"] = value["generated"]
                if result["status"] == "cannot_repair_locally":
                    failure(cid, "expansion", ValueError("CANNOT_REPAIR_LOCALLY"), cannot=True)
                    return
                data = result["proof_bytes"]
                if data == lane["_original_bytes"]:
                    lane.update(operation="expanded", local_result="unchanged_patch_audit_skipped")
                    lane["post_expansion"]["audit"]["skip_reason"] = "patch_preserved_source_bytes"
                    return
                try:
                    fresh = _snapshot(data, output / "intermediate" / cid / "proof.md", output / "intermediate" / cid)
                except ValueError as error:
                    failure(cid, "audit", error)
                    return
                intermediate[cid] = fresh
                lane["post_expansion"].update(proof_path=fresh["provenance"]["source_path"],
                    proof_file_sha256=frozen.digest(data), proof_sha256=frozen.text_digest(data),
                    block_provenance=fresh["provenance"])
            batch("expansion", patch_ids, patch_systems, patch, patched)

            audit_ids = [cid for cid in CANDIDATES if cid in intermediate and lanes[cid]["failure"] is None]
            original_snippets = {cid: _original_snippets(snapshots[cid], lanes[cid]["block_patch"]["patches"])
                                 for cid in audit_ids}
            audit_systems = {cid: prompts.audit_system(problem["claim"], intermediate[cid]["view"], issues[cid],
                original_snippets[cid]) for cid in audit_ids}
            def audit(cid):
                generated = boundary.default_markdown_call(endpoint=job["runtime"]["qwen_endpoint"], model=boundary.QWEN_MODEL,
                    system_prompt=audit_systems[cid], user_prompt=prompts.AUDIT_USER,
                    output_dir=output / "run/candidates" / cid / "post_block_audit", stage_name="post_block_audit",
                    temperature=0.2, seed_key=lanes[cid]["seeds"]["audit_seed_key"], reasoning_effort=None,
                    parser=_issue_parser(intermediate[cid]["bank"]), model_timeout_sec=14400)
                parsed, artifact = _issue_artifacts(output / "intermediate" / cid / "audit", generated["text"], intermediate[cid]["bank"])
                return {"generated": generated, "issues": parsed, "artifact": artifact}
            def audited(cid, value):
                lane = lanes[cid]
                audit_issues[cid] = value["issues"]
                lane["post_expansion"]["audit"].update(value["artifact"])
                lane["native_audit"] = value["generated"]
                if not value["issues"]:
                    lane.update(operation="expanded", local_result="patched_audit_passed", adopted_from="expansion",
                                _proof_bytes=intermediate[cid]["data"])
            batch("audit", audit_ids, audit_systems, audit, audited)

            resolve_ids = [cid for cid in audit_ids if audit_issues.get(cid)]
            resolve_systems = {cid: prompts.expansion_system(problem["claim"], intermediate[cid]["view"],
                lanes[cid]["native_audit"]["text"], audit_issues[cid], resolving=True,
                restore_context=original_snippets[cid]) for cid in resolve_ids}
            def resolve(cid):
                generated = call_gemma(cid, "resolve", resolve_systems[cid], _patch_parser(intermediate[cid], audit_issues[cid]))
                result, artifact = _patch_artifacts(output / "intermediate" / cid / "resolve", generated["text"], intermediate[cid], audit_issues[cid])
                return {"generated": generated, "result": result, "artifact": artifact}
            def resolved(cid, value):
                lane, result = lanes[cid], value["result"]
                lane["post_expansion"]["resolve"].update(value["artifact"])
                lane["native_resolve"] = value["generated"]
                if result["status"] == "cannot_repair_locally":
                    failure(cid, "resolve", ValueError("CANNOT_REPAIR_LOCALLY"), cannot=True)
                elif result["proof_bytes"] == intermediate[cid]["data"]:
                    failure(cid, "resolve", ValueError("Audit issues remained but the resolve changed no bytes"))
                else:
                    lane.update(operation="expanded", local_result="resolved", adopted_from="resolve", _proof_bytes=result["proof_bytes"])
            batch("resolve", resolve_ids, resolve_systems, resolve, resolved)
            summary.update(state="completed_with_fallbacks" if any(l["failure"] for l in lanes.values()) else "completed",
                           stage="finished")
        update()
        legacy.verify_sources(sources)
    except BaseException as error:
        summary.update(state="interrupted" if isinstance(error, KeyboardInterrupt) else "failed",
                       error=f"{type(error).__name__}: {error}")
        raise
    finally:
        summary.update(finished_at=legacy.now(), elapsed_seconds=time.monotonic() - began)
        summary["local_result_counts"] = {key: sum(l["local_result"] == key for l in lanes.values())
                                         for key in sorted({l["local_result"] for l in lanes.values()})}
        try:
            legacy.verify_sources(sources)
            launcher.verify()
        except Exception as error:
            summary.update(state="failed", integrity_error=f"{type(error).__name__}: {error}")
            frozen.write(output / "summary.json", summary)
            frozen.write(output / "status.json", summary)
            raise
        frozen.write(output / "summary.json", summary)
        frozen.write(output / "status.json", summary)
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job", required=True, type=Path)
    parser.add_argument("--execute-models", action="store_true")
    args = parser.parse_args(argv)
    def interrupt(signum, frame):
        raise frozen.Interrupted(signum)
    previous = {sig: signal.signal(sig, interrupt) for sig in (signal.SIGINT, signal.SIGTERM)}
    try:
        run(args.job, execute_models=args.execute_models)
        return 0
    except frozen.Interrupted as error:
        print(str(error), file=sys.stderr, flush=True)
        os._exit(128 + error.signum)
    except KeyboardInterrupt:
        os._exit(130)
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    finally:
        for sig, handler in previous.items():
            signal.signal(sig, handler)


if __name__ == "__main__":
    raise SystemExit(main())
