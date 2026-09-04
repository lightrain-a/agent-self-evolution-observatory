#!/usr/bin/env python3
"""R70 zero-provider revised semantic-control freeze for B1.

R68 proposed 660 trajectories across five arms. An independent GPT-5.6 Sol
Extra-High pre-execution review returned REDUCE_OR_REDIRECT. R70 preserves the
same 66 outcome-blind unused R54 units but freezes only the controls that buy
identification:

Qwen: P-neutral / T-truthful on all 66 + S-count-preserving shuffle on 57 mixed
Llama: P-neutral / T-truthful on all 66

Total: 321 prospective trajectories. Execution remains closed.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib, random
from datetime import datetime, timezone
from typing import Any

PAPER_ID="D2-PAPER-FAILURE-MEMORY-PROVENANCE"
PANEL_N=66; MIXED_N=57
QWEN="Qwen2.5-7B-Instruct"; LLAMA="Meta-Llama-3.1-8B-Instruct"
FIELD="source_outcome_status"; CODES={"success":"S","failure":"F","unknown":"U"}
PREFIX="[Retrieved Memory Context]\n[Source outcome codes: S=success, F=failure, U=unknown]\n"
QWEN_ARMS=["P_neutral","T_truthful","S_shuffled"]
LLAMA_ARMS=["P_neutral","T_truthful"]
R54_FROZEN_SHA="fc906765f2f94b053996bef2d7a085b6a2534b0922f2929da253390d3b855b72"
R68_PANEL_FILE_SHA="5e0a3cb743a608896b7192a73207bc0240fe1a1b9d30f23f062c9abfc2ee491d"
PANEL_IDS_SHA="7c2b84aee347faba6d369abb403eb3a25afb164b8f5c6800ba867c25d1017187"
TOKEN_AUDIT_FILE_SHA="4532df3d431ef2c7fed27c4cc1db63f2b35ffe706237f7bff97f356e5c150017"
REVIEW_FILE_SHA="3531dc2702d16a2c4acb490a488579dd8875b373e1e265b2a84a1dab430762ac"
QWEN_MANIFEST_SHA="8217d7fab3a27687560d143f1671769f004a3f1f12018c87f0b5ed31b34d2a67"
LLAMA_MANIFEST_SHA="2add9259f78d5d8a63aad10fc15c9d7cfaf7a14f58b670e61279930b79c81340"
SHUFFLE_SEED="B1-R70-SHUFFLE-20260904"; ARM_SEED="B1-R70-ARM-20260904"; BOOTSTRAP_SEED=20260904
STATUS="R70_SEMANTIC_CONTROL_R2_READY_FOR_INDEPENDENT_R2_REVIEW"


def now():return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def load(p:pathlib.Path)->dict[str,Any]:
 v=json.loads(p.read_text(encoding="utf-8"));
 if not isinstance(v,dict):raise RuntimeError(f"not-object:{p}")
 return v
def canonical(v:Any)->str:return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"),default=str)
def digest(v:Any)->str:return hashlib.sha256(canonical(v).encode()).hexdigest()
def sha(p:pathlib.Path)->str:
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(8*1024*1024),b""):h.update(b)
 return h.hexdigest()
def valid(v:dict[str,Any])->bool:return isinstance(v.get("receipt_sha256"),str) and v["receipt_sha256"]==digest({k:x for k,x in v.items() if k!="receipt_sha256"})
def ids_hash(xs:list[str])->str:return hashlib.sha256("\n".join(xs).encode()).hexdigest()

def r54_suffix(r54:dict[str,Any],panel:dict[str,Any])->list[dict[str,Any]]:
 rows=[r for r in r54.get("rows") or [] if r.get("has_eligible_frozen_retrieval") is True][40:]
 ids=[str(r["validation_task_id"]) for r in rows]
 if len(rows)!=PANEL_N or ids_hash(ids)!=PANEL_IDS_SHA or ids!=[str(x) for x in panel.get("representative_ids") or []]:raise RuntimeError("R70-panel-drift")
 return rows

def selected(row:dict[str,Any])->list[dict[str,Any]]:
 out=[s for s in row.get("selected") or [] if s.get("eligible") is True]
 if not out or any(type(s.get("source_outcome_success")) is not bool or not str(s.get("content") or "") for s in out):raise RuntimeError(f"bad-selected:{row.get('validation_task_id')}")
 return out

def truth_codes(sel:list[dict[str,Any]])->list[str]:return [CODES["success"] if s["source_outcome_success"] else CODES["failure"] for s in sel]
def shuffled_codes(tid:str,truth:list[str])->list[str]|None:
 if len(set(truth))<2:return None
 rng=random.Random(int(hashlib.sha256(f"{SHUFFLE_SEED}|{tid}".encode()).hexdigest()[:16],16));cand=truth[:]
 for _ in range(1024):
  rng.shuffle(cand)
  if cand!=truth:break
 if cand==truth or sorted(cand)!=sorted(truth):raise RuntimeError(f"shuffle-failed:{tid}")
 return cand

def render(sel:list[dict[str,Any]],codes:list[str])->str:
 rows=[{"position":i,"content":str(s["content"]),FIELD:code} for i,(s,code) in enumerate(zip(sel,codes))]
 return PREFIX+json.dumps(rows,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def render_contexts(row:dict[str,Any])->dict[str,str]:
 sel=selected(row);truth=truth_codes(sel);shuf=shuffled_codes(str(row["validation_task_id"]),truth)
 out={"P_neutral":render(sel,[CODES["unknown"]]*len(sel)),"T_truthful":render(sel,truth)}
 if shuf is not None:out["S_shuffled"]=render(sel,shuf)
 return out

def arm_order(model:str,tid:str,arms:list[str])->list[str]:
 rng=random.Random(int(hashlib.sha256(f"{ARM_SEED}|{model}|{tid}".encode()).hexdigest()[:16],16));out=list(arms);rng.shuffle(out);return out

def panel_truth_codes(rec:dict[str,Any])->list[str]:
 vals=[]
 for s in rec.get("selected") or []:
  if type(s.get("source_outcome_success")) is not bool:raise RuntimeError(f"panel-outcome-invalid:{rec.get('validation_task_id')}")
  vals.append(CODES["success"] if s["source_outcome_success"] else CODES["failure"])
 if not vals:raise RuntimeError(f"panel-selected-empty:{rec.get('validation_task_id')}")
 return vals

def build_renderer_audit(panel:dict[str,Any],token_audit:dict[str,Any])->dict[str,Any]:
 records=[];mixed=0
 for rec in panel.get("records") or []:
  tid=str(rec["validation_task_id"]);truth=panel_truth_codes(rec);shuf=shuffled_codes(tid,truth);mixed+=int(shuf is not None)
  if shuf is not None and sorted(shuf)!=sorted(truth):raise RuntimeError(f"count-not-preserved:{tid}")
  records.append({"task_id":tid,"retrieved_memory_count":len(truth),"mixed_provenance":shuf is not None,"truthful_code_sequence_sha256":digest(truth),"shuffled_code_sequence_sha256":digest(shuf) if shuf is not None else None,"selected_content_sequence_sha256":rec["selected_content_sequence_sha256"],"runtime_context_hash_bound_only_after_rebinding_original_R54":True})
 if len(records)!=PANEL_N or mixed!=MIXED_N:raise RuntimeError(f"panel-shape:{len(records)}:{mixed}")
 out={"schema_version":"1.0","paper_id":PAPER_ID,"receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R70-RENDERER-AUDIT","status":"R70_REPRESENTATION_MATCHED_P_T_S_RENDERER_AUDIT_PASS","recorded_at":now(),"bindings":{"r68_panel_receipt_sha256":panel["receipt_sha256"],"tokenizer_audit_receipt_sha256":token_audit["receipt_sha256"]},"field":FIELD,"codes":CODES,"value_type":"string","units":PANEL_N,"mixed_units":MIXED_N,"checks":{"P_T_same_schema_and_content_all_66":True,"P_T_S_same_schema_and_content_all_57_mixed":True,"S_is_nonidentity_count_preserving_within_retrieval_shuffle":True,"P_T_token_footprint_equal_under_both_executors_all_66":True,"P_T_S_token_footprint_equal_under_both_executors_all_57_mixed":True,"memory_order_and_membership_hash_bound_to_R68_panel":True,"runtime_must_rebind_original_R54_content_before_rendering":True,"no_task_outcome_observed":True},"rows":records,"scientific_authority":False,"experiment_authority":False};out["receipt_sha256"]=digest(out);return out

def build_schedule(panel:dict[str,Any])->dict[str,Any]:
 q=[];l=[];oq=0;ol=0
 for rec in panel.get("records") or []:
  tid=str(rec["validation_task_id"]);mixed=shuffled_codes(tid,panel_truth_codes(rec)) is not None;arms=["P_neutral","T_truthful"]+(["S_shuffled"] if mixed else [])
  for arm in arm_order(QWEN,tid,arms):q.append({"stage_ordinal":oq,"model":QWEN,"task_id":tid,"arm":arm});oq+=1
  for arm in arm_order(LLAMA,tid,["P_neutral","T_truthful"]):l.append({"stage_ordinal":ol,"model":LLAMA,"task_id":tid,"arm":arm});ol+=1
 if len(q)!=189 or len(l)!=132:raise RuntimeError(f"schedule-size:{len(q)}:{len(l)}")
 return {"Qwen_stage":q,"Llama_stage":l}

def freeze(*,panel_path:pathlib.Path,token_audit_path:pathlib.Path,review_path:pathlib.Path,qwen_manifest_path:pathlib.Path,llama_manifest_path:pathlib.Path,r71_runner_sha:str,outdir:pathlib.Path)->dict[str,pathlib.Path]:
 checks=[(panel_path,R68_PANEL_FILE_SHA,"panel"),(token_audit_path,TOKEN_AUDIT_FILE_SHA,"token-audit"),(review_path,REVIEW_FILE_SHA,"review"),(qwen_manifest_path,QWEN_MANIFEST_SHA,"qwen-manifest"),(llama_manifest_path,LLAMA_MANIFEST_SHA,"llama-manifest")]
 for p,h,n in checks:
  if sha(p)!=h:raise RuntimeError(f"{n}-file-hash-drift:{sha(p)}")
 panel,token_audit,review,qm,lm=map(load,[panel_path,token_audit_path,review_path,qwen_manifest_path,llama_manifest_path])
 if not all(valid(x) for x in [panel,token_audit,review,qm,lm]):raise RuntimeError("receipt-hash-invalid")
 if review.get("verdict")!="REDUCE_OR_REDIRECT" or token_audit.get("status")!="R70_P_T_S_TOKEN_FOOTPRINT_MATCH_PASS_ZERO_MODEL":raise RuntimeError("review-or-token-gate-not-pass")
 if len(panel.get("representative_ids") or [])!=PANEL_N or panel.get("representative_ids_sha256")!=PANEL_IDS_SHA:raise RuntimeError("panel-unit-drift")
 renderer=build_renderer_audit(panel,token_audit);schedule=build_schedule(panel);mixed_ids=[str(r["validation_task_id"]) for r in panel.get("records") or [] if len(set(panel_truth_codes(r)))==2]
 protocol={"schema_version":"1.0","paper_id":PAPER_ID,"receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R70-SEMANTIC-CONTROL-R2-PROTOCOL","status":STATUS,"recorded_at":now(),"role":"REVISED_ZERO_PROVIDER_SEMANTIC_CONTROL_PROTOCOL_AFTER_INDEPENDENT_REVIEW","scientific_question":"Does truthful source-outcome information change closed-loop terminal success beyond a representation- and token-footprint-matched neutral explicit-field control?","bindings":{"r54_frozen_retrieval_file_sha256":R54_FROZEN_SHA,"r68_panel_file_sha256":sha(panel_path),"r68_panel_receipt_sha256":panel["receipt_sha256"],"r70_tokenizer_audit_file_sha256":sha(token_audit_path),"r70_tokenizer_audit_receipt_sha256":token_audit["receipt_sha256"],"r70_independent_review_file_sha256":sha(review_path),"r70_independent_review_receipt_sha256":review["receipt_sha256"],"r70_renderer_audit_receipt_sha256":renderer["receipt_sha256"],"r70_freeze_runner_sha256":sha(pathlib.Path(__file__).resolve()),"r71_execute_runner_sha256":r71_runner_sha,"qwen_parent_manifest_file_sha256":sha(qwen_manifest_path),"llama_parent_manifest_file_sha256":sha(llama_manifest_path)},"units":{"count":66,"representative_ids":list(panel["representative_ids"]),"representative_ids_sha256":panel["representative_ids_sha256"],"mixed_provenance_ids":mixed_ids,"mixed_provenance_count":len(mixed_ids),"selection_rule":"exhaustive R54 outcome-blind eligible suffix eligible[40:]","historical_treatment_overlap":0},"field_control":{"field":FIELD,"value_type":"string","codes":CODES,"shared_prefix":PREFIX,"P_neutral":"all values U","T_truthful":"S/F from frozen source outcome","S_shuffled":"within-retrieval nonidentity permutation of S/F preserving exact per-prompt multiset","same_token_footprint_verified_for_both_executor_tokenizers":True},"run_matrix":{"Qwen":{"P_neutral":66,"T_truthful":66,"S_shuffled":57,"total":189},"Llama":{"P_neutral":66,"T_truthful":66,"S_shuffled":0,"total":132},"total_new_trajectories":321,"reduction_vs_rejected_R68_660":339},"staging":{"Qwen":{"schedule":schedule["Qwen_stage"],"seal":"no Qwen effect inspection until all 189 scheduled Qwen units are terminal or prospectively classified technical-missing"},"Llama":{"schedule":schedule["Llama_stage"],"design_frozen_before_Qwen_exposure":True,"commitment_to_run_independent_of_Qwen_result":True,"may_execute_after_Qwen_analysis":True,"seal":"no Llama effect inspection until all 132 Llama scheduled units are terminal or prospectively classified technical-missing"}},"analysis":{"primary":{"executor":QWEN,"contrast":"T_truthful - P_neutral","n":66,"endpoint":"paired native OSInteraction terminal success","test":"two-sided exact paired sign test alpha=0.05","intervals":["100000-resample paired percentile bootstrap","conservative sparse-discordance paired RD"],"decision":{"EFFECT_DETECTED":"two-sided exact p<0.05 AND conservative technical-missing sensitivity excludes 0 in the same direction","NO_EFFECT_DETECTED":"otherwise; does not imply equivalence, practical smallness, or prompt-format-only explanation"}},"gatekept_correctness":{"executor":QWEN,"contrast":"T_truthful - S_shuffled","n":57,"opens_confirmatory_interpretation_only_if_primary_EFFECT_DETECTED":True,"correctness_sensitive":"same-direction exact p<0.05 AND conservative technical-missing sensitivity excludes 0","otherwise":"mechanism unresolved"},"executor_replication":{"executor":LLAMA,"contrast":"T_truthful - P_neutral","n":66,"no_pooling":True,"successful_replication":"effect independently detected in same direction as Qwen primary","otherwise":"report independent estimate; no null/equivalence upgrade"},"diagnostics":{"first_executable_action":"descriptive_only","step_count":"descriptive_only","subgroups":"descriptive_only"},"multiplicity":"fixed hierarchy: Qwen T-P primary at alpha .05; Qwen T-S gate-kept at alpha .05 only after primary; Llama separately labelled executor replication; diagnostics cannot rescue primary"},"failure_policy":{"scientific_boundary":"treatment exposure, not durable STARTED","pre_exposure_infrastructure_failure":{"definition":"failure before first treatment-conditioned inference dispatch; includes task/container reset/build failures and transport failures provably before dispatch","max_total_attempts_same_unit_arm":3,"fresh_reset_each_attempt":True,"replacement":False,"all_attempts_logged":True},"post_exposure":{"native_model_or_environment_failure":"scientific outcome under native evaluator","genuine_external_technical_failure":"TECHNICAL_MISSING_INVALID; no rerun","complete_pair_primary_report":True,"missing_pair_sensitivity":"for m technical-missing pairs among N planned, paired RD worst/best bounds [(sum observed effects-m)/N,(sum observed effects+m)/N]; confirmatory conclusion must survive"}},"hard_limits":{"no_N0_no_memory":True,"no_M1_masked":True,"no_R4_reversed":True,"no_additional_SOTA_memory_baseline":True,"no_panel_shrink_or_replacement":True,"no_cross_model_pooling":True,"no_equivalence_claim":True,"no_semantic_reasoning_claim_from_first_action":True,"no_PSMG_or_L3_claim":True,"no_change_to_Llama_design_or_run_commitment_after_Qwen_open":True},"preexecution_accounting":{"new_model_trajectories":0,"task_outcomes_observed":0,"external_provider_calls":0},"scientific_authority":False,"experiment_authority":False,"gpu_authority":False};protocol["receipt_sha256"]=digest(protocol)
 outdir.mkdir(parents=True,exist_ok=True);rp=outdir/"d2-failure-memory-provenance-r70-semantic-control-r2-renderer-audit.json";pp=outdir/"d2-failure-memory-provenance-r70-semantic-control-r2-protocol.json";rp.write_text(json.dumps(renderer,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");protocol["bindings"]["r70_renderer_audit_file_sha256"]=sha(rp);protocol.pop("receipt_sha256",None);protocol["receipt_sha256"]=digest(protocol);pp.write_text(json.dumps(protocol,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 hold={"schema_version":"1.0","paper_id":PAPER_ID,"receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R70-SEMANTIC-CONTROL-R2-HOLD","recorded_at":now(),"status":"HOLD_REVISED_DESIGN_REQUIRES_INDEPENDENT_R2_REVIEW_BEFORE_EXECUTION","protocol_receipt_sha256":protocol["receipt_sha256"],"planned_trajectories":321,"authority":{"qwen_execution":False,"llama_execution":False,"gpu":False,"analysis":False,"PSMG":False,"L3":False,"paper_claim_change":False},"new_model_trajectories":0,"scientific_authority":False,"experiment_authority":False,"gpu_authority":False};hold["receipt_sha256"]=digest(hold);hp=outdir/"d2-failure-memory-provenance-r70-semantic-control-r2-execution-hold.json";hp.write_text(json.dumps(hold,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");return {"renderer":rp,"protocol":pp,"hold":hp}

def main():
 p=argparse.ArgumentParser();
 for x in ["panel","token-audit","review","qwen-manifest","llama-manifest","output-dir"]:p.add_argument("--"+x,type=pathlib.Path,required=True)
 p.add_argument("--r71-runner-sha",required=True);a=p.parse_args();res=freeze(panel_path=a.panel.resolve(),token_audit_path=a.token_audit.resolve(),review_path=a.review.resolve(),qwen_manifest_path=a.qwen_manifest.resolve(),llama_manifest_path=a.llama_manifest.resolve(),r71_runner_sha=a.r71_runner_sha,outdir=a.output_dir.resolve());print(json.dumps({k:str(v) for k,v in res.items()},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
