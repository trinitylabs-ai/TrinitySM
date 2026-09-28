"""Frozen voter: 24 concurrent scripted chat calls and preserved BF, network blocked."""
from dataclasses import asdict
import json
from pathlib import Path
import socket
import sys
import threading
from cross_lane_replay import sample as make_sample
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'harnesses/imo_proof_pipeline/releases/1.11.0/engine/source'))
from experiments.local_math_verifier.cross_lane_voter import live as w
root=Path(sys.argv[1]);root.mkdir()
candidates=[]
for i in range(4):
 p=root/f'proof_{i}.md';p.write_text(f'Proof {i}.\n')
 candidates.append({'candidate_id':f'lane_{i}','selected_stage':'refinement_2','proof_path':str(p),'proof_sha256':w.digest(p.read_bytes().strip())})
root=root/'job'
w.prepare(root,'P','Prove the claim.',candidates,{'raw_seed_offset':0,'seed_namespace':w.DEFAULT_NAMESPACE,'model_timeout_sec':600,'gemma_endpoint':'http://127.0.0.1:8030/v1','qwen_endpoint':'http://127.0.0.1:8027/v1'},'a'*64)
sample=make_sample()
def blocked(*args, **kwargs):
    raise AssertionError('Network is blocked during offline regression')
socket.socket.connect = blocked
socket.create_connection = blocked

from scripts import run_v263_v290 as queue
_, backend = queue.load_engines()
bf = backend.v263.parent._budget_forcing
calls, lock, barrier = [], threading.Lock(), threading.Barrier(24)

def physical(**kwargs):
    folder, stage = Path(kwargs['output_dir']), kwargs['stage']
    folder.mkdir(parents=True, exist_ok=True)
    forced = bool(kwargs.get('continuation_instruction'))
    config = asdict(kwargs['config'])
    assert config['temperature'] == 0.2
    if forced:
        assert '[Preserved reasoning]\nPRIMARY REASONING' in kwargs['prior_generation']
        assert '[Preserved response]\nPRIMARY ANSWER' in kwargs['prior_generation']
        assert kwargs['continuation_instruction'] == (root / 'BF_CUE.md').read_text()
    with lock:
        calls.append({'stage': stage, 'forced': forced, 'model': kwargs['model']})
        first_wave = len(calls) <= 24
    if first_wave:
        barrier.wait(timeout=20)
    text = sample.strip() if forced else 'PRIMARY ANSWER'
    reasoning = 'FORCED REASONING' if forced else 'PRIMARY REASONING'
    metadata = {'stage': stage, 'model': kwargs['model'], 'config': config, 'finish_reason': 'stop',
        'prompt_sha256': w.digest(kwargs['prompt'].encode()), 'user_prompt_sha256': w.digest(kwargs['user_prompt'].encode()),
        'system_prompt_path': str(folder / (stage + '.prompt.txt')), 'user_prompt_path': str(folder / (stage + '.user_prompt.txt'))}
    raw = {'choices': [{'finish_reason': 'stop', 'message': {'content': text, 'reasoning_content': reasoning}}]}
    for suffix, value in (('.raw_response.json', json.dumps(raw)), ('.metadata.json', json.dumps(metadata)),
            ('.prompt.txt', kwargs['prompt']), ('.user_prompt.txt', kwargs['user_prompt']), ('.reasoning.txt', reasoning)):
        (folder / (stage + suffix)).write_text(value)
    return {'text': text, 'reasoning': reasoning, 'metadata': metadata}


bf._ORIGINAL=physical
sys.argv=['voter','--root',str(root)]
assert w.main()==0
assert len(calls)==48 and sum(c['forced'] for c in calls)==24
status=w.read(root/'status.json')
assert status['max_concurrency_per_model']=={'gemma':12,'qwen':12}
assert w.main()==0 and len(calls)==48
print('VOTER_TRANSPORT_OK: 24 logical calls, 48 scripted physical calls, 12 per model, same chat BF, resume zero extra calls, network blocked')
