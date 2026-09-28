import importlib.util
import json
from pathlib import Path

import pytest

spec=importlib.util.spec_from_file_location('publication',Path(__file__).resolve().parents[1]/'scripts/publish_v2_study_when_complete.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_completion_publisher_rejects_unrelated_staged_changes():
    allowed=module.allowed_paths('example')
    module.check_staged(['benchmarks/reports/example/results.json'],allowed)
    with pytest.raises(RuntimeError,match='Unrelated'):
        module.check_staged(['README.md'],allowed)
    with pytest.raises(RuntimeError,match='Unrelated'):
        module.check_staged(['benchmarks/reports/example_other/result.json'],allowed)


def test_completion_runner_uses_effective_two_grade_plan():
    assert module.study_runner(dict(repeats=2,unique_proofs=749,planned_grades=1498))=='scripts/run_v2_pairs.py'
    with pytest.raises(ValueError,match='effective repetition count'):
        module.study_runner(dict(repeats=2,unique_proofs=749,planned_grades=2996))
    with pytest.raises(ValueError,match='explicit'):
        module.study_runner(dict(unique_proofs=749,planned_grades=1498))


def test_two_grade_completion_generates_matrices_without_model_calls_or_push(monkeypatch,tmp_path):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'scripts'))
    import report_v2_matrices
    manifest=dict(run_id='test',repeats=2,unique_proofs=1,planned_grades=2)
    monkeypatch.setattr(report_v2_matrices,'load_manifest',lambda _:manifest)
    (tmp_path/'work').mkdir()
    (tmp_path/'results.json').write_text(json.dumps(dict(state='completed',active_batch=None,
                                                       completed_grades=2,completed_proofs=1)))
    monkeypatch.setattr(module.sys,'argv',['publish','--study',str(tmp_path)])
    monkeypatch.setattr(module.time,'sleep',lambda _:None)
    calls=[]
    monkeypatch.setattr(module,'command',lambda args:calls.append(args) or '')
    assert module.main()==0
    assert any('scripts/run_v2_pairs.py' in args for args in calls)
    assert any('scripts/report_v2_matrices.py' in args for args in calls)
    assert all('scripts/run_v2_consistency.py' not in args and '--execute-models' not in args and 'git' not in args for args in calls)
    assert json.loads((tmp_path/'work/publication_status.json').read_text())['state']=='verified'
