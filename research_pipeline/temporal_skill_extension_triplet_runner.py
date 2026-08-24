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
def execute(base:Path,owner_suffix:str):
 plan=read(base/'plan.json');eps=read(base/'endpoints.json')['endpoints'];out=base/'results.json';a=core.load_assets()
 for e in eps:a['endpoints'][e['endpoint_id']]=e;a['source'][e['endpoint_id']]='R4'
 core.recover_orphan_raw(out,plan);old=core.load_csv_rows(base/'results.csv');bad=[k for k,r in old.items() if r.get('runtime_valid')!='True']
 if bad:raise RuntimeError('invalid checkpoint '+bad[0])
 ident=plan['model_identity'];raw=ArkSettings.from_env(required=True)
 if raw.base_url.rstrip('/')!=ident['required_plan_base_url'].rstrip('/'):raise RuntimeError('non-Plan route')
 client=ArkResponsesClient(ArkSettings(api_key=raw.api_key,base_url=raw.base_url,default_model=raw.default_model,timeout_seconds=180,max_retries=0));auth=acquire_authority(DATA,PID+':EXT:'+owner_suffix,plan['plan_body_sha256'],'temporal-extension-triplet','pilot',plan['experiment']);outcome='runner-exception';idx={core.row_key(r):i for i,r in enumerate(plan['rows'])}
 try:
  core.checkpoint_progress(out,plan,'pilot','running')
  for r in plan['rows']:
   k=core.row_key(r)
   if k in core.load_csv_rows(base/'results.csv'):continue
   x=run_one(client,a,r);core.persist_checkpoint(out,x,idx[k]);core.checkpoint_progress(out,plan,'pilot','running',f'last={k}')
   if not x.get('runtime_valid'):outcome=str(x.get('failure_kind') or 'runtime-invalid');core.checkpoint_progress(out,plan,'pilot','stopped',outcome);return {'status':'stopped','reason':outcome,'unit':k}
  rows=core.load_csv_rows(base/'results.csv');drift=[k for k,r in rows.items() if r.get('resolved_model')!=ident['required_resolved_model']];gate={'schema_version':'1.0','gate':plan['experiment']+'-RUNTIME','pass':len(rows)==len(plan['rows']) and not drift,'calls':len(rows),'model_drift':drift,'scientific_outcomes_inspected_for_promotion':False};core.atomic_json(base/'pilot-gate.json',gate);outcome='completed' if gate['pass'] else 'pilot-fail';core.checkpoint_progress(out,plan,'pilot',outcome);return {'status':outcome,'gate':gate}
 finally:release_authority(DATA,PID+':EXT:'+owner_suffix,str(auth['authority_id']),outcome)
def summary(base:Path):
 rows=core.load_csv_rows(base/'results.csv');by={}
 for r in rows.values():by.setdefault(r['endpoint_id'],{})[r['arm']]=1 if r['family_success']=='True' else 0
 return {'endpoints':by,'rates':{arm:sum(a[arm] for a in by.values())/len(by) for arm in ['N_FRESH','B_GENERIC','T_FROZEN']},'contrasts':{e:{'T-N':a['T_FROZEN']-a['N_FRESH'],'T-B':a['T_FROZEN']-a['B_GENERIC'],'B-N':a['B_GENERIC']-a['N_FRESH']} for e,a in by.items()}}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('cmd',choices=['run','summary']);ap.add_argument('--base',type=Path,required=True);ap.add_argument('--owner',default='TRIPLET');x=ap.parse_args();print(json.dumps(execute(x.base,x.owner) if x.cmd=='run' else summary(x.base),indent=2))
if __name__=='__main__':main()
