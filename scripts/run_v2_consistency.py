#!/usr/bin/env python3
"""Resume four fresh strict-v2 assessments per frozen proof; publish consistency."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import fcntl
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import random
import signal
import subprocess
import sys
import time

from score_imo_v2 import ROOT, POLICY_SHA256, ARCHIVE
from score_v2_consistency_worker import prepare_study_runner
from report_strict_v2 import first_valid_response


def now():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
    tmp.replace(path)


def consistency(vectors):
    if not vectors:
        return dict(proofs=0)
    assert all(len(v) == 4 and all(type(x) is int and 0 <= x <= 7 for x in v) for v in vectors)
    n = len(vectors)
    ranges = [max(v)-min(v) for v in vectors]
    return dict(proofs=n, exact_agreement=sum(x == 0 for x in ranges)/n,
                within_one_point=sum(x <= 1 for x in ranges)/n,
                pairwise_agreement=sum(a == b for v in vectors for a,b in itertools.combinations(v,2))/(6*n),
                mean_range=sum(ranges)/n,
                mean_population_sd=sum(math.sqrt(sum((x-sum(v)/4)**2 for x in v)/4) for v in vectors)/n,
                range_counts=dict(sorted(Counter(ranges).items())),
                crosses_six_threshold=sum(min(v)<6<=max(v) for v in vectors),
                crosses_three_four_boundary=sum(min(v)<=3<max(v) for v in vectors))


def base_for(study, unit):
    return ROOT / f"benchmarks/{unit['benchmark']}/results/{study['run_id']}"


def grade_path(study, unit, repeat):
    return base_for(study, unit) / f"grades/{unit['unit_id']}/g{repeat}.json"


def check_grade(study, unit, repeat, value):
    for key in ['unit_id', 'problem_id', 'problem_sha256', 'reference_sha256', 'proof_sha256']:
        assert value[key] == unit[key], f'Grade identity mismatch: {key}'
    assert value['repeat'] == repeat and value['policy_sha256'] == POLICY_SHA256
    assert value['model'] == study['model'] and value['reasoning_effort'] == study['reasoning_effort']
    assert value['isolation_audit']['tool_calls'] == 0
    assert type(value['grade']['score']) is int and 0 <= value['grade']['score'] <= 7


def collect(study):
    found = {}
    for unit in study['units']:
        for repeat in range(1,5):
            path = grade_path(study, unit, repeat)
            if path.exists():
                value = read(path); check_grade(study, unit, repeat, value)
                found[unit['unit_id'], repeat] = value
    return found


def publish(study, directory, found, active=None, attempts=None):
    vectors, rows = {}, []
    for unit in study['units']:
        grades = [found.get((unit['unit_id'], i)) for i in range(1,5)]
        scores = [g['grade']['score'] if g else None for g in grades]
        if all(g is not None for g in grades):
            vectors[unit['unit_id']] = scores
        rows.append(dict(unit_id=unit['unit_id'], problem_id=unit['problem_id'], scores=scores,
                         grade_files=[str(grade_path(study,unit,i).relative_to(ROOT)) if grades[i-1] else None for i in range(1,5)]))
    cohorts = []
    for benchmark, cohort in sorted({(o['benchmark'],o['cohort']) for o in study['observations']}):
        members = [o for o in study['observations'] if (o['benchmark'],o['cohort']) == (benchmark,cohort)]
        ids = {o['unit_id'] for o in members}
        result = dict(benchmark=benchmark, cohort=cohort, submissions=len(members),
                      unique_proofs=len(ids), consistency=consistency([vectors[x] for x in ids if x in vectors]))
        if ids <= vectors.keys():
            by_problem = defaultdict(list)
            for o in members: by_problem[o['problem_id']].append(vectors[o['unit_id']])
            result.update(problems=len(by_problem), maximum_points=7*len(by_problem),
                          average_points=sum(sum(sum(v)/4 for v in vs)/len(vs) for vs in by_problem.values()),
                          oracle_at_4_points=sum(max(sum(v)/4 for v in vs) for vs in by_problem.values()),
                          repeat_average_points=[sum(sum(v[i] for v in vs)/len(vs) for vs in by_problem.values()) for i in range(4)],
                          repeat_oracle_at_4_points=[sum(max(v[i] for v in vs) for vs in by_problem.values()) for i in range(4)])
        cohorts.append(result)
    result = dict(schema='workshop-v2-consistency-results-v1', updated_at=now(),
                  state='completed' if len(found)==study['planned_grades'] else 'running',
                  planned_grades=study['planned_grades'], completed_grades=len(found),
                  completed_quartets=len(vectors), policy_sha256=POLICY_SHA256,
                  model=study['model'], reasoning_effort=study['reasoning_effort'],
                  overall=consistency(list(vectors.values())), cohorts=cohorts, rows=rows,
                  metadata_disagreements=sum(not g['grade']['contract_consistent'] for g in found.values()),
                  retries_within_accepted_calls=sum(g.get('response_selection',{}).get('total_attempts',1)-1 for g in found.values()),
                  active_batch=active, task_attempts=attempts or {})
    write(directory/'results.json', result)
    lines = ['# Four independent strict-v2 grades per proof', '',
             f"Status: **{result['state']}**; {len(found)}/{study['planned_grades']} grades; {len(vectors)}/{study['unique_proofs']} complete quartets.", '',
             f"Evaluator: `{study['model']}` / `{study['reasoning_effort']}`. Policy SHA-256: `{POLICY_SHA256}`.", '',
             'Every repetition is a fresh isolated call with the same statement, reference, proof, and v2 policy. No earlier scores, cohort labels, or other repetitions enter the prompt.', '',
             'Incomplete quartets are excluded from provisional consistency statistics, never assigned zero. Final cohort score matrices appear only when every included proof has four grades.', '',
             '## Consistency', '',
             '| Set / cohort | Complete unique proofs | Four-score agreement | Pairwise agreement | Within one point | Mean range | Mean SD |',
             '|---|---:|---:|---:|---:|---:|---:|']
    for label, c in [('All unique proofs',result['overall'])]+[(x['benchmark']+' / '+x['cohort'],x['consistency']) for x in cohorts]:
        if c['proofs']:
            lines.append(f"| {label} | {c['proofs']} | {100*c['exact_agreement']:.2f}% | {100*c['pairwise_agreement']:.2f}% | {100*c['within_one_point']:.2f}% | {c['mean_range']:.3f} | {c['mean_population_sd']:.3f} |")
    lines += ['', 'SD uses the four-score population standard deviation. Pairwise agreement uses all six pairs per proof. Identical mathematical inputs share their quartet across cohort memberships and count once in the overall result.', '',
              f"Score/metadata disagreements retained: {result['metadata_disagreements']}. These are flagged observations, not grounds for resampling a numerical grade.", '',
              f"Automatic retries within accepted calls: {result['retries_within_accepted_calls']}. Failed slots remain missing until a valid response is obtained.", '',
              '## Cohort scores', '',
              '| Set / cohort | Average points | Oracle@4 points | Maximum |', '|---|---:|---:|---:|']
    for c in cohorts:
        if 'average_points' in c:
            lines.append(f"| {c['benchmark']} / {c['cohort']} | {c['average_points']:.2f} | {c['oracle_at_4_points']:.2f} | {c['maximum_points']} |")
    lines += ['', 'Each submitted proof receives the mean of its four grades. Average gives each problem equal weight; Oracle@4 takes the best of its available candidate proofs after averaging grades. Grading repetitions are not extra proof candidates. Experimental and supplementary cohorts remain separate.', '',
              'This measures repeatability under v2. It does not establish that v2 is more consistent than v1, because v1 is not repeated in this study. Strict-v2 IMO-ProofBench scores are distinct from the published IMOBench B.5 scale. The generation comparison is retrospective, not a controlled claim about extended reasoning alone.', '',
              '## Per-proof results', '', '| Problem | Proof identity | Four scores |', '|---|---|---|']
    for row in rows:
        cells = []
        for value, path in zip(row['scores'],row['grade_files']):
            cells.append('—' if value is None else f"[{value}]({os.path.relpath(ROOT/path,directory)})")
        lines.append(f"| {row['problem_id']} | `{row['unit_id'][:16]}` | {', '.join(cells)} |")
    (directory/'REPORT.md').write_text('\n'.join(lines)+'\n')
    return result


def export_batch(study, batch, output, runner):
    units = {u['unit_id']:u for u in study['units']}
    for item in batch:
        unit = units[item['unit_id']]; repeat = item['repeat']
        dest = grade_path(study,unit,repeat)
        if dest.exists(): continue
        case = output / f"p{unit['problem_number']}" / item['candidate_id']
        if not (case/'summary.json').exists(): continue
        native = read(case/'summary.json'); meta = read(case/'manifest.json')
        if native['state'] != 'completed': continue
        grade, selection = first_valid_response(case/'codex.jsonl',runner)
        for key in ['problem_sha256','reference_sha256','proof_sha256']:
            assert native[key] == unit[key]
        assert native['policy_sha256'] == POLICY_SHA256
        problem = read(ROOT/unit['problem']); statement=(problem.get('claim') or problem.get('problem') or problem.get('statement')).strip()
        prompt = runner.grading_prompt(problem=statement,reference=(ROOT/unit['reference']).read_text().strip(),
                                       proof=(ROOT/unit['proof']).read_text().strip(),grading_policy=runner.STRICT_POLICY)
        assert hashlib.sha256(prompt.encode()).hexdigest() == meta['prompt_sha256']
        value = dict(schema='workshop-v2-independent-grade-v1', unit_id=unit['unit_id'], problem_id=unit['problem_id'], repeat=repeat,
                     **{k:unit[k] for k in ['problem_sha256','reference_sha256','proof_sha256']},
                     policy_sha256=POLICY_SHA256, model=native['grader'], reasoning_effort=native['reasoning_effort'],
                     prompt_sha256=meta['prompt_sha256'], grade=grade, response_selection=selection,
                     completed_at=native['completed_at'], isolation_audit=read(case/'isolation_audit.json'),
                     source_batch=output.name, native_rejection_count=len(native['errors']))
        check_grade(study,unit,repeat,value);write(dest,value)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--study',type=Path,required=True)
    p.add_argument('--execute-models',action='store_true')
    p.add_argument('--workers',type=int,default=8)
    p.add_argument('--chunk-size',type=int,default=32)
    p.add_argument('--retry-rounds',type=int,default=3)
    a=p.parse_args();directory=a.study.resolve();study=read(directory/'manifest.json')
    assert study['policy_sha256']==POLICY_SHA256 and study['repeats']==4
    assert a.workers>0 and a.chunk_size>0 and a.retry_rounds>0
    runner=prepare_study_runner()
    for u in study['units']:
        for field in ['proof','reference']:
            assert hashlib.sha256((ROOT/u[field]).read_text().strip().encode()).hexdigest()==u[field+'_sha256']
        payload=read(ROOT/u['problem']);statement=(payload.get('claim') or payload.get('problem') or payload.get('statement')).strip()
        assert hashlib.sha256(statement.encode()).hexdigest()==u['problem_sha256']
    work=directory/'work';work.mkdir(exist_ok=True)
    with (work/'coordinator.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        attempts=read(work/'attempts.json') if (work/'attempts.json').exists() else {}
        # Recover completed responses after interruption before scheduling work.
        # This prevents a valid, unexported result from becoming an extra draw.
        for benchmark in sorted({u['benchmark'] for u in study['units']}):
            private=ROOT/f"benchmarks/{benchmark}/results/{study['run_id']}/grading/work"
            for binding in sorted(private.glob('batch_*.bindings.json')):
                output=private/binding.name.removesuffix('.bindings.json')
                export_batch(study,read(binding),output,runner)
        found=collect(study);publish(study,directory,found,attempts=attempts)
        if not a.execute_models: return
        frozen_files=['scripts/score_imo_v2.py','scripts/score_v2_consistency_worker.py','scripts/run_v2_consistency.py','scripts/report_strict_v2.py',
                      'docs/public_release/grading/strict_olympiad_policy_v2.txt','docs/public_release/grading/evaluator_instructions.txt']
        hashes={f:digest(ROOT/f) for f in frozen_files}
        config=dict(model=study['model'],reasoning_effort=study['reasoning_effort'],workers=a.workers,
                    chunk_size=a.chunk_size,policy_sha256=POLICY_SHA256,source_hashes=hashes,
                    malformed_or_failed_attempts_only_retried=True,semantic_disagreements_retained=True,
                    earlier_grades_reused=False,ordering_seed=20260918)
        config['study_manifest_sha256']=digest(directory/'manifest.json')
        config_path=directory/'execution_config.json'
        if config_path.exists(): assert read(config_path)==config,'Execution configuration changed'
        else: write(config_path,config)
        launcher=Path.home()/'.codex/skills/strict-gold-informed-olympiad-scorer/scripts/score.py'
        if not launcher.is_file():launcher=ARCHIVE/'score.py'
        assert digest(launcher)=='7a4cfb1c678717d045889eb58fd0714a9932c8a2f29902ed210a363a15d8a12a'
        units=list(study['units']);random.Random(20260918).shuffle(units)
        while len(found)<study['planned_grades']:
            assert hashes=={f:digest(ROOT/f) for f in frozen_files},'Frozen evaluator code changed'
            pending=[(u,i) for u in units for i in range(1,5) if (u['unit_id'],i) not in found
                     and attempts.get(u['unit_id']+f':{i}',0)<a.retry_rounds]
            if not pending:
                result=publish(study,directory,found,attempts=attempts);result['state']='incomplete_after_retries'
                write(directory/'results.json',result);raise SystemExit(2)
            benchmark=pending[0][0]['benchmark']
            chosen=[(u,i) for u,i in pending if u['benchmark']==benchmark][:a.chunk_size]
            base=base_for(study,chosen[0][0]);private=base/'grading/work';private.mkdir(parents=True,exist_ok=True)
            number=len(list(private.glob('batch_*.tasks.json')))+1;name=f'batch_{number:05d}'
            output=private/name;manifest=private/(name+'.tasks.json');batch=[];tasks=[]
            for u,i in chosen:
                cid='u'+u['unit_id']+f'_g{i}';batch.append(dict(unit_id=u['unit_id'],repeat=i,candidate_id=cid))
                tasks.append(dict(problem_number=u['problem_number'],problem_id=u['problem_id'],candidate_id=cid,
                                  **{k+'_path':str(ROOT/u[k]) for k in ['problem','reference','proof']},
                                  expected_hashes={k:u[k] for k in ['problem_sha256','reference_sha256','proof_sha256']}))
                key=u['unit_id']+f':{i}';attempts[key]=attempts.get(key,0)+1
            write(manifest,dict(schema='gold-informed-generic-proof-task-manifest-v1',tasks=tasks))
            write(private/(name+'.bindings.json'),batch);write(work/'attempts.json',attempts)
            wrapper=private/'launcher/scripts';wrapper.mkdir(parents=True,exist_ok=True)
            (wrapper/'__init__.py').write_text('')
            (wrapper/'run_gold_informed_calibrated_codex_scores.py').write_text(
                'import runpy,sys\nsys.path.insert(0,'+repr(str(ROOT/'scripts'))+')\nrunpy.run_path('+repr(str(ROOT/'scripts/score_v2_consistency_worker.py'))+',run_name="__main__")\n')
            command=[sys.executable,'-B',str(launcher),'--generic-task-manifest',str(manifest),'--output-dir',str(output),
                     '--workers',str(a.workers),'--reasoning-effort',study['reasoning_effort']]
            with (private/(name+'.log')).open('w') as log:
                child=subprocess.Popen(command,cwd=wrapper.parent,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                try:
                    while child.poll() is None:
                        export_batch(study,batch,output,runner);found=collect(study)
                        publish(study,directory,found,active=benchmark+'/'+name,attempts=attempts)
                        print(json.dumps(dict(updated_at=now(),completed=len(found),total=study['planned_grades'],active=benchmark+'/'+name)),flush=True)
                        time.sleep(30)
                except BaseException:
                    os.killpg(child.pid,signal.SIGTERM);child.wait();raise
            export_batch(study,batch,output,runner);found=collect(study);publish(study,directory,found,attempts=attempts)
        print('Completed all four independent grades for every frozen proof.',flush=True)


if __name__=='__main__':
    main()
