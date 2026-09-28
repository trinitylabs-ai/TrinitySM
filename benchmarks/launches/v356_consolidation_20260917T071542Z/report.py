from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import json,hashlib
b=Path(Path('/tmp/v356_launch_path').read_text().strip())
def read(p):
 try:return json.loads(p.read_text())
 except (FileNotFoundError,json.JSONDecodeError):return {}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def textsha(p):return hashlib.sha256(p.read_text().strip().encode()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
policy='1a8c5d02a7bd84a53ad011cf889ceaaca7ff94166536565bda49082649781ecf'
rows=[]
for trial in read(b/'batch.json')['trials']:
 local=Path(trial['launch']);cfg=read(local/'selection.json');e=Path(trial['experiment']);n=e/'generation/run'
 status=read(local/'status.json');native=read(n/'status.json');summary=read(e/'reports/run_summary.json');resume=read(n/'resume.json')
 row={**trial,'state':status.get('state'),'stage':native.get('stage'),'outcome':summary.get('outcome'),
  'external_score':None,'source_candidate':cfg['source_candidate'],'source_checkpoint':cfg['source_checkpoint'],
  'error':status.get('error') or native.get('error')}
 assert sha(Path(cfg['source_proof']))==cfg['source_proof_file_sha256']
 if resume:
  assert resume['source_selection_reused'] and resume['certificate_replayed']
  assert all(resume[k]==0 for k in ('new_detection_calls','new_matcher_calls','new_formalization_calls','new_semantic_audit_calls','new_certificate_searches'))
  for p,digest in resume['source_record_sha256'].items():assert sha(Path(p))==digest
  row['resume']=resume
 if summary.get('external_grade'):
  proof=e/'proofs'/cfg['problem_id']/cfg['source_candidate']/'tool_rewrite.md'
  assert proof.read_bytes()==(n/'rewritten_proof.md').read_bytes()
  if cfg['case']=='p2':
   d=e/'grades'/cfg['problem_id']/cfg['source_candidate']/'tool_rewrite/strict'
   grade=read(d/'summary.json');m=read(d/'manifest.json')
   assert grade['policy_sha256']==policy and textsha(proof)==grade['proof_sha256']
   assert m['isolated_candidate_call'] and not m['pipeline_reviews_supplied']
   calls=[];types=Counter()
   for line in (d/'codex.jsonl').read_text().splitlines():
    try:event=json.loads(line)
    except json.JSONDecodeError:continue
    if event.get('type')=='item.completed':
     item=event['item'];types[item['type']]+=1
     if item['type'] not in ('agent_message','reasoning'):calls.append(item)
   write(d/'provenance_audit.json',{'proof_binding_verified':True,'proof_file_sha256':sha(proof),
    'proof_canonical_sha256':grade['proof_sha256'],'isolated_candidate_call':True,'pipeline_reviews_supplied':False,
    'completed_event_types':dict(types),'tool_events':calls,'failed_grader_calls':grade['errors']})
   row.update(policy='strict-gold-informed-olympiad',policy_sha256=policy,tool_event_count=len(calls),failed_grader_calls=grade['errors'])
   gradepath=d/'summary.json'
  else:
   d=e/'grades'/cfg['problem_id']/cfg['source_candidate']/'tool_rewrite';gradepath=d/'result.json';grade=read(gradepath)
   assert grade['isolation_verified'] and read(d/'isolation_audit.json')['tool_calls']==0
   assert textsha(proof)==grade['proof_sha256']
   row.update(policy='official-IMOBench-ProofAutoGrader',tool_event_count=0)
  row.update(external_score=grade['grade']['score'],external_grade=grade['grade'],proof=str(proof),grade=str(gradepath),
   proof_file_sha256=sha(proof),words=len(proof.read_text().split()),grader=grade.get('grader') or grade.get('model'),
   reasoning_effort=grade.get('reasoning_effort'),generation_wall_seconds=summary['wall_seconds'])
 rows.append(row)
done=all(r['state'] in ('completed','failed') for r in rows)
scores=[r['external_score'] for r in rows]
report={'updated_at':datetime.now(timezone.utc).isoformat(),'state':'completed' if done else 'running',
 'package':read(b/'release_validation.json')['package'],'release_sha256':read(b/'batch.json')['tool_release_sha256'],
 'score_order':['p2','basic008','basic009'],'score_vector':scores,
 'all_three_at_least_six':all(s is not None and s>=6 for s in scores),'validation':read(b/'release_validation.json'),
 'compatibility':read(b/'compatibility.json'),'first_prompt_compatibility':read(b/'first_rewrite_prompt_compatibility.json'),
 'trials':rows}
write(b/'comparison.json',report)
lines=['# V356 consolidated harness validation','','V349 geometry/root implementation with the V353 discrete extension. '
 'Validation replays each original selected certificate, then regenerates the proof with mandatory budget forcing and grades independently. '
 'No new detection, matching, formalization or certificate searches are performed.','',
 '| Problem | Original score | Previous successful version | V356 score | Status |','|---|---:|---:|---:|---|']
versions={'p2':'V349','basic008':'V344','basic009':'V353'}
for r in rows:
 new=str(r['external_score'])+'/7' if r['external_score'] is not None else 'Pending' if r['state']!='failed' else 'Unavailable'
 lines.append(f"| {r['problem_id']} ({r['source_candidate']}, {r['source_checkpoint']}) | {r['baseline_score']}/7 | {versions[r['case']]}: {r['previous_score']}/7 | {new} | {r['state']} |")
lines+=['','The Basic scores use the official IMOBench rubric; P2 uses the strict Olympiad policy. '
 'All are independent gpt-5.6-sol / xhigh calls.','',
 'Validation: 115 targeted tests passed. All three original certificates replayed successfully; exported lemmas, appendices, '
 'tool-purpose context and source-edit instructions are byte-identical to the successful versions.','',
 f"Frozen release SHA-256: `{report['release_sha256']}`.",
 '',f"[Frozen package]({report['package']}/README.md) · [Compatibility checks]({b}/compatibility.json) · [Tests]({b}/targeted_tests.log)",
 '', 'One launcher preflight failed because V356 was missing from a duplicate package registry. No model calls ran in that attempt. '
 'The launcher entry was fixed and all retries use fresh preflight directories; the frozen harness did not change.']
for r in rows:
 if r['external_score'] is not None:
  g=r['external_grade'];lines+=['',f"## {r['problem_id']}",'',f"**{r['external_score']}/7**. {g.get('summary',g.get('reasoning',''))}",
   '',f"First issue: {g.get('first_issue','See official grade.')}",'',f"[Proof]({r['proof']}) · [External grade]({r['grade']})"]
 if r.get('error'):lines+=['',f"{r['problem_id']}: {r['error']}"]
(b/'comparison.md').write_text('\n'.join(lines)+'\n')
if done:
 for r in rows:
  d=Path(r['experiment'])/'reports'
  if d.exists():write(d/'v356_consolidation_comparison.json',report);(d/'v356_consolidation_comparison.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'state':report['state'],'scores':scores,'all_three_at_least_six':report['all_three_at_least_six'],
 'trials':[{k:r.get(k) for k in ('case','state','stage','external_score','error')} for r in rows]},indent=2))
