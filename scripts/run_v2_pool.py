#!/usr/bin/env python3
"""Run retained v2 grades in a replenished pool without waiting for chunk tails."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import random
import signal
import subprocess
import sys
import time

import run_v2_pairs as pairs
import v2_response_recovery as recovery

original = pairs.original
ROOT = original.ROOT


def process_identity(pid):
    try:
        stat = Path(f'/proc/{pid}/stat').read_text().rsplit(') ', 1)[1].split()
        return None if stat[0] == 'Z' else stat[19]
    except FileNotFoundError:
        return None


def process_is_live(pid, identity):
    return identity is not None and process_identity(pid) == identity


def save_jobs(path, jobs):
    original.write(path,[dict(pid=j['pid'],process_identity=j['identity'],
                              output=str(j['output'].relative_to(ROOT)),slots=j['slots'],
                              bindings=str(j['output'].with_name(j['output'].name+'.bindings.json').relative_to(ROOT)))
                        for j in jobs])


def reserved_keys(jobs):
    return {(item['unit_id'], item['repeat']) for job in jobs for item in job['bindings']}


def choose_tasks(units, found, jobs, attempts, workers, retries):
    available = max(0, workers - sum(job['slots'] for job in jobs))
    reserved = reserved_keys(jobs)
    return [(u, repeat) for u in units for repeat in [1, 2]
            if (u['unit_id'], repeat) not in found and (u['unit_id'], repeat) not in reserved
            and attempts.get(u['unit_id']+f':{repeat}', 0) < retries][:available]


def publish(study, directory, found, jobs, workers, attempts, state=None, error=None):
    value = pairs.publish(study, directory, found, state=state,
                          active='rolling_pool' if jobs else None, attempts=attempts, error=error)
    value['concurrent_grader_limit'] = workers
    value['active_jobs'] = [dict(output=str(job['output'].relative_to(ROOT)), slots=job['slots'],
                                 inherited=job['process'] is None,
                                 pending=sum((b['unit_id'], b['repeat']) not in found for b in job['bindings']))
                            for job in jobs]
    original.write(directory/'results.json', value)
    print(json.dumps({k:value[k] for k in ['updated_at','state','completed_grades','planned_grades',
                                          'concurrent_grader_limit','active_jobs']}), flush=True)
    return value


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--study',type=Path,required=True)
    parser.add_argument('--workers',type=int,default=12)
    parser.add_argument('--execute-models',action='store_true')
    parser.add_argument('--retry-rounds',type=int,default=3)
    args=parser.parse_args()
    assert args.workers>0 and args.retry_rounds>0
    directory=args.study.resolve();study=pairs.load_plan(directory);work=directory/'work'
    runner=pairs.prepare_study_runner()
    original.first_valid_response=recovery.first_valid_response
    failures_path=work/'response_export_failures.json'
    failures=original.read(failures_path) if failures_path.exists() else {}
    def export(bindings, output):
        recovery.export_cases(original,study,bindings,output,runner,failures)
        original.write(failures_path,failures)
    old=original.read(directory/'execution_config_pairs.json')
    for name,expected in old['source_hashes'].items():
        assert original.digest(ROOT/name)==expected,f'Frozen source changed: {name}'
    for unit in study['units']:
        for key in ['proof','reference']:
            assert hashlib.sha256((ROOT/unit[key]).read_text().strip().encode()).hexdigest()==unit[key+'_sha256']
        problem=original.read(ROOT/unit['problem'])
        statement=(problem.get('claim') or problem.get('problem') or problem.get('statement')).strip()
        assert hashlib.sha256(statement.encode()).hexdigest()==unit['problem_sha256']
    launcher=Path.home()/'.codex/skills/strict-gold-informed-olympiad-scorer/scripts/score.py'
    assert original.digest(launcher)=='7a4cfb1c678717d045889eb58fd0714a9932c8a2f29902ed210a363a15d8a12a'
    config=dict(schema='workshop-v2-rolling-pool-v1',workers=args.workers,repeats=2,
                scheduling='One isolated assessment per job; replenish free slots across benchmarks.',
                model=study['model'],reasoning_effort=study['reasoning_effort'],policy_sha256=study['policy_sha256'],
                source_hashes={**old['source_hashes'],
                               **{name:original.digest(ROOT/name) for name in ['scripts/run_v2_pool.py','scripts/v2_response_recovery.py']}})
    config_path=directory/'execution_config_pool.json'
    if config_path.exists():assert original.read(config_path)==config
    elif args.execute_models:original.write(config_path,config)
    with (work/'coordinator.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        for benchmark in sorted({u['benchmark'] for u in study['units']}):
            private=ROOT/f"benchmarks/{benchmark}/results/{study['run_id']}/grading/work"
            for binding in sorted(private.glob('*.bindings.json')):
                export(pairs.retained_bindings(original.read(binding)),
                       private/binding.name.removesuffix('.bindings.json'))
        found=pairs.collect(study)
        attempts_path=work/'pair_attempts.json'
        attempts=original.read(attempts_path) if attempts_path.exists() else {}
        jobs=[]
        inherited_path=work/'inherited_batches.json'
        if inherited_path.exists():
            for inherited in original.read(inherited_path):
                if not process_is_live(inherited['pid'],inherited['process_identity']):continue
                output=ROOT/inherited['output']
                bindings=pairs.retained_bindings(original.read(ROOT/inherited['bindings']))
                jobs.append(dict(output=output,bindings=bindings,slots=inherited['slots'],process=None,
                                 pid=inherited['pid'],identity=inherited['process_identity'],log=None))
        if not args.execute_models:
            publish(study,directory,found,jobs,args.workers,attempts)
            return 0
        assert sum(job['slots'] for job in jobs)<=args.workers
        units=list(study['units']);random.Random(20260918).shuffle(units)
        try:
            while True:
                assert all(original.digest(ROOT/name)==h for name,h in config['source_hashes'].items())
                for job in list(jobs):
                    export(job['bindings'],job['output'])
                    quota=pairs.usage_limit_error(job['output'])
                    if quota:
                        for running in jobs:
                            try:os.killpg(running['pid'],signal.SIGTERM)
                            except ProcessLookupError:pass
                        for running in jobs:
                            if running['process'] is not None:running['process'].wait()
                            export(running['bindings'],running['output'])
                        found=pairs.collect(study)
                        publish(study,directory,found,[],args.workers,attempts,state='blocked_usage_limit',error=quota)
                        return 3
                    alive=(job['process'].poll() is None if job['process'] is not None
                           else process_is_live(job['pid'],job['identity']))
                    if not alive:
                        export(job['bindings'],job['output'])
                        if job['log'] is not None:job['log'].close()
                        jobs.remove(job)
                found=pairs.collect(study)
                if len(found)==study['planned_grades'] and not jobs:
                    publish(study,directory,found,[],args.workers,attempts)
                    return 0
                chosen=choose_tasks(units,found,jobs,attempts,args.workers,args.retry_rounds)
                for unit,repeat in chosen:
                    private=original.base_for(study,unit)/'grading/work'
                    number=len(list(private.glob('pool_job_*.tasks.json')))+1
                    name=f'pool_job_{number:05d}';output=private/name
                    cid='u'+unit['unit_id']+f'_g{repeat}'
                    bindings=[dict(unit_id=unit['unit_id'],repeat=repeat,candidate_id=cid)]
                    task=dict(problem_number=unit['problem_number'],problem_id=unit['problem_id'],candidate_id=cid,
                              **{k+'_path':str(ROOT/unit[k]) for k in ['problem','reference','proof']},
                              expected_hashes={k:unit[k] for k in ['problem_sha256','reference_sha256','proof_sha256']})
                    manifest=private/(name+'.tasks.json')
                    original.write(manifest,dict(schema='gold-informed-generic-proof-task-manifest-v1',tasks=[task]))
                    original.write(private/(name+'.bindings.json'),bindings)
                    key=unit['unit_id']+f':{repeat}';attempts[key]=attempts.get(key,0)+1
                    original.write(attempts_path,attempts)
                    log=(private/(name+'.log')).open('w')
                    command=[sys.executable,'-B',str(launcher),'--generic-task-manifest',str(manifest),
                             '--output-dir',str(output),'--workers','1','--reasoning-effort',study['reasoning_effort']]
                    process=subprocess.Popen(command,cwd=private/'launcher',stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                    jobs.append(dict(output=output,bindings=bindings,slots=1,process=process,pid=process.pid,
                                     identity=process_identity(process.pid),log=log))
                    save_jobs(inherited_path,jobs)
                if not jobs:
                    publish(study,directory,found,[],args.workers,attempts,state='incomplete_after_retries')
                    return 2
                publish(study,directory,found,jobs,args.workers,attempts)
                # Persist all live jobs so a subsequent operator can adopt them without duplicate calls.
                save_jobs(inherited_path,jobs)
                time.sleep(10)
        except BaseException:
            # Let isolated grader processes finish; inherited_batches.json binds a safe recovery.
            save_jobs(inherited_path,jobs)
            publish(study,directory,pairs.collect(study),jobs,args.workers,attempts,state='scheduler_interrupted')
            raise


if __name__=='__main__':
    raise SystemExit(main())
