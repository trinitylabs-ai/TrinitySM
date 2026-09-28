"""Resume a saved radical certificate into the existing generic proof rewriter.

No new formalization, backend search, or human mathematical hints. Consistency
is a parallel diagnostic: pending and timed-out checks do not delay packaging.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

from . import backend_comparison as backends, radical_certificate as radical, saved_witness, rewrite
from .radical_packaging_trial import accepted_system
from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906.contracts import EvidenceBundle, SynthesisAdapter, TaskInputs
from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906.tool_purpose import DETECTION_DOCUMENT, MATCHER_DOCUMENT

base = rewrite.pipeline.base
stable_hash = backends.division.exact_tools.stable_hash


def read(path):
    return json.loads(path.read_text())


def diagnostic(trial):
    path = trial / "consistency/status.json"
    result = read(path) if path.is_file() else {"checked": False, "state": "pending"}
    if result.get("checked") is True and result.get("consistent") is False:
        raise ValueError("consistency diagnostic established contradictory assumptions")
    return {key: result.get(key) for key in ("state", "checked", "consistent", "elapsed_seconds")}


def saved_inputs(trial):
    manifest = read(trial / "manifest.json")
    request_path = Path(manifest["request_path"])
    preview_path = Path(manifest["preview_path"]) if manifest.get("preview_path") else None
    request, admission, preview, system = accepted_system(request_path, preview_path)
    if request != read(trial / "request.json") or admission != manifest["admission"]:
        raise ValueError("saved trial request or admission changed")
    return request_path, preview_path, request, admission, preview, system


def prepared_lift(trial, request, preview, artifacts):
    root = trial / "lift/prepared"
    prepared_path = root / "prepared.json"
    prepared = read(prepared_path)
    worker = read(trial / "lift/worker_result.json")
    returned = dict(worker)
    returned.pop("prepared_file_sha256", None)
    if returned != prepared or worker.get("prepared_file_sha256") != base.sha256_file(prepared_path):
        raise ValueError("saved prepared lift changed")
    expected = {"source_arguments_sha256": stable_hash(request["arguments"]),
                "candidate_arguments_sha256": stable_hash(request["arguments"]),
                "guard_program_sha256": stable_hash(request["guard_program"]),
                "transform_sha256": preview["transform_sha256"]}
    if prepared.get("state") != "prepared" or any(prepared.get(key) != value for key, value in expected.items()):
        raise ValueError("prepared lift does not bind the accepted source and transform")
    required = ("full_source_lift_certificate.json", "typed_guard_binding.json", "laurent_transform.json")
    for name in required:
        path = root / name
        if base.sha256_file(path) != prepared.get("artifact_sha256", {}).get(name):
            raise ValueError("saved lift artifact changed: " + name)
        artifacts["lift_" + name] = path
    lift = read(root / required[0])
    payload = dict(lift)
    digest = payload.pop("certificate_sha256", None)
    if digest != stable_hash(payload) or digest != prepared["full_source_lift_certificate_sha256"]:
        raise ValueError("lift certificate internal binding changed")
    if lift.get("verified") is not True or not all(lift.get("implication_replay", {}).get(key) is True for key in (
            "source_equations_to_derived_equations", "derived_target_to_source_target_under_recorded_nonzero_guards",
            "all_circle_pairs_substituted_simultaneously")):
        raise ValueError("saved lift implication replay is incomplete")
    if any(lift.get(key) != value for key, value in expected.items() if key != "candidate_arguments_sha256"):
        raise ValueError("lift certificate source binding changed")
    artifacts.update(prepared_lift=prepared_path, lift_worker_result=trial / "lift/worker_result.json")
    return lift, read(root / "laurent_transform.json"), read(root / "typed_guard_binding.json")


def source_statement(request):
    """Print only the frozen implication, never a claimed derivation of it."""
    import sympy as sp
    from cognitive_well_harness_v0_3_282_unit_circle_laurent_elimination_20260905.symbol_safety import FreshNames
    symbols, equations, target, guards = backends.division.initial(request)
    target_label = sp.latex(FreshNames(symbols).take("T"))
    lines = ["## Algebraic lemma", "For the variables " + ", ".join(
        f"\\({sp.latex(symbol)}\\)" for symbol in symbols) + ", assume the following equations:"]
    lines.extend(f"\\[{sp.latex(value)}=0.\\]" for value in equations.values())
    if guards:
        lines.append("Assume also these nonzero conditions:")
        lines.extend(f"\\[{sp.latex(value)}\\ne0.\\]" for value in guards)
    lines.append(f"Then \\({target_label}={sp.latex(target)}=0\\).")
    markdown = "\n\n".join(lines)
    return markdown, {"schema": "saved-verified-implication-statement-only-v1",
        "target_label_latex": target_label, "presentation_kind": "statement_only",
        "certificate_derivation_supplied": False, "model_must_prove_inserted_lemma": True,
        "new_certificate_expansion": False, "saved_verification_rebound": True,
        "markdown_characters": len(markdown)}


STATEMENT_ONLY_POLICY = """Presentation mode: STATEMENT ONLY, not a supplied proof.
The saved exact certificate verifies the frozen algebraic implication, but its
multiplier identity and derivation have deliberately NOT been supplied here.
The immutable inserted block states the lemma only. Do not treat its insertion,
the VERIFIED_SUPPORT label, or the saved verification as a written proof.
The proof author must supply a complete human-readable derivation of this lemma
in the replacement itself, as well as both connections to the original theorem.
The auditor must check that derivation too, not only the surrounding application.
An unsupported algebraic leap or a citation to computation must fail the audit.
No proof-as-submitted acceptance follows just from the machine-certified result.
"""

APPENDIX_POLICY = """The full proof of the frozen algebraic lemma is supplied as
Appendix A and is appended unchanged to the submitted proof. It includes the
source-to-Laurent substitutions, justified nonzero conditions, all exact multiplier
coefficients, the contradiction identity, and the implication back to the source
target. You may cite this appendix for that algebra; you need not rediscover or
repeat it in the main text. This is not the earlier statement-only presentation.
The main proof must still derive every lemma input and guard from the original
theorem and explicitly translate its conclusion back to the theorem. The auditor
must judge the main proof together with its attached appendix, and must not
mistake the supplied algebraic proof for a proof of those semantic connections.
"""

ATTACH_ONLY_POLICY = """Appendix A is a complete, independently checked proof of
the exact lemma statement provided here. Its body is intentionally NOT in your
input; deterministic code appends it unchanged to your submitted main proof.
Cite Appendix A for that lemma without reproducing, rediscovering, or inventing
its internal calculations. Your responsibility is the main proof: derive every
lemma input and nonzero guard from the theorem and explicitly connect its
conclusion back to the theorem. Qwen receives and audits the complete assembled
document, including the actual appendix. Do not describe this workflow in the
mathematical proof; just refer to Appendix A where appropriate.
"""


def render_saved(trial, output, *, factor_first=False, statement_only=False, with_appendix=False):
    if with_appendix and (factor_first or statement_only):
        raise ValueError("appendix mode supplies the full proof without slow factorization")
    diagnostic(trial)
    request_path, preview_path, request, admission, preview, system = saved_inputs(trial)
    root = trial / "certificate/identity"
    certificate = read(root / "certificate.json")
    verified = read(root / "verification.json")
    if read(root / "system.json") != system or verified.get("verified") is not True:
        raise ValueError("radical certificate does not bind this system")
    if (verified.get("certificate_sha256") != stable_hash(certificate)
            or verified.get("system_sha256") != stable_hash(system)):
        raise ValueError("saved radical verification binding changed")
    artifacts = {"request": request_path, "trial_request": trial / "request.json", "trial_manifest": trial / "manifest.json",
                 "radical_certificate": root / "certificate.json", "radical_system": root / "system.json",
                 "radical_verification": root / "verification.json"}
    sample = request_path.parents[4]
    final_audit = request_path.parents[1] / "03_final_semantic_audit"
    for name in ("parser.json", "result.json", "input_formalization.md", "audit.md"):
        artifacts["semantic_" + name] = final_audit / name
    for name in ("theorem.md", "source_proof.md", "detection.md", "matcher.md"):
        artifacts[name] = sample / "input" / name
    artifacts["sample_manifest"] = sample / "manifest.json"
    if preview is not None:
        lift, transform, guards = prepared_lift(trial, request, preview, artifacts)
        if radical.system_payload(*backends.integration._decode_transform_payload(transform)) != system:
            raise ValueError("lift and radical certificate have different reduced systems")
        artifacts["preview"] = preview_path / "preview.json"
    if statement_only:
        markdown, presentation = source_statement(request)
    elif preview is None:
        markdown, presentation = radical.render(system, certificate, factor_first=factor_first,
                                               table_multipliers=with_appendix)
    else:
        markdown, presentation = saved_witness.render_laurent(arguments=request["arguments"],
            lift=lift, transform=transform, guard_ledger=guards, replay=verified, radical_identity=certificate,
            factor_first=factor_first, table_multipliers=with_appendix)
    if with_appendix:
        boundary = (saved_witness.STATEMENT_END if preview is not None else
                    "\n\nWork over the complex numbers. Suppose, for a contradiction, ")
        if markdown.count(boundary) != 1:
            raise ValueError("appendix requires a unique source statement/proof boundary")
        markdown, body = markdown.split(boundary, 1)
        appendix = "# Appendix A — Proof of the algebraic lemma" + boundary + body
        base.write_text(output / "saved_appendix.md", appendix)
        presentation.update(presentation_kind="statement_with_verified_appendix",
            certificate_derivation_supplied=True, model_must_prove_inserted_lemma=False,
            appendix_sha256=base.sha256_text(appendix), appendix_characters=len(appendix),
            markdown_characters=len(markdown))
    diagnostic(trial)
    record = {**presentation, "verified": True, "scope": "original_target_under_compiled_guards",
              "request_sha256": admission["request_sha256"], "laurent_lift_verified": preview is not None,
              "consistency_policy": "nonblocking_diagnostic", "new_formalization_calls": 0,
              "new_singular_calls": 0, "markdown_sha256": base.sha256_text(markdown),
              "source_artifacts": {key: {"path": str(path.resolve()), "sha256": base.sha256_file(path)}
                                   for key, path in artifacts.items()}}
    base.write_text(output / "saved_lemma.md", markdown)
    backends.write(output / "saved_lemma_verification.json", record)
    return {"state": "rendered", "verified": True, "markdown_characters": len(markdown),
            "appendix_characters": record.get("appendix_characters", 0),
            "abbreviation_count": record.get("abbreviation_count"), "target_label_latex": record["target_label_latex"]}


class SavedRadicalProvider:
    provider_id = "lossless_saved_guarded_radical_v1"

    def __init__(self, trial, output, tool_record, *, appendix_in_rewriter_prompt=True):
        self.trial, self.output, self.tool_record = trial, output, tool_record
        self.appendix_in_rewriter_prompt = appendix_in_rewriter_prompt
        self.verification = read(output / "saved_lemma_verification.json")
        if self.verification.get("presentation_kind") == "statement_only":
            self.provider_id = "saved_guarded_radical_statement_only_v1"
        elif self.verification.get("presentation_kind") == "statement_with_verified_appendix":
            self.provider_id = "saved_guarded_radical_verified_appendix_v1"
        self.appendix = ((output / "saved_appendix.md").read_text().strip()
            if self.verification.get("appendix_sha256") else "")
        self.markdown = (output / "saved_lemma.md").read_text().strip()
        self.records = self.verification["source_artifacts"]

    def materialize(self):
        diagnostic(self.trial)
        if base.sha256_text(self.markdown) != self.verification["markdown_sha256"]:
            raise ValueError("rendered radical lemma changed")
        if self.appendix and base.sha256_text(self.appendix) != self.verification["appendix_sha256"]:
            raise ValueError("saved appendix changed")
        for key, row in self.records.items():
            if base.sha256_file(Path(row["path"])) != row["sha256"]:
                raise ValueError("rendered radical source artifact changed: " + key)
        return EvidenceBundle(self.provider_id, "VERIFIED_SUPPORT", self.markdown, self.verification,
                              self.tool_record, {key: Path(row["path"]) for key, row in self.records.items()},
                              appendix_markdown=self.appendix,
                              appendix_in_rewriter_prompt=self.appendix_in_rewriter_prompt)


def reuse_appendix(trial, source, output):
    """Reuse an unchanged checked presentation; no rendering or algebra replay."""
    provider = SavedRadicalProvider(trial, source, {})
    bundle = provider.materialize()
    record = dict(bundle.verification)
    _, _, _, admission, preview, _ = saved_inputs(trial)
    expected = {"presentation_kind": "statement_with_verified_appendix", "verified": True,
                "certificate_derivation_supplied": True, "coefficient_tables_reparsed": True,
                "laurent_lift_verified": preview is not None}
    if any(record.get(key) != value for key, value in expected.items()) or not bundle.appendix_markdown:
        raise ValueError("saved appendix is not a complete checked radical presentation")
    if Path(record["source_artifacts"]["trial_manifest"]["path"]).resolve() != (trial / "manifest.json").resolve():
        raise ValueError("saved appendix belongs to another certificate trial")
    if record["request_sha256"] != admission["request_sha256"]:
        raise ValueError("saved appendix request binding changed")
    base.write_text(output / "saved_lemma.md", bundle.markdown)
    base.write_text(output / "saved_appendix.md", bundle.appendix_markdown)
    backends.write(output / "saved_lemma_verification.json", record)
    backends.write(output / "appendix_reuse.json", {"source": str(source), "new_algebra_replay": False,
        "source_verification_sha256": base.sha256_file(source / "saved_lemma_verification.json"),
        "appendix_sha256": record["appendix_sha256"]})
    return {"state": "reused", "verified": True, "markdown_characters": len(bundle.markdown),
            "appendix_characters": len(bundle.appendix_markdown),
            "target_label_latex": record["target_label_latex"]}


def wait_for_previous(source):
    """A queue dependency, not mathematical input. Never stop the preceding run."""
    if not source.is_dir():
        raise ValueError("previous run directory is missing")
    while True:
        for name in ("result.json", "status.json"):
            path = source / name
            if not path.is_file():
                continue
            try:
                record = read(path)
            except json.JSONDecodeError:
                continue
            if record.get("state") in {"completed", "failed_closed", "stopped_by_user"}:
                return {"path": str(path), "sha256": base.sha256_file(path), "state": record["state"]}
        time.sleep(10)


def render_bounded(trial, output, timeout=600, memory=4096, *, factor_first=False, with_appendix=False):
    command = [sys.executable, "-B", "-m", __package__ + ".radical_resume_synthesis", "--render-worker",
               "--trial", str(trial), "--output", str(output), "--memory", str(memory)]
    if factor_first:
        command.append("--factor-first")
    if with_appendix:
        command.append("--with-appendix")
    with (output / "render.log").open("w") as log:
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=5)
            raise TimeoutError("saved radical rendering exceeded its CPU time cap")
    result_path = output / "render_result.json"
    if not result_path.is_file():
        raise ValueError(f"render worker exited {process.returncode} without a result")
    result = read(result_path)
    if process.returncode != 0 or result.get("verified") is not True:
        raise ValueError("saved radical rendering failed: " + str(result))
    return result


def run(trial, output, master_seed, *, no_time_limit=False, factor_first=False, skip_rendering=False,
        with_appendix=False, appendix_attach_only=False, appendix_from=None, wait_for_run=None,
        additional_documents=None, gemma=None, qwen=None, repair_from=None, repair_cycle=None,
        max_cycles=3, final_qwen_revision=True):
    rewrite.assert_generic_boundary()
    if sum((skip_rendering, factor_first, with_appendix)) > 1:
        raise ValueError("skip-rendering, factor-first, and with-appendix are mutually exclusive")
    if (appendix_attach_only or appendix_from is not None) and not with_appendix:
        raise ValueError("appendix options require with-appendix")
    if not 1 <= max_cycles <= 3:
        raise ValueError("require 1..3 synthesis cycles")
    if (repair_from is None) != (repair_cycle is None):
        raise ValueError("repair requires both a source run and a cycle")
    if repair_from is not None:
        from . import saved_repair
        if not (with_appendix and appendix_attach_only):
            raise ValueError("saved repair requires attach-only appendix synthesis")
        if additional_documents is not None:
            raise ValueError("saved repair reuses the original associated documents")
        additional_documents = saved_repair.documents(repair_from)
        appendix_from = appendix_from or repair_from
    output.mkdir(parents=True, exist_ok=False)
    status = {"state": "running", "stage": "lemma_rendering", "trial": str(trial), "started": time.time(),
              "consistency_policy": "nonblocking_diagnostic", "new_formalization_calls": 0,
              "new_singular_calls": 0, "proof_rewrite_started": False}
    timeout = None if no_time_limit else 600
    status.update(render_timeout_seconds=timeout, request_timeout_seconds=timeout,
                  wall_clock_deadline=None, factor_first=factor_first,
                  certificate_rendering_skipped=skip_rendering,
                  certificate_derivation_supplied=not skip_rendering,
                  verified_appendix_requested=with_appendix,
                  appendix_in_rewriter_prompt=not appendix_attach_only,
                  appendix_from=str(appendix_from) if appendix_from else None,
                  wait_for_run=str(wait_for_run) if wait_for_run else None,
                  final_qwen_revision=bool(with_appendix and appendix_attach_only and final_qwen_revision),
                  json_model_output=False, manual_mathematical_content=False)
    backends.write(output / "status.json", status)
    try:
        if appendix_from is not None:
            rendered = reuse_appendix(trial, appendix_from, output)
        elif skip_rendering:
            status.update(stage="saved_certificate_binding")
            backends.write(output / "status.json", status)
            rendered = render_saved(trial, output, statement_only=True)
        else:
            rendered = render_bounded(trial, output, timeout=timeout, factor_first=factor_first,
                                      with_appendix=with_appendix)
        status.update(rendered=rendered, stage="proof_synthesis")
        backends.write(output / "status.json", status)
        request_path, _, request, _, _, _ = saved_inputs(trial)
        sample = request_path.parents[4]
        documents = {name: (sample / "input" / name).read_text().strip()
                     for name in ("theorem.md", "source_proof.md", "detection.md", "matcher.md")}
        extra = dict(additional_documents or {})
        if set(extra) & {DETECTION_DOCUMENT, MATCHER_DOCUMENT}:
            raise ValueError("additional documents cannot replace detector/matcher decisions")
        task = TaskInputs(read(sample / "manifest.json")["problem_id"], documents["theorem.md"],
                          documents["source_proof.md"], {DETECTION_DOCUMENT: documents["detection.md"],
                                                       MATCHER_DOCUMENT: documents["matcher.md"], **extra})
        detection = base.protocol.parse_detection(documents["detection.md"])
        matcher = base._parse_matcher(documents["matcher.md"], detection["desired_exact_fact"])
        provider = SavedRadicalProvider(trial, output, {"operation": matcher["operation"], "claim": matcher["claim"],
            "decision": "PROVED", "backend": "guarded_radical_membership",
            "scope": "conditional_target_vanishing_not_ordinary_ideal_membership"},
            appendix_in_rewriter_prompt=not appendix_attach_only)
        # Semantic bindings remain model-authored, untrusted context. No human
        # interpretation of the theorem or certificate is introduced here.
        from . import division_experiment
        formal_text = (request_path.parents[1] / "03_final_semantic_audit/input_formalization.md").read_text().strip()
        parsed = division_experiment.parse_proposal(formal_text, domain_inputs=documents,
            require_domain_ledger=read(sample / "manifest.json").get("domain_ledger_enabled", False))
        adapter = SynthesisAdapter("generic_saved_radical", task, provider,
            replace(rewrite.synthesis_contract(parsed["bindings"], rendered["target_label_latex"]),
                    max_cycles=max_cycles))
        initial_proof, initial_audit = None, None
        if repair_from is not None:
            initial_proof, initial_audit, repair_record = saved_repair.load(repair_from, repair_cycle,
                task=task, evidence=provider.materialize(), contract=adapter.contract)
            backends.write(output / "repair_resume.json", repair_record)
        calls = rewrite.BudgetedCalls(output / "model_budget.json", max_stages=2 * max_cycles
            + (2 if with_appendix and appendix_attach_only and final_qwen_revision else 0))

        def checked_call(**kwargs):
            provider.materialize()
            if skip_rendering or with_appendix:
                policy = APPENDIX_POLICY if with_appendix else STATEMENT_ONLY_POLICY
                if appendix_attach_only and kwargs["stage"].endswith("rewrite"):
                    policy = ATTACH_ONLY_POLICY
                kwargs["system_prompt"] += "\n\n" + policy
                kwargs["user_prompt"] = kwargs["user_prompt"].replace(
                    "# Exact-Evidence Verdict", "# Accepted Formalization — Semantic Bindings Still Require Derivation\n\n"
                    + formal_text + "\n\n# Exact-Evidence Verdict", 1)
                if skip_rendering:
                    kwargs["user_prompt"] = kwargs["user_prompt"].replace(
                        "# EXPLICIT Certified Lemma — Immutable, Represented by the Required Marker",
                        "# EXPLICIT Lemma Statement — Its Proof Must Be Written by You")
            status.update(stage=kwargs["stage"], proof_rewrite_started=True)
            backends.write(output / "status.json", status)
            kwargs["request_timeout_sec"] = timeout
            return calls(**kwargs)

        gemma = gemma or base.Role("http://127.0.0.1:8030/v1", base.DEFAULT_GEMMA_MODEL, 0.2, "max")
        qwen = qwen or base.Role("http://127.0.0.1:8027/v1", base.DEFAULT_QWEN_MODEL, 0.1, None)
        if wait_for_run is not None:
            status.update(state="queued", stage="waiting_for_previous_run")
            backends.write(output / "status.json", status)
            status["queue_dependency"] = wait_for_previous(wait_for_run)
            provider.materialize()
            status.update(state="running", stage="proof_synthesis")
            backends.write(output / "status.json", status)
        if with_appendix and appendix_attach_only:
            from . import appendix_synthesis
            def on_stage(stage):
                status.update(stage=stage, proof_rewrite_started=True)
                backends.write(output / "status.json", status)
            packaged = appendix_synthesis.run(task=task, provider=provider,
                formalization=formal_text, bindings=parsed["bindings"],
                target_label=rendered["target_label_latex"], output=output / "02_synthesis",
                gemma=gemma, qwen=qwen, seed=master_seed, model_call=calls,
                request_timeout=timeout, on_stage=on_stage, initial_proof=initial_proof,
                initial_audit=initial_audit, max_cycles=max_cycles,
                final_qwen_revision=final_qwen_revision)
            result, forcing = packaged["synthesis"], packaged["budget_forcing"]
        else:
            result = rewrite.pipeline.synthesis_pipeline.run(adapter=adapter, output_dir=output / "02_synthesis",
                gemma=gemma, qwen=qwen, master_seed=master_seed, model_call=checked_call)
            forcing = rewrite.pipeline._verify_synthesis_budget_forcing(synthesis_root=output / "02_synthesis",
                synthesis=result, gemma=gemma, qwen=qwen, expected_timeout_sec=timeout)
        provider.materialize()
        status.update(state=result["state"], stage="finished", synthesis=result, budget_forcing=forcing)
        rewrite.assert_generic_boundary()
    except Exception as error:
        status.update(state="failed_closed", error=f"{type(error).__name__}: {error}")
    backends.write(output / "status.json", status)
    backends.write(output / "result.json", status)
    return status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trial", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--master-seed", type=int, default=3090921)
    parser.add_argument("--render-worker", action="store_true")
    parser.add_argument("--memory", type=int, default=4096)
    parser.add_argument("--no-time-limit", action="store_true",
                        help="No rendering or model HTTP wall-clock timeout; token/memory/call budgets remain.")
    parser.add_argument("--factor-first", action="store_true",
                        help="Try exact factorization before lossless common-subexpression rendering.")
    parser.add_argument("--skip-rendering", action="store_true",
                        help="Rebind saved verification and pass only its frozen statement to synthesis; models must write and audit the lemma proof.")
    parser.add_argument("--with-appendix", action="store_true",
                        help="Supply and attach the complete saved lemma proof using exact coefficient tables, with no slow factorization.")
    parser.add_argument("--appendix-attach-only", action="store_true",
                        help="Omit the body from Gemma input; still attach the full verified appendix before Qwen audit.")
    parser.add_argument("--appendix-from", type=Path, help="Reuse an already prepared hash-bound appendix.")
    parser.add_argument("--wait-for-run", type=Path, help="Queue inference until this previous run is terminal.")
    parser.add_argument("--repair-from", type=Path, help="Resume a saved draft with its own rejecting Qwen audit.")
    parser.add_argument("--repair-cycle", type=int)
    parser.add_argument("--max-cycles", type=int, default=3)
    args = parser.parse_args()
    if args.render_worker:
        resource.setrlimit(resource.RLIMIT_AS, (args.memory * 1024**2, args.memory * 1024**2))
        try:
            result = render_saved(args.trial, args.output, factor_first=args.factor_first, with_appendix=args.with_appendix)
        except Exception as error:
            result = {"state": "failed_closed", "verified": False, "error": f"{type(error).__name__}: {error}"}
        backends.write(args.output / "render_result.json", result)
    else:
        result = run(args.trial.resolve(), args.output.resolve(), args.master_seed,
                     no_time_limit=args.no_time_limit, factor_first=args.factor_first,
                     skip_rendering=args.skip_rendering, with_appendix=args.with_appendix,
                     appendix_attach_only=args.appendix_attach_only,
                     repair_from=args.repair_from.resolve() if args.repair_from else None,
                     repair_cycle=args.repair_cycle, max_cycles=args.max_cycles,
                     appendix_from=args.appendix_from.resolve() if args.appendix_from else None,
                     wait_for_run=args.wait_for_run.resolve() if args.wait_for_run else None)
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
