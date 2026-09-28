
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import fcntl,json,subprocess,time
HERE=Path(__file__).resolve().parent
C=json.loads((HERE/'batch.json').read_text())
def read(p):
 try:return json.loads(p.read_text())
 except (FileNotFoundError,json.JSONDecodeError):return {}
def now():return datetime.now(timezone.utc).isoformat()
def run(row):
 local=Path(row['launch'])
 with (local/'supervisor.log').open('w') as out:
  proc=subprocess.run(['/usr/bin/python3','-u','-B',str(local/'run_trial.py')],cwd=C['workspace'],stdout=out,stderr=subprocess.STDOUT)
 return {'candidate':row['candidate'],'returncode':proc.returncode,'status':read(local/'status.json')}
def progress(done=False):
 rows=[]
 for row in C['trials']:
  e=Path(row['experiment']);n=e/'generation/run';s=read(n/'status.json');sup=read(Path(row['launch'])/'status.json')
  report=read(e/'reports/run_summary.json')
  rows.append({**row,'supervisor':sup,'native_stage':s.get('stage'),'native_state':s.get('state'),'outcome':s.get('outcome'),
   'drafts_returned':len(list(n.glob('02_formalizations/sample_*/cycles/cycle_*/parser.json'))),
   'compiled':len(list(n.glob('02_formalizations/sample_*/cycles/cycle_*/compilation.json'))),
   'calls':[{k:v for k,v in x.items() if k in ('stage','state')} for p in n.rglob('model_budget.json') for x in read(p).get('calls',[])],
   'external_grade':report.get('external_grade')})
 data={'state':'completed' if done else 'running','updated_at':now(),'trials':rows}
 tmp=HERE/'status.tmp';tmp.write_text(json.dumps(data,indent=2)+'\n');tmp.replace(HERE/'status.json')
 if done:(HERE/'combined_results.json').write_text(json.dumps(rows,indent=2)+'\n')
lock=(HERE/'.batch.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
with ThreadPoolExecutor(max_workers=C['concurrency']) as pool:
 futures=[pool.submit(run,r) for r in C['trials']]
 while not all(f.done() for f in futures):progress();time.sleep(10)
 results=[f.result() for f in futures]
progress(True)
(HERE/'completion.json').write_text(json.dumps({'completed_at':now(),'results':results},indent=2)+'\n')
