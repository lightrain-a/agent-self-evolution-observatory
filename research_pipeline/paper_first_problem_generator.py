from __future__ import annotations

import hashlib,json,os,re
from collections import Counter
from queue import Queue
from datetime import datetime,timezone
from pathlib import Path
from threading import Event,Thread
from typing import Any,Callable

from .ark_provider import ArkResponsesClient,ArkSettings,extract_json_object
from .config import PROJECT_ROOT,StorageSettings
from .paper_first_fresh_saturation import REDUCTION_PATTERNS, reduction_pattern_audit
from .paper_first_primary_evidence import load_private_primary_pool,private_primary_pool_path
from .paper_first_problem_discovery_contract import DISCOVERY_LANES, DISCOVERY_OPERATOR_VERSION, SEARCH_PORTFOLIO_PRIMITIVES, FORBIDDEN_DISCOVERY_LANES, LANE_DISTINCT_SOURCE_MINIMUM, PAPERABILITY_AXES, audit_problem_candidate
from .paper_first_problem_gate_queue import default_auto_inbox_path
from .paper_first_problem_generator_prompts import generator_prompt,reviewer_prompt
from .paper_first_problem_search_portfolio import DEFAULT_FORMULATION_BUDGET, DEFAULT_RAW_SEEDS, _maxmin_select, _normalize_paperability_axes, _paperability_survives, recover_archived_formulation_payload, run_search_portfolio
from .premium_model_policy import preferred_model, stage_model_priority
from .public_state_redaction import redact_private_paths

DEFAULT_JSON=PROJECT_ROOT/"generated"/"paper-first-problem-generator-state.json"
DEFAULT_JS=PROJECT_ROOT/"generated"/"paper-first-problem-generator-state.js"
PORTABLE_REVIEW_RECEIPT_LIMIT=64
PORTABLE_BLOCKED_MEMORY_LIMIT=24
DURABLE_PRINCIPLE_DEAD_END_JSON=PROJECT_ROOT/"generated"/"paper-first-search-portfolio-design-adjudication.json"
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

def _archived_replay_metadata(result:dict[str,Any],raw_sha256:str,stage:str,*,expected_request_fingerprint:str="")->dict[str,Any]:
    """Validate an explicitly archived provider response used with zero new provider calls."""
    if result.get("raw_replayed_without_provider") is not True:
        return {}
    origin_run_id=str(result.get("raw_origin_run_id") or "").strip();origin_sha=str(result.get("raw_origin_sha256") or "").strip().lower();origin_request=str(result.get("raw_origin_request_fingerprint") or "").strip().lower()
    expected=str(expected_request_fingerprint or "").strip().lower()
    if not origin_run_id or not re.fullmatch(r"[0-9a-f]{64}",origin_sha) or origin_sha!=str(raw_sha256 or "").strip().lower():
        raise ValueError(f"{stage}-archived-replay-provenance-invalid")
    if expected and (not re.fullmatch(r"[0-9a-f]{64}",origin_request) or origin_request!=expected):
        raise ValueError(f"{stage}-archived-replay-request-fingerprint-mismatch")
    if list(result.get("transport_attempts") or []):
        raise ValueError(f"{stage}-archived-replay-cannot-carry-transport-attempts")
    return {"raw_replayed_without_provider":True,"provider_calls_executed":0,"raw_origin_run_id":origin_run_id,"raw_origin_sha256":origin_sha,"raw_origin_request_fingerprint":origin_request}

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
            payload={"schema_version":"1.0","generated_at":_now(),"run_id":run_id,"stage":stage,"status":"ORPHANED_POST_NO_RECEIPT","request_audit":{key:row.get(key) for key in ("request_fingerprint","prompt_sha256","requested_model","max_output_tokens","temperature","thinking_profile","wall_clock_seconds","provider_wall_clock_timeout")},"provider_error_audit":row.get("provider_error_audit") or {},"replay_policy":"BLOCK_AUTOMATIC_REPLAY_UNTIL_EXPLICIT_OPERATOR_OVERRIDE","scientific_authority":False,"authority":{"paper":False,"method":False,"experiment":False,"p0":False,"gpu":False}}
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


def _search_closure_rows(memory:dict[str,Any])->list[dict[str,Any]]:
    """Canonical closed_objects first; legacy blocked_objects is read-only fallback."""
    canonical=isinstance((memory or {}).get("closed_objects"),list)
    rows=(memory or {}).get("closed_objects") if canonical else ((memory or {}).get("blocked_objects") or [])
    return [
        row for row in (rows or [])
        if isinstance(row,dict)
        and (row.get("search_closure_certified") is True or (not canonical and row.get("dead_end_certified") is True))
    ]


def _durable_principle_dead_end_examples(path:Path=DURABLE_PRINCIPLE_DEAD_END_JSON,limit:int=12,current_refs:set[str]|None=None)->list[dict[str,Any]]:
    try: payload=json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError): return []
    memory=payload.get("shadow_search_memory") or payload.get("shadow_dead_end_memory") or {};rows=_search_closure_rows(memory)
    examples=[]
    for order,row in enumerate(rows):
        counter=row.get("counter_explanation") or {}
        if not isinstance(counter,dict): counter={}
        refs=[str(ref) for ref in (row.get("current_source_refs") or []) if str(ref)][:4]
        examples.append({
            "source_candidate_id":str(row.get("source_candidate_id") or ""),
            "title":str(row.get("title") or "")[:280],
            "search_primitive":str(row.get("search_primitive") or ""),
            "source_refs":refs,
            "strongest_reduction":str(row.get("strongest_reduction") or "")[:700],
            "opposite_principle":str(counter.get("opposite_principle") or "")[:500],
            "opposite_search_seed":str(counter.get("opposite_search_seed") or "")[:700],
            "reopen_condition":str(counter.get("reopen_condition") or row.get("reopen_only_if") or "")[:700],
            "closure_layer":str(row.get("closure_layer") or ""),
            "failure_layer":str(row.get("failure_layer") or ""),
            "memory_class":str(row.get("memory_class") or ""),
            "principle_update_allowed":row.get("principle_update_allowed") is True,
            "broader_core_principle_falsified":row.get("broader_core_principle_falsified") is True,
            "search_closure_certified":True,
            "dead_end_certified":row.get("dead_end_certified") is True,
            "scientific_authority":False,
            "_order":order,
        })
    limit=max(1,int(limit));current={str(ref) for ref in (current_refs or set()) if str(ref)}
    if current:
        examples.sort(key=lambda row:(len(set(row.get("source_refs") or []) & current),row.get("_order",0)),reverse=True)
        chosen=examples[:limit]
    else:
        chosen=examples[-limit:]
    for row in chosen: row.pop("_order",None)
    return chosen


def _search_closure_reentry_audit(candidate:dict[str,Any],path:Path=DURABLE_PRINCIPLE_DEAD_END_JSON,prior_source_grounding:dict[str,Any]|None=None)->dict[str,Any]:
    lane=str(candidate.get("discovery_lane") or "").strip().upper();evidence=candidate.get("empirical_evidence") or {}
    refs={str((evidence.get(key) or {}).get("ref") or "").strip() for key in ("source_a","source_b") if str((evidence.get(key) or {}).get("ref") or "").strip()}
    grounding=prior_source_grounding if isinstance(prior_source_grounding,dict) else {}
    try: payload=json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError): payload={}
    matches=[]
    memory=payload.get("shadow_search_memory") or payload.get("shadow_dead_end_memory") or {}
    for row in _search_closure_rows(memory):
        primitive=str(row.get("search_primitive") or "").strip().upper();dead_refs={str(ref).strip() for ref in (row.get("current_source_refs") or []) if str(ref).strip()}
        if lane and primitive==lane and refs and dead_refs==refs:
            matches.append({"source_candidate_id":str(row.get("source_candidate_id") or ""),"match_kind":"TYPED_EXACT_SOURCE_SCOPE","reopen_condition":str(((row.get("counter_explanation") or {}).get("reopen_condition")) or row.get("reopen_only_if") or "")[:700],"source_refs":sorted(dead_refs)})
            continue
        closure=row.get("fresh_phenomenon_closure") or {}
        closure_ref=str(closure.get("source_ref") or "").strip();closed_hashes={str(value).strip() for value in (closure.get("closed_evidence_sha256") or []) if re.fullmatch(r"[0-9a-f]{64}",str(value).strip())}
        grounded_rows=[grounding.get(key) or {} for key in ("source_a","source_b")]
        exact_grounding=bool(grounded_rows and all(item.get("grounded") is True and item.get("evidence_sha256_verified") is True and re.fullmatch(r"[0-9a-f]{64}",str(item.get("evidence_sha256") or "")) for item in grounded_rows))
        grounded_refs={str(item.get("ref") or "").strip() for item in grounded_rows if str(item.get("ref") or "").strip()}
        grounded_hashes={str(item.get("evidence_sha256") or "").strip() for item in grounded_rows if str(item.get("evidence_sha256") or "").strip()}
        if closure_ref and closed_hashes and refs==dead_refs==grounded_refs=={closure_ref} and exact_grounding and grounded_hashes and grounded_hashes.issubset(closed_hashes):
            matches.append({"source_candidate_id":str(row.get("source_candidate_id") or ""),"match_kind":"CERTIFIED_EXACT_EVIDENCE_CLOSURE","reopen_condition":str(((row.get("counter_explanation") or {}).get("reopen_condition")) or row.get("reopen_only_if") or "")[:700],"source_refs":sorted(dead_refs),"grounded_evidence_sha256":sorted(grounded_hashes),"closed_evidence_sha256":sorted(closed_hashes)})
    return {"checked":True,"blocked":bool(matches),"matched_source_candidate_ids":[row["source_candidate_id"] for row in matches if row["source_candidate_id"]],"matches":matches,"reopen_requires_new_evidence":True,"scientific_authority":False}


_principle_dead_end_reentry_audit=_search_closure_reentry_audit  # legacy helper alias


def _private_dead_end_prompt_memory(storage:StorageSettings,public_memory:dict[str,Any],current_refs:set[str]|None=None)->dict[str,Any]:
    local=_local_blocked_problem_rows(storage)
    examples=[]
    for row in local[-12:]:
        examples.append({key:row.get(key) for key in ("title","discovery_lane","source_refs","matched_patterns","strongest_reduction","reason","lane_contract_verified","source_claims_grounded")})
    principle_examples=_durable_principle_dead_end_examples(current_refs=current_refs)
    blocked_by_lane={str(key):int(value or 0) for key,value in (public_memory.get("blocked_by_lane") or {}).items()}
    lane_search_priority=sorted(DISCOVERY_LANES,key=lambda lane:(blocked_by_lane.get(lane,0),DISCOVERY_LANES.index(lane)))
    return {
        "summary":{key:public_memory.get(key) for key in ("blocked_candidate_attempts","blocked_by_lane","reduction_pattern_counts","top_reduction_basin","repeated_reduction_basin")},
        "lane_search_priority":lane_search_priority,
        "recent_blocked_examples":examples,
        "typed_closed_basins":principle_examples,
        "typed_closed_basin_count":len(principle_examples),
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


def _provider_wall_clock_seconds(max_output_tokens:int)->float:
    configured=str(os.getenv("ARK_WALL_CLOCK_SECONDS") or "").strip()
    if configured:
        try:return min(max(float(configured),30.0),600.0)
        except ValueError:pass
    return 360.0 if int(max_output_tokens)>=5000 else 180.0


def _respond_with_wall_clock_deadline(client:ArkResponsesClient,*,wall_clock_seconds:float,**kwargs):
    """Bound one provider POST by total wall time, not only socket inactivity.

    The worker is daemonized because a timed-out POST has ambiguous provider acceptance.
    Callers must treat the timeout as an orphan and must not retry/fallback automatically.
    """
    result_queue=Queue(maxsize=1)
    def worker():
        try:result_queue.put(("result",client.respond(**kwargs)))
        except BaseException as error:result_queue.put(("error",error))
    thread=Thread(target=worker,daemon=True,name="ark-response-wall-clock")
    thread.start();thread.join(max(0.01,float(wall_clock_seconds)))
    if thread.is_alive():
        error=RuntimeError(f"Ark provider wall-clock timeout after {float(wall_clock_seconds):.1f}s without an auditable response")
        error.provider_wall_clock_timeout=True
        raise error
    kind,payload=result_queue.get_nowait()
    if kind=="error":raise payload
    return payload


def _ark(*,prompt,model,max_output_tokens,temperature=0.0,stage="problem_generation",allow_transport_fallback=True):
    base=ArkSettings.from_env(required=False)
    if not base.api_key: raise RuntimeError("ARK_API_KEY_NOT_CONFIGURED")
    timeout_floor=180.0 if int(max_output_tokens)>=5000 else 90.0
    settings=ArkSettings(api_key=base.api_key,base_url=base.base_url,default_model=base.default_model,timeout_seconds=min(max(base.timeout_seconds,timeout_floor),180.0),max_retries=0)
    priorities=list(stage_model_priority(stage))
    candidates=[model] if not allow_transport_fallback else [model]+[candidate for candidate in priorities if candidate!=model][:1]
    attempts=[];wall_clock_seconds=_provider_wall_clock_seconds(max_output_tokens)
    for index,candidate in enumerate(candidates):
        request_audit=_provider_request_audit(stage=stage,prompt=prompt,model=candidate,max_output_tokens=max_output_tokens,temperature=temperature)
        try:
            thinking=None if str(candidate).lower().startswith("glm") else "disabled"
            result=_respond_with_wall_clock_deadline(ArkResponsesClient(settings),wall_clock_seconds=wall_clock_seconds,prompt=prompt,model=candidate,max_output_tokens=max_output_tokens,temperature=temperature,thinking=thinking,store=True,allow_thinking_compatibility_fallback=allow_transport_fallback)
            attempts.append({**request_audit,"requested_model":candidate,"status":"success","resolved_model":str(result.get("resolved_model") or candidate),"assistant_output_present":True,"wall_clock_seconds":wall_clock_seconds})
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
            wall_clock_timeout=getattr(error,"provider_wall_clock_timeout",False) is True
            attempt={**request_audit,"requested_model":candidate,"status":"error-no-output","error_kind":kind or "non-retryable-provider-error","assistant_output_present":False,"provider_error_audit":_provider_error_audit(error),"wall_clock_seconds":wall_clock_seconds,"provider_wall_clock_timeout":wall_clock_timeout}
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
            if wall_clock_timeout or not kind or index>=len(candidates)-1:
                detail=";".join(f"{row['requested_model']}:{row.get('error_kind') or row['status']}" for row in attempts)
                final=RuntimeError(f"Ark provider failed before an auditable assistant output; attempts={detail}")
                final.transport_attempts=attempts;final.provider_wall_clock_timeout=wall_clock_timeout
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
        "paperability_axes":dict(raw.get("paperability_axes") or {}) if isinstance(raw.get("paperability_axes"),dict) else {},"paperability_claim":str(raw.get("paperability_claim") or "").strip(),
        "reviewer_attack":str(raw.get("reviewer_attack") or "").strip(),"reviewer_attack_class":str(raw.get("reviewer_attack_class") or "").strip(),"repair_axis":str(raw.get("repair_axis") or "").strip(),"why_attack_no_longer_applies":str(raw.get("why_attack_no_longer_applies") or "").strip(),
        "closest_work":dict(raw.get("closest_work") or {}) if isinstance(raw.get("closest_work"),dict) else {},"closest_work_distance":raw.get("closest_work_distance"),
        "mature_theory_baselines":raw.get("mature_theory_baselines") or [],"reduction_falsifiability_contract":raw.get("reduction_falsifiability_contract") or {},
        "same_information_nonreducibility":raw.get("same_information_nonreducibility") or {},"exact_prediction":str(raw.get("exact_prediction") or "").strip(),
        "strongest_same_information_baseline":str(raw.get("strongest_same_information_baseline") or "").strip(),"domain_transfer_audit":raw.get("domain_transfer_audit") or {},
        "saturation_scan":_normalize_saturation_scan(raw.get("saturation_scan")),"cheapest_problem_falsifier":str(raw.get("cheapest_problem_falsifier") or "").strip(),
        "endpoint_headroom_requirement":str(raw.get("endpoint_headroom_requirement") or "").strip(),"importance":str(raw.get("importance") or "").strip(),"likely_iclr_story":str(raw.get("likely_iclr_story") or "").strip(),
        "semantic_reduction_review":{"reviewed":False,"block_only":True,"verdict":"BLOCK","reviewer_model":"","raw_sha256":"","source_claims_grounded":False,"source_claim_grounding":{},"lane_contract_verified":False,"lane_contract_reason":"unreviewed","matched_patterns":[],"strongest_reduction":"unreviewed"},
        "authority":{k:False for k in ("method_design","experiment_blueprint","local_validation","p0","gpu","full_experiment")}}
_PRE_REVIEW_PROVISIONAL_BLOCKER_PREFIXES=("unresolved-exact-reduction-test:","saturation-exact-reduction-pending:")

def _pre_review_blockers(c,reg):
    audit=audit_problem_candidate(c,primary_evidence_by_ref=reg,require_primary_registry=True,require_semantic_review=False)
    blockers=[str(value) for value in audit.get("blockers") or []]
    pending=any(blocker.startswith(_PRE_REVIEW_PROVISIONAL_BLOCKER_PREFIXES) for blocker in blockers)
    contract=c.get("reduction_falsifiability_contract") or {}
    checked_prefix=("same_observable_information_checked","ex_ante_exact_prediction_checked","distinguishing_prediction_checked","scope_boundary_checked")
    provisional_contract_incomplete=bool(pending and isinstance(contract,dict) and all(contract.get(key) is True for key in checked_prefix) and contract.get("all_exact_reduction_tests_resolved") is False)
    hard=[]
    for blocker in blockers:
        if blocker.startswith(_PRE_REVIEW_PROVISIONAL_BLOCKER_PREFIXES):
            continue
        if blocker=="reduction-falsifiability-contract-incomplete" and provisional_contract_incomplete:
            continue
        hard.append(blocker)
    return sorted(set(hard))

def _annotate_search_closure_reentry(cands:list[dict[str,Any]],prior_grounding_by_candidate:dict[str,dict[str,Any]]|None=None)->list[dict[str,Any]]:
    prior=prior_grounding_by_candidate if isinstance(prior_grounding_by_candidate,dict) else {}
    for candidate in cands:
        candidate_id=str(candidate.get("candidate_id") or "")
        candidate["search_closure_reentry_audit"]=_search_closure_reentry_audit(candidate,prior_source_grounding=prior.get(candidate_id) or {})
    return cands


_annotate_principle_dead_end_reentry=_annotate_search_closure_reentry  # legacy helper alias


def _reviewable(c,reg):
    return bool(audit_problem_candidate(c,primary_evidence_by_ref=reg,require_primary_registry=True,require_semantic_review=False,allow_pending_reduction_for_semantic_review=True).get("passed"))

_PRE_F0_REDUCTION_BLOCKER_PREFIXES=(
    "unresolved-exact-reduction-test:",
    "saturation-exact-reduction-pending:",
    "mature-theory-valid-hard-veto:",
    "saturation-proven-hard-reduction:",
)

def _paperability_surviving_axes(candidate:dict[str,Any])->list[str]:
    axes=candidate.get("paperability_axes") or {}
    if not isinstance(axes,dict):return []
    return [axis for axis in PAPERABILITY_AXES if str((axes.get(axis) or {}).get("status") or "").strip().upper() in {"SUPPORTED","PLAUSIBLE"}]


def _pre_f0_route(candidate:dict[str,Any],registry:dict[str,dict[str,Any]])->dict[str,Any]:
    """Route only reduction-limited, paperable candidates to zero-authority evidence acquisition.

    This does not weaken the final Problem Gate. A positive cheap falsifier must return
    to exact same-information reduction before Paper Design eligibility.
    """
    audit=audit_problem_candidate(candidate,primary_evidence_by_ref=registry,require_primary_registry=True,require_semantic_review=False)
    blockers=[str(value) for value in audit.get("blockers") or []]
    reduction_blockers=[value for value in blockers if value.startswith(_PRE_F0_REDUCTION_BLOCKER_PREFIXES)]
    other_blockers=[value for value in blockers if value not in reduction_blockers and value!="reduction-falsifiability-contract-incomplete"]
    surviving=_paperability_surviving_axes(candidate);axes=candidate.get("paperability_axes") or {};p_status=str((axes.get("P") or {}).get("status") or "").strip().upper()
    hard_principle=any(value.startswith(("mature-theory-valid-hard-veto:","saturation-proven-hard-reduction:")) for value in reduction_blockers)
    non_principle=[axis for axis in surviving if axis!="P"]
    hard_principle_repairable=bool(hard_principle and p_status=="REDUCED" and non_principle)
    pending=any(value.startswith(("unresolved-exact-reduction-test:","saturation-exact-reduction-pending:")) for value in reduction_blockers)
    eligible=bool(not other_blockers and str(candidate.get("cheapest_problem_falsifier") or "").strip() and surviving and (pending or hard_principle_repairable))
    return {
        "eligible":eligible,
        "surviving_axes":surviving,
        "non_principle_surviving_axes":non_principle,
        "principle_axis_status":p_status,
        "reduction_blockers":reduction_blockers,
        "other_blockers":other_blockers,
        "route_reason":"P_REDUCED_NON_P_AXIS_SURVIVES" if hard_principle_repairable else ("EXACT_REDUCTION_PENDING" if pending else "NOT_REDUCTION_LIMITED"),
        "scientific_authority":False,
    }

def _pre_f0_candidate_row(normalized:dict[str,Any],route:dict[str,Any])->dict[str,Any]:
    evidence=normalized.get("empirical_evidence") or {};primary_refs=sorted({str((evidence.get(key) or {}).get("ref") or "").strip() for key in ("source_a","source_b") if str((evidence.get(key) or {}).get("ref") or "").strip().startswith("arXiv:")})
    return {
        "candidate_id":normalized.get("candidate_id"),"title":normalized.get("title"),"discovery_lane":normalized.get("discovery_lane"),"source_branch_id":normalized.get("source_branch_id"),"primary_refs":primary_refs,
        "paperability_axes":normalized.get("paperability_axes") or {},"surviving_paperability_axes":route.get("surviving_axes") or [],"non_principle_surviving_axes":route.get("non_principle_surviving_axes") or [],"route_reason":route.get("route_reason"),"reduction_blockers":route.get("reduction_blockers") or [],
        "exact_prediction":normalized.get("exact_prediction"),"strongest_same_information_baseline":normalized.get("strongest_same_information_baseline"),"cheapest_problem_falsifier":normalized.get("cheapest_problem_falsifier"),"endpoint_headroom_requirement":normalized.get("endpoint_headroom_requirement"),
        "post_f0_requirement":"RERUN_EXACT_SAME_INFORMATION_REDUCTION_BEFORE_PROBLEM_GATE","scientific_authority":False,"authority":{"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False},
    }

def _norm_text(value:str)->str:
    return " ".join(str(value or "").lower().split())

def _evidence_excerpt_matches(excerpt:str,evidence_text:str)->bool:
    excerpt_norm=_norm_text(excerpt);evidence_norm=_norm_text(evidence_text)
    if not excerpt_norm or not evidence_norm:return False
    if excerpt_norm in evidence_norm:return True
    # arXiv HTML/math extraction can duplicate rendered numerals (for example 8 -> 88 or
    # 0.56 -> 0.560.56). Ignore only numeric/formula rendering while requiring the lexical
    # word sequence itself to remain a contiguous exact span; this is not semantic/fuzzy match.
    excerpt_words=re.findall(r"[a-z]+(?:-[a-z]+)*",excerpt_norm);evidence_words=re.findall(r"[a-z]+(?:-[a-z]+)*",evidence_norm)
    if len(excerpt_words)<4 or len(excerpt_words)>len(evidence_words):return False
    width=len(excerpt_words)
    return any(evidence_words[index:index+width]==excerpt_words for index in range(len(evidence_words)-width+1))

def _source_grounding(review:dict[str,Any],candidate:dict[str,Any],registry:dict[str,dict[str,Any]])->tuple[dict[str,Any],bool]:
    support=review.get("source_claim_support") or {};out={};all_grounded=True
    evidence=candidate.get("empirical_evidence") or {}
    for key in ("source_a","source_b"):
        source=evidence.get(key) or {};ref=str(source.get("ref") or "").strip();record=registry.get(ref) or {}
        item=support.get(key) or {};supported=item.get("supported") is True;excerpt=str(item.get("evidence_excerpt") or "").strip();declared_source=str(item.get("evidence_source") or "").strip().lower()
        words=excerpt.split();excerpt_norm=_norm_text(excerpt);abstract=_norm_text(record.get("abstract") or "");role=str(source.get("evidence_role") or "").strip().upper()
        fact_rows=[fact for fact in (record.get("empirical_facts") or []) if isinstance(fact,dict)]
        typed=record.get("typed_evidence") or {};assumption_rows=[fact for fact in typed.get("operational_assumptions") or [] if isinstance(fact,dict)];failure_rows=[fact for fact in typed.get("measured_failures") or [] if isinstance(fact,dict)];boundary_rows=[fact for fact in typed.get("boundary_observations") or [] if isinstance(fact,dict)]
        facts=[_norm_text(str(fact.get("text") or "")) for fact in fact_rows];assumptions=[_norm_text(str(fact.get("text") or "")) for fact in assumption_rows];failures=[_norm_text(str(fact.get("text") or "")) for fact in failure_rows];boundaries=[_norm_text(str(fact.get("text") or "")) for fact in boundary_rows]
        abstract_match=_evidence_excerpt_matches(excerpt,record.get("abstract") or "");fact_match=bool(excerpt_norm and any(_evidence_excerpt_matches(excerpt,str(fact.get("text") or "")) for fact in fact_rows));assumption_match=bool(excerpt_norm and any(_evidence_excerpt_matches(excerpt,str(fact.get("text") or "")) for fact in assumption_rows));failure_match=bool(excerpt_norm and any(_evidence_excerpt_matches(excerpt,str(fact.get("text") or "")) for fact in failure_rows));boundary_match=bool(excerpt_norm and any(_evidence_excerpt_matches(excerpt,str(fact.get("text") or "")) for fact in boundary_rows))
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
        eligible_rows=assumption_rows if role=="OPERATIONAL_ASSUMPTION" else (fact_rows+failure_rows+boundary_rows)
        matched_hashes=sorted({str(row.get("text_sha256") or "").strip() for row in eligible_rows if _evidence_excerpt_matches(excerpt,str(row.get("text") or "")) and re.fullmatch(r"[0-9a-f]{64}",str(row.get("text_sha256") or "").strip())})
        evidence_sha256=matched_hashes[0] if grounded and len(matched_hashes)==1 else ""
        out[key]={"ref":ref,"supported":supported,"evidence_role":role,"evidence_kind":evidence_kind,"evidence_source":evidence_source,"declared_evidence_source":declared_source,"declared_source_valid":declared_source_valid,"declared_source_matches":declared_source_matches,"evidence_excerpt":excerpt,"excerpt_verified":excerpt_verified,"grounded":grounded,"evidence_sha256":evidence_sha256,"evidence_sha256_verified":bool(evidence_sha256)}
        all_grounded=all_grounded and grounded
    return out,all_grounded


def _load_prior_reviewer_grounding(*,raw_path:Path,expected_raw_sha256:str,candidates:list[dict[str,Any]],registry:dict[str,dict[str,Any]])->tuple[dict[str,dict[str,Any]],dict[str,Any]]:
    """Reuse only source excerpts from an archived reviewer, never its scientific judgment."""
    path=Path(raw_path);raw=path.read_text(encoding="utf-8");actual_sha=_sha(raw)
    if not re.fullmatch(r"[0-9a-f]{64}",str(expected_raw_sha256 or "")) or actual_sha!=str(expected_raw_sha256):raise ValueError("prior-reviewer-raw-sha-mismatch")
    payload=extract_json_object(raw);reviews={str(row.get("candidate_id") or ""):row for row in (payload.get("reviews") or []) if isinstance(row,dict)}
    out={};verified=0
    for candidate in candidates:
        candidate_id=str(candidate.get("candidate_id") or "");review=reviews.get(candidate_id) or {}
        grounding,_=_source_grounding(review,candidate,registry);out[candidate_id]=grounding
        if grounding and all((grounding.get(key) or {}).get("evidence_sha256_verified") is True for key in ("source_a","source_b")):verified+=1
    audit={"raw_sha256":actual_sha,"candidate_grounding_checked":len(candidates),"candidate_exact_evidence_grounding_verified":verified,"prior_verdict_reused":False,"prior_lane_contract_reused":False,"prior_reduction_judgment_reused":False,"scientific_authority":False}
    return out,audit


def _strip_json_fence(raw:str)->str:
    text=str(raw or "").strip()
    if text.startswith("```"):
        newline=text.find("\n")
        if newline<0:return text
        text=text[newline+1:]
        if text.rstrip().endswith("```"):text=text.rstrip()[:-3]
    return text.strip()


def _repair_block_only_reviewer_outer_braces(raw:str)->tuple[dict[str,Any]|None,str,list[int]]:
    """Repair only missing outer `}` delimiters around complete BLOCK review objects.

    The review strings and nested scientific fields are never edited. Each review fragment must
    become independently valid JSON by appending exactly one closing brace, and the recovered
    payload is accepted only when every verdict is BLOCK. CLEAR-capable recovery remains fail-closed.
    """
    text=_strip_json_fence(raw)
    try:
        payload=json.loads(text)
        if isinstance(payload,dict):return payload,text,[]
    except json.JSONDecodeError:
        pass
    prefix=re.match(r'^\{\s*"reviews"\s*:\s*\[',text)
    if not prefix:return None,"",[]
    starts=[match.start() for match in re.finditer(r'\{\s*"candidate_id"\s*:',text)]
    array_close=text.rfind("]");root_close=text.rfind("}")
    if not starts or array_close<starts[-1] or root_close<array_close or text[array_close+1:root_close].strip() or text[root_close+1:].strip():return None,"",[]
    insertions=[]
    for index,start in enumerate(starts):
        if index+1<len(starts):
            boundary=starts[index+1]-1
            while boundary>=0 and text[boundary].isspace():boundary-=1
            if boundary<start or text[boundary]!=",":return None,"",[]
        else:boundary=array_close
        fragment=text[start:boundary].strip()
        try:
            parsed=json.loads(fragment);needs_close=False
        except json.JSONDecodeError:
            try:parsed=json.loads(fragment+"}");needs_close=True
            except json.JSONDecodeError:return None,"",[]
        if not isinstance(parsed,dict) or not str(parsed.get("candidate_id") or "").strip() or str(parsed.get("verdict") or "").strip().upper()!="BLOCK":return None,"",[]
        if needs_close:insertions.append(boundary)
    if not insertions:return None,"",[]
    repaired=text
    for offset in sorted(insertions,reverse=True):repaired=repaired[:offset]+"}"+repaired[offset:]
    try:payload=json.loads(repaired)
    except json.JSONDecodeError:return None,"",[]
    reviews=payload.get("reviews") if isinstance(payload,dict) else None
    if set(payload or {})!={"reviews"} or not isinstance(reviews,list) or len(reviews)!=len(starts) or any(not isinstance(row,dict) or str(row.get("verdict") or "").strip().upper()!="BLOCK" for row in reviews):return None,"",[]
    candidate_ids=[str(row.get("candidate_id") or "").strip() for row in reviews]
    if any(not value for value in candidate_ids) or len(candidate_ids)!=len(set(candidate_ids)):return None,"",[]
    return payload,repaired,insertions


def recover_archived_block_only_reviewer_raw(*,storage:StorageSettings,reviewer_raw_path:Path,reviewer_raw_sha256:str,resolved_model:str="",run_id:str="archived-reviewer-recovery")->dict[str,Any]:
    """Create a zero-provider audit receipt for a malformed archived BLOCK-only reviewer raw."""
    path=Path(reviewer_raw_path);raw=path.read_text(encoding="utf-8");actual_sha=_sha(raw)
    if not re.fullmatch(r"[0-9a-f]{64}",str(reviewer_raw_sha256 or "")) or actual_sha!=str(reviewer_raw_sha256):raise ValueError("reviewer-raw-sha-mismatch")
    payload,repaired,offsets=_repair_block_only_reviewer_outer_braces(raw)
    if payload is None or not offsets:raise ValueError("reviewer-raw-not-safe-block-only-punctuation-repair")
    repaired_sha=_sha(repaired);root=_root(storage)/"reviewer-recoveries";root.mkdir(parents=True,exist_ok=True)
    repaired_path=root/f"{run_id}-{actual_sha[:12]}-repaired.json";receipt_path=root/f"{run_id}-{actual_sha[:12]}-receipt.json"
    repaired_path.write_text(repaired+"\n",encoding="utf-8")
    candidate_ids=[str(row.get("candidate_id") or "") for row in payload.get("reviews") or []]
    receipt={"schema_version":"1.0","run_id":run_id,"status":"PARSE_REPAIRED_MISSING_REVIEW_OUTER_BRACES_BLOCK_ONLY_ZERO_AUTHORITY","resolved_model":str(resolved_model or ""),"raw_sha256":actual_sha,"repaired_sha256":repaired_sha,"repair_type":"MISSING_REVIEW_OUTER_CLOSING_BRACES","inserted_closing_brace_count":len(offsets),"insertion_offsets_in_stripped_json":offsets,"candidate_ids":candidate_ids,"all_recovered_verdicts_block":True,"review_string_content_mutated":False,"nested_review_fields_mutated":False,"provider_calls_executed":0,"scientific_authority":False,"authority":{"paper":False,"method":False,"experiment":False,"p0":False,"gpu":False}}
    receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return receipt


def _apply_reviews(cands,payload,requested,resolved,generator_resolved,raw_sha,registry):
    by={str(r.get("candidate_id") or ""):r for r in (payload or {}).get("reviews") or [] if isinstance(r,dict)};known={r["key"] for r in REDUCTION_PATTERNS};generator_models={x for x in str(generator_resolved or "").split("|") if x};ind=bool(resolved and generator_models and resolved not in generator_models)
    for c in cands:
        r=by.get(c["candidate_id"]) or {};v=str(r.get("verdict") or "BLOCK").upper();matched=sorted({str(x) for x in r.get("matched_patterns") or [] if str(x) in known});grounding,grounded=_source_grounding(r,c,registry);lane_verified=r.get("lane_contract_verified") is True;reduction_class=str(r.get("reduction_class") or "").strip().upper();exact_test=str(r.get("exact_reduction_test") or "").strip()
        if reduction_class in {"VALID_HARD_VETO","NEEDS_EXACT_REDUCTION_TEST"}:v="BLOCK"
        if not ind or not grounded or not lane_verified:v="BLOCK"
        final_clear=bool(v=="CLEAR" and ind and grounded and lane_verified)
        c["semantic_reduction_review"]={"reviewed":bool(r) and bool(raw_sha),"block_only":True,"verdict":"CLEAR" if final_clear else "BLOCK","reviewer_model":resolved or requested,"reviewer_requested_model":requested,"generator_resolved_model":generator_resolved,"independent_resolved_model":ind,"raw_sha256":raw_sha,"source_claims_grounded":grounded,"source_claim_grounding":grounding,"lane_contract_verified":lane_verified,"lane_contract_reason":str(r.get("lane_contract_reason") or ""),"matched_patterns":matched,"reduction_class":reduction_class,"exact_reduction_test":exact_test,"strongest_reduction":str(r.get("strongest_reduction") or ("reviewer-not-independent" if not ind else ("source-claim-grounding-failed" if not grounded else ("lane-contract-review-failed" if not lane_verified else "review-unavailable")))),"reason":str(r.get("reason") or ""),"authority":False}
        contract=dict(c.get("reduction_falsifiability_contract") or {})
        if reduction_class in {"VALID_HARD_VETO","NEEDS_EXACT_REDUCTION_TEST"}:
            contract["all_exact_reduction_tests_resolved"]=False
        # A block-only AI reviewer may add blockers, but CLEAR cannot by itself
        # resolve a generator-declared exact-reduction falsifier.  Pending status
        # must remain pending until non-AI evidence closes the registered test.
        c["reduction_falsifiability_contract"]=contract
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
        lane=str(item.get("lane") or "").strip().upper();status=str(item.get("status") or "").strip().upper();reason=" ".join(str(item.get("reason") or "").split())[:500].rstrip()
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
    return {"zero_candidates_is_valid":True,"discovery_operator_version":DISCOVERY_OPERATOR_VERSION,"single_source_anomaly_first_enabled":True,"source_coverage_saturation_reopens_once_on_operator_change":True,"search_portfolio_enabled":portfolio,"search_portfolio_is_shadow_only":not portfolio,"legacy_published_search_portfolio_remains_shadow_only":True,"search_portfolio_primitives":list(SEARCH_PORTFOLIO_PRIMITIVES),"canonical_transaction_forbids_search_portfolio":not portfolio,"one_content_addressed_pool_allows_at_most_one_live_generator_call":not portfolio,"one_content_addressed_pool_allows_at_most_one_live_generator_call_per_discovery_operator":not portfolio,"one_content_addressed_pool_allows_at_most_one_discovery_transaction":True,"bounded_provider_subcalls_inside_discovery_transaction":portfolio,"portfolio_generator_subcall_budget":48 if portfolio else 1,"portfolio_semantic_reviewer_subcall_budget":4 if portfolio else 1,"one_generator_call_max":not portfolio,"one_semantic_reviewer_call_max":not portfolio,"expansion_precedes_reduction":portfolio,"attack_repair_split_before_formulation":portfolio,"reviewer_objection_is_evolution_input_not_terminal_stop":portfolio,"paperability_axes":dict(PAPERABILITY_AXES) if portfolio else {},"principle_reduction_does_not_auto_close_other_paperability_axes":portfolio,"cheap_problem_falsifier_may_precede_final_exact_reduction":portfolio,"pre_f0_evidence_acquisition_has_zero_scientific_authority":True,"exact_reduction_required_before_final_problem_gate":True,"mature_theory_veto_delayed_until_formulation":portfolio,"diversity_archives_required":portfolio,"branch_lineage_required":portfolio,"reduction_falsifiability_contract_required":portfolio,"generic_theory_label_cannot_veto":portfolio,"format_retry_forbidden":True,"transport_only_no_output_fallback_allowed":True,"transport_fallback_max_additional_provider_attempts":1,"transport_fallback_requires_zero_auditable_assistant_output":True,"transport_fallback_is_single_logical_generator_call":True,"thinking_disabled":True,"multi_lane_discovery_enabled":True,"allowed_discovery_lanes":list(DISCOVERY_LANES),"forbidden_discovery_lanes":list(FORBIDDEN_DISCOVERY_LANES),"verified_primary_registry_required":True,"semantic_reviewer_is_block_only":True,"independent_reviewer_must_ground_both_source_claims_to_exact_primary_evidence_excerpts":True,"reviewer_declared_excerpt_source_is_audit_metadata_not_grounding_authority":True,"exact_excerpt_location_is_machine_inferred":True,"independent_reviewer_must_verify_lane_contract":True,"reduction_pending_may_reach_block_only_semantic_review":True,"reduction_pending_cannot_pass_problem_gate":True,"contradiction_requires_matched_intervention_semantics":True,"contradiction_requires_matched_adaptation_stage":True,"same_resolved_model_cannot_count_as_independent_review":True,"raw_model_output_archived_before_parsing":True,"generation_notes_are_advisory_not_scientific_authority":True,"zero_candidate_rationale_required":True,"discovery_saturation_memory_has_zero_scientific_authority":True,"reviewer_blocked_problem_memory_has_zero_scientific_authority":True,"repeated_reduction_basin_requires_search_escape":True,"portable_blocked_problem_memory_is_search_control_only":True,"one_generator_call_must_audit_all_discovery_lanes":not portfolio,"portfolio_expansion_must_audit_all_discovery_lanes":portfolio,"lane_search_diagnostics_have_zero_scientific_authority":True,"lane_search_output_order_is_canonicalized_after_validation":True,"historically_underexplored_lanes_are_searched_first":True,"lane_search_never_requires_candidate":True,"last_completed_lane_search_is_portable_zero_authority_receipt":True,"terminal_zero_call_skip_preserves_last_completed_lane_search":True,"portable_review_receipts_are_scheduler_metadata_only":True,"portable_review_receipts_have_zero_scientific_authority":True,"primary_source_coverage_receipts_are_inherited_transactionally":True,"source_coverage_saturation_skips_model_call":True,"source_coverage_saturation_skips_model_call_after_current_operator_receipt":True,"source_coverage_saturation_operator_upgrade_recompile_is_explicit_exception":True,"incomplete_retrieval_without_new_lane_source_skips_model_call":True,"retrieval_incomplete_is_compute_control_not_scientific_negative":True,"carrier_probe_pending_skips_model_call":True,"carrier_probe_pending_is_compute_control_not_scientific_negative":True,"source_coverage_saturation_is_compute_control_not_scientific_negative":True,"new_lane_grounded_primary_source_reopens_generation":True,"candidate_inbox_has_zero_scientific_authority":True,"automatic_method_authority":False,"automatic_experiment_authority":False,"automatic_p0_authority":False}


def _empty_summary(primary_evidence_records=0):
    lanes={lane:0 for lane in DISCOVERY_LANES};lanes["OTHER"]=0
    return {"primary_evidence_records":primary_evidence_records,"raw_seeds":0,"semantic_unique_seeds":0,"unique_problem_families":0,"breadth_archive":0,"archive_pairwise_distance":0.0,"evolved_branches":0,"max_branch_depth":0,"reviewer_attacks":0,"repair_children":0,"portfolio_calls":0,"pre_f0_eligible":0,"generated":0,"structurally_reviewable":0,"semantic_clear":0,"semantic_blocked":0,"written_to_auto_inbox":0,"generated_by_lane":dict(lanes),"structurally_reviewable_by_lane":dict(lanes),"semantic_clear_by_lane":dict(lanes),"semantic_blocked_by_lane":dict(lanes)}


def run_problem_generator(*,storage=None,primary_pool_path=None,auto_inbox_path=None,saturation_ledger_path=None,generator_model=None,reviewer_model=None,generator_responder:Responder|None=None,reviewer_responder:Responder|None=None,now=None,pool_max_age_hours=MAX_POOL_AGE_HOURS,max_candidates=MAX_CANDIDATES,blocked_problem_memory:dict[str,Any]|None=None,portfolio_mode:bool|None=None,target_raw_seeds:int=DEFAULT_RAW_SEEDS,strict_provider:bool=False,defer_reviewer:bool=False,allow_orphan_replay:bool=False):
    storage=storage or StorageSettings.from_env();primary_pool_path=primary_pool_path or private_primary_pool_path(storage);auto_inbox_path=auto_inbox_path or default_auto_inbox_path(storage)
    generator_model=generator_model or os.getenv("PAPER_FIRST_PROBLEM_GENERATOR_MODEL",GENERATOR_MODEL);reviewer_model=reviewer_model or os.getenv("PAPER_FIRST_PROBLEM_REVIEW_MODEL",REVIEWER_MODEL);current=(now or _now_dt()).astimezone(timezone.utc);run_id=current.strftime("%Y%m%dT%H%M%SZ");portfolio_mode=False if portfolio_mode is None else bool(portfolio_mode)
    archived=_archive_previous(storage,auto_inbox_path);pool=load_private_primary_pool(primary_pool_path) or {};reg=_registry(pool);psha=_pool_sha(pool) if pool else "";d=_parse_iso(pool.get("generated_at"));age=None if d is None else max(0.0,(current-d).total_seconds()/3600)
    inherited_receipts=[dict(row) for row in ((pool.get("source_coverage") or {}).get("portable_review_receipts") or []) if isinstance(row,dict)]
    blocked_problem_memory=blocked_problem_memory or _public_blocked_problem_memory(storage)
    dead_end_prompt_memory=_private_dead_end_prompt_memory(storage,blocked_problem_memory,current_refs=set(reg))
    policy=_base_policy(portfolio=portfolio_mode)
    generator_is_glm=str(generator_model).lower().startswith("glm");generator_max_output_tokens=15000 if generator_is_glm else 6500
    policy["strict_provider_transport"]=bool(strict_provider);policy["semantic_reviewer_deferred"]=bool(defer_reviewer);policy["thinking_compatibility_repost_allowed"]=not bool(strict_provider)
    policy["thinking_disabled"]=not generator_is_glm;policy["generator_thinking_profile"]="provider-default" if generator_is_glm else "disabled";policy["generator_max_output_tokens"]=generator_max_output_tokens
    policy["provider_orphan_replay_forbidden"]=not bool(allow_orphan_replay);policy["provider_orphan_override_requires_explicit_operator_action"]=True
    if strict_provider:
        policy["transport_only_no_output_fallback_allowed"]=False;policy["transport_fallback_max_additional_provider_attempts"]=0
    state={"schema_version":"3.0-double-funnel" if portfolio_mode else "2.5","generated_at":_now(),"run_id":run_id,"primary_pool_path":str(primary_pool_path),"auto_inbox_path":str(auto_inbox_path),"archived_previous_auto_inbox":archived,"generator_model":generator_model,"reviewer_model":reviewer_model,"policy":policy,"summary":_empty_summary(len(reg)),"raw_artifacts":{},"generation_notes":"","search_diagnostics":{"lane_search_priority":list(SEARCH_PORTFOLIO_PRIMITIVES if portfolio_mode else (dead_end_prompt_memory.get("lane_search_priority") or DISCOVERY_LANES)),"lane_search_complete":False,"lane_search":[],"last_completed_lane_search":{},"scientific_authority":False},"saturation_memory":{"ledger_entries":len(_load_saturation_ledger(storage,saturation_ledger_path)),"prior_identical_zero_runs":0,"current_run_recorded":False,"portable_review_receipts":inherited_receipts[-PORTABLE_REVIEW_RECEIPT_LIMIT:],"blocked_problem_memory":blocked_problem_memory,"scientific_authority":False},"pre_f0_candidates":[],"candidates":[]}
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
    generator_prompt_text=""
    if portfolio_mode:
        state["discovery_transaction_audit"]={
            "mode":"CANONICAL_DOUBLE_FUNNEL",
            "pool_sha256":psha,
            "discovery_operator_version":DISCOVERY_OPERATOR_VERSION,
            "target_raw_seeds":int(target_raw_seeds),
            "generator_subcall_budget":int(policy["portfolio_generator_subcall_budget"]),
            "semantic_reviewer_subcall_budget":int(policy["portfolio_semantic_reviewer_subcall_budget"]),
            "historical_shadow_portfolio_promoted":False,
            "scientific_authority":False,
        }
    else:
        generator_prompt_text=generator_prompt(list(reg.values()),dead_end_memory=dead_end_prompt_memory)
        generator_request_audit=_provider_request_audit(stage="problem_generation",prompt=generator_prompt_text,model=generator_model,max_output_tokens=generator_max_output_tokens,temperature=0.0)
        state["generator_request_audit"]=generator_request_audit
        if generator_responder is None and not allow_orphan_replay and _provider_orphan_exists(storage,generator_request_audit["request_fingerprint"]):
            state["provider_orphan_audits"]=[{"request_fingerprint":generator_request_audit["request_fingerprint"],"status":"ORPHANED_POST_NO_RECEIPT","requested_model":generator_model,"stage":"problem_generation","scientific_authority":False}]
            state["coverage_skip_reason"]="An identical provider request previously timed out without a response receipt. Automatic replay is blocked because provider acceptance is ambiguous; explicit operator override is required."
            return finish("SKIPPED_ORPHANED_PROVIDER_REQUEST")
    call=generator_responder or (lambda **kwargs:_ark(stage="problem_generation",allow_transport_fallback=not strict_provider,**kwargs));rows=[];generator_resolved_models=[]
    if portfolio_mode:
        provenance=[];generator_subcall_budget=int(policy["portfolio_generator_subcall_budget"]);portfolio_transport_abort=Event();portfolio_orphan_audits=[]
        def portfolio_call(*,role,prompt,model,max_output_tokens):
            if portfolio_transport_abort.is_set():raise RuntimeError("canonical-double-funnel-transport-fail-fast")
            if len(provenance)>=generator_subcall_budget:raise RuntimeError("canonical-double-funnel-generator-subcall-budget-exhausted")
            temperature=0.85 if role.startswith("expand-") else (0.60 if role.startswith("evolve-g1") else (0.35 if role.startswith("evolve-g2") else (0.45 if role.startswith("repair-") else 0.15)))
            request_audit=_provider_request_audit(stage=f"portfolio:{role}",prompt=prompt,model=model,max_output_tokens=max_output_tokens,temperature=temperature)
            if generator_responder is None and not allow_orphan_replay and _provider_orphan_exists(storage,request_audit["request_fingerprint"]):
                portfolio_orphan_audits.append({"request_fingerprint":request_audit["request_fingerprint"],"status":"ORPHANED_POST_NO_RECEIPT","requested_model":model,"stage":f"portfolio:{role}","replay_blocked_before_provider":True,"scientific_authority":False});portfolio_transport_abort.set()
                raise RuntimeError(f"portfolio-provider-orphan-replay-blocked:{role}:{request_audit['request_fingerprint']}")
            try:res=call(prompt=prompt,model=model,max_output_tokens=max_output_tokens,temperature=temperature)
            except Exception as error:
                attempts=list(getattr(error,"transport_attempts",[]) or []);orphan_audits=_archive_provider_orphans(storage,run_id,f"portfolio:{role}",attempts)
                if orphan_audits:
                    portfolio_orphan_audits.extend(orphan_audits);portfolio_transport_abort.set()
                raise
            raw=str(res.get("text") or "");path,sha=_write_raw(storage,run_id,role,model,raw);resolved=str(res.get("resolved_model") or model);generator_resolved_models.append(resolved);attempts=list(res.get("transport_attempts") or []);safe_attempts,receipt_audits=_archive_provider_receipts(storage,run_id,role,attempts);orphan_audits=_archive_provider_orphans(storage,run_id,f"portfolio:{role}",attempts)
            replay_meta=_archived_replay_metadata(res,sha,f"portfolio:{role}",expected_request_fingerprint=request_audit["request_fingerprint"])
            entry={"role":role,"sha256":sha,"requested_model":model,"resolved_model":resolved,"temperature":temperature,"request_fingerprint":request_audit["request_fingerprint"],"transport_attempts":safe_attempts,"provider_calls_executed":0 if replay_meta else 1,"scientific_authority":False,**replay_meta}
            if receipt_audits:entry["provider_receipt_audits"]=receipt_audits
            if orphan_audits:entry["provider_orphan_audits"]=orphan_audits
            provenance.append(entry);return res
        try:
            portfolio=run_search_portfolio(records=list(reg.values()),call=portfolio_call,model=generator_model,target_raw_seeds=target_raw_seeds,dead_end_memory=dead_end_prompt_memory)
            if portfolio_transport_abort.is_set():
                state["provider_orphan_audits"]=portfolio_orphan_audits[-8:]
                fingerprints=sorted({str(row.get("request_fingerprint") or "") for row in portfolio_orphan_audits if row.get("request_fingerprint")})
                raise RuntimeError("canonical-double-funnel-ambiguous-provider-orphan-fail-fast:"+",".join(fingerprints[:4]))
            formulated=portfolio.get("formulated_candidates") or [];machine_reviewable=[];pre_f0_eligible=[];machine_blocked=[]
            for raw_candidate in formulated:
                normalized=_normalize(raw_candidate,reg);audit=audit_problem_candidate(normalized,primary_evidence_by_ref=reg,require_primary_registry=True,require_semantic_review=False)
                if audit.get("passed"):
                    machine_reviewable.append(raw_candidate);continue
                pre_f0=_pre_f0_route(normalized,reg)
                if pre_f0.get("eligible"):
                    pre_f0_eligible.append(_pre_f0_candidate_row(normalized,pre_f0));continue
                machine_blocked.append({"candidate_id":normalized.get("candidate_id"),"title":normalized.get("title"),"discovery_lane":normalized.get("discovery_lane"),"blockers":audit.get("blockers") or [],"surviving_paperability_axes":pre_f0.get("surviving_axes") or []})
            rows=machine_reviewable;state["pre_f0_candidates"]=pre_f0_eligible;portfolio["machine_reduction_audit"]={"reviewable":len(machine_reviewable),"pre_f0_eligible":len(pre_f0_eligible),"blocked":len(machine_blocked),"pre_f0_rows":pre_f0_eligible,"blocked_rows":machine_blocked,"scientific_authority":False}
            private_dir=_root(storage)/"search-portfolios";private_dir.mkdir(parents=True,exist_ok=True);private_path=private_dir/f"{run_id}-portfolio.json";private_text=json.dumps(portfolio,ensure_ascii=False,indent=2)+"\n";private_path.write_text(private_text,encoding="utf-8");private_sha=_sha(private_text)
            state["search_portfolio_private_path"]=str(private_path);state["portfolio_provenance"]=provenance
            public_keys=("policy","config","summary","lane_counts","archive_lane_counts","family_counts");state["search_portfolio"]={k:portfolio.get(k) for k in public_keys};state["search_portfolio"]["archive_counts"]={k:len(v) for k,v in (portfolio.get("archives") or {}).items()};state["search_portfolio"]["scientific_authority"]=False
            ps=portfolio.get("summary") or {};ps["machine_reviewable"]=len(machine_reviewable);ps["pre_f0_eligible"]=len(pre_f0_eligible);ps["machine_reduction_blocked"]=len(machine_blocked);state["search_portfolio"]["summary"]=ps;state["summary"].update({"raw_seeds":ps.get("raw_seeds",0),"semantic_unique_seeds":ps.get("semantic_unique",0),"unique_problem_families":ps.get("unique_problem_families",0),"breadth_archive":ps.get("breadth_archive",0),"archive_pairwise_distance":ps.get("mean_archive_pairwise_distance",0.0),"evolved_branches":ps.get("evolved_branches",0),"max_branch_depth":ps.get("max_branch_depth",0),"reviewer_attacks":ps.get("reviewer_attacks",0),"repair_children":ps.get("repair_children",0),"pre_f0_eligible":len(pre_f0_eligible),"portfolio_calls":ps.get("portfolio_calls",0)})
            lane_counts=portfolio.get("lane_counts") or {};priority=list(state["search_diagnostics"]["lane_search_priority"]);state["search_diagnostics"].update({"lane_search_complete":True,"lane_search":[{"lane":lane,"status":"EXPANDED" if int(lane_counts.get(lane) or 0)>0 else "EMPTY","raw_seed_count":int(lane_counts.get(lane) or 0),"reason":"Search Portfolio expansion shard produced grounded seeds." if int(lane_counts.get(lane) or 0)>0 else "No machine-valid grounded seed survived expansion contract."} for lane in priority]})
            state["generation_notes"]=(f"Canonical double funnel expanded {ps.get('raw_seeds',0)} grounded raw seeds into {ps.get('semantic_unique',0)} semantic-unique / {ps.get('unique_problem_families',0)} structural families, evolved {ps.get('evolved_branches',0)} branches, issued {ps.get('reviewer_attacks',0)} attacks and {ps.get('repair_children',0)} repair children, formulated {ps.get('formulated_candidates',0)}, routed {len(pre_f0_eligible)} to zero-authority pre-F0 evidence acquisition, and left {len(machine_reviewable)} candidates eligible for independent semantic review after exact machine reduction. Pre-F0 is not a Problem-Gate pass; exact same-information reduction remains mandatory before Paper Design.")
            synth=_sha(json.dumps({"portfolio_sha256":private_sha,"calls":[x["sha256"] for x in provenance]},sort_keys=True,separators=(",",":")));resolved_join="|".join(sorted(set(generator_resolved_models))) or generator_model;state["raw_artifacts"]["generator"]={"sha256":synth,"requested_model":generator_model,"resolved_model":resolved_join,"portfolio":True,"portfolio_sha256":private_sha,"calls":len(provenance),"provider_calls_executed":sum(int(x.get("provider_calls_executed") or 0) for x in provenance),"archived_replay_subcalls":sum(x.get("raw_replayed_without_provider") is True for x in provenance)}
        except Exception as e:state["error"]=f"{type(e).__name__}:{str(e)[:300]}";state["portfolio_provenance"]=provenance;return finish("GENERATOR_ERROR_ZERO_AUTHORITY")
    else:
        try:
            res=call(prompt=generator_prompt_text,model=generator_model,max_output_tokens=generator_max_output_tokens);raw=str(res.get("text") or "");p,sha=_write_raw(storage,run_id,"generator",generator_model,raw);resolved=str(res.get("resolved_model") or generator_model);generator_resolved_models=[resolved];transport_attempts=list(res.get("transport_attempts") or []);safe_attempts,receipt_audits=_archive_provider_receipts(storage,run_id,"generator",transport_attempts);orphan_audits=_archive_provider_orphans(storage,run_id,"problem_generation",transport_attempts);replay_meta=_archived_replay_metadata(res,sha,"generator",expected_request_fingerprint=generator_request_audit["request_fingerprint"]);state["raw_artifacts"]["generator"]={"path":p,"sha256":sha,"requested_model":generator_model,"resolved_model":resolved,"transport_attempts":safe_attempts,"transport_fallback_used":bool(res.get("transport_fallback_used")),"provider_calls_executed":0 if replay_meta else 1,**replay_meta};
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
        cands=_annotate_search_closure_reentry([_normalize(r,reg) for r in rows])
        try:_validate_lane_search_candidates(lane_search,cands)
        except Exception as e:state["error"]=f"{type(e).__name__}:{str(e)[:300]}";return finish("GENERATOR_ERROR_ZERO_AUTHORITY")
        state["search_diagnostics"].update({"lane_search_complete":True,"lane_search":lane_search});reviewable=[c for c in cands if _reviewable(c,reg)];state["summary"].update({"generated":len(cands),"structurally_reviewable":len(reviewable),"generated_by_lane":_count_by_lane(cands),"structurally_reviewable_by_lane":_count_by_lane(reviewable)})
    if portfolio_mode:
        cands=_annotate_search_closure_reentry([_normalize(r,reg) for r in rows]);reviewable=[c for c in cands if _reviewable(c,reg)];state["summary"].update({"generated":len(cands),"structurally_reviewable":len(reviewable),"generated_by_lane":_count_by_lane(cands),"structurally_reviewable_by_lane":_count_by_lane(reviewable)})
    if reviewable and defer_reviewer:
        state["summary"].update({"semantic_clear":0,"semantic_blocked":0,"semantic_review_unavailable":len(reviewable),"written_to_auto_inbox":0,"semantic_clear_by_lane":_count_by_lane([]),"semantic_blocked_by_lane":_count_by_lane([]),"semantic_review_unavailable_by_lane":_count_by_lane(reviewable)})
        state["candidates"]=[{"candidate_id":c["candidate_id"],"title":c["title"],"discovery_lane":c["discovery_lane"],"source_branch_id":c.get("source_branch_id") or "","source_refs":[c["empirical_evidence"]["source_a"]["ref"],c["empirical_evidence"]["source_b"]["ref"]],"semantic_verdict":"UNREVIEWED","lane_contract_verified":False,"matched_patterns":[]} for c in cands]
        return finish("GENERATED_AWAIT_SEMANTIC_REVIEW",[])
    if reviewable:
        call2=reviewer_responder or (lambda **kwargs:_ark(stage="semantic_review",allow_transport_fallback=not strict_provider,**kwargs));batch_size=6 if portfolio_mode else max(1,len(reviewable));review_receipts=[];gen_resolved="|".join(sorted(set(generator_resolved_models))) or generator_model
        for start in range(0,len(reviewable),batch_size):
            batch=reviewable[start:start+batch_size]
            try:
                role=f"semantic-review-{start//batch_size+1}" if portfolio_mode else "semantic-review";review_prompt_text=reviewer_prompt(batch,reg);review_max_tokens=5200 if portfolio_mode else 4200;review_request_audit=_provider_request_audit(stage="semantic_review",prompt=review_prompt_text,model=reviewer_model,max_output_tokens=review_max_tokens,temperature=0.0)
                res=call2(prompt=review_prompt_text,model=reviewer_model,max_output_tokens=review_max_tokens);raw=str(res.get("text") or "");p,sha=_write_raw(storage,run_id,role,reviewer_model,raw);rresolved=str(res.get("resolved_model") or reviewer_model);safe_attempts,receipt_audits=_archive_provider_receipts(storage,run_id,role,list(res.get("transport_attempts") or []));replay_meta=_archived_replay_metadata(res,sha,role,expected_request_fingerprint=review_request_audit["request_fingerprint"]);review_receipt={"sha256":sha,"requested_model":reviewer_model,"resolved_model":rresolved,"request_fingerprint":review_request_audit["request_fingerprint"],"transport_attempts":safe_attempts,"transport_fallback_used":bool(res.get("transport_fallback_used")),"provider_calls_executed":0 if replay_meta else 1,**replay_meta};
                if receipt_audits:review_receipt["provider_receipt_audits"]=receipt_audits
                review_receipts.append(review_receipt);_apply_reviews(batch,extract_json_object(raw),reviewer_model,rresolved,gen_resolved,sha,reg)
            except Exception as e:
                role=f"semantic-review-{start//batch_size+1}" if portfolio_mode else "semantic-review";safe_attempts,receipt_audits=_archive_provider_receipts(storage,run_id,role,list(getattr(e,"transport_attempts",[]) or []));state.setdefault("semantic_review_errors",[]).append(f"batch-{start//batch_size+1}:{type(e).__name__}:{str(e)[:240]}")
                if safe_attempts:state.setdefault("semantic_review_transport_attempts",[]).append({"batch":start//batch_size+1,"attempts":safe_attempts})
                if receipt_audits:state.setdefault("provider_receipt_audits",[]).extend(receipt_audits)
                _apply_reviews(batch,None,reviewer_model,"",gen_resolved,"",reg)
        if portfolio_mode:
            state["semantic_reviewer_batches"]=review_receipts
            if review_receipts:state["raw_artifacts"]["semantic_reviewer"]={"sha256":_sha("|".join(str(row.get("sha256") or "") for row in review_receipts)),"requested_model":reviewer_model,"resolved_model":"|".join(sorted({str(row.get('resolved_model') or '') for row in review_receipts if row.get('resolved_model')})),"calls":len(review_receipts),"provider_calls_executed":sum(int(row.get("provider_calls_executed") or 0) for row in review_receipts),"archived_replay_subcalls":sum(row.get("raw_replayed_without_provider") is True for row in review_receipts)}
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
    state["candidates"]=[{"candidate_id":c["candidate_id"],"title":c["title"],"discovery_lane":c["discovery_lane"],"source_branch_id":c.get("source_branch_id") or "","source_refs":[c["empirical_evidence"]["source_a"]["ref"],c["empirical_evidence"]["source_b"]["ref"]],"paperability_axes":c.get("paperability_axes") or {},"semantic_verdict":c["semantic_reduction_review"]["verdict"],"lane_contract_verified":c["semantic_reduction_review"].get("lane_contract_verified") is True,"matched_patterns":c["semantic_reduction_review"].get("matched_patterns") or []} for c in cands]
    if cands:return finish("GENERATED_AWAIT_PROBLEM_GATE",cands)
    if portfolio_mode and state.get("pre_f0_candidates"):return finish("GENERATED_PRE_F0_EVIDENCE_ACQUISITION",[])
    return finish("GENERATED_ZERO_CANDIDATES",[])


def resume_semantic_reviewer(*,storage=None,primary_pool_path:Path,generator_raw_path:Path,generator_raw_sha256:str,generator_requested_model:str,generator_resolved_model:str,source_generator_run_id:str,reviewer_model:str|None=None,auto_inbox_path:Path|None=None,reviewer_responder:Responder|None=None,strict_provider:bool=True,expected_pool_sha256:str="",prior_reviewer_raw_path:Path|None=None,prior_reviewer_raw_sha256:str="",now=None)->dict[str,Any]:
    """Resume only the independent semantic reviewer from archived Generator output.

    This path never invokes the Generator. It reconstructs machine-reviewable candidates from the
    archived raw Generator artifact, verifies the frozen Primary pool and raw SHA, then performs at
    most one reviewer call. Provider failure leaves candidates unreviewed with zero authority.
    """
    storage=storage or StorageSettings.from_env();reviewer_model=reviewer_model or os.getenv("PAPER_FIRST_PROBLEM_REVIEW_MODEL",REVIEWER_MODEL);current=(now or _now_dt()).astimezone(timezone.utc);run_id=current.strftime("%Y%m%dT%H%M%SZ")
    primary_pool_path=Path(primary_pool_path);generator_raw_path=Path(generator_raw_path);auto_inbox_path=Path(auto_inbox_path) if auto_inbox_path is not None else _root(storage)/"semantic-review-resume-inbox.json"
    pool=load_private_primary_pool(primary_pool_path) or {};reg=_registry(pool);psha=_pool_sha(pool) if pool else ""
    state={"schema_version":"1.0","generated_at":_now(),"run_id":run_id,"source_generator_run_id":str(source_generator_run_id or ""),"source_generator_raw_sha256":str(generator_raw_sha256 or ""),"generator_requested_model":str(generator_requested_model or ""),"generator_resolved_model":str(generator_resolved_model or ""),"reviewer_model":reviewer_model,"primary_pool_sha256":psha,"policy":{"reviewer_only_resume":True,"generator_calls_authorized":0,"one_semantic_reviewer_call_max":True,"strict_provider_transport":bool(strict_provider),"same_resolved_model_cannot_count_as_independent_review":True,"prior_reviewer_grounding_may_be_reverified":True,"prior_reviewer_verdict_reuse_forbidden":True,"exact_evidence_closure_blocks_redundant_review":True,"automatic_method_authority":False,"automatic_experiment_authority":False,"automatic_p0_authority":False,"automatic_gpu_authority":False},"summary":_empty_summary(len(reg)),"raw_artifacts":{},"candidates":[],"scientific_authority":False}
    def finish(status,cands=[]):
        state["status"]=status;_write_inbox(auto_inbox_path,source_generator_run_id or run_id,status,cands,psha);return state
    if pool.get("status")!="READY" or len(reg)<4:return finish("SKIPPED_INSUFFICIENT_PRIMARY_EVIDENCE")
    if expected_pool_sha256 and psha!=expected_pool_sha256:state["error"]="primary-pool-sha-mismatch";return finish("REVIEWER_RESUME_INPUT_INVALID")
    try: raw=generator_raw_path.read_text(encoding="utf-8")
    except OSError as e:state["error"]=f"generator-raw-read-error:{type(e).__name__}";return finish("REVIEWER_RESUME_INPUT_INVALID")
    actual_raw_sha=_sha(raw)
    if not generator_raw_sha256 or actual_raw_sha!=str(generator_raw_sha256):state["error"]="generator-raw-sha-mismatch";return finish("REVIEWER_RESUME_INPUT_INVALID")
    try:
        payload=extract_json_object(raw);rows=payload.get("candidates") or []
        if not isinstance(rows,list) or len(rows)>MAX_CANDIDATES or any(not isinstance(row,dict) for row in rows):raise ValueError("generator-candidate-array-invalid")
        normalized=[_normalize(row,reg) for row in rows];prior_grounding={}
        if prior_reviewer_raw_path is not None or prior_reviewer_raw_sha256:
            if prior_reviewer_raw_path is None or not prior_reviewer_raw_sha256:raise ValueError("prior-reviewer-grounding-provenance-incomplete")
            prior_grounding,grounding_audit=_load_prior_reviewer_grounding(raw_path=Path(prior_reviewer_raw_path),expected_raw_sha256=prior_reviewer_raw_sha256,candidates=normalized,registry=reg);state["prior_reviewer_grounding_audit"]=grounding_audit
        cands=_annotate_search_closure_reentry(normalized,prior_grounding);reviewable=[c for c in cands if _reviewable(c,reg)]
    except Exception as e:state["error"]=f"generator-raw-parse-error:{type(e).__name__}:{str(e)[:240]}";return finish("REVIEWER_RESUME_INPUT_INVALID")
    state["summary"].update({"generated":len(cands),"structurally_reviewable":len(reviewable),"generated_by_lane":_count_by_lane(cands),"structurally_reviewable_by_lane":_count_by_lane(reviewable)})
    if not reviewable:
        state["summary"].update({"semantic_clear":0,"semantic_blocked":len(cands),"written_to_auto_inbox":0,"semantic_clear_by_lane":_count_by_lane([]),"semantic_blocked_by_lane":_count_by_lane(cands)})
        state["candidates"]=[{"candidate_id":c["candidate_id"],"title":c["title"],"discovery_lane":c["discovery_lane"],"semantic_verdict":"BLOCK_PRE_REVIEW","search_closure_reentry_audit":c.get("search_closure_reentry_audit") or {}} for c in cands]
        return finish("SKIPPED_NO_STRUCTURALLY_REVIEWABLE_CANDIDATES")
    call=reviewer_responder or (lambda **kwargs:_ark(stage="semantic_review",allow_transport_fallback=not strict_provider,**kwargs))
    try:
        res=call(prompt=reviewer_prompt(reviewable,reg),model=reviewer_model,max_output_tokens=4200);review_raw=str(res.get("text") or "");path,sha=_write_raw(storage,run_id,"semantic-review-resume",reviewer_model,review_raw);resolved=str(res.get("resolved_model") or reviewer_model);transport_attempts=list(res.get("transport_attempts") or []);safe_attempts,receipt_audits=_archive_provider_receipts(storage,run_id,"semantic-review-resume",transport_attempts);orphan_audits=_archive_provider_orphans(storage,run_id,"semantic_review",transport_attempts);state["raw_artifacts"]["semantic_reviewer"]={"path":path,"sha256":sha,"requested_model":reviewer_model,"resolved_model":resolved,"transport_attempts":safe_attempts,"transport_fallback_used":bool(res.get("transport_fallback_used"))};
        if receipt_audits:state["raw_artifacts"]["semantic_reviewer"]["provider_receipt_audits"]=receipt_audits
        if orphan_audits:state["provider_orphan_audits"]=orphan_audits
        _apply_reviews(reviewable,extract_json_object(review_raw),reviewer_model,resolved,generator_resolved_model,sha,reg)
    except Exception as e:
        transport_attempts=list(getattr(e,"transport_attempts",[]) or []);safe_attempts,receipt_audits=_archive_provider_receipts(storage,run_id,"semantic-review-resume",transport_attempts);orphan_audits=_archive_provider_orphans(storage,run_id,"semantic_review",transport_attempts);state["error"]=f"{type(e).__name__}:{str(e)[:300]}";state["semantic_review_transport_attempts"]=safe_attempts
        if receipt_audits:state["provider_receipt_audits"]=receipt_audits
        if orphan_audits:state["provider_orphan_audits"]=orphan_audits
        _apply_reviews(reviewable,None,reviewer_model,"",generator_resolved_model,"",reg)
        state["summary"].update({"semantic_clear":0,"semantic_blocked":0,"semantic_review_unavailable":len(reviewable),"written_to_auto_inbox":0,"semantic_clear_by_lane":_count_by_lane([]),"semantic_blocked_by_lane":_count_by_lane([]),"semantic_review_unavailable_by_lane":_count_by_lane(reviewable)})
        state["candidates"]=[{"candidate_id":c["candidate_id"],"title":c["title"],"discovery_lane":c["discovery_lane"],"semantic_verdict":"UNREVIEWED"} for c in reviewable]
        return finish("REVIEWER_ERROR_ZERO_AUTHORITY")
    clear_rows=[c for c in reviewable if (c.get("semantic_reduction_review") or {}).get("verdict")=="CLEAR"];blocked_rows=[c for c in reviewable if c not in clear_rows]
    state["summary"].update({"semantic_clear":len(clear_rows),"semantic_blocked":len(blocked_rows),"written_to_auto_inbox":len(reviewable),"semantic_clear_by_lane":_count_by_lane(clear_rows),"semantic_blocked_by_lane":_count_by_lane(blocked_rows)})
    state["candidates"]=[{"candidate_id":c["candidate_id"],"title":c["title"],"discovery_lane":c["discovery_lane"],"source_refs":[c["empirical_evidence"]["source_a"]["ref"],c["empirical_evidence"]["source_b"]["ref"]],"semantic_verdict":(c.get("semantic_reduction_review") or {}).get("verdict"),"lane_contract_verified":(c.get("semantic_reduction_review") or {}).get("lane_contract_verified") is True,"matched_patterns":(c.get("semantic_reduction_review") or {}).get("matched_patterns") or []} for c in reviewable]
    return finish("GENERATED_AWAIT_PROBLEM_GATE",reviewable)


def recover_archived_portfolio_ingestion(*,storage:StorageSettings|None=None,primary_pool_path:Path,source_generator_state:dict[str,Any])->dict[str,Any]:
    """Re-run only formulation ingestion from one content-addressed canonical portfolio.

    Upstream expansion/evolution/repair membership is frozen to the archived private
    portfolio. Provider bytes are never regenerated. Bounded serialization recovery may
    expose reduction-limited pre-F0 rows, but any machine-reviewable recovered candidate
    fail-closes because an independent semantic reviewer would still be required.
    """
    storage=storage or StorageSettings.from_env();pool=load_private_primary_pool(Path(primary_pool_path)) or {};reg={str(row.get("ref") or ""):row for row in pool.get("records") or [] if isinstance(row,dict) and row.get("ref")}
    source=source_generator_state if isinstance(source_generator_state,dict) else {};policy=source.get("policy") or {};summary=source.get("summary") or {};run_id=str(source.get("run_id") or "").strip();receipt=(source.get("saturation_memory") or {}).get("current_review_receipt") or {}
    if source.get("status")!="GENERATED_ZERO_CANDIDATES" or policy.get("search_portfolio_enabled") is not True or not run_id:raise ValueError("portfolio-ingestion-replay-requires-canonical-zero-candidate-double-funnel")
    pool_sha=_pool_sha(pool)
    if pool.get("status")!="READY" or len(reg)<4 or str(receipt.get("pool_sha256") or "")!=pool_sha or str(receipt.get("discovery_operator_version") or "")!=DISCOVERY_OPERATOR_VERSION:raise ValueError("portfolio-ingestion-replay-primary-or-receipt-mismatch")
    generator_artifact=(source.get("raw_artifacts") or {}).get("generator") or {};portfolio_sha=str(generator_artifact.get("portfolio_sha256") or "").strip().lower();portfolio_path=_root(storage)/"search-portfolios"/f"{run_id}-portfolio.json"
    if not re.fullmatch(r"[0-9a-f]{64}",portfolio_sha) or not portfolio_path.is_file() or hashlib.sha256(portfolio_path.read_bytes()).hexdigest()!=portfolio_sha:raise ValueError("portfolio-ingestion-replay-private-portfolio-mismatch")
    portfolio=json.loads(portfolio_path.read_text(encoding="utf-8"));parents={str(row.get("seed_id") or ""):row for row in [*(portfolio.get("repaired") or []),*(portfolio.get("evolved") or []),*(portfolio.get("unique_seeds") or [])] if isinstance(row,dict) and row.get("seed_id")}
    provenance=[row for row in source.get("portfolio_provenance") or [] if isinstance(row,dict) and str(row.get("role") or "").startswith("formulate-")]
    provenance.sort(key=lambda row:int(str(row.get("role") or "formulate-999").rsplit("-",1)[-1]))
    raw_dir=_root(storage)/"raw-generations";recovered=[];recovery_audits=[]
    for prov in provenance:
        role=str(prov.get("role") or "");sha=str(prov.get("sha256") or "").strip().lower();model=str(prov.get("requested_model") or "")
        if not re.fullmatch(r"[0-9a-f]{64}",sha):raise ValueError("portfolio-ingestion-replay-formulation-sha-missing")
        matches=list(raw_dir.glob(f"{run_id}-{role}-{model}-{sha[:12]}.txt"))
        if len(matches)!=1 or hashlib.sha256(matches[0].read_bytes()).hexdigest()!=sha:raise ValueError(f"portfolio-ingestion-replay-raw-mismatch:{role}")
        payload,audit=recover_archived_formulation_payload(matches[0].read_text(encoding="utf-8",errors="replace"));audit={**audit,"role":role,"source_raw_sha256":sha,"requested_model":model,"resolved_model":str(prov.get("resolved_model") or ""),"request_fingerprint":str(prov.get("request_fingerprint") or ""),"scientific_authority":False};recovery_audits.append(audit)
        for item in payload.get("candidates") or []:
            if not isinstance(item,dict):continue
            parent=parents.get(str(item.get("source_branch_id") or ""))
            if not parent:raise ValueError(f"portfolio-ingestion-replay-parent-missing:{role}")
            row=dict(item);row["source_branch_id"]=parent["seed_id"];row["branch_depth"]=parent.get("branch_depth",0);row["discovery_lane"]=parent["discovery_lane"];row["empirical_evidence"]=parent["empirical_evidence"];row["lane_evidence"]=parent["lane_evidence"];row["paperability_axes"]=_normalize_paperability_axes(item.get("paperability_axes") or parent.get("paperability_axes"));row["paperability_survives"]=_paperability_survives(row["paperability_axes"]);row["reviewer_attack"]=parent.get("reviewer_attack") or "";row["reviewer_attack_class"]=parent.get("reviewer_attack_class") or "";row["repair_axis"]=parent.get("repair_axis") or "";row["why_attack_no_longer_applies"]=parent.get("why_attack_no_longer_applies") or "";recovered.append(row)
    for index,row in enumerate(recovered,1):row["candidate_id"]=f"PORT-{index:03d}"
    machine_reviewable=[];pre_f0=[];blocked=[]
    for raw_candidate in recovered:
        normalized=_normalize(raw_candidate,reg);audit=audit_problem_candidate(normalized,primary_evidence_by_ref=reg,require_primary_registry=True,require_semantic_review=False)
        if audit.get("passed"):machine_reviewable.append({"candidate_id":normalized.get("candidate_id"),"title":normalized.get("title"),"source_branch_id":normalized.get("source_branch_id")});continue
        route=_pre_f0_route(normalized,reg)
        if route.get("eligible"):pre_f0.append(_pre_f0_candidate_row(normalized,route));continue
        blocked.append({"candidate_id":normalized.get("candidate_id"),"title":normalized.get("title"),"source_branch_id":normalized.get("source_branch_id"),"blockers":audit.get("blockers") or [],"surviving_paperability_axes":route.get("surviving_axes") or []})
    if machine_reviewable:raise ValueError("portfolio-ingestion-replay-requires-semantic-review:"+",".join(str(row.get("candidate_id") or "") for row in machine_reviewable))
    if not pre_f0:raise ValueError("portfolio-ingestion-replay-recovers-no-pre-f0-candidates")
    new_run_id=_now_dt().strftime("%Y%m%dT%H%M%SZ")+"-ingestion-replay";recovery_material={"source_run_id":run_id,"source_portfolio_sha256":portfolio_sha,"pool_sha256":pool_sha,"recovery_audits":recovery_audits,"pre_f0_candidate_ids":[row["candidate_id"] for row in pre_f0]};recovery_sha=_sha(json.dumps(recovery_material,ensure_ascii=False,sort_keys=True,separators=(",",":")))
    state=json.loads(json.dumps(source,ensure_ascii=False));state.pop("discovery_transaction_id",None);state.pop("discovery_transaction_role",None);state["run_id"]=new_run_id;state["generated_at"]=_now();state["status"]="GENERATED_PRE_F0_EVIDENCE_ACQUISITION";state["candidates"]=[];state["pre_f0_candidates"]=pre_f0;state["policy"]["archived_portfolio_ingestion_replay_zero_provider"]=True;state["policy"]["formulation_serialization_recovery_is_bounded_complete_object_only"]=True
    state["summary"].update({"pre_f0_eligible":len(pre_f0),"generated":0,"structurally_reviewable":0,"semantic_clear":0,"semantic_blocked":0,"written_to_auto_inbox":0})
    sp=state.setdefault("search_portfolio",{}).setdefault("summary",{});sp.update({"recovered_formulated_candidates":len(recovered),"recovered_pre_f0_eligible":len(pre_f0),"recovered_machine_blocked":len(blocked),"recovery_provider_calls_executed":0})
    state["portfolio_ingestion_recovery"]={"source_generator_run_id":run_id,"source_transaction_id":str(source.get("discovery_transaction_id") or ""),"source_portfolio_sha256":portfolio_sha,"recovery_sha256":recovery_sha,"formulation_receipts":recovery_audits,"recovered_candidates":len(recovered),"pre_f0_eligible":len(pre_f0),"blocked_rows":blocked,"provider_calls_executed":0,"semantic_reviewer_calls_executed":0,"scientific_authority":False}
    source_raw_sha=str(generator_artifact.get("sha256") or "");state["raw_artifacts"]["generator"]={"sha256":recovery_sha,"requested_model":str(generator_artifact.get("requested_model") or ""),"resolved_model":str(generator_artifact.get("resolved_model") or ""),"portfolio":True,"portfolio_sha256":portfolio_sha,"calls":0,"provider_calls_executed":0,"archived_replay_subcalls":len(recovery_audits),"raw_replayed_without_provider":True,"raw_origin_run_id":run_id,"raw_origin_sha256":source_raw_sha}
    state.pop("semantic_reviewer_batches",None);state["raw_artifacts"].pop("semantic_reviewer",None)
    diagnostics=state.setdefault("search_diagnostics",{});last=dict(diagnostics.get("last_completed_lane_search") or {});last.update({"run_id":new_run_id,"generator_status":state["status"],"generated_at":state["generated_at"],"scientific_authority":False});diagnostics["last_completed_lane_search"]=_normalize_last_completed_lane_search_receipt(last)
    source_refs=sorted(reg);new_receipt={"run_id":new_run_id,"pool_sha256":pool_sha,"negative_space_sha256":str(receipt.get("negative_space_sha256") or ""),"discovery_operator_version":DISCOVERY_OPERATOR_VERSION,"source_refs":source_refs,"status":state["status"],"requested_model":str(generator_artifact.get("requested_model") or ""),"resolved_model":str(generator_artifact.get("resolved_model") or ""),"raw_sha256":recovery_sha,"scientific_authority":False};sat=state.setdefault("saturation_memory",{});sat["current_review_receipt"]=new_receipt;portable=[dict(row) for row in sat.get("portable_review_receipts") or [] if isinstance(row,dict)];portable=[row for row in portable if str(row.get("run_id") or "")!=new_run_id];portable.append(dict(new_receipt));sat["portable_review_receipts"]=portable[-PORTABLE_REVIEW_RECEIPT_LIMIT:];sat["portable_review_receipt_count"]=len(sat["portable_review_receipts"]);sat["current_run_recorded"]=True;sat["scientific_authority"]=False
    state["generation_notes"]=(f"Zero-provider archived formulation-ingestion replay recovered {len(recovered)} complete formulation candidates from the source double-funnel transaction; {len(pre_f0)} are reduction-limited Pre-F0 evidence-acquisition rows, {len(blocked)} remain machine-blocked, and no semantic-review-required candidate was silently downgraded. Exact same-information reduction remains mandatory before Problem Gate.")
    return state


def public_problem_generator_state(state:dict[str,Any],storage:StorageSettings|None=None)->dict[str,Any]:
    public=json.loads(json.dumps(state,ensure_ascii=False))
    for key in ("primary_pool_path","auto_inbox_path","archived_previous_auto_inbox","search_portfolio_private_path"):
        public.pop(key,None)
    for artifact in (public.get("raw_artifacts") or {}).values():
        if isinstance(artifact,dict):artifact.pop("path",None)
    return redact_private_paths(public,storage=storage or StorageSettings.from_env())


def write_archived_portfolio_ingestion_replay_state(json_path=DEFAULT_JSON,js_path=DEFAULT_JS,previous_public_state_path=None,*,storage:StorageSettings|None=None,primary_pool_path:Path,auto_inbox_path:Path|None=None):
    storage=storage or StorageSettings.from_env();previous_path=Path(previous_public_state_path) if previous_public_state_path is not None else Path(json_path);source=load_problem_generator_state(previous_path);state=recover_archived_portfolio_ingestion(storage=storage,primary_pool_path=Path(primary_pool_path),source_generator_state=source);pool=load_private_primary_pool(Path(primary_pool_path)) or {};psha=_pool_sha(pool);auto=Path(auto_inbox_path) if auto_inbox_path is not None else default_auto_inbox_path(storage);_write_inbox(auto,state["run_id"],state["status"],[],psha);public=public_problem_generator_state(state,storage=storage);Path(json_path).parent.mkdir(parents=True,exist_ok=True);Path(json_path).write_text(json.dumps(public,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");Path(js_path).write_text("window.PAPER_FIRST_PROBLEM_GENERATOR = "+json.dumps(public,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8");return state


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
        if not run_id or len(refs)<4 or status not in {"GENERATED_ZERO_CANDIDATES","GENERATED_AWAIT_PROBLEM_GATE","EXTERNAL_FRESH_INTAKE_REVIEWED"} or row.get("scientific_authority") is not False:
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
    if not run_id or not isinstance(raw_rows,list): return {}
    declared_statuses={str((row or {}).get("status") or "").strip().upper() for row in raw_rows if isinstance(row,dict)}
    expected_lanes=SEARCH_PORTFOLIO_PRIMITIVES if declared_statuses and declared_statuses.issubset({"EXPANDED","EMPTY"}) else DISCOVERY_LANES
    if set(priority)!=set(expected_lanes) or len(priority)!=len(expected_lanes) or len(raw_rows)!=len(expected_lanes): return {}
    rows=[]; statuses=set()
    for item in raw_rows:
        if not isinstance(item,dict): return {}
        lane=str(item.get("lane") or "").strip().upper(); status=str(item.get("status") or "").strip().upper(); reason=" ".join(str(item.get("reason") or "").split())[:500].rstrip()
        if lane not in expected_lanes or not reason: return {}
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
    mode="portfolio_expansion" if (source.get("policy") or {}).get("search_portfolio_enabled") is True else "anomaly_first_evidence_tuple_audit"
    return _normalize_last_completed_lane_search_receipt({"run_id":source.get("run_id"),"generator_status":source.get("status"),"generated_at":source.get("generated_at"),"mode":mode,"discovery_operator_version":str((source.get("policy") or {}).get("discovery_operator_version") or ""),"lane_search_priority":diagnostics.get("lane_search_priority"),"lane_search":diagnostics.get("lane_search"),"generation_notes":source.get("generation_notes"),"scientific_authority":False})


def _merge_last_completed_lane_search(state:dict[str,Any],previous:dict[str,Any],seed:dict[str,Any]|None=None)->dict[str,Any]:
    diagnostics=state.setdefault("search_diagnostics",{}); previous_diagnostics=previous.get("search_diagnostics") or {}
    candidates=[_normalize_last_completed_lane_search_receipt(previous_diagnostics.get("last_completed_lane_search")),_completed_lane_search_receipt_from_state(previous),_normalize_last_completed_lane_search_receipt(seed),_completed_lane_search_receipt_from_state(state)]
    chosen={}
    for candidate in candidates:
        if candidate: chosen=candidate
    diagnostics["last_completed_lane_search"]=chosen; diagnostics["scientific_authority"]=False
    return state


def replay_problem_generator_raw(
    *,
    storage: StorageSettings | None = None,
    primary_pool_path: Path,
    generator_raw_path: Path,
    generator_raw_sha256: str,
    generator_requested_model: str,
    generator_resolved_model: str,
    source_generator_run_id: str,
    source_discovery_operator_version: str,
    auto_inbox_path: Path | None = None,
    saturation_ledger_path: Path | None = None,
    blocked_problem_memory: dict[str, Any] | None = None,
    prior_reviewer_raw_path: Path | None = None,
    prior_reviewer_raw_sha256: str = "",
    now=None,
    max_candidates: int = MAX_CANDIDATES,
) -> dict[str, Any]:
    """Recompile archived Generator raw under the current pool/operator with zero provider calls.

    This is valid only when the archived assistant output is already complete and content-addressed.
    It re-runs all deterministic source/lane/dead-end/reduction checks. Any candidate that would
    require a current semantic reviewer causes a fail-closed replay status rather than a provider call.
    """
    storage = storage or StorageSettings.from_env()
    primary_pool_path = Path(primary_pool_path); generator_raw_path = Path(generator_raw_path)
    auto_inbox_path = Path(auto_inbox_path) if auto_inbox_path is not None else default_auto_inbox_path(storage)
    current = (now or _now_dt()).astimezone(timezone.utc); run_id = current.strftime("%Y%m%dT%H%M%SZ") + "-replay"
    pool = load_private_primary_pool(primary_pool_path) or {}; reg = _registry(pool); psha = _pool_sha(pool) if pool else ""
    blocked_problem_memory = blocked_problem_memory or _public_blocked_problem_memory(storage)
    dead_end_prompt_memory = _private_dead_end_prompt_memory(storage, blocked_problem_memory, current_refs=set(reg))
    inherited_receipts=[dict(row) for row in ((pool.get("source_coverage") or {}).get("portable_review_receipts") or []) if isinstance(row,dict)]
    policy = _base_policy(portfolio=False)
    policy.update({
        "generator_replayed_without_provider": True,
        "generator_replay_requires_exact_raw_sha256": True,
        "generator_replay_rechecks_current_machine_contract": True,
        "generator_replay_cannot_invoke_semantic_reviewer": True,
        "prior_reviewer_grounding_may_be_reverified": True,
        "prior_reviewer_verdict_reuse_forbidden": True,
        "exact_evidence_closure_blocks_redundant_review": True,
        "automatic_provider_calls_authorized": 0,
    })
    state={
        "schema_version":"2.5","generated_at":_now(),"run_id":run_id,"primary_pool_path":str(primary_pool_path),
        "auto_inbox_path":str(auto_inbox_path),"generator_model":str(generator_requested_model or ""),"reviewer_model":"",
        "policy":policy,"summary":_empty_summary(len(reg)),"raw_artifacts":{},"generation_notes":"",
        "search_diagnostics":{"lane_search_priority":list(dead_end_prompt_memory.get("lane_search_priority") or DISCOVERY_LANES),"lane_search_complete":False,"lane_search":[],"last_completed_lane_search":{},"scientific_authority":False},
        "saturation_memory":{"ledger_entries":len(_load_saturation_ledger(storage,saturation_ledger_path)),"prior_identical_zero_runs":0,"current_run_recorded":False,"portable_review_receipts":inherited_receipts[-PORTABLE_REVIEW_RECEIPT_LIMIT:],"blocked_problem_memory":blocked_problem_memory,"scientific_authority":False},
        "source_generator_run_id":str(source_generator_run_id or ""),"source_discovery_operator_version":str(source_discovery_operator_version or ""),
        "provider_calls_executed":0,"semantic_reviewer_calls_executed":0,"candidates":[],
    }
    def finish(status:str,cands:list[dict[str,Any]]|None=None):
        cands=cands or []; state["status"]=status; _write_inbox(auto_inbox_path,run_id,status,cands,psha); _record_saturation_run(storage,state,psha,reg,saturation_ledger_path); return state
    if pool.get("status")!="READY" or len(reg)<4:return finish("REPLAY_INSUFFICIENT_PRIMARY_EVIDENCE")
    try: raw=generator_raw_path.read_text(encoding="utf-8")
    except OSError as error: state["error"]=f"raw-read-error:{type(error).__name__}";return finish("REPLAY_INPUT_INVALID")
    actual_sha=_sha(raw)
    if not re.fullmatch(r"[0-9a-f]{64}",str(generator_raw_sha256 or "")) or actual_sha!=str(generator_raw_sha256):state["error"]="raw-sha-mismatch";return finish("REPLAY_INPUT_INVALID")
    try:
        payload=extract_json_object(raw); rows=payload.get("candidates") or []
        if not isinstance(rows,list) or len(rows)>max_candidates or any(not isinstance(row,dict) for row in rows):raise ValueError("generator-candidate-array-invalid")
        state["generation_notes"]=str(payload.get("generation_notes") or "")[:2400].strip()
        lane_search=_normalize_lane_search(payload.get("lane_search"),reg,state["search_diagnostics"]["lane_search_priority"])
        normalized=[_normalize(row,reg) for row in rows];prior_grounding={}
        if prior_reviewer_raw_path is not None or prior_reviewer_raw_sha256:
            if prior_reviewer_raw_path is None or not prior_reviewer_raw_sha256:raise ValueError("prior-reviewer-grounding-provenance-incomplete")
            prior_grounding,grounding_audit=_load_prior_reviewer_grounding(raw_path=Path(prior_reviewer_raw_path),expected_raw_sha256=prior_reviewer_raw_sha256,candidates=normalized,registry=reg);state["prior_reviewer_grounding_audit"]=grounding_audit
        cands=_annotate_search_closure_reentry(normalized,prior_grounding);_validate_lane_search_candidates(lane_search,cands)
    except Exception as error:
        state["error"]=f"raw-recompile-error:{type(error).__name__}:{str(error)[:300]}";return finish("REPLAY_INPUT_INVALID")
    reviewable=[candidate for candidate in cands if _reviewable(candidate,reg)]
    state["search_diagnostics"].update({"lane_search_complete":True,"lane_search":lane_search})
    state["summary"].update({"generated":len(cands),"structurally_reviewable":len(reviewable),"generated_by_lane":_count_by_lane(cands),"structurally_reviewable_by_lane":_count_by_lane(reviewable)})
    archived_path,archived_sha=_write_raw(storage,run_id,"generator-replay",str(generator_requested_model or "unknown"),raw)
    state["raw_artifacts"]["generator"]={"path":archived_path,"sha256":archived_sha,"requested_model":str(generator_requested_model or ""),"resolved_model":str(generator_resolved_model or generator_requested_model or ""),"raw_replayed_without_provider":True,"raw_origin_path":str(generator_raw_path),"raw_origin_run_id":str(source_generator_run_id or ""),"raw_origin_discovery_operator_version":str(source_discovery_operator_version or ""),"provider_calls_executed":0}
    if reviewable:
        blocked_before_review=[candidate for candidate in cands if candidate not in reviewable];reviewable_ids={id(candidate) for candidate in reviewable}
        state["summary"].update({"semantic_clear":0,"semantic_blocked":len(blocked_before_review),"semantic_review_unavailable":len(reviewable),"written_to_auto_inbox":0,"semantic_clear_by_lane":_count_by_lane([]),"semantic_blocked_by_lane":_count_by_lane(blocked_before_review),"semantic_review_unavailable_by_lane":_count_by_lane(reviewable)})
        state["candidates"]=[{"candidate_id":c["candidate_id"],"title":c["title"],"discovery_lane":c["discovery_lane"],"semantic_verdict":"UNREVIEWED_REPLAY_REQUIRES_REVIEWER" if id(c) in reviewable_ids else "BLOCK_PRE_REVIEW_REPLAY","lane_contract_verified":False,"matched_patterns":[],"search_closure_reentry_audit":c.get("search_closure_reentry_audit") or {}} for c in cands]
        return finish("REPLAY_REQUIRES_SEMANTIC_REVIEW",[])
    for candidate in cands:
        candidate["semantic_reduction_review"].update({"reviewed":False,"verdict":"BLOCK","lane_contract_verified":False,"lane_contract_reason":"current-machine-contract-blocked-before-review","strongest_reduction":"current-machine-contract-blocked-before-review"})
    state["summary"].update({"semantic_clear":0,"semantic_blocked":len(cands),"written_to_auto_inbox":len(cands),"semantic_clear_by_lane":_count_by_lane([]),"semantic_blocked_by_lane":_count_by_lane(cands)})
    state["candidates"]=[{"candidate_id":c["candidate_id"],"title":c["title"],"discovery_lane":c["discovery_lane"],"source_refs":[c["empirical_evidence"]["source_a"]["ref"],c["empirical_evidence"]["source_b"]["ref"]],"semantic_verdict":"BLOCK_PRE_REVIEW_REPLAY","lane_contract_verified":False,"matched_patterns":[],"search_closure_reentry_audit":c.get("search_closure_reentry_audit") or {}} for c in cands]
    return finish("GENERATED_ZERO_CANDIDATES" if not cands else "GENERATED_AWAIT_PROBLEM_GATE",cands)


def write_replayed_problem_generator_state(json_path=DEFAULT_JSON,js_path=DEFAULT_JS,previous_public_state_path=None,last_completed_lane_search_seed=None,**kwargs):
    previous_path=Path(previous_public_state_path) if previous_public_state_path is not None else json_path
    previous=load_problem_generator_state(previous_path);storage=kwargs.get("storage") or StorageSettings.from_env();blocked_problem_memory=_public_blocked_problem_memory(storage,previous_path)
    state=replay_problem_generator_raw(**kwargs,blocked_problem_memory=blocked_problem_memory)
    _merge_portable_review_receipts(state,previous);_merge_last_completed_lane_search(state,previous,last_completed_lane_search_seed)
    public=public_problem_generator_state(state,storage=storage);json_path.parent.mkdir(parents=True,exist_ok=True);json_path.write_text(json.dumps(public,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");js_path.write_text("window.PAPER_FIRST_PROBLEM_GENERATOR = "+json.dumps(public,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8");return state


def write_problem_generator_state(json_path=DEFAULT_JSON,js_path=DEFAULT_JS,previous_public_state_path=None,last_completed_lane_search_seed=None,**kwargs):
    # Keep this low-level writer legacy-safe: canonical scheduling opts into the
    # double funnel explicitly. This prevents receipt replay/repair utilities from
    # silently expanding one historical call into a provider-call portfolio.
    previous_path=Path(previous_public_state_path) if previous_public_state_path is not None else json_path
    previous=load_problem_generator_state(previous_path)
    storage=kwargs.get("storage") or StorageSettings.from_env()
    blocked_problem_memory=_public_blocked_problem_memory(storage,previous_path)
    state=run_problem_generator(**kwargs,blocked_problem_memory=blocked_problem_memory)
    _merge_portable_review_receipts(state,previous)
    _merge_last_completed_lane_search(state,previous,last_completed_lane_search_seed)
    public=public_problem_generator_state(state,storage=kwargs.get("storage"));json_path.parent.mkdir(parents=True,exist_ok=True);json_path.write_text(json.dumps(public,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");js_path.write_text("window.PAPER_FIRST_PROBLEM_GENERATOR = "+json.dumps(public,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8");return state

if __name__=="__main__":print(json.dumps(write_problem_generator_state(),ensure_ascii=False))
