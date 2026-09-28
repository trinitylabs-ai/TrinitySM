"""Model-free coverage of background server lifecycle and process ownership."""
import argparse
import importlib.util
import io
import json
import os
from pathlib import Path
import signal
import select
import socket
import subprocess
import sys
from unittest.mock import Mock

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location('local_servers', ROOT / 'scripts/local_servers.py')
servers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(servers)


def args(tmp_path, **updates):
    values = dict(model_dir=tmp_path / 'models', gemma_gpu=0, qwen_gpu=1, timeout=1, dry_run=False)
    values.update(updates)
    return argparse.Namespace(**values)


def record(model='gemma', pid=2345, **updates):
    values = dict(model=model, port=servers.PORTS[model], pid=pid, start_time='1234',
                  boot_id='boot-a', token='owned-token', gpu=0 if model == 'gemma' else 1,
                  model_dir='/models')
    values.update(updates)
    return values


@pytest.fixture
def isolated(tmp_path, monkeypatch):
    state = tmp_path / 'state'
    monkeypatch.setattr(servers, 'STATE_DIR', state)
    monkeypatch.setattr(servers, 'require_linux', lambda: None)
    monkeypatch.setattr(servers, 'preflight', Mock())
    monkeypatch.setattr(servers, 'port_occupied', lambda port: False)
    monkeypatch.setattr(servers, 'members', lambda saved, known=(): [{'pid': saved['pid']}])
    monkeypatch.setattr(servers, 'ready', lambda model: True)
    return state


@pytest.mark.parametrize('payload,expected', [
    ({'data': [{'id': 'google/gemma-4-31B-it'}]}, True),
    ({'data': [{'id': 'another-model'}]}, False),
    ({'data': []}, False), ({'data': None}, False), ([], False),
])
def test_readiness_requires_expected_served_model_id(monkeypatch, payload, expected):
    opener = Mock()
    opener.open.return_value = io.StringIO(json.dumps(payload))
    monkeypatch.setattr(servers, 'build_opener', lambda *args: opener)
    assert servers.ready('gemma') is expected
    opener.open.assert_called_once_with('http://127.0.0.1:8030/v1/models', timeout=2)


def test_readiness_handles_http_failure(monkeypatch):
    opener = Mock()
    opener.open.side_effect = OSError('connection refused')
    monkeypatch.setattr(servers, 'build_opener', lambda *args: opener)
    assert not servers.ready('qwen')


def test_dry_run_is_portable_and_has_no_files_or_processes(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(servers, 'STATE_DIR', tmp_path / 'state')
    def forbidden(*args, **kwargs):
        pytest.fail('Dry-run must not inspect Linux state, launch processes, or preflight models')
    for name in ('require_linux', 'preflight', 'launch'):
        monkeypatch.setattr(servers, name, forbidden)
    assert servers.main(['start', '--dry-run', '--model-dir', str(tmp_path / 'models'),
                         '--gemma-gpu', '2', '--qwen-gpu', '3']) == 0
    assert list(tmp_path.iterdir()) == []
    output = capsys.readouterr().out
    assert '8030' in output and '8027' in output
    assert 'CUDA_VISIBLE_DEVICES' in output and 'serve_models.py' in output
    assert 'google/gemma-4-31B-it' in output and 'Qwen/Qwen3.6-27B' in output


@pytest.mark.parametrize('flags', [
    ['--gemma-gpu', '-1'], ['--qwen-gpu', '-1'], ['--gemma-gpu', '1'],
    ['--timeout', '0'], ['--timeout', '-2'], ['--timeout', 'nan'], ['--timeout', 'inf'],
])
def test_invalid_options_are_rejected_before_writes(tmp_path, monkeypatch, flags):
    monkeypatch.setattr(servers, 'STATE_DIR', tmp_path / 'state')
    with pytest.raises(SystemExit) as result:
        servers.main(['start', *flags])
    assert result.value.code == 2 and list(tmp_path.iterdir()) == []


def test_start_launches_both_then_writes_state_and_waits(isolated, tmp_path, monkeypatch):
    arguments = args(tmp_path)
    calls = []
    def launch(model, plan, supplied):
        calls.append(model)
        return Mock(), record(model, pid=2345 + len(calls), model_dir=str(arguments.model_dir))
    monkeypatch.setattr(servers, 'launch', launch)
    checks = []
    def ready(model):
        assert calls == ['gemma', 'qwen']
        checks.append(model)
        return True
    monkeypatch.setattr(servers, 'ready', ready)
    servers.start(arguments)
    assert checks == ['gemma', 'qwen']
    assert servers.preflight.call_count == 2
    assert servers.read_state('gemma')['pid'] == 2346
    assert servers.read_state('qwen')['pid'] == 2347
    assert (isolated / 'gemma.json').stat().st_mode & 0o777 == 0o600


def test_repeat_start_reuses_matching_managed_servers(isolated, tmp_path, monkeypatch):
    isolated.mkdir()
    for model in servers.PORTS:
        servers.write_state(model, record(model, model_dir=str(tmp_path / 'models')))
    launch = Mock(side_effect=AssertionError('Must reuse running servers'))
    monkeypatch.setattr(servers, 'launch', launch)
    servers.start(args(tmp_path))
    launch.assert_not_called()
    servers.preflight.assert_not_called()


def test_reuse_rejects_changed_settings(isolated, tmp_path):
    isolated.mkdir()
    servers.write_state('gemma', record(model_dir='/somewhere-else'))
    with pytest.raises(servers.ServerError, match='different settings'):
        servers.start(args(tmp_path))


@pytest.mark.parametrize('reason', ['timeout', 'interrupt', 'launch_failure', 'early_exit'])
def test_start_failure_cleans_only_new_servers(isolated, tmp_path, monkeypatch, reason):
    isolated.mkdir()
    existing = record(model_dir=str(tmp_path / 'models'))
    servers.write_state('gemma', existing)
    created = record('qwen', pid=2346, model_dir=str(tmp_path / 'models'))
    process = Mock()
    monkeypatch.setattr(servers, 'launch', lambda *unused: (process, created))
    stopped = []
    monkeypatch.setattr(servers, 'terminate', lambda saved: stopped.append(saved['model']))
    monkeypatch.setattr(servers.time, 'sleep', lambda _: None)
    monkeypatch.setattr(servers.time, 'monotonic', Mock(side_effect=[0, 5]))
    if reason == 'interrupt':
        monkeypatch.setattr(servers, 'ready', Mock(side_effect=KeyboardInterrupt))
    elif reason == 'launch_failure':
        original = servers.write_state
        def failing_write(model, saved):
            if model == 'qwen':
                raise OSError('disk full')
            original(model, saved)
        monkeypatch.setattr(servers, 'write_state', failing_write)
    elif reason == 'early_exit':
        monkeypatch.setattr(servers, 'members', lambda saved, known=(): [] if saved['model'] == 'qwen' else [{}])
    else:
        monkeypatch.setattr(servers, 'ready', lambda _: False)
    with pytest.raises((servers.ServerError, KeyboardInterrupt, OSError)):
        servers.start(args(tmp_path))
    assert stopped == ['qwen']
    assert servers.read_state('gemma') == existing
    assert not servers.state_path('qwen').exists()
    process.wait.assert_called_once_with(timeout=1)


def test_both_preflight_before_any_launch(isolated, tmp_path, monkeypatch):
    monkeypatch.setattr(servers, 'preflight', Mock(side_effect=[None, servers.ServerError('missing weights')]))
    launch = Mock()
    monkeypatch.setattr(servers, 'launch', launch)
    with pytest.raises(servers.ServerError, match='missing weights'):
        servers.start(args(tmp_path))
    launch.assert_not_called()


def test_unmanaged_occupied_port_is_not_adopted_or_stopped(isolated, tmp_path, monkeypatch):
    monkeypatch.setattr(servers, 'port_occupied', lambda _: True)
    launch, terminate = Mock(), Mock()
    monkeypatch.setattr(servers, 'launch', launch)
    monkeypatch.setattr(servers, 'terminate', terminate)
    with pytest.raises(servers.ServerError, match='unmanaged server'):
        servers.start(args(tmp_path))
    launch.assert_not_called()
    terminate.assert_not_called()


def fake_proc(tmp_path, monkeypatch):
    proc = tmp_path / 'proc'
    (proc / 'sys/kernel/random').mkdir(parents=True)
    (proc / 'sys/kernel/random/boot_id').write_text('boot-a\n')
    monkeypatch.setattr(servers, 'PROC', proc)
    return proc


def put_process(proc, pid=2345, start='1234', group=2345, session=2345, token='owned-token', state='S'):
    path = proc / str(pid)
    path.mkdir(exist_ok=True)
    fields = [state, '1', str(group), str(session)] + ['0'] * 15 + [start]
    (path / 'stat').write_text(f'{pid} (python with (parentheses)) ' + ' '.join(fields))
    (path / 'environ').write_bytes(f'{servers.TOKEN_KEY}={token}\0OTHER=value\0'.encode())


def test_proc_identity_handles_spaces_and_includes_owned_workers(tmp_path, monkeypatch):
    proc = fake_proc(tmp_path, monkeypatch)
    put_process(proc)
    put_process(proc, pid=2346, start='1235')
    put_process(proc, pid=9999, start='777', group=9999, session=9999, token='foreign')
    assert sorted(item['pid'] for item in servers.members(record())) == [2345, 2346]
    assert servers.process_info(2345)['start_time'] == '1234'


@pytest.mark.parametrize('change', ['pid_reused', 'session_wrong', 'group_wrong'])
def test_stale_or_foreign_identity_refuses_termination(tmp_path, monkeypatch, change):
    proc = fake_proc(tmp_path, monkeypatch)
    options = {'pid_reused': {'start': '999'}, 'session_wrong': {'session': 9999},
               'group_wrong': {'group': 9999}}[change]
    put_process(proc, **options)
    kill = Mock()
    monkeypatch.setattr(servers, 'signal_member', kill)
    with pytest.raises(servers.ServerError):
        servers.terminate(record())
    kill.assert_not_called()


def test_previous_boot_record_cannot_own_processes(tmp_path, monkeypatch):
    proc = fake_proc(tmp_path, monkeypatch)
    put_process(proc)
    assert servers.members(record(boot_id='old-boot')) == []
    assert servers.members(record(boot_id='old-boot'), known=[servers.process_info(2345)]) == []


def test_owned_orphan_workers_remain_collectable(tmp_path, monkeypatch):
    proc = fake_proc(tmp_path, monkeypatch)
    put_process(proc, pid=2346, start='1235')
    assert [item['pid'] for item in servers.members(record())] == [2346]


def test_pidfd_rechecks_identity_after_open(tmp_path, monkeypatch):
    proc = fake_proc(tmp_path, monkeypatch)
    put_process(proc)
    info = servers.process_info(2345)
    def open_fd(pid):
        put_process(proc, start='999', token='foreign')
        return 42
    monkeypatch.setattr(os, 'pidfd_open', open_fd, raising=False)
    close, send = Mock(), Mock()
    monkeypatch.setattr(os, 'close', close)
    monkeypatch.setattr(signal, 'pidfd_send_signal', send, raising=False)
    servers.signal_member(info, record(), signal.SIGTERM)
    send.assert_not_called()
    close.assert_called_once_with(42)


def test_pidfd_signals_only_verified_identity(tmp_path, monkeypatch):
    proc = fake_proc(tmp_path, monkeypatch)
    put_process(proc)
    monkeypatch.setattr(os, 'pidfd_open', lambda pid: 42, raising=False)
    monkeypatch.setattr(os, 'close', Mock())
    send = Mock()
    monkeypatch.setattr(signal, 'pidfd_send_signal', send, raising=False)
    servers.signal_member(servers.process_info(2345), record(), signal.SIGTERM)
    send.assert_called_once_with(42, signal.SIGTERM)


def test_stop_escalates_when_term_does_not_exit(monkeypatch):
    info = {'pid': 2345}
    monkeypatch.setattr(servers, 'members', Mock(side_effect=[[info], []]))
    monkeypatch.setattr(servers.time, 'monotonic', Mock(side_effect=[0, 1, 1, 1]))
    monkeypatch.setattr(servers.time, 'sleep', lambda _: None)
    send = Mock()
    monkeypatch.setattr(servers, 'signal_member', send)
    saved = record()
    servers.terminate(saved, grace=0)
    assert [call.args[2] for call in send.call_args_list] == [signal.SIGTERM, signal.SIGKILL]


def test_stop_is_repeatable_and_preserves_unmanaged_processes(isolated, monkeypatch):
    isolated.mkdir()
    for model in servers.PORTS:
        servers.write_state(model, record(model))
    stopped = []
    monkeypatch.setattr(servers, 'terminate', lambda saved: stopped.append(saved['model']))
    servers.stop()
    servers.stop()
    assert stopped == ['gemma', 'qwen']
    assert not list(isolated.glob('*.json'))


def test_launch_detaches_and_appends_both_output_streams(isolated, tmp_path, monkeypatch):
    isolated.mkdir()
    (isolated / 'gemma.log').write_text('previous run\n')
    process = Mock(pid=2345)
    captured = {}
    def popen(command, **kwargs):
        captured.update(kwargs, command=command)
        kwargs['stdout'].write(b'new run\n')
        return process
    monkeypatch.setattr(subprocess, 'Popen', popen)
    monkeypatch.setattr(servers, 'process_info', lambda pid: {'start_time': '1234'})
    monkeypatch.setattr(servers, 'boot_id', lambda: 'boot-a')
    plan = servers.plans(args(tmp_path))['gemma']
    actual, saved = servers.launch('gemma', plan, args(tmp_path))
    assert actual is process and saved['pid'] == 2345
    assert captured['start_new_session'] is True
    assert captured['stdin'] == subprocess.DEVNULL and captured['stderr'] == subprocess.STDOUT
    assert 'serve_models.py' in ' '.join(captured['command'])
    assert captured['env'][servers.TOKEN_KEY] == saved['token']
    assert captured['env']['SPT_NOENV'] == '1'
    assert (isolated / 'gemma.log').read_text() == 'previous run\nnew run\n'


def test_status_reports_readiness_pid_and_logs(isolated, monkeypatch, capsys):
    isolated.mkdir()
    servers.write_state('gemma', record())
    servers.status()
    output = capsys.readouterr().out
    assert 'gemma: ready; PID 2345' in output
    assert 'qwen: not managed/running; PID -' in output
    assert str(isolated / 'gemma.log') in output


def test_stop_continues_after_one_corrupt_state(isolated, monkeypatch):
    isolated.mkdir()
    servers.state_path('gemma').write_text('not json')
    servers.write_state('qwen', record('qwen'))
    stopped = []
    monkeypatch.setattr(servers, 'terminate', lambda saved: stopped.append(saved['model']))
    with pytest.raises(servers.ServerError, match='gemma'):
        servers.stop()
    assert stopped == ['qwen']
    assert servers.state_path('gemma').read_text() == 'not json'
    assert not servers.state_path('qwen').exists()


def test_status_continues_after_one_corrupt_state(isolated, capsys):
    isolated.mkdir()
    servers.state_path('gemma').write_text('not json')
    servers.write_state('qwen', record('qwen'))
    servers.status()
    output = capsys.readouterr().out
    assert 'gemma: stale/unverified:' in output and 'qwen: ready;' in output


def test_second_launch_failure_cleans_first_launch(isolated, tmp_path, monkeypatch):
    first = record(model_dir=str(tmp_path / 'models'))
    process = Mock()
    monkeypatch.setattr(servers, 'launch', Mock(side_effect=[(process, first), OSError('spawn failed')]))
    stopped = []
    monkeypatch.setattr(servers, 'terminate', lambda saved: stopped.append(saved['model']))
    with pytest.raises(OSError, match='spawn failed'):
        servers.start(args(tmp_path))
    assert stopped == ['gemma'] and not servers.state_path('gemma').exists()


@pytest.mark.parametrize('signum', [signal.SIGINT, signal.SIGTERM])
def test_interrupt_during_launch_is_deferred_until_child_is_tracked(isolated, tmp_path, monkeypatch, signum):
    process = Mock()
    first = record(model_dir=str(tmp_path / 'models'))
    def launch(*unused):
        os.kill(os.getpid(), signum)
        return process, first
    monkeypatch.setattr(servers, 'launch', launch)
    stopped = []
    monkeypatch.setattr(servers, 'terminate', lambda saved: stopped.append(saved['model']))
    with pytest.raises(KeyboardInterrupt):
        servers.start(args(tmp_path))
    assert stopped == ['gemma'] and not servers.state_path('gemma').exists()


def test_preflight_rejects_missing_venv_and_weights(tmp_path):
    python = tmp_path / 'python'
    vllm = tmp_path / 'vllm'
    checkpoint = tmp_path / 'model'
    plan = {'serving_command': [str(python), str(vllm)], 'required': [checkpoint]}
    with pytest.raises(servers.ServerError, match='--install'):
        servers.preflight(plan)
    python.touch()
    vllm.touch()
    with pytest.raises(servers.ServerError, match='--download-models'):
        servers.preflight(plan)
    checkpoint.mkdir()
    (checkpoint / 'config.json').write_text('{}')
    (checkpoint / 'model.safetensors').touch()
    servers.preflight(plan)


@pytest.mark.skipif(not (sys.platform.startswith('linux') and hasattr(os, 'pidfd_open')
                        and hasattr(signal, 'pidfd_send_signal')),
                    reason='Real /proc/pidfd lifecycle requires Linux and Python pidfd support')
def test_real_linux_owned_child_stop():
    servers.require_linux()
    child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'],
                             env=dict(os.environ, **{servers.TOKEN_KEY: 'synthetic-owned-test'}),
                             start_new_session=True, stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        info = servers.process_info(child.pid)
        saved = record(pid=child.pid, start_time=info['start_time'], boot_id=servers.boot_id(),
                       token='synthetic-owned-test')
        assert servers.members(saved)
        servers.terminate(saved, grace=0.3)
        assert child.wait(timeout=2) == -signal.SIGTERM
        assert servers.members(saved) == []
    finally:
        if child.poll() is None:
            child.kill()
            child.wait(timeout=2)


def test_sigterm_during_readiness_cleans_new_children(isolated, tmp_path, monkeypatch):
    process = Mock()
    def launch(model, *unused):
        return process, record(model, pid=2345 if model == 'gemma' else 2346,
                               model_dir=str(tmp_path / 'models'))
    monkeypatch.setattr(servers, 'launch', launch)
    stopped = []
    monkeypatch.setattr(servers, 'terminate', lambda saved: stopped.append(saved['model']))
    def ready(model):
        os.kill(os.getpid(), signal.SIGTERM)
    monkeypatch.setattr(servers, 'ready', ready)
    previous = signal.getsignal(signal.SIGTERM)
    assert servers.main(['start', '--model-dir', str(tmp_path / 'models')]) == 130
    assert stopped == ['qwen', 'gemma']
    assert not list(isolated.glob('*.json'))
    assert signal.getsignal(signal.SIGTERM) == previous


def clobber_environment(proc, pid):
    # setproctitle can overwrite the kernel-visible initial environ area.
    (proc / str(pid) / 'environ').write_bytes(b'vLLM::EngineCore\0' + b'\0' * 128)


def remove_process(proc, pid):
    directory = proc / str(pid)
    for path in directory.iterdir():
        path.unlink()
    directory.rmdir()


def test_live_leader_authenticates_session_after_environment_is_clobbered(tmp_path, monkeypatch):
    proc = fake_proc(tmp_path, monkeypatch)
    put_process(proc)
    put_process(proc, pid=2346, start='1235')
    clobber_environment(proc, 2345)
    clobber_environment(proc, 2346)
    assert servers.process_token(2345) is None
    assert servers.process_token(2346) is None
    assert sorted(item['pid'] for item in servers.members(record())) == [2345, 2346]


def test_unanchored_orphan_without_token_remains_unmanageable(tmp_path, monkeypatch):
    proc = fake_proc(tmp_path, monkeypatch)
    put_process(proc, pid=2346, start='1235')
    clobber_environment(proc, 2346)
    send = Mock()
    monkeypatch.setattr(servers, 'signal_member', send)
    with pytest.raises(servers.ServerError, match='ownership'):
        servers.terminate(record())
    send.assert_not_called()


def test_verified_surviving_worker_anchors_rescan_after_leader_exit(tmp_path, monkeypatch):
    proc = fake_proc(tmp_path, monkeypatch)
    put_process(proc)
    put_process(proc, pid=2346, start='1235')
    clobber_environment(proc, 2346)
    known = servers.members(record())
    remove_process(proc, 2345)
    assert [item['pid'] for item in servers.members(record(), known=known)] == [2346]


def test_reused_known_worker_cannot_anchor_an_orphan_session(tmp_path, monkeypatch):
    proc = fake_proc(tmp_path, monkeypatch)
    put_process(proc, pid=2346, start='1235')
    known = [servers.process_info(2346)]
    put_process(proc, pid=2346, start='9999')
    clobber_environment(proc, 2346)
    with pytest.raises(servers.ServerError, match='ownership'):
        servers.members(record(), known=known)


@pytest.mark.parametrize('field', ['group', 'session'])
def test_changed_known_worker_session_cannot_authenticate_an_orphan(tmp_path, monkeypatch, field):
    proc = fake_proc(tmp_path, monkeypatch)
    put_process(proc, pid=2346, start='1235')
    known = [servers.process_info(2346)]
    put_process(proc, pid=2346, start='1235', **{field: 9999})
    # This unverified member must not be trusted via the now-moved known worker.
    put_process(proc, pid=2347, start='1236')
    clobber_environment(proc, 2346)
    clobber_environment(proc, 2347)
    with pytest.raises(servers.ServerError, match='ownership'):
        servers.members(record(), known=known)


def test_token_clobber_after_authentication_does_not_block_pidfd_signal(tmp_path, monkeypatch):
    proc = fake_proc(tmp_path, monkeypatch)
    put_process(proc)
    info = servers.members(record())[0]
    clobber_environment(proc, 2345)
    monkeypatch.setattr(os, 'pidfd_open', lambda pid: 42, raising=False)
    monkeypatch.setattr(os, 'close', Mock())
    send = Mock()
    monkeypatch.setattr(signal, 'pidfd_send_signal', send, raising=False)
    servers.signal_member(info, record(), signal.SIGTERM)
    send.assert_called_once_with(42, signal.SIGTERM)


def test_stop_rechecks_known_worker_when_leader_exits_first(tmp_path, monkeypatch):
    proc = fake_proc(tmp_path, monkeypatch)
    put_process(proc)
    put_process(proc, pid=2346, start='1235')
    clobber_environment(proc, 2345)
    clobber_environment(proc, 2346)
    sent = []
    def send(info, saved, signum):
        sent.append((info['pid'], signum))
        if info['pid'] == 2345 or signum == signal.SIGKILL:
            remove_process(proc, info['pid'])
    monkeypatch.setattr(servers, 'signal_member', send)
    monkeypatch.setattr(servers.time, 'sleep', lambda _: None)
    monkeypatch.setattr(servers.time, 'monotonic', Mock(side_effect=[0, 0, 1, 1, 1]))
    servers.terminate(record(), grace=0.5)
    assert (2345, signal.SIGTERM) in sent
    assert [sig for pid, sig in sent if pid == 2346] == [signal.SIGTERM, signal.SIGKILL]
    assert servers.members(record()) == []


def test_start_preserves_unverified_existing_state_instead_of_launching_again(isolated, tmp_path, monkeypatch):
    isolated.mkdir()
    original = record(model_dir=str(tmp_path / 'models'))
    servers.write_state('gemma', original)
    monkeypatch.setattr(servers, 'members', Mock(side_effect=servers.ServerError('ownership uncertain')))
    # A still-loading server may not yet have opened its port.
    monkeypatch.setattr(servers, 'port_occupied', lambda _: False)
    launch, terminate = Mock(), Mock()
    monkeypatch.setattr(servers, 'launch', launch)
    monkeypatch.setattr(servers, 'terminate', terminate)
    with pytest.raises(servers.ServerError, match='ownership'):
        servers.start(args(tmp_path))
    launch.assert_not_called()
    terminate.assert_not_called()
    assert servers.read_state('gemma') == original


@pytest.mark.skipif(not sys.platform.startswith('linux'), reason='Real setproctitle regression requires Linux')
def test_real_linux_setproctitle_child_remains_owned():
    pytest.importorskip('setproctitle')
    servers.require_linux()
    environment = dict(os.environ, **{servers.TOKEN_KEY: 'synthetic-title-test'})
    environment.pop('SPT_NOENV', None)  # Reproduce existing processes before the prevention fix.
    code = ('import setproctitle,time; setproctitle.setproctitle("vLLM::SyntheticWorker"); '
            'print("renamed", flush=True); time.sleep(60)')
    child = subprocess.Popen([sys.executable, '-c', code], env=environment, start_new_session=True,
                             stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                             text=True)
    try:
        assert select.select([child.stdout], [], [], 5)[0], 'Synthetic child did not become ready'
        assert child.stdout.readline().strip() == 'renamed'
        info = servers.process_info(child.pid)
        saved = record(pid=child.pid, start_time=info['start_time'], boot_id=servers.boot_id(),
                       token='synthetic-title-test')
        assert servers.process_token(child.pid) is None
        assert [item['pid'] for item in servers.members(saved)] == [child.pid]
        servers.terminate(saved, grace=0.3)
        assert child.wait(timeout=2) == -signal.SIGTERM
    finally:
        child.stdout.close()
        if child.poll() is None:
            child.kill()
            child.wait(timeout=2)


def test_anchor_exit_during_scan_does_not_authenticate_unverified_members(tmp_path, monkeypatch):
    proc = fake_proc(tmp_path, monkeypatch)
    put_process(proc)
    put_process(proc, pid=2346, start='1235')
    clobber_environment(proc, 2346)
    original = servers.process_info
    leader_reads = []
    def inspect(pid):
        if pid == 2345:
            leader_reads.append(pid)
            # Initial anchor, enumeration, then the final anchor recheck.
            if len(leader_reads) == 3:
                remove_process(proc, 2345)
        return original(pid)
    monkeypatch.setattr(servers, 'process_info', inspect)
    with pytest.raises(servers.ServerError, match='anchor exited'):
        servers.members(record())


def test_single_gpu_initializes_and_sleeps_models_sequentially(isolated, tmp_path, monkeypatch):
    arguments = args(tmp_path, single_gpu=2, gemma_gpu=2, qwen_gpu=2, swap_dir=tmp_path / 'swap')
    events = []
    def launch(model, plan, supplied):
        events.append(('launch', model))
        assert plan['gpu'] == 2 and plan['sleep_mode']
        return Mock(), record(model, gpu=2, model_dir=str(arguments.model_dir),
                              sleep_mode=True, swap_dir=str(arguments.swap_dir))
    monkeypatch.setattr(servers, 'launch', launch)
    monkeypatch.setattr(servers, 'wait_ready', lambda records, timeout: events.append(('ready', tuple(records))))
    monkeypatch.setattr(servers, 'set_sleep', lambda model, asleep, timeout: events.append(('sleep', model, asleep)))
    servers.start(arguments)
    assert events == [('launch', 'gemma'), ('ready', ('gemma',)), ('sleep', 'gemma', True),
                      ('launch', 'qwen'), ('ready', ('qwen',)), ('sleep', 'qwen', True),
                      ('sleep', 'gemma', False)]


@pytest.mark.parametrize('failure_at,expected', [(1, ['gemma']), (2, ['qwen', 'gemma']), (3, ['qwen', 'gemma'])])
def test_single_gpu_sleep_failure_cleans_only_new_servers(isolated, tmp_path, monkeypatch, failure_at, expected):
    arguments = args(tmp_path, single_gpu=0, qwen_gpu=0, swap_dir=tmp_path / 'swap')
    monkeypatch.setattr(servers, 'launch', lambda model, *_: (Mock(), record(model)))
    monkeypatch.setattr(servers, 'wait_ready', lambda *a: None)
    sleeper = Mock(side_effect=[None] * (failure_at - 1) + [servers.ServerError('sleep failed')])
    monkeypatch.setattr(servers, 'set_sleep', sleeper)
    stopped = []
    monkeypatch.setattr(servers, 'terminate', lambda saved: stopped.append(saved['model']))
    with pytest.raises(servers.ServerError, match='sleep failed'):
        servers.start(arguments)
    assert stopped == expected
    assert not list(isolated.glob('*.json'))


def test_single_gpu_reuses_qwen_awake_without_switching(isolated, tmp_path, monkeypatch):
    arguments = args(tmp_path, single_gpu=0, qwen_gpu=0, swap_dir=tmp_path / 'swap')
    isolated.mkdir()
    for model in servers.PORTS:
        servers.write_state(model, record(model, gpu=0, model_dir=str(arguments.model_dir),
                                         sleep_mode=True, swap_dir=str(arguments.swap_dir)))
    launch, sleeper = Mock(), Mock()
    monkeypatch.setattr(servers, 'launch', launch)
    monkeypatch.setattr(servers, 'set_sleep', sleeper)
    monkeypatch.setattr(servers, 'sleeping', lambda model: model == 'gemma')
    servers.start(arguments)
    launch.assert_not_called()
    sleeper.assert_not_called()


def test_single_gpu_rejects_partial_setup_without_mutating(isolated, tmp_path, monkeypatch):
    arguments = args(tmp_path, single_gpu=0, qwen_gpu=0, swap_dir=tmp_path / 'swap')
    isolated.mkdir()
    saved = record(gpu=0, model_dir=str(arguments.model_dir), sleep_mode=True, swap_dir=str(arguments.swap_dir))
    servers.write_state('gemma', saved)
    launch, sleeper = Mock(), Mock()
    monkeypatch.setattr(servers, 'launch', launch)
    monkeypatch.setattr(servers, 'set_sleep', sleeper)
    with pytest.raises(servers.ServerError, match='Partial single-GPU'):
        servers.start(arguments)
    launch.assert_not_called()
    sleeper.assert_not_called()
    assert servers.read_state('gemma') == saved


def test_single_gpu_dry_run_and_mutually_exclusive_options(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(servers, 'STATE_DIR', tmp_path / 'state')
    monkeypatch.setattr(servers, 'launch', Mock(side_effect=AssertionError('dry run started server')))
    assert servers.main(['start', '--single-gpu', '2', '--swap-dir', str(tmp_path / 'swap'), '--dry-run']) == 0
    output = capsys.readouterr().out
    assert '--enable-sleep-mode' in output and '30064771072' in output
    assert 'VLLM_SERVER_DEV_MODE' in output
    assert list(tmp_path.iterdir()) == []
    for flags in (['--single-gpu', '0', '--gemma-gpu', '0'], ['--single-gpu', '-1'], ['--swap-dir', '/tmp/swap']):
        with pytest.raises(SystemExit) as error:
            servers.main(['start', *flags, '--dry-run'])
        assert error.value.code == 2


@pytest.mark.skipif(not sys.platform.startswith('linux'), reason='Linux TCP TIME_WAIT behavior')
def test_port_probe_reuses_closed_server_but_preserves_active_listener():
    with socket.socket() as listener:
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            listener.bind(('127.0.0.1', 0))
        except PermissionError:
            pytest.skip('Local socket binding unavailable in sandbox; run this regression on the host')
        listener.listen()
        port = listener.getsockname()[1]
        assert servers.port_occupied(port)
        with socket.create_connection(('127.0.0.1', port), timeout=2) as client:
            connection, _ = listener.accept()
            connection.close()  # The server initiates close and enters TIME_WAIT.
            assert client.recv(1) == b''
    with socket.socket() as no_reuse:
        with pytest.raises(OSError):
            no_reuse.bind(('127.0.0.1', port))
    assert not servers.port_occupied(port)
