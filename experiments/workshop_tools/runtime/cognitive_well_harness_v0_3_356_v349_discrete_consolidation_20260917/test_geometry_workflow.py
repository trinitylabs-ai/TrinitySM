"""Automatic dispatch, isolated semantic gate, and evidence provenance tests."""
from pathlib import Path
import json
import pytest
from . import proof_harness as harness, geometry_workflow as workflow
from .test_geometry_program import program
from .test_proof_harness import decisions
from .test_division_audit_repair import audit

THEOREM='The positive number satisfies the displayed equation.'
BODY='''symbols = x, y
premise = positive :: (gt x 0) :: The positive number
premise = relation :: (eq (mul x y) x) :: satisfies the displayed equation
target = desired :: (eq y 1)'''


def sources(tmp_path):
    problem=tmp_path/'source.json';proof=tmp_path/'proof.md'
    problem.write_text(json.dumps({'problem_id':'synthetic','statement':THEOREM,'reference_solution':'HIDDEN_REFERENCE_SENTINEL'}))
    proof.write_text('The conclusion follows from the displayed equation by cancellation.')
    root=tmp_path/'run'
    harness.run(problem_file=problem,proof_file=proof,output=root)
    return root,proof.read_text()


@pytest.mark.parametrize('operation',['exact_geometry','rational_identity'])
def test_new_matcher_operation_reaches_geometry_route(tmp_path,monkeypatch,operation):
    problem=tmp_path/'source.json';proof=tmp_path/'proof.md'
    problem.write_text(json.dumps({'problem_id':'synthetic','statement':THEOREM,'reference_solution':'HIDDEN_REFERENCE_SENTINEL'}))
    proof.write_text('An unsupported algebraic conclusion follows.')
    detection,matched=decisions(proof.read_text(),operation=operation)
    events=[]
    class Calls:
        def __init__(self,*a,**kw):pass
        def __call__(self,**kw):
            assert 'HIDDEN_REFERENCE_SENTINEL' not in kw['user_prompt']
            answer=detection if kw['stage'].endswith('gap_detection') else matched
            return answer,kw['parser'](answer),{}
    monkeypatch.setattr(harness.rewrite,'BudgetedCalls',Calls)
    def track(output,root,**kw):
        events.append(kw['matcher']['operation'])
        return {'state':'completed','exact_verified':False}
    monkeypatch.setattr(workflow,'run_track',track)
    result=harness.run(problem_file=problem,proof_file=proof,output=tmp_path/'run',execute_models=True,
                       config=harness.Config(batch_size=1,workers=1,cycles=1))
    assert events==[operation]
    assert result['outcome']=='NO_CERTIFIED_REWRITE'


@pytest.mark.parametrize('operation',['exact_geometry','rational_identity'])
@pytest.mark.parametrize('accepted',[True,False])
@pytest.mark.parametrize('shorthand',[True,False])
@pytest.mark.parametrize('source_mode',['literal','reference','quoted'])
def test_same_draft_audit_controls_certificate_and_synthesis(tmp_path,monkeypatch,accepted,operation,shorthand,source_mode):
    root,proof=sources(tmp_path)
    detection,matched=decisions(proof,operation=operation)
    acq=root/'01_acquisition'
    for name,text in [('input/original_theorem.md',THEOREM),('input/resolver1_proof.md',proof),
                      ('01_detection/detection.md',detection),('02_matcher/matcher.md',matched)]:
        harness.base.write_text(acq/name,text)
    matcher=harness.base._parse_matcher(matched,harness.acquisition.protocol.parse_detection(detection)['desired_exact_fact'],harness.matcher_operations())
    monkeypatch.setattr(workflow.certificate,'validate_markdown_budget_forcing',lambda *a,**kw:None)
    events=[];providers=[];synthesis_events=[]
    lines=[]
    for line in BODY.splitlines():
        if line.startswith('premise'):
            prefix,excerpt=line.rsplit(' :: ',1)
            if source_mode=='reference':excerpt='@source:S0001'
            elif source_mode=='quoted':excerpt='"'+excerpt+'"'
            line=prefix+' :: '+excerpt
        lines.append(line)
    canonical_body='\n'.join(lines)
    def calls(**kw):
        events.append(kw['stage'])
        body=canonical_body.replace('premise = ','premise ').replace('target = ','target ') if shorthand else canonical_body
        answer=program(body) if kw['stage']=='geometry_formalization' else audit(accepted)
        assert 'HIDDEN_REFERENCE_SENTINEL' not in kw['system_prompt']+kw['user_prompt']
        if kw['stage']=='geometry_formalization':
            assert '# Exact Source Spans' in kw['user_prompt'] and '@source:S0001' in kw['user_prompt']
        if kw['stage']=='geometry_semantic_audit':
            assert '"source_bindings"' in kw['user_prompt']
            assert 'Deterministic Geometry Compilation' in kw['user_prompt']
            assert 'certificate.json' not in kw['user_prompt']
        return answer,kw['parser'](answer),{}
    actual_synthesis=workflow.appendix_synthesis.run
    core=workflow.appendix_synthesis.rewrite.pipeline.synthesis_pipeline
    monkeypatch.setattr(workflow.appendix_synthesis.rewrite.pipeline,
        '_verify_synthesis_budget_forcing',lambda **kw:[])
    def synthesis(**kw):
        providers.append(kw['provider'])
        evidence=kw['provider'].materialize()
        assert evidence.verification['geometry_compilation_replayed']
        assert not evidence.appendix_in_rewriter_prompt
        assert json.loads(kw['provider'].paths['normalization'].read_text())['applied']==shorthand
        assert kw['provider'].paths['normalized_draft'].read_text().strip()==program(canonical_body)
        def model_call(**request):
            synthesis_events.append(request['stage'])
            assert operation in request['user_prompt']
            assert 'HIDDEN_REFERENCE_SENTINEL' not in request['user_prompt']
            if request['stage'].endswith('rewrite'):
                assert evidence.appendix_markdown not in request['user_prompt']
                answer='Assume x is positive and xy=x. The checked cancellation lemma applies.\n\n[[VERIFIED_EXACT_EVIDENCE]]\n\nSince x is nonzero, the conclusion is y=1.'
                answer+='\n\n'+('More explicitly, subtract x from both sides of xy=x to obtain x(y-1)=0. '
                    'A positive real number cannot equal zero. Consequently x has a multiplicative inverse, '
                    'so multiplying this last equality by that inverse gives y-1=0. Adding one to both sides '
                    'gives the required equality y=1. Conversely, substituting y=1 into the original equation '
                    'gives x=x, so the claimed conclusion is consistent with every positive value of x. '
                    'The excluded case x=0 would not permit this cancellation and is ruled out precisely '
                    'by the positivity hypothesis. All divisions in this argument therefore have a nonzero denominator.')
            else:
                assert evidence.appendix_markdown in request['user_prompt']
                answer='# Decision\n\nPASS\n\n# Checks\n\n'+'\n'.join(
                    '- '+name+': PASS' for name in core.protocol.PROOF_AUDIT_CHECKS)
                answer+='\n\n# Gap Closure\n\n'+'\n'.join(
                    '- '+name+': The displayed positive cancellation establishes y=1.'
                    for name in core.tool_purpose.GAP_CLOSURE_LABELS)
                answer+='\n\n# Issues\n\nNONE'
            return answer,request['parser'](answer),{}
        kw['model_call']=model_call
        return actual_synthesis(**kw)
    monkeypatch.setattr(workflow.appendix_synthesis,'run',synthesis)
    if not accepted:
        monkeypatch.setattr(workflow,'certificate_search',lambda *a,**k:pytest.fail('rejected draft reached exact backend'))
    result=workflow.run_track(root,root/'02_formalizations/sample_01',config=harness.Config(cycles=1),
        seed=1,matcher=matcher,select=lambda p,fn:fn(),should_stop=lambda:False,caller=calls)
    assert result['state']=='completed',result
    assert result['exact_verified']==accepted
    assert events==['geometry_formalization','geometry_semantic_audit']
    if accepted:
        assert synthesis_events==[
            'modular_exact_evidence_whole_proof_rewrite',
            'modular_exact_evidence_whole_proof_audit']*2
        provider=providers[0]
        for name in ['normalization','normalized_draft','compilation','theorem']:
            saved=provider.paths[name].read_bytes()
            provider.paths[name].write_text('Changed after audit')
            with pytest.raises(ValueError,match='source drift'):provider.materialize()
            provider.paths[name].write_bytes(saved)
        provider.paths['draft'].write_text(program(BODY)+'\nChanged after audit')
        with pytest.raises(ValueError,match='source drift'):provider.materialize()


def test_runtime_has_no_benchmark_fixture_or_adapter_import():
    from . import geometry_program, geometry_normalization, shared_feedback, source_binding, relative_sign, guard_closure, real_branches
    import ast
    for module in [geometry_program,geometry_normalization,shared_feedback,source_binding,relative_sign,guard_closure,real_branches,workflow]:
        source=Path(module.__file__).read_text()
        imports=[n for n in ast.walk(ast.parse(source)) if isinstance(n,(ast.Import,ast.ImportFrom))]
        names=[n.module for n in imports if isinstance(n,ast.ImportFrom)]
        assert not any(name and ('benchmark' in name or 'experiment' in name or 'test_' in name) for name in names)
        for forbidden in ['PB-Advanced-', 'PB-Basic-', 'imo2026_p2', 't07_r02', 'hand_checked_coordinate_certificate', 'legacy_problem_specific_adapters']:
            assert forbidden not in source
