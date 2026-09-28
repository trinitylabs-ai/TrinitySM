"""The public CLI describes and delegates the actual pipeline without seed drift."""
import json
import subprocess
import sys

import pytest
from test_public_reproduction import ROOT, load, pipeline

ENTRY = ROOT / 'harnesses/proof_workshop/run.py'


def invoke(*arguments):
    return subprocess.run([sys.executable, '-B', str(ENTRY), *arguments],
                          cwd=ROOT, capture_output=True, text=True, timeout=30)


def test_help_uses_public_name_and_documents_engine_and_controller_options():
    result = invoke('--help')
    assert result.returncode == 0, result.stderr
    assert 'Workshop Pipeline' in result.stdout
    assert 'IMO Proof Pipeline' not in result.stdout and 'R1-C' not in result.stdout
    native = load('cli_frozen_launcher', 'harnesses/imo_proof_pipeline/releases/1.7.0/launch.py')
    profile = pipeline.read(pipeline.IMPLEMENTATION / 'releases/1.7.0/profile.json')
    expected = {option for action in native.options(profile)._actions for option in action.option_strings}
    expected |= {'--release', '--list-releases', '--collect-only'}
    public = {option for action in pipeline.options()._actions for option in action.option_strings}
    assert public == expected
    assert all(option in result.stdout for option in expected)
    assert 'no model calls' in result.stdout and 'last completed proof' in result.stdout


def test_version_reports_the_public_project_release():
    result = invoke('--version')
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == 'TrinitySM 0.1.0-rc.1'


def test_inspection_distinguishes_project_version_from_verified_engine():
    result = invoke('--verify')
    assert result.returncode == 0, result.stderr
    record = json.loads(result.stdout)
    assert record['name'] == 'TrinitySM' and record['component'] == 'Workshop Pipeline'
    assert record['version'] == '0.1.0-rc.1'
    assert record['implementation_release'] == '1.12.0'
    assert record['project_manifest_sha256'] == pipeline.sha(ROOT / 'project.json')
    assert record['implementation_sha256'] == pipeline.sha(pipeline.IMPLEMENTATION / 'releases/1.12.0/release.json')
    assert record['verified_files'] == len(pipeline.read(pipeline.IMPLEMENTATION / 'releases/1.12.0/release.json')['files'])
    assert record['stages'] == list(pipeline.STAGES) and record['terminal_stage'] == 'refinement_3'
    assert record['controller_sha256'] == pipeline.sha(ROOT / 'harnesses/proof_workshop/pipeline.py')
    assert record['new_run_final_selector'] == pipeline.selector_policy.binding('1.12.0')


def test_release_listing_stays_machine_readable():
    result = invoke('--list-releases')
    assert result.returncode == 0 and result.stdout.splitlines() == ['1.7.0', '1.8.0', '1.9.0', '1.10.0', '1.11.0', '1.12.0']


@pytest.mark.parametrize('arguments', [
    ['--collect-only', '--execute-models'],
    ['--collect-only', '--dry-run'],
    ['--collect-only', '--seed-namespace', 'ignored'],
    ['--verify', '--execute-models'],
    ['--skip-failed-problem', 'synthetic', '--dry-run'],
    ['--execute-models'],  # Missing statement-only problem directory.
    ['--unknown-option'],
])
def test_invalid_cli_arguments_fail_before_launch_or_output_writes(tmp_path, monkeypatch, arguments):
    def forbidden(*args, **kwargs):
        pytest.fail('Invalid arguments must not start the implementation')
    monkeypatch.setattr(pipeline, 'run_process', forbidden)
    monkeypatch.setattr(pipeline, 'show_release', forbidden)
    run = tmp_path / 'new-run'
    with pytest.raises(SystemExit) as error:
        pipeline.main(['--output-dir', str(run), *arguments])
    assert error.value.code == 2
    assert list(tmp_path.iterdir()) == []


def test_explicit_engine_options_are_forwarded_without_changing_values():
    native = load('cli_forwarding_launcher', 'harnesses/imo_proof_pipeline/releases/1.7.0/launch.py')
    profile = pipeline.read(pipeline.IMPLEMENTATION / 'releases/1.7.0/profile.json')
    supplied = ['--problem-dir', '/tmp/statements with spaces', '--output-dir', '/tmp/proofs with spaces',
                '--problem-id', 'Problem-A', '--problem-id', 'Problem-B', '--limit', '2',
                '--gemma-endpoint', 'http://127.0.0.1:8031/v1', '--qwen-endpoint', 'http://127.0.0.1:8028/v1',
                '--model-timeout-sec', '601', '--seed-namespace', 'unchanged namespace:0',
                '--raw-seed-offset', '0', '--resume', '--skip-failed-problem', 'Problem-A',
                '--skip-failed-problem', 'Problem-B', '--execute-models']
    expected = vars(native.options(profile).parse_args(supplied))
    command = pipeline.implementation_command(pipeline.options().parse_args(supplied))
    assert vars(native.options(profile).parse_args(command[5:])) == expected


@pytest.mark.parametrize('custom_seed', [False, True])
def test_real_preflight_preserves_defaults_and_explicit_seed_settings(tmp_path, custom_seed):
    statements = tmp_path / 'statements'
    statements.mkdir()
    (statements / 'Synthetic-001.json').write_text(json.dumps({
        'problem_id': 'Synthetic-001', 'problem': 'If x=0, prove x*x=0.'}))
    run = tmp_path / 'run'
    flags = ['--seed-namespace', 'public cli:unchanged', '--raw-seed-offset', '17'] if custom_seed else []
    result = invoke('--problem-dir', str(statements), '--output-dir', str(run), '--dry-run', *flags)
    assert result.returncode == 0, result.stdout + result.stderr
    identity = pipeline.read(run / 'harness_release.json')
    defaults = pipeline.read(pipeline.IMPLEMENTATION / 'releases/1.7.0/profile.json')['run_defaults']
    expected = dict(defaults, seed_namespace='public cli:unchanged', raw_seed_offset=17) if custom_seed else defaults
    assert {key: identity['parameters'][key] for key in expected} == expected
    assert identity['final_selector'] == pipeline.selector_policy.binding('1.12.0')
    assert pipeline.selector_policy.saved(run)['binding'] == identity['final_selector']
    receipt = pipeline.read(run / 'full_pipeline_preflight.json')
    assert receipt['model_calls'] == 0 and receipt['terminal_stage'] == 'refinement_3'
    assert receipt['project_name'] == 'TrinitySM' and receipt['project_version'] == '0.1.0-rc.1'
    assert receipt['implementation_release'] == '1.12.0'
    assert not (run / 'proofs').exists()
