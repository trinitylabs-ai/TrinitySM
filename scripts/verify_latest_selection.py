#!/usr/bin/env python3
"""Recompute released two-pass scores and all 144 selector votes offline."""
from pathlib import Path
import hashlib,itertools,json,re

POLICY='d1c93550ca49f52a35fe4c0eb0b1ccca9534e9112d928002667e404c367de4e4'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def textsha(text):return hashlib.sha256(text.strip().encode()).hexdigest()
def read(path):return json.loads(Path(path).read_text())
def response_winner(text):
    """Read one explicit saved vote; never infer a preference from prose."""
    normalized=text.replace('\r\n','\n').replace('**','').replace('`','')
    fields=re.findall(r'^\s*(?:[-*]\s*)?Winner\s*:',normalized,re.M|re.I)
    choices=re.findall(r'^\s*(?:[-*]\s*)?Winner\s*:\s*([AB])\s*[.]?\s*$',normalized,re.M|re.I)
    assert len(fields)==len(choices)==1,'Saved response must contain exactly one explicit Winner: A or B'
    return choices[0].upper()
def metric(problem,scores):
    return dict(average=sum(scores.values())/4,oracle_at_4=max(scores.values()),selector_at_1=scores[problem['selected_candidate']])
def summarize(problems,mode):
    rows=[]
    for p in problems:
        scores={r['candidate_id']: (sum(r['scores'])/2 if mode=='mean' else r['scores'][mode-1]) for r in p['lanes']}
        rows.append(dict(problem_id=p['problem_id'],**metric(p,scores)))
    return dict(rows=rows,totals={m:sum(r[m] for r in rows) for m in ('average','oracle_at_4','selector_at_1')},maximum=42)

def verify(root):
    root=Path(root);data=read(root/'SCORECARD.json')
    assert data['quality']=='graded' and data['model']=='gpt-5.6-sol' and data['reasoning_effort']=='xhigh'
    assert data['policy_sha256']==POLICY
    for name,digest in data['artifacts'].items():
        path=(root/name).resolve();assert path.is_relative_to(root.resolve()) and sha(path)==digest,name
    ps=data['problems'];assert {p['problem_id'] for p in ps}=={f'imo2026_p{i}' for i in range(1,7)} and len(ps)==6
    if data['benchmark_status']=='fresh_uniform_b112':
        identities=[]
        for p in ps:
            provenance=p['provenance']
            assert provenance['fresh_end_to_end_b112'] and provenance['generation_release']=='1.12.0'
            identities.append((provenance['release_sha256'], provenance['runtime']))
        assert all(identity==identities[0] for identity in identities)
        assert len({p['provenance']['selection_run_id'] for p in ps})==6
    for p in ps:
        lanes={r['candidate_id']:r for r in p['lanes']};order=p['seed_derived_candidate_order']
        assert len(lanes)==len(order)==4 and set(order)==set(lanes)
        for r in lanes.values():
            assert len(r['scores'])==len(r['grades'])==2
            assert r['proof'] in data['artifacts']
            assert textsha((root/r['proof']).read_text())==r['proof_sha256']
            for rep,path in enumerate(r['grades'],1):
                assert path in data['artifacts']
                g=read(root/path)
                assert all(r in data['artifacts'] for r in g['raw_responses'])
                assert g['proof_sha256']==r['proof_sha256'] and g['problem_id']==p['problem_id'] and g['pass_index']==rep
                assert g['score']==r['scores'][rep-1] and type(g['score']) is int and 0<=g['score']<=7
                assert g['grade']['score']==g['score'] and g['grade']['contract_consistent']
                assert g['model']==data['model'] and g['reasoning_effort']==data['reasoning_effort'] and g['policy_sha256']==POLICY
                assert g['isolation_audit']['tool_calls']==0 and len(g['raw_responses'])>=1
        votes=p['votes'];assert len(votes)==24
        pairs={tuple(sorted(x)) for x in itertools.combinations(order,2)}
        actual=set();counts={c:0 for c in order};flips=0
        for vote in votes:
            assert vote['valid'] and vote['binding_verified']
            assert vote['response'] in data['artifacts'] and vote['input'] in data['artifacts']
            assert sha(root/vote['input'])==vote['input_sha256']
            pair=tuple(sorted(vote['presentation_order']));assert pair in pairs
            key=(pair,vote['model_key'],vote['order']);assert key not in actual;actual.add(key)
            selected=vote['presentation_order'][0 if vote['winner_label']=='A' else 1]
            assert vote['winner_label'] in ('A','B') and vote['selected_candidate']==selected
            assert hashlib.sha256((root/vote['response']).read_bytes()).hexdigest()==vote['response_sha256']
            assert response_winner((root/vote['response']).read_text())==vote['winner_label'], 'Saved response winner differs from vote metadata'
            counts[selected]+=1
        assert actual=={(pair,m,o) for pair in pairs for m in ('gemma','qwen') for o in ('forward','reverse')}
        for pair in pairs:
            for m in ('gemma','qwen'):
                two=[v for v in votes if tuple(sorted(v['presentation_order']))==pair and v['model_key']==m]
                assert two[0]['presentation_order']==list(reversed(two[1]['presentation_order']))
                flips+=two[0]['selected_candidate']!=two[1]['selected_candidate']
        assert p['selected_candidate']==max(order,key=lambda c:counts[c])
        assert p['votes_received']==counts and p['order_disagreements']==flips and p['order_pairs']==12
    passes=[summarize(ps,r) for r in (1,2)]
    chosen=min(range(2),key=lambda i:(passes[i]['totals']['average'],i))+1
    assert data['pass_results']==passes and data['mean_grade_results']==summarize(ps,'mean')
    assert data['lower_average_pass']==chosen
    assert data['headline_aggregation'] in ('mean_of_two_grades_per_proof','complete_pass_with_lower_total_average')
    expected=summarize(ps,'mean') if data['headline_aggregation']=='mean_of_two_grades_per_proof' else passes[chosen-1]
    assert data['headline']==expected
    return data

def number(x):return f'{x:.3f}'.rstrip('0').rstrip('.')
def markdown(data):
    metrics=('average','selector_at_1','oracle_at_4')
    lines=['| Problem | Average | Selector@1 | Oracle@4 |', '|---|---:|---:|---:|']
    for r in data['headline']['rows']:
        lines.append('| '+r['problem_id'].split('_')[-1].upper()+' | '+' | '.join(number(r[m]) for m in metrics)+' |')
    lines.append(f"| **Total (of {number(data['headline']['maximum'])})** | "+' | '.join('**'+number(data['headline']['totals'][m])+'**' for m in metrics)+' |')
    first,second=data['pass_results']
    if all(first['totals'][m]==second['totals'][m] for m in metrics):
        lines+=['','Both grading passes give the same totals.']
    proofs=sum(len(p['lanes']) for p in data['problems'])
    lines+=['',f'[All {proofs} proofs, every vote and both grades](docs/results/imo2026_b112_selection_20260922/README.md)','']
    return '\n'.join(lines)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--bundle',type=Path,default=Path(__file__).resolve().parents[1]/'docs/results/imo2026_b112_selection_20260922');a=p.parse_args()
    d=verify(a.bundle);print(json.dumps(dict(state='verified',problems=6,proofs=24,grades=48,votes=144,headline=d['headline']['totals']),indent=2))
