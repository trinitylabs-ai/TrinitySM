"""Byte-exact, reclaimable CPU backup storage for vLLM sleep-mode weights.

Ordinary CUDA memcpy still copies the same allocation bytes. File-backed pages
avoid the pinned allocator's RAM amplification and the two-model swap peak.
Unlink after mmap ensures that buffers disappear on wakeup or process exit.
"""
import os
from pathlib import Path
import tempfile


def backup_tensor(size_in_bytes):
    import torch
    root = Path(os.environ['GPU0_SWAP_STORAGE'])
    root.mkdir(parents=True, exist_ok=True)
    fd, path = tempfile.mkstemp(prefix='weights-', dir=root)
    try:
        os.ftruncate(fd, size_in_bytes)
        return torch.from_file(path, shared=True, size=size_in_bytes, dtype=torch.uint8)
    finally:
        os.close(fd)
        os.unlink(path)
