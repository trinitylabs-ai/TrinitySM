"""Preserved real assumptions, semantic gating, and the full evidence provider."""
import copy
import json
from pathlib import Path

import pytest

from . import geometry_program as compiler, geometry_workflow as workflow
from . import proof_harness as harness, real_branches as real
from .test_geometry_program import program
from .test_geometry_workflow import sources
from .test_proof_harness import decisions
from .test_division_audit_repair import audit

THEOREM='The real numbers x and y are positive and have equal squares.'
DRAFT=program('''symbols = x, y
premise = x_positive :: (gt x 0) :: @source:S0001
premise = y_positive :: (gt y 0) :: @source:S0001
premise = squares :: (eq (pow x 2) (pow y 2)) :: @source:S0001
target = equal :: (eq x y)''')


def test_compiler_preserves_strict_weak_nonzero_and_rational_signs():
    raw=program('''symbols = x, y
premise = denominator :: (ne y 0) :: @source:S0001
premise = weak :: (ge x 0) :: @source:S0001
premise = quotient :: (gt (div x y) 0) :: @source:S0001
premise = equation :: (eq (pow x 2) (pow y 2)) :: @source:S0001
target = equal :: (eq x y)''')
    compiled=compiler.compile_program(raw,'The listed conditions hold.')
    context=real.Context(compiled['system'])
    facts={label:(relation,str(value)) for relation,value,label in context.conditions}
    assert facts=={'weak':('ge','x'),'quotient':('gt','x*y'),'denominator':('ne','y')}
    admission=compiled['report']['admitted_real_conditions']
    assert admission['original_domains_checked']
    assert not admission['source_semantics_verified']
    assert real.solve(compiled['system'])['verified']


@pytest.mark.parametrize('accepted',[False,True])
def test_branch_evidence_reaches_synthesis_only_after_semantic_audit(tmp_path,monkeypatch,accepted):
    root,proof=sources(tmp_path)
    detection,matched=decisions(proof,operation='exact_geometry')
    acq=root/'01_acquisition'
    for name,text in [('input/original_theorem.md',THEOREM),('input/resolver1_proof.md',proof),
                      ('01_detection/detection.md',detection),('02_matcher/matcher.md',matched)]:
        harness.base.write_text(acq/name,text)
    matcher=harness.base._parse_matcher(matched,harness.acquisition.protocol.parse_detection(detection)['desired_exact_fact'],harness.matcher_operations())
    monkeypatch.setattr(workflow.certificate,'validate_markdown_budget_forcing',lambda *a,**kw:None)
    events=[];providers=[]
    def caller(**kw):
        events.append(kw['stage'])
        if kw['stage']=='geometry_formalization':text=DRAFT
        else:
            assert 'admitted_real_conditions' in kw['user_prompt']
            assert 'source_semantics_verified' in kw['user_prompt']
            assert 'certificate.json' not in kw['user_prompt']
            text=audit(accepted)
        return text,kw['parser'](text),{}
    def synthesize(**kw):
        provider=kw['provider'];providers.append(provider)
        evidence=provider.materialize()
        assert evidence.verification['real_branch_derivation_supplied']
        assert evidence.verification['geometry_compilation_replayed']
        assert 'Case 1' in evidence.appendix_markdown and 'Case 2' in evidence.appendix_markdown
        assert evidence.appendix_markdown.count('>0')==2
        assert not evidence.appendix_in_rewriter_prompt
        assert json.loads(provider.paths['certificate'].read_text())['schema']==real.SCHEMA
        return {'state':'test_synthesis_only'}
    monkeypatch.setattr(workflow.appendix_synthesis,'run',synthesize)
    if not accepted:
        monkeypatch.setattr(workflow,'certificate_search',lambda *a,**kw:pytest.fail('rejected source reached search'))
    config=harness.Config(cycles=1)
    track=root/'branch_track'
    result=workflow.run_track(root,track,config=config,seed=19,matcher=matcher,
        select=lambda p,fn:fn(),should_stop=lambda:False,caller=caller)
    assert result['state']=='completed',result
    assert result['exact_verified']==accepted
    assert len(providers)==int(accepted)
    assert events==['geometry_formalization','geometry_semantic_audit']
    if accepted:
        provider=providers[0]
        original=provider.paths['system'].read_text()
        changed=json.loads(original);changed['real_conditions']=[]
        provider.paths['system'].write_text(json.dumps(changed))
        with pytest.raises(ValueError,match='source drift'):provider.materialize()
        inputs={key:provider.paths[key] for key in ['theorem','proof','detection','matcher']}
        with pytest.raises(ValueError,match='target/source mismatch'):
            workflow.GeometryProvider(inputs=inputs,cycle=track/'cycles/cycle_01',
                certificate_root=provider.paths['system'].parent,matcher=matcher,config=config)
        provider.paths['system'].write_text(original)
        assert provider.materialize().verification['verified']


def test_inconclusive_real_search_falls_back_and_legacy_system_skips_it(tmp_path,monkeypatch):
    compiled=compiler.compile_program(DRAFT,THEOREM)
    calls=[]
    def bounded(function,args,*limits):
        calls.append(function)
        return {'verified':False,'verdict':'INCONCLUSIVE','reason':'test budget'}
    monkeypatch.setattr(workflow,'bounded',bounded)
    monkeypatch.setattr(compiler,'guard_subsets',lambda system:[])
    result=workflow.certificate_search(compiled,tmp_path/'new',timeout=30,memory=4096)
    assert not result['exact_verified']
    assert calls==[real.solve,workflow.division.solve]
    calls.clear();legacy=copy.deepcopy(compiled);legacy['system'].pop('real_conditions')
    result=workflow.certificate_search(legacy,tmp_path/'legacy',timeout=30,memory=4096)
    assert not result['exact_verified'] and calls==[workflow.division.solve]
