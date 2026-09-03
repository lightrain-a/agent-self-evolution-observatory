#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ARMS=("win_c","first_fail","progress_fail","progress_contrast")
AUDIT_STATUS="PASS_SINGLE_CASE_S1_FULL_INTEGRITY_READY_FOR_ANALYSIS"
AUTH_STATUS="AUTHORIZED_E2_R17_SINGLE_CASE_S1_ANALYSIS"
EPS=1.0/18.0

def sha(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->dict[str,Any]: return json.loads(p.read_text(encoding="utf-8"))
def req(x:bool,m:str)->None:
    if not x: raise RuntimeError(m)
def atomic(p:Path,d:dict[str,Any])->None:
    p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+".tmp"); t.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8"); t.replace(p)
def rows(path:Path,key:str)->dict[str,dict[str,Any]]:
    out={}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip(): r=json.loads(line); out[str(r[key])]=r
    return out

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--contract",type=Path,required=True); ap.add_argument("--execution-authorization",type=Path,required=True); ap.add_argument("--analysis-authorization",type=Path,required=True); ap.add_argument("--completion-audit",type=Path,required=True); ap.add_argument("--run-summary",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); a=ap.parse_args(); req(not a.output.exists(),"S1 analysis already exists")
    c=load(a.contract); ea=load(a.execution_authorization); aa=load(a.analysis_authorization); au=load(a.completion_audit); s=load(a.run_summary); csha=sha(a.contract); easha=sha(a.execution_authorization); aush=sha(a.completion_audit); ssha=sha(a.run_summary)
    req(c.get("status")=="FROZEN_E2_R17_SINGLE_CASE_DIAGNOSTIC_WITNESS_S1","S1 contract drift"); req(ea.get("status")=="AUTHORIZED_E2_R17_SINGLE_CASE_DIAGNOSTIC_WITNESS_S1" and ea.get("contract_sha256")==csha,"S1 exec auth drift")
    req(au.get("status")==AUDIT_STATUS and au.get("scientific_scores_read") is False and au.get("partial_effect_read") is False and au.get("analyzer_run") is False,"S1 audit not clean"); req(au.get("contract_sha256")==csha and au.get("execution_authorization_sha256")==easha and au.get("run_summary_sha256")==ssha,"S1 audit binding drift")
    req(aa.get("status")==AUTH_STATUS and aa.get("single_use") is True,"S1 analysis auth drift"); req(aa.get("contract_sha256")==csha and aa.get("execution_authorization_sha256")==easha and aa.get("completion_audit_sha256")==aush and aa.get("run_summary_sha256")==ssha,"S1 analysis auth binding drift"); req(aa.get("analyzer_sha256")==sha(Path(__file__)) and Path(aa.get("analysis_output_path",""))==a.output,"S1 analyzer/output authority drift")
    ar={r["arm"]:r for r in s["arms"]}; req(set(ar)==set(ARMS),"S1 arm set drift"); heldout=c["heldout_task_ids"]; scores={}
    # First heldout-score access occurs only after the full audit and single-use authorization gates above.
    for arm in ARMS:
        manifest=rows(Path(ar[arm]["eval_manifest_path"]),"task_id"); req(set(manifest)==set(heldout),f"S1 heldout set drift {arm}"); vals=[]
        for task in heldout:
            ref=load(Path(manifest[task]["trajectory_ref_path"])); value=float(ref["score"]); req(value in (0.0,1.0),"S1 score must be binary"); vals.append(value)
        scores[arm]=vals
    j={arm:statistics.fmean(scores[arm]) for arm in ARMS}; successes={arm:int(sum(scores[arm])) for arm in ARMS}
    gains={arm:j[arm]-j["first_fail"] for arm in ("progress_fail","progress_contrast")}; candidate="progress_fail" if gains["progress_fail"]>=gains["progress_contrast"] else "progress_contrast"
    gate_gain=gains[candidate]>=EPS-1e-15; gate_control=j[candidate]>=j["win_c"]-1e-15; advance=gate_gain and gate_control
    if j["progress_fail"]>j["first_fail"] and j["progress_contrast"]<=j["progress_fail"]: mechanism="WITNESS_SELECTION_SIGNAL"
    elif j["progress_contrast"]>j["progress_fail"] and j["progress_contrast"]>j["first_fail"]: mechanism="SUCCESS_FAILURE_CONTRAST_SIGNAL"
    elif max(j["progress_fail"],j["progress_contrast"])>j["first_fail"] and max(j["progress_fail"],j["progress_contrast"])<j["win_c"]: mechanism="FIRST_FAIL_HARM_REPAIRED_BUT_NO_WINNER_ONLY_GAIN"
    else: mechanism="NO_CLEAR_DIAGNOSTIC_WITNESS_SIGNAL"
    payload={"schema_version":"1.0","artifact_type":"e2-r17-single-case-diagnostic-witness-s1-analysis","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":"S1_SIGNAL_PASS_ADVANCE_TO_S2" if advance else "S1_SIGNAL_FAIL_STOP_NO_S2","contract_sha256":csha,"execution_authorization_sha256":easha,"analysis_authorization_sha256":sha(a.analysis_authorization),"completion_audit_sha256":aush,"run_summary_sha256":ssha,"case_stream":"e1-tsr-00","development_only":True,"n_heldout":18,"arm_successes":successes,"arm_success_rate":j,"candidate":candidate,"candidate_minus_first_fail":gains[candidate],"candidate_minus_win_c":j[candidate]-j["win_c"],"s1_gate":{"minimum_candidate_minus_first_fail":EPS,"candidate_minus_first_fail_pass":gate_gain,"candidate_ge_win_c_pass":gate_control,"advance_to_s2":advance},"mechanism_readout":mechanism,"task_level_scores":{arm:{task:int(value) for task,value in zip(heldout,scores[arm])} for arm in ARMS},"interpretation_boundary":"Development-only single-case mechanism signal. No confirmatory, E3, paper-promotion, or submission claim is authorized.","authority":{"s2_execution":False,"e3_confirmation":False,"second_backbone":False,"public_benchmark":False,"paper_promotion":False,"submission":False}}
    atomic(a.output,payload); print(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)); return 0 if advance else 3
if __name__=="__main__": raise SystemExit(main())
