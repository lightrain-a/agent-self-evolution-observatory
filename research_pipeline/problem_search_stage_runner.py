from __future__ import annotations

import argparse,hashlib,json,os,re
from datetime import datetime,timezone
from pathlib import Path

from .ark_provider import extract_json_object
from .config import PROJECT_ROOT
from .dead_end_failure_layers import normalize_closed_row
from .paper_first_problem_discovery_contract import SEARCH_PORTFOLIO_PRIMITIVES, audit_problem_candidate, audit_shadow_problem_candidate
from .paper_first_problem_generator import _ark,_apply_reviews,_normalize
from .paper_first_problem_generator_prompts import reviewer_prompt
from .premium_model_policy import PREMIUM_AUTO, preferred_model
from .paper_first_problem_falsifier_preflight import write_problem_falsifier_preflight,write_support_inventory_request
from .paper_first_evidence_acquisition import (
    PLAN_FILENAME as EVIDENCE_PLAN_FILENAME,
    adjudicate_evidence_receipts,
    build_provisional_evidence_plan,
    build_substrate_preflight_request,
    compile_evidence_designs,
    compile_evidence_reviews,
    compile_operationalization_recompiles,
    compile_substrate_preflight,
    compile_harness_implementation_receipts,
    evidence_design_prompt,
    evidence_review_prompt,
    operationalization_recompile_prompt,
)
from .problem_search_control_snapshot import STAGE_RUNNER_ARTIFACT_SCHEMA,validate_shadow_run_control
from .paper_first_primary_evidence import parse_arxiv_page,extract_empirical_fact_candidates,extract_typed_evidence_candidates
from .paper_first_problem_search_portfolio import (
    _archives,_assign_structural_clusters,_evolution_prompt,_expansion_prompt,_formulation_prompt,
    _fresh_evidence_sha,_fresh_phenomenon_priors,_fresh_phenomenon_target,_inversion_asset_records,_positive_residual_asset_records,_search_asset_records,_maxmin_select,_normalize_seed,_score,_semantic_dedup,_source_refs,_valid_seed,
)


DEFAULT_SHADOW_SEARCH_MEMORY_PATH=PROJECT_ROOT/"generated"/"paper-first-search-portfolio-design-adjudication.json"
DEFAULT_SHADOW_DEAD_END_MEMORY_PATH=DEFAULT_SHADOW_SEARCH_MEMORY_PATH  # legacy import alias


def _resolve_run_pool(run_root:Path,pool_path:Path|None=None)->Path|None:
    if pool_path is not None:return pool_path
    local=run_root/"frozen-primary-evidence-pool.json"
    return local if local.exists() else None


def _resolve_run_memory(run_root:Path,memory_path:Path|None=None)->Path|None:
    if memory_path is not None:return memory_path
    local=run_root/"shadow-search-memory.json"
    if local.exists():return local
    legacy=run_root/"shadow-dead-end-memory.json"
    return legacy if legacy.exists() else None


def _require_resolved_pool(run_root:Path,pool_path:Path|None=None)->Path:
    resolved=_resolve_run_pool(run_root,pool_path)
    if resolved is None:raise ValueError("shadow stage requires --pool or run-local frozen-primary-evidence-pool.json")
    return resolved


def _assert_run_control(run_root:Path,pool_path:Path|None=None,memory_path:Path|None=None)->str:
    resolved_pool=_resolve_run_pool(run_root,pool_path)
    resolved_memory=_resolve_run_memory(run_root,memory_path)
    receipt=validate_shadow_run_control(run_root=run_root,pool_path=resolved_pool,memory_path=resolved_memory)
    return str(receipt.get("control_snapshot_sha256") or "")


def _require_artifact_control(payload:dict,control_sha:str,path:Path,expected_schema:str|None=None)->None:
    if not control_sha:return
    if str(payload.get("control_snapshot_sha256") or "")!=control_sha:
        raise ValueError(f"mixed shadow control snapshot artifact: {path.name}")
    if expected_schema is not None and str(payload.get("schema_version") or "")!=expected_schema:
        raise ValueError(f"shadow artifact schema drift: {path.name} expected={expected_schema} actual={payload.get('schema_version')}")

def _review_generator_receipts(run_root:Path,selected:list[dict],control_sha:str)->tuple[list[dict],str]:
    """Resolve the actual model identities that generated this review batch.

    Machine-audit rows retain the formulation artifact that produced each candidate.
    Independence must be checked against those provider receipts, never against a
    requested alias or a hard-coded historical generator name.
    """
    receipts=[]
    seen=set()
    for row in selected:
        name=str(row.get("source_artifact") or "").strip()
        if not name or Path(name).name!=name or not name.startswith("formulate-p") or not name.endswith(".json"):
            raise ValueError("semantic review requires a valid formulation source artifact")
        if name in seen:continue
        seen.add(name)
        path=run_root/name
        if not path.is_file():raise ValueError(f"semantic review missing generator receipt artifact: {name}")
        payload=json.loads(path.read_text(encoding="utf-8"));_require_artifact_control(payload,control_sha,path,STAGE_RUNNER_ARTIFACT_SCHEMA)
        requested=str(payload.get("requested_model") or "").strip();resolved=str(payload.get("resolved_model") or "").strip();raw_sha=str(payload.get("raw_sha256") or "").strip()
        if not resolved or not re.fullmatch(r"[0-9a-f]{64}",raw_sha):
            raise ValueError(f"semantic review generator receipt incomplete: {name}")
        receipts.append({"source_artifact":name,"requested_model":requested,"resolved_model":resolved,"raw_sha256":raw_sha})
    resolved_models=sorted({row["resolved_model"] for row in receipts})
    if not resolved_models:raise ValueError("semantic review requires generator resolved-model receipts")
    return receipts,"|".join(resolved_models)


def _archive_raw_before_parse(run_root:Path,stem:str,raw:str,resolved_model:str)->tuple[str,Path]:
    sha=hashlib.sha256(raw.encode()).hexdigest();raw_root=run_root/"raw";raw_root.mkdir(parents=True,exist_ok=True);path=raw_root/f"{stem}-{sha[:12]}.txt";path.write_text(raw,encoding="utf-8");return sha,path


def _repair_truncated_optional_notes(raw:str,scientific_fields:tuple[str,...])->tuple[dict|None,str,int]:
    """Recover only fully closed scientific arrays followed by truncated optional notes.

    Bytes inside the named scientific arrays are never edited. We discard only an
    incomplete top-level `notes` suffix and close the already-complete root object.
    Any truncation inside a scientific array remains a hard parse failure.
    """
    text=str(raw or "").strip()
    if text.startswith("```"):
        lines=text.splitlines()
        if lines and lines[0].startswith("```"):text="\n".join(lines[1:])
    marker='\n  "notes":'
    split=text.rfind(marker)
    if split<0:return None,"",0
    suffix=text[split:]
    prefix=text[:split].rstrip()
    if not prefix.endswith(','):return None,"",0
    repaired=prefix[:-1].rstrip()+"\n}"
    try:payload=json.loads(repaired)
    except Exception:return None,"",0
    if not isinstance(payload,dict):return None,"",0
    if any(not isinstance(payload.get(field),list) for field in scientific_fields):return None,"",0
    if set(payload)-set(scientific_fields):return None,"",0
    return payload,repaired,len(suffix)


def _repair_truncated_formulation_notes(raw:str)->tuple[dict|None,str,int]:
    return _repair_truncated_optional_notes(raw,("candidates","rejected"))


def _repair_truncated_expansion_notes(raw:str)->tuple[dict|None,str,int]:
    return _repair_truncated_optional_notes(raw,("seeds",))


def _parse_archived_json(run_root:Path,stem:str,raw:str,resolved_model:str)->tuple[dict,str]:
    sha,_=_archive_raw_before_parse(run_root,stem,raw,resolved_model)
    try:return extract_json_object(raw),sha
    except Exception as error:
        repair=None;scientific_fields=[]
        if stem.startswith("formulate-"):
            repair=_repair_truncated_formulation_notes(raw);scientific_fields=["candidates","rejected"]
        elif stem.startswith("expand-"):
            repair=_repair_truncated_expansion_notes(raw);scientific_fields=["seeds"]
        if repair is not None:
            payload,repaired,discarded=repair
            if payload is not None:
                repaired_sha=hashlib.sha256(repaired.encode()).hexdigest();receipt={"schema_version":"1.0","stage":stem,"status":"PARSE_REPAIRED_TRAILING_METADATA_ONLY_ZERO_AUTHORITY","resolved_model":resolved_model,"raw_sha256":sha,"repaired_sha256":repaired_sha,"repair_type":"TRUNCATED_OPTIONAL_TRAILING_NOTES","discarded_field":"notes","discarded_suffix_chars":discarded,"scientific_fields_preserved":scientific_fields,"scientific_array_bytes_mutated":False,"string_content_mutation_allowed":False,"scientific_authority":False,"authority":{"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False}}
                (run_root/f"repair-{stem}-{sha[:12]}.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");return payload,sha
        err={"schema_version":"1.0","stage":stem,"status":"PARSE_ERROR_ZERO_AUTHORITY","resolved_model":resolved_model,"raw_sha256":sha,"error":f"{type(error).__name__}:{str(error)[:1200]}","scientific_authority":False}
        (run_root/f"error-{stem}-{sha[:12]}.json").write_text(json.dumps(err,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");raise


def _repair_array_delimiter_colons(raw:str)->tuple[str,int]:
    """Repair only impossible top-level ':' delimiters inside JSON arrays.

    String bytes are never changed. A colon is replaced only when the current
    JSON container is an array; valid JSON cannot use ':' there as a delimiter.
    """
    chars=list(raw);stack=[];in_string=False;escaped=False;repairs=0
    for i,ch in enumerate(chars):
        if in_string:
            if escaped:escaped=False
            elif ch=='\\':escaped=True
            elif ch=='"':in_string=False
            continue
        if ch=='"':in_string=True;continue
        if ch in '[{':stack.append(ch);continue
        if ch in ']}':
            if stack:stack.pop()
            continue
        if ch==':' and stack and stack[-1]=='[':
            chars[i]=',';repairs+=1
    return ''.join(chars),repairs


def _parse_archived_evidence_design_json(run_root:Path,stem:str,raw:str,resolved_model:str)->tuple[dict,str]:
    sha,_=_archive_raw_before_parse(run_root,stem,raw,resolved_model)
    try:return extract_json_object(raw),sha
    except Exception as first_error:
        repaired,count=_repair_array_delimiter_colons(raw)
        if not (1<=count<=2):
            err={"schema_version":"1.0","stage":stem,"status":"PARSE_ERROR_ZERO_AUTHORITY","resolved_model":resolved_model,"raw_sha256":sha,"parse_repair_attempted":False,"array_colon_candidates":count,"error":f"{type(first_error).__name__}:{str(first_error)[:1200]}","scientific_authority":False}
            (run_root/f"error-{stem}-{sha[:12]}.json").write_text(json.dumps(err,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");raise
        try:payload=extract_json_object(repaired)
        except Exception as repair_error:
            err={"schema_version":"1.0","stage":stem,"status":"PARSE_REPAIR_FAILED_ZERO_AUTHORITY","resolved_model":resolved_model,"raw_sha256":sha,"repair_type":"ARRAY_CONTAINER_COLON_TO_COMMA","repair_count":count,"error":f"{type(repair_error).__name__}:{str(repair_error)[:1200]}","scientific_authority":False}
            (run_root/f"error-{stem}-{sha[:12]}.json").write_text(json.dumps(err,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");raise
        repaired_sha=hashlib.sha256(repaired.encode()).hexdigest();receipt={"schema_version":"1.0","stage":stem,"status":"PARSE_REPAIRED_PUNCTUATION_ONLY_ZERO_AUTHORITY","resolved_model":resolved_model,"raw_sha256":sha,"repaired_sha256":repaired_sha,"repair_type":"ARRAY_CONTAINER_COLON_TO_COMMA","repair_count":count,"string_content_mutation_allowed":False,"scientific_authority":False,"authority":{"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False}}
        (run_root/f"repair-{stem}-{sha[:12]}.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");return payload,sha


def _ark_with_provider_receipt(*,run_root:Path,stem:str,requested_model:str,context:dict|None=None,**kwargs)->dict:
    try:
        return _ark(model=requested_model,**kwargs)
    except Exception as error:
        message=f"{type(error).__name__}:{str(error)[:1600]}";fingerprint=hashlib.sha256(json.dumps({"stage":stem,"requested_model":requested_model,"error":message},sort_keys=True,separators=(",",":")).encode()).hexdigest()
        timeout=any(token in message.lower() for token in ("timeout","timed out","read timed out"))
        payload={"schema_version":"1.0","generated_at":datetime.now(timezone.utc).replace(microsecond=0).isoformat(),"stage":stem,"status":"PROVIDER_TIMEOUT_ZERO_AUTHORITY" if timeout else "PROVIDER_ERROR_ZERO_AUTHORITY","requested_model":requested_model,"complete_response_received":False,"raw_sha256":"","error_fingerprint":fingerprint,"error":message,"scientific_authority":False,"authority":{"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False}}
        if isinstance(context,dict):payload.update({k:v for k,v in context.items() if k in {"lane","part","generation","branch_ids","candidate_ids","requested","requested_children","control_snapshot_sha256"}})
        run_root.mkdir(parents=True,exist_ok=True);(run_root/f"error-{stem}-provider-{fingerprint[:12]}.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        raise

def _provider_success_metadata(*,run_root:Path,stem:str,response:dict)->dict:
    """Persist provider transport provenance without exposing provider response IDs.

    `_ark` may issue one fallback model request after a no-output transport failure, and
    `ArkResponsesClient` may issue one compatibility POST when disabled thinking is rejected.
    Successful stage artifacts must count those POSTs rather than silently collapsing them into
    one logical model call. Provider response IDs remain run-local recovery material; public-safe
    artifacts keep only content-addressed receipt audits.
    """
    attempts=[];receipt_dir=run_root/"provider-receipts"
    for raw in response.get("transport_attempts") or []:
        if not isinstance(raw,dict):continue
        row=dict(raw);receipt=row.pop("provider_receipt",None)
        if isinstance(receipt,dict) and str(receipt.get("response_id") or "").strip():
            text=json.dumps(receipt,ensure_ascii=False,sort_keys=True,separators=(",",":"));sha=hashlib.sha256(text.encode()).hexdigest()
            receipt_dir.mkdir(parents=True,exist_ok=True);path=receipt_dir/f"{stem}-{sha[:12]}.json"
            if not path.exists():
                path.write_text(json.dumps({"schema_version":"1.0","stage":stem,"provider_receipt":receipt,"provider_receipt_sha256":sha,"scientific_authority":False},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            row["provider_receipt_audit"]={"provider_receipt_sha256":sha,"status":str(receipt.get("status") or ""),"requested_model":str(receipt.get("requested_model") or row.get("requested_model") or ""),"resolved_model":str(receipt.get("resolved_model") or ""),"incomplete_reason":str(receipt.get("incomplete_reason") or ""),"scientific_authority":False}
        attempts.append(row)
    compatibility=response.get("thinking_compatibility_fallback") is True
    # A successful `_ark` response always represents at least one provider POST. Each top-level
    # transport attempt is one POST; a successful thinking-compatibility fallback adds one more.
    calls=max(1,len(attempts))+int(compatibility)
    return {"provider_calls_executed":calls,"transport_fallback_used":response.get("transport_fallback_used") is True,"transport_attempts":attempts,"thinking_compatibility_fallback":compatibility}


def _shadow_search_memory(path:Path|None)->dict:
    """Load search-control memory and normalize legacy snapshots at the boundary.

    Canonical search memory is ``shadow_search_memory.closed_objects`` and every
    deduplication row must carry ``search_closure_certified=true``. Historical
    ``blocked_objects/dead_end_certified`` snapshots are accepted only here, then
    translated into the canonical search-closure representation before use.
    """
    resolved=path or DEFAULT_SHADOW_SEARCH_MEMORY_PATH
    if not resolved.exists():return {}
    payload=json.loads(resolved.read_text(encoding="utf-8"))
    canonical_container=bool(isinstance(payload,dict) and isinstance(payload.get("shadow_search_memory"),dict))
    memory=(payload.get("shadow_search_memory") or payload.get("shadow_dead_end_memory")) if isinstance(payload,dict) else None
    if not isinstance(memory,dict):memory=payload if isinstance(payload,dict) else {}
    canonical_container=canonical_container or ("closed_objects" in memory and "blocked_objects" not in memory)
    if memory.get("scientific_authority") is not False or memory.get("live_source_coverage_effect") is not False or memory.get("cannot_mutate_canonical_generator_or_queue") is not True:
        raise ValueError("shadow search-control memory must be zero-authority and unable to mutate canonical discovery")

    closed=[];holds=[]
    if canonical_container:
        raw_closed=memory.get("closed_objects") or []
        raw_holds=memory.get("hold_objects") or []
        if not isinstance(raw_closed,list) or any(not isinstance(row,dict) for row in raw_closed):
            raise ValueError("canonical shadow_search_memory.closed_objects must be a list of objects")
        if any(row.get("search_closure_certified") is not True for row in raw_closed):
            raise ValueError("canonical closed_objects rows must set search_closure_certified=true")
        for source in raw_closed:
            row=normalize_closed_row(dict(source));row["search_closure_certified"]=True;row["dead_end_certified"]=bool(row.get("failure_layer")=="core_principle" and row.get("principle_update_allowed") is True);closed.append(row)
        for source in raw_holds:
            if not isinstance(source,dict):continue
            row=dict(source);row["dead_end_certified"]=False;row.setdefault("memory_class","REOPENABLE_HOLD");holds.append(row)
    else:
        # Explicit legacy migration only: old snapshots used blocked_objects and
        # overloaded dead_end_certified for both search control and science.
        all_rows=[dict(row) for row in list(memory.get("closed_objects") or memory.get("blocked_objects") or [])+list(memory.get("hold_objects") or []) if isinstance(row,dict)]
        for row in all_rows:
            basin=str(row.get("basin") or "");disposition=str(row.get("disposition") or "")
            certified=row.get("search_closure_certified") is True or row.get("dead_end_certified") is True or basin.startswith("current-source-hard-veto-") or disposition in {"STOP_CURRENT_PRIMARY_COLLISION","STOP_MATURE_THEORY_REDUCTION"}
            if certified:
                row=normalize_closed_row(row);row["search_closure_certified"]=True;row["dead_end_certified"]=bool(row.get("failure_layer")=="core_principle" and row.get("principle_update_allowed") is True);closed.append(row)
            else:
                row["dead_end_certified"]=False;row.setdefault("memory_class","REOPENABLE_HOLD");holds.append(row)
    memory=dict(memory);memory["closed_objects"]=closed;memory["hold_objects"]=holds
    if canonical_container:memory.pop("blocked_objects",None)
    else:memory["blocked_objects"]=closed  # legacy compatibility only; never used for canonical deduplication
    return memory


# Legacy function alias for archived callers/tests. New code must use search-memory semantics.
_shadow_dead_end_memory=_shadow_search_memory


def _text_tokens(value:str)->set[str]:
    return {token for token in re.findall(r"[a-z0-9]+",str(value or "").lower()) if len(token)>=3}


def _text_jaccard(left:str,right:str)->float:
    a,b=_text_tokens(left),_text_tokens(right)
    return len(a&b)/len(a|b) if a and b else 0.0


def _fresh_target_seed_match(seed:dict,target:dict)->bool:
    """Require Seed 1 to address the assigned evidence-level phenomenon, not just its paper."""
    ref=str(target.get("ref") or "").strip();target_text=str(target.get("phenomenon_text") or "").strip()
    if not ref or ref not in _source_refs(seed) or not target_text:return False
    evidence=seed.get("empirical_evidence") or {};lane=seed.get("lane_evidence") or {}
    candidate_text=" ".join([
        str(seed.get("title") or ""),str(seed.get("problem_seed") or ""),str(seed.get("scientific_tension") or ""),str(seed.get("agent_specific_constraint") or ""),
        str((evidence.get("source_a") or {}).get("claim") or ""),str((evidence.get("source_b") or {}).get("claim") or ""),
        " ".join(str(value or "") for value in lane.values()),
    ])
    target_tokens=_text_tokens(target_text);candidate_tokens=_text_tokens(candidate_text);overlap=len(target_tokens&candidate_tokens)
    # Primary claims often paraphrase the boundary, so avoid brittle exact-string
    # matching while still rejecting a different anomaly from the same paper.
    return overlap>=3 and (overlap/max(1,min(len(target_tokens),12))>=0.25 or _text_jaccard(target_text,candidate_text)>=0.10)


def _iter_search_closures(memory:dict)->list[dict]:
    """Read canonical search closures with legacy blocked_objects fallback."""
    canonical=isinstance((memory or {}).get("closed_objects"),list)
    rows=(memory or {}).get("closed_objects") if canonical else ((memory or {}).get("blocked_objects") or [])
    return [
        row for row in (rows or [])
        if isinstance(row,dict)
        and (row.get("search_closure_certified") is True or (not canonical and row.get("dead_end_certified") is True))
    ]


def _search_closure_seed_blocker(seed:dict,memory:dict,pool_sha:str,registry:dict|None=None)->dict|None:
    lane=str(seed.get("discovery_lane") or "").strip().upper()
    evidence=seed.get("empirical_evidence") or {}
    refs=sorted({str((evidence.get(key) or {}).get("ref") or "").strip() for key in ("source_a","source_b") if str((evidence.get(key) or {}).get("ref") or "").strip()})
    claims=" ".join(str((evidence.get(key) or {}).get("claim") or "") for key in ("source_a","source_b"))
    problem=" ".join(str(seed.get(key) or "") for key in ("title","problem_seed","scientific_tension","structural_signature","irreducible_object","exact_prediction"))
    for row in _iter_search_closures(memory):
        basin=str(row.get("basin") or "")
        row_lane=str(row.get("search_primitive") or "").strip().upper()
        memory_refs=sorted({str(ref) for ref in row.get("current_source_refs") or [] if str(ref)})
        if basin.startswith(("semantic-exact-reduction-","semantic-lane-contract-")):
            if str(row.get("frozen_pool_sha256") or "")!=str(pool_sha or ""):continue
            if row_lane!=lane or refs!=memory_refs:continue
            claim_sim=_text_jaccard(claims," ".join(str(value) for value in row.get("evidence_claims") or []))
            problem_sim=_text_jaccard(problem,str(row.get("problem_text") or ""))
            if claim_sim<0.55 and problem_sim<0.35:continue
            return {"basin":basin,"source_candidate_id":str(row.get("source_candidate_id") or ""),"search_primitive":lane,"source_refs":refs,"claim_similarity":round(claim_sim,4),"problem_similarity":round(problem_sim,4),"reason":"same frozen evidence pool re-entered a persisted search closure without new evidence satisfying its reopen boundary","scientific_authority":False}
        if basin.startswith("principle-readjudication-"):
            # Evidence-level fresh-phenomenon closures are stronger than free-text
            # similarity.  If a seed's grounded claim/lane evidence reuses the exact
            # content-addressed primary evidence that a principle certificate closed,
            # repackaging the question cannot reopen it.  A different evidence item
            # from the same paper remains eligible because closure is evidence-level,
            # never source-level.
            closure=row.get("fresh_phenomenon_closure") or {}
            closure_ref=str(closure.get("source_ref") or "").strip() if isinstance(closure,dict) else ""
            closure_hashes={str(value or "").strip().lower() for value in (closure.get("closed_evidence_sha256") or []) if re.fullmatch(r"[0-9a-f]{64}",str(value or "").strip().lower())} if isinstance(closure,dict) else set()
            record=(registry or {}).get(closure_ref) if closure_ref else None
            if refs==[closure_ref] and closure_hashes and isinstance(record,dict):
                closed_texts=[]
                for values in (record.get("typed_evidence") or {}).values():
                    for item in values or []:
                        if isinstance(item,dict) and _fresh_evidence_sha(item) in closure_hashes:
                            text=" ".join(str(item.get("text") or "").split())
                            if text:closed_texts.append(text)
                for item in record.get("empirical_facts") or []:
                    if isinstance(item,dict) and _fresh_evidence_sha(item) in closure_hashes:
                        text=" ".join(str(item.get("text") or "").split())
                        if text:closed_texts.append(text)
                evidence=seed.get("empirical_evidence") or {};lane_evidence=seed.get("lane_evidence") or {}
                seed_evidence_texts=[str((evidence.get(key) or {}).get("claim") or "") for key in ("source_a","source_b")]
                seed_evidence_texts.extend(str(value or "") for value in lane_evidence.values())
                evidence_sim=max((_text_jaccard(candidate,closed) for candidate in seed_evidence_texts if candidate for closed in closed_texts),default=0.0)
                if evidence_sim>=0.50:
                    return {"basin":basin,"source_candidate_id":str(row.get("source_candidate_id") or ""),"search_primitive":lane,"source_refs":refs,"claim_similarity":round(evidence_sim,4),"problem_similarity":0.0,"closed_evidence_match":True,"reason":"same content-addressed primary evidence re-entered an exact principle-closed fresh phenomenon without new evidence satisfying its reopen boundary","scientific_authority":False}
            # Certified search closures persist across shadow pools. Keep the
            # machine veto deliberately narrow: the typed primitive and exact
            # primary-source set must be unchanged, and the proposed problem must
            # still be semantically close to the certified scope.  Adding new
            # primary evidence or moving to a materially different problem object
            # therefore remains a valid reopen path.
            if not row_lane or row_lane!=lane or not memory_refs or refs!=memory_refs:continue
            memory_problem=" ".join(str(row.get(key) or "") for key in ("title","problem_text"))
            problem_sim=max(_text_jaccard(problem,str(row.get("problem_text") or "")),_text_jaccard(problem+" "+claims,memory_problem))
            if problem_sim<0.28:continue
            return {"basin":basin,"source_candidate_id":str(row.get("source_candidate_id") or ""),"search_primitive":lane,"source_refs":refs,"claim_similarity":0.0,"problem_similarity":round(problem_sim,4),"reason":"same typed primary-source problem re-entered a persisted search closure without new evidence satisfying its reopen boundary","scientific_authority":False}
    return None


# Legacy alias for archived callers/tests; canonical semantics are search-closure deduplication.
_semantic_dead_end_seed_blocker=_search_closure_seed_blocker


def _compile_expansion_raw(*,pool:Path|None,run_root:Path,lane:str,count:int,part:int,memory_path:Path|None,requested_model:str,resolved_model:str,raw:str,raw_replayed_without_provider:bool=False,raw_origin_control_snapshot_sha256:str="",control_sha_override:str="",provider_metadata:dict|None=None)->dict:
    pool=_require_resolved_pool(run_root,pool);memory_path=_resolve_run_memory(run_root,memory_path);control_sha=str(control_sha_override or "") or _assert_run_control(run_root,pool,memory_path)
    payload=json.loads(pool.read_text(encoding="utf-8"));records=payload.get("records") or []
    lane=lane.strip().upper()
    if lane not in SEARCH_PORTFOLIO_PRIMITIVES:raise ValueError(f"unknown search primitive {lane}")
    memory=_shadow_search_memory(memory_path);effective_records=list(_search_asset_records(memory))+list(records);registry={str(r.get("ref")):r for r in effective_records if isinstance(r,dict) and r.get("ref")};fresh_target=_fresh_phenomenon_target(records,part,dead_end_memory=memory) if lane=="UNEXPLAINED_BOUNDARY" else {};fresh_target_id=str(fresh_target.get("phenomenon_id") or "")
    parsed,raw_sha=_parse_archived_json(run_root,f"expand-{lane}-p{part}",raw,resolved_model)
    pool_sha=str(payload.get("frozen_pool_sha256") or "").strip();seeds=[];search_closure_blocks=[]
    for i,item in enumerate(parsed.get("seeds") or [],1):
        if not isinstance(item,dict):continue
        row=_normalize_seed(item,lane,i);row["seed_id"]=f"{lane}-P{part}-{i:03d}"
        if not _valid_seed(row,registry):continue
        blocker=_search_closure_seed_blocker(row,memory,pool_sha,registry)
        if blocker:
            search_closure_blocks.append({"seed_id":row["seed_id"],**blocker});continue
        seeds.append(row)
    inversion_asset_refs={str(row.get("ref") or "") for row in _inversion_asset_records(memory)};inversion_asset_seed_count=sum(any(ref in inversion_asset_refs for ref in _source_refs(seed)) for seed in seeds)
    positive_asset_refs={str(row.get("ref") or "") for row in _positive_residual_asset_records(memory)};positive_residual_seed_count=sum(any(ref in positive_asset_refs for ref in _source_refs(seed)) for seed in seeds);positive_required=bool(lane=="UNEXPLAINED_BOUNDARY" and positive_asset_refs and count>=(2 if inversion_asset_refs else 1))
    fresh_priors=_fresh_phenomenon_priors(records,dead_end_memory=memory);fresh_refs={str(row.get("ref") or "") for row in fresh_priors};fresh_ids={str(row.get("phenomenon_id") or "") for row in fresh_priors};fresh_target_ref=str(fresh_target.get("ref") or "");fresh_required=bool(lane=="UNEXPLAINED_BOUNDARY" and not inversion_asset_refs and not positive_asset_refs and fresh_target_ref and fresh_target_id and count>0);fresh_seed_count=sum(any(ref in fresh_refs for ref in _source_refs(seed)) for seed in seeds);fresh_target_source_satisfied=bool(seeds and fresh_target_ref in _source_refs(seeds[0]));fresh_target_phenomenon_satisfied=bool(seeds and _fresh_target_seed_match(seeds[0],fresh_target));fresh_target_satisfied=fresh_target_source_satisfied and fresh_target_phenomenon_satisfied
    if fresh_required and not fresh_target_satisfied:seeds=[]
    transport={"provider_calls_executed":0,"transport_fallback_used":False,"transport_attempts":[],"thinking_compatibility_fallback":False} if raw_replayed_without_provider else dict(provider_metadata or {"provider_calls_executed":1,"transport_fallback_used":False,"transport_attempts":[],"thinking_compatibility_fallback":False})
    out={"schema_version":STAGE_RUNNER_ARTIFACT_SCHEMA,"control_snapshot_sha256":control_sha,"lane":lane,"part":part,"requested":count,"requested_model":requested_model,"resolved_model":resolved_model,"raw_sha256":raw_sha,"raw_archived_before_parse":True,"raw_replayed_without_provider":bool(raw_replayed_without_provider),"raw_origin_control_snapshot_sha256":str(raw_origin_control_snapshot_sha256 or ""),**transport,"shadow_search_memory_sha256":hashlib.sha256(json.dumps(memory,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest() if memory else "","frozen_pool_sha256":pool_sha,"valid_seeds":len(seeds),"inversion_asset_seed_count":inversion_asset_seed_count,"inversion_asset_requirement_satisfied":(not inversion_asset_refs or inversion_asset_seed_count>0),"positive_residual_seed_count":positive_residual_seed_count,"positive_residual_requirement_satisfied":(not positive_required or positive_residual_seed_count>0),"fresh_phenomenon_seed_count":fresh_seed_count,"fresh_phenomenon_requirement_satisfied":(not fresh_required or fresh_target_satisfied),"fresh_phenomenon_target_ref":fresh_target_ref,"fresh_phenomenon_target_id":fresh_target_id,"fresh_phenomenon_target_kind":str(fresh_target.get("phenomenon_kind") or ""),"fresh_phenomenon_target_text":str(fresh_target.get("phenomenon_text") or ""),"fresh_phenomenon_target_source_satisfied":fresh_target_source_satisfied,"fresh_phenomenon_target_exact_satisfied":fresh_target_phenomenon_satisfied,"fresh_phenomenon_refs":sorted(fresh_refs),"fresh_phenomenon_ids":sorted(fresh_ids),"search_closure_blocks":search_closure_blocks,"search_closure_block_count":len(search_closure_blocks),"seeds":seeds,"scientific_authority":False}
    run_root.mkdir(parents=True,exist_ok=True);(run_root/f"expand-{lane}-p{part}.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return {k:out[k] for k in ("lane","part","requested","resolved_model","raw_sha256","valid_seeds")}


def expand(*,pool:Path|None,run_root:Path,lane:str,count:int=6,model:str=PREMIUM_AUTO,part:int=1,memory_path:Path|None=None) -> dict:
    model=preferred_model("portfolio_expand",model)
    pool=_require_resolved_pool(run_root,pool);memory_path=_resolve_run_memory(run_root,memory_path);control_sha=_assert_run_control(run_root,pool,memory_path)
    payload=json.loads(pool.read_text(encoding="utf-8"));records=payload.get("records") or [];memory=_shadow_search_memory(memory_path);lane=lane.strip().upper();fresh_target=_fresh_phenomenon_target(records,part,dead_end_memory=memory) if lane=="UNEXPLAINED_BOUNDARY" else {};fresh_target_id=str(fresh_target.get("phenomenon_id") or "");prompt=_expansion_prompt(lane,records,count,memory,fresh_target_ref=str(fresh_target.get("ref") or ""),fresh_target_phenomenon_id=fresh_target_id)
    res=_ark_with_provider_receipt(run_root=run_root,stem=f"expand-{lane}-p{part}",requested_model=model,context={"lane":lane,"part":part,"requested":count,"fresh_target_ref":str(fresh_target.get("ref") or ""),"fresh_target_phenomenon_id":fresh_target_id,"control_snapshot_sha256":control_sha},prompt=prompt,max_output_tokens=5200,temperature=.85);raw=str(res.get("text") or "");resolved=str(res.get("resolved_model") or model);provider_metadata=_provider_success_metadata(run_root=run_root,stem=f"expand-{lane}-p{part}",response=res)
    return _compile_expansion_raw(pool=pool,run_root=run_root,lane=lane,count=count,part=part,memory_path=memory_path,requested_model=model,resolved_model=resolved,raw=raw,control_sha_override=control_sha,provider_metadata=provider_metadata)


def replay_expand(*,pool:Path|None,run_root:Path,lane:str,count:int,part:int,memory_path:Path|None,raw_input:Path,expected_raw_sha256:str,requested_model:str,resolved_model:str,raw_origin_control_snapshot_sha256:str)->dict:
    if not raw_input.is_file():raise ValueError(f"raw replay input unavailable: {raw_input}")
    expected=str(expected_raw_sha256 or "").strip().lower();origin=str(raw_origin_control_snapshot_sha256 or "").strip().lower()
    if not re.fullmatch(r"[0-9a-f]{64}",expected):raise ValueError("raw replay requires exact --raw-sha256")
    if not re.fullmatch(r"[0-9a-f]{64}",origin):raise ValueError("raw replay requires exact --raw-origin-control")
    raw=raw_input.read_text(encoding="utf-8");actual=hashlib.sha256(raw.encode()).hexdigest()
    if actual!=expected:raise ValueError(f"raw replay digest mismatch expected={expected} actual={actual}")
    requested=str(requested_model or "").strip();resolved=str(resolved_model or "").strip()
    if not requested or not resolved:raise ValueError("raw replay requires requested and resolved model identities")
    resolved_pool=_require_resolved_pool(run_root,pool);resolved_memory=_resolve_run_memory(run_root,memory_path);control_sha=_assert_run_control(run_root,resolved_pool,resolved_memory)
    return _compile_expansion_raw(pool=resolved_pool,run_root=run_root,lane=lane,count=count,part=part,memory_path=resolved_memory,requested_model=requested,resolved_model=resolved,raw=raw,raw_replayed_without_provider=True,raw_origin_control_snapshot_sha256=origin,control_sha_override=control_sha)


def assemble(*,run_root:Path,archive_capacity:int=48,evolution_parents:int=24)->dict:
    control_sha=_assert_run_control(run_root)
    previous_parent_ids=[];previous_base_path=run_root/"base.json"
    if previous_base_path.is_file():
        previous=json.loads(previous_base_path.read_text(encoding="utf-8"));_require_artifact_control(previous,control_sha,previous_base_path,"1.2")
        previous_parent_ids=[str(row.get("seed_id") or "") for row in previous.get("parents") or [] if isinstance(row,dict) and str(row.get("seed_id") or "")]
    raw=[];shards=[];fresh_anchor_ids=[];fresh_anchor_seen=set()
    for path in sorted(run_root.glob("expand-*.json")):
        payload=json.loads(path.read_text(encoding="utf-8"));_require_artifact_control(payload,control_sha,path,STAGE_RUNNER_ARTIFACT_SCHEMA);rows=[dict(row) for row in (payload.get("seeds") or []) if isinstance(row,dict)]
        target_bound=bool(payload.get("fresh_phenomenon_requirement_satisfied") is True and payload.get("fresh_phenomenon_target_source_satisfied") is True and payload.get("fresh_phenomenon_target_exact_satisfied") is True and rows)
        if target_bound:
            anchor=rows[0];anchor_id=str(anchor.get("seed_id") or "");
            if not anchor_id:raise ValueError(f"fresh target shard lacks Seed 1 identity: {path.name}")
            anchor["fresh_target_anchor"]=True;anchor["fresh_target_ref"]=str(payload.get("fresh_phenomenon_target_ref") or "");anchor["fresh_target_id"]=str(payload.get("fresh_phenomenon_target_id") or "")
            if anchor_id not in fresh_anchor_seen:fresh_anchor_seen.add(anchor_id);fresh_anchor_ids.append(anchor_id)
        block_count=int(payload.get("search_closure_block_count") if "search_closure_block_count" in payload else (payload.get("semantic_dead_end_block_count") or 0))
        raw.extend(rows);shards.append({"path":path.name,"lane":payload.get("lane"),"part":payload.get("part","legacy"),"requested":payload.get("requested"),"valid_seeds":len(rows),"search_closure_blocks":block_count,"raw_sha256":payload.get("raw_sha256"),"resolved_model":payload.get("resolved_model"),"fresh_target_anchor_id":str(rows[0].get("seed_id") or "") if target_bound else ""})
    unique,dups=_semantic_dedup(raw,protected_ids=fresh_anchor_ids);unique_ids={str(row.get("seed_id") or "") for row in unique}
    if not set(fresh_anchor_ids).issubset(unique_ids):raise ValueError("fresh target anchor lost during semantic dedup")
    unique,clusters=_assign_structural_clusters(unique);archives=_archives(unique,archive_capacity,required_ids=fresh_anchor_ids);by_id={row["seed_id"]:row for row in unique};breadth=[by_id[sid] for sid in archives["breadth"] if sid in by_id];breadth_ids={str(row.get("seed_id") or "") for row in breadth}
    if not set(fresh_anchor_ids).issubset(breadth_ids):raise ValueError("fresh target anchor lost from breadth archive")
    preserved_previous=[seed_id for seed_id in previous_parent_ids if seed_id in breadth_ids]
    required_parent_ids=preserved_previous+[seed_id for seed_id in fresh_anchor_ids if seed_id not in set(preserved_previous)]
    parents=_maxmin_select(breadth,min(evolution_parents,len(breadth)),required_ids=required_parent_ids)
    parent_ids=[str(row.get("seed_id") or "") for row in parents]
    if parent_ids[:len(preserved_previous)]!=preserved_previous:raise ValueError("incremental shadow reassembly reordered an existing parent prefix")
    if not set(fresh_anchor_ids).issubset(set(parent_ids)):raise ValueError("fresh target anchor lost from evolution parents")
    lane_counts={lane:sum(row.get("discovery_lane")==lane for row in raw) for lane in SEARCH_PORTFOLIO_PRIMITIVES};archive_lanes={lane:sum(by_id[sid].get("discovery_lane")==lane for sid in archives["breadth"] if sid in by_id) for lane in SEARCH_PORTFOLIO_PRIMITIVES}
    out={"schema_version":"1.2","control_snapshot_sha256":control_sha,"shards":shards,"summary":{"raw_seeds":len(raw),"search_closure_blocks":sum(int(shard.get("search_closure_blocks") or 0) for shard in shards),"semantic_unique":len(unique),"semantic_duplicates":len(dups),"structural_clusters":clusters,"breadth_archive":len(archives["breadth"]),"evolution_parents":len(parents),"fresh_target_anchors":len(fresh_anchor_ids),"fresh_target_anchors_preserved":sum(str(row.get("seed_id") or "") in set(fresh_anchor_ids) for row in parents),"previous_parent_prefix":len(previous_parent_ids),"previous_parent_prefix_preserved":len(preserved_previous),"lane_coverage":sum(value>0 for value in lane_counts.values()),"archive_lane_coverage":sum(value>0 for value in archive_lanes.values())},"policy":{"fresh_target_anchor_survives_semantic_dedup":True,"fresh_target_anchor_survives_breadth_archive":True,"fresh_target_anchor_survives_evolution_parent_selection":True,"fresh_target_anchor_is_prioritized_in_formulation_budget":True,"incremental_reassembly_preserves_existing_parent_prefix":True},"fresh_target_anchor_ids":fresh_anchor_ids,"previous_parent_prefix_ids":preserved_previous,"lane_counts":lane_counts,"archive_lane_counts":archive_lanes,"archives":archives,"duplicates":dups,"unique_seeds":unique,"parents":parents,"scientific_authority":False}
    (run_root/"base.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return out["summary"]


def evolve(*,pool:Path|None,run_root:Path,generation:int,part:int,batch_size:int=6,model:str=PREMIUM_AUTO,memory_path:Path|None=None)->dict:
    model=preferred_model("portfolio_evolve",model)
    pool=_require_resolved_pool(run_root,pool);memory_path=_resolve_run_memory(run_root,memory_path);control_sha=_assert_run_control(run_root,pool,memory_path)
    pool_payload=json.loads(pool.read_text(encoding="utf-8"));records=pool_payload.get("records") or [];memory=_shadow_search_memory(memory_path);effective_records=list(_search_asset_records(memory))+list(records);registry={str(r.get("ref")):r for r in effective_records if isinstance(r,dict) and r.get("ref")};pool_sha=str(pool_payload.get("frozen_pool_sha256") or "").strip();base_path=run_root/"base.json";base=json.loads(base_path.read_text(encoding="utf-8"));_require_artifact_control(base,control_sha,base_path,"1.2")
    if generation==1:parents=base.get("parents") or []
    elif generation==2:
        g1=[]
        for path in sorted(run_root.glob("evolve-g1-p*.json")):
            payload=json.loads(path.read_text(encoding="utf-8"));_require_artifact_control(payload,control_sha,path,STAGE_RUNNER_ARTIFACT_SCHEMA);g1.extend(payload.get("children") or [])
        parents=_maxmin_select(g1,min(12,len(g1)))
    else:raise ValueError("generation must be 1 or 2")
    start=(part-1)*batch_size;batch=parents[start:start+batch_size]
    if not batch:raise ValueError(f"empty evolution batch generation={generation} part={part}")
    temperature=.60 if generation==1 else .35;prompt=_evolution_prompt(batch,generation)+" SHADOW SEARCH-CLOSURE MEMORY (search control only; never scientific authority)="+json.dumps(memory,ensure_ascii=False,separators=(",",":"));res=_ark_with_provider_receipt(run_root=run_root,stem=f"evolve-g{generation}-p{part}",requested_model=model,context={"generation":generation,"part":part,"requested_children":len(batch),"control_snapshot_sha256":control_sha},prompt=prompt,max_output_tokens=5200,temperature=temperature);raw=str(res.get("text") or "");resolved=str(res.get("resolved_model") or model);payload,raw_sha=_parse_archived_json(run_root,f"evolve-g{generation}-p{part}",raw,resolved);pmap={p["seed_id"]:p for p in batch};children=[];search_closure_blocks=[]
    for i,item in enumerate(payload.get("children") or [],1):
        if not isinstance(item,dict):continue
        parent=pmap.get(str(item.get("parent_id") or ""))
        if not parent:continue
        merged={**parent,**item,"discovery_lane":parent["discovery_lane"],"empirical_evidence":parent["empirical_evidence"],"lane_evidence":parent["lane_evidence"],"cross_domain_origin":parent.get("cross_domain_origin","")};row=_normalize_seed(merged,parent["discovery_lane"],i);row["seed_id"]=f"{parent['seed_id']}-G{generation}";row["parent_id"]=parent["seed_id"];row["branch_depth"]=generation
        if not _valid_seed(row,registry):continue
        blocker=_search_closure_seed_blocker(row,memory,pool_sha,registry)
        if blocker:
            search_closure_blocks.append({"seed_id":row["seed_id"],**blocker});continue
        children.append(row)
    out={"schema_version":STAGE_RUNNER_ARTIFACT_SCHEMA,"control_snapshot_sha256":control_sha,"generation":generation,"part":part,"parent_ids":[p["seed_id"] for p in batch],"requested_children":len(batch),"valid_children":len(children),"requested_model":model,"resolved_model":resolved,"raw_sha256":raw_sha,"raw_archived_before_parse":True,"shadow_search_memory_sha256":hashlib.sha256(json.dumps(memory,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest() if memory else "","frozen_pool_sha256":pool_sha,"search_closure_blocks":search_closure_blocks,"search_closure_block_count":len(search_closure_blocks),"temperature":temperature,"children":children,"scientific_authority":False}
    (run_root/f"evolve-g{generation}-p{part}.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return {k:out[k] for k in ("generation","part","requested_children","valid_children","resolved_model","raw_sha256")}


def formulation_pool(run_root:Path,budget:int=24,control_sha:str="")->list[dict]:
    base_path=run_root/"base.json";base=json.loads(base_path.read_text(encoding="utf-8"));_require_artifact_control(base,control_sha,base_path,"1.2");rows=list(base.get("parents") or []);required_ids={str(value) for value in base.get("fresh_target_anchor_ids") or [] if str(value)}
    for path in sorted(run_root.glob("evolve-g1-p*.json")):
        payload=json.loads(path.read_text(encoding="utf-8"));_require_artifact_control(payload,control_sha,path,STAGE_RUNNER_ARTIFACT_SCHEMA);rows.extend(payload.get("children") or [])
    for path in sorted(run_root.glob("evolve-g2-p*.json")):
        payload=json.loads(path.read_text(encoding="utf-8"));_require_artifact_control(payload,control_sha,path,STAGE_RUNNER_ARTIFACT_SCHEMA);rows.extend(payload.get("children") or [])
    rows,_=_assign_structural_clusters(rows)
    if len(rows)<=budget:return rows
    return _maxmin_select(rows,budget,required_ids=required_ids)


_PROBLEM_FALSIFIER_ONLY_BLOCKERS=("reduction-falsifiability-contract-incomplete","saturation-exact-reduction-pending:","unresolved-exact-reduction-test:")


def _problem_falsifier_eligible(candidate:dict,audit:dict)->bool:
    blockers=[str(value) for value in audit.get("blockers") or []]
    if not blockers or audit.get("passed") is True:return False
    if not all(any(blocker.startswith(prefix) for prefix in _PROBLEM_FALSIFIER_ONLY_BLOCKERS) for blocker in blockers):return False
    if not any(blocker.startswith(("saturation-exact-reduction-pending:","unresolved-exact-reduction-test:")) for blocker in blockers):return False
    return all(str(candidate.get(key) or "").strip() for key in ("exact_prediction","strongest_same_information_baseline","cheapest_problem_falsifier"))


def _formulation_precheck(candidate:dict,registry:dict)->tuple[str,dict,dict]:
    normalized=_normalize(candidate,registry)
    audit=audit_shadow_problem_candidate(normalized,primary_evidence_by_ref=registry,require_primary_registry=True,require_semantic_review=False)
    if audit.get("passed") is True:return "machine-ready",normalized,audit
    if _problem_falsifier_eligible(normalized,audit):return "reduction-pending",normalized,audit
    return "rejected",normalized,audit


def formulate(*,pool:Path|None,run_root:Path,part:int,batch_size:int=2,budget:int=24,model:str=PREMIUM_AUTO,memory_path:Path|None=None)->dict:
    model=preferred_model("portfolio_formulate",model)
    pool=_require_resolved_pool(run_root,pool);memory_path=_resolve_run_memory(run_root,memory_path);control_sha=_assert_run_control(run_root,pool,memory_path)
    pool_payload=json.loads(pool.read_text(encoding="utf-8"));records=pool_payload.get("records") or [];memory=_shadow_search_memory(memory_path);effective_records=list(_search_asset_records(memory))+list(records);registry={str(r.get("ref")):r for r in effective_records if isinstance(r,dict) and r.get("ref")};pool_sha=str(pool_payload.get("frozen_pool_sha256") or "").strip();branches=formulation_pool(run_root,budget,control_sha);start=(part-1)*batch_size;batch=branches[start:start+batch_size]
    if not batch:raise ValueError(f"empty formulation batch part={part}")
    prompt=_formulation_prompt(batch,registry,memory);res=_ark_with_provider_receipt(run_root=run_root,stem=f"formulate-p{part}",requested_model=model,context={"part":part,"branch_ids":[b["seed_id"] for b in batch],"control_snapshot_sha256":control_sha},prompt=prompt,max_output_tokens=5600,temperature=.15);raw=str(res.get("text") or "");resolved=str(res.get("resolved_model") or model);provider_metadata=_provider_success_metadata(run_root=run_root,stem=f"formulate-p{part}",response=res);payload,raw_sha=_parse_archived_json(run_root,f"formulate-p{part}",raw,resolved);live=[x for x in (payload.get("candidates") or []) if isinstance(x,dict)];dead=[x for x in (payload.get("rejected") or []) if isinstance(x,dict)]
    # Preserve branch provenance and typed evidence deterministically. The model
    # may sharpen claims but cannot silently change the source refs or lane. A
    # deterministic precheck then separates machine-ready problems from exact-
    # reduction uncertainty and all other formulation failures. Reduction-pending
    # objects remain zero-authority and may only enter the problem-falsifier path.
    by={b["seed_id"]:b for b in batch};normalized=[];reduction_pending=[];search_closure_blocks=[]
    for i,item in enumerate(live,1):
        parent=by.get(str(item.get("source_branch_id") or ""))
        if not parent:continue
        row=dict(item);row["model_candidate_id"]=str(row.get("candidate_id") or "").strip();row["candidate_id"]=f"SHADOW-P{part:02d}-C{i:02d}";row["source_branch_id"]=parent["seed_id"];row["branch_depth"]=parent.get("branch_depth",0);row["discovery_lane"]=parent["discovery_lane"];row["empirical_evidence"]=parent["empirical_evidence"];row["lane_evidence"]=parent["lane_evidence"]
        blocker=_search_closure_seed_blocker(row,memory,pool_sha,registry)
        if blocker:
            search_closure_blocks.append({"candidate_id":row["candidate_id"],"source_branch_id":parent["seed_id"],**blocker});continue
        route,audited,audit=_formulation_precheck(row,registry)
        if route=="machine-ready":
            normalized.append(row);continue
        if route=="reduction-pending":
            reduction_pending.append({"candidate_id":row["candidate_id"],"model_candidate_id":row["model_candidate_id"],"source_branch_id":row["source_branch_id"],"title":row.get("title"),"discovery_lane":row.get("discovery_lane"),"blockers":list(audit.get("blockers") or []),"exact_prediction":audited.get("exact_prediction"),"strongest_same_information_baseline":audited.get("strongest_same_information_baseline"),"cheapest_problem_falsifier":audited.get("cheapest_problem_falsifier"),"candidate":row,"scientific_authority":False,"authority":{"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False}});continue
        dead.append({"source_branch_id":row["source_branch_id"],"candidate_id":row["candidate_id"],"title":row.get("title"),"reason":"deterministic formulation precheck found blockers beyond exact-reduction uncertainty","matched_mature_theory":audited.get("strongest_same_information_baseline"),"reduction_class":"FORMULATION_MACHINE_CONTRACT_INCOMPLETE","exact_reduction_test":audited.get("cheapest_problem_falsifier"),"blockers":list(audit.get("blockers") or []),"rejection_origin":"deterministic-formulation-precheck","candidate":row,"scientific_authority":False})
    out={"schema_version":STAGE_RUNNER_ARTIFACT_SCHEMA,"control_snapshot_sha256":control_sha,"part":part,"branch_ids":[b["seed_id"] for b in batch],"requested_model":model,"resolved_model":resolved,"raw_sha256":raw_sha,"raw_archived_before_parse":True,"raw_replayed_without_provider":False,"raw_origin_control_snapshot_sha256":"",**provider_metadata,"shadow_search_memory_sha256":hashlib.sha256(json.dumps(memory,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest() if memory else "","frozen_pool_sha256":pool_sha,"search_closure_blocks":search_closure_blocks,"search_closure_block_count":len(search_closure_blocks),"candidates":normalized,"reduction_pending":reduction_pending,"reduction_pending_count":len(reduction_pending),"rejected":dead,"scientific_authority":False}
    (run_root/f"formulate-p{part}.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return {"part":part,"branches":len(batch),"candidates":len(normalized),"reduction_pending":len(reduction_pending),"rejected":len(dead),"resolved_model":out["resolved_model"],"raw_sha256":out["raw_sha256"]}


def replay_formulate(*,pool:Path|None,run_root:Path,part:int,raw_input:Path,expected_raw_sha256:str,requested_model:str,resolved_model:str,raw_origin_control_snapshot_sha256:str,batch_size:int=2,budget:int=24,memory_path:Path|None=None)->dict:
    """Recompile an archived formulation response under the current qualified control with zero provider calls."""
    if not raw_input.is_file():raise ValueError(f"raw replay input unavailable: {raw_input}")
    expected=str(expected_raw_sha256 or "").strip().lower();origin=str(raw_origin_control_snapshot_sha256 or "").strip().lower()
    if not re.fullmatch(r"[0-9a-f]{64}",expected):raise ValueError("formulation raw replay requires exact --raw-sha256")
    if not re.fullmatch(r"[0-9a-f]{64}",origin):raise ValueError("formulation raw replay requires exact --raw-origin-control")
    raw=raw_input.read_text(encoding="utf-8");actual=hashlib.sha256(raw.encode()).hexdigest()
    if actual!=expected:raise ValueError(f"formulation raw replay digest mismatch expected={expected} actual={actual}")
    requested=str(requested_model or "").strip();resolved=str(resolved_model or "").strip()
    if not requested or not resolved:raise ValueError("formulation raw replay requires requested and resolved model identities")
    pool=_require_resolved_pool(run_root,pool);memory_path=_resolve_run_memory(run_root,memory_path);control_sha=_assert_run_control(run_root,pool,memory_path)
    pool_payload=json.loads(pool.read_text(encoding="utf-8"));records=pool_payload.get("records") or [];memory=_shadow_search_memory(memory_path);effective_records=list(_search_asset_records(memory))+list(records);registry={str(r.get("ref")):r for r in effective_records if isinstance(r,dict) and r.get("ref")};pool_sha=str(pool_payload.get("frozen_pool_sha256") or "").strip();branches=formulation_pool(run_root,budget,control_sha);start=(part-1)*batch_size;batch=branches[start:start+batch_size]
    if not batch:raise ValueError(f"empty formulation replay batch part={part}")
    payload,raw_sha=_parse_archived_json(run_root,f"formulate-p{part}",raw,resolved);live=[x for x in (payload.get("candidates") or []) if isinstance(x,dict)];dead=[x for x in (payload.get("rejected") or []) if isinstance(x,dict)]
    by={b["seed_id"]:b for b in batch};normalized=[];reduction_pending=[];search_closure_blocks=[]
    for i,item in enumerate(live,1):
        parent=by.get(str(item.get("source_branch_id") or ""))
        if not parent:continue
        row=dict(item);row["model_candidate_id"]=str(row.get("candidate_id") or "").strip();row["candidate_id"]=f"SHADOW-P{part:02d}-C{i:02d}";row["source_branch_id"]=parent["seed_id"];row["branch_depth"]=parent.get("branch_depth",0);row["discovery_lane"]=parent["discovery_lane"];row["empirical_evidence"]=parent["empirical_evidence"];row["lane_evidence"]=parent["lane_evidence"]
        blocker=_search_closure_seed_blocker(row,memory,pool_sha,registry)
        if blocker:
            search_closure_blocks.append({"candidate_id":row["candidate_id"],"source_branch_id":parent["seed_id"],**blocker});continue
        route,audited,audit=_formulation_precheck(row,registry)
        if route=="machine-ready":normalized.append(row);continue
        if route=="reduction-pending":
            reduction_pending.append({"candidate_id":row["candidate_id"],"model_candidate_id":row["model_candidate_id"],"source_branch_id":row["source_branch_id"],"title":row.get("title"),"discovery_lane":row.get("discovery_lane"),"blockers":list(audit.get("blockers") or []),"exact_prediction":audited.get("exact_prediction"),"strongest_same_information_baseline":audited.get("strongest_same_information_baseline"),"cheapest_problem_falsifier":audited.get("cheapest_problem_falsifier"),"candidate":row,"scientific_authority":False,"authority":{"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False}});continue
        dead.append({"source_branch_id":row["source_branch_id"],"candidate_id":row["candidate_id"],"title":row.get("title"),"reason":"deterministic formulation precheck found blockers beyond exact-reduction uncertainty","matched_mature_theory":audited.get("strongest_same_information_baseline"),"reduction_class":"FORMULATION_MACHINE_CONTRACT_INCOMPLETE","exact_reduction_test":audited.get("cheapest_problem_falsifier"),"blockers":list(audit.get("blockers") or []),"rejection_origin":"deterministic-formulation-precheck","candidate":row,"scientific_authority":False})
    out={"schema_version":STAGE_RUNNER_ARTIFACT_SCHEMA,"control_snapshot_sha256":control_sha,"part":part,"branch_ids":[b["seed_id"] for b in batch],"requested_model":requested,"resolved_model":resolved,"raw_sha256":raw_sha,"raw_archived_before_parse":True,"raw_replayed_without_provider":True,"raw_origin_control_snapshot_sha256":origin,"provider_calls_executed":0,"transport_fallback_used":False,"transport_attempts":[],"thinking_compatibility_fallback":False,"shadow_search_memory_sha256":hashlib.sha256(json.dumps(memory,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest() if memory else "","frozen_pool_sha256":pool_sha,"search_closure_blocks":search_closure_blocks,"search_closure_block_count":len(search_closure_blocks),"candidates":normalized,"reduction_pending":reduction_pending,"reduction_pending_count":len(reduction_pending),"rejected":dead,"scientific_authority":False}
    (run_root/f"formulate-p{part}.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return {"part":part,"branches":len(batch),"candidates":len(normalized),"reduction_pending":len(reduction_pending),"rejected":len(dead),"resolved_model":resolved,"raw_sha256":raw_sha,"provider_calls_executed":0}


def machine_audit(*,pool:Path|None,run_root:Path)->dict:
    pool=_require_resolved_pool(run_root,pool);control_sha=_assert_run_control(run_root,pool)
    records=json.loads(pool.read_text(encoding="utf-8")).get("records") or [];memory=_shadow_search_memory(_resolve_run_memory(run_root,None));effective_records=list(_search_asset_records(memory))+list(records);registry={str(r.get("ref")):r for r in effective_records if isinstance(r,dict) and r.get("ref")}
    reviewable=[];reduction_pending=[];blocked=[];problem_falsifier_queue=[];formulated=0;machine_ready_input=0;pending_input=0
    def process(item:dict,path:Path,part:int,idx:int,route_origin:str)->None:
        nonlocal formulated,machine_ready_input,pending_input
        outer=dict(item);raw_candidate=dict(outer.get("candidate") or outer) if route_origin=="formulation-reduction-pending" else dict(outer)
        stored_id=str(outer.get("candidate_id") or raw_candidate.get("candidate_id") or "").strip();canonical_id=stored_id if stored_id.startswith(f"SHADOW-P{part:02d}-C") else f"SHADOW-P{part:02d}-C{idx:02d}"
        model_id=str(outer.get("model_candidate_id") or raw_candidate.get("model_candidate_id") or raw_candidate.get("candidate_id") or "").strip();raw_candidate["model_candidate_id"]=model_id;raw_candidate["candidate_id"]=canonical_id
        candidate=_normalize(raw_candidate,registry);audit=audit_shadow_problem_candidate(candidate,primary_evidence_by_ref=registry,require_primary_registry=True,require_semantic_review=False);falsifier_eligible=_problem_falsifier_eligible(candidate,audit)
        row={"candidate_id":candidate["candidate_id"],"model_candidate_id":model_id,"source_artifact":path.name,"route_origin":route_origin,"candidate":candidate,"audit":audit,"problem_falsifier_eligible":falsifier_eligible}
        formulated+=1;machine_ready_input+=int(route_origin=="formulation-machine-ready");pending_input+=int(route_origin=="formulation-reduction-pending")
        if audit.get("passed") is True:
            if route_origin=="formulation-reduction-pending":
                row["routing_error"]="reduction-pending artifact unexpectedly became machine-ready without reformulation";blocked.append(row)
            else:reviewable.append(row)
            return
        if falsifier_eligible:
            reduction_pending.append(row);problem_falsifier_queue.append({"candidate_id":candidate["candidate_id"],"title":candidate.get("title"),"discovery_lane":candidate.get("discovery_lane"),"source_branch_id":candidate.get("source_branch_id"),"source_artifact":path.name,"blockers":list(audit.get("blockers") or []),"irreducible_object":candidate.get("irreducible_object"),"endpoint_headroom_requirement":candidate.get("endpoint_headroom_requirement"),"exact_prediction":candidate.get("exact_prediction"),"strongest_same_information_baseline":candidate.get("strongest_same_information_baseline"),"cheapest_problem_falsifier":candidate.get("cheapest_problem_falsifier"),"candidate":candidate,"scientific_authority":False,"authority":{"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False}});return
        blocked.append(row)
    for path in sorted(run_root.glob("formulate-p*.json"),key=lambda value:int(value.stem.split("p")[-1])):
        payload=json.loads(path.read_text(encoding="utf-8"));_require_artifact_control(payload,control_sha,path,STAGE_RUNNER_ARTIFACT_SCHEMA);part=int(payload.get("part") or path.stem.split("p")[-1])
        for idx,item in enumerate(payload.get("candidates") or [],1):
            if isinstance(item,dict):process(item,path,part,idx,"formulation-machine-ready")
        for idx,item in enumerate(payload.get("reduction_pending") or [],1):
            if isinstance(item,dict):process(item,path,part,idx,"formulation-reduction-pending")
    ids=[row["candidate_id"] for row in reviewable+reduction_pending+blocked]
    if len(ids)!=len(set(ids)):raise ValueError("shadow machine audit candidate ids must be unique across ready, reduction-pending, and blocked routes")
    out={"schema_version":"1.3-shadow","control_snapshot_sha256":control_sha,"summary":{"formulated":formulated,"machine_ready_input":machine_ready_input,"formulation_reduction_pending_input":pending_input,"reviewable":len(reviewable),"reduction_pending":len(reduction_pending),"blocked":len(blocked),"problem_falsifier_eligible":len(problem_falsifier_queue),"live_problem_gate_eligible":0},"policy":{"formulation_precheck_separates_machine_ready_from_reduction_pending":True,"machine_audit_rechecks_both_routes":True,"reduction_pending_is_not_scientific_block_or_pass":True,"problem_falsifier_route_is_zero_authority":True,"only_exact_reduction_uncertainty_can_enter_problem_falsifier_route":True,"closest_work_lane_provenance_or_schema_failures_cannot_enter_problem_falsifier_route":True,"problem_falsifier_route_cannot_authorize_paper_design_method_experiment_p0_or_gpu":True,"reduction_pending_enters_bounded_evidence_design_portfolio":True,"evidence_acquisition_authority_is_not_scientific_claim_authority":True},"reviewable":reviewable,"reduction_pending":reduction_pending,"blocked":blocked,"problem_falsifier_queue":problem_falsifier_queue,"scientific_authority":False,"authority":{"live_problem_gate":False,"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False}}
    evidence=build_provisional_evidence_plan(out,run_id=run_root.name);evidence["control_snapshot_sha256"]=control_sha
    out["summary"]["provisional_problem_candidates"]=int((evidence.get("summary") or {}).get("provisional_problem_candidates") or 0);out["summary"]["evidence_design_selected"]=int((evidence.get("summary") or {}).get("design_selected") or 0)
    (run_root/"machine-audit.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (run_root/EVIDENCE_PLAN_FILENAME).write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return out["summary"]


def evidence_design(*,pool:Path|None,run_root:Path,part:int,batch_size:int=2,model:str=PREMIUM_AUTO)->dict:
    model=preferred_model("evidence_design",model)
    pool=_require_resolved_pool(run_root,pool);control_sha=_assert_run_control(run_root,pool)
    machine_path=run_root/"machine-audit.json";machine=json.loads(machine_path.read_text(encoding="utf-8"));_require_artifact_control(machine,control_sha,machine_path,"1.3-shadow")
    plan_path=run_root/EVIDENCE_PLAN_FILENAME
    if not plan_path.exists():
        plan=build_provisional_evidence_plan(machine,run_id=run_root.name);plan["control_snapshot_sha256"]=control_sha;plan_path.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    plan=json.loads(plan_path.read_text(encoding="utf-8"))
    if str(plan.get("control_snapshot_sha256") or "")!=control_sha:raise ValueError("bounded evidence plan control snapshot mismatch")
    prompt,candidate_ids=evidence_design_prompt(plan,part=part,batch_size=batch_size)
    res=_ark_with_provider_receipt(run_root=run_root,stem=f"evidence-design-p{part}",requested_model=model,context={"part":part,"candidate_ids":candidate_ids,"control_snapshot_sha256":control_sha},prompt=prompt,max_output_tokens=5200,temperature=0.0)
    raw=str(res.get("text") or "");resolved=str(res.get("resolved_model") or model);payload,sha=_parse_archived_evidence_design_json(run_root,f"evidence-design-p{part}",raw,resolved)
    state=compile_evidence_designs(plan,payload,part=part,design_model=resolved);state["control_snapshot_sha256"]=control_sha;plan_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    artifact={"schema_version":STAGE_RUNNER_ARTIFACT_SCHEMA,"control_snapshot_sha256":control_sha,"part":part,"candidate_ids":candidate_ids,"requested_model":model,"resolved_model":resolved,"raw_sha256":sha,"raw_archived_before_parse":True,"designs":payload.get("designs") or [],"plan_summary":state.get("summary") or {},"scientific_authority":False,"authority":{"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False}}
    (run_root/f"evidence-design-p{part}.json").write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return {"part":part,"candidate_ids":candidate_ids,"resolved_model":resolved,"raw_sha256":sha,"summary":state.get("summary") or {},"scientific_authority":False}


def evidence_operationalization_recompile(*,run_root:Path,part:int,batch_size:int=2,model:str=PREMIUM_AUTO)->dict:
    model=preferred_model("evidence_recompile",model)
    control_sha=_assert_run_control(run_root);plan_path=run_root/EVIDENCE_PLAN_FILENAME;plan=json.loads(plan_path.read_text(encoding="utf-8"))
    if str(plan.get("control_snapshot_sha256") or "")!=control_sha:raise ValueError("bounded evidence plan control snapshot mismatch")
    prompt,candidate_ids=operationalization_recompile_prompt(plan,part=part,batch_size=batch_size);res=_ark_with_provider_receipt(run_root=run_root,stem=f"evidence-recompile-p{part}",requested_model=model,context={"part":part,"candidate_ids":candidate_ids,"control_snapshot_sha256":control_sha},prompt=prompt,max_output_tokens=5600,temperature=0.0)
    raw=str(res.get("text") or "");resolved=str(res.get("resolved_model") or model);payload,sha=_parse_archived_evidence_design_json(run_root,f"evidence-recompile-p{part}",raw,resolved);state=compile_operationalization_recompiles(plan,payload,part=part,recompiler_model=resolved);state["control_snapshot_sha256"]=control_sha;plan_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    artifact={"schema_version":STAGE_RUNNER_ARTIFACT_SCHEMA,"control_snapshot_sha256":control_sha,"part":part,"candidate_ids":candidate_ids,"requested_model":model,"resolved_model":resolved,"raw_sha256":sha,"raw_archived_before_parse":True,"recompiles":payload.get("recompiles") or [],"plan_summary":state.get("summary") or {},"scientific_authority":False,"authority":{"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False}}
    (run_root/f"evidence-recompile-p{part}.json").write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");return {"part":part,"candidate_ids":candidate_ids,"resolved_model":resolved,"raw_sha256":sha,"summary":state.get("summary") or {},"scientific_authority":False}


def evidence_contract_review(*,run_root:Path,part:int,batch_size:int=2,model:str=PREMIUM_AUTO)->dict:
    model=preferred_model("evidence_review",model)
    control_sha=_assert_run_control(run_root);plan_path=run_root/EVIDENCE_PLAN_FILENAME;plan=json.loads(plan_path.read_text(encoding="utf-8"))
    if str(plan.get("control_snapshot_sha256") or "")!=control_sha:raise ValueError("bounded evidence plan control snapshot mismatch")
    prompt,candidate_ids=evidence_review_prompt(plan,part=part,batch_size=batch_size);res=_ark_with_provider_receipt(run_root=run_root,stem=f"evidence-review-p{part}",requested_model=model,context={"part":part,"candidate_ids":candidate_ids,"control_snapshot_sha256":control_sha},prompt=prompt,max_output_tokens=4200,temperature=0.0)
    raw=str(res.get("text") or "");resolved=str(res.get("resolved_model") or model);payload,sha=_parse_archived_evidence_design_json(run_root,f"evidence-review-p{part}",raw,resolved);state=compile_evidence_reviews(plan,payload,part=part,reviewer_model=resolved);state["control_snapshot_sha256"]=control_sha;plan_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    artifact={"schema_version":STAGE_RUNNER_ARTIFACT_SCHEMA,"control_snapshot_sha256":control_sha,"part":part,"candidate_ids":candidate_ids,"requested_model":model,"resolved_model":resolved,"raw_sha256":sha,"raw_archived_before_parse":True,"reviews":payload.get("reviews") or [],"plan_summary":state.get("summary") or {},"scientific_authority":False,"authority":{"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False}}
    (run_root/f"evidence-review-p{part}.json").write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");return {"part":part,"candidate_ids":candidate_ids,"resolved_model":resolved,"raw_sha256":sha,"summary":state.get("summary") or {},"scientific_authority":False}


def evidence_substrate_request(*,run_root:Path)->dict:
    control_sha=_assert_run_control(run_root);plan_path=run_root/EVIDENCE_PLAN_FILENAME;plan=json.loads(plan_path.read_text(encoding="utf-8"))
    if str(plan.get("control_snapshot_sha256") or "")!=control_sha:raise ValueError("bounded evidence plan control snapshot mismatch")
    state=build_substrate_preflight_request(plan);state["control_snapshot_sha256"]=control_sha;(run_root/"evidence-substrate-preflight-request.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");return {"status":state.get("status"),"summary":state.get("summary") or {},"scientific_authority":False}


def evidence_substrate_compile(*,run_root:Path,receipt_path:Path)->dict:
    control_sha=_assert_run_control(run_root);plan_path=run_root/EVIDENCE_PLAN_FILENAME;plan=json.loads(plan_path.read_text(encoding="utf-8"))
    if str(plan.get("control_snapshot_sha256") or "")!=control_sha:raise ValueError("bounded evidence plan control snapshot mismatch")
    receipts=json.loads(receipt_path.read_text(encoding="utf-8"));state=compile_substrate_preflight(plan,receipts);state["control_snapshot_sha256"]=control_sha;plan_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    artifact={"schema_version":STAGE_RUNNER_ARTIFACT_SCHEMA,"control_snapshot_sha256":control_sha,"receipt_sha256":hashlib.sha256(receipt_path.read_bytes()).hexdigest(),"summary":state.get("summary") or {},"scientific_authority":False,"authority":{"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False}}
    (run_root/"evidence-substrate-preflight.json").write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");return {"status":state.get("status"),"summary":state.get("summary") or {},"scientific_authority":False}


def evidence_harness_compile(*,run_root:Path,receipt_path:Path)->dict:
    control_sha=_assert_run_control(run_root);plan_path=run_root/EVIDENCE_PLAN_FILENAME;plan=json.loads(plan_path.read_text(encoding="utf-8"))
    if str(plan.get("control_snapshot_sha256") or "")!=control_sha:raise ValueError("bounded evidence plan control snapshot mismatch")
    receipts=json.loads(receipt_path.read_text(encoding="utf-8"));state=compile_harness_implementation_receipts(plan,receipts);state["control_snapshot_sha256"]=control_sha;plan_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    artifact={"schema_version":STAGE_RUNNER_ARTIFACT_SCHEMA,"control_snapshot_sha256":control_sha,"receipt_sha256":hashlib.sha256(receipt_path.read_bytes()).hexdigest(),"summary":state.get("summary") or {},"scientific_authority":False,"authority":{"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False}}
    (run_root/"evidence-harness-implementation.json").write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");return {"status":state.get("status"),"summary":state.get("summary") or {},"scientific_authority":False}


def evidence_adjudicate(*,run_root:Path,receipt_path:Path)->dict:
    control_sha=_assert_run_control(run_root);plan_path=run_root/EVIDENCE_PLAN_FILENAME;plan=json.loads(plan_path.read_text(encoding="utf-8"))
    if str(plan.get("control_snapshot_sha256") or "")!=control_sha:raise ValueError("bounded evidence plan control snapshot mismatch")
    receipts=json.loads(receipt_path.read_text(encoding="utf-8"));state=adjudicate_evidence_receipts(plan,receipts);state["control_snapshot_sha256"]=control_sha;plan_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    artifact={"schema_version":STAGE_RUNNER_ARTIFACT_SCHEMA,"control_snapshot_sha256":control_sha,"receipt_sha256":hashlib.sha256(receipt_path.read_bytes()).hexdigest(),"summary":state.get("summary") or {},"scientific_authority":False,"authority":{"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False}}
    (run_root/"evidence-acquisition-adjudication.json").write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return {"status":state.get("status"),"summary":state.get("summary") or {},"scientific_authority":False}


def review(*,pool:Path|None,run_root:Path,part:int,batch_size:int=2,model:str=PREMIUM_AUTO)->dict:
    model=preferred_model("semantic_review",model)
    pool=_require_resolved_pool(run_root,pool);control_sha=_assert_run_control(run_root,pool)
    records=json.loads(pool.read_text(encoding="utf-8")).get("records") or [];memory=_shadow_search_memory(_resolve_run_memory(run_root,None));effective_records=list(_search_asset_records(memory))+list(records);registry={str(r.get("ref")):r for r in effective_records if isinstance(r,dict) and r.get("ref")}
    audit_path=run_root/"machine-audit.json";audit=json.loads(audit_path.read_text(encoding="utf-8"));_require_artifact_control(audit,control_sha,audit_path,"1.3-shadow");rows=audit.get("reviewable") or [];start=(part-1)*batch_size;selected=rows[start:start+batch_size]
    if not selected:raise ValueError(f"empty review batch part={part}")
    generator_receipts,generator_resolved=_review_generator_receipts(run_root,selected,control_sha)
    candidates=[dict(row["candidate"]) for row in selected];prompt=reviewer_prompt(candidates,registry,shadow_mode=True);res=_ark_with_provider_receipt(run_root=run_root,stem=f"review-p{part}",requested_model=model,context={"part":part,"candidate_ids":[c["candidate_id"] for c in candidates],"control_snapshot_sha256":control_sha},prompt=prompt,max_output_tokens=5200,temperature=0.0);raw=str(res.get("text") or "");resolved=str(res.get("resolved_model") or model);payload,sha=_parse_archived_json(run_root,f"review-p{part}",raw,resolved)
    _apply_reviews(candidates,payload,model,resolved,generator_resolved,sha,registry)
    out={"schema_version":STAGE_RUNNER_ARTIFACT_SCHEMA,"control_snapshot_sha256":control_sha,"part":part,"candidate_ids":[c["candidate_id"] for c in candidates],"requested_model":model,"resolved_model":resolved,"generator_resolved_model":generator_resolved,"generator_receipts":generator_receipts,"raw_sha256":sha,"raw_archived_before_parse":True,"candidates":candidates,"scientific_authority":False}
    (run_root/f"review-p{part}.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return {"part":part,"candidate_ids":out["candidate_ids"],"resolved_model":resolved,"raw_sha256":sha,"semantic_clear":sum((c.get("semantic_reduction_review") or {}).get("verdict")=="CLEAR" for c in candidates)}


def finalize(*,pool:Path|None,run_root:Path)->dict:
    pool=_require_resolved_pool(run_root,pool);control_sha=_assert_run_control(run_root,pool)
    records=json.loads(pool.read_text(encoding="utf-8")).get("records") or [];memory=_shadow_search_memory(_resolve_run_memory(run_root,None));effective_records=list(_search_asset_records(memory))+list(records);registry={str(r.get("ref")):r for r in effective_records if isinstance(r,dict) and r.get("ref")}
    machine_path=run_root/"machine-audit.json";machine=json.loads(machine_path.read_text(encoding="utf-8"));_require_artifact_control(machine,control_sha,machine_path,"1.3-shadow");reviewed=[]
    for path in sorted(run_root.glob("review-p*.json"),key=lambda value:int(value.stem.split("p")[-1])):
        payload=json.loads(path.read_text(encoding="utf-8"));_require_artifact_control(payload,control_sha,path,STAGE_RUNNER_ARTIFACT_SCHEMA);reviewed.extend([row for row in (payload.get("candidates") or []) if isinstance(row,dict)])
    by_id={str(row.get("candidate_id") or ""):row for row in reviewed if row.get("candidate_id")};final_rows=[]
    for row in machine.get("reviewable") or []:
        candidate=by_id.get(str(row.get("candidate_id") or "")) or dict(row.get("candidate") or {})
        shadow=audit_shadow_problem_candidate(candidate,primary_evidence_by_ref=registry,require_primary_registry=True,require_semantic_review=True)
        live=audit_problem_candidate(candidate,primary_evidence_by_ref=registry,require_primary_registry=True,require_semantic_review=True)
        final_rows.append({"candidate_id":candidate.get("candidate_id"),"title":candidate.get("title"),"search_primitive":candidate.get("discovery_lane"),"shadow_clear":bool(shadow.get("passed")),"shadow_audit":shadow,"live_problem_gate_compatible":bool(live.get("passed")),"live_problem_gate_blockers":live.get("blockers") or [],"candidate":candidate})
    clear=sum(row["shadow_clear"] for row in final_rows);live_ready=sum(row["shadow_clear"] and row["live_problem_gate_compatible"] for row in final_rows)
    out={"schema_version":"1.1-shadow","control_snapshot_sha256":control_sha,"summary":{"machine_reviewable":len(machine.get("reviewable") or []),"reviewed":len(final_rows),"semantic_clear":clear,"semantic_blocked":len(final_rows)-clear,"shadow_survivors":clear,"live_problem_gate_compatible_survivors":live_ready,"live_paper_design_eligible":0},"rows":final_rows,"scientific_authority":False,"policy":{"shadow_survival_is_not_live_problem_gate_pass":True,"shadow_survivor_must_be_reformulated_under_a_live_empirical_lane":True,"canonical_generator_and_queue_untouched":True},"authority":{"live_problem_gate":False,"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False}}
    (run_root/"shadow-final-audit.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return out["summary"]


def main()->None:
    ap=argparse.ArgumentParser()
    ap.add_argument("command",choices=("expand","replay-expand","assemble","evolve","formulate","replay-formulate","audit","evidence-design","evidence-recompile","evidence-review","evidence-substrate-request","evidence-substrate-compile","evidence-harness-compile","evidence-adjudicate","falsifier-request","falsifier-preflight","review","finalize"))
    ap.add_argument("--pool",type=Path);ap.add_argument("--run-root",type=Path,required=True);ap.add_argument("--lane");ap.add_argument("--count",type=int,default=6);ap.add_argument("--part",type=int,default=1);ap.add_argument("--generation",type=int,default=1);ap.add_argument("--model",default=PREMIUM_AUTO);ap.add_argument("--memory",type=Path);ap.add_argument("--raw-input",type=Path);ap.add_argument("--raw-sha256",default="");ap.add_argument("--raw-origin-control",default="");ap.add_argument("--resolved-model",default="");ap.add_argument("--support-inventory",type=Path);ap.add_argument("--evidence-receipts",type=Path);ap.add_argument("--substrate-receipts",type=Path);ap.add_argument("--harness-receipts",type=Path);a=ap.parse_args()
    stop_marker=a.run_root/"shadow-run-qualification-stop.json"
    if stop_marker.exists():
        state=json.loads(stop_marker.read_text(encoding="utf-8"));raise SystemExit(f"shadow run stopped by qualification gate: {state.get('status','STOPPED')}")
    control_sha=_assert_run_control(a.run_root,a.pool,a.memory)
    if a.command=="expand":result=expand(pool=a.pool,run_root=a.run_root,lane=a.lane,count=a.count,model=a.model,part=a.part,memory_path=a.memory)
    elif a.command=="replay-expand":
        if a.raw_input is None:raise SystemExit("--raw-input is required for replay-expand")
        result=replay_expand(pool=a.pool,run_root=a.run_root,lane=a.lane,count=a.count,part=a.part,memory_path=a.memory,raw_input=a.raw_input,expected_raw_sha256=a.raw_sha256,requested_model=a.model,resolved_model=a.resolved_model,raw_origin_control_snapshot_sha256=a.raw_origin_control)
    elif a.command=="assemble":result=assemble(run_root=a.run_root)
    elif a.command=="evolve":result=evolve(pool=a.pool,run_root=a.run_root,generation=a.generation,part=a.part,model=a.model,memory_path=a.memory)
    elif a.command=="formulate":result=formulate(pool=a.pool,run_root=a.run_root,part=a.part,model=a.model,memory_path=a.memory)
    elif a.command=="replay-formulate":
        if a.raw_input is None:raise SystemExit("--raw-input is required for replay-formulate")
        result=replay_formulate(pool=a.pool,run_root=a.run_root,part=a.part,memory_path=a.memory,raw_input=a.raw_input,expected_raw_sha256=a.raw_sha256,requested_model=a.model,resolved_model=a.resolved_model,raw_origin_control_snapshot_sha256=a.raw_origin_control)
    elif a.command=="audit":result=machine_audit(pool=a.pool,run_root=a.run_root)
    elif a.command=="evidence-design":result=evidence_design(pool=a.pool,run_root=a.run_root,part=a.part,model=a.model)
    elif a.command=="evidence-recompile":result=evidence_operationalization_recompile(run_root=a.run_root,part=a.part,model=a.model)
    elif a.command=="evidence-review":result=evidence_contract_review(run_root=a.run_root,part=a.part,model=a.model)
    elif a.command=="evidence-substrate-request":result=evidence_substrate_request(run_root=a.run_root)
    elif a.command=="evidence-substrate-compile":
        if a.substrate_receipts is None:raise SystemExit("--substrate-receipts is required for evidence-substrate-compile")
        result=evidence_substrate_compile(run_root=a.run_root,receipt_path=a.substrate_receipts)
    elif a.command=="evidence-harness-compile":
        if a.harness_receipts is None:raise SystemExit("--harness-receipts is required for evidence-harness-compile")
        result=evidence_harness_compile(run_root=a.run_root,receipt_path=a.harness_receipts)
    elif a.command=="evidence-adjudicate":
        if a.evidence_receipts is None:raise SystemExit("--evidence-receipts is required for evidence-adjudicate")
        result=evidence_adjudicate(run_root=a.run_root,receipt_path=a.evidence_receipts)
    elif a.command=="falsifier-request":
        machine_path=a.run_root/"machine-audit.json";machine=json.loads(machine_path.read_text(encoding="utf-8"));_require_artifact_control(machine,control_sha,machine_path,"1.3-shadow");state=write_support_inventory_request(run_root=a.run_root);result={"status":state.get("status"),"summary":state.get("summary"),"scientific_authority":False}
    elif a.command=="falsifier-preflight":
        if a.support_inventory is None:raise SystemExit("--support-inventory is required for falsifier-preflight")
        machine_path=a.run_root/"machine-audit.json";machine=json.loads(machine_path.read_text(encoding="utf-8"));_require_artifact_control(machine,control_sha,machine_path,"1.3-shadow");state=write_problem_falsifier_preflight(run_root=a.run_root,support_inventory_path=a.support_inventory);result={"status":state.get("status"),"summary":state.get("summary"),"scientific_authority":False}
    elif a.command=="finalize":result=finalize(pool=a.pool,run_root=a.run_root)
    else:result=review(pool=a.pool,run_root=a.run_root,part=a.part,model=a.model)
    print(json.dumps(result,ensure_ascii=False))

if __name__=="__main__":main()
