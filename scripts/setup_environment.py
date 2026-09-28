#!/usr/bin/env python3
"""Set up local solver/serving environments and optionally download pinned models."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'configs/workshop_models.json'


def validate_python(version_info, label):
    if len(version_info) < 4 or tuple(version_info[:2]) != (3, 11) or version_info[3] != 'final':
        version = '.'.join(str(part) for part in version_info[:3])
        level = version_info[3] if len(version_info) > 3 else 'unknown release level'
        raise RuntimeError(
            f'{label} uses Python {version} ({level}). A stable Python 3.11 release '
            'is required; the recorded environment uses Python 3.11.15. '
            'Use a stable interpreter and recreate any prerelease virtual environments; '
            'see docs/local_reproduction.md#replace-a-prerelease-python-environment.'
        )


def check_environment_python(python):
    try:
        result = subprocess.run(
            [str(python), '-I', '-c', 'import json,sys; print(json.dumps(list(sys.version_info)))'],
            capture_output=True, text=True, check=True,
        )
        version_info = json.loads(result.stdout)
        if not isinstance(version_info, list):
            raise ValueError('invalid Python version response')
    except (OSError, subprocess.CalledProcessError, ValueError) as error:
        raise RuntimeError(f'Cannot inspect Python interpreter {python}: {error}') from error
    validate_python(version_info, str(python))


def ensure_environment(env_path):
    """Reuse a working environment, or repair an interrupted pip bootstrap."""
    if env_path.is_symlink():
        raise RuntimeError('Virtual environment paths must not be symlinks.')
    python = env_path / 'bin/python'
    try:
        if not python.exists():
            venv.EnvBuilder(with_pip=True).create(env_path)
        check_environment_python(python)
        pip_command = [str(python), '-m', 'pip', '--version']
        probe = subprocess.run(pip_command, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL, check=False)
        if probe.returncode:
            print(f'Repairing missing or unusable pip in {env_path.name}...', flush=True)
            subprocess.run([str(python), '-m', 'ensurepip', '--upgrade'], check=True)
            subprocess.run(pip_command, check=True)
    except (OSError, subprocess.CalledProcessError) as error:
        raise RuntimeError(
            f'Could not prepare {env_path}. Stable Python 3.11 with venv/ensurepip support is required. '
            'On Debian/Ubuntu, a system interpreter needs its matching python3.11-venv package; '
            'first verify that python3.11 -VV reports a final release, not 3.11.0rc1. '
            'See docs/local_reproduction.md#replace-a-prerelease-python-environment. '
            f'Underlying error: {error}'
        ) from error
    return python


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', action='store_true', help='Create virtual environments and install dependencies.')
    parser.add_argument('--download-models', action='store_true', help='Download weights from their providers into the local cache.')
    parser.add_argument('--model-dir', type=Path, default=ROOT / '.models')
    args = parser.parse_args()
    catalog = json.loads(CATALOG.read_text())
    for spec in catalog['models'].values():
        print(f"{spec['repository']} @ {spec['revision']}\n  {spec['download_url']}", flush=True)
    if not (args.install or args.download_models):
        print('No installation or download requested. Use --install --download-models for local setup.')
        return
    try:
        validate_python(sys.version_info, 'Setup interpreter')
    except RuntimeError as error:
        parser.error(str(error))
    solver_python = ROOT / '.venv-solver/bin/python'
    if args.install:
        for role in ('solver', 'serving'):
            env_path = ROOT / ('.venv-' + role)
            try:
                environment_python = ensure_environment(env_path)
            except RuntimeError as error:
                parser.error(str(error))
            subprocess.run([str(environment_python), '-m', 'pip', 'install', '-r',
                            str(ROOT / f'requirements-{role}.txt')], check=True)
    if args.download_models:
        if not solver_python.exists():
            parser.error('Install the solver environment with --install first.')
        if not args.install:
            try:
                check_environment_python(solver_python)
            except RuntimeError as error:
                parser.error(str(error))
        # Credentials, if required by the provider, come from the user's HF login
        # or HF_TOKEN environment variable. They are never arguments or files here.
        code = (
            'import json,sys\nfrom huggingface_hub import snapshot_download\n'
            'catalog=json.load(open(sys.argv[1]))\n'
            'for spec in catalog["models"].values():\n'
            ' snapshot_download(repo_id=spec["repository"], revision=spec["revision"], cache_dir=sys.argv[2])\n'
        )
        subprocess.run([str(solver_python), '-B', '-c', code, str(CATALOG),
                        str(args.model_dir.expanduser().resolve())], check=True)
    print('Setup complete. See docs/local_reproduction.md for local serving and proof generation.')


if __name__ == '__main__':
    main()
