from __future__ import annotations

import hashlib,json,os
from datetime import datetime,timezone
from pathlib import Path
from typing import Any,Callable

from .ark_provider import ArkResponsesClient,ArkSettings,extract_json_object
from .config import PROJECT_ROOT,StorageSettings
from .paper_first_fresh_saturation import REDUCTION_PATTERNS
from .paper_first_primary_evidence import load_private_primary_pool,private_primary_pool_path
from .paper_first_problem_discovery_contract import audit_problem_candidate
from .paper_first_problem_gate_queue import default_auto_inbox_path
from .paper_first_problem_generator_prompts import generator_prompt,reviewer_prompt
from .public_state_redaction import redact_private_paths

DEFAULT_JSON=PROJECT_ROOT/"generated"/"paper-first-problem-generator-state.json"
DEFAULT_JS=PROJECT_ROOT/"generated"/"paper-first-problem-generator-state.js"
GENERATOR_MODEL="ark-code-latest"; REVIEWER_MODEL="glm-5.2"; MAX_CANDIDATES=5; MAX_POOL_AGE_HOURS=36.0
Responder=Callable[...,dict[str,Any]]


def _now_dt(): return datetime.now(timezone.utc)
def _now(): return _now_dt().replace(microsecond=0).isoformat()
def _parse_iso(v):
    try:
        d=datetime.fromisoformat(str(v or "").replace("Z","+00:00")); return (d if d.tzinfo else d.replace(tzinfo=timezone.utc)).astimezone(timezone.utc)
    except ValueError:return None

def _root(s:StorageSettings): return s.data_root/"paper-first-problem-discovery"
def _sha(text:str): return hashlib.sha256(text.encode()).hexdigest()
def _pool_sha(pool):
    rows=[]
    for r in pool.get("records") or []:
        if not isinstance(r,dict): continue
        rows.append({
            "ref":r.get("ref"),
            "source_sha256":r.get("source_sha256"),
            "abstract_sha256":r.get("abstract_sha256"),
            "fulltext_sha256":r.get("fulltext_sha256"),
            "empirical_fact_sha256":[str(f.get("text_sha256") or "") for f in (r.get("empirical_facts") or []) if isinstance(f,dict)],
        })
    return hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def _registry(pool): return {str(r.get("ref")):r for r in pool.get("records") or [] if isinstance(r,dict) and r.get("primary_source_verified") is True and r.get("ref")}

def _archive_previous(storage,auto):
    if not auto.exists(): return ""
    try: raw=auto.read_bytes()
    except OSError:return ""
    if not raw:return ""
    sha=hashlib.sha256(raw).hexdigest(); d=_root(storage)/"archive"; d.mkdir(parents=True,exist_ok=True); p=d/f"auto-inbox-{sha[:16]}.json"
    if not p.exists():p.write_bytes(raw)
    return str(p)

def _write_raw(storage,run_id,role,model,text):
    d=_root(storage)/"raw-generations";d.mkdir(parents=True,exist_ok=True);sha=_sha(text);p=d/f"{run_id}-{role}-{model.replace('/','-')}-{sha[:12]}.txt";p.write_text(text,encoding="utf-8");return str(p),sha

def _write_inbox(path,run_id,status,candidates,pool_sha):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps({"schema_version":"1.0","generated_at":_now(),"generator_run_id":run_id,"status":status,"evidence_pool_sha256":pool_sha,"authority":{"paper":False,"method":False,"experiment":False,"p0":False,"gpu":False},"candidates":candidates},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def _saturation_ledger_path(storage:StorageSettings)->Path:
    return _root(storage)/"discovery-saturation-ledger.json"


def _negative_space_sha()->str:
    payload=[{"key":row.get("key"),"veto":row.get("veto"),"mature_theories":row.get("mature_theories")} for row in REDUCTION_PATTERNS]
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()


def _load_saturation_ledger(storage:StorageSettings)->list[dict[str,Any]]:
    path=_saturation_ledger_path(storage)
    try: payload=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError): return []
    rows=payload.get("runs") if isinstance(payload,dict) else None
    return [row for row in (rows or []) if isinstance(row,dict)]


def _record_saturation_run(storage:StorageSettings,state:dict[str,Any],pool_sha:str,registry:dict[str,dict[str,Any]])->None:
    if state.get("status") not in {"GENERATED_ZERO_CANDIDATES","GENERATED_AWAIT_PROBLEM_GATE"}: return
    ledger=_load_saturation_ledger(storage)
    raw=(state.get("raw_artifacts") or {}).get("generator") or {}
    key={"pool_sha256":pool_sha,"negative_space_sha256":_negative_space_sha(),"requested_model":state.get("generator_model"),"resolved_model":raw.get("resolved_model")}
    prior_identical=sum(
        row.get("status")=="GENERATED_ZERO_CANDIDATES" and all(row.get(k)==v for k,v in key.items())
        for row in ledger
    )
    entry={
        "run_id":state.get("run_id"),"generated_at":state.get("generated_at"),**key,
        "primary_evidence_records":len(registry),"source_refs":sorted(registry),"status":state.get("status"),
        "generated":(state.get("summary") or {}).get("generated",0),"semantic_clear":(state.get("summary") or {}).get("semantic_clear",0),
        "raw_sha256":raw.get("sha256"),"generation_notes":str(state.get("generation_notes") or "")[:2400],
        "scientific_authority":False,
    }
    ledger.append(entry); ledger=ledger[-200:]
    path=_saturation_ledger_path(storage); path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps({"schema_version":"1.0","runs":ledger},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    state["saturation_memory"]={"ledger_entries":len(ledger),"prior_identical_zero_runs":prior_identical,"current_run_recorded":True,"scientific_authority":False}

def _ark(*,prompt,model,max_output_tokens):
    s=ArkSettings.from_env(required=False)
    if not s.api_key: raise RuntimeError("ARK_API_KEY_NOT_CONFIGURED")
    s=ArkSettings(api_key=s.api_key,base_url=s.base_url,default_model=s.default_model,timeout_seconds=min(max(s.timeout_seconds,90.0),180.0),max_retries=0)
    return ArkResponsesClient(s).respond(prompt,model=model,max_output_tokens=max_output_tokens,temperature=0.0,thinking="disabled")

def _source(raw,key,reg):
    src=(raw.get("empirical_contradiction") or {}).get(key) or {};ref=str(src.get("ref") or "").strip();r=reg.get(ref) or {}
    return {"ref":ref,"title":str(r.get("title") or ""),"claim":str(src.get("claim") or "").strip(),"primary_source":bool(r),"primary_url":str(r.get("primary_url") or ""),"source_sha256":str(r.get("source_sha256") or "")}
def _normalize(raw,reg):
    c=raw.get("empirical_contradiction") or {};return {
        "candidate_id":str(raw.get("candidate_id") or "").strip(),"title":str(raw.get("title") or "").strip(),
        "empirical_contradiction":{"source_a":_source(raw,"source_a",reg),"source_b":_source(raw,"source_b",reg),"tension":str(c.get("tension") or "").strip()},
        "irreducible_object":str(raw.get("irreducible_object") or "").strip(),"mature_theory_baselines":raw.get("mature_theory_baselines") or [],
        "same_information_nonreducibility":raw.get("same_information_nonreducibility") or {},"exact_prediction":str(raw.get("exact_prediction") or "").strip(),
        "strongest_same_information_baseline":str(raw.get("strongest_same_information_baseline") or "").strip(),"domain_transfer_audit":raw.get("domain_transfer_audit") or {},
        "saturation_scan":raw.get("saturation_scan") or {"checked":False,"matched_patterns":[]},"cheapest_problem_falsifier":str(raw.get("cheapest_problem_falsifier") or "").strip(),
        "endpoint_headroom_requirement":str(raw.get("endpoint_headroom_requirement") or "").strip(),
        "semantic_reduction_review":{"reviewed":False,"block_only":True,"verdict":"BLOCK","reviewer_model":"","raw_sha256":"","source_claims_grounded":False,"source_claim_grounding":{},"matched_patterns":[],"strongest_reduction":"unreviewed"},
        "authority":{k:False for k in ("method_design","experiment_blueprint","local_validation","p0","gpu","full_experiment")}}
def _reviewable(c,reg):
    return bool(audit_problem_candidate(c,primary_evidence_by_ref=reg,require_primary_registry=True,require_semantic_review=False).get("passed"))
def _norm_text(value:str)->str:
    return " ".join(str(value or "").lower().split())

def _source_grounding(review:dict[str,Any],candidate:dict[str,Any],registry:dict[str,dict[str,Any]])->tuple[dict[str,Any],bool]:
    support=review.get("source_claim_support") or {};out={};all_grounded=True
    contradiction=candidate.get("empirical_contradiction") or {}
    for key in ("source_a","source_b"):
        source=contradiction.get(key) or {};ref=str(source.get("ref") or "").strip();record=registry.get(ref) or {}
        item=support.get(key) or {};supported=item.get("supported") is True;excerpt=str(item.get("evidence_excerpt") or "").strip();declared_source=str(item.get("evidence_source") or "").strip().lower()
        words=excerpt.split();excerpt_norm=_norm_text(excerpt);abstract=_norm_text(record.get("abstract") or "")
        facts=[_norm_text(str(fact.get("text") or "")) for fact in (record.get("empirical_facts") or []) if isinstance(fact,dict)]
        abstract_match=bool(excerpt_norm and excerpt_norm in abstract)
        fulltext_match=bool(excerpt_norm and any(excerpt_norm in fact for fact in facts))
        evidence_source="abstract" if abstract_match else ("fulltext" if fulltext_match else "")
        source_consistent=declared_source in {"","abstract","fulltext"} and (not declared_source or declared_source==evidence_source)
        excerpt_verified=bool(4<=len(words)<=30 and evidence_source and source_consistent)
        grounded=bool(supported and excerpt_verified and record.get("primary_source_verified") is True)
        out[key]={"ref":ref,"supported":supported,"evidence_source":evidence_source,"declared_evidence_source":declared_source,"evidence_excerpt":excerpt,"excerpt_verified":excerpt_verified,"grounded":grounded}
        all_grounded=all_grounded and grounded
    return out,all_grounded

def _apply_reviews(cands,payload,requested,resolved,generator_resolved,raw_sha,registry):
    by={str(r.get("candidate_id") or ""):r for r in (payload or {}).get("reviews") or [] if isinstance(r,dict)};known={r["key"] for r in REDUCTION_PATTERNS};ind=bool(resolved and resolved!=generator_resolved)
    for c in cands:
        r=by.get(c["candidate_id"]) or {};v=str(r.get("verdict") or "BLOCK").upper();matched=sorted({str(x) for x in r.get("matched_patterns") or [] if str(x) in known});grounding,grounded=_source_grounding(r,c,registry)
        if not ind or not grounded:v="BLOCK"
        c["semantic_reduction_review"]={"reviewed":bool(r) and bool(raw_sha),"block_only":True,"verdict":"CLEAR" if v=="CLEAR" and ind and grounded else "BLOCK","reviewer_model":resolved or requested,"reviewer_requested_model":requested,"generator_resolved_model":generator_resolved,"independent_resolved_model":ind,"raw_sha256":raw_sha,"source_claims_grounded":grounded,"source_claim_grounding":grounding,"matched_patterns":matched,"strongest_reduction":str(r.get("strongest_reduction") or ("reviewer-not-independent" if not ind else ("source-claim-grounding-failed" if not grounded else "review-unavailable"))),"reason":str(r.get("reason") or ""),"authority":False}
        if matched:
            scan=c.get("saturation_scan") or {};c["saturation_scan"]={"checked":True,"matched_patterns":sorted(set(list(scan.get("matched_patterns") or [])+matched))}
    return cands


def run_problem_generator(*,storage=None,primary_pool_path=None,auto_inbox_path=None,generator_model=None,reviewer_model=None,generator_responder:Responder|None=None,reviewer_responder:Responder|None=None,now=None,pool_max_age_hours=MAX_POOL_AGE_HOURS,max_candidates=MAX_CANDIDATES):
    storage=storage or StorageSettings.from_env();primary_pool_path=primary_pool_path or private_primary_pool_path(storage);auto_inbox_path=auto_inbox_path or default_auto_inbox_path(storage)
    generator_model=generator_model or os.getenv("PAPER_FIRST_PROBLEM_GENERATOR_MODEL",GENERATOR_MODEL);reviewer_model=reviewer_model or os.getenv("PAPER_FIRST_PROBLEM_REVIEW_MODEL",REVIEWER_MODEL);current=(now or _now_dt()).astimezone(timezone.utc);run_id=current.strftime("%Y%m%dT%H%M%SZ")
    archived=_archive_previous(storage,auto_inbox_path);pool=load_private_primary_pool(primary_pool_path) or {};reg=_registry(pool);psha=_pool_sha(pool) if pool else "";d=_parse_iso(pool.get("generated_at"));age=None if d is None else max(0.0,(current-d).total_seconds()/3600)
    state={"schema_version":"1.2","generated_at":_now(),"run_id":run_id,"primary_pool_path":str(primary_pool_path),"auto_inbox_path":str(auto_inbox_path),"archived_previous_auto_inbox":archived,"generator_model":generator_model,"reviewer_model":reviewer_model,"policy":{"zero_candidates_is_valid":True,"one_generator_call_max":True,"one_semantic_reviewer_call_max":True,"format_retry_forbidden":True,"thinking_disabled":True,"verified_primary_registry_required":True,"semantic_reviewer_is_block_only":True,"independent_reviewer_must_ground_both_source_claims_to_exact_primary_evidence_excerpts":True,"same_resolved_model_cannot_count_as_independent_review":True,"raw_model_output_archived_before_parsing":True,"generation_notes_are_advisory_not_scientific_authority":True,"zero_candidate_rationale_required":True,"discovery_saturation_memory_has_zero_scientific_authority":True,"candidate_inbox_has_zero_scientific_authority":True,"automatic_method_authority":False,"automatic_experiment_authority":False,"automatic_p0_authority":False},"summary":{"primary_evidence_records":len(reg),"generated":0,"structurally_reviewable":0,"semantic_clear":0,"semantic_blocked":0,"written_to_auto_inbox":0},"raw_artifacts":{},"generation_notes":"","saturation_memory":{"ledger_entries":len(_load_saturation_ledger(storage)),"prior_identical_zero_runs":0,"current_run_recorded":False,"scientific_authority":False},"candidates":[]}
    def finish(status,cands=[]): state["status"]=status;_write_inbox(auto_inbox_path,run_id,status,cands,psha);_record_saturation_run(storage,state,psha,reg);return state
    if pool.get("status")!="READY" or len(reg)<4:return finish("SKIPPED_INSUFFICIENT_PRIMARY_EVIDENCE")
    if age is None or age>pool_max_age_hours:state["primary_pool_age_hours"]=age;return finish("SKIPPED_STALE_PRIMARY_EVIDENCE")
    state["primary_pool_age_hours"]=round(age,4);call=generator_responder or _ark
    try:
        res=call(prompt=generator_prompt(list(reg.values())),model=generator_model,max_output_tokens=6500);raw=str(res.get("text") or "");p,sha=_write_raw(storage,run_id,"generator",generator_model,raw);resolved=str(res.get("resolved_model") or generator_model);state["raw_artifacts"]["generator"]={"path":p,"sha256":sha,"requested_model":generator_model,"resolved_model":resolved};payload=extract_json_object(raw);state["generation_notes"]=str(payload.get("generation_notes") or "")[:2400].strip();rows=payload.get("candidates") or []
        if not isinstance(rows,list) or len(rows)>max_candidates or any(not isinstance(r,dict) for r in rows):raise ValueError("generator-candidate-array-invalid")
        if not rows and not state["generation_notes"]:raise ValueError("zero-candidate-generation-notes-required")
    except Exception as e:state["error"]=f"{type(e).__name__}:{str(e)[:300]}";return finish("GENERATOR_ERROR_ZERO_AUTHORITY")
    cands=[_normalize(r,reg) for r in rows];reviewable=[c for c in cands if _reviewable(c,reg)];state["summary"].update({"generated":len(cands),"structurally_reviewable":len(reviewable)})
    if reviewable:
        call2=reviewer_responder or _ark
        try:
            res=call2(prompt=reviewer_prompt(reviewable,reg),model=reviewer_model,max_output_tokens=4200);raw=str(res.get("text") or "");p,sha=_write_raw(storage,run_id,"semantic-review",reviewer_model,raw);rresolved=str(res.get("resolved_model") or reviewer_model);state["raw_artifacts"]["semantic_reviewer"]={"path":p,"sha256":sha,"requested_model":reviewer_model,"resolved_model":rresolved};_apply_reviews(cands,extract_json_object(raw),reviewer_model,rresolved,resolved,sha,reg)
        except Exception as e:state["semantic_review_error"]=f"{type(e).__name__}:{str(e)[:300]}";_apply_reviews(cands,None,reviewer_model,"",resolved,"",reg)
    for c in cands:
        if c not in reviewable:c["semantic_reduction_review"].update({"reviewed":False,"verdict":"BLOCK","strongest_reduction":"structural-or-provenance-gate-failed"})
    clear=sum((c.get("semantic_reduction_review") or {}).get("verdict")=="CLEAR" for c in cands);state["summary"].update({"semantic_clear":clear,"semantic_blocked":len(cands)-clear,"written_to_auto_inbox":len(cands)});state["candidates"]=[{"candidate_id":c["candidate_id"],"title":c["title"],"source_refs":[c["empirical_contradiction"]["source_a"]["ref"],c["empirical_contradiction"]["source_b"]["ref"]],"semantic_verdict":c["semantic_reduction_review"]["verdict"],"matched_patterns":c["semantic_reduction_review"].get("matched_patterns") or []} for c in cands]
    return finish("GENERATED_ZERO_CANDIDATES" if not cands else "GENERATED_AWAIT_PROBLEM_GATE",cands)


def public_problem_generator_state(state:dict[str,Any],storage:StorageSettings|None=None)->dict[str,Any]:
    public=json.loads(json.dumps(state,ensure_ascii=False))
    for key in ("primary_pool_path","auto_inbox_path","archived_previous_auto_inbox"):
        public.pop(key,None)
    for artifact in (public.get("raw_artifacts") or {}).values():
        if isinstance(artifact,dict):artifact.pop("path",None)
    return redact_private_paths(public,storage=storage or StorageSettings.from_env())


def load_problem_generator_state(path:Path=DEFAULT_JSON):
    if not path.exists():
        return {"schema_version":"1.2","status":"NOT_RUN","policy":{"zero_candidates_is_valid":True,"semantic_reviewer_is_block_only":True,"generation_notes_are_advisory_not_scientific_authority":True,"zero_candidate_rationale_required":True,"discovery_saturation_memory_has_zero_scientific_authority":True,"candidate_inbox_has_zero_scientific_authority":True,"automatic_method_authority":False,"automatic_experiment_authority":False,"automatic_p0_authority":False},"summary":{"primary_evidence_records":0,"generated":0,"structurally_reviewable":0,"semantic_clear":0,"semantic_blocked":0,"written_to_auto_inbox":0},"generation_notes":"","saturation_memory":{"ledger_entries":0,"prior_identical_zero_runs":0,"current_run_recorded":False,"scientific_authority":False},"candidates":[],"raw_artifacts":{}}
    try:p=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError):return {"schema_version":"1.2","status":"STATE_UNREADABLE","policy":{"zero_candidates_is_valid":True,"semantic_reviewer_is_block_only":True,"generation_notes_are_advisory_not_scientific_authority":True,"zero_candidate_rationale_required":True,"discovery_saturation_memory_has_zero_scientific_authority":True,"candidate_inbox_has_zero_scientific_authority":True,"automatic_method_authority":False,"automatic_experiment_authority":False,"automatic_p0_authority":False},"summary":{"primary_evidence_records":0,"generated":0,"structurally_reviewable":0,"semantic_clear":0,"semantic_blocked":0,"written_to_auto_inbox":0},"generation_notes":"","saturation_memory":{"ledger_entries":0,"prior_identical_zero_runs":0,"current_run_recorded":False,"scientific_authority":False},"candidates":[],"raw_artifacts":{}}
    return p if isinstance(p,dict) else {"schema_version":"1.0","status":"STATE_INVALID","policy":{},"summary":{},"candidates":[],"raw_artifacts":{}}


def write_problem_generator_state(json_path=DEFAULT_JSON,js_path=DEFAULT_JS,**kwargs):
    state=run_problem_generator(**kwargs);public=public_problem_generator_state(state,storage=kwargs.get("storage"));json_path.parent.mkdir(parents=True,exist_ok=True);json_path.write_text(json.dumps(public,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");js_path.write_text("window.PAPER_FIRST_PROBLEM_GENERATOR = "+json.dumps(public,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8");return state

if __name__=="__main__":print(json.dumps(write_problem_generator_state(),ensure_ascii=False))
