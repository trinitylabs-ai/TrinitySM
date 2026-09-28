"""External scheduling adapter; frozen engine files remain unchanged."""
import importlib.abc
import importlib.machinery
import os
from pathlib import Path
import subprocess
import sys

if os.environ.get('GPU0_BULK_URL'):
    here = Path(__file__).resolve().parent
    sys.path.insert(0, str(here.parent))
    from client import patch_module

    targets = {
        'experiments.local_math_verifier.runtime',
        'experiments.local_math_verifier.cross_lane_voter.timeout_adapter',
        'cognitive_well_harness_v0_3_249_v108_third_resolve_all_call_budget_forcing_20260904.budget_forcing',
        'cognitive_well_harness_v0_3_257_v108_third_resolve_raw_t10_bf_temp07_20260904.budget_forcing',
        'cognitive_well_harness_v0_3_290_p5_iterated_review_fusion_20260906.repair_boundary',
    }

    class Loader(importlib.abc.Loader):
        def __init__(self, original): self.original = original
        def create_module(self, spec): return self.original.create_module(spec)
        def exec_module(self, module):
            self.original.exec_module(module)
            expected = Path(os.environ['GPU0_BULK_ENGINE']).resolve()
            if not Path(module.__file__).resolve().is_relative_to(expected):
                raise RuntimeError('Refusing to patch an unpinned engine')
            patch_module(module)

    class Finder(importlib.abc.MetaPathFinder):
        def find_spec(self, fullname, path=None, target=None):
            if fullname not in targets: return None
            spec = importlib.machinery.PathFinder.find_spec(fullname, path)
            spec.loader = Loader(spec.loader)
            return spec

    sys.meta_path.insert(0, Finder())
    original_popen = subprocess.Popen
    class Popen(original_popen):
        def __init__(self, *args, **kwargs):
            env = dict(kwargs.get('env') or os.environ)
            if env.get('GPU0_BULK_URL'):
                paths = env.get('PYTHONPATH', '').split(os.pathsep)
                env['PYTHONPATH'] = os.pathsep.join([str(here)] + [p for p in paths if p and p != str(here)])
                env['PYTHONDONTWRITEBYTECODE'] = '1'
                kwargs['env'] = env
            super().__init__(*args, **kwargs)
    subprocess.Popen = Popen

# Python imports only the first sitecustomize on PYTHONPATH. Delegate to the
# captured per-run policy when the single-GPU transport adapter is first.
if os.environ.get('WORKSHOP_LABEL_RECOVERY'):
    import importlib.util
    policy_root = Path(os.environ['WORKSHOP_LABEL_RECOVERY']).resolve().parent
    spec = importlib.util.spec_from_file_location(
        'workshop_label_site', policy_root / 'label_runtime/sitecustomize.py')
    try:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as error:
        raise SystemExit('Cannot activate captured label recovery: ' + str(error)) from error
