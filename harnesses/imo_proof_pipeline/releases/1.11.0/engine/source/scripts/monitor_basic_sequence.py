#!/usr/bin/env python3
"""Three-minute snapshots for the currently active queue in a Basic sequence."""
import argparse
import fcntl
import json
from pathlib import Path
import sys
import time
REPO=Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:sys.path.insert(0,str(REPO))
from scripts import monitor_basic_mtp4_20260911 as monitor
from scripts import run_v263_v290 as runner


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    args=parser.parse_args()
    root=args.root.resolve()
    with (root/'monitor.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        while True:
            overall=monitor.read(root/'status.json')
            monitor.ROOT=Path(overall['active_run'])
            snapshot=monitor.snapshot()
            snapshot['sequence']=overall
            problem_id=snapshot.get('queue',{}).get('problem_id')
            if problem_id:
                number=int(problem_id.rsplit('-',1)[1])
                phase=monitor.ROOT/'problems'/problem_id/f'01_source/p{number}/01_raw_lazy_enhanced_resolve'
                snapshot['frontend']=monitor.read(phase/'status.json')
            snapshot['strict']=monitor.read(REPO/'runs/basic_strict_incremental_20260911/status.json')
            runner.write(root/'monitor_latest.json',snapshot)
            with (root/'monitor_3min.jsonl').open('a') as log:
                log.write(json.dumps(snapshot)+'\n')
            print(json.dumps(snapshot),flush=True)
            if overall.get('state') in {'completed','completed_with_failed_lanes','paused_on_failure','stopped','stopped_by_user'}:
                return
            time.sleep(180)


if __name__=='__main__':main()
