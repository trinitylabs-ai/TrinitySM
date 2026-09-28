import copy
import json
import threading

import pytest
import sympy as sp

from . import radical_certificate as radical, radical_packaging_trial as trial, radical_resume_synthesis as resume, saved_witness
from .test_saved_witness import UnitWitnessRenderingTests


@pytest.mark.parametrize("diagnostic", [{}, {"checked": False}, {"checked": False, "consistent": False},
                                       {"checked": True, "consistent": True}])
def test_consistency_does_not_block_verified_packaging(diagnostic):
    checks = {"certificate": {"verified": True}, "lift": {"state": "prepared"}, "consistency": diagnostic}
    assert trial.packaging_ready(checks, needs_lift=True)


def test_failed_certificate_missing_lift_and_known_contradiction_are_not_ready():
    assert not trial.packaging_ready({"certificate": {"verified": False}}, needs_lift=False)
    assert not trial.packaging_ready({"certificate": {"verified": True}}, needs_lift=True)
    assert not trial.packaging_ready({"certificate": {"verified": True},
        "consistency": {"checked": True, "consistent": False}}, needs_lift=False)


@pytest.mark.parametrize("needs_lift", [False, True])
@pytest.mark.parametrize("certificate", [
    {"state": "certificate_not_proved", "verified": False},
    {"state": "certificate_timeout", "verified": False},
    {"state": "timeout", "verified": False, "checked": False},
    {"state": "failed_closed", "error": "synthetic worker failure"},
    {"outcome": "PROVED"},
    {"verified": 1},
])
def test_unverified_certificate_skips_all_followups(tmp_path, monkeypatch, needs_lift, certificate):
    observed = []
    preview = tmp_path / "preview" if needs_lift else None
    monkeypatch.setattr(trial, "accepted_system", lambda *args: ({}, {},
        {"transform": True} if needs_lift else None,
        {"symbols": [], "generators": {}, "guards": {}}))

    def bounded(stage, request_path, preview_path, output, timeout, memory):
        observed.append(stage)
        assert stage == "certificate"
        assert (timeout, memory) == (600, 4096)
        return copy.deepcopy(certificate)

    def forbidden(*args, **kwargs):
        raise AssertionError("unverified certificate launched follow-up work")

    monkeypatch.setattr(trial, "bounded", bounded)
    monkeypatch.setattr(trial, "ThreadPoolExecutor", forbidden)
    result = trial.run(tmp_path / "request", preview, tmp_path / "out", on_ready=forbidden)
    assert observed == ["certificate"]
    assert result["state"] == "not_certified"
    assert result["checks"]["certificate"] == certificate
    assert result["checks"]["consistency"]["state"] == "skipped"
    assert ("lift" in result["checks"]) is needs_lift
    assert not result.get("packaging_started")
    assert not (tmp_path / "out/consistency").exists()
    assert not (tmp_path / "out/lift").exists()
    assert json.loads((tmp_path / "out/result.json").read_text()) == result
    manifest = json.loads((tmp_path / "out/manifest.json").read_text())
    assert manifest["check_scheduling_policy"] == trial.CHECK_SCHEDULING_POLICY


def test_certificate_exception_preserved_without_followups(tmp_path, monkeypatch):
    monkeypatch.setattr(trial, "accepted_system", lambda *args: ({}, {}, None,
        {"symbols": [], "generators": {}, "guards": {}}))

    def fail(stage, *args):
        assert stage == "certificate"
        raise RuntimeError("synthetic exception")

    monkeypatch.setattr(trial, "bounded", fail)
    result = trial.run(tmp_path / "request", None, tmp_path / "out")
    assert result["checks"]["certificate"] == {
        "state": "failed_closed", "error": "RuntimeError: synthetic exception"}
    assert result["checks"]["consistency"]["state"] == "skipped"
    assert result["state"] == "not_certified"


@pytest.mark.parametrize("needs_lift", [False, True])
def test_handoff_starts_before_consistency_finishes(tmp_path, monkeypatch, needs_lift):
    started = threading.Event()
    certificate_finished = threading.Event()
    lift_finished = threading.Event()
    observed = []
    monkeypatch.setattr(trial, "accepted_system", lambda *args: ({}, {},
        {"transform": True} if needs_lift else None,
        {"symbols": [], "generators": {}, "guards": {}}))

    def bounded(stage, *args):
        observed.append(stage)
        if stage == "certificate":
            certificate_finished.set()
            return {"verified": True}
        assert certificate_finished.is_set(), "follow-up ran before certificate verification"
        if stage == "consistency":
            assert started.wait(2), "handoff incorrectly waited for consistency"
            return {"checked": False, "consistent": False}
        assert stage == "lift" and needs_lift
        lift_finished.set()
        return {"state": "prepared"}

    def handoff(output):
        assert certificate_finished.is_set()
        assert not needs_lift or lift_finished.is_set()
        started.set()
        return {"started": True}

    monkeypatch.setattr(trial, "bounded", bounded)
    result = trial.run(tmp_path / "request", tmp_path / "preview" if needs_lift else None,
                       tmp_path / "out", on_ready=handoff)
    assert observed[0] == "certificate"
    assert set(observed) == ({"certificate", "consistency", "lift"} if needs_lift
                             else {"certificate", "consistency"})
    assert result["packaging_started"] and result["packaging_result"]["started"]
    assert result["state"] == "ready_for_packaging"


def test_late_consistency_contradiction_still_invalidates_result(tmp_path, monkeypatch):
    started = threading.Event()
    monkeypatch.setattr(trial, "accepted_system", lambda *args: ({}, {}, None,
        {"symbols": [], "generators": {}, "guards": {}}))

    def bounded(stage, *args):
        if stage == "certificate":
            return {"verified": True}
        assert stage == "consistency"
        assert started.wait(2)
        return {"checked": True, "consistent": False}

    monkeypatch.setattr(trial, "bounded", bounded)
    result = trial.run(tmp_path / "request", None, tmp_path / "out",
                       on_ready=lambda output: started.set() or {"started": True})
    assert result["packaging_started"]
    assert result["consistency_contradiction"]
    assert result["state"] == "contradictory_source"


def test_diagnostic_timeout_is_not_contradiction(tmp_path):
    trial.backends.write(tmp_path / "consistency/status.json", {"checked": False, "consistent": False})
    assert resume.diagnostic(tmp_path)["checked"] is False
    trial.backends.write(tmp_path / "consistency/status.json", {"checked": True, "consistent": False})
    with pytest.raises(ValueError, match="contradictory"):
        resume.diagnostic(tmp_path)


@pytest.mark.parametrize("factor_first", [False, True])
def test_radical_witness_reuses_full_laurent_exposition(tmp_path, factor_first):
    context, lift = UnitWitnessRenderingTests()._certificate(tmp_path / "ordinary")
    root = context.source_artifacts["source_lift"].parent
    transform = json.loads((root / "laurent_transform.json").read_text())
    guards = json.loads((root / "typed_guard_binding.json").read_text())
    system = radical.system_payload(*radical.backends.integration._decode_transform_payload(transform))
    verified = radical.export(system, tmp_path / "radical", timeout=5, memory=1024)
    assert verified["verified"]
    certificate = json.loads((tmp_path / "radical/certificate.json").read_text())
    markdown, record = saved_witness.render_laurent(arguments=context.arguments, lift=lift,
        transform=transform, guard_ledger=guards, replay=verified, radical_identity=certificate,
        factor_first=factor_first)
    assert record["verified"] and record["membership_kind"] == "guarded_radical"
    for text in ("inverse identity", "nonzero", "contradiction", "proving the lemma"):
        assert text in markdown
    assert saved_witness.audit_statement(markdown, record).startswith("## Algebraic lemma")
    changed = copy.deepcopy(transform)
    symbols = [sp.Symbol(name) for name in transform["symbols"]]
    changed["guards"]["unsupported"] = radical.laurent._payload(sp.Integer(2), symbols)
    with pytest.raises(ValueError, match="source witness"):
        saved_witness.render_laurent(arguments=context.arguments, lift=lift,
            transform=changed, guard_ledger=guards, replay=verified, radical_identity=certificate)


def test_factor_presentation_is_shorter_and_exact():
    x, y = sp.symbols("x y")
    original = sp.expand((x+y)**8 * (x-y)**3)
    definitions, compact = saved_witness._compact([original], [x,y], factor_first=True)
    resolved = {}
    for name, expression in definitions:
        resolved[name] = expression.xreplace(resolved)
    assert sp.expand(compact[0].xreplace(resolved)-original) == 0
    assert sum(len(sp.latex(item)) for _, item in definitions) + len(sp.latex(compact[0])) < len(sp.latex(original))


def test_unlimited_render_passes_none_to_process_wait(tmp_path, monkeypatch):
    observed = {}

    class Process:
        returncode = 0

        def wait(self, *, timeout):
            observed["timeout"] = timeout

    def popen(command, **kwargs):
        observed["command"] = command
        trial.backends.write(tmp_path / "render_result.json", {"verified": True})
        return Process()

    monkeypatch.setattr(resume.subprocess, "Popen", popen)
    assert resume.render_bounded(tmp_path / "trial", tmp_path, timeout=None, factor_first=True)["verified"]
    assert observed["timeout"] is None
    assert "--factor-first" in observed["command"]


def test_statement_only_does_not_invoke_certificate_render_or_factor(tmp_path, monkeypatch):
    request = {"arguments": {"symbols": ["x", "y"], "generators": {
        "D1": {"mul": [{"symbol": "x"}, {"symbol": "y"}]}}, "target": {"symbol": "x"}},
        "guard_program": {"source_nonzero": {"nonzero_y": {"symbol": "y"}}, "provenance_divisions": {}}}
    sample = tmp_path / "sample"
    request_path = sample / "cycles/cycle_01/03_execution/04_tool/request.json"
    trial_root, output = tmp_path / "trial", tmp_path / "output"
    admission = {"request_sha256": resume.stable_hash(request)}
    system = {"synthetic": True}
    certificate = {"synthetic_identity": True}
    trial.backends.write(trial_root / "certificate/identity/system.json", system)
    trial.backends.write(trial_root / "certificate/identity/certificate.json", certificate)
    trial.backends.write(trial_root / "certificate/identity/verification.json", {
        "verified": True, "system_sha256": resume.stable_hash(system),
        "certificate_sha256": resume.stable_hash(certificate)})
    for path in (request_path, trial_root / "request.json", trial_root / "manifest.json", sample / "manifest.json"):
        trial.backends.write(path, request)
    for name in ("theorem.md", "source_proof.md", "detection.md", "matcher.md"):
        resume.base.write_text(sample / "input" / name, "Synthetic source")
    for name in ("parser.json", "result.json", "input_formalization.md", "audit.md"):
        resume.base.write_text(request_path.parents[1] / "03_final_semantic_audit" / name, "Synthetic acceptance")
    monkeypatch.setattr(resume, "saved_inputs", lambda *_: (request_path, None, request, admission, None, system))

    def forbidden(*args, **kwargs):
        raise AssertionError("statement-only path attempted expensive presentation or replay")

    monkeypatch.setattr(radical, "render", forbidden)
    monkeypatch.setattr(radical, "replay", forbidden)
    monkeypatch.setattr(saved_witness, "render_laurent", forbidden)
    monkeypatch.setattr(sp, "factor", forbidden)
    result = resume.render_saved(trial_root, output, statement_only=True)
    assert result["verified"]
    record = resume.read(output / "saved_lemma_verification.json")
    assert record["presentation_kind"] == "statement_only"
    assert record["certificate_derivation_supplied"] is False
    assert record["model_must_prove_inserted_lemma"] is True
    provider = resume.SavedRadicalProvider(trial_root, output, {})
    assert provider.materialize().provider_id == "saved_guarded_radical_statement_only_v1"
    markdown = provider.markdown
    assert "x y=0" in markdown and "y\\ne0" in markdown and "T=x=0" in markdown
    resume.base.write_text(request_path, "changed")
    with pytest.raises(ValueError, match="source artifact changed"):
        provider.materialize()


def test_statement_only_policy_requires_written_derivation_and_audit():
    assert "not a supplied proof" in resume.STATEMENT_ONLY_POLICY
    assert "auditor must check that derivation too" in resume.STATEMENT_ONLY_POLICY
    assert "must fail the audit" in resume.STATEMENT_ONLY_POLICY


def test_skip_rendering_cannot_enable_factorization(tmp_path):
    with pytest.raises(ValueError, match="mutually exclusive"):
        resume.run(tmp_path / "trial", tmp_path / "output", 1, skip_rendering=True, factor_first=True)
