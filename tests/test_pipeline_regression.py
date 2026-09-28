"""Statement-to-final-proof regression with network access disabled."""
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('release', ['A','B'])
@pytest.mark.parametrize('verdict', ['CERTIFIED', 'REJECTED'])
def test_all_four_lanes_complete_three_passes_without_prompt_or_proof_drift(tmp_path, verdict, release):
    output = tmp_path / 'run'
    result = subprocess.run([sys.executable, '-B', str(ROOT / 'tests/pipeline_regression_driver.py'),
                             str(output), verdict, *(['--harness-b'] if release=='B' else [])], cwd=ROOT, text=True, capture_output=True, timeout=90)
    assert result.returncode == 0, result.stdout + result.stderr
    actual = json.loads((output / 'regression_result.json').read_text())
    expected = json.loads((ROOT / 'tests/fixtures' / ('pipeline_' + verdict.lower() + '.json')).read_text())
    assert actual == expected


@pytest.mark.parametrize('release', ['A','B'])
def test_recovery_replays_real_completed_lane_receipts_without_models(tmp_path, release):
    result = subprocess.run([sys.executable, '-B', str(ROOT / 'tests/pipeline_regression_driver.py'),
                             str(tmp_path / 'run'), 'CERTIFIED', '--recover', *(['--harness-b'] if release=='B' else [])],
                            cwd=ROOT, text=True, capture_output=True, timeout=90)
    assert result.returncode == 0, result.stdout + result.stderr
