from __future__ import annotations

import hashlib,json,os,re
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from typing import Any,Callable

from .ark_provider import ArkResponsesClient,ArkSettings,extract_json_object
from .config import PROJECT_ROOT,StorageSettings
from .paper_first_fresh_saturation import REDUCTION_PATTERNS, reduction_pattern_audit
from .paper_first_primary_evidence import load_private_primary_pool,private_primary_pool_path
from .paper_first_problem_discovery_contract import DISCOVERY_LANES, DISCOVERY_OPERATOR_VERSION, SEARCH_PORTFOLIO_PRIMITIVES, FORBIDDEN_DISCOVERY_LANES, LANE_DISTINCT_SOURCE_MINIMUM, audit_problem_candidate
from .paper_first_problem_gate_queue import default_auto_inbox_path
from .paper_first_problem_generator_prompts import generator_prompt,reviewer_prompt
from .paper_first_problem_search_portfolio import DEFAULT_RAW_SEEDS, run_search_portfolio
from .premium_model_policy import preferred_model, stage_model_priority
from .public_state_redaction import redact_private_paths

DEFAULT_JSON=PROJECT_ROOT/"generated"/"paper-first-problem-generator-state.json"
DEFAULT_JS=PROJECT_ROOT/"generated"/"paper-first-problem-generator-state.js"
PORTABLE_REVIEW_RECEIPT_LIMIT=64
PORTABLE_BLOCKED_MEMORY_LIMIT=24
GENERATOR_MODEL=preferred_model("problem_generation"); REVIEWER_MODEL=preferred_model("semantic_review"); MAX_CANDIDATES=5; MAX_POOL_AGE_HOURS=36.0
Responder=Callable[...,dict[str,Any]]


def _now_dt(): return datetime.now(timezone.utc)
def _now(): return _now_dt().replace(microsecond=0).isoformat()
def _parse_iso(v):
    try:
        d=datetime.fromisoformat(str(v or "").replace("Z","+00:00")); return (d if d.tzinfo else d.replace(tzinfo=timezone.utc)).astimezone(timezone.utc)
    except ValueError:return None

def _root(s:StorageSettings): return s.data_root/"paper-first-problem-discovery"
def _sha(text:str): return hashlib.sha256(text.encode()).hexdigest()
def _provider_request_audit(*,stage:str,prompt:str,model:str,max_output_tokens:int,temperature:float)->dict[str,Any]:
    thinking_profile="provider-default" if str(model).lower().startswith("glm") else "disabled"
    material={"stage":stage,"prompt_sha256":_sha(prompt),"requested_model":str(model),"max_output_tokens":int(max_output_tokens),"temperature":float(temperature),"thinking_profile":thinking_profile}
    return {**material,"request_fingerprint":_sha(json.dumps(material,sort_keys=True,separators=(",",":"),ensure_ascii=False)),"scientific_authority":False}
def _provider_error_audit(error:Exception)->dict[str,Any]:
    text=str(error or "");match=re.search(r"Ark HTTP\s+(\d{3})",text,re.IGNORECASE)
    return {"exception_type":type(error).__name__,"http_status":int(match.group(1)) if match else None,"detail_sha256":_sha(text),"scientific_authority":False}
def _provider_orphan_path(storage:StorageSettings,request_fingerprint:str)->Path:
    return _root(storage)/"provider-orphans"/f"{request_fingerprint}.json"
def _provider_orphan_exists(storage:StorageSettings,request_fingerprint:str)->bool:
    return _provider_orphan_path(storage,request_fingerprint).exists()
def _archive_provider_orphans(storage:StorageSettings,run_id:str,stage:str,attempts:list[dict[str,Any]]|None)->list[dict[str,Any]]:
    audits=[]
    for row in attempts or []:
        if not isinstance(row,dict) or row.get("error_kind")!="transport-timeout-or-connection" or row.get("provider_receipt"): continue
        fingerprint=str(row.get("request_fingerprint") or "").strip()
        if len(fingerprint)!=64: continue
        audit={"request_fingerprint":fingerprint,"status":"ORPHANED_POST_NO_RECEIPT","requested_model":str(row.get("requested_model") or ""),"stage":stage,"scientific_authority":False}
        path=_provider_orphan_path(storage,fingerprint);path.parent.mkdir(parents=True,exist_ok=True)
        if not path.exists():
            payload={"schema_version":"1.0","generated_at":_now(),"run_id":run_id,"stage":stage,"status":"ORPHANED_POST_NO_RECEIPT","request_audit":{key:row.get(key) for key in ("request_fingerprint","prompt_sha256","requested_model","max_output_tokens","temperature","thinking_profile")},"provider_error_audit":row.get("provider_error_audit") or {},"replay_policy":"BLOCK_AUTOMATIC_REPLAY_UNTIL_EXPLICIT_OPERATOR_OVERRIDE","scientific_authority":False,"authority":{"paper":False,"method":False,"experiment":False,"p0":False,"gpu":False}}
            path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        audits.append(audit)
    return audits
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
            "typed_evidence_sha256":{key:[str(f.get("text_sha256") or "") for f in ((r.get("typed_evidence") or {}).get(key) or []) if isinstance(f,dict)] for key in ("operational_assumptions","measured_failures","boundary_observations")},
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


def _archive_provider_receipts(storage:StorageSettings,run_id:str,stage:str,attempts:list[dict[str,Any]]|None)->tuple[list[dict[str,Any]],list[dict[str,Any]]]:
    """Persist exact provider response IDs privately and return public-safe transport attempts.

    A provider response ID is operational recovery material, not public scientific state. The
    returned attempts replace it with a content fingerprint so a disconnected run can be audited
    without exposing or depending on the raw provider identifier.
    """
    sanitized=[];audits=[];private_dir=_root(storage)/"provider-receipts"
    for row in attempts or []:
        if not isinstance(row,dict): continue
        public_row=dict(row);receipt=public_row.pop("provider_receipt",None)
        if isinstance(receipt,dict) and str(receipt.get("response_id") or "").strip():
            receipt=dict(receipt);receipt_text=json.dumps(receipt,sort_keys=True,separators=(",",":"),ensure_ascii=False);receipt_sha=_sha(receipt_text)
            payload={"schema_version":"1.0","generated_at":_now(),"run_id":run_id,"stage":stage,"provider_receipt":receipt,"provider_receipt_sha256":receipt_sha,"scientific_authority":False,"authority":{"paper":False,"method":False,"experiment":False,"p0":False,"gpu":False}}
            private_dir.mkdir(parents=True,exist_ok=True);path=private_dir/f"{run_id}-{stage}-{receipt_sha[:12]}.json"
            if not path.exists(): path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            audit={"provider_receipt_sha256":receipt_sha,"status":str(receipt.get("status") or ""),"requested_model":str(receipt.get("requested_model") or public_row.get("requested_model") or ""),"resolved_model":str(receipt.get("resolved_model") or ""),"incomplete_reason":str(receipt.get("incomplete_reason") or ""),"scientific_authority":False}
            public_row["provider_receipt_audit"]=audit;audits.append(audit)
        sanitized.append(public_row)
    return sanitized,audits


def _write_inbox(path,run_id,status,candidates,pool_sha):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps({"schema_version":"2.0","generated_at":_now(),"generator_run_id":run_id,"status":status,"evidence_pool_sha256":pool_sha,"authority":{"paper":False,"method":False,"experiment":False,"p0":False,"gpu":False},"candidates":candidates},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def _saturation_ledger_path(storage:StorageSettings)->Path:
    return _root(storage)/"discovery-saturation-ledger.json"


def _negative_space_sha()->str:
    payload=[{"key":row.get("key"),"veto":row.get("veto"),"mature_theories":row.get("mature_theories"),"audit_class":row.get("audit_class")} for row in reduction_pattern_audit()]
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()


def _load_saturation_ledger(storage:StorageSettings,path:Path|None=None)->list[dict[str,Any]]:
    path=Path(path) if path is not None else _saturation_ledger_path(storage)
    try: payload=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError): return []
    rows=payload.get("runs") if isinstance(payload,dict) else None
    return [row for row in (rows or []) if isinstance(row,dict)]


def _blocked_memory_signature(row:dict[str,Any])->str:
    material={
        "lane":str(row.get("discovery_lane") or ""),
        "title":" ".join(str(row.get("title") or "").lower().split()),
        "matched_patterns":sorted(str(x) for x in row.get("matched_patterns") or [] if str(x)),
        "strongest_reduction":" ".join(str(row.get("strongest_reduction") or "").lower().split())[:500],
    }
    return hashlib.sha256(json.dumps(material,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()[:20]


def _local_blocked_problem_rows(storage:StorageSettings)->list[dict[str,Any]]:
    root=_root(storage); paths=list((root/"archive").glob("auto-inbox-*.json"))
    current=root/"auto-candidate-inbox.json"
    if current.exists(): paths.append(current)
    rows=[];seen=set()
    for path in sorted(paths):
        try: payload=json.loads(path.read_text(encoding="utf-8"))
        except (OSError,json.JSONDecodeError): continue
        run_id=str(payload.get("generator_run_id") or "").strip()
        for candidate in payload.get("candidates") or []:
            if not isinstance(candidate,dict): continue
            review=candidate.get("semantic_reduction_review") or {}
            if str(review.get("verdict") or "").upper()!="BLOCK": continue
            cid=str(candidate.get("candidate_id") or "").strip();dedup=(run_id,cid)
            if dedup in seen: continue
            seen.add(dedup)
            evidence=candidate.get("empirical_evidence") or {}
            source_refs=[str((evidence.get(k) or {}).get("ref") or "").strip() for k in ("source_a","source_b")]
            row={
                "run_id":run_id,"candidate_id":cid,"title":str(candidate.get("title") or "")[:240],
                "discovery_lane":str(candidate.get("discovery_lane") or "").strip().upper(),
                "source_refs":[ref for ref in source_refs if ref],
                "lane_contract_verified":review.get("lane_contract_verified") is True,
                "source_claims_grounded":review.get("source_claims_grounded") is True,
                "matched_patterns":sorted({str(x) for x in review.get("matched_patterns") or [] if str(x)}),
                "strongest_reduction":str(review.get("strongest_reduction") or "")[:600],
                "reason":str(review.get("reason") or "")[:1000],
                "scientific_authority":False,
            }
            row["signature_id"]=_blocked_memory_signature(row);rows.append(row)
    return rows


def _public_blocked_problem_memory(storage:StorageSettings,previous_public_state_path:Path|None=None)->dict[str,Any]:
    local=_local_blocked_problem_rows(storage)
    inherited=[]
    if previous_public_state_path is not None and previous_public_state_path.exists():
        try: previous=json.loads(previous_public_state_path.read_text(encoding="utf-8"))
        except (OSError,json.JSONDecodeError): previous={}
        previous_saturation=previous.get("saturation_memory") or {}; previous_memory=previous_saturation.get("blocked_problem_memory") or {}
        inherited_rows=previous_memory.get("portable_blocked_problem_memory") or previous_saturation.get("portable_blocked_problem_memory") or []
        inherited=[dict(row) for row in inherited_rows if isinstance(row,dict)]
    # Keep portable memory compact: no private excerpts/reviewer prose, only search-control fingerprints.
    portable_by_sig={}
    for row in inherited:
        sig=str(row.get("signature_id") or "").strip()
        if sig and row.get("scientific_authority") is False: portable_by_sig[sig]=row
    for row in local:
        public_row={key:row.get(key) for key in ("signature_id","title","discovery_lane","matched_patterns","strongest_reduction","lane_contract_verified","source_claims_grounded")}
        public_row["scientific_authority"]=False;portable_by_sig[row["signature_id"]]=public_row
    portable=list(portable_by_sig.values())[-PORTABLE_BLOCKED_MEMORY_LIMIT:]
    all_rows=portable
    lanes=Counter(str(row.get("discovery_lane") or "OTHER") for row in all_rows)
    pattern_counts=Counter(str(pattern) for row in all_rows for pattern in row.get("matched_patterns") or [] if str(pattern))
    reduction_counts=Counter(str(row.get("strongest_reduction") or "") for row in all_rows if str(row.get("strongest_reduction") or ""))
    grounded=sum(row.get("source_claims_grounded") is True for row in all_rows);lane_ok=sum(row.get("lane_contract_verified") is True for row in all_rows)
    top_pattern,top_count=(pattern_counts.most_common(1)[0] if pattern_counts else ("",0));attempts=len(all_rows)
    repeated=bool(top_count>=3 and top_count/max(attempts,1)>=0.4)
    return {
        "blocked_candidate_attempts":attempts,"lane_contract_verified_blocks":lane_ok,"source_grounded_blocks":grounded,
        "blocked_by_lane":dict(lanes),"reduction_pattern_counts":dict(pattern_counts),"strongest_reduction_counts":dict(reduction_counts),
        "top_reduction_basin":{"pattern":top_pattern,"count":top_count,"fraction":round(top_count/max(attempts,1),4) if attempts else 0.0},
        "repeated_reduction_basin":repeated,"search_escape_required":repeated,
        "portable_blocked_problem_memory":portable,"scientific_authority":False,
    }


def _private_dead_end_prompt_memory(storage:StorageSettings,public_memory:dict[str,Any])->dict[str,Any]:
    local=_local_blocked_problem_rows(storage)
    examples=[]
    for row in local[-12:]:
        examples.append({key:row.get(key) for key in ("title","discovery_lane","source_refs","matched_patterns","strongest_reduction","reason","lane_contract_verified","source_claims_grounded")})
    blocked_by_lane={str(key):int(value or 0) for key,value in (public_memory.get("blocked_by_lane") or {}).items()}
    lane_search_priority=sorted(DISCOVERY_LANES,key=lambda lane:(blocked_by_lane.get(lane,0),DISCOVERY_LANES.index(lane)))
    return {
        "summary":{key:public_memory.get(key) for key in ("blocked_candidate_attempts","blocked_by_lane","reduction_pattern_counts","top_reduction_basin","repeated_reduction_basin")},
        "lane_search_priority":lane_search_priority,
        "recent_blocked_examples":examples,
        "scientific_authority":False,
    }


def _is_current_operator_receipt(row:dict[str,Any],pool_sha:str,negative_space_sha:str)->bool:
    return bool(
        row.get("status") in {"GENERATED_ZERO_CANDIDATES","GENERATED_AWAIT_PROBLEM_GATE"}
        and row.get("pool_sha256")==pool_sha
        and row.get("negative_space_sha256")==negative_space_sha
        and row.get("discovery_operator_version")==DISCOVERY_OPERATOR_VERSION
        and row.get("scientific_authority") is False
    )


def _has_current_operator_receipt(storage:StorageSettings,pool_sha:str,portable_receipts:list[dict[str,Any]]|None=None,saturation_ledger_path:Path|None=None)->bool:
    negative_space_sha=_negative_space_sha()
    rows=[*_load_saturation_ledger(storage,saturation_ledger_path),*[row for row in (portable_receipts or []) if isinstance(row,dict)]]
    return any(_is_current_operator_receipt(row,pool_sha,negative_space_sha) for row in rows)


def _record_saturation_run(storage:StorageSettings,state:dict[str,Any],pool_sha:str,registry:dict[str,dict[str,Any]],saturation_ledger_path:Path|None=None)->None:
    if state.get("status") not in {"GENERATED_ZERO_CANDIDATES","GENERATED_AWAIT_PROBLEM_GATE"}: return
    ledger=_load_saturation_ledger(storage,saturation_ledger_path)
    raw=(state.get("raw_artifacts") or {}).get("generator") or {}
    key={"pool_sha256":pool_sha,"negative_space_sha256":_negative_space_sha(),"discovery_operator_version":DISCOVERY_OPERATOR_VERSION,"requested_model":state.get("generator_model"),"resolved_model":raw.get("resolved_model")}
    prior_identical=sum(row.get("status")=="GENERATED_ZERO_CANDIDATES" and all(row.get(k)==v for k,v in key.items()) for row in ledger)
    entry={"run_id":state.get("run_id"),"generated_at":state.get("generated_at"),**key,"primary_evidence_records":len(registry),"source_refs":sorted(registry),"status":state.get("status"),"generated":(state.get("summary") or {}).get("generated",0),"semantic_clear":(state.get("summary") or {}).get("semantic_clear",0),"raw_sha256":raw.get("sha256"),"generation_notes":str(state.get("generation_notes") or "")[:2400],"scientific_authority":False}
    ledger.append(entry);ledger=ledger[-200:]
    path=Path(saturation_ledger_path) if saturation_ledger_path is not None else _saturation_ledger_path(storage);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps({"schema_version":"1.0","runs":ledger},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    receipt={
        "run_id":str(state.get("run_id") or ""),
        "pool_sha256":pool_sha,
        "negative_space_sha256":key["negative_space_sha256"],
        "discovery_operator_version":DISCOVERY_OPERATOR_VERSION,
        "source_refs":sorted(registry),
        "status":str(state.get("status") or ""),
        "requested_model":state.get("generator_model"),
        "resolved_model":raw.get("resolved_model"),
        "raw_sha256":raw.get("sha256"),
        "scientific_authority":False,
    }
    prior_saturation=state.get("saturation_memory") or {}
    inherited=[dict(row) for row in prior_saturation.get("portable_review_receipts") or [] if isinstance(row,dict)]
    state["saturation_memory"]={"ledger_entries":len(ledger),"prior_identical_zero_runs":prior_identical,"current_run_recorded":True,"current_review_receipt":receipt,"portable_review_receipts":inherited[-PORTABLE_REVIEW_RECEIPT_LIMIT:],"blocked_problem_memory":prior_saturation.get("blocked_problem_memory") or {"blocked_candidate_attempts":0,"portable_blocked_problem_memory":[],"scientific_authority":False},"scientific_authority":False}


def _transport_no_output_error(error: Exception) -> str:
    text=str(error or "").lower()
    if "response incomplete before assistant output" in text: return "provider-incomplete-before-output"
    if "neither assistant output_text nor function_call" in text: return "provider-empty-output"
    if any(token in text for token in ("timed out","timeout","connectionerror","connection error","remote disconnected","connection reset")): return "transport-timeout-or-connection"
    if any(token in text for token in ("ark http 408","ark http 429","ark http 500","ark http 502","ark http 503","ark http 504")): return "provider-retryable-http"
    return ""


def _ark(*,prompt,model,max_output_tokens,temperature=0.0,stage="problem_generation",allow_transport_fallback=True):
    base=ArkSettings.from_env(required=False)
    if not base.api_key: raise RuntimeError("ARK_API_KEY_NOT_CONFIGURED")
    settings=ArkSettings(api_key=base.api_key,base_url=base.base_url,default_model=base.default_model,timeout_seconds=min(max(base.timeout_seconds,90.0),180.0),max_retries=0)
    priorities=list(stage_model_priority(stage))
    candidates=[model] if not allow_transport_fallback else [model]+[candidate for candidate in priorities if candidate!=model][:1]
    attempts=[]
    for index,candidate in enumerate(candidates):
        request_audit=_provider_request_audit(stage=stage,prompt=prompt,model=candidate,max_output_tokens=max_output_tokens,temperature=temperature)
        try:
            thinking=None if str(candidate).lower().startswith("glm") else "disabled"
            result=ArkResponsesClient(settings).respond(prompt,model=candidate,max_output_tokens=max_output_tokens,temperature=temperature,thinking=thinking,store=True,allow_thinking_compatibility_fallback=allow_transport_fallback)
            attempts.append({**request_audit,"requested_model":candidate,"status":"success","resolved_model":str(result.get("resolved_model") or candidate),"assistant_output_present":True})
            return {**result,"logical_requested_model":model,"transport_attempts":attempts,"transport_fallback_used":index>0,"transport_fallback_stage":stage}
        except Exception as error:
            kind=_transport_no_output_error(error)
            response_id=str(getattr(error,"response_id","") or "")
            response_status=str(getattr(error,"response_status","") or "")
            receipt={
                "response_id":response_id,
                "status":response_status,
                "requested_model":str(getattr(error,"requested_model",candidate) or candidate),
                "resolved_model":str(getattr(error,"resolved_model",candidate) or candidate),
                "incomplete_reason":str(getattr(error,"incomplete_reason","") or ""),
            } if response_id else None
            attempt={**request_audit,"requested_model":candidate,"status":"error-no-output","error_kind":kind or "non-retryable-provider-error","assistant_output_present":False,"provider_error_audit":_provider_error_audit(error)}
            if receipt is not None:
                attempt["provider_receipt"]=receipt
            attempts.append(attempt)
            if response_id and response_status in {"queued","in_progress"}:
                pending=RuntimeError(
                    "Ark provider response is pending; re-POST forbidden;"
                    f" requested_model={candidate}; status={response_status}"
                )
                pending.provider_receipt=receipt
                pending.transport_attempts=attempts
                raise pending from error
            if not kind or index>=len(candidates)-1:
                detail=";".join(f"{row['requested_model']}:{row.get('error_kind') or row['status']}" for row in attempts)
                final=RuntimeError(f"Ark provider failed before an auditable assistant output; attempts={detail}")
                final.transport_attempts=attempts
                if receipt is not None:
                    final.provider_receipt=receipt
                raise final from error

def _source(raw,key,reg):
    src=(raw.get("empirical_evidence") or {}).get(key) or {};ref=str(src.get("ref") or "").strip();r=reg.get(ref) or {}
    return {"ref":ref,"title":str(r.get("title") or ""),"claim":str(src.get("claim") or "").strip(),"evidence_role":str(src.get("evidence_role") or "").strip().upper(),"primary_source":bool(r),"primary_url":str(r.get("primary_url") or ""),"source_sha256":str(r.get("source_sha256") or "")}
def _normalize_saturation_scan(raw_scan):
    scan=raw_scan if isinstance(raw_scan,dict) else {}
    known={str(row.get("key") or "") for row in REDUCTION_PATTERNS}
    matched=[];pending=[];rejected=[];invalid=[]
    for value in scan.get("matched_patterns") or []:
        text=str(value or "").strip()
        if not text: continue
        if text in known:
            matched.append(text);continue
        key=next((candidate for candidate in known if text.startswith(candidate+" ") or text.startswith(candidate+":") or text.startswith(candidate+"—") or text.startswith(candidate+"-")),"")
        if key and "reject" in text[len(key):].lower():
            rejected.append({"key":key,"reason":text[len(key):].strip(" :-—")});continue
        invalid.append(text)
    for row in scan.get("pending_patterns") or []:
        if not isinstance(row,dict): invalid.append(str(row));continue
        key=str(row.get("key") or "").strip();test=str(row.get("exact_reduction_test") or "").strip();reason=str(row.get("reason") or "").strip()
        if key in known and (test or reason): pending.append({"key":key,"exact_reduction_test":test,"reason":reason})
        else: invalid.append(json.dumps(row,ensure_ascii=False,sort_keys=True))
    for row in scan.get("rejected_patterns") or []:
        if not isinstance(row,dict): invalid.append(str(row));continue
        key=str(row.get("key") or "").strip();reason=str(row.get("reason") or "").strip()
        if key in known and reason: rejected.append({"key":key,"reason":reason})
        else: invalid.append(json.dumps(row,ensure_ascii=False,sort_keys=True))
    dedup_rejected=[];seen=set()
    for row in rejected:
        signature=(row["key"],row["reason"])
        if signature not in seen: seen.add(signature);dedup_rejected.append(row)
    return {"checked":scan.get("checked") is True,"matched_patterns":sorted(set(matched)),"pending_patterns":pending,"rejected_patterns":dedup_rejected,"invalid_entries":invalid}


def _normalize(raw,reg):
    evidence=raw.get("empirical_evidence") or {};lane=str(raw.get("discovery_lane") or "").strip().upper();lane_evidence=raw.get("lane_evidence") or {}
    return {
        "candidate_id":str(raw.get("candidate_id") or "").strip(),"title":str(raw.get("title") or "").strip(),"discovery_lane":lane,
        "empirical_evidence":{"source_a":_source(raw,"source_a",reg),"source_b":_source(raw,"source_b",reg),"relation":str(evidence.get("relation") or "").strip()},
        "lane_evidence":dict(lane_evidence) if isinstance(lane_evidence,dict) else {},
        "source_branch_id":str(raw.get("source_branch_id") or "").strip(),"branch_depth":int(raw.get("branch_depth") or 0),
        "irreducible_object":str(raw.get("irreducible_object") or "").strip(),"novelty_category":str(raw.get("novelty_category") or "").strip(),
        "closest_work":dict(raw.get("closest_work") or {}) if isinstance(raw.get("closest_work"),dict) else {},"closest_work_distance":raw.get("closest_work_distance"),
        "mature_theory_baselines":raw.get("mature_theory_baselines") or [],"reduction_falsifiability_contract":raw.get("reduction_falsifiability_contract") or {},
        "same_information_nonreducibility":raw.get("same_information_nonreducibility") or {},"exact_prediction":str(raw.get("exact_prediction") or "").strip(),
        "strongest_same_information_baseline":str(raw.get("strongest_same_information_baseline") or "").strip(),"domain_transfer_audit":raw.get("domain_transfer_audit") or {},
        "saturation_scan":_normalize_saturation_scan(raw.get("saturation_scan")),"cheapest_problem_falsifier":str(raw.get("cheapest_problem_falsifier") or "").strip(),
        "endpoint_headroom_requirement":str(raw.get("endpoint_headroom_requirement") or "").strip(),"importance":str(raw.get("importance") or "").strip(),"likely_iclr_story":str(raw.get("likely_iclr_story") or "").strip(),
        "semantic_reduction_review":{"reviewed":False,"block_only":True,"verdict":"BLOCK","reviewer_model":"","raw_sha256":"","source_claims_grounded":False,"source_claim_grounding":{},"lane_contract_verified":False,"lane_contract_reason":"unreviewed","matched_patterns":[],"strongest_reduction":"unreviewed"},
        "authority":{k:False for k in ("method_design","experiment_blueprint","local_validation","p0","gpu","full_experiment")}}
def _reviewable(c,reg):
    return bool(audit_problem_candidate(c,primary_evidence_by_ref=reg,require_primary_registry=True,require_semantic_review=False).get("passed"))
def _norm_text(value:str)->str:
    return " ".join(str(value or "").lower().split())

def _source_grounding(review:dict[str,Any],candidate:dict[str,Any],registry:dict[str,dict[str,Any]])->tuple[dict[str,Any],bool]:
    support=review.get("source_claim_support") or {};out={};all_grounded=True
    evidence=candidate.get("empirical_evidence") or {}
    for key in ("source_a","source_b"):
        source=evidence.get(key) or {};ref=str(source.get("ref") or "").strip();record=registry.get(ref) or {}
        item=support.get(key) or {};supported=item.get("supported") is True;excerpt=str(item.get("evidence_excerpt") or "").strip();declared_source=str(item.get("evidence_source") or "").strip().lower()
        words=excerpt.split();excerpt_norm=_norm_text(excerpt);abstract=_norm_text(record.get("abstract") or "");role=str(source.get("evidence_role") or "").strip().upper()
        facts=[_norm_text(str(fact.get("text") or "")) for fact in (record.get("empirical_facts") or []) if isinstance(fact,dict)]
        typed=record.get("typed_evidence") or {};assumptions=[_norm_text(str(fact.get("text") or "")) for fact in typed.get("operational_assumptions") or [] if isinstance(fact,dict)];failures=[_norm_text(str(fact.get("text") or "")) for fact in typed.get("measured_failures") or [] if isinstance(fact,dict)];boundaries=[_norm_text(str(fact.get("text") or "")) for fact in typed.get("boundary_observations") or [] if isinstance(fact,dict)]
        abstract_match=bool(excerpt_norm and excerpt_norm in abstract);fact_match=bool(excerpt_norm and any(excerpt_norm in fact for fact in facts));assumption_match=bool(excerpt_norm and any(excerpt_norm in fact for fact in assumptions));failure_match=bool(excerpt_norm and any(excerpt_norm in fact for fact in failures));boundary_match=bool(excerpt_norm and any(excerpt_norm in fact for fact in boundaries))
        if assumption_match:evidence_kind="operational_assumption"
        elif failure_match:evidence_kind="measured_failure"
        elif boundary_match:evidence_kind="boundary_observation"
        elif fact_match:evidence_kind="empirical_fact"
        elif abstract_match:evidence_kind="abstract"
        else:evidence_kind=""
        evidence_source="abstract" if evidence_kind=="abstract" else ("fulltext" if evidence_kind else "")
        declared_source_valid=declared_source in {"","abstract","fulltext"}
        declared_source_matches=bool(not declared_source or declared_source==evidence_source)
        role_consistent=(role=="OPERATIONAL_ASSUMPTION" and assumption_match) or (role=="EMPIRICAL_FACT" and (abstract_match or fact_match or failure_match or boundary_match))
        excerpt_verified=bool(4<=len(words)<=30 and evidence_source and role_consistent)
        grounded=bool(supported and excerpt_verified and record.get("primary_source_verified") is True)
        out[key]={"ref":ref,"supported":supported,"evidence_role":role,"evidence_kind":evidence_kind,"evidence_source":evidence_source,"declared_evidence_source":declared_source,"declared_source_valid":declared_source_valid,"declared_source_matches":declared_source_matches,"evidence_excerpt":excerpt,"excerpt_verified":excerpt_verified,"grounded":grounded}
        all_grounded=all_grounded and grounded
    return out,all_grounded

def _apply_reviews(cands,payload,requested,resolved,generator_resolved,raw_sha,registry):
    by={str(r.get("candidate_id") or ""):r for r in (payload or {}).get("reviews") or [] if isinstance(r,dict)};known={r["key"] for r in REDUCTION_PATTERNS};generator_models={x for x in str(generator_resolved or "").split("|") if x};ind=bool(resolved and generator_models and resolved not in generator_models)
    for c in cands:
        r=by.get(c["candidate_id"]) or {};v=str(r.get("verdict") or "BLOCK").upper();matched=sorted({str(x) for x in r.get("matched_patterns") or [] if str(x) in known});grounding,grounded=_source_grounding(r,c,registry);lane_verified=r.get("lane_contract_verified") is True;reduction_class=str(r.get("reduction_class") or "").strip().upper();exact_test=str(r.get("exact_reduction_test") or "").strip()
        if reduction_class in {"VALID_HARD_VETO","NEEDS_EXACT_REDUCTION_TEST"}:v="BLOCK"
        if not ind or not grounded or not lane_verified:v="BLOCK"
        c["semantic_reduction_review"]={"reviewed":bool(r) and bool(raw_sha),"block_only":True,"verdict":"CLEAR" if v=="CLEAR" and ind and grounded and lane_verified else "BLOCK","reviewer_model":resolved or requested,"reviewer_requested_model":requested,"generator_resolved_model":generator_resolved,"independent_resolved_model":ind,"raw_sha256":raw_sha,"source_claims_grounded":grounded,"source_claim_grounding":grounding,"lane_contract_verified":lane_verified,"lane_contract_reason":str(r.get("lane_contract_reason") or ""),"matched_patterns":matched,"reduction_class":reduction_class,"exact_reduction_test":exact_test,"strongest_reduction":str(r.get("strongest_reduction") or ("reviewer-not-independent" if not ind else ("source-claim-grounding-failed" if not grounded else ("lane-contract-review-failed" if not lane_verified else "review-unavailable")))),"reason":str(r.get("reason") or ""),"authority":False}
        scan=dict(c.get("saturation_scan") or {});scan["checked"]=True
        if matched and reduction_class=="VALID_HARD_VETO":scan["matched_patterns"]=sorted(set(list(scan.get("matched_patterns") or [])+matched))
        elif matched and reduction_class=="NEEDS_EXACT_REDUCTION_TEST":
            pending=list(scan.get("pending_patterns") or []);pending.extend({"key":key,"exact_reduction_test":exact_test or "independent reviewer requested exact reduction test"} for key in matched);scan["pending_patterns"]=pending
        elif matched and reduction_class in {"SOFT_COLLISION","TOO_GENERIC_TO_VETO"}:
            rejected=list(scan.get("rejected_patterns") or []);rejected.extend({"key":key,"reason":str(r.get("reason") or "reviewer found similarity but not exact candidate-level reduction")} for key in matched);scan["rejected_patterns"]=rejected
        c["saturation_scan"]=scan
    return cands


def _count_by_lane(cands):
    counts={lane:0 for lane in DISCOVERY_LANES};counts["OTHER"]=0
    for c in cands:
        lane=str(c.get("discovery_lane") or "").strip().upper();counts[lane if lane in counts else "OTHER"]+=1
    return counts


LANE_SEARCH_STATUSES={"NO_PAIR","REDUCIBLE","CANDIDATE"}


def _normalize_lane_search(raw:Any,registry:dict[str,dict[str,Any]],expected_priority:list[str]|tuple[str,...]|None=None)->list[dict[str,Any]]:
    if not isinstance(raw,list): raise ValueError("generator-lane-search-array-required")
    rows=[];seen=set()
    for item in raw:
        if not isinstance(item,dict): raise ValueError("generator-lane-search-entry-invalid")
        lane=str(item.get("lane") or "").strip().upper();status=str(item.get("status") or "").strip().upper();reason=" ".join(str(item.get("reason") or "").split())[:500]
        refs=[str(ref or "").strip() for ref in (item.get("source_refs") or []) if str(ref or "").strip()]
        if lane not in DISCOVERY_LANES or lane in seen: raise ValueError("generator-lane-search-lane-invalid-or-duplicate")
        if status not in LANE_SEARCH_STATUSES: raise ValueError("generator-lane-search-status-invalid")
        if not reason: raise ValueError("generator-lane-search-reason-required")
        if status=="NO_PAIR" and refs: raise ValueError("generator-lane-search-no-pair-must-have-no-refs")
        if status in {"REDUCIBLE","CANDIDATE"}:
            minimum=LANE_DISTINCT_SOURCE_MINIMUM[lane]
            if len(refs)!=len(set(refs)) or not (minimum<=len(refs)<=2) or any(ref not in registry for ref in refs): raise ValueError("generator-lane-search-evidence-tuple-invalid")
        rows.append({"lane":lane,"status":status,"source_refs":refs,"reason":reason});seen.add(lane)
    if set(seen)!=set(DISCOVERY_LANES) or len(rows)!=len(DISCOVERY_LANES): raise ValueError("generator-lane-search-must-cover-all-lanes")
    priority=[str(lane or "").strip().upper() for lane in (expected_priority or DISCOVERY_LANES)]
    if len(priority)!=len(DISCOVERY_LANES) or set(priority)!=set(DISCOVERY_LANES): raise ValueError("generator-lane-search-priority-invalid")
    by_lane={row["lane"]:row for row in rows}
    return [by_lane[lane] for lane in priority]


def _candidate_ref_pair(candidate:dict[str,Any])->set[str]:
    evidence=candidate.get("empirical_evidence") or {}
    return {str((evidence.get(key) or {}).get("ref") or "").strip() for key in ("source_a","source_b") if str((evidence.get(key) or {}).get("ref") or "").strip()}


def _validate_lane_search_candidates(lane_search:list[dict[str,Any]],candidates:list[dict[str,Any]])->None:
    by_lane={row["lane"]:row for row in lane_search}
    for lane in DISCOVERY_LANES:
        row=by_lane[lane];lane_candidates=[candidate for candidate in candidates if str(candidate.get("discovery_lane") or "").strip().upper()==lane]
        if lane_candidates and row["status"]!="CANDIDATE": raise ValueError("generator-lane-search-candidate-status-mismatch")
        if row["status"]=="CANDIDATE":
            if not lane_candidates: raise ValueError("generator-lane-search-candidate-missing")
            pair=set(row.get("source_refs") or [])
            if not any(_candidate_ref_pair(candidate)==pair for candidate in lane_candidates): raise ValueError("generator-lane-search-candidate-pair-mismatch")


def _base_policy(*,portfolio:bool=False):
    return {"zero_candidates_is_valid":True,"discovery_operator_version":DISCOVERY_OPERATOR_VERSION,"single_source_anomaly_first_enabled":True,"source_coverage_saturation_reopens_once_on_operator_change":True,"search_portfolio_enabled":portfolio,"search_portfolio_is_shadow_only":True,"search_portfolio_primitives":list(SEARCH_PORTFOLIO_PRIMITIVES),"canonical_transaction_forbids_search_portfolio":True,"one_content_addressed_pool_allows_at_most_one_live_generator_call":True,"one_content_addressed_pool_allows_at_most_one_live_generator_call_per_discovery_operator":True,"one_generator_call_max":not portfolio,"one_semantic_reviewer_call_max":not portfolio,"expansion_precedes_reduction":portfolio,"mature_theory_veto_delayed_until_formulation":portfolio,"diversity_archives_required":portfolio,"branch_lineage_required":portfolio,"reduction_falsifiability_contract_required":portfolio,"generic_theory_label_cannot_veto":portfolio,"format_retry_forbidden":True,"transport_only_no_output_fallback_allowed":True,"transport_fallback_max_additional_provider_attempts":1,"transport_fallback_requires_zero_auditable_assistant_output":True,"transport_fallback_is_single_logical_generator_call":True,"thinking_disabled":True,"multi_lane_discovery_enabled":True,"allowed_discovery_lanes":list(DISCOVERY_LANES),"forbidden_discovery_lanes":list(FORBIDDEN_DISCOVERY_LANES),"verified_primary_registry_required":True,"semantic_reviewer_is_block_only":True,"independent_reviewer_must_ground_both_source_claims_to_exact_primary_evidence_excerpts":True,"reviewer_declared_excerpt_source_is_audit_metadata_not_grounding_authority":True,"exact_excerpt_location_is_machine_inferred":True,"independent_reviewer_must_verify_lane_contract":True,"same_resolved_model_cannot_count_as_independent_review":True,"raw_model_output_archived_before_parsing":True,"generation_notes_are_advisory_not_scientific_authority":True,"zero_candidate_rationale_required":True,"discovery_saturation_memory_has_zero_scientific_authority":True,"reviewer_blocked_problem_memory_has_zero_scientific_authority":True,"repeated_reduction_basin_requires_search_escape":True,"portable_blocked_problem_memory_is_search_control_only":True,"one_generator_call_must_audit_all_discovery_lanes":not portfolio,"portfolio_expansion_must_audit_all_discovery_lanes":portfolio,"lane_search_diagnostics_have_zero_scientific_authority":True,"lane_search_output_order_is_canonicalized_after_validation":True,"historically_underexplored_lanes_are_searched_first":True,"lane_search_never_requires_candidate":True,"last_completed_lane_search_is_portable_zero_authority_receipt":True,"terminal_zero_call_skip_preserves_last_completed_lane_search":True,"portable_review_receipts_are_scheduler_metadata_only":True,"portable_review_receipts_have_zero_scientific_authority":True,"primary_source_coverage_receipts_are_inherited_transactionally":True,"source_coverage_saturation_skips_model_call":True,"source_coverage_saturation_skips_model_call_after_current_operator_receipt":True,"source_coverage_saturation_operator_upgrade_recompile_is_explicit_exception":True,"incomplete_retrieval_without_new_lane_source_skips_model_call":True,"retrieval_incomplete_is_compute_control_not_scientific_negative":True,"carrier_probe_pending_skips_model_call":True,"carrier_probe_pending_is_compute_control_not_scientific_negative":True,"source_coverage_saturation_is_compute_control_not_scientific_negative":True,"new_lane_grounded_primary_source_reopens_generation":True,"candidate_inbox_has_zero_scientific_authority":True,"automatic_method_authority":False,"automatic_experiment_authority":False,"automatic_p0_authority":False}


def _empty_summary(primary_evidence_records=0):
    lanes={lane:0 for lane in DISCOVERY_LANES};lanes["OTHER"]=0
    return {"primary_evidence_records":primary_evidence_records,"raw_seeds":0,"semantic_unique_seeds":0,"unique_problem_families":0,"breadth_archive":0,"archive_pairwise_distance":0.0,"evolved_branches":0,"max_branch_depth":0,"portfolio_calls":0,"generated":0,"structurally_reviewable":0,"semantic_clear":0,"semantic_blocked":0,"written_to_auto_inbox":0,"generated_by_lane":dict(lanes),"structurally_reviewable_by_lane":dict(lanes),"semantic_clear_by_lane":dict(lanes),"semantic_blocked_by_lane":dict(lanes)}


def run_problem_generator(*,storage=None,primary_pool_path=None,auto_inbox_path=None,saturation_ledger_path=None,generator_model=None,reviewer_model=None,generator_responder:Responder|None=None,reviewer_responder:Responder|None=None,now=None,pool_max_age_hours=MAX_POOL_AGE_HOURS,max_candidates=MAX_CANDIDATES,blocked_problem_memory:dict[str,Any]|None=None,portfolio_mode:bool|None=None,target_raw_seeds:int=DEFAULT_RAW_SEEDS,strict_provider:bool=False,defer_reviewer:bool=False,allow_orphan_replay:bool=False):
    storage=storage or StorageSettings.from_env();primary_pool_path=primary_pool_path or private_primary_pool_path(storage);auto_inbox_path=auto_inbox_path or default_auto_inbox_path(storage)
    generator_model=generator_model or os.getenv("PAPER_FIRST_PROBLEM_GENERATOR_MODEL",GENERATOR_MODEL);reviewer_model=reviewer_model or os.getenv("PAPER_FIRST_PROBLEM_REVIEW_MODEL",REVIEWER_MODEL);current=(now or _now_dt()).astimezone(timezone.utc);run_id=current.strftime("%Y%m%dT%H%M%SZ");portfolio_mode=False if portfolio_mode is None else bool(portfolio_mode)
    if portfolio_mode:
        raise ValueError("search-portfolio-is-shadow-only-use-run_search_portfolio")
    archived=_archive_previous(storage,auto_inbox_path);pool=load_private_primary_pool(primary_pool_path) or {};reg=_registry(pool);psha=_pool_sha(pool) if pool else "";d=_parse_iso(pool.get("generated_at"));age=None if d is None else max(0.0,(current-d).total_seconds()/3600)
    inherited_receipts=[dict(row) for row in ((pool.get("source_coverage") or {}).get("portable_review_receipts") or []) if isinstance(row,dict)]
    blocked_problem_memory=blocked_problem_memory or _public_blocked_problem_memory(storage)
    dead_end_prompt_memory=_private_dead_end_prompt_memory(storage,blocked_problem_memory)
    policy=_base_policy(portfolio=False)
    generator_is_glm=str(generator_model).lower().startswith("glm");generator_max_output_tokens=15000 if generator_is_glm else 6500
    policy["strict_provider_transport"]=bool(strict_provider);policy["semantic_reviewer_deferred"]=bool(defer_reviewer);policy["thinking_compatibility_repost_allowed"]=not bool(strict_provider)
    policy["thinking_disabled"]=not generator_is_glm;policy["generator_thinking_profile"]="provider-default" if generator_is_glm else "disabled";policy["generator_max_output_tokens"]=generator_max_output_tokens
    policy["provider_orphan_replay_forbidden"]=not bool(allow_orphan_replay);policy["provider_orphan_override_requires_explicit_operator_action"]=True
    if strict_provider:
        policy["transport_only_no_output_fallback_allowed"]=False;policy["transport_fallback_max_additional_provider_attempts"]=0
    state={"schema_version":"2.5","generated_at":_now(),"run_id":run_id,"primary_pool_path":str(primary_pool_path),"auto_inbox_path":str(auto_inbox_path),"archived_previous_auto_inbox":archived,"generator_model":generator_model,"reviewer_model":reviewer_model,"policy":policy,"summary":_empty_summary(len(reg)),"raw_artifacts":{},"generation_notes":"","search_diagnostics":{"lane_search_priority":list(dead_end_prompt_memory.get("lane_search_priority") or DISCOVERY_LANES),"lane_search_complete":False,"lane_search":[],"last_completed_lane_search":{},"scientific_authority":False},"saturation_memory":{"ledger_entries":len(_load_saturation_ledger(storage,saturation_ledger_path)),"prior_identical_zero_runs":0,"current_run_recorded":False,"portable_review_receipts":inherited_receipts[-PORTABLE_REVIEW_RECEIPT_LIMIT:],"blocked_problem_memory":blocked_problem_memory,"scientific_authority":False},"candidates":[]}
    def finish(status,cands=[]): state["status"]=status;_write_inbox(auto_inbox_path,run_id,status,cands,psha);_record_saturation_run(storage,state,psha,reg,saturation_ledger_path);return state
    if pool.get("status")!="READY" or len(reg)<4:return finish("SKIPPED_INSUFFICIENT_PRIMARY_EVIDENCE")
    if age is None or age>pool_max_age_hours:state["primary_pool_age_hours"]=age;return finish("SKIPPED_STALE_PRIMARY_EVIDENCE")
    state["primary_pool_age_hours"]=round(age,4)
    coverage=pool.get("source_coverage") or {}
    state["source_coverage"]={"coverage_exhausted":coverage.get("coverage_exhausted") is True,"source_retrieval_complete":coverage.get("source_retrieval_complete") is not False,"eligible_lane_linked_sources":int(coverage.get("eligible_lane_linked_sources") or 0),"reviewed_lane_linked_sources":int(coverage.get("reviewed_lane_linked_sources") or 0),"unreviewed_lane_linked_sources":int(coverage.get("unreviewed_lane_linked_sources") or 0),"unreviewed_no_lane_sources":int(coverage.get("unreviewed_no_lane_sources") or 0),"carrier_probe_required":coverage.get("carrier_probe_required") is True,"carrier_probe_pending":int(coverage.get("carrier_probe_pending") or 0),"carrier_probe_complete":coverage.get("carrier_probe_complete") is not False,"scientific_authority":False}
    if not state["source_coverage"]["source_retrieval_complete"] and state["source_coverage"]["unreviewed_lane_linked_sources"]==0:
        state["coverage_skip_reason"]="The retrieval window is incomplete and no unreviewed lane-grounded source was recovered from the available corpus; the existing pool cannot trigger another live generator call."
        return finish("SKIPPED_SOURCE_RETRIEVAL_INCOMPLETE")
    if state["source_coverage"]["carrier_probe_required"] and state["source_coverage"]["carrier_probe_pending"]>0 and state["source_coverage"]["unreviewed_lane_linked_sources"]==0:
        state["coverage_skip_reason"]="No newly rescued lane-grounded source is ready yet; bounded no-lane carrier probing still has pending sources, so the existing content-addressed pool cannot trigger another live generator call."
        return finish("SKIPPED_SOURCE_CARRIER_PROBE_PENDING")
    if state["source_coverage"]["coverage_exhausted"] and state["source_coverage"]["unreviewed_lane_linked_sources"]==0:
        if _has_current_operator_receipt(storage,psha,inherited_receipts,saturation_ledger_path):
            state["coverage_skip_reason"]="No unreviewed freshness/relevance-qualified source remains and this exact evidence pool has already completed the current discovery operator; generation resumes when evidence, the mature-reduction ledger, or the discovery operator changes."
            return finish("SKIPPED_SOURCE_COVERAGE_SATURATED")
        state["operator_recompile_reason"]="Source coverage is saturated, but this evidence pool has no completed receipt for the current anomaly-first discovery operator. One bounded recompilation is allowed; scientific gates are unchanged."
    generator_prompt_text=generator_prompt(list(reg.values()),dead_end_memory=dead_end_prompt_memory)
    generator_request_audit=_provider_request_audit(stage="problem_generation",prompt=generator_prompt_text,model=generator_model,max_output_tokens=generator_max_output_tokens,temperature=0.0)
    state["generator_request_audit"]=generator_request_audit
    if generator_responder is None and not allow_orphan_replay and _provider_orphan_exists(storage,generator_request_audit["request_fingerprint"]):
        state["provider_orphan_audits"]=[{"request_fingerprint":generator_request_audit["request_fingerprint"],"status":"ORPHANED_POST_NO_RECEIPT","requested_model":generator_model,"stage":"problem_generation","scientific_authority":False}]
        state["coverage_skip_reason"]="An identical provider request previously timed out without a response receipt. Automatic replay is blocked because provider acceptance is ambiguous; explicit operator override is required."
        return finish("SKIPPED_ORPHANED_PROVIDER_REQUEST")
    call=generator_responder or (lambda **kwargs:_ark(stage="problem_generation",allow_transport_fallback=not strict_provider,**kwargs));rows=[];generator_resolved_models=[]
    if portfolio_mode:
        provenance=[]
        def portfolio_call(*,role,prompt,model,max_output_tokens):
            temperature=0.85 if role.startswith("expand-") else (0.60 if role.startswith("evolve-g1") else (0.35 if role.startswith("evolve-g2") else 0.15))
            res=call(prompt=prompt,model=model,max_output_tokens=max_output_tokens,temperature=temperature);raw=str(res.get("text") or "");path,sha=_write_raw(storage,run_id,role,model,raw);resolved=str(res.get("resolved_model") or model);generator_resolved_models.append(resolved);provenance.append({"role":role,"sha256":sha,"requested_model":model,"resolved_model":resolved,"temperature":temperature});return res
        try:
            portfolio=run_search_portfolio(records=list(reg.values()),call=portfolio_call,model=generator_model,target_raw_seeds=target_raw_seeds,dead_end_memory=dead_end_prompt_memory)
            formulated=portfolio.get("formulated_candidates") or [];machine_reviewable=[];machine_blocked=[]
            for raw_candidate in formulated:
                normalized=_normalize(raw_candidate,reg);audit=audit_problem_candidate(normalized,primary_evidence_by_ref=reg,require_primary_registry=True,require_semantic_review=False)
                if audit.get("passed"):machine_reviewable.append(raw_candidate)
                else:machine_blocked.append({"candidate_id":normalized.get("candidate_id"),"title":normalized.get("title"),"discovery_lane":normalized.get("discovery_lane"),"blockers":audit.get("blockers") or []})
            rows=machine_reviewable;portfolio["machine_reduction_audit"]={"reviewable":len(machine_reviewable),"blocked":len(machine_blocked),"blocked_rows":machine_blocked,"scientific_authority":False}
            private_dir=_root(storage)/"search-portfolios";private_dir.mkdir(parents=True,exist_ok=True);private_path=private_dir/f"{run_id}-portfolio.json";private_text=json.dumps(portfolio,ensure_ascii=False,indent=2)+"\n";private_path.write_text(private_text,encoding="utf-8");private_sha=_sha(private_text)
            state["search_portfolio_private_path"]=str(private_path);state["portfolio_provenance"]=provenance
            public_keys=("policy","config","summary","lane_counts","archive_lane_counts","family_counts");state["search_portfolio"]={k:portfolio.get(k) for k in public_keys};state["search_portfolio"]["archive_counts"]={k:len(v) for k,v in (portfolio.get("archives") or {}).items()};state["search_portfolio"]["scientific_authority"]=False
            ps=portfolio.get("summary") or {};ps["machine_reviewable"]=len(machine_reviewable);ps["machine_reduction_blocked"]=len(machine_blocked);state["search_portfolio"]["summary"]=ps;state["summary"].update({"raw_seeds":ps.get("raw_seeds",0),"semantic_unique_seeds":ps.get("semantic_unique",0),"unique_problem_families":ps.get("unique_problem_families",0),"breadth_archive":ps.get("breadth_archive",0),"archive_pairwise_distance":ps.get("mean_archive_pairwise_distance",0.0),"evolved_branches":ps.get("evolved_branches",0),"max_branch_depth":ps.get("max_branch_depth",0),"portfolio_calls":ps.get("portfolio_calls",0)})
            lane_counts=portfolio.get("lane_counts") or {};priority=list(state["search_diagnostics"]["lane_search_priority"]);state["search_diagnostics"].update({"lane_search_complete":True,"lane_search":[{"lane":lane,"status":"EXPANDED" if int(lane_counts.get(lane) or 0)>0 else "EMPTY","raw_seed_count":int(lane_counts.get(lane) or 0),"reason":"Search Portfolio expansion shard produced grounded seeds." if int(lane_counts.get(lane) or 0)>0 else "No machine-valid grounded seed survived expansion contract."} for lane in priority]})
            state["generation_notes"]=(f"Search Portfolio expanded {ps.get('raw_seeds',0)} grounded raw seeds into {ps.get('semantic_unique',0)} semantic-unique / {ps.get('unique_problem_families',0)} structural families, evolved {ps.get('evolved_branches',0)} branches, formulated {ps.get('formulated_candidates',0)}, and left {len(machine_reviewable)} machine-reviewable candidates after delayed exact reduction. Zero final candidates remains valid and is not by itself evidence of field saturation.")
            synth=_sha(json.dumps({"portfolio_sha256":private_sha,"calls":[x["sha256"] for x in provenance]},sort_keys=True,separators=(",",":")));resolved_join="|".join(sorted(set(generator_resolved_models))) or generator_model;state["raw_artifacts"]["generator"]={"sha256":synth,"requested_model":generator_model,"resolved_model":resolved_join,"portfolio":True,"portfolio_sha256":private_sha,"calls":len(provenance)}
        except Exception as e:state["error"]=f"{type(e).__name__}:{str(e)[:300]}";state["portfolio_provenance"]=provenance;return finish("GENERATOR_ERROR_ZERO_AUTHORITY")
    else:
        try:
            res=call(prompt=generator_prompt_text,model=generator_model,max_output_tokens=generator_max_output_tokens);raw=str(res.get("text") or "");p,sha=_write_raw(storage,run_id,"generator",generator_model,raw);resolved=str(res.get("resolved_model") or generator_model);generator_resolved_models=[resolved];transport_attempts=list(res.get("transport_attempts") or []);safe_attempts,receipt_audits=_archive_provider_receipts(storage,run_id,"generator",transport_attempts);orphan_audits=_archive_provider_orphans(storage,run_id,"problem_generation",transport_attempts);state["raw_artifacts"]["generator"]={"path":p,"sha256":sha,"requested_model":generator_model,"resolved_model":resolved,"transport_attempts":safe_attempts,"transport_fallback_used":bool(res.get("transport_fallback_used"))};
            if receipt_audits:state["raw_artifacts"]["generator"]["provider_receipt_audits"]=receipt_audits
            if orphan_audits:state["provider_orphan_audits"]=orphan_audits
            payload=extract_json_object(raw);state["generation_notes"]=str(payload.get("generation_notes") or "")[:2400].strip();lane_search=_normalize_lane_search(payload.get("lane_search"),reg,state["search_diagnostics"]["lane_search_priority"]);rows=payload.get("candidates") or []
            if not isinstance(rows,list) or len(rows)>max_candidates or any(not isinstance(r,dict) for r in rows):raise ValueError("generator-candidate-array-invalid")
            if not rows and not state["generation_notes"]:raise ValueError("zero-candidate-generation-notes-required")
        except Exception as e:
            transport_attempts=list(getattr(e,"transport_attempts",[]) or []);safe_attempts,receipt_audits=_archive_provider_receipts(storage,run_id,"generator",transport_attempts);orphan_audits=_archive_provider_orphans(storage,run_id,"problem_generation",transport_attempts);state["error"]=f"{type(e).__name__}:{str(e)[:300]}";state["provider_transport_attempts"]=safe_attempts
            if receipt_audits:state["provider_receipt_audits"]=receipt_audits
            if orphan_audits:state["provider_orphan_audits"]=orphan_audits
            return finish("GENERATOR_ERROR_ZERO_AUTHORITY")
        cands=[_normalize(r,reg) for r in rows]
        try:_validate_lane_search_candidates(lane_search,cands)
        except Exception as e:state["error"]=f"{type(e).__name__}:{str(e)[:300]}";return finish("GENERATOR_ERROR_ZERO_AUTHORITY")
        state["search_diagnostics"].update({"lane_search_complete":True,"lane_search":lane_search});reviewable=[c for c in cands if _reviewable(c,reg)];state["summary"].update({"generated":len(cands),"structurally_reviewable":len(reviewable),"generated_by_lane":_count_by_lane(cands),"structurally_reviewable_by_lane":_count_by_lane(reviewable)})
    if portfolio_mode:
        cands=[_normalize(r,reg) for r in rows];reviewable=[c for c in cands if _reviewable(c,reg)];state["summary"].update({"generated":len(cands),"structurally_reviewable":len(reviewable),"generated_by_lane":_count_by_lane(cands),"structurally_reviewable_by_lane":_count_by_lane(reviewable)})
    if reviewable and defer_reviewer:
        state["summary"].update({"semantic_clear":0,"semantic_blocked":0,"semantic_review_unavailable":len(reviewable),"written_to_auto_inbox":0,"semantic_clear_by_lane":_count_by_lane([]),"semantic_blocked_by_lane":_count_by_lane([]),"semantic_review_unavailable_by_lane":_count_by_lane(reviewable)})
        state["candidates"]=[{"candidate_id":c["candidate_id"],"title":c["title"],"discovery_lane":c["discovery_lane"],"source_branch_id":c.get("source_branch_id") or "","source_refs":[c["empirical_evidence"]["source_a"]["ref"],c["empirical_evidence"]["source_b"]["ref"]],"semantic_verdict":"UNREVIEWED","lane_contract_verified":False,"matched_patterns":[]} for c in cands]
        return finish("GENERATED_AWAIT_SEMANTIC_REVIEW",[])
    if reviewable:
        call2=reviewer_responder or (lambda **kwargs:_ark(stage="semantic_review",allow_transport_fallback=not strict_provider,**kwargs));batch_size=6 if portfolio_mode else max(1,len(reviewable));review_receipts=[];gen_resolved="|".join(sorted(set(generator_resolved_models))) or generator_model
        for start in range(0,len(reviewable),batch_size):
            batch=reviewable[start:start+batch_size]
            try:
                res=call2(prompt=reviewer_prompt(batch,reg),model=reviewer_model,max_output_tokens=5200 if portfolio_mode else 4200);raw=str(res.get("text") or "");role=f"semantic-review-{start//batch_size+1}" if portfolio_mode else "semantic-review";p,sha=_write_raw(storage,run_id,role,reviewer_model,raw);rresolved=str(res.get("resolved_model") or reviewer_model);safe_attempts,receipt_audits=_archive_provider_receipts(storage,run_id,role,list(res.get("transport_attempts") or []));review_receipt={"sha256":sha,"requested_model":reviewer_model,"resolved_model":rresolved,"transport_attempts":safe_attempts,"transport_fallback_used":bool(res.get("transport_fallback_used"))};
                if receipt_audits:review_receipt["provider_receipt_audits"]=receipt_audits
                review_receipts.append(review_receipt);_apply_reviews(batch,extract_json_object(raw),reviewer_model,rresolved,gen_resolved,sha,reg)
            except Exception as e:
                role=f"semantic-review-{start//batch_size+1}" if portfolio_mode else "semantic-review";safe_attempts,receipt_audits=_archive_provider_receipts(storage,run_id,role,list(getattr(e,"transport_attempts",[]) or []));state.setdefault("semantic_review_errors",[]).append(f"batch-{start//batch_size+1}:{type(e).__name__}:{str(e)[:240]}")
                if safe_attempts:state.setdefault("semantic_review_transport_attempts",[]).append({"batch":start//batch_size+1,"attempts":safe_attempts})
                if receipt_audits:state.setdefault("provider_receipt_audits",[]).extend(receipt_audits)
                _apply_reviews(batch,None,reviewer_model,"",gen_resolved,"",reg)
        if portfolio_mode:
            state["semantic_reviewer_batches"]=review_receipts
            if review_receipts:state["raw_artifacts"]["semantic_reviewer"]={"sha256":_sha("|".join(str(row.get("sha256") or "") for row in review_receipts)),"requested_model":reviewer_model,"resolved_model":"|".join(sorted({str(row.get('resolved_model') or '') for row in review_receipts if row.get('resolved_model')})),"calls":len(review_receipts)}
        elif review_receipts:state["raw_artifacts"]["semantic_reviewer"]={**review_receipts[0]}
        if state.get("semantic_review_errors"):
            unavailable=[c for c in reviewable if not (c.get("semantic_reduction_review") or {}).get("reviewed")];reviewed=[c for c in reviewable if c not in unavailable];clear_reviewed=[c for c in reviewed if (c.get("semantic_reduction_review") or {}).get("verdict")=="CLEAR"];blocked_reviewed=[c for c in reviewed if c not in clear_reviewed]
            state["summary"].update({"semantic_clear":len(clear_reviewed),"semantic_blocked":len(blocked_reviewed),"semantic_review_unavailable":len(unavailable),"written_to_auto_inbox":0,"semantic_clear_by_lane":_count_by_lane(clear_reviewed),"semantic_blocked_by_lane":_count_by_lane(blocked_reviewed),"semantic_review_unavailable_by_lane":_count_by_lane(unavailable)})
            state["candidates"]=[{"candidate_id":c["candidate_id"],"title":c["title"],"discovery_lane":c["discovery_lane"],"source_branch_id":c.get("source_branch_id") or "","source_refs":[c["empirical_evidence"]["source_a"]["ref"],c["empirical_evidence"]["source_b"]["ref"]],"semantic_verdict":(c.get("semantic_reduction_review") or {}).get("verdict") if (c.get("semantic_reduction_review") or {}).get("reviewed") else "UNREVIEWED","lane_contract_verified":(c.get("semantic_reduction_review") or {}).get("lane_contract_verified") is True,"matched_patterns":(c.get("semantic_reduction_review") or {}).get("matched_patterns") or []} for c in cands]
            return finish("REVIEWER_ERROR_ZERO_AUTHORITY",[])
    for c in cands:
        if c not in reviewable:c["semantic_reduction_review"].update({"reviewed":False,"verdict":"BLOCK","lane_contract_verified":False,"lane_contract_reason":"structural-or-provenance-gate-failed","strongest_reduction":"structural-or-provenance-gate-failed"})
    clear_rows=[c for c in cands if (c.get("semantic_reduction_review") or {}).get("verdict")=="CLEAR"];blocked_rows=[c for c in cands if c not in clear_rows]
    state["summary"].update({"semantic_clear":len(clear_rows),"semantic_blocked":len(blocked_rows),"written_to_auto_inbox":len(cands),"semantic_clear_by_lane":_count_by_lane(clear_rows),"semantic_blocked_by_lane":_count_by_lane(blocked_rows)})
    state["candidates"]=[{"candidate_id":c["candidate_id"],"title":c["title"],"discovery_lane":c["discovery_lane"],"source_branch_id":c.get("source_branch_id") or "","source_refs":[c["empirical_evidence"]["source_a"]["ref"],c["empirical_evidence"]["source_b"]["ref"]],"semantic_verdict":c["semantic_reduction_review"]["verdict"],"lane_contract_verified":c["semantic_reduction_review"].get("lane_contract_verified") is True,"matched_patterns":c["semantic_reduction_review"].get("matched_patterns") or []} for c in cands]
    return finish("GENERATED_ZERO_CANDIDATES" if not cands else "GENERATED_AWAIT_PROBLEM_GATE",cands)


def public_problem_generator_state(state:dict[str,Any],storage:StorageSettings|None=None)->dict[str,Any]:
    public=json.loads(json.dumps(state,ensure_ascii=False))
    for key in ("primary_pool_path","auto_inbox_path","archived_previous_auto_inbox","search_portfolio_private_path"):
        public.pop(key,None)
    for artifact in (public.get("raw_artifacts") or {}).values():
        if isinstance(artifact,dict):artifact.pop("path",None)
    return redact_private_paths(public,storage=storage or StorageSettings.from_env())


def _empty_state(status):
    return {"schema_version":"2.5","status":status,"policy":_base_policy(portfolio=False),"summary":_empty_summary(),"generation_notes":"","search_diagnostics":{"lane_search_priority":list(DISCOVERY_LANES),"lane_search_complete":False,"lane_search":[],"last_completed_lane_search":{},"scientific_authority":False},"saturation_memory":{"ledger_entries":0,"prior_identical_zero_runs":0,"current_run_recorded":False,"portable_review_receipts":[],"blocked_problem_memory":{"blocked_candidate_attempts":0,"portable_blocked_problem_memory":[],"scientific_authority":False},"scientific_authority":False},"candidates":[],"raw_artifacts":{}}


def load_problem_generator_state(path:Path=DEFAULT_JSON):
    if not path.exists():return _empty_state("NOT_RUN")
    try:p=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError):return _empty_state("STATE_UNREADABLE")
    return p if isinstance(p,dict) else _empty_state("STATE_INVALID")


def _merge_portable_review_receipts(state:dict[str,Any],previous:dict[str,Any])->dict[str,Any]:
    saturation=state.setdefault("saturation_memory",{})
    rows=[]
    previous_saturation=previous.get("saturation_memory") or {}
    for row in previous_saturation.get("portable_review_receipts") or []:
        if isinstance(row,dict): rows.append(dict(row))
    for row in saturation.get("portable_review_receipts") or []:
        if isinstance(row,dict): rows.append(dict(row))
    current=saturation.get("current_review_receipt")
    if isinstance(current,dict): rows.append(dict(current))
    by_run:dict[str,dict[str,Any]]={}
    for row in rows:
        run_id=str(row.get("run_id") or "").strip();status=str(row.get("status") or "")
        refs=sorted({str(ref).strip() for ref in row.get("source_refs") or [] if str(ref).strip().startswith("arXiv:")})
        if not run_id or len(refs)<4 or status not in {"GENERATED_ZERO_CANDIDATES","GENERATED_AWAIT_PROBLEM_GATE"} or row.get("scientific_authority") is not False:
            continue
        normalized=dict(row);normalized["run_id"]=run_id;normalized["source_refs"]=refs;normalized["scientific_authority"]=False
        by_run[run_id]=normalized
    receipts=list(by_run.values())[-PORTABLE_REVIEW_RECEIPT_LIMIT:]
    saturation["portable_review_receipts"]=receipts
    saturation["portable_review_receipt_count"]=len(receipts)
    saturation["scientific_authority"]=False
    return state


def _normalize_last_completed_lane_search_receipt(value:Any)->dict[str,Any]:
    if not isinstance(value,dict): return {}
    run_id=str(value.get("run_id") or "").strip()
    if value.get("scientific_authority") is not False: return {}
    priority=[str(x or "").strip().upper() for x in value.get("lane_search_priority") or []]
    raw_rows=value.get("lane_search") or []
    if not run_id or set(priority)!=set(DISCOVERY_LANES) or len(priority)!=len(DISCOVERY_LANES) or not isinstance(raw_rows,list) or len(raw_rows)!=len(DISCOVERY_LANES): return {}
    rows=[]; statuses=set()
    for item in raw_rows:
        if not isinstance(item,dict): return {}
        lane=str(item.get("lane") or "").strip().upper(); status=str(item.get("status") or "").strip().upper(); reason=" ".join(str(item.get("reason") or "").split())[:500]
        if lane not in DISCOVERY_LANES or not reason: return {}
        statuses.add(status)
        if status in {"EXPANDED","EMPTY"}:
            rows.append({"lane":lane,"status":status,"raw_seed_count":max(0,int(item.get("raw_seed_count") or 0)),"reason":reason}); continue
        refs=[str(ref or "").strip() for ref in item.get("source_refs") or [] if str(ref or "").strip()]
        if status not in LANE_SEARCH_STATUSES: return {}
        if status=="NO_PAIR" and refs: return {}
        if status in {"REDUCIBLE","CANDIDATE"}:
            minimum=LANE_DISTINCT_SOURCE_MINIMUM[lane]
            if len(refs)!=len(set(refs)) or not (minimum<=len(refs)<=2) or any(not ref.startswith("arXiv:") for ref in refs): return {}
        rows.append({"lane":lane,"status":status,"source_refs":refs,"reason":reason})
    if [row["lane"] for row in rows]!=priority: return {}
    declared_mode=str(value.get("mode") or "").strip()
    declared_operator=str(value.get("discovery_operator_version") or "").strip()
    if statuses.issubset({"EXPANDED","EMPTY"}):
        mode="portfolio_expansion"
    elif statuses.issubset(set(LANE_SEARCH_STATUSES)):
        # Preserve historical pair-audit provenance. Only receipts explicitly
        # produced under the current operator are labeled anomaly-first.
        mode="anomaly_first_evidence_tuple_audit" if declared_operator==DISCOVERY_OPERATOR_VERSION else (declared_mode or "legacy_pair_audit")
    else: return {}
    return {"run_id":run_id,"generator_status":str(value.get("generator_status") or ""),"generated_at":str(value.get("generated_at") or ""),"mode":mode,"discovery_operator_version":declared_operator,"lane_search_priority":priority,"lane_search":rows,"generation_notes":" ".join(str(value.get("generation_notes") or "").split())[:800],"scientific_authority":False}


def _completed_lane_search_receipt_from_state(source:dict[str,Any])->dict[str,Any]:
    diagnostics=source.get("search_diagnostics") or {}
    if diagnostics.get("lane_search_complete") is not True: return {}
    return _normalize_last_completed_lane_search_receipt({"run_id":source.get("run_id"),"generator_status":source.get("status"),"generated_at":source.get("generated_at"),"mode":"anomaly_first_evidence_tuple_audit","discovery_operator_version":str((source.get("policy") or {}).get("discovery_operator_version") or ""),"lane_search_priority":diagnostics.get("lane_search_priority"),"lane_search":diagnostics.get("lane_search"),"generation_notes":source.get("generation_notes"),"scientific_authority":False})


def _merge_last_completed_lane_search(state:dict[str,Any],previous:dict[str,Any],seed:dict[str,Any]|None=None)->dict[str,Any]:
    diagnostics=state.setdefault("search_diagnostics",{}); previous_diagnostics=previous.get("search_diagnostics") or {}
    candidates=[_normalize_last_completed_lane_search_receipt(previous_diagnostics.get("last_completed_lane_search")),_completed_lane_search_receipt_from_state(previous),_normalize_last_completed_lane_search_receipt(seed),_completed_lane_search_receipt_from_state(state)]
    chosen={}
    for candidate in candidates:
        if candidate: chosen=candidate
    diagnostics["last_completed_lane_search"]=chosen; diagnostics["scientific_authority"]=False
    return state


def write_problem_generator_state(json_path=DEFAULT_JSON,js_path=DEFAULT_JS,previous_public_state_path=None,last_completed_lane_search_seed=None,**kwargs):
    previous_path=Path(previous_public_state_path) if previous_public_state_path is not None else json_path
    previous=load_problem_generator_state(previous_path)
    storage=kwargs.get("storage") or StorageSettings.from_env()
    blocked_problem_memory=_public_blocked_problem_memory(storage,previous_path)
    state=run_problem_generator(**kwargs,blocked_problem_memory=blocked_problem_memory)
    _merge_portable_review_receipts(state,previous)
    _merge_last_completed_lane_search(state,previous,last_completed_lane_search_seed)
    public=public_problem_generator_state(state,storage=kwargs.get("storage"));json_path.parent.mkdir(parents=True,exist_ok=True);json_path.write_text(json.dumps(public,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");js_path.write_text("window.PAPER_FIRST_PROBLEM_GENERATOR = "+json.dumps(public,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8");return state

if __name__=="__main__":print(json.dumps(write_problem_generator_state(),ensure_ascii=False))
