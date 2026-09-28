"""Vote semantics, binding, partial portfolios and resume; no network calls."""
import json
from pathlib import Path
import subprocess
import sys
import threading
import pytest
from test_public_reproduction import pipeline, ROOT
from cross_lane_replay import sample, response
v = pipeline.voter_module('1.11.0')

def setup(tmp_path,n=4):
    candidates=[]
    for i in range(n):
        p=tmp_path/f'lane_{i}.md';p.write_text(f'Proof for lane {i}.\n')
        candidates.append({'candidate_id':f'lane_{i}','proof_path':str(p),'proof_sha256':v.digest(p.read_bytes().strip()),
                           'selected_stage':'refinement_2' if i%2 else 'refinement_3','grade':'DO_NOT_PASS_GRADE'})
    runtime={'raw_seed_offset':0,'seed_namespace':v.DEFAULT_NAMESPACE,'model_timeout_sec':600,
             'gemma_endpoint':'http://127.0.0.1:8030/v1','qwen_endpoint':'http://127.0.0.1:8027/v1'}
    root=tmp_path/'voter';v.prepare(root,'P','Prove the claim.',candidates,runtime,'a'*64)
    return root,{'problem_id':'P','problem':'Prove the claim.','candidates':candidates,'runtime':runtime,'release_sha256':'a'*64}

@pytest.mark.parametrize('n',[1,2,3,4])
def test_complete_pairs_for_each_available_portfolio(tmp_path,n):
    root,expected=setup(tmp_path,n);cfg,manifest,tasks=v.verify(root,expected=expected)
    assert len(tasks)==2*n*(n-1)
    assert 'DO_NOT_PASS_GRADE' not in ''.join(p.read_text() for p in root.rglob('*.md'))
    calls=[];result=v.run(root,lambda **kw:(calls.append(kw) or response(kw)))
    assert len(calls)==len(tasks)
    assert result['summaries']['combined']['winner']==manifest['seed_derived_candidate_order'][0]
    assert set(result['summaries']['combined']['votes'].values())=={2*(n-1)}
    assert result['summaries']['combined']['order_disagreement_rate']==(1 if n>1 else None)
    v.run(root,lambda **kw:pytest.fail('Resume repeated a completed call'))
    assert v.collect(root,expected=expected)['state']=='completed'

def test_parallel_pools_reach_twelve_each(tmp_path):
    root,_=setup(tmp_path);barrier=threading.Barrier(24,timeout=10)
    def call(**kw):
        barrier.wait();return response(kw)
    result=v.run(root,call)
    assert result['observed_runtime']['max_concurrency_per_model']=={'gemma':12,'qwen':12}
    assert result['observed_runtime']['max_concurrency_observed']==24

def test_reparse_saved_response_and_reject_tampering(tmp_path):
    root,expected=setup(tmp_path,2);v.run(root,lambda **kw:response(kw))
    task=v.verify(root)[2][0];p=root/'cases'/task['case_id']/'result.json'
    value=v.read(p);value['winner_label']='B';value['selected_candidate']='forged';v.write(p,value)
    assert v.collect(root,expected=expected)['vote_table'][0]['winner_label']=='A'
    call_path=p.parent/'audit/call_result.json';call=v.read(call_path);call['text']+='tampering';v.write(call_path,call)
    result=v.collect(root,expected=expected)
    assert result['state']=='incomplete' and result['summaries']['combined']['winner'] is None
    p=root/'audit_plan.json';plan=v.read(p);plan['audits'].pop();v.write(p,plan)
    with pytest.raises(ValueError):v.collect(root,expected=expected)

def test_interrupted_call_is_not_repeated_or_counted(tmp_path):
    root,_=setup(tmp_path,2);task=v.verify(root)[2][0]
    v.write(root/'cases'/task['case_id']/'call_started.json',{})
    result=v.run(root,lambda **kw:response(kw))
    assert result['state']=='incomplete' and result['summaries']['combined']['valid_calls']==3
    v.run(root,lambda **kw:pytest.fail('Repeated interrupted or completed inference'))

def test_sources_and_runtime_are_bound(tmp_path):
    root,expected=setup(tmp_path,2);expected['runtime']['raw_seed_offset']=1
    with pytest.raises(ValueError):v.collect(root,expected=expected)
    expected['runtime']['raw_seed_offset']=0;Path(expected['candidates'][0]['proof_path']).write_text('changed')
    with pytest.raises(ValueError):v.collect(root,expected=expected)

@pytest.mark.parametrize('text',[sample('A or B'),sample('tie'),sample()+'\nWinner: B',sample().replace('## Proof B','## Proof A')])
def test_ambiguous_output_fails_without_model_repair(text):
    with pytest.raises(ValueError):v.parse(text)

@pytest.mark.parametrize('veto',[False,True])
def test_actual_pipeline_audit_then_vote_and_offline_collection(tmp_path,veto):
    result=subprocess.run([sys.executable,'-B',str(ROOT/'tests/pipeline_regression_driver.py'),str(tmp_path/'run'),
        'CERTIFIED','--voter-b',*(['--audit-veto'] if veto else [])],cwd=ROOT,text=True,capture_output=True,timeout=90)
    assert result.returncode==0,result.stdout+result.stderr
    d=json.loads((tmp_path/'run/final_results.json').read_text())
    assert d['cross_lane_voter_enabled'] and d['completed_proofs']==4
    selected=d['problem_selections'][0]
    assert selected['state']=='completed' and len(selected['vote_table'])==24
    lane=next(r for r in d['lanes'] if r['candidate_id']==selected['selected_candidate'])
    assert (tmp_path/'run'/selected['proof']).read_bytes()==(tmp_path/'run'/lane['proof']).read_bytes()

def test_new_release_preserves_existing_source():
    releases=ROOT/'harnesses/imo_proof_pipeline/releases'
    before=json.loads((releases/'1.10.0/engine/freeze.json').read_text())['files']
    after=json.loads((releases/'1.11.0/engine/freeze.json').read_text())['files']
    assert {k for k in before if k.startswith('source/') and before[k]!=after[k]}=={'source/scripts/continue_r1_audited.py'}
    assert pipeline.sha(releases/'1.10.0/release.json')=='5946f96d1b427d7f358db5ebdb5d1a438197ec6d5f3c4a4d337996c473980200'
    assert pipeline.sha(releases/'1.11.0/release.json')=='a0f2b88b6baac0dcea7e413788c16090adbd3f3c89062ff6e1a2ea2e564d4f7a'
    for name in ('AUDIT_PROMPT.md','BF_CUE.md','live.py'):
        assert (v.HERE/name).read_bytes()==(ROOT/'harnesses/cross_lane_voter'/name).read_bytes()
    # Development adds explicit format recovery around the unchanged parser;
    # the historical release retains the original entry point and bytes.
    import ast
    frozen=ast.parse((v.HERE/'validation.py').read_text())
    current=ast.parse((ROOT/'harnesses/cross_lane_voter/validation.py').read_text())
    old=next(n for n in frozen.body if isinstance(n,ast.FunctionDef) and n.name=='parse')
    strict=next(n for n in current.body if isinstance(n,ast.FunctionDef) and n.name=='strict_parse')
    strict.name='parse'
    assert ast.dump(old)==ast.dump(strict)


def test_frozen_chat_bf_transport(tmp_path):
    result=subprocess.run([sys.executable,'-B',str(ROOT/'tests/cross_lane_transport_driver.py'),str(tmp_path/'transport')],
                          cwd=ROOT,text=True,capture_output=True,timeout=60)
    assert result.returncode==0,result.stdout+result.stderr
    assert 'VOTER_TRANSPORT_OK' in result.stdout

def test_voter_release_keeps_all_earlier_checkpoints_after_interruption(tmp_path):
    result=subprocess.run([sys.executable,'-B',str(ROOT/'tests/pipeline_regression_driver.py'),str(tmp_path/'run'),
        'CERTIFIED','--voter-b','--recover'],cwd=ROOT,text=True,capture_output=True,timeout=90)
    assert result.returncode==0,result.stdout+result.stderr
    d=json.loads((tmp_path/'run/final_results.json').read_text())
    assert d['completed_proofs']==4 and d['problem_selections'][0]['state']=='unavailable'


def test_statement_binding_before_refinement_exists(tmp_path):
    pipeline.write(tmp_path/'manifest.json',{'problems':[{'problem_id':'P','problem':'Prove X.'}]})
    pipeline.write(tmp_path/'inputs/P.json',{'problem_id':'P','problem':'Prove X.'})
    assert pipeline.voter_problem(tmp_path,'P')=='Prove X.'
    pipeline.write(tmp_path/'inputs/P.json',{'problem_id':'P','problem':'Prove Y.'})
    with pytest.raises(ValueError):pipeline.voter_problem(tmp_path,'P')
