"""Keep grader slots busy without duplicating inherited or accepted assessments."""
import importlib
from pathlib import Path

import pytest


@pytest.fixture
def pool(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'scripts'))
    return importlib.import_module('run_v2_pool')


def test_active_call_reserves_slot_and_is_never_duplicated(pool):
    units=[dict(unit_id=x) for x in ['a','b','c']]
    found={('a',1):{}}
    jobs=[dict(slots=1,bindings=[dict(unit_id='a',repeat=2)])]
    chosen=pool.choose_tasks(units,found,jobs,{},workers=3,retries=3)
    assert [(u['unit_id'],i) for u,i in chosen]==[('b',1),('b',2)]


def test_freed_slot_is_filled_while_a_slow_call_remains(pool):
    units=[dict(unit_id=x) for x in ['a','b','c']]
    jobs=[dict(slots=1,bindings=[dict(unit_id='a',repeat=1)])]
    found={('a',2):{},('b',1):{}}
    chosen=pool.choose_tasks(units,found,jobs,{},workers=2,retries=3)
    assert [(u['unit_id'],i) for u,i in chosen]==[('b',2)]


def test_pool_never_schedules_discarded_or_exhausted_attempts(pool):
    chosen=pool.choose_tasks([dict(unit_id='a')],{},[],{'a:1':3},workers=12,retries=3)
    assert [(u['unit_id'],i) for u,i in chosen]==[('a',2)]
    assert pool.choose_tasks([dict(unit_id='a')],{},[dict(slots=12,bindings=[])],{},12,3)==[]


def test_missing_process_identity_cannot_adopt_a_dead_job(pool, monkeypatch):
    monkeypatch.setattr(pool, 'process_identity', lambda pid: None)
    assert not pool.process_is_live(123, None)
    assert not pool.process_is_live(123, 'old-start-time')
    monkeypatch.setattr(pool, 'process_identity', lambda pid: 'new-start-time')
    assert not pool.process_is_live(123, 'old-start-time')
    assert pool.process_is_live(123, 'new-start-time')
