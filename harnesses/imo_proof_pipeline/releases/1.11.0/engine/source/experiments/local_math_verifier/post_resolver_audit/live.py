"""Bound R2/R3 audits with server-sized concurrency and resumable artifacts.

This module has no grading imports. The live worker uses only its bundled engine.
Collection revalidates saved responses and never makes model calls.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import ExitStack
from datetime import datetime, timezone
import argparse
import difflib
import fcntl
import hashlib
import json
from pathlib import Path
import threading
import time

from .bindings import verify_audit_binding
from .validation import ACCEPT, KEEP, VERSION, select_candidate, validate_audit

HERE = Path(__file__).resolve().parent
POLICY_ID = 'r2-r3-dual-audit-both-orders-v1'
MODELS = {'gemma': 'google/gemma-4-31B-it', 'qwen': 'Qwen/Qwen3.6-27B'}
ORDERS = ('forward', 'reverse')
MODEL_WORKERS = {'gemma': 12, 'qwen': 12}
WORKERS_TOTAL = sum(MODEL_WORKERS.values())


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
    temporary.replace(path)


def exact(path, data):
    """Resume immutable inputs only when every byte matches."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError('Saved audit input/configuration changed: ' + str(path))
    else:
        with path.open('xb') as handle:
            handle.write(data)
    return digest(data)


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode()


def changes_for(baseline, candidate):
    changes = []
    for kind, a, b, c, d in difflib.SequenceMatcher(
            None, baseline.strip().splitlines(), candidate.strip().splitlines(), autojunk=False).get_opcodes():
        if kind != 'equal':
            changes.append({'id': f'D{len(changes)+1:03d}', 'kind': kind,
                            'baseline_lines': [a + 1, b], 'candidate_lines': [c + 1, d]})
    return changes


def input_text(problem, baseline, candidate, changes, order='forward'):
    def numbered(data):
        return '\n'.join(f'{i}: {line}' for i, line in enumerate(data.decode().strip().splitlines(), 1))
    prefix = (f'# Problem\n\n{problem.strip()}\n\nBaseline SHA256: {digest(baseline)}\n'
              f'Candidate SHA256: {digest(candidate)}\n\n')
    sections = [f'# Baseline proof\n\n{numbered(baseline)}\n\n',
                f'# Candidate proof\n\n{numbered(candidate)}\n\n']
    if order == 'reverse':
        sections.reverse()
    blocks = '\n'.join(f"- {c['id']}: {c['kind']}; baseline lines {c['baseline_lines']}; "
                       f"candidate lines {c['candidate_lines']}" for c in changes)
    return prefix + ''.join(sections) + '# Changed blocks\n\n' + blocks + '\n'


def prepare(root, pair, runtime, release_sha256):
    """Snapshot only statement and proofs; never pass caller-supplied extra fields."""
    root = Path(root)
    baseline, candidate = (Path(pair[k]).read_bytes() for k in ('baseline_path', 'candidate_path'))
    if not baseline.strip() or not candidate.strip():
        raise ValueError('Cannot audit an empty proof')
    for role, data in (('baseline', baseline), ('candidate', candidate)):
        if digest(data.decode().strip().encode()) != pair[role + '_proof_sha256']:
            raise ValueError('Completed source proof changed: ' + role)
    material = [pair['problem_id'], pair['candidate_id'], digest(baseline), digest(candidate)]
    case_id = 'case_' + digest(json.dumps(material).encode())[:16]
    changes = changes_for(baseline.decode(), candidate.decode())
    case = {'case_id': case_id, 'problem_id': pair['problem_id'], 'candidate_id': pair['candidate_id'],
            'baseline_sha256': digest(baseline), 'candidate_sha256': digest(candidate),
            'identical': baseline.strip() == candidate.strip(), 'changes': changes}
    files = {'baseline.md': baseline, 'candidate.md': candidate,
             'problem.md': pair['problem'].strip().encode()}
    def snapshot(ident, order):
        contents = dict(files, **{'audit_input.md': input_text(pair['problem'], baseline, candidate, changes, order).encode()})
        return {name: exact(root / 'model_inputs' / ident / name, data) for name, data in contents.items()}
    case['files'] = snapshot(case_id, 'forward')
    case['input_sha256'] = case['files']['audit_input.md']
    tasks = []
    if not case['identical']:
        for model in MODELS:
            for order in ORDERS:
                ident = f'{case_id}_{model}_{order}'
                task = {**case, 'case_id': ident, 'original_case_id': case_id,
                        'model_key': model, 'order': order,
                        'seed_key': f"post-resolver-preservation:{runtime['seed_namespace']}:{case_id}"}
                task['files'] = snapshot(ident, order)
                task['input_sha256'] = task['files']['audit_input.md']
                tasks.append(task)
    pins = {name: exact(root / name, data) for name, data in {
        'AUDIT_PROMPT.md': (HERE / 'AUDIT_PROMPT.md').read_bytes(),
        'BF_CUE.md': (HERE / 'BF_CUE.md').read_bytes(),
        'manifest.json': encoded({'cases': [case]}),
        'audit_plan.json': encoded({'audits': tasks})}.items()}
    cfg = {'policy_id': POLICY_ID, 'validator_version': VERSION, 'release_sha256': release_sha256,
           'pins': pins, 'workers_total': WORKERS_TOTAL, 'workers_per_model': MODEL_WORKERS, 'temperature': 0.2,
           'model_timeout_sec': runtime['model_timeout_sec'],
           'seed_namespace': runtime['seed_namespace'],
           'auditors': {m: {'model': model, 'endpoint': runtime[m + '_endpoint']} for m, model in MODELS.items()}}
    exact(root / 'config.json', encoded(cfg))
    return case, tasks


def verify_inputs(root):
    root = Path(root)
    cfg = read(root / 'config.json')
    if cfg['policy_id'] != POLICY_ID or cfg['validator_version'] != VERSION:
        raise ValueError('Unknown audit policy')
    if (cfg['workers_total'] != WORKERS_TOTAL or cfg.get('workers_per_model') != MODEL_WORKERS or cfg['temperature'] != 0.2
            or {m: a['model'] for m, a in cfg['auditors'].items()} != MODELS):
        raise ValueError('Audit model or sampling policy changed')
    for name, expected in cfg['pins'].items():
        if digest((root / name).read_bytes()) != expected:
            raise ValueError('Audit input pin changed: ' + name)
    for name in ('AUDIT_PROMPT.md', 'BF_CUE.md'):
        if (root / name).read_bytes() != (HERE / name).read_bytes():
            raise ValueError('Audit prompt differs from this release')
    cases = read(root / 'manifest.json')['cases']
    tasks = read(root / 'audit_plan.json')['audits']
    if len(cases) != 1:
        raise ValueError('Expected one bound lane')
    case = cases[0]
    for item in [case, *tasks]:
        for name, expected in item['files'].items():
            if digest((root / 'model_inputs' / item['case_id'] / name).read_bytes()) != expected:
                raise ValueError('Proof/input snapshot changed: ' + name)
    return cfg, case, tasks


def verified_vote(root, task):
    """Reparse saved output, ignoring any untrusted saved accept/reject field."""
    folder = Path(root) / 'cases' / task['case_id']
    result = read(folder / 'result.json')
    call_path = folder / 'audit/call_result.json'
    vote = {'model_key': task['model_key'], 'order': task['order'],
            'original_case_id': task['original_case_id'], 'valid': False, 'decision': KEEP}
    if not call_path.exists():
        return {**vote, 'error': result.get('error', 'Audit call did not complete')}
    call = read(call_path)
    binding = verify_audit_binding(root, task, result, call)
    return {**vote, **validate_audit(call['text'], task), 'binding_verified': binding['verified']}


def collect(root, baseline, candidate, release_sha256, *, expected_case=None, runtime=None):
    """Return a fresh selection from bound responses, without any inference."""
    root = Path(root)
    cfg, case, tasks = verify_inputs(root)
    if (cfg['release_sha256'] != release_sha256 or digest(baseline) != case['baseline_sha256']
            or digest(candidate) != case['candidate_sha256']):
        raise ValueError('Audit belongs to different proofs or release')
    if expected_case is not None:
        problem = (root / 'model_inputs' / case['case_id'] / 'problem.md').read_text()
        if (any(case[k] != expected_case[k] for k in ('problem_id', 'candidate_id'))
                or problem != expected_case['problem'].strip()):
            raise ValueError('Audit problem or lane identity changed')
    if runtime is not None:
        if (cfg['seed_namespace'] != runtime['seed_namespace']
                or cfg['model_timeout_sec'] != runtime['model_timeout_sec']
                or any(cfg['auditors'][m]['endpoint'] != runtime[m + '_endpoint'] for m in MODELS)):
            raise ValueError('Audit runtime differs from saved run')
    if case['identical']:
        return {'decision': ACCEPT, 'state': 'identical_no_calls', 'audit_attempted': False,
                'candidate_approvals': 0, 'required_approvals': 0, 'votes': []}
    votes = []
    for task in tasks:
        try:
            vote = verified_vote(root, task)
        except Exception as error:
            vote = {'model_key': task['model_key'], 'order': task['order'],
                    'original_case_id': case['case_id'], 'valid': False, 'decision': KEEP,
                    'error': f'{type(error).__name__}: {error}'}
        votes.append(vote)
    result = select_candidate(case['case_id'], votes, tuple(MODELS))
    return {**result, 'state': 'audited' if all(v['valid'] for v in votes) else 'failure_fallback',
            'audit_attempted': True, 'votes': votes,
            'order_disagreement': {m: len({v['decision'] for v in votes if v['model_key'] == m}) > 1
                                   for m in MODELS}}


def execute_task(root, task, caller):
    root = Path(root)
    cfg, _, _ = verify_inputs(root)
    folder = root / 'cases' / task['case_id']
    folder.mkdir(parents=True, exist_ok=True)
    completed = folder / 'result.json'
    if completed.exists():
        return verified_vote(root, task)
    prompt = (root / 'AUDIT_PROMPT.md').read_text()
    result = {k: task[k] for k in ('case_id', 'original_case_id', 'problem_id', 'model_key', 'order')}
    result.update(binding=digest(json.dumps(task, sort_keys=True).encode() + prompt.encode()),
                  started_at=datetime.now(timezone.utc).isoformat())
    began = time.monotonic()
    try:
        call_dir = folder / 'audit'
        if (call_dir / 'call_result.json').exists():
            call = read(call_dir / 'call_result.json')
        else:
            if call_dir.exists():
                raise ValueError('Interrupted audit preserved; no duplicate model call')
            call_dir.mkdir()
            write(folder / 'call_started.json', result)
            auditor = cfg['auditors'][task['model_key']]
            call = caller(**auditor, system_prompt=prompt,
                user_prompt=(root / 'model_inputs' / task['case_id'] / 'audit_input.md').read_text(),
                output_dir=call_dir, stage_name='post_resolver_replacement_audit', temperature=0.2,
                seed_key=task['seed_key'], reasoning_effort=None, parser=lambda text: {'valid': True},
                model_timeout_sec=cfg['model_timeout_sec'])
            # The canonical transport normally writes this; scripted transports may not.
            if not (call_dir / 'call_result.json').exists():
                write(call_dir / 'call_result.json', call)
        result['audit_sha256'] = call['final_sha256']
        verify_audit_binding(root, task, result, call)
        result.update(validate_audit(call['text'], task))
    except Exception as error:
        result.update(valid=False, decision=KEEP, error=f'{type(error).__name__}: {error}')
    result.update(finished_at=datetime.now(timezone.utc).isoformat(), elapsed_seconds=time.monotonic() - began)
    write(completed, result)
    return result


def run_job(job_path, caller):
    job = read(job_path)
    roots = [Path(path) for path in job['lane_roots']]
    # Preserve the recorded lane/model/order schedule. Separate server-sized pools
    # keep Qwen's waiting work from occupying available Gemma slots.
    all_tasks = [(root, task) for root in roots for task in verify_inputs(root)[2]]
    lookup = {(str(root), t['model_key'], t['order']): t for root, t in all_tasks}
    changed = [root for root in roots if verify_inputs(root)[2]]
    schedule = []
    for i in range(len(changed)):
        for offset, model, order in ((0, 'gemma', 'forward'), (1, 'qwen', 'forward'),
                                     (2, 'gemma', 'reverse'), (0, 'qwen', 'reverse')):
            root = changed[(i + offset) % len(changed)]
            schedule.append((root, lookup[(str(root), model, order)]))
    output = Path(job_path).parent
    began = time.monotonic()
    status = {'state': 'running', 'workers_total': WORKERS_TOTAL, 'workers_per_model': dict(MODEL_WORKERS),
              'total_calls': len(schedule), 'completed_calls': 0,
              'active_calls': 0, 'active_per_model': {model: 0 for model in MODELS},
              'max_concurrency_observed': 0, 'max_concurrency_per_model': {model: 0 for model in MODELS},
              'submission_order': [task['case_id'] for _, task in schedule]}
    write(output / 'status.json', status)
    lock = threading.Lock()

    def monitored(root, task):
        model = task['model_key']
        with lock:
            status['active_calls'] += 1
            status['active_per_model'][model] += 1
            status['max_concurrency_observed'] = max(status['max_concurrency_observed'], status['active_calls'])
            status['max_concurrency_per_model'][model] = max(
                status['max_concurrency_per_model'][model], status['active_per_model'][model])
            write(output / 'status.json', status)
        try:
            return execute_task(root, task, caller)
        finally:
            with lock:
                status['active_calls'] -= 1
                status['active_per_model'][model] -= 1
                write(output / 'status.json', status)

    with ExitStack() as stack:
        pools = {model: stack.enter_context(ThreadPoolExecutor(max_workers=workers))
                 for model, workers in MODEL_WORKERS.items()}
        futures = [pools[task['model_key']].submit(monitored, root, task) for root, task in schedule]
        for future in as_completed(futures):
            future.result()
            with lock:
                status['completed_calls'] += 1
                write(output / 'status.json', status)
    selections = []
    for root in roots:
        cfg, case, _ = verify_inputs(root)
        files = root / 'model_inputs' / case['case_id']
        result = collect(root, (files / 'baseline.md').read_bytes(), (files / 'candidate.md').read_bytes(), cfg['release_sha256'])
        write(root / 'selection.json', result)
        selections.append({'candidate_id': case['candidate_id'], **result})
    status.update(state='completed', elapsed_seconds=time.monotonic() - began, selections=selections)
    write(output / 'status.json', status)
    return status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--job', required=True, type=Path)
    args = parser.parse_args()
    # Model imports occur only in the explicit live worker, never in collection.
    from scripts import run_v263_v290 as queue
    from experiments.local_math_verifier import refinement_bf_policy as policy
    _, backend = queue.load_engines()
    prompt = (HERE / 'AUDIT_PROMPT.md').read_text()
    policy.ROLE_SPECIFIC_CUES['post_resolver_audit'] = (HERE / 'BF_CUE.md').read_text()
    route = policy.make_route('post_resolver_audit', r'post_resolver_replacement_audit_cap_[0-9]+', prompt)
    events = args.job.parent / ('bf_events_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.jsonl')
    with (args.job.parent / 'audit.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            with policy.install(backend.v263.parent._budget_forcing, policy.ROLE_SPECIFIC, events, routes=[route]):
                run_job(args.job, backend.repair_boundary.default_markdown_call)
        except Exception as error:
            path = args.job.parent / 'status.json'
            status = read(path) if path.exists() else {}
            write(path, {**status, 'state': 'failed', 'error': f'{type(error).__name__}: {error}'})
            raise


if __name__ == '__main__':
    main()
