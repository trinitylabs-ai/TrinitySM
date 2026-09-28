#!/usr/bin/env python3
"""Run Workshop Pipeline with recorded experiment identity and environment.

No scoring calls. Artifact identities are external sidecar records, preserving
the exact native solver and grader files.
"""
import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import signal
import subprocess
import sys
import time

from environment_capture import capture, render_markdown, sha, write

ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS = ('imo2026', 'imo-proofbench/basic', 'imo-proofbench/advanced')


def now():
    return datetime.now(timezone.utc).isoformat()


def destination(benchmark, run_id):
    if benchmark not in BENCHMARKS or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,127}', run_id):
        raise ValueError('Use a known benchmark and a simple unique run ID (letters, numbers, underscore, dot, hyphen)')
    base = ROOT / 'benchmarks' / benchmark / 'results'
    path = base / run_id
    if path.is_symlink() or not path.resolve().is_relative_to(base.resolve()):
        raise ValueError('Experiment path must remain inside its benchmark results directory')
    return path


def index_artifacts(experiment, generation_finished=False):
    experiment = Path(experiment)
    identity = json.loads((experiment / 'experiment.json').read_text())
    run_id = identity['run_id']
    excluded = {'artifact_index.jsonl', 'artifact_index.jsonl.tmp', '.experiment.lock'}
    records = []
    for current, directories, files in os.walk(experiment, followlinks=False):
        current = Path(current)
        directories[:] = [d for d in sorted(directories) if d not in ('.venv', '__pycache__', 'scratch', '.git')
                          and not (current / d).is_symlink()
                          and (generation_finished or current / d != experiment / 'generation/run')
                          and current / d != experiment / 'grading/work']
        for name in sorted(files):
            path = current / name
            if path.is_symlink() or name in excluded or name.endswith('.lock'):
                continue
            rel = str(path.relative_to(experiment))
            category = ('score' if rel.startswith('grades/') else
                        'proof' if rel.startswith('proofs/') or name.endswith('_proof.md') else
                        'verification' if any(s in name for s in ('validation', 'audit', 'review', 'verify')) else
                        'timing' if name.endswith('metadata.json') or 'timing' in name or name == 'completion.json' else 'provenance')
            # Read one coherent byte snapshot. Skip files still changing during publication.
            before = path.stat()
            data = path.read_bytes()
            after = path.stat()
            if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                continue
            record = {'run_id': run_id, 'artifact_id': hashlib.sha256((run_id + '\0' + rel).encode()).hexdigest(),
                      'path': rel, 'kind': category, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
            if path.suffix == '.json' and category == 'timing':
                try:
                    metadata = json.loads(data)
                    record['timing'] = {k: metadata[k] for k in ('started_at', 'completed_at', 'latency_seconds',
                                         'elapsed_seconds', 'usage', 'model', 'stage') if k in metadata}
                except (ValueError, TypeError):
                    pass
            records.append(record)
    temp = experiment / 'artifact_index.jsonl.tmp'
    temp.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in records))
    temp.replace(experiment / 'artifact_index.jsonl')
    return len(records)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--benchmark', choices=BENCHMARKS, required=True)
    p.add_argument('--run-id', required=True)
    p.add_argument('--release', choices=('1.7.0', '1.8.0', '1.9.0', '1.10.0', '1.11.0', '1.12.0'), default='1.12.0')
    p.add_argument('--solver-python', default=sys.executable)
    p.add_argument('--grader-python')
    p.add_argument('--container-image')
    p.add_argument('--container-digest')
    p.add_argument('--problem-id', action='append')
    p.add_argument('--limit', type=int)
    p.add_argument('--seed-namespace', default='v263-v290:problem-only')
    p.add_argument('--raw-seed-offset', type=int, default=0)
    p.add_argument('--model-timeout-sec', type=int, default=600)
    p.add_argument('--gemma-port', type=int, default=8030)
    p.add_argument('--qwen-port', type=int, default=8027)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--dry-run', action='store_true')
    mode.add_argument('--execute-models', action='store_true')
    mode.add_argument('--index-only', action='store_true')
    args = p.parse_args()
    output = destination(args.benchmark, args.run_id)
    if args.index_only:
        completion = output / 'generation/completion.json'
        finished = completion.exists() and json.loads(completion.read_text()).get('worker_exited') is True
        print(json.dumps({'run_id': args.run_id, 'indexed': index_artifacts(output, finished)}))
        return
    if not re.fullmatch(r'\d+\.\d+\.\d+', args.release):
        p.error('Specify an explicit semantic release version')
    launcher = ROOT / 'harnesses/proof_workshop/run.py'
    subprocess.run([args.solver_python, '-B', str(launcher), '--release', args.release, '--verify'], check=True)
    output.mkdir(parents=True, exist_ok=False)
    for directory in ('generation', 'proofs', 'grades', 'grading', 'reports', 'environment'):
        (output / directory).mkdir()
    # An exclusive experiment-level lock is independent of the solver queue lock.
    with (output / '.experiment.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        identity = {'schema': 'imo-experiment-v1', 'run_id': args.run_id, 'benchmark': args.benchmark,
                    'created_at': now(), 'harness_release': args.release,
                    'launcher_sha256': sha(__file__), 'state': 'preparing',
                    'generation_output': 'generation/run', 'grading_output': 'grading/work'}
        write(output / 'experiment.json', identity)
        inputs = ROOT / 'benchmarks' / args.benchmark / 'problems'
        argv = [args.solver_python, '-u', '-B', str(launcher), '--release', args.release,
                '--problem-dir', str(inputs), '--output-dir', str(output / 'generation/run'),
                '--seed-namespace', args.seed_namespace, '--raw-seed-offset', str(args.raw_seed_offset),
                '--model-timeout-sec', str(args.model_timeout_sec),
                '--gemma-endpoint', f'http://127.0.0.1:{args.gemma_port}/v1',
                '--qwen-endpoint', f'http://127.0.0.1:{args.qwen_port}/v1',
                '--dry-run' if args.dry_run else '--execute-models']
        for pid in args.problem_id or []:
            argv += ['--problem-id', pid]
        if args.limit is not None:
            argv += ['--limit', str(args.limit)]
        write(output / 'generation/launch.json', {'run_id': args.run_id, 'argv': argv, 'cwd': str(ROOT)})
        (output / 'generation/launch.sh').write_text('#!/usr/bin/env bash\nset -euo pipefail\ncd ' +
                                                     shlex.quote(str(ROOT)) + '\nexec ' + shlex.join(argv) + '\n')
        try:
            env = capture(output / 'environment/start', args.run_id, 'before_generation', args.solver_python,
                          args.grader_python, args.release, args.execute_models, args.gemma_port, args.qwen_port,
                          args.container_image, args.container_digest)
        except Exception as e:
            identity.update(state='snapshot_failed', error=f'{type(e).__name__}: {e}')
            write(output / 'experiment.json', identity)
            raise
        (output / 'ENVIRONMENT.md').write_text(render_markdown(env, 'environment/start/'))
        identity.update(state='running', snapshot_sha256=sha(output / 'environment/start/environment.json'))
        write(output / 'experiment.json', identity)
        start = time.monotonic()
        started_at = now()
        child = None
        def forward(signum, _frame):
            if child is not None and child.poll() is None:
                os.killpg(child.pid, signum)
        previous = {s: signal.signal(s, forward) for s in (signal.SIGINT, signal.SIGTERM)}
        returncode = None
        try:
            with (output / 'generation/console.log').open('w') as log:
                child = subprocess.Popen(argv, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                returncode = child.wait()
        finally:
            for s, handler in previous.items():
                signal.signal(s, handler)
            exited = child is not None and child.poll() is not None
            write(output / 'generation/completion.json', {'run_id': args.run_id, 'started_at': started_at,
                  'completed_at': now(), 'wall_seconds': time.monotonic() - start, 'worker_exited': exited,
                  'returncode': returncode, 'excludes_environment_capture_and_grading': True})
            identity.update(state='completed' if returncode == 0 else 'failed_or_interrupted')
            write(output / 'experiment.json', identity)
            index_artifacts(output, generation_finished=exited)
        raise SystemExit(returncode)


if __name__ == '__main__':
    main()
