#!/usr/bin/env python3
"""R85 complete P/T-only analysis for B1 R72/R73.

Reads only P_neutral and T_truthful rows from the sealed Qwen/Llama ledgers.
Qwen S_shuffled rows are explicitly filtered before any inferential/reporting
function receives the data, because the R72/R73 correctness gate remained closed.
Also materializes the optional R80 strong-model matched panel, without granting
strong-model execution authority.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib
from typing import Any

try:
 import failure_memory_semantic_control_r73 as r73
 import failure_memory_paired_id_reporting_r75 as r75
 import failure_memory_scale_validation_r80 as r80
except ImportError:
 from . import failure_memory_semantic_control_r73 as r73
 from . import failure_memory_paired_id_reporting_r75 as r75
 from . import failure_memory_scale_validation_r80 as r80

PAPER_ID="D2-PAPER-FAILURE-MEMORY-PROVENANCE"
PT_ARMS={"P_neutral","T_truthful"}

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
def rows(p:pathlib.Path)->list[dict[str,Any]]:
 return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]
def pt_only(rs:list[dict[str,Any]])->list[dict[str,Any]]:return [x for x in rs if str(x.get("arm")) in PT_ARMS]

def assert_stage(rs:list[dict[str,Any]],expected:int,name:str)->None:
 if len(rs)!=expected:raise RuntimeError(f"{name}-row-count:{len(rs)}")
 if any(x.get("status")!="COMPLETE" for x in rs):raise RuntimeError(f"{name}-not-all-complete")
 if [int(x.get("stage_ordinal")) for x in rs]!=list(range(expected)):raise RuntimeError(f"{name}-ordinal-drift")

def direction_label(stats:dict[str,Any])->str:
 d=int(stats.get("direction") or 0)
 return "T_GREATER_THAN_P" if d>0 else ("T_LESS_THAN_P" if d<0 else "ZERO_NET_DIFFERENCE")

def final_state(q:dict[str,Any],l:dict[str,Any])->str:
 qe=bool(q.get("effect_detected"));le=bool(l.get("effect_detected"))
 if not qe and not le:return "NO_RESOLVED_PT_INCREMENT_ON_EITHER_EXECUTOR"
 if qe and le and int(q.get("direction") or 0)==int(l.get("direction") or 0):return "SAME_DIRECTION_EFFECT_DETECTED_ON_BOTH_EXECUTORS"
 if qe and not le:return "QWEN_ONLY_EFFECT_DETECTED_NO_LLAMA_REPLICATION"
 if not qe and le:return "LLAMA_ONLY_EFFECT_DETECTED_EXECUTOR_HETEROGENEITY"
 return "OPPOSITE_DIRECTION_EFFECTS_EXECUTOR_HETEROGENEITY"

def main():
 ap=argparse.ArgumentParser()
 for x in ["protocol","panel","r80","r83","authority","qwen-ledger","llama-ledger","output"]:ap.add_argument("--"+x,type=pathlib.Path,required=True)
 a=ap.parse_args();protocol,panel,r80freeze,r83,auth=map(load,[a.protocol,a.panel,a.r80,a.r83,a.authority])
 if not all(valid(x) for x in [protocol,panel,r80freeze,r83,auth]):raise RuntimeError("R85-input-receipt-invalid")
 au=auth.get("authority") or {}
 if au.get("analysis") is not True or au.get("qwen_PT_read") is not True or au.get("llama_PT_read") is not True or au.get("qwen_TS_read") is not False:raise RuntimeError("R85-authority-scope-invalid")
 if au.get("strong_model_execution") or au.get("paper_claim_change"):raise RuntimeError("R85-authority-too-broad")
 b=auth.get("bindings") or {}
 if sha(a.qwen_ledger)!=b.get("qwen_terminal_ledger_sha256") or sha(a.llama_ledger)!=b.get("llama_terminal_ledger_sha256"):raise RuntimeError("R85-stage-ledger-sha-drift")
 q_all=rows(a.qwen_ledger);l_all=rows(a.llama_ledger);assert_stage(q_all,189,"qwen");assert_stage(l_all,132,"llama")
 q=pt_only(q_all);l=pt_only(l_all)
 if len(q)!=132 or len(l)!=132:raise RuntimeError(f"R85-PT-row-count-drift:{len(q)}:{len(l)}")
 # No S row exists downstream of this point.
 if any(str(x.get("arm"))=="S_shuffled" for x in q):raise RuntimeError("R85-S-row-leak")
 ids=[str(x) for x in panel.get("representative_ids") or []]
 if len(ids)!=66:raise RuntimeError("R85-panel-cardinality-drift")
 qstats=r73.contrast(q,ids,"T_truthful","P_neutral")
 lstats=r73.contrast(l,ids,"T_truthful","P_neutral")
 qids=r75.paired_id_summary(q,"P_neutral","T_truthful",ids)
 lids=r75.paired_id_summary(l,"P_neutral","T_truthful",ids)
 # Verify recomputed Qwen primary matches the already-open R83 result.
 old=r83.get("Qwen_primary_T_minus_P") or {}
 for key in ["planned_pairs","complete_pairs","technical_missing_pairs","paired_risk_difference_complete_pairs","left_only_success","right_only_success","discordant_pairs","exact_two_sided_signflip_p","effect_detected","direction"]:
  if qstats.get(key)!=old.get(key):raise RuntimeError(f"R85-Qwen-R83-drift:{key}")
 discordant,controls=r80.classify(q,l,ids);matches=r80.select_controls(panel,discordant,controls) if discordant else []
 strong_panel=[]
 for m in matches:
  strong_panel.extend([m["discordant_task_id"],m["matched_control_task_id"]])
 strong_panel=list(dict.fromkeys(strong_panel))
 cross={
  "P_neutral":r75.cross_executor_success_overlap(q,l,"P_neutral","Qwen2.5-7B-Instruct","Meta-Llama-3.1-8B-Instruct"),
  "T_truthful":r75.cross_executor_success_overlap(q,l,"T_truthful","Qwen2.5-7B-Instruct","Meta-Llama-3.1-8B-Instruct"),
 }
 state=final_state(qstats,lstats)
 out={
  "schema_version":"1.0","paper_id":PAPER_ID,"receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R85-FINAL-PT-ONLY-ANALYSIS","recorded_date":"2026-09-06","status":"R85_FINAL_PT_ONLY_ANALYSIS_COMPLETE_QWEN_TS_REMAINS_SEALED","role":"COMPLETE_321_STAGE_SEAL_PT_ONLY_CAUSAL_REPORT",
  "bindings":{"protocol_receipt_sha256":protocol["receipt_sha256"],"r80_scale_freeze_receipt_sha256":r80freeze["receipt_sha256"],"r83_qwen_interim_receipt_sha256":r83["receipt_sha256"],"r84_analysis_authority_receipt_sha256":auth["receipt_sha256"],"qwen_terminal_ledger_sha256":sha(a.qwen_ledger),"llama_terminal_ledger_sha256":sha(a.llama_ledger)},
  "stage_seal":{"Qwen":{"planned_rows":189,"complete_rows":189,"technical_missing":0,"exit_code":0},"Llama":{"planned_rows":132,"complete_rows":132,"technical_missing":0,"exit_code":0},"total_planned":321,"total_complete":321},
  "Qwen_primary_T_minus_P":qstats,"Qwen_primary_paired_id_reporting":qids,"Qwen_primary_state":"EFFECT_DETECTED" if qstats["effect_detected"] else "NO_EFFECT_DETECTED","Qwen_direction":direction_label(qstats),
  "Llama_replication_T_minus_P":lstats,"Llama_replication_paired_id_reporting":lids,"Llama_state":"EFFECT_DETECTED" if lstats["effect_detected"] else "NO_EFFECT_DETECTED","Llama_direction":direction_label(lstats),
  "cross_executor_success_set_overlap":cross,"cross_model_pooling":False,
  "final_PT_state":state,
  "Qwen_gatekept_T_minus_S":{"gate":"NOT_OPENED_BY_FROZEN_R72_R73_PRIMARY_GATE","stats":None,"paired_id_reporting":None,"S_rows_read_by_R85":False},
  "R80_strong_scale_trigger":{"D":len(discordant),"discordant_task_ids":discordant,"concordant_control_pool_size":len(controls),"matched_pairs":matches,"strong_panel_task_ids":strong_panel,"planned_strong_trajectories":4*len(discordant),"triggered":bool(discordant),"execution_authorized":False,"model_download_authorized":False,"strong_model_repository":r80freeze["strong_model"]["repository"],"strong_model_revision":r80freeze["strong_model"]["revision"]},
  "interpretation_rules":{"NO_EFFECT_DETECTED":"no resolved truthful-information increment; not equivalence, not proof of zero, not provenance irrelevance","task_substitution":"equal aggregate success can coexist with discordant task identities; report both","executor_heterogeneity":"differences across Qwen/Llama are descriptive unless independently detected under each frozen contrast","strong_scale":"external-validity diagnostic only; cannot rewrite R72/R73 primary claim"},
  "paper_claim_change_authorized":False,"strong_model_execution_authorized":False,"scientific_authority":False,"experiment_authority":False,"gpu_authority":False,
 }
 out["receipt_sha256"]=digest(out);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({"status":out["status"],"receipt_sha256":out["receipt_sha256"],"final_PT_state":state,"D":len(discordant),"qwen_TS_read":False},sort_keys=True))
if __name__=="__main__":main()
