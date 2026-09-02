#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

ARMS=("g0_base","g1_verify","g2_complete","g3_complete_recover")


def sha(path:Path)->str: return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path:Path)->dict[str,Any]: return json.loads(path.read_text(encoding="utf-8"))
def require(c:bool,m:str)->None:
    if not c: raise RuntimeError(m)
def rows(path:Path,key:str)->dict[str,dict[str,Any]]:
    out={}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r=json.loads(line); v=str(r[key]); require(v not in out,f"duplicate {key}: {v}"); out[v]=r
    return out
def atomic(path:Path,payload:dict[str,Any])->None:
    path.parent.mkdir(parents=True,exist_ok=True); tmp=path.with_suffix(path.suffix+".tmp"); tmp.write_text(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8"); tmp.replace(path)

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--contract",type=Path,required=True); ap.add_argument("--execution-authorization",type=Path,required=True); ap.add_argument("--analysis-authorization",type=Path,required=True); ap.add_argument("--completion-audit",type=Path,required=True); ap.add_argument("--run-summary",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); args=ap.parse_args()
    require(not args.output.exists(),"analysis output exists")
    c=load(args.contract); ea=load(args.execution_authorization); aa=load(args.analysis_authorization); audit=load(args.completion_audit); summary=load(args.run_summary); csha=sha(args.contract); easha=sha(args.execution_authorization)
    require(c.get("status")=="FROZEN_E2_R17_SINGLE_CASE_CONSTRAINED_STATE_MICRO","contract drift")
    require(ea.get("status")=="AUTHORIZED_E2_R17_SINGLE_CASE_CONSTRAINED_STATE_MICRO_MEASUREMENT" and ea.get("contract_sha256")==csha,"execution auth drift")
    require(audit.get("status")=="PASS_CONSTRAINED_STATE_MICRO_FULL_INTEGRITY_READY_FOR_ANALYSIS","audit not passing")
    require(aa.get("status")=="AUTHORIZED_E2_R17_SINGLE_CASE_CONSTRAINED_STATE_MICRO_ANALYSIS" and aa.get("single_use") is True,"analysis auth drift")
    require(aa.get("contract_sha256")==csha and aa.get("execution_authorization_sha256")==easha,"analysis binding drift")
    require(aa.get("completion_audit_sha256")==sha(args.completion_audit) and aa.get("run_summary_sha256")==sha(args.run_summary),"analysis audit/summary drift")
    require(aa.get("analyzer_sha256")==sha(Path(__file__)) and Path(aa.get("analysis_output_path","")).resolve()==args.output.resolve(),"analysis code/output binding drift")
    summary_rows={row["arm"]:row for row in summary["rows"]}; require(tuple(summary_rows)==ARMS,"summary arm drift")
    task_ids=list(c["heldout_task_ids"]); scores:dict[str,dict[str,int]]={}
    for arm in ARMS:
        manifest=rows(Path(summary_rows[arm]["eval_manifest_path"]),"task_id"); require(set(manifest)==set(task_ids),f"heldout set drift {arm}")
        arm_scores={}
        for task in task_ids:
            ref=load(Path(manifest[task]["trajectory_ref_path"])); score=float(ref["score"]); require(score in (0.0,1.0),"binary score drift"); arm_scores[task]=int(score)
        scores[arm]=arm_scores
    successes={arm:sum(values.values()) for arm,values in scores.items()}; rates={arm:successes[arm]/len(task_ids) for arm in ARMS}; baseline=rates["g0_base"]
    passing=[arm for arm in ARMS[1:] if rates[arm]-baseline >= 1.0/18.0-1e-15]
    selected=passing[0] if passing else None
    status="CONSTRAINED_STATE_MICRO_SCREEN_PASS" if selected else "CONSTRAINED_STATE_MICRO_SCREEN_FAIL"
    payload={"schema_version":"1.0","artifact_type":"e2-r17-single-case-constrained-state-micro-analysis","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":status,"case_stream":"e1-tsr-00","development_only":True,"contract_sha256":csha,"execution_authorization_sha256":easha,"analysis_authorization_sha256":sha(args.analysis_authorization),"completion_audit_sha256":sha(args.completion_audit),"run_summary_sha256":sha(args.run_summary),"n_heldout":len(task_ids),"arm_successes":successes,"arm_success_rate":rates,"difference_vs_g0":{arm:rates[arm]-baseline for arm in ARMS[1:]},"screen_threshold":1.0/18.0,"simplest_passing_arm":selected,"advance_to_stability_remeasurement":bool(selected),"task_level_scores":scores,"mechanism_readout":("A deterministic minimal repair state improved over the base by at least one of 18 tasks; remeasurement is required before any stabilization claim." if selected else "None of the deterministic repair ladder states improved over base by the frozen one-task threshold."),"authority":{"new_followup_execution":False,"e3_confirmation":False,"second_backbone":False,"public_benchmark":False,"paper_promotion":False,"submission":False}}
    atomic(args.output,payload); print(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)); return 0 if selected else 3

if __name__=="__main__": raise SystemExit(main())
