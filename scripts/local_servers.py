#!/usr/bin/env python3
"""Start, inspect, or stop both local vLLM servers (Linux; no model downloads)."""
import argparse
from contextlib import contextmanager
import fcntl
import json
import math
import os
from pathlib import Path
import secrets
import signal
import socket
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import ProxyHandler, Request, build_opener

import serve_models

ROOT = Path(__file__).resolve().parents[1]
STATE_DIR = ROOT / '.workshop/servers'
PROC = Path('/proc')
TOKEN_KEY = 'WORKSHOP_SERVER_TOKEN'
PORTS = {'gemma': 8030, 'qwen': 8027}


class ServerError(RuntimeError):
    pass


def model_id(model):
    catalog = json.loads((ROOT / 'configs/workshop_models.json').read_text())
    return catalog['models'][model]['repository']


def ready(model):
    """A live TCP port alone is insufficient: require the pinned served model ID."""
    try:
        opener = build_opener(ProxyHandler({}))
        with opener.open(f'http://127.0.0.1:{PORTS[model]}/v1/models', timeout=2) as response:
            payload = json.load(response)
        return any(isinstance(item, dict) and item.get('id') == model_id(model)
                   for item in payload.get('data', []))
    except (OSError, URLError, ValueError, TypeError, AttributeError):
        return False


def control(model, path, *, post=False, timeout=300):
    opener = build_opener(ProxyHandler({}))
    request = Request(f'http://127.0.0.1:{PORTS[model]}' + path, data=b'' if post else None)
    with opener.open(request, timeout=timeout) as response:
        raw = response.read()
    return json.loads(raw) if raw else {}


def sleeping(model):
    value = control(model, '/is_sleeping', timeout=5).get('is_sleeping')
    if type(value) is not bool:
        raise ServerError(f'{model} did not report its sleep state')
    return value


def set_sleep(model, asleep, timeout):
    control(model, '/sleep?level=1&mode=wait' if asleep else '/wake_up', post=True, timeout=timeout)
    if sleeping(model) != asleep:
        raise ServerError(f'{model} failed to {"sleep" if asleep else "wake"}')


def port_occupied(port):
    with socket.socket() as sock:
        # Like the model server, permit reuse after a closed connection's
        # TIME_WAIT period starts; an active listener still prevents binding.
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(('127.0.0.1', port))
        except OSError:
            return True
    return False


def require_linux():
    if not (sys.platform.startswith('linux') and hasattr(os, 'pidfd_open')
            and hasattr(signal, 'pidfd_send_signal') and (PROC / 'sys/kernel/random/boot_id').is_file()):
        raise ServerError('Server management requires Linux with /proc and pidfd support (kernel 5.3+).')
    try:
        fd = os.pidfd_open(os.getpid())
        os.close(fd)
    except OSError as error:
        raise ServerError(f'Linux pidfd support is unavailable: {error}') from error


def boot_id():
    return (PROC / 'sys/kernel/random/boot_id').read_text().strip()


def process_info(pid):
    try:
        # comm may contain spaces and parentheses; fields after its final ')' are fixed.
        fields = (PROC / str(pid) / 'stat').read_text().rsplit(')', 1)[1].split()
        return {'pid': pid, 'state': fields[0], 'group': int(fields[2]),
                'session': int(fields[3]), 'start_time': fields[19]}
    except (FileNotFoundError, ProcessLookupError, PermissionError):
        return None


def process_token(pid):
    try:
        prefix = (TOKEN_KEY + '=').encode()
        return next((item[len(prefix):].decode() for item in
                     (PROC / str(pid) / 'environ').read_bytes().split(b'\0')
                     if item.startswith(prefix)), None)
    except (FileNotFoundError, ProcessLookupError):
        return None


def same_member(current, saved, record):
    return bool(current and current['state'] != 'Z'
                and current['start_time'] == saved['start_time']
                and current['group'] == record['pid']
                and current['session'] == record['pid'])


def members(record, known=()):
    """Find owned session members, also after its original leader has exited."""
    if record['boot_id'] != boot_id():
        return []
    leader = process_info(record['pid'])
    if leader and leader['start_time'] != record['start_time']:
        raise ServerError('Saved PID has been reused; refusing to manage that process.')
    if leader and (leader['group'] != record['pid'] or leader['session'] != record['pid']):
        raise ServerError('Saved process is no longer the recorded session leader.')
    # setproctitle may overwrite /proc/PID/environ. A live, recorded kernel
    # identity anchors the private session even when its environment is unreadable.
    anchors = ([leader] if same_member(leader, record, record) else [])
    anchors += [info for info in known
                if same_member(process_info(info['pid']), info, record)]
    result = []
    for path in PROC.iterdir():
        if not path.name.isdigit():
            continue
        info = process_info(int(path.name))
        if not info or info['group'] != record['pid'] or info['state'] == 'Z':
            continue
        if info['session'] != record['pid'] or (not anchors and process_token(info['pid']) != record['token']):
            current = process_info(info['pid'])
            if not current or current['state'] == 'Z':
                continue
            raise ServerError(f'Process {info["pid"]} ownership cannot be verified; leaving it untouched.')
        result.append(info)
    if anchors and not any(same_member(process_info(info['pid']), info, record) for info in anchors):
        # The group may have disappeared during /proc enumeration. Do not use
        # an expired anchor to authenticate a subsequently recycled session ID.
        result = [info for info in result if same_member(process_info(info['pid']), info, record)]
        trusted = {(info['pid'], info['start_time']) for info in known}
        for info in result:
            if ((info['pid'], info['start_time']) not in trusted
                    and process_token(info['pid']) != record['token']):
                raise ServerError('Ownership anchor exited during inspection; retry status or stop.')
    return result


def signal_member(info, record, signum):
    """Use a pidfd, then recheck identity, so a recycled PID is never signalled."""
    try:
        fd = os.pidfd_open(info['pid'])
    except ProcessLookupError:
        return
    try:
        current = process_info(info['pid'])
        # info was authenticated by members(); only its immutable kernel
        # identity is needed here, including after the session leader exits.
        if same_member(current, info, record):
            try:
                signal.pidfd_send_signal(fd, signum)
            except ProcessLookupError:
                pass
    finally:
        os.close(fd)


def terminate(record, grace=10):
    pending = members(record)
    for info in pending:
        signal_member(info, record, signal.SIGTERM)
    deadline = time.monotonic() + grace
    while pending and time.monotonic() < deadline:
        time.sleep(0.2)
        pending = members(record, known=pending)
    # Re-scan and recheck identity before each escalation, including forked workers.
    deadline = time.monotonic() + 5
    while pending and time.monotonic() < deadline:
        for info in pending:
            signal_member(info, record, signal.SIGKILL)
        time.sleep(0.1)
        pending = members(record, known=pending)
    if pending:
        raise ServerError('Owned processes did not exit; their state file has been preserved.')


def state_path(model):
    return STATE_DIR / (model + '.json')


def read_state(model):
    path = state_path(model)
    if not path.exists():
        return None
    try:
        record = json.loads(path.read_text())
        if (record['model'] != model or record['port'] != PORTS[model]
                or type(record['pid']) is not int or record['pid'] <= 1
                or not all(isinstance(record[key], str) and record[key]
                           for key in ('start_time', 'boot_id', 'token', 'model_dir'))
                or type(record['gpu']) is not int):
            raise ValueError('invalid server identity')
        return record
    except (ValueError, KeyError, TypeError) as error:
        raise ServerError(f'Invalid state file {path}: {error}') from error


def write_state(model, record):
    path = state_path(model)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(record, indent=2) + '\n')
    temp.chmod(0o600)
    temp.replace(path)


@contextmanager
def lock():
    STATE_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (STATE_DIR / 'manager.lock').open('a') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise ServerError('Another local_servers command is running.') from error
        yield


@contextmanager
def defer_interrupt():
    # Do not leave an untracked child if interrupted during Popen/state creation.
    interrupted = []
    previous = {sig: signal.signal(sig, lambda *_: interrupted.append(True))
                for sig in (signal.SIGINT, signal.SIGTERM)}
    try:
        yield
    finally:
        for sig, handler in previous.items():
            signal.signal(sig, handler)
    if interrupted:
        raise KeyboardInterrupt


def plans(args):
    result = {}
    for model in PORTS:
        gpu = getattr(args, model + '_gpu')
        sleep_mode = getattr(args, 'single_gpu', None) is not None
        swap_dir = getattr(args, 'swap_dir', None) or ROOT / '.workshop/servers/swap'
        command, environment, required = serve_models.plan(model, args.model_dir, gpu,
                                                           sleep_mode=sleep_mode, swap_dir=swap_dir)
        extra = ['--sleep-mode', '--swap-dir', str(swap_dir)] if sleep_mode else []
        result[model] = {'command': [sys.executable, '-B', str(ROOT / 'scripts/serve_models.py'),
                                    '--model', model, '--model-dir', str(args.model_dir), '--gpu', str(gpu), *extra],
                         'serving_command': command, 'environment': environment,
                         'required': required, 'gpu': gpu, 'sleep_mode': sleep_mode,
                         'swap_dir': str(swap_dir) if sleep_mode else None}
    return result


def preflight(plan):
    for executable in plan['serving_command'][:2]:
        if not Path(executable).is_file():
            raise ServerError('Run python3.11 scripts/setup_environment.py --install first.')
    for checkpoint in plan['required']:
        if not (checkpoint / 'config.json').is_file() or not any(checkpoint.glob('*.safetensors')):
            raise ServerError(f'Missing checkpoint: {checkpoint}; run setup with --download-models.')


def launch(model, plan, args):
    token = secrets.token_hex(32)
    # vLLM renames processes; preserve /proc/PID/environ for orphan recovery.
    env = dict(os.environ, **{TOKEN_KEY: token, 'SPT_NOENV': '1'})
    with (STATE_DIR / (model + '.log')).open('ab') as output:
        process = subprocess.Popen(plan['command'], cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                                   stdout=output, stderr=subprocess.STDOUT, start_new_session=True)
    # Popen returns after exec, and the inherited token survives serve_models' execve.
    info = process_info(process.pid)
    if not info:
        process.wait()
        raise ServerError(f'{model} exited immediately; see {STATE_DIR / (model + ".log")}')
    record = {'model': model, 'port': PORTS[model], 'pid': process.pid,
              'start_time': info['start_time'], 'boot_id': boot_id(), 'token': token,
              'gpu': plan['gpu'], 'model_dir': str(args.model_dir),
              'sleep_mode': plan['sleep_mode'], 'swap_dir': plan['swap_dir']}
    return process, record


def wait_ready(records, timeout):
    deadline = time.monotonic() + timeout
    while True:
        for model, record in records.items():
            if not members(record):
                raise ServerError(f'{model} exited before becoming ready; see {STATE_DIR / (model + ".log")}')
        if all(ready(model) for model in records):
            return
        if time.monotonic() >= deadline:
            raise ServerError(f'Servers were not ready within {timeout:g} seconds; inspect {STATE_DIR}/*.log')
        time.sleep(1)


def start(args):
    server_plans = plans(args)
    single_gpu = getattr(args, 'single_gpu', None) is not None
    if args.dry_run:
        for model, plan in server_plans.items():
            print(json.dumps({'model': model, 'port': PORTS[model],
                              'log': str(STATE_DIR / (model + '.log')),
                              'expected_model_id': model_id(model), **plan},
                             indent=2, default=str))
        return
    require_linux()
    with lock():
        records, new_models = {}, []
        for model, plan in server_plans.items():
            record = read_state(model)
            active = record and members(record)
            if active:
                if (record['gpu'] != plan['gpu'] or record['model_dir'] != str(args.model_dir)
                        or record.get('sleep_mode', False) != plan['sleep_mode']
                        or (single_gpu and record.get('swap_dir') != plan['swap_dir'])):
                    raise ServerError(f'{model} already runs with different settings; stop it first.')
                records[model] = record
            else:
                if port_occupied(PORTS[model]):
                    raise ServerError(f'Port {PORTS[model]} is occupied by an unmanaged server; leaving it untouched.')
                preflight(plan)
                new_models.append(model)
        if single_gpu and records:
            if new_models:
                raise ServerError('Partial single-GPU setup; stop the managed servers, then restart both.')
            wait_ready(records, args.timeout)
            if sum(not sleeping(model) for model in PORTS) != 1:
                raise ServerError('Expected exactly one awake model; stop and restart the single-GPU setup.')
            print('Single-GPU servers are ready. Run scripts/run_single_gpu.py.', flush=True)
            return
        started = []
        try:
            for model in new_models:
                with defer_interrupt():
                    process, record = launch(model, server_plans[model], args)
                    started.append((model, process, record))
                    records[model] = record
                    write_state(model, record)
                print(f'{model}: started PID {record["pid"]}; log {STATE_DIR / (model + ".log")}', flush=True)
                if single_gpu:
                    wait_ready({model: record}, args.timeout)
                    set_sleep(model, True, args.timeout)
            if single_gpu:
                set_sleep('gemma', False, args.timeout)
                print('Single-GPU servers are ready: Gemma awake, Qwen asleep. Run scripts/run_single_gpu.py.', flush=True)
            else:
                wait_ready(records, args.timeout)
                print('Both servers are ready. You can now run scripts/reproduce.py generate.', flush=True)
            return
        except BaseException:
            for model, process, record in reversed(started):
                try:
                    terminate(record)
                    process.wait(timeout=1)
                    state_path(model).unlink(missing_ok=True)
                except (OSError, ServerError, subprocess.TimeoutExpired) as error:
                    print(f'{model}: cleanup incomplete: {error}', file=sys.stderr)
            raise


def status():
    require_linux()
    for model, port in PORTS.items():
        record = None
        try:
            record = read_state(model)
            active = record and members(record)
            state = ('ready' if ready(model) else 'starting/unhealthy') if active else 'not managed/running'
            if active and record.get('sleep_mode') and state == 'ready':
                state = 'sleeping (weights offloaded)' if sleeping(model) else 'awake'
        except (OSError, ServerError) as error:
            state = 'stale/unverified: ' + str(error)
        pid = str(record['pid']) if record else '-'
        log = record.get("log_path", str(STATE_DIR / (model + ".log"))) if record else str(STATE_DIR / (model + ".log"))
        gpu = record['gpu'] if record else '-'
        print(f'{model}: {state}; PID {pid}; GPU {gpu}; port {port}; log {log}')


def stop():
    require_linux()
    failures = []
    with lock():
        for model in PORTS:
            try:
                record = read_state(model)
                if record:
                    terminate(record)
                    state_path(model).unlink(missing_ok=True)
                print(f'{model}: stopped (unmanaged processes are left untouched)')
            except (OSError, ServerError) as error:
                failures.append(f'{model}: {error}')
    if failures:
        raise ServerError('\n'.join(failures))


def interrupt_start(*_):
    raise KeyboardInterrupt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    start_parser = commands.add_parser('start', help='Launch both servers in the background and wait for readiness.')
    start_parser.add_argument('--model-dir', type=Path, default=ROOT / '.models')
    start_parser.add_argument('--gemma-gpu', type=int, help='Gemma GPU in two-GPU mode (default: 0).')
    start_parser.add_argument('--qwen-gpu', type=int, help='Qwen GPU in two-GPU mode (default: 1).')
    start_parser.add_argument('--single-gpu', type=int, metavar='N', help='Recorded 96 GB mode: alternate Gemma/Qwen on GPU N with sleeping weights offloaded.')
    start_parser.add_argument('--swap-dir', type=Path, help='Disk directory for sleeping model weights; use a local SSD with sufficient free space.')
    start_parser.add_argument('--timeout', type=float, default=900, help='Timeout per startup/sleep phase in seconds (default: 900).')
    start_parser.add_argument('--dry-run', action='store_true', help='Print commands; do not write files or start processes.')
    commands.add_parser('status', help='Show managed process identity, readiness, and log paths.')
    commands.add_parser('stop', help='Stop only this manager\'s servers and their workers.')
    args = parser.parse_args(argv)
    if args.command == 'start':
        if args.single_gpu is not None:
            if args.single_gpu < 0 or args.gemma_gpu is not None or args.qwen_gpu is not None:
                parser.error('--single-gpu requires one nonnegative index and cannot be combined with per-model GPU options.')
            args.gemma_gpu = args.qwen_gpu = args.single_gpu
            args.swap_dir = (args.swap_dir or ROOT / '.workshop/servers/swap').expanduser().resolve()
        else:
            args.gemma_gpu = args.gemma_gpu if args.gemma_gpu is not None else 0
            args.qwen_gpu = args.qwen_gpu if args.qwen_gpu is not None else 1
            if args.swap_dir:
                parser.error('--swap-dir requires --single-gpu')
            if args.gemma_gpu < 0 or args.qwen_gpu < 0 or args.gemma_gpu == args.qwen_gpu:
                parser.error('GPU indices must be distinct and nonnegative; use --single-gpu N to switch models on one GPU.')
        if not math.isfinite(args.timeout) or args.timeout <= 0:
            parser.error('--timeout must be a positive finite number.')
        args.model_dir = args.model_dir.expanduser().resolve()
    try:
        if args.command == 'start':
            previous = signal.signal(signal.SIGTERM, interrupt_start)
            try:
                start(args)
            finally:
                signal.signal(signal.SIGTERM, previous)
        elif args.command == 'status':
            status()
        else:
            stop()
    except KeyboardInterrupt:
        print('Interrupted; see any cleanup errors above.', file=sys.stderr)
        return 130
    except (OSError, ServerError) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
