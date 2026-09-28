"""Run the pinned P2 trial, then publish and strictly grade an accepted rewrite."""
from datetime import datetime, timezone
from pathlib import Path
import fcntl
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import time
import grade_imobench

HERE=Path(__file__).resolve().parent
CONFIG=json.loads((HERE/'selection.json').read_text())
ROOT=Path(CONFIG['workspace'])
EXPERIMENT=Path(CONFIG['experiment'])
NATIVE=EXPERIMENT/'generation/run'
SKILL=Path('/home/user/.codex/skills/strict-gold-informed-olympiad-scorer')
ACTIVE=None


def now():return datetime.now(timezone.utc).isoformat()
def read(path):return json.loads(Path(path).read_text())
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def text_sha(path):return hashlib.sha256(Path(path).read_text().strip().encode()).hexdigest()
def write(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(data,indent=2)+'\n');tmp.replace(path)


def command(argv,log,env=None):
    global ACTIVE
    with log.open('w') as stream:
        ACTIVE=subprocess.Popen(argv,cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
        code=ACTIVE.wait();ACTIVE=None
    return code


def forward(number,frame):
    if ACTIVE is not None and ACTIVE.poll() is None:os.killpg(ACTIVE.pid,number)


def snapshot(source,checkpoint):
    target=EXPERIMENT/'proofs/imo2026_p2/t07_r02'/(checkpoint+'.md')
    target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    return {'path':str(target.relative_to(EXPERIMENT)),'source':str(source),
        'checkpoint':checkpoint,'sha256':sha(target),'canonical_text_sha256':text_sha(target)}


def grade(proofrow,summary):
    proof=EXPERIMENT/proofrow['path'];grading=EXPERIMENT/'grading'
    work=grading/'work/strict_tool_rewrite';work.mkdir(parents=True,exist_ok=False)
    scratch=work/'tmp';scratch.mkdir()
    config=grading/'strict_config';config.mkdir()
    inputs={}
    for name,source in {'SKILL.md':SKILL/'SKILL.md','rubric.md':SKILL/'references/rubric.md',
        'score.py':SKILL/'scripts/score.py','runner.py':ROOT/'scripts/run_v097_p145_gold_informed_calibrated_codex_scores_20260827.py',
        'contract.py':ROOT/'scripts/external_olympiad_scorer/contract.py',
        'grade_schema.json':ROOT/'scripts/external_olympiad_scorer/grade_schema.json'}.items():
        shutil.copyfile(source,config/name);inputs[name]={'path':str(source),'sha256':sha(source)}
    argv=[CONFIG['grader_python'],'-B',str(SKILL/'scripts/score.py'),'--proof-task',f'imo2026_p2:t07_r02={proof}',
        '--problem-root',str(ROOT/'benchmarks/imo2026/problems'),
        '--reference-root',str(ROOT/'math_harness_references/imo2026_mechmath_20260817'),
        '--output-dir',str(work/'scores'),'--workers','1']
    env=os.environ.copy()
    for key in ('PYTHONPATH','PYTHONHOME','OPENAI_BASE_URL','OPENAI_API_BASE','GEMMA_ENDPOINT','QWEN_ENDPOINT'):env.pop(key,None)
    env.update(CUDA_VISIBLE_DEVICES='',NVIDIA_VISIBLE_DEVICES='none',PYTHONNOUSERSITE='1',
        PYTHONDONTWRITEBYTECODE='1',TMPDIR=str(scratch))
    write(grading/'launch.json',{'command':argv,'cwd':str(ROOT),'started_at':now(),
        'proof_sha256':sha(proof),'skill_inputs':inputs,'isolation':'one proof, problem, and gold reference; no pipeline reviews or scores'})
    summary['grading_status']='running';write(EXPERIMENT/'reports/run_summary.json',summary)
    write(HERE/'status.json',{'state':'grading','updated_at':now(),'run_id':CONFIG['run_id']})
    started=time.monotonic();code=command(argv,grading/'console.log',env)
    write(grading/'completion.json',{'returncode':code,'completed_at':now(),'wall_seconds':time.monotonic()-started})
    assert code==0,'Strict scorer failed; inspect grading/console.log'
    case=work/'scores/p2/t07_r02';result=read(case/'summary.json');manifest=read(case/'manifest.json')
    assert result['state']=='completed' and result['policy_mode']=='strict'
    assert result['grader']=='gpt-5.6-sol' and result['reasoning_effort']=='xhigh'
    assert result['proof_sha256']==proofrow['canonical_text_sha256']==text_sha(proof)
    assert proofrow['sha256']==sha(proof)
    assert manifest['isolated_candidate_call'] and not manifest['pipeline_reviews_supplied']
    dest=EXPERIMENT/'grades/imo2026_p2/t07_r02/tool_rewrite/strict';dest.mkdir(parents=True)
    for name in ('summary.json','manifest.json','codex.jsonl'):
        if (case/name).exists():shutil.copyfile(case/name,dest/name)
    value=result['grade']
    summary.update(grading_status='completed',external_grade=value,grader=result['grader'],
        reasoning_effort=result['reasoning_effort'],policy_sha256=result['policy_sha256'],failed_grader_calls=result['errors'])
    write(EXPERIMENT/'reports/strict_score.json',result)
    (EXPERIMENT/'reports/strict_score.md').write_text(
        f"# P2 V356 strict score\n\n**{value['score']}/7 — {value['verdict']}**\n\n{value['summary']}\n\n"
        f"First issue: {value['first_issue']}\n\nModel: {result['grader']}; effort: {result['reasoning_effort']}. "
        f"Failed calls: {len(result['errors'])}.\n\nPolicy SHA-256: `{result['policy_sha256']}`.\n")
    proofrow['strict_grade']=str((dest/'summary.json').relative_to(EXPERIMENT))


def verify(native):
    manifest=read(native/'manifest.json')
    assert manifest['harness_revision']=='0.3.356+v349-discrete-consolidation.1'
    assert manifest['gold_inputs'] is False and manifest['generation_reference_reads'] is False
    assert manifest['budget_forcing'] and not manifest['associated_documents']
    resume=manifest['resume'];assert resume['certificate_replayed'] and resume['source_selection_reused']
    for key in ('new_detection_calls','new_matcher_calls','new_formalization_calls','new_semantic_audit_calls','new_certificate_searches'):
        assert resume[key]==0
    assert resume['prior_external_scores_supplied'] is False
    assert sha(native/'input/source_proof.md')==CONFIG['source_proof_file_sha256']
    for name,digest in manifest['input_artifacts'].items():assert sha(native/name)==digest
    expected=Path(CONFIG['batch'])/'compatibility'/CONFIG['case']
    assert (native/'export/lemma.md').read_text().strip()==(expected/'lemma.md').read_text().strip()
    assert (native/'export/appendix.md').read_text().strip()==(expected/'appendix.md').read_text().strip()
    return manifest


def publish():
    completion=read(EXPERIMENT/'generation/completion.json');assert completion['worker_exited']
    manifest=verify(NATIVE);result=read(NATIVE/'result.json')
    assert read(EXPERIMENT/'experiment.json')['tool_harness']['release_sha256']==CONFIG['tool_release_sha256']
    write(HERE/'status.json',{'state':'publishing_and_grading','updated_at':now()})
    if CONFIG['benchmark']=='imo-proofbench/basic':
        summary=grade_imobench.publish_and_grade(CONFIG,{'workspace':str(ROOT)})
    else:
        summary={'run_id':CONFIG['run_id'],'problem_id':CONFIG['problem_id'],'candidate':CONFIG['source_candidate'],
            'outcome':result.get('outcome'),'proof_audit_passed':result.get('proof_audit_passed',False),
            'returncode':completion['returncode'],'wall_seconds':completion['wall_seconds'],
            'external_grade':None,'grading_status':'no_accepted_rewrite','error':result.get('error')}
        artifact={'schema':'tool-harness-result-artifact-manifest-v1','run_id':CONFIG['run_id'],
            'harness_revision':manifest['harness_revision'],'release_sha256':CONFIG['tool_release_sha256'],
            'proofs':[snapshot(NATIVE/'input/source_proof.md','submitted_R1-C3')]}
        write(EXPERIMENT/'manifest.json',artifact);write(EXPERIMENT/'reports/run_summary.json',summary)
        if result.get('proof_audit_passed'):
            proof=snapshot(NATIVE/'rewritten_proof.md','tool_rewrite')
            assert proof['canonical_text_sha256']==result['rewritten_proof_sha256']
            artifact['proofs'].append(proof);write(EXPERIMENT/'manifest.json',artifact)
            grade(proof,summary)
        write(EXPERIMENT/'manifest.json',artifact)
    summary.update(version='0.3.356',baseline_score=CONFIG['baseline_score'],previous_tool_score=CONFIG['previous_tool_score'],
        source_checkpoint=CONFIG['source_checkpoint'],candidate=CONFIG['source_candidate'],resume=manifest['resume'])
    if result.get('proof_audit_passed'):
        old=Path(CONFIG['previous_experiment'])/'proofs'/CONFIG['problem_id']/CONFIG['source_candidate']/'tool_rewrite.md'
        new=NATIVE/'rewritten_proof.md'
        summary['proof_comparison']={'new_file_sha256':sha(new),'new_words':len(new.read_text().split())}
        if old.exists():summary['proof_comparison'].update(old_file_sha256=sha(old),old_words=len(old.read_text().split()))
    write(EXPERIMENT/'reports/run_summary.json',summary)
    subprocess.run([sys.executable,'-B',str(ROOT/'benchmarks/run_experiment.py'),'--benchmark',CONFIG['benchmark'],
        '--run-id',CONFIG['run_id'],'--index-only'],cwd=ROOT,check=True)
    return summary


def main():
    lock=(HERE/'.trial.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    for number in (signal.SIGTERM,signal.SIGINT):signal.signal(number,forward)
    try:
        assert read(Path(CONFIG['batch'])/'compatibility.json')['passed']
        write(HERE/'status.json',{'state':'preflight','started_at':now()})
        assert command(CONFIG['preflight_command'],HERE/'preflight.log')==0,'Preflight failed'
        manifest=verify(Path(CONFIG['preflight_experiment'])/'generation/run')
        write(HERE/'preflight_verified.json',{'passed':True,'resume':manifest['resume']})
        assert not EXPERIMENT.exists()
        write(HERE/'status.json',{'state':'generation','started_at':now(),'run_id':CONFIG['run_id']})
        code=command(CONFIG['command'],HERE/'launcher.log')
        assert (EXPERIMENT/'generation/completion.json').exists(),f'Launcher exited {code} without completion record'
        summary=publish()
        write(HERE/'status.json',{'state':'completed','completed_at':now(),'run_id':CONFIG['run_id'],
            'outcome':summary['outcome'],'grade':summary['external_grade'],'report':str(EXPERIMENT/'reports/run_summary.json')})
    except Exception as error:
        write(HERE/'status.json',{'state':'failed','updated_at':now(),'run_id':CONFIG['run_id'],
            'error':f'{type(error).__name__}: {error}'})
        raise


if __name__=='__main__':main()
