#!/usr/bin/env python3
"""R82 pre-analysis freeze for B1 R72/R73.

This script is deliberately outcome-blind with respect to the completed Qwen
stage.  It binds the sealed Qwen terminal-ledger file hash and freezes the
non-adaptive Llama continuation *before* any Qwen terminal_success value is
opened.  It also emits a Qwen-only interim-analysis authority so the user may
inspect Qwen without changing the already-frozen Llama replication.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, pathlib
from typing import Any

PAPER_ID="D2-PAPER-FAILURE-MEMORY-PROVENANCE"
CLEAN_LLAMA_SOURCE="/data/wyt/b1-r76-memrl-source-c1b322ca"
QWEN_PLANNED=189
LLAMA_PLANNED=132


def canonical(v:Any)->str:return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"),default=str)
def digest(v:Any)->str:return hashlib.sha256(canonical(v).encode()).hexdigest()
def load(p:pathlib.Path)->dict[str,Any]:
    v=json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(v,dict):raise RuntimeError(f"not-object:{p}")
    return v
def valid(v:dict[str,Any])->bool:return isinstance(v.get("receipt_sha256"),str) and v["receipt_sha256"]==digest({k:x for k,x in v.items() if k!="receipt_sha256"})
def sha(p:pathlib.Path)->str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(8*1024*1024),b""):h.update(b)
    return h.hexdigest()


def derived_llama_manifest(parent:dict[str,Any],parent_file_sha:str)->dict[str,Any]:
    m=copy.deepcopy(parent)
    old=m["execution_manifest"]["source"]["checkout"]
    m["execution_manifest"]["source"]["checkout"]=CLEAN_LLAMA_SOURCE
    m["status"]="R82_LLAMA_PATH_EQUIVALENT_EXECUTION_MANIFEST_PRE_QWEN_ANALYSIS"
    m["role"]="R72_LLAMA_EXECUTION_PATH_EQUIVALENT_NONADAPTIVE_REALIZATION"
    m["parent_manifest_receipt_sha256"]=parent["receipt_sha256"]
    m["parent_manifest_file_sha256"]=parent_file_sha
    m["path_equivalence"]={
        "only_scientific_manifest_change":"execution_manifest.source.checkout",
        "old_checkout":old,
        "new_checkout":CLEAN_LLAMA_SOURCE,
        "required_source_revision":m["execution_manifest"]["source"]["revision"],
        "required_pinned_source_file_sha256":m["execution_manifest"]["source"]["pinned_source_file_sha256"],
        "changes_model":False,"changes_task":False,"changes_renderer":False,
        "changes_retrieval":False,"changes_decoding":False,"changes_evaluator":False,
        "runtime_host_preflight_required_before_first_exposure":True,
    }
    m["created_before_qwen_terminal_outcomes_opened"]=True
    m["scientific_authority"]=False
    m["receipt_sha256"]=digest({k:v for k,v in m.items() if k!="receipt_sha256"})
    return m


def schedule_sha(protocol:dict[str,Any])->str:
    sched=list(protocol["staging"]["Llama"]["schedule"])
    if len(sched)!=LLAMA_PLANNED:raise RuntimeError(f"llama-schedule-cardinality-drift:{len(sched)}")
    return digest(sched)


def llama_authority(protocol:dict[str,Any],r74:dict[str,Any],r80:dict[str,Any],manifest:dict[str,Any],qwen_file_sha:str)->dict[str,Any]:
    out={
      "schema_version":"1.0","paper_id":PAPER_ID,
      "receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R82-LLAMA-NONADAPTIVE-EXECUTION-AUTHORITY",
      "recorded_date":"2026-09-06",
      "status":"R82_LLAMA_STAGE_NONADAPTIVE_AUTHORIZED_BEFORE_QWEN_OUTCOME_OPEN",
      "role":"LLAMA_STAGE_ONLY_EXECUTION_AUTHORITY_FROZEN_BEFORE_QWEN_INTERIM_ANALYSIS",
      "protocol_receipt_sha256":protocol["receipt_sha256"],
      "bindings":{
        "r74_design_closeout_receipt_sha256":r74["receipt_sha256"],
        "r80_scale_freeze_receipt_sha256":r80["receipt_sha256"],
        "llama_path_equivalent_manifest_receipt_sha256":manifest["receipt_sha256"],
        "qwen_sealed_terminal_file_sha256":qwen_file_sha,
        "qwen_sealed_terminal_rows":QWEN_PLANNED,
        "qwen_sealed_technical_missing":0,
        "llama_frozen_schedule_sha256":schedule_sha(protocol),
        "llama_frozen_schedule_rows":LLAMA_PLANNED,
      },
      "authority":{"qwen_execution":False,"llama_execution":True,"analysis":False,"gpu":True,"PSMG":False,"L3":False,"paper_claim_change":False,"strong_model_download":False,"strong_model_execution":False},
      "scope":{"stage":"Llama","planned_stage_trajectories":LLAMA_PLANNED,"arms":["P_neutral","T_truthful"],"schedule_is_nonadaptive_to_qwen_outcomes":True,"resume_only_under_frozen_R73_rules":True,"cross_model_pooling":False,"complete_analysis_requires_separate_successor_authority":True},
      "qwen_terminal_outcomes_opened_when_authority_created":False,
      "scientific_authority":False,"experiment_authority":True,"gpu_authority":True,
    }
    out["receipt_sha256"]=digest(out);return out


def qwen_analysis_authority(protocol:dict[str,Any],llama_auth:dict[str,Any],qwen_file_sha:str)->dict[str,Any]:
    out={
      "schema_version":"1.0","paper_id":PAPER_ID,
      "receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R82-QWEN-INTERIM-ANALYSIS-AUTHORITY",
      "recorded_date":"2026-09-06",
      "status":"R82_QWEN_STAGE_ONLY_INTERIM_ANALYSIS_AUTHORIZED_AFTER_LLAMA_FREEZE",
      "role":"QWEN_ONLY_INTERIM_ANALYSIS_WITH_NONADAPTIVE_LLAMA_CONTINUATION_ALREADY_FROZEN",
      "protocol_receipt_sha256":protocol["receipt_sha256"],
      "bindings":{"qwen_sealed_terminal_file_sha256":qwen_file_sha,"qwen_sealed_terminal_rows":QWEN_PLANNED,"qwen_sealed_technical_missing":0,"llama_nonadaptive_authority_receipt_sha256":llama_auth["receipt_sha256"],"llama_frozen_schedule_sha256":llama_auth["bindings"]["llama_frozen_schedule_sha256"]},
      "authority":{"qwen_execution":False,"llama_execution":False,"analysis":True,"gpu":False,"PSMG":False,"L3":False,"paper_claim_change":False,"strong_model_download":False,"strong_model_execution":False},
      "scope":{"analysis":"Qwen_stage_only","primary_contrast":"T_truthful-P_neutral","planned_pairs":66,"gatekept_correctness":"T_truthful-S_shuffled only if Qwen primary effect_detected under frozen R73 rule","paired_id_reporting_required":True,"no_cross_model_pooling":True,"cannot_change_llama_schedule_or_model":True,"not_final_321_analysis":True},
      "scientific_authority":False,"experiment_authority":False,"gpu_authority":False,
    }
    out["receipt_sha256"]=digest(out);return out


def main():
    ap=argparse.ArgumentParser()
    for x in ["protocol","r74","r80","llama-parent","llama-manifest-output","llama-authority-output","qwen-analysis-authority-output"]:ap.add_argument("--"+x,type=pathlib.Path,required=True)
    ap.add_argument("--qwen-sealed-terminal-file-sha256",required=True)
    a=ap.parse_args();p=load(a.protocol);r74=load(a.r74);r80=load(a.r80);lp=load(a.llama_parent)
    if not all(valid(x) for x in [p,r74,r80,lp]):raise RuntimeError("R82-input-receipt-invalid")
    if (r74.get("scientific_design") or {}).get("verdict")!="PASS_R72_ZERO_PROVIDER_DESIGN":raise RuntimeError("R82-R74-not-pass")
    if r80.get("status")!="R80_STRONG_SCALE_MODEL_AND_MATCH_RULE_FROZEN_OUTCOME_BLIND_EXECUTION_NOT_AUTHORIZED":raise RuntimeError("R82-R80-not-frozen")
    if len(a.qwen_sealed_terminal_file_sha256)!=64:raise RuntimeError("R82-qwen-file-sha-invalid")
    lm=derived_llama_manifest(lp,sha(a.llama_parent));la=llama_authority(p,r74,r80,lm,a.qwen_sealed_terminal_file_sha256);qa=qwen_analysis_authority(p,la,a.qwen_sealed_terminal_file_sha256)
    a.llama_manifest_output.write_text(json.dumps(lm,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    a.llama_authority_output.write_text(json.dumps(la,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    a.qwen_analysis_authority_output.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":"R82_PRE_QWEN_ANALYSIS_FREEZE_COMPLETE","llama_manifest_receipt_sha256":lm["receipt_sha256"],"llama_authority_receipt_sha256":la["receipt_sha256"],"qwen_analysis_authority_receipt_sha256":qa["receipt_sha256"],"llama_schedule_sha256":la["bindings"]["llama_frozen_schedule_sha256"],"qwen_outcomes_opened":False},sort_keys=True))
if __name__=="__main__":main()
