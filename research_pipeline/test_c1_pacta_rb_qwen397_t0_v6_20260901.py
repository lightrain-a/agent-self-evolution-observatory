from pathlib import Path
import json
from research_pipeline import c1_pacta_rb_qwen397_t0_runtime_v6 as rt
from research_pipeline import run_c1_pacta_rb_qwen397_t0_v6_20260901 as r

def test_budget_separation_and_retry_contract():
    assert rt.SOURCE_MAX_COMPLETION_TOKENS==16384
    assert rt.PACTA_FIRST_DECISION_BUDGET==512
    assert rt.RATE_LIMIT_MAX_RETRIES==2
    assert rt.RATE_LIMIT_BACKOFF_SECONDS==(60,120)

def test_rate_limit_classifier():
    raw=b'{"error":{"code":"rate_limit_exceeded","message":"rate limit exceeded."}}'
    assert rt.rate_limit_error(400,raw)
    assert rt.rate_limit_error(429,raw)
    assert not rt.rate_limit_error(500,raw)
    assert not rt.rate_limit_error(400,b'{"error":{"code":"bad_request"}}')

def test_remaining_pool_is_exactly_ten_and_consumed_excluded():
    assert len(r.FUTURES)==10
    assert r.CONSUMED_SOURCE not in r.FUTURES
    assert 'scikit-learn__scikit-learn-14496' in r.FUTURES
    assert 'pytest-dev__pytest-5840' in r.FUTURES

def test_prepare_freezes_no_replacement(tmp_path,monkeypatch):
    ids=list(r.FUTURES)
    monkeypatch.setattr(r,'verify_frozen',lambda:{})
    monkeypatch.setattr(r,'pool_units',lambda:{x:{'source_task_id':x,'task_family':'repo/'+str(i),'source_task_sha256':'a'*64,'source_base_commit':'b'*40,'source_task':'task'} for i,x in enumerate(ids)})
    monkeypatch.setattr(r,'digest_map',lambda:{x:'c'*64 for x in ids})
    monkeypatch.setattr(r,'image_repo',lambda x:'repo/'+x)
    root=tmp_path/'run';out=r.prepare(root)
    assert out['scheduled']==10
    c=json.loads((root/'contract.json').read_text());s=json.loads((root/'acquisition-schedule.json').read_text())
    assert c['source_max_completion_tokens']==16384
    assert c['pacta_first_decision_budget_unchanged']==512
    assert c['replacement'] is False and c['top_up'] is False
    assert c['consumed_excluded_source']==r.CONSUMED_SOURCE
    assert s['scheduled_count']==10
    assert all(x['logical_attempts']==1 for x in s['schedule'])

def test_v6_has_no_method_execution_surface():
    s=Path(r.__file__).read_text()
    for x in ('execute_writer','execute_binder','execute_shadow','execute_final'):
        assert x not in s
    assert 'STOP_BEFORE_PACTA' in s
    assert 'full_6_plus_5_design_recovered":False' in s

def test_runtime_always_writes_run_json():
    s=Path(rt.__file__).read_text()
    assert 'atomic_json(unit_root/"run.json",run)' in s
    assert 'failure_layer is None' in s
    assert 'raw_responses==provider.transport_attempts' in s
