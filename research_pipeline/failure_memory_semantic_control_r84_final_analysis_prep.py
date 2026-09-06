#!/usr/bin/env python3
"""R84 final P/T-only analysis authority for the completed B1 R72/R73 run.

This prep binds the sealed Qwen and Llama stage ledgers by SHA256 and authorizes
only the already-preregistered P_neutral vs T_truthful analysis on each executor.
Qwen T_truthful vs S_shuffled remains sealed because R83 classified the Qwen
primary as NO_EFFECT_DETECTED. No model execution or paper-claim change is granted.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib
from typing import Any

PAPER_ID="D2-PAPER-FAILURE-MEMORY-PROVENANCE"
STATUS="R84_FINAL_PT_ONLY_ANALYSIS_AUTHORIZED_LLAMA_OUTCOME_STILL_UNOPENED"

def canonical(v:Any)->str:return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"),default=str)
def digest(v:Any)->str:return hashlib.sha256(canonical(v).encode()).hexdigest()
def load(p:pathlib.Path)->dict[str,Any]:
    v=json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(v,dict):raise RuntimeError(f"not-object:{p}")
    return v
def valid(v:dict[str,Any])->bool:return isinstance(v.get("receipt_sha256"),str) and v["receipt_sha256"]==digest({k:x for k,x in v.items() if k!="receipt_sha256"})

def build(protocol:dict[str,Any],r80:dict[str,Any],r82:dict[str,Any],r83:dict[str,Any],qsha:str,lsha:str,qrows:int,lrows:int)->dict[str,Any]:
    if not all(valid(x) for x in [protocol,r80,r82,r83]):raise RuntimeError("R84-input-receipt-invalid")
    if r83.get("Qwen_primary_state")!="NO_EFFECT_DETECTED":raise RuntimeError("R84-unexpected-Qwen-primary-state")
    if r83.get("Qwen_gatekept_T_minus_S",{}).get("gate")!="NOT_OPENED_BY_FROZEN_R72_R73_PRIMARY_GATE" or r83.get("Qwen_gatekept_T_minus_S",{}).get("stats") is not None:raise RuntimeError("R84-Qwen-TS-not-sealed")
    if qrows!=189 or lrows!=132:raise RuntimeError("R84-stage-cardinality-drift")
    if (r82.get("authority") or {}).get("llama_execution") is not True:raise RuntimeError("R84-R82-Llama-authority-drift")
    out={
      "schema_version":"1.0","paper_id":PAPER_ID,"receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R84-FINAL-PT-ONLY-ANALYSIS-AUTHORITY","recorded_date":"2026-09-06","status":STATUS,"role":"POST_STAGE_SEAL_PRE_LLAMA_OUTCOME_OPEN_ANALYSIS_AUTHORITY",
      "protocol_receipt_sha256":protocol["receipt_sha256"],
      "bindings":{"r80_scale_freeze_receipt_sha256":r80["receipt_sha256"],"r82_llama_authority_receipt_sha256":r82["receipt_sha256"],"r83_qwen_interim_receipt_sha256":r83["receipt_sha256"],"qwen_terminal_ledger_sha256":qsha,"llama_terminal_ledger_sha256":lsha,"qwen_terminal_rows":qrows,"llama_terminal_rows":lrows},
      "authority":{"analysis":True,"qwen_PT_read":True,"llama_PT_read":True,"qwen_TS_read":False,"qwen_execution":False,"llama_execution":False,"gpu":False,"PSMG":False,"L3":False,"paper_claim_change":False,"strong_model_download":False,"strong_model_execution":False},
      "scope":{"Qwen_primary":"T_truthful minus P_neutral, n=66","Llama_replication":"T_truthful minus P_neutral, n=66","paired_id_reporting_required":True,"cross_executor_pooling":False,"Qwen_correctness_T_minus_S":"SEALED_NOT_AUTHORIZED","strong_scale_panel_generation":"allowed only from sealed P/T classification under R80 deterministic matching; execution remains unauthorized"},
      "llama_terminal_outcomes_opened_when_authority_created":False,
      "scientific_authority":False,"experiment_authority":False,"gpu_authority":False,
    }
    out["receipt_sha256"]=digest(out);return out

def main():
    ap=argparse.ArgumentParser()
    for x in ["protocol","r80","r82","r83","output"]:ap.add_argument("--"+x,type=pathlib.Path,required=True)
    ap.add_argument("--qwen-ledger-sha",required=True);ap.add_argument("--llama-ledger-sha",required=True)
    ap.add_argument("--qwen-rows",type=int,required=True);ap.add_argument("--llama-rows",type=int,required=True)
    a=ap.parse_args();out=build(load(a.protocol),load(a.r80),load(a.r82),load(a.r83),a.qwen_ledger_sha,a.llama_ledger_sha,a.qwen_rows,a.llama_rows)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":out["status"],"receipt_sha256":out["receipt_sha256"],"qwen_TS_read":False,"llama_outcomes_opened":False},sort_keys=True))
if __name__=="__main__":main()
