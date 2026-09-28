from dataclasses import replace
import json

import pytest
import sympy as sp

from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906 import contracts, prompts, validation, pipeline as core
from . import radical_certificate as radical, radical_resume_synthesis as resume, saved_witness
from .test_saved_witness import UnitWitnessRenderingTests


def fixture(tmp_path):
    source = tmp_path / "source.md"
    source.write_text("If x=y then x-y=0.")
    appendix = "# Appendix A — Proof of the algebraic lemma\n\nSubtract y from x=y to obtain x-y=0."
    statement = "**Lemma.** If x=y then x-y=0.\n\n" + "\n".join(
        f"For integer index {j}, the same conclusion implies {j}(x-y)=0." for j in range(1,21))
    evidence = contracts.EvidenceBundle("synthetic_appendix", "VERIFIED_SUPPORT",
        statement, {"verified": True, "appendix_sha256": core.base.sha256_text(appendix)},
        {"decision": "PROVED"}, {"source": source}, appendix)
    contract = contracts.SynthesisContract("[[VERIFIED_EXACT_EVIDENCE]]", ("Derive and apply the lemma.",),
        (), (), "Check the application and the supplied appendix.", semantic_conclusion_only=True)
    task = contracts.TaskInputs("synthetic", source.read_text(), "We need to show x-y=0.", {})
    return evidence, contract, task


def test_appendix_inserted_once_at_end_and_tampering_rejected(tmp_path):
    evidence, contract, _ = fixture(tmp_path)
    raw = "We have x=y.\n\n" + contract.evidence_marker + "\n\nAppendix A proves the lemma, giving the conclusion."
    proof = validation.materialize_and_lint(raw, evidence, contract)
    assert proof.endswith(evidence.appendix_markdown)
    assert proof.count(evidence.appendix_markdown) == 1
    assert validation.lint_report(raw, evidence, contract)["appendix_count"] == 1
    for changed in (replace(evidence, appendix_markdown=""), replace(evidence, appendix_markdown="changed")):
        with pytest.raises(ValueError, match="appendix"):
            validation.materialize_and_lint(raw, changed, contract)
    with pytest.raises(ValueError, match="copy"):
        validation.materialize_and_lint(raw + "\n\n" + evidence.appendix_markdown, evidence, contract)


def test_repair_prompt_does_not_duplicate_appendix(tmp_path):
    evidence, contract, task = fixture(tmp_path)
    previous = validation.materialize_and_lint("Setup.\n" + contract.evidence_marker + "\nConclusion.", evidence, contract)
    prompt = prompts.rewrite_prompt(task=task, evidence=evidence, contract=contract,
        previous_proof=previous, prior_audit={"issues": ["Explain the substitution."]})
    assert prompt.count(evidence.appendix_markdown) == 1
    assert "do not copy the appendix or re-prove its internal" in prompt
    assert prompt.index("# Untrusted Previous Proof") < prompt.index(evidence.appendix_markdown)
    audit = prompts.audit_prompt(task=task, evidence=evidence, proof=previous)
    assert audit.count(evidence.appendix_markdown) == 1


@pytest.mark.parametrize("visible", [True, False])
def test_core_synthesis_audits_the_full_proof_with_appendix(tmp_path, visible):
    evidence, contract, task = fixture(tmp_path)
    evidence = replace(evidence, appendix_in_rewriter_prompt=visible)

    class Provider:
        provider_id = evidence.provider_id
        def materialize(self):
            return evidence

    calls = []
    def model_call(**kwargs):
        calls.append(kwargs["stage"])
        if kwargs["stage"].endswith("rewrite"):
            assert (evidence.appendix_markdown in kwargs["user_prompt"]) is visible
            text = "Since x=y, apply the following lemma proved in Appendix A.\n\n" + contract.evidence_marker + "\n\nThus x-y=0."
        else:
            assert kwargs["user_prompt"].endswith(evidence.appendix_markdown)
            text = "# Decision\n\nPASS\n\n# Checks\n\n" + "\n".join(
                "- " + name + ": PASS" for name in core.protocol.PROOF_AUDIT_CHECKS) + "\n\n# Issues\n\nNONE"
        return text, kwargs["parser"](text), {}

    role = core.base.Role("http://127.0.0.1:1/v1", "fake", .1, None)
    result = core.run(adapter=contracts.SynthesisAdapter("synthetic", task, Provider(), contract),
        output_dir=tmp_path / "synthesis", gemma=role, qwen=role, master_seed=1, model_call=model_call)
    assert result["state"] == "completed" and len(calls) == 2
    lock = json.loads((tmp_path / "synthesis/protocol_lock.json").read_text())
    assert lock["appendix_sha256"] == evidence.verification["appendix_sha256"]
    assert lock["appendix_in_rewriter_prompt"] is visible


def test_attach_only_omits_body_on_first_and_repair_prompts_but_attaches_it(tmp_path):
    evidence, contract, task = fixture(tmp_path)
    evidence = replace(evidence, appendix_in_rewriter_prompt=False)
    raw = "Apply the lemma proved in Appendix A.\n" + contract.evidence_marker + "\nThus the conclusion follows."
    proof = validation.materialize_and_lint(raw, evidence, contract)
    for previous in (None, proof):
        prompt = prompts.rewrite_prompt(task=task, evidence=evidence, contract=contract,
            previous_proof=previous, prior_audit={"issues": ["Derive the source condition."]})
        assert evidence.appendix_markdown not in prompt
        assert "intentionally omitted from your input" in prompt
        assert "Subtract y from x=y" not in prompt
    assert proof.endswith(evidence.appendix_markdown)
    assert prompts.audit_prompt(task=task, evidence=evidence, proof=proof).endswith(evidence.appendix_markdown)
    with pytest.raises(ValueError, match="actual appendix"):
        validation.validate_appendix(replace(evidence, appendix_markdown=""))


def test_queue_waits_for_terminal_predecessor_without_modifying_it(tmp_path, monkeypatch):
    source = tmp_path / "previous"
    resume.backends.write(source / "status.json", {"state": "running"})
    sleeps = []
    def sleep(seconds):
        sleeps.append(seconds)
        resume.backends.write(source / "result.json", {"state": "failed_closed"})
    monkeypatch.setattr(resume.time, "sleep", sleep)
    dependency = resume.wait_for_previous(source)
    assert sleeps == [10] and dependency["state"] == "failed_closed"
    assert resume.read(source / "status.json") == {"state": "running"}


def test_table_renderer_avoids_factor_and_cse_and_rejects_false_identity(tmp_path, monkeypatch):
    x = sp.Symbol("x")
    system = radical.system_payload([x], [("eq", x*x)], x, {})
    assert radical.export(system, tmp_path / "exact", timeout=5, memory=1024)["verified"]
    certificate = json.loads((tmp_path / "exact/certificate.json").read_text())
    def forbidden(*args, **kwargs):
        raise AssertionError("slow factorization or CSE was called")
    monkeypatch.setattr(sp, "factor", forbidden)
    monkeypatch.setattr(saved_witness, "_compact", forbidden)
    markdown, record = radical.render(system, certificate, table_multipliers=True)
    assert record["coefficient_tables_reparsed"]
    assert "```text" in markdown and "Exact expansion" in markdown and "contradiction" in markdown
    certificate["multipliers"][0]["terms"] = []
    with pytest.raises(ValueError, match="re-expansion"):
        radical.render(system, certificate, table_multipliers=True)


def test_full_laurent_table_appendix_retains_lift_and_source_conclusion(tmp_path):
    context, lift = UnitWitnessRenderingTests()._certificate(tmp_path / "ordinary")
    root = context.source_artifacts["source_lift"].parent
    transform = json.loads((root / "laurent_transform.json").read_text())
    guards = json.loads((root / "typed_guard_binding.json").read_text())
    system = radical.system_payload(*radical.backends.integration._decode_transform_payload(transform))
    verified = radical.export(system, tmp_path / "radical", timeout=5, memory=1024)
    certificate = json.loads((tmp_path / "radical/certificate.json").read_text())
    markdown, record = saved_witness.render_laurent(arguments=context.arguments, lift=lift, transform=transform,
        guard_ledger=guards, replay=verified, radical_identity=certificate, table_multipliers=True)
    assert record["coefficient_tables_reparsed"] and not record["horner_and_cse_reexpanded"]
    assert markdown.count(saved_witness.STATEMENT_END) == 1
    assert "inverse identities" in markdown and "contradiction" in markdown and "proving the lemma" in markdown


def test_coefficient_table_handles_gaussian_rationals_and_common_monomial():
    x, y = sp.symbols("x y")
    value = sp.expand(x**3 * ((sp.Rational(1,3)+sp.I/7)*y**2 - 2*y + 5))
    payload = radical.laurent._payload(value, [x,y])
    assert sp.expand(radical.payload_polynomial(payload, [x,y]).as_expr()-value) == 0
    text = radical.coefficient_table(payload, [x,y], sp.Symbol("M"))
    assert "1/3,1/7|2" in text and "x^{3}" in text
    assert "x^{3}" in text and "no variables" not in text
