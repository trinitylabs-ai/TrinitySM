"""Offline tests against the actual frozen BF/caller and request binding."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import sys
import threading
import socket

def no_network(*args, **kwargs):
    raise AssertionError('Unexpected network request')
socket.socket.connect = no_network
socket.socket.connect_ex = no_network
socket.create_connection = no_network
if 'client' in sys.modules:  # Exercise the single-GPU lease wrapper offline.
    def scheduler_api(path, body=None):
        assert path in ('/enqueue', '/release'), path
        return {'state': 'granted' if path == '/enqueue' else 'released'}
    sys.modules['client'].api = scheduler_api

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'harnesses/imo_proof_pipeline/releases/1.12.0/engine/source'))
from scripts import run_v263_v290 as queue
from experiments.local_math_verifier import timeout_recovery as timeout
from experiments.local_math_verifier.cross_lane_voter import live
from experiments.local_math_verifier.cross_lane_voter.mechanical_recovery import restore_checks_label
from experiments.local_math_verifier.cross_lane_voter import timeout_adapter as adapter
_, backend = queue.load_engines()
bf = backend.v263.parent._budget_forcing
original_raw = bf._ORIGINAL
local = threading.local()
def clock():
    return getattr(local, 'seconds', 0.0)
fixture = TemporaryDirectory(prefix='selection_timeout_sources_')
base = Path(fixture.name)
cs=[]
for i in range(2):
    p=base/f'proof{i}.md';p.write_text(f'Proof {i}.')
    cs.append(dict(candidate_id=f'lane{i}', selected_stage='refinement_2',
        proof_path=str(p), proof_sha256=live.digest(p.read_bytes())))
source=base/'source'
live.prepare(source,'P','Prove X.',cs,dict(raw_seed_offset=0,seed_namespace=live.DEFAULT_NAMESPACE,
    model_timeout_sec=600,gemma_endpoint='http://127.0.0.1:8030/v1',qwen_endpoint='http://127.0.0.1:8027/v1'),'a'*64)
task=live.read(source/'audit_plan.json')['audits'][0]
system=(source/'AUDIT_PROMPT.md').read_text()
user=(source/'model_inputs'/task['case_id']/'audit_input.md').read_text()
TEXT = '''# Proof comparison
## Proof A
Established theorem: Checked A claim.
Claim gap: NONE.
Qualifications and supplied repairs: NONE.
Decisive checks: Lines 1-2 checked.
## Proof B
Established theorem: Checked B claim.
Claim gap: Missing implication at line 2.
Qualifications and supplied repairs: NONE.
Decisive checks: Lines 1-2 checked.
## Decision
Winner: A
Reason: A establishes the required implication; B leaves it unsupported.
'''

def fake(**kw):
    local.calls.append(kw)
    index = len(local.calls) - 1
    mode, seconds, text = local.script[index]
    text = text.strip()
    local.seconds += seconds
    dest, stage = Path(kw['output_dir']), kw['stage']
    dest.mkdir(parents=True, exist_ok=True)
    for suffix, content in [('.prompt.txt', kw['prompt']), ('.user_prompt.txt', kw['user_prompt']),
                            ('.reasoning.txt', 'Preserved argument, not a standalone choice.')]:
        (dest / (stage + suffix)).write_text(content)
    meta = dict(model=kw['model'], endpoint=kw['endpoint'], finish_reason='length' if mode == 'length' else 'stop', config=asdict(kw['config']),
        prompt_sha256=adapter.sha(kw['prompt']), user_prompt_sha256=adapter.sha(kw['user_prompt']),
        system_prompt_path=str(dest / (stage + '.prompt.txt')),
        user_prompt_path=str(dest / (stage + '.user_prompt.txt')),
        response_path=str(dest / (stage + '.raw_response.json')),
        reasoning_path=str(dest / (stage + '.reasoning.txt')))
    result = dict(text=text, reasoning='Preserved argument; do not infer the winner from this trace.', metadata=meta)
    raw = {'choices': [{'message': {'content': text, 'reasoning': result['reasoning']}, 'finish_reason': meta['finish_reason']}]}
    for suffix, data in [('.raw_response.json', raw), ('.metadata.json', meta)]:
        (dest / (stage + suffix)).write_text(json.dumps(data))
    if mode == 'timeout':
        partial = dest / (stage + '.timeout.partial.json')
        partial.write_text(json.dumps(raw))
        raise timeout.GenerationTimeout(result, dict(wall_timeout_seconds=seconds, partial_path=str(partial),
            partial_sha256=hashlib.sha256(partial.read_bytes()).hexdigest()))
    return result

def check(name, script, expected_calls, action, fail=False):
    local.seconds, local.calls, local.script = 0.0, [], script
    with TemporaryDirectory(prefix='voter_timeout_test_') as tmp:
        kwargs = dict(endpoint='http://127.0.0.1:8030/v1', model=live.MODELS['gemma'],
            system_prompt=system, user_prompt=user, output_dir=Path(tmp) / 'audit',
            stage_name='cross_lane_proof_comparison', temperature=0.2,
            seed_key=task['seed_key'], reasoning_effort=None, parser=lambda _: {'valid': True},
            model_timeout_sec=600)
        try:
            result = current_caller(**kwargs)
        except timeout.TimeoutRecoveryFailure:
            assert fail, name
        except Exception:
            for path in Path(tmp).rglob('validation.json'):
                print(path.name, path.read_text())
            raise
        else:
            assert not fail, name
            assert live.parse(result['text'])['winner_label'] == 'A'
            record = {k: task[k] for k in ('case_id', 'original_case_id', 'problem_id', 'model_key', 'order')}
            record.update(binding=live.digest(json.dumps(task, sort_keys=True).encode() + system.encode()),
                          audit_sha256=result['final_sha256'])
            live.verify_audit_binding(source, task, record, result)
            observed = result['metadata'].get('comparison_timeout_policy', {}).get('action')
            assert observed == action, (name, observed, action)
            if name.startswith('prose_'):
                repair = live.parse(result['text'])['mechanical_recovery']
                assert repair['policy'] == 'missing-checks-heading-existing-prose-line-citations-v3'
                assert repair['original_response_sha256'] == adapter.sha(text_from_stdin)
                assert result['text'] == text_from_stdin
                assert repair['model_calls'] == 0 and not repair['new_mathematical_text']
        assert len(local.calls) == expected_calls, (name, len(local.calls))
        if action == 'one_answer_only_continuation' or fail:
            last = local.calls[-1]
            assert last['config'].thinking_enabled is False
            assert last['config'].timeout_seconds == 120 and last['config'].max_tokens == 8192
            assert last['prior_generation'].startswith('[Preserved reasoning]')
            assert last['config'].seed == local.calls[0]['config'].seed
            assert last['config'].temperature == local.calls[0]['config'].temperature
            assert last['prompt'] == system and last['user_prompt'] == user
        if name == 'bf_timeout':
            assert local.calls[1]['config'].timeout_seconds == 500
        return name

bf._ORIGINAL = fake
try:
    with adapter.install(bf, backend.repair_boundary.default_markdown_call, live.parse,
                         restore_checks_label, clock=clock) as current_caller:
        tests = [
            ('normal_bf', [('ok', 100, TEXT), ('ok', 100, TEXT)], 2, None, False),
            ('initial_partial_answer', [('timeout', 600, TEXT)], 1, 'use_initial_answer', False),
            ('reasoning_only', [('timeout', 600, ''), ('ok', 10, TEXT)], 2, 'one_answer_only_continuation', False),
            ('bf_timeout', [('ok', 100, TEXT), ('timeout', 500, '')], 2, 'use_initial_answer', False),
            ('late_primary', [('ok', 601, TEXT)], 1, 'use_initial_answer', False),
            ('continuation_timeout', [('timeout', 600, ''), ('timeout', 120, '')], 2, 'one_answer_only_continuation', True),
        ]
        if '--prose-recovery' in sys.argv:
            text_from_stdin = sys.stdin.read().strip()
            tests += [
                ('prose_primary', [('ok', 100, text_from_stdin), ('ok', 100, text_from_stdin)], 2, None, False),
                ('prose_continuation', [('timeout', 600, ''), ('ok', 64, text_from_stdin)], 2, 'one_answer_only_continuation', False),
                ('prose_partial', [('timeout', 600, text_from_stdin)], 1, 'use_initial_answer', False),
                ('invalid_prose_continuation', [('timeout', 600, ''), ('ok', 64, text_from_stdin.replace('Line 13', 'Line 10'))], 2, 'one_answer_only_continuation', True),
                ('prose_truncated_continuation', [('timeout', 600, ''), ('length', 64, text_from_stdin)], 2, 'one_answer_only_continuation', True),
            ]
        results = [check(*test) for test in tests]
        # Same installed adapter, concurrent logical calls and independent clocks/traces.
        with ThreadPoolExecutor(max_workers=2) as pool:
            jobs = [pool.submit(check, *tests[i]) for i in (2, 3)]
            results += ['concurrent_' + job.result() for job in jobs]
finally:
    bf._ORIGINAL = original_raw
fixture.cleanup()
print(json.dumps(dict(state='passed', checks=results, check_count=len(results), model_calls=0), indent=2))
