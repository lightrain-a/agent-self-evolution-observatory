#!/usr/bin/env python3
"""R80 outcome-blind freeze for the optional B1 strong-executor scale check.

This module freezes the strong-model identity and the deterministic matched-control
selection rule before any R72/R73 outcome is observed.  It does not execute a
model and grants no execution authority.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib
from fractions import Fraction
from typing import Any

PAPER_ID="D2-PAPER-FAILURE-MEMORY-PROVENANCE"
MODEL_REPO="Qwen/Qwen2.5-32B-Instruct"
MODEL_REVISION="c53f764956643a675cfff8ad85b3c9e9b3029e06"
MATCH_SEED="B1-R80-STRONG-SCALE-MATCH-20260905"


def canonical(v:Any)->str:return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"),default=str)
def digest(v:Any)->str:return hashlib.sha256(canonical(v).encode()).hexdigest()
def load(p:pathlib.Path)->dict[str,Any]:
 v=json.loads(p.read_text(encoding="utf-8"))
 if not isinstance(v,dict):raise RuntimeError(f"not-object:{p}")
 return v
def valid(v:dict[str,Any])->bool:return isinstance(v.get("receipt_sha256"),str) and v["receipt_sha256"]==digest({k:x for k,x in v.items() if k!="receipt_sha256"})

def feature(row:dict[str,Any])->dict[str,Any]:
 sel=list(row.get("selected") or []);sig=list(row.get("cluster_signature") or [])
 return {
  "selected_count":len(sel),
  "success_count":sum(int(bool(x.get("source_outcome_success"))) for x in sel),
  "failure_count":sum(int(not bool(x.get("source_outcome_success"))) for x in sel),
  "cluster_signature":sig,
  "cluster_signature_count":len(sig),
  "instruction_utf8_bytes":len(str(row.get("task_instruction") or "").encode("utf-8")),
 }

def jaccard_distance(a:list[str],b:list[str])->Fraction:
 A=set(a);B=set(b);u=len(A|B)
 return Fraction(u-len(A&B),u or 1)

def tie(did:str,cid:str)->str:return hashlib.sha256(f"{MATCH_SEED}|{did}|{cid}".encode()).hexdigest()
def distance(drow:dict[str,Any],crow:dict[str,Any])->tuple[Any,...]:
 d=feature(drow);c=feature(crow)
 return (
  abs(d["selected_count"]-c["selected_count"]),
  abs(d["success_count"]-c["success_count"]),
  jaccard_distance(d["cluster_signature"],c["cluster_signature"]),
  abs(d["cluster_signature_count"]-c["cluster_signature_count"]),
  abs(d["instruction_utf8_bytes"]-c["instruction_utf8_bytes"]),
  tie(str(drow["validation_task_id"]),str(crow["validation_task_id"])),
 )
def distance_json(drow:dict[str,Any],crow:dict[str,Any])->dict[str,Any]:
 x=distance(drow,crow);j=x[2]
 return {"selected_count_absdiff":x[0],"success_count_absdiff":x[1],"skill_jaccard_distance":{"numerator":j.numerator,"denominator":j.denominator},"skill_count_absdiff":x[3],"instruction_utf8_bytes_absdiff":x[4],"tie_sha256":x[5]}

def classify(qrows:list[dict[str,Any]],lrows:list[dict[str,Any]],ids:list[str])->tuple[list[str],list[str]]:
 def armmap(rows):
  z={}
  for r in rows:z.setdefault(str(r.get("task_id")),{})[str(r.get("arm"))]=r
  return z
 q=armmap(qrows);l=armmap(lrows);discord=[];controls=[]
 for tid in ids:
  states=[]
  for by in [q,l]:
   p=by.get(tid,{}).get("P_neutral");t=by.get(tid,{}).get("T_truthful")
   if not p or not t or type(p.get("terminal_success")) is not bool or type(t.get("terminal_success")) is not bool:
    raise RuntimeError(f"R80-scale-panel-requires-complete-P-T-classification:{tid}")
   states.append(bool(p["terminal_success"])!=bool(t["terminal_success"]))
  if any(states):discord.append(tid)
  elif not any(states):controls.append(tid)
 return discord,controls

def select_controls(panel:dict[str,Any],discordant:list[str],controls:list[str])->list[dict[str,Any]]:
 by={str(r["validation_task_id"]):r for r in panel.get("records") or []};order=[str(x) for x in panel.get("representative_ids") or []]
 if not set(discordant+controls)<=set(by):raise RuntimeError("R80-panel-id-drift")
 if len(discordant)>len(controls):raise RuntimeError("R80-insufficient-concordant-controls")
 chosen=[];available=set(controls)
 for did in [x for x in order if x in set(discordant)]:
  ranked=sorted(available,key=lambda cid:distance(by[did],by[cid]));cid=ranked[0];available.remove(cid)
  chosen.append({"discordant_task_id":did,"matched_control_task_id":cid,"discordant_features":feature(by[did]),"control_features":feature(by[cid]),"distance":distance_json(by[did],by[cid])})
 return chosen

def build_freeze(panel:dict[str,Any],protocol:dict[str,Any])->dict[str,Any]:
 out={
  "schema_version":"1.0","paper_id":PAPER_ID,"receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R80-STRONG-SCALE-OUTCOME-BLIND-FREEZE","recorded_date":"2026-09-05","status":"R80_STRONG_SCALE_MODEL_AND_MATCH_RULE_FROZEN_OUTCOME_BLIND_EXECUTION_NOT_AUTHORIZED","role":"OPTIONAL_POST_R73_EXTERNAL_VALIDITY_FREEZE",
  "bindings":{"r68_panel_receipt_sha256":panel["receipt_sha256"],"r72_protocol_receipt_sha256":protocol["receipt_sha256"],"panel_representative_ids_sha256":panel["representative_ids_sha256"]},
  "strong_model":{"repository":MODEL_REPO,"revision":MODEL_REVISION,"family":"Qwen2.5","parameter_scale":"32.5B","license":"Apache-2.0","selection_reason":"same-family scale-up from the Qwen2.5-7B primary executor; isolates capability/scale better than changing both family and scale","future_materialization_requirement":"Before any strong-model outcome, download exactly this revision and freeze a complete local file SHA256 manifest plus tokenizer/config hashes.","decoding":{"temperature":0.0,"do_sample":False,"max_new_tokens":512},"environment":"same OSInteraction task/parser/evaluator semantics as R72/R73; host may differ only after a separately validated runtime-equivalence preflight"},
  "trigger":{"classification_source":"union of P_neutral/T_truthful terminal-discordant task IDs across sealed Qwen and sealed Llama R73 stages","requires_complete_PT_classification_for_all_66_tasks_on_both_executors":True,"D_zero_action":"DO_NOT_RUN_STRONG_SCALE_CHECK","technical_missing_action":"HOLD_STRONG_SCALE_CHECK_NO_AUTOMATIC_PANEL","discordant_ids_deduplicated":True},
  "control_pool":"tasks with P/T terminal concordance on both Qwen and Llama after both R73 stage seals",
  "matching":{"without_replacement":True,"discordant_iteration_order":"frozen R68 panel order","seed":MATCH_SEED,"lexicographic_distance":["absolute selected-retrieval-count difference","absolute truthful-source-success-count difference","cluster-signature Jaccard distance","absolute cluster-signature-size difference","absolute UTF-8 instruction-byte-length difference","SHA256(B1-R80 seed|discordant_id|candidate_id) deterministic tie-break"],"uses_strong_model_outcome":False,"manual_override_allowed":False},
  "strong_stage":{"arms":["P_neutral","T_truthful"],"trajectory_count_formula":"4D = (D discordant + D matched concordant controls) x 2 arms","cross_model_pooling":False,"primary_R72_R73_claim_change_allowed":False,"S_shuffled":False},
  "authority":{"strong_model_download":False,"strong_model_execution":False,"qwen_execution":False,"llama_execution":False,"analysis":False,"PSMG":False,"L3":False,"paper_claim_change":False},
  "outcomes_observed_during_freeze":0,"scientific_authority":False,"experiment_authority":False,"gpu_authority":False,
 }
 out["receipt_sha256"]=digest(out);return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--panel",type=pathlib.Path,required=True);ap.add_argument("--protocol",type=pathlib.Path,required=True);ap.add_argument("--output",type=pathlib.Path,required=True);a=ap.parse_args();panel=load(a.panel);protocol=load(a.protocol)
 if not valid(panel) or not valid(protocol):raise RuntimeError("R80-input-receipt-invalid")
 out=build_freeze(panel,protocol);a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({"status":out["status"],"receipt_sha256":out["receipt_sha256"],"strong_model_revision":MODEL_REVISION},sort_keys=True))
if __name__=="__main__":main()
