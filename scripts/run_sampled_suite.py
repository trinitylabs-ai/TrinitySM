#!/usr/bin/env python3
"""Run all six IMO 2026 problems, plus three random Basic and three Advanced problems."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import re
import secrets
import signal
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS = ('imo2026', 'imo-proofbench/basic', 'imo-proofbench/advanced')
DEFAULT_NAMESPACE = 'v263-v290:problem-only'


def uint32(value):
    number = int(value)
    if not 0 <= number <= 0xFFFFFFFF:
        raise argparse.ArgumentTypeError('Seed must be between 0 and 4294967295')
    return number


def now():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    temporary.replace(path)


def make_plan(run_id, sample_seed, generation_seed, solver_python, release='1.12.0'):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,127}', run_id):
        raise ValueError('Use a simple run ID: letters, numbers, underscore, dot or hyphen (max 128 characters)')
    rng = random.Random(sample_seed)
    namespace = DEFAULT_NAMESPACE if generation_seed is None else f'workshop-generation:{generation_seed}'
    offset = 0 if generation_seed is None else generation_seed
    jobs = []
    for benchmark in BENCHMARKS:
        base = ROOT / 'benchmarks' / benchmark
        catalog_path = base / 'catalog.json'
        catalog = json.loads(catalog_path.read_text())
        pool = sorted(catalog['generation_inputs']['files'], key=lambda row: row['problem_id'])
        if len({row['problem_id'] for row in pool}) != len(pool):
            raise ValueError(f'Duplicate problem IDs in {benchmark}')
        if benchmark == 'imo2026' and len(pool) != 6:
            raise ValueError('Expected all six IMO 2026 problems')
        selected = pool if benchmark == 'imo2026' else sorted(rng.sample(pool, 3), key=lambda row: row['problem_id'])
        for row in selected:
            path = base / row['path']
            if path.resolve().parent != (base / 'problems').resolve():
                raise ValueError(f'Expected a statement-only problem file: {path}')
            if hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
                raise ValueError(f'Problem input differs from catalog: {path}')
        output = base / 'results' / run_id
        if output.exists() or output.is_symlink():
            raise ValueError(f'Run already exists; choose a new --run-id: {output}')
        command = [str(solver_python), '-u', '-B', str(ROOT / 'benchmarks/run_experiment.py'),
                   '--benchmark', benchmark, '--run-id', run_id, '--release', release,
                   '--solver-python', str(solver_python), '--gemma-port', '8030', '--qwen-port', '8027',
                   '--raw-seed-offset', str(offset), '--seed-namespace', namespace, '--execute-models']
        for row in selected:
            command += ['--problem-id', row['problem_id']]
        jobs.append(dict(benchmark=benchmark, problem_ids=[row['problem_id'] for row in selected],
                         inputs=selected, catalog_sha256=hashlib.sha256(catalog_path.read_bytes()).hexdigest(),
                         command=command, console_log=str(output / 'generation/console.log'),
                         proofs=str(output / 'generation/run/proofs'),
                         final_results=str(output / 'generation/run/final_results.json')))
    return dict(schema='workshop-sampled-suite-v1', run_id=run_id, sample_seed=sample_seed,
                generation_seed=generation_seed, raw_seed_offset=offset, seed_namespace=namespace,
                problem_count=sum(len(job['problem_ids']) for job in jobs),
                candidates_per_problem=4, external_grading=False, jobs=jobs)


class Runner:
    def __init__(self):
        self.child = None
        self.stopped = None

    def stop(self, signum, _frame):
        self.stopped = signum
        if self.child is not None:
            try:
                self.child.send_signal(signum)
            except ProcessLookupError:
                pass

    def run(self, job):
        # run_experiment forwards signals to its pipeline and waits for export.
        if self.stopped is not None:
            return 128 + self.stopped
        self.child = subprocess.Popen(job['command'], cwd=ROOT, start_new_session=True,
                                      env=dict(os.environ, PYTHONUNBUFFERED='1',
                                               HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1'))
        if self.stopped is not None:
            self.stop(self.stopped, None)
        log = None
        try:
            while True:
                finished = self.child.poll() is not None
                if self.stopped is not None and not finished:
                    # Cover a signal arriving just before the launcher's child
                    # is assigned; its forwarding handler may not see it yet.
                    self.stop(self.stopped, None)
                if log is None and Path(job['console_log']).is_file():
                    log = Path(job['console_log']).open(errors='replace')
                if log is not None:
                    chunk = log.read()
                    if chunk:
                        print(chunk, end='', flush=True)
                if finished:
                    return 128 + self.stopped if self.stopped is not None else self.child.returncode
                try:
                    self.child.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    pass
        finally:
            if log is not None:
                log.close()
            if self.child.poll() is None:
                self.child.terminate()
                self.child.wait()
            self.child = None


def execute(plan, state_dir):
    state_dir.mkdir(parents=True, exist_ok=False)
    write_json(state_dir / 'plan.json', plan)
    state = dict(state='running', started_at=now(), outcomes=[])
    runner = Runner()
    previous = {s: signal.signal(s, runner.stop) for s in (signal.SIGINT, signal.SIGTERM)}
    try:
        for index, job in enumerate(plan['jobs'], 1):
            if runner.stopped is not None:
                state.update(state='interrupted', signal=runner.stopped)
                return 128 + runner.stopped
            state['active_benchmark'] = job['benchmark']
            write_json(state_dir / 'status.json', state)
            print(f"\n[{index}/{len(plan['jobs'])}] {job['benchmark']}: {', '.join(job['problem_ids'])}", flush=True)
            code = runner.run(job)
            state['outcomes'].append(dict(benchmark=job['benchmark'], returncode=code,
                                          finished_at=now(), final_results=job['final_results']))
            if code:
                state.update(state='interrupted' if runner.stopped is not None else 'failed')
                print(f"Suite stopped: {job['benchmark']} exited with {code}; saved proofs remain in {job['proofs']}", flush=True)
                return code if code > 0 else 128 - code
        state['state'] = 'completed'
        print(f"\nSuite completed: {plan['problem_count']} problems. New proofs are ungraded.", flush=True)
        return 0
    except Exception as error:
        state.update(state='failed', error=f'{type(error).__name__}: {error}')
        raise
    finally:
        state.pop('active_benchmark', None)
        state['finished_at'] = now()
        write_json(state_dir / 'status.json', state)
        for s, handler in previous.items():
            signal.signal(s, handler)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id', required=True)
    sampling = parser.add_mutually_exclusive_group()
    sampling.add_argument('--sample-seed', type=uint32, help='Problem-selection seed (default: 0)')
    sampling.add_argument('--random-sample-seed', action='store_true', help='Draw and record a new problem-selection seed')
    seeds = parser.add_mutually_exclusive_group()
    seeds.add_argument('--generation-seed', type=uint32, help='Explicit raw offset and refinement namespace seed')
    seeds.add_argument('--random-generation-seed', action='store_true', help='Draw and record a new generation seed; default preserves original fixed seeds')
    parser.add_argument('--release', choices=('1.7.0','1.8.0','1.9.0','1.10.0','1.11.0','1.12.0'), default='1.12.0')
    parser.add_argument('--solver-python', type=Path, default=ROOT / '.venv-solver/bin/python')
    parser.add_argument('--dry-run', action='store_true', help='Print selection and commands; no files, servers or model calls')
    args = parser.parse_args(argv)
    sample_seed = (secrets.randbits(32) if args.random_sample_seed else
                   0 if args.sample_seed is None else args.sample_seed)
    generation_seed = secrets.randbits(32) if args.random_generation_seed else args.generation_seed
    # Keep the venv executable path: resolving its symlink can select base Python.
    solver = args.solver_python.expanduser().absolute()
    try:
        plan = make_plan(args.run_id, sample_seed, generation_seed, solver, args.release)
        plan['sample_seed_mode'] = 'random' if args.random_sample_seed else 'fixed'
        plan['generation_seed_mode'] = ('random' if args.random_generation_seed else
                                        'original' if generation_seed is None else 'explicit')
        state_dir = ROOT / '.workshop/runs' / args.run_id
        if state_dir.exists() or state_dir.is_symlink():
            raise ValueError(f'Suite already exists; choose a new --run-id: {state_dir}')
        if args.dry_run:
            print(json.dumps(plan, indent=2))
            return 0
        if not solver.is_file():
            raise ValueError('Solver Python missing; run scripts/setup_environment.py --install first')
        print(f"Run: {args.run_id}\nSelection seed: {sample_seed}\nGeneration seed: " +
              ('original fixed settings' if generation_seed is None else str(generation_seed)), flush=True)
        print(f"Plan: {state_dir / 'plan.json'}\nStatus: {state_dir / 'status.json'}", flush=True)
        return execute(plan, state_dir)
    except (ValueError, OSError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    raise SystemExit(main())
