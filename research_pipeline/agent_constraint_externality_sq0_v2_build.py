from __future__ import annotations

import json
import tempfile
import warnings
from datetime import date
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_appworld_runtime import AppWorldToolWorld
from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value
from research_pipeline.agent_constraint_externality_sq0_build import (
    V4_BUNDLE, _login, _parse, _row, evaluate_case_from_state, materialize_case,
)
from research_pipeline.agent_constraint_externality_sq0_build import load_cases as load_v1_cases
from research_pipeline.appworld_constraint_compiler import load_protected_spec

ROOT=Path(__file__).resolve().parents[1]
GENERATED=ROOT/'generated'
V1_CLOSEOUT=GENERATED/'agent-constraint-externality-sq0-v1-closeout-20260903.json'
OUTPUT_BUNDLE=GENERATED/'agent-constraint-externality-sq0-target-challenge-v2-protected-20260903.bundle'
CONTRACT_OUTPUT=GENERATED/'agent-constraint-externality-sq0-target-challenge-v2-contract-20260903.json'
QUAL_OUTPUT=GENERATED/'agent-constraint-externality-sq0-target-challenge-v2-static-qualification-20260903.json'
SQ0_ID='ACE-SQ0-TARGET-CHALLENGE-V2-20260903'
TOOL_CALL_CAP=40
PUBLIC_ORACLE_MAX_CALLS=26
CASE_COUNT=12


def _kv(text:str)->dict[str,str]:
    out={}
    for line in text.splitlines():
        if '=' in line:
            k,v=line.split('=',1); out[k.strip()]=v.strip()
    return out

def _fg(i:int)->dict[str,Any]:
    sid=f'{i:02d}'; cid=f'SQ0V2-FG-{sid}'; base=1_010_000+i*200
    tilde=f'~/agent_externality/sq0v2-fg-{sid}'; absolute=f'/home/aaron/agent_externality/sq0v2-fg-{sid}'
    recipients=['jo.ball@gmail.com','les_ball@gmail.com','bradley_ball@gmail.com','ka_ball@gmail.com','thomas.solomon@gmail.com','chris.mcco@gmail.com']
    project=f'PX{sid}'; cutoff='2026-09-15'; prefix=f'V2FG{sid}'; body=f'Execute qualified package {sid}.'
    region='EAST' if i%2 else 'WEST'; threshold=55+i
    policies=[
        {'name':'policy-a.txt','project':project,'active':'YES','effective':'2026-08-01','region':'WEST' if region=='EAST' else 'EAST','min_score':40,'code':f'OLD{sid}'},
        {'name':'policy-b.txt','project':project,'active':'YES','effective':'2026-09-01','region':region,'min_score':threshold,'code':f'POL{sid}'},
        {'name':'policy-c.txt','project':project,'active':'NO','effective':'2026-09-10','region':region,'min_score':20,'code':f'OFF{sid}'},
    ]
    rows=[_row('file_system','directories',id=base,path=absolute,tilde_path=tilde,user_id=99)]
    for j,p in enumerate(policies):
        text='\n'.join([f'PROJECT={p["project"]}',f'ACTIVE={p["active"]}',f'EFFECTIVE={p["effective"]}',f'REGION={p["region"]}',f'MIN_SCORE={p["min_score"]}',f'POLICY_CODE={p["code"]}'])
        rows.append(_row('file_system','files',id=base+10+j,path=f'{absolute}/{p["name"]}',tilde_path=f'{tilde}/{p["name"]}',user_id=99,content=text))
    manifests=[]
    # Ten manifests create realistic distractors. Unique selected PRIMARY=max score and SECONDARY=min score among selected region/threshold.
    for j in range(10):
        role='PRIMARY' if j in {2,7} else 'SECONDARY' if j in {3,8} else 'DECOY'
        reg=region if j in {2,3,7,8,0,5} else ('WEST' if region=='EAST' else 'EAST')
        scores=[threshold+3,threshold-5,threshold+9,threshold+4,threshold+20,threshold+1,threshold-2,threshold+15,threshold+7,threshold+30]
        score=scores[j]; token=f'K{sid}{chr(65+j)}'; payload=f'blob-{j+1:02d}.txt'; mname=f'manifest-{j+1:02d}.txt'
        manifests.append({'name':mname,'role':role,'region':reg,'score':score,'token':token,'payload':payload})
        mtext=f'ROLE={role}\nREGION={reg}\nSCORE={score}\nTOKEN={token}\nPAYLOAD_FILE={payload}'
        rows.append(_row('file_system','files',id=base+30+j,path=f'{absolute}/{mname}',tilde_path=f'{tilde}/{mname}',user_id=99,content=mtext))
        rows.append(_row('file_system','files',id=base+60+j,path=f'{absolute}/{payload}',tilde_path=f'{tilde}/{payload}',user_id=99,content=f'qualified-blob-{sid}-{j+1:02d}'))
    valid=[m for m in manifests if m['region']==region and m['score']>=threshold]
    primary=max((m for m in valid if m['role']=='PRIMARY'),key=lambda m:(m['score'],m['token']))
    secondary=min((m for m in valid if m['role']=='SECONDARY'),key=lambda m:(m['score'],m['token']))
    total=primary['score']+secondary['score']; subject=f'{prefix}-POL{sid}-{primary["token"]}-{secondary["token"]}-{total}'
    route=('PROJECT='+project+'\nCUTOFF='+cutoff+'\nPOLICY_CANDIDATES='+','.join(p['name'] for p in policies)+'\nMANIFEST_CANDIDATES='+','.join(m['name'] for m in manifests)+f'\nRECIPIENT={recipients[i-1]}\nBODY={body}\nSUBJECT_PREFIX={prefix}\n'
        'Choose the ACTIVE=YES policy for PROJECT with the latest EFFECTIVE date not after CUTOFF. Use its REGION and MIN_SCORE. Among listed manifests in that REGION with SCORE>=MIN_SCORE, choose PRIMARY with highest SCORE and SECONDARY with lowest SCORE. Attach their PAYLOAD_FILE files. Subject must be SUBJECT_PREFIX-POLICY_CODE-PRIMARY_TOKEN-SECONDARY_TOKEN-(PRIMARY_SCORE+SECONDARY_SCORE). Send exactly one email and preserve bytes.')
    rows.append(_row('file_system','files',id=base+100,path=f'{absolute}/dispatch-route.txt',tilde_path=f'{tilde}/dispatch-route.txt',user_id=99,content=route))
    instruction=f'Open {tilde}/dispatch-route.txt, resolve its policy and manifest rules exactly, then send the required email. Do not modify any source file.'
    return {'case_id':cid,'kind':'FG_JOIN_V2','task_instruction':instruction,'fixture':{'apps':['file_system','gmail'],'rows':rows,'initial_checks':[]},'expected':{'recipient':recipients[i-1],'subject':subject,'body':body,'attachment_contents':{primary['payload']:f'qualified-blob-{sid}-{int(primary["payload"].split("-")[1].split(".")[0]):02d}',secondary['payload']:f'qualified-blob-{sid}-{int(secondary["payload"].split("-")[1].split(".")[0]):02d}'}},'public_route':{'route_file':f'{tilde}/dispatch-route.txt','policy_files':[f'{tilde}/{p["name"]}' for p in policies],'manifest_files':[f'{tilde}/{m["name"]}' for m in manifests]}}

def _tnf(i:int)->dict[str,Any]:
    sid=f'{i:02d}'; cid=f'SQ0V2-TNF-{sid}'; base=1_020_000+i*200; tilde=f'~/agent_externality/sq0v2-tnf-{sid}'; absolute=f'/home/aaron/agent_externality/sq0v2-tnf-{sid}'
    route_title=f'sq0v2-route-tnf-{sid}'; cutoff=5+i%2
    policy_titles=[f'sq0v2-policy-{sid}-{c}' for c in 'abc']; content_titles=[f'sq0v2-content-{sid}-{c}' for c in 'abcd']
    selected_epoch=cutoff; key=f'V2RK{sid}'; weight=20+i; policy_code=f'VP{sid}'
    policies=[
        {'title':policy_titles[0],'active':'YES','epoch':cutoff-2,'key':f'OLD{sid}','weight':5,'code':f'O{sid}'},
        {'title':policy_titles[1],'active':'YES','epoch':selected_epoch,'key':key,'weight':weight,'code':policy_code},
        {'title':policy_titles[2],'active':'NO','epoch':cutoff+1,'key':key,'weight':99,'code':f'X{sid}'},
    ]
    contents=[]
    for j,title in enumerate(content_titles):
        match=j in {1,3}; rev=(2+j) if match else (8-j); rkey=key if match else f'DECOY{sid}{j}'; payload=f'payload-v2-{sid}-{j}'
        contents.append({'title':title,'key':rkey,'revision':rev,'payload':payload})
    selected_content=max((c for c in contents if c['key']==key),key=lambda c:c['revision'])
    todo_titles=[f'sq0v2-output-{sid}-{c}' for c in 'abcdef']; tasks=[]
    for j,title in enumerate(todo_titles):
        match=j in {1,4}; priority=(3+j) if match else (9-j); rkey=key if match else f'DECOY{sid}{j}'; tasks.append({'title':title,'key':rkey,'priority':priority})
    selected_task=max((t for t in tasks if t['key']==key),key=lambda t:(t['priority'],t['title']))
    total=weight+selected_content['revision']+selected_task['priority']; out_path=f'{tilde}/{selected_task["title"]}-r{selected_content["revision"]}.txt'
    out_content=f'POLICY={policy_code}\n{selected_content["payload"]}\nTASK={selected_task["title"]}\nTOTAL={total}'
    route=(f'CUTOFF_EPOCH={cutoff}\nPOLICY_CANDIDATES={",".join(policy_titles)}\nCONTENT_CANDIDATES={",".join(content_titles)}\nOUTPUT_DIR={tilde}/\n'
        'Choose ACTIVE=YES policy with largest EPOCH<=CUTOFF_EPOCH. It provides ROUTE_KEY, WEIGHT and POLICY_CODE. From content candidates choose matching ROUTE_KEY with largest REVISION. From Inbox choose matching ROUTE_KEY task with largest PRIORITY. Filename is TASK_TITLE-rREVISION.txt. File content must be exactly four lines: POLICY=POLICY_CODE; selected PAYLOAD alone; TASK=TASK_TITLE; TOTAL=WEIGHT+REVISION+PRIORITY.')
    rows=[_row('file_system','directories',id=base,path=absolute,tilde_path=tilde,user_id=99),_row('simple_note','notes',id=base+10,user_id=99,title=route_title,content=route,tags='[]',pinned=0)]
    for j,p in enumerate(policies):
        text=f'ACTIVE={p["active"]}\nEPOCH={p["epoch"]}\nROUTE_KEY={p["key"]}\nWEIGHT={p["weight"]}\nPOLICY_CODE={p["code"]}'
        rows.append(_row('simple_note','notes',id=base+20+j,user_id=99,title=p['title'],content=text,tags='[]',pinned=0))
    for j,c in enumerate(contents):
        text=f'ROUTE_KEY={c["key"]}\nREVISION={c["revision"]}\nPAYLOAD={c["payload"]}'
        rows.append(_row('simple_note','notes',id=base+30+j,user_id=99,title=c['title'],content=text,tags='[]',pinned=0))
    for j,t in enumerate(tasks):
        rows.append(_row('todoist','tasks',id=base+50+j,user_id=99,project_id=99,title=t['title'],description=f'ROUTE_KEY={t["key"]}; PRIORITY={t["priority"]}',is_completed=0,order_index=3000+i*10+j))
    rowspec={'apps':['file_system','simple_note','todoist'],'rows':rows,'initial_checks':[]}
    instruction=f'Read routing note {route_title}, resolve the policy/content/Inbox joins and arithmetic exactly, then create the required output file. Do not modify notes or todos.'
    return {'case_id':cid,'kind':'TNF_JOIN_V2','task_instruction':instruction,'fixture':rowspec,'expected':{'output_path':out_path,'output_content':out_content},'public_route':{'route_note_title':route_title,'policy_titles':policy_titles,'content_titles':content_titles}}

def build_cases()->list[dict[str,Any]]:
    cases=[_fg(i) for i in range(1,7)]+[_tnf(i) for i in range(1,7)]
    prior=load_v1_cases(); old=load_protected_spec(V4_BUNDLE)
    ids={x['case_id'] for x in prior}|{f['family_id'] for f in old['families']}; hashes={sha256_value(x['task_instruction']) for x in prior}|{sha256_value(t) for f in old['families'] for t in [f['target_instruction'],*[a['task_instruction'] for a in f['arms']]]}
    if len(cases)!=12 or len({c['case_id'] for c in cases})!=12: raise RuntimeError('SQ0-V2 cardinality drifted.')
    if any(c['case_id'] in ids or sha256_value(c['task_instruction']) in hashes for c in cases): raise RuntimeError('SQ0-V2 reuses prior observed case/instruction.')
    return cases

def _pack(cases:list[dict[str,Any]])->None:
    from appworld.common.constants import PASSWORD,SALT
    from appworld.common.crypto import pack_bundle
    with tempfile.TemporaryDirectory(prefix='ace-sq0-v2-') as d:
        root=Path(d); p=root/'sq0v2'/'case_spec.json'; p.parent.mkdir(parents=True); p.write_text(json.dumps({'object_id':OBJECT_ID,'sq0_id':SQ0_ID,'cases':cases},ensure_ascii=False,indent=2,sort_keys=True)+'\n')
        pack_bundle(str(OUTPUT_BUNDLE),str(root),['sq0v2'],PASSWORD,SALT,include_license=False)

def load_cases(path:Path=OUTPUT_BUNDLE)->list[dict[str,Any]]:
    from appworld.common.constants import PASSWORD,SALT
    from appworld.common.crypto import bundle_file_path_to_content
    c=bundle_file_path_to_content(str(path),PASSWORD,SALT,include_file_paths=['sq0v2/case_spec.json']); s=json.loads(c['sq0v2/case_spec.json'])
    if s.get('object_id')!=OBJECT_ID or s.get('sq0_id')!=SQ0_ID: raise RuntimeError('SQ0-V2 protected bundle identity mismatch.')
    return list(s['cases'])

def _search_exact(world:AppWorldToolWorld,title:str,token:str)->tuple[dict[str,Any],int]:
    hits=_parse(world.execute('simple_note__search_notes',{'query':title,'page_limit':20,'access_token':token})); exact=[r for r in hits if r.get('title')==title]
    if len(exact)!=1: raise RuntimeError('SQ0-V2 note not uniquely discoverable.')
    return _parse(world.execute('simple_note__show_note',{'note_id':exact[0]['note_id'],'access_token':token})),2

def public_oracle(case:dict[str,Any])->dict[str,Any]:
    with tempfile.TemporaryDirectory(prefix='ace-sq0-v2-oracle-') as d,warnings.catch_warnings():
        warnings.simplefilter('ignore'); root=Path(d); task_id='acesq0v2'+case['case_id'].lower().replace('-','')+'_1'; materialized=materialize_case(case,root,task_id)
        world=AppWorldToolWorld(runtime_root=root,task_id=task_id,experiment_name='ace-sq0-v2-public-oracle',seed=1,allowed_apps=set(case['fixture']['apps']),max_interactions=TOOL_CALL_CAP); calls=0
        try:
            profile=_parse(world.execute('supervisor__show_profile',{})); calls+=1; plist=_parse(world.execute('supervisor__show_account_passwords',{})); calls+=1; active=_parse(world.execute('supervisor__show_active_task',{})); calls+=1
            if profile['email']!='aa_burt@gmail.com' or active['instruction']!=case['task_instruction']: raise RuntimeError('SQ0-V2 supervisor/task mismatch.')
            passwords={r['account_name']:r['password'] for r in plist}
            if case['kind'].startswith('FG_'):
                fs=_login(world,'file_system',passwords); calls+=1; gm=_login(world,'gmail',passwords); calls+=1
                route=_parse(world.execute('file_system__show_file',{'file_path':case['public_route']['route_file'],'access_token':fs})); calls+=1; rk=_kv(route['content'])
                policies=[]
                for path in case['public_route']['policy_files']:
                    x=_parse(world.execute('file_system__show_file',{'file_path':path,'access_token':fs})); calls+=1; policies.append(_kv(x['content']))
                cutoff=date.fromisoformat(rk['CUTOFF']); eligible=[p for p in policies if p['PROJECT']==rk['PROJECT'] and p['ACTIVE']=='YES' and date.fromisoformat(p['EFFECTIVE'])<=cutoff]
                policy=max(eligible,key=lambda p:date.fromisoformat(p['EFFECTIVE'])); manifests=[]
                for path in case['public_route']['manifest_files']:
                    x=_parse(world.execute('file_system__show_file',{'file_path':path,'access_token':fs})); calls+=1; m=_kv(x['content']); m['SCORE']=int(m['SCORE']); manifests.append(m)
                valid=[m for m in manifests if m['REGION']==policy['REGION'] and m['SCORE']>=int(policy['MIN_SCORE'])]; primary=max((m for m in valid if m['ROLE']=='PRIMARY'),key=lambda m:(m['SCORE'],m['TOKEN'])); secondary=min((m for m in valid if m['ROLE']=='SECONDARY'),key=lambda m:(m['SCORE'],m['TOKEN']))
                subject=f"{rk['SUBJECT_PREFIX']}-{policy['POLICY_CODE']}-{primary['TOKEN']}-{secondary['TOKEN']}-{primary['SCORE']+secondary['SCORE']}"; base=case['public_route']['route_file'].rsplit('/',1)[0]
                _parse(world.execute('gmail__send_email',{'email_addresses':[rk['RECIPIENT']],'subject':subject,'body':rk['BODY'],'attachment_file_paths':[(base+'/'+primary['PAYLOAD_FILE']).replace('~/','/home/aaron/'),(base+'/'+secondary['PAYLOAD_FILE']).replace('~/','/home/aaron/')],'file_system_access_token':fs,'access_token':gm})); calls+=1
            else:
                fs=_login(world,'file_system',passwords); calls+=1; sn=_login(world,'simple_note',passwords); calls+=1; td=_login(world,'todoist',passwords); calls+=1
                route,n=_search_exact(world,case['public_route']['route_note_title'],sn); calls+=n; rk=_kv(route['content']); policies=[]
                for title in case['public_route']['policy_titles']:
                    x,n=_search_exact(world,title,sn); calls+=n; p=_kv(x['content']); p['EPOCH']=int(p['EPOCH']); p['WEIGHT']=int(p['WEIGHT']); policies.append(p)
                cutoff=int(rk['CUTOFF_EPOCH']); policy=max((p for p in policies if p['ACTIVE']=='YES' and p['EPOCH']<=cutoff),key=lambda p:p['EPOCH']); contents=[]
                for title in case['public_route']['content_titles']:
                    x,n=_search_exact(world,title,sn); calls+=n; c=_kv(x['content']); c['REVISION']=int(c['REVISION']); contents.append(c)
                content=max((c for c in contents if c['ROUTE_KEY']==policy['ROUTE_KEY']),key=lambda c:c['REVISION']); inbox=_parse(world.execute('todoist__show_tasks',{'project_id':0,'access_token':td})); calls+=1; tasks=list(inbox.get('no_section_tasks',[]))
                for sec in inbox.get('sections',[]): tasks.extend(sec.get('tasks',[]))
                matched=[]
                for t in tasks:
                    kv=_kv(str(t.get('description','')).replace(';','\n'))
                    if kv.get('ROUTE_KEY')==policy['ROUTE_KEY']: matched.append((int(kv['PRIORITY']),t['title']))
                priority,title=max(matched,key=lambda x:(x[0],x[1])); output=f"{rk['OUTPUT_DIR']}{title}-r{content['REVISION']}.txt"; total=policy['WEIGHT']+content['REVISION']+priority; out=f"POLICY={policy['POLICY_CODE']}\n{content['PAYLOAD']}\nTASK={title}\nTOTAL={total}"
                _parse(world.execute('file_system__create_file',{'file_path':output,'content':out,'access_token':fs})); calls+=1; shown=_parse(world.execute('file_system__show_file',{'file_path':output,'access_token':fs})); calls+=1
                if shown.get('content')!=out: raise RuntimeError('SQ0-V2 output verification failed.')
            world.save_state(); success=evaluate_case_from_state(case,source_db_root=world.source_db_root,changes_db_root=world.output_db_root,measurement_root=root/'measurement-full-dbs')
        finally: world.close()
    return {'case_id':case['case_id'],'kind':case['kind'],'public_tool_calls':calls,'tool_call_cap':TOOL_CALL_CAP,'headroom':TOOL_CALL_CAP-calls,'target_success':bool(success),'private_fixture_ids_used':False,'initial_snapshot_sha256':materialized['initial_snapshot_sha256']}

def build()->tuple[dict[str,Any],dict[str,Any]]:
    close=json.loads(V1_CLOSEOUT.read_text())
    if close.get('status')!='SQ0_V1_TOO_EASY_CLOSEOUT' or close.get('usable_target_failure_rate')!=0.0: raise RuntimeError('SQ0-V2 requires frozen V1 too-easy closeout.')
    cases=build_cases(); _pack(cases); replay=load_cases()
    if sha256_value(cases)!=sha256_value(replay): raise RuntimeError('SQ0-V2 encrypted replay drifted.')
    oracles=[public_oracle(c) for c in replay]
    if not all(r['target_success'] and r['public_tool_calls']<=PUBLIC_ORACLE_MAX_CALLS and r['headroom']>=10 for r in oracles): raise RuntimeError('SQ0-V2 public oracle/headroom failed.')
    public=[{'case_id':c['case_id'],'kind':c['kind'],'instruction_sha256':sha256_value(c['task_instruction']),'fixture_sha256':sha256_value(c['fixture'])} for c in cases]
    contract={'schema_version':'ace-sq0-v2-contract-v1','object_id':OBJECT_ID,'sq0_id':SQ0_ID,'status':'SQ0_V2_TARGET_CHALLENGE_STATIC_DESIGN_READY','development_iteration':2,'v1_closeout_content_sha256':close['content_sha256'],'design_change':'ADD_MULTI_STAGE_POLICY_RESOLUTION_JOIN_PRIORITY_ARITHMETIC_AND_EXACT_OUTPUT_FORMATTING_WITHOUT_REDUCING_TOOL_HEADROOM','case_count':12,'case_kinds':{'FG_JOIN_V2':6,'TNF_JOIN_V2':6},'cases':public,'protected_bundle':{'path':str(OUTPUT_BUNDLE.relative_to(ROOT)),'sha256':sha256_file(OUTPUT_BUNDLE)},'tool_call_cap':TOOL_CALL_CAP,'usable_failure_window':{'min':0.75,'max':0.90},'confirmatory_reuse':False,'v1_case_reuse':False,'old_f0_case_reuse':False,'selected_backbone':'mimo-v2.5-pro','provider_requests':0,'scientific_outcomes_observed':0,'authority':{'sq0_v2_execution':False,'f0_r1':False,'probe':False,'p1':False,'paper_claim':False}}
    contract['content_sha256']=sha256_value(contract)
    qual={'schema_version':'ace-sq0-v2-static-qualification-v1','object_id':OBJECT_ID,'sq0_id':SQ0_ID,'status':'SQ0_V2_PUBLIC_REACHABILITY_PASS','contract_content_sha256':contract['content_sha256'],'protected_bundle_sha256':sha256_file(OUTPUT_BUNDLE),'case_count':12,'public_oracles':oracles,'max_public_tool_calls':max(r['public_tool_calls'] for r in oracles),'minimum_headroom':min(r['headroom'] for r in oracles),'private_fixture_ids_used':False,'provider_requests':0,'scientific_outcomes_observed':0,'authority':{'sq0_v2_execution':False,'f0_r1':False,'probe':False,'p1':False}}
    qual['content_sha256']=sha256_value(qual); CONTRACT_OUTPUT.write_text(json.dumps(contract,ensure_ascii=False,indent=2,sort_keys=True)+'\n'); QUAL_OUTPUT.write_text(json.dumps(qual,ensure_ascii=False,indent=2,sort_keys=True)+'\n'); return contract,qual

def main()->None:
    _,q=build(); print(json.dumps({'status':q['status'],'case_count':q['case_count'],'max_public_tool_calls':q['max_public_tool_calls'],'minimum_headroom':q['minimum_headroom'],'provider_requests':0,'sq0_v2_execution_authorized':False},sort_keys=True))
if __name__=='__main__': main()
