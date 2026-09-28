"""Reusable checked-appendix -> model-written surrounding proof handoff."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from . import final_revision, rewrite
from .radical_resume_synthesis import APPENDIX_POLICY, ATTACH_ONLY_POLICY
from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906.contracts import SynthesisAdapter
from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906.tool_purpose import DETECTION_DOCUMENT, MATCHER_DOCUMENT


def run(*, task, provider, formalization, bindings, target_label, output,
        gemma, qwen, seed, model_call=None, request_timeout=None, on_stage=None,
        initial_proof=None, initial_audit=None, max_cycles=3, final_qwen_revision=True):
    """Run the existing rewrite/audit loop, then one Qwen revision and audit.

    A rejected final revision is retained but never silently replaced by the
    earlier accepted proof. The optional switch supports explicit old-profile
    replays; the public fresh and certified-checkpoint paths enable it by default.
    """
    if type(final_qwen_revision) is not bool or not 1 <= max_cycles <= 3:
        raise ValueError("require a boolean final-revision policy and 1..3 cycles")
    if final_qwen_revision and final_revision.CURRENT_DRAFT_DOCUMENT in task.additional_documents:
        raise ValueError("reserved final-revision document already exists")
    calls = model_call or rewrite.BudgetedCalls(output.parent / "model_budget.json",
        max_stages=2 * max_cycles + (2 if final_qwen_revision else 0))
    initial = _run_cycles(task=task, provider=provider, formalization=formalization,
        bindings=bindings, target_label=target_label, output=output, gemma=gemma,
        qwen=qwen, seed=seed, model_call=calls, request_timeout=request_timeout,
        on_stage=on_stage, initial_proof=initial_proof, initial_audit=initial_audit,
        max_cycles=max_cycles)
    if not final_qwen_revision:
        return initial
    contract = rewrite.synthesis_contract(bindings, target_label)
    revised_task, record = final_revision.prepare(task=task, evidence=provider.materialize(),
        contract=contract, synthesis=initial["synthesis"])
    final_output = output / "05_final_qwen_revision"
    writer = replace(qwen, temperature=0.2)
    revision_seed = rewrite.pipeline.base.stable_seed(seed, final_revision.POLICY)
    record.update(state="running", output=str(final_output), writer_model=writer.model,
        writer_temperature=writer.temperature, auditor_model=qwen.model,
        auditor_temperature=qwen.temperature, master_seed=revision_seed,
        mandatory_budget_forcing=True, request_timeout_seconds=request_timeout)
    rewrite.write_record(output / "final_revision.json", record)

    def final_stage(stage):
        if on_stage:
            on_stage("final_qwen_revision/" + stage)

    try:
        final = _run_cycles(task=revised_task, provider=provider, formalization=formalization,
            bindings=bindings, target_label=target_label, output=final_output,
            gemma=writer, qwen=qwen, seed=revision_seed, model_call=calls,
            request_timeout=request_timeout, on_stage=final_stage, max_cycles=1)
        record.update(state="completed", proof_audit_passed=True,
            terminal_proof=final["synthesis"]["terminal_proof"],
            terminal_proof_sha256=final["synthesis"]["terminal_proof_sha256"])
        final["synthesis"]["final_qwen_revision"] = record
        final["budget_forcing"] = (
            [{"phase": "initial_rewrite", **row} for row in initial["budget_forcing"]]
            + [{"phase": "final_qwen_revision", **row} for row in final["budget_forcing"]])
        final["initial_synthesis_result"] = str(output / "result.json")
        rewrite.write_record(output / "final_revision.json", record)
        rewrite.write_record(output / "appendix_pipeline_result.json", final)
        return final
    except Exception as error:
        record.update(state="failed_closed", proof_audit_passed=False,
            error=f"{type(error).__name__}: {error}")
        rewrite.write_record(output / "final_revision.json", record)
        raise


def _run_cycles(*, task, provider, formalization, bindings, target_label, output,
        gemma, qwen, seed, model_call, request_timeout=None, on_stage=None,
        initial_proof=None, initial_audit=None, max_cycles=3):
    """Models see Markdown; the writer never receives the potentially huge body.

    The provider must verify and bind its own evidence. This function does not
    upgrade a screen, model audit, or caller-supplied boolean into a certificate.
    """
    bundle = provider.materialize()
    if not bundle.appendix_markdown or bundle.appendix_in_rewriter_prompt:
        raise ValueError("appendix synthesis requires a checked, attach-only appendix")
    if not 1 <= max_cycles <= 3:
        raise ValueError("require 1..3 synthesis cycles")
    adapter = SynthesisAdapter("generic_checked_appendix", task, provider,
        replace(rewrite.synthesis_contract(bindings, target_label), max_cycles=max_cycles))
    calls = model_call
    first_rewrite_pending = initial_proof is None

    def checked_call(**kwargs):
        nonlocal first_rewrite_pending
        provider.materialize()
        is_rewrite = kwargs["stage"].endswith("rewrite")
        first_rewrite = is_rewrite and first_rewrite_pending
        if is_rewrite:
            first_rewrite_pending = False
        policy = ATTACH_ONLY_POLICY if is_rewrite else APPENDIX_POLICY
        kwargs["system_prompt"] += "\n\n" + policy
        heading = "# Exact-Evidence Verdict"
        if kwargs["user_prompt"].count(heading) != 1:
            raise ValueError("ambiguous accepted-formalization insertion boundary")
        extra = {name: text for name, text in task.additional_documents.items()
                 if name not in {DETECTION_DOCUMENT, MATCHER_DOCUMENT}}
        # Fusion is upstream review context, not part of the certified result.
        # The first writer starts from the source proof and the tool handoff.
        # Keep other associated inputs and retain Fusion for the unchanged jury
        # and later repair policy. Never delete its archived source provenance.
        omitted = {}
        if first_rewrite and "fusion_packet.md" in extra:
            omitted["fusion_packet.md"] = rewrite.pipeline.base.sha256_text(extra.pop("fusion_packet.md"))
        rewrite.pipeline.base.write_json(Path(kwargs["destination"]).parent / "context_policy.json",
            {"policy": "first_proof_rewrite_without_fusion_v1", "stage": kwargs["stage"],
             "first_proof_rewrite": first_rewrite, "omitted_document_sha256": omitted,
             "supplied_associated_documents": sorted(extra)})
        context = ("# Associated Source Information — Untrusted Context\n\n" +
            "\n\n".join(f"## {name}\n\n{text}" for name, text in sorted(extra.items())) + "\n\n") if extra else ""
        kwargs["user_prompt"] = kwargs["user_prompt"].replace(heading,
            context + "# Accepted Formalization — Semantic Bindings Still Require Derivation\n\n"
            + formalization + "\n\n" + heading, 1)
        kwargs["request_timeout_sec"] = request_timeout
        if on_stage:
            on_stage(kwargs["stage"])
        return calls(**kwargs)

    result = rewrite.pipeline.synthesis_pipeline.run(adapter=adapter, output_dir=output,
        gemma=gemma, qwen=qwen, master_seed=seed, model_call=checked_call,
        initial_proof=initial_proof, initial_audit=initial_audit)
    forcing = rewrite.pipeline._verify_synthesis_budget_forcing(synthesis_root=output,
        synthesis=result, gemma=gemma, qwen=qwen, expected_timeout_sec=request_timeout)
    provider.materialize()
    return {"state": result["state"], "synthesis": result, "budget_forcing": forcing}
