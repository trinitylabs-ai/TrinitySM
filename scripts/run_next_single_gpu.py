#!/usr/bin/env python3
"""Select a disjoint problem set and run it after an existing single-GPU run."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import random
import re
import sys
import time

import run_single_gpu as runner

ROOT = Path(__file__).resolve().parents[1]


def identifier(value):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,95}', value):
        raise argparse.ArgumentTypeError('Use a simple run ID of at most 96 characters.')
    return value


def prepare(args):
    if args.run_id == args.after_run:
        raise ValueError('The next run needs a fresh run ID.')
    source = ROOT / '.workshop/single_gpu' / args.after_run / 'plan.json'
    data = source.read_bytes()
    prior = json.loads(data)
    if prior.get('schema') != 'workshop-single-gpu-run-v1' or prior.get('run_id') != args.after_run:
        raise ValueError('Previous run plan has the wrong identity.')
    excluded = {(j['benchmark'], j['problem_id']) for j in prior['jobs']}
    if not excluded or len(excluded) != len(prior['jobs']):
        raise ValueError('Previous run plan has empty or duplicate problems.')
    counts = dict(zip(runner.BENCHMARKS, (args.imo_count, args.basic_count, args.advanced_count)))
    if any(n < 0 for n in counts.values()) or not sum(counts.values()):
        raise ValueError('Select at least one problem with nonnegative counts.')
    rng = random.Random(args.sample_seed)
    selected, known = [], set()
    for benchmark, count in counts.items():
        rows = runner.read(ROOT / 'benchmarks' / benchmark / 'catalog.json')['generation_inputs']['files']
        ids = sorted(row['problem_id'] for row in rows)
        if len(ids) != len(set(ids)):
            raise ValueError('Duplicate catalog problem IDs: ' + benchmark)
        known.update((benchmark, pid) for pid in ids)
        pool = [pid for pid in ids if (benchmark, pid) not in excluded]
        if count > len(pool):
            raise ValueError(f'{benchmark}: only {len(pool)} unselected problems remain; requested {count}.')
        selected.extend(sorted(rng.sample(pool, count)))
    if excluded - known:
        raise ValueError('Previous plan contains unknown benchmark/problem IDs.')
    argv = ['--benchmark', 'all', '--gpu', str(args.gpu), '--broker-port', str(args.broker_port),
            '--run-id', args.run_id, '--solver-python', str(args.solver_python)]
    for pid in selected:
        argv += ['--problem-id', pid]
    if args.generation_seed is not None:
        argv += ['--generation-seed', str(args.generation_seed)]
    # Reuse the unchanged runner's path, input-hash and output-collision checks.
    native = runner.plan(argparse.Namespace(benchmark='all', problem_id=selected,
        run_id=args.run_id, gpu=args.gpu, broker_port=args.broker_port,
        solver_python=args.solver_python, generation_seed=args.generation_seed))
    return dict(schema='workshop-next-single-gpu-v1', run_id=args.run_id, after_run=args.after_run,
        previous_plan=str(source), previous_plan_sha256=hashlib.sha256(data).hexdigest(),
        excluded_problems=[dict(benchmark=b, problem_id=p) for b, p in sorted(excluded)],
        sample_seed=args.sample_seed, counts=counts, selected_problems=selected,
        generation_seed=args.generation_seed, native_plan=native,
        argv=argv)


def previous_finished(record):
    source = Path(record['previous_plan'])
    if hashlib.sha256(source.read_bytes()).hexdigest() != record['previous_plan_sha256']:
        raise ValueError('Previous run plan changed while waiting.')
    status = runner.read(source.with_name('status.json'))
    state = status.get('state')
    if state in ('failed', 'interrupted'):
        raise ValueError(f'Previous runner is {state}; inspect it before scheduling another run.')
    if state in ('starting', 'running', 'waiting_for_server'):
        return False
    if state not in ('completed', 'completed_with_failures'):
        raise ValueError('Unknown previous run status: ' + str(state))
    expected = {p['problem_id'] for p in record['excluded_problems']}
    jobs = status.get('jobs', [])
    if (len(jobs) != len(expected) or {j['problem_id'] for j in jobs} != expected
            or any(type(j.get('returncode')) is not int for j in jobs)):
        raise ValueError('Previous terminal status does not confirm that every problem exited.')
    # A terminal status can be written shortly before broker cleanup finishes.
    lock = ROOT / '.workshop/servers/single_gpu_run.lock'
    if lock.exists():
        with lock.open('r') as stream:
            try:
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return False
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--after-run', type=identifier, required=True)
    parser.add_argument('--run-id', type=identifier, required=True)
    for group in ('imo', 'basic', 'advanced'):
        parser.add_argument('--' + group + '-count', type=int, default=2)
    parser.add_argument('--sample-seed', type=runner.generation_seed, default=43)
    parser.add_argument('--generation-seed', type=runner.generation_seed,
                        help='Omit to retain the original fixed generation settings.')
    parser.add_argument('--gpu', type=int, default=0)
    parser.add_argument('--broker-port', type=int, default=18890)
    parser.add_argument('--solver-python', type=Path, default=ROOT / '.venv-solver/bin/python')
    parser.add_argument('--wait', action='store_true', help='Wait for the previous run to exit, then launch.')
    parser.add_argument('--dry-run', action='store_true', help='Print selection and plan without waiting or writing files.')
    args = parser.parse_args(argv)
    try:
        record = prepare(args)
        if args.dry_run:
            print(json.dumps(record, indent=2))
            return 0
        destination = ROOT / '.workshop/runs' / (args.run_id + '.followup.json')
        if destination.exists():
            raise ValueError('Follow-up plan already exists; choose a fresh run ID.')
        print('Next problems: ' + ', '.join(record['selected_problems']), flush=True)
        announced = False
        while not previous_finished(record):
            if not args.wait:
                raise ValueError('Previous run is still active; run later or use --wait.')
            if not announced:
                print(f'Waiting for {args.after_run} to finish and release the GPU scheduler.', flush=True)
                announced = True
            time.sleep(15)
        # Recheck fresh paths after waiting. The native runner acquires its own
        # exclusive scheduler lock before any model work, closing launch races.
        if prepare(args) != record:
            raise ValueError('Selection or configuration changed while waiting.')
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open('x') as stream:
            json.dump(record, stream, indent=2)
            stream.write('\n')
        print(f'Previous work exited. Starting {args.run_id}; plan: {destination}', flush=True)
        os.execv(sys.executable, [sys.executable, '-u', '-B', str(ROOT / 'scripts/run_single_gpu.py'), *record['argv']])
    except (OSError, ValueError, KeyError) as error:
        parser.error(str(error))
    except KeyboardInterrupt:
        return 130


if __name__ == '__main__':
    raise SystemExit(main())
