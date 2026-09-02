#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATUS="PASS_SINGLE_CASE_FIRST_FAIL_STABILITY_FULL_INTEGRITY_READY_FOR_ANALYSIS"
ARMS=("win_c","first_fail")
REPS=(1,2)


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
    req(meta.get("contract_sha256")==csha and meta.get("authorization_sha256")==asha,"ledger authority drift")
    req(int(meta.get("total_limit",-1))==191 and int(meta.get("per_unit_limit",-1))==11,"ledger budget drift")
    req(len(claims)==len(set(claims)) and len(claims)<=191,"ledger duplicate/budget drift")
    counts=Counter(u for u,_ in claims)
    for u,n in counts.items(): req(n<=11 and sorted(i for uu,i in claims if uu==u)==list(range(1,n+1)),f"ledger sequence drift {u}")
    return len(claims)


def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--contract",type=Path,required=True); ap.add_argument("--execution-authorization",type=Path,required=True); ap.add_argument("--run-summary",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); ap.add_argument("--analysis-output",type=Path); a=ap.parse_args()
    req(not a.output.exists(),"stability audit already exists")
    if a.analysis_output: req(not a.analysis_output.exists(),"stability analysis exists before audit")
    c=load(a.contract); ea=load(a.execution_authorization); s=load(a.run_summary); csha=sha(a.contract); easha=sha(a.execution_authorization)
    req(c.get("status")=="FROZEN_E2_R17_SINGLE_CASE_FIRST_FAIL_STABILITY","stability contract drift")
    req(ea.get("status")=="AUTHORIZED_E2_R17_SINGLE_CASE_FIRST_FAIL_STABILITY_MEASUREMENT" and ea.get("contract_sha256")==csha,"stability execution authorization drift")
    req(s.get("status")=="COMPLETED_PENDING_SEPARATE_STABILITY_ANALYSIS" and s.get("contract_sha256")==csha and s.get("authorization_sha256")==easha,"stability summary binding drift")
    req(s.get("inference_performed") is False and s.get("partial_effect_read") is False and s.get("analyzer_run") is False,"stability runner crossed outcome boundary")
    req(int(s.get("new_learned_states",-1))==0 and int(s.get("measurement_states",-1))==4 and int(s.get("heldout_rollout_units",-1))==72,"stability cardinality drift")
    req(s.get("measurement_replicates")==[1,2] and s.get("arms")==["win_c","first_fail"],"stability design drift")

    # Parent S1 learned states are immutable and reused exactly; no updater execution is allowed here.
    parent_states={x["arm"]:x for x in c["learned_states"]}; req(set(parent_states)==set(ARMS),"parent state set drift")
    for arm,state in parent_states.items():
        skill=Path(state["skill_post_path"]); receipt=Path(state["update_receipt_path"])
        req(skill.is_file() and sha(skill)==state["skill_post_sha256"],f"parent skill drift {arm}")
        req(receipt.is_file() and sha(receipt)==state["update_receipt_sha256"],f"parent update receipt drift {arm}")

    run=Path(c["run_root"]); req(run.is_dir(),"stability run root missing")
    failures=sorted(run.rglob("*failure*.json")); req(not failures,"stability technical failure artifacts present")
    lease=Path(c["lineage_lease_path"]); ld=load(lease); req(ld.get("status")=="COMPLETED_FIRST_FAIL_STABILITY" and ld.get("contract_sha256")==csha and ld.get("authorization_sha256")==easha,"stability terminal lease drift")
    heldout=set(c["heldout_task_ids"]); summary_rows={(int(r["replicate"]),r["arm"]):r for r in s["rows"]}; req(set(summary_rows)=={(r,a) for r in REPS for a in ARMS},"stability summary row set drift")
    provider_claims={}
    for rep in REPS:
        for arm in ARMS:
            row=summary_rows[(rep,arm)]; em=Path(row["eval_manifest_path"]); req(em.is_file() and sha(em)==row["eval_manifest_sha256"],f"eval manifest drift rep{rep}/{arm}")
            erows=rows(em,"task_id"); req(set(erows)==heldout and len(erows)==18,f"heldout set drift rep{rep}/{arm}")
            binding=parent_states[arm]
            for task,r in erows.items():
                sp=Path(r["summary_path"]); rp=Path(r["trajectory_ref_path"])
                req(sp.is_file() and sha(sp)==r["summary_sha256"],f"eval summary drift rep{rep}/{arm}/{task}")
                req(rp.is_file() and sha(rp)==r["trajectory_ref_sha256"],f"eval ref drift rep{rep}/{arm}/{task}")
                sd=load(sp); req(sd.get("status")=="COMPLETED" and int(sd.get("k"))==1,"eval status/K drift")
                req(sd.get("skill_pre_sha256")==binding["skill_post_sha256"] and sd.get("updater_receipt_sha256")==binding["update_receipt_sha256"],f"frozen-state binding drift rep{rep}/{arm}/{task}")
                ref=load(rp); traj=Path(ref["trajectory_path"]); req(traj.is_file() and sha(traj)==ref["trajectory_sha256"],f"trajectory drift rep{rep}/{arm}/{task}")
                # Outcome-blind: never access heldout score here.
            provider_claims[f"rep{rep}/{arm}"]=audit_ledger(run/f"replicate_{rep}"/arm/"provider_budget.sqlite3",csha,easha)
    payload={"schema_version":"1.0","artifact_type":"e2-r17-single-case-first-fail-stability-completion-integrity-audit","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":STATUS,"contract_path":str(a.contract),"contract_sha256":csha,"execution_authorization_path":str(a.execution_authorization),"execution_authorization_sha256":easha,"run_summary_path":str(a.run_summary),"run_summary_sha256":sha(a.run_summary),"lineage_lease_path":str(lease),"lineage_lease_sha256":sha(lease),"new_learned_states":0,"measurement_states":4,"heldout_rollout_units":72,"provider_claims_by_measurement_state":provider_claims,"frozen_parent_state_binding_pass":True,"provider_budget_binding_pass":True,"provider_claim_uniqueness_pass":True,"scientific_scores_read":False,"partial_effect_read":False,"analyzer_run":False,"authority":{"mint_single_use_stability_analysis_authorization":True,"provider_io":False,"scientific_execution":False,"updater":False,"paper_promotion":False,"submission":False}}
    atomic(a.output,payload); print(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)); return 0

if __name__=="__main__": raise SystemExit(main())
