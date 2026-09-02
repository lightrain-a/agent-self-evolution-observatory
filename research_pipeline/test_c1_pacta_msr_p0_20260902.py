from __future__ import annotations
import json
from pathlib import Path
import pytest
from research_pipeline import c1_pacta_msr_qwen397_p0_core as c
from research_pipeline import run_c1_pacta_msr_qwen397_p0_stages_20260902 as s
from research_pipeline import run_c1_pacta_msr_qwen397_p0_final_20260902 as f


def test_gate_is_strict_and_margin_explicit():
    g=c.gate({'S1':['a']*6,'S2':['a']*6,'F1':['b']*6,'F2':['b']*6})
    assert g['B1']==1 and g['B2']==1 and g['WS']==0 and g['WF']==0 and g['margin']==1 and g['G'] is True
    h=c.gate({'S1':['a']*6,'S2':['a']*6,'F1':['a']*6,'F2':['a']*6})
    assert h['margin']==0 and h['G'] is False


def test_dual_shadow_geometry_is_384_and_deterministic():
    pilot=[{'unit_id':f'u{i}'} for i in range(8)]
    a=s.schedule_shadow(pilot);b=s.schedule_shadow(pilot)
    assert a==b and len(a)==384
    assert {x['selector'] for x in a}=={'G0_STEP0','GPLUS_MATCHED_REVEAL'}
    assert all(1<=x['replicate']<=6 and x['block'] in {1,2} for x in a)


def test_policy_messages_native_has_no_adapted_support_and_plus_has_exact_probe_transcript():
    config={'agent':{'system_template':'SYS','instance_template':'TASK={{task}}','action_observation_template':'OBS={{output.output}}'}}
    native=c.policy_messages(config,'T','MEM',None,'GPLUS_MATCHED_REVEAL',{'command':'git status --short','observation':{'output':'clean','returncode':0,'timeout':False}})
    assert 'ADAPTED SUPPORT' not in native[0]['content']
    assert native[2]['role']=='assistant' and 'git status --short' in native[2]['content']
    assert native[3]['content']=='OBS=clean'
    bound=c.policy_messages(config,'T','MEM','NOTE','G0_STEP0',None)
    assert 'ADAPTED SUPPORT:\nNOTE' in bound[0]['content'] and len(bound)==2


def test_execution_contract_has_single_variable_mechanism_gate_and_rate_matched_control():
    d=json.loads(c.EXECUTION_CONTRACT.read_text())
    assert d['shadow']['calls']==384 and d['final']['calls']==384
    assert d['mechanism_gate']['Gplus_open_count']=='2..6/8'
    assert d['mechanism_gate']['mean_margin_Gplus_minus_G0_ge']==0.05
    assert d['mechanism_gate']['positive_margin_improvement_count_ge']==5
    assert d['rate_matched_random']['reroll'] is False
    assert d['p0_hard_caps']=={'input_tokens':10000000,'output_tokens':1000000}


def test_stage_and_final_modules_do_not_execute_terminal_or_evaluator():
    src=Path(s.__file__).read_text()+Path(f.__file__).read_text()
    assert 'terminal_evaluator' not in src
    assert 'run_evaluator' not in src
    assert 'execute_trajectory' not in src
    assert "choices=('prepare','probe','writer','binder','shadow')" in Path(s.__file__).read_text()


def test_final_guard_fails_before_provider_when_mechanism_gate_absent(tmp_path:Path):
    (tmp_path/'shadow-result.json').write_text(json.dumps({'status':'HOLD_MSR_MECHANISM_GATE','mechanism_gate_pass':False}))
    with pytest.raises(RuntimeError,match='mechanism gate not passed'):
        f.final(tmp_path)
    assert not (tmp_path/'final').exists()


def test_source_key_is_only_runtime_environment_name():
    src=Path(c.__file__).read_text()+Path(s.__file__).read_text()+Path(f.__file__).read_text()
    assert 'AA_API_KEY' in src
    assert 'sk-' not in src
