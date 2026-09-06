#!/usr/bin/env python3
"""R93 frozen complete-only analysis for the B1 12-run strong-scale check.

This analysis is intentionally diagnostic, not a population-effect estimator.
It asks whether each of the three R80-triggering P/T discordant tasks remains
P/T-discordant under Qwen2.5-32B and whether the three matched concordant
controls develop background P/T discordance.  It is frozen before any 32B task
outcome is observed and runs only after all 12 terminal rows are sealed.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib
from typing import Any

PAPER_ID="D2-PAPER-FAILURE-MEMORY-PROVENANCE"
DISCORDANT=["338","494","376"]
CONTROLS=["185","148","390"]
PAIRING={"338":"185","494":"148","376":"390"}

def canonical(v:Any)->str:return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"),default=str)
def digest(v:Any)->str:return hashlib.sha256(canonical(v).encode()).hexdigest()
def load(p:pathlib.Path)->dict[str,Any]:
 v=json.loads(p.read_text(encoding="utf-8"));
 if not isinstance(v,dict):raise RuntimeError(f"not-object:{p}")
 return v
def valid(v:dict[str,Any])->bool:return isinstance(v.get("receipt_sha256"),str) and v["receipt_sha256"]==digest({k:x for k,x in v.items() if k!="receipt_sha256"})
def sha(p:pathlib.Path)->str:
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(8*1024*1024),b""):h.update(b)
 return h.hexdigest()
def rows(p:pathlib.Path)->list[dict[str,Any]]:return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]

def analyze(r87:dict[str,Any],r85:dict[str,Any],authority:dict[str,Any],ledger:pathlib.Path)->dict[str,Any]:
 if not all(valid(x) for x in [r87,r85,authority]):raise RuntimeError("R93-input-receipt-invalid")
 a=authority.get("authority") or {}
 if a.get("analysis") is not True or a.get("strong_scale_analysis") is not True or a.get("strong_model_execution") is not False:raise RuntimeError("R93-analysis-authority-scope")
 if authority.get("r87_protocol_receipt_sha256")!=r87["receipt_sha256"] or authority.get("r85_final_pt_receipt_sha256")!=r85["receipt_sha256"]:raise RuntimeError("R93-authority-binding-drift")
 if authority.get("strong_terminal_ledger_sha256")!=sha(ledger):raise RuntimeError("R93-ledger-sha-drift")
 rs=rows(ledger);schedule=list(r87["panel"]["schedule"])
 if len(rs)!=12 or len(schedule)!=12:raise RuntimeError("R93-stage-not-12")
 expected=[(int(x["stage_ordinal"]),str(x["task_id"]),str(x["arm"])) for x in schedule]
 got=[(int(x["stage_ordinal"]),str(x["task_id"]),str(x["arm"])) for x in rs]
 if got!=expected:raise RuntimeError("R93-schedule-ledger-drift")
 if any(x.get("status")!="COMPLETE" or type(x.get("terminal_success")) is not bool for x in rs):raise RuntimeError("R93-stage-not-complete")
 by={}
 for x in rs:by.setdefault(str(x["task_id"]),{})[str(x["arm"])]=x
 task_rows=[]
 for tid in r87["panel"]["task_ids"]:
  d=by.get(str(tid),{});p=d.get("P_neutral");t=d.get("T_truthful")
  if not p or not t:raise RuntimeError(f"R93-missing-pair:{tid}")
  task_rows.append({"task_id":str(tid),"role":"historical_discordant" if str(tid) in DISCORDANT else "matched_control","matched_partner":PAIRING.get(str(tid)) or next((k for k,v in PAIRING.items() if v==str(tid)),None),"P_terminal_success":bool(p["terminal_success"]),"T_terminal_success":bool(t["terminal_success"]),"PT_discordant":bool(p["terminal_success"])!=bool(t["terminal_success"]),"P_steps":int(p.get("steps") or 0),"T_steps":int(t.get("steps") or 0),"first_action_diff":p.get("first_executable_action")!=t.get("first_executable_action")})
 persistent=[x["task_id"] for x in task_rows if x["role"]=="historical_discordant" and x["PT_discordant"]]
 control_disc=[x["task_id"] for x in task_rows if x["role"]=="matched_control" and x["PT_discordant"]]
 if control_disc:state="MATCHED_CONTROL_BACKGROUND_DISCORDANCE_WEAKENS_TARGETED_SCALE_INTERPRETATION"
 elif not persistent:state="ALL_THREE_7B8B_DISCORDANCES_RESOLVE_AT_32B_WITH_CONCORDANT_CONTROLS"
 else:state="ONE_OR_MORE_PROVENANCE_DISCORDANCES_PERSIST_AT_32B_WITH_CONCORDANT_CONTROLS"
 out={"schema_version":"1.0","paper_id":PAPER_ID,"receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R93-STRONG-SCALE-COMPLETE-ONLY-ANALYSIS","recorded_date":"2026-09-06","status":"R93_STRONG_SCALE_ANALYSIS_COMPLETE","role":"TARGETED_EXTERNAL_VALIDITY_CAPABILITY_BOUNDARY_DIAGNOSTIC","bindings":{"r87_protocol_receipt_sha256":r87["receipt_sha256"],"r85_final_pt_receipt_sha256":r85["receipt_sha256"],"analysis_authority_receipt_sha256":authority["receipt_sha256"],"strong_terminal_ledger_sha256":sha(ledger)},"task_rows":task_rows,"historical_discordant_task_ids":DISCORDANT,"matched_control_task_ids":CONTROLS,"persistent_discordant_task_ids":persistent,"persistent_discordant_count":len(persistent),"matched_control_discordant_task_ids":control_disc,"matched_control_discordant_count":len(control_disc),"state":state,"interpretation_rules":{"all_resolve":"consistent with the observed 7B/8B flips being executor capability/recovery-boundary sensitive at this stronger same-family executor; not proof of universal scale monotonicity","persist":"provenance-sensitive terminal branching persists for at least one outcome-selected case at 32B scale; prevalence remains unknown","control_discordance":"matched controls reveal nonzero background P/T instability at 32B, weakening targeted persistence/resolution attribution","always":"targeted post-selection diagnostic only; no population ATE, no cross-model pooling, no rewrite of R72/R73 primary result"},"population_effect_estimated":False,"cross_model_pooling":False,"changes_R85_primary_claim":False,"paper_claim_change_authorized":False,"scientific_authority":False,"experiment_authority":False,"gpu_authority":False};out["receipt_sha256"]=digest(out);return out

def main():
 p=argparse.ArgumentParser()
 for x in ["r87","r85","authority","ledger","output"]:p.add_argument("--"+x,type=pathlib.Path,required=True)
 a=p.parse_args();out=analyze(load(a.r87),load(a.r85),load(a.authority),a.ledger);a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({"status":out["status"],"receipt_sha256":out["receipt_sha256"],"state":out["state"],"persistent":out["persistent_discordant_count"],"control_discordance":out["matched_control_discordant_count"]},sort_keys=True))
if __name__=="__main__":main()
