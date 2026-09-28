"""B 1.12 selection contracts and real pipeline integration; no model calls."""
import json
from pathlib import Path
import subprocess
import sys
import pytest
from test_public_reproduction import pipeline, ROOT
from cross_lane_replay import response

a = pipeline.audit_module('1.12.0')
v = pipeline.voter_module('1.12.0')
CASE = dict(baseline_sha256='a'*64, candidate_sha256='b'*64, changes=[dict(id='D001')])

@pytest.mark.parametrize('text', ['Decision: ACCEPT_CANDIDATE', '**Decision:** ACCEPT_CANDIDATE\n## Target obligation\nStatus: UNRESOLVED'])
def test_explicit_choice_survives_body_diagnostics(text):
    result = a.validate_audit(text, CASE)
    assert result['valid'] and result['decision'] == a.ACCEPT
    assert not result['body_validation_valid'] and result['body_validation_errors']

@pytest.mark.parametrize('text', ['Decision: A', 'Decision: ACCEPT_CANDIDATE or KEEP_BASELINE',
    'Decision: ACCEPT_CANDIDATE\nDecision: ACCEPT_CANDIDATE', 'Decision: ACCEPT_CANDIDATE\nDecision: KEEP_BASELINE', 'No decision'])
def test_missing_or_ambiguous_raw_choice_rejects(text):
    result = a.validate_audit(text, CASE)
    assert not result['valid'] and result['decision'] == a.KEEP

def test_unanimity_and_hard_identity():
    votes = [dict(a.validate_audit('Decision: ACCEPT_CANDIDATE', CASE), original_case_id='C', model_key=m, order=o)
             for m in ('gemma', 'qwen') for o in ('forward', 'reverse')]
    assert a.select_candidate('C', votes, tuple(a.MODELS))['decision'] == a.ACCEPT
    assert a.select_candidate('C', votes[:3], tuple(a.MODELS))['decision'] == a.KEEP
    assert a.select_candidate('C', votes[:3]+[votes[0]], tuple(a.MODELS))['decision'] == a.KEEP
    votes[-1]['decision'] = a.KEEP
    assert a.select_candidate('C', votes, tuple(a.MODELS))['decision'] == a.KEEP
    assert not a.validate_audit('Decision: ACCEPT_CANDIDATE', {**CASE, 'candidate_sha256':'forged'})['valid']

def test_latest_voter_full_schedule_resume_and_bindings(tmp_path):
    candidates=[]
    for i in range(4):
        p=tmp_path/f'lane{i}.md';p.write_text(f'Proof {i}.')
        candidates.append(dict(candidate_id=f'lane{i}', proof_path=str(p), proof_sha256=v.digest(p.read_bytes()),
                               selected_stage='refinement_2', grade='SECRET_EVALUATION'))
    runtime=dict(raw_seed_offset=0, seed_namespace=v.DEFAULT_NAMESPACE, model_timeout_sec=600,
                 gemma_endpoint='http://127.0.0.1:8030/v1',qwen_endpoint='http://127.0.0.1:8027/v1')
    root=tmp_path/'voter';v.prepare(root,'P','Prove X.',candidates,runtime,'a'*64)
    cfg,m,tasks=v.verify(root)
    assert len(tasks)==24 and m['comparison_runtime']['workers_per_model']=={'gemma':12,'qwen':12}
    assert m['comparison_runtime']['timeout_policy']['logical_limit_seconds']==600
    assert 'SECRET_EVALUATION' not in ''.join(p.read_text() for p in root.rglob('*.md'))
    calls=[]
    result=v.run(root,lambda **kw:(calls.append(kw) or response(kw)))
    assert len(calls)==24 and result['state']=='completed'
    assert result['summaries']['combined']['winner']==m['seed_derived_candidate_order'][0]
    v.run(root,lambda **kw:pytest.fail('Duplicate inference'))
    path=root/'cases'/tasks[0]['case_id']/'audit/call_result.json'
    d=v.read(path);d['text']+='forged';v.write(path,d)
    assert v.collect(root)['state']=='incomplete'

@pytest.mark.parametrize('veto',[False,True])
def test_full_three_refinements_audit_then_voter(tmp_path,veto):
    proc=subprocess.run([sys.executable,'-B',str(ROOT/'tests/pipeline_regression_driver.py'),
        str(tmp_path/'run'),'CERTIFIED','--selection-upgrade-b','--voter-b',*(['--audit-veto'] if veto else [])],
        cwd=ROOT,text=True,capture_output=True,timeout=90)
    assert proc.returncode==0,proc.stdout+proc.stderr
    data=json.loads((tmp_path/'run/final_results.json').read_text())
    assert data['implementation_release']=='1.12.0' and data['completed_proofs']==4
    assert len(data['problem_selections'][0]['vote_table'])==24
    assert data['problem_selections'][0]['policy_id']==v.POLICY_ID
    for lane in data['lanes']:
        assert lane['selected_stage']==('refinement_2' if veto and lane['candidate_id']=='t10_r01' else 'refinement_3')

def test_timeout_transports():
    proc=subprocess.run([sys.executable,'-B',str(ROOT/'tests/selection_timeout_driver.py')],
                        cwd=ROOT,text=True,capture_output=True,timeout=60)
    assert proc.returncode==0,proc.stdout+proc.stderr
    assert json.loads(proc.stdout)['check_count']==8

def test_release_retains_generation_and_historical_identity():
    releases=ROOT/'harnesses/imo_proof_pipeline/releases'
    old=json.loads((releases/'1.11.0/engine/freeze.json').read_text())['files']
    new=json.loads((releases/'1.12.0/engine/freeze.json').read_text())['files']
    for name,digest in old.items():
        if name.startswith('source/') and name != 'source/scripts/continue_r1_audited.py' and not any(part in name for part in ('/cross_lane_voter/','/post_resolver_audit/')):
            assert new[name]==digest,name
    assert pipeline.sha(releases/'1.11.0/release.json')=='a0f2b88b6baac0dcea7e413788c16090adbd3f3c89062ff6e1a2ea2e564d4f7a'
    assert pipeline.DEFAULT_RELEASE=='1.12.0'
    assert '1.11.0' in pipeline.SUPPORTED_RELEASES
