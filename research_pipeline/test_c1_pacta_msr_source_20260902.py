from __future__ import annotations
from pathlib import Path
from research_pipeline import run_c1_pacta_msr_source_20260902 as r


def test_verify_resolves_ten_fresh_source_units():
    rows,q=r.verify()
    assert len(rows)==10
    assert len({x['source_task_id'] for x in rows})==10
    assert len({x['future_task_id'] for x in rows})==10
    assert all(x['source_task_id']!=x['future_task_id'] for x in rows)
    assert all(x['digest_ref'].startswith('docker.1ms.run/') for x in rows)
    assert q['source_trajectory_output_budget']==16384
    assert q['pacta_first_decision_budget']==512


def test_schedule_is_deterministic_and_future_locked():
    rows,_=r.verify();a=r.schedule(rows);b=r.schedule(rows)
    assert a==b and len(a)==10
    assert [x['sequence'] for x in a]==list(range(1,11))
    assert all(x['logical_attempts']==1 for x in a)
    assert all(x['selected_memory']=='' for x in a)
    assert all(x['future_task_executed'] is False for x in a)


def test_source_runner_preserves_separate_budgets_and_no_method_execution_surface():
    assert r.SOURCE_MAX_COMPLETION_TOKENS==16384
    assert r.PACTA_FIRST_DECISION_BUDGET==512
    source=Path(r.__file__).read_text()
    assert 'execute_writer' not in source
    assert 'execute_binder' not in source
    assert 'execute_shadow' not in source
    assert 'execute_final' not in source
    assert "'future_task_executions':0" in source
    assert "'replacement':False" in source
    assert "'top_up':False" in source
