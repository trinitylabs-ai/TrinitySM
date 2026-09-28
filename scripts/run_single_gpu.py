#!/usr/bin/env python3
"""Run B 1.12.0 with the recorded 96 GB Gemma/Qwen sleep/wake scheduler."""
import argparse
import fcntl
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
import time
from urllib.request import ProxyHandler, build_opener

import local_servers
from reproduce import BENCHMARKS, generation_seed

ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / 'harnesses/single_gpu'
ENGINE = ROOT / 'harnesses/imo_proof_pipeline/releases/1.12.0/engine/source'
SERVER_HEALTH_GRACE_SECONDS = 180


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(value, indent=2) + '\n')
    temp.replace(path)


def plan(args):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,95}', args.run_id):
        raise ValueError('Use a fresh simple run ID of at most 96 letters, numbers, dots, underscores or hyphens.')
    if args.gpu < 0 or not 1 <= args.broker_port <= 65535 or args.broker_port in local_servers.PORTS.values():
        raise ValueError('Use a nonnegative GPU index and a separate broker port in 1..65535.')
    groups = BENCHMARKS if args.benchmark == 'all' else (args.benchmark,)
    requested = set(args.problem_id or [])
    counts = {group: getattr(args, option, None) for group, option in zip(
        BENCHMARKS, ('imo_count', 'basic_count', 'advanced_count'))}
    sampling = any(value is not None for value in counts.values())
    sample_seed = getattr(args, 'sample_seed', None)
    random_sample = getattr(args, 'random_sample_seed', False)
    if sampling:
        if requested:
            raise ValueError('Choose explicit --problem-id values or per-benchmark counts, not both.')
        if any(value is not None and (type(value) is not int or value < 0) for value in counts.values()):
            raise ValueError('Problem counts must be nonnegative integers.')
        if any(value and group not in groups for group, value in counts.items()):
            raise ValueError('Use --benchmark all when selecting counts from multiple benchmarks.')
        counts = {group: value or 0 for group, value in counts.items()}
        if not sum(counts.values()):
            raise ValueError('Select at least one problem.')
        sample_seed = secrets.randbits(32) if random_sample else (1729 if sample_seed is None else sample_seed)
        rng = random.Random(sample_seed)
    elif sample_seed is not None or random_sample:
        raise ValueError('Sampling seeds require --imo-count, --basic-count or --advanced-count.')
    seed = secrets.randbits(32) if getattr(args, 'random_generation_seed', False) else args.generation_seed
    jobs, found = [], set()
    solver = args.solver_python.expanduser().absolute()
    for benchmark in groups:
        base = ROOT / 'benchmarks' / benchmark
        rows = sorted(read(base / 'catalog.json')['generation_inputs']['files'], key=lambda r: r['problem_id'])
        if sampling:
            count = counts[benchmark]
            if count > len(rows):
                raise ValueError(f'{benchmark}: requested {count} problems, but only {len(rows)} are available.')
            rows = sorted(rng.sample(rows, count), key=lambda r: r['problem_id'])
        for row in rows:
            pid = row['problem_id']
            if requested and pid not in requested:
                continue
            if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,30}', pid) or pid in found:
                raise ValueError('Invalid or duplicate catalog problem ID: ' + pid)
            path = base / row['path']
            if (path.resolve().parent != (base / 'problems').resolve()
                    or hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']):
                raise ValueError('Statement differs from the published catalog: ' + pid)
            found.add(pid)
            run_id = args.run_id + '_' + pid
            output = base / 'results' / run_id
            if output.exists() or output.is_symlink():
                raise ValueError('Run already exists; choose a fresh --run-id: ' + str(output))
            command = [str(solver), '-u', '-B', str(ROOT / 'benchmarks/run_experiment.py'),
                       '--benchmark', benchmark, '--problem-id', pid, '--run-id', run_id,
                       '--release', '1.12.0', '--solver-python', str(solver), '--execute-models']
            if seed is not None:
                command += ['--raw-seed-offset', str(seed),
                            '--seed-namespace', f'workshop-generation:{seed}']
            jobs.append(dict(problem_id=pid, benchmark=benchmark, run_id=run_id,
                             input_sha256=row['sha256'], command=command,
                             output=str(output), final_results=str(output / 'generation/run/final_results.json')))
    if not jobs or requested - found:
        raise ValueError('Unknown or empty problem selection: ' + ', '.join(sorted(requested - found)))
    state_dir = ROOT / '.workshop/single_gpu' / args.run_id
    if state_dir.exists():
        raise ValueError('Scheduler run already exists; choose a fresh --run-id: ' + str(state_dir))
    adapter_hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in sorted(ADAPTER.rglob('*.py'))}
    record = dict(schema='workshop-single-gpu-run-v1', run_id=args.run_id, release='1.12.0',
                release_sha256=hashlib.sha256((ENGINE.parents[1] / 'release.json').read_bytes()).hexdigest(),
                gpu=args.gpu, broker_url=f'http://127.0.0.1:{args.broker_port}',
                directory=str(state_dir), problem_count=len(jobs), candidates_per_problem=4,
                proof_concurrency_by_model={'gemma': 8, 'qwen': 12}, comparison_concurrency=12,
                switch_quiet_seconds=20, queue_time_excluded_from_inference_deadlines=True,
                server_health_grace_seconds=SERVER_HEALTH_GRACE_SECONDS,
                external_grading=False, adapter_sha256=adapter_hashes, jobs=jobs)
    if sampling:
        record['sampling'] = dict(counts=counts, seed=sample_seed, random_seed=random_sample,
                                  algorithm='random.Random.sample from sorted catalogs, in benchmark order')
    if seed is not None:
        record['generation_seed'] = seed
    return record


def environment(record):
    env = dict(os.environ)
    env.pop('PYTHONHOME', None)
    env.pop('GPU0_COMPLETED_RESPONSE_REPLAY', None)
    env.update(GPU0_BULK_URL=record['broker_url'], GPU0_BULK_ENGINE=str(ENGINE),
               PYTHONPATH=str(ADAPTER / 'client_compat'), PYTHONDONTWRITEBYTECODE='1',
               HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1')
    return env


def broker_status(record):
    with build_opener(ProxyHandler({})).open(record['broker_url'] + '/status', timeout=5) as response:
        value = json.load(response)
    if value.get('directory') != record['directory']:
        raise RuntimeError('Broker identity differs from this run')
    return value


def verify_servers(gpu):
    local_servers.require_linux()
    for role in local_servers.PORTS:
        saved = local_servers.read_state(role)
        if not (saved and saved.get('sleep_mode') and saved['gpu'] == gpu
                and local_servers.members(saved) and local_servers.ready(role)):
            raise RuntimeError(f'{role}: first run local_servers.py start --single-gpu {gpu}')
    if sum(not local_servers.sleeping(role) for role in local_servers.PORTS) != 1:
        raise RuntimeError('Exactly one model must be awake before starting the scheduler')


class Runner:
    def __init__(self):
        self.children = []
        self.interrupted = None

    def stop(self, signum, _frame=None):
        self.interrupted = signum
        # Each benchmark launcher forwards signals to all of its pipeline workers.
        for child, _ in self.children:
            if child.poll() is None:
                child.send_signal(signum)

    def cleanup(self):
        for child, _ in self.children:
            if child.poll() is None:
                child.terminate()
        deadline = time.monotonic() + 30
        for child, _ in self.children:
            try:
                child.wait(timeout=max(0.1, deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()

    def run(self, record):
        root = Path(record['directory'])
        root.mkdir(parents=True, exist_ok=False)
        (root / 'logs').mkdir()
        write(root / 'plan.json', record)
        state = dict(state='starting', pid=os.getpid(), jobs=[])
        broker = None
        previous = {sig: signal.signal(sig, self.stop) for sig in (signal.SIGINT, signal.SIGTERM)}
        try:
            command = [sys.executable, '-u', '-B', str(ADAPTER / 'broker.py'),
                       '--directory', str(root), '--port', record['broker_url'].rsplit(':', 1)[1],
                       '--gpu', str(record['gpu']), '--owner-pid', str(os.getpid()),
                       '--gemma-proof-limit', '8', '--qwen-proof-limit', '12']
            with (root / 'broker.log').open('w') as log:
                broker = subprocess.Popen(command, cwd=ROOT, stdin=subprocess.DEVNULL,
                                          stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            deadline = time.monotonic() + 30
            while True:
                if self.interrupted:
                    raise InterruptedError('Interrupted before problem admission')
                if broker.poll() is not None:
                    raise RuntimeError('Broker exited; inspect ' + str(root / 'broker.log'))
                try:
                    status = broker_status(record)
                    if status['state'] == 'ready':
                        break
                except OSError:
                    pass
                if time.monotonic() >= deadline:
                    raise TimeoutError('Broker startup timed out')
                time.sleep(0.2)
            env = environment(record)
            for job in record['jobs']:
                if self.interrupted:
                    raise InterruptedError('Interrupted during problem admission')
                with (root / 'logs' / (job['problem_id'] + '.log')).open('w') as log:
                    child = subprocess.Popen(job['command'], cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                                             stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                self.children.append((child, job))
            write(root / 'all_problems_admitted.json', {'problems': len(self.children)})
            state['state'] = 'running'
            print(f"Admitted {len(self.children)} problems. Scheduler status: {root / 'scheduler_status.json'}", flush=True)
            paused_since = None
            while True:
                if self.interrupted:
                    raise InterruptedError('Interrupted by user')
                if broker.poll() is not None:
                    raise RuntimeError('Broker exited during generation; inspect broker.log')
                status = broker_status(record)
                if status['state'] in ('failed', 'stopped'):
                    raise RuntimeError('Scheduler stopped admitting requests: ' + str(status.get('error') or status.get('health_error')))
                if status['state'] == 'paused':
                    # First-use kernel compilation can briefly delay /health.
                    # The broker holds new admissions and retries its probe;
                    # existing logical calls keep their original deadlines.
                    if paused_since is None:
                        paused_since = time.monotonic()
                        print('Server health probe delayed; waiting for automatic recovery.', flush=True)
                    waited = time.monotonic() - paused_since
                    state.update(state='waiting_for_server', server_wait_seconds=waited,
                                 health_error=status.get('health_error'))
                    if waited >= SERVER_HEALTH_GRACE_SECONDS:
                        raise RuntimeError(f'Server health did not recover within {SERVER_HEALTH_GRACE_SECONDS} seconds: '
                                           + str(status.get('health_error')))
                elif paused_since is not None:
                    print('Server health recovered; generation continues.', flush=True)
                    paused_since = None
                    state['state'] = 'running'
                    state.pop('server_wait_seconds', None)
                    state.pop('health_error', None)
                state['jobs'] = [dict(problem_id=job['problem_id'], pid=child.pid, returncode=child.poll(),
                                      final_results=job['final_results']) for child, job in self.children]
                write(root / 'status.json', state)
                if all(child.poll() is not None for child, _ in self.children):
                    break
                time.sleep(1)
            failed = any(child.returncode for child, _ in self.children)
            state['state'] = 'completed_with_failures' if failed else 'completed'
            return 1 if failed else 0
        except BaseException as error:
            state.update(state='interrupted' if self.interrupted else 'failed', error=str(error))
            raise
        finally:
            self.cleanup()
            if broker and broker.poll() is None:
                broker.terminate()
                try:
                    broker.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    broker.kill()
                    broker.wait()
            write(root / 'status.json', state)
            for sig, handler in previous.items():
                signal.signal(sig, handler)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--benchmark', choices=(*BENCHMARKS, 'all'), default='imo-proofbench/basic')
    parser.add_argument('--problem-id', action='append')
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--gpu', type=int, default=0)
    parser.add_argument('--broker-port', type=int, default=18890)
    parser.add_argument('--solver-python', type=Path, default=ROOT / '.venv-solver/bin/python')
    for option in ('imo', 'basic', 'advanced'):
        parser.add_argument('--' + option + '-count', type=int,
                            help='Sample this many problems; omitted counts select zero when any count is supplied.')
    sample = parser.add_mutually_exclusive_group()
    sample.add_argument('--sample-seed', type=generation_seed, help='Problem sampling only; default 1729 in count mode.')
    sample.add_argument('--random-sample-seed', action='store_true', help='Draw and record one problem-sampling seed.')
    generation = parser.add_mutually_exclusive_group()
    generation.add_argument('--generation-seed', type=generation_seed)
    generation.add_argument('--random-generation-seed', action='store_true',
                            help='Draw and record one generation seed shared by all selected problems.')
    parser.add_argument('--dry-run', action='store_true', help='Print the plan without files, processes, or model calls.')
    args = parser.parse_args(argv)
    try:
        record = plan(args)
        if args.dry_run:
            print(json.dumps(record, indent=2))
            return 0
        if not args.solver_python.expanduser().is_file():
            raise ValueError('Install the solver environment with setup_environment.py --install first.')
        verify_servers(args.gpu)
        with (local_servers.STATE_DIR / 'single_gpu_run.lock').open('a') as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise ValueError('Another single-GPU generation runner is active.')
            if local_servers.port_occupied(args.broker_port):
                raise ValueError('Broker port is occupied; choose a free --broker-port.')
            return Runner().run(record)
    except (InterruptedError, KeyboardInterrupt):
        print('Interrupted; completed artifacts are preserved.', file=sys.stderr)
        return 130
    except (OSError, RuntimeError, ValueError) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
