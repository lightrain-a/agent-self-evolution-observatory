from __future__ import annotations

import hashlib, json, re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .paper_development_guidance import research_memory_entry as paper_development_guidance_memory_entry

SCHEMA_VERSION="1.1"
DEFAULT_JSON=PROJECT_ROOT/"generated"/"research-memory-wiki.json"
DEFAULT_JS=PROJECT_ROOT/"generated"/"research-memory-wiki.js"
DEFAULT_CLAIM_LEDGER_JSON=PROJECT_ROOT/"generated"/"asset-first-stri-paper-quality-v2-20260816.json"
PURPOSES={"IDEA_SEARCH","EXPERIMENT_DESIGN","PAPER_DESIGN"};DURABILITY={"transient","recurring-systemic","scientific"}
POLICY={
 "schema_version":SCHEMA_VERSION,"wiki_is_compiled_from_canonical_artifacts_not_a_second_source_of_truth":True,
 "wiki_has_zero_scientific_authority":True,"search_closure_is_not_scientific_dead_end":True,
 "only_core_principle_closure_may_be_scientific_dead_end":True,"every_closure_and_hold_requires_reopen_condition":True,
 "failure_memory_is_layer_typed_and_scope_bound":True,"success_memory_is_scope_bound_and_not_automatic_generalization":True,
 "transient_operational_noise_is_not_prompt_eligible":True,"recurring_operational_failure_may_become_systemic_precheck":True,
 "query_pack_is_context_not_scientific_verdict":True,"query_pack_never_relaxes_downstream_gates":True,
 "query_pack_is_bounded_and_content_addressed":True,"idea_search_experiment_design_and_paper_design_use_distinct_memory_priorities":True,
 "paper_review_patterns_are_prechecks_not_scientific_verdicts":True,"paper_review_memory_never_authorizes_new_experiments":True,
 "paper_design_reserves_at_least_one_review_lesson_when_available":True,
 "reviewer_prose_and_rationale_are_excluded_from_memory_projection":True,
 "human_advisor_paper_development_guidance_is_structured_not_raw_prose":True,
 "paper_design_reserves_paper_development_guidance_when_available":True,
 "paper_development_guidance_cannot_change_scientific_or_experiment_authority":True,
}

def _now():return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def _t(v,n=1800):return " ".join(str(v or "").split())[:n]
def _sha(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def _id(kind,*parts):return f"MEM-{kind[:4].upper()}-{hashlib.sha256('|'.join(str(x or '') for x in parts).encode()).hexdigest()[:18]}"
def _refs(r):return sorted({str(x).strip() for k in ("current_source_refs","source_refs","evidence_refs") for x in r.get(k) or [] if str(x).strip()})[:12]

def load_default_claim_ledger(path:Path=DEFAULT_CLAIM_LEDGER_JSON)->list[dict]:
 try:p=json.loads(path.read_text(encoding="utf-8"))
 except (OSError,json.JSONDecodeError):return []
 return [dict(r) for r in ((p.get("audit") or {}).get("claim_ledger") or []) if isinstance(r,dict)]

def _closure(r:dict,hold=False)->dict:
 c=r.get("counter_explanation") if isinstance(r.get("counter_explanation"),dict) else {}
 fl=_t(r.get("failure_layer"),100);cl=_t(r.get("closure_layer") or fl or "problem_novelty",100)
 dead=bool(r.get("dead_end_certified") is True and fl=="core_principle");kind="HOLD" if hold else ("SCIENTIFIC_CLOSURE" if dead else "SEARCH_CLOSURE")
 cid=_t(r.get("source_candidate_id") or r.get("candidate_id") or r.get("id"),160);strong=_t(r.get("strongest_reduction") or r.get("reason"),1000);reopen=_t(c.get("reopen_condition") or r.get("reopen_only_if"),900)
 return {"memory_id":_id(kind,cid,cl,strong,reopen),"kind":kind,"title":_t(r.get("title") or r.get("problem_text") or cid,420),"summary":strong or _t(r.get("problem_text"),1000),"candidate_id":cid,"scope":_t(c.get("scope") or r.get("scope") or r.get("basin"),700),"affected_layer":fl or cl,"memory_class":_t(r.get("memory_class"),100),"durability_class":"scientific","prompt_eligible":True,"search_closure_certified":r.get("search_closure_certified") is True,"scientific_dead_end_certified":dead,"principle_update_allowed":r.get("principle_update_allowed") is True,"reopen_condition":reopen,"opposite_search_seed":_t(c.get("opposite_search_seed"),900),"reusable_precheck":"","source_refs":_refs(r),"source_artifact":"shadow_search_memory","reuse_effectiveness":{},"scientific_authority":False}

def _failures(lib:dict)->list[dict]:
 groups=defaultdict(list)
 for r in lib.get("assets") or []:
  if isinstance(r,dict) and _t(r.get("signature"),240):groups[_t(r.get("signature"),240)].append(r)
 reuse={_t(r.get("signature"),240):r for r in lib.get("reusable_prechecks") or [] if isinstance(r,dict)};out=[]
 for sig,rows in sorted(groups.items()):
  rr=reuse.get(sig) or {};layer=_t(rr.get("affected_layer") or rows[0].get("affected_layer"),100);occ=max(len(rows),int(rr.get("occurrences") or 0));rc=sum(int((r.get("reuse_effectiveness") or {}).get("reuse_count") or 0) for r in rows);hc=sum(int((r.get("reuse_effectiveness") or {}).get("helped_count") or 0) for r in rows);xc=sum(int((r.get("reuse_effectiveness") or {}).get("hurt_count") or 0) for r in rows)
  if layer=="execution":dur="recurring-systemic" if occ>=2 else "transient"
  elif layer in {"authority-protocol","runtime","infrastructure"}:dur="recurring-systemic" if occ>=2 or rc else "transient"
  else:dur="scientific"
  out.append({"memory_id":_id("FAILURE_ASSET",sig,layer),"kind":"FAILURE_ASSET","title":sig,"summary":_t(rows[0].get("does_not_imply"),700),"candidate_id":"","scope":json.dumps({"ideas":sorted({_t(r.get('idea_id'),160) for r in rows if _t(r.get('idea_id'),160)}),"reuse_scope":rows[0].get("reuse_scope") or {}},ensure_ascii=False,sort_keys=True),"affected_layer":layer,"memory_class":"FAILURE_ASSET","durability_class":dur,"prompt_eligible":dur!="transient","search_closure_certified":False,"scientific_dead_end_certified":False,"principle_update_allowed":False,"reopen_condition":"","opposite_search_seed":"","reusable_precheck":_t(rr.get("reusable_precheck") or rows[0].get("reusable_precheck"),1200),"source_refs":sorted({_t(r.get("evidence_ref"),500) for r in rows if _t(r.get("evidence_ref"),500)})[:6],"source_artifact":"failure_asset_library","occurrences":occ,"last_revalidated":max((_t(r.get("last_revalidated"),50) for r in rows),default=""),"reuse_effectiveness":{"reuse_count":rc,"helped_count":hc,"hurt_count":xc},"scientific_authority":False})
 return out

def _successes(iteration:dict,claims:list[dict])->list[dict]:
 out=[]
 for r in iteration.get("nodes") or []:
  if not isinstance(r,dict) or _t(r.get("diagnosis"),80)!="positive-signal":continue
  iid=_t(r.get("idea_id"),160);ok=r.get("belief_update_allowed") is True
  out.append({"memory_id":_id("SUCCESS_ASSET","experiment",iid,r.get("phase")),"kind":"SUCCESS_ASSET","title":f"{iid} {_t(r.get('phase'),50)} positive signal","summary":_t(r.get("decision_reason") or r.get("diagnosis"),800),"candidate_id":iid,"scope":_t(r.get("phase"),100),"affected_layer":_t(r.get("diagnosis_layer"),100),"memory_class":"SUCCESS_ASSET","durability_class":"scientific","prompt_eligible":ok,"search_closure_certified":False,"scientific_dead_end_certified":False,"principle_update_allowed":False,"reopen_condition":"","opposite_search_seed":"","reusable_precheck":"Reuse only after matching scope, substrate, truth, and comparison contract.","source_refs":[_t(r.get("artifact_dir"),500)] if _t(r.get("artifact_dir"),500) else [],"source_artifact":"experiment_iteration","reuse_effectiveness":{},"scientific_authority":False})
 for r in claims:
  st=_t(r.get("adjudication_status"),80)
  if st not in {"SUPPORTED","SUPPORTED_NARROWLY"} or r.get("trace_complete") is not True:continue
  cid=_t(r.get("claim_id"),120)
  out.append({"memory_id":_id("SUCCESS_ASSET","claim",cid,st,r.get("claim_text")),"kind":"SUCCESS_ASSET","title":f"Claim {cid}: {st}","summary":_t(r.get("claim_text"),1000),"candidate_id":cid,"scope":"AFFIRMATIVE_NARROW_ONLY" if st=="SUPPORTED_NARROWLY" else "AFFIRMATIVE_SUPPORTED","affected_layer":_t(r.get("claim_type"),100),"memory_class":"CLAIM_EVIDENCE_SUCCESS","durability_class":"scientific","prompt_eligible":True,"search_closure_certified":False,"scientific_dead_end_certified":False,"principle_update_allowed":False,"reopen_condition":"","opposite_search_seed":"","reusable_precheck":"Do not generalize beyond the adjudicated claim surface; re-match the evidence contract in new scope.","source_refs":[str(x) for x in r.get("evidence_ids") or [] if str(x)][:10],"source_artifact":"asset_first_stri_claim_ledger","reuse_effectiveness":{},"scientific_authority":False})
 return out

def _questions(meta:dict)->list[dict]:
 out=[]
 for r in meta.get("unresolved_questions") or []:
  if not isinstance(r,dict):continue
  pid=_t(r.get("principle_id"),160);iid=_t(r.get("idea_id"),160);u=_t(r.get("uncertainty"),900)
  out.append({"memory_id":_id("OPEN_QUESTION",pid,iid,u),"kind":"OPEN_QUESTION","title":f"Unresolved principle: {pid or iid}","summary":u,"candidate_id":iid,"scope":pid,"affected_layer":"core_principle","memory_class":"OPEN_QUESTION","durability_class":"scientific","prompt_eligible":True,"search_closure_certified":False,"scientific_dead_end_certified":False,"principle_update_allowed":False,"reopen_condition":"Resolve the named uncertainty with new identifiable evidence.","opposite_search_seed":u,"reusable_precheck":"","source_refs":[],"source_artifact":"scientific_meta_trace.unresolved_questions","reuse_effectiveness":{},"scientific_authority":False})
 return out

def _repeated_block(generator:dict)->list[dict]:
 m=((generator.get("saturation_memory") or {}).get("blocked_problem_memory") or {});b=m.get("top_reduction_basin") or {};pat=_t(b.get("pattern"),320);count=int(b.get("count") or 0)
 if m.get("repeated_reduction_basin") is not True or not pat:return []
 return [{"memory_id":_id("REPEATED_REVIEW_BLOCK",pat,count),"kind":"REPEATED_REVIEW_BLOCK","title":f"Repeated reviewer-reduction basin: {pat}","summary":f"{count} blocked attempts concentrate in this basin; search outside it before another jury call.","candidate_id":"","scope":json.dumps(m.get("blocked_by_lane") or {},sort_keys=True),"affected_layer":"search_control","memory_class":"REPEATED_REVIEW_BLOCK","durability_class":"recurring-systemic","prompt_eligible":True,"search_closure_certified":False,"scientific_dead_end_certified":False,"principle_update_allowed":False,"reopen_condition":"A materially different scientific object or new observable must defeat the repeated strongest reduction.","opposite_search_seed":f"Search outside the {pat} basin.","reusable_precheck":"Mechanically reject pure renamings of the repeated reduction basin before review.","source_refs":[],"source_artifact":"problem_generator.blocked_problem_memory","occurrences":count,"reuse_effectiveness":{},"scientific_authority":False}]

def _discovery_lessons(discovery_cycle:dict|None)->list[dict]:
 out=[]
 for r in (discovery_cycle or {}).get("lessons") or []:
  if not isinstance(r,dict):continue
  lid=_t(r.get("lesson_id"),160);summary=_t(r.get("summary"),1000);reopen=_t(r.get("reopen_condition"),900);precheck=_t(r.get("reusable_precheck"),1000)
  if not lid or not summary or not reopen or not precheck:continue
  lesson_type=_t(r.get("lesson_type"),100);dur="scientific" if lesson_type=="SCIENTIFIC_REDUCTION" else "recurring-systemic"
  out.append({"memory_id":_id("DISCOVERY_LESSON",lid,summary,reopen),"kind":"DISCOVERY_LESSON","title":_t(r.get("title") or lid,420),"summary":summary,"candidate_id":_t(r.get("candidate_id"),160),"scope":lesson_type,"affected_layer":_t(r.get("affected_layer"),100),"memory_class":lesson_type or "DISCOVERY_LESSON","durability_class":dur,"prompt_eligible":True,"search_closure_certified":False,"scientific_dead_end_certified":False,"principle_update_allowed":False,"reopen_condition":reopen,"opposite_search_seed":_t(r.get("opposite_search_seed"),900),"reusable_precheck":precheck,"source_refs":[str(x) for x in r.get("source_refs") or [] if str(x)][:10],"source_artifact":"longitudinal_safety_discovery_cycle","reuse_effectiveness":{},"scientific_authority":False})
 return out

def _review_lessons(paper_ledger_index:dict|None)->list[dict]:
 out=[]
 for row in (paper_ledger_index or {}).get("entries") or []:
  if not isinstance(row,dict):continue
  learning=row.get("review_learning") or {};receipts=int(learning.get("review_receipts") or 0);critical=int(learning.get("decision_critical_objections") or 0)
  if receipts<=0:continue
  paper_id=_t(row.get("paper_id"),160);categories={str(k):int(v or 0) for k,v in (learning.get("category_counts") or {}).items()};evidence={str(k):int(v or 0) for k,v in (learning.get("evidence_state_counts") or {}).items()};actions={str(k):int(v or 0) for k,v in (learning.get("action_class_counts") or {}).items()}
  durable=receipts>=2 and critical>0;dur="recurring-systemic" if durable else "transient"
  summary=f"{receipts} structured Mock-PC receipts contain {critical} decision-critical objections. Categories={json.dumps(categories,sort_keys=True)}; evidence_states={json.dumps(evidence,sort_keys=True)}; action_classes={json.dumps(actions,sort_keys=True)}."
  out.append({"memory_id":_id("REVIEW_LESSON",paper_id,summary),"kind":"REVIEW_LESSON","title":f"Paper review pattern: {paper_id}","summary":summary,"candidate_id":paper_id,"scope":"paper-design-and-internal-review","affected_layer":"paper_review","memory_class":"PAPER_REVIEW_PATTERN","durability_class":dur,"prompt_eligible":durable,"search_closure_certified":False,"scientific_dead_end_certified":False,"principle_update_allowed":False,"reopen_condition":"","opposite_search_seed":"","reusable_precheck":"Before Paper Design and Mock PC, explicitly check recurring objection categories and evidence states from prior papers. Treat the pattern as a precheck, never as scientific evidence or experiment authorization.","source_refs":[f"paper-ledger:{paper_id}:mock-pc"],"source_artifact":"paper_acceptance_ledger.review_learning","occurrences":receipts,"review_learning":{"decision_critical_objections":critical,"category_counts":categories,"evidence_state_counts":evidence,"action_class_counts":actions,"targeted_experiment_proposals":int(learning.get("targeted_experiment_proposals") or 0),"claim_expansion_requests_preserved_as_limitations":int(learning.get("claim_expansion_requests_preserved_as_limitations") or 0)},"scientific_authority":False})
 return out

def lint_research_memory_wiki(wiki:dict)->dict:
 errors=[];warnings=[];rows=[r for r in wiki.get("entries") or [] if isinstance(r,dict)];ids=[str(r.get("memory_id") or "") for r in rows]
 if len(ids)!=len(set(ids)):errors.append({"code":"duplicate-memory-id"})
 for r in rows:
  mid=str(r.get("memory_id") or "");kind=str(r.get("kind") or "");dur=str(r.get("durability_class") or "")
  if r.get("scientific_authority") is not False:errors.append({"code":"memory-authority-leak","memory_id":mid})
  if dur not in DURABILITY:errors.append({"code":"invalid-durability-class","memory_id":mid})
  if dur=="transient" and r.get("prompt_eligible") is True:errors.append({"code":"transient-noise-is-prompt-eligible","memory_id":mid})
  if kind in {"SEARCH_CLOSURE","SCIENTIFIC_CLOSURE","HOLD"} and not _t(r.get("reopen_condition"),900):errors.append({"code":"closure-or-hold-missing-reopen-condition","memory_id":mid})
  if kind=="SCIENTIFIC_CLOSURE" and (r.get("scientific_dead_end_certified") is not True or r.get("affected_layer")!="core_principle"):errors.append({"code":"scientific-closure-not-core-principle-certified","memory_id":mid})
  if kind!="SCIENTIFIC_CLOSURE" and r.get("principle_update_allowed") is True:errors.append({"code":"non-core-memory-cannot-update-principle","memory_id":mid})
  if kind=="FAILURE_ASSET":
   if not _t(r.get("affected_layer"),100):errors.append({"code":"failure-asset-missing-layer","memory_id":mid})
   if not _t(r.get("reusable_precheck"),900):errors.append({"code":"failure-asset-missing-precheck","memory_id":mid})
   if int((r.get("reuse_effectiveness") or {}).get("reuse_count") or 0)==0 and dur!="transient":warnings.append({"code":"failure-asset-not-yet-effectiveness-validated","memory_id":mid,"detail":r.get("title")})
   if dur!="transient" and not _t(r.get("last_revalidated"),50):warnings.append({"code":"durable-failure-memory-missing-revalidation-date","memory_id":mid,"detail":r.get("title")})
  if kind=="DISCOVERY_LESSON":
   if not _t(r.get("reopen_condition"),900) or not _t(r.get("reusable_precheck"),900):errors.append({"code":"discovery-lesson-missing-reopen-or-precheck","memory_id":mid})
   if r.get("principle_update_allowed") is not False or r.get("scientific_dead_end_certified") is not False:errors.append({"code":"discovery-lesson-illegal-scientific-authority","memory_id":mid})
  if kind=="HOLD" and not r.get("source_refs"):warnings.append({"code":"hold-missing-source-ref","memory_id":mid})
  if kind=="SUCCESS_ASSET" and not r.get("source_refs"):warnings.append({"code":"success-memory-missing-evidence-ref","memory_id":mid})
  if kind=="REVIEW_LESSON":
   if r.get("affected_layer")!="paper_review" or r.get("principle_update_allowed") is not False:errors.append({"code":"review-lesson-authority-or-layer-invalid","memory_id":mid})
   if not _t(r.get("reusable_precheck"),900):errors.append({"code":"review-lesson-missing-precheck","memory_id":mid})
   if any(key in r for key in ("reviewer_text","reviewer_prose","action_reason","reviewer_rationale")):errors.append({"code":"review-lesson-exposes-reviewer-prose","memory_id":mid})
  if kind=="PAPER_DEVELOPMENT_GUIDANCE":
   guidance=r.get("guidance") or {};dims=guidance.get("dimensions") or []
   if r.get("affected_layer")!="paper_development" or r.get("principle_update_allowed") is not False:errors.append({"code":"paper-development-guidance-authority-or-layer-invalid","memory_id":mid})
   if not _t(r.get("reusable_precheck"),900):errors.append({"code":"paper-development-guidance-missing-precheck","memory_id":mid})
   if len(dims)!=4:errors.append({"code":"paper-development-guidance-must-have-four-dimensions","memory_id":mid})
   if any(key in r for key in ("raw_advisor_text","advisor_prose","reviewer_text","reviewer_prose")):errors.append({"code":"paper-development-guidance-exposes-raw-prose","memory_id":mid})
 return {"schema_version":SCHEMA_VERSION,"status":"PASS" if not errors else "FAIL","errors":errors,"warnings":warnings,"summary":{"errors":len(errors),"warnings":len(warnings),"unconsumed_failure_assets":sum(x.get("code")=="failure-asset-not-yet-effectiveness-validated" for x in warnings),"missing_revalidation_dates":sum(x.get("code")=="durable-failure-memory-missing-revalidation-date" for x in warnings)},"scientific_authority":False}

def build_research_memory_wiki(*,search_design_state:dict,failure_asset_library:dict,scientific_meta_trace:dict,candidate_portfolio:dict,experiment_iteration:dict,generator_state:dict,claim_ledger:list[dict]|None=None,paper_ledger_index:dict|None=None,discovery_cycle:dict|None=None,generated_at:str|None=None)->dict:
 mem=search_design_state.get("shadow_search_memory") or {};entries=[]
 entries += [_closure(r) for r in mem.get("closed_objects") or [] if isinstance(r,dict)]
 entries += [_closure(r,True) for r in mem.get("hold_objects") or [] if isinstance(r,dict)]
 entries += _failures(failure_asset_library)+_successes(experiment_iteration,claim_ledger if claim_ledger is not None else load_default_claim_ledger())+_questions(scientific_meta_trace)+_repeated_block(generator_state)+_discovery_lessons(discovery_cycle)+_review_lessons(paper_ledger_index)
 entries.append(paper_development_guidance_memory_entry())
 entries=sorted(entries,key=lambda r:(str(r.get("kind") or ""),str(r.get("memory_id") or "")));kc=Counter(r["kind"] for r in entries);dc=Counter(r["durability_class"] for r in entries)
 out={"schema_version":SCHEMA_VERSION,"generated_at":generated_at or _now(),"status":"MEMORY_COMPILED","policy":dict(POLICY),"source_manifest":{"search_memory_closed_objects":len(mem.get("closed_objects") or []),"search_memory_hold_objects":len(mem.get("hold_objects") or []),"failure_assets":int((failure_asset_library.get("summary") or {}).get("assets") or 0),"candidate_portfolio_visible":int((candidate_portfolio.get("summary") or {}).get("visible_candidates") or 0),"unresolved_principles":int((scientific_meta_trace.get("summary") or {}).get("unresolved_principles") or 0),"generator_blocked_attempts":int((((generator_state.get("saturation_memory") or {}).get("blocked_problem_memory") or {}).get("blocked_candidate_attempts") or 0)),"paper_review_ledgers":int(((paper_ledger_index or {}).get("summary") or {}).get("papers") or 0),"discovery_failure_lessons":len((discovery_cycle or {}).get("lessons") or [])},"summary":{"entries":len(entries),"search_closures":kc.get("SEARCH_CLOSURE",0),"scientific_closures":kc.get("SCIENTIFIC_CLOSURE",0),"holds":kc.get("HOLD",0),"failure_assets":kc.get("FAILURE_ASSET",0),"success_assets":kc.get("SUCCESS_ASSET",0),"open_questions":kc.get("OPEN_QUESTION",0),"repeated_review_blocks":kc.get("REPEATED_REVIEW_BLOCK",0),"discovery_lessons":kc.get("DISCOVERY_LESSON",0),"review_lessons":kc.get("REVIEW_LESSON",0),"paper_development_guidance":kc.get("PAPER_DEVELOPMENT_GUIDANCE",0),"prompt_eligible":sum(r.get("prompt_eligible") is True for r in entries),"transient":dc.get("transient",0),"recurring_systemic":dc.get("recurring-systemic",0),"scientific":dc.get("scientific",0)},"entries":entries,"scientific_authority":False,"authority":{"problem_gate":False,"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False}}
 out["wiki_sha256"]=_sha({"schema_version":SCHEMA_VERSION,"policy":out["policy"],"source_manifest":out["source_manifest"],"entries":entries});out["lint"]=lint_research_memory_wiki(out);out["status"]="MEMORY_COMPILED" if out["lint"]["status"]=="PASS" else "MEMORY_INVALID";return out

def _tokens(v:Any)->set[str]:
 text=(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,sort_keys=True)).lower();return set(re.findall(r"[a-z0-9_\-]{4,}|[\u4e00-\u9fff]{2,}",text))
def _weight(k,p):
 weights={
  "IDEA_SEARCH":{"SCIENTIFIC_CLOSURE":120,"DISCOVERY_LESSON":115,"SEARCH_CLOSURE":105,"HOLD":95,"REPEATED_REVIEW_BLOCK":90,"OPEN_QUESTION":85,"SUCCESS_ASSET":65,"FAILURE_ASSET":55,"REVIEW_LESSON":50,"PAPER_DEVELOPMENT_GUIDANCE":35},
  "EXPERIMENT_DESIGN":{"FAILURE_ASSET":125,"HOLD":105,"SUCCESS_ASSET":90,"SCIENTIFIC_CLOSURE":80,"PAPER_DEVELOPMENT_GUIDANCE":80,"REVIEW_LESSON":75,"SEARCH_CLOSURE":70,"DISCOVERY_LESSON":65,"OPEN_QUESTION":60,"REPEATED_REVIEW_BLOCK":45},
  "PAPER_DESIGN":{"PAPER_DEVELOPMENT_GUIDANCE":160,"REVIEW_LESSON":130,"SCIENTIFIC_CLOSURE":105,"SEARCH_CLOSURE":95,"FAILURE_ASSET":90,"SUCCESS_ASSET":85,"HOLD":80,"OPEN_QUESTION":75,"REPEATED_REVIEW_BLOCK":70,"DISCOVERY_LESSON":55},
 }
 return weights.get(p,{}).get(k,0)
def _render(r):
 parts=[f"{r.get('memory_id')} | {r.get('kind')} | durability={r.get('durability_class')} | layer={r.get('affected_layer') or '-'}",f"title={_t(r.get('title'),420)}"]
 for key,label,lim in (("summary","lesson",900),("reusable_precheck","precheck",900),("reopen_condition","reopen",700),("opposite_search_seed","opposite_search_seed",700)):
  if _t(r.get(key),lim):parts.append(f"{label}={_t(r.get(key),lim)}")
 if r.get("source_refs"):parts.append("refs="+",".join(str(x) for x in r.get("source_refs")[:5]))
 return "\n  ".join(parts)

def compile_research_memory_query_pack(wiki:dict,*,purpose:str,context:Any=None,max_chars:int=8000,max_items:int=24)->dict:
 purpose=str(purpose or "").upper()
 if purpose not in PURPOSES:raise ValueError(f"unknown research-memory purpose:{purpose}")
 lint=wiki.get("lint") or lint_research_memory_wiki(wiki)
 if lint.get("status")!="PASS":raise ValueError("research memory wiki failed semantic lint")
 ct=_tokens(context or {});rank=[]
 for i,r in enumerate(wiki.get("entries") or []):
  if not isinstance(r,dict) or r.get("prompt_eligible") is not True or r.get("scientific_authority") is not False or r.get("durability_class")=="transient":continue
  k=str(r.get("kind") or "");w=_weight(k,purpose)
  if not w:continue
  rt=_tokens({x:r.get(x) for x in ("title","summary","scope","affected_layer","reusable_precheck","reopen_condition","opposite_search_seed","source_refs")});score=w+8*len(ct&rt)+(12 if k=="FAILURE_ASSET" and int((r.get("reuse_effectiveness") or {}).get("helped_count") or 0)>0 else 0)
  rank.append((score,-i,r))
 rank.sort(reverse=True,key=lambda x:(x[0],x[1]));budget=max(1200,min(int(max_chars),16000));cap=max(1,min(int(max_items),64));selected=[];chunks=[];used=0
 ordered=rank
 if purpose=="PAPER_DESIGN":
  guidance=next((item for item in rank if str(item[2].get("kind") or "")=="PAPER_DEVELOPMENT_GUIDANCE"),None)
  review=next((item for item in rank if str(item[2].get("kind") or "")=="REVIEW_LESSON"),None)
  reserved=[item for item in (guidance,review) if item is not None]
  if reserved:ordered=reserved+[item for item in rank if item not in reserved]
 reserved_kinds={"PAPER_DEVELOPMENT_GUIDANCE","REVIEW_LESSON"} if purpose=="PAPER_DESIGN" else set()
 reserved_cap=max(320,budget//3) if reserved_kinds else budget
 for score,_,r in ordered:
  if len(selected)>=cap:break
  kind=str(r.get("kind") or "");text=_render(r)
  if kind in reserved_kinds and len(text)>reserved_cap:text=text[:max(0,reserved_cap-1)].rstrip()+"…"
  extra=len(text)+(2 if chunks else 0)
  if chunks and used+extra>budget:
   if kind not in reserved_kinds:continue
   allowance=budget-used-(2 if chunks else 0)
   if allowance<220:continue
   text=text[:max(0,allowance-1)].rstrip()+"…";extra=len(text)+(2 if chunks else 0)
  if not chunks and extra>budget:text=text[:budget];extra=len(text)
  chunks.append(text);used+=extra;selected.append({"memory_id":r.get("memory_id"),"kind":kind,"durability_class":r.get("durability_class"),"affected_layer":r.get("affected_layer"),"score":score})
 text="\n\n".join(chunks);out={"schema_version":SCHEMA_VERSION,"purpose":purpose,"wiki_sha256":str(wiki.get("wiki_sha256") or ""),"selected_memory_ids":[str(r.get("memory_id") or "") for r in selected],"selected":selected,"text":text,"summary":{"selected":len(selected),"review_lessons_selected":sum(str(r.get("kind") or "")=="REVIEW_LESSON" for r in selected),"paper_development_guidance_selected":sum(str(r.get("kind") or "")=="PAPER_DEVELOPMENT_GUIDANCE" for r in selected),"available_prompt_eligible":sum(isinstance(r,dict) and r.get("prompt_eligible") is True and r.get("durability_class")!="transient" for r in wiki.get("entries") or []),"characters":len(text),"character_budget":budget,"transient_excluded":sum(isinstance(r,dict) and r.get("durability_class")=="transient" for r in wiki.get("entries") or [])},"policy":{"memory_is_context_not_scientific_verdict":True,"past_failure_is_not_automatic_veto":True,"past_success_is_not_automatic_generalization":True,"paper_review_pattern_is_precheck_not_verdict":True,"paper_review_pattern_cannot_authorize_experiments":True,"paper_design_reserves_review_lesson_when_available":purpose!="PAPER_DESIGN" or any(str(r.get("kind") or "")=="REVIEW_LESSON" for r in selected) or not any(isinstance(r,dict) and r.get("kind")=="REVIEW_LESSON" and r.get("prompt_eligible") is True and r.get("durability_class")!="transient" for r in wiki.get("entries") or []),"paper_development_guidance_is_precheck_not_scientific_verdict":True,"paper_development_guidance_cannot_authorize_experiments":True,"paper_design_reserves_development_guidance_when_available":purpose!="PAPER_DESIGN" or any(str(r.get("kind") or "")=="PAPER_DEVELOPMENT_GUIDANCE" for r in selected) or not any(isinstance(r,dict) and r.get("kind")=="PAPER_DEVELOPMENT_GUIDANCE" and r.get("prompt_eligible") is True and r.get("durability_class")!="transient" for r in wiki.get("entries") or []),"reopen_condition_requires_new_evidence":True,"transient_operational_noise_excluded":True,"downstream_scientific_gates_unchanged":True},"scientific_authority":False}
 out["query_pack_sha256"]=_sha({k:out[k] for k in ("schema_version","purpose","wiki_sha256","selected_memory_ids","text","policy")});return out

def load_research_memory_wiki(path:Path=DEFAULT_JSON)->dict:
 try:p=json.loads(path.read_text(encoding="utf-8"))
 except OSError as error:raise FileNotFoundError(f"research memory wiki unavailable:{path}") from error
 except json.JSONDecodeError as error:raise ValueError("research memory wiki JSON invalid") from error
 if not isinstance(p,dict) or lint_research_memory_wiki(p).get("status")!="PASS":raise ValueError("research memory wiki invalid")
 return p

def write_research_memory_wiki(wiki:dict,*,json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS)->None:
 if lint_research_memory_wiki(wiki).get("status")!="PASS":raise ValueError("cannot persist invalid research memory wiki")
 json_path.parent.mkdir(parents=True,exist_ok=True);json_path.write_text(json.dumps(wiki,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");js_path.write_text("window.RESEARCH_MEMORY_WIKI = "+json.dumps(wiki,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
