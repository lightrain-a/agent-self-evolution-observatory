from __future__ import annotations

import json, tempfile, threading, time, urllib.request
from pathlib import Path
from typing import Any

from research_pipeline import agent_constraint_externality_atomgit_repeat_common as c
from research_pipeline import agent_constraint_externality_atomgit_repeat_execute as exe
from research_pipeline import agent_constraint_externality_atomgit_repeat_mcp_bridge as bridge
from research_pipeline.agent_constraint_externality_atomgit_repeat_dev_reserve_build import OUTPUT_BUNDLE
from research_pipeline.agent_constraint_externality_confirmatory_preexec import decide_repeat_count_after_two, decide_N_star
from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value

ROOT=Path(__file__).resolve().parents[1]


def q1_branch(unit:dict[str,Any])->dict[str,Any]:
    c.patch_live()
    with tempfile.TemporaryDirectory(prefix='ace-repeat-r2-q1-') as d:
        root=Path(d); atom,work=c.prepare_atom(root); progress=root/'bridge-progress.json'; trajectory=root/'trajectory.jsonl'; task='acer2q1'+sha256_value(unit['unit_id'])[:12]+'_1'; payload=exe.mcp_payload(unit,root,progress,trajectory,task); proc=None; done=threading.Event(); errors=[]
        try:
            proc,base,token=c.live.start_daemon(atom_home=atom,workdir=work,log_path=root/'daemon.log'); (atom/'mcp.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); c.live.http_json(base,token,'/live/mode',method='POST',body={'mode':'build'}); before=int(c.live.codingplan_usage(base,token)['used'])
            def stream()->None:
                req=urllib.request.Request(base+'/live',headers={'Authorization':'Bearer '+token})
                try:
                    with urllib.request.urlopen(req,timeout=60) as response:
                        for _ in response:
                            if done.is_set(): break
                except Exception as exc:
                    if not done.is_set(): errors.append(f'{type(exc).__name__}: {exc}')
            th=threading.Thread(target=stream,daemon=True); th.start(); deadline=time.time()+45
            while time.time()<deadline:
                if errors: raise c.RepeatStop(errors[-1])
                if progress.is_file() and json.loads(progress.read_text(encoding='utf-8')).get('status')=='TOOLS_LISTED': break
                time.sleep(.1)
            else: raise c.RepeatStop('repeat Q1 did not list AppWorld tools')
            after=int(c.live.codingplan_usage(base,token)['used']); state=json.loads(progress.read_text(encoding='utf-8'))
            if after!=before or int(state.get('tool_count',0))<=0: raise c.RepeatStop('repeat Q1 crossed zero-request boundary')
            scientific=c.scientific_state_sha(unit['family_id'],Path(state['source_db_root']))
            c.live.http_json(base,token,'/live/stop',method='POST',body={}); done.set(); th.join(timeout=2)
            return {'unit_id':unit['unit_id'],'family_id':unit['family_id'],'arm':unit['arm'],'branch':unit['branch'],'repeat':unit['repeat'],'codingplan_model_requests':0,'tool_count':int(state['tool_count']),'scientific_state_sha256':scientific,'initial_snapshot_sha256_including_instruction':state['initial_snapshot_sha256'],'instruction_sha256':state['instruction_sha256']}
        finally:
            done.set()
            if proc is not None: c.live.terminate_process(proc)

def synthetic_analysis_smoke()->dict[str,Any]:
    _,m,_=c.parents(); ids=c.selected_ids(m); rows=[]
    for fi,fid in enumerate(ids):
        for arm_i,arm in enumerate(c.ARMS):
            for branch_i,branch in enumerate(c.BRANCHES):
                for repeat in c.REPEATS:
                    rows.append({'family_id':fid,'arm':arm,'branch':branch,'repeat':repeat,'valid':True,'target_success':bool((fi+arm_i+branch_i)%2),'crr':0.25+0.01*((fi+arm_i+branch_i)%3)})
    decision=decide_repeat_count_after_two(rows)
    if decision['status']!='REPEAT_QUALIFICATION_PASS_R2' or decision['R_star']!=2: raise c.RepeatStop('direction-blind repeat analyzer smoke failed')
    n=decide_N_star(rows,2)
    if n.get('development_effect_mean_emitted') is not False or n.get('development_effect_sign_emitted') is not False or n.get('selection_uses_effect_direction') is not False: raise c.RepeatStop('N* analyzer leaks direction')
    return {'repeat_decision_status':decision['status'],'repeat_R_star':decision['R_star'],'n_decision_status':n['status'],'n_decision_N_star':n['N_star'],'effect_mean_emitted':False,'effect_sign_emitted':False}

def build()->dict[str,Any]:
    close,manifest,freeze=c.parents(); index=c.family_index(); units=c.units()
    ids=c.selected_ids(manifest)
    if len(ids)!=6 or sum(fid.startswith('ACE-DEV-FG-') for fid in ids)!=3 or sum(fid.startswith('ACE-DEV-TNF-') for fid in ids)!=3: raise c.RepeatStop('repeat family balance drift')
    if freeze['repeat_qualification']['development_family_count']!=6 or freeze['repeat_qualification']['initial_repeats']!=2: raise c.RepeatStop('preexec repeat contract drift')
    pair_checks=[]
    for fid in ids:
        for arm in c.ARMS:
            for repeat in c.REPEATS:
                no=c.visible_instruction(fid,arm,'NO_UPDATE'); real=c.visible_instruction(fid,arm,'REAL_REPAIR'); rb=c.repair_bytes(fid)
                if real.encode()!=no.encode()+c.INJECTION_PREFIX+rb: raise c.RepeatStop('exact repair injection drift')
                if rb in no.encode(): raise c.RepeatStop('repair leaked into NO_UPDATE')
                pair_checks.append({'family_id':fid,'arm':arm,'repeat':repeat,'seed':c.REPEAT_SEEDS[repeat],'scientific_fixture_sha256':c.scientific_fixture_sha(fid),'branch_order':list(c.frozen_branch_order(fid,arm,repeat)),'repair_sha256':c.repair_record(fid)['repair_sha256']})
    # Mechanically exercise the new wrapper on both branches of one paired cell without a model request.
    first=units[0]; paired=[u for u in units if c.pair_key(u)==c.pair_key(first)]
    if len(paired)!=2: raise c.RepeatStop('Q1 pair geometry drift')
    q1=[q1_branch(u) for u in paired]
    if q1[0]['scientific_state_sha256']!=q1[1]['scientific_state_sha256']: raise c.RepeatStop('Q1 branch scientific state mismatch')
    if q1[0]['initial_snapshot_sha256_including_instruction']==q1[1]['initial_snapshot_sha256_including_instruction']: raise c.RepeatStop('Q1 should distinguish visible instructions while preserving scientific state')
    usage=c.usage(); smoke=synthetic_analysis_smoke()
    out={'schema_version':'ace-repeat-dev-r2-readiness-v1','object_id':OBJECT_ID,'status':'ATOMGIT_REPEAT_DEV_R2_ZERO_PROVIDER_READY_AWAITING_SEPARATE_HUMAN_AUTHORITY','repair_closeout_content_sha256':close['content_sha256'],'repair_closeout_file_sha256':sha256_file(c.REPAIR_CLOSEOUT),'repair_manifest_content_sha256':manifest['content_sha256'],'repair_manifest_file_sha256':sha256_file(c.REPAIR_MANIFEST),'preexec_freeze_content_sha256':freeze['content_sha256'],'reserve_bundle_sha256':sha256_file(OUTPUT_BUNDLE),'family_ids':ids,'family_count':6,'category_balance':{'FG':3,'TNF':3},'r2_panel':{'arms':list(c.ARMS),'branches':list(c.BRANCHES),'repeats':list(c.REPEATS),'repeat_seeds':{str(k):v for k,v in c.REPEAT_SEEDS.items() if k in c.REPEATS},'r3_seed_reserved_if_triggered':c.REPEAT_SEEDS[3],'episode_count':72,'condition_cell_count':36,'scientific_unit':'family','unit_ids_sha256':sha256_value([u['unit_id'] for u in units]),'branch_order_salt':c.BRANCH_ORDER_SALT,'pair_checks_sha256':sha256_value(pair_checks)},'measurement':{'target_success':'existing exact target evaluator','crr':'newly failed initially-satisfied non-target constraints / 2; mechanically sum(not constraint_pass)/2','initial_non_target_constraints_per_arm':2,'crr_equals_one_minus_non_target_preservation':True,'invalid_measurement_disposition':'TECHNICAL_STOP_NO_REPLAY'},'pairing':{'no_update_real_repair_same_scientific_fixture':True,'runtime_scientific_state_sha_required_equal_within_family_arm_repeat':True,'supervisor_instruction_excluded_from_scientific_state_sha':True,'exact_real_repair_injection':'base arm instruction + fixed prefix + exact repair bytes','no_update_contains_repair':False},'quota_policy':{'rolling_limit':500,'pair_start_min_remaining':c.MIN_REMAINING_PAIR,'unit_start_min_remaining':c.MIN_REMAINING_UNIT,'pre_dispatch_hold_resumable':True,'post_dispatch_failure_replay':False,'full_panel_may_span_windows':True,'quota_is_operational_not_scientific':True},'q1_pair':q1,'q1_model_requests':0,'current_usage_observation':usage,'analysis_smoke':smoke,'provider_requests_created':0,'scientific_repeat_outcomes_created':0,'scientific_externality_outcomes_created':0,'runner_sha256':sha256_file(ROOT/'research_pipeline/agent_constraint_externality_atomgit_repeat_execute.py'),'bridge_sha256':sha256_file(ROOT/'research_pipeline/agent_constraint_externality_atomgit_repeat_mcp_bridge.py'),'common_sha256':sha256_file(ROOT/'research_pipeline/agent_constraint_externality_atomgit_repeat_common.py'),'authority':{'development_repeat_qualification':False,'target_only_verification':False,'rq1_rq2':False,'rq3':False,'rq4':False,'paper_claim':False},'next_required_action':'Separate human execution authority for exactly the frozen 72-episode R*=2 development panel. Do not infer or inspect RQ1/RQ2.'}
    out['content_sha256']=sha256_value(out); c.writej(c.READINESS,out)
    pre={'schema_version':'ace-repeat-dev-r2-preflight-v1','object_id':OBJECT_ID,'status':'ATOMGIT_REPEAT_DEV_R2_PREFLIGHT_PASS_AUTHORITY_CLOSED','readiness_content_sha256':out['content_sha256'],'unit_ids_sha256':out['r2_panel']['unit_ids_sha256'],'q1_model_requests':0,'provider_requests_created':0,'scientific_outcomes_created':0,'authority':out['authority']};pre['content_sha256']=sha256_value(pre);c.writej(c.PREFLIGHT,pre)
    return out

def main()->None: print(json.dumps(build(),ensure_ascii=False,sort_keys=True))
if __name__=='__main__': main()
