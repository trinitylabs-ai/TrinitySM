from pathlib import Path
import json,hashlib
b=Path(Path('/tmp/v356_launch_path').read_text().strip());out=[]
for c in ('p2','basic008','basic009'):
 s=json.loads((b/c/'selection.json').read_text());n=Path(s['experiment'])/'generation/run/synthesis';old=Path(s['previous_experiment'])/'generation/run'
 sources=list(old.glob('synthesis/02_rewrite/cycle_01/model/attempt_01_cap_32768/*.user_prompt.txt')) or list(old.glob('02_formalizations/sample_*/cycles/cycle_*/synthesis/02_rewrite/cycle_01/model/attempt_01_cap_32768/*.user_prompt.txt'))
 dest=list(n.glob('02_rewrite/cycle_01/model/attempt_01_cap_32768/*.user_prompt.txt'))
 if not dest:print(c,'awaiting prompt');continue
 matches=[p for p in sources if p.read_bytes()==dest[0].read_bytes()]
 item={'case':c,'new_prompt':str(dest[0]),'byte_identical_to_successful_source':bool(matches),'matching_original_prompt':str(matches[0]) if matches else None,'sha256':hashlib.sha256(dest[0].read_bytes()).hexdigest()}
 if matches:
  new_system=dest[0].with_name(dest[0].name.replace('.user_prompt.txt','.prompt.txt'));old_system=matches[0].with_name(matches[0].name.replace('.user_prompt.txt','.prompt.txt'))
  item['system_prompt_byte_identical']=new_system.read_bytes()==old_system.read_bytes()
 out.append(item);print(c,item['byte_identical_to_successful_source'],item.get('system_prompt_byte_identical'))
(b/'first_rewrite_prompt_compatibility.json').write_text(json.dumps(out,indent=2)+'\n')
