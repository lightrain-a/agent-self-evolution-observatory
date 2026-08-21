from __future__ import annotations
import hashlib,json,re
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
from .config import PROJECT_ROOT
from .paper_first_problem_search_portfolio import _jaccard,_maxmin_select,_score,_seed_key,recover_archived_formulation_payload

SCHEMA_VERSION="1.0-round3-branch-dag"
DEFAULT_JSON=PROJECT_ROOT/"generated/round3-provenance-manifest.json"
DEFAULT_JS=PROJECT_ROOT/"generated/round3-provenance-manifest.js"
DEFAULT_PORTFOLIO=PROJECT_ROOT/"generated/research-data/paper-first-problem-discovery/search-portfolios/20260820T141425Z-portfolio.json"
DEFAULT_RAW_DIR=PROJECT_ROOT/"generated/research-data/paper-first-problem-discovery/raw-generations"
DEFAULT_GENERATOR=PROJECT_ROOT/"generated/paper-first-problem-generator-state.json"
DEFAULT_TRANSACTION=PROJECT_ROOT/"generated/research-data/runs/paper-first-discovery-transactions/ed883b998c767cc6f47f77986c007a76be23a089ac9e7e274c71069e4b669de3.json"
POLICY={"manifest_is_derived_provenance_not_scientific_evidence":True,"model_rejection_is_search_disposition_not_scientific_failure":True,"missing_complete_output_object_is_provenance_event_not_rejection":True,"provider_or_serialization_failure_has_no_belief_authority":True,"branch_expansion_is_not_a_conservative_elimination_funnel":True,"manifest_cannot_authorize_problem_gate_method_experiment_p0_or_gpu":True}
AUTHORITY={k:False for k in ("claim_mutation","scientific_closure","problem_gate","method","experiment","p0","gpu")}

def _load(p):v=json.loads(Path(p).read_text());assert isinstance(v,dict);return v
def _fsha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def _sha(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def _now():return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def _dedup(raw):
 kept=[];exact={};out=[]
 for r in sorted(raw,key=_score,reverse=True):
  lane=str(r.get("discovery_lane") or "");exact.setdefault(lane,set());same=[p for p in kept if p.get("discovery_lane")==lane];key=_seed_key(r)
  exact_rep=next((p for p in same if _seed_key(p)==key),None);near=max(same,key=lambda p:_jaccard(r,p),default=None);sim=_jaccard(r,near) if near else 0.0
  if key in exact[lane]:decision,rep="DROP_EXACT_WITHIN_LANE_DUPLICATE",exact_rep
  elif sim>=.78:decision,rep="DROP_SEMANTIC_WITHIN_LANE_NEAR_DUPLICATE",near
  else:decision,rep="KEEP_SEMANTIC_UNIQUE",None;exact[lane].add(key);kept.append(r)
  out.append({"seed_id":r["seed_id"],"seed_sha256":_sha(r),"lane":lane,"decision":decision,"representative_seed_id":str((rep or {}).get("seed_id") or ""),"similarity":round(sim,4) if rep else 0.0,"belief_authority":False,"scientific_authority":False})
 return kept,out

def _pools(p):
 unique=list(p["unique_seeds"]);by={r["seed_id"]:r for r in unique};breadth=[by[x] for x in p["archives"]["breadth"]];c=p["config"]
 parents=_maxmin_select(breadth,min(int(c["evolution_parents"]),len(breadth)));evolved=list(p["evolved"]);repaired=list(p["repaired"]);source=repaired+evolved+parents;budget=min(int(c["formulation_budget"]),len(source))
 pool=_maxmin_select(source,budget,required_ids=[r["seed_id"] for r in repaired[:min(len(repaired),budget)]])
 return parents,evolved,pool

def build_round3_provenance_manifest(*,portfolio_path=DEFAULT_PORTFOLIO,raw_dir=DEFAULT_RAW_DIR,generator_path=DEFAULT_GENERATOR,transaction_path=DEFAULT_TRANSACTION):
 p=_load(portfolio_path);g=_load(generator_path);t=_load(transaction_path);rec=g.get("portfolio_ingestion_recovery") or {};psha=_fsha(portfolio_path)
 if t.get("status")!="COMMITTED" or t.get("scientific_authority") is not False:raise ValueError("transaction-not-committed-zero-authority")
 if t.get("transaction_id")!=rec.get("source_transaction_id") or psha!=rec.get("source_portfolio_sha256"):raise ValueError("transaction-or-portfolio-binding-mismatch")
 prov={str(x.get("role") or ""):x for x in g.get("portfolio_provenance") or [] if isinstance(x,dict)}
 raw=[x for x in p.get("raw_seeds") or [] if isinstance(x,dict)];byrole={}
 for s in raw:
  m=re.fullmatch(r"(.+)-P(\d+)-(\d+)",s["seed_id"])
  if not m:raise ValueError("raw-seed-role-missing")
  byrole.setdefault(f"expand-{m.group(1).lower()}-p{m.group(2)}",{})[int(m.group(3))]=s
 roles=sorted((x for x in prov if x.startswith("expand-")));size=int(p["config"]["expansion_shard_size"]);slots=[]
 for role in roles:
  receipt=prov[role];observed=byrole.get(role,{})
  for i in range(1,size+1):
   seed=observed.get(i);slots.append({"slot_id":f"{role}:slot-{i:03d}","role":role,"request_fingerprint":str(receipt.get("request_fingerprint") or ""),"raw_receipt_sha256":str(receipt.get("sha256") or ""),"seed_id":str((seed or {}).get("seed_id") or ""),"seed_sha256":_sha(seed) if seed else "","disposition":"VALID_RAW_SEED" if seed else "UNREALIZED_GENERATION_SLOT","failure_layer":"" if seed else "provider_or_serialization","belief_authority":False,"scientific_authority":False})
 unique,dedup=_dedup(raw);expected={x["seed_id"] for x in p["unique_seeds"]}
 if {x["seed_id"] for x in unique}!=expected:raise ValueError("dedup-replay-mismatch")
 logged={x["seed_id"] for x in p["duplicate_log"]}
 if any(x["decision"].startswith("DROP_") and x["seed_id"] not in logged for x in dedup):raise ValueError("dedup-receipt-missing")
 parents,evolved,pool=_pools(p);known={x["seed_id"] for x in [*p["unique_seeds"],*p["evolved"],*p["repaired"]]};branches=[]
 for stage,rows in (("SEMANTIC_UNIQUE_ROOT",p["unique_seeds"]),("EVOLVED_BRANCH",p["evolved"]),("REPAIR_CHILD",p["repaired"])):
  for row in rows:
   parent=str(row.get("parent_id") or "")
   if parent and parent not in known:raise ValueError("branch-parent-missing:"+parent)
   branches.append({"branch_id":row["seed_id"],"branch_sha256":_sha(row),"stage":stage,"parent_branch_id":parent,"scientific_authority":False})
 rrec={str(x.get("role") or ""):x for x in rec.get("formulation_receipts") or [] if isinstance(x,dict)};inputs=[];candidates=[];invalid=[];ordinal=0
 for off in range(0,len(pool),2):
  role=f"formulate-{off//2+1}";batch=pool[off:off+2];ids={x["seed_id"] for x in batch};rr=rrec.get(role) or {};rawsha=str(rr.get("source_raw_sha256") or "");matches=list(Path(raw_dir).glob(f"*-{role}-*-{rawsha[:12]}.txt"))
  if len(matches)!=1 or _fsha(matches[0])!=rawsha:raise ValueError("formulation-raw-mismatch:"+role)
  payload,audit=recover_archived_formulation_payload(matches[0].read_text(errors="replace"));live={};dead={}
  for x in payload.get("candidates") or []:
   sid=str(x.get("source_branch_id") or "")
   if sid not in ids:raise ValueError("candidate-source-outside-batch")
   live.setdefault(sid,[]).append(x)
  for x in payload.get("rejected") or []:
   sid=str(x.get("source_branch_id") or "")
   if sid not in ids:invalid.append({"role":role,"source_branch_id":sid,"rejection_object_sha256":_sha(x),"disposition":"INVALID_REJECTION_TARGET_NOT_IN_BATCH","scientific_authority":False});continue
   dead.setdefault(sid,[]).append(x)
  for branch in batch:
   sid=branch["seed_id"];yes=live.get(sid,[]);no=dead.get(sid,[])
   disposition="CONFLICTING_COMPLETE_OUTPUT_OBJECTS" if yes and no else ("RECOVERED_CANDIDATE" if yes else ("MODEL_REJECTED_ZERO_AUTHORITY" if no else "NO_COMPLETE_FORMULATION_OUTPUT_OBJECT"))
   row={"role":role,"source_branch_id":sid,"source_branch_sha256":_sha(branch),"raw_sha256":rawsha,"request_fingerprint":str(rr.get("request_fingerprint") or ""),"recovery_mode":audit["mode"],"disposition":disposition,"candidate_ids":[],"rejection_receipt_sha256":[_sha(x) for x in no],"belief_authority":False,"scientific_authority":False}
   for item in yes:
    ordinal+=1;cid=f"PORT-{ordinal:03d}";row["candidate_ids"].append(cid);candidates.append({"candidate_id":cid,"source_branch_id":sid,"candidate_object_sha256":_sha(item),"formulation_role":role,"formulation_raw_sha256":rawsha,"scientific_authority":False})
   inputs.append(row)
 pref0={x["candidate_id"]:x for x in g.get("pre_f0_candidates") or []};blocked={x["candidate_id"]:x for x in rec.get("blocked_rows") or []};routes=[]
 for c in candidates:
  cid=c["candidate_id"]
  if cid in pref0:route="PRE_F0_EVIDENCE_ACQUISITION";reason=str(pref0[cid].get("route_reason") or "");snapshot=str(pref0[cid].get("candidate_snapshot_sha256") or "")
  elif cid in blocked:route="MACHINE_BLOCKED";reason="|".join(str(x) for x in blocked[cid].get("blockers") or []);snapshot=""
  else:route="ROUTE_MISSING";reason="";snapshot=""
  routes.append({**c,"route":route,"route_reason_sha256":hashlib.sha256(reason.encode()).hexdigest() if reason else "","candidate_snapshot_sha256":snapshot,"route_receipt_sha256":_sha({"candidate_id":cid,"candidate_object_sha256":c["candidate_object_sha256"],"route":route,"reason":reason,"scientific_authority":False}),"belief_authority":False,"scientific_authority":False})
 summary={"requested_generation_slots":len(slots),"valid_raw_seeds":sum(x["disposition"]=="VALID_RAW_SEED" for x in slots),"unrealized_generation_slots":sum(x["disposition"]=="UNREALIZED_GENERATION_SLOT" for x in slots),"raw_seed_dispositions":len(dedup),"semantic_unique_kept":sum(x["decision"]=="KEEP_SEMANTIC_UNIQUE" for x in dedup),"dedup_dropped":sum(x["decision"].startswith("DROP_") for x in dedup),"branch_nodes":len(branches),"evolution_parents":len(parents),"evolved_branches":len(evolved),"repair_children":len(p["repaired"]),"formulation_inputs":len(inputs),"recovered_candidates":len(candidates),"model_rejected_zero_authority":sum(x["disposition"]=="MODEL_REJECTED_ZERO_AUTHORITY" for x in inputs),"inputs_without_complete_output_object":sum(x["disposition"]=="NO_COMPLETE_FORMULATION_OUTPUT_OBJECT" for x in inputs),"invalid_rejection_targets":len(invalid),"pre_f0_routes":sum(x["route"]=="PRE_F0_EVIDENCE_ACQUISITION" for x in routes),"machine_blocked_routes":sum(x["route"]=="MACHINE_BLOCKED" for x in routes),"route_missing":sum(x["route"]=="ROUTE_MISSING" for x in routes)}
 complete=bool(summary["requested_generation_slots"]==int(p["config"]["requested_raw_seeds"]) and summary["valid_raw_seeds"]==len(raw) and summary["raw_seed_dispositions"]==len(raw) and summary["semantic_unique_kept"]==len(expected) and summary["formulation_inputs"]==len(pool) and summary["recovered_candidates"]==int(rec["recovered_candidates"]) and summary["route_missing"]==0)
 state={"schema_version":SCHEMA_VERSION,"generated_at":_now(),"status":"ROUND3_PROVENANCE_COMPLETE" if complete else "ROUND3_PROVENANCE_INCOMPLETE","policy":dict(POLICY),"transaction":{"transaction_id":t["transaction_id"],"status":t["status"],"generator_receipt_sha256":str(t.get("generator_receipt_sha256") or ""),"source_pool_sha256":str(t.get("source_pool_sha256") or ""),"discovery_operator_version":str(t.get("discovery_operator_version") or "")},"source_artifacts":{"portfolio_sha256":psha,"ingestion_recovery_sha256":str(rec.get("recovery_sha256") or ""),"source_generator_run_id":str(rec.get("source_generator_run_id") or "")},"summary":summary,"coverage":{"generation_slots_receipted":len(slots)==summary["requested_generation_slots"],"raw_to_unique_dispositions_complete":len(dedup)==len(raw),"branch_parentage_complete":all(not x["parent_branch_id"] or x["parent_branch_id"] in known for x in branches),"formulation_input_dispositions_complete":len(inputs)==len(pool),"candidate_routes_complete":summary["route_missing"]==0,"record_level_lineage_complete":complete},"generation_slots":slots,"raw_seed_dispositions":dedup,"branch_nodes":branches,"formulation_inputs":inputs,"invalid_rejection_targets":invalid,"candidate_routes":routes,"scientific_authority":False,"authority":dict(AUTHORITY)}
 state["manifest_content_sha256"]=_sha({k:v for k,v in state.items() if k not in {"generated_at","manifest_content_sha256"}});errors=validate_round3_provenance_manifest(state)
 if errors:raise ValueError("invalid-round3-manifest:"+";".join(errors))
 return state

def validate_round3_provenance_manifest(s):
 errors=[]
 if s.get("status")!="ROUND3_PROVENANCE_COMPLETE" or s.get("scientific_authority") is not False:errors.append("manifest-status-or-authority")
 if (s.get("coverage") or {}).get("record_level_lineage_complete") is not True:errors.append("lineage-incomplete")
 if (s.get("transaction") or {}).get("status")!="COMMITTED":errors.append("transaction-not-committed")
 if any((s.get("authority") or {}).get(k) is not False for k in AUTHORITY):errors.append("authority-leak")
 for key in ("generation_slots","raw_seed_dispositions","branch_nodes","formulation_inputs","candidate_routes"):
  if any(not isinstance(x,dict) or x.get("scientific_authority") is not False for x in s.get(key) or []):errors.append("row-authority:"+key)
 expected=_sha({k:v for k,v in s.items() if k not in {"generated_at","manifest_content_sha256"}})
 if s.get("manifest_content_sha256")!=expected:errors.append("content-hash-mismatch")
 return errors

def write_round3_provenance_manifest(json_path=DEFAULT_JSON,js_path=DEFAULT_JS,**kwargs):
 s=build_round3_provenance_manifest(**kwargs);Path(json_path).write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n");Path(js_path).write_text("window.ROUND3_PROVENANCE_MANIFEST = "+json.dumps(s,ensure_ascii=False,separators=(",",":"))+";\n");return s

def load_round3_provenance_manifest(path=DEFAULT_JSON):
 if not Path(path).is_file():return {"schema_version":SCHEMA_VERSION,"status":"ROUND3_PROVENANCE_MISSING","policy":dict(POLICY),"summary":{},"coverage":{"record_level_lineage_complete":False},"scientific_authority":False,"authority":dict(AUTHORITY)}
 s=_load(path);errors=validate_round3_provenance_manifest(s)
 return s if not errors else {"schema_version":SCHEMA_VERSION,"status":"ROUND3_PROVENANCE_INVALID","errors":errors,"policy":dict(POLICY),"summary":s.get("summary") or {},"coverage":{"record_level_lineage_complete":False},"scientific_authority":False,"authority":dict(AUTHORITY)}

if __name__=="__main__":print(json.dumps(write_round3_provenance_manifest(),ensure_ascii=False,indent=2))
