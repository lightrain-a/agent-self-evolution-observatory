#!/usr/bin/env python3
"""R68 zero-provider freeze for the fresh B1 semantic-control panel."""
from __future__ import annotations
import argparse, hashlib, json, pathlib, random
from datetime import datetime, timezone
from typing import Any, Iterable

PAPER_ID="D2-PAPER-FAILURE-MEMORY-PROVENANCE"
PREFIX="[Retrieved Memory Context]\n"; FIELD="source_outcome_success"; UNKNOWN="UNKNOWN"
ARMS=["N0_no_memory","M1_masked","P2_unknown","T3_truthful","R4_reversed"]
MODELS=["Qwen2.5-7B-Instruct","Meta-Llama-3.1-8B-Instruct"]
R54_FROZEN_SHA="fc906765f2f94b053996bef2d7a085b6a2534b0922f2929da253390d3b855b72"
R54_SELECTION_SHA="39957119208258bd0bbd7a9a613cfa3403e9693229cb9452714c655774ad071c"
PANEL_ID_SHA="7c2b84aee347faba6d369abb403eb3a25afb164b8f5c6800ba867c25d1017187"
SEED=20260904; PREFIX_N=40; PANEL_N=66
STATUS_PROTOCOL="R68_SEMANTIC_CONTROL_READY_FOR_INDEPENDENT_PREEXECUTION_REVIEW"


def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def canonical(v): return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"),default=str).encode()
def digest(v): return hashlib.sha256(canonical(v)).hexdigest()
def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open("rb") as f:
  for c in iter(lambda:f.read(8*1024*1024),b""): h.update(c)
 return h.hexdigest()
def load(p):
 v=json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
 if not isinstance(v,dict): raise RuntimeError(f"not-object:{p}")
 return v
def valid(v): return isinstance(v.get("receipt_sha256"),str) and v["receipt_sha256"]==digest({k:x for k,x in v.items() if k!="receipt_sha256"})
def ids_hash(xs:Iterable[str]): return hashlib.sha256("\n".join(str(x) for x in xs).encode()).hexdigest()


def compact_selected(row:dict[str,Any],include_content:bool=True):
 out=[]
 for i,s in enumerate(list(row.get("selected") or [])):
  tid=str(row.get("validation_task_id"))
  if s.get("eligible") is not True: raise RuntimeError(f"ineligible-selected:{tid}:{i}")
  if type(s.get("source_outcome_success")) is not bool: raise RuntimeError(f"nonboolean-outcome:{tid}:{i}")
  content=str(s.get("content") or "")
  if not content: raise RuntimeError(f"empty-content:{tid}:{i}")
  ch=hashlib.sha256(content.encode()).hexdigest()
  if s.get("content_utf8_sha256") and ch!=s["content_utf8_sha256"]: raise RuntimeError(f"content-hash-drift:{tid}:{i}")
  item={"rank":int(s.get("rank",i)),"memory_id":str(s.get("memory_id") or ""),"memory_id_sha256":str(s.get("memory_id_sha256") or ""),"source_task_id":str(s.get("source_task_id") or ""),"source_outcome_success":bool(s["source_outcome_success"]),"content_utf8_sha256":ch}
  if include_content:item["content"]=content
  out.append(item)
 if not out: raise RuntimeError(f"empty-retrieval:{row.get('validation_task_id')}")
 return out


def select_panel(frozen:dict[str,Any],old:dict[str,Any]):
 if frozen.get("paper_id")!=PAPER_ID or old.get("paper_id")!=PAPER_ID: raise RuntimeError("paper-id-drift")
 if int(frozen.get("validation_treatment_outcomes_observed") or 0)!=0 or old.get("selection_uses_validation_outcomes") is not False: raise RuntimeError("R54-not-outcome-blind")
 eligible=[r for r in list(frozen.get("rows") or []) if r.get("has_eligible_frozen_retrieval") is True]
 if len(eligible)!=106: raise RuntimeError(f"eligible-count:{len(eligible)}")
 oldids=[str(x) for x in old.get("primary_representative_ids") or []]+[str(x) for x in old.get("utilization_representative_ids") or []]
 if len(oldids)!=40 or [str(r["validation_task_id"]) for r in eligible[:40]]!=oldids: raise RuntimeError("old-40-prefix-drift")
 rem=eligible[PREFIX_N:]
 ids=[str(r["validation_task_id"]) for r in rem]
 if len(ids)!=PANEL_N or ids_hash(ids)!=PANEL_ID_SHA or set(ids)&set(oldids): raise RuntimeError("fresh-panel-drift")
 records=[]; global_pol=set(); mixed=0
 for oi,r in enumerate(rem,start=PREFIX_N):
  sel=compact_selected(r,False); pol={bool(s["source_outcome_success"]) for s in sel}; global_pol|=pol; mixed+=int(pol=={False,True})
  ins=str(r.get("task_instruction") or "")
  records.append({"r54_eligible_order_index":oi,"validation_task_id":str(r["validation_task_id"]),"cluster_signature":r.get("signature"),"cluster_members":list(r.get("members") or []),"task_instruction":ins,"task_instruction_utf8_sha256":hashlib.sha256(ins.encode()).hexdigest(),"selected":sel,"selected_count":len(sel),"selected_polarities":sorted("success" if p else "failure" for p in pol),"selected_content_sequence_sha256":digest([s["content_utf8_sha256"] for s in sel]),"selected_source_outcome_sequence_sha256":digest([s["source_outcome_success"] for s in sel])})
 if global_pol!={False,True}: raise RuntimeError("panel-polarity-drift")
 out={"schema_version":"1.0","paper_id":PAPER_ID,"role":"R68_FRESH_UNEXPOSED_SEMANTIC_CONTROL_PANEL","recorded_at":now(),"selection_basis":"all R54 outcome-blind eligible rows after the exact historical 32-primary + 8-utilization prefix; no new ranking, cutoff tuning, replacement, or outcome filtering","r54_eligible_count":106,"historical_exposed_prefix_count":40,"fresh_unexposed_panel_count":66,"representative_ids":ids,"representative_ids_sha256":ids_hash(ids),"records":records,"global_source_outcome_polarities":["failure","success"],"mixed_polarity_task_count":mixed,"prior_primary_or_utilization_overlap_count":0,"panel_selection_uses_new_outcomes":False,"panel_treatment_outcomes_observed_before_freeze":0,"scientific_authority":False,"experiment_authority":False}
 out["receipt_sha256"]=digest(out); return out


def visible_rows(selected,mode):
 out=[]
 for i,s in enumerate(selected):
  b={"position":i,"content":str(s["content"])}
  if mode=="masked": out.append(b)
  elif mode=="unknown": out.append({**b,FIELD:UNKNOWN})
  elif mode=="truthful": out.append({**b,FIELD:bool(s["source_outcome_success"])})
  elif mode=="reversed": out.append({**b,FIELD:not bool(s["source_outcome_success"])})
  else: raise ValueError(mode)
 return out


def render_arms(record):
 sel=list(record["selected"]); m=visible_rows(sel,"masked"); u=visible_rows(sel,"unknown"); t=visible_rows(sel,"truthful"); r=visible_rows(sel,"reversed")
 core=lambda xs:[{"position":x["position"],"content":x["content"]} for x in xs]
 if not(core(m)==core(u)==core(t)==core(r)): raise RuntimeError("content-drift")
 if any(set(a)!=set(b) or set(b)!=set(c) for a,b,c in zip(u,t,r)): raise RuntimeError("format-drift")
 for s,a,b,c in zip(sel,t,r,u):
  if a[FIELD] is not bool(s["source_outcome_success"]) or b[FIELD] is bool(s["source_outcome_success"]) or c[FIELD]!=UNKNOWN: raise RuntimeError("semantic-field-drift")
 enc=lambda xs:PREFIX+json.dumps(xs,ensure_ascii=False,sort_keys=True,separators=(",",":"))
 return {"N0_no_memory":"","M1_masked":enc(m),"P2_unknown":enc(u),"T3_truthful":enc(t),"R4_reversed":enc(r)}


def arm_order(model,tid):
 rng=random.Random(int(hashlib.sha256(f"B1-R68-SEMCTRL|{SEED}|{model}|{tid}".encode()).hexdigest()[:16],16)); a=list(ARMS); rng.shuffle(a); return a

def build_audit(panel,frozen):
 rows=[];by={str(r["validation_task_id"]):r for r in frozen["rows"]}
 for rec in panel["records"]:
  full={"validation_task_id":rec["validation_task_id"],"selected":compact_selected(by[rec["validation_task_id"]],True)};ctx=render_arms(full);rows.append({"task_id":rec["validation_task_id"],"context_sha256":{a:hashlib.sha256(ctx[a].encode()).hexdigest() for a in ARMS},"content_sequence_sha256":rec["selected_content_sequence_sha256"],"outcome_sequence_sha256":rec["selected_source_outcome_sequence_sha256"]})
 out={"schema_version":"1.0","paper_id":PAPER_ID,"role":"R68_FIVE_ARM_RENDERER_STATIC_AUDIT","recorded_at":now(),"panel_receipt_sha256":panel["receipt_sha256"],"units":len(rows),"arms":ARMS,"checks":{"no_memory_context_empty":True,"masked_omits_explicit_field":True,"unknown_truthful_reversed_share_field_key_and_row_structure":True,"truthful_uses_bound_boolean":True,"reversed_is_exact_boolean_complement":True,"M_P_T_R_preserve_retrieval_membership_order_and_content":True,"audit_only_ids_scores_hidden_from_executor":True},"rows":rows,"new_treatment_outcomes_observed":0,"external_provider_calls":0,"scientific_authority":False,"experiment_authority":False};out["receipt_sha256"]=digest(out);return out


def build_protocol(panel,audit,execute_sha,qwen_sha,llama_sha):
 sched=[];o=0
 for model in MODELS:
  for tid in panel["representative_ids"]:
   for arm in arm_order(model,tid): sched.append({"ordinal":o,"model":model,"task_id":tid,"arm":arm});o+=1
 out={"schema_version":"1.0","paper_id":PAPER_ID,"role":"R68_SEMANTIC_CONTROL_PROTOCOL_FROZEN_ZERO_PROVIDER","status":"R68_SEMANTIC_CONTROL_READY_FOR_INDEPENDENT_PREEXECUTION_REVIEW","recorded_at":now(),"scientific_question":"Does truthful source-outcome information add local-policy or terminal value beyond a format-matched UNKNOWN field when memory content is identical?","bindings":{"r54_frozen_retrieval_file_sha256":R54_FROZEN_SHA,"r54_old_selection_file_sha256":R54_SELECTION_SHA,"panel_receipt_sha256":panel["receipt_sha256"],"renderer_static_audit_receipt_sha256":audit["receipt_sha256"],"r68_freeze_runner_sha256":sha(pathlib.Path(__file__).resolve()),"r69_execute_runner_sha256":execute_sha,"qwen_parent_manifest_file_sha256":qwen_sha,"llama_parent_manifest_file_sha256":llama_sha},"units":{"benchmark":"MemRL/LifelongAgentBench OSInteraction validation","statistical_unit":"fresh exact sorted skill_list-signature cluster representative","count_per_executor":66,"representative_ids":panel["representative_ids"],"representative_ids_sha256":panel["representative_ids_sha256"],"historical_R56_R61_primary_or_utilization_overlap_count":0,"selection_rule":panel["selection_basis"]},"executors":{"primary":"Qwen2.5-7B-Instruct","replication":"Meta-Llama-3.1-8B-Instruct","shared_source_bank_retriever_task_renderer":True,"cross_model_pooling":False},"arms":{"N0_no_memory":"no retrieved-memory context; contextual baseline only","M1_masked":"same frozen content/order; explicit outcome field omitted","P2_unknown":"same content/order and field key; constant UNKNOWN value","T3_truthful":"same content/order and field key; truthful boolean source outcome","R4_reversed":"same content/order and field key; complemented boolean source outcome"},"baseline_logic":{"memory_content_value":"M1_masked - N0_no_memory","field_presence_prompt_surface":"P2_unknown - M1_masked","primary_semantic_information":"T3_truthful - P2_unknown","correctness_sensitivity":"T3_truthful - R4_reversed","legacy_total_explicit_field_effect":"T3_truthful - M1_masked"},"renderer":{"prefix":PREFIX,"serialization":"canonical JSON sort_keys + compact separators","field":FIELD,"unknown_sentinel":UNKNOWN,"P_T_R_identical_key_and_row_structure":True,"T_R_boolean_type_matched":True,"M_P_T_R_content_order_fixed":True},"execution":{"arms_per_unit":5,"models":2,"planned_arm_runs":660,"temperature":0.0,"fresh_OSInteraction_container_per_arm":True,"no_retrieval_rerun":True,"no_retry_after_STARTED":True,"resume_only_never_started_schedule_suffix":True,"analysis_sealed_until_all_660_terminal":True,"external_provider_calls":0},"randomization":{"seed":SEED,"algorithm":"SHA256(seed|model|task)-seeded five-arm shuffle","outcome_adaptive_randomization":False,"schedule":sched},"analysis":{"primary_executor":"Qwen2.5-7B-Instruct","executor_replication":"Meta-Llama-3.1-8B-Instruct","primary_contrast":["T3_truthful","P2_unknown"],"primary_endpoint":"paired terminal-success difference","secondary_contrasts":{"correctness":["T3_truthful","R4_reversed"],"field_presence":["P2_unknown","M1_masked"],"memory_content":["M1_masked","N0_no_memory"],"legacy_total_field":["T3_truthful","M1_masked"]},"local_policy_endpoint":"normalized first-executable-action divergence","efficiency_endpoint":"paired step-count difference","bootstrap":"95% paired percentile, 100000 resamples, seed 20260904","test":"two-sided exact paired sign test on discordant terminal pairs","sparse_discordance_audit":"Bonferroni combined 97.5% Clopper-Pearson component intervals","no_cross_model_pooling":True,"no_equivalence_claim_without_prospective_equivalence_procedure":True,"no_semantic_reasoning_claim_from_first_action_alone":True},"hard_limits":{"no_old_32_outcome_reuse_in_new_primary_statistics":True,"no_panel_replacement_or_shrinkage":True,"no_effect_inspection_before_all_660_terminal":True,"no_arm_change_after_first_exposure":True,"no_new_model_after_first_exposure":True,"no_PSMG_efficacy_claim":True,"no_L3_transport_claim":True},"preexecution_accounting":{"new_selected_unit_treatment_outcomes_observed":0,"planned_runs_executed":0,"provider_calls":0},"scientific_authority":False,"experiment_authority":False,"gpu_authority":False};out["receipt_sha256"]=digest(out);return out


def freeze(r54_path,selection_path,outdir,execute_runner_sha,qwen_manifest_sha,llama_manifest_sha):
 if sha(r54_path)!=R54_FROZEN_SHA or sha(selection_path)!=R54_SELECTION_SHA: raise RuntimeError("R54-file-hash-drift")
 f,o=load(r54_path),load(selection_path)
 if not valid(f) or not valid(o): raise RuntimeError("R54-receipt-invalid")
 panel=select_panel(f,o);audit=build_audit(panel,f);outdir.mkdir(parents=True,exist_ok=True)
 pp=outdir/"d2-failure-memory-provenance-r68-semantic-control-panel.json";ap=outdir/"d2-failure-memory-provenance-r68-semantic-control-renderer-audit.json";pp.write_text(json.dumps(panel,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");ap.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 protocol=build_protocol(panel,audit,execute_runner_sha,qwen_manifest_sha,llama_manifest_sha);protocol["bindings"].update({"panel_file_sha256":sha(pp),"renderer_static_audit_file_sha256":sha(ap)});protocol.pop("receipt_sha256",None);protocol["receipt_sha256"]=digest(protocol)
 pr=outdir/"d2-failure-memory-provenance-r68-semantic-control-protocol.json";pr.write_text(json.dumps(protocol,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 hold={"schema_version":"1.0","paper_id":PAPER_ID,"receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R68-SEMANTIC-CONTROL-EXECUTION-HOLD","recorded_at":now(),"status":"HOLD_INDEPENDENT_PREEXECUTION_REVIEW_REQUIRED","protocol_receipt_sha256":protocol["receipt_sha256"],"planned_arm_runs":660,"authority":{"semantic_control_execution":False,"qwen":False,"llama":False,"gpu":False,"PSMG":False,"L3":False,"paper_claim_change":False},"new_treatment_outcomes_observed":0,"scientific_authority":False,"experiment_authority":False,"gpu_authority":False};hold["receipt_sha256"]=digest(hold);hp=outdir/"d2-failure-memory-provenance-r68-semantic-control-execution-hold.json";hp.write_text(json.dumps(hold,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 return {"panel":pp,"audit":ap,"protocol":pr,"hold":hp}


def main():
 p=argparse.ArgumentParser();p.add_argument("--r54-frozen-retrieval",type=pathlib.Path,required=True);p.add_argument("--r54-old-selection",type=pathlib.Path,required=True);p.add_argument("--execute-runner-sha",required=True);p.add_argument("--qwen-manifest-sha",required=True);p.add_argument("--llama-manifest-sha",required=True);p.add_argument("--output-dir",type=pathlib.Path,required=True);a=p.parse_args();r=freeze(a.r54_frozen_retrieval.resolve(),a.r54_old_selection.resolve(),a.output_dir.resolve(),a.execute_runner_sha,a.qwen_manifest_sha,a.llama_manifest_sha);print(json.dumps({k:str(v) for k,v in r.items()},ensure_ascii=False,indent=2))
if __name__=="__main__":main()

