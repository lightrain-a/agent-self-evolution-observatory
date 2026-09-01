import json
from pathlib import Path
from research_pipeline import c1_pacta_rb_qwen397_t0_runtime_v7 as rt
from research_pipeline import run_c1_pacta_rb_qwen397_t0_v7_20260901 as r

def test_timeout_template_falls_back_to_official_default(monkeypatch):
    monkeypatch.setattr(rt,'load_agent_default',lambda field:'Timed out {{action["action"]}} :: {{output}}' if field=='timeout_template' else None)
    config={'agent':{}}
    visible=rt.render_timeout_observation(config,'sleep 61','partial')
    assert visible=='Timed out sleep 61 :: partial'

def test_timeout_template_prefers_yaml_if_present(monkeypatch):
    monkeypatch.setattr(rt,'load_agent_default',lambda field: (_ for _ in ()).throw(AssertionError('fallback should not run')))
    config={'agent':{'timeout_template':'YAML {{action["action"]}} {{output}}'}}
    assert rt.render_timeout_observation(config,'cmd','out')=='YAML cmd out'

def test_v7_keeps_60_second_environment_timeout_and_16k_source_budget():
    source=Path(rt.__file__).read_text()
    assert 'timeout=60' in source
    assert rt.SOURCE_MAX_COMPLETION_TOKENS==16384
    assert rt.PACTA_FIRST_DECISION_BUDGET==512

def test_v7_pool_is_exactly_seven_untouched_sources():
    assert len(r.FUTURES)==7
    assert set(r.CONSUMED_SOURCES).isdisjoint(r.FUTURES)
    assert set(r.CONSUMED_SOURCES)=={'pydata__xarray-4966','scikit-learn__scikit-learn-14496','psf__requests-1766','matplotlib__matplotlib-24627'}

def test_prepare_freezes_seven_and_no_replacement(tmp_path,monkeypatch):
    ids=list(r.FUTURES)
    monkeypatch.setattr(r,'verify_frozen',lambda:{})
    monkeypatch.setattr(r,'pool_units',lambda:{x:{'source_task_id':x,'task_family':'repo/'+str(i),'source_task_sha256':'a'*64,'source_base_commit':'b'*40,'source_task':'task'} for i,x in enumerate(ids)})
    monkeypatch.setattr(r,'digest_map',lambda:{x:'c'*64 for x in ids})
    monkeypatch.setattr(r,'image_repo',lambda x:'repo/'+x)
    root=tmp_path/'run';out=r.prepare(root)
    assert out['scheduled']==7
    c=json.loads((root/'contract.json').read_text());s=json.loads((root/'acquisition-schedule.json').read_text())
    assert c['scheduled_source_units']==7
    assert c['prior_valid_trajectories']==2
    assert c['maximum_total_valid_original_pool_after_v7']==9
    assert c['replacement'] is False and c['top_up'] is False
    assert s['scheduled_count']==7

def test_v7_has_no_method_execution_surface():
    source=Path(r.__file__).read_text()
    for x in ('execute_writer','execute_binder','execute_shadow','execute_final'):
        assert x not in source
    assert 'STOP_BEFORE_PACTA' in source
