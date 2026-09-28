"""Synthetic final-revision wiring tests: no inference, gold, or saved success."""
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from . import appendix_synthesis, final_revision, proof_harness, rewrite
from .test_appendix import fixture
from .test_harness import _forcing
from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906 import pipeline as core, validation


class Models:
    def __init__(self, evidence, *, reject_final=False, reject_initial=False, invalid_final=False,
                 bad_forcing=False):
        self.evidence = evidence
        self.reject_final, self.reject_initial = reject_final, reject_initial
        self.invalid_final, self.bad_forcing = invalid_final, bad_forcing
        self.calls = []

    def __call__(self, **kw):
        self.calls.append(kw)
        final = "05_final_qwen_revision" in Path(kw["destination"]).parts
        if kw["stage"].endswith("rewrite"):
            label = "Final revision" if final else "Initial draft"
            text = label + ". Since x=y, apply the lemma proved in Appendix A.\n\n"
            text += "[[VERIFIED_EXACT_EVIDENCE]]\n\nHence x-y=0."
            if final and self.invalid_final:
                text += "\n\n" + self.evidence.appendix_markdown
        else:
            passed = not (self.reject_final if final else self.reject_initial)
            text = "# Decision\n\n" + ("PASS" if passed else "FAIL") + "\n\n# Checks\n\n"
            text += "\n".join(f"- {label}: {'PASS' if passed or index else 'FAIL'}"
                for index, label in enumerate(core.protocol.PROOF_AUDIT_CHECKS))
            text += "\n\n# Issues\n\n" + ("NONE" if passed else "- Derive the necessary lemma input.")
        metadata = _forcing(text=text, stage=kw["stage"], model=kw["role"].model)
        metadata["request_timeout_sec"] = kw["request_timeout_sec"]
        if final and self.bad_forcing:
            metadata["metadata"]["v0257_budget_forcing"]["forced_text_sha256"] = "tampered"
        return text, kw["parser"](text), metadata


def setup(tmp_path):
    evidence, contract, task = fixture(tmp_path)
    evidence = replace(evidence, appendix_in_rewriter_prompt=False)
    provider = SimpleNamespace(materialize=lambda: evidence)
    return evidence, contract, task, provider


def execute(tmp_path, evidence, task, provider, model, **kwargs):
    config = proof_harness.Config()
    return appendix_synthesis.run(task=task, provider=provider, formalization="Frozen semantic bindings.",
        bindings={"source_basis": "Frozen semantic bindings."}, target_label="T", output=tmp_path / "synthesis", gemma=config.proof_writer(),
        qwen=config.qwen(), seed=123, model_call=model, max_cycles=1, **kwargs)


def test_final_revision_uses_qwen_same_context_and_checked_appendix(tmp_path):
    evidence, contract, task, provider = setup(tmp_path)
    task = replace(task, additional_documents={"fusion_packet.md": "FUSION_CONTEXT",
                                              "associated.md": "OTHER_CONTEXT"})
    model = Models(evidence)
    stages = []
    result = execute(tmp_path, evidence, task, provider, model, on_stage=stages.append)
    assert result["state"] == "completed" and len(model.calls) == 4
    assert [kw["role"].model for kw in model.calls] == [proof_harness.base.DEFAULT_QWEN_MODEL] * 4
    assert [kw["role"].temperature for kw in model.calls] == [.2, .1, .2, .1]
    assert all(kw["request_timeout_sec"] is None for kw in model.calls)
    assert stages[-1].startswith("final_qwen_revision/")
    first, _, final, audit = model.calls
    for kw in model.calls:
        assert "Frozen semantic bindings." not in kw["system_prompt"]
        assert "Frozen semantic bindings." in kw["user_prompt"]
    assert first["system_prompt"] == final["system_prompt"]
    for kw in (first, final):
        assert evidence.appendix_markdown not in kw["user_prompt"]
        assert kw["user_prompt"].count(evidence.markdown) == 1
        assert "FUSION_CONTEXT" not in kw["user_prompt"]
        assert "OTHER_CONTEXT" in kw["user_prompt"]
        assert "Frozen semantic bindings." in kw["user_prompt"]
    assert final_revision.CURRENT_DRAFT_DOCUMENT not in first["user_prompt"]
    assert final_revision.INSTRUCTION in final["user_prompt"]
    assert "Initial draft." in final["user_prompt"]
    assert "# Prior Jury Issues\n\nNONE" in final["user_prompt"]
    assert "# Previous Replacement Proof\n\nNONE" in final["user_prompt"]
    assert final["user_prompt"].index(task.source_proof) < final["user_prompt"].index(final_revision.INSTRUCTION)
    assert audit["user_prompt"].count(evidence.appendix_markdown) == 1
    assert "Final revision." in audit["user_prompt"] and "FUSION_CONTEXT" in audit["user_prompt"]
    final_proof = Path(result["synthesis"]["terminal_proof"]).read_text().strip()
    assert final_proof.startswith("Final revision.")
    assert final_proof.endswith(evidence.appendix_markdown)
    assert final_proof.count(evidence.markdown) == final_proof.count(evidence.appendix_markdown) == 1
    assert len(result["budget_forcing"]) == 2
    assert {row["phase"] for row in result["budget_forcing"]} == {"initial_rewrite", "final_qwen_revision"}
    published = proof_harness.publish(tmp_path / "published", {"selected": {"result": result}})
    assert Path(published["rewritten_proof"]).read_text().strip() == final_proof
    assert published["final_qwen_revision"]["state"] == "completed"
    assert (tmp_path / "synthesis/terminal_proof.md").read_text().startswith("Initial draft.")
    assert not (tmp_path / "synthesis/strict_score").exists()


@pytest.mark.parametrize("failure", ["audit", "parser", "forcing"])
def test_final_failure_never_publishes_initial_proof_as_final(tmp_path, failure):
    evidence, _, task, provider = setup(tmp_path)
    model = Models(evidence, reject_final=failure == "audit", invalid_final=failure == "parser",
                   bad_forcing=failure == "forcing")
    with pytest.raises((ValueError, RuntimeError)):
        execute(tmp_path, evidence, task, provider, model)
    record = proof_harness.resume.read(tmp_path / "synthesis/final_revision.json")
    assert record["state"] == "failed_closed" and not record["proof_audit_passed"]
    assert len(model.calls) == (3 if failure == "parser" else 4)
    assert (tmp_path / "synthesis/terminal_proof.md").is_file()  # preserved, not promoted
    assert not (tmp_path / "synthesis/appendix_pipeline_result.json").exists()
    if failure == "audit":
        assert (tmp_path / "synthesis/05_final_qwen_revision/02_rewrite/cycle_01/terminal_proof.md").is_file()
        assert not (tmp_path / "synthesis/05_final_qwen_revision/terminal_proof.md").exists()


def test_no_final_calls_when_initial_audit_rejects(tmp_path):
    evidence, _, task, provider = setup(tmp_path)
    model = Models(evidence, reject_initial=True)
    with pytest.raises(RuntimeError, match="no proof passed"):
        execute(tmp_path, evidence, task, provider, model)
    assert len(model.calls) == 2
    assert not (tmp_path / "synthesis/05_final_qwen_revision").exists()


@pytest.mark.parametrize("third_passes", [True, False])
def test_qwen_writes_all_three_cycles_and_audits_separately(tmp_path, third_passes):
    evidence, _, task, provider = setup(tmp_path)
    class ThreeCycles(Models):
        def __call__(self, **kw):
            self.reject_initial = not (third_passes and "cycle_03" in Path(kw["destination"]).parts)
            return super().__call__(**kw)
    model = ThreeCycles(evidence)
    config = proof_harness.Config()
    def run():
        return appendix_synthesis.run(task=task, provider=provider,
            formalization="Frozen semantic bindings.", bindings={}, target_label="T",
            output=tmp_path / "synthesis", gemma=config.proof_writer(), qwen=config.qwen(),
            seed=123, model_call=model, max_cycles=3)
    if third_passes:
        result = run()
        assert result["state"] == "completed" and len(model.calls) == 8
    else:
        with pytest.raises(RuntimeError, match="no proof passed"):
            run()
        assert len(model.calls) == 6
    for index, kw in enumerate(model.calls):
        assert kw["role"].model == proof_harness.base.DEFAULT_QWEN_MODEL
        assert kw["role"].endpoint == config.qwen_endpoint
        assert kw["role"].temperature == (.2 if index % 2 == 0 else .1)
        assert kw["request_timeout_sec"] is None
        assert (evidence.appendix_markdown in kw["user_prompt"]) == (index % 2 == 1)
        assert "Frozen semantic bindings." not in kw["system_prompt"]
    assert "Derive the necessary lemma input." in model.calls[2]["user_prompt"]
    assert "Derive the necessary lemma input." in model.calls[4]["user_prompt"]
    lock = proof_harness.resume.read(tmp_path / "synthesis/protocol_lock.json")
    assert lock["proof_rewriter_model"] == config.qwen().model
    assert lock["proof_candidate_policy"] == "one_model_candidate_per_cycle"


def test_shared_budget_accounts_for_exactly_two_additional_stages(tmp_path, monkeypatch):
    evidence, _, task, provider = setup(tmp_path)
    model = Models(evidence)
    monkeypatch.setattr(rewrite.pipeline, "_mandatory_budget_forced_model_call", model)
    result = execute(tmp_path, evidence, task, provider, None)
    budget = proof_harness.resume.read(tmp_path / "model_budget.json")
    assert result["state"] == "completed"
    assert budget["max_model_stages"] == len(budget["calls"]) == 4
    assert budget["token_caps"] == [32768, 49152]
    assert budget["thinking_token_budget"] == 16384
    assert all(kw["prompt_character_limit"] == 180000 for kw in model.calls)


def test_explicit_old_profile_makes_only_initial_calls(tmp_path):
    evidence, _, task, provider = setup(tmp_path)
    model = Models(evidence)
    result = execute(tmp_path, evidence, task, provider, model, final_qwen_revision=False)
    assert result["state"] == "completed" and len(model.calls) == 2
    assert not (tmp_path / "synthesis/final_revision.json").exists()


@pytest.mark.parametrize("mutation", ["hash", "appendix", "lemma", "marker", "audit"])
def test_revision_rejects_mutated_checkpoint(tmp_path, mutation):
    evidence, contract, task, _ = setup(tmp_path)
    proof = validation.materialize_and_lint("Use the lemma.\n" + contract.evidence_marker + "\nDone.", evidence, contract)
    path = tmp_path / "proof.md"
    row = {"state": "completed", "proof_audit_passed": True, "terminal_proof": str(path),
           "terminal_proof_sha256": core.base.sha256_text(proof)}
    if mutation == "appendix":
        proof = proof.replace(evidence.appendix_markdown, "Changed appendix")
    elif mutation == "lemma":
        proof = proof.replace(evidence.markdown, "Changed lemma")
    elif mutation == "marker":
        proof = contract.evidence_marker + "\n" + proof
    elif mutation == "audit":
        row["proof_audit_passed"] = False
    if mutation != "hash":
        row["terminal_proof_sha256"] = core.base.sha256_text(proof)
    else:
        row["terminal_proof_sha256"] = "wrong"
    core.base.write_text(path, proof)
    with pytest.raises(ValueError):
        final_revision.prepare(task=task, evidence=evidence, contract=contract, synthesis=row)


def test_reserved_revision_document_rejected_before_calls(tmp_path):
    evidence, _, task, provider = setup(tmp_path)
    task = replace(task, additional_documents={final_revision.CURRENT_DRAFT_DOCUMENT: "Unbound draft"})
    model = Models(evidence)
    with pytest.raises(ValueError, match="reserved"):
        execute(tmp_path, evidence, task, provider, model)
    assert not model.calls and not (tmp_path / "synthesis").exists()


def test_final_revision_has_no_benchmark_specific_inputs():
    source = Path(final_revision.__file__).read_text()
    for token in ("imo2026", "t07_r01", "v0324r43", "strict_score", "legacy_problem_specific", "3036e724"):
        assert token not in source
