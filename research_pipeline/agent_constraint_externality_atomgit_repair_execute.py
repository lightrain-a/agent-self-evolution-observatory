from __future__ import annotations

import argparse, json, queue, threading, time, urllib.request
from pathlib import Path
from typing import Any

from research_pipeline import agent_constraint_externality_atomgit_repair_common as c
from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, canonical_bytes, sha256_file, sha256_value


def freeze_repair(fid:str,raw_text:str,meta:dict[str,Any])->dict[str,Any]:
    raw_path,repair_path,record_path=c.repair_paths(fid); c.REPAIRS.mkdir(parents=True,exist_ok=True)
    if raw_path.exists() or repair_path.exists() or record_path.exists(): raise c.RepairStop(f'repair exists: {fid}')
    raw=raw_text.encode(); norm=raw_text.replace('\r\n','\n').strip().encode(); raw_path.write_bytes(raw); repair_path.write_bytes(norm)
    r={'schema_version':'ace-repeat-dev-repair-record-v1','object_id':OBJECT_ID,'family_id':fid,'surface':'PERSISTENT_PROCEDURAL_REPAIR_NOTE','raw_repair_path':str(raw_path.relative_to(c.ROOT)),'raw_repair_sha256':sha256_file(raw_path),'raw_repair_byte_length':len(raw),'repair_path':str(repair_path.relative_to(c.ROOT)),'repair_sha256':sha256_file(repair_path),'repair_byte_length':len(norm),'human_edited':False,**meta}
    r['content_sha256']=sha256_value(r); c.writej(record_path,r); return r

def run_family(proj:dict[str,Any],fid:str,remaining:int)->dict[str,Any]:
    uid=c.unit_id(fid)
    if c.ledger_states().get(uid) is not None: raise c.RepairStop(f'replay forbidden: {uid}')
    payload=c.writer_payload(proj,fid); root=c.RUN_ROOT/fid.lower()
    if root.exists(): raise c.RepairStop(f'unit root exists: {root}')
    root.mkdir(parents=True); atom,work=c.prepare_atom(root); proc=None; stop=threading.Event(); errors=[]; events:queue.Queue[dict[str,Any]]=queue.Queue()
    prompt='Write exactly one concise persistent procedural repair note for this target failure. Use only the supplied target-only evidence. Do not use tools or mention hidden experiment structure. Output only the repair note.\n\n'+canonical_bytes(payload).decode()
    req_sha=sha256_value(payload)
    try:
        proc,base,token=c.live.start_daemon(atom_home=atom,workdir=work,log_path=root/'daemon.log'); before=dict(c.live.codingplan_usage(base,token)); need=remaining+c.QUOTA_MARGIN
        if int(before['remaining'])<need: raise c.RepairStop(f'quota hold before dispatch: need {need}, have {before["remaining"]}')
        request=urllib.request.Request(base+'/live',headers={'Authorization':'Bearer '+token})
        def stream()->None:
            try:
                with urllib.request.urlopen(request,timeout=390) as response:
                    for raw in response:
                        if stop.is_set(): break
                        line=raw.decode('utf-8','replace').strip()
                        if not line.startswith('data:'): continue
                        try: events.put(json.loads(line[5:].strip()))
                        except Exception: pass
            except Exception as exc:
                errors.append(f'{type(exc).__name__}: {exc}'); events.put({'type':'stream_exception','message':errors[-1]})
        th=threading.Thread(target=stream,daemon=True); th.start(); time.sleep(.4)
        c.append_ledger({'schema_version':'ace-repeat-dev-repair-ledger-v1','object_id':OBJECT_ID,'execution_id':c.EXECUTION_ID,'event':'DISPATCH','unit_id':uid,'family_id':fid,'provider':c.PROVIDER,'model_profile':c.MODEL_PROFILE,'model_id':c.MODEL_ID,'prompt_sha256':req_sha,'projection_family_sha256':sha256_value(proj['families'][fid]),'codingplan_window_before':before,'attempt':1,'retry_allowed':False,'time_ns':time.time_ns()})
        submit=c.live.http_json(base,token,'/live/message',method='POST',body={'message':prompt,'provider':c.MODEL_PROFILE,'client_input_id':'ace-repeat-dev-repair'})
        if submit.get('accepted') is not True:
            c.append_ledger({'schema_version':'ace-repeat-dev-repair-ledger-v1','object_id':OBJECT_ID,'execution_id':c.EXECUTION_ID,'event':'FAILURE','unit_id':uid,'family_id':fid,'failure_class':'REPAIR_SUBMIT_REJECTED_AFTER_DISPATCH','message':str(submit)[:400],'retry_attempted':False,'time_ns':time.time_ns()}); raise c.RepairStop('submit rejected')
        chunks=[]; toks=[]; saw=False; reason=None; failure=None; deadline=time.time()+360
        while time.time()<deadline:
            try: e=events.get(timeout=.5)
            except queue.Empty:
                if errors: failure=errors[-1]; break
                continue
            k=e.get('type')
            if k=='text': chunks.append(str(e.get('content','')))
            elif k=='tokens': toks.append({'prompt':int(e.get('prompt',0)),'completion':int(e.get('completion',0))})
            elif k in {'tool_start','permission_request'}: failure='REPAIR_TOOL_USE_FORBIDDEN'; break
            elif k in {'error','stream_exception'}: failure=str(e.get('message',k)); break
            elif k=='state':
                running=bool(e.get('running')); saw=saw or running
                if not running and saw: reason=str(e.get('stop_reason') or 'unknown'); break
        stop.set(); after=dict(c.live.codingplan_usage(base,token)); th.join(timeout=2)
        if failure or reason!='stopped' or len(toks)!=1:
            c.append_ledger({'schema_version':'ace-repeat-dev-repair-ledger-v1','object_id':OBJECT_ID,'execution_id':c.EXECUTION_ID,'event':'FAILURE','unit_id':uid,'family_id':fid,'failure_class':'REPAIR_WRITER_PROTOCOL_INVALID','message':str(failure or reason or f'model_rounds={len(toks)}')[:400],'retry_attempted':False,'codingplan_window_after':after,'time_ns':time.time_ns()}); raise c.RepairStop(f'writer invalid: {fid}')
        text=''.join(chunks)
        if not text.strip(): raise c.RepairStop(f'empty repair: {fid}')
        if any(term in text.lower() for term in c.FORBIDDEN_REPAIR_TERMS): raise c.RepairStop(f'structural contamination: {fid}')
        meta={'generation_model_id':c.MODEL_ID,'generation_model_profile':c.MODEL_PROFILE,'generation_request_sha256':req_sha,'projected_tool_trajectory_sha256':proj['families'][fid]['projected_tool_trajectory_sha256'],'target_failure_slice_sha256':proj['families'][fid]['target_failure_slice_sha256'],'generation_model_round_count':1,'generation_prompt_tokens_total':toks[0]['prompt'],'generation_completion_tokens_total':toks[0]['completion'],'codingplan_window_before':before,'codingplan_window_after':after,'injection_position':'AFTER_TASK_INSTRUCTION','exposure_rule':'UPDATE_ONLY_EXACT_BYTES'}
        rec=freeze_repair(fid,text,meta)
        c.append_ledger({'schema_version':'ace-repeat-dev-repair-ledger-v1','object_id':OBJECT_ID,'execution_id':c.EXECUTION_ID,'event':'COMPLETION','unit_id':uid,'family_id':fid,'repair_sha256':rec['repair_sha256'],'repair_record_sha256':rec['content_sha256'],'model_round_count':1,'prompt_tokens_total':toks[0]['prompt'],'completion_tokens_total':toks[0]['completion'],'codingplan_window_after':after,'time_ns':time.time_ns()}); return rec
    finally:
        stop.set()
        if proc is not None: c.live.terminate_process(proc)

def record_for(fid:str)->dict[str,Any]|None:
    _,repair,record=c.repair_paths(fid)
    if not record.is_file(): return None
    x=c.readj(record); h=x.get('content_sha256'); y=dict(x); y.pop('content_sha256',None)
    if h!=sha256_value(y) or not repair.is_file() or x.get('repair_sha256')!=sha256_file(repair): raise c.RepairStop(f'repair integrity drift: {fid}')
    return x

def finalize(proj:dict[str,Any])->dict[str,Any]:
    rows=c.ledger_rows(); d=[r for r in rows if r.get('event')=='DISPATCH']; ok=[r for r in rows if r.get('event')=='COMPLETION']; bad=[r for r in rows if r.get('event')=='FAILURE']; expected={c.unit_id(fid) for fid in c.selected_ids(proj)}
    if bad: status='ATOMGIT_REPEAT_DEV_REPAIR_GENERATION_TECHNICAL_STOP_NO_REPEAT_AUTHORITY'
    elif len(d)==len(ok)==6 and {r['unit_id'] for r in d}==expected=={r['unit_id'] for r in ok}: status='ATOMGIT_REPEAT_DEV_SIX_REPAIRS_FROZEN_REPEAT_AUTHORITY_CLOSED'
    else: status='ATOMGIT_REPEAT_DEV_REPAIR_GENERATION_INCOMPLETE_HOLD'
    repairs={fid:rec for fid in c.selected_ids(proj) if (rec:=record_for(fid)) is not None}
    m={'schema_version':'ace-repeat-dev-repairs-manifest-v1','object_id':OBJECT_ID,'status':status,'execution_id':c.EXECUTION_ID,'projection_content_sha256':proj['content_sha256'],'selected_family_ids':proj['selected_family_ids'],'repair_count':len(repairs),'repairs':repairs,'ledger_sha256':sha256_file(c.LEDGER) if c.LEDGER.is_file() else None,'repair_writer_model_round_count':sum(int(r.get('model_round_count',0)) for r in ok),'human_edits':0,'raw_source_trajectory_visible_to_writer':False,'scientific_externality_outcomes_observed':0,'authority':{'repair_generation_closed':True,'development_repeat_qualification':False,'rq1_rq2':False,'paper_claim':False}}
    m['content_sha256']=sha256_value(m); c.writej(c.MANIFEST,m)
    out={'schema_version':'ace-repeat-dev-repair-result-v1','object_id':OBJECT_ID,'status':status,'execution_id':c.EXECUTION_ID,'manifest_content_sha256':m['content_sha256'],'manifest_file_sha256':sha256_file(c.MANIFEST),'repair_count':len(repairs),'dispatch_count':len(d),'completion_count':len(ok),'failure_count':len(bad),'ledger_sha256':m['ledger_sha256'],'scientific_externality_outcomes_observed':0,'next_legal_action':'If and only if six repairs are frozen, build zero-provider R*=2 repeat-panel readiness and obtain a separate execution authority.','authority':m['authority']}
    out['content_sha256']=sha256_value(out); c.writej(c.RESULT,out); return out

def execute()->dict[str,Any]:
    proj=c.projection(); auth=c.verified(c.AUTH,'USER_AUTHORIZED_ATOMGIT_REPEAT_DEV_REPAIR_GENERATION_ONLY'); contract=c.verified(c.CONTRACT,'ATOMGIT_REPEAT_DEV_REPAIR_GENERATION_EXECUTION_AUTHORIZED')
    if contract['human_authorization_content_sha256']!=auth['content_sha256'] or contract['projection_content_sha256']!=proj['content_sha256']: raise c.RepairStop('execution binding drift')
    if contract['runner_sha256']!=sha256_file(Path(__file__)) or contract['common_sha256']!=sha256_file(Path(c.__file__)): raise c.RepairStop('runner/common SHA drift')
    if contract['g1_quota_release_file_sha256']!=sha256_file(c.G1_RELEASE): raise c.RepairStop('G1 release binding drift')
    if not auth['authority']['repair_generation'] or auth['authority']['development_repeat_qualification']: raise c.RepairStop('authority scope drift')
    c.patch_live(); c.RUN_ROOT.mkdir(parents=True,exist_ok=True); ids=c.selected_ids(proj)
    for i,fid in enumerate(ids):
        state=c.ledger_states().get(c.unit_id(fid))
        if state=='COMPLETION': continue
        if state is not None: return finalize(proj)
        run_family(proj,fid,len(ids)-i)
    return finalize(proj)

def main()->None:
    p=argparse.ArgumentParser();p.add_argument('--preflight',action='store_true');p.add_argument('--usage-only',action='store_true');p.add_argument('--execute',action='store_true');a=p.parse_args()
    if sum((a.preflight,a.usage_only,a.execute))!=1: raise SystemExit('choose one')
    if a.preflight: x=c.preflight(Path(__file__))
    elif a.usage_only: x={'status':'ZERO_REQUEST_USAGE_PROBE','usage':c.usage(),'model_requests':0}
    else: x=execute()
    print(json.dumps(x,ensure_ascii=False,sort_keys=True))
if __name__=='__main__': main()
