"""Run the existing strict-scoring skill after a hash-bound synthesis completes."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--skill-launcher", type=Path, required=True)
    args = parser.parse_args()
    root = args.run_root.resolve()
    if args.output_dir.exists():
        raise FileExistsError(args.output_dir)
    print("Waiting for completed synthesis; no grading or GPU call launched yet.", flush=True)
    while True:
        manifest_path = root / "manifest.json"
        if manifest_path.is_file():
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                # The source writer replaces small ledger files non-atomically.
                time.sleep(30)
                continue
            if manifest.get("state") == "failed_closed":
                print("Synthesis failed closed; no terminal proof submitted for grading.", flush=True)
                return
            if manifest.get("state") == "completed":
                proof_path = Path(manifest["terminal_proof"]).resolve()
                if root not in proof_path.parents:
                    raise ValueError("terminal proof is outside its run root")
                proof = proof_path.read_text(encoding="utf-8").strip()
                if hashlib.sha256(proof.encode("utf-8")).hexdigest() != manifest["terminal_proof_sha256"]:
                    raise ValueError("completed terminal proof hash mismatch")
                task = f"{manifest['problem_id']}:generic_packaging={proof_path}"
                command = [sys.executable, str(args.skill_launcher.resolve()),
                           "--proof-task", task, "--output-dir", str(args.output_dir.resolve()),
                           "--workers", "1"]
                print(f"Launching isolated strict scoring of {proof_path}", flush=True)
                subprocess.run(command, cwd=Path(__file__).resolve().parents[1], check=True)
                return
        time.sleep(30)


if __name__ == "__main__":
    main()
