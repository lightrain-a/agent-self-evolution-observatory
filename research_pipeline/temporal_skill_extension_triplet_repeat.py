from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from research_pipeline import temporal_skill_g0_execute as core
from research_pipeline.temporal_skill_extension_benign_generic import run_one
from research_pipeline.ark_provider import ArkResponsesClient,ArkSettings
from research_pipeline.experiment_authority import acquire_authority,release_authority
PID=core.PAPER_ID;DATA=core.DATA_ROOT
def read(p):return json.loads(p.read_text())
def prep(base:Path):
 src=read(base/'plan.json');d=base/'repeat-robustness-r1';d.mkdir(exist_ok=True);rows=[{**r,'repeat_id':1} for r in src['rows']];plan={'schema_version':'1.0','paper_id':PID,'experiment':src['experiment']+'_REPEAT_ROBUSTNESS','rows':rows,'model_identity':src['model_identity'],'summary':{'endpoints':len({r['endpoint_id'] for r in rows}),'repeat_id':1,'planned_model_calls':len(rows)},'selection_rule':'Repeat all endpoints from the already frozen pilot; no endpoint selection after outcomes; repeat is robustness only and not an independent scientific unit.'};plan['plan_body_sha256']=core.canonical_sha({k:v for k,v in plan.items() if k!='plan_body_sha256'});auth={'schema_version':'1.0','status':'HUMAN_EXECUTION_AUTHORITY_RECORDED','authorized_by':'explicit user directive in current conversation','execution_authorized':True,'provider_spend_authorized':True,'bound_plan_body_sha256':plan['plan_body_sha256'],'bounded_budget':{'model_calls_upper_bound':len(rows),'reruns_allowed':False,'resume_missing_only':True},'outcome_driven_endpoint_selection':False,'inferential_unit':'endpoint, not repeat'};auth['authorization_sha256']=core.canonical_sha({k:v for k,v in auth.items() if k!='authorization_sha256'});core.atomic_json(d/'plan.json',plan);core.atomic_json(d/'authorization.json',auth);return {'dir':str(d),'calls':len(rows),'plan_sha':plan['plan_body_sha256']}
def execute(base:Path,owner:str):
 d=base/'repeat-robustness-r1';plan=read(d/'plan.json');eps=read(base/'endpoints.json')['endpoints'];out=d/'results.json';a=core.load_assets()
 for e in eps:a['endpoints'][e['endpoint_id']]=e;a['source'][e['endpoint_id']]='R4'
 core.recover_orphan_raw(out,plan);old=core.load_csv_rows(d/'results.csv');bad=[k for k,r in old.items() if r.get('runtime_valid')!='True']
 if bad:raise RuntimeError('invalid checkpoint '+bad[0])
 ident=plan['model_identity'];raw=ArkSettings.from_env(required=True)
 if raw.base_url.rstrip('/')!=ident['required_plan_base_url'].rstrip('/'):raise RuntimeError('non-Plan route')
 client=ArkResponsesClient(ArkSettings(api_key=raw.api_key,base_url=raw.base_url,default_model=raw.default_model,timeout_seconds=180,max_retries=0));auth=acquire_authority(DATA,PID+':EXT:'+owner,plan['plan_body_sha256'],'temporal-extension-repeat','replicate',plan['experiment']);outcome='runner-exception';idx={core.row_key(r):i for i,r in enumerate(plan['rows'])}
 try:
  core.checkpoint_progress(out,plan,'repeat-robustness','running')
  for r in plan['rows']:
   k=core.row_key(r)
   if k in core.load_csv_rows(d/'results.csv'):continue
   x=run_one(client,a,r);core.persist_checkpoint(out,x,idx[k]);core.checkpoint_progress(out,plan,'repeat-robustness','running',f'last={k}')
   if not x.get('runtime_valid'):outcome=str(x.get('failure_kind') or 'runtime-invalid');core.checkpoint_progress(out,plan,'repeat-robustness','stopped',outcome);return {'status':'stopped','reason':outcome}
  rows=core.load_csv_rows(d/'results.csv');outcome='completed';core.checkpoint_progress(out,plan,'repeat-robustness','completed');return {'status':'completed','rows':len(rows),'model_drift':sum(r.get('resolved_model')!=ident['required_resolved_model'] for r in rows.values())}
 finally:release_authority(DATA,PID+':EXT:'+owner,str(auth['authority_id']),outcome)
def summary(base:Path):
 p0=core.load_csv_rows(base/'results.csv');p1=core.load_csv_rows(base/'repeat-robustness-r1'/'results.csv');by={}
 for src in (p0,p1):
  for r in src.values():by.setdefault(r['endpoint_id'],{}).setdefault(r['arm'],[]).append(1 if r['family_success']=='True' else 0)
 return by
def main():
 ap=argparse.ArgumentParser();ap.add_argument('cmd',choices=['prepare','run','summary']);ap.add_argument('--base',type=Path,required=True);ap.add_argument('--owner',default='TRIPLET-REPEAT');x=ap.parse_args();print(json.dumps(prep(x.base) if x.cmd=='prepare' else execute(x.base,x.owner) if x.cmd=='run' else summary(x.base),indent=2))
if __name__=='__main__':main()
