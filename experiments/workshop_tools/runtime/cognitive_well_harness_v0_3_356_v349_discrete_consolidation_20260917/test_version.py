"""The successor must execute and report its own versioned implementation."""
import hashlib
import json
from pathlib import Path

from . import HARNESS_REVISION, HARNESS_VERSION, PARENT_HARNESS_VERSION
from . import matched_tools, pipeline, proof_harness, backend_comparison, gaussian_backend
from .polynomial_export import POLICY
from . import positive_multiple
from . import geometry_domain_feedback, real_branches
from .synthesis_core import tool_purpose


def test_version_identity_and_local_implementation():
    assert HARNESS_VERSION == "0.3.356"
    assert HARNESS_REVISION == "0.3.356+v349-discrete-consolidation.1"
    assert PARENT_HARNESS_VERSION == "0.3.349"
    assert pipeline.HARNESS_VERSION == "0.3.356"
    assert proof_harness.HARNESS_REVISION == "0.3.356+v349-discrete-consolidation.1"
    assert matched_tools.SCHEMA == "v0326-matched-exact-computation-v1"
    assert pipeline.synthesis_pipeline.tool_purpose is tool_purpose
    assert pipeline.synthesis_pipeline.prompts.tool_purpose is tool_purpose
    assert tool_purpose.EXPLICIT_SOURCE_POLICY == "unique_whitespace_then_paired_dollar_quote_v2"
    root = Path(__file__).parent.resolve()
    for module in (matched_tools, pipeline, proof_harness):
        assert Path(module.__file__).resolve().parent == root
    assert backend_comparison.gaussian_backend is gaussian_backend
    assert Path(gaussian_backend.__file__).resolve().parent == root


def test_package_manifest_matches_source_files():
    root = Path(__file__).parent
    release = json.loads((root / "release.json").read_text())
    assert release["version"] == "0.3.356"
    assert release["parent_version"] == "0.3.349"
    assert release["automatic_geometry_integration"] is True
    assert release["revision"] == "0.3.356+v349-discrete-consolidation.1"
    assert release["geometry_normalization"] == "geometry-structural-syntax-v5"
    assert release['shared_feedback']['policy']=='seeded-single-peer-feedback-v2'
    assert release['shared_feedback']['max_prompt_characters']==6000
    assert release['source_binding']=='exact-source-spans-v2'
    assert release['relative_orientation']=='replayed-relative-polynomial-sign-v1'
    assert release['polynomial_export'] == POLICY
    assert release['positive_multiple_nonzero']['policy'] == positive_multiple.POLICY
    assert release['geometry_domain_feedback']['policy'] == geometry_domain_feedback.POLICY
    assert release['geometry_domain_feedback']['changes_acceptance_rules'] is False
    assert release['real_branch_certificate']['schema'] == real_branches.SCHEMA
    assert release['geometry_backend_order'][0] == real_branches.SCHEMA
    assert release['real_branch_certificate']['max_nodes'] == real_branches.MAX_NODES
    assert release['real_conditions'] == 'preserve-admitted-real-conditions-v1'
    actual = {str(p.relative_to(root)) for p in root.rglob('*')
              if p.is_file() and p.suffix in {'.py', '.md'} and '__pycache__' not in p.parts}
    assert set(release["files_sha256"]) == actual
    for name, expected in release["files_sha256"].items():
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == expected, name


def test_public_result_reports_v328_with_compatible_schema(tmp_path):
    result = proof_harness.run_matched_tool(operation="rational_identity",
        arguments_markdown="```exact-args\nsymbols = NONE\ncheck = identity :: (eq (mul 7 8) 56)\n```",
        output=tmp_path / "versioned_result")
    assert result["harness_revision"] == "0.3.356+v349-discrete-consolidation.1"
    assert result["schema"] == "v0326-matched-exact-computation-v1"
    assert result["verdict"] == "IDENTITY_VERIFIED"
