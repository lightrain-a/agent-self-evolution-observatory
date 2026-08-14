from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import StorageSettings
from .paper_first_primary_evidence import (
    DEFAULT_MAX_PUBLICATION_AGE_DAYS,
    EMPIRICAL_FACT_EXTRACTION_VERSION,
    TYPED_EVIDENCE_EXTRACTION_VERSION,
    _paper_lane_keys,
    extract_empirical_fact_candidates,
    extract_typed_evidence_candidates,
    parse_arxiv_page,
)
from .paper_first_scientific_object_ontology import _matches_candidate, _matches_object_purity, load_scientific_object_config
from .paper_first_scientific_object_retrieval_audit import load_private_shadow_scientific_object_retrieval_audit

DEFAULT_LEDGER_NAME = "scientific-object-candidate-evidence-ledger-v1.json"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_date(value: str) -> datetime | None:
    raw=str(value or "").strip()
    if not raw:
        return None
    try:
        parsed=datetime.fromisoformat(raw + ("T00:00:00+00:00" if "T" not in raw else ""))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed=parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _latest_cache(root: Path, pattern: str) -> Path | None:
    candidates=sorted(root.glob(pattern),key=lambda path:path.stat().st_mtime,reverse=True)
    return candidates[0] if candidates else None


def _verified_cache_record(
    *,
    candidate_key: str,
    ref: str,
    title_hint: str,
    publication_date: str,
    source_root: Path,
    config: dict[str, Any],
    now: datetime,
    max_publication_age_days: float,
) -> tuple[dict[str, Any] | None, str | None]:
    if not ref.startswith("arXiv:"):
        return None,"invalid-ref"
    aid=ref.split(":",1)[1]
    primary_path=_latest_cache(source_root,f"arxiv-{aid}-*.html")
    if primary_path is None:
        return None,"primary-cache-missing"
    try:
        primary_bytes=primary_path.read_bytes()
    except OSError:
        return None,"primary-cache-unreadable"
    primary_sha=hashlib.sha256(primary_bytes).hexdigest()
    if not primary_path.stem.endswith(primary_sha[:12]):
        return None,"primary-cache-sha-mismatch"
    parsed=parse_arxiv_page(primary_bytes.decode("utf-8",errors="replace"))
    if not parsed["title"] or not parsed["abstract"]:
        return None,"primary-cache-parse-failed"
    publication=_parse_date(publication_date)
    if publication is None or max(0.0,(now-publication).total_seconds()/86400.0)>float(max_publication_age_days):
        return None,"publication-outside-freshness-window"
    spec=config["candidates"][candidate_key]
    probe={"title":parsed["title"],"abstract":parsed["abstract"]}
    if not _matches_candidate(probe,spec):
        return None,"candidate-object-match-failed"
    fulltext_path=_latest_cache(source_root,f"arxiv-full-{aid}-*.html")
    fulltext_sha="";fulltext=""
    if fulltext_path is not None:
        try:
            fulltext_bytes=fulltext_path.read_bytes()
            fulltext_sha=hashlib.sha256(fulltext_bytes).hexdigest()
            if fulltext_path.stem.endswith(fulltext_sha[:12]):
                fulltext=fulltext_bytes.decode("utf-8",errors="replace")
            else:
                fulltext_sha=""
        except OSError:
            fulltext_sha="";fulltext=""
    empirical=extract_empirical_fact_candidates(fulltext) if fulltext else []
    typed=extract_typed_evidence_candidates(fulltext) if fulltext else {"operational_assumptions":[],"measured_failures":[],"boundary_observations":[]}
    return {
        "ref":ref,
        "candidate_key":candidate_key,
        "title":parsed["title"],
        "title_hint":str(title_hint or "")[:300],
        "abstract":parsed["abstract"],
        "publication_date":publication_date,
        "source_sha256":primary_sha,
        "abstract_sha256":hashlib.sha256(parsed["abstract"].encode("utf-8")).hexdigest(),
        "fulltext_sha256":fulltext_sha,
        "primary_source_verified":True,
        "direct_object_match":_matches_object_purity(probe,spec),
        "lane_keys":list(_paper_lane_keys(probe)),
        "empirical_facts":empirical,
        "typed_evidence":typed,
        "empirical_fact_extraction_version":EMPIRICAL_FACT_EXTRACTION_VERSION,
        "typed_evidence_extraction_version":TYPED_EVIDENCE_EXTRACTION_VERSION,
        "shadow_candidate_evidence":True,
        "source_exposure_effect":False,
        "live_query_effect":False,
        "scientific_authority":False,
    },None


def build_scientific_object_candidate_evidence_ledger(
    *,
    storage: StorageSettings | None = None,
    retrieval_state: dict[str, Any] | None = None,
    now: datetime | None = None,
    max_publication_age_days: float = DEFAULT_MAX_PUBLICATION_AGE_DAYS,
) -> dict[str, Any]:
    storage=storage or StorageSettings.from_env();current=(now or _now()).astimezone(timezone.utc)
    retrieval=retrieval_state or load_private_shadow_scientific_object_retrieval_audit(storage=storage)
    config=load_scientific_object_config();source_root=storage.data_root/"paper-first-problem-discovery"/"primary-sources"
    results:dict[str,Any]={};all_records=[];all_errors=[]
    retrieval_complete=str(retrieval.get("status") or "")=="SHADOW_OBJECT_RETRIEVAL_AUDIT_COMPLETE"
    if retrieval_complete:
        for candidate_key,row in (retrieval.get("results") or {}).items():
            if candidate_key not in config["candidates"] or not isinstance(row,dict):
                continue
            candidate_records=[];candidate_errors=[]
            for meta in row.get("rows") or []:
                if not isinstance(meta,dict) or meta.get("already_reviewed") is True:
                    continue
                record,error=_verified_cache_record(candidate_key=candidate_key,ref=str(meta.get("ref") or ""),title_hint=str(meta.get("title") or ""),publication_date=str(meta.get("publication_date") or ""),source_root=source_root,config=config,now=current,max_publication_age_days=max_publication_age_days)
                if record is not None:
                    candidate_records.append(record);all_records.append(record)
                else:
                    candidate_errors.append({"ref":str(meta.get("ref") or ""),"error":error});all_errors.append({"candidate_key":candidate_key,"ref":str(meta.get("ref") or ""),"error":error})
            results[candidate_key]={
                "discovered_new_support_refs":sum(not bool(meta.get("already_reviewed")) for meta in row.get("rows") or [] if isinstance(meta,dict)),
                "primary_verified":len(candidate_records),
                "fulltext_verified":sum(len(str(record.get("fulltext_sha256") or ""))==64 for record in candidate_records),
                "empirical_supported":sum(bool(record.get("empirical_facts")) for record in candidate_records),
                "measured_failure_supported":sum(bool((record.get("typed_evidence") or {}).get("measured_failures")) for record in candidate_records),
                "direct_object_verified":sum(bool(record.get("direct_object_match")) for record in candidate_records),
                "pending_cache":len(candidate_errors),
                "errors":candidate_errors,
                "scientific_authority":False,
            }
    status="SHADOW_CANDIDATE_EVIDENCE_COMPLETE" if retrieval_complete and not all_errors else ("SHADOW_CANDIDATE_EVIDENCE_PARTIAL" if retrieval_complete else "SHADOW_CANDIDATE_EVIDENCE_BLOCKED_RETRIEVAL_INCOMPLETE")
    return {
        "schema_version":"1.0","generated_at":current.replace(microsecond=0).isoformat(),"status":status,
        "policy":{"scientific_authority":False,"shadow_only":True,"network_fetch_forbidden":True,"source_exposure_effect":False,"live_query_effect":False,"generator_called":False,"reviewer_called":False,"candidate_primary_verification_does_not_activate_lane":True,"support_purity_and_ownership_gates_still_required":True,"freshness_days":float(max_publication_age_days)},
        "summary":{"candidate_objects":len(results),"primary_verified":len(all_records),"fulltext_verified":sum(len(str(record.get("fulltext_sha256") or ""))==64 for record in all_records),"empirical_supported":sum(bool(record.get("empirical_facts")) for record in all_records),"measured_failure_supported":sum(bool((record.get("typed_evidence") or {}).get("measured_failures")) for record in all_records),"direct_object_verified":sum(bool(record.get("direct_object_match")) for record in all_records),"pending_cache":len(all_errors),"activation_authorized":0},
        "results":results,"records":all_records,"errors":all_errors,"scientific_authority":False,
    }


def public_scientific_object_candidate_evidence_summary(ledger: dict[str, Any]) -> dict[str, Any]:
    results={}
    for key,row in (ledger.get("results") or {}).items():
        if not isinstance(row,dict):
            continue
        results[str(key)]={
            "discovered_new_support_refs":int(row.get("discovered_new_support_refs") or 0),
            "primary_verified":int(row.get("primary_verified") or 0),
            "fulltext_verified":int(row.get("fulltext_verified") or 0),
            "empirical_supported":int(row.get("empirical_supported") or 0),
            "measured_failure_supported":int(row.get("measured_failure_supported") or 0),
            "direct_object_verified":int(row.get("direct_object_verified") or 0),
            "pending_cache":int(row.get("pending_cache") or 0),
            "error_count":len(row.get("errors") or []),
            "scientific_authority":False,
        }
    summary=ledger.get("summary") or {}
    return {
        "schema_version":"1.0",
        "status":str(ledger.get("status") or "NOT_RUN"),
        "policy":{
            "scientific_authority":False,
            "shadow_only":True,
            "network_fetch_forbidden":True,
            "source_exposure_effect":False,
            "live_query_effect":False,
            "candidate_primary_verification_does_not_activate_lane":True,
            "support_purity_and_ownership_gates_still_required":True,
        },
        "summary":{
            "candidate_objects":len(results),
            "primary_verified":int(summary.get("primary_verified") or 0),
            "fulltext_verified":int(summary.get("fulltext_verified") or 0),
            "empirical_supported":int(summary.get("empirical_supported") or 0),
            "measured_failure_supported":int(summary.get("measured_failure_supported") or 0),
            "direct_object_verified":int(summary.get("direct_object_verified") or 0),
            "pending_cache":int(summary.get("pending_cache") or 0),
            "activation_authorized":0,
        },
        "results":results,
        "scientific_authority":False,
    }


def candidate_extra_records_from_ledger(ledger: dict[str, Any]) -> dict[str,list[dict[str,Any]]]:
    out:dict[str,list[dict[str,Any]]]={}
    for row in ledger.get("records") or []:
        if not isinstance(row,dict) or row.get("primary_source_verified") is not True or row.get("scientific_authority") is not False:
            continue
        key=str(row.get("candidate_key") or "")
        if key: out.setdefault(key,[]).append(dict(row))
    return out


def load_scientific_object_candidate_evidence_ledger(*,storage:StorageSettings|None=None,path:Path|None=None)->dict[str,Any]:
    storage=storage or StorageSettings.from_env();source=path or storage.data_root/"paper-first-problem-discovery"/DEFAULT_LEDGER_NAME
    if not source.exists(): return {"schema_version":"1.0","status":"NOT_RUN","policy":{"scientific_authority":False},"summary":{"primary_verified":0,"activation_authorized":0},"results":{},"records":[],"errors":[],"scientific_authority":False}
    try: payload=json.loads(source.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError): return {"schema_version":"1.0","status":"STATE_UNREADABLE","policy":{"scientific_authority":False},"summary":{"primary_verified":0,"activation_authorized":0},"results":{},"records":[],"errors":[{"error":"state-unreadable"}],"scientific_authority":False}
    return payload if isinstance(payload,dict) else {"schema_version":"1.0","status":"STATE_INVALID","policy":{"scientific_authority":False},"summary":{"primary_verified":0,"activation_authorized":0},"results":{},"records":[],"errors":[{"error":"state-invalid"}],"scientific_authority":False}


def write_private_scientific_object_candidate_evidence_ledger(*,storage:StorageSettings|None=None,output_path:Path|None=None)->dict[str,Any]:
    storage=storage or StorageSettings.from_env();state=build_scientific_object_candidate_evidence_ledger(storage=storage);target=output_path or storage.data_root/"paper-first-problem-discovery"/DEFAULT_LEDGER_NAME;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");return state


if __name__=="__main__":
    state=write_private_scientific_object_candidate_evidence_ledger();print(json.dumps(state["summary"],ensure_ascii=False))
