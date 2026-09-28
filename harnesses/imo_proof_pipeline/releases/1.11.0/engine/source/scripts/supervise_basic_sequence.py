#!/usr/bin/env python3
"""Finish a frozen Basic tail queue, then its separately seeded rerun queue."""
from __future__ import annotations

import argparse
import fcntl
import json
from pathlib import Path
import subprocess
import sys
import time

REPO=Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0,str(REPO))
from scripts import run_v263_v290 as runner

FINISHED={'completed','completed_with_failed_lanes'}


def read(path):
    return runner.read(path) if path.is_file() else {}


def run_stage(root, queue, command, stage, *, start=False):
    journal=root/(stage+'_supervisor')
    journal.mkdir(exist_ok=True)
    launched=False
    while True:
        state=read(queue/'status.json')
        runner.write(root/'status.json',{'state':'running','stage':stage,'active_run':str(queue),
            'problem_id':state.get('problem_id'),'queue_state':state.get('state')})
        if state.get('state') in FINISHED:
            return
        if state.get('state') in {'stopped','stopped_by_user'}:
            raise RuntimeError('Queue was stopped; supervisor will not restart it')
        launch_command=None
        if start and not launched and state.get('state')=='pending':
            launch_command=command
        elif state.get('state')=='paused_on_failure':
            manifest=read(queue/'manifest.json')
            failed=[]
            for row in manifest['problems']:
                problem_root=queue/'problems'/row['problem_id']
                summary=read(problem_root/'summary.json')
                if summary.get('state')=='failed_closed':
                    runner.validate_failed_portfolio(problem_root,row['problem_id'])
                    failed.append(row['problem_id'])
            if state.get('problem_id') not in failed:
                raise RuntimeError('Paused queue lacks a validated exhausted portfolio; inspection required')
            launch_command=list(command)
            if '--resume' not in launch_command:
                launch_command.append('--resume')
            for problem_id in failed:
                launch_command+=['--skip-failed-problem',problem_id]
        if launch_command is not None:
            # A queue reports its terminal status before releasing its lock.
            with (queue/'queue.lock').open('a') as lock:
                try:
                    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
                except BlockingIOError:
                    time.sleep(1)
                    continue
            stamp=str(time.time_ns())
            runner.write(journal/(stamp+'.json'),{'command':launch_command,'before_status':state})
            with (journal/(stamp+'.log')).open('w') as log:
                child=subprocess.Popen(launch_command,cwd=REPO,stdout=log,stderr=subprocess.STDOUT)
            launched=True
            # Wait for the new worker to publish status, without replaying a pause.
            deadline=time.monotonic()+30
            while time.monotonic()<deadline and read(queue/'status.json')==state and child.poll() is None:
                time.sleep(1)
            if child.poll() not in {None,0} and read(queue/'status.json')==state:
                raise RuntimeError('Queue failed to start; see supervisor log')
        time.sleep(15)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    args=parser.parse_args()
    root=args.root.resolve()
    plan=read(root/'plan.json')
    with (root/'supervisor.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        try:
            run_stage(root,Path(plan['primary_run']),plan['primary_command'],'primary_027_030')
            run_stage(root,Path(plan['rerun_run']),plan['rerun_command'],'reruns_009_026',start=True)
            states=[read(Path(plan[key])/'status.json') for key in ('primary_run','rerun_run')]
            failed=sum(s.get('failed_lane_count',0) for s in states)
            runner.write(root/'status.json',{'state':'completed_with_failed_lanes' if failed else 'completed',
                'stage':'generation_done','active_run':plan['rerun_run'],'problem_count':6,'failed_lane_count':failed})
        except Exception as error:
            previous=read(root/'status.json')
            runner.write(root/'status.json',{**previous,'state':'paused_on_failure','error':f'{type(error).__name__}: {error}'})
            raise


if __name__=='__main__':
    main()
