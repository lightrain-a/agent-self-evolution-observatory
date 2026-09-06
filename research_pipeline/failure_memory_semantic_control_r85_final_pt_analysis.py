#!/usr/bin/env python3
"""R85 complete P/T-only analysis for B1 R72/R73.

Reads only P_neutral and T_truthful rows from the sealed Qwen/Llama ledgers.
Qwen S_shuffled rows are explicitly filtered before any inferential/reporting
function receives the data, because the R72/R73 correctness gate remained closed.
This standalone version embeds the frozen R75 paired-ID reporting and R80 strong-
scale matching logic so analysis does not depend on extra helper-file transfer.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib
from fractions import Fraction
from typing import Any, Iterable

try:
 import failure_memory_semantic_control_r73 as r73
except ImportError:
 from . import failure_memory_semantic_control_r73 as r73

PAPER_ID="D2-PAPER-FAILURE-MEMORY-PROVENANCE"
PT_ARMS={"P_neutral","T_truthful"}
MATCH_SEED="B1-R80-STRONG-SCALE-MATCH-20260905"

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
def _sort_ids(xs:Iterable[str])->list[str]:
 vals=[str(x) for x in xs]
 try:return sorted(vals,key=lambda x:int(x))
 except Exception:return sorted(vals)

def assert_stage(rs:list[dict[str,Any]],expected:int,name:str)->None:
 if len(rs)!=expected:raise RuntimeError(f"{name}-row-count:{len(rs)}")
 if any(x.get("status")!="COMPLETE" for x in rs):raise RuntimeError(f"{name}-not-all-complete")
 if [int(x.get("stage_ordinal")) for x in rs]!=list(range(expected)):raise RuntimeError(f"{name}-ordinal-drift")

def paired_id_summary(rs:list[dict[str,Any]],left_arm:str,right_arm:str,planned_ids:list[str])->dict[str,Any]:
 by:dict[str,dict[str,dict[str,Any]]]={}
 for row in rs:
  tid=str(row["task_id"]);arm=str(row["arm"])
  if arm not in {left_arm,right_arm}:continue
  if tid in by and arm in by[tid]:raise RuntimeError(f"duplicate-arm-row:{tid}:{arm}")
  by.setdefault(tid,{})[arm]=row
 ids=_sort_ids(planned_ids)
 if set(by)!=set(ids):raise RuntimeError(f"paired-id-domain-drift:missing={_sort_ids(set(ids)-set(by))}:extra={_sort_ids(set(by)-set(ids))}")
 incomplete=[];left_success=set();right_success=set();both_success=set();left_only=set();right_only=set();both_fail=set()
 for tid in ids:
  d=by[tid]
  if set(d)!={left_arm,right_arm}:incomplete.append(tid);continue
  yl=d[left_arm].get("terminal_success");yr=d[right_arm].get("terminal_success")
  if type(yl) is not bool or type(yr) is not bool:incomplete.append(tid);continue
  if yl:left_success.add(tid)
  if yr:right_success.add(tid)
  if yl and yr:both_success.add(tid)
  elif yl and not yr:left_only.add(tid)
  elif yr and not yl:right_only.add(tid)
  else:both_fail.add(tid)
 complete_n=len(ids)-len(incomplete);union=left_success|right_success;inter=left_success&right_success
 subset=None
 if not incomplete:
  if left_success==right_success:subset="equal"
  elif left_success<right_success:subset=f"{left_arm}_strict_subset_of_{right_arm}"
  elif right_success<left_success:subset=f"{right_arm}_strict_subset_of_{left_arm}"
  else:subset="neither_subset"
 return {"left_arm":left_arm,"right_arm":right_arm,"planned_pairs":len(ids),"complete_pairs":complete_n,"left_success_count":len(left_success),"right_success_count":len(right_success),"net_success_count_difference_right_minus_left":len(right_success)-len(left_success),"both_success_count":len(both_success),"left_only_success_count":len(left_only),"right_only_success_count":len(right_only),"both_fail_count":len(both_fail),"left_success_task_ids":_sort_ids(left_success),"right_success_task_ids":_sort_ids(right_success),"both_success_task_ids":_sort_ids(both_success),"left_only_success_task_ids":_sort_ids(left_only),"right_only_success_task_ids":_sort_ids(right_only),"both_fail_task_ids":_sort_ids(both_fail),"discordant_task_ids":_sort_ids(left_only|right_only),"incomplete_task_ids":_sort_ids(incomplete),"success_set_intersection_count":len(inter),"success_set_union_count":len(union),"success_set_jaccard":len(inter)/len(union) if union else 1.0,"outcome_agreement_fraction":(len(both_success)+len(both_fail))/complete_n if complete_n else None,"outcome_discordance_fraction":(len(left_only)+len(right_only))/complete_n if complete_n else None,"same_success_task_set":left_success==right_success if not incomplete else None,"success_set_subset_relation":subset,"interpretation":"Net success-count difference and task-level success substitution are distinct quantities; a zero net difference can coexist with many discordant task IDs."}

def cross_executor_success_overlap(a_rows:list[dict[str,Any]],b_rows:list[dict[str,Any]],arm:str)->dict[str,Any]:
 def s(rs):return {str(r["task_id"]) for r in rs if str(r.get("arm"))==arm and r.get("terminal_success") is True}
 a,b=s(a_rows),s(b_rows);inter=a&b;union=a|b
 return {"arm":arm,"executor_a":"Qwen2.5-7B-Instruct","executor_b":"Meta-Llama-3.1-8B-Instruct","executor_a_success_count":len(a),"executor_b_success_count":len(b),"both_executor_success_task_ids":_sort_ids(inter),"executor_a_only_success_task_ids":_sort_ids(a-b),"executor_b_only_success_task_ids":_sort_ids(b-a),"success_set_jaccard":len(inter)/len(union) if union else 1.0,"inferential_role":"descriptive_only_no_pooling"}

def feature(row:dict[str,Any])->dict[str,Any]:
 sel=list(row.get("selected") or []);sig=list(row.get("cluster_signature") or [])
 return {"selected_count":len(sel),"success_count":sum(int(bool(x.get("source_outcome_success"))) for x in sel),"failure_count":sum(int(not bool(x.get("source_outcome_success"))) for x in sel),"cluster_signature":sig,"cluster_signature_count":len(sig),"instruction_utf8_bytes":len(str(row.get("task_instruction") or "").encode("utf-8"))}
def jaccard_distance(a:list[str],b:list[str])->Fraction:
 A=set(a);B=set(b);u=len(A|B);return Fraction(u-len(A&B),u or 1)
def tie(did:str,cid:str)->str:return hashlib.sha256(f"{MATCH_SEED}|{did}|{cid}".encode()).hexdigest()
def distance(drow:dict[str,Any],crow:dict[str,Any])->tuple[Any,...]:
 d=feature(drow);c=feature(crow)
 return (abs(d["selected_count"]-c["selected_count"]),abs(d["success_count"]-c["success_count"]),jaccard_distance(d["cluster_signature"],c["cluster_signature"]),abs(d["cluster_signature_count"]-c["cluster_signature_count"]),abs(d["instruction_utf8_bytes"]-c["instruction_utf8_bytes"]),tie(str(drow["validation_task_id"]),str(crow["validation_task_id"])))
def distance_json(drow:dict[str,Any],crow:dict[str,Any])->dict[str,Any]:
 x=distance(drow,crow);j=x[2];return {"selected_count_absdiff":x[0],"success_count_absdiff":x[1],"skill_jaccard_distance":{"numerator":j.numerator,"denominator":j.denominator},"skill_count_absdiff":x[3],"instruction_utf8_bytes_absdiff":x[4],"tie_sha256":x[5]}
def classify(qrows:list[dict[str,Any]],lrows:list[dict[str,Any]],ids:list[str])->tuple[list[str],list[str]]:
 def armmap(rs):
  z={}
  for r in rs:z.setdefault(str(r.get("task_id")),{})[str(r.get("arm"))]=r
  return z
 q=armmap(qrows);l=armmap(lrows);discord=[];controls=[]
 for tid in ids:
  states=[]
  for by in [q,l]:
   p=by.get(tid,{}).get("P_neutral");t=by.get(tid,{}).get("T_truthful")
   if not p or not t or type(p.get("terminal_success")) is not bool or type(t.get("terminal_success")) is not bool:raise RuntimeError(f"R80-scale-panel-requires-complete-P-T-classification:{tid}")
   states.append(bool(p["terminal_success"])!=bool(t["terminal_success"]))
  if any(states):discord.append(tid)
  else:controls.append(tid)
 return discord,controls
def select_controls(panel:dict[str,Any],discordant:list[str],controls:list[str])->list[dict[str,Any]]:
 by={str(r["validation_task_id"]):r for r in panel.get("records") or []};order=[str(x) for x in panel.get("representative_ids") or []];chosen=[];available=set(controls)
 if len(discordant)>len(controls):raise RuntimeError("R80-insufficient-concordant-controls")
 for did in [x for x in order if x in set(discordant)]:
  cid=sorted(available,key=lambda x:distance(by[did],by[x]))[0];available.remove(cid);chosen.append({"discordant_task_id":did,"matched_control_task_id":cid,"discordant_features":feature(by[did]),"control_features":feature(by[cid]),"distance":distance_json(by[did],by[cid])})
 return chosen

def direction_label(stats:dict[str,Any])->str:
 d=int(stats.get("direction") or 0);return "T_GREATER_THAN_P" if d>0 else ("T_LESS_THAN_P" if d<0 else "ZERO_NET_DIFFERENCE")
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
 if any(str(x.get("arm"))=="S_shuffled" for x in q):raise RuntimeError("R85-S-row-leak")
 ids=[str(x) for x in panel.get("representative_ids") or []]
 if len(ids)!=66:raise RuntimeError("R85-panel-cardinality-drift")
 qstats=r73.contrast(q,ids,"T_truthful","P_neutral");lstats=r73.contrast(l,ids,"T_truthful","P_neutral")
 qids=paired_id_summary(q,"P_neutral","T_truthful",ids);lids=paired_id_summary(l,"P_neutral","T_truthful",ids)
 old=r83.get("Qwen_primary_T_minus_P") or {}
 for key in ["planned_pairs","complete_pairs","technical_missing_pairs","paired_risk_difference_complete_pairs","left_only_success","right_only_success","discordant_pairs","exact_two_sided_signflip_p","effect_detected","direction"]:
  if qstats.get(key)!=old.get(key):raise RuntimeError(f"R85-Qwen-R83-drift:{key}")
 discordant,controls=classify(q,l,ids);matches=select_controls(panel,discordant,controls) if discordant else []
 strong_panel=[]
 for m in matches:strong_panel.extend([m["discordant_task_id"],m["matched_control_task_id"]])
 strong_panel=list(dict.fromkeys(strong_panel))
 state=final_state(qstats,lstats)
 out={"schema_version":"1.0","paper_id":PAPER_ID,"receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R85-FINAL-PT-ONLY-ANALYSIS","recorded_date":"2026-09-06","status":"R85_FINAL_PT_ONLY_ANALYSIS_COMPLETE_QWEN_TS_REMAINS_SEALED","role":"COMPLETE_321_STAGE_SEAL_PT_ONLY_CAUSAL_REPORT","bindings":{"protocol_receipt_sha256":protocol["receipt_sha256"],"r80_scale_freeze_receipt_sha256":r80freeze["receipt_sha256"],"r83_qwen_interim_receipt_sha256":r83["receipt_sha256"],"r84_analysis_authority_receipt_sha256":auth["receipt_sha256"],"qwen_terminal_ledger_sha256":sha(a.qwen_ledger),"llama_terminal_ledger_sha256":sha(a.llama_ledger)},"stage_seal":{"Qwen":{"planned_rows":189,"complete_rows":189,"technical_missing":0,"exit_code":0},"Llama":{"planned_rows":132,"complete_rows":132,"technical_missing":0,"exit_code":0},"total_planned":321,"total_complete":321},"Qwen_primary_T_minus_P":qstats,"Qwen_primary_paired_id_reporting":qids,"Qwen_primary_state":"EFFECT_DETECTED" if qstats["effect_detected"] else "NO_EFFECT_DETECTED","Qwen_direction":direction_label(qstats),"Llama_replication_T_minus_P":lstats,"Llama_replication_paired_id_reporting":lids,"Llama_state":"EFFECT_DETECTED" if lstats["effect_detected"] else "NO_EFFECT_DETECTED","Llama_direction":direction_label(lstats),"cross_executor_success_set_overlap":{"P_neutral":cross_executor_success_overlap(q,l,"P_neutral"),"T_truthful":cross_executor_success_overlap(q,l,"T_truthful")},"cross_model_pooling":False,"final_PT_state":state,"Qwen_gatekept_T_minus_S":{"gate":"NOT_OPENED_BY_FROZEN_R72_R73_PRIMARY_GATE","stats":None,"paired_id_reporting":None,"S_rows_read_by_R85":False},"R80_strong_scale_trigger":{"D":len(discordant),"discordant_task_ids":discordant,"concordant_control_pool_size":len(controls),"matched_pairs":matches,"strong_panel_task_ids":strong_panel,"planned_strong_trajectories":4*len(discordant),"triggered":bool(discordant),"execution_authorized":False,"model_download_authorized":False,"strong_model_repository":r80freeze["strong_model"]["repository"],"strong_model_revision":r80freeze["strong_model"]["revision"]},"interpretation_rules":{"NO_EFFECT_DETECTED":"no resolved truthful-information increment; not equivalence, not proof of zero, not provenance irrelevance","task_substitution":"equal aggregate success can coexist with discordant task identities; report both","executor_heterogeneity":"differences across Qwen/Llama are descriptive unless independently detected under each frozen contrast","strong_scale":"external-validity diagnostic only; cannot rewrite R72/R73 primary claim"},"paper_claim_change_authorized":False,"strong_model_execution_authorized":False,"scientific_authority":False,"experiment_authority":False,"gpu_authority":False}
 out["receipt_sha256"]=digest(out);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({"status":out["status"],"receipt_sha256":out["receipt_sha256"],"final_PT_state":state,"D":len(discordant),"qwen_TS_read":False},sort_keys=True))
if __name__=="__main__":main()
