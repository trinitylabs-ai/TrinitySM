"""Bounded certificate checks on one immutable, previously accepted request.

This resumes saved algebra, not model formalization. A positive screen alone
never authorizes synthesis. All stage artifacts, including failures, survive.
Certificate export runs first; only a verified certificate starts follow-up
checks. A failed export never spends time on a lift or consistency diagnostic.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

from . import backend_comparison as backends
from . import radical_certificate as radical


CHECK_SCHEDULING_POLICY = "certificate_first_followups_on_verified_v1"


def accepted_system(request_path, preview_path=None):
    request, admission = backends.accepted_request(request_path)
    if preview_path is not None:
        preview, decoded = backends.bound_preview(preview_path, request)
        return request, admission, preview, radical.system_payload(*decoded)
    symbols, equations, target, guards = backends.division.initial(request)
    system = radical.system_payload(symbols, list(equations.items()), target,
                                   {f"guard_{i}": guard for i, guard in enumerate(guards)})
    return request, admission, None, system


def worker(stage, request_path, preview_path, output, timeout, memory):
    resource.setrlimit(resource.RLIMIT_AS, (memory * 1024**2, memory * 1024**2))
    request, admission, preview, system = accepted_system(request_path, preview_path)
    if stage == "certificate":
        return radical.export(system, output / "identity", timeout=timeout, memory=memory)
    if stage == "consistency":
        return radical.consistency(system, timeout=timeout, memory=memory)
    if stage == "lift":
        if preview is None:
            raise ValueError("a direct source certificate does not use a Laurent lift")
        validation = {
            "schema": "cognitive-well-v0309-identity-source-validation-v1",
            "decision": "ACCEPT", "identity": True,
            "reason": "source and candidate are the same canonical guarded formalization",
            "source_arguments_sha256": backends.division.exact_tools.stable_hash(request["arguments"]),
            "candidate_arguments_sha256": backends.division.exact_tools.stable_hash(request["arguments"]),
            "guard_program_sha256": backends.division.exact_tools.stable_hash(request["guard_program"]),
        }
        backends.write(output / "identity_source_validation.json", validation)
        result = backends.integration.preprocess_only(
            source_arguments=request["arguments"], candidate_arguments=request["arguments"],
            guard_program=request["guard_program"], exact_transformation_validation=validation,
            output_dir=output / "prepared", expected_transform_sha256=preview["transform_sha256"],
            expected_derived_profile=preview["derived_profile"],
            expected_structural_preview_sha256=hashlib.sha256((preview_path / "preview.json").read_bytes()).hexdigest())
        return {key: value for key, value in result.items() if key != "_runtime"}
    raise ValueError("unknown certificate check")


def bounded(stage, request_path, preview_path, output, timeout, memory):
    output.mkdir(parents=True, exist_ok=False)
    started = time.time()
    backends.write(output / "status.json", {"state": "running", "stage": stage, "started": started})
    command = [sys.executable, "-B", "-m", __package__ + ".radical_packaging_trial",
               "--worker", stage, "--request", str(request_path),
               "--output", str(output), "--timeout", str(timeout), "--memory", str(memory)]
    if preview_path is not None:
        command += ["--preview", str(preview_path)]
    with (output / "worker.log").open("w") as log:
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            process.wait(timeout=timeout + 10)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=5)
            result = {"state": "timeout", "verified": False, "checked": False}
        else:
            path = output / "worker_result.json"
            result = json.loads(path.read_text()) if path.is_file() else {
                "state": "failed_closed", "error": f"worker exited {process.returncode} without a result"}
            if process.returncode != 0:
                result = {"state": "failed_closed", "error": f"worker exit {process.returncode}", "result": result}
    result.update(stage=stage, elapsed_seconds=round(time.time() - started, 3))
    backends.write(output / "status.json", result)
    return result


def packaging_ready(checks, *, needs_lift):
    """A pending/unknown consistency diagnostic cannot delay checked evidence."""
    consistency = checks.get("consistency", {})
    if consistency.get("checked") is True and consistency.get("consistent") is False:
        return False
    return (checks.get("certificate", {}).get("verified") is True
            and (not needs_lift or checks.get("lift", {}).get("state") == "prepared"))


def run(request_path, preview_path, output, timeout=600, memory=4096, *, on_ready=None):
    request, admission, preview, system = accepted_system(request_path, preview_path)
    output.mkdir(parents=True, exist_ok=False)
    status = {"state": "running", "stage": "certificate", "model_calls": 0,
              "request_path": str(request_path), "preview_path": str(preview_path) if preview_path else None,
              "admission": admission, "profile": {"variables": len(system["symbols"]),
                  "generators": len(system["generators"]), "guards": len(system["guards"])}, "checks": {},
              "timeout_seconds_per_check": timeout, "memory_mb_per_check": memory,
              "check_scheduling_policy": CHECK_SCHEDULING_POLICY,
              "consistency_policy": "parallel_nonblocking_diagnostic_contradictions_flagged",
              "promotable": False, "proof_rewrite_started": False}
    backends.write(output / "manifest.json", status)
    backends.write(output / "status.json", status)
    backends.write(output / "request.json", request)
    stages = ("consistency", "lift") if preview is not None else ("consistency",)
    try:
        status["checks"]["certificate"] = bounded(
            "certificate", request_path, preview_path, output / "certificate", timeout, memory)
    except Exception as error:
        status["checks"]["certificate"] = {
            "state": "failed_closed", "error": f"{type(error).__name__}: {error}"}
    if status["checks"]["certificate"].get("verified") is not True:
        status["checks"].update({stage: {"state": "skipped", "reason": "certificate_not_verified"}
                                 for stage in stages})
        status.update(state="not_certified", stage="checks_finished")
        backends.write(output / "status.json", status)
        backends.write(output / "result.json", status)
        return status

    status.update(stage="post_certificate_checks")
    backends.write(output / "status.json", status)
    handoff = None
    with ThreadPoolExecutor(max_workers=len(stages)+1) as pool:
        def start_handoff_if_ready():
            nonlocal handoff
            if packaging_ready(status["checks"], needs_lift=preview is not None):
                status.update(state="ready_for_packaging", ready_at=time.time())
                backends.write(output / "status.json", status)
                if on_ready is not None and handoff is None:
                    # A direct certificate needs no lift and must not wait for
                    # the first consistency future to finish before synthesis.
                    handoff = pool.submit(on_ready, output)
                    status.update(packaging_started=True)

        jobs = {pool.submit(bounded, stage, request_path, preview_path, output / stage, timeout, memory): stage
                for stage in stages}
        start_handoff_if_ready()
        backends.write(output / "status.json", status)
        for future in as_completed(jobs):
            stage = jobs[future]
            try:
                status["checks"][stage] = future.result()
            except Exception as error:
                status["checks"][stage] = {"state": "failed_closed", "error": f"{type(error).__name__}: {error}"}
            start_handoff_if_ready()
            backends.write(output / "status.json", status)
    checks = status["checks"]
    ready = packaging_ready(checks, needs_lift=preview is not None)
    status.update(state="ready_for_packaging" if ready else "not_certified", stage="checks_finished")
    if checks.get("consistency", {}).get("checked") is True and checks["consistency"].get("consistent") is False:
        status.update(consistency_contradiction=True, state="contradictory_source")
    if handoff is not None:
        try:
            status["packaging_result"] = handoff.result()
        except Exception as error:
            status["packaging_error"] = f"{type(error).__name__}: {error}"
    backends.write(output / "status.json", status)
    backends.write(output / "result.json", status)
    return status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--preview", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--memory", type=int, default=4096)
    parser.add_argument("--worker", choices=("certificate", "consistency", "lift"))
    args = parser.parse_args()
    if args.worker:
        try:
            result = worker(args.worker, args.request, args.preview, args.output, args.timeout, args.memory)
        except Exception as error:
            result = {"state": "failed_closed", "error": f"{type(error).__name__}: {error}"}
        backends.write(args.output / "worker_result.json", result)
    else:
        result = run(args.request.resolve(), args.preview.resolve() if args.preview else None,
                     args.output.resolve(), args.timeout, args.memory)
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
