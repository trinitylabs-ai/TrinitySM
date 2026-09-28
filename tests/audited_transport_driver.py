"""Exercise the frozen original Draft and live audit BF through scripted HTTP."""
from dataclasses import asdict
import json
from pathlib import Path
import socket
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / 'harnesses/imo_proof_pipeline/releases' / (sys.argv[3] if len(sys.argv) > 3 else '1.10.0') / 'engine/source'
sys.path.insert(0, str(ENGINE))
from scripts import run_v263_v290 as queue
from experiments.local_math_verifier.post_resolver_audit import live
from post_resolver_audit_replay import response


def blocked(*args, **kwargs):
    raise AssertionError('Network forbidden in transport regression')


socket.socket.connect = blocked
socket.create_connection = blocked
frontend, backend = queue.load_engines()
bf = backend.v263.parent._budget_forcing
output = Path(sys.argv[1])
mode = sys.argv[2]
calls, lock = [], threading.Lock()
audit_lanes = 6 if '--six-lanes' in sys.argv else 4 if '--four-lanes' in sys.argv else 1
wave_size = min(audit_lanes * 4, 24)
barrier = threading.Barrier(wave_size, timeout=10) if audit_lanes > 1 else None


def physical(**kwargs):
    folder, stage = Path(kwargs['output_dir']), kwargs['stage']
    folder.mkdir(parents=True, exist_ok=True)
    forced = bool(kwargs.get('continuation_instruction'))
    config = asdict(kwargs['config'])
    expansion = stage.startswith('lazy_in_place_resolve')
    assert config['temperature'] == (0.2 if mode == 'audit' else 0.4 if expansion else 0.1)
    if forced:
        assert '[Preserved reasoning]\nPRIMARY REASONING' in kwargs['prior_generation']
        assert '[Preserved response]\nPRIMARY ANSWER' in kwargs['prior_generation']
        assert kwargs['continuation_instruction'] == ((live.HERE / 'BF_CUE.md').read_text() if mode == 'audit' else bf.TEXT_CONTINUATION)
        if mode == 'audit':
            value = response({'output_dir': folder, 'system_prompt': kwargs['prompt'],
                              'user_prompt': kwargs['user_prompt'], 'model': kwargs['model'], 'temperature': 0.2})
            text = value['text'].strip()
        elif expansion:
            text = ('BEGIN_REPAIR_AUDIT\nCONCLUSION_ACTION: PRESERVE\nORIGINAL_CLASSIFICATION: true\n'
                    'REPAIRED_CLASSIFICATION: true\nCHANGE_BASIS: NONE\nCHANGE_JUSTIFICATION: NONE\nEND_REPAIR_AUDIT\n'
                    'BEGIN_REPAIRED_PROOF\nThe complete explicit derivation proves the claim.\nEND_REPAIRED_PROOF')
        else:
            text = 'Supply the omitted derivation explicitly.'
    else:
        text = 'PRIMARY ANSWER'
    reasoning = 'FORCED REASONING' if forced else 'PRIMARY REASONING'
    metadata = {'stage': stage, 'model': kwargs['model'], 'config': config, 'finish_reason': 'stop',
                'prompt_sha256': live.digest(kwargs['prompt'].encode()),
                'user_prompt_sha256': live.digest(kwargs['user_prompt'].encode()),
                'system_prompt_path': str(folder / (stage + '.prompt.txt')),
                'user_prompt_path': str(folder / (stage + '.user_prompt.txt'))}
    raw = {'choices': [{'finish_reason': 'stop', 'message': {'content': text, 'reasoning_content': reasoning}}]}
    for suffix, value in (('.raw_response.json', json.dumps(raw)), ('.metadata.json', json.dumps(metadata)),
                          ('.prompt.txt', kwargs['prompt']), ('.user_prompt.txt', kwargs['user_prompt']),
                          ('.reasoning.txt', reasoning)):
        (folder / (stage + suffix)).write_text(value)
    with lock:
        calls.append({'model': kwargs['model'], 'stage': stage, 'forced': forced, 'config': config})
        first_wave = len(calls) <= wave_size
    if barrier is not None and first_wave:
        barrier.wait()
    return {'text': text, 'reasoning': reasoning, 'metadata': metadata}


bf._ORIGINAL = physical
if mode == 'draft':
    runtime = frontend.GPU0FourSlotStageRuntime(frontend.RuntimeConfig())
    row = {'candidate_id': 't10_r01', 'proof': 'A proof with an omitted derivation.',
           'proof_sha256': live.digest(b'A proof with an omitted derivation.'), 'seed': 123, 'temperature': 1.0}
    checked = frontend.run_lazy_check(runtime=runtime, output_dir=output, row=row)
    result = frontend.run_lazy_resolve(runtime=runtime, output_dir=output, problem='Prove the claim.', row=checked)
    assert result['lazy_resolve_temperature'] == 0.4
    assert len(calls) == 4 and sum(c['forced'] for c in calls) == 2
    # No-issues lanes retain their source proof without any expansion calls.
    frontend.run_lazy_resolve(runtime=runtime, output_dir=output, problem='Prove the claim.',
                             row={**checked, 'has_lazy_issues': False})
    assert len(calls) == 4
else:
    output.mkdir()
    baseline, candidate = output / 'r2.md', output / 'r3.md'
    baseline.write_text('An omitted derivation.\n'); candidate.write_text('The explicit derivation.\n')
    roots = [output / ('lane_' + str(i)) for i in range(audit_lanes)]
    for i, root in enumerate(roots):
        live.prepare(root, {'problem_id': 'P', 'candidate_id': 'lane_' + str(i), 'problem': 'Prove the claim.',
            'baseline_path': str(baseline), 'candidate_path': str(candidate),
            'baseline_proof_sha256': live.digest(baseline.read_bytes().strip()),
            'candidate_proof_sha256': live.digest(candidate.read_bytes().strip())},
            {'seed_namespace': 'audit-test:0', 'model_timeout_sec': 600,
             'gemma_endpoint': 'http://127.0.0.1:8030/v1', 'qwen_endpoint': 'http://127.0.0.1:8027/v1'}, 'a' * 64)
    job = output / 'job.json'; live.write(job, {'lane_roots': list(map(str, roots))})
    sys.argv = ['live', '--job', str(job)]
    live.main()
    assert len(calls) == 8 * len(roots) and sum(c['forced'] for c in calls) == 4 * len(roots), calls
    assert all(live.read(root / 'selection.json')['decision'] == live.ACCEPT for root in roots)
    if audit_lanes > 1:
        status = live.read(output / 'status.json')
        assert status['max_concurrency_observed'] == wave_size
        assert status['max_concurrency_per_model'] == {'gemma': wave_size // 2, 'qwen': wave_size // 2}
    assert set(c['model'] for c in calls) == set(live.MODELS.values())
    events = [json.loads(line) for p in output.glob('bf_events_*.jsonl') for line in p.read_text().splitlines()]
    assert len(events) == 4 * len(roots)
    live.main()
    assert len(calls) == 8 * len(roots), 'Resume issued new requests'
print('TRANSPORT_OK', mode)
