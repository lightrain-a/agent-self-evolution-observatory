from __future__ import annotations
import json
from pathlib import Path
import pytest
from research_pipeline.c1_pacta_rb_qwen397 import build_final_schedule,build_shadow_schedule,gate,writer_twins_valid
from research_pipeline import c1_pacta_rb_qwen397_p0_core as core
from research_pipeline import run_c1_pacta_rb_qwen397_p0_stages_20260901 as stages

EXPECTED_PILOT=[
 'sphinx-doc__sphinx-8593=>sphinx-doc__sphinx-7748',
 'django__django-13449=>django__django-11400',
 'pylint-dev__pylint-7080=>pylint-dev__pylint-8898',
 'mwaskom__seaborn-3187=>mwaskom__seaborn-3069',
 'psf__requests-1766=>psf__requests-1724',
 'astropy__astropy-7166=>astropy__astropy-14096']
EXPECTED_SEALED=[
 'pytest-dev__pytest-5840=>pytest-dev__pytest-5809',
 'sympy__sympy-15599=>sympy__sympy-18189',
 'scikit-learn__scikit-learn-14496=>scikit-learn__scikit-learn-10908']
EXPECTED_RANDOM=[
 'sphinx-doc__sphinx-8593=>sphinx-doc__sphinx-7748',
 'mwaskom__seaborn-3187=>mwaskom__seaborn-3069',
 'psf__requests-1766=>psf__requests-1724',
 'pylint-dev__pylint-7080=>pylint-dev__pylint-8898',
 'astropy__astropy-7166=>astropy__astropy-14096',
 'django__django-13449=>django__django-11400']

def test_static_hashes_and_nine_unit_geometry():
 assert core.verify_inputs()==core.EXPECTED
 u=core.units();assert len(u)==9;assert len({x['task_family'] for x in u})==9
 assert all(Path(x['source_trajectory_path']).is_file() and Path(x['writer_input_trajectory_path']).is_file() for x in u)

def test_old_salt_yields_exact_six_three_split_and_random_order():
 p,s=core.split();assert [x['unit_id'] for x in p]==EXPECTED_PILOT;assert [x['unit_id'] for x in s]==EXPECTED_SEALED
 assert [x['unit_id'] for x in core.ranked(p,core.RANDOM_SALT)]==EXPECTED_RANDOM
 assert not (set(EXPECTED_PILOT)&set(EXPECTED_SEALED))

def test_prepare_is_zero_provider_and_freezes_schedules(tmp_path:Path):
 root=tmp_path/'p0';a=stages.prepare(root);assert a['status']=='P0_PREPARE_PASS';assert a['writer_calls']==a['binder_calls']==a['shadow_calls']==a['final_calls']==0
 c=json.loads((root/'contract.json').read_text());s=json.loads((root/'pilot-split.json').read_text());assert c['pilot']==EXPECTED_PILOT;assert c['sealed']==EXPECTED_SEALED;assert c['random_ranking_pre_shadow']==EXPECTED_RANDOM
 assert c['replacement'] is False and c['top_up'] is False and c['terminal_locked'] is True and c['other_models_locked'] is True
 assert len((root/'shadow-schedule.jsonl').read_text().splitlines())==144;assert s['sealed_provider_calls']==0

def test_stage_budgets_are_separate_and_frozen():
 assert core.WRITER_MAX==2048;assert core.BINDER_MAX==512;assert core.FIRST_DECISION_MAX==512
 assert core.WRITER_TEMP==0.0 and core.BINDER_TEMP==0.0 and core.POLICY_TEMP==0.2
 assert core.INPUT_CAP==5_000_000 and core.OUTPUT_CAP==500_000

def test_writer_branch_intervention_changes_only_official_instruction():
 u=core.split()[0][0];ms,cs=core.writer_messages(u,'success');mf,cf=core.writer_messages(u,'failure')
 assert cs==cf;assert ms[1]==mf[1];assert ms[0]!=mf[0];assert 'successfully resolved' in ms[0]['content'];assert 'attempted to resolve the issue but failed' in mf[0]['content']
 assert ms[1]['content'].startswith('**Query:**') and '**Trajectory:**' in ms[1]['content']

def test_writer_validator_and_invariance():
 good='# Memory Item 1\n## Title T\n## Description D\n## Content C';m,n=core.validate_memory(good);assert n==1 and m==good
 with pytest.raises(RuntimeError):core.validate_memory('plain text')
 base={'trajectory_sha256':'t','source_task_sha256':'q','requested_model':core.MODEL,'resolved_model':core.MODEL,'temperature':0.0,'context_sha256':'c'}
 assert writer_twins_valid({**base,'branch':'success','memory_sha256':'s'},{**base,'branch':'failure','memory_sha256':'f'})
 assert not writer_twins_valid({**base,'branch':'success','memory_sha256':'x'},{**base,'branch':'failure','memory_sha256':'x'})

def test_scb_is_carrier_adaptation_and_bounded():
 u=core.split()[0][0];messages,prompt=core.binder_messages(u,'memory');assert 'ultimate coding task' in core.BINDER_INSTRUCTION.lower();assert 'current agent state' in prompt.lower();assert core.INITIAL_STATE in prompt
 note,n=core.validate_binding('Prioritize inspecting the relevant implementation before editing it.');assert n<=60
 with pytest.raises(RuntimeError):core.validate_binding(' '.join(['word']*61))

def test_shadow_gate_and_final_geometries_are_frozen():
 p,_=core.split();shadow=build_shadow_schedule(p);assert len(shadow)==144;assert len({r['case_id'] for r in shadow})==144
 samples={'S1':['a']*6,'S2':['a']*6,'F1':['b']*6,'F2':['b']*6};g=gate(samples);assert g=={'B1':1.0,'B2':1.0,'WS':0.0,'WF':0.0,'G':True}
 final=build_final_schedule(p,set(EXPECTED_PILOT[:3]),set(EXPECTED_RANDOM[:3]));assert len(final)==288;assert len({r['case_id'] for r in final})==288
 assert all(r['unit_id'] in EXPECTED_PILOT for r in final);assert not any(r['unit_id'] in EXPECTED_SEALED for r in final)

def test_random_rate_matching_semantics():
 p,_=core.split();ids=[x['unit_id'] for x in p]
 from research_pipeline.c1_pacta_rb_qwen397 import rate_matched_random
 assert rate_matched_random(ids,3)==EXPECTED_RANDOM[:3]

def test_provider_has_no_scientific_retry_and_cumulative_caps(tmp_path:Path):
 call=tmp_path/'writer'/'calls'/'one.json';call.parent.mkdir(parents=True);call.write_text(json.dumps({'usage':{'prompt_tokens':123,'completion_tokens':45}}))
 p=core.Provider('dummy',tmp_path,core.MODEL,core.MODEL);assert p.input_tokens==123 and p.output_tokens==45 and p.start_input==123 and p.start_output==45
 src=Path(core.__file__).read_text();assert "'provider_retries':0" in src;assert 'RATE_LIMIT_MAX_RETRIES' not in src

def test_scientific_runner_has_no_terminal_or_environment_execution_surface():
 src=Path(stages.__file__).read_text();assert 'docker' not in src.lower();assert 'execute_trajectory' not in src;assert 'run_evaluator' not in src and 'terminal_evaluator' not in src
 assert "'terminal_locked':True" in src;assert 'sealed_provider_calls' in src;assert "pilot_units(root)" in src
