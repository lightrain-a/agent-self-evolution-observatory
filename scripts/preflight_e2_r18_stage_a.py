#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,shutil,sqlite3,subprocess,tempfile
from datetime import datetime,timezone
from pathlib import Path

def sha(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path): return json.loads(p.read_text(encoding='utf-8'))
def req(x:bool,msg:str):
    if not x: raise RuntimeError(msg)
def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--contract',type=Path,required=True); ap.add_argument('--preflight-authorization',type=Path,required=True); ap.add_argument('--env-file',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
    req(not a.output.exists(),'preflight output already exists')
    c=load(a.contract); au=load(a.preflight_authorization); csha=sha(a.contract); asha=sha(a.preflight_authorization)
    req(c.get('status')=='FROZEN_E2_R18_DIAGNOSTIC_VALUE_STAGE_A_POOL_SUPPORT','contract status drift')
    req(au.get('status')=='AUTHORIZED_E2_R18_DIAGNOSTIC_VALUE_STAGE_A_PREFLIGHT','preflight auth status drift')
    req(au.get('contract_sha256')==csha,'preflight auth contract drift')
    req(au.get('authority',{}).get('provider_io') is False and au.get('authority',{}).get('scientific_experiment') is False,'preflight authority overbroad')
    for label,item in c['bound_code'].items(): req((Path(item['path']).is_file() and sha(Path(item['path']))==item['sha256']),f'bound code drift {label}')
    for key in ['preregistration','future_substrate_eligibility','fresh_heldout_qualification']:
        item=c[key]; p=Path(item['path']); req(p.is_file() and sha(p)==item['sha256'],f'{key} drift')
    suite=Path(c['suite']['root']); split=suite/'r17_split_manifest.json'; req(sha(suite/'suite_manifest.json')==c['suite']['suite_manifest_sha256'],'suite drift'); req(sha(split)==c['suite']['split_manifest_sha256'],'split drift')
    sp=load(split); streams=sp['e3_future_streams']; req(list(streams)==c['streams'],'stream ordering drift')
    all_tasks=[t for s in c['streams'] for t in streams[s]]; req(len(all_tasks)==96 and len(set(all_tasks))==96,'future task count drift')
    scope=au['execution_scope']; req(set(scope['allowed_task_ids'])==set(all_tasks),'preflight scope task drift'); req(scope['exact_k']==8,'preflight K drift')
    actor=Path(c['bound_code']['actor_stage_a']['path']); py=Path(c['runtime']['python_executable'])
    tmp=Path(tempfile.mkdtemp(prefix='e2r18-stage-a-preflight-')); ledger=tmp/'provider_budget.sqlite3'; passes=[]
    try:
        for stream in c['streams']:
            out=tmp/f'{stream}.json'; rr=tmp/'runs'/stream
            cmd=[str(py),str(actor),'--env-file',str(a.env_file),'--suite-root',str(suite),'--mindmemos-root',c['mindmemos']['root'],'--run-root',str(rr),'--identity',c['model_identity']['path'],'--authorization',str(a.preflight_authorization),'--mode','e1','--model',c['actor']['requested_model'],'--stream-id',stream,'--k','8','--prefix-ks','1,2,4,8','--max-turns',str(c['actor']['max_turns']),'--max-output-tokens',str(c['actor']['max_output_tokens']),'--concurrency',str(c['actor']['concurrency']),'--provider-budget-ledger',str(ledger),'--provider-total-call-limit',str(c['budget']['max_provider_calls']),'--provider-per-unit-call-limit',str(c['actor']['max_turns']),'--preflight-only','--output',str(out)]
            r=subprocess.run(cmd,capture_output=True,text=True,cwd=Path(__file__).resolve().parents[1]); req(r.returncode==0,f'actor preflight failed {stream}: {r.stderr[-800:]}')
            d=load(out); req(d.get('status')=='PASS_BEFORE_PROVIDER_IO' and d.get('provider_calls')==0 and d.get('provider_claims')==0,f'preflight crossed provider boundary {stream}'); req(d.get('task_ids')==streams[stream],f'task ordering drift {stream}'); passes.append(stream)
        con=sqlite3.connect(f'file:{ledger}?mode=ro',uri=True); claims=con.execute('select count(*) from claims').fetchone()[0]; con.close(); req(claims==0,'preflight provider claims nonzero')
    finally: shutil.rmtree(tmp,ignore_errors=True)
    payload={'schema_version':'1.0','artifact_type':'e2-r18-stage-a-actual-actor-path-preflight','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'status':'PASS_R18_STAGE_A_ACTUAL_PATH_12_OF_12_ZERO_PROVIDER','contract_sha256':csha,'preflight_authorization_sha256':asha,'streams_expected':12,'streams_passed':len(passes),'stream_ids':passes,'tasks_validated':96,'k':8,'provider_calls':0,'provider_claims':0,'updater_calls':0,'heldout_evaluations':0,'stopped_before_provider_io':True,'authority':{'mint_stage_a_execution_authorization':False,'provider_io':False,'scientific_execution':False}}
    a.output.write_text(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+'\n'); print(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
