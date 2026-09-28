#!/usr/bin/env python3
"""IMO Proof Pipeline: a versioned entry point for the unchanged frozen solver."""
import argparse
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
from urllib.parse import urlparse


RELEASE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def verify(release=RELEASE):
    manifest = read(release / 'release.json')
    entries = list(release.rglob('*'))
    if any(p.is_symlink() for p in entries):
        raise ValueError('Release contains a symbolic link')
    actual = {str(p.relative_to(release)) for p in entries if p.is_file()}
    if actual != set(manifest['files']) | {'release.json'}:
        raise ValueError('Release has missing or unlisted files')
    for name, expected in manifest['files'].items():
        path = release / name
        if path.is_symlink() or not path.resolve().is_relative_to(release.resolve()) or sha(path) != expected:
            raise ValueError(f'Release file changed: {name}')
    upstream = read(release / 'engine/freeze.json')
    if sha(release / 'engine/freeze.json') != manifest['upstream']['freeze_sha256']:
        raise ValueError('Upstream release changed')
    for name, expected in upstream['files'].items():
        if manifest['files'].get('engine/' + name) != expected:
            raise ValueError('Composite differs from its frozen engine')
    return manifest, read(release / 'profile.json')


def server_settings(endpoint, expected, proc=Path('/proc')):
    """Check existing local servers without changing them or issuing inference."""
    url = urlparse(endpoint)
    if url.scheme != 'http' or url.hostname not in ('127.0.0.1', 'localhost', '::1'):
        raise ValueError('This release requires verifiable local model servers')
    matches = []
    for entry in proc.iterdir():
        if not entry.name.isdigit():
            continue
        try:
            argv = (entry / 'cmdline').read_bytes().decode().rstrip('\0').split('\0')
        except (OSError, UnicodeError):
            continue
        def value(flag):
            return argv[argv.index(flag) + 1] if flag in argv and argv.index(flag) + 1 < len(argv) else None
        if value('--port') != str(url.port or 80) or value('--served-model-name') != expected['model']:
            continue
        observed = {flag: value(flag) for flag in expected['flags']}
        if observed != expected['flags']:
            raise ValueError(f"Server settings differ from this release: {expected['model']}")
        spec = json.loads(value('--speculative-config') or '{}')
        if spec.get('method') != 'mtp' or spec.get('num_speculative_tokens') != 4:
            raise ValueError('This release requires MTP=4')
        if json.loads(value('--default-chat-template-kwargs') or '{}').get('enable_thinking') is not True:
            raise ValueError('This release requires thinking enabled')
        if '--async-scheduling' not in argv or '--language-model-only' not in argv:
            raise ValueError('Server scheduling/model mode differs from this release')
        model_path = value('serve')
        if not model_path or Path(model_path).name != expected['snapshot']:
            raise ValueError('Server model snapshot differs from this release')
        if expected.get('assistant_snapshot') and Path(spec.get('model', '')).name != expected['assistant_snapshot']:
            raise ValueError('MTP assistant snapshot differs from this release')
        matches.append({'pid': int(entry.name), 'model': expected['model'], 'snapshot': expected['snapshot'],
                        'mtp': 4, 'flags': observed})
    if len(matches) != 1:
        raise ValueError(f"Expected one matching local server: {expected['model']}")
    return matches[0]


def options(profile):
    defaults = profile['run_defaults']
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', action='store_true')
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--problem-dir', type=Path)
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--problem-id', action='append')
    parser.add_argument('--limit', type=int)
    parser.add_argument('--gemma-endpoint', default=defaults['gemma_endpoint'])
    parser.add_argument('--qwen-endpoint', default=defaults['qwen_endpoint'])
    parser.add_argument('--model-timeout-sec', type=int, default=defaults['model_timeout_sec'])
    parser.add_argument('--seed-namespace', default=defaults['seed_namespace'])
    parser.add_argument('--raw-seed-offset', type=int, default=defaults['raw_seed_offset'])
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--skip-failed-problem', action='append')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--dry-run', action='store_true')
    mode.add_argument('--execute-models', action='store_true')
    return parser


def launch(args, manifest, profile, release=RELEASE):
    source = release / 'engine/source'
    output = args.output_dir.resolve()
    # Reject old/active runs without an IMO Proof Pipeline identity. Naming a
    # historical run must never modify it or attach another solver to it.
    if output.is_relative_to(release.parent.resolve()) or release.resolve().is_relative_to(output):
        raise ValueError('Run output must be outside the versioned releases')
    if args.resume:
        if not (output / 'harness_release.json').is_file():
            raise ValueError('This is not a run created by this composite release')
    elif output.exists():
        raise FileExistsError(f'Use a new output directory: {output}')
    parameters = {key: str(value) if isinstance(value, Path) else value for key, value in vars(args).items()
                  if key not in ('resume', 'skip_failed_problem', 'verify', 'version', 'output_dir')}
    parameters['problem_dir'] = str(args.problem_dir.resolve())
    identity = {'schema': 'imo-proof-pipeline-run-v1', 'name': manifest['name'], 'version': manifest['version'],
                'release_sha256': sha(release / 'release.json'), 'upstream': manifest['upstream'],
                'profile_sha256': manifest['files']['profile.json'], 'parameters': parameters}
    if args.resume and read(output / 'harness_release.json') != identity:
        raise ValueError('Resume changes release or run configuration')
    # Load only the frozen queue's stdlib orchestration module. Engine imports
    # remain deferred to the separate problem workers, exactly as originally.
    spec = importlib.util.spec_from_file_location('imo_proof_pipeline_frozen_queue', source / 'scripts/run_v263_v290.py')
    queue = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(queue)
    queue.collect_problems(args.problem_dir, args.problem_id, args.limit)
    command = [sys.executable, '-u', '-B', str(source / 'scripts/run_v263_v290.py'),
               '--problem-dir', parameters['problem_dir'], '--output-dir', str(output),
               '--gemma-endpoint', args.gemma_endpoint, '--qwen-endpoint', args.qwen_endpoint,
               '--model-timeout-sec', str(args.model_timeout_sec), '--seed-namespace', args.seed_namespace,
               '--raw-seed-offset', str(args.raw_seed_offset), '--dry-run' if args.dry_run else '--execute-models']
    # The wrapper prepares manifest/input snapshots before launching the original
    # queue. That queue must use its existing resume path for this prepared run.
    command.append('--resume')
    for pid in args.problem_id or []:
        command += ['--problem-id', pid]
    for pid in args.skip_failed_problem or []:
        command += ['--skip-failed-problem', pid]
    if args.limit is not None:
        command += ['--limit', str(args.limit)]
    if args.skip_failed_problem and not args.resume:
        raise ValueError('--skip-failed-problem requires --resume')
    observed = {} if args.dry_run else {
        role: server_settings(getattr(args, role + '_endpoint'), expected)
        for role, expected in profile['servers'].items()}
    output.mkdir(parents=True, exist_ok=args.resume)
    with (output / '.composite.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if not args.resume:
            queue.freeze_queue(args)
            with (output / 'harness_release.json').open('x') as handle:
                json.dump(identity, handle, indent=2); handle.write('\n')
        log_number = len(list(output.glob('composite_launch_*.json')))
        with (output / f'composite_launch_{log_number:03d}.json').open('x') as handle:
            json.dump({'command': command, 'cwd': str(source), 'python': sys.executable,
                       'python_version': sys.version, 'verified_servers': observed}, handle, indent=2)
            handle.write('\n')
        env = dict(os.environ)
        env.pop('PYTHONHOME', None)
        env.update(PYTHONPATH=str(source), PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1')
        # Same launcher, flags, environment root, prompts and seeds as before.
        child = subprocess.Popen(command, cwd=source, env=env, start_new_session=True)
        def forward(signum, frame):
            try:
                os.killpg(child.pid, signum)
            except ProcessLookupError:
                pass
        previous = {sig: signal.signal(sig, forward) for sig in (signal.SIGINT, signal.SIGTERM)}
        try:
            return child.wait()
        finally:
            for sig, handler in previous.items():
                signal.signal(sig, handler)
            if child.poll() is None:
                forward(signal.SIGTERM, None)
                try:
                    child.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    forward(signal.SIGKILL, None)
                    child.wait()


def main():
    manifest, profile = verify()
    parser = options(profile)
    args = parser.parse_args()
    if args.version or args.verify:
        print(json.dumps({'name': manifest['name'], 'version': manifest['version'],
                          'release_sha256': sha(RELEASE / 'release.json'),
                          'verified_files': len(manifest['files']), 'upstream': manifest['upstream']}, indent=2))
        return 0
    if not args.problem_dir or not args.output_dir or not (args.dry_run or args.execute_models):
        parser.error('Provide --problem-dir, --output-dir, and --dry-run or --execute-models')
    return launch(args, manifest, profile)


if __name__ == '__main__':
    raise SystemExit(main())
