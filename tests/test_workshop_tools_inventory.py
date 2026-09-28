"""The distributed Tools entry point verifies without external grading references."""
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_tools_entry_point_verifies_shipped_runtime_without_external_reference():
    directory = ROOT / 'experiments/workshop_tools'
    inventory = json.loads((directory / 'runtime_inventory.json').read_text())
    for row in inventory['excluded_reference_files']:
        assert not (directory / 'runtime' / row['path']).exists()
        assert row['path'] not in {entry['path'] for entry in inventory['files']}
    result = subprocess.run([sys.executable, '-B', str(directory / 'run.py'), '--verify'],
                            cwd=ROOT, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    assert f"Verified {len(inventory['files'])} experimental runtime files." in result.stdout
