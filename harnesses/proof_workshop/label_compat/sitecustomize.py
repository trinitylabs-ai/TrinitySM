"""Activate this run's captured normalization policy in engine child processes."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys


def activate():
    policy_path = Path(os.environ['WORKSHOP_LABEL_RECOVERY']).resolve()
    if getattr(subprocess.Popen, '_workshop_label_policy', None) == str(policy_path):
        return
    record = json.loads(policy_path.read_text())
    identity = json.loads((policy_path.parent / 'harness_release.json').read_text())
    if record['binding'] != identity['label_recovery']:
        raise ValueError('Label recovery differs from the saved run identity')
    directory = policy_path.parent / 'label_runtime'
    if set(record['binding']['files']) != {'label_recovery.py', 'sitecustomize.py', 'comparison_recovery.py'}:
        raise ValueError('Unexpected label recovery file inventory')
    for name, expected in record['binding']['files'].items():
        path = directory / name
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('Captured label recovery code changed: ' + name)
    engine = Path(record['engine']).resolve()
    if hashlib.sha256((engine.parents[1] / 'release.json').read_bytes()).hexdigest() != identity['release_sha256']:
        raise ValueError('Label recovery engine differs from the saved release')
    spec = importlib.util.spec_from_file_location('workshop_active_label_recovery', directory / 'label_recovery.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if module.POLICY != record['binding']['policy']:
        raise ValueError('Label recovery policy changed')
    module.install(engine, persistent=True, receipt_directory=policy_path.parent / 'label_recoveries')
    original_popen = subprocess.Popen

    class Popen(original_popen):
        def __init__(self, *args, **kwargs):
            supplied = kwargs.get('env')
            environment = dict(os.environ if supplied is None else supplied)
            environment['WORKSHOP_LABEL_RECOVERY'] = str(policy_path)
            paths = environment.get('PYTHONPATH', '').split(os.pathsep)
            environment['PYTHONPATH'] = os.pathsep.join([str(directory)] +
                [p for p in paths if p and p != str(directory)])
            environment['PYTHONDONTWRITEBYTECODE'] = '1'
            kwargs['env'] = environment
            super().__init__(*args, **kwargs)

    Popen._workshop_label_policy = str(policy_path)
    subprocess.Popen = Popen


if os.environ.get('WORKSHOP_LABEL_RECOVERY'):
    try:
        activate()
    except Exception as error:
        # Python otherwise only prints sitecustomize exceptions and continues.
        raise SystemExit('Cannot activate captured label recovery: ' + str(error)) from error
