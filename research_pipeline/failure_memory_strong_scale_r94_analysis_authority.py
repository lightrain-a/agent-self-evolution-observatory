#!/usr/bin/env python3
"""R94 post-stage, pre-outcome analysis authority for B1 strong-scale.

Binds the exact 12-row terminal ledger after execution has stopped.  It checks
only row count, schedule identity, and technical completion without interpreting
terminal_success values, then authorizes the already-frozen R93 analysis.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib
from typing import Any

PAPER_ID="D2-PAPER-FAILURE-MEMORY-PROVENANCE"

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

def build(r87:dict[str,Any],r85:dict[str,Any],r92:dict[str,Any],analysis_script:pathlib.Path,ledger:pathlib.Path)->dict[str,Any]:
 if not all(valid(x) for x in [r87,r85,r92]):raise RuntimeError("R94-input-receipt-invalid")
 if r92.get("status")!="R92_STRONG_SCALE_12RUN_EXECUTION_AUTHORIZED_ANALYSIS_CLOSED":raise RuntimeError("R94-R92-status")
 rs=rows(ledger);schedule=r87["panel"]["schedule"]
 if len(rs)!=12 or len(schedule)!=12:raise RuntimeError("R94-stage-not-12")
 expected=[(int(x["stage_ordinal"]),str(x["task_id"]),str(x["arm"])) for x in schedule];got=[(int(x["stage_ordinal"]),str(x["task_id"]),str(x["arm"])) for x in rs]
 if got!=expected:raise RuntimeError("R94-schedule-drift")
 if any(x.get("status")!="COMPLETE" for x in rs):raise RuntimeError("R94-not-all-complete")
 out={"schema_version":"1.0","paper_id":PAPER_ID,"receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R94-STRONG-SCALE-ANALYSIS-AUTHORITY","recorded_date":"2026-09-06","status":"R94_STRONG_SCALE_ANALYSIS_AUTHORIZED_AFTER_12ROW_SEAL","role":"POST_STAGE_SEAL_PRE_OUTCOME_INTERPRETATION_AUTHORITY","r87_protocol_receipt_sha256":r87["receipt_sha256"],"r85_final_pt_receipt_sha256":r85["receipt_sha256"],"strong_terminal_ledger_sha256":sha(ledger),"bindings":{"r92_execution_authority_receipt_sha256":r92["receipt_sha256"],"r93_analysis_script_sha256":sha(analysis_script),"schedule_sha256":r87["panel"]["schedule_sha256"]},"stage_seal":{"rows":12,"all_status_complete":True,"schedule_exact":True},"authority":{"analysis":True,"strong_scale_analysis":True,"strong_model_execution":False,"gpu":False,"paper_claim_change":False,"qwen_execution":False,"llama_execution":False,"PSMG":False,"L3":False},"terminal_success_values_interpreted_when_created":False,"scientific_authority":False,"experiment_authority":False,"gpu_authority":False};out["receipt_sha256"]=digest(out);return out

def main():
 p=argparse.ArgumentParser()
 for x in ["r87","r85","r92","analysis-script","ledger","output"]:p.add_argument("--"+x,type=pathlib.Path,required=True)
 a=p.parse_args();out=build(load(a.r87),load(a.r85),load(a.r92),a.analysis_script,a.ledger);a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({"status":out["status"],"receipt_sha256":out["receipt_sha256"],"terminal_success_interpreted":False},sort_keys=True))
if __name__=="__main__":main()
