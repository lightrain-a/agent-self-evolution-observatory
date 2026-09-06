#!/usr/bin/env python3
"""R83 Qwen-only interim analysis for B1 R72/R73.

This analysis is permitted only after the R82 non-adaptive Llama continuation
has been frozen and pushed.  It analyzes the completed Qwen stage without
changing Llama execution.  The gate-kept T-vs-S correctness contrast is not
opened unless the frozen Qwen T-vs-P primary gate detects an effect.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib
from typing import Any

try:
    from . import failure_memory_semantic_control_r73 as r73
    from . import failure_memory_paired_id_reporting_r75 as r75
except ImportError:
    import failure_memory_semantic_control_r73 as r73  # type: ignore
    import failure_memory_paired_id_reporting_r75 as r75  # type: ignore

PAPER_ID="D2-PAPER-FAILURE-MEMORY-PROVENANCE"
STATUS="R83_QWEN_STAGE_INTERIM_ANALYSIS_COMPLETE_LLAMA_STILL_FROZEN_UNEXECUTED"


def canonical(v:Any)->str:return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"),default=str)
def digest(v:Any)->str:return hashlib.sha256(canonical(v).encode()).hexdigest()
def file_sha(p:pathlib.Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:pathlib.Path)->dict[str,Any]:
    v=json.loads(p.read_text(encoding="utf-8"));
    if not isinstance(v,dict):raise RuntimeError(f"not-object:{p}")
    return v
def valid(v:dict[str,Any])->bool:return isinstance(v.get("receipt_sha256"),str) and v["receipt_sha256"]==digest({k:x for k,x in v.items() if k!="receipt_sha256"})
def rows(p:pathlib.Path)->list[dict[str,Any]]:return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def validate_inputs(protocol:dict[str,Any],panel:dict[str,Any],authority:dict[str,Any],terminal_path:pathlib.Path)->list[dict[str,Any]]:
    if not all(valid(x) for x in [protocol,panel,authority]):raise RuntimeError("R83-input-receipt-invalid")
    if authority.get("status")!="R82_QWEN_STAGE_ONLY_INTERIM_ANALYSIS_AUTHORIZED_AFTER_LLAMA_FREEZE":raise RuntimeError("R83-analysis-authority-status-drift")
    if authority.get("protocol_receipt_sha256")!=protocol.get("receipt_sha256"):raise RuntimeError("R83-protocol-binding-drift")
    a=authority.get("authority") or {}
    if a.get("analysis") is not True or any(a.get(k) for k in ["qwen_execution","llama_execution","gpu","PSMG","L3","paper_claim_change","strong_model_download","strong_model_execution"]):raise RuntimeError("R83-analysis-authority-too-broad")
    got_sha=file_sha(terminal_path)
    if got_sha!=(authority.get("bindings") or {}).get("qwen_sealed_terminal_file_sha256"):raise RuntimeError(f"R83-qwen-ledger-sha-drift:{got_sha}")
    rr=rows(terminal_path)
    sched=list(protocol["staging"]["Qwen"]["schedule"])
    if len(rr)!=189 or len(sched)!=189:raise RuntimeError(f"R83-qwen-stage-cardinality-drift:{len(rr)}:{len(sched)}")
    expected=[(int(x["stage_ordinal"]),str(x["task_id"]),str(x["arm"])) for x in sched]
    got=[(int(x["stage_ordinal"]),str(x["task_id"]),str(x["arm"])) for x in rr]
    if got!=expected:raise RuntimeError("R83-qwen-ledger-schedule-drift")
    if any(x.get("status")!="COMPLETE" for x in rr):raise RuntimeError("R83-qwen-stage-not-all-complete")
    return rr


def tp_rows_only(rr:list[dict[str,Any]])->list[dict[str,Any]]:
    return [x for x in rr if str(x.get("arm")) in {"P_neutral","T_truthful"}]


def contrast_stats(rr:list[dict[str,Any]],ids:list[str],left:str,right:str)->dict[str,Any]:
    return r73.contrast(rr,ids,left,right)


def paired_summary(rr:list[dict[str,Any]],ids:list[str],left:str,right:str)->dict[str,Any]:
    subset=[x for x in rr if str(x.get("arm")) in {left,right}]
    return r75.paired_id_summary(subset,left,right,ids)


def analyze(protocol:dict[str,Any],panel:dict[str,Any],authority:dict[str,Any],terminal_path:pathlib.Path)->dict[str,Any]:
    rr=validate_inputs(protocol,panel,authority,terminal_path)
    ids=[str(x) for x in panel["representative_ids"]]
    if len(ids)!=66:raise RuntimeError("R83-primary-id-count-drift")

    # Primary is opened first and alone.
    tp=tp_rows_only(rr)
    primary=contrast_stats(tp,ids,"T_truthful","P_neutral")
    primary_ids=paired_summary(tp,ids,"P_neutral","T_truthful")
    primary_state="EFFECT_DETECTED" if primary["effect_detected"] else "NO_EFFECT_DETECTED"

    # Only after primary gate resolution may correctness outcomes be inspected.
    correctness_gate_open=bool(primary["effect_detected"])
    if correctness_gate_open:
        mixed=[str(x) for x in protocol["units"]["mixed_provenance_ids"]]
        if len(mixed)!=57:raise RuntimeError("R83-mixed-id-count-drift")
        correctness=contrast_stats(rr,mixed,"T_truthful","S_shuffled")
        correctness_ids=paired_summary(rr,mixed,"S_shuffled","T_truthful")
        correctness_payload={"gate":"OPENED_BY_QWEN_PRIMARY_EFFECT_DETECTED","stats":correctness,"paired_id_reporting":correctness_ids}
    else:
        correctness_payload={"gate":"NOT_OPENED_BY_FROZEN_R72_R73_PRIMARY_GATE","stats":None,"paired_id_reporting":None}

    out={
      "schema_version":"1.0","paper_id":PAPER_ID,
      "receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R83-QWEN-INTERIM-ANALYSIS",
      "recorded_date":"2026-09-06","status":STATUS,
      "role":"QWEN_ONLY_INTERIM_ANALYSIS_AFTER_NONADAPTIVE_LLAMA_FREEZE_NOT_FINAL_321_ANALYSIS",
      "bindings":{"protocol_receipt_sha256":protocol["receipt_sha256"],"r82_qwen_analysis_authority_receipt_sha256":authority["receipt_sha256"],"r82_llama_nonadaptive_authority_receipt_sha256":authority["bindings"]["llama_nonadaptive_authority_receipt_sha256"],"qwen_terminal_file_sha256":file_sha(terminal_path),"llama_frozen_schedule_sha256":authority["bindings"]["llama_frozen_schedule_sha256"]},
      "Qwen_primary_T_minus_P":primary,
      "Qwen_primary_paired_id_reporting":primary_ids,
      "Qwen_primary_state":primary_state,
      "Qwen_gatekept_T_minus_S":correctness_payload,
      "interpretation_rules":{"NO_EFFECT_DETECTED":"No resolved truthful-information increment under the frozen Qwen primary gate; this is not equivalence and does not prove provenance is useless.","EFFECT_DETECTED":"Truthful-vs-neutral field treatment effect detected on Qwen; only then may T-vs-S correctness sensitivity be interpreted."},
      "Llama_execution_status":"FROZEN_NONADAPTIVE_NOT_YET_EXECUTED_AT_THIS_ANALYSIS",
      "cross_model_pooling":False,
      "changes_llama_schedule_or_model":False,
      "changes_R72_R73_primary_design":False,
      "paper_claim_change_authorized":False,
      "strong_model_execution_authorized":False,
      "scientific_authority":False,"experiment_authority":False,"gpu_authority":False,
    }
    out["receipt_sha256"]=digest(out);return out


def main():
    ap=argparse.ArgumentParser()
    for x in ["protocol","panel","authority","qwen-terminal","output"]:ap.add_argument("--"+x,type=pathlib.Path,required=True)
    a=ap.parse_args();p=load(a.protocol);panel=load(a.panel);au=load(a.authority);out=analyze(p,panel,au,a.qwen_terminal)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":out["status"],"receipt_sha256":out["receipt_sha256"],"primary_state":out["Qwen_primary_state"],"correctness_gate":out["Qwen_gatekept_T_minus_S"]["gate"]},sort_keys=True))
if __name__=="__main__":main()
