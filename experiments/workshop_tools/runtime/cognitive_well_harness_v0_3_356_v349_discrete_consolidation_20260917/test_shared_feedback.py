"""Concurrent exchange must preserve run isolation and every local evidence gate."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import threading

import pytest

from . import shared_feedback as shared, proof_harness as harness
from . import geometry_workflow as geometry, division_fresh_audited as fresh
from .test_proof_harness import decisions
from .test_geometry_program import program
from .test_geometry_workflow import THEOREM, BODY, sources
from .test_division_audit_repair import audit, write_inputs
from .test_rational_division import FORMALIZATION


def board(path, samples=8):
    return shared.Board(path, input_artifacts={'statement':shared.sha('synthetic')}, samples=samples, cycles=3)


def test_concurrent_complete_journal_single_peer_rotation_and_immutable_snapshots(tmp_path):
    exchange=board(tmp_path/'board')
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(lambda s:exchange.lane(s).publish(1,'parser_rejected','Same error','draft '+str(s)),range(1,9)))
    events=[json.loads(p.read_text()) for p in sorted((exchange.root/'events').glob('*.json'))]
    assert len(events)==8 and {e['id'] for e in events}==set(range(1,9))
    assert {e['sample'] for e in events}==set(range(1,9))
    assert exchange.snapshot(1,1)[0]==''
    text,snapshot=exchange.snapshot(1,2)
    assert snapshot['peer_events']==7 and snapshot['unique_observations']==1
    assert len(snapshot['included'])==1 and len(snapshot['included'][0]['event_ids'])==1
    selected=snapshot['selected_peer'];assert selected in range(2,9)
    assert all(('lane '+str(s)+';') not in text for s in range(2,9) if s!=selected)
    before=json.dumps(snapshot,sort_keys=True)
    exchange.lane(2).publish(2,'parser_rejected','Same  error','revised draft')
    current,record=exchange.snapshot(1,3)
    assert record['selected_peer'] != selected and record['selected_peer'] in range(2,9)
    assert record['as_of_event']==9 and snapshot['as_of_event']==8
    assert json.dumps(snapshot,sort_keys=True)==before
    assert exchange.snapshot(1,2)==(text,snapshot)


def test_prompt_budget_keeps_full_journal_but_only_selected_latest_draft_details(tmp_path):
    exchange=board(tmp_path/'board')
    for cycle in range(1,4):
        for sample in range(2,9):
            for kind in ['parser_rejected','semantic_rejected','tool_inconclusive']:
                text=f'{sample}:{cycle}:{kind} '+('long feedback '*1000)+'END_FULL_FEEDBACK'
                exchange.lane(sample).publish(cycle,kind,text,'draft '+str(cycle))
    prompt,record=exchange.snapshot(1,3)
    assert len(prompt)<=shared.MAX_PROMPT_CHARS==6000
    assert all(x['excerpt_truncated'] for x in record['included'])
    assert len(record['included'])==3 and record['selected_cycle']==3
    assert set(record['global_error_categories'])=={'parser_or_compiler_rejection','semantic_audit_rejection','inconclusive_tool_search'}
    events={e['id']:e for p in (exchange.root/'events').glob('*.json') for e in [json.loads(p.read_text())]}
    detail=[events[i] for g in record['included'] for i in g['event_ids']]
    assert {e['sample'] for e in detail}=={record['selected_peer']}
    assert {e['cycle'] for e in detail}=={3}
    assert len(events)==63 and all(e['text'].endswith('END_FULL_FEEDBACK') for e in events.values())
    assert 'END_FULL_FEEDBACK' not in prompt


def test_seeded_choice_is_replayable_given_availability_and_does_not_wait(tmp_path):
    choices=[]
    for index,order in enumerate([list(range(2,9)),list(range(8,1,-1))]):
        exchange=shared.Board(tmp_path/str(index),input_artifacts={'statement':'same'},samples=8,cycles=3,master_seed=37)
        assert exchange.snapshot(1,1)[0]==''
        for sample in order:exchange.lane(sample).publish(1,'parser_rejected','error','draft')
        _,second=exchange.snapshot(1,2);_,third=exchange.snapshot(1,3)
        choices.append((second['selected_peer'],third['selected_peer']))
        assert choices[-1][0]!=choices[-1][1]
    assert choices[0]==choices[1]
    exchange=board(tmp_path/'one-peer',samples=2)
    assert exchange.snapshot(1,2)[1]['selected_peer'] is None
    exchange.lane(2).publish(1,'parser_rejected','error','draft')
    assert exchange.snapshot(1,3)[1]['selected_peer']==2
    exchange=board(tmp_path/'exhausted',samples=2)
    exchange.lane(2).publish(1,'parser_rejected','error','draft')
    assert exchange.snapshot(1,2)[1]['selected_peer']==2
    prompt,last=exchange.snapshot(1,3)
    assert last['selected_peer'] is None and not last['included']
    assert 'parser_or_compiler_rejection' in prompt and 'proceed without waiting' in prompt


def test_only_exact_duplicates_within_selected_draft_are_grouped(tmp_path):
    exchange=board(tmp_path/'board',samples=2)
    for text in ['Same error','Same error','Same  error']:
        exchange.lane(2).publish(1,'parser_rejected',text,'draft')
    _,record=exchange.snapshot(1,2)
    assert record['unique_observations']==2
    assert sorted(len(g['event_ids']) for g in record['included'])==[1,2]


def test_run_isolation_own_feedback_and_saved_prompt_binding(tmp_path):
    first=board(tmp_path/'first',samples=2);second=board(tmp_path/'second',samples=2)
    first.lane(2).publish(1,'semantic_rejected','PEER_ISSUE','foreign draft')
    assert second.snapshot(1,2)[0]==''
    assert first.snapshot(2,2)[0]==''
    prompt=first.lane(1).augment('Current contract',2,tmp_path/'cycle')
    record=json.loads((tmp_path/'cycle/peer_feedback.json').read_text())
    body=(tmp_path/'cycle/peer_feedback.md').read_text()
    assert record['prompt_sha256']==shared.sha(body)
    assert record['augmented_prompt_sha256']==shared.sha(prompt)
    assert 'PEER_ISSUE' in prompt and 'foreign draft' not in prompt
    with pytest.raises(FileExistsError):board(tmp_path/'first',samples=2)
    with pytest.raises(ValueError):first.snapshot(3,2)
    with pytest.raises(ValueError):first.lane(1).publish(1,'gold_score','hidden grade','draft')


def test_summaries_prioritize_exact_issues_and_exclude_witnesses():
    decision={'decision':'REJECT','issues':['Derive the nonzero condition.'],
              'checks':{'guard':False,'source':True}}
    text=shared.audit_summary(decision)
    assert 'Derive the nonzero condition.' in text and 'Failed check: guard' in text
    result={'exact_verified':False,'certificate':{'body':'HUGE_WITNESS_SENTINEL'},
            'stages':[{'stage':'division','result':{'state':'timeout','certificate':'HUGE_WITNESS_SENTINEL'}}]}
    text=shared.tool_summary(result)
    assert 'timeout' in text and 'not a disproof' in text and 'HUGE_WITNESS_SENTINEL' not in text


@pytest.mark.parametrize('operation',['exact_geometry','polynomial_ideal_membership'])
@pytest.mark.parametrize('enabled',[True,False])
def test_eight_harness_lanes_exchange_feedback_on_retry_only(tmp_path,monkeypatch,operation,enabled):
    problem=tmp_path/'problem.json';proof=tmp_path/'proof.md'
    problem.write_text(json.dumps({'problem_id':'synthetic','statement':THEOREM,'reference_solution':'HIDDEN_GOLD'}))
    proof.write_text('The conclusion requires a calculation.')
    detection,matcher=decisions(proof.read_text(),operation=operation)
    barrier=threading.Barrier(8)
    publish=shared.Board.publish
    def synchronized(self,sample,cycle,kind,*args,**kwargs):
        publish(self,sample,cycle,kind,*args,**kwargs)
        if cycle==1 and kind=='parser_rejected':barrier.wait(timeout=20)
    monkeypatch.setattr(shared.Board,'publish',synchronized)
    monkeypatch.setattr(geometry,'compile_bounded',geometry.compiler.compile_program)
    monkeypatch.setattr(fresh.certificate,'validate_markdown_budget_forcing',lambda *a,**k:None)
    calls=[]
    class Calls:
        def __init__(self,*args,**kwargs):pass
        def __call__(self,**kw):
            calls.append(kw['stage'])
            assert 'HIDDEN_GOLD' not in kw['user_prompt']
            if kw['stage'].endswith('gap_detection'):text=detection
            elif kw['stage'].endswith('operation_matcher'):text=matcher
            else:
                parts=Path(kw['destination']).parts
                cycle=next(p for p in parts if p.startswith('cycle_'))
                assert (shared.HEADER in kw['user_prompt'])==(enabled and cycle=='cycle_02')
                text='Unparseable synthetic draft.'
            return text,kw['parser'](text),{}
    monkeypatch.setattr(harness.rewrite,'BudgetedCalls',Calls)
    result=harness.run(problem_file=problem,proof_file=proof,output=tmp_path/'run',execute_models=True,
        config=harness.Config(batch_size=8,workers=8,cycles=2,shared_lane_feedback=enabled))
    assert result['state']=='completed' and result['outcome']=='NO_CERTIFIED_REWRITE',result
    assert len(calls)==18 and len(result['samples'])==8
    snapshots=list((tmp_path/'run/02_formalizations').glob('sample_*/cycles/cycle_02/peer_feedback.json'))
    if enabled:
        assert len(snapshots)==8
        events={e['id']:e for p in (tmp_path/'run/shared_feedback/events').glob('*.json')
                for e in [json.loads(p.read_text())]}
        assert len(events)==16
        for path in snapshots:
            record=json.loads(path.read_text())
            seen={events[i]['sample'] for group in record['included'] for i in group['event_ids']}
            assert seen=={record['selected_peer']} and record['selected_peer']!=record['sample']
            assert set(record['available_peers'])==set(range(1,9))-{record['sample']}
    else:
        assert not snapshots and not (tmp_path/'run/shared_feedback').exists()


@pytest.mark.parametrize('route',['geometry','algebra'])
def test_peer_success_never_bypasses_own_audit_or_enters_auditor_prompt(tmp_path,monkeypatch,route):
    exchange=board(tmp_path/'board',samples=2)
    exchange.lane(2).publish(1,'semantic_accepted','PEER_SUCCESS_SENTINEL','other draft')
    exchange.lane(2).publish(1,'tool_verified','PEER_CERTIFICATE_SENTINEL','other draft')
    monkeypatch.setattr(fresh.certificate,'validate_markdown_budget_forcing',lambda *a,**kw:None)
    monkeypatch.setattr(geometry,'compile_bounded',geometry.compiler.compile_program)
    authors=[];reviews=[];tools=[]
    def caller(**kw):
        if kw['stage'] in {'geometry_formalization',fresh.division.STAGE,fresh.recovery.REPAIR_STAGE}:
            authors.append(kw['user_prompt'])
            assert ('PEER_SUCCESS_SENTINEL' in kw['user_prompt'])==(len(authors)==2)
            text='invalid first draft' if len(authors)==1 else (program(BODY) if route=='geometry' else '# Decision\nCALL_TOOL\n'+FORMALIZATION)
        else:
            assert 'PEER_SUCCESS_SENTINEL' not in kw['user_prompt'] and 'PEER_CERTIFICATE_SENTINEL' not in kw['user_prompt']
            assert shared.HEADER not in kw['user_prompt']
            reviews.append(len(reviews)==1)
            text=audit(reviews[-1])
        return text,kw['parser'](text),{}
    def tool(*args,**kwargs):
        assert reviews==[False,True]
        tools.append(1)
        return {'exact_verified':False,'verdict':'INCONCLUSIVE','stages':[]}
    if route=='geometry':
        output,proof=sources(tmp_path)
        detection,matched=decisions(proof,operation='exact_geometry')
        acq=output/'01_acquisition'
        for name,text in [('input/original_theorem.md',THEOREM),('input/resolver1_proof.md',proof),
                          ('01_detection/detection.md',detection),('02_matcher/matcher.md',matched)]:
            harness.base.write_text(acq/name,text)
        matcher=harness.base._parse_matcher(matched,harness.acquisition.protocol.parse_detection(detection)['desired_exact_fact'],harness.matcher_operations())
        monkeypatch.setattr(geometry,'certificate_search',tool)
        result=geometry.run_track(output,output/'02_formalizations/sample_01',config=harness.Config(),seed=1,
            matcher=matcher,select=lambda p,fn:pytest.fail('no certificate'),should_stop=lambda:False,
            caller=caller,feedback=exchange.lane(1))
    else:
        output=tmp_path/'algebra';write_inputs(output)
        result=fresh.execute(output,{},'Original contract',1,caller=caller,tool=tool,feedback=exchange.lane(1))
    assert result['state']=='completed',result
    assert len(authors)==3 and reviews==[False,True] and tools==[1]
    kinds={json.loads(p.read_text())['kind'] for p in (exchange.root/'events').glob('*.json')}
    assert {'parser_rejected','semantic_rejected','semantic_accepted','tool_inconclusive'} <= kinds
