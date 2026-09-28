"""Domain diagnostics must inform retries without supplying mathematical facts."""
import copy
import json
from types import SimpleNamespace

import pytest
import sympy as sp

from . import geometry_domain_feedback as feedback, geometry_program as geometry
from . import geometry_workflow as workflow, proof_harness as harness
from .test_geometry_program import program
from .test_geometry_workflow import sources, THEOREM
from .test_proof_harness import decisions
from .test_division_audit_repair import audit
from cognitive_well_harness_v0_3_347_positive_multiple_domains_20260916 import geometry_program as parent


def retained_draft(name='d'):
    return program(f'''symbols = {name}, y
define = hidden :: (div {name} {name})
define = alias :: hidden
define = unrelated :: (div y y)
premise = positive :: (gt y 0) :: The condition holds.
premise = equation :: (eq y 1) :: The condition holds.
retain = omitted :: {name} is nonzero :: The condition holds. :: Needed for cancellation.
target = identity :: (eq alias 1)''')


@pytest.mark.parametrize('name',['d','parameter'])
def test_rejection_reports_actual_context_without_assuming_retained_prose(name):
    raw=retained_draft(name);theorem='The condition holds.'
    with pytest.raises(ValueError) as previous:parent.compile_program(raw,theorem)
    with pytest.raises(feedback.DomainFailure) as failure:geometry.compile_program(raw,theorem)
    assert str(failure.value)==str(previous.value)
    report=failure.value.domain_diagnostics
    assert report['failed_conditions'][0]['expression']==name
    assert report['failed_conditions'][0]['relation']=='ne'
    assert report['available_sign_facts'][0]['label']=='positive'
    assert not report['available_nonzero_facts']
    assert report['retained_only_as_prose'][0]['label']=='omitted'
    assert report['encoded_equations_not_used_for_domains'][0]['label']=='equation'
    assert not report['equations_used_for_domain_proofs']
    assert {r['label'] for r in report['definitions_sharing_failed_domain']}=={'hidden','alias'}
    assert report['source_semantics_verified'] is False
    assert raw==retained_draft(name)
    with pytest.raises(feedback.DomainFailure) as repeated:geometry.compile_program(raw,theorem)
    assert report==repeated.value.domain_diagnostics


@pytest.mark.parametrize('premises',[
    'premise = self :: (gt (mul (div x x) x) 0) :: The condition holds.',
    'premise = first :: (ne (div x y) 0) :: The condition holds.\npremise = second :: (ne (div y x) 0) :: The condition holds.',
])
def test_pending_source_conditions_are_never_reported_as_available(premises):
    raw=program('symbols = x, y\n'+premises+'\ntarget = identity :: (eq x x)')
    with pytest.raises(feedback.DomainFailure) as failure:geometry.compile_program(raw,'The condition holds.')
    report=failure.value.domain_diagnostics
    assert report['stage']=='source_comparison_domain'
    assert not report['available_nonzero_facts'] and not report['available_sign_facts']
    assert report['failed_conditions']
    assert len(report['failed_conditions'])==len(report['source_premises'])


def test_cleared_equation_has_no_claim_of_domain_admission():
    raw=program('''symbols = x, d
premise = quotient :: (eq (div x d) 1) :: The condition holds.
target = identity :: (eq x x)''')
    with pytest.raises(feedback.DomainFailure) as failure:geometry.compile_program(raw,'The condition holds.')
    report=failure.value.domain_diagnostics
    assert report['stage']=='rational_premise_domain'
    assert report['failed_conditions'][0]['source_label']=='quotient'
    assert report['failed_conditions'][0]['expression']=='d'
    assert report['encoded_equations_not_used_for_domains'][0]['domain_status']=='not_asserted_by_this_diagnostic'


def test_successful_compilation_preserves_math_and_adds_admitted_conditions(monkeypatch):
    raw=program('''symbols = d
premise = guard :: (ne d 0) :: The condition holds.
retain = unrelated :: The condition holds. :: Not needed for the identity.
target = identity :: (eq (div d d) 1)''')
    monkeypatch.setattr(feedback,'build',lambda *a:pytest.fail('diagnostic on success'))
    compiled=geometry.compile_program(raw,'The condition holds.')
    conditions=compiled['system'].pop('real_conditions')
    admission=compiled['report'].pop('admitted_real_conditions')
    assert [row['relation'] for row in conditions]==['ne']
    assert admission['conditions']==conditions and admission['original_domains_checked']
    assert admission['source_semantics_verified'] is False
    assert compiled==parent.compile_program(raw,'The condition holds.')


def test_structured_failure_survives_real_worker_and_reaches_inspection():
    raw=retained_draft()
    with pytest.raises(feedback.DomainFailure) as failure:
        workflow.compile_bounded(raw,'The condition holds.',timeout=10)
    result=workflow.inspect(raw,'The condition holds.')
    assert not result['parser_valid'] and 'proposal' not in result
    assert result['domain_diagnostics']==failure.value.domain_diagnostics
    assert 'Retained only as prose' in result['parser_feedback']
    assert 'omitted: d is nonzero' in result['parser_feedback']
    assert 'A bounded domain proof failed' in result['parser_feedback']


def test_plain_parser_errors_and_declines_remain_plain():
    bad=workflow.inspect('Invalid input.','The condition holds.')
    assert not bad['parser_valid'] and 'domain_diagnostics' not in bad
    declined=workflow.inspect('# Decision\nNO_TOOL\n\n# Reason\nUnsupported.','The condition holds.')
    assert declined['parser_valid'] and not declined['proposal']['call_requested']
    assert 'domain_diagnostics' not in declined


def test_auxiliary_fallback_preserves_structured_failure(monkeypatch):
    monkeypatch.setattr(geometry.syntax,'MAX_EXPANDED_OPERATIONS',800)
    raw=program('''symbols = x, y, z
define = H :: (div (pow (add x y z) 12) (sub x y))
define = K :: (pow H 2)
target = identity :: (eq K K)''')
    with pytest.raises(feedback.DomainFailure) as failure:geometry.compile_program(raw,'An identity.')
    assert str(failure.value).startswith('auxiliary fallback after')
    assert failure.value.domain_diagnostics['failed_conditions']


def test_diagnostic_is_bounded_deterministic_and_calls_no_prover():
    x=sp.Symbol('x',real=True);long='huge '*2000
    parsed={'retained':[{'label':str(i),'description':long,'excerpt':long,'reason':long} for i in range(100)],
            'premises':[(str(i),['eq',long,0],long) for i in range(100)],'definitions':[]}
    ev=SimpleNamespace(definition_obligations={})
    signs=SimpleNamespace(facts=[(x,True,str(i)) for i in range(100)],nonzeros=[(x,str(i)) for i in range(100)])
    before=copy.deepcopy(parsed)
    args=(parsed,ev,signs,[(str(i),x) for i in range(100)],[feedback.condition(x,'ne','division')],'construction_domain')
    report=feedback.build(*args)
    assert report==feedback.build(*args) and parsed==before
    assert report['truncated']
    assert len(json.dumps(report,ensure_ascii=True))<=feedback.MAX_DIAGNOSTIC_CHARACTERS
    rendered=feedback.render(report)
    assert len(rendered)<=feedback.MAX_FEEDBACK_CHARACTERS
    assert 'incomplete' in rendered and 'Failed conditions' in rendered
    assert len(feedback.render_failure(long,report))<=feedback.MAX_FEEDBACK_CHARACTERS


@pytest.mark.parametrize('accepted',[False,True])
def test_domain_feedback_reaches_retry_and_semantic_audit_still_gates_tools(tmp_path,monkeypatch,accepted):
    root,proof=sources(tmp_path)
    detection,matched=decisions(proof,operation='exact_geometry')
    acq=root/'01_acquisition'
    for name,text in [('input/original_theorem.md',THEOREM),('input/resolver1_proof.md',proof),
                      ('01_detection/detection.md',detection),('02_matcher/matcher.md',matched)]:
        harness.base.write_text(acq/name,text)
    matcher=harness.base._parse_matcher(matched,harness.acquisition.protocol.parse_detection(detection)['desired_exact_fact'],harness.matcher_operations())
    monkeypatch.setattr(workflow.certificate,'validate_markdown_budget_forcing',lambda *a,**kw:None)
    bad=program('''symbols = x
retain = positivity :: The positive number :: Not encoded.
target = cancellation :: (eq (div x x) 1)''')
    fixed=program('''symbols = x
premise = positivity :: (gt x 0) :: The positive number
target = cancellation :: (eq (div x x) 1)''')
    events=[];tools=[]
    def caller(**kwargs):
        stage=kwargs['stage'];events.append(stage)
        if len(events)==1:text=bad
        elif len(events)==2:
            assert stage=='geometry_formalization'
            assert 'Retained only as prose' in kwargs['user_prompt']
            assert 'Failed conditions' in kwargs['user_prompt']
            assert 'positivity: The positive number' in kwargs['user_prompt']
            assert 'HIDDEN_REFERENCE_SENTINEL' not in kwargs['user_prompt']
            text=fixed
        else:
            assert stage=='geometry_semantic_audit'
            assert 'Domain-check context' not in kwargs['user_prompt']
            text=audit(accepted)
        return text,kwargs['parser'](text),{}
    def search(*args,**kwargs):
        tools.append(True);return {'exact_verified':False,'stages':[]}
    monkeypatch.setattr(workflow,'certificate_search',search)
    result=workflow.run_track(root,root/'diagnostic_track',config=harness.Config(cycles=2),seed=17,
        matcher=matcher,select=lambda *a:pytest.fail('unexpected synthesis'),should_stop=lambda:False,caller=caller)
    assert result['state']=='completed',result
    assert events==['geometry_formalization','geometry_formalization','geometry_semantic_audit']
    assert len(tools)==int(accepted)
    saved=json.loads((root/'diagnostic_track/cycles/cycle_01/parser.json').read_text())
    assert saved['domain_diagnostics']['retained_only_as_prose'][0]['label']=='positivity'
