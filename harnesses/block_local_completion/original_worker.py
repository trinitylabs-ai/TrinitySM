"""Saved raw proofs through the unchanged lazy/full-proof expansion at t=0.4."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import os
from pathlib import Path
import signal
import sys
import time

from . import worker as common

legacy, frozen = common.legacy, common.frozen
require, IntegrityError = common.require, common.IntegrityError
CANDIDATES = common.CANDIDATES
PIPELINE_CONFIG = {"neighbor_blocks": 0, "max_audit_passes": 0, "max_resolve_passes": 0}


@contextmanager
def expansion_temperature(runtime, systems):
    """Override only this runtime instance's original expansion temperature."""
    original = runtime.gemma_call
    had_value, saved = "gemma_call" in runtime.__dict__, runtime.__dict__.get("gemma_call")
    def call(**kwargs):
        require(kwargs.get("name") == "lazy_in_place_resolve"
                and kwargs.get("system_prompt") in systems
                and kwargs.get("user_prompt") == legacy.EXPANSION_USER
                and kwargs.get("temperature") == 0.7,
                "Unexpected request reached the original expansion temperature adapter")
        return original(**{**kwargs, "temperature": 0.4})
    runtime.gemma_call = call
    try:
        yield
    finally:
        if had_value:
            runtime.gemma_call = saved
        else:
            del runtime.gemma_call


def run(job_path, *, execute_models=False):
    job, sources = common.validate_job(job_path, strategy="original")
    require(job["dry_run"] != bool(execute_models), "Live jobs require --execute-models; dry runs must omit it")
    launcher, release_manifest, profile = frozen.load_release()
    backend = frozen.load_backend()
    frontend = backend.v108.v097
    runtime = frontend.GPU0FourSlotStageRuntime(frontend.RuntimeConfig(gemma_endpoint=job["runtime"]["gemma_endpoint"]))
    require((runtime.config.lazy_max_tokens, runtime.config.solver_max_tokens, runtime.config.protocol_attempts)
            == (16384, 65536, 2), "Frozen frontend settings changed")
    lazy_module = sys.modules[frontend.run_lazy_check.__module__]
    expansion_module = sys.modules[frontend.run_lazy_resolve.__module__]
    bf = backend.v263.parent._budget_forcing
    servers = {} if job["dry_run"] else {"gemma": launcher.server_settings(
        job["runtime"]["gemma_endpoint"], profile["servers"]["gemma"])}
    legacy.verify_sources(sources)
    output = frozen.checked_path(job["output_dir"])
    output.mkdir(parents=True, exist_ok=False)
    began, problem = time.monotonic(), job["problem"]
    summary = {"schema": "block-local-result-v1", "experiment": common.EXPERIMENT,
        "strategy": "original", "processing_scope": job["processing_scope"], "pipeline_config": PIPELINE_CONFIG,
        "problem_id": problem["problem_id"], "source_arm": "raw", "dry_run": job["dry_run"],
        "job_sha256": sources[str(frozen.checked_path(str(Path(job_path).absolute())))],
        "input_manifest_path": job["input_manifest_path"], "input_manifest_sha256": job["input_manifest_sha256"],
        "runtime": job["runtime"], "release_identity": {"release": release_manifest["version"],
            "release_sha256": frozen.digest((frozen.RELEASE / "release.json").read_bytes()), "verified_servers": servers},
        "state": "running", "started_at": legacy.now(), "elapsed_seconds": 0.0, "lanes": [],
        "grading_performed": False, "mathematically_verified": False,
        "pipeline": "raw_original_lazy_check_conditional_full_proof_expansion",
        "budget_forcing": "original_chat_reasoning_and_response_full_replacement",
        "temperature_override": {"stage": "lazy_in_place_resolve", "frozen_default": 0.7, "effective": 0.4}}
    lanes, rows, scans, timings = {}, {}, {}, {}

    def update():
        summary["lanes"] = legacy.export_lanes(output, lanes)
        frozen.write(output / "status.json", summary)

    def verify_inputs():
        legacy.verify_sources(sources)
        for lane in lanes.values():
            p = lane["original_provenance"]
            try:
                frozen.read_bound(p["source_path"], p["source_file_sha256"])
            except Exception as error:
                raise IntegrityError(str(error)) from error

    def batch(phase, ids, task, accept):
        if not ids:
            return
        summary["stage"] = phase
        update()
        def execute(cid):
            timings[cid] = time.monotonic()
            verify_inputs()
            result = task(cid)
            verify_inputs()
            return result
        def done(cid, value):
            lane = lanes[cid]
            elapsed = time.monotonic() - timings[cid]
            lane["phase_elapsed_seconds"][phase] = elapsed
            lane["elapsed_seconds"] += elapsed
            if "error" in value:
                error = value["error"]
                lane.update(operation="failed", local_result="invalid_or_failed", adopted_from="original",
                    failure={"stage": phase, "error_type": type(error).__name__, "status": "failed",
                             "error": str(error), "at": legacy.now()})
            else:
                accept(cid, value)
            update()
        legacy.run_batch(ids, execute, done, policy_error=IntegrityError)

    try:
        frozen.write(output / "job.json", job)
        frozen.write(output / "input/problem.json", {"problem_id": problem["problem_id"], "claim": problem["claim"]})
        for candidate in job["candidates"]:
            cid = candidate["candidate_id"]
            data = frozen.read_bound(candidate["proof_path"], candidate["proof_file_sha256"])
            snapshot = output / "input" / (cid + ".md")
            snapshot.write_bytes(data)
            seed = legacy.seed_for(job["runtime"]["seed_namespace"], cid)
            lanes[cid] = {"candidate_id": cid, "source_stage": "raw", "source_proof_path": candidate["proof_path"],
                "source_proof_file_sha256": candidate["proof_file_sha256"], "operation": "preflight_only",
                "local_result": "preflight_only", "adopted_from": "original", "failure": None,
                "elapsed_seconds": 0.0, "phase_elapsed_seconds": {}, "_proof_bytes": data,
                "original_provenance": {"source_path": str(snapshot), "source_file_sha256": frozen.digest(data)},
                "seeds": {"candidate": seed, "lazy_check": legacy.stage_seed(seed, "lazy_check"),
                          "expansion": legacy.stage_seed(seed, "lazy_in_place_resolve")}}
            rows[cid] = {"candidate_id": cid, "proof": snapshot.read_text(encoding="utf-8").strip(),
                "proof_sha256": candidate["proof_sha256"], "seed": seed,
                "temperature": 1.0 if cid.startswith("t10") else 0.7}
            lanes[cid]["lazy_check_prompt"] = legacy.record_prompts(output, cid, "lazy_check",
                lazy_module.lazy_phrasing(rows[cid]["proof"]), legacy.LAZY_USER, bf.TEXT_CONTINUATION)
        if job["dry_run"]:
            summary.update(state="preflight_passed", model_calls=0)
        else:
            def check(cid):
                scan = frontend.run_lazy_check(runtime=runtime, output_dir=output / "run", row=dict(rows[cid]))
                report = str(scan["lazy_report"]).strip()
                require(report and scan["candidate_id"] == cid and scan["proof_sha256"] == rows[cid]["proof_sha256"],
                        "Lazy output lost its source identity")
                require(scan["lazy_report_sha256"] == frozen.digest(report.encode())
                        and scan["has_lazy_issues"] is (report != "NO_ISSUES"), "Lazy report identity changed")
                return scan
            def checked(cid, scan):
                scans[cid] = scan
                lane = lanes[cid]
                path, digest = common._text(output / "original" / cid / "lazy_report.txt", scan["lazy_report"])
                lane["original_provenance"].update(lazy_report_path=path, lazy_report_file_sha256=digest)
                lane.update(lazy_report=scan["lazy_report"], lazy_report_sha256=scan["lazy_report_sha256"],
                    has_lazy_issues=scan["has_lazy_issues"], native_lazy_generation=scan["lazy_generation"])
                if not scan["has_lazy_issues"]:
                    lane.update(operation="no_issues", local_result="no_issues")
            batch("lazy_check", list(CANDIDATES), check, checked)
            expanding = [cid for cid in CANDIDATES if cid in scans and scans[cid]["has_lazy_issues"]]
            systems = {cid: expansion_module.lazy_in_place_expansion_prompt(problem=problem["claim"].strip(),
                current_proof=rows[cid]["proof"], local_gaps=scans[cid]["lazy_report"]) for cid in expanding}
            for cid in expanding:
                lanes[cid]["expansion_prompt"] = legacy.record_prompts(output, cid, "expansion", systems[cid],
                    legacy.EXPANSION_USER, bf.TEXT_CONTINUATION)
            def expand(cid):
                result = frontend.run_lazy_resolve(runtime=runtime, problem=problem["claim"].strip(),
                    output_dir=output / "run", row=scans[cid])
                generation = result.get("expansion_generation")
                if not isinstance(generation, dict) or not isinstance(generation.get("text"), str):
                    raise ValueError("Expansion has no complete generated envelope")
                parsed = expansion_module.expansion_parser(generation["text"])
                if not parsed.get("valid") or not str(parsed.get("proof") or "").strip():
                    raise ValueError("Expansion did not return a valid complete proof envelope")
                proof_path = frozen.checked_path(result["checked_proof_path"])
                require(proof_path.is_relative_to(output / "run/candidates" / cid)
                        and result["candidate_id"] == cid, "Expansion output escaped its lane")
                data = proof_path.read_bytes()
                require(data == (str(parsed["proof"]).strip() + "\n").encode("utf-8")
                        and frozen.text_digest(data) == result["checked_proof_sha256"]
                        and result["conclusion_action"] == parsed["conclusion_action"],
                        "Expansion proof differs from parsed envelope")
                # Keep the frozen result.json intact; expose the actual request
                # temperature alongside its constant-based legacy annotation.
                result = {**result, "frozen_declared_lazy_resolve_temperature": result["lazy_resolve_temperature"],
                          "lazy_resolve_temperature": 0.4}
                return {"result": result, "proof_bytes": data, "response": generation["text"], "parsed": parsed}
            def expanded(cid, value):
                lane = lanes[cid]
                directory = output / "original" / cid
                raw_path, raw_hash = common._text(directory / "expansion_response.txt", value["response"])
                proof_path = directory / "parsed_proof.md"
                proof_path.write_bytes(value["proof_bytes"])
                lane["original_provenance"].update(expansion_response_path=raw_path,
                    expansion_response_file_sha256=raw_hash, parsed_proof_path=str(proof_path),
                    parsed_proof_file_sha256=frozen.digest(value["proof_bytes"]),
                    conclusion_action=value["parsed"]["conclusion_action"])
                lane.update(operation="expanded", local_result="original_expanded", adopted_from="expansion",
                    _proof_bytes=value["proof_bytes"], native_expansion=value["result"],
                    conclusion_action=value["parsed"]["conclusion_action"])
            with expansion_temperature(runtime, set(systems.values())):
                batch("expansion", expanding, expand, expanded)
            summary.update(state="completed_with_fallbacks" if any(lane["failure"] for lane in lanes.values()) else "completed",
                           stage="finished")
        update()
        verify_inputs()
    except BaseException as error:
        summary.update(state="interrupted" if isinstance(error, KeyboardInterrupt) else "failed",
                       error=f"{type(error).__name__}: {error}")
        raise
    finally:
        summary.update(finished_at=legacy.now(), elapsed_seconds=time.monotonic() - began)
        summary["local_result_counts"] = {key: sum(lane["local_result"] == key for lane in lanes.values())
                                         for key in sorted({lane["local_result"] for lane in lanes.values()})}
        try:
            verify_inputs()
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
