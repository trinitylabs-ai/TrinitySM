"""Scripted comparator response with real transport bindings."""
import hashlib
from pathlib import Path

def sample(winner='A'):
    text = '# Proof comparison\n\n'
    for label in ('A','B'):
        text += f'## Proof {label}\nEstablished theorem: Full quantified claim.\nClaim gap: NONE, all cases covered.\nQualifications and supplied repairs: NONE.\nDecisive checks: Lines 1-3 justify the conclusion.\n\n'
    return text + f'## Decision\nWinner: {winner}\nReason: The stated justification is stronger.\n'

def response(kw, winner='A'):
    sha=lambda data:hashlib.sha256(data).hexdigest()
    folder=Path(kw['output_dir']);folder.mkdir(parents=True,exist_ok=True)
    text=sample(winner)
    (folder/'system.md').write_text(kw['system_prompt']);(folder/'input.md').write_text(kw['user_prompt']);(folder/'final.md').write_text(text)
    return {'text':text,'final_sha256':sha(text.encode()),'final_path':str(folder/'final.md'),
            'metadata':{'prompt_sha256':sha(kw['system_prompt'].encode()),'user_prompt_sha256':sha(kw['user_prompt'].encode()),
            'model':kw['model'],'system_prompt_path':str(folder/'system.md'),'user_prompt_path':str(folder/'input.md')}}
