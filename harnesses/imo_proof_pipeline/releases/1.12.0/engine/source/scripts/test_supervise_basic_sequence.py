from pathlib import Path
import pytest
from scripts import supervise_basic_sequence as supervisor
from scripts import report_basic_attempts as history


def test_exhausted_portfolio_advances_without_repeating_model_work(tmp_path,monkeypatch):
    queue=tmp_path/'queue';queue.mkdir()
    supervisor.runner.write(queue/'manifest.json',{'problems':[{'problem_id':'Example-001'}]})
    supervisor.runner.write(queue/'status.json',{'state':'paused_on_failure','problem_id':'Example-001'})
    supervisor.runner.write(queue/'problems/Example-001/summary.json',{'state':'failed_closed'})
    verified=[];calls=[]
    monkeypatch.setattr(supervisor.runner,'validate_failed_portfolio',lambda p,n:verified.append(n))
    monkeypatch.setattr(supervisor.time,'sleep',lambda _:None)
    class Child:
        def poll(self):return 0
    def spawn(command,**kwargs):
        calls.append(command)
        supervisor.runner.write(queue/'status.json',{'state':'completed_with_failed_lanes'})
        return Child()
    monkeypatch.setattr(supervisor.subprocess,'Popen',spawn)
    supervisor.run_stage(tmp_path,queue,['python','runner.py'],'test')
    assert verified==['Example-001']
    assert calls==[['python','runner.py','--resume','--skip-failed-problem','Example-001']]


def test_incomplete_failure_is_not_silently_restarted(tmp_path,monkeypatch):
    queue=tmp_path/'queue';queue.mkdir()
    supervisor.runner.write(queue/'manifest.json',{'problems':[{'problem_id':'Example-001'}]})
    supervisor.runner.write(queue/'status.json',{'state':'paused_on_failure','problem_id':'Example-001'})
    monkeypatch.setattr(supervisor.subprocess,'Popen',lambda *a,**k:pytest.fail('unexpected restart'))
    with pytest.raises(RuntimeError,match='validated exhausted'):
        supervisor.run_stage(tmp_path,queue,['python','runner.py'],'test')


def test_history_retains_old_scores_when_new_attempt_is_worse(tmp_path):
    old={'problem_number':1,'candidate_id':'t10_r01','source_summary':'/old/problems/one/summary.json','grade':{'score':7}}
    new={**old,'source_summary':'/new/problems/one/summary.json','grade':{'score':2}}
    history.write(tmp_path/'prior_strict_summary.json',{'rows':[old],'policy_sha256':'policy','model':'model','reasoning_effort':'xhigh'})
    result=history.report_history(tmp_path,[new])
    assert result['attempt_count']==2
    assert result['sum_per_problem_best_across_attempts']==7
    assert {r['grade']['score'] for r in result['rows']}=={2,7}
