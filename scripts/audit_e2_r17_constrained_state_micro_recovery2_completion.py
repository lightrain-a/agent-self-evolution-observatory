#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, sqlite3, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
ARMS=("g0_base","g1_verify","g2_complete","g3_complete_recover")
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->dict[str,Any]:return json.loads(p.read_text(encoding='utf-8'))
def req(c:bool,m:str)->None:
    if not c:raise RuntimeError(m)
def rows(p:Path,key:str)->dict[str,dict[str,Any]]:
    out={}
    for line in p.read_text(encoding='utf-8').splitlines():
        if line.strip():
            r=json.loads(line);v=str(r[key]);req(v not in out,f'duplicate {key}:{v}');out[v]=r
    return out
def atomic(p:Path,d:dict[str,Any])->None:p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8');t.replace(p)
def ledger_count(p:Path)->int:
    if not p.exists():return 0
    c=sqlite3.connect(f'file:{p}?mode=ro',uri=True);n=c.execute('select count(*) from claims').fetchone()[0];c.close();return int(n)
def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--contract',type=Path,required=True);ap.add_argument('--authorization',type=Path,required=True);ap.add_argument('--run-summary',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--analysis-output',type=Path);a=ap.parse_args();req(not a.output.exists(),'recovery2 audit exists');
    if a.analysis_output:req(not a.analysis_output.exists(),'analysis exists before audit')
    c,au,s=load(a.contract),load(a.authorization),load(a.run_summary);cs,aus=sha(a.contract),sha(a.authorization);req(c.get('status')=='FROZEN_E2_R17_SINGLE_CASE_CONSTRAINED_STATE_MICRO','contract drift');req(au.get('status')=='AUTHORIZED_E2_R17_SINGLE_CASE_CONSTRAINED_STATE_MICRO_MEASUREMENT' and au.get('contract_sha256')==cs,'auth drift');req(s.get('status')=='COMPLETED_PENDING_SEPARATE_CONSTRAINED_STATE_ANALYSIS' and s.get('contract_sha256')==cs and s.get('authorization_sha256')==aus,'summary binding drift');req(int(s.get('heldout_rollout_units',-1))==72 and int(s.get('inherited_completed_measurements',-1))==45 and int(s.get('new_measurements',-1))==27,'summary cardinality drift');req(s.get('partial_effect_read') is False and s.get('analyzer_run') is False,'outcome boundary drift')
    rec=c['recovery2'];run=Path(c['run_root']);req(not list(run.rglob('eval_failure_*.json')),'child technical failure present');state_map={x['arm']:x for x in c['states']};held=set(c['heldout_task_ids']);parent_cs=rec['parent_contract_sha256'];parent_as=rec['parent_authorization_sha256'];summary_rows={x['arm']:x for x in s['rows']};verified=0;inherited=0;child=0
    parent_tasks={}
    for arm in ARMS:
        pm=Path(rec['parent_manifests'][arm]['path']);pr=rows(pm,'task_id');parent_tasks[arm]=set(pr);cm=Path(summary_rows[arm]['eval_manifest_path']);req(cm.is_file() and sha(cm)==summary_rows[arm]['eval_manifest_sha256'],f'combined manifest drift {arm}');cr=rows(cm,'task_id');req(set(cr)==held and len(cr)==18,f'combined heldout drift {arm}')
        for task,row in cr.items():
            sp=Path(row['summary_path']);rp=Path(row['trajectory_ref_path']);req(sp.is_file() and sha(sp)==row['summary_sha256'],f'summary drift {arm}/{task}');req(rp.is_file() and sha(rp)==row['trajectory_ref_sha256'],f'ref drift {arm}/{task}');sd=load(sp);req(sd.get('status')=='COMPLETED' and int(sd.get('k'))==1 and sd.get('skill_pre_sha256')==state_map[arm]['skill_sha256'],f'eval binding drift {arm}/{task}');
            if task in parent_tasks[arm]:req(sd.get('contract_sha256')==parent_cs and sd.get('authorization_sha256')==parent_as,f'parent provenance drift {arm}/{task}');inherited+=1
            else:req(sd.get('contract_sha256')==cs and sd.get('authorization_sha256')==aus,f'child provenance drift {arm}/{task}');child+=1
            ref=load(rp);tp=Path(ref['trajectory_path']);req(tp.is_file() and sha(tp)==ref['trajectory_sha256'],f'trajectory drift {arm}/{task}');verified+=1
    req((verified,inherited,child)==(72,45,27),'provenance cardinality drift')
    parent=Path(rec['parent_run_root']);pclaims={arm:ledger_count(parent/'measurement'/arm/'provider_budget.sqlite3') for arm in ARMS};orig=ledger_count(Path(rec['original_failed_lineage']['provider_ledger_path']));cumulative=dict(pclaims);cumulative['g3_complete_recover']+=orig;child_claims={arm:ledger_count(run/'measurement'/arm/'provider_budget.sqlite3') for arm in ARMS};req(all(cumulative[x]+child_claims[x]<=191 for x in ARMS),'cumulative provider budget exceeded');lease=Path(c['lineage_lease_path']);req(lease.is_file() and load(lease).get('status')=='COMPLETED_CONSTRAINED_STATE_MICRO','recovery2 lease not complete')
    payload={'schema_version':'1.0','artifact_type':'e2-r17-constrained-state-micro-recovery2-completion-audit','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'status':'PASS_CONSTRAINED_STATE_MICRO_FULL_INTEGRITY_READY_FOR_ANALYSIS','contract_sha256':cs,'execution_authorization_sha256':aus,'run_summary_path':str(a.run_summary),'run_summary_sha256':sha(a.run_summary),'heldout_rollout_units':verified,'inherited_completed_measurements':inherited,'new_measurements':child,'explicit_429_recovery_units':1,'completed_unit_replay':False,'new_updater_calls':0,'technical_failures':0,'parent_claims_by_arm':pclaims,'original_failed_claims_g3':orig,'child_claims_by_arm':child_claims,'cumulative_claims_by_arm':{arm:cumulative[arm]+child_claims[arm] for arm in ARMS},'scientific_scores_read':False,'partial_effect_read':False,'analyzer_run':False,'lineage_lease_sha256':sha(lease),'authority':{'mint_single_use_analysis_authorization':True,'provider_io':False,'updater':False,'heldout_evaluation':False,'paper_promotion':False}};atomic(a.output,payload);print(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
