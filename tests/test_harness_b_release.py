"""Promotion contracts; no inference calls."""
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
RELEASES=ROOT/'harnesses/imo_proof_pipeline/releases'


def test_previous_a_and_promoted_policy_are_exact():
    import hashlib
    assert hashlib.sha256((RELEASES/'1.7.0/release.json').read_bytes()).hexdigest()=='1374943fba9e8a39a734160565b926a5b3c869d79ea0b80ed8e5deebd34685b2'
    assert (RELEASES/'1.8.0/engine/source/experiments/local_math_verifier/refinement_bf_policy.py').read_bytes()==(ROOT/'harnesses/refinement_bf_ablation/policy.py').read_bytes()
    old=json.loads((RELEASES/'1.7.0/engine/freeze.json').read_text())['files']
    new=json.loads((RELEASES/'1.8.0/engine/freeze.json').read_text())['files']
    assert {k for k,v in old.items() if new[k]!=v}=={'source/scripts/run_v263_v290.py'}
    a=json.loads((RELEASES/'1.7.0/profile.json').read_text())
    b=json.loads((RELEASES/'1.8.0/profile.json').read_text())
    assert b['generation'].pop('refinement_bf')['harness_variant']=='B'
    assert a==b


def test_explicit_a_verifies_as_previous_version():
    result=subprocess.run([sys.executable,'-B',str(ROOT/'harnesses/proof_workshop/run.py'),'--release','1.7.0','--verify'],capture_output=True,text=True,check=True)
    value=json.loads(result.stdout)
    assert value['harness_variant']=='A' and value['implementation_release']=='1.7.0'


def test_b_real_routes_match_archived_b_and_metadata():
    code=r'''
import importlib.util,json,sys
from pathlib import Path
from scripts import run_v263_v290 as queue
from experiments.local_math_verifier import refinement_bf as b
_,backend=queue.load_engines()
root=Path(sys.argv[1]);sys.path.insert(0,str(root))
from harnesses.refinement_bf_ablation import worker
from dataclasses import asdict
assert [asdict(r) for r in b.build_routes(backend)]==[asdict(r) for r in worker.build_routes(backend)]
assert queue.refinement_policy_manifest()==b.manifest()
assert len(b.build_routes(backend))==14
'''
    subprocess.run([sys.executable,'-B','-c',code,str(ROOT)],cwd=RELEASES/'1.8.0/engine/source',check=True)
