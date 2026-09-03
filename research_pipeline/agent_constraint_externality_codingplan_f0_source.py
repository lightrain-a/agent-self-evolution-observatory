from __future__ import annotations

import argparse, json, os, queue, shutil, threading, time, urllib.request
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_appworld_runtime import evaluate_arm_from_materialized_state
from research_pipeline.agent_constraint_externality_codingplan_mimo25pro_live import (
    APPWORLD_PYTHON, APPWORLD_ROOT, BASE_URL, CONTEXT_WINDOW, MODEL_ID, MODEL_PROFILE,
    MODEL_ROUND_CAP, PROVIDER, RETRY_MAX_ATTEMPTS, V4_BUNDLE,
)
import research_pipeline.agent_constraint_externality_codingplan_qwen38_capability as live
from research_pipeline.agent_constraint_externality_f0_execute import (
    F0_FAMILIES, enumerate_source_units, freeze_repair, target_only_updater_payload,
)
from research_pipeline.agent_constraint_externality_runner_core import (
    OBJECT_ID, AppendOnlyLedger, EpisodeUnit, RunnerError, canonical_bytes,
    sha256_file, sha256_value,
)
from research_pipeline.appworld_constraint_compiler import load_protected_spec

ROOT=Path(__file__).resolve().parents[1]; GENERATED=ROOT/'generated'
PROTOCOL=GENERATED/'agent-constraint-externality-f0-frozen-protocol-20260831.json'
SELECTION=GENERATED/'agent-constraint-externality-capability-backbone-selection-final-20260903.json'
CAP_RESULT=GENERATED/'agent-constraint-externality-codingplan-mimo25pro-capability-b3-result-20260903.json'
CAP_CLOSEOUT=GENERATED/'agent-constraint-externality-codingplan-mimo25pro-capability-b3-closeout-20260903.json'
AUTH=GENERATED/'agent-constraint-externality-f0-human-authorization-20260903.json'
ADDENDUM=GENERATED/'agent-constraint-externality-f0-mimo25pro-transport-addendum-20260903.json'
Q1=GENERATED/'agent-constraint-externality-f0-mimo25pro-mcp-q1-predispatch-20260903.json'
CONTRACT=GENERATED/'agent-constraint-externality-f0-mimo25pro-source-contract-20260903.json'
REPAIRS_DIR=GENERATED/'agent-constraint-externality-f0-repairs-mimo25pro-20260903'
REPAIRS_MANIFEST=GENERATED/'agent-constraint-externality-f0-repairs-manifest-mimo25pro-20260903.json'
BRIDGE=ROOT/'research_pipeline/agent_constraint_externality_codingplan_f0_mcp_bridge.py'
RUNTIME=ROOT/'runtimes/agent-constraint-externality-f0-mimo25pro-20260903'
SOURCE_LEDGER=RUNTIME/'source-ledger.jsonl'; UPDATER_LEDGER=RUNTIME/'updater-ledger.jsonl'
SOURCE_ROOT=RUNTIME/'source'; UPDATER_ROOT=RUNTIME/'updater'
EXECUTION_ID='ACE-F0-MIMO25PRO-20260903'; TOOL_CALL_CAP=16

class F0Stop(RunnerError): pass

def readj(p:Path)->dict[str,Any]: return json.loads(p.read_text(encoding='utf-8'))
def writej(p:Path,x:dict[str,Any])->None:
    p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def verified(p:Path,status:str|None=None)->dict[str,Any]:
    x=readj(p)
    if x.get('object_id')!=OBJECT_ID: raise F0Stop(f'object mismatch: {p}')
    if status and x.get('status')!=status: raise F0Stop(f'status mismatch: {p}: {x.get("status")}')
    h=x.get('content_sha256')
    if h:
        y=dict(x); y.pop('content_sha256',None)
        if h!=sha256_value(y): raise F0Stop(f'content hash mismatch: {p}')
    return x

def patch_live()->None:
    live.MODEL_PROFILE=MODEL_PROFILE; live.TOOL_CALL_CAP=TOOL_CALL_CAP; live.MODEL_ROUND_CAP=MODEL_ROUND_CAP

def atom_config(updater:bool=False)->str:
    system=('Output exactly one concise persistent procedural repair note based only on supplied target failure evidence. Do not use tools.' if updater else 'Complete the AppWorld task using only AppWorld MCP tools. Preserve unrelated state. Batch independent AppWorld tool calls when possible.')
    return f'''default_provider = "{MODEL_PROFILE}"
default_model = "{MODEL_PROFILE}"
auto_update = false
auto_commit = false
[provider_accounts.AtomGit]
provider = "openai"
base_url = "{BASE_URL}"
[models."{MODEL_PROFILE}"]
account = "AtomGit"
model = "{MODEL_ID}"
context_window = {CONTEXT_WINDOW}
retry_max_attempts = {RETRY_MAX_ATTEMPTS}
system_prompt = "{system}"
[loop_config]
max_rounds = {MODEL_ROUND_CAP}
[coding]
max_rounds = {MODEL_ROUND_CAP}
shell_guard_policy = "prompt"
[tools.todo]
enabled = false
[ui]
ai_session_naming = false
'''
def prep_atom(root:Path,updater:bool=False)->tuple[Path,Path]:
    root=root.resolve(); ah=root/'atomcode-home'; wd=root/'atomcode-workdir'; ah.mkdir(parents=True,exist_ok=False); wd.mkdir(parents=True,exist_ok=False)
    src=Path.home()/'.atomcode/auth.toml'
    if not src.is_file(): raise F0Stop('AtomCode auth missing')
    shutil.copy2(src,ah/'auth.toml'); os.chmod(ah/'auth.toml',0o600)
    (ah/'config.toml').write_text(atom_config(updater),encoding='utf-8')
    msg='# F0 updater\nDo not use tools. Output only the repair note.\n' if updater else '# F0 AppWorld run\nUse only mcp__appworld__ tools. Never use host coding, shell, web, memory, agent, skill, or code-graph tools. Preserve unrelated AppWorld state.\n'
    (wd/'AGENTS.md').write_text(msg,encoding='utf-8'); return ah,wd

def source_arm(fam:dict[str,Any])->dict[str,Any]:
    ref=next(a for a in fam['arms'] if a['coupling_level']=='INDEPENDENT'); arm=dict(ref)
    arm['task_instruction']=fam['target_instruction']; arm['constraints']=[c for c in ref['constraints'] if c['role']=='TARGET']; return arm

def mcp_payload(*,family_id:str,instruction:Path,root:Path,progress:Path,trajectory:Path,task_id:str)->dict[str,Any]:
    args=['-m','research_pipeline.agent_constraint_externality_codingplan_f0_mcp_bridge','--appworld-root',str(APPWORLD_ROOT),'--bundle',str(V4_BUNDLE),'--family-id',family_id,'--coupling-level','INDEPENDENT','--instruction-file',str(instruction),'--source-target-only','--seed','1200','--runtime-root',str(root/'appworld'),'--task-id',task_id,'--experiment-name','ace-f0-mimo25pro-source','--progress',str(progress),'--trajectory',str(trajectory),'--tool-call-cap',str(TOOL_CALL_CAP)]
    return {'mcpServers':{'appworld':{'command':str(APPWORLD_PYTHON),'args':args,'env':{'PYTHONPATH':str(ROOT)},'timeout_ms':30000,'trust':True}}}

def task_run(unit:EpisodeUnit,fam:dict[str,Any],arm:dict[str,Any],root:Path,ledger:AppendOnlyLedger)->dict[str,Any]:
    patch_live(); state=ledger.states().get(unit.unit_id)
    if state=='COMPLETION': return next(r for r in ledger.rows() if r['unit_id']==unit.unit_id and r['event']=='COMPLETION')['result']
    if state is not None: raise F0Stop(f'replay forbidden: {unit.unit_id}: {state}')
    if root.exists(): raise F0Stop(f'unit root exists: {root}')
    root.mkdir(parents=True); ah,wd=prep_atom(root); instruction=root/'instruction.txt'; progress=root/'progress.json'; trajectory=root/'trajectory.jsonl'
    instruction.write_text(fam['target_instruction'],encoding='utf-8'); task_id='acef0'+sha256_value(unit.unit_id)[:12]+'_1'
    process=None
    try:
        process,base,token=live.start_daemon(atom_home=ah,workdir=wd,log_path=root/'daemon.log')
        (ah/'mcp.json').write_text(json.dumps(mcp_payload(family_id=unit.family_id,instruction=instruction,root=root,progress=progress,trajectory=trajectory,task_id=task_id),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        live.http_json(base,token,'/live/mode',method='POST',body={'mode':'build'})
        def before()->dict[str,Any]:
            p=readj(progress)
            if p.get('status')!='TOOLS_LISTED': raise F0Stop('MCP tools not listed')
            usage=live.codingplan_usage(base,token)
            if int(usage['remaining'])<MODEL_ROUND_CAP+5: raise F0Stop('insufficient CodingPlan headroom')
            ledger.dispatch(unit,prompt_sha256=sha256_value(fam['target_instruction']),snapshot_sha256=p['initial_snapshot_sha256'],repair_sha256=None,requested_model=MODEL_ID,provider=PROVIDER,base_url='ATOMCODE_SIGNED_DAEMON_LOCAL')
            return {'usage_before':usage}
        lr=live.run_live_turn(base=base,token=token,instruction=fam['target_instruction'],progress_path=progress,before_submit=before)
        usage_before=dict(lr['pre_submit']['usage_before']); time.sleep(.2); usage_after=live.codingplan_usage(base,token)
        if lr['prohibited_tool']:
            ledger.fail(unit,failure_class='F0_HARNESS_CONTAMINATION',message=str(lr['prohibited_tool']),receipts=[]); raise F0Stop('prohibited tool')
        if lr['error_message'] or lr['stop_reason']!='stopped':
            msg=str(lr['error_message'] or lr['stop_reason']); ledger.fail(unit,failure_class='F0_INCOMPLETE_AGENT_LOOP',message=msg[:400],receipts=[]); raise F0Stop(msg)
    finally:
        if process is not None: live.terminate_process(process)
    p=readj(progress); ev=evaluate_arm_from_materialized_state(arm=arm,source_db_root=Path(p['source_db_root']),changes_db_root=Path(p['changes_db_root']),measurement_db_root=root/'measurement-full-dbs')
    result={'evaluation':ev,'tool_loop_completed':True,'atomcode_stop_reason':lr['stop_reason'],'appworld_tool_call_count':int(p.get('tool_call_count',0)),'model_round_count':int(lr['model_round_count']),'prompt_tokens_total':int(lr['prompt_tokens_total']),'completion_tokens_total':int(lr['completion_tokens_total']),'codingplan_window_before':usage_before,'codingplan_window_after':usage_after,'trajectory_path':str(trajectory),'trajectory_sha256':sha256_file(trajectory) if trajectory.is_file() else sha256_value([]),'bridge_progress_sha256':sha256_file(progress)}
    ledger.complete(unit,receipts=[],result=result); return result

def updater_generate(family_id:str,payload:dict[str,Any],trajectory_sha:str)->tuple[bytes,bytes,dict[str,Any]]:
    unit=EpisodeUnit(namespace='source',key=(family_id,'updater'),stage='F0_REPAIR_GENERATION',family_id=family_id); ledger=AppendOnlyLedger(UPDATER_LEDGER)
    if ledger.states().get(unit.unit_id) is not None: raise F0Stop(f'updater replay forbidden: {unit.unit_id}')
    root=UPDATER_ROOT/family_id.lower()
    if root.exists(): raise F0Stop(f'updater root exists: {root}')
    root.mkdir(parents=True); ah,wd=prep_atom(root,True); process=None; stop=threading.Event(); errors:list[str]=[]; events:'queue.Queue[dict[str,Any]]'=queue.Queue()
    prompt='Write one concise persistent procedural repair note for the target failure. Do not discuss other constraints, topology, coupling, or arm assignment. Output only the note.\n\n'+canonical_bytes(payload).decode('utf-8')
    try:
        process,base,token=live.start_daemon(atom_home=ah,workdir=wd,log_path=root/'daemon.log'); req=urllib.request.Request(base+'/live',headers={'Authorization':'Bearer '+token})
        def stream()->None:
            try:
                with urllib.request.urlopen(req,timeout=390) as response:
                    for raw in response:
                        if stop.is_set(): break
                        line=raw.decode('utf-8','replace').strip()
                        if not line.startswith('data:'): continue
                        try: events.put(json.loads(line[5:].strip()))
                        except Exception: continue
            except Exception as exc: errors.append(f'{type(exc).__name__}: {exc}'); events.put({'type':'stream_exception','message':errors[-1]})
        th=threading.Thread(target=stream,daemon=True); th.start(); time.sleep(.5); before=live.codingplan_usage(base,token)
        ledger.dispatch(unit,prompt_sha256=sha256_value(payload),snapshot_sha256=trajectory_sha,repair_sha256=None,requested_model=MODEL_ID,provider=PROVIDER,base_url='ATOMCODE_SIGNED_DAEMON_LOCAL')
        submit=live.http_json(base,token,'/live/message',method='POST',body={'message':prompt,'provider':MODEL_PROFILE,'client_input_id':'ace-f0-updater'})
        if submit.get('accepted') is not True: ledger.fail(unit,failure_class='F0_UPDATER_SUBMIT_REJECTED',message=str(submit)[:400],receipts=[]); raise F0Stop('updater submit rejected')
        text:list[str]=[]; toks:list[dict[str,int]]=[]; saw=False; reason=None; err=None; deadline=time.time()+360
        while time.time()<deadline:
            try: e=events.get(timeout=.5)
            except queue.Empty: continue
            k=e.get('type')
            if k=='text': text.append(str(e.get('content','')))
            elif k=='tokens': toks.append({'prompt':int(e.get('prompt',0)),'completion':int(e.get('completion',0))})
            elif k in {'tool_start','permission_request'}: err='UPDATER_TOOL_USE_FORBIDDEN'; break
            elif k in {'error','stream_exception'}: err=str(e.get('message',k)); break
            elif k=='state':
                running=bool(e.get('running')); saw=saw or running
                if not running and saw: reason=str(e.get('stop_reason') or 'unknown'); break
        stop.set(); after=live.codingplan_usage(base,token)
        if err or reason!='stopped': ledger.fail(unit,failure_class='F0_UPDATER_INCOMPLETE',message=str(err or reason)[:400],receipts=[]); raise F0Stop(str(err or reason))
        raw_text=''.join(text)
        if not raw_text.strip(): ledger.fail(unit,failure_class='F0_UPDATER_EMPTY',message='empty',receipts=[]); raise F0Stop('empty updater')
        raw=raw_text.encode(); norm=raw_text.replace('\r\n','\n').strip().encode(); meta={'surface':'PERSISTENT_PROCEDURAL_REPAIR_NOTE','raw_sha256':sha256_value(raw_text),'normalized_sha256':sha256_value(norm.decode()),'raw_byte_length':len(raw),'normalized_byte_length':len(norm),'word_count':len(norm.decode().split()),'fixed_tokenizer':'UTF8_WHITESPACE_V1','fixed_tokenizer_token_count':len(norm.decode().split()),'procedural_clause_count':sum(1 for x in norm.decode().replace(';','.').split('.') if x.strip()),'injection_position':'AFTER_TASK_INSTRUCTION','exposure_rule':'UPDATE_ONLY_EXACT_BYTES','generation_model_id':MODEL_ID,'generation_requested_model_id':MODEL_ID,'generation_resolved_model_id':MODEL_ID,'generation_model_profile':MODEL_PROFILE,'generation_request_sha256':sha256_value(payload),'source_trajectory_sha256':trajectory_sha,'generation_model_round_count':len(toks),'generation_prompt_tokens_total':sum(x['prompt'] for x in toks),'generation_completion_tokens_total':sum(x['completion'] for x in toks),'codingplan_window_before':before,'codingplan_window_after':after}
        ledger.complete(unit,receipts=[],result={'metadata':meta}); return raw,norm,meta
    finally:
        stop.set()
        if process is not None: live.terminate_process(process)

def rec_path(fid:str)->Path: return GENERATED/f'agent-constraint-externality-f0-repair-record-{fid.lower()}-mimo25pro-20260903.json'

def run_source(fid:str)->dict[str,Any]:
    verified(CONTRACT,'F0_CODINGPLAN_MIMO25PRO_SOURCE_AUTHORIZED')
    if fid not in F0_FAMILIES: raise F0Stop('unknown F0 family')
    spec=load_protected_spec(V4_BUNDLE); fam=next(x for x in spec['families'] if x['family_id']==fid); arm=source_arm(fam); unit=next(x for x in enumerate_source_units() if x.family_id==fid)
    result=task_run(unit,fam,arm,SOURCE_ROOT/fid.lower(),AppendOnlyLedger(SOURCE_LEDGER)); success=bool(result['evaluation']['target_success'])
    if success: return {'family_id':fid,'target_success':True,'repair_generated':False}
    rp=rec_path(fid)
    if rp.exists(): raise F0Stop('repair record exists')
    tp=Path(result['trajectory_path']); traj=[json.loads(x) for x in tp.read_text(encoding='utf-8').splitlines() if x.strip()]
    targets=[c for c in arm['constraints'] if c['role']=='TARGET']; payload=target_only_updater_payload(target_constraint_spec={'constraints':targets},target_task_instruction=fam['target_instruction'],target_failure_slice=result['evaluation']['target'],target_tool_trajectory=traj)
    raw,norm,meta=updater_generate(fid,payload,sha256_value(traj)); rec=freeze_repair(REPAIRS_DIR,fid,norm,meta,raw_bytes=raw); rec['object_id']=OBJECT_ID; rec['source_unit_id']=unit.unit_id; rec['source_evaluation_sha256']=sha256_value(result['evaluation']); rec['record_content_sha256']=sha256_value(rec); writej(rp,rec)
    return {'family_id':fid,'target_success':False,'repair_generated':True,'repair_sha256':rec['repair_sha256']}

def finalize_sources()->dict[str,Any]:
    verified(CONTRACT,'F0_CODINGPLAN_MIMO25PRO_SOURCE_AUTHORIZED'); ledger=AppendOnlyLedger(SOURCE_LEDGER); states=ledger.states(); expected={u.unit_id for u in enumerate_source_units()}
    if set(states)!=expected or any(v!='COMPLETION' for v in states.values()): raise F0Stop('all eight source units must complete')
    repairs:dict[str,Any]={}
    for fid in F0_FAMILIES:
        p=rec_path(fid)
        if p.is_file():
            r=readj(p); h=r.get('record_content_sha256'); y=dict(r); y.pop('record_content_sha256',None)
            if h!=sha256_value(y): raise F0Stop(f'repair record hash mismatch: {fid}')
            repairs[fid]=r
    eligible=[f for f in F0_FAMILIES if f in repairs]; norepair=[f for f in F0_FAMILIES if f not in repairs]
    m={'schema_version':'ace-f0-repairs-v1','object_id':OBJECT_ID,'status':'F0_SOURCE_COMPLETE' if len(eligible)>=6 else 'F0_UPDATE_UPTAKE_INSUFFICIENT_STOP','source_family_count':8,'eligible_families':eligible,'no_repair_eligible':norepair,'repairs':repairs,'updater_model_request_count':len(repairs),'repair_generation_provider_request_cap':8,'human_edits':0,'source_ledger_sha256':sha256_file(SOURCE_LEDGER),'updater_ledger_sha256':sha256_file(UPDATER_LEDGER) if UPDATER_LEDGER.is_file() else None,'selected_backbone':{'provider':PROVIDER,'model_profile':MODEL_PROFILE,'model_id':MODEL_ID,'harness':'ATOMCODE_CODINGPLAN_MCP_V1'},'scientific_outcomes_observed':0,'authority':{'probe':False,'p1':False,'toolsandbox':False,'appworld_ul':False,'paper_claim':False}}
    m['manifest_content_sha256']=sha256_value(m); writej(REPAIRS_MANIFEST,m); return m

def qualify_q1()->dict[str,Any]:
    patch_live(); fid=F0_FAMILIES[0]; spec=load_protected_spec(V4_BUNDLE); fam=next(x for x in spec['families'] if x['family_id']==fid)
    import tempfile
    with tempfile.TemporaryDirectory(prefix='ace-f0-q1-') as d:
        root=Path(d); ah,wd=prep_atom(root); inst=root/'instruction.txt'; inst.write_text(fam['target_instruction'],encoding='utf-8'); progress=root/'progress.json'; traj=root/'trajectory.jsonl'; task='acef0q1_1'; process=None; done=threading.Event(); errors:list[str]=[]
        try:
            process,base,token=live.start_daemon(atom_home=ah,workdir=wd,log_path=root/'daemon.log'); (ah/'mcp.json').write_text(json.dumps(mcp_payload(family_id=fid,instruction=inst,root=root,progress=progress,trajectory=traj,task_id=task),ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); live.http_json(base,token,'/live/mode',method='POST',body={'mode':'build'}); before=int(live.codingplan_usage(base,token)['used']); req=urllib.request.Request(base+'/live',headers={'Authorization':'Bearer '+token})
            def stream()->None:
                try:
                    with urllib.request.urlopen(req,timeout=60) as response:
                        for _ in response:
                            if done.is_set(): break
                except Exception as exc:
                    if not done.is_set(): errors.append(f'{type(exc).__name__}: {exc}')
            th=threading.Thread(target=stream,daemon=True); th.start(); deadline=time.time()+45
            while time.time()<deadline:
                if errors: raise F0Stop(errors[-1])
                if progress.is_file() and readj(progress).get('status')=='TOOLS_LISTED': break
                time.sleep(.1)
            else: raise F0Stop('Q1 tools not listed')
            after=int(live.codingplan_usage(base,token)['used']); live.http_json(base,token,'/live/stop',method='POST',body={}); done.set(); th.join(timeout=2); p=readj(progress); out={'schema_version':'ace-f0-mimo25pro-mcp-q1-v1','object_id':OBJECT_ID,'status':'F0_CODINGPLAN_MIMO25PRO_MCP_PREDISPATCH_PASS','model_profile':MODEL_PROFILE,'model_id':MODEL_ID,'session_mcp_progress_status':p.get('status'),'codingplan_model_requests':after-before,'scientific_dispatch_sent':False,'bridge_source_sha256':sha256_file(BRIDGE),'runner_source_sha256':sha256_file(Path(__file__)),'bundle_sha256':sha256_file(V4_BUNDLE),'scientific_outcomes_observed':0}
            if out['codingplan_model_requests']!=0 or out['session_mcp_progress_status']!='TOOLS_LISTED': raise F0Stop('Q1 zero-request check failed')
            out['content_sha256']=sha256_value(out); return out
        finally:
            done.set()
            if process is not None: live.terminate_process(process)

def freeze_authority()->dict[str,Any]:
    protocol=readj(PROTOCOL); selection=verified(SELECTION,'CAPABILITY_BACKBONE_SELECTED_MIMO25PRO_PASS'); result=verified(CAP_RESULT,'CAPABILITY_CALIBRATION_PASS'); close=verified(CAP_CLOSEOUT,'CODINGPLAN_MIMO25PRO_B3_PASS_CLOSEOUT')
    expected={'provider':PROVIDER,'model_profile':MODEL_PROFILE,'model_id':MODEL_ID,'harness':'ATOMCODE_CODINGPLAN_MCP_V1'}
    if selection['selected_backbone']!=expected: raise F0Stop('selected backbone drifted')
    auth={'schema_version':'ace-f0-human-authorization-v1','object_id':OBJECT_ID,'status':'USER_AUTHORIZED_F0_AFTER_MIMO25PRO_CAPABILITY_PASS','authorized_at':'2026-09-03T14:41:00+08:00','authorization_source':'CURRENT_SESSION_USER_MESSAGE_CONTINUE_AFTER_EXPLICIT_F0_AUTHORIZATION_GATE','selected_backbone_content_sha256':selection['content_sha256'],'scope':'F0_ONLY_SOURCE_REPAIR_AND_CONDITIONAL_PROBES_UNDER_FROZEN_PROTOCOL','authority':{'f0':True,'p1':False,'toolsandbox':False,'appworld_ul':False,'paper_claim':False},'scientific_outcomes_observed':0}; auth['content_sha256']=sha256_value(auth); writej(AUTH,auth)
    add={'schema_version':'ace-f0-selected-backbone-transport-addendum-v1','object_id':OBJECT_ID,'status':'F0_SELECTED_BACKBONE_TRANSPORT_COMPATIBILITY_ADDENDUM_PASS','frozen_protocol_artifact':str(PROTOCOL.relative_to(ROOT)),'frozen_protocol_file_sha256':sha256_file(PROTOCOL),'legacy_preselection_harness_field':protocol['harness'],'selected_backbone_harness':'ATOMCODE_CODINGPLAN_MCP_V1','reason':'F0 executes the selected backbone under the same harness used for valid capability calibration; the legacy harness field predated final backbone selection.','scientific_variables_changed':[],'preserved':['family_ids','source_phase','probe_phase','update_surface','metrics','adjudication','exactly_once','post_f0_authority'],'selected_backbone_content_sha256':selection['content_sha256'],'capability_result_content_sha256':result['content_sha256'],'authority':{'f0_transport':True,'p1':False,'toolsandbox':False,'appworld_ul':False,'paper_claim':False},'scientific_outcomes_observed':0}; add['content_sha256']=sha256_value(add); writej(ADDENDUM,add)
    q=qualify_q1(); writej(Q1,q)
    c={'schema_version':'ace-f0-codingplan-mimo25pro-source-contract-v1','object_id':OBJECT_ID,'execution_id':EXECUTION_ID,'status':'F0_CODINGPLAN_MIMO25PRO_SOURCE_AUTHORIZED','authorization_content_sha256':auth['content_sha256'],'transport_addendum_content_sha256':add['content_sha256'],'q1_content_sha256':q['content_sha256'],'selected_backbone_content_sha256':selection['content_sha256'],'capability_closeout_content_sha256':close['content_sha256'],'model':{'provider':PROVIDER,'profile':MODEL_PROFILE,'id':MODEL_ID,'context_window':CONTEXT_WINDOW,'retry_max_attempts':RETRY_MAX_ATTEMPTS},'harness':{'id':'ATOMCODE_CODINGPLAN_MCP_V1','appworld_tool_call_cap':TOOL_CALL_CAP,'model_round_cap_per_episode':MODEL_ROUND_CAP,'retry_allowed':False,'replacement_allowed':False,'ai_session_naming':False,'subagents':False},'source_phase':protocol['source_phase'],'probe_phase':protocol['probe_phase'],'metrics':protocol['metrics'],'adjudication':protocol['adjudication'],'exactly_once':protocol['exactly_once'],'execution_policy':{'source_now':True,'repair_generation_now':True,'probe_only_after_repair_manifest_frozen_and_committed':True,'partial_probe_effects_readable':False},'authority':{'source':True,'repair_generation':True,'probe':False,'f0':True,'p1':False,'toolsandbox':False,'appworld_ul':False,'paper_claim':False},'scientific_outcomes_observed':0}; c['content_sha256']=sha256_value(c); writej(CONTRACT,c); return {'authorization':auth,'addendum':add,'q1':q,'contract':c}

def main()->None:
    p=argparse.ArgumentParser(); p.add_argument('--freeze',action='store_true'); p.add_argument('--source-unit',choices=list(F0_FAMILIES)); p.add_argument('--finalize-sources',action='store_true'); a=p.parse_args(); n=sum(bool(x) for x in [a.freeze,a.source_unit,a.finalize_sources]);
    if n!=1: raise SystemExit('choose exactly one action')
    if a.freeze:
        x=freeze_authority(); print(json.dumps({'authorization':x['authorization']['status'],'q1':x['q1']['status'],'q1_model_requests':x['q1']['codingplan_model_requests'],'contract':x['contract']['status'],'f0_authorized':True,'p1_authorized':False},sort_keys=True))
    elif a.source_unit: print(json.dumps(run_source(a.source_unit),sort_keys=True))
    else:
        x=finalize_sources(); print(json.dumps({'status':x['status'],'eligible_family_count':len(x['eligible_families']),'eligible_families':x['eligible_families'],'updater_model_request_count':x['updater_model_request_count']},sort_keys=True))
if __name__=='__main__': main()
