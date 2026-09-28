from pathlib import Path

import pytest

from . import after_fusion as fusion, proof_harness as harness


def make_handoff(tmp_path, monkeypatch):
    problem, proof = tmp_path / "problem.json", tmp_path / "proof.md"
    harness.rewrite.write_record(problem, {"problem_id": "synthetic", "statement": "If x=y, prove x-y=0."})
    harness.base.write_text(proof, "The desired identity follows by an omitted computation.")
    fields = {
        "verdict": "REPAIR_NEEDED",
        **{f"reviewer_{i}_assessment": "DEFECT_VALIDATED | The calculation is missing." for i in range(1, 4)},
        "decisive_location": proof.read_text().strip(),
        "failed_obligation": "Derive the stated identity.",
        "independent_validation": "The needed calculation is absent.",
        "impact_on_proof": "The conclusion is unsupported.",
        "repair_scope": "LOCAL", "resolver_brief": "Supply the missing calculation.",
        "preservable_material": "The hypotheses and target."}
    final = "FUSION_REPAIR_NEEDED\n" + "\n".join(f"{key}: {value}" for key, value in fields.items()) + "\nEND_FUSION_REPAIR_NEEDED"
    task = {"problem_id": "synthetic", "problem_path": str(problem), "proof_path": str(proof),
        "problem_sha256": harness.base.sha256_text("If x=y, prove x-y=0."),
        "proof_sha256": harness.base.sha256_text(proof.read_text().strip())}
    record = {"task": task, "final": final, "final_sha256": harness.base.sha256_text(final),
              "parsed": fusion.parse_fusion(final)}
    assert record["parsed"]["valid"], record["parsed"]
    path = tmp_path / "effective_fusion_result.json"
    harness.rewrite.write_record(path, record)
    # Gate re-expansion itself is covered by the existing repair-boundary suite;
    # this fixture isolates the downstream handoff, including rejected briefs.
    monkeypatch.setattr(fusion, "verify_existing_gate", lambda *a: ("REJECTED", []))
    return path, record


def test_real_shape_handoff_is_bound_and_gate_status_is_not_model_input(tmp_path, monkeypatch):
    path, record = make_handoff(tmp_path, monkeypatch)
    result = fusion.run(fusion_result=path, output=tmp_path / "out", seed=7)
    assert result["state"] == "prepared" and result["upstream_model_calls"] == 0
    assert result["brief_gate_disposition"] == "REJECTED"
    packet = (tmp_path / "out/input/fusion_packet.md").read_text()
    assert record["final"] in packet
    assert "REJECTED" not in packet
    assert "Supply the missing calculation." in packet
    plan = fusion.saved.read(tmp_path / "out/tool_rewrite/manifest.json")
    assert plan["associated_documents"] == ["fusion_packet.md"] and not plan["preloaded_certificate"]


@pytest.mark.parametrize("field", ["final_sha256", "proof_sha256", "problem_sha256"])
def test_handoff_tampering_fails_before_any_model(tmp_path, monkeypatch, field):
    path, record = make_handoff(tmp_path, monkeypatch)
    target = record if field == "final_sha256" else record["task"]
    target[field] = "changed"
    harness.rewrite.write_record(path, record)
    with pytest.raises(ValueError, match="mismatch"):
        fusion.load(path)


def test_persisted_callback_and_terminal_proof_publication(tmp_path, monkeypatch):
    path, record = make_handoff(tmp_path, monkeypatch)
    def downstream(**kw):
        assert kw["execute_models"] and kw["problem_id"] == "synthetic"
        assert not kw.get("associated") and kw["fusion_result"] == path
        assert fusion.load(kw["fusion_result"]).fusion == record["final"]
        proof = kw["output"] / "rewritten_proof.md"
        text = "Main proof.\n\n# Appendix A\n\nComplete exact lemma proof."
        harness.base.write_text(proof, text)
        return {"state": "completed", "outcome": "REWRITTEN_AUDIT_PASS", "rewritten_proof": str(proof),
                "rewritten_proof_sha256": harness.base.sha256_text(text)}
    monkeypatch.setattr(harness, "run", downstream)
    result = fusion.run_after_fusion_result({**record, "_v290_effective_result_path": str(path)},
        output=tmp_path / "out", seed=8, execute_models=True)
    assert result["outcome"] == "REWRITTEN_AUDIT_PASS" and not result["needs_regular_resolver"]
    assert Path(result["rewritten_proof"]).read_text().count("# Appendix A") == 1
    with pytest.raises(ValueError, match="differs"):
        fusion.run_after_fusion_result({**record, "final": "changed", "_v290_effective_result_path": str(path)},
            output=tmp_path / "bad", seed=9)


def test_declined_tool_returns_to_host_resolver_without_changed_fusion(tmp_path, monkeypatch):
    path, record = make_handoff(tmp_path, monkeypatch)
    seen = []
    monkeypatch.setattr(harness, "run", lambda **k: {"state": "completed", "outcome": "NO_TOOL"})
    result = fusion.run(fusion_result=path, output=tmp_path / "out", seed=1, execute_models=True,
        fallback=lambda handoff: seen.append(handoff.fusion) or {"state": "host_resolver_called"})
    assert seen == [record["final"]] and result["fallback_used"]
    assert not (tmp_path / "out/rewritten_proof.md").exists()


def test_mechanical_failure_does_not_use_fallback(tmp_path, monkeypatch):
    path, _ = make_handoff(tmp_path, monkeypatch)
    monkeypatch.setattr(harness, "run", lambda **k: {"state": "failed_closed", "error": "binding mismatch"})
    result = fusion.run(fusion_result=path, output=tmp_path / "out", seed=1, execute_models=True,
        fallback=lambda *a: pytest.fail("mechanical failures must not become model decisions"))
    assert result["state"] == "failed_closed" and not result["needs_regular_resolver"]


def test_missing_mandatory_gate_is_not_silently_bypassed(tmp_path):
    with pytest.raises(ValueError, match="completed mandatory"):
        fusion.verify_existing_gate(tmp_path / "effective_fusion_result.json", {"task": {}}, "problem", "proof")
