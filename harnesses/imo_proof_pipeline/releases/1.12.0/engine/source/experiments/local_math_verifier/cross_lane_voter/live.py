"""Grade-free selection among audited lane finals, with no inference on collection."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import ExitStack
from datetime import datetime, timezone
import fcntl
import itertools
import json
from pathlib import Path
import re
import threading
import time

from ..post_resolver_audit.bindings import verify_audit_binding
from ..post_resolver_audit.live import digest, encoded, exact, read, write, MODELS, MODEL_WORKERS
from .validation import parse

HERE = Path(__file__).resolve().parent
POLICY_ID = 'cross-lane-symmetric-obligation-audit-prompt-v2'
DEFAULT_NAMESPACE = 'v263-v290:problem-only'


def specification(problem_id, problem, candidates, runtime, release_sha256):
    """Build the entire plan from whitelisted inputs, before reading any responses."""
    if not re.fullmatch(r'[A-Za-z0-9_-]+', problem_id) or not problem.strip():
        raise ValueError('Invalid problem identity or empty statement')
    if not 1 <= len(candidates) <= 4:
        raise ValueError('Expected one to four available lane finals')
    rows, contents = [], {'problem.md': problem.encode()}
    for candidate in candidates:
        cid, data = candidate['candidate_id'], candidate['data']
        if not re.fullmatch(r'[A-Za-z0-9_-]+', cid) or not data.strip():
            raise ValueError('Invalid lane or empty final proof')
        rows.append({'candidate_id': cid, 'source_stage': candidate['selected_stage'],
                     'proof_file_sha256': digest(data),
                     'proof_sha256': digest(data.decode().strip().encode())})
        contents['proofs/' + cid + '.md'] = data
    if len({r['candidate_id'] for r in rows}) != len(rows):
        raise ValueError('Duplicate lane final')
    seed = runtime['raw_seed_offset']
    if not isinstance(seed, int):
        raise ValueError('Expected integer seed offset')
    rows.sort(key=lambda c: digest(json.dumps([seed, problem_id, c['proof_file_sha256'],
                                              c['candidate_id'], 'blind_order'], ensure_ascii=False).encode()))
    namespace = runtime['seed_namespace']
    cases, tasks = [], []

    def snapshot(ident, a, b, order):
        first, second = (a, b) if order == 'forward' else (b, a)
        def numbered(data):
            return '\n'.join(f'{i}: {line}' for i, line in enumerate(data.decode().strip().splitlines(), 1))
        user = '# Problem\n\n' + problem.strip() + '\n\n# Proof A\n\n' + numbered(first)
        user += '\n\n# Proof B\n\n' + numbered(second) + '\n'
        files = {'baseline.md': a, 'candidate.md': b, 'problem.md': problem.encode(), 'audit_input.md': user.encode()}
        for name, data in files.items():
            contents[f'model_inputs/{ident}/{name}'] = data
        return {name: digest(data) for name, data in files.items()}

    for index, (a, b) in enumerate(itertools.combinations(rows, 2), 1):
        ident = f'pair_{index:02d}'
        first, second = (contents['proofs/' + c['candidate_id'] + '.md'] for c in (a, b))
        files = snapshot(ident, first, second, 'forward')
        case = {'case_id': ident, 'problem_id': problem_id, 'candidate_ids': [a['candidate_id'], b['candidate_id']],
                'baseline_sha256': digest(first), 'candidate_sha256': digest(second), 'changes': [],
                'files': files, 'input_sha256': files['audit_input.md']}
        cases.append(case)
        for order in ('forward', 'reverse'):
            for model in MODELS:
                tid = f'{ident}_{model}_{order}'
                files = snapshot(tid, first, second, order)
                seed_key = f'cross-lane-comparison:{seed}:{problem_id}:{ident}'
                if namespace != DEFAULT_NAMESPACE:
                    seed_key += ':' + namespace
                tasks.append({**case, 'case_id': tid, 'original_case_id': ident, 'model_key': model,
                    'order': order, 'files': files, 'input_sha256': files['audit_input.md'],
                    'presentation_order': case['candidate_ids'] if order == 'forward' else list(reversed(case['candidate_ids'])),
                    'seed_key': seed_key, 'batch_id': 'single_complete_round_robin'})
    # Retain the tested interleaving for four lanes; smaller portfolios also mix both orders.
    if len(cases) == 6:
        tasks = [t for nominal in ('forward', 'reverse') for i in (1, 4, 2, 5, 3, 6)
                 for t in tasks if t['original_case_id'] == f'pair_{i:02d}' and
                 t['order'] == (nominal if i <= 3 else ('reverse' if nominal == 'forward' else 'forward'))]
    manifest = {'policy_id': POLICY_ID, 'problem_id': problem_id, 'seed': seed,
                'seed_namespace': namespace, 'candidates': rows, 'cases': cases,
                'seed_derived_candidate_order': [r['candidate_id'] for r in rows],
                'candidate_order_rule': 'sha256(json.dumps([seed, problem_id, exact_proof_hash, candidate_id, blind_order])) ascending',
                'comparison_runtime': {'batch_size': len(tasks), 'calls_per_model': len(tasks) // 2,
                    'workers_total': 24, 'workers_per_model': MODEL_WORKERS, 'batch_assignment_seed': None,
                    'batching': 'one complete round-robin; independent model/order conversations',
                    'timeout_policy': read(HERE / 'timeout_policy.json')}}
    contents.update({'AUDIT_PROMPT.md': (HERE / 'AUDIT_PROMPT.md').read_bytes(),
                     'BF_CUE.md': (HERE / 'BF_CUE.md').read_bytes(),
                     'timeout_policy.json': (HERE / 'timeout_policy.json').read_bytes(),
                     'manifest.json': encoded(manifest), 'audit_plan.json': encoded({'audits': tasks})})
    cfg = {'policy_id': POLICY_ID, 'release_sha256': release_sha256, 'temperature': 0.2,
           'runtime': {k: runtime[k] for k in ('raw_seed_offset', 'seed_namespace', 'model_timeout_sec', 'gemma_endpoint', 'qwen_endpoint')},
           'auditors': {m: {'model': model, 'endpoint': runtime[m + '_endpoint']} for m, model in MODELS.items()},
           'pins': {name: digest(data) for name, data in sorted(contents.items())}}
    contents['config.json'] = encoded(cfg)
    return contents, cfg, manifest, tasks


def source_candidates(candidates):
    rows = []
    for row in candidates:
        data = Path(row['proof_path']).read_bytes()
        if digest(data.decode().strip().encode()) != row['proof_sha256']:
            raise ValueError('Final proof differs from its selected checkpoint')
        rows.append({'candidate_id': row['candidate_id'], 'selected_stage': row['selected_stage'], 'data': data})
    return rows


def prepare(root, problem_id, problem, candidates, runtime, release_sha256):
    contents, cfg, manifest, tasks = specification(problem_id, problem, source_candidates(candidates), runtime, release_sha256)
    for name, data in contents.items():
        exact(Path(root) / name, data)
    return cfg, manifest, tasks


def verify(root, *, expected=None):
    root = Path(root)
    cfg, manifest = read(root / 'config.json'), read(root / 'manifest.json')
    if expected is None:
        candidates = [{'candidate_id': r['candidate_id'], 'selected_stage': r['source_stage'],
                       'data': (root / 'proofs' / (r['candidate_id'] + '.md')).read_bytes()}
                      for r in manifest['candidates']]
        args = (manifest['problem_id'], (root / 'problem.md').read_text(), candidates, cfg['runtime'], cfg['release_sha256'])
    else:
        args = (expected['problem_id'], expected['problem'], source_candidates(expected['candidates']),
                expected['runtime'], expected['release_sha256'])
    contents, expected_cfg, expected_manifest, tasks = specification(*args)
    for name, data in contents.items():
        if (root / name).read_bytes() != data:
            raise ValueError('Voter source, plan or configuration changed: ' + name)
    return expected_cfg, expected_manifest, tasks


def verified_vote(root, task):
    root = Path(root)
    vote = {k: task[k] for k in ('case_id', 'original_case_id', 'problem_id', 'model_key', 'order', 'presentation_order')}
    try:
        folder = root / 'cases' / task['case_id']
        result, call = read(folder / 'result.json'), read(folder / 'audit/call_result.json')
        verify_audit_binding(root, task, result, call)
        vote.update(parse(call['text']), binding_verified=True)
        vote['selected_candidate'] = task['presentation_order'][0 if vote['winner_label'] == 'A' else 1]
        vote['elapsed_seconds'] = result.get('elapsed_seconds')
        vote['timeout_fallback'] = call['metadata'].get('comparison_timeout_policy')
    except Exception as error:
        vote.update(valid=False, selected_candidate=None, error=f'{type(error).__name__}: {error}')
    return vote


def summarize(manifest, votes):
    ordered, summaries = manifest['seed_derived_candidate_order'], {}
    for model in ('gemma', 'qwen', 'combined'):
        rows = [v for v in votes if model == 'combined' or v['model_key'] == model]
        valid = [v for v in rows if v.get('valid')]
        expected = len(manifest['cases']) * (4 if model == 'combined' else 2)
        complete = len(rows) == len(valid) == expected
        counts = {cid: sum(v['selected_candidate'] == cid for v in valid) for cid in ordered}
        pairs = []
        for m in (tuple(MODELS) if model == 'combined' else (model,)):
            for case in manifest['cases']:
                two = [v for v in valid if v['model_key'] == m and v['original_case_id'] == case['case_id']]
                if len(two) == 2:
                    pairs.append({'model': m, 'pair': case['case_id'],
                                  'disagreement': two[0]['selected_candidate'] != two[1]['selected_candidate']})
        disagreement = sum(p['disagreement'] for p in pairs)
        summaries[model] = {'complete': complete, 'valid_calls': len(valid), 'expected_calls': expected,
            'votes': counts, 'winner': max(ordered, key=lambda c: counts[c]) if complete else None,
            'completed_order_pairs': len(pairs), 'disagreeing_pairs': disagreement,
            'order_disagreement_rate': disagreement / len(pairs) if pairs else None}
    return {'policy_id': POLICY_ID, 'problem_id': manifest['problem_id'], 'grade_access': False,
            'seed_derived_candidate_order': ordered, 'comparison_runtime': manifest['comparison_runtime'],
            'summaries': summaries, 'vote_table': votes,
            'state': 'completed' if summaries['combined']['complete'] else 'incomplete'}


def collect(root, *, expected=None):
    _, manifest, tasks = verify(root, expected=expected)
    return summarize(manifest, [verified_vote(root, task) for task in tasks])


def execute(root, task, caller):
    root = Path(root)
    folder = root / 'cases' / task['case_id']
    folder.mkdir(parents=True, exist_ok=True)
    if (folder / 'result.json').exists():
        return verified_vote(root, task)
    cfg = read(root / 'config.json')
    prompt = (root / 'AUDIT_PROMPT.md').read_text()
    result = {k: task[k] for k in ('case_id', 'original_case_id', 'problem_id', 'model_key', 'order', 'presentation_order')}
    result['binding'] = digest(json.dumps(task, sort_keys=True).encode() + prompt.encode())
    result['started_at'] = datetime.now(timezone.utc).isoformat()
    began = time.monotonic()
    try:
        call_path = folder / 'audit/call_result.json'
        if call_path.exists():
            call = read(call_path)
        else:
            if (folder / 'call_started.json').exists() or (folder / 'audit').exists():
                raise ValueError('Interrupted comparison preserved; no duplicate inference')
            write(folder / 'call_started.json', result)
            call = caller(**cfg['auditors'][task['model_key']], system_prompt=prompt,
                user_prompt=(root / 'model_inputs' / task['case_id'] / 'audit_input.md').read_text(),
                output_dir=folder / 'audit', stage_name='cross_lane_proof_comparison',
                temperature=0.2, seed_key=task['seed_key'], reasoning_effort=None,
                parser=lambda text: {'valid': True}, model_timeout_sec=cfg['runtime']['model_timeout_sec'])
            if not call_path.exists():
                write(call_path, call)
        result['audit_sha256'] = call['final_sha256']
        verify_audit_binding(root, task, result, call)
        result.update(parse(call['text']))
    except Exception as error:
        result.update(valid=False, error=f'{type(error).__name__}: {error}')
    result['elapsed_seconds'] = time.monotonic() - began
    write(folder / 'result.json', result)
    return verified_vote(root, task)


def report(root, selection):
    lines = ['# Cross-lane voter', '', '| Lane | Gemma | Qwen | Combined |', '|---|---:|---:|---:|']
    for cid in selection['seed_derived_candidate_order']:
        counts = [selection['summaries'][m]['votes'][cid] for m in ('gemma', 'qwen', 'combined')]
        lines.append(f'| {cid} | {counts[0]} | {counts[1]} | {counts[2]} |')
    for model, summary in selection['summaries'].items():
        lines.extend(['', f"{model}: winner {summary['winner'] or 'UNRESOLVED'}; valid calls "
            f"{summary['valid_calls']}/{summary['expected_calls']}; order disagreement "
            f"{summary['disagreeing_pairs']}/{summary['completed_order_pairs']} "
            f"(rate: {summary['order_disagreement_rate']})."])
    lines.extend(['', '| Model | A | B | Winner | Valid |', '|---|---|---|---|---|'])
    for vote in selection['vote_table']:
        a, b = vote['presentation_order']
        lines.append(f"| {vote['model_key']} | {a} | {b} | {vote['selected_candidate']} | {vote['valid']} |")
    fallbacks = [v for v in selection['vote_table'] if v.get('timeout_fallback')]
    lines += ['', 'Timeout fallbacks: ' + str(len(fallbacks)) + '.']
    for vote in fallbacks:
        lines.append(f"- {vote['case_id']}: {vote['timeout_fallback']['action']}")
    write(Path(root) / 'SELECTIONS.json', selection)
    (Path(root) / 'REPORT.md').write_text('\n'.join(lines) + '\n')


def run(root, caller):
    root = Path(root)
    _, manifest, tasks = verify(root)
    if (root / 'status.json').exists() and read(root / 'status.json').get('state') == 'completed':
        selection = collect(root)
        selection['observed_runtime'] = read(root / 'status.json')
        report(root, selection)
        return selection
    began, lock = time.monotonic(), threading.Lock()
    status = {'state': 'running', 'total_calls': len(tasks), 'completed_calls': 0,
              'workers_total': 24, 'workers_per_model': MODEL_WORKERS, 'active_per_model': dict.fromkeys(MODELS, 0),
              'max_concurrency_per_model': dict.fromkeys(MODELS, 0), 'max_concurrency_observed': 0}
    def monitored(task):
        model = task['model_key']
        def measured_call(**kwargs):
            with lock:
                status['active_per_model'][model] += 1
                status['max_concurrency_per_model'][model] = max(status['max_concurrency_per_model'][model], status['active_per_model'][model])
                status['max_concurrency_observed'] = max(status['max_concurrency_observed'], sum(status['active_per_model'].values()))
                write(root / 'status.json', status)
            try:
                return caller(**kwargs)
            finally:
                with lock:
                    status['active_per_model'][model] -= 1
                    write(root / 'status.json', status)
        try:
            return execute(root, task, measured_call)
        finally:
            with lock:
                status['completed_calls'] += 1
                write(root / 'status.json', status)
    with ExitStack() as stack:
        pools = {m: stack.enter_context(ThreadPoolExecutor(max_workers=n)) for m, n in MODEL_WORKERS.items()}
        futures = [pools[t['model_key']].submit(monitored, t) for t in tasks]
        for future in as_completed(futures):
            future.result()
    selection = collect(root)
    status.update(state=selection['state'], elapsed_seconds=time.monotonic() - began,
                  valid_calls=selection['summaries']['combined']['valid_calls'])
    selection['observed_runtime'] = status
    report(root, selection)
    write(root / 'status.json', status)
    return selection


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    args = parser.parse_args()
    verify(args.root)
    from scripts import run_v263_v290 as queue
    from experiments.local_math_verifier import refinement_bf_policy as policy
    _, backend = queue.load_engines()
    policy.ROLE_SPECIFIC_CUES['cross_lane_comparison'] = (HERE / 'BF_CUE.md').read_text()
    route = policy.make_route('cross_lane_comparison', r'cross_lane_proof_comparison_cap_[0-9]+', (HERE / 'AUDIT_PROMPT.md').read_text())
    events = args.root / ('bf_events_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.jsonl')
    with (args.root / 'controller.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with policy.install(backend.v263.parent._budget_forcing, policy.ROLE_SPECIFIC, events, routes=[route]):
            from . import timeout_adapter
            from .mechanical_recovery import restore_checks_label
            from .validation import strict_parse
            with timeout_adapter.install(backend.v263.parent._budget_forcing,
                    backend.repair_boundary.default_markdown_call, strict_parse, restore_checks_label) as caller:
                selection = run(args.root, caller)
    return 0 if selection['state'] == 'completed' else 2


if __name__ == '__main__':
    raise SystemExit(main())
