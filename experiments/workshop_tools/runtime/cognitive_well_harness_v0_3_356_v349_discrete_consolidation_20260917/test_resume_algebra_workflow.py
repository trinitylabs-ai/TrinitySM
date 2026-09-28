from types import SimpleNamespace

import pytest

from . import algebra_workflow as workflow, proof_harness as harness, resume_algebra_workflow as recovery
from .test_domain_ledger import draft, INPUTS
from .test_proof_harness import sources


def saved_prefix(tmp_path, monkeypatch):
    parsed = harness.fresh.division.parse_proposal(draft(), domain_inputs=INPUTS, require_domain_ledger=True)
    request = {key: parsed[key] for key in ("arguments", "guard_program")}
    admission = {"request_sha256": harness.resume.stable_hash(request), "parser": "PASS", "semantic": "ACCEPT"}
    monkeypatch.setattr(workflow.backends, "accepted_request", lambda path: (request, admission))
    radical = {"state": "not_certified", "admission": admission,
               "checks": {"certificate": {"state": "certificate_timeout", "verified": False}}}
    stages = [{"stage": "division", "result": {"verdict": "INCONCLUSIVE", "exact_verified": False}},
              {"stage": "guarded_radical", "result": radical}]
    old = tmp_path / "prefix"
    harness.rewrite.write_record(old / "request.json", request)
    harness.rewrite.write_record(old / "cascade_status.json", {"request_sha256": admission["request_sha256"], "stages": stages})
    harness.rewrite.write_record(old / "guarded_radical/result.json", radical)
    return old, parsed, request


def test_recovery_skips_completed_backends_without_claiming_proof(tmp_path, monkeypatch):
    old, parsed, request = saved_prefix(tmp_path, monkeypatch)
    monkeypatch.setattr(workflow.division, "invoke_tool", lambda *a, **k: pytest.fail("division repeated"))
    monkeypatch.setattr(workflow.packaging, "run", lambda *a, **k: pytest.fail("radical repeated"))
    calls = []
    monkeypatch.setattr(workflow.backends.integration, "bounded_preview_only", lambda **k:
        calls.append(k) or {"state": "ineligible"})
    result = workflow.execute(parsed, tmp_path / "new", config=harness.Config(), seed=1, documents={},
        select=lambda *a: pytest.fail("no proof to select"), should_stop=lambda: False, resume_after_radical=old)
    assert len(calls) == 1 and calls[0]["source_arguments"] == request["arguments"]
    assert result["state"] == "completed" and not result["exact_verified"]
    assert result["reused_stages"] == ["division", "guarded_radical"]
    with pytest.raises(ValueError, match="completed non-proving prefix"):
        workflow.resume_prefix(old, {**request, "guard_program": {}})
    prior = harness.resume.read(old / "guarded_radical/result.json")
    prior["checks"]["certificate"]["verified"] = True
    harness.rewrite.write_record(old / "guarded_radical/result.json", prior)
    with pytest.raises(ValueError, match="cannot be reused"):
        workflow.resume_prefix(old, request)


def test_recovery_entry_uses_saved_seed_and_inputs_no_model_calls(tmp_path, monkeypatch):
    problem, proof = sources(tmp_path)
    source, output = tmp_path / "source", tmp_path / "recovery"
    harness.run(problem_file=problem, proof_file=proof, output=source,
        config=harness.Config(batch_size=1, workers=1), seed=17)
    sample = source / "02_formalizations/sample_01"
    state = {"state": "failed_closed", "error": "RuntimeError: Laurent preview child exited 1",
             "cycle": 3, "master_seed": 4321}
    harness.rewrite.write_record(sample / "status.json", state)
    harness.rewrite.write_record(sample / "manifest.json", {})
    tool = sample / "cycles/cycle_03/03_execution/04_tool"
    for name in ("request.json", "cascade_status.json", "guarded_radical/result.json"):
        harness.rewrite.write_record(tool / name, {})
    task = SimpleNamespace(source_proof=proof.read_text(), theorem=INPUTS["theorem.md"], problem_id="synthetic")
    monkeypatch.setattr(workflow, "source_context", lambda *a: ({}, {}, task, {"accepted": True}, "draft", {}))
    monkeypatch.setattr(workflow, "resume_prefix", lambda *a: [])
    seen = []
    def execute(parsed, destination, **kw):
        seen.append(kw)
        assert parsed == {"accepted": True} and kw["resume_after_radical"] == tool
        assert kw["seed"] == 4321
        return {"state": "completed", "exact_verified": False}
    monkeypatch.setattr(workflow, "execute", execute)
    result = recovery.run(source, output, ["sample_01"])
    assert len(seen) == 1 and result["outcome"] == "NO_CERTIFIED_REWRITE"
    assert result["new_formalization_calls"] == 0 and result["new_semantic_audit_calls"] == 0
    assert harness.resume.read(sample / "status.json") == state
