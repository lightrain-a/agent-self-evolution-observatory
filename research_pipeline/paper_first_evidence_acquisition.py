from __future__ import annotations

import hashlib,json,re
from datetime import datetime,timezone
from pathlib import Path
from typing import Any

PLAN_FILENAME="evidence-acquisition-plan.json"
SCHEMA_VERSION="1.0"
MAX_ACTIVE=4; MAX_DEPTH=2; MAX_UNITS=128; MAX_WALL_MIN=90; MAX_GPU_HOURS=1.0; MAX_MODEL_CALLS=256
MODES={"PRIMARY_ASSET_REUSE","FIRST_PARTY_REPLAY","FIRST_PARTY_SANDBOX","FIRST_PARTY_ROLLOUT","FIRST_PARTY_SIMULATION"}
SOURCE_MODES={"SOURCE_SPECIFIC_REQUIRED","REPRODUCIBLE_FIRST_PARTY"}
ADAPTERS={"PRIMARY_ASSET_ONLY","SUBSTRATE_PREFLIGHT_REQUIRED"}
OUTCOMES={"REDUCTION_SUPPORTED","RESIDUAL_SURVIVES","INCONCLUSIVE"}
SUBSTRATE_DISPOSITIONS={"EXISTING_HARNESS_READY","MINIMAL_HARNESS_IMPLEMENTATION_READY","SOURCE_SPECIFIC_REQUIRED","SUBSTRATE_UNAVAILABLE","BUDGET_INFEASIBLE","PROTOCOL_REPAIR_REQUIRED"}
AUTHORITY={"scientific_claim":False,"live_problem_gate":False,"paper_design":False,"method":False,"p0":False,"full_experiment":False}
POLICY={
 "reduction_pending_is_provisional_not_failed":True,
 "exploration_authority_is_separate_from_scientific_claim_authority":True,
 "first_party_evidence_may_be_acquired_before_problem_gate_pass":True,
 "first_party_evidence_must_use_independent_truth":True,
 "candidate_mechanism_cannot_define_labels_or_ground_truth":True,
 "same_information_baseline_is_mandatory":True,
 "frozen_scientific_fields_are_compiler_owned":True,
 "outcome_labels_are_compiler_owned":True,
 "execution_adapter_is_compiler_owned":True,
 "independent_evidence_contract_review_required_before_execution":True,
 "evidence_designer_cannot_self_review":True,
 "bounded_substrate_preflight_required_after_contract_review":True,
 "contract_review_clear_does_not_authorize_execution":True,
 "prior_support_receipt_is_review_context_not_automatic_veto":True,
 "support_inventory_is_one_acquisition_route_not_a_global_prerequisite":True,
 "source_specific_claims_still_require_source_specific_assets":True,
 "source_asset_dependency_may_receive_one_operationalization_recompile":True,
 "operationalization_recompile_cannot_change_frozen_prediction_or_baseline":True,
 "operationalization_recompile_requires_independent_equivalence_review":True,
 "operationalization_recompile_is_single_attempt":True,
 "new_evidence_never_auto_certifies_novelty":True,
 "residual_survival_returns_to_semantic_and_current_source_review":True,
 "bounded_evidence_execution_is_not_p0":True,
 "experiment_tree_branch_depth_is_bounded":True,
 "single_variable_repair_only_after_inconclusive":True,
 "automatic_method_training_forbidden":True,
 "second_backbone_forbidden":True,
 "hidden_outcome_retuning_forbidden":True,
 "research_memory_query_pack_required_before_evidence_design":True,
 "research_memory_query_pack_is_zero_authority":True,
 "transient_operational_memory_excluded_from_evidence_design":True,
 "research_memory_query_pack_receipt_required":True,
 "scientific_authority":False,
}

def _now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def _b(v,n=2200): return " ".join(str(v or "").split())[:n]
def _sha(v): return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def _queue(machine:dict)->list[dict]:
 if machine.get("scientific_authority") is not False: raise ValueError("machine audit must be zero-authority")
 auth=machine.get("authority") or {}
 if any(auth.get(k) is not False for k in ("paper_design","method","experiment","p0","gpu")): raise ValueError("machine audit leaked downstream authority")
 rows=[r for r in machine.get("problem_falsifier_queue") or [] if isinstance(r,dict)];seen=set()
 for r in rows:
  cid=str(r.get("candidate_id") or "").strip()
  if not cid or cid in seen: raise ValueError("problem-falsifier ids must be unique")
  seen.add(cid)
  if not all(_b(r.get(k)) for k in ("exact_prediction","strongest_same_information_baseline","cheapest_problem_falsifier")): raise ValueError(f"falsifier fields incomplete:{cid}")
 return rows

def build_provisional_evidence_plan(machine:dict,*,run_id:str="",max_active:int=MAX_ACTIVE)->dict:
 ranked=sorted(_queue(machine),key=lambda r:(len(r.get("blockers") or []),str(r.get("candidate_id") or "")))
 cap=max(0,min(int(max_active),MAX_ACTIVE));entries=[]
 for rank,r in enumerate(ranked,1):
  selected=rank<=cap
  candidate=r.get("candidate") or {}
  evidence=candidate.get("empirical_evidence") or {}
  source_refs=sorted({str((evidence.get(key) or {}).get("ref") or "") for key in ("source_a","source_b") if str((evidence.get(key) or {}).get("ref") or "").startswith("arXiv:")})
  entries.append({
   "candidate_id":str(r.get("candidate_id") or ""),"title":_b(r.get("title"),500),"discovery_lane":str(r.get("discovery_lane") or ""),"source_branch_id":str(r.get("source_branch_id") or ""),"source_refs":source_refs,
   "priority_rank":rank,"selection_basis":"fewest-unresolved-reduction-blockers-then-stable-id","design_selected":selected,
   "status":"NEEDS_BOUNDED_EVIDENCE_DESIGN" if selected else "DEFERRED_BY_ACTIVE_PORTFOLIO_BUDGET",
   "frozen_irreducible_object":_b(r.get("irreducible_object"),2400),"frozen_endpoint_headroom_requirement":_b(r.get("endpoint_headroom_requirement"),1800),"frozen_exact_prediction":_b(r.get("exact_prediction")),"frozen_same_information_baseline":_b(r.get("strongest_same_information_baseline"),1600),"frozen_falsifier_expression":_b(r.get("cheapest_problem_falsifier"),2400),
   "blockers":sorted({str(x) for x in r.get("blockers") or [] if str(x)}),"tree":{"depth":0,"parent_contract_sha256":"","repair_count":0},"design":{},"contract_sha256":"","execution_authorized":False,"scientific_authority":False,"authority":dict(AUTHORITY)})
 selected=sum(r["design_selected"] for r in entries)
 return {"schema_version":SCHEMA_VERSION,"generated_at":_now(),"run_id":run_id,"status":"EVIDENCE_DESIGN_PENDING" if selected else "NO_REDUCTION_PENDING_EVIDENCE_WORK","policy":dict(POLICY),"portfolio":{"selection":"bounded-top-k","max_active_candidates":MAX_ACTIVE,"active_candidates":selected,"experiment_tree_max_depth":MAX_DEPTH},"summary":_summary(entries),"entries":entries,"scientific_authority":False,"authority":dict(AUTHORITY)}

def _summary(entries:list[dict])->dict:
 return {
  "provisional_problem_candidates":len(entries),"design_selected":sum(r.get("design_selected") is True for r in entries),"design_pending":sum(r.get("status")=="NEEDS_BOUNDED_EVIDENCE_DESIGN" for r in entries),"design_invalid":sum(r.get("status")=="HOLD_EVIDENCE_DESIGN_INVALID" for r in entries),
  "wait_primary_asset":sum(r.get("status")=="WAIT_PRIMARY_ASSET_RELEASE" for r in entries),"operationalization_recompile_pending":sum(r.get("status")=="NEEDS_OPERATIONALIZATION_RECOMPILE" for r in entries),"operationalization_recompiled":sum(bool(r.get("operationalization_recompile")) for r in entries),"operationalization_intrinsic_source_specific":sum((r.get("operationalization_recompile_adjudication") or {}).get("verdict")=="INTRINSIC_SOURCE_SPECIFIC" for r in entries),"review_pending":sum(r.get("status")=="NEEDS_INDEPENDENT_EVIDENCE_REVIEW" for r in entries),"review_clear":sum((r.get("evidence_review") or {}).get("verdict")=="CLEAR_FOR_SUBSTRATE_PREFLIGHT" for r in entries),"review_revise":sum((r.get("evidence_review") or {}).get("verdict")=="REVISE" for r in entries),"review_blocked":sum(r.get("status")=="HOLD_EVIDENCE_REVIEW_BLOCKED" for r in entries),"substrate_preflight_pending":sum(r.get("status")=="READY_FOR_BOUNDED_SUBSTRATE_PREFLIGHT" for r in entries),"substrate_ready":sum((r.get("substrate_preflight") or {}).get("disposition")=="EXISTING_HARNESS_READY" for r in entries),"substrate_implementation_pending":sum(r.get("status")=="NEEDS_MINIMAL_HARNESS_IMPLEMENTATION" for r in entries),"harness_runtime_hold":sum(r.get("status")=="HOLD_HARNESS_RUNTIME_SUPPORT" for r in entries),"substrate_hold":sum(r.get("status") in {"HOLD_SUBSTRATE_UNAVAILABLE","HOLD_SUBSTRATE_BUDGET_INFEASIBLE"} for r in entries),"execution_ready":sum(r.get("status")=="READY_FOR_BOUNDED_EVIDENCE_ACQUISITION" for r in entries),"execution_completed":sum(bool(r.get("evidence_receipt")) for r in entries),
  "reduction_supported":sum(r.get("status")=="STOP_EXACT_REDUCTION_SUPPORTED" for r in entries),"residual_survives":sum(r.get("status")=="RETURN_TO_SEMANTIC_CURRENT_SOURCE_REVIEW" for r in entries),"inconclusive":sum(r.get("status") in {"BRANCH_REPAIR_READY","HOLD_INCONCLUSIVE_TREE_BUDGET_EXHAUSTED"} for r in entries),"branch_repair_ready":sum(r.get("status")=="BRANCH_REPAIR_READY" for r in entries),
  "deferred_by_portfolio_budget":sum(r.get("status")=="DEFERRED_BY_ACTIVE_PORTFOLIO_BUDGET" for r in entries),"paper_design_authorized":0,"method_authorized":0,"p0_authorized":0,"full_experiment_authorized":0}

def _plan_status(entries:list[dict])->str:
 s=_summary(entries)
 if s["residual_survives"]:return "EVIDENCE_RESULTS_REQUIRE_REVIEW"
 if s["branch_repair_ready"]:return "EVIDENCE_BRANCH_REPAIR_READY"
 if s["execution_ready"]:return "EVIDENCE_EXECUTION_READY"
 if s["substrate_implementation_pending"]:return "EVIDENCE_HARNESS_IMPLEMENTATION_PENDING"
 if s["substrate_preflight_pending"]:return "EVIDENCE_SUBSTRATE_PREFLIGHT_PENDING"
 if s["review_pending"]:return "EVIDENCE_REVIEW_PENDING"
 if s["operationalization_recompile_pending"]:return "EVIDENCE_OPERATIONALIZATION_RECOMPILE_PENDING"
 if s["design_pending"]:return "EVIDENCE_DESIGN_PENDING"
 if s["harness_runtime_hold"]:return "EVIDENCE_HARNESS_RUNTIME_HOLD"
 return "EVIDENCE_WAIT_OR_HOLD"

def write_provisional_evidence_plan(*,run_root:Path,machine_audit:dict|None=None)->dict:
 machine_audit=machine_audit or json.loads((run_root/"machine-audit.json").read_text(encoding="utf-8"));state=build_provisional_evidence_plan(machine_audit,run_id=run_root.name)
 (run_root/PLAN_FILENAME).write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");return state

def evidence_design_prompt(plan:dict,*,part:int=1,batch_size:int=2,research_memory_query_pack:dict|None=None)->tuple[str,list[str]]:
 selected=[r for r in plan.get("entries") or [] if isinstance(r,dict) and r.get("design_selected") is True and r.get("status") in {"NEEDS_BOUNDED_EVIDENCE_DESIGN","BRANCH_REPAIR_READY"}]
 batch=selected[:batch_size]
 if not batch: raise ValueError(f"empty bounded-evidence design batch part={part}")
 compact=[{"candidate_id":r["candidate_id"],"title":r.get("title"),"exact_prediction":r.get("frozen_exact_prediction"),"strongest_same_information_baseline":r.get("frozen_same_information_baseline"),"falsifier_expression":r.get("frozen_falsifier_expression"),"prior_support":r.get("prior_support") or {},"blockers":r.get("blockers") or [],"tree_depth":int((r.get("tree") or {}).get("depth") or 0),"required_single_variable_repair":_b((r.get("branch_repair") or {}).get("changed_variable"),1800),"required_design_revision":_b(r.get("review_feedback"),1800)} for r in batch]
 memory_pack=research_memory_query_pack or {"purpose":"EXPERIMENT_DESIGN","selected_memory_ids":[],"text":"","scientific_authority":False}
 prompt=f'''You design bounded scientific evidence acquisition for REDUCTION-PENDING paper problems. This is exploration only, not novelty certification and not method design.

For each candidate produce exactly one cheapest discriminating contract. New FIRST-PARTY evidence is allowed when the phenomenon can be independently reproduced. prior_support records the old source-asset audit: it is context, not an automatic veto. You must explicitly avoid substituting a synthetic proxy when prior_support says the frozen unit depends on source-specific provenance, latent state, lineage, hidden trace, or unreleased exact arms. Do not require an author release merely because the original paper did not expose the needed unit. If the claim is inherently about an unreleased source-specific unit and first-party reproduction would change the scientific object, use SOURCE_SPECIFIC_REQUIRED + PRIMARY_ASSET_REUSE.

Hard rules:
- Copy candidate_id exactly. The compiler, not the model, binds the frozen prediction/baseline/falsifier fields after parsing; never try to reinterpret them.
- Candidate mechanism cannot define labels, truth, or the data-generating process. State independent truth.
- Candidate prediction and strongest baseline must use the same observable information and matched budget.
- No proposed-method training, second backbone, hidden-outcome retuning, paper-scale experiment, or unbounded search.
- First-party acquisition needs >=3 anti-bake-in controls and an independently grounded reproduction target.
- Define exactly three decision criteria. The compiler owns the REDUCTION_SUPPORTED / RESIDUAL_SURVIVES / INCONCLUSIVE labels and maps your criteria to them; RESIDUAL_SURVIVES only returns to semantic + current-source review.
- An INCONCLUSIVE repair is optional. If you provide one, name exactly one changed variable; leaving it empty means stop/hold on INCONCLUSIVE. If required_single_variable_repair is nonempty, the new branch must change exactly that variable and preserve every other frozen element.
- If required_design_revision is nonempty, revise only the evidence contract defect named there; do not change the frozen scientific question, prediction, baseline, or falsifier.
- Caps: max_units<={MAX_UNITS}, max_wall_minutes<={MAX_WALL_MIN}, max_gpu_hours<={MAX_GPU_HOURS}, max_model_calls<={MAX_MODEL_CALLS}.
- HISTORICAL RESEARCH MEMORY is mandatory context. Read every selected item. FAILURE_ASSET supplies a reusable precheck, never a scientific veto; HOLD is reopenable; SUCCESS_ASSET is scope-bound. Do not repeat a recorded failure mode without satisfying its precheck or explaining why the scope differs.
Allowed acquisition_mode={sorted(MODES)}; source_specificity={sorted(SOURCE_MODES)}. Do not choose a concrete execution adapter: the compiler maps PRIMARY_ASSET_REUSE to PRIMARY_ASSET_ONLY and every first-party mode to SUBSTRATE_PREFLIGHT_REQUIRED.

HISTORICAL_RESEARCH_MEMORY={json.dumps(memory_pack,ensure_ascii=False,separators=(",",":"))}

Return JSON only: {{"designs":[{{"candidate_id":"...","changed_variable":"","source_specificity":"...","acquisition_mode":"...","reproduction_target":"...","independent_truth":"...","causal_unit":"...","observable":"...","intervention":"...","same_information_lock":"...","matched_baseline_execution":"...","anti_bake_in_controls":["...","...","..."],"decision_criteria":{{"baseline_reduction_supported":"criterion under which the strongest same-information baseline explains the frozen prediction and the candidate should STOP","candidate_residual_survives":"criterion under which a distinguishing residual remains after the strongest baseline and the candidate returns to semantic/current-source review","inconclusive":"criterion for no valid separation"}},"single_variable_repair_if_inconclusive":"","adapter_intent":"brief description of the runtime you expect","budget":{{"max_units":1,"max_wall_minutes":1,"max_gpu_hours":0.0,"max_model_calls":0}}}}]}}
CANDIDATES={json.dumps(compact,ensure_ascii=False,separators=(",",":"))}'''
 return prompt,[r["candidate_id"] for r in batch]

def _audit_design(d:dict,e:dict)->list[str]:
 err=[]
 if str(d.get("candidate_id") or "")!=str(e.get("candidate_id") or ""): err.append("candidate-id-mismatch")
 required_repair=_b((e.get("branch_repair") or {}).get("changed_variable"),1800);changed=_b(d.get("changed_variable"),1800)
 if required_repair and changed!=required_repair: err.append("branch-repair-changed-variable-mismatch")
 if not required_repair and changed: err.append("initial-design-must-not-declare-repair-variable")
 source=str(d.get("source_specificity") or "").upper();mode=str(d.get("acquisition_mode") or "").upper();adapter=str(d.get("execution_adapter") or "").upper()
 if source not in SOURCE_MODES: err.append("invalid-source-specificity")
 if mode not in MODES: err.append("invalid-acquisition-mode")
 if adapter not in ADAPTERS: err.append("invalid-execution-adapter")
 if source=="SOURCE_SPECIFIC_REQUIRED" and mode!="PRIMARY_ASSET_REUSE": err.append("source-specific-must-use-primary-asset")
 if mode=="PRIMARY_ASSET_REUSE" and adapter!="PRIMARY_ASSET_ONLY": err.append("primary-asset-requires-primary-adapter")
 if mode!="PRIMARY_ASSET_REUSE" and adapter!="SUBSTRATE_PREFLIGHT_REQUIRED": err.append("first-party-must-use-compiler-substrate-preflight-adapter")
 for k in ("reproduction_target","independent_truth","causal_unit","observable","intervention","same_information_lock","matched_baseline_execution"):
  if not _b(d.get(k)): err.append("missing:"+k)
 controls=[str(x).strip() for x in d.get("anti_bake_in_controls") or [] if str(x).strip()]
 if mode!="PRIMARY_ASSET_REUSE" and len(controls)<3: err.append("first-party-needs-three-anti-bake-in-controls")
 criteria=d.get("decision_criteria") or {}
 if not isinstance(criteria,dict) or any(not _b(criteria.get(k)) for k in ("baseline_reduction_supported","candidate_residual_survives","inconclusive")): err.append("three-way-decision-criteria-incomplete")
 budget=d.get("budget") or {}
 try: units=int(budget.get("max_units"));wall=int(budget.get("max_wall_minutes"));gpu=float(budget.get("max_gpu_hours"));calls=int(budget.get("max_model_calls"))
 except (TypeError,ValueError): err.append("invalid-budget-types")
 else:
  if not 1<=units<=MAX_UNITS: err.append("budget-max-units-out-of-range")
  if not 1<=wall<=MAX_WALL_MIN: err.append("budget-wall-out-of-range")
  if not 0<=gpu<=MAX_GPU_HOURS: err.append("budget-gpu-out-of-range")
  if not 0<=calls<=MAX_MODEL_CALLS: err.append("budget-model-calls-out-of-range")
 text=" ".join(_b(d.get(k),4000).lower() for k in ("reproduction_target","intervention","matched_baseline_execution"))
 if any(t in text for t in ("train the proposed method","fine-tune the proposed method","second backbone","tune on hidden","retune on hidden")): err.append("forbidden-method-or-hidden-tuning")
 return sorted(set(err))

def _promote_deferred(entries:list[dict])->None:
 active_statuses={"NEEDS_BOUNDED_EVIDENCE_DESIGN","NEEDS_OPERATIONALIZATION_RECOMPILE","NEEDS_INDEPENDENT_EVIDENCE_REVIEW","READY_FOR_BOUNDED_SUBSTRATE_PREFLIGHT","NEEDS_MINIMAL_HARNESS_IMPLEMENTATION","READY_FOR_BOUNDED_EVIDENCE_ACQUISITION","BRANCH_REPAIR_READY","RETURN_TO_SEMANTIC_CURRENT_SOURCE_REVIEW"}
 active=sum(r.get("design_selected") is True and r.get("status") in active_statuses for r in entries)
 for row in sorted(entries,key=lambda r:int(r.get("priority_rank") or 10**9)):
  if active>=MAX_ACTIVE:break
  if row.get("status")=="DEFERRED_BY_ACTIVE_PORTFOLIO_BUDGET":
   row["design_selected"]=True;row["status"]="NEEDS_BOUNDED_EVIDENCE_DESIGN";active+=1

def compile_evidence_designs(plan:dict,payload:dict,*,part:int=1,design_model:str="")->dict:
 if plan.get("scientific_authority") is not False or (plan.get("policy") or {}).get("reduction_pending_is_provisional_not_failed") is not True: raise ValueError("invalid provisional evidence plan")
 entries=[dict(r) for r in plan.get("entries") or [] if isinstance(r,dict)];by={str(r.get("candidate_id") or ""):r for r in entries};seen=set()
 for d in [x for x in payload.get("designs") or [] if isinstance(x,dict)]:
  cid=str(d.get("candidate_id") or "").strip()
  if not cid or cid in seen: raise ValueError("evidence design ids must be unique")
  seen.add(cid);e=by.get(cid)
  prior_status=str(e.get("status") or "") if e else ""
  if not e or e.get("design_selected") is not True or prior_status not in {"NEEDS_BOUNDED_EVIDENCE_DESIGN","BRANCH_REPAIR_READY"}: raise ValueError(f"design not selected/pending:{cid}")
  # Frozen scientific fields are compiler-owned, never model-owned. Any model text in these keys is discarded.
  d=dict(d);d["adapter_intent"]=_b(d.get("adapter_intent") or d.get("execution_adapter"),1800);d["execution_adapter"]="PRIMARY_ASSET_ONLY" if str(d.get("acquisition_mode") or "").upper()=="PRIMARY_ASSET_REUSE" else "SUBSTRATE_PREFLIGHT_REQUIRED";d["frozen_exact_prediction"]=e.get("frozen_exact_prediction");d["frozen_same_information_baseline"]=e.get("frozen_same_information_baseline");d["frozen_falsifier_expression"]=e.get("frozen_falsifier_expression")
  criteria=d.get("decision_criteria") or {};d["decision_rule"]={"REDUCTION_SUPPORTED":criteria.get("baseline_reduction_supported",""),"RESIDUAL_SURVIVES":criteria.get("candidate_residual_survives",""),"INCONCLUSIVE":criteria.get("inconclusive","")}
  errors=_audit_design(d,e);e["design"]=json.loads(json.dumps(d,ensure_ascii=False));e["design_audit"]={"passed":not errors,"errors":errors};e["design_provenance"]={"resolved_model":str(design_model or ""),"part":part,"scientific_authority":False};e.pop("evidence_review",None)
  if errors: e["status"]="HOLD_EVIDENCE_DESIGN_INVALID";e["execution_authorized"]=False;continue
  if prior_status=="BRANCH_REPAIR_READY":
   tree=dict(e.get("tree") or {});tree["parent_contract_sha256"]=str(e.get("contract_sha256") or "");tree["depth"]=int((e.get("branch_repair") or {}).get("next_depth") or int(tree.get("depth") or 0)+1);tree["repair_count"]=int(tree.get("repair_count") or 0)+1;e["tree"]=tree
  e["contract_sha256"]=_sha({"candidate_id":cid,"tree":e.get("tree") or {},"design":e["design"],"policy_version":SCHEMA_VERSION})
  if str(d.get("source_specificity") or "").upper()=="SOURCE_SPECIFIC_REQUIRED":
   e["source_specific_design"]=json.loads(json.dumps(e["design"],ensure_ascii=False));e["status"]="NEEDS_OPERATIONALIZATION_RECOMPILE" if int(e.get("operationalization_recompile_attempts") or 0)==0 else "WAIT_PRIMARY_ASSET_RELEASE";e["execution_authorized"]=False
  else: e["status"]="NEEDS_INDEPENDENT_EVIDENCE_REVIEW";e["execution_authorized"]=False;e["authority"]=dict(AUTHORITY)
 _promote_deferred(entries)
 out=dict(plan);out.update({"generated_at":_now(),"entries":entries,"summary":_summary(entries),"last_design_part":part,"scientific_authority":False,"authority":dict(AUTHORITY)})
 out["status"]=_plan_status(entries)
 return out

def operationalization_recompile_prompt(plan:dict,*,part:int=1,batch_size:int=2,research_memory_query_pack:dict|None=None)->tuple[str,list[str]]:
 rows=[r for r in plan.get("entries") or [] if isinstance(r,dict) and r.get("status")=="NEEDS_OPERATIONALIZATION_RECOMPILE"][:batch_size]
 if not rows:raise ValueError(f"empty operationalization-recompile batch part={part}")
 compact=[{"candidate_id":r.get("candidate_id"),"title":r.get("title"),"frozen_irreducible_object":r.get("frozen_irreducible_object"),"frozen_exact_prediction":r.get("frozen_exact_prediction"),"frozen_same_information_baseline":r.get("frozen_same_information_baseline"),"frozen_falsifier_expression":r.get("frozen_falsifier_expression"),"frozen_endpoint_headroom_requirement":r.get("frozen_endpoint_headroom_requirement"),"prior_support":r.get("prior_support") or {},"source_specific_design":r.get("source_specific_design") or r.get("design") or {}} for r in rows]
 memory_pack=research_memory_query_pack or {"purpose":"EXPERIMENT_DESIGN","selected_memory_ids":[],"text":"","scientific_authority":False}
 prompt=f'''You are recompiling only the OPERATIONALIZATION of a reduction falsifier whose first attempt depended on unavailable author/source assets. This is not permission to change the paper problem.

Immutable compiler-owned fields: irreducible scientific object, exact prediction, strongest same-information baseline, and endpoint headroom requirement. You may change only how new evidence is instantiated and measured.

For each candidate choose exactly one verdict:
- RECOMPILED_FIRST_PARTY: the unavailable source asset is incidental to the scientific object, and a first-party experiment can instantiate the SAME variables/contrast without defining the result into the test.
- INTRINSIC_SOURCE_SPECIFIC: at least one variable/contrast in the exact prediction intrinsically depends on the original named method, hidden lineage/state, or author-only unit; changing it would change the scientific object.
- BLOCK_NO_EQUIVALENT_OPERATIONALIZATION: no non-baked-in equivalent experiment can be specified from available public semantics.

RECOMPILED_FIRST_PARTY requirements:
1. Preserve the exact prediction and same-information baseline semantically without weakening them.
2. List >=4 scientific_object_invariants that the new experiment preserves.
3. Explicitly name source_specific_dependencies_removed and explain why each is acquisition provenance/nuisance rather than part of the scientific object.
4. Give an equivalence_probe that can FAIL before the main falsifier if the new operationalization is not faithful.
5. No synthetic generator may encode the predicted threshold/sign/order by construction. Independent truth is mandatory.
6. Same-information baseline must receive exactly the same observables and budget.
7. Stay within caps: units<={MAX_UNITS}, wall<={MAX_WALL_MIN} min, GPU<={MAX_GPU_HOURS} h, model calls<={MAX_MODEL_CALLS}.
8. No proposed-method training, second backbone, hidden-outcome tuning, or paper-scale search.
9. The output design must use source_specificity=REPRODUCIBLE_FIRST_PARTY and a non-PRIMARY_ASSET_REUSE acquisition mode.
10. Read HISTORICAL RESEARCH MEMORY before recompiling. Reuse relevant prechecks, but historical failure cannot replace the current equivalence test and historical success cannot authorize transport.

HISTORICAL_RESEARCH_MEMORY={json.dumps(memory_pack,ensure_ascii=False,separators=(",",":"))}

Return JSON only: {{"recompiles":[{{"candidate_id":"...","verdict":"RECOMPILED_FIRST_PARTY|INTRINSIC_SOURCE_SPECIFIC|BLOCK_NO_EQUIVALENT_OPERATIONALIZATION","reason":"...","scientific_object_invariants":["...","...","...","..."],"source_specific_dependencies_removed":["..."],"why_dependencies_are_not_scientific_object":"...","transport_scope":"...","equivalence_probe":"...","equivalence_failure_action":"return to source-specific wait","design":{{"candidate_id":"...","changed_variable":"operationalization only","source_specificity":"REPRODUCIBLE_FIRST_PARTY","acquisition_mode":"FIRST_PARTY_REPLAY|FIRST_PARTY_SANDBOX|FIRST_PARTY_ROLLOUT|FIRST_PARTY_SIMULATION","reproduction_target":"...","independent_truth":"...","causal_unit":"...","observable":"...","intervention":"...","same_information_lock":"...","matched_baseline_execution":"...","anti_bake_in_controls":["...","...","..."],"decision_criteria":{{"baseline_reduction_supported":"...","candidate_residual_survives":"...","inconclusive":"..."}},"single_variable_repair_if_inconclusive":"","adapter_intent":"brief description of expected runtime","budget":{{"max_units":1,"max_wall_minutes":1,"max_gpu_hours":0.0,"max_model_calls":0}}}}}}]}}
CANDIDATES={json.dumps(compact,ensure_ascii=False,separators=(",",":"))}'''
 return prompt,[str(r.get("candidate_id") or "") for r in rows]

def compile_operationalization_recompiles(plan:dict,payload:dict,*,part:int=1,recompiler_model:str="")->dict:
 entries=[dict(r) for r in plan.get("entries") or [] if isinstance(r,dict)];by={str(r.get("candidate_id") or ""):r for r in entries};seen=set()
 for item in [x for x in payload.get("recompiles") or [] if isinstance(x,dict)]:
  cid=str(item.get("candidate_id") or "").strip()
  if not cid or cid in seen:raise ValueError("operationalization recompile ids must be nonempty and unique")
  seen.add(cid);e=by.get(cid)
  if not e or e.get("status")!="NEEDS_OPERATIONALIZATION_RECOMPILE":raise ValueError(f"no operationalization recompile pending:{cid}")
  if int(e.get("operationalization_recompile_attempts") or 0)>=1:raise ValueError(f"operationalization recompile is single-attempt:{cid}")
  e["operationalization_recompile_attempts"]=1;verdict=str(item.get("verdict") or "").strip().upper();reason=_b(item.get("reason"),2200)
  if verdict not in {"RECOMPILED_FIRST_PARTY","INTRINSIC_SOURCE_SPECIFIC","BLOCK_NO_EQUIVALENT_OPERATIONALIZATION"}:raise ValueError(f"invalid operationalization recompile verdict:{cid}:{verdict}")
  adjudication={"verdict":verdict,"reason":reason,"recompiler_model":str(recompiler_model or ""),"part":part,"scientific_authority":False};e["operationalization_recompile_adjudication"]=adjudication;e["execution_authorized"]=False;e["authority"]=dict(AUTHORITY)
  if verdict=="INTRINSIC_SOURCE_SPECIFIC":e["status"]="WAIT_PRIMARY_ASSET_RELEASE";e["review_feedback"]=reason;continue
  if verdict=="BLOCK_NO_EQUIVALENT_OPERATIONALIZATION":e["status"]="HOLD_NO_EQUIVALENT_OPERATIONALIZATION";e["review_feedback"]=reason;continue
  invariants=[_b(x,900) for x in item.get("scientific_object_invariants") or [] if _b(x,900)];removed=[_b(x,900) for x in item.get("source_specific_dependencies_removed") or [] if _b(x,900)];why=_b(item.get("why_dependencies_are_not_scientific_object"),2200);scope=_b(item.get("transport_scope"),1600);probe=_b(item.get("equivalence_probe"),2200);fail_action=_b(item.get("equivalence_failure_action"),1200);design=dict(item.get("design") or {})
  if len(invariants)<4 or not removed or not all((why,scope,probe,fail_action)):e["status"]="HOLD_EVIDENCE_DESIGN_INVALID";e["operationalization_recompile_audit"]={"passed":False,"errors":["operationalization-equivalence-contract-incomplete"]};continue
  design["candidate_id"]=cid;design["changed_variable"]="";design["adapter_intent"]=_b(design.get("adapter_intent") or design.get("execution_adapter"),1800);design["execution_adapter"]="PRIMARY_ASSET_ONLY" if str(design.get("acquisition_mode") or "").upper()=="PRIMARY_ASSET_REUSE" else "SUBSTRATE_PREFLIGHT_REQUIRED";design["frozen_exact_prediction"]=e.get("frozen_exact_prediction");design["frozen_same_information_baseline"]=e.get("frozen_same_information_baseline");design["frozen_falsifier_expression"]=e.get("frozen_falsifier_expression");criteria=design.get("decision_criteria") or {};design["decision_rule"]={"REDUCTION_SUPPORTED":criteria.get("baseline_reduction_supported",""),"RESIDUAL_SURVIVES":criteria.get("candidate_residual_survives",""),"INCONCLUSIVE":criteria.get("inconclusive","")}
  errors=_audit_design(design,e)
  if str(design.get("source_specificity") or "").upper()!="REPRODUCIBLE_FIRST_PARTY" or str(design.get("acquisition_mode") or "").upper()=="PRIMARY_ASSET_REUSE":errors.append("recompile-must-be-first-party")
  errors=sorted(set(errors));e["operationalization_recompile_audit"]={"passed":not errors,"errors":errors}
  if errors:e["status"]="HOLD_EVIDENCE_DESIGN_INVALID";continue
  e["original_source_specific_design"]=json.loads(json.dumps(e.get("source_specific_design") or e.get("design") or {},ensure_ascii=False));e["design"]=json.loads(json.dumps(design,ensure_ascii=False));e["design_provenance"]={"resolved_model":str(recompiler_model or ""),"part":part,"stage":"operationalization-recompile","scientific_authority":False};e["operationalization_recompile"]={"scientific_object_invariants":invariants,"source_specific_dependencies_removed":removed,"why_dependencies_are_not_scientific_object":why,"transport_scope":scope,"equivalence_probe":probe,"equivalence_failure_action":fail_action,"scientific_authority":False};e["contract_sha256"]=_sha({"candidate_id":cid,"tree":e.get("tree") or {},"frozen_irreducible_object":e.get("frozen_irreducible_object"),"frozen_exact_prediction":e.get("frozen_exact_prediction"),"frozen_same_information_baseline":e.get("frozen_same_information_baseline"),"operationalization_recompile":e["operationalization_recompile"],"design":e["design"],"policy_version":SCHEMA_VERSION});e["status"]="NEEDS_INDEPENDENT_EVIDENCE_REVIEW"
 _promote_deferred(entries);out=dict(plan);out.update({"generated_at":_now(),"entries":entries,"summary":_summary(entries),"last_operationalization_recompile_part":part,"scientific_authority":False,"authority":dict(AUTHORITY)});out["status"]=_plan_status(entries);return out

def evidence_review_prompt(plan:dict,*,part:int=1,batch_size:int=2)->tuple[str,list[str]]:
 rows=[r for r in plan.get("entries") or [] if isinstance(r,dict) and r.get("status")=="NEEDS_INDEPENDENT_EVIDENCE_REVIEW"][:batch_size]
 if not rows:raise ValueError(f"empty independent evidence-review batch part={part}")
 compact=[{"candidate_id":r.get("candidate_id"),"frozen_irreducible_object":r.get("frozen_irreducible_object"),"frozen_exact_prediction":r.get("frozen_exact_prediction"),"frozen_same_information_baseline":r.get("frozen_same_information_baseline"),"frozen_falsifier_expression":r.get("frozen_falsifier_expression"),"frozen_endpoint_headroom_requirement":r.get("frozen_endpoint_headroom_requirement"),"prior_support":r.get("prior_support") or {},"operationalization_recompile":r.get("operationalization_recompile") or {},"design":r.get("design") or {},"design_model":(r.get("design_provenance") or {}).get("resolved_model","")} for r in rows]
 prompt=f'''You are an independent scientific contract reviewer. Review bounded evidence-acquisition designs only; do not judge paper novelty and do not authorize Method/P0/GPU.

A CLEAR design must satisfy ALL checks:
1. independent_truth_valid: outcomes/labels come from an external environment, benchmark, program, or otherwise independently frozen truth; the candidate mechanism does not generate truth.
2. scientific_object_preserved: first-party reproduction measures the same scientific object as the frozen problem. A synthetic proxy that merely encodes the claimed mechanism is not enough.
3. no_mechanism_bake_in: the simulator/sandbox/data construction does not force the candidate prediction by design; controls allow the strongest baseline to win.
4. same_information_baseline_valid: candidate residual and strongest frozen baseline use the same observable information, units, and matched budget.
5. falsifier_not_method_evaluation: the run discriminates the frozen paper problem/reduction, not a newly invented proposed method.
6. outcome_semantics_valid: baseline_reduction_supported means the strongest same-information baseline EXPLAINS the frozen prediction and therefore the candidate should stop; candidate_residual_survives means the baseline FAILS to explain a replicated distinguishing residual and therefore the candidate returns to semantic/current-source review.
7. bounded_budget_valid: the contract stays within the frozen bounded-evidence caps and does not hide paper-scale training/search.
8. prior_support_constraint_respected: if prior_support identified an unavailable source-specific unit, first-party reproduction is CLEAR only when the design preserves the frozen scientific object without manufacturing the missing provenance/latent/lineage/arm by construction.
9. operationalization_equivalence_valid: if operationalization_recompile is nonempty, every frozen scientific-object invariant and exact-prediction variable survives unchanged, removed dependencies are genuinely acquisition provenance/nuisance, and the equivalence_probe can independently fail before the main falsifier. If no recompile is present, mark this true.

Verdicts: CLEAR_FOR_SUBSTRATE_PREFLIGHT, REVISE, SOURCE_SPECIFIC_REQUIRED, BLOCK_BAKE_IN.
- CLEAR only if all nine checks are true. CLEAR means only that local substrate feasibility may now be checked; it never authorizes execution by itself.
- REVISE only for one repairable contract defect; name one concrete revision without changing frozen prediction/baseline/falsifier.
- SOURCE_SPECIFIC_REQUIRED if first-party reproduction would change the scientific object and the unreleased author/source asset is genuinely required.
- BLOCK_BAKE_IN if independent evidence cannot be obtained without defining the result into the test.

Return JSON only: {{"reviews":[{{"candidate_id":"...","verdict":"...","checks":{{"independent_truth_valid":true,"scientific_object_preserved":true,"no_mechanism_bake_in":true,"same_information_baseline_valid":true,"falsifier_not_method_evaluation":true,"outcome_semantics_valid":true,"bounded_budget_valid":true,"prior_support_constraint_respected":true,"operationalization_equivalence_valid":true}},"reason":"...","required_revision":""}}]}}
DESIGNS={json.dumps(compact,ensure_ascii=False,separators=(",",":"))}'''
 return prompt,[str(r.get("candidate_id") or "") for r in rows]

def compile_evidence_reviews(plan:dict,payload:dict,*,part:int=1,reviewer_model:str="")->dict:
 entries=[dict(r) for r in plan.get("entries") or [] if isinstance(r,dict)];by={str(r.get("candidate_id") or ""):r for r in entries};seen=set();required_checks=("independent_truth_valid","scientific_object_preserved","no_mechanism_bake_in","same_information_baseline_valid","falsifier_not_method_evaluation","outcome_semantics_valid","bounded_budget_valid","prior_support_constraint_respected","operationalization_equivalence_valid")
 for review in [x for x in payload.get("reviews") or [] if isinstance(x,dict)]:
  cid=str(review.get("candidate_id") or "").strip()
  if not cid or cid in seen:raise ValueError("evidence review ids must be nonempty and unique")
  seen.add(cid);e=by.get(cid)
  if not e or e.get("status")!="NEEDS_INDEPENDENT_EVIDENCE_REVIEW":raise ValueError(f"evidence review has no pending design:{cid}")
  design_model=str((e.get("design_provenance") or {}).get("resolved_model") or "")
  if reviewer_model and design_model and reviewer_model==design_model:raise ValueError(f"evidence reviewer must be independent from designer:{cid}")
  verdict=str(review.get("verdict") or "").strip().upper();checks=review.get("checks") or {};all_checks=isinstance(checks,dict) and all(checks.get(k) is True for k in required_checks);reason=_b(review.get("reason"),1800);revision=_b(review.get("required_revision"),1800)
  normalized={"verdict":verdict,"checks":{k:checks.get(k) is True for k in required_checks},"reason":reason,"required_revision":revision,"reviewer_model":str(reviewer_model or ""),"part":part,"scientific_authority":False};e["evidence_review"]=normalized;e["execution_authorized"]=False;e["authority"]=dict(AUTHORITY)
  if verdict=="CLEAR_FOR_SUBSTRATE_PREFLIGHT" and all_checks:
   e["status"]="READY_FOR_BOUNDED_SUBSTRATE_PREFLIGHT";e["execution_authorized"]=False;e["authority"]={**dict(AUTHORITY),"bounded_substrate_preflight":True}
  elif verdict=="SOURCE_SPECIFIC_REQUIRED":
   e["status"]="NEEDS_OPERATIONALIZATION_RECOMPILE" if int(e.get("operationalization_recompile_attempts") or 0)==0 else "WAIT_PRIMARY_ASSET_RELEASE";e["review_feedback"]=reason or revision
  elif verdict=="REVISE" and revision:
   count=int(e.get("design_revision_count") or 0)+1;e["design_revision_count"]=count;e["review_feedback"]=revision
   if count<=1:e["status"]="NEEDS_BOUNDED_EVIDENCE_DESIGN"
   else:e["status"]="HOLD_EVIDENCE_REVIEW_BLOCKED"
  else:
   e["status"]="HOLD_EVIDENCE_REVIEW_BLOCKED";e["review_feedback"]=reason or revision or "independent evidence review did not clear all mandatory checks"
 _promote_deferred(entries);out=dict(plan);out.update({"generated_at":_now(),"entries":entries,"summary":_summary(entries),"last_review_part":part,"scientific_authority":False,"authority":dict(AUTHORITY)});out["status"]=_plan_status(entries);return out

def build_substrate_preflight_request(plan:dict)->dict:
 rows=[]
 for e in plan.get("entries") or []:
  if not isinstance(e,dict) or e.get("status")!="READY_FOR_BOUNDED_SUBSTRATE_PREFLIGHT":continue
  d=e.get("design") or {};rows.append({"candidate_id":e.get("candidate_id"),"title":e.get("title"),"contract_sha256":e.get("contract_sha256"),"prior_support":e.get("prior_support") or {},"acquisition_mode":d.get("acquisition_mode"),"execution_adapter":d.get("execution_adapter"),"budget":d.get("budget") or {},"reproduction_target":d.get("reproduction_target"),"independent_truth":d.get("independent_truth"),"review":e.get("evidence_review") or {},"allowed_dispositions":sorted(SUBSTRATE_DISPOSITIONS),"scientific_authority":False})
 return {"schema_version":"1.0","generated_at":_now(),"status":"SUBSTRATE_PREFLIGHT_REQUEST_READY" if rows else "NO_SUBSTRATE_PREFLIGHT_PENDING","summary":{"pending":len(rows),"execution_authorized":0,"scientific_authority":0},"rows":rows,"scientific_authority":False,"authority":dict(AUTHORITY)}

def compile_substrate_preflight(plan:dict,receipt_payload:dict)->dict:
 entries=[dict(r) for r in plan.get("entries") or [] if isinstance(r,dict)];by={str(r.get("candidate_id") or ""):r for r in entries};seen=set()
 for rec in [x for x in receipt_payload.get("receipts") or [] if isinstance(x,dict)]:
  cid=str(rec.get("candidate_id") or "").strip()
  if not cid or cid in seen:raise ValueError("substrate preflight ids must be nonempty and unique")
  seen.add(cid);e=by.get(cid)
  if not e or e.get("status")!="READY_FOR_BOUNDED_SUBSTRATE_PREFLIGHT":raise ValueError(f"substrate preflight has no review-cleared contract:{cid}")
  if str(rec.get("contract_sha256") or "")!=str(e.get("contract_sha256") or ""):raise ValueError(f"substrate preflight contract digest mismatch:{cid}")
  disposition=str(rec.get("disposition") or "").strip().upper();reason=_b(rec.get("reason"),2200);inventory=_b(rec.get("inventory_summary"),2600)
  if disposition not in SUBSTRATE_DISPOSITIONS:raise ValueError(f"invalid substrate disposition:{cid}:{disposition}")
  if not reason or not inventory:raise ValueError(f"substrate preflight requires reason and inventory summary:{cid}")
  out={"disposition":disposition,"reason":reason,"inventory_summary":inventory,"checked_at":_now(),"scientific_authority":False}
  e["execution_authorized"]=False;e["authority"]=dict(AUTHORITY)
  if disposition=="EXISTING_HARNESS_READY":
   sha=str(rec.get("asset_manifest_sha256") or "").strip().lower()
   if not re.fullmatch(r"[0-9a-f]{64}",sha) or rec.get("probe_passed") is not True or rec.get("budget_feasible") is not True:raise ValueError(f"existing harness readiness requires manifest, probe, and budget PASS:{cid}")
   out.update({"asset_manifest_sha256":sha,"probe_passed":True,"budget_feasible":True});e["status"]="READY_FOR_BOUNDED_EVIDENCE_ACQUISITION";e["execution_authorized"]=True;e["authority"]={**dict(AUTHORITY),"bounded_evidence_acquisition":True}
  elif disposition=="MINIMAL_HARNESS_IMPLEMENTATION_READY":
   sha=str(rec.get("harness_plan_sha256") or "").strip().lower();scope=_b(rec.get("implementation_scope"),2200)
   if not re.fullmatch(r"[0-9a-f]{64}",sha) or not scope or rec.get("budget_feasible") is not True:raise ValueError(f"minimal harness implementation requires bounded plan digest/scope/budget:{cid}")
   out.update({"harness_plan_sha256":sha,"implementation_scope":scope,"budget_feasible":True});e["status"]="NEEDS_MINIMAL_HARNESS_IMPLEMENTATION";e["authority"]={**dict(AUTHORITY),"bounded_harness_implementation":True}
  elif disposition=="PROTOCOL_REPAIR_REQUIRED":
   revision=_b(rec.get("required_revision"),1800)
   if not revision:raise ValueError(f"protocol repair requires one bounded required_revision:{cid}")
   count=int(e.get("design_revision_count") or 0)+1;e["design_revision_count"]=count;e["review_feedback"]=revision;e["execution_authorized"]=False;e["authority"]=dict(AUTHORITY)
   if count<=1:e["status"]="NEEDS_BOUNDED_EVIDENCE_DESIGN"
   else:e["status"]="HOLD_EVIDENCE_REVIEW_BLOCKED"
  elif disposition=="SOURCE_SPECIFIC_REQUIRED":
   e["status"]="WAIT_PRIMARY_ASSET_RELEASE";e["review_feedback"]=reason
  elif disposition=="BUDGET_INFEASIBLE":
   e["status"]="HOLD_SUBSTRATE_BUDGET_INFEASIBLE";e["review_feedback"]=reason
  else:
   e["status"]="HOLD_SUBSTRATE_UNAVAILABLE";e["review_feedback"]=reason
  e["substrate_preflight"]=out
 _promote_deferred(entries);result=dict(plan);result.update({"generated_at":_now(),"entries":entries,"summary":_summary(entries),"scientific_authority":False,"authority":dict(AUTHORITY)});result["status"]=_plan_status(entries);return result

def compile_harness_implementation_receipts(plan:dict,receipt_payload:dict)->dict:
 entries=[dict(r) for r in plan.get("entries") or [] if isinstance(r,dict)];by={str(r.get("candidate_id") or ""):r for r in entries};seen=set()
 for rec in [x for x in receipt_payload.get("receipts") or [] if isinstance(x,dict)]:
  cid=str(rec.get("candidate_id") or "").strip()
  if not cid or cid in seen:raise ValueError("harness implementation receipt ids must be nonempty and unique")
  seen.add(cid);e=by.get(cid)
  if not e or e.get("status")!="NEEDS_MINIMAL_HARNESS_IMPLEMENTATION":raise ValueError(f"no bounded harness implementation pending:{cid}")
  if str(rec.get("contract_sha256") or "")!=str(e.get("contract_sha256") or ""):raise ValueError(f"harness implementation contract digest mismatch:{cid}")
  implementation_status=str(rec.get("implementation_status") or "PASS").strip().upper()
  if implementation_status=="SUPPORT_BLOCKED":
   manifest=str(rec.get("failure_manifest_sha256") or "").strip().lower();reason=_b(rec.get("reason"),2400);reopen=_b(rec.get("reopen_condition"),1800);failure_class=str(rec.get("failure_class") or "").strip().lower()
   if not re.fullmatch(r"[0-9a-f]{64}",manifest) or not reason or not reopen or failure_class not in {"support","runtime","support/runtime"}:raise ValueError(f"harness support-blocked receipt incomplete:{cid}")
   e["harness_implementation_failure"]={"implementation_status":"SUPPORT_BLOCKED","failure_manifest_sha256":manifest,"failure_class":failure_class,"reason":reason,"reopen_condition":reopen,"belief_authority":False,"scientific_authority":False};e["status"]="HOLD_HARNESS_RUNTIME_SUPPORT";e["execution_authorized"]=False;e["authority"]=dict(AUTHORITY);continue
  if implementation_status!="PASS":raise ValueError(f"invalid harness implementation status:{cid}:{implementation_status}")
  sha=str(rec.get("harness_manifest_sha256") or "").strip().lower();summary=_b(rec.get("implementation_summary"),2400)
  if not re.fullmatch(r"[0-9a-f]{64}",sha) or not summary or rec.get("sandboxed") is not True or rec.get("probe_passed") is not True or rec.get("budget_feasible") is not True:raise ValueError(f"bounded harness implementation receipt incomplete:{cid}")
  e["harness_implementation"]={"implementation_status":"PASS","harness_manifest_sha256":sha,"implementation_summary":summary,"sandboxed":True,"probe_passed":True,"budget_feasible":True,"scientific_authority":False};e["status"]="READY_FOR_BOUNDED_EVIDENCE_ACQUISITION";e["execution_authorized"]=True;e["authority"]={**dict(AUTHORITY),"bounded_evidence_acquisition":True}
 result=dict(plan);result.update({"generated_at":_now(),"entries":entries,"summary":_summary(entries),"scientific_authority":False,"authority":dict(AUTHORITY)});result["status"]=_plan_status(entries);return result

def compile_harness_runtime_invalidations(plan:dict,receipt_payload:dict)->dict:
 entries=[dict(r) for r in plan.get("entries") or [] if isinstance(r,dict)];by={str(r.get("candidate_id") or ""):r for r in entries};seen=set()
 for rec in [x for x in receipt_payload.get("receipts") or [] if isinstance(x,dict)]:
  cid=str(rec.get("candidate_id") or "").strip()
  if not cid or cid in seen:raise ValueError("harness runtime invalidation ids must be nonempty and unique")
  seen.add(cid);e=by.get(cid)
  if not e or e.get("status")!="READY_FOR_BOUNDED_EVIDENCE_ACQUISITION" or e.get("execution_authorized") is not True:raise ValueError(f"no execution-ready harness to invalidate:{cid}")
  if str(rec.get("contract_sha256") or "")!=str(e.get("contract_sha256") or ""):raise ValueError(f"harness invalidation contract digest mismatch:{cid}")
  current=(e.get("harness_implementation") or {}).get("harness_manifest_sha256")
  if str(rec.get("harness_manifest_sha256") or "")!=str(current or ""):raise ValueError(f"harness invalidation manifest mismatch:{cid}")
  failure_manifest=str(rec.get("failure_manifest_sha256") or "").strip().lower();failure_class=str(rec.get("failure_class") or "").strip().lower();reason=_b(rec.get("reason"),2800);reopen=_b(rec.get("reopen_condition"),2200)
  charged=rec.get("provider_calls_charged",0);remaining=rec.get("remaining_model_call_budget",MAX_MODEL_CALLS)
  if not re.fullmatch(r"[0-9a-f]{64}",failure_manifest) or failure_class not in {"support","runtime","support/runtime","protocol","operational"} or not reason or not reopen:raise ValueError(f"harness runtime invalidation incomplete:{cid}")
  if not isinstance(charged,int) or charged<0 or not isinstance(remaining,int) or not 0<=remaining<=MAX_MODEL_CALLS:raise ValueError(f"harness runtime invalidation budget invalid:{cid}")
  e["harness_runtime_invalidation"]={"failure_manifest_sha256":failure_manifest,"failure_class":failure_class,"reason":reason,"reopen_condition":reopen,"provider_calls_charged":charged,"remaining_model_call_budget":remaining,"belief_authority":False,"scientific_authority":False}
  e["execution_authorized"]=False;e["status"]="HOLD_HARNESS_RUNTIME_SUPPORT";e["authority"]=dict(AUTHORITY)
 result=dict(plan);result.update({"generated_at":_now(),"entries":entries,"summary":_summary(entries),"scientific_authority":False,"authority":dict(AUTHORITY)});result["status"]=_plan_status(entries);return result


def compile_harness_runtime_repair_receipts(plan:dict,receipt_payload:dict)->dict:
 entries=[dict(r) for r in plan.get("entries") or [] if isinstance(r,dict)];by={str(r.get("candidate_id") or ""):r for r in entries};seen=set()
 for rec in [x for x in receipt_payload.get("receipts") or [] if isinstance(x,dict)]:
  cid=str(rec.get("candidate_id") or "").strip()
  if not cid or cid in seen:raise ValueError("harness runtime repair ids must be nonempty and unique")
  seen.add(cid);e=by.get(cid)
  if not e or e.get("status")!="HOLD_HARNESS_RUNTIME_SUPPORT" or e.get("execution_authorized") is not False:raise ValueError(f"no runtime-held harness to repair:{cid}")
  if str(rec.get("contract_sha256") or "")!=str(e.get("contract_sha256") or ""):raise ValueError(f"runtime repair contract digest mismatch:{cid}")
  invalid=e.get("harness_runtime_invalidation") or {};failure_manifest=str(invalid.get("failure_manifest_sha256") or "")
  if str(rec.get("failure_manifest_sha256") or "")!=failure_manifest:raise ValueError(f"runtime repair failure-manifest mismatch:{cid}")
  previous=(e.get("harness_implementation") or {}).get("harness_manifest_sha256")
  if str(rec.get("replaces_harness_manifest_sha256") or "")!=str(previous or ""):raise ValueError(f"runtime repair previous-manifest mismatch:{cid}")
  new_plan=str(rec.get("replacement_harness_plan_sha256") or "").strip().lower();new_manifest=str(rec.get("harness_manifest_sha256") or "").strip().lower();summary=_b(rec.get("implementation_summary"),2600)
  if not re.fullmatch(r"[0-9a-f]{64}",new_plan) or not re.fullmatch(r"[0-9a-f]{64}",new_manifest) or not summary:raise ValueError(f"runtime repair manifest/plan incomplete:{cid}")
  if rec.get("sandboxed") is not True or rec.get("probe_passed") is not True or rec.get("budget_feasible") is not True or rec.get("scientific_object_unchanged") is not True or rec.get("protocol_only_change") is not True:raise ValueError(f"runtime repair invariants not satisfied:{cid}")
  prior_charged=invalid.get("provider_calls_charged");remaining=invalid.get("remaining_model_call_budget");retry_cap=rec.get("replacement_provider_call_cap")
  if not isinstance(prior_charged,int) or prior_charged<0 or not isinstance(remaining,int) or remaining<0 or not isinstance(retry_cap,int) or retry_cap<=0 or retry_cap>remaining:raise ValueError(f"runtime repair budget invalid:{cid}")
  e["prior_harness_implementation"]=dict(e.get("harness_implementation") or {})
  e["harness_implementation"]={"implementation_status":"PASS","harness_manifest_sha256":new_manifest,"implementation_summary":summary,"sandboxed":True,"probe_passed":True,"budget_feasible":True,"scientific_authority":False}
  e["harness_runtime_repair"]={"failure_manifest_sha256":failure_manifest,"replacement_harness_plan_sha256":new_plan,"replaces_harness_manifest_sha256":str(previous or ""),"replacement_harness_manifest_sha256":new_manifest,"provider_calls_already_charged":prior_charged,"remaining_model_call_budget_before_repair":remaining,"replacement_provider_call_cap":retry_cap,"scientific_object_unchanged":True,"protocol_only_change":True,"belief_authority":False,"scientific_authority":False}
  e["execution_authorized"]=True;e["status"]="READY_FOR_BOUNDED_EVIDENCE_ACQUISITION";e["authority"]={**dict(AUTHORITY),"bounded_evidence_acquisition":True}
 result=dict(plan);result.update({"generated_at":_now(),"entries":entries,"summary":_summary(entries),"scientific_authority":False,"authority":dict(AUTHORITY)});result["status"]=_plan_status(entries);return result


def write_compiled_evidence_designs(*,run_root:Path,payload:dict,part:int=1,design_model:str="")->dict:
 path=run_root/PLAN_FILENAME;state=compile_evidence_designs(json.loads(path.read_text(encoding="utf-8")),payload,part=part,design_model=design_model);path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");return state

def adjudicate_evidence_receipts(plan:dict,receipt_payload:dict)->dict:
 entries=[dict(r) for r in plan.get("entries") or [] if isinstance(r,dict)];by={str(r.get("candidate_id") or ""):r for r in entries};seen=set()
 for rec in [x for x in receipt_payload.get("receipts") or [] if isinstance(x,dict)]:
  cid=str(rec.get("candidate_id") or "").strip()
  if not cid or cid in seen: raise ValueError("evidence receipt ids must be unique")
  seen.add(cid);e=by.get(cid)
  if not e or e.get("status")!="READY_FOR_BOUNDED_EVIDENCE_ACQUISITION": raise ValueError(f"no execution-ready contract:{cid}")
  if str(rec.get("contract_sha256") or "")!=str(e.get("contract_sha256") or ""): raise ValueError(f"contract digest mismatch:{cid}")
  outcome=str(rec.get("outcome") or "").upper();manifest=str(rec.get("evidence_manifest_sha256") or "").lower();units=rec.get("qualified_units")
  if outcome not in OUTCOMES: raise ValueError(f"invalid evidence outcome:{cid}")
  if not re.fullmatch(r"[0-9a-f]{64}",manifest): raise ValueError(f"manifest digest required:{cid}")
  if rec.get("protocol_valid") is not True: raise ValueError(f"invalid protocol cannot update belief:{cid}")
  if not isinstance(units,int) or units<=0 or not _b(rec.get("metric_summary")): raise ValueError(f"qualified evidence summary required:{cid}")
  e["execution_authorized"]=False;e["evidence_receipt"]={"outcome":outcome,"qualified_units":units,"evidence_manifest_sha256":manifest,"metric_summary":_b(rec.get("metric_summary"),1800),"protocol_valid":True}
  if outcome=="REDUCTION_SUPPORTED": e["status"]="STOP_EXACT_REDUCTION_SUPPORTED";e["next_action"]="persist-semantic-dead-end"
  elif outcome=="RESIDUAL_SURVIVES": e["status"]="RETURN_TO_SEMANTIC_CURRENT_SOURCE_REVIEW";e["next_action"]="semantic-and-current-source-review"
  else:
   depth=int((e.get("tree") or {}).get("depth") or 0);repair=_b((e.get("design") or {}).get("single_variable_repair_if_inconclusive"),1800)
   if depth<MAX_DEPTH and repair: e["status"]="BRANCH_REPAIR_READY";e["next_action"]="single-variable-repair";e["branch_repair"]={"changed_variable":repair,"next_depth":depth+1}
   else: e["status"]="HOLD_INCONCLUSIVE_TREE_BUDGET_EXHAUSTED";e["next_action"]="stop-or-human-reformulation"
 _promote_deferred(entries)
 out=dict(plan);out.update({"generated_at":_now(),"entries":entries,"summary":_summary(entries),"scientific_authority":False,"authority":dict(AUTHORITY)});out["status"]=_plan_status(entries)
 return out

def validate_evidence_plan(state:dict)->list[str]:
 errors=[];policy=state.get("policy") or {};summary=state.get("summary") or {}
 if state.get("scientific_authority") is not False: errors.append("plan cannot carry scientific authority")
 for k,v in POLICY.items():
  if policy.get(k)!=v: errors.append("policy-mismatch:"+k)
 if any(int(summary.get(k) or 0)!=0 for k in ("paper_design_authorized","method_authorized","p0_authorized","full_experiment_authorized")): errors.append("downstream-authority-leak")
 entries=[r for r in state.get("entries") or [] if isinstance(r,dict)]
 if len(entries)!=int(summary.get("provisional_problem_candidates") or 0): errors.append("candidate-accounting-mismatch")
 for r in entries:
  if r.get("scientific_authority") is not False: errors.append("entry-scientific-authority-leak")
  if r.get("execution_authorized") is True:
   if r.get("status")!="READY_FOR_BOUNDED_EVIDENCE_ACQUISITION" or not re.fullmatch(r"[0-9a-f]{64}",str(r.get("contract_sha256") or "")):errors.append("execution-without-valid-contract")
   if (r.get("evidence_review") or {}).get("verdict")!="CLEAR_FOR_SUBSTRATE_PREFLIGHT":errors.append("execution-without-independent-review-clear")
   substrate=(r.get("substrate_preflight") or {}).get("disposition")
   implemented=bool(r.get("harness_implementation"))
   if substrate!="EXISTING_HARNESS_READY" and not (substrate=="MINIMAL_HARNESS_IMPLEMENTATION_READY" and implemented):errors.append("execution-without-substrate-or-verified-harness")
  if r.get("status")=="READY_FOR_BOUNDED_SUBSTRATE_PREFLIGHT" and r.get("execution_authorized") is not False:errors.append("contract-review-clear-cannot-authorize-execution")
  auth=r.get("authority") or {}
  if any(auth.get(k) is not False for k in ("scientific_claim","live_problem_gate","paper_design","method","p0","full_experiment")): errors.append("entry-downstream-authority-leak")
 return sorted(set(errors))
