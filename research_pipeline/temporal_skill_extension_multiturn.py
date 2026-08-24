from __future__ import annotations
import argparse,csv,hashlib,json,os,random,sys,time
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from research_pipeline import temporal_skill_g0_execute as core
from research_pipeline.ark_provider import ArkResponsesClient,ArkSettings
from research_pipeline.experiment_authority import acquire_authority,release_authority
PID=core.PAPER_ID;DATA=core.DATA_ROOT
SRC=DATA/'paper-acceptance'/'source-native-replay'/PID/'20260824-extension-eia-future-nonceiling'
BASE=DATA/'paper-acceptance'/'source-native-replay'/PID/'20260824-extension-multiturn-tool-vs-context';PLAN=BASE/'plan.json';AUTH=BASE/'authorization.json';RESULTS=BASE/'results.csv';CHECK=BASE/'checkpoint.json'
MODEL='deepseek-v4-pro';RES='deepseek-v4-pro-260425';URL='https://ark.cn-beijing.volces.com/api/plan/v3';OWNER=PID+':EXT:MULTITURN'
TOOL={'type':'function','name':'temporal_filter','description':'Filter the supplied release evidence to the stated cutoff. Call this if temporal admissibility would help the final answer.','parameters':{'type':'object','properties':{},'additionalProperties':False}}
def sh(b:bytes):return hashlib.sha256(b).hexdigest()
def csha(x):return sh(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
def read(p):return json.loads(p.read_text())
def atomic(p,obj):p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');os.replace(tmp,p)
def append_row(row):
 RESULTS.parent.mkdir(parents=True,exist_ok=True);exists=RESULTS.exists();fields=['endpoint_id','arm','condition_position','planning_sha256','helper_output_sha256','tool_called','tool_call_count','model_calls','runtime_valid','family_success','resolved_model','final_text_sha256','raw_receipt_path']
 with RESULTS.open('a',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=fields);
  if not exists:w.writeheader()
  w.writerow({k:row.get(k,'') for k in fields});f.flush();os.fsync(f.fileno())
def done():
 if not RESULTS.exists():return set()
 return {r['endpoint_id']+'|'+r['arm'] for r in csv.DictReader(RESULTS.open())}
def prep():
 BASE.mkdir(parents=True,exist_ok=True);eps=read(SRC/'endpoints_clean.json')['endpoints'];targets=[e['endpoint_id'] for e in eps];order={}
 for e in targets:
  arms=['BASE','CONTEXT','TOOL'];random.Random(int(sh(('E2-MT|'+e).encode())[:16],16)).shuffle(arms);order[e]=arms
 plan={'schema_version':'1.0','paper_id':PID,'experiment':'E2_EXTENSION_MULTITURN_TOOL_VS_CONTEXT','endpoint_ids':targets,'arms':['BASE','CONTEXT','TOOL'],'branch_order':order,'shared_planning_calls':4,'max_model_calls':20,'model_identity':{'requested_model':MODEL,'required_resolved_model':RES,'required_plan_base_url':URL},'estimand':'Exploratory multi-turn availability/use contrast after a shared pre-treatment planning state. BASE receives no helper; CONTEXT receives exact T1 output as ordinary context; TOOL exposes a real temporal_filter function and the model endogenously decides whether to call it. TOOL-vs-CONTEXT is not claimed as a pure placement estimand because endogenous invocation is part of treatment.','selection_rule':'All four clean EIA future endpoints frozen before multi-turn outcomes; no endpoint selection from prior single-turn outcomes.'};plan['plan_body_sha256']=csha({k:v for k,v in plan.items() if k!='plan_body_sha256'})
 auth={'schema_version':'1.0','status':'HUMAN_EXECUTION_AUTHORITY_RECORDED','authorized_by':'explicit user directive in current conversation','execution_authorized':True,'provider_spend_authorized':True,'bound_plan_body_sha256':plan['plan_body_sha256'],'bounded_budget':{'max_model_calls':20,'reruns_allowed':False,'resume_missing_only':True},'outcome_driven_endpoint_selection_authorized':False,'r15_contract_mutation_authorized':False};auth['authorization_sha256']=csha({k:v for k,v in auth.items() if k!='authorization_sha256'});atomic(PLAN,plan);atomic(AUTH,auth);return {'endpoints':4,'max_calls':20,'plan_sha':plan['plan_body_sha256'],'orders':order}
def post(client:ArkResponsesClient,body:dict[str,Any]):
 r=client.session.post(client.endpoint,json=body,timeout=client.settings.timeout_seconds);payload=r.json()
 if r.status_code>=400:raise RuntimeError(f"Ark HTTP {r.status_code}: {payload}")
 if payload.get('model')!=RES:raise RuntimeError('resolved-model-drift:'+str(payload.get('model')))
 return payload
def text(payload):return ArkResponsesClient.output_text(payload)
def safe_receipt(path,payload,extra=None):
 obj={'status':payload.get('status'),'resolved_model':payload.get('model'),'response_id_sha256':sh(str(payload.get('id') or '').encode()),'output':payload.get('output'),'usage':payload.get('usage') or {}}
 if extra:obj.update(extra)
 atomic(path,obj)
def planning_prompt(e):return 'You are analyzing a time-sensitive evidence task. Work only from the supplied package. This is TURN 1: do not provide the final requested answer yet. Return one JSON object with keys need_temporal_assistance (boolean), provisional_latest_evidence_ref (string or null), and reason_short (string).\nINPUT_JSON:\n'+json.dumps({'task':e['task'],'cutoff_date':e['cutoff_date'],'evidence_package':e['package']},ensure_ascii=False,sort_keys=True,separators=(',',':'))
def final_instruction(e,arm,helper):
 base='TURN 2: now return the final answer as one JSON object matching this schema, with no markdown or extra prose: '+json.dumps(e['output_schema'],ensure_ascii=False,sort_keys=True)+'. Respect the cutoff and use only supplied evidence.'
 if arm=='BASE':return base+' No helper output is available.'
 if arm=='CONTEXT':return base+' The following precomputed context note is available; verify it against the evidence: '+json.dumps(helper,ensure_ascii=False,sort_keys=True,separators=(',',':'))
 return base+' A temporal_filter function is available. Decide yourself whether to call it before answering.'
def history(plan_prompt,p1,next_text):return [{'role':'user','content':plan_prompt}]+list(p1.get('output') or [])+[{'role':'user','content':next_text}]
def execute():
 plan=read(PLAN);eps={e['endpoint_id']:e for e in read(SRC/'endpoints_clean.json')['endpoints']};assets=core.load_assets();
 for e in eps.values():assets['endpoints'][e['endpoint_id']]=e;assets['source'][e['endpoint_id']]='R4'
 raw=ArkSettings.from_env(required=True)
 if raw.base_url.rstrip('/')!=URL:raise RuntimeError('non-Plan route')
 client=ArkResponsesClient(ArkSettings(api_key=raw.api_key,base_url=raw.base_url,default_model=raw.default_model,timeout_seconds=180,max_retries=0));authority=acquire_authority(DATA,OWNER,plan['plan_body_sha256'],'temporal-extension-multiturn','pilot',plan['experiment']);outcome='runner-exception';calls=0
 try:
  completed=done()
  for eid in plan['endpoint_ids']:
   e=eps[eid];edir=BASE/'raw'/eid.replace(':','_');edir.mkdir(parents=True,exist_ok=True);pp=planning_prompt(e);pfile=edir/'planning.json'
   if pfile.exists():p1=read(edir/'planning-provider.json')
   else:
    p1=post(client,{'model':MODEL,'input':pp,'max_output_tokens':384,'temperature':0,'thinking':{'type':'disabled'}});calls+=1;safe_receipt(pfile,p1,{'prompt_sha256':sh(pp.encode())});atomic(edir/'planning-provider.json',p1)
   helper=assets['targeted_modules'][('R4','temporal_cutoff')].skill(e['package'],e['skill_context']);hsha=csha(helper)
   for arm in plan['branch_order'][eid]:
    key=eid+'|'+arm
    if key in completed:continue
    started=time.time();tool_called=False;tool_count=0;branch_calls=0;inst=final_instruction(e,arm,helper);body={'model':MODEL,'input':history(pp,p1,inst),'max_output_tokens':768,'temperature':0,'thinking':{'type':'disabled'}}
    if arm=='TOOL':body['tools']=[TOOL]
    p2=post(client,body);calls+=1;branch_calls+=1;safe_receipt(edir/f'{arm}-step2.json',p2,{'instruction_sha256':sh(inst.encode()),'helper_output_sha256':hsha})
    final=p2
    if arm=='TOOL':
     fc=ArkResponsesClient.function_calls(p2);tool_count=len(fc);tool_called=bool(fc)
     if fc:
      # respond to every call with the same frozen T1 output; duplicate calls are visible but not rewarded.
      inp=history(pp,p1,inst)+list(p2.get('output') or [])
      for c in fc:inp.append({'type':'function_call_output','call_id':c['call_id'],'output':json.dumps(helper,ensure_ascii=False,sort_keys=True,separators=(',',':'))})
      final=post(client,{'model':MODEL,'input':inp,'max_output_tokens':768,'temperature':0,'thinking':{'type':'disabled'},'tools':[TOOL]});calls+=1;branch_calls+=1;safe_receipt(edir/f'{arm}-final.json',final,{'tool_call_count':tool_count,'helper_output_sha256':hsha})
    ft=text(final);runtime_valid=bool(ft);success=False
    if runtime_valid:
     try:pred,sc=core.parse_and_score(assets,e,ft);success=bool(sc['success'])
     except Exception:runtime_valid=False
    row={'endpoint_id':eid,'arm':arm,'condition_position':plan['branch_order'][eid].index(arm),'planning_sha256':sh(text(p1).encode()),'helper_output_sha256':hsha,'tool_called':tool_called,'tool_call_count':tool_count,'model_calls':branch_calls,'runtime_valid':runtime_valid,'family_success':success,'resolved_model':final.get('model'),'final_text_sha256':sh(ft.encode()),'raw_receipt_path':str(edir/f'{arm}-final.json' if arm=='TOOL' and tool_called else edir/f'{arm}-step2.json')};append_row(row);completed.add(key);atomic(CHECK,{'schema_version':'1.0','plan_body_sha256':plan['plan_body_sha256'],'completed_branches':len(completed),'total_branches':12,'provider_calls_this_resume':calls,'last_key':key})
    if not runtime_valid:outcome='runtime-invalid';return {'status':'stopped','key':key,'calls':calls}
  outcome='completed';return {'status':'completed','branches':len(done()),'provider_calls_this_resume':calls}
 finally:release_authority(DATA,OWNER,str(authority['authority_id']),outcome)
def summary():
 rows=list(csv.DictReader(RESULTS.open()));by={}
 for r in rows:by.setdefault(r['endpoint_id'],{})[r['arm']]={'success':r['family_success']=='True','tool_called':r['tool_called']=='True','tool_call_count':int(r['tool_call_count'] or 0),'model_calls':int(r['model_calls'] or 0)}
 rates={a:sum(x[a]['success'] for x in by.values())/len(by) for a in ['BASE','CONTEXT','TOOL']};return {'endpoints':by,'success_rates':rates,'tool_call_rate':sum(x['TOOL']['tool_called'] for x in by.values())/len(by),'tool_vs_context_endpoint_delta':{e:int(x['TOOL']['success'])-int(x['CONTEXT']['success']) for e,x in by.items()}}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('cmd',choices=['prepare','run','summary']);x=ap.parse_args();print(json.dumps(prep() if x.cmd=='prepare' else execute() if x.cmd=='run' else summary(),indent=2))
if __name__=='__main__':main()
