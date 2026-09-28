import json
import pytest
from . import proof_harness as h, geometry_workflow
from .test_proof_harness import sources, decisions


def saved(tmp_path,monkeypatch):
    problem,proof=sources(tmp_path)
    old=tmp_path/'old'
    h.run(problem_file=problem,proof_file=proof,output=old)
    detection,matcher=decisions(proof.read_text().strip(),operation='exact_geometry')
    root=old/'01_acquisition'
    h.base.write_text(root/'input/original_theorem.md',json.loads((old/'input/problem.json').read_text())['statement'])
    h.base.write_text(root/'input/resolver1_proof.md',proof.read_text().strip())
    calls=[]
    for folder,stage,text in [('01_detection','direct_laurent_gap_detection',detection),
                               ('02_matcher','direct_laurent_operation_matcher',matcher)]:
        h.base.write_text(root/folder/('detection.md' if folder=='01_detection' else 'matcher.md'),text)
        calls.append({'stage':stage,'state':'completed','attempt':1,'cap':32768})
        h.rewrite.write_record(root/folder/'model/attempt_01_cap_32768'/f'{stage}.metadata.json',
                               {'config':{'timeout_seconds':600}})
    h.rewrite.write_record(root/'model_budget.json',{'calls':calls})
    h.rewrite.write_record(root/'manifest.json',{'allowed_matcher_operations':list(h.matcher_operations())})
    checked=[]
    monkeypatch.setattr(h.fresh.certificate,'validate_markdown_budget_forcing',lambda *a,**k:checked.append(k['expected_stage']))
    monkeypatch.setattr(h.rewrite,'BudgetedCalls',lambda *a,**k:pytest.fail('acquisition reuse called a model'))
    return problem,proof,old,checked


def test_reuse_starts_at_formalization_and_records_zero_new_calls(tmp_path,monkeypatch):
    problem,proof,old,checked=saved(tmp_path,monkeypatch)
    events=[]
    def track(*args,**kwargs):
        events.append(kwargs['matcher']['operation']);return {'state':'completed','exact_verified':False}
    monkeypatch.setattr(geometry_workflow,'run_track',track)
    out=tmp_path/'retry'
    result=h.run(problem_file=problem,proof_file=proof,output=out,execute_models=True,
                 acquisition_from=old,config=h.Config(batch_size=1,workers=1,cycles=1))
    assert events==['exact_geometry'] and result['outcome']=='NO_CERTIFIED_REWRITE'
    assert set(checked)=={'direct_laurent_gap_detection','direct_laurent_operation_matcher'}
    assert json.loads((out/'01_acquisition/model_budget.json').read_text())['new_model_calls']==0


@pytest.mark.parametrize('drift',['proof','menu','producer','theorem'])
def test_reuse_rejects_input_menu_and_producer_drift(tmp_path,monkeypatch,drift):
    problem,proof,old,_=saved(tmp_path,monkeypatch)
    if drift=='proof':(old/'input/source_proof.md').write_text('changed')
    elif drift=='menu':h.rewrite.write_record(old/'01_acquisition/manifest.json',{'allowed_matcher_operations':[]})
    elif drift=='producer':h.rewrite.write_record(old/'01_acquisition/model_budget.json',{'calls':[]})
    else:(old/'01_acquisition/input/original_theorem.md').write_text('changed')
    with pytest.raises(ValueError):
        h.run(problem_file=problem,proof_file=proof,output=tmp_path/'new',acquisition_from=old)
