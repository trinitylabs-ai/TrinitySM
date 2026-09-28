"""Recorded vLLM compatibility for one GPU and file-backed sleeping weights.

Scope the advisory NVML name scan to the chosen GPU, as in the recorded run
with GPU 1 offline. Retain the standard serving compatibility fixes too.
"""
import importlib.abc
import importlib.machinery
import os
from pathlib import Path
import runpy
import sys

gpu = os.environ.get('CUDA_VISIBLE_DEVICES', '')
if not gpu.isdecimal():
    raise RuntimeError('Single-GPU sleep mode requires one numeric CUDA device index')


class Loader(importlib.abc.Loader):
    def __init__(self, original): self.original = original
    def create_module(self, spec): return self.original.create_module(spec)
    def exec_module(self, module):
        source = self.original.get_source(module.__name__)
        if module.__name__ == 'vllm.platforms.cuda':
            old = 'device_names = [cls._get_physical_device_name(i) for i in range(device_ids)]'
            new = f'device_names = [cls._get_physical_device_name({int(gpu)})]  # selected GPU only'
        else:
            old = '''cpu_backup_tensor = torch.empty(
                    size_in_bytes,
                    dtype=torch.uint8,
                    device="cpu",
                    pin_memory=PIN_MEMORY,
                )'''
            new = '''from swap_storage import backup_tensor
                cpu_backup_tensor = backup_tensor(size_in_bytes)'''
        assert source.count(old) == 1, 'vLLM compatibility target changed'
        exec(compile(source.replace(old, new), self.original.get_filename(module.__name__), 'exec'), module.__dict__)


class Finder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname not in ('vllm.platforms.cuda', 'vllm.device_allocator.cumem'): return None
        spec = importlib.machinery.PathFinder.find_spec(fullname, path)
        spec.loader = Loader(spec.loader)
        return spec


sys.meta_path.insert(0, Finder())
sys.path.insert(0, str(Path(__file__).resolve().parent))
runpy.run_path(os.environ['WORKSHOP_BASE_COMPAT'])
