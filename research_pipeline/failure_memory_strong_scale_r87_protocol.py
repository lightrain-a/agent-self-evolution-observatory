#!/usr/bin/env python3
"""R87 zero-execution protocol for the triggered 12-run B1 strong-scale check.

R85 mechanically triggered D=3 under the pre-outcome R80 rule.  R87 freezes the
six-task strong panel, deterministic within-task P/T arm order, runtime-equivalence
requirements, and descriptive interpretation before any strong-model outcome.
It grants no model download or execution authority.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib
from typing import Any

PAPER_ID="D2-PAPER-FAILURE-MEMORY-PROVENANCE"
SEED="B1-R87-STRONG-PT-ORDER-20260906"
EXPECTED_PANEL=["338","185","494","148","376","390"]

def canonical(v:Any)->str:return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"),default=str)
def digest(v:Any)->str:return hashlib.sha256(canonical(v).encode()).hexdigest()
def load(p:pathlib.Path)->dict[str,Any]:
 v=json.loads(p.read_text(encoding="utf-8"));
 if not isinstance(v,dict):raise RuntimeError(f"not-object:{p}")
 return v
def valid(v:dict[str,Any])->bool:return isinstance(v.get("receipt_sha256"),str) and v["receipt_sha256"]==digest({k:x for k,x in v.items() if k!="receipt_sha256"})
def arm_order(tid:str)->list[str]:
 h=hashlib.sha256(f"{SEED}|{tid}".encode()).digest()[0]
 return ["P_neutral","T_truthful"] if h%2==0 else ["T_truthful","P_neutral"]

def build(r80:dict[str,Any],r85:dict[str,Any],r86:dict[str,Any],panel:dict[str,Any],protocol:dict[str,Any])->dict[str,Any]:
 if not all(valid(x) for x in [r80,r85,r86,panel,protocol]):raise RuntimeError("R87-input-receipt-invalid")
 st=r85.get("R80_strong_scale_trigger") or {}
 if st.get("D")!=3 or st.get("strong_panel_task_ids")!=EXPECTED_PANEL or not st.get("triggered"):raise RuntimeError("R87-trigger-drift")
 if r86.get("authority",{}).get("strong_model_execution") is not False:raise RuntimeError("R87-R86-execution-must-remain-closed")
 if r80["strong_model"]["repository"]!="Qwen/Qwen2.5-32B-Instruct" or r80["strong_model"]["revision"]!="c53f764956643a675cfff8ad85b3c9e9b3029e06":raise RuntimeError("R87-model-drift")
 by={str(x["validation_task_id"]):x for x in panel.get("records") or []}
 if not set(EXPECTED_PANEL)<=set(by):raise RuntimeError("R87-panel-task-missing")
 schedule=[];ordinal=0
 for tid in EXPECTED_PANEL:
  for arm in arm_order(tid):
   schedule.append({"stage_ordinal":ordinal,"task_id":tid,"arm":arm,"task_instruction_utf8_sha256":by[tid]["task_instruction_utf8_sha256"],"selected_content_sequence_sha256":by[tid]["selected_content_sequence_sha256"]});ordinal+=1
 pairs={str(x["discordant_task_id"]):str(x["matched_control_task_id"]) for x in st["matched_pairs"]}
 out={
  "schema_version":"1.0","paper_id":PAPER_ID,"receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R87-STRONG-SCALE-12RUN-PROTOCOL","recorded_date":"2026-09-06","status":"R87_STRONG_SCALE_PROTOCOL_FROZEN_EXECUTION_CLOSED","role":"POST_R85_TRIGGERED_EXTERNAL_VALIDITY_DIAGNOSTIC_PROTOCOL",
  "bindings":{"r80_scale_freeze_receipt_sha256":r80["receipt_sha256"],"r85_final_pt_receipt_sha256":r85["receipt_sha256"],"r86_materialization_authority_receipt_sha256":r86["receipt_sha256"],"r68_panel_receipt_sha256":panel["receipt_sha256"],"r72_protocol_receipt_sha256":protocol["receipt_sha256"]},
  "scientific_scope":{"question":"Do the three P/T terminal-discordant cases observed on the frozen 7B/8B executors remain P/T-discordant under a substantially stronger same-family Qwen2.5 executor?","inferential_role":"targeted external-validity / capability-boundary diagnostic only","population_effect_estimation":False,"cross_model_pooling":False,"primary_R72_R73_claim_change_allowed":False},
  "model":{"repository":r80["strong_model"]["repository"],"revision":r80["strong_model"]["revision"],"family":"Qwen2.5","parameter_scale":"32.5B","decoding":{"temperature":0.0,"do_sample":False,"max_new_tokens":512},"required_precision":"same released checkpoint dtype; no quantization","materialization_receipt_required_before_execution":True},
  "runtime":{"preferred_host":"222.20.126.231","reason":"same A100/OSInteraction runtime host as the frozen R72/R73 primary stages; minimizes host/runtime variation","clean_memrl_revision":"c1b322ca43de36ddf64c6712f89d0095bfc35ce0","docker_image_id":"sha256:02c5cb67fff7bfddda09ca63e5318628d02d943767e6cd59069ece755253f036","renderer":"reuse R72 P_neutral/T_truthful rendering byte-for-byte","fresh_container_per_arm":True,"no_rerun_after_treatment_exposure":True,"runtime_equivalence_preflight_required":True},
  "panel":{"D":3,"discordant_task_ids":["338","494","376"],"matched_controls":pairs,"task_ids":EXPECTED_PANEL,"task_count":6,"arms":["P_neutral","T_truthful"],"trajectory_count":12,"arm_order_seed":SEED,"schedule":schedule,"schedule_sha256":digest(schedule)},
  "analysis":{"open_only_after_12_terminal_rows":True,"primary_readout":"P/T terminal discordance persistence for each of Tasks 338, 494, 376","control_readout":"P/T terminal discordance among matched controls 185, 148, 390","first_action_and_step_diagnostics":"descriptive_only","interpretation":{"discordant_cases_all_concordant_and_controls_concordant":"consistent with the observed 7B/8B flips being capability/recovery-boundary sensitive at this stronger executor; not proof that larger models are generally provenance-invariant","one_or_more_discordant_cases_persist_and_controls_concordant":"provenance-sensitive terminal branching persists on at least one case at 32B scale","matched_control_discordance_present":"strong-model background P/T instability is nonzero on matched controls; targeted persistence interpretation is weakened/inconclusive"}},
  "authority":{"strong_model_download":False,"strong_model_execution":False,"analysis":False,"gpu":False,"qwen_execution":False,"llama_execution":False,"PSMG":False,"L3":False,"paper_claim_change":False},
  "strong_model_outcomes_observed_during_freeze":0,"scientific_authority":False,"experiment_authority":False,"gpu_authority":False,
 }
 out["receipt_sha256"]=digest(out);return out

def main():
 ap=argparse.ArgumentParser()
 for x in ["r80","r85","r86","panel","protocol","output"]:ap.add_argument("--"+x,type=pathlib.Path,required=True)
 a=ap.parse_args();out=build(load(a.r80),load(a.r85),load(a.r86),load(a.panel),load(a.protocol));a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({"status":out["status"],"receipt_sha256":out["receipt_sha256"],"schedule_sha256":out["panel"]["schedule_sha256"],"execution":False},sort_keys=True))
if __name__=="__main__":main()
