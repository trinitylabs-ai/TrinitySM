"""Bind format recovery to new runs; legacy runs retain their original behavior."""
from contextlib import contextmanager
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SOURCES = {'label_recovery.py': HERE / 'label_recovery.py',
           'sitecustomize.py': HERE / 'label_compat/sitecustomize.py',
           'comparison_recovery.py': HERE.parent / 'cross_lane_voter/mechanical_recovery.py'}
POLICY = 'explicit-stage-and-comparison-format-normalization-v2'
INVENTORIES = {
    'explicit-stage-label-normalization-v1': {'label_recovery.py', 'sitecustomize.py'},
    POLICY: set(SOURCES),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def binding(version):
    if version != '1.12.0':
        return None
    return dict(policy=POLICY, files={name: sha(path) for name, path in SOURCES.items()})


def prepare(root, engine):
    identity = json.loads((root / 'harness_release.json').read_text())
    bound = identity.get('label_recovery')
    if bound is None:
        return  # An existing run without this binding is never upgraded.
    destination = root / 'label_runtime'
    destination.mkdir()
    for name, source in SOURCES.items():
        data = source.read_bytes()
        if hashlib.sha256(data).hexdigest() != bound['files'][name]:
            raise ValueError('Label recovery changed during run preparation')
        with (destination / name).open('xb') as handle:
            handle.write(data)
    with (root / 'label_recovery.json').open('x') as handle:
        json.dump(dict(binding=bound, engine=str(engine.resolve())), handle, indent=2)
        handle.write('\n')


def saved(root):
    root = Path(root).resolve()
    identity_path = root / 'harness_release.json'
    if not identity_path.exists():
        return None
    identity = json.loads(identity_path.read_text())
    bound = identity.get('label_recovery')
    if bound is None:
        return None
    record = json.loads((root / 'label_recovery.json').read_text())
    if record['binding'] != bound or set(bound['files']) != INVENTORIES.get(bound['policy']):
        raise ValueError('Label recovery differs from the saved run identity')
    for name, expected in bound['files'].items():
        path = root / 'label_runtime' / name
        if path.is_symlink() or sha(path) != expected:
            raise ValueError('Captured label recovery code changed: ' + name)
    engine = Path(record['engine']).resolve()
    if sha(engine.parents[1] / 'release.json') != identity['release_sha256']:
        raise ValueError('Label recovery engine differs from the saved release')
    return record


def environment(root, original):
    result = dict(original)
    if saved(root) is None:
        # A child run cannot inherit a different run's normalization policy.
        result.pop('WORKSHOP_LABEL_RECOVERY', None)
        return result
    directory = str(Path(root).resolve() / 'label_runtime')
    result['WORKSHOP_LABEL_RECOVERY'] = str(Path(root).resolve() / 'label_recovery.json')
    result['PYTHONPATH'] = os.pathsep.join([directory] +
        [p for p in result.get('PYTHONPATH', '').split(os.pathsep) if p and p != directory])
    result['PYTHONDONTWRITEBYTECODE'] = '1'
    return result


@contextmanager
def validation(root):
    record = saved(root)
    if record is None:
        yield
        return
    name = 'workshop_label_recovery_' + record['binding']['files']['label_recovery.py']
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, Path(root) / 'label_runtime/label_recovery.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sys.modules[name] = module
    with sys.modules[name].enabled(record['engine']):
        yield
