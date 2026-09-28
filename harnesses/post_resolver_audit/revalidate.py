"""Offline revalidation of saved audits, including partially completed runs."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from statistics import mean

from .bindings import verify_audit_binding
from .validation import ACCEPT, KEEP, VERSION, select_candidate, validate_audit
from .validation_v1 import validate_audit as validate_previous

MODELS = {'gemma': ('gemma',), 'qwen': ('qwen',), 'both': ('gemma', 'qwen')}

def read(path): return json.loads(Path(path).read_text())
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path, value):
    path=Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temp=path.with_name(path.name+'.tmp'); temp.write_text(json.dumps(value,indent=2)+'\n'); temp.replace(path)

def replay(roots, output):
    output=Path(output); output.mkdir(parents=True,exist_ok=True)
    votes=[]; selected=[]; pending=[]; provenance={}; expected_audits=0; total_cases=0
    for root in map(Path,roots):
        cfg=read(root/'config.json')
        for name in ('manifest.json','audit_plan.json','AUDIT_PROMPT.md'):
            assert sha(root/name)==cfg['pins'][name], 'Source pin mismatch: '+str(root/name)
            provenance[str(root/name)]=cfg['pins'][name]
        cases=read(root/'manifest.json')['cases']; tasks=read(root/'audit_plan.json')['audits']
        expected_audits+=len(tasks); total_cases+=len(cases)
        original_cases={c['case_id']:c for c in cases}; root_votes=[]
        assert len({t['case_id'] for t in tasks})==len(tasks)
        for task in tasks:
            folder=root/'cases'/task['case_id']; path=folder/'result.json'
            if not path.exists():continue
            result=read(path)
            call_path=folder/'audit/call_result.json'
            prior_valid=result['state']=='audited'
            vote={k:task[k] for k in ('case_id','original_case_id','problem_id','model_key','order')}
            vote.update(source_root=str(root), original_state=result['state'], original_decision=result['decision'],
                        original_validation_errors=result.get('validation_errors',[]), original_valid=prior_valid,
                        source_record_state=result['state'],source_record_decision=result['decision'],
                        source_record_validation_errors=result.get('validation_errors',[]),
                        valid=False, decision=KEEP, model_decision=result.get('model_decision'), errors=[], warnings=[])
            try:
                if not call_path.exists():
                    raise ValueError('No completed saved response: '+str(result.get('error')))
                call=read(call_path)
                binding=verify_audit_binding(root,task,result,call)
                previous=validate_previous(call['text'],task)
                parsed=validate_audit(call['text'],task)
                vote.update(original_valid=previous['valid'],original_decision=previous['decision'],
                            original_state='audited' if previous['valid'] else 'validation_fallback',
                            original_validation_errors=previous['errors'],prior_validator_version=previous['validator_version'])
                vote.update(parsed,binding_verified=True,binding=binding['binding'],response_path=str(call_path))
                provenance.update(binding['source_hashes'])
                provenance[str(path)]=sha(path);provenance[str(call_path)]=sha(call_path)
            except (ValueError,KeyError,AssertionError,OSError) as error:
                vote.update(valid=False,decision=KEEP,binding_verified=False,errors=['Binding/transport failure: '+str(error)])
            vote['state']='audited' if vote['valid'] else 'validation_fallback'
            root_votes.append(vote)
            write(output/'votes'/(vote['case_id']+'.json'),vote)
        votes.extend(root_votes)
        for case in cases:
            folder=root/'model_inputs'/case['case_id']
            for name,expected in case['files'].items():
                assert sha(folder/name)==expected, 'Proof packet hash mismatch: '+str(folder/name)
                provenance[str(folder/name)]=expected
            for role in ('baseline','candidate'):
                assert case[role+'_sha256']==case['files'][role+'.md']
            same=(folder/'baseline.md').read_text().strip()==(folder/'candidate.md').read_text().strip()
            assert case['identical']==same
            group=[v for v in root_votes if v['original_case_id']==case['case_id']]
            if not same and len(group)!=4:
                pending.append({'source_root':str(root),'case_id':case['case_id'],'problem_id':case['problem_id'],
                                'completed_audits':len(group),'required_audits':4})
                continue
            strategies={}
            for key,models in MODELS.items():
                chosen=[v for v in group if v['model_key'] in models]
                prior=[{**v,'valid':v['original_valid'],'decision':v['original_decision']} for v in chosen]
                before=select_candidate(case['case_id'],prior,models)['decision'] if not same else KEEP
                after=select_candidate(case['case_id'],chosen,models)['decision'] if not same else KEEP
                strategies[key]={'prior':before,'v2':after}
                role='candidate' if after==ACCEPT else 'baseline'
                dest=output/'selected_proofs'/key/(case['case_id']+'.md');dest.parent.mkdir(parents=True,exist_ok=True)
                content=(folder/(role+'.md')).read_bytes()
                if not dest.exists() or dest.read_bytes()!=content:dest.write_bytes(content)
                assert sha(dest)==case[role+'_sha256']
            selected.append({'case_id':case['case_id'],'problem_id':case['problem_id'],'source_root':str(root),
                             'identical':same,'strategies':strategies,'audit_results':group})
    assert len({c['case_id'] for c in selected})==len(selected), 'Duplicate case across sources'
    write(output/'SELECTIONS.json',{'validator_version':VERSION,'rows':selected,'pending':pending,'grade_access':False})
    # Evaluation labels are joined only after decisions have been written.
    for case in selected:
        root=Path(case['source_root']);cfg=read(root/'config.json');path=root/'evaluation_only/labels.json'
        if 'evaluation_only/labels.json' in cfg['pins']:
            assert sha(path)==cfg['pins']['evaluation_only/labels.json']
        label=next(r for r in read(path)['rows'] if r['case_id']==case['case_id'])
        if 'r2_scores' in label:
            for role in ('r2','final'):
                p=Path(label[role+'_grades_path']);assert sha(p)==label[role+'_grades_sha256'];provenance[str(p)]=sha(p)
            scores2,scores3=label['r2_scores'],label['final_scores'];lane=label['candidate_id']
            policy='Strict Olympiad v2; two existing judgments per proof'
        else:
            for role in ('r2','r3'):
                p=Path(label[role+'_grade']);assert sha(p)==label[role+'_grade_file_sha256'];provenance[str(p)]=sha(p)
            scores2,scores3=[label['r2']],[label['r3']];lane=label['lane']
            policy='IMOBench B.5 v1; one existing judgment per proof'
        case.update(lane=lane,r2_scores=scores2,r3_scores=scores3,grading_policy=policy,delta=mean(scores3)-mean(scores2))
        for values in case['strategies'].values():
            for mode in ('prior','v2'):
                values[mode+'_scores']=scores3 if values[mode]==ACCEPT else scores2
    metrics={}
    for key in MODELS:
        metrics[key]={}
        for mode in ('prior','v2'):
            metrics[key][mode]={
                'pairs':len(selected),
                'selected_mean':mean(mean(r['strategies'][key][mode+'_scores']) for r in selected) if selected else None,
                'regressions_blocked':sum(r['delta']<0 and r['strategies'][key][mode]==KEEP for r in selected),
                'regressions_total':sum(r['delta']<0 for r in selected),
                'gains_retained':sum(r['delta']>0 and r['strategies'][key][mode]==ACCEPT for r in selected),
                'gains_total':sum(r['delta']>0 for r in selected),
                'adopted_r3':sum(r['strategies'][key][mode]==ACCEPT for r in selected)}
    changes=[v for v in votes if v['valid']!=v['original_valid'] or v['decision']!=v['original_decision']]
    diagnostics={}
    for model in MODELS['both']:
        pairs=[[v for v in r['audit_results'] if v['model_key']==model] for r in selected if not r['identical']]
        valid=[p for p in pairs if len(p)==2 and all(v['valid'] for v in p)]
        n=sum(p[0]['decision']!=p[1]['decision'] for p in valid)
        diagnostics[model]={'valid_pairs':len(valid),'invalid_pairs':len(pairs)-len(valid),
                            'order_disagreements':n,'order_disagreement_rate':n/len(valid) if valid else None}
    value={'validator_version':VERSION,'quality':'complete' if len(votes)==expected_audits else 'partial',
           'updated_at':datetime.now(timezone.utc).isoformat(),'new_model_calls':0,'prompts_modified':False,
           'completed_audits':len(votes),'expected_audits':expected_audits,'total_cases':total_cases,
           'evaluated_pairs':len(selected),'pending_pairs':pending,'votes_changed':len(changes),'changed_votes':changes,
           'invalid_audits':sum(not v['valid'] for v in votes),'binding_failures':sum(not v.get('binding_verified') for v in votes),
           'metrics':metrics,'order_diagnostics':diagnostics,'rows':selected,'votes':votes,'source_hashes':provenance,
           'source_runs':list(map(str,roots))}
    write(output/'REPORT.json',value)
    lines=['# Audit revalidation: code-owned proof identities','',
           f"Status: {value['quality']}; {len(votes)}/{expected_audits} audit responses available, {len(selected)}/{total_cases} pairs evaluated.",'',
           'No prompts changed and no model calls made. Model-echoed hashes are optional diagnostics. The proof files, request metadata and saved response bindings are verified in code. Prior means the same saved text revalidated with V1; other validation rules are unchanged.','',
           f"Changed vote validity or verdict: {len(changes)}. Invalid audits remaining: {value['invalid_audits']}; binding/transport failures: {value['binding_failures']}.",'',
           '| Strategy | Prior selected mean | V2 selected mean | Declines blocked | Gains retained |','|---|---:|---:|---:|---:|']
    for key,mm in metrics.items():
        a,b=mm['prior'],mm['v2']
        fmt=lambda n:'N/A' if n is None else f'{n:.5f}'
        lines.append(f"| {key} | {fmt(a['selected_mean'])} | {fmt(b['selected_mean'])} | {b['regressions_blocked']}/{b['regressions_total']} | {b['gains_retained']}/{b['gains_total']} |")
    lines+=['','| Auditor | Order disagreements | Valid pairs | Invalid pairs |','|---|---:|---:|---:|']
    for key,d in diagnostics.items():lines.append(f"| {key} | {d['order_disagreements']} | {d['valid_pairs']} | {d['invalid_pairs']} |")
    lines+=['','## Changed vote validation','','| Problem | Case | Model/order | Prior verdict | V2 verdict | Valid now | Prior errors |','|---|---|---|---|---|---|---|']
    for v in changes:
        lines.append(f"| {v['problem_id']} | {v['original_case_id']} | {v['model_key']}/{v['order']} | {v['original_decision']} | {v['decision']} | {v['valid']} | {'; '.join(v['original_validation_errors'])} |")
    lines+=['','## Paired scores','','| Problem | Lane | R2 | R3 | Gemma V2 | Qwen V2 | Combined V2 |','|---|---|---|---|---|---|---|']
    for r in sorted(selected,key=lambda x:(x['problem_id'],x['lane'])):
        picked=[str(r['strategies'][k]['v2_scores']) for k in MODELS]
        lines.append(f"| {r['problem_id']} | {r['lane']} | {r['r2_scores']} | {r['r3_scores']} | "+' | '.join(picked)+' |')
    lines+=['','Partial reports exclude unfinished pairs from means. Single-pass B.5 scores and two-pass Strict Olympiad scores remain in separate reports. Original artifacts and prior reports are preserved.','']
    tmp=output/'REPORT.md.tmp';tmp.write_text('\n'.join(lines));tmp.replace(output/'REPORT.md')
    return value
