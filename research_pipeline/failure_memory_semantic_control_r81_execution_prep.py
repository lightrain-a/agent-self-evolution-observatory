#!/usr/bin/env python3
"""R81 pre-outcome Qwen-only execution preparation for B1 R72/R73.

Creates a path-equivalent Qwen execution manifest plus a narrowly scoped authority.
No model call is performed here.  The scientific treatment remains the frozen R72
protocol; only the dirty shared MemRL checkout path is replaced by a clean detached
worktree at the exact same source commit and pinned file hashes.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, pathlib
from typing import Any

PAPER_ID="D2-PAPER-FAILURE-MEMORY-PROVENANCE"
CLEAN_QWEN_SOURCE="/data/wyt/b1-r76-memrl-source-c1b322ca"
STATUS="R81_QWEN_STAGE_AUTHORIZED_PATH_EQUIVALENT_RUNTIME_PREOUTCOME"

def canonical(v:Any)->str:return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"),default=str)
def digest(v:Any)->str:return hashlib.sha256(canonical(v).encode()).hexdigest()
def load(p:pathlib.Path)->dict[str,Any]:
 v=json.loads(p.read_text(encoding="utf-8"));
 if not isinstance(v,dict):raise RuntimeError(f"not-object:{p}")
 return v
def valid(v:dict[str,Any])->bool:return isinstance(v.get("receipt_sha256"),str) and v["receipt_sha256"]==digest({k:x for k,x in v.items() if k!="receipt_sha256"})
def sha(p:pathlib.Path)->str:
 h=hashlib.sha256();
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()

def derived_manifest(parent:dict[str,Any],parent_file_sha:str)->dict[str,Any]:
 m=copy.deepcopy(parent);old=m["execution_manifest"]["source"]["checkout"]
 m["execution_manifest"]["source"]["checkout"]=CLEAN_QWEN_SOURCE
 m["status"]="R81_QWEN_PATH_EQUIVALENT_EXECUTION_MANIFEST_PREOUTCOME"
 m["role"]="R72_QWEN_EXECUTION_PATH_EQUIVALENT_REALIZATION"
 m["parent_manifest_receipt_sha256"]=parent["receipt_sha256"]
 m["parent_manifest_file_sha256"]=parent_file_sha
 m["path_equivalence"]={"only_scientific_manifest_change":"execution_manifest.source.checkout","old_checkout":old,"new_checkout":CLEAN_QWEN_SOURCE,"required_source_revision":m["execution_manifest"]["source"]["revision"],"required_pinned_source_file_sha256":m["execution_manifest"]["source"]["pinned_source_file_sha256"],"runtime_host_preflight_required_before_first_exposure":True,"changes_model":False,"changes_task":False,"changes_renderer":False,"changes_retrieval":False,"changes_decoding":False,"changes_evaluator":False}
 m["validation_treatment_outcomes_observed"]=0
 m["primary_confirmatory_outcomes_observed"]=0
 m["scientific_authority"]=False
 m["receipt_sha256"]=digest({k:v for k,v in m.items() if k!="receipt_sha256"})
 return m

def authority(protocol:dict[str,Any],r74:dict[str,Any],r80:dict[str,Any],manifest:dict[str,Any])->dict[str,Any]:
 a={"schema_version":"1.0","paper_id":PAPER_ID,"receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R81-QWEN-STAGE-EXECUTION-AUTHORITY","recorded_date":"2026-09-05","status":STATUS,"role":"QWEN_STAGE_ONLY_EXECUTION_AUTHORITY_AFTER_R3_DESIGN_PASS_AND_R80_PREOUTCOME_SCALE_FREEZE","protocol_receipt_sha256":protocol["receipt_sha256"],"bindings":{"r74_design_closeout_receipt_sha256":r74["receipt_sha256"],"r80_scale_freeze_receipt_sha256":r80["receipt_sha256"],"qwen_path_equivalent_manifest_receipt_sha256":manifest["receipt_sha256"],"qwen_path_equivalent_source_checkout":CLEAN_QWEN_SOURCE},"authority":{"qwen_execution":True,"llama_execution":False,"analysis":False,"gpu":True,"PSMG":False,"L3":False,"paper_claim_change":False,"strong_model_download":False,"strong_model_execution":False},"scope":{"stage":"Qwen","planned_stage_trajectories":189,"arms":["P_neutral","T_truthful","S_shuffled"],"resume_only_under_frozen_R73_rules":True,"no_interim_scientific_analysis":True,"Llama_stage_requires_separate_successor_authority":True,"complete_analysis_requires_separate_successor_authority":True},"outcomes_observed_when_authority_created":0,"scientific_authority":False,"experiment_authority":True,"gpu_authority":True}
 a["receipt_sha256"]=digest(a);return a

def main():
 ap=argparse.ArgumentParser();
 for x in ["protocol","r74","r80","qwen-parent","derived-manifest-output","authority-output"]:ap.add_argument("--"+x,type=pathlib.Path,required=True)
 a=ap.parse_args();p=load(a.protocol);r74=load(a.r74);r80=load(a.r80);parent=load(a.qwen_parent)
 if not all(valid(x) for x in [p,r74,r80,parent]):raise RuntimeError("R81-input-receipt-invalid")
 if r74.get("status")!="R74_R72_R73_DESIGN_PASS_EXECUTION_STILL_USER_GATED" or (r74.get("scientific_design") or {}).get("verdict")!="PASS_R72_ZERO_PROVIDER_DESIGN":raise RuntimeError("R81-R74-not-pass")
 if r80.get("status")!="R80_STRONG_SCALE_MODEL_AND_MATCH_RULE_FROZEN_OUTCOME_BLIND_EXECUTION_NOT_AUTHORIZED":raise RuntimeError("R81-R80-not-frozen")
 if p.get("receipt_sha256")!=(r74.get("bindings") or {}).get("r72_protocol_receipt_sha256"):raise RuntimeError("R81-protocol-R74-binding-drift")
 if (r80.get("bindings") or {}).get("r72_protocol_receipt_sha256")!=p["receipt_sha256"]:raise RuntimeError("R81-R80-protocol-binding-drift")
 mf=derived_manifest(parent,sha(a.qwen_parent));au=authority(p,r74,r80,mf)
 a.derived_manifest_output.write_text(json.dumps(mf,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 a.authority_output.write_text(json.dumps(au,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({"status":au["status"],"manifest_receipt_sha256":mf["receipt_sha256"],"authority_receipt_sha256":au["receipt_sha256"],"qwen_execution":True,"llama_execution":False,"analysis":False},sort_keys=True))
if __name__=="__main__":main()
