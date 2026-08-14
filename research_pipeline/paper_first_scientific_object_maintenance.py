from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .config import StorageSettings
from .paper_first_primary_evidence import DEFAULT_JSON as PRIMARY_JSON, load_primary_evidence_state
from .paper_first_problem_generator import DEFAULT_JSON as GENERATOR_JSON
from .paper_first_problem_gate_queue import DEFAULT_JSON as QUEUE_JSON
from .paper_first_scientific_object_candidate_evidence import write_private_scientific_object_candidate_evidence_ledger
from .paper_first_scientific_object_ontology import write_private_scientific_object_audit
from .paper_first_scientific_object_retrieval_audit import (
    load_private_shadow_scientific_object_retrieval_audit,
    write_private_shadow_scientific_object_retrieval_audit,
)

Writer = Callable[..., dict[str, Any]]
StateLoader = Callable[..., dict[str, Any]]
ShaProvider = Callable[[], dict[str, str | None]]


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_iso(value: str) -> datetime | None:
    raw=str(value or "").strip()
    if not raw:
        return None
    try:
        parsed=datetime.fromisoformat(raw.replace("Z","+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed=parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _file_sha(path: Path) -> str | None:
    if not path.exists():
        return None
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def _canonical_shas() -> dict[str,str|None]:
    return {"primary":_file_sha(PRIMARY_JSON),"generator":_file_sha(GENERATOR_JSON),"queue":_file_sha(QUEUE_JSON)}


def _call(writer: Writer, storage: StorageSettings) -> dict[str, Any]:
    return writer(storage=storage)


def run_shadow_scientific_object_maintenance(
    *,
    storage: StorageSettings | None = None,
    primary_state: dict[str, Any] | None = None,
    now: datetime | None = None,
    minimum_complete_audit_age_days: float = 7.0,
    retrieval_writer: Writer = write_private_shadow_scientific_object_retrieval_audit,
    candidate_writer: Writer = write_private_scientific_object_candidate_evidence_ledger,
    ontology_writer: Writer = write_private_scientific_object_audit,
    retrieval_state_loader: StateLoader = load_private_shadow_scientific_object_retrieval_audit,
    canonical_sha_provider: ShaProvider = _canonical_shas,
) -> dict[str, Any]:
    """Run a bounded shadow object-recall maintenance pass after live coverage closes.

    Network retrieval is permitted only for the shadow retrieval writer and at
    most once per completed audit age window. Candidate primary verification
    and ontology recomputation are private/offline. Canonical Primary,
    Generator, and Queue files are byte-hash guarded before/after the pass.
    """
    storage=storage or StorageSettings.from_env();current=(now or _now()).astimezone(timezone.utc)
    primary=primary_state or load_primary_evidence_state();summary=primary.get("summary") or {}
    before=canonical_sha_provider()
    base={
        "schema_version":"1.0","generated_at":current.replace(microsecond=0).isoformat(),
        "policy":{"scientific_authority":False,"shadow_only":True,"runs_after_live_discovery_only":True,"live_coverage_must_be_exhausted":True,"live_retrieval_must_be_complete":True,"carrier_probe_must_be_complete":True,"completed_retrieval_audit_minimum_age_days":float(minimum_complete_audit_age_days),"shared_arxiv_rate_limit_cooldown":True,"canonical_primary_generator_queue_must_remain_byte_identical":True,"generator_called":False,"reviewer_called":False,"automatic_lane_activation":False},
        "live_primary":{"status":primary.get("status"),"source_retrieval_complete":summary.get("source_retrieval_complete"),"source_coverage_exhausted":summary.get("source_coverage_exhausted"),"carrier_probe_complete":summary.get("carrier_probe_complete",True)},
        "steps":[],"generator_called":False,"reviewer_called":False,"scientific_authority":False,
    }
    eligible=bool(primary.get("status")=="READY" and summary.get("source_retrieval_complete") is True and summary.get("source_coverage_exhausted") is True and summary.get("carrier_probe_complete",True) is True)
    if not eligible:
        base.update({"status":"SKIPPED_LIVE_SOURCE_COVERAGE_NOT_CLOSED","canonical_public_state_unchanged":canonical_sha_provider()==before})
        return base

    previous=retrieval_state_loader(storage=storage)
    previous_time=_parse_iso(str(previous.get("generated_at") or ""))
    previous_age=None if previous_time is None else max(0.0,(current-previous_time).total_seconds()/86400.0)
    recent_complete=bool(previous.get("status")=="SHADOW_OBJECT_RETRIEVAL_AUDIT_COMPLETE" and previous_age is not None and previous_age<float(minimum_complete_audit_age_days))
    if recent_complete:
        retrieval=previous
        base["steps"].append({"step":"shadow-object-retrieval","status":"SKIPPED_RECENT_COMPLETE_AUDIT","age_days":round(float(previous_age),4),"scientific_authority":False})
    else:
        retrieval=_call(retrieval_writer,storage)
        base["steps"].append({"step":"shadow-object-retrieval","status":retrieval.get("status"),"scientific_authority":False})

    candidate=_call(candidate_writer,storage)
    ontology=_call(ontology_writer,storage)
    base["steps"].append({"step":"shadow-candidate-primary-verification","status":candidate.get("status"),"summary":dict(candidate.get("summary") or {}),"scientific_authority":False})
    base["steps"].append({"step":"shadow-object-ontology","status":ontology.get("status"),"summary":dict(ontology.get("summary") or {}),"scientific_authority":False})
    after=canonical_sha_provider();unchanged=after==before
    if not unchanged:
        raise RuntimeError("shadow scientific-object maintenance mutated canonical Primary/Generator/Queue")
    status="SHADOW_OBJECT_MAINTENANCE_COMPLETE" if retrieval.get("status")=="SHADOW_OBJECT_RETRIEVAL_AUDIT_COMPLETE" else "SHADOW_OBJECT_MAINTENANCE_RETRIEVAL_INCOMPLETE"
    base.update({"status":status,"retrieval_audit_status":retrieval.get("status"),"candidate_evidence_status":candidate.get("status"),"ontology_status":ontology.get("status"),"canonical_public_state_unchanged":True})
    run_dir=storage.run_dir/"paper-first-object-maintenance";run_dir.mkdir(parents=True,exist_ok=True);target=run_dir/f"object-maintenance-{current.strftime('%Y%m%dT%H%M%SZ')}.json";target.write_text(json.dumps(base,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");base["artifact_path"]=str(target)
    return base


if __name__=="__main__":
    print(json.dumps(run_shadow_scientific_object_maintenance(),ensure_ascii=False,indent=2))
