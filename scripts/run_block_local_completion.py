#!/usr/bin/env python3
"""Independent raw-proof block repair, audit and conditional resolve experiment."""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harnesses.block_local_completion.runner import main

if __name__ == '__main__':
    raise SystemExit(main())
