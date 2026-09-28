"""Offline publication contracts: grade aggregation and evidence integrity."""
import copy
import importlib.util
import itertools
import json
from pathlib import Path
import sys
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from verify_latest_selection import POLICY, sha, textsha, summarize, verify, markdown, response_winner
from export_latest_selection import put, finish, update_readme, options

def fixture_bundle(tmp_path):
    problems=[]
    for i in range(1,7):
        pid=f'imo2026_p{i}';order=['d','c','b','a'];lanes=[]
        for j,c in enumerate(order):
            proof=put(tmp_path,f'proofs/{pid}/{c}.md',f'Proof {i}/{c}.');ph=textsha((tmp_path/proof).read_text());grades=[]
            scores=[7-j,j+1]
            for rep in (1,2):
                raw=put(tmp_path,f'grades/{pid}/{c}_{rep}.txt',f'Score: {scores[rep-1]}')
                grades.append(put(tmp_path,f'grades/{pid}/{c}_{rep}.json',dict(proof_sha256=ph,problem_id=pid,
                    pass_index=rep,score=scores[rep-1],grade=dict(score=scores[rep-1],contract_consistent=True),
                    model='gpt-5.6-sol',reasoning_effort='xhigh',policy_sha256=POLICY,
                    isolation_audit={'tool_calls':0},raw_responses=[raw])))
            lanes.append(dict(candidate_id=c,proof=proof,proof_sha256=ph,scores=scores,grades=grades,stage='refinement_2'))
        votes=[]
        for n,pair in enumerate(itertools.combinations(order,2)):
            for model in ('gemma','qwen'):
                for ordering in ('forward','reverse'):
                    shown=list(pair if ordering=='forward' else reversed(pair));case=f'{n}_{model}_{ordering}'
                    response=put(tmp_path,f'votes/{pid}/{case}.md','Winner: A')
                    inp=put(tmp_path,f'votes/{pid}/{case}_input.md','Both proofs')
                    votes.append(dict(original_case_id=str(n),case_id=case,model_key=model,order=ordering,presentation_order=shown,
                        valid=True,binding_verified=True,winner_label='A',selected_candidate=shown[0],response=response,response_sha256=sha(tmp_path/response),
                        input=inp,input_sha256=sha(tmp_path/inp)))
        problems.append(dict(problem_id=pid,lanes=lanes,seed_derived_candidate_order=order,votes=votes,selected_candidate='d',votes_received={c:6 for c in order},
            order_disagreements=12,order_pairs=12,provenance=dict(generation_release='fixture',selection_run_id='fixture')))
    return problems

def test_complete_pass_and_seed_tie(tmp_path):
    ps=fixture_bundle(tmp_path);d=finish(tmp_path,ps,'complete_pass_with_lower_total_average')
    assert d['lower_average_pass']==2
    assert d['headline']['totals']==dict(average=15,oracle_at_4=24,selector_at_1=6)
    assert verify(tmp_path)==d
    text=markdown(d)
    assert text.startswith('| Problem | Average | Selector@1 | Oracle@4 |\n')
    assert '| P1 | 2.5 | 1 | 4 |' in text
    assert '| **Total (of 42)** | **15** | **6** | **24** |' in text
    assert 'Both grading passes give the same totals.' not in text

def test_mean_is_oracle_of_means_not_mean_of_oracles(tmp_path):
    ps=fixture_bundle(tmp_path);d=finish(tmp_path,ps,'mean_of_two_grades_per_proof')
    assert d['headline']['totals']==dict(average=24,oracle_at_4=24,selector_at_1=24)
    assert (d['pass_results'][0]['totals']['oracle_at_4']+d['pass_results'][1]['totals']['oracle_at_4'])/2==33
    assert '| **Total (of 42)** | **24** | **24** | **24** |' in markdown(d)

@pytest.mark.parametrize('aggregation,expected',[
    (None,dict(average=24,oracle_at_4=24,selector_at_1=24)),
    ('complete_pass_with_lower_total_average',dict(average=15,oracle_at_4=24,selector_at_1=6)),
])
def test_export_defaults_to_proof_means_and_retains_explicit_historical_replay(tmp_path,aggregation,expected):
    args=options().parse_args(['--suite',str(tmp_path),*(['--aggregation',aggregation] if aggregation else [])])
    d=finish(tmp_path,fixture_bundle(tmp_path),args.aggregation)
    assert d['headline']['totals']==expected
    assert d['headline_aggregation']==(aggregation or 'mean_of_two_grades_per_proof')

@pytest.mark.parametrize('text,winner',[
    ('## Decision\nWinner: A\nReason: comparison','A'),
    ('## Decision\r\n- **Winner:** b.\r\nReason: comparison','B'),
    ('```markdown\n## Decision\nWinner: B\nReason: comparison\n```','B'),
])
def test_saved_vote_accepts_recorded_markdown_variants(text,winner):
    assert response_winner(text)==winner

@pytest.mark.parametrize('response',[
    'No explicit winner.', 'Winner: C', 'Winner: A or B',
    'Winner: A\nWinner: B', 'Winner: A\nWinner: A',
    'Winner: A\nWinner: unclear',
])
def test_malformed_saved_vote_fails_even_with_matching_artifact_hashes(tmp_path,response):
    d=finish(tmp_path,fixture_bundle(tmp_path),'mean_of_two_grades_per_proof')
    vote=d['problems'][0]['votes'][0];path=tmp_path/vote['response'];path.write_text(response)
    vote['response_sha256']=d['artifacts'][vote['response']]=sha(path)
    (tmp_path/'SCORECARD.json').write_text(json.dumps(d))
    with pytest.raises(AssertionError,match='exactly one explicit Winner'):
        verify(tmp_path)

def test_reversed_vote_metadata_fails_even_with_consistent_tally(tmp_path):
    d=finish(tmp_path,fixture_bundle(tmp_path),'mean_of_two_grades_per_proof')
    problem=d['problems'][0];vote=problem['votes'][1]
    assert vote['presentation_order']==['c','d'] and vote['winner_label']=='A'
    vote.update(winner_label='B',selected_candidate='d')
    problem['votes_received']['c']-=1;problem['votes_received']['d']+=1
    problem['order_disagreements']-=1
    # The fixture's chosen proof remains d, so its headline and grades are unchanged.
    # Only the metadata conflicts with the saved response, whose hash still matches.
    assert (tmp_path/vote['response']).read_text()=='Winner: A'
    assert sha(tmp_path/vote['response'])==vote['response_sha256']
    (tmp_path/'SCORECARD.json').write_text(json.dumps(d))
    with pytest.raises(AssertionError,match='Saved response winner differs'):
        verify(tmp_path)

def test_tampered_proof_fails(tmp_path):
    d=finish(tmp_path,fixture_bundle(tmp_path),'complete_pass_with_lower_total_average')
    (tmp_path/d['problems'][0]['lanes'][0]['proof']).write_text('Different proof')
    with pytest.raises(AssertionError):verify(tmp_path)

def test_invalid_vote_and_duplicate_pair_fail(tmp_path):
    d=finish(tmp_path,fixture_bundle(tmp_path),'complete_pass_with_lower_total_average')
    p=tmp_path/'SCORECARD.json';d['problems'][0]['votes'][1]=copy.deepcopy(d['problems'][0]['votes'][0]);p.write_text(json.dumps(d))
    with pytest.raises(AssertionError):verify(tmp_path)

def test_readme_preserves_historical_matrix_and_is_idempotent(tmp_path):
    root=tmp_path/'evidence';root.mkdir();d=finish(root,fixture_bundle(root),'complete_pass_with_lower_total_average')
    p=tmp_path/'README.md';p.write_text('### IMO 2026\n\n<!-- BEGIN IMO2026 SCORE MATRIX -->original<!-- END IMO2026 SCORE MATRIX -->\n')
    update_readme(tmp_path,d);once=p.read_text();update_readme(tmp_path,d)
    assert p.read_text()==once and '<!-- BEGIN IMO2026 SCORE MATRIX -->original<!-- END IMO2026 SCORE MATRIX -->' in once

def test_fresh_suite_requires_same_release_and_runtime(tmp_path):
    ps=fixture_bundle(tmp_path)
    for p in ps:
        p['provenance'].update(fresh_end_to_end_b112=True,generation_release='1.12.0',
            selection_run_id=p['problem_id']+'_fresh',release_sha256='e8d94232e00c0c3297fbbfa466df7634055ed6aa2876ba1786d94a87858041c9',
            runtime={'raw_seed_offset':0,'workers':4})
    d=finish(tmp_path,ps,'complete_pass_with_lower_total_average')
    assert d['benchmark_status']=='fresh_uniform_b112'
    assert 'These problems informed selector development' not in markdown(d)
    assert 'These problems informed selector development' in (tmp_path/'README.md').read_text()
    d['problems'][3]['provenance']['runtime']['workers']=6
    (tmp_path/'SCORECARD.json').write_text(json.dumps(d))
    with pytest.raises(AssertionError):verify(tmp_path)

def test_provisional_cannot_be_relabelled_as_uniform(tmp_path):
    d=finish(tmp_path,fixture_bundle(tmp_path),'complete_pass_with_lower_total_average')
    d['benchmark_status']='fresh_uniform_b112'
    (tmp_path/'SCORECARD.json').write_text(json.dumps(d))
    with pytest.raises((KeyError,AssertionError)):verify(tmp_path)

@pytest.mark.parametrize('different_metric',[None,'average','selector_at_1','oracle_at_4'])
def test_same_pass_totals_sentence_checks_every_metric(tmp_path,different_metric):
    d=finish(tmp_path,fixture_bundle(tmp_path),'mean_of_two_grades_per_proof')
    d['pass_results'][1]['totals']=copy.deepcopy(d['pass_results'][0]['totals'])
    if different_metric:
        d['pass_results'][1]['totals'][different_metric]+=0.5
    assert ('Both grading passes give the same totals.' in markdown(d)) is (different_metric is None)

def test_published_readme_block_matches_generator():
    import report_qwen_selection as qwen
    d=verify(ROOT/'docs/results/imo2026_b112_selection_20260922')
    assert d['headline_aggregation']=='mean_of_two_grades_per_proof'
    assert d['headline']==d['mean_grade_results']
    text=(ROOT/'README.md').read_text()
    begin='<!-- BEGIN LATEST SELECTOR RESULTS -->\n'
    end='<!-- END LATEST SELECTOR RESULTS -->'
    assert text.count(begin)==text.count(end)==1
    assert text.split(begin,1)[1].split(end,1)[0]==qwen.imo_section(qwen.build())
    assert '[All 24 proofs, every vote and both grades]' in markdown(d)
