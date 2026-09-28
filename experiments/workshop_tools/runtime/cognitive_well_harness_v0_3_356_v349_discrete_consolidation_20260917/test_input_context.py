"""Synthetic input-provenance regressions; no model or benchmark access."""
from pathlib import Path

import pytest

from . import after_fusion as fusion, input_context as context, proof_harness as harness
from .test_after_fusion import make_handoff
from .test_proof_harness import sources


@pytest.mark.parametrize("name", ["gold.md", "reference_solution.md", "grading.md", "fusion_packet.md"])
def test_arbitrary_associated_files_rejected_before_any_read(tmp_path, monkeypatch, name):
    monkeypatch.setattr(Path, "read_text", lambda *a, **k: pytest.fail("an input was opened"))
    monkeypatch.setattr(harness, "acquire", lambda *a, **k: pytest.fail("model called"))
    with pytest.raises(ValueError, match="associated documents are disabled"):
        harness.run(problem_file=tmp_path / "problem.json", proof_file=tmp_path / "proof.md",
            output=tmp_path / "out", associated=[tmp_path / name], execute_models=True)
    assert not (tmp_path / "out").exists()


def test_arbitrary_context_name_is_not_forwarded():
    with pytest.raises(ValueError, match="not model context"):
        harness.associated_context({"gold.md": "REFERENCE_CANARY"})


def test_primary_only_and_legacy_primary_only_snapshots_resume(tmp_path):
    problem, proof = sources(tmp_path)
    source = tmp_path / "source"
    manifest = harness.run(problem_file=problem, proof_file=proof, output=source)
    assert manifest["generation_reference_reads"] is False
    assert manifest["associated_provenance"] == {"policy": context.POLICY, "source": "none"}
    assert context.load_saved(source, manifest) == {}
    manifest.pop("associated_provenance")
    assert context.load_saved(source, manifest) == {}


def test_verified_fusion_context_round_trips_without_reference_fields(tmp_path, monkeypatch):
    path, record = make_handoff(tmp_path, monkeypatch)
    fusion.run(fusion_result=path, output=tmp_path / "out", seed=7)
    source = tmp_path / "out/tool_rewrite"
    manifest = harness.resume.read(source / "manifest.json")
    documents = context.load_saved(source, manifest)
    assert documents == {context.FUSION_DOCUMENT: fusion.render_packet(fusion.load(path))}
    assert record["final"] in documents[context.FUSION_DOCUMENT]
    assert manifest["associated_provenance"]["source"] == "verified_effective_fusion"
    assert manifest["associated_provenance"]["fusion_result"] == str(path.resolve())
    assert (tmp_path / "out/input/fusion_packet.md").read_text().strip() == documents[context.FUSION_DOCUMENT]


def test_fusion_cannot_bind_a_different_primary_proof(tmp_path, monkeypatch):
    path, record = make_handoff(tmp_path, monkeypatch)
    other = tmp_path / "different_proof.md"
    harness.base.write_text(other, "An unrelated submitted proof.")
    with pytest.raises(ValueError, match="another problem or proof"):
        harness.run(problem_file=Path(record["task"]["problem_path"]), proof_file=other,
            output=tmp_path / "out", fusion_result=path)
    assert not (tmp_path / "out").exists()


def test_fusion_supports_problem_id_supplied_by_handoff(tmp_path, monkeypatch):
    path, record = make_handoff(tmp_path, monkeypatch)
    problem = Path(record["task"]["problem_path"])
    payload = harness.resume.read(problem)
    payload.pop("problem_id")
    harness.rewrite.write_record(problem, payload)
    result = fusion.run(fusion_result=path, output=tmp_path / "out", seed=7)
    assert result["state"] == "prepared", result
    source = tmp_path / "out/tool_rewrite"
    assert context.load_saved(source, harness.resume.read(source / "manifest.json"))


@pytest.mark.parametrize("names", [["gold.md"], ["../reference.md"], ["fusion_packet.md"]])
def test_legacy_unbound_attachments_rejected_without_reading(tmp_path, monkeypatch, names):
    monkeypatch.setattr(Path, "read_text", lambda *a, **k: pytest.fail("unbound file opened"))
    with pytest.raises(ValueError, match="associated documents"):
        context.load_saved(tmp_path, {"associated_documents": names})


def test_unexpected_snapshot_path_rejected_without_reading(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "read_text", lambda *a, **k: pytest.fail("unexpected file opened"))
    monkeypatch.setattr(harness.base, "sha256_file", lambda *a: pytest.fail("unexpected file hashed"))
    with pytest.raises(ValueError, match="artifact names"):
        context.load_saved(tmp_path, {"associated_documents": [],
            "input_artifacts": {"../reference_solution.md": "0" * 64}})


def test_modified_snapshot_not_accepted_even_with_updated_local_hash(tmp_path, monkeypatch):
    path, _ = make_handoff(tmp_path, monkeypatch)
    fusion.run(fusion_result=path, output=tmp_path / "out", seed=7)
    source = tmp_path / "out/tool_rewrite"
    manifest = harness.resume.read(source / "manifest.json")
    name = "input/associated/fusion_packet.md"
    harness.base.write_text(source / name, "REFERENCE_CANARY")
    manifest["input_artifacts"][name] = harness.base.sha256_file(source / name)
    with pytest.raises(ValueError, match="differs from verified Fusion"):
        context.load_saved(source, manifest)


def test_changed_fusion_provenance_rejected(tmp_path, monkeypatch):
    path, _ = make_handoff(tmp_path, monkeypatch)
    fusion.run(fusion_result=path, output=tmp_path / "out", seed=7)
    source = tmp_path / "out/tool_rewrite"
    manifest = harness.resume.read(source / "manifest.json")
    manifest["associated_provenance"]["document_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="provenance changed"):
        context.load_saved(source, manifest)
