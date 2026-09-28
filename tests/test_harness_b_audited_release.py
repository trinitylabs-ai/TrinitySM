"""Promotion and real three-pass orchestration checks without inference."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
RELEASES = ROOT / 'harnesses/imo_proof_pipeline/releases'


def test_original_releases_and_prompts_preserved():
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    assert sha(RELEASES / '1.7.0/release.json') == '1374943fba9e8a39a734160565b926a5b3c869d79ea0b80ed8e5deebd34685b2'
    assert sha(RELEASES / '1.8.0/release.json') == '4f4ee1cc8da3584ff46ad7a686275b8067dd32ed3d8dd081af50239015cfc1b7'
    assert sha(RELEASES / '1.9.0/release.json') == 'a3157d47c1865cf096cc61761f6eb2fada37b1ae80519ce778e3df611b391b9b'
    old = json.loads((RELEASES / '1.8.0/engine/freeze.json').read_text())['files']
    new = json.loads((RELEASES / '1.9.0/engine/freeze.json').read_text())['files']
    changed_source = {k for k, v in old.items() if k.startswith('source/') and new[k] != v}
    assert changed_source == {'source/cognitive_well_harness_v0_3_47_lazy_in_place_expansion_20260823/contracts.py'}
    for name in ('validation.py', 'bindings.py', 'AUDIT_PROMPT.md', 'BF_CUE.md'):
        assert (RELEASES / '1.9.0/engine/source/experiments/local_math_verifier/post_resolver_audit' / name).read_bytes() == (ROOT / 'harnesses/post_resolver_audit' / name).read_bytes()
    newest = json.loads((RELEASES / '1.10.0/engine/freeze.json').read_text())['files']
    changed_source = {k for k, v in new.items() if k.startswith('source/') and newest[k] != v}
    assert changed_source == {'source/experiments/local_math_verifier/post_resolver_audit/live.py',
                              'source/scripts/continue_r1_audited.py'}
    for name in ('validation.py', 'bindings.py', 'live.py', 'AUDIT_PROMPT.md', 'BF_CUE.md'):
        assert (RELEASES / '1.10.0/engine/source/experiments/local_math_verifier/post_resolver_audit' / name).read_bytes() == (ROOT / 'harnesses/post_resolver_audit' / name).read_bytes()
    before = json.loads((RELEASES / '1.9.0/profile.json').read_text())
    after = json.loads((RELEASES / '1.10.0/profile.json').read_text())
    assert after['generation']['post_resolver_audit']['workers_total'] == 24
    assert after['generation']['post_resolver_audit']['workers_per_model'] == {'gemma': 12, 'qwen': 12}
    after['generation']['post_resolver_audit'].pop('workers_per_model')
    after['generation']['post_resolver_audit']['workers_total'] = 4
    for model in ('gemma', 'qwen'):
        assert after['servers'][model]['flags']['--max-num-seqs'] == '12'
        after['servers'][model]['flags']['--max-num-seqs'] = before['servers'][model]['flags']['--max-num-seqs']
    assert before == after


@pytest.mark.parametrize('verdict', ['CERTIFIED', 'REJECTED'])
@pytest.mark.parametrize('veto', [False, True])
@pytest.mark.parametrize('release', ['1.9.0', '1.10.0'])
def test_real_three_passes_then_audit_and_collect_only(tmp_path, verdict, veto, release):
    result = subprocess.run([sys.executable, '-B', str(ROOT / 'tests/pipeline_regression_driver.py'),
                             str(tmp_path / 'run'), verdict, '--audited-b',
                             *(['--audit-veto'] if veto else []),
                             *(['--audited-b-1-9'] if release == '1.9.0' else [])],
                            cwd=ROOT, text=True, capture_output=True, timeout=90)
    assert result.returncode == 0, result.stdout + result.stderr


def test_audited_release_retains_r2_r1_and_lazy_when_later_stages_missing(tmp_path):
    result = subprocess.run([sys.executable, '-B', str(ROOT / 'tests/pipeline_regression_driver.py'),
                             str(tmp_path / 'run'), 'CERTIFIED', '--audited-b', '--recover'],
                            cwd=ROOT, text=True, capture_output=True, timeout=90)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize('mode', ['draft', 'audit'])
@pytest.mark.parametrize('release', ['1.9.0', '1.10.0'])
def test_real_chat_bf_temperatures_and_saved_bindings(tmp_path, mode, release):
    result = subprocess.run([sys.executable, '-B', str(ROOT / 'tests/audited_transport_driver.py'),
                             str(tmp_path / 'output'), mode, release], cwd=ROOT, text=True,
                            capture_output=True, timeout=45)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'TRANSPORT_OK ' + mode in result.stdout
