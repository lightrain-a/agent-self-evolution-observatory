from __future__ import annotations
import argparse, hashlib, html, json, re, sys
from datetime import datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from research_pipeline import temporal_skill_g0_execute as core
from research_pipeline.temporal_skill_extension_benign_generic import run_one
from research_pipeline.ark_provider import ArkResponsesClient,ArkSettings
from research_pipeline.experiment_authority import acquire_authority,release_authority
PID=core.PAPER_ID; DATA=core.DATA_ROOT
BASE=DATA/'paper-acceptance'/'source-native-replay'/PID/'20260824-extension-eia-future-nonceiling'
OUT=BASE/'results.json'; PLAN=BASE/'plan.json'; STAGE=BASE/'stage.json'; AUTH=BASE/'authorization.json'
CLEAN=['2026_07_01','2026_07_08','2026_07_15','2026_07_22','2026_07_29','2026_08_05','2026_08_12','2026_08_19']
MODEL='deepseek-v4-pro'; RES='deepseek-v4-pro-260425'; URL='https://ark.cn-beijing.volces.com/api/plan/v3'; OWNER=PID+':EXT:EIA-CLEAN'
def sh(b): return hashlib.sha256(b).hexdigest()
def csha(x): return sh(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
def iso(s): return datetime.strptime(s.strip(),'%B %d, %Y').date().isoformat()
def load(p): return json.loads(p.read_text())
def parse_source(token):
 p=BASE/'raw_sources'/f'wpsr_{token}.html'; raw=p.read_bytes(); s=raw.decode('utf-8','replace'); s=re.sub(r'<!--.*?-->',' ',s,flags=re.S); s=re.sub(r'<script.*?</script>|<style.*?</style>',' ',s,flags=re.I|re.S); s=re.sub(r'<[^>]+>',' ',s); s=html.unescape(' '.join(s.split())); m=re.search(r'Data for week ending\s+(.+?)\s+\|\s+Release Date:\s+(.+?)\s+\|',s)
 if not m: raise RuntimeError('header parse '+token)
 de,rel=m.groups(); ref='doc_'+sh(raw)[:12]
 return {'token':token,'evidence_ref':ref,'release_date':iso(rel),'reporting_period':iso(de),'raw_sha256':sh(raw),'raw_bytes':len(raw),'document_spans':[{'span_id':f'{ref}:s000','text':'Weekly Petroleum Status Report'},{'span_id':f'{ref}:s001','text':f'Data for week ending {de}'},{'span_id':f'{ref}:s002','text':f'Release Date: {rel}'}]}
def prepare():
 src=[parse_source(t) for t in CLEAN]
 # fail closed if URL token and first-party header disagree in this clean window
 for x in src:
  if x['release_date']!=x['token'].replace('_','-'): raise RuntimeError(f"source-date mismatch {x['token']}->{x['release_date']}")
 eps=[]
 for i in range(3,7):
  target=src[i]; past=src[i-3:i+1]; future=src[i+1]; rec=past+[future]
  eps.append({'endpoint_id':f"eia-future-cutoff::{target['evidence_ref']}",'phase':'EXT-EIA-CLEAN','failure_family':'temporal_cutoff','publisher':'EIA','domain':'energy','cutoff_date':target['release_date'],'target_release_date':target['release_date'],'task':'At the stated cutoff, identify the latest admissible EIA Weekly Petroleum Status Report and recover the data-ending week represented by that release. One post-cutoff distractor is present. Use only the supplied first-party package.','output_schema':{'evidence_refs_used':'array[string]','latest_evidence_ref':'string','reporting_period':'string'},'package':{'evidence_metadata':[{'evidence_ref':x['evidence_ref'],'release_date':x['release_date'],'schema_version':'1'} for x in rec],'release_records':[{'evidence_ref':x['evidence_ref'],'release_date':x['release_date'],'document_spans':x['document_spans']} for x in rec]},'skill_context':{'cutoff_date':target['release_date'],'schema_ceiling':'1'},'gold':{'admissible_evidence_refs':[x['evidence_ref'] for x in past],'latest_evidence_ref':target['evidence_ref'],'reporting_period':target['reporting_period']},'future_distractor':future['evidence_ref']})
 rows=[]
 for e in eps:
  for pos,(arm,cid) in enumerate([('N_FRESH','N0'),('B_GENERIC','BGEN'),('T_FROZEN','T1')]): rows.append({'endpoint_id':e['endpoint_id'],'failure_family':'temporal_cutoff','phase':'EXT-EIA-CLEAN','repeat_id':0,'arm':arm,'condition_id':cid,'condition_position':pos,'requested_model':MODEL,'required_resolved_model':RES})
 plan={'schema_version':'1.0','paper_id':PID,'experiment':'E2_EXTENSION_EIA_CLEAN_FUTURE','rows':rows,'model_identity':{'requested_model':MODEL,'required_resolved_model':RES,'required_plan_base_url':URL},'summary':{'independent_endpoints':4,'repeats':1,'planned_model_calls':12},'selection_rule':'Four consecutive clean targets 2026-07-22, 07-29, 08-05, 08-12 from a first-party window fixed before model calls; 08-19 is only the next-release distractor. 06-24 excluded before outcomes for source-header/date mismatch.'}; plan['plan_body_sha256']=csha({k:v for k,v in plan.items() if k!='plan_body_sha256'})
 stage={'schema_version':'1.0','bound_plan_body_sha256':plan['plan_body_sha256'],'pilot':{'model_calls':12,'row_keys':[core.row_key(r) for r in rows],'promotion_gate':'runtime/protocol/checkpoint integrity only','scientific_outcomes_used_for_promotion':False}}; stage['stage_contract_sha256']=csha({k:v for k,v in stage.items() if k!='stage_contract_sha256'})
 auth={'schema_version':'1.0','status':'HUMAN_EXECUTION_AUTHORITY_RECORDED','authorized_by':'explicit user directive in current conversation','execution_authorized':True,'provider_spend_authorized':True,'scientific_reopen_authorized':True,'bound_plan_body_sha256':plan['plan_body_sha256'],'bound_stage_contract_sha256':stage['stage_contract_sha256'],'bounded_budget':{'model_calls_upper_bound':12,'reruns_allowed':False,'resume_missing_only':True},'outcome_driven_selection_authorized':False}; auth['authorization_sha256']=csha({k:v for k,v in auth.items() if k!='authorization_sha256'})
 core.atomic_json(BASE/'source_manifest_clean.json',{'schema_version':'1.0','status':'FROZEN_BEFORE_MODEL_OUTCOMES','sources':src,'endpoints':4,'selection_rule':plan['selection_rule'],'source_anomaly_excluded':'2026-06-24 header says 2026-06-14','new_model_calls_at_freeze':0}); core.atomic_json(BASE/'endpoints_clean.json',{'schema_version':'1.0','endpoints':eps}); core.atomic_json(PLAN,plan); core.atomic_json(STAGE,stage); core.atomic_json(AUTH,auth)
 return {'endpoints':[e['target_release_date'] for e in eps],'calls':12,'plan_sha':plan['plan_body_sha256']}
def assets():
 a=core.load_assets(); eps=load(BASE/'endpoints_clean.json')['endpoints']
 for e in eps: a['endpoints'][e['endpoint_id']]=e; a['source'][e['endpoint_id']]='R4'
 return a
def execute():
 plan=load(PLAN); stage=load(STAGE); a=assets(); core.recover_orphan_raw(OUT,plan); existing=core.load_csv_rows(BASE/'results.csv'); bad=[k for k,r in existing.items() if r.get('runtime_valid')!='True']
 if bad: raise RuntimeError('invalid checkpoint '+bad[0])
 raw=ArkSettings.from_env(required=True)
 if raw.base_url.rstrip('/')!=URL: raise RuntimeError('non-Plan route')
 client=ArkResponsesClient(ArkSettings(api_key=raw.api_key,base_url=raw.base_url,default_model=raw.default_model,timeout_seconds=180,max_retries=0)); auth=acquire_authority(DATA,OWNER,plan['plan_body_sha256'],'temporal-extension-eia-clean','pilot','E2-EIA-CLEAN-PILOT-20260824'); outcome='runner-exception'; idx={core.row_key(r):i for i,r in enumerate(plan['rows'])}
 try:
  core.checkpoint_progress(OUT,plan,'pilot','running')
  for r in plan['rows']:
   k=core.row_key(r)
   if k in core.load_csv_rows(BASE/'results.csv'): continue
   x=run_one(client,a,r); core.persist_checkpoint(OUT,x,idx[k]); core.checkpoint_progress(OUT,plan,'pilot','running',f'last={k}')
   if not x.get('runtime_valid'): outcome=str(x.get('failure_kind') or 'runtime-invalid'); core.checkpoint_progress(OUT,plan,'pilot','stopped',outcome); return {'status':'stopped','reason':outcome,'unit':k}
  rows=core.load_csv_rows(BASE/'results.csv'); req=stage['pilot']['row_keys']; missing=[k for k in req if k not in rows]; invalid=[k for k in req if k in rows and rows[k].get('runtime_valid')!='True']; drift=[k for k in req if k in rows and rows[k].get('resolved_model')!=RES]; gate={'schema_version':'1.0','gate':'E2-EIA-CLEAN-PILOT-RUNTIME','pass':not(missing or invalid or drift),'pilot_calls':12,'missing':missing,'runtime_invalid':invalid,'model_drift':drift,'scientific_outcomes_inspected_for_promotion':False}; core.atomic_json(BASE/'pilot-gate.json',gate); outcome='pilot-pass' if gate['pass'] else 'pilot-fail'; core.checkpoint_progress(OUT,plan,'pilot',outcome); return {'status':outcome,'gate':gate}
 finally: release_authority(DATA,OWNER,str(auth['authority_id']),outcome)
def summary():
 rows=core.load_csv_rows(BASE/'results.csv'); by={}
 for r in rows.values(): by.setdefault(r['endpoint_id'],{})[r['arm']]=1 if r['family_success']=='True' else 0
 return {'endpoints':by,'rates':{arm:sum(a[arm] for a in by.values())/len(by) for arm in ['N_FRESH','B_GENERIC','T_FROZEN']},'contrasts':{e:{'T-N':a['T_FROZEN']-a['N_FRESH'],'T-B':a['T_FROZEN']-a['B_GENERIC'],'B-N':a['B_GENERIC']-a['N_FRESH']} for e,a in by.items()}}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('cmd',choices=['prepare','pilot','summary']);x=ap.parse_args();print(json.dumps(prepare() if x.cmd=='prepare' else execute() if x.cmd=='pilot' else summary(),indent=2))
if __name__=='__main__': main()
