"""Standalone execution and artifacts for selection after proof generation."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import secrets
import signal
import subprocess
import sys
import time

from . import VERSION
from . import inputs as input_io
from .client import NativeBFClient, POLICY
from .protocols import protocol_identity
from .selector import select_problem

ROOT = Path(__file__).resolve().parents[2]


def now():
    return datetime.now(timezone.utc).isoformat()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temp.replace(path)


def code_identity():
    paths = sorted(Path(__file__).parent.glob('*.py'))
    adapter = ROOT / 'scripts/select_proofs.py'
    if adapter.is_file():
        paths.append(adapter)
    try:
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                                         stderr=subprocess.DEVNULL, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        commit = None
    return {'version': VERSION, 'git_commit': commit,
            'files': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
            'protocols': protocol_identity()}


def metadata(inputs):
    """Keep source identity on disk without ever including it in model packets."""
    result = {k: v for k, v in inputs.items() if k != 'problems'}
    result['problems'] = []
    for problem in inputs['problems']:
        result['problems'].append({
            **{k: v for k, v in problem.items() if k not in {'problem', 'candidates'}},
            'candidates': [{k: v for k, v in c.items() if k != 'proof'} for c in problem['candidates']]})
    return result


def report(inputs, outcomes, state):
    lines = ['# Independent proof selection', '', f'Run: `{inputs["run_id"]}`',
             f'State: **{state}**', '',
             'Selections are model judgments, not external grades or formal proof verification.',
             'Each selected file is an unchanged member of its four-candidate input bank.', '',
             '| Problem | Selected candidate | Basis | Selection time | Proof |',
             '| --- | --- | --- | ---: | --- |']
    for row in outcomes:
        pid = row['problem_id']
        if row['state'] == 'completed':
            lines.append(f'| {pid} | {row["selected_candidate_id"]} | {row["selection_basis"]} | '
                         f'{row["elapsed_seconds"]:.1f}s | [proof](problems/{pid}/selected_proof.md) |')
        else:
            lines.append(f'| {pid} | — | {row["state"]} | — | — |')
    lines += ['', 'Full assessments, uncertainty and comparison tie handling are recorded in each',
              '`problems/<problem_id>/selection.json`. Native extended reasoning requests, token IDs, reasoning,',
              'responses and token accounting remain under that problem directory.', '',
              'The final comparison uses compact assessment packets; individual reviews and audits',
              'read the full candidate proof. This evidence-only comparison is itself fallible.', '',
              'The generation pipeline and its four final proof exports were not modified.', '']
    return '\n'.join(lines)


class SelectionInterrupted(KeyboardInterrupt):
    def __init__(self, signum):
        self.signum = signum
        super().__init__(f'Selection interrupted by signal {signum}')


def execute(inputs, output_dir, client, *, seed, max_rounds, configuration=None):
    """No model calls until all inputs, protocols and destination are preflighted."""
    output_dir = Path(output_dir).absolute()
    input_io.verify_sources(inputs)
    identity = code_identity()
    input_io.require(not output_dir.exists() and not output_dir.is_symlink(),
                     'Selection output already exists; choose a new selection ID or output directory')
    input_io.require(not any(p.is_symlink() for p in output_dir.parents),
                     'Selection output must not have symlink parents')
    output_dir.mkdir(parents=True, exist_ok=False)
    state = {'state': 'running', 'run_id': inputs['run_id'], 'started_at': now(),
             'selection_seed': seed, 'outcomes': []}
    started = time.monotonic()
    write(output_dir / 'plan.json', {'schema': 'proof-selector-plan-v1', 'inputs': metadata(inputs),
          'implementation': identity, 'selection_seed': seed, 'max_rounds': max_rounds,
          'configuration': configuration or {},
          'bf_policy': POLICY,
          'external_grading': False, 'proof_modification': False})
    write(output_dir / 'status.json', state)
    try:
        for index, problem in enumerate(inputs['problems'], 1):
            input_io.verify_sources(inputs)
            pid = problem['problem_id']
            state['active_problem'] = pid
            write(output_dir / 'status.json', state)
            print(f'{now()} {pid}: selecting {index}/{len(inputs["problems"])} from four final proofs', flush=True)
            directory = output_dir / 'problems' / pid
            directory.mkdir(parents=True, exist_ok=False)
            frozen = directory / 'inputs'
            frozen.mkdir()
            (frozen / 'problem.txt').write_text(problem['problem'], encoding='utf-8')
            for candidate in problem['candidates']:
                (frozen / (candidate['candidate_id'] + '.md')).write_bytes(candidate['proof'].encode('utf-8'))
            result = select_problem(problem_id=pid, problem=problem['problem'],
                candidates=problem['candidates'], client=client, output_dir=directory,
                seed=seed, max_rounds=max_rounds)
            selected = next(c for c in problem['candidates'] if c['candidate_id'] == result['selected_candidate_id'])
            input_io.require(result.get('state') == 'completed'
                             and result['selected_proof_sha256'] == selected['proof_file_sha256'],
                             'Selector result is not bound to the original candidate')
            input_io.verify_sources(inputs)
            (directory / 'selected_proof.md').write_bytes(selected['proof'].encode('utf-8'))
            state['outcomes'].append({'problem_id': pid, 'state': 'completed',
                'selected_candidate_id': result['selected_candidate_id'],
                'selected_proof_sha256': result['selected_proof_sha256'],
                'selection_basis': result['selection_basis'], 'elapsed_seconds': result['elapsed_seconds']})
            write(output_dir / 'status.json', state)
            (output_dir / 'REPORT.md').write_text(report(inputs, state['outcomes'], 'running'), encoding='utf-8')
            print(f'{now()} {pid}: selected {selected["candidate_id"]}; '
                  f'basis={result["selection_basis"]}; elapsed={result["elapsed_seconds"]:.1f}s', flush=True)
        input_io.verify_sources(inputs)
        input_io.require(code_identity() == identity, 'Selector implementation changed during execution')
        state['state'] = 'completed'
        return state
    except BaseException as error:
        state['state'] = 'interrupted' if isinstance(error, (KeyboardInterrupt, SystemExit)) else 'failed'
        if isinstance(error, SelectionInterrupted):
            state['exit_code'] = 128 + error.signum
        elif isinstance(error, KeyboardInterrupt):
            state['exit_code'] = 130
        elif isinstance(error, SystemExit):
            state['exit_code'] = error.code if isinstance(error.code, int) else None
        state['error'] = f'{type(error).__name__}: {error}'
        if state.get('active_problem') not in {r['problem_id'] for r in state['outcomes']}:
            state['outcomes'].append({'problem_id': state.get('active_problem'), 'state': state['state']})
        raise
    finally:
        state.pop('active_problem', None)
        state.update(finished_at=now(), elapsed_seconds=time.monotonic() - started)
        write(output_dir / 'status.json', state)
        (output_dir / 'REPORT.md').write_text(report(inputs, state['outcomes'], state['state']), encoding='utf-8')


def uint32(value):
    number = int(value)
    if not 0 <= number <= 0xFFFFFFFF:
        raise argparse.ArgumentTypeError('Seed must be in 0..4294967295')
    return number


def positive(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError('Value must be positive')
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(description='Select one saved proof per problem using an isolated native extended reasoning module.')
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--run-id', help='Completed 6+3+3 sampled suite ID')
    source.add_argument('--input-manifest', type=Path, help='Standalone hash-bound four-proof input bank')
    source.add_argument('--published-imo', action='store_true',
                        help='Use the 24 existing baseline IMO 2026 proofs in the public release snapshot')
    parser.add_argument('--problem-id', action='append', help='Select only these problem IDs; may be repeated')
    parser.add_argument('--selection-id', default=None)
    parser.add_argument('--output-dir', type=Path, help='Fresh directory; default .workshop/selections/<run>/<selection>')
    seeds = parser.add_mutually_exclusive_group()
    seeds.add_argument('--selection-seed', type=uint32, default=None)
    seeds.add_argument('--random-selection-seed', action='store_true')
    parser.add_argument('--max-rounds', type=int, choices=(1, 2, 3), default=3)
    parser.add_argument('--bf-extensions', type=int, choices=range(5), default=1)
    parser.add_argument('--thinking-budget', type=positive, default=65536)
    parser.add_argument('--answer-max-tokens', type=positive, default=8192)
    parser.add_argument('--max-input-tokens', type=positive, default=24576)
    parser.add_argument('--max-continuation-input-tokens', type=positive, default=98304)
    parser.add_argument('--timeout', type=positive, default=2400)
    parser.add_argument('--attempts', type=int, choices=(1, 2), default=2)
    parser.add_argument('--gemma-endpoint', default='http://127.0.0.1:8030/v1')
    parser.add_argument('--qwen-endpoint', default='http://127.0.0.1:8027/v1')
    parser.add_argument('--dry-run', action='store_true', help='Validate local inputs/protocols only; no writes or server calls')
    args = parser.parse_args(argv)
    previous = {}
    try:
        selection_id = input_io.identifier(args.selection_id or 'selection_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
        seed = secrets.randbits(32) if args.random_selection_seed else (args.selection_seed or 0)
        if args.published_imo:
            inputs = input_io.load_published_imo(ROOT, args.problem_id)
        elif args.run_id:
            inputs = input_io.load_suite(ROOT, args.run_id, args.problem_id)
        else:
            inputs = input_io.load_manifest(args.input_manifest, args.problem_id)
        output = args.output_dir or ROOT / '.workshop/selections' / inputs['run_id'] / selection_id
        input_io.require(not output.exists() and not output.is_symlink(), 'Selection output already exists')
        identity = code_identity()
        configuration = {key: getattr(args, key) for key in (
            'gemma_endpoint', 'qwen_endpoint', 'timeout', 'thinking_budget', 'answer_max_tokens',
            'bf_extensions', 'max_input_tokens', 'max_continuation_input_tokens', 'attempts')}
        if args.dry_run:
            print(json.dumps({'dry_run': True, 'run_id': inputs['run_id'], 'selection_id': selection_id,
                'selection_seed': seed, 'problem_ids': [p['problem_id'] for p in inputs['problems']],
                'output_dir': str(output), 'max_rounds': args.max_rounds, 'configuration': configuration,
                'bf_policy': POLICY, 'implementation': identity}, ensure_ascii=False, indent=2))
            return 0
        client = NativeBFClient(**configuration)
        def stop(signum, frame):
            raise SelectionInterrupted(signum)
        for signum in (signal.SIGINT, signal.SIGTERM):
            previous[signum] = signal.signal(signum, stop)
        print(f'Selection: {selection_id}\nSeed: {seed}\nReport: {output / "REPORT.md"}', flush=True)
        execute(inputs, output, client, seed=seed, max_rounds=args.max_rounds, configuration=configuration)
        return 0
    except SelectionInterrupted as error:
        print(str(error), file=sys.stderr)
        return 128 + error.signum
    except KeyboardInterrupt:
        return 130
    except Exception as error:
        print(f'Selection failed: {type(error).__name__}: {error}', file=sys.stderr)
        return 1
    finally:
        for signum, handler in previous.items():
            signal.signal(signum, handler)


if __name__ == '__main__':
    raise SystemExit(main())
