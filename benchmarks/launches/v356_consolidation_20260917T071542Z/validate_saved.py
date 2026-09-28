from pathlib import Path
import hashlib,importlib,json,sys,time
ROOT=Path('/opt/proof-workshop');sys.path.insert(0,str(ROOT))
B=Path(Path('/tmp/v356_launch_path').read_text().strip())
NEW='cognitive_well_harness_v0_3_356_v349_discrete_consolidation_20260917'
CASES=[
 ('p2','geometry','cognitive_well_harness_v0_3_349_checked_real_branches_20260916',
  'benchmarks/imo2026/results/p2_c3_t07r02_real_branches_v349_20260916T232047Z/generation/run'),
 ('basic008','root','cognitive_well_harness_v0_3_344_root_syntax_normalization_20260916',
  'benchmarks/imo-proofbench/basic/results/basic_p008_t10_r01_raw_roots_v344_20260916T155741Z/generation/run'),
 ('basic009','discrete','cognitive_well_harness_v0_3_353_discrete_synthesis_binding_20260917',
  'benchmarks/imo-proofbench/basic/results/basic009_t07_r01_r1c3_v352_20260917T033155Z/generation/run')]
def read(p):return json.loads(p.read_text())
def digest(text):return hashlib.sha256(text.encode()).hexdigest()
def provider(package,source,kind):
 h=importlib.import_module(package+'.proof_harness');w=importlib.import_module(package+'.'+kind+'_workflow')
 config=h.Config.from_saved(read(source/'manifest.json')['config']);a=source/'01_acquisition'
 paths={'theorem':a/'input/original_theorem.md','proof':a/'input/resolver1_proof.md',
  'detection':a/'01_detection/detection.md','matcher':a/'02_matcher/matcher.md'}
 detection=h.acquisition.protocol.parse_detection(paths['detection'].read_text().strip())
 parser=getattr(h,'parse_matcher',h.base._parse_matcher)
 matcher=parser(paths['matcher'].read_text().strip(),detection['desired_exact_fact'],h.matcher_operations(config.excluded_operations))
 cycle=Path(read(source/'selection.json')['request_path']).parent
 kwargs=dict(inputs=paths,cycle=cycle,matcher=matcher,config=config)
 if kind=='geometry':
  row=next(r for r in read(cycle.parent.parent/'result.json')['cycles'] if r['cycle']==int(cycle.name.removeprefix('cycle_')))
  kwargs['certificate_root']=Path(row['certificate_root'])
 return getattr(w,{'geometry':'GeometryProvider','root':'RootProvider','discrete':'DiscreteProvider'}[kind])(**kwargs)
def main():
 resume=importlib.import_module(NEW+'.selected_resume');purpose=importlib.import_module(NEW+'.synthesis_core.tool_purpose')
 results=[]
 for name,kind,old,relative in CASES:
  start=time.monotonic();source=ROOT/relative
  original=provider(old,source,kind).materialize()
  native,config,new_provider,task,compiled,record,workflow=resume.prepare(source,source/'input/problem.json',source/'input/source_proof.md')
  current=new_provider.materialize()
  assert current.markdown==original.markdown, name+' lemma changed'
  assert current.appendix_markdown==original.appendix_markdown, name+' appendix changed'
  assert current.tool_record==original.tool_record and dict(current.source_artifacts)==dict(original.source_artifacts)
  previous_purpose=importlib.import_module(old+'.synthesis_core.tool_purpose')
  assert purpose.render_tool_purpose(task,current)==previous_purpose.render_tool_purpose(task,original)
  assert purpose.explicit_update_source(task,current)==previous_purpose.explicit_update_source(task,original)
  target=B/'compatibility'/name;target.mkdir(parents=True)
  (target/'lemma.md').write_text(current.markdown);(target/'appendix.md').write_text(current.appendix_markdown)
  (target/'verification.json').write_text(json.dumps(current.verification,indent=2)+'\n')
  (target/'resume.json').write_text(json.dumps(record,indent=2)+'\n')
  result={'case':name,'baseline_package':old,'source_run':str(source),'operation':record['operation'],
   'certificate_replayed':True,'original_selection_reused':True,'statement_byte_identical':True,'appendix_byte_identical':True,
   'tool_purpose_byte_identical':True,'explicit_source_update_identical':True,'certificate_sources_unchanged':True,
   'statement_sha256':digest(current.markdown),'appendix_sha256':digest(current.appendix_markdown),
   'new_model_calls':0,'seconds':time.monotonic()-start}
  results.append(result);print(json.dumps(result),flush=True)
 (B/'compatibility.json').write_text(json.dumps({'passed':True,'cases':results},indent=2)+'\n')
 print('ALL THREE SAVED SUCCESS PATHS MATCH',flush=True)
if __name__=='__main__':main()
