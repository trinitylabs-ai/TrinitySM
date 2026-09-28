#!/usr/bin/env python3
"""Workshop Pipeline: run a pinned release of the composite proof harness."""
import os
from pathlib import Path
import sys


if __name__ == '__main__':
    controller = Path(__file__).resolve().parent / 'pipeline.py'
    os.execv(sys.executable, [sys.executable, '-B', str(controller), *sys.argv[1:]])
