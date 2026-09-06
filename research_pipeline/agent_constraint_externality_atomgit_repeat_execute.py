from __future__ import annotations

import argparse, json, time
from pathlib import Path
from typing import Any

from research_pipeline import agent_constraint_externality_atomgit_repeat_common as c
from research_pipeline.agent_constraint_externality_appworld_runtime import evaluate_arm_from_materialized_state
from research_pipeline.agent_constraint_externality_atomgit_repeat_dev_reserve_build import OUTPUT_BUNDLE
from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value

ROOT=Path(__file__).resolve().parents[1]
BRIDGE=ROOT/'research_pipeline/agent_constraint_externality_atomgit_repeat_mcp_bridge.py'
RESULT=ROOT/'generated/agent-constraint-externality-atomgit-repeat-r2-result-20260906.json'
ROWS=ROOT/'generated/agent-constraint-externality-atomgit-repeat-r2-measurements-20260906.json'


def mcp_payload(unit:dict[str,Any],root:Path,progress:Path,trajectory:Path,task_id:str)->dict[str,Any]:
    args=['-m','research_pipeline.agent_constraint_externality_atomgit_repeat_mcp_bridge','--bundle',str(OUTPUT_BUNDLE),'--family-id',unit['family_id'],'--arm',unit['arm'],'--branch',unit['branch'],'--repeat',str(unit['repeat']),'--runtime-root',str(root/'appworld'),'--task-id',task_id,'--experiment-name','ace-atomgit-repeat-dev-r2','--progress',str(progress),'--trajectory',str(trajectory),'--tool-call-cap',str(c.TOOL_CALL_CAP)]
    return {'mcpServers':{'appworld':{'command':str(c.APPWORLD_PYTHON),'args':args,'env':{'PYTHONPATH':str(ROOT)},'timeout_ms':30000,'trust':True}}}

def trajectory_audit(path:Path,expected:int)->dict[str,Any]:
    if not path.is_file(): raise c.RepeatStop('repeat trajectory missing')
    rows=[json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]; d=[x for x in rows if x.get('event')=='TOOL_DISPATCH']; z=[x for x in rows if x.get('event')=='TOOL_COMPLETION']; rejected=[x for x in rows if x.get('event')=='TOOL_REJECTED']
    di={x['tool_id']:x for x in d}; zi={x['tool_id']:x for x in z}
    if rejected or len(d)!=expected or len(z)!=expected or len(di)!=expected or set(di)!=set(zi): raise c.RepeatStop('repeat trajectory dangling/duplicate/rejected tool unit')
    return {'row_count':len(rows),'trajectory_sha256':sha256_file(path),'all_tool_dispatches_closed':True}

def prepare_unit(unit:dict[str,Any],root:Path)->tuple[Path,Path,Path,Path,dict[str,Any]]:
    atom,work=c.prepare_atom(root); progress=root/'bridge-progress.json'; trajectory=root/'trajectory.jsonl'; task='acerepr2'+sha256_value(unit['unit_id'])[:14]+'_1'; return atom,work,progress,trajectory,mcp_payload(unit,root,progress,trajectory,task)
def arm_for(unit:dict[str,Any])->dict[str,Any]:
    family=c.family_index()[unit['family_id']]; rows=[a for a in family['arms'] if a['coupling_level']==unit['arm']]
    if len(rows)!=1: raise c.RepeatStop('repeat arm binding drift')
    return rows[0]
def is_pair_first(unit:dict[str,Any])->bool:
    return c.frozen_branch_order(unit['family_id'],unit['arm'],int(unit['repeat']))[0]==unit['branch']

def execute()->dict[str,Any]:
    c.patch_live(); auth=c.verified(c.AUTH,'USER_AUTHORIZED_ATOMGIT_REPEAT_DEV_R2_ONLY'); contract=c.verified(c.CONTRACT,'ATOMGIT_REPEAT_DEV_R2_EXECUTION_AUTHORIZED'); close,manifest,_=c.parents()
    if not auth['authority']['development_repeat_qualification'] or auth['authority'].get('target_only_verification') or auth['authority'].get('rq1_rq2'): raise c.RepeatStop('repeat authority scope drift')
    if contract['human_authorization_content_sha256']!=auth['content_sha256'] or contract['repair_closeout_content_sha256']!=close['content_sha256']: raise c.RepeatStop('repeat execution parent binding drift')
    if contract['runner_sha256']!=sha256_file(Path(__file__)) or contract['bridge_sha256']!=sha256_file(BRIDGE): raise c.RepeatStop('repeat runner/bridge SHA drift')
    expected_units=c.units()
    if contract['unit_ids_sha256']!=sha256_value([u['unit_id'] for u in expected_units]): raise c.RepeatStop('repeat unit manifest drift')
    c.RUN_ROOT.mkdir(parents=True,exist_ok=True); states=c.live.ledger_states(c.LEDGER)
    for unit in expected_units:
        uid=unit['unit_id']; state=states.get(uid)
        if state=='COMPLETION': continue
        if state is not None: return finalize('ATOMGIT_REPEAT_DEV_R2_TECHNICAL_STOP_AFTER_DISPATCH')
        quota=c.usage(); needed=c.MIN_REMAINING_PAIR if is_pair_first(unit) else c.MIN_REMAINING_UNIT
        if int(quota['remaining'])<needed: return {'status':'ATOMGIT_REPEAT_DEV_R2_PRE_DISPATCH_QUOTA_HOLD','next_unit_id':uid,'required_remaining':needed,'codingplan_usage':quota,'model_requests_created_by_hold':0}
        root=c.RUN_ROOT/sha256_value(uid)[:18]
        if root.exists(): raise c.RepeatStop(f'repeat unit root exists before dispatch: {root}')
        root.mkdir(); atom,work,progress,trajectory,payload=prepare_unit(unit,root); proc=None; visible=c.visible_instruction(unit['family_id'],unit['arm'],unit['branch']); repair=c.repair_record(unit['family_id']); arm=arm_for(unit)
        try:
            proc,base,token=c.live.start_daemon(atom_home=atom,workdir=work,log_path=root/'atomcode-daemon.log'); (atom/'mcp.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); c.live.http_json(base,token,'/live/mode',method='POST',body={'mode':'build'})
            def before_submit()->dict[str,Any]:
                p=json.loads(progress.read_text(encoding='utf-8'))
                if p.get('status')!='TOOLS_LISTED': raise c.RepeatStop('repeat MCP tools not listed')
                q=dict(c.live.codingplan_usage(base,token)); required=c.MIN_REMAINING_UNIT
                if int(q['remaining'])<required: raise c.RepeatStop('repeat quota dropped before dispatch')
                state_sha=c.scientific_state_sha(unit['family_id'],Path(p['source_db_root']))
                row={'schema_version':'ace-repeat-dev-r2-ledger-v1','object_id':OBJECT_ID,'execution_id':c.EXECUTION_ID,'event':'DISPATCH','unit_id':uid,'family_id':unit['family_id'],'arm':unit['arm'],'branch':unit['branch'],'repeat':unit['repeat'],'seed':unit['seed'],'provider':c.PROVIDER,'model_profile':c.MODEL_PROFILE,'model_id':c.MODEL_ID,'prompt_sha256':sha256_value(visible),'scientific_fixture_sha256':c.scientific_fixture_sha(unit['family_id']),'scientific_state_sha256':state_sha,'initial_snapshot_sha256_including_instruction':p['initial_snapshot_sha256'],'repair_sha256':repair['repair_sha256'] if unit['branch']=='REAL_REPAIR' else None,'bundle_sha256':sha256_file(OUTPUT_BUNDLE),'codingplan_window_before':q,'attempt':1,'retry_allowed':False,'time_ns':time.time_ns()}; c.live.append_jsonl(c.LEDGER,row); return {'usage_before':q,'scientific_state_sha256':state_sha}
            lr=c.live.run_live_turn(base=base,token=token,instruction=visible,progress_path=progress,before_submit=before_submit,timeout_seconds=480); after=dict(c.live.codingplan_usage(base,token))
            if lr['prohibited_tool'] or lr['error_message'] or lr['stop_reason']!='stopped':
                c.live.append_jsonl(c.LEDGER,{'schema_version':'ace-repeat-dev-r2-ledger-v1','object_id':OBJECT_ID,'execution_id':c.EXECUTION_ID,'event':'FAILURE','unit_id':uid,'family_id':unit['family_id'],'arm':unit['arm'],'branch':unit['branch'],'repeat':unit['repeat'],'failure_class':'REPEAT_INTERFACE_OR_AGENT_LOOP_INVALID','message':str(lr['prohibited_tool'] or lr['error_message'] or lr['stop_reason'])[:400],'codingplan_window_after':after,'retry_attempted':False,'time_ns':time.time_ns()}); return finalize('ATOMGIT_REPEAT_DEV_R2_TECHNICAL_STOP_AFTER_DISPATCH')
        finally:
            if proc is not None: c.live.terminate_process(proc)
        p=json.loads(progress.read_text(encoding='utf-8')); calls=int(p.get('tool_call_count',0))
        try:
            audit=trajectory_audit(trajectory,calls); evaluation=evaluate_arm_from_materialized_state(arm=arm,source_db_root=Path(p['source_db_root']),changes_db_root=Path(p['changes_db_root']),measurement_db_root=root/'measurement-full-dbs'); value=c.crr(evaluation)
        except Exception as exc:
            c.live.append_jsonl(c.LEDGER,{'schema_version':'ace-repeat-dev-r2-ledger-v1','object_id':OBJECT_ID,'execution_id':c.EXECUTION_ID,'event':'FAILURE','unit_id':uid,'family_id':unit['family_id'],'arm':unit['arm'],'branch':unit['branch'],'repeat':unit['repeat'],'failure_class':'REPEAT_MEASUREMENT_INVALID','message':f'{type(exc).__name__}: {exc}'[:400],'retry_attempted':False,'time_ns':time.time_ns()}); return finalize('ATOMGIT_REPEAT_DEV_R2_TECHNICAL_STOP_AFTER_DISPATCH')
        completion={'schema_version':'ace-repeat-dev-r2-ledger-v1','object_id':OBJECT_ID,'execution_id':c.EXECUTION_ID,'event':'COMPLETION','unit_id':uid,'family_id':unit['family_id'],'arm':unit['arm'],'branch':unit['branch'],'repeat':unit['repeat'],'seed':unit['seed'],'valid':True,'target_success':bool(evaluation['target_success']),'crr':value,'non_target_results':evaluation['non_target'],'repair_sha256':repair['repair_sha256'] if unit['branch']=='REAL_REPAIR' else None,'scientific_state_sha256':c.scientific_state_sha(unit['family_id'],Path(p['source_db_root'])),'appworld_tool_call_count':calls,'model_round_count':int(lr['model_round_count']),'prompt_tokens_total':int(lr['prompt_tokens_total']),'completion_tokens_total':int(lr['completion_tokens_total']),'trajectory_sha256':audit['trajectory_sha256'],'trajectory_row_count':audit['row_count'],'codingplan_window_after':after,'time_ns':time.time_ns()}; c.live.append_jsonl(c.LEDGER,completion); states=c.live.ledger_states(c.LEDGER)
    return finalize('ATOMGIT_REPEAT_DEV_R2_PANEL_COMPLETE_PENDING_DIRECTION_BLIND_ADJUDICATION')

def finalize(status:str)->dict[str,Any]:
    rows=c.live.ledger_rows(c.LEDGER) if c.LEDGER.is_file() else []; d=[r for r in rows if r.get('event')=='DISPATCH']; z=[r for r in rows if r.get('event')=='COMPLETION']; f=[r for r in rows if r.get('event')=='FAILURE']
    measurements=[{k:r[k] for k in ('family_id','arm','branch','repeat','valid','target_success','crr','scientific_state_sha256','repair_sha256')} for r in z]
    out={'schema_version':'ace-repeat-dev-r2-result-v1','object_id':OBJECT_ID,'status':status,'execution_id':c.EXECUTION_ID,'planned_episode_count':72,'dispatch_count':len(d),'completion_count':len(z),'failure_count':len(f),'measurement_rows':len(measurements),'ledger_sha256':sha256_file(c.LEDGER) if c.LEDGER.is_file() else None,'scientific_model_round_count':sum(int(r.get('model_round_count',0)) for r in z),'appworld_tool_call_total':sum(int(r.get('appworld_tool_call_count',0)) for r in z),'direction_blind_repeat_decision_not_run':True,'scientific_externality_claim_authority':False,'authority':{'development_repeat_execution_closed':status!='ATOMGIT_REPEAT_DEV_R2_PRE_DISPATCH_QUOTA_HOLD','repeat_analysis':status=='ATOMGIT_REPEAT_DEV_R2_PANEL_COMPLETE_PENDING_DIRECTION_BLIND_ADJUDICATION','target_only_verification':False,'rq1_rq2':False,'rq3':False,'rq4':False,'paper_claim':False}}
    out['content_sha256']=sha256_value(out); ROWS.write_text(json.dumps({'schema_version':'ace-repeat-dev-r2-measurements-v1','object_id':OBJECT_ID,'rows':measurements,'ledger_sha256':out['ledger_sha256']},ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8'); RESULT.write_text(json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8'); return out

def main()->None:
    p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');p.add_argument('--usage-only',action='store_true');a=p.parse_args()
    if a.usage_only: print(json.dumps({'status':'ZERO_REQUEST_USAGE_PROBE','usage':c.usage(),'model_requests':0},sort_keys=True));return
    if not a.execute: raise SystemExit('--execute required')
    print(json.dumps(execute(),ensure_ascii=False,sort_keys=True))
if __name__=='__main__': main()
