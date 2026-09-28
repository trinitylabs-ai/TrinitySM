"""Actual saved transport binding regression, isolated from running artifacts."""
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil

import pytest

from harnesses.post_resolver_audit.bindings import verify_audit_binding
from harnesses.post_resolver_audit.validation import validate_audit

SOURCE=Path(os.environ.get('PROOF_AUDIT_FIXTURE', str(Path(__file__).resolve().parents[1] / '.workshop/experiments/proofbench_r2_r3_full60_audit_20260921T162620Z')))
TASK_ID='case_e6b48d9baa56_gemma_reverse'

@pytest.fixture
def saved():
    if not SOURCE.exists():pytest.skip('Saved audit fixture unavailable')
    plan=json.loads((SOURCE/'audit_plan.json').read_text())['audits']
    task=next(t for t in plan if t['case_id']==TASK_ID)
    folder=SOURCE/'cases'/TASK_ID
    return task,json.loads((folder/'result.json').read_text()),json.loads((folder/'audit/call_result.json').read_text())

def test_real_truncated_echo_accepts_with_verified_transport(saved):
    task,result,call=saved
    assert verify_audit_binding(SOURCE,task,result,call)['verified']
    parsed=validate_audit(call['text'],task)
    assert parsed['valid'] and parsed['decision']=='ACCEPT_CANDIDATE'
    assert parsed['warnings']

@pytest.mark.parametrize('mutation',['response_text','request_binding','transport_input','wrong_order'])
def test_real_binding_tampering_still_rejected(saved,mutation):
    task,result,call=deepcopy(saved)
    if mutation=='response_text':call['text']+=' altered'
    elif mutation=='request_binding':result['binding']='0'*64
    elif mutation=='transport_input':call['metadata']['user_prompt_sha256']='0'*64
    elif mutation=='wrong_order':result['order']='forward'
    with pytest.raises(ValueError):verify_audit_binding(SOURCE,task,result,call)

def test_altered_actual_proof_rejected(saved,tmp_path):
    task,result,call=saved
    for name in ('config.json','manifest.json','audit_plan.json','AUDIT_PROMPT.md'):
        shutil.copyfile(SOURCE/name,tmp_path/name)
    for cid in (task['case_id'],task['original_case_id']):
        shutil.copytree(SOURCE/'model_inputs'/cid,tmp_path/'model_inputs'/cid)
    proof=tmp_path/'model_inputs'/task['original_case_id']/'baseline.md'
    proof.write_text(proof.read_text()+' altered proof')
    with pytest.raises(ValueError,match='Hash mismatch'):
        verify_audit_binding(tmp_path,task,result,call)
