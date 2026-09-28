#!/usr/bin/env python3
"""Independent saved final proof → lazy-check → conditional expansion experiment."""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harnesses.post_c3_completion.runner import main

if __name__ == '__main__':
    raise SystemExit(main())
