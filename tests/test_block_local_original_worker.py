"""Original-prompt control with real frozen runtime/BF and offline inference."""
import json
from pathlib import Path
import subprocess
import sys

import pytest

from harnesses.block_local_completion import original_worker as worker


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
        data = (f"  Header π {cid}.\r\n\r\nMissing argument.\r\n\r\nTail unchanged.\r\n ").encode()
        path = write(root / "inputs/imo2026_p2" / (cid + ".md"), data)
        candidates.append({"candidate_id": cid, "proof_path": str(path), "selected_stage": "raw",
            "proof_file_sha256": worker.frozen.digest(data), "proof_sha256": worker.frozen.text_digest(data)})
    manifest = write(root / "inputs/manifest.json", {"schema": "block-local-inputs-v1", "source_arm": "raw",
        "release_sha256": worker.frozen.digest((worker.frozen.RELEASE / "release.json").read_bytes()),
        "source_hashes": {}, "problems": [{"problem": problem, "candidates": candidates}]})
    return write(root / "job.json", {"schema": "block-local-job-v1", "experiment": worker.common.EXPERIMENT,
        "strategy": "original", "processing_scope": "all_saved_raw_proofs", "pipeline_config": worker.PIPELINE_CONFIG,
        "source_arm": "raw", "dry_run": False, "output_dir": str(root / "output"),
        "problem": problem, "candidates": candidates,
        "runtime": {"gemma_endpoint": "http://127.0.0.1:8030/v1", "qwen_endpoint": "http://127.0.0.1:8027/v1",
                    "model_timeout_sec": 14400, "workers": 4, "seed_namespace": "block-local-raw:0:imo2026_p2",
                    "repair_temperature": 0.4},
        "input_manifest_path": str(manifest), "input_manifest_sha256": worker.frozen.digest(manifest.read_bytes())})


SCRIPT = r'''
from dataclasses import asdict
import json
from pathlib import Path
import sys
import threading
from harnesses.block_local_completion import original_worker as worker

job_path, mode = Path(sys.argv[1]), sys.argv[2]
job = json.loads(job_path.read_text())
source = {c['candidate_id']: Path(c['proof_path']).read_bytes() for c in job['candidates']}
real_load = worker.frozen.load_release
servers = []
def load():
    launcher, manifest, profile = real_load()
    def server(endpoint, expected):
        servers.append(expected['model'])
        assert expected['model']=='google/gemma-4-31B-it'
        return {'offline_test':True, 'model':expected['model']}
    launcher.server_settings = server
    return launcher, manifest, profile
worker.frozen.load_release = load
backend = worker.frozen.load_backend()
frontend = backend.v108.v097
lazy = sys.modules[frontend.run_lazy_check.__module__]
expansion = sys.modules[frontend.run_lazy_resolve.__module__]
bf = backend.v263.parent._budget_forcing
original_symbols = frontend.run_lazy_check, frontend.run_lazy_resolve, lazy.lazy_phrasing, bf._continue_primary, bf.continuation_instruction
calls, lock = [], threading.Lock()
all_lanes = set(worker.CANDIDATES)
accepted = {'lazy_check':set(), 'expansion':set()}
arrived = {(phase,forced):set() for phase in accepted for forced in (False,True)}
barriers = {key:threading.Barrier(4,timeout=5) for key in arrived}
real_batch = worker.legacy.run_batch
batch_index = 0
def synchronized_batch(ids, task, on_result, *, policy_error):
    global batch_index
    phase = ('lazy_check','expansion')[batch_index]
    batch_index += 1
    assert set(ids)==all_lanes
    def done(cid,value):
        on_result(cid,value)
        with lock: accepted[phase].add(cid)
    real_batch(ids,task,done,policy_error=policy_error)
    assert accepted[phase]==all_lanes
if mode=='batch_all': worker.legacy.run_batch=synchronized_batch
report = 'The missing implication requires an explicit derivation.'
def envelope(cid):
    return ('BEGIN_REPAIR_AUDIT\nCONCLUSION_ACTION: PRESERVE\nORIGINAL_CLASSIFICATION: implication holds\n'
        'REPAIRED_CLASSIFICATION: implication holds\nCHANGE_BASIS: NONE\nCHANGE_JUSTIFICATION: NONE\nEND_REPAIR_AUDIT\n'
        'BEGIN_REPAIRED_PROOF\nA complete repaired proof for '+cid+'.\nEND_REPAIRED_PROOF')
def physical(**kwargs):
    root, stage = Path(kwargs['output_dir']), kwargs['stage']
    root.mkdir(parents=True,exist_ok=True)
    cid = next(part for part in root.parts if part in worker.CANDIDATES)
    assert stage.startswith(('lazy_check_attempt','lazy_in_place_resolve_attempt')),stage
    phase = 'lazy_check' if stage.startswith('lazy_check') else 'expansion'
    forced = bool(kwargs.get('continuation_instruction'))
    config = asdict(kwargs['config'])
    assert kwargs['model']=='google/gemma-4-31B-it'
    assert config['temperature']==(0.1 if phase=='lazy_check' else 0.4)
    assert config['max_tokens']==(65536 if phase=='expansion' else 32768 if forced else 16384)
    assert (config['top_p'],config['top_k'],config['timeout_seconds'])==(0.95,64,14400)
    rowproof = source[cid].decode().replace('\r\n','\n').strip()
    expected_system = (lazy.lazy_phrasing(rowproof) if phase=='lazy_check' else
        expansion.lazy_in_place_expansion_prompt(problem=job['problem']['claim'],current_proof=rowproof,local_gaps=report))
    assert kwargs['prompt']==expected_system
    assert kwargs['user_prompt']==(worker.legacy.LAZY_USER if phase=='lazy_check' else worker.legacy.EXPANSION_USER)
    candidate_seed = worker.legacy.seed_for(job['runtime']['seed_namespace'],cid)
    if 'attempt2' not in stage:
        assert config['seed']==worker.legacy.stage_seed(candidate_seed,'lazy_check' if phase=='lazy_check' else 'lazy_in_place_resolve')
    if mode=='batch_all':
        with lock:
            if phase=='expansion': assert accepted['lazy_check']==all_lanes
            assert cid not in arrived[phase,forced]
            arrived[phase,forced].add(cid)
        barriers[phase,forced].wait()
    if forced:
        assert kwargs['continuation_instruction']==bf.TEXT_CONTINUATION
        assert '[Preserved reasoning]\nPRIMARY REASONING' in kwargs['prior_generation']
        assert '[Preserved response]\nPRIMARY ANSWER' in kwargs['prior_generation']
        if phase=='lazy_check':
            text = report if mode=='batch_all' or (mode!='no_issues' and cid=='t10_r01') else 'NO_ISSUES'
        else:
            text = 'Malformed full proof without repair envelope.' if mode=='malformed' else envelope(cid)
    else:
        text = 'PRIMARY ANSWER'
    reasoning = 'FORCED REASONING' if forced else 'PRIMARY REASONING'
    metadata = {'stage':stage,'model':kwargs['model'],'config':config,'finish_reason':'stop'}
    raw = {'choices':[{'finish_reason':'stop','message':{'content':text,'reasoning_content':reasoning}}]}
    for suffix,data in (('.raw_response.json',json.dumps(raw)),('.metadata.json',json.dumps(metadata)),
        ('.prompt.txt',kwargs['prompt']),('.user_prompt.txt',kwargs['user_prompt']),('.reasoning.txt',reasoning)):
        (root/(stage+suffix)).write_text(data)
    with lock: calls.append({'phase':phase,'forced':forced,'cid':cid,'config':config})
    return {'text':text,'reasoning':reasoning,'metadata':metadata}
bf._ORIGINAL=physical
result = worker.run(job_path,execute_models=True)
assert (frontend.run_lazy_check,frontend.run_lazy_resolve,lazy.lazy_phrasing,bf._continue_primary,bf.continuation_instruction)==original_symbols
assert servers==['google/gemma-4-31B-it']
assert result['strategy']=='original' and result['pipeline_config']=={'neighbor_blocks':0,'max_audit_passes':0,'max_resolve_passes':0}
assert result['runtime']['repair_temperature']==0.4
assert result['state']==('completed_with_fallbacks' if mode=='malformed' else 'completed')
for lane in result['lanes']:
    cid=lane['candidate_id']
    final=Path(lane['proof_path']).read_bytes()
    provenance=lane['original_provenance']
    for pathkey,hashkey in (('source_path','source_file_sha256'),('lazy_report_path','lazy_report_file_sha256')):
        assert worker.frozen.digest(Path(provenance[pathkey]).read_bytes())==provenance[hashkey]
    assert Path(provenance['source_path']).read_bytes()==source[cid]
    assert 'post_expansion' not in lane and 'block_patch' not in lane
    should_expand = mode=='batch_all' or (mode=='accept' and cid=='t10_r01')
    if should_expand:
        assert lane['operation']=='expanded' and lane['local_result']=='original_expanded'
        assert final==('A complete repaired proof for '+cid+'.\n').encode()
        assert Path(provenance['parsed_proof_path']).read_bytes()==final
        rawtext=Path(provenance['expansion_response_path']).read_text()
        assert rawtext==envelope(cid)
        assert worker.frozen.digest(rawtext.encode())==provenance['expansion_response_file_sha256']
        assert worker.frozen.digest(final)==provenance['parsed_proof_file_sha256']
        assert lane['native_expansion']['lazy_resolve_temperature']==0.4
        assert lane['native_expansion']['frozen_declared_lazy_resolve_temperature']==0.7
        assert json.loads((Path(job['output_dir'])/'run/candidates'/cid/'result.json').read_text())['lazy_resolve_temperature']==0.7
    else:
        assert final==source[cid] and lane['adopted_from']=='original'
        assert lane['operation']==('failed' if mode=='malformed' and cid=='t10_r01' else 'no_issues')
    assert abs(sum(lane['phase_elapsed_seconds'].values())-lane['elapsed_seconds'])<0.00001
for candidate in job['candidates']:
    assert Path(candidate['proof_path']).read_bytes()==source[candidate['candidate_id']]
if mode=='batch_all':
    assert batch_index==2 and len(calls)==16
    assert all(ids==all_lanes for ids in arrived.values())
elif mode=='no_issues': assert len(calls)==8 and all(c['phase']=='lazy_check' for c in calls)
elif mode=='accept': assert len(calls)==10
assert not result['grading_performed'] and not result['mathematically_verified']
print('ORIGINAL_OFFLINE_OK '+mode)
'''


@pytest.mark.parametrize("mode", ["accept", "no_issues", "malformed", "batch_all"])
def test_original_prompts_bf_and_temperature_only_control(job_file, mode):
    result = subprocess.run([sys.executable, "-B", "-c", SCRIPT, str(job_file), mode],
        cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, timeout=40)
    assert result.returncode == 0, result.stdout + "\n" + result.stderr
    assert "ORIGINAL_OFFLINE_OK " + mode in result.stdout


@pytest.mark.parametrize("change", ["strategy", "temperature", "pipeline"])
def test_wrong_control_configuration_fails_before_runtime(job_file, monkeypatch, change):
    job = json.loads(job_file.read_text())
    if change == "strategy": job["strategy"] = "block"
    if change == "temperature": job["runtime"]["repair_temperature"] = 0.7
    if change == "pipeline": job["pipeline_config"]["max_audit_passes"] = 1
    write(job_file, job)
    monkeypatch.setattr(worker.frozen, "load_backend", lambda: pytest.fail("must fail before runtime loads"))
    with pytest.raises(worker.IntegrityError):
        worker.run(job_file, execute_models=True)


def test_temperature_adapter_restores_instance_on_error():
    class Runtime:
        def gemma_call(self, **kwargs):
            assert kwargs["temperature"] == 0.4
            raise RuntimeError("request failed")
    runtime = Runtime()
    with pytest.raises(RuntimeError, match="request failed"):
        with worker.expansion_temperature(runtime, {"unchanged system"}):
            runtime.gemma_call(name="lazy_in_place_resolve", system_prompt="unchanged system",
                user_prompt=worker.legacy.EXPANSION_USER, temperature=0.7)
    assert "gemma_call" not in runtime.__dict__


def test_original_dry_run_preserves_bytes_without_inference(job_file):
    job = json.loads(job_file.read_text())
    job["dry_run"] = True
    write(job_file, job)
    script = '''
import sys
from pathlib import Path
from harnesses.block_local_completion import original_worker as worker
backend=worker.frozen.load_backend()
def forbidden(**kwargs): raise AssertionError('dry run attempted inference')
backend.v263.parent._budget_forcing._ORIGINAL=forbidden
result=worker.run(Path(sys.argv[1]))
assert result['state']=='preflight_passed' and result['model_calls']==0
assert all(l['operation']=='preflight_only' and not l['changed'] for l in result['lanes'])
print('ORIGINAL_DRY_OK')
'''
    result = subprocess.run([sys.executable, "-B", "-c", script, str(job_file)],
        cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "ORIGINAL_DRY_OK" in result.stdout
