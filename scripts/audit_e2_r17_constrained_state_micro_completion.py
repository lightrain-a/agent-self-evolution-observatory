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
    ap=argparse.ArgumentParser(); ap.add_argument("--contract",type=Path,required=True); ap.add_argument("--authorization",type=Path,required=True); ap.add_argument("--run-summary",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); ap.add_argument("--analysis-output",type=Path); args=ap.parse_args()
    require(not args.output.exists(),"completion audit exists")
    if args.analysis_output: require(not args.analysis_output.exists(),"analysis exists before audit")
    c=load(args.contract); a=load(args.authorization); s=load(args.run_summary); csha=sha(args.contract); asha=sha(args.authorization)
    require(c.get("status")=="FROZEN_E2_R17_SINGLE_CASE_CONSTRAINED_STATE_MICRO","contract drift")
    require(a.get("status")=="AUTHORIZED_E2_R17_SINGLE_CASE_CONSTRAINED_STATE_MICRO_MEASUREMENT" and a.get("contract_sha256")==csha,"authorization drift")
    require(s.get("status")=="COMPLETED_PENDING_SEPARATE_CONSTRAINED_STATE_ANALYSIS","summary incomplete")
    require(s.get("contract_sha256")==csha and s.get("authorization_sha256")==asha,"summary binding drift")
    require(int(s.get("heldout_rollout_units",-1))==72 and int(s.get("new_updater_calls",-1))==0,"summary cardinality/updater drift")
    require(s.get("partial_effect_read") is False and s.get("analyzer_run") is False and s.get("inference_performed") is False,"runner crossed outcome boundary")
    run=Path(c["run_root"]); failure_files=list(run.rglob("eval_failure_*.json")); require(not failure_files,"technical failure artifacts present")
    state_map={row["arm"]:row for row in c["states"]}; require(tuple(state_map)==ARMS,"state set drift")
    held=set(c["heldout_task_ids"]); verified=0
    summary_rows={row["arm"]:row for row in s["rows"]}; require(tuple(summary_rows)==ARMS,"summary arm drift")
    for arm in ARMS:
        row=summary_rows[arm]; manifest=Path(row["eval_manifest_path"]); require(manifest.is_file() and sha(manifest)==row["eval_manifest_sha256"],f"manifest drift {arm}")
        erows=rows(manifest,"task_id"); require(set(erows)==held and len(erows)==18,f"heldout drift {arm}")
        for task,e in erows.items():
            sp=Path(e["summary_path"]); rp=Path(e["trajectory_ref_path"]); require(sp.is_file() and sha(sp)==e["summary_sha256"],f"summary drift {arm}/{task}"); require(rp.is_file() and sha(rp)==e["trajectory_ref_sha256"],f"ref drift {arm}/{task}")
            sd=load(sp); require(sd.get("status")=="COMPLETED" and int(sd.get("k"))==1,f"eval status/K drift {arm}/{task}"); require(sd.get("skill_pre_sha256")==state_map[arm]["skill_sha256"],f"skill binding drift {arm}/{task}")
            ref=load(rp); traj=Path(ref["trajectory_path"]); require(traj.is_file() and sha(traj)==ref["trajectory_sha256"],f"trajectory drift {arm}/{task}")
            # Outcome blind: no score access.
            verified += 1
    lease=Path(c["lineage_lease_path"]); require(lease.is_file(),"lease missing"); ld=load(lease); require(ld.get("status")=="COMPLETED_CONSTRAINED_STATE_MICRO","lease not complete")
    payload={"schema_version":"1.0","artifact_type":"e2-r17-single-case-constrained-state-micro-completion-audit","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":"PASS_CONSTRAINED_STATE_MICRO_FULL_INTEGRITY_READY_FOR_ANALYSIS","contract_sha256":csha,"execution_authorization_sha256":asha,"run_summary_path":str(args.run_summary),"run_summary_sha256":sha(args.run_summary),"heldout_rollout_units":verified,"new_updater_calls":0,"technical_failures":0,"scientific_scores_read":False,"partial_effect_read":False,"analyzer_run":False,"lineage_lease_sha256":sha(lease),"authority":{"mint_single_use_analysis_authorization":True,"provider_io":False,"updater":False,"heldout_evaluation":False,"paper_promotion":False}}
    atomic(args.output,payload); print(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)); return 0

if __name__=="__main__": raise SystemExit(main())
