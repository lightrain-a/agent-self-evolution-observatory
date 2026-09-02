#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path

def sha(p:Path|str)->str: return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p:Path|str): return json.loads(Path(p).read_text(encoding='utf-8'))
def req(x:bool,msg:str):
    if not x: raise RuntimeError(msg)
def main()->int:
 ap=argparse.ArgumentParser(); ap.add_argument('--contract',type=Path,required=True); ap.add_argument('--candidate-authorization',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
 req(not a.output.exists(),'runner-entry preflight exists')
 c=load(a.contract); au=load(a.candidate_authorization); csha=sha(a.contract)
 req(c['status']=='FROZEN_E2_R18_DIAGNOSTIC_VALUE_STAGE_A_POOL_SUPPORT','contract status drift')
 req(au['status']=='CANDIDATE_E2_R18_DIAGNOSTIC_VALUE_STAGE_A_REPAIR1','candidate status drift'); req(au['contract_sha256']==csha,'candidate contract drift')
 req(au['supersedes_authorization_sha256']==sha('generated/e2-r18-diagnostic-value-stage-a-execution-authorization-20260902.json'),'supersession drift')
 blocker=Path(au['blocker_path']); req(sha(blocker)==au['blocker_sha256'],'blocker drift'); req(load(blocker)['provider_calls']==0,'failed attempt crossed provider boundary')
 for _,item in c['bound_code'].items(): req(Path(item['path']).is_file() and sha(item['path'])==item['sha256'],f"bound code drift {item['path']}")
 identity=Path(c['model_identity']['path']); req(sha(identity)==c['model_identity']['sha256'],'identity drift'); req(load(identity)['status']=='PASS_CURRENT_REVIEW_TRANCHE','identity status')
 suite=Path(c['suite']['root']); split=suite/'r17_split_manifest.json'; req(sha(suite/'suite_manifest.json')==c['suite']['suite_manifest_sha256'],'suite drift'); req(sha(split)==c['suite']['split_manifest_sha256'],'split drift'); req(sha(suite/'r17_controlled_metadata.json')==c['suite']['metadata_sha256'],'metadata drift')
 sp=load(split); streams=sp['e3_future_streams']; req(list(streams)==c['streams'],'stream order drift'); tasks=[t for s in c['streams'] for t in streams[s]]
 sc=au['execution_scope']; req(set(sc['allowed_task_ids'])==set(tasks),'task scope drift'); req(sc['allowed_modes']==['e1'] and sc['exact_k']==8,'mode/K drift'); req(sc['runtime_python_executable']==c['runtime']['python_executable'],'runtime python drift'); req(sc['runtime_freeze_sha256']==c['runtime']['freeze_sha256'],'runtime freeze drift'); req(sc['runtime_qualification_sha256']==c['runtime']['qualification_sha256'],'runtime qualification drift'); req(sc['required_skill_pre_sha256']==c['mindmemos']['initial_skill_sha256'],'skill binding drift')
 py=Path(c['runtime']['python_executable']); req(py.is_file(),'runtime python missing'); req(sha(c['runtime']['freeze_path'])==c['runtime']['freeze_sha256'],'freeze file drift'); req(sha(c['runtime']['qualification_path'])==c['runtime']['qualification_sha256'],'runtime qualification artifact drift')
 q=load(c['runtime']['qualification_path']); req(q['status']=='PASS_ZERO_PROVIDER_FULL_MINDMEMOS_RUNTIME_R2','runtime qualification status')
 head=subprocess.check_output(['git','-C',c['mindmemos']['root'],'rev-parse','HEAD'],text=True).strip(); req(head==c['mindmemos']['commit'],'MindMemOS commit drift'); req(sha(Path(c['mindmemos']['root'])/'resources/skill_evolve/spreadsheetbench_init_skill/xlsx/SKILL.md')==c['mindmemos']['initial_skill_sha256'],'initial skill drift')
 req(not Path(c['run_root']).exists(),'run root exists'); req(not Path(c['global_lineage_lease']['path']).exists(),'global lease exists')
 auth=au['authority']; req(auth['scientific_experiment'] is True and auth['r18_stage_a_pool_support'] is True and auth['provider_io'] is True,'candidate execution authority malformed')
 for k in ['updater','heldout_evaluation','analyzer','paper_promotion','second_backbone','public_benchmark']: req(auth[k] is False,f'overbroad {k}')
 payload={'schema_version':'1.0','artifact_type':'e2-r18-stage-a-runner-entry-preflight','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'status':'PASS_R18_STAGE_A_REPAIR1_RUNNER_ENTRY_BEFORE_GLOBAL_LEASE','contract_sha256':csha,'candidate_authorization_sha256':sha(a.candidate_authorization),'runtime_bindings_pass':True,'scope_96_tasks_pass':True,'global_lease_absent':True,'run_root_absent':True,'failed_attempt_provider_calls':0,'provider_calls':0,'provider_claims':0,'stopped_before_global_lease_and_provider_io':True}
 a.output.write_text(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+'\n'); print(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
