#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATUS="PASS_SINGLE_CASE_S1_FULL_INTEGRITY_READY_FOR_ANALYSIS"
ARMS=("win_c","first_fail","progress_fail","progress_contrast")

def sha(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->dict[str,Any]: return json.loads(p.read_text(encoding="utf-8"))
def req(x:bool,m:str)->None:
    if not x: raise RuntimeError(m)
def atomic(p:Path,d:dict[str,Any])->None:
    p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+".tmp"); t.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8"); t.replace(p)
def rows(path:Path,key:str)->dict[str,dict[str,Any]]:
    out={}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r=json.loads(line); v=str(r[key]); req(v not in out,f"duplicate {key}: {v}"); out[v]=r
    return out

def audit_ledger(db:Path,csha:str,asha:str)->int:
    req(db.is_file(),f"missing ledger {db}"); con=sqlite3.connect(f"file:{db}?mode=ro",uri=True)
    try:
        meta={str(k):str(v) for k,v in con.execute("SELECT key,value FROM metadata")}; claims=[(str(u),int(i)) for u,i in con.execute("SELECT unit_id,unit_call_index FROM claims")]
    finally: con.close()
    req(meta.get("contract_sha256")==csha and meta.get("authorization_sha256")==asha,"ledger authority drift"); req(int(meta.get("total_limit",-1))==191 and int(meta.get("per_unit_limit",-1))==11,"ledger budget drift"); req(len(claims)==len(set(claims)) and len(claims)<=191,"ledger duplicate/budget drift")
    counts=Counter(u for u,_ in claims)
    for u,n in counts.items(): req(n<=11 and sorted(i for uu,i in claims if uu==u)==list(range(1,n+1)),f"ledger sequence drift {u}")
    return len(claims)

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--contract",type=Path,required=True); ap.add_argument("--execution-authorization",type=Path,required=True); ap.add_argument("--run-summary",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); ap.add_argument("--analysis-output",type=Path); a=ap.parse_args(); req(not a.output.exists(),"S1 audit already exists");
    if a.analysis_output: req(not a.analysis_output.exists(),"S1 analysis exists before audit")
    c=load(a.contract); auth=load(a.execution_authorization); s=load(a.run_summary); csha=sha(a.contract); asha=sha(a.execution_authorization)
    req(c.get("status")=="FROZEN_E2_R17_SINGLE_CASE_DIAGNOSTIC_WITNESS_S1","S1 contract drift"); req(auth.get("status")=="AUTHORIZED_E2_R17_SINGLE_CASE_DIAGNOSTIC_WITNESS_S1" and auth.get("contract_sha256")==csha,"S1 auth drift")
    req(s.get("status")=="COMPLETED_PENDING_SEPARATE_S1_ANALYSIS" and s.get("contract_sha256")==csha and s.get("authorization_sha256")==asha,"S1 summary binding drift"); req(s.get("inference_performed") is False and s.get("partial_effect_read") is False and s.get("analyzer_run") is False,"runner crossed outcome boundary"); req(int(s.get("learned_states",-1))==4 and int(s.get("heldout_rollout_units",-1))==72,"S1 cardinality drift")
    run=Path(c["run_root"]); req(run.is_dir(),"S1 run root missing"); failures=sorted(run.rglob("*failure*.json")); req(not failures,"S1 technical failure artifacts present")
    lease=Path(c["lineage_lease_path"]); ld=load(lease); req(ld.get("status")=="COMPLETED_SINGLE_CASE_S1" and ld.get("contract_sha256")==csha and ld.get("authorization_sha256")==asha,"S1 terminal lease drift")
    evidence=run/"evidence_four_arm_receipt.json"; ed=load(evidence); req(ed.get("contract_sha256")==csha and ed.get("authorization_sha256")==asha and ed.get("partial_effect_read") is False,"S1 evidence receipt drift"); req(len(ed.get("evidence_receipts") or [])==8,"S1 evidence receipt cardinality drift")
    arm_rows={r["arm"]:r for r in s.get("arms") or []}; req(set(arm_rows)==set(ARMS),"S1 arm set drift"); heldout=set(c["heldout_task_ids"]); provider_claims={}
    for arm in ARMS:
        ar=arm_rows[arm]; state=Path(ar["state_root"]); skill=state/"update/skill_post/SKILL.md"; receipt=Path(ar["update_receipt_path"]); req(skill.is_file() and sha(skill)==ar["skill_post_sha256"],f"skill drift {arm}"); req(receipt.is_file() and sha(receipt)==ar["update_receipt_sha256"],f"receipt drift {arm}"); ur=load(receipt); req(ur.get("contract_sha256")==csha and ur.get("authorization_sha256")==asha and ur.get("causal_purity_mode")=="arm_blinded_selected_evidence","update provenance drift")
        em=Path(ar["eval_manifest_path"]); req(em.is_file() and sha(em)==ar["eval_manifest_sha256"],f"eval manifest drift {arm}"); erows=rows(em,"task_id"); req(set(erows)==heldout and len(erows)==18,f"heldout set drift {arm}")
        for task,r in erows.items():
            sp=Path(r["summary_path"]); rp=Path(r["trajectory_ref_path"]); req(sp.is_file() and sha(sp)==r["summary_sha256"],f"eval summary drift {arm}/{task}"); req(rp.is_file() and sha(rp)==r["trajectory_ref_sha256"],f"eval ref drift {arm}/{task}"); sd=load(sp); req(sd.get("status")=="COMPLETED" and int(sd.get("k"))==1 and sd.get("skill_pre_sha256")==ar["skill_post_sha256"] and sd.get("updater_receipt_sha256")==ar["update_receipt_sha256"],f"eval binding drift {arm}/{task}"); ref=load(rp); traj=Path(ref["trajectory_path"]); req(traj.is_file() and sha(traj)==ref["trajectory_sha256"],f"trajectory drift {arm}/{task}")
            # Outcome-blind: never access the heldout outcome value here.
        provider_claims[arm]=audit_ledger(state/"checkpoints/provider_budget.sqlite3",csha,asha)
    payload={"schema_version":"1.0","artifact_type":"e2-r17-single-case-s1-completion-integrity-audit","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":STATUS,"contract_path":str(a.contract),"contract_sha256":csha,"execution_authorization_path":str(a.execution_authorization),"execution_authorization_sha256":asha,"run_summary_path":str(a.run_summary),"run_summary_sha256":sha(a.run_summary),"lineage_lease_path":str(lease),"lineage_lease_sha256":sha(lease),"evidence_receipt_path":str(evidence),"evidence_receipt_sha256":sha(evidence),"learned_states":4,"heldout_rollout_units":72,"arms":list(ARMS),"provider_claims_by_arm":provider_claims,"provider_budget_binding_pass":True,"provider_claim_uniqueness_pass":True,"scientific_scores_read":False,"partial_effect_read":False,"analyzer_run":False,"authority":{"mint_single_use_s1_analysis_authorization":True,"provider_io":False,"scientific_execution":False,"paper_promotion":False,"submission":False}}
    atomic(a.output,payload); print(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
