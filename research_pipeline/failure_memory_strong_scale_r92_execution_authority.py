#!/usr/bin/env python3
"""R92 narrow 12-run execution authority for B1 strong-scale.

Requires the pre-outcome R87 protocol, exact R89 model receipt, R90 runtime
manifest, and R91 zero-benchmark-call preflight PASS.  It authorizes only the
12 frozen P/T trajectories and leaves analysis / paper-claim change closed.
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

def build(r87:dict[str,Any],r89:dict[str,Any],manifest:dict[str,Any],preflight:dict[str,Any])->dict[str,Any]:
 if not all(valid(x) for x in [r87,r89,manifest,preflight]):raise RuntimeError("R92-input-receipt-invalid")
 if r87.get("status")!="R87_STRONG_SCALE_PROTOCOL_FROZEN_EXECUTION_CLOSED":raise RuntimeError("R92-R87-status")
 if r89.get("status")!="R89_QWEN25_32B_EXACT_REVISION_MATERIALIZED_HASHED_EXECUTION_STILL_CLOSED":raise RuntimeError("R92-R89-status")
 if manifest.get("status")!="R90_STRONG_RUNTIME_MANIFEST_MATERIALIZED_EXECUTION_STILL_CLOSED":raise RuntimeError("R92-manifest-status")
 if preflight.get("status")!="R91_STRONG_RUNTIME_PREFLIGHT_PASS_ZERO_BENCHMARK_CALLS":raise RuntimeError("R92-preflight-status")
 if preflight.get("benchmark_model_calls")!=0 or preflight.get("treatment_exposures")!=0:raise RuntimeError("R92-preflight-not-zero-exposure")
 b=preflight.get("bindings") or {}
 if b.get("r87_protocol_receipt_sha256")!=r87["receipt_sha256"] or b.get("r89_materialization_receipt_sha256")!=r89["receipt_sha256"] or b.get("r90_runtime_manifest_receipt_sha256")!=manifest["receipt_sha256"]:raise RuntimeError("R92-binding-drift")
 if len(r87["panel"]["schedule"])!=12 or r87["panel"]["trajectory_count"]!=12:raise RuntimeError("R92-schedule-drift")
 out={"schema_version":"1.0","paper_id":PAPER_ID,"receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R92-STRONG-SCALE-12RUN-EXECUTION-AUTHORITY","recorded_date":"2026-09-06","status":"R92_STRONG_SCALE_12RUN_EXECUTION_AUTHORIZED_ANALYSIS_CLOSED","role":"NARROW_POST_PREFLIGHT_STRONG_SCALE_EXECUTION_AUTHORITY","r87_protocol_receipt_sha256":r87["receipt_sha256"],"runtime_manifest_receipt_sha256":manifest["receipt_sha256"],"bindings":{"r89_materialization_receipt_sha256":r89["receipt_sha256"],"r91_preflight_receipt_sha256":preflight["receipt_sha256"],"schedule_sha256":r87["panel"]["schedule_sha256"]},"scope":{"task_ids":r87["panel"]["task_ids"],"trajectory_count":12,"arms":["P_neutral","T_truthful"],"no_rerun_after_treatment_exposure":True,"no_interim_outcome_inspection":True,"complete_stage_before_analysis":True},"authority":{"strong_model_execution":True,"gpu":True,"analysis":False,"paper_claim_change":False,"qwen_execution":False,"llama_execution":False,"PSMG":False,"L3":False},"scientific_authority":False,"experiment_authority":True,"gpu_authority":True};out["receipt_sha256"]=digest(out);return out

def main():
 p=argparse.ArgumentParser()
 for x in ["r87","r89","manifest","preflight","output"]:p.add_argument("--"+x,type=pathlib.Path,required=True)
 a=p.parse_args();out=build(load(a.r87),load(a.r89),load(a.manifest),load(a.preflight));a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({"status":out["status"],"receipt_sha256":out["receipt_sha256"],"trajectories":12,"analysis":False},sort_keys=True))
if __name__=="__main__":main()
