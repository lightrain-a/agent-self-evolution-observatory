from pathlib import Path
import inspect
import pytest

from research_pipeline.c1_pacta_rb_qwen397_t0_runtime import parse_action
from research_pipeline.run_c1_pacta_rb_qwen397_t0_source_20260901 import FUTURES

def test_parser_matches_frozen_single_fence():
    assert parse_action("THOUGHT: x\n\n```bash\npwd\n```") == "pwd"
    with pytest.raises(ValueError):
        parse_action("no action")
    with pytest.raises(ValueError):
        parse_action("```bash\npwd\n```\n```bash\nls\n```")

def test_fixed_pool_no_replacement():
    assert len(FUTURES) == 11
    assert len(set(FUTURES)) == len(set(FUTURES.values())) == 11
    assert set(FUTURES).isdisjoint(FUTURES.values())

def test_t0_runner_has_no_method_stages():
    source = Path(inspect.getsourcefile(parse_action)).read_text()
    assert "SUCCESSFUL_SI" not in source
    assert "FAILED_SI" not in source
    for forbidden in ("binder_calls", "shadow_calls", "final_measurement_calls", "future_task_executions"):
        assert f'"{forbidden}":0' in source

def test_future_tasks_not_loaded_as_policy_input():
    from research_pipeline import run_c1_pacta_rb_qwen397_t0_source_20260901 as runner
    source = inspect.getsource(runner.acquire)
    assert 'units[instance]["source_task"]' in source
    assert '["future_task"]' not in source

def test_old_roots_are_distinct():
    old = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-qwen397-t0-source-trajectory-20260831-v1")
    new = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-qwen397-t0-source-trajectory-20260901-v2")
    assert old != new
