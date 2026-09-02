#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

AUDIT_STATUS="PASS_SINGLE_CASE_FIRST_FAIL_STABILITY_FULL_INTEGRITY_READY_FOR_ANALYSIS"
AUTH_STATUS="AUTHORIZED_E2_R17_SINGLE_CASE_FIRST_FAIL_STABILITY_ANALYSIS"
EPS=1.0/18.0
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
            r=json.loads(line); out[str(r[key])]=r
    return out


def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--contract",type=Path,required=True); ap.add_argument("--execution-authorization",type=Path,required=True); ap.add_argument("--analysis-authorization",type=Path,required=True); ap.add_argument("--completion-audit",type=Path,required=True); ap.add_argument("--run-summary",type=Path,required=True); ap.add_argument("--parent-s1-analysis",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); a=ap.parse_args()
    req(not a.output.exists(),"stability analysis already exists")
    c=load(a.contract); ea=load(a.execution_authorization); aa=load(a.analysis_authorization); au=load(a.completion_audit); s=load(a.run_summary); parent=load(a.parent_s1_analysis)
    csha=sha(a.contract); easha=sha(a.execution_authorization); aush=sha(a.completion_audit); ssha=sha(a.run_summary)
    req(c.get("status")=="FROZEN_E2_R17_SINGLE_CASE_FIRST_FAIL_STABILITY","stability contract drift")
    req(ea.get("status")=="AUTHORIZED_E2_R17_SINGLE_CASE_FIRST_FAIL_STABILITY_MEASUREMENT" and ea.get("contract_sha256")==csha,"stability execution auth drift")
    req(au.get("status")==AUDIT_STATUS and au.get("scientific_scores_read") is False and au.get("partial_effect_read") is False and au.get("analyzer_run") is False,"stability audit not clean")
    req(au.get("contract_sha256")==csha and au.get("execution_authorization_sha256")==easha and au.get("run_summary_sha256")==ssha,"stability audit binding drift")
    req(aa.get("status")==AUTH_STATUS and aa.get("single_use") is True,"stability analysis auth drift")
    req(aa.get("contract_sha256")==csha and aa.get("execution_authorization_sha256")==easha and aa.get("completion_audit_sha256")==aush and aa.get("run_summary_sha256")==ssha,"stability analysis auth binding drift")
    req(aa.get("analyzer_sha256")==sha(Path(__file__)) and Path(aa.get("analysis_output_path",""))==a.output,"stability analyzer/output authority drift")
    req(parent.get("status")=="S1_SIGNAL_FAIL_STOP_NO_S2" and parent.get("case_stream")=="e1-tsr-00","parent S1 analysis drift")
    req(c["design"]["sha256"]==sha(Path(c["design"]["path"])),"stability design binding drift")

    summary_rows={(int(r["replicate"]),r["arm"]):r for r in s["rows"]}; req(set(summary_rows)=={(r,a) for r in REPS for a in ARMS},"stability row set drift")
    heldout=c["heldout_task_ids"]; score_by_rep_arm:dict[int,dict[str,list[float]]]={}
    # First score access occurs only after the full audit and single-use authorization checks above.
    for rep in REPS:
        score_by_rep_arm[rep]={}
        for arm in ARMS:
            manifest=rows(Path(summary_rows[(rep,arm)]["eval_manifest_path"]),"task_id"); req(set(manifest)==set(heldout),f"heldout set drift rep{rep}/{arm}")
            vals=[]
            for task in heldout:
                ref=load(Path(manifest[task]["trajectory_ref_path"])); value=float(ref["score"]); req(value in (0.0,1.0),"stability score must be binary"); vals.append(value)
            score_by_rep_arm[rep][arm]=vals

    replicate_rows=[]; diffs=[]
    for rep in REPS:
        j={arm:statistics.fmean(score_by_rep_arm[rep][arm]) for arm in ARMS}; diff=j["first_fail"]-j["win_c"]; diffs.append(diff)
        replicate_rows.append({"replicate":rep,"win_c_successes":int(sum(score_by_rep_arm[rep]["win_c"])),"first_fail_successes":int(sum(score_by_rep_arm[rep]["first_fail"])),"j_win_c":j["win_c"],"j_first_fail":j["first_fail"],"difference_first_fail_minus_win_c":diff,"minimum_difference_pass":diff>=EPS-1e-15})
    mean_diff=statistics.fmean(diffs); each_pass=all(d>=EPS-1e-15 for d in diffs); mean_pass=mean_diff>=EPS-1e-15; stable=each_pass and mean_pass
    status="FIRST_FAIL_FROZEN_STATE_STABILITY_PASS" if stable else "FIRST_FAIL_FROZEN_STATE_STABILITY_FAIL_MEASUREMENT_INSTABILITY"
    payload={"schema_version":"1.0","artifact_type":"e2-r17-single-case-first-fail-stability-analysis","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":status,"contract_sha256":csha,"execution_authorization_sha256":easha,"analysis_authorization_sha256":sha(a.analysis_authorization),"completion_audit_sha256":aush,"run_summary_sha256":ssha,"parent_s1_analysis_path":str(a.parent_s1_analysis),"parent_s1_analysis_sha256":sha(a.parent_s1_analysis),"case_stream":"e1-tsr-00","development_only":True,"new_learned_states":0,"measurement_replicates":[1,2],"replicate_results":replicate_rows,"mean_difference_first_fail_minus_win_c":mean_diff,"stability_gate":{"minimum_difference_each_replicate":EPS,"minimum_mean_difference":EPS,"each_replicate_pass":each_pass,"mean_difference_pass":mean_pass,"pass":stable},"historical_s1_rep0":{"descriptive_only":True,"j_win_c":parent["arm_success_rate"]["win_c"],"j_first_fail":parent["arm_success_rate"]["first_fail"],"difference_first_fail_minus_win_c":parent["arm_success_rate"]["first_fail"]-parent["arm_success_rate"]["win_c"]},"interpretation":"Tests whether the surprising S1 First-Fail advantage persists when the exact same learned First-Fail and WIN-C skills are re-measured twice without any updater/state regeneration.","authority":{"s2_execution":False,"new_updater_execution":False,"e3_confirmation":False,"second_backbone":False,"public_benchmark":False,"paper_promotion":False,"submission":False}}
    atomic(a.output,payload); print(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)); return 0 if stable else 3

if __name__=="__main__": raise SystemExit(main())
