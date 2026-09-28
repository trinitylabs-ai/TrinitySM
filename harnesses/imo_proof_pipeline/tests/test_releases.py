import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


publisher = load('publisher', ROOT / 'tools/publish_release.py')
runtime = load('runtime', ROOT / 'tools/launch_template.py')


@pytest.fixture
def package(tmp_path):
    root = tmp_path / 'composite'
    (root / 'tools').mkdir(parents=True)
    shutil.copy2(ROOT / 'tools/launch_template.py', root / 'tools/launch_template.py')
    shutil.copy2(ROOT / 'profile.json', root / 'profile.json')
    engine = tmp_path / 'upstream'
    script = engine / 'source/scripts/run_v263_v290.py'
    script.parent.mkdir(parents=True)
    script.write_text('''import json,os,pathlib,sys
def collect_problems(*args):
 return []
def freeze_queue(args):
 (args.output_dir/'manifest.json').write_text('{}')
if __name__=='__main__':
 args=sys.argv
 assert '--dry-run' in args
 out=pathlib.Path(args[args.index('--output-dir')+1])
 if '--resume' not in args:
  out.mkdir(exist_ok=False)
 else:
  assert (out/'manifest.json').is_file()
 with (out/'executions.jsonl').open('a') as f:
  f.write(json.dumps({'args':args[1:],'cwd':os.getcwd(),'pythonpath':os.environ['PYTHONPATH']})+'\\n')
''')
    prompt = engine / 'source/prompts/original.md'
    prompt.parent.mkdir(); prompt.write_text('Generic original prompt.')
    publisher.write(engine / 'freeze.json', {'release_id': 'test-engine',
        'files': {str(p.relative_to(engine)): publisher.sha(p) for p in (script, prompt)}})
    (engine / 'SHA256SUMS').write_text('test index\n')
    publisher.publish(engine, root / 'profile.json', '1.0.0', 'initial', 'Initial test', root)
    return root, engine


def test_release_verifies_and_rejects_changed_or_added_assets(package):
    root, _ = package
    release = root / 'releases/1.0.0'
    runtime.verify(release)
    prompt = release / 'engine/source/prompts/original.md'
    saved = prompt.read_bytes()
    prompt.write_text('Modified problem-specific prompt.')
    with pytest.raises(ValueError, match='changed'):
        runtime.verify(release)
    prompt.write_bytes(saved)
    extra = release / 'engine/source/extra.py'
    extra.write_text('pass')
    with pytest.raises(ValueError, match='unlisted'):
        runtime.verify(release)
    extra.unlink()
    (release / 'linked').symlink_to(release / 'engine', target_is_directory=True)
    with pytest.raises(ValueError, match='symbolic'):
        runtime.verify(release)


def test_versions_are_append_only_and_patch_cannot_change_behavior(package):
    root, engine = package
    profile = root / 'profile.json'
    old = (root / 'releases/1.0.0/release.json').read_bytes()
    with pytest.raises(FileExistsError):
        publisher.publish(engine, profile, '1.0.0', 'initial', 'Overwrite', root)
    with pytest.raises(ValueError, match='increment'):
        publisher.publish(engine, profile, '1.0.2', 'patch', 'Skip version', root)
    publisher.publish(engine, profile, '1.0.1', 'patch', 'Metadata only', root)
    assert (root / 'releases/1.0.0/release.json').read_bytes() == old
    data = json.loads(profile.read_text())
    data['run_defaults']['seed_namespace'] = 'explicit-new-default'
    publisher.write(profile, data)
    with pytest.raises(ValueError, match='minor/major'):
        publisher.publish(engine, profile, '1.0.2', 'patch', 'Changed defaults', root)
    publisher.publish(engine, profile, '1.1.0', 'minor', 'Changed defaults', root)
    for version in ('1.0.0', '1.0.1', '1.1.0'):
        runtime.verify(root / 'releases' / version)


def test_dry_run_preserves_original_seed_flags_and_locks_resume(package, tmp_path, monkeypatch):
    root, _ = package
    release = root / 'releases/1.0.0'
    manifest, profile = runtime.verify(release)
    output = tmp_path / 'run'
    args = runtime.options(profile).parse_args(['--problem-dir', str(tmp_path / 'statements'),
                                               '--output-dir', str(output), '--dry-run'])
    def forbidden(*a, **kw):
        raise AssertionError('Dry run must not inspect or call servers')
    monkeypatch.setattr(runtime, 'server_settings', forbidden)
    assert runtime.launch(args, manifest, profile, release) == 0
    record = json.loads((output / 'executions.jsonl').read_text())
    argv = record['args']
    assert argv[argv.index('--seed-namespace') + 1] == 'v263-v290:problem-only'
    assert argv[argv.index('--raw-seed-offset') + 1] == '0'
    assert record['cwd'] == record['pythonpath'] == str(release / 'engine/source')
    identity = (output / 'harness_release.json').read_bytes()
    args.resume = True
    assert runtime.launch(args, manifest, profile, release) == 0
    assert (output / 'harness_release.json').read_bytes() == identity
    args.raw_seed_offset = 1
    with pytest.raises(ValueError, match='Resume changes'):
        runtime.launch(args, manifest, profile, release)
    assert len((output / 'executions.jsonl').read_text().splitlines()) == 2


def test_existing_historical_run_is_never_modified(package, tmp_path):
    root, _ = package
    release = root / 'releases/1.0.0'
    manifest, profile = runtime.verify(release)
    output = tmp_path / 'historical'
    output.mkdir(); (output / 'manifest.json').write_text('original')
    args = runtime.options(profile).parse_args(['--problem-dir', str(tmp_path), '--output-dir', str(output), '--dry-run'])
    with pytest.raises(FileExistsError):
        runtime.launch(args, manifest, profile, release)
    args.resume = True
    with pytest.raises(ValueError, match='not a run created'):
        runtime.launch(args, manifest, profile, release)
    assert [p.name for p in output.iterdir()] == ['manifest.json']


def test_server_profile_rejects_wrong_mtp_and_weights(tmp_path):
    expected = json.loads((ROOT / 'profile.json').read_text())['servers']['qwen']
    proc = tmp_path / 'proc'; case = proc / '123'; case.mkdir(parents=True)
    argv = ['vllm', 'serve', '/cache/snapshots/' + expected['snapshot'], '--served-model-name', expected['model'],
            '--port', '8027', '--speculative-config', '{"method":"mtp","num_speculative_tokens":4}',
            '--default-chat-template-kwargs', '{"enable_thinking":true}', '--async-scheduling', '--language-model-only']
    for flag, value in expected['flags'].items():
        argv += [flag, value]
    def save():
        (case / 'cmdline').write_bytes(('\0'.join(argv) + '\0').encode())
    save()
    assert runtime.server_settings('http://127.0.0.1:8027/v1', expected, proc)['mtp'] == 4
    idx = argv.index('--speculative-config') + 1
    argv[idx] = '{"method":"mtp","num_speculative_tokens":0}'; save()
    with pytest.raises(ValueError, match='MTP=4'):
        runtime.server_settings('http://127.0.0.1:8027/v1', expected, proc)
    argv[idx] = '{"method":"mtp","num_speculative_tokens":4}'
    argv[2] = '/different/weights'; save()
    with pytest.raises(ValueError, match='snapshot'):
        runtime.server_settings('http://127.0.0.1:8027/v1', expected, proc)


def test_current_published_release_verifies():
    registry = json.loads((ROOT / 'releases/index.json').read_text())
    assert set(registry['releases']) == {'1.7.0', '1.8.0', '1.9.0', '1.10.0', '1.11.0', '1.12.0'}
    manifest, profile = runtime.verify(ROOT / 'releases/1.7.0')
    assert manifest['version'] == '1.7.0'
    assert profile['components'] == {'frontend': '0.3.263', 'backend': '0.3.290+goldfree.1'}
