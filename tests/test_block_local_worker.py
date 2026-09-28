"""Offline worker checks with real frozen runtime/BF and mocked physical inference."""
import json
from pathlib import Path
import subprocess
import sys

import pytest

from harnesses.block_local_completion import blocks, policy, prompts, worker


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value if isinstance(value, bytes) else json.dumps(value).encode())
    return path


@pytest.fixture
def job_file(tmp_path):
    root = tmp_path.resolve()
    claim = "Prove the stated implication."
    problem = {"problem_id": "imo2026_p2", "problem_number": 2, "claim": claim,
               "problem_sha256": worker.frozen.digest(claim.encode())}
    candidates = []
    for cid in worker.CANDIDATES:
        data = (f"  Header π {cid}.\r\n\r\nMissing argument.\r\n\r\n"
                "Middle unchanged.\r\n\r\nLater unchanged.\r\n\r\nTail unchanged.\r\n ").encode()
        path = write(root / "inputs/imo2026_p2" / (cid + ".md"), data)
        candidates.append({"candidate_id": cid, "proof_path": str(path), "selected_stage": "raw",
            "proof_file_sha256": worker.frozen.digest(data), "proof_sha256": worker.frozen.text_digest(data)})
    manifest = write(root / "inputs/manifest.json", {"schema": "block-local-inputs-v1", "source_arm": "raw",
        "release_sha256": worker.frozen.digest((worker.frozen.RELEASE / "release.json").read_bytes()),
        "source_hashes": {}, "problems": [{"problem": problem, "candidates": candidates}]})
    return write(root / "job.json", {"schema": "block-local-job-v1", "experiment": worker.EXPERIMENT,
        "processing_scope": "all_saved_raw_proofs", "pipeline_config": worker.PIPELINE_CONFIG,
        "strategy": "block",
        "source_arm": "raw", "dry_run": False, "output_dir": str(root / "output"),
        "problem": problem, "candidates": candidates,
        "runtime": {"gemma_endpoint": "http://127.0.0.1:8030/v1", "qwen_endpoint": "http://127.0.0.1:8027/v1",
                    "model_timeout_sec": 14400, "workers": 4, "seed_namespace": "block-local-raw:0:imo2026_p2",
                    "repair_temperature": 0.7},
        "input_manifest_path": str(manifest), "input_manifest_sha256": worker.frozen.digest(manifest.read_bytes())})


SCRIPT = r'''
from dataclasses import asdict
import json
from pathlib import Path
import sys
import threading
from harnesses.block_local_completion import worker, policy, blocks, prompts

job_path, mode = Path(sys.argv[1]), sys.argv[2]
job = json.loads(job_path.read_text())
source_bytes = {c['candidate_id']: Path(c['proof_path']).read_bytes() for c in job['candidates']}
real_load = worker.frozen.load_release
servers = []
def load():
    launcher, manifest, profile = real_load()
    def server(endpoint, expected):
        servers.append(expected['model'])
        return {'offline_test': True, 'model': expected['model']}
    launcher.server_settings = server
    return launcher, manifest, profile
worker.frozen.load_release = load
backend = worker.frozen.load_backend()
bf = backend.v263.parent._budget_forcing
calls, lock = [], threading.Lock()
phases = ('lazy_check', 'expansion', 'audit', 'resolve')
all_lanes = set(worker.CANDIDATES)
accepted = {phase: set() for phase in phases}
arrived = {(phase, forced): set() for phase in phases for forced in (False, True)}
barriers = {(phase, forced): threading.Barrier(4, timeout=5) for phase in phases for forced in (False, True)}
batch_index = 0
real_run_batch = worker.legacy.run_batch
def synchronized_batch(ids, task, on_result, *, policy_error):
    global batch_index
    phase = phases[batch_index]
    batch_index += 1
    assert set(ids) == all_lanes
    def accepted_result(cid, value):
        on_result(cid, value)
        with lock:
            accepted[phase].add(cid)
    real_run_batch(ids, task, accepted_result, policy_error=policy_error)
    assert accepted[phase] == all_lanes
if mode == 'batch_all':
    worker.legacy.run_batch = synchronized_batch
issue = '<ISSUES>\n<ISSUE id="I1" blocks="B0002">\nJustify the missing implication and preserve later uses.\n</ISSUE>\n</ISSUES>'
def patch(text, block='B0002'):
    return '<PATCHES>\n<REPLACE blocks="'+block+'" issues="I1">\n'+text+'\n</REPLACE>\n</PATCHES>'
def physical(**kwargs):
    root, stage = Path(kwargs['output_dir']), kwargs['stage']
    root.mkdir(parents=True, exist_ok=True)
    cid = next(part for part in root.parts if part in worker.CANDIDATES)
    phase = ('audit' if stage.startswith('post_block_audit') else
             'resolve' if stage.startswith('post_block_resolve') else
             'lazy_check' if stage.startswith('lazy_check') else 'expansion')
    forced = bool(kwargs.get('continuation_instruction'))
    config = asdict(kwargs['config'])
    assert config['timeout_seconds'] == 14400
    assert config['max_tokens'] == (49152 if phase=='audit' else 65536 if phase in ('expansion','resolve') else 32768 if forced else 16384)
    assert (config['top_p'], config['top_k']) == ((1.0,-1) if phase=='audit' else (0.95,64))
    assert config['temperature'] == (0.1 if phase=='lazy_check' else 0.2 if phase=='audit' else job['runtime']['repair_temperature'])
    if mode == 'batch_all':
        with lock:
            if phases.index(phase):
                assert accepted[phases[phases.index(phase)-1]] == all_lanes, 'next phase started before prior results completed'
            assert cid not in arrived[phase, forced], 'superfluous physical call'
            arrived[phase, forced].add(cid)
        # No physical request may finish until all four eligible lanes have
        # entered the same primary/BF round. A serial implementation times out.
        barriers[phase, forced].wait()
    candidate = worker.legacy.seed_for(job['runtime']['seed_namespace'], cid)
    seed = (backend.repair_boundary.stable_seed(str(worker.legacy.stage_seed(candidate,'post_block_audit')),'49152') if phase=='audit'
            else worker.legacy.stage_seed(candidate, {'lazy_check':'lazy_check','expansion':'lazy_in_place_resolve','resolve':'post_block_resolve'}[phase]))
    if 'attempt2' not in stage:
        assert config['seed'] == seed, (phase,config['seed'],seed)
    if forced:
        assert '[Preserved reasoning]' in kwargs['prior_generation']
        assert '[Preserved response]' in kwargs['prior_generation']
        assert 'PRIMARY REASONING' in kwargs['prior_generation'] and 'PRIMARY ANSWER' in kwargs['prior_generation']
        assert kwargs['continuation_instruction'] == policy.CUES[phase]
        if phase=='lazy_check':
            text = issue if mode=='batch_all' or (cid=='t10_r01' and mode!='no_issues') else 'NO_ISSUES'
            if mode=='bad_issue' and cid=='t10_r01': text = issue.replace('B0002','B9999')
        elif phase=='expansion':
            text = patch('Expanded argument.')
            if mode=='cannot': text = 'CANNOT_REPAIR_LOCALLY'
            if mode=='full_proof': text = 'BEGIN_REPAIRED_PROOF\nEntire rewritten proof.\nEND_REPAIRED_PROOF'
            if mode=='outside': text = patch('Unauthorized tail rewrite.','B0005')
            if mode=='unchanged': text = patch('Missing argument.')
        elif phase=='audit':
            assert kwargs['model'] == 'Qwen/Qwen3.6-27B'
            assert 'CURRENT PATCHED PROOF BLOCKS' in kwargs['prompt'] and 'Expanded argument.' in kwargs['prompt']
            assert 'ORIGINAL CHANGED SNIPPETS' in kwargs['prompt'] and 'Missing argument.' in kwargs['prompt']
            text = issue if mode in ('resolve','restore','resolve_cannot','resolve_bad','resolve_unchanged','batch_all') else 'NO_ISSUES'
            if mode=='audit_bad': text = 'This is not a structured audit.'
        else:
            assert 'CURRENT PROOF BLOCKS' in kwargs['prompt'] and 'Expanded argument.' in kwargs['prompt']
            assert 'restore originally valid text' in kwargs['prompt'] and 'Missing argument.' in kwargs['prompt']
            text = patch('Resolved argument.')
            if mode=='restore': text = patch('Missing argument.')
            if mode=='resolve_cannot': text = 'CANNOT_REPAIR_LOCALLY'
            if mode=='resolve_bad': text = 'Whole proof again.'
            if mode=='resolve_unchanged': text = patch('Expanded argument.')
    else:
        text = 'PRIMARY ANSWER'
    with lock: calls.append({'phase':phase,'forced':forced,'cid':cid,'config':config})
    reasoning = 'FORCED REASONING' if forced else 'PRIMARY REASONING'
    metadata = {'stage':stage,'model':kwargs['model'],'config':config,'finish_reason':'stop'}
    raw = {'choices':[{'finish_reason':'stop','message':{'content':text,'reasoning_content':reasoning}}]}
    for suffix,data in (('.raw_response.json',json.dumps(raw)),('.metadata.json',json.dumps(metadata)),
        ('.prompt.txt',kwargs['prompt']),('.user_prompt.txt',kwargs['user_prompt']),('.reasoning.txt',reasoning)):
        (root/(stage+suffix)).write_text(data)
    return {'text':text,'reasoning':reasoning,'metadata':metadata}
bf._ORIGINAL = physical
before = bf._continue_primary, bf.continuation_instruction
result = worker.run(job_path, execute_models=True)
assert (bf._continue_primary,bf.continuation_instruction)==before
assert servers == ['google/gemma-4-31B-it','Qwen/Qwen3.6-27B']
lane = result['lanes'][0]
original = source_bytes['t10_r01']
final = Path(lane['proof_path']).read_bytes()
failed = mode in ('cannot','full_proof','outside','bad_issue','audit_bad','resolve_cannot','resolve_bad','resolve_unchanged')
assert result['state'] == ('completed_with_fallbacks' if failed else 'completed'), result
if mode=='accept':
    assert final == original.replace(b'Missing argument.',b'Expanded argument.')
    assert lane['local_result']=='patched_audit_passed' and lane['adopted_from']=='expansion'
    assert len(calls)==12
elif mode in ('resolve','restore','batch_all'):
    assert final == (original if mode=='restore' else original.replace(b'Missing argument.',b'Resolved argument.'))
    assert lane['local_result']=='resolved' and lane['adopted_from']=='resolve'
    assert len(calls)==(32 if mode=='batch_all' else 14)
else:
    assert final==original, (mode,final)
    assert lane['adopted_from']=='original'
if failed: assert lane['operation']=='failed'
if mode in ('no_issues','bad_issue'): assert not any(c['phase']!='lazy_check' for c in calls)
if mode in ('cannot','full_proof','outside','unchanged'): assert not any(c['phase'] in ('audit','resolve') for c in calls)
if mode=='unchanged': assert lane['local_result']=='unchanged_patch_audit_skipped'
if mode=='no_issues': assert len(calls)==8
for item in result['lanes'][1:]:
    assert item['operation']==('expanded' if mode=='batch_all' else 'no_issues')
    expected = source_bytes[item['candidate_id']]
    if mode=='batch_all':
        expected = expected.replace(b'Missing argument.',b'Resolved argument.')
        assert item['local_result']=='resolved'
    assert Path(item['proof_path']).read_bytes()==expected
if mode=='batch_all':
    assert batch_index==4
    assert all(ids==all_lanes for ids in arrived.values())
    assert all(ids==all_lanes for ids in accepted.values())
assert result['runtime']['repair_temperature']==job['runtime']['repair_temperature']
for phase in phases:
    event_path = Path(job['output_dir'])/(phase+'_continuations.jsonl')
    if not event_path.exists(): continue
    for line in event_path.read_text().splitlines():
        event = json.loads(line)
        expected = 0.1 if phase=='lazy_check' else 0.2 if phase=='audit' else job['runtime']['repair_temperature']
        assert event['config']['temperature']==expected
        assert event['response_config']['temperature']==expected
for c in job['candidates']: assert Path(c['proof_path']).read_bytes()==source_bytes[c['candidate_id']]
assert result['grading_performed'] is False and result['mathematically_verified'] is False
for item in result['lanes']:
    assert abs(sum(item['phase_elapsed_seconds'].values())-item['elapsed_seconds'])<0.00001
print('OFFLINE_OK '+mode)
'''


@pytest.mark.parametrize("mode", ["accept", "resolve", "restore", "no_issues", "cannot", "full_proof", "outside",
                                 "bad_issue", "unchanged", "audit_bad", "resolve_cannot", "resolve_bad", "resolve_unchanged"])
def test_actual_frozen_runtime_bf_and_atomic_chain_offline(job_file, mode):
    result = subprocess.run([sys.executable, "-B", "-c", SCRIPT, str(job_file), mode],
                            cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + "\n" + result.stderr
    assert "OFFLINE_OK " + mode in result.stdout


@pytest.mark.parametrize("repair_temperature", [0.7, 0.4])
def test_four_lane_primary_and_bf_concurrency_with_stage_barriers(job_file, repair_temperature):
    job = json.loads(job_file.read_text())
    job["runtime"]["repair_temperature"] = repair_temperature
    write(job_file, job)
    result = subprocess.run([sys.executable, "-B", "-c", SCRIPT, str(job_file), "batch_all"],
                            cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, timeout=40)
    assert result.returncode == 0, result.stdout + "\n" + result.stderr
    assert "OFFLINE_OK batch_all" in result.stdout


@pytest.mark.parametrize("value", [None, True, False, 0, 1, "0.7", 0.1, 0.2, 0.3, float("nan"), float("inf")])
def test_invalid_repair_temperature_fails_before_model_runtime(job_file, monkeypatch, value):
    job = json.loads(job_file.read_text())
    job["runtime"]["repair_temperature"] = value
    write(job_file, job)
    monkeypatch.setattr(worker.frozen, "load_backend", lambda: pytest.fail("model runtime should not load"))
    with pytest.raises(worker.IntegrityError, match="Repair temperature"):
        worker.run(job_file, execute_models=True)


def test_missing_repair_temperature_fails_before_model_runtime(job_file, monkeypatch):
    job = json.loads(job_file.read_text())
    del job["runtime"]["repair_temperature"]
    write(job_file, job)
    monkeypatch.setattr(worker.frozen, "load_backend", lambda: pytest.fail("model runtime should not load"))
    with pytest.raises(worker.IntegrityError, match="runtime fields"):
        worker.run(job_file, execute_models=True)


@pytest.mark.parametrize("field,value", [("experiment", "wrong"), ("schema", "post-c3-job-v1"),
    ("processing_scope", "all_saved_final_proofs"), ("source_arm", "B"),
    ("pipeline_config", {"neighbor_blocks": 2, "max_audit_passes": 1, "max_resolve_passes": 1})])
def test_wrong_experiment_or_scope_rejected_before_loading_models(job_file, monkeypatch, field, value):
    job = json.loads(job_file.read_text())
    job[field] = value
    write(job_file, job)
    monkeypatch.setattr(worker.frozen, "load_backend", lambda: pytest.fail("model runtime should not load"))
    with pytest.raises(worker.IntegrityError):
        worker.run(job_file, execute_models=True)


def test_non_raw_or_changed_source_rejected(job_file):
    job = json.loads(job_file.read_text())
    Path(job["candidates"][0]["proof_path"]).write_text("Changed proof")
    with pytest.raises(ValueError):
        worker.validate_job(job_file)


def test_later_checkpoint_cannot_be_mislabeled_as_raw(job_file):
    job = json.loads(job_file.read_text())
    job["candidates"][0]["selected_stage"] = "refinement_1"
    manifest = Path(job["input_manifest_path"])
    bank = json.loads(manifest.read_text())
    bank["problems"][0]["candidates"] = job["candidates"]
    write(manifest, bank)
    job["input_manifest_sha256"] = worker.frozen.digest(manifest.read_bytes())
    write(job_file, job)
    with pytest.raises(ValueError, match="Only raw"):
        worker.validate_job(job_file)


def test_uncertain_segmentation_fails_dry_preflight_without_inference(job_file):
    job = json.loads(job_file.read_text())
    job["dry_run"] = True
    candidate = job["candidates"][0]
    data = b"An unmatched \\[ mathematical expression."
    Path(candidate["proof_path"]).write_bytes(data)
    candidate["proof_file_sha256"] = worker.frozen.digest(data)
    candidate["proof_sha256"] = worker.frozen.text_digest(data)
    manifest = Path(job["input_manifest_path"])
    bank = json.loads(manifest.read_text())
    bank["problems"][0]["candidates"] = job["candidates"]
    write(manifest, bank)
    job["input_manifest_sha256"] = worker.frozen.digest(manifest.read_bytes())
    write(job_file, job)
    result = subprocess.run([sys.executable, "-B", "-m", "harnesses.block_local_completion.worker", "--job", str(job_file)],
                            cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, timeout=20)
    assert result.returncode == 1 and "segmentation failed" in result.stderr
    summary = json.loads((Path(job["output_dir"]) / "summary.json").read_text())
    assert summary["state"] == "failed"
    assert summary["lanes"][0]["failure"]["stage"] == "segmentation"
    assert Path(summary["lanes"][0]["proof_path"]).read_bytes() == data


def test_dry_run_has_no_model_calls_and_preserves_all_raw_bytes(job_file, monkeypatch):
    job = json.loads(job_file.read_text())
    job["dry_run"] = True
    write(job_file, job)
    script = """
from pathlib import Path
import sys
from harnesses.block_local_completion import worker
backend=worker.frozen.load_backend()
def forbidden(**kwargs): raise AssertionError('dry run attempted inference')
backend.v263.parent._budget_forcing._ORIGINAL=forbidden
result=worker.run(Path(sys.argv[1]))
assert result['state']=='preflight_passed' and result['model_calls']==0
assert all(l['operation']=='preflight_only' and not l['changed'] for l in result['lanes'])
print('DRY_OK')
"""
    result = subprocess.run([sys.executable, "-B", "-c", script, str(job_file)], capture_output=True, text=True,
                            cwd=Path(__file__).resolve().parents[1], timeout=20)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "DRY_OK" in result.stdout


def test_patch_parser_never_serializes_candidate_bytes_into_runtime_metadata():
    data = b"First.\n\nGap.\n\nLast."
    bank = blocks.build_blocks(data)
    issues = blocks.parse_issues('<ISSUES>\n<ISSUE id="I1" blocks="B0002">\nGap\n</ISSUE>\n</ISSUES>', bank)
    parsed = worker._patch_parser({"data": data, "bank": bank}, issues)(
        '<PATCHES>\n<REPLACE blocks="B0002" issues="I1">\nRepaired.\n</REPLACE>\n</PATCHES>')
    assert parsed["valid"] and "proof_bytes" not in parsed
    json.dumps(parsed)
