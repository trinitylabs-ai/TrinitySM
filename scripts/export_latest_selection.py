#!/usr/bin/env python3
"""Export preserved, hash-checked selection results; never calls a model."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
from verify_latest_selection import POLICY, read, sha, textsha, summarize, verify, markdown, number

BUNDLE = Path('docs/results/imo2026_b112_selection_20260922')
BEGIN = '<!-- BEGIN LATEST SELECTOR RESULTS -->'
END = '<!-- END LATEST SELECTOR RESULTS -->'

def put(root, name, data):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = data if isinstance(data, bytes) else (data.encode() if isinstance(data, str) else (json.dumps(data, indent=2, ensure_ascii=False)+'\n').encode())
    if path.exists():
        if path.read_bytes() != raw:
            raise ValueError('Refusing to overwrite different evidence: '+str(name))
    else:
        path.write_bytes(raw)
    return str(name)

def load_voter(repo):
    spec=importlib.util.spec_from_file_location('publication_pipeline',repo/'harnesses/proof_workshop/pipeline.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.voter_module('1.12.0')

def export_grade(root, pid, cid, grade, proof_hash):
    assert grade['proof_sha256']==proof_hash and grade['problem_id']==pid
    assert grade['model']=='gpt-5.6-sol' and grade['reasoning_effort']=='xhigh' and grade['policy_sha256']==POLICY
    evidence=Path(grade['evidence'])
    assert sha(evidence/'evidence_hashes.json')==grade['evidence_sha256']
    hashes=read(evidence/'evidence_hashes.json')
    for name,digest in hashes.items():
        assert Path(name).name==name and sha(evidence/name)==digest, name
    isolation=read(evidence/'isolation_audit.json');assert isolation['tool_calls']==0
    rep=grade['pass_index'];folder=Path('grades')/pid/f'{cid}_pass{rep}'
    raw=[put(root,folder/path.name,path.read_bytes()) for path in sorted(evidence.glob('raw_response_*.txt'))]
    assert raw
    # Keep evaluator answers and content identities, without machine paths or reference bodies.
    keys=('problem_id','submission_id','pass_index','score','verdict','grade','model','reasoning_effort',
          'policy_sha256','problem_sha256','proof_sha256','reference_sha256','evidence_sha256')
    result={k:grade[k] for k in keys}
    result.update(isolation_audit=isolation,raw_responses=raw,source_evidence_hashes=hashes)
    return put(root,folder/'grade.json',result)

def export_problem(root, report, proofs, grades, voter_root, voter, provenance):
    pid=report['problem_id'];selection=report['selection'];lanes=[]
    source=report.get('lane_grades') or {r['candidate_id']:r for r in report['lanes']}
    manifest=read(voter_root/'manifest.json')
    for cid,row in sorted(source.items()):
        proof=proofs(cid,row);digest=textsha(proof.read_text());assert digest==row['proof_sha256']
        candidate=next(c for c in manifest['candidates'] if c['candidate_id']==cid)
        assert candidate['proof_sha256']==digest
        grade_paths=[]
        for i,g in enumerate(grades(cid,row),1):
            assert g['pass_index']==i and g['score']==row['scores'][i-1]
            grade_paths.append(export_grade(root,pid,cid,g,digest))
        lanes.append(dict(candidate_id=cid,stage=row.get('stage',row.get('selected_stage')),
            proof=put(root,Path('proofs')/pid/f'{cid}.md',proof.read_bytes()),proof_sha256=digest,
            scores=row['scores'],grades=grade_paths))
    votes=[];saved={v['case_id']:v for v in selection['vote_table']}
    plan=read(voter_root/'audit_plan.json')
    put(root,Path('votes')/pid/'AUDIT_PROMPT.md',(voter_root/'AUDIT_PROMPT.md').read_bytes())
    for task in plan['audits']:
        vote=voter.verified_vote(voter_root,task)
        assert vote['valid'] and vote['binding_verified'],vote
        assert vote['selected_candidate']==saved[task['case_id']]['selected_candidate']
        call=read(voter_root/'cases'/task['case_id']/'audit/call_result.json')
        folder=Path('votes')/pid/task['case_id']
        response=put(root,folder/'response.md',call['text'])
        input_path=put(root,folder/'input.md',(voter_root/'model_inputs'/task['case_id']/'audit_input.md').read_bytes())
        keys=('case_id','original_case_id','model_key','order','presentation_order','valid','binding_verified',
              'winner_label','selected_candidate','response_sha256','reason','elapsed_seconds')
        votes.append({**{k:vote.get(k) for k in keys},'response':response,'input':input_path,
                      'prompt_sha256':call['metadata']['prompt_sha256'],
                      'input_sha256':call['metadata']['user_prompt_sha256']})
    fresh=voter.summarize(manifest,votes);combined=fresh['summaries']['combined']
    assert combined['complete'] and combined['winner']==report['selected_candidate']
    assert combined['votes']==selection['summaries']['combined']['votes']
    return dict(problem_id=pid,lanes=lanes,seed_derived_candidate_order=manifest['seed_derived_candidate_order'],
        votes=votes,selected_candidate=combined['winner'],votes_received=combined['votes'],
        order_disagreements=combined['disagreeing_pairs'],order_pairs=combined['completed_order_pairs'],
        provenance=provenance)

def export_prior(root, prior, voter):
    report=read(prior/'reports/REPORT.json');assert report['quality']=='graded' and report['model_grade_access'] is False
    assert {p['problem_id'] for p in report['problems']}=={f'imo2026_p{i}' for i in range(2,7)}
    result=[]
    for p in report['problems']:
        pid=p['problem_id']
        result.append(export_problem(root,p,
            lambda cid,row:prior/'proofs'/pid/(cid+'.md'),
            lambda cid,row:[read(prior/'grades'/pid/f'{cid}_pass{i}.json') for i in (1,2)],
            prior/'voters'/pid,voter,
            dict(generation_release='1.11.0',source_suite=Path(report['source_suite']).name,
                 selection_run_id=prior.name,source_report_sha256=sha(prior/'reports/REPORT.json'),
                 r2_r3_policy=report['source_policy'],cross_lane_policy=report['cross_lane_policy'],
                 timeout_policy='logical-600s-initial-else-one-answer-only-120s-v1' if pid in ('imo2026_p5','imo2026_p6') else 'original experiment timeout policy',
                 fresh_end_to_end_b112=False)))
    return result

def finish(root, problems, aggregation):
    problems=sorted(problems,key=lambda p:p['problem_id'])
    fresh=all(p['provenance'].get('fresh_end_to_end_b112') for p in problems)
    passes=[summarize(problems,i) for i in (1,2)];lower=min(range(2),key=lambda i:(passes[i]['totals']['average'],i))+1
    data=dict(schema='imo2026-provisional-selector-scorecard-v1',quality='graded',model='gpt-5.6-sol',reasoning_effort='xhigh',
        policy_sha256=POLICY,problems=problems,pass_results=passes,mean_grade_results=summarize(problems,'mean'),
        lower_average_pass=lower,headline_aggregation=aggregation,
        benchmark_status='fresh_uniform_b112' if fresh else 'provisional_mixed_provenance',
        official_suite_requirement=('All six problems were generated fresh end to end with the identical frozen B 1.12.0 harness and recorded settings.' if fresh else 'All six problems must be generated fresh end to end with the identical frozen B 1.12.0 harness and recorded settings. P2-P6 rerun remains pending.'),
        headline=summarize(problems,'mean') if aggregation=='mean_of_two_grades_per_proof' else passes[lower-1])
    lines=['# '+('Fresh B 1.12.0' if fresh else 'Provisional')+' IMO 2026 results with both selectors','',data['official_suite_requirement'],'',
        ('P1 completed first; P2–P6 were then rerun fresh. The same frozen release, launch parameters, server/model settings and grading protocol are verified for every problem. These problems informed selector development; this is not a held-out evaluation.' if fresh else 'P1 is a fresh B 1.12.0 run; P2–P6 reuse B 1.11.0 proofs with revised selection. These are development results, not a uniform B 1.12.0 benchmark.'), '',
        '## Every selected lane final','', '| Problem | Lane | Stage | Pass 1 | Pass 2 | Mean | Cross-lane winner |', '|---|---|---|---:|---:|---:|---|']
    for p in problems:
        for r in p['lanes']:
            lines.append(f"| {p['problem_id']} | [{r['candidate_id']}]({r['proof']}) | {r['stage']} | {r['scores'][0]} | {r['scores'][1]} | {number(sum(r['scores'])/2)} | {'yes' if r['candidate_id']==p['selected_candidate'] else ''} |")
    lines+=['','## Provenance','']
    for p in problems:
        timing=p['provenance'].get('generation_wall_seconds')
        lines.append(f"- {p['problem_id']}: generation {p['provenance']['generation_release']}; run `{p['provenance']['selection_run_id']}`; order disagreements {p['order_disagreements']}/{p['order_pairs']}."+(f' Generation elapsed: {timing/60:.1f} minutes.' if timing is not None else ''))
    lines+=['','Each proof has two independent Strict Olympiad v2 grades, including preserved evaluator answers. Hashes and every vote are in SCORECARD.json. Reference bodies and machine-specific execution logs are excluded. Source evidence hashes preserve the link to the complete local archive.', '',
        'Recompute and verify from the repository root: `python -B scripts/verify_latest_selection.py`. No inference calls or reference solutions are needed.','']
    put(root,'README.md','\n'.join(lines))
    data['artifacts']={str(p.relative_to(root)):sha(p) for p in sorted(root.rglob('*')) if p.is_file() and p.name!='SCORECARD.json'}
    put(root,'SCORECARD.json',data);verify(root)
    return data

def update_readme(repo,data):
    path=repo/'README.md';text=path.read_text();section=BEGIN+'\n'+markdown(data)+END
    if BEGIN in text:
        left,remaining=text.split(BEGIN,1);_,right=remaining.split(END,1);text=left+section+right
    else:
        text=text.replace('### IMO 2026\n','### IMO 2026\n\n'+section+'\n',1)
    path.write_text(text)

def export_native(root,native,voter,release_hash):
    report=read(native/'reports/REPORT.json');assert report['quality']=='graded'
    final=read(native/'generation/run/final_results.json')
    completion=read(native/'generation/completion.json')
    assert completion['worker_exited'] and completion['returncode']==0
    assert final['implementation_release']=='1.12.0' and final['implementation_sha256']==release_hash
    assert final['state'] in ('completed','completed_with_fallbacks') and final['completed_proofs']==4
    assert final['post_resolver_audit_enabled'] and final['cross_lane_voter_enabled']
    identity=read(native/'generation/run/harness_release.json')
    assert identity['version']=='1.12.0' and identity['release_sha256']==release_hash
    params={k:v for k,v in identity['parameters'].items() if k not in ('problem_dir','problem_id')}
    assert params['raw_seed_offset']==0 and params['seed_namespace']=='v263-v290:problem-only'
    assert params['execute_models'] and not params['dry_run'] and params['model_timeout_sec']==600
    launch=read(native/'generation/run/composite_launch_000.json')
    servers={m:{k:v for k,v in row.items() if k!='pid'} for m,row in launch['verified_servers'].items()}
    return export_problem(root,report,lambda cid,row:native/'proofs'/(cid+'.md'),lambda cid,row:row['grades'],
        native/'generation/run'/report['selection']['artifact_directory'],voter,
        dict(generation_release='1.12.0',selection_run_id=native.name,source_report_sha256=sha(native/'reports/REPORT.json'),
             fresh_end_to_end_b112=True,release_sha256=release_hash,generation_wall_seconds=completion['wall_seconds'],
             runtime=dict(parameters=params,servers=servers,profile_sha256=identity['profile_sha256'])))

def options():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1])
    group=p.add_mutually_exclusive_group(required=True);group.add_argument('--p1',type=Path);group.add_argument('--suite',type=Path)
    p.add_argument('--prior',type=Path)
    p.add_argument('--aggregation',choices=['complete_pass_with_lower_total_average','mean_of_two_grades_per_proof'],
        default='mean_of_two_grades_per_proof',
        help='Default: mean of the two grades per proof; lower complete pass is retained for historical replay.')
    return p

def main():
    a=options().parse_args()
    root=a.repo/BUNDLE;root.mkdir(parents=True,exist_ok=True);voter=load_voter(a.repo)
    release_hash=sha(a.repo/'harnesses/imo_proof_pipeline/releases/1.12.0/release.json')
    if a.suite:
        assert read(a.suite/'status.json')['state']=='completed'
        suite=read(a.suite/'reports/ALL_SIX.json')
        assert suite['quality']=='graded' and suite['benchmark_status']=='fresh_uniform_b112'
        assert suite['release_sha256']==release_hash and len(suite['native_runs'])==6
        problems=[export_native(root,Path(r['output']),voter,release_hash) for r in suite['native_runs']]
        data=finish(root,problems,a.aggregation);update_readme(a.repo,data)
        print(json.dumps({'state':'exported','benchmark_status':data['benchmark_status'],'headline':data['headline']['totals']}))
        return
    assert a.prior is not None,'--prior is required for the earlier mixed-provenance mode'
    assert read(a.p1/'status.json')['state']=='completed'
    assert read(a.p1/'reports/REPORT.json')['quality']==read(a.p1/'reports/ALL_SIX.json')['quality']=='graded'
    native=Path(str(a.p1)+'_native');report=read(native/'reports/REPORT.json');assert report['quality']=='graded'
    final=read(native/'generation/run/final_results.json');assert final['implementation_release']=='1.12.0'
    p1=export_problem(root,report,lambda cid,row:native/'proofs'/(cid+'.md'),lambda cid,row:row['grades'],
        native/'generation/run'/report['selection']['artifact_directory'],voter,
        dict(generation_release='1.12.0',selection_run_id=native.name,source_report_sha256=sha(native/'reports/REPORT.json'),
             fresh_end_to_end_b112=True,release_sha256=sha(a.repo/'harnesses/imo_proof_pipeline/releases/1.12.0/release.json')))
    data=finish(root,[p1,*export_prior(root,a.prior,voter)],a.aggregation);update_readme(a.repo,data)
    print(json.dumps({'state':'exported','bundle':str(BUNDLE),'headline':data['headline']['totals']}))

if __name__=='__main__':main()
