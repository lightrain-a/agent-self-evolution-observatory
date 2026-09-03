from __future__ import annotations
import inspect,json
from pathlib import Path
import pytest
from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_q03_precedence_20260903 as q03


def test_contract_freezes_synthetic_only_24_call_gate():
    o=json.loads(q03.CONTRACT.read_text())
    assert o['status']=='FROZEN_PRE_Q03_PROVIDER_CALL'
    assert o['panel']['fixture_count']==8 and o['panel']['replicates_per_fixture']==3
    assert o['panel']['total_calls']==24 and o['panel']['history_depths_by_replicate']==[0,6,18]
    assert o['panel']['real_c1_task_text_used'] is False and o['panel']['fresh2_task_text_used'] is False
    assert o['pass_rule']['native_tool_event_count']==0 and o['pass_rule']['required']=='24/24'
    assert o['root_cause']['fresh2_replay_forbidden'] is True


def test_bridge_is_project_precedence_text_only_surface():
    assert q03.WITNESS in q03.BRIDGE
    assert 'PROJECT INSTRUCTION OVERRIDE' in q03.BRIDGE
    for name in ('list_directory','read_file','grep','glob','use_skill','MCP'):
        assert name in q03.BRIDGE
    assert 'ordinary assistant text' in q03.BRIDGE
    assert 'never execute it' in q03.BRIDGE


def test_fixture_geometry_and_markers_are_unique():
    assert len(q03.FIXTURES)==8 and q03.DEPTHS==(0,6,18)
    assert len({x[0] for x in q03.FIXTURES})==8
    assert len({x[2] for x in q03.FIXTURES})==8
    assert all(x[2] in x[3] for x in q03.FIXTURES)
    assert sum(1 for x in q03.FIXTURES for _ in q03.DEPTHS)==24


def test_fixture_history_is_synthetic_and_contains_no_fresh2_task_ids():
    forbidden=('pydata__xarray-3677','matplotlib__matplotlib-20488','psf__requests-5414','django__django-15503')
    for fixture in q03.FIXTURES:
        for depth in q03.DEPTHS:
            text=json.dumps(q03.msgs(fixture,depth),ensure_ascii=False)
            assert 'synthetic' in text.lower()
            assert all(token not in text for token in forbidden)
            assert len(q03.msgs(fixture,depth))==2+2*depth+(1 if depth else 0)


def test_jsonl_audit_detects_phantom_tool_and_maxrounds():
    raw='\n'.join([
        json.dumps({'type':'run.started','model':'qwen3.8-27b'}),
        json.dumps({'type':'reasoning.delta','text':'inspect'}),
        json.dumps({'type':'usage','prompt_tokens':10,'completion_tokens':5}),
        json.dumps({'type':'tool.completed','content':'unknown or unmounted tool: list_directory','is_error':True}),
        json.dumps({'type':'error','message':'max rounds (1) reached'}),
        json.dumps({'type':'turn.completed','stop_reason':'MaxRounds','exit_code':1}),
    ])
    a=q03.audit_jsonl(raw)
    assert a['model']=='qwen3.8-27b' and len(a['usage'])==1
    assert len(a['tools'])==1 and a['tools'][0]['type']=='tool.completed'
    assert a['maxrounds'] is True


def test_jsonl_audit_accepts_clean_text_only_shape():
    text=q03.WITNESS+'\nTHOUGHT: inspect.\n```bash\nls -la # Q03_DIR_MARKER\n```'
    raw='\n'.join([
        json.dumps({'type':'run.started','model':'qwen3.8-27b'}),
        json.dumps({'type':'message.delta','text':text}),
        json.dumps({'type':'usage','prompt_tokens':10,'completion_tokens':20}),
        json.dumps({'type':'turn.completed','stop_reason':'Stopped','exit_code':0}),
    ])
    a=q03.audit_jsonl(raw)
    assert a['text']==text and not a['tools'] and not a['trunc'] and not a['maxrounds']


def test_prepare_is_zero_provider_and_run_reuses_frozen_q02_transport():
    s=inspect.getsource(q03.prepare)
    assert 'q02.invoke' not in s and 'subprocess.run' in s  # version only
    r=inspect.getsource(q03.run)
    assert 'q02.invoke' in r
    assert 'fresh3_authorized' in r


def test_no_downstream_scientific_execution_surface():
    s=inspect.getsource(q03)
    for token in ('execute_trajectory(', 'writer_phase(', 'binder_phase(', 'shadow_phase(', 'final_measurement('):
        assert token not in s
    assert "'scientific_source_tasks_used':0" in s


def test_parent_hash_and_verdict_are_current():
    q03.verify_parent()


def test_prepare_refuses_existing_root(tmp_path:Path):
    with pytest.raises(RuntimeError,match='exists'):
        q03.prepare(tmp_path)
