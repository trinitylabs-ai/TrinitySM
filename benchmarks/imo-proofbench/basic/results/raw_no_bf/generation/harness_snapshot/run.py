#!/usr/bin/env python3
"""Four Gemma raw drafts per problem, one request per draft, with MTP=4."""
from __future__ import annotations

import argparse
import concurrent.futures
import fcntl
import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SCHEMA = 'gemma4-four-raw-mtp4-no-budget-forcing-v1'
MODEL = 'google/gemma-4-31B-it'
CANDIDATES = (
    ('t10_r01', 1.0, 2360094352), ('t10_r02', 1.0, 2367214500),
    ('t07_r01', 0.7, 3233582896), ('t07_r02', 0.7, 220229344),
)
PROMPT_HASHES = {
    'system.txt': 'aea702bbb2bb3724a3c50ae71117337361c1856b7fa5a8928fbca5f095385225',
    'user_prefix.txt': '59d1388a237de6a1b77ef9570c9e0c3715ce98f30df349ca9617e195ea7f45cb',
    'user_suffix.txt': '7daed8aac343155656d7aed6763aaa78d8eb2ed531319035ce9770e8b7db441a',
}


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    tmp.replace(path)


def prompts():
    result = {}
    for name, expected in PROMPT_HASHES.items():
        text = (HERE / 'prompts' / name).read_text(encoding='utf-8')
        if sha(text) != expected:
            raise ValueError(f'Frozen prompt changed: {name}')
        result[name] = text
    return result


def collect_problems(directory, selected):
    rows = []
    for path in sorted(directory.glob('*.json')):
        value = read(path)
        if not isinstance(value, dict) or set(value) not in ({'problem_id', 'problem'}, {'problem_id', 'claim'}):
            raise ValueError(f'Expected only problem_id and problem/claim: {path}')
        pid, statement = value['problem_id'], value.get('problem', value.get('claim'))
        if not isinstance(pid, str) or not re.fullmatch(r'[A-Za-z0-9_-]+', pid):
            raise ValueError(f'Invalid problem ID: {path}')
        if not isinstance(statement, str) or not statement.strip():
            raise ValueError(f'Empty problem statement: {path}')
        rows.append({'problem_id': pid, 'problem': statement.strip()})
    rows.sort(key=lambda row: row['problem_id'])
    if not rows or len({r['problem_id'] for r in rows}) != len(rows):
        raise ValueError('Problem directory must contain unique statement-only JSON files')
    # Number before selection to retain the previous harness's seed derivation.
    rows = [dict(row, problem_number=i) for i, row in enumerate(rows, 1)]
    if selected:
        unknown = set(selected) - {r['problem_id'] for r in rows}
        if unknown:
            raise ValueError(f'Unknown requested problems: {sorted(unknown)}')
        rows = [r for r in rows if r['problem_id'] in selected]
    return rows


def stable_seed(number, candidate, base, offset):
    base = (base + offset) & 0xFFFFFFFF
    material = f'v048:p{number}:{candidate}:{base}:cold_draft'
    return int.from_bytes(hashlib.sha256(material.encode()).digest()[:4], 'big') or 1


def endpoint_url(value):
    value = value.rstrip('/')
    parsed = urllib.parse.urlsplit(value)
    if (parsed.scheme != 'http' or parsed.hostname not in {'localhost', '127.0.0.1', '::1'}
            or parsed.path != '/v1' or parsed.query or parsed.fragment or parsed.username):
        raise ValueError('Use the local vLLM endpoint, e.g. http://127.0.0.1:8030/v1')
    return value


def make_request(problem, candidate, config, prompt):
    cid, temperature, base = candidate
    return {
        'model': MODEL,
        'messages': [
            {'role': 'system', 'content': prompt['system.txt']},
            {'role': 'user', 'content': prompt['user_prefix.txt'] + problem['problem'] + prompt['user_suffix.txt']},
        ],
        'temperature': temperature, 'top_p': 0.95, 'top_k': 64,
        'seed': stable_seed(problem['problem_number'], cid, base, config['raw_seed_offset']),
        'max_tokens': config['max_tokens'], 'n': 1, 'stream': False,
        'min_tokens': 0, 'ignore_eos': False,
        'chat_template_kwargs': {'enable_thinking': True},
    }


def http_json(url, payload=None, timeout=15):
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode('utf-8')
    request = urllib.request.Request(url, data=data, headers={
        'Content-Type': 'application/json', 'Authorization': 'Bearer EMPTY',
    }, method='GET' if data is None else 'POST')
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def option(argv, name):
    values = []
    for i, arg in enumerate(argv):
        if arg == name and i + 1 < len(argv):
            values.append(argv[i + 1])
        elif arg.startswith(name + '='):
            values.append(arg.split('=', 1)[1])
    return values[-1] if values else None


def validate_server_arguments(argv):
    speculative = json.loads(option(argv, '--speculative-config') or '{}')
    if speculative.get('method') != 'mtp' or speculative.get('num_speculative_tokens') != 4:
        raise ValueError('Gemma server must run with method=mtp and num_speculative_tokens=4')
    dtype = option(argv, '--dtype')
    if dtype not in {'bfloat16', 'bf16'}:
        raise ValueError('Gemma server must preserve the BF16 model configuration')
    if option(argv, '--reasoning-parser') != 'gemma4':
        raise ValueError('Gemma server must use the gemma4 reasoning parser')
    return {'speculative_config': speculative, 'dtype': dtype, 'reasoning_parser': 'gemma4'}


def verify_server(endpoint, proc_root=Path('/proc')):
    models = http_json(endpoint + '/models')
    served = [r for r in models.get('data', []) if r.get('id') == MODEL]
    if len(served) != 1:
        raise ValueError(f'Endpoint must serve {MODEL}')
    port = urllib.parse.urlsplit(endpoint).port or 80
    inodes = set()
    for name in ('tcp', 'tcp6'):
        path = proc_root / 'net' / name
        if not path.exists():
            continue
        for line in path.read_text().splitlines()[1:]:
            fields = line.split()
            if len(fields) > 9 and fields[3] == '0A' and int(fields[1].rsplit(':', 1)[1], 16) == port:
                inodes.add(fields[9])
    candidates = []
    for path in proc_root.glob('[0-9]*/cmdline'):
        try:
            raw = path.read_bytes()
            argv = raw.decode().rstrip('\0').split('\0')
            if not any(Path(arg).name == 'vllm' or arg == 'vllm.entrypoints.openai.api_server' for arg in argv):
                continue
            if int(option(argv, '--port') or 8000) != port:
                continue
            sockets = set()
            for fd in (path.parent / 'fd').iterdir():
                try:
                    sockets.add(os.readlink(fd))
                except OSError:
                    continue
            if not any(f'socket:[{inode}]' in sockets for inode in inodes):
                continue
            start_ticks = (path.parent / 'stat').read_text().rsplit(')', 1)[1].split()[19]
            candidates.append({'pid': int(path.parent.name), 'process_start_ticks': start_ticks,
                'argv_sha256': hashlib.sha256(raw).hexdigest(), **validate_server_arguments(argv)})
        except (OSError, UnicodeError):
            continue
    if len(candidates) != 1:
        raise ValueError('Cannot verify one local listening vLLM process; MTP=4 is not established')
    return {'verified_at': now(), 'endpoint': endpoint, 'model': MODEL,
            'model_root': served[0].get('root'), 'max_model_len': served[0].get('max_model_len'),
            **candidates[0]}


def decode_response(raw):
    if len(raw.get('choices', [])) != 1:
        raise ValueError('Expected exactly one generated choice')
    choice = raw['choices'][0]
    message = choice.get('message') or {}
    if message.get('tool_calls') or message.get('function_call'):
        raise ValueError('Unexpected tool call in a proof-generation response')
    proof = message.get('content') or ''
    reasoning = message.get('reasoning_content') or message.get('reasoning') or ''
    if not isinstance(proof, str) or not isinstance(reasoning, str):
        raise ValueError('Expected text content and reasoning')
    proof, reasoning = proof.strip(), reasoning.strip()
    finish = choice.get('finish_reason')
    if finish not in {'stop', 'length'}:
        raise ValueError(f'Unexpected finish reason: {finish!r}')
    state = 'truncated' if finish == 'length' else 'completed' if proof else 'reasoning_only' if reasoning else 'empty_response'
    return state, proof, reasoning, finish


def save_response(case, raw, result):
    state, proof, reasoning, finish = decode_response(raw)
    (case / 'reasoning.txt').write_text(reasoning + ('\n' if reasoning else ''), encoding='utf-8')
    if proof:
        (case / 'draft_proof.md').write_text(proof + '\n', encoding='utf-8')
    result.update(state=state, finish_reason=finish, usage=raw.get('usage') or {}, response_id=raw.get('id'),
        raw_response_sha256=sha(json.dumps(raw, sort_keys=True)),
        proof_path=str(case / 'draft_proof.md') if proof else None,
        proof_sha256=sha(proof) if proof else None, reasoning_sha256=sha(reasoning),
        final_content_present=bool(proof), truncated=finish == 'length')
    return result


def generate(case, request, config, server):
    started = time.monotonic()
    result = {'state': 'running', 'started_at': now(), 'request_sha256': sha(json.dumps(request, sort_keys=True)),
        'model': MODEL, 'seed': request['seed'], 'temperature': request['temperature'],
        'budget_forcing': False, 'continuation_requests': 0, 'generation_requests': 1,
        'server_pid': server['pid'], 'server_process_start_ticks': server['process_start_ticks'],
        'server_argv_sha256': server['argv_sha256']}
    write(case / 'request_started.json', result)
    try:
        raw = http_json(config['endpoint'] + '/chat/completions', request, config['timeout_sec'])
        write(case / 'raw_response.json', raw)
        save_response(case, raw, result)
    except Exception as error:
        if isinstance(error, urllib.error.HTTPError):
            (case / 'http_error.txt').write_bytes(error.read())
        result.update(state='failed', error=f'{type(error).__name__}: {error}')
    result.update(completed_at=now(), elapsed_seconds=time.monotonic() - started)
    write(case / 'result.json', result)
    return result


def cached_result(case, expected):
    if not (case / 'result.json').exists():
        if (case / 'request_started.json').exists():
            previous = read(case / 'request_started.json')
            if previous['request_sha256'] != expected:
                raise ValueError(f'Interrupted request identity changed: {case}')
            if (case / 'raw_response.json').exists():
                try:
                    result = save_response(case, read(case / 'raw_response.json'), dict(previous))
                    result.update(recovered_from_saved_response=True, completed_at=now(), elapsed_seconds=None)
                except (ValueError, TypeError, KeyError) as error:
                    result = dict(previous, state='failed', error=f'Invalid saved response: {error}')
            else:
                result = dict(previous, state='interrupted',
                              error='Prior request has no saved result; automatic regeneration is disabled')
            write(case / 'result.json', result)
            return result
        return None
    result = read(case / 'result.json')
    if result['request_sha256'] != expected:
        raise ValueError(f'Cached request identity changed: {case}')
    if result.get('proof_path') and sha((case / 'draft_proof.md').read_text().strip()) != result['proof_sha256']:
        raise ValueError(f'Saved proof changed: {case}')
    if result.get('reasoning_sha256') is not None and sha((case / 'reasoning.txt').read_text().strip()) != result['reasoning_sha256']:
        raise ValueError(f'Saved reasoning changed: {case}')
    if result.get('raw_response_sha256') and sha(json.dumps(read(case / 'raw_response.json'), sort_keys=True)) != result['raw_response_sha256']:
        raise ValueError(f'Saved response changed: {case}')
    return result


def summarize(output, tasks, results, state, active_problem=None):
    rows = [dict(task, **results.get((task['problem_id'], task['candidate_id']), {'state': 'pending'})) for task in tasks]
    counts = Counter(row['state'] for row in rows)
    value = {'schema': SCHEMA, 'state': state, 'updated_at': now(), 'active_problem': active_problem,
        'total': len(rows), 'finished': sum(row['state'] != 'pending' for row in rows),
        'counts': dict(counts), 'proofs_saved': sum(bool(row.get('proof_path')) for row in rows),
        'budget_forcing': False, 'rows': rows}
    write(output / 'summary.json', value)
    write(output / 'status.json', {k: v for k, v in value.items() if k != 'rows'})
    return value


def run(args):
    if not 0 <= args.raw_seed_offset <= 0xFFFFFFFF or args.max_tokens < 1 or args.timeout_sec < 1:
        raise ValueError('Invalid seed offset, token cap, or timeout')
    output = args.output_dir.resolve()
    prompt = prompts()
    problems = collect_problems(args.problem_dir, args.problem_id)
    config = {'endpoint': endpoint_url(args.endpoint), 'model': MODEL, 'max_tokens': args.max_tokens,
        'timeout_sec': args.timeout_sec, 'raw_seed_offset': args.raw_seed_offset,
        'workers': 4, 'mtp_speculative_tokens': 4, 'budget_forcing': False,
        'requests_per_candidate': 1, 'prompt_sha256': PROMPT_HASHES,
        'runner_sha256': sha(Path(__file__).read_text())}
    identity = {'schema': SCHEMA, 'config': config, 'problems': problems}
    fingerprint = sha(json.dumps(identity, sort_keys=True))
    if output.exists() and any(output.iterdir()) and not args.resume:
        raise ValueError('Use an empty output directory, or --resume with the original settings')
    output.mkdir(parents=True, exist_ok=True)
    with (output / '.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        manifest = output / 'manifest.json'
        if manifest.exists():
            if read(manifest)['fingerprint'] != fingerprint:
                raise ValueError('Resume changed the inputs, prompts, code, or generation settings')
        else:
            write(manifest, dict(identity, fingerprint=fingerprint, created_at=now()))
        tasks, requests, results = [], {}, {}
        for problem in problems:
            pid = problem['problem_id']
            frozen = output / 'inputs' / f'{pid}.json'
            if frozen.exists() and read(frozen) != problem:
                raise ValueError(f'Frozen input changed: {pid}')
            write(frozen, problem)
            for candidate in CANDIDATES:
                cid = candidate[0]
                case = output / 'problems' / pid / 'candidates' / cid
                request = make_request(problem, candidate, config, prompt)
                expected = sha(json.dumps(request, sort_keys=True))
                if (case / 'request.json').exists() and read(case / 'request.json') != request:
                    raise ValueError(f'Frozen request changed: {pid}/{cid}')
                write(case / 'request.json', request)
                task = {'problem_id': pid, 'problem_number': problem['problem_number'], 'candidate_id': cid,
                    'checkpoint': 'raw_draft_no_budget_forcing', 'request_path': str(case / 'request.json'),
                    'result_path': str(case / 'result.json')}
                tasks.append(task); requests[pid, cid] = request
                existing = cached_result(case, expected)
                if existing:
                    results[pid, cid] = existing
        if not args.execute_models:
            return summarize(output, tasks, results, 'dry_run')
        server = None
        for problem in problems:
            pid = problem['problem_id']
            pending = [t for t in tasks if t['problem_id'] == pid and (pid, t['candidate_id']) not in results]
            if not pending:
                continue
            summarize(output, tasks, results, 'checking_server', pid)
            try:
                current = verify_server(config['endpoint'])
                if server and any(current[k] != server[k] for k in ('pid', 'process_start_ticks', 'argv_sha256')):
                    raise ValueError('Gemma server changed during the run')
                prior_server = output / 'server_verification.json'
                if prior_server.exists() and read(prior_server)['argv_sha256'] != current['argv_sha256']:
                    raise ValueError('Gemma server launch configuration changed since the previous request')
                if current.get('max_model_len') and config['max_tokens'] >= current['max_model_len']:
                    raise ValueError('Token cap leaves no context space for the prompt')
            except Exception as error:
                summarize(output, tasks, results, 'failed_server_verification', pid)
                write(output / 'server_failure.json', {'at': now(), 'error': f'{type(error).__name__}: {error}'})
                raise
            server = current
            write(output / 'server_verification.json', server)
            write(output / 'server_verifications' / f'{pid}_{time.time_ns()}.json', server)
            summarize(output, tasks, results, 'running', pid)
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
                futures = {pool.submit(generate, Path(t['result_path']).parent,
                    requests[pid, t['candidate_id']], config, server): t for t in pending}
                while futures:
                    done, _ = concurrent.futures.wait(futures, timeout=60, return_when=concurrent.futures.FIRST_COMPLETED)
                    for future in done:
                        task = futures.pop(future)
                        results[pid, task['candidate_id']] = future.result()
                    summary = summarize(output, tasks, results, 'running', pid)
                    print(json.dumps({k: v for k, v in summary.items() if k != 'rows'}), flush=True)
        complete = all(r['state'] == 'completed' for r in results.values())
        return summarize(output, tasks, results, 'completed' if complete else 'completed_with_issues')


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--problem-dir', type=Path, default=REPO / 'data/imo_proofbench_basic_problem_only')
    parser.add_argument('--problem-id', action='append', default=[])
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--endpoint', default='http://127.0.0.1:8030/v1')
    parser.add_argument('--max-tokens', type=int, default=65536)
    parser.add_argument('--raw-seed-offset', type=int, default=0)
    parser.add_argument('--timeout-sec', type=float, default=14400)
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--execute-models', action='store_true', help='Without this flag, only stage requests; no network calls')
    return parser.parse_args(argv)


if __name__ == '__main__':
    arguments = parse_args()
    try:
        summary = run(arguments)
    except Exception as error:
        # Do not overwrite another process's run status after a lock rejection.
        print(json.dumps({'state': 'error', 'error': f'{type(error).__name__}: {error}'}), flush=True)
        raise SystemExit(1)
    print(json.dumps({k: v for k, v in summary.items() if k != 'rows'}), flush=True)
    raise SystemExit(0 if summary['state'] in {'completed', 'dry_run'} else 2)
