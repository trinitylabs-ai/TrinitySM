#!/usr/bin/env python3
"""Run independent selection on saved final proofs; never import the generation runtime."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harnesses.proof_selector.runner import main


if __name__ == '__main__':
    raise SystemExit(main())
