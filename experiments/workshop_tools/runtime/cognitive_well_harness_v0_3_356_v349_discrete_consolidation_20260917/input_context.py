"""Generation context from a verified producer, never arbitrary auxiliary files.

The primary problem/proof are caller-supplied. This policy excludes separate
reference/grade documents; it cannot determine whether a caller mislabels a gold
solution as the primary proof. No mathematical content is edited or filtered.
"""
from pathlib import Path

POLICY = "bound-fusion-only-no-reference-loader-v1"
FUSION_DOCUMENT = "fusion_packet.md"


def from_fusion(path, problem, proof):
    from . import after_fusion, proof_harness as harness

    if path is None:
        return {}, {"policy": POLICY, "source": "none"}
    handoff = after_fusion.load(Path(path))
    source_problem = harness.acquisition.v0220.load_problem(handoff.problem_path,
        explicit_problem_id=handoff.problem_id)
    source_proof = handoff.proof_path.read_text().strip()
    if (handoff.problem_id != problem.problem_id
            or source_problem.statement.strip() != problem.statement.strip()
            or source_proof != proof.strip()):
        raise ValueError("associated Fusion binds another problem or proof")
    packet = after_fusion.render_packet(handoff)
    handoff.validate()
    return {FUSION_DOCUMENT: packet}, {
        "policy": POLICY, "source": "verified_effective_fusion",
        "fusion_result": str(Path(path).resolve()),
        "source_artifacts": handoff.artifacts,
        "document_sha256": harness.base.sha256_text(packet),
    }


def load_saved(source, manifest):
    """Reject unbound legacy attachments before opening any auxiliary file."""
    from . import proof_harness as harness

    names = manifest.get("associated_documents", [])
    provenance = manifest.get("associated_provenance")
    if names not in ([], [FUSION_DOCUMENT]):
        raise ValueError("unverified associated documents are not allowed during resume")
    if names and (not isinstance(provenance, dict)
            or provenance.get("policy") != POLICY
            or provenance.get("source") != "verified_effective_fusion"):
        raise ValueError("saved associated documents lack verified Fusion provenance")
    if not names and provenance not in (None, {"policy": POLICY, "source": "none"}):
        raise ValueError("associated provenance does not match the saved documents")
    expected = {"input/problem.json", "input/source_proof.md"}
    expected.update("input/associated/" + name for name in names)
    if set(manifest.get("input_artifacts", {})) != expected:
        raise ValueError("unexpected generation input artifact names")
    if names:
        problem = harness.acquisition.v0220.load_problem(source / "input/problem.json")
        proof = (source / "input/source_proof.md").read_text().strip()
        documents, replay = from_fusion(provenance["fusion_result"], problem, proof)
        if replay != provenance:
            raise ValueError("associated Fusion provenance changed")
    else:
        documents = {}
    for name, digest in manifest["input_artifacts"].items():
        if harness.base.sha256_file(source / name) != digest:
            raise ValueError("source harness input drift")
    for name, text in documents.items():
        if (source / "input/associated" / name).read_text().strip() != text:
            raise ValueError("associated snapshot differs from verified Fusion")
    return documents
