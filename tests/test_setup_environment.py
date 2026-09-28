"""Environment setup recovers interrupted installs without model downloads."""
import importlib.util
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace
from unittest.mock import Mock

import pytest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    'workshop_setup_environment', ROOT / 'scripts/setup_environment.py')
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)
STABLE_PYTHON = (3, 11, 15, 'final', 0)


@pytest.fixture
def stable_environment_python(monkeypatch):
    check = Mock()
    monkeypatch.setattr(setup, 'check_environment_python', check)
    return check


def existing_environment(tmp_path):
    env_path = tmp_path / '.venv-solver'
    python = env_path / 'bin/python'
    python.parent.mkdir(parents=True)
    python.touch()
    return env_path, python


def test_healthy_environment_is_reused_without_reinstalling_pip(
        tmp_path, monkeypatch, stable_environment_python):
    env_path, python = existing_environment(tmp_path)
    marker = env_path / 'installed-package'
    marker.write_text('preserve existing packages')
    builder = Mock()
    run = Mock(return_value=SimpleNamespace(returncode=0))
    monkeypatch.setattr(setup.venv, 'EnvBuilder', builder)
    monkeypatch.setattr(setup.subprocess, 'run', run)

    assert setup.ensure_environment(env_path) == python
    stable_environment_python.assert_called_once_with(python)
    builder.assert_not_called()
    run.assert_called_once()
    assert run.call_args.args[0] == [str(python), '-m', 'pip', '--version']
    assert run.call_args.kwargs['stdout'] == subprocess.DEVNULL
    assert run.call_args.kwargs['stderr'] == subprocess.DEVNULL
    assert marker.read_text() == 'preserve existing packages'


def test_existing_python_without_pip_is_repaired(tmp_path, monkeypatch, stable_environment_python):
    env_path, python = existing_environment(tmp_path)
    builder = Mock()
    calls = []

    def run(command, **kwargs):
        calls.append((command, kwargs))
        return SimpleNamespace(returncode=1 if len(calls) == 1 else 0)

    monkeypatch.setattr(setup.venv, 'EnvBuilder', builder)
    monkeypatch.setattr(setup.subprocess, 'run', run)

    assert setup.ensure_environment(env_path) == python
    builder.assert_not_called()
    assert [command for command, _ in calls] == [
        [str(python), '-m', 'pip', '--version'],
        [str(python), '-m', 'ensurepip', '--upgrade'],
        [str(python), '-m', 'pip', '--version'],
    ]
    assert calls[1][1]['check'] is True
    assert calls[2][1]['check'] is True


@pytest.mark.parametrize('directory_exists', (False, True))
def test_missing_python_recreates_environment_including_interrupted_directory(
        tmp_path, monkeypatch, directory_exists, stable_environment_python):
    env_path = tmp_path / '.venv-solver'
    if directory_exists:
        env_path.mkdir()
    python = env_path / 'bin/python'

    def create(path):
        assert path == env_path
        python.parent.mkdir(parents=True, exist_ok=True)
        python.touch()

    builder = Mock(return_value=SimpleNamespace(create=Mock(side_effect=create)))
    run = Mock(return_value=SimpleNamespace(returncode=0))
    monkeypatch.setattr(setup.venv, 'EnvBuilder', builder)
    monkeypatch.setattr(setup.subprocess, 'run', run)

    assert setup.ensure_environment(env_path) == python
    builder.assert_called_once_with(with_pip=True)
    builder.return_value.create.assert_called_once_with(env_path)
    run.assert_called_once()
    assert run.call_args.args[0] == [str(python), '-m', 'pip', '--version']


def test_symlink_environment_is_rejected_before_any_process(tmp_path, monkeypatch):
    target = tmp_path / 'other-environment'
    target.mkdir()
    env_path = tmp_path / '.venv-solver'
    env_path.symlink_to(target, target_is_directory=True)
    builder, run = Mock(), Mock()
    monkeypatch.setattr(setup.venv, 'EnvBuilder', builder)
    monkeypatch.setattr(setup.subprocess, 'run', run)

    with pytest.raises(RuntimeError, match='symlink'):
        setup.ensure_environment(env_path)
    builder.assert_not_called()
    run.assert_not_called()


@pytest.mark.parametrize('failure_stage', ('ensurepip', 'pip'))
def test_failed_pip_repair_explains_venv_package_needed(
        tmp_path, monkeypatch, failure_stage, stable_environment_python):
    env_path, _ = existing_environment(tmp_path)

    def run(command, **kwargs):
        if not kwargs.get('check'):
            return SimpleNamespace(returncode=1)
        if command[2] == failure_stage:
            raise subprocess.CalledProcessError(1, command)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(setup.subprocess, 'run', run)
    with pytest.raises(RuntimeError, match='python3.11-venv'):
        setup.ensure_environment(env_path)


def test_setup_failure_stops_before_requirements_or_downloads(tmp_path, monkeypatch, capsys):
    ensure = Mock(side_effect=RuntimeError('Install python3.11-venv and retry.'))
    run = Mock()
    monkeypatch.setattr(setup, 'ROOT', tmp_path)
    monkeypatch.setattr(setup, 'ensure_environment', ensure)
    monkeypatch.setattr(setup.subprocess, 'run', run)
    monkeypatch.setattr(setup.sys, 'version_info', STABLE_PYTHON)
    monkeypatch.setattr(setup.sys, 'argv', ['setup_environment.py', '--install', '--download-models'])

    with pytest.raises(SystemExit) as error:
        setup.main()
    assert error.value.code == 2
    assert 'python3.11-venv' in capsys.readouterr().err
    ensure.assert_called_once_with(tmp_path / '.venv-solver')
    run.assert_not_called()


@pytest.mark.parametrize('version', ((3, 11, 0, 'final', 0), STABLE_PYTHON))
def test_stable_python_311_is_accepted(version):
    setup.validate_python(version, 'test interpreter')


@pytest.mark.parametrize('version', (
    (3, 11, 0, 'alpha', 1),
    (3, 11, 0, 'beta', 5),
    (3, 11, 0, 'candidate', 1),
    (3, 10, 15, 'final', 0),
    (3, 12, 0, 'final', 0),
))
def test_incompatible_python_has_actionable_version_error(version):
    with pytest.raises(RuntimeError) as error:
        setup.validate_python(version, 'test interpreter')
    assert 'stable Python 3.11' in str(error.value)
    assert '3.11.15' in str(error.value)
    assert 'test interpreter' in str(error.value)


def test_existing_interpreter_version_is_read_in_isolated_mode(tmp_path, monkeypatch):
    python = tmp_path / '.venv-serving/bin/python'
    run = Mock(return_value=SimpleNamespace(returncode=0, stdout=json.dumps(STABLE_PYTHON)))
    monkeypatch.setattr(setup.subprocess, 'run', run)

    setup.check_environment_python(python)
    run.assert_called_once_with(
        [str(python), '-I', '-c', 'import json,sys; print(json.dumps(list(sys.version_info)))'],
        capture_output=True, text=True, check=True)


def test_existing_prerelease_is_rejected_before_pip_or_environment_changes(tmp_path, monkeypatch):
    env_path, python = existing_environment(tmp_path)
    run = Mock(return_value=SimpleNamespace(
        returncode=0, stdout=json.dumps([3, 11, 0, 'candidate', 1])))
    builder = Mock()
    monkeypatch.setattr(setup.subprocess, 'run', run)
    monkeypatch.setattr(setup.venv, 'EnvBuilder', builder)

    with pytest.raises(RuntimeError, match='stable Python 3.11'):
        setup.ensure_environment(env_path)
    builder.assert_not_called()
    run.assert_called_once()
    assert run.call_args.args[0][:3] == [str(python), '-I', '-c']
    assert python.exists()


def test_prerelease_caller_stops_before_environment_setup_or_downloads(tmp_path, monkeypatch, capsys):
    ensure, run = Mock(), Mock()
    monkeypatch.setattr(setup, 'ROOT', tmp_path)
    monkeypatch.setattr(setup, 'ensure_environment', ensure)
    monkeypatch.setattr(setup.subprocess, 'run', run)
    monkeypatch.setattr(setup.sys, 'version_info', (3, 11, 0, 'candidate', 1))
    monkeypatch.setattr(setup.sys, 'argv', ['setup_environment.py', '--install', '--download-models'])

    with pytest.raises(SystemExit) as error:
        setup.main()
    assert error.value.code == 2
    assert 'stable Python 3.11' in capsys.readouterr().err
    ensure.assert_not_called()
    run.assert_not_called()
    assert list(tmp_path.iterdir()) == []


def test_download_only_rejects_existing_prerelease_solver(tmp_path, monkeypatch, capsys):
    _, python = existing_environment(tmp_path)
    run = Mock(return_value=SimpleNamespace(
        returncode=0, stdout=json.dumps([3, 11, 0, 'candidate', 1])))
    monkeypatch.setattr(setup, 'ROOT', tmp_path)
    monkeypatch.setattr(setup.subprocess, 'run', run)
    monkeypatch.setattr(setup.sys, 'version_info', STABLE_PYTHON)
    monkeypatch.setattr(setup.sys, 'argv', ['setup_environment.py', '--download-models'])

    with pytest.raises(SystemExit) as error:
        setup.main()
    assert error.value.code == 2
    assert 'stable Python 3.11' in capsys.readouterr().err
    run.assert_called_once()
    assert run.call_args.args[0][:3] == [str(python), '-I', '-c']


def test_serving_prerelease_stops_its_install_and_all_downloads(tmp_path, monkeypatch, capsys):
    existing_environment(tmp_path)
    serving_python = tmp_path / '.venv-serving/bin/python'
    serving_python.parent.mkdir(parents=True)
    serving_python.touch()
    calls = []

    def run(command, **kwargs):
        calls.append(command)
        if command[1] == '-I':
            version = (3, 11, 0, 'candidate', 1) if command[0] == str(serving_python) else STABLE_PYTHON
            return SimpleNamespace(returncode=0, stdout=json.dumps(version))
        assert command[1:3] == ['-m', 'pip'], 'Unexpected download or bootstrap process'
        assert command[0] != str(serving_python), 'pip ran in the prerelease serving environment'
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(setup, 'ROOT', tmp_path)
    monkeypatch.setattr(setup.subprocess, 'run', run)
    monkeypatch.setattr(setup.sys, 'version_info', STABLE_PYTHON)
    monkeypatch.setattr(setup.sys, 'argv', ['setup_environment.py', '--install', '--download-models'])

    with pytest.raises(SystemExit) as error:
        setup.main()
    assert error.value.code == 2
    assert 'stable Python 3.11' in capsys.readouterr().err
    assert any(command[0] == str(serving_python) for command in calls)
