from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from research_pipeline import temporal_skill_g0_execute as core
from research_pipeline.temporal_skill_extension_benign_generic import run_one
from research_pipeline.temporal_skill_extension_eia_clean import BASE,assets,MODEL,RES,URL
from research_pipeline.ark_provider import ArkResponsesClient,ArkSettings
from research_pipeline.experiment_authority import acquire_authority,release_authority
PID=core.PAPER_ID;DATA=core.DATA_ROOT;DIR=BASE/'repeat-robustness-r1';OUT=DIR/'results.json';PLAN=DIR/'plan.json';AUTH=DIR/'authorization.json';OWNER=PID+':EXT:EIA-CLEAN-REPEAT'
def read(p):return json.loads(p.read_text())
def prep():
 base=read(BASE/'plan.json');rows=[{**r,'repeat_id':1} for r in base['rows']];plan={'schema_version':'1.0','paper_id':PID,'experiment':'E2_EXTENSION_EIA_CLEAN_REPEAT_ROBUSTNESS','rows':rows,'model_identity':base['model_identity'],'summary':{'endpoints':4,'repeat_id':1,'planned_model_calls':12},'selection_rule':'Repeat robustness on all four previously frozen clean EIA endpoints; no endpoint selection after pilot outcomes; repeat is not an independent scientific unit.'};plan['plan_body_sha256']=core.canonical_sha({k:v for k,v in plan.items() if k!='plan_body_sha256'});auth={'schema_version':'1.0','status':'HUMAN_EXECUTION_AUTHORITY_RECORDED','authorized_by':'explicit user directive in current conversation','execution_authorized':True,'provider_spend_authorized':True,'bound_plan_body_sha256':plan['plan_body_sha256'],'bounded_budget':{'model_calls_upper_bound':12,'reruns_allowed':False,'resume_missing_only':True},'outcome_driven_endpoint_selection':False,'trigger':'post-pilot robustness after informative N/B/T separation','inferential_unit':'endpoint, not repeat'};auth['authorization_sha256']=core.canonical_sha({k:v for k,v in auth.items() if k!='authorization_sha256'});core.atomic_json(PLAN,plan);core.atomic_json(AUTH,auth);return {'calls':12,'plan_sha':plan['plan_body_sha256']}
def execute():
 plan=read(PLAN);a=assets();core.recover_orphan_raw(OUT,plan);old=core.load_csv_rows(DIR/'results.csv');bad=[k for k,r in old.items() if r.get('runtime_valid')!='True'];
 if bad:raise RuntimeError('bad checkpoint '+bad[0])
 raw=ArkSettings.from_env(required=True)
 if raw.base_url.rstrip('/')!=URL:raise RuntimeError('non-Plan route')
 client=ArkResponsesClient(ArkSettings(api_key=raw.api_key,base_url=raw.base_url,default_model=raw.default_model,timeout_seconds=180,max_retries=0));auth=acquire_authority(DATA,OWNER,plan['plan_body_sha256'],'temporal-extension-eia-repeat','replicate','E2-EIA-CLEAN-REPEAT-20260824');outcome='runner-exception';idx={core.row_key(r):i for i,r in enumerate(plan['rows'])}
 try:
  core.checkpoint_progress(OUT,plan,'repeat-robustness','running')
  for r in plan['rows']:
   k=core.row_key(r)
   if k in core.load_csv_rows(DIR/'results.csv'):continue
   x=run_one(client,a,r);core.persist_checkpoint(OUT,x,idx[k]);core.checkpoint_progress(OUT,plan,'repeat-robustness','running',f'last={k}')
   if not x.get('runtime_valid'):outcome=str(x.get('failure_kind') or 'runtime-invalid');core.checkpoint_progress(OUT,plan,'repeat-robustness','stopped',outcome);return {'status':'stopped','reason':outcome}
  rows=core.load_csv_rows(DIR/'results.csv');outcome='completed';core.checkpoint_progress(OUT,plan,'repeat-robustness','completed');return {'status':'completed','rows':len(rows),'model_drift':sum(r.get('resolved_model')!=RES for r in rows.values())}
 finally:release_authority(DATA,OWNER,str(auth['authority_id']),outcome)
def summary():
 p0=core.load_csv_rows(BASE/'results.csv');p1=core.load_csv_rows(DIR/'results.csv');by={}
 for src in (p0,p1):
  for r in src.values():by.setdefault(r['endpoint_id'],{}).setdefault(r['arm'],[]).append(1 if r['family_success']=='True' else 0)
 return {e:{a:v for a,v in arms.items()} for e,arms in by.items()}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('cmd',choices=['prepare','run','summary']);x=ap.parse_args();print(json.dumps(prep() if x.cmd=='prepare' else execute() if x.cmd=='run' else summary(),indent=2))
if __name__=='__main__':main()
