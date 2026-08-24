from __future__ import annotations
import csv,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from research_pipeline import temporal_skill_g0_execute as core
from research_pipeline.ark_provider import ArkResponsesClient,ArkSettings
from research_pipeline.experiment_authority import acquire_authority,release_authority
from research_pipeline.temporal_skill_extension_multiturn import MODEL,RES,URL,planning_prompt,history,post,text,safe_receipt,sh,csha
PID=core.PAPER_ID;DATA=core.DATA_ROOT;SRC=DATA/'paper-acceptance'/'source-native-replay'/PID/'20260824-extension-bls-cpi-crossdomain';BASE=DATA/'paper-acceptance'/'source-native-replay'/PID/'20260824-extension-bls-cpi-planning-base';PLAN=BASE/'plan.json';RESULTS=BASE/'results.csv';OWNER=PID+':EXT:BLS-PLANNING'
def atomic(p,o):p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n');os.replace(t,p)
def prep():
 eps=json.load(open(SRC/'endpoints.json'))['endpoints'];plan={'schema_version':'1.0','paper_id':PID,'experiment':'E2_EXTENSION_BLS_PLANNING_BASE','endpoint_ids':[e['endpoint_id'] for e in eps],'model_identity':{'requested_model':MODEL,'required_resolved_model':RES,'required_plan_base_url':URL},'planned_model_calls':8,'selection_rule':'BLS cross-domain planning-only falsifier on all four prospectively frozen CPI endpoints; no helper and no endpoint selection.'};plan['plan_body_sha256']=csha({k:v for k,v in plan.items() if k!='plan_body_sha256'});atomic(PLAN,plan);return plan
def run():
 plan=json.load(open(PLAN));eps={e['endpoint_id']:e for e in json.load(open(SRC/'endpoints.json'))['endpoints']};a=core.load_assets()
 for e in eps.values():a['endpoints'][e['endpoint_id']]=e;a['source'][e['endpoint_id']]='R4'
 completed=set()
 if RESULTS.exists():completed={r['endpoint_id'] for r in csv.DictReader(open(RESULTS))}
 raw=ArkSettings.from_env(required=True)
 if raw.base_url.rstrip('/')!=URL:raise RuntimeError('non-Plan route')
 client=ArkResponsesClient(ArkSettings(api_key=raw.api_key,base_url=raw.base_url,default_model=raw.default_model,timeout_seconds=180,max_retries=0));auth=acquire_authority(DATA,OWNER,plan['plan_body_sha256'],'temporal-extension-planning-repeat','replicate',plan['experiment']);outcome='runner-exception';calls=0
 try:
  for eid in plan['endpoint_ids']:
   if eid in completed:continue
   e=eps[eid];d=BASE/'raw'/eid.replace(':','_');d.mkdir(parents=True,exist_ok=True);pp=planning_prompt(e);p1=post(client,{'model':MODEL,'input':pp,'max_output_tokens':384,'temperature':0,'thinking':{'type':'disabled'}});calls+=1;safe_receipt(d/'planning.json',p1,{'prompt_sha256':sh(pp.encode())})
   inst='TURN 2: now return the final answer as one JSON object matching this schema, with no markdown or extra prose: '+json.dumps(e['output_schema'],ensure_ascii=False,sort_keys=True)+'. Respect the cutoff and use only supplied evidence. No helper output is available.';p2=post(client,{'model':MODEL,'input':history(pp,p1,inst),'max_output_tokens':768,'temperature':0,'thinking':{'type':'disabled'}});calls+=1;safe_receipt(d/'final.json',p2,{'instruction_sha256':sh(inst.encode())});ft=text(p2);valid=bool(ft);success=False
   if valid:
    try:pred,sc=core.parse_and_score(a,e,ft);success=bool(sc['success'])
    except Exception:valid=False
   exists=RESULTS.exists();fields=['endpoint_id','runtime_valid','family_success','resolved_model','planning_sha256','final_text_sha256','raw_receipt_path']
   with RESULTS.open('a',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader() if not exists else None;w.writerow({'endpoint_id':eid,'runtime_valid':valid,'family_success':success,'resolved_model':p2.get('model'),'planning_sha256':sh(text(p1).encode()),'final_text_sha256':sh(ft.encode()),'raw_receipt_path':str(d/'final.json')});f.flush();os.fsync(f.fileno())
   atomic(BASE/'checkpoint.json',{'completed_endpoints':len(completed)+1,'total_endpoints':4,'provider_calls_this_resume':calls,'last_endpoint':eid});completed.add(eid)
   if not valid:outcome='runtime-invalid';return {'status':'stopped','endpoint':eid}
  outcome='completed';return {'status':'completed','endpoints':len(completed),'provider_calls_this_resume':calls}
 finally:release_authority(DATA,OWNER,str(auth['authority_id']),outcome)
def summary():
 r=list(csv.DictReader(open(RESULTS)));return {'successes':sum(x['family_success']=='True' for x in r),'total':len(r),'rows':[{x:y for x,y in z.items() if x in ['endpoint_id','family_success','resolved_model']} for z in r]}
if __name__=='__main__':
 import argparse;ap=argparse.ArgumentParser();ap.add_argument('cmd',choices=['prepare','run','summary']);x=ap.parse_args();print(json.dumps(prep() if x.cmd=='prepare' else run() if x.cmd=='run' else summary(),indent=2))
