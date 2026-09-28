"""Prevent the previously observed geometry export change from reentering V356."""
from pathlib import Path
import hashlib
import json
import pytest

HERE = Path(__file__).parent
BASELINES = json.loads((HERE/'consolidation_hashes.json').read_text())


@pytest.mark.parametrize('name', [
    'geometry_workflow.py', 'geometry_program.py', 'geometry_normalization.py',
    'root_workflow.py', 'root_classification.py', 'root_normalization.py',
    'polynomial_export.py', 'real_branches.py', 'radical_certificate.py',
    'rational_division.py', 'appendix_synthesis.py', 'final_revision.py',
    'rewrite.py', 'synthesis_core/prompts.py', 'synthesis_core/pipeline.py',
])
def test_v349_generation_and_exact_evidence_paths_are_unchanged(name):
    assert hashlib.sha256((HERE/name).read_bytes()).hexdigest() == BASELINES['geometry'][name]


@pytest.mark.parametrize('name', ['discrete_certificates.py', 'discrete_workflow.py',
    'discrete_resume.py', 'synthesis_core/tool_purpose.py'])
def test_v353_discrete_extension_is_unchanged(name):
    assert hashlib.sha256((HERE/name).read_bytes()).hexdigest() == BASELINES['discrete'][name]


def test_v355_geometry_exporter_is_absent():
    assert not (HERE/'geometry_derivation.py').exists()
    assert not (HERE/'geometry_export_resume.py').exists()
