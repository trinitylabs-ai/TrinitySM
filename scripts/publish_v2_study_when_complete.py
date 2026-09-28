#!/usr/bin/env python3
"""Verify a completed repetition study, then optionally commit and push its artifacts."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def command(args):
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=True).stdout


def allowed_paths(run_id):
    return [f'benchmarks/reports/{run_id}',
            *[f'benchmarks/{b}/results/{run_id}' for b in ['imo-proofbench/basic','imo-proofbench/advanced','imo2026']]]


def check_staged(names, allowed):
    if any(not any(name == prefix or name.startswith(prefix + '/') for prefix in allowed) for name in names):
        raise RuntimeError('Unrelated staged changes exist; completion publication will not commit them')


def study_runner(manifest):
    repeats = manifest.get('repeats')
    if repeats not in (2, 4):
        raise ValueError('Expected an explicit two- or four-grade protocol')
    if manifest['planned_grades'] != repeats * manifest['unique_proofs']:
        raise ValueError('Planned assessments do not match the effective repetition count')
    return 'scripts/run_v2_pairs.py' if repeats == 2 else 'scripts/run_v2_consistency.py'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--study',type=Path,required=True)
    p.add_argument('--push',action='store_true')
    a=p.parse_args();directory=a.study.resolve()
    from report_v2_matrices import load_manifest
    manifest=load_manifest(directory)
    runner=study_runner(manifest)
    status=directory/'work/publication_status.json'
    def record(state, **extra):
        status.write_text(json.dumps(dict(state=state,updated_at=datetime.now(timezone.utc).isoformat(),**extra),indent=2)+'\n')
    record('waiting_for_grades')
    while True:
        result=json.loads((directory/'results.json').read_text())
        if result['state']=='completed' and result['active_batch'] is None:
            break
        if result['state']=='incomplete_after_retries':
            record('requires_retry',completed=result['completed_grades'],planned=result['planned_grades'])
            return 2
        if result['state']=='blocked_usage_limit':
            record('waiting_for_quota',completed=result['completed_grades'],planned=result['planned_grades'])
            return 3
        time.sleep(30)
    try:
        time.sleep(5)  # Let the coordinator release its lock after its final write.
        record('verifying')
        command([sys.executable,'-B',runner,'--study',str(directory)])
        command([sys.executable,'-B','-m','pytest','-q','-p','no:cacheprovider',
                 'tests/test_v2_consistency.py','tests/test_strict_v2.py','tests/test_score_report.py',
                 'tests/test_public_reproduction.py','tests/test_release_prompt_boundary.py','tests/test_raw_ablation.py',
                 'tests/test_v2_publication.py','tests/test_v2_matrices.py','tests/test_v2_pairs.py'])
        result=json.loads((directory/'results.json').read_text())
        assert result['completed_grades']==manifest['planned_grades']
        assert result.get('completed_proofs',result.get('completed_quartets'))==manifest['unique_proofs']
        command([sys.executable,'-B','scripts/report_v2_matrices.py','--study',str(directory)])
        if a.push:
            assert command(['git','branch','--show-current']).strip()=='release/public-rc1'
            allowed=allowed_paths(manifest['run_id'])
            check_staged(command(['git','diff','--cached','--name-only']).splitlines(),allowed)
            command(['git','add','--',*allowed])
            check_staged(command(['git','diff','--cached','--name-only']).splitlines(),allowed)
            command([sys.executable,'-B','scripts/audit_release.py'])
            command(['git','diff','--cached','--check'])
            if command(['git','diff','--cached','--name-only']).strip():
                command(['git','commit','-m','Publish repeated strict v2 benchmark consistency results'])
            command(['git','push','origin','release/public-rc1'])
            record('pushed',commit=command(['git','rev-parse','HEAD']).strip())
        else:
            record('verified')
    except Exception as error:
        record('publication_failed',error=type(error).__name__,detail=str(error))
        raise
    return 0


if __name__=='__main__':
    raise SystemExit(main())
