from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path
from typing import Any

from .config import StorageSettings
from .paper_first_global_relation_recall import load_global_relation_recall_state
from .paper_first_problem_generator import load_problem_generator_state
from .paper_first_relation_coverage import portable_review_receipts, relation_universe_digest
from .paper_first_scientific_object_ontology import reviewed_primary_cache_records


def _refs(receipts: list[dict[str, Any]]) -> set[str]:
    return {str(ref) for row in receipts for ref in row.get("source_refs") or [] if str(ref).startswith("arXiv:")}


def _evidence_flags(row: dict[str, Any]) -> dict[str, bool]:
    typed=row.get("typed_evidence") or {}
    return {
        "empirical": bool(row.get("empirical_facts")),
        "assumption": bool(typed.get("operational_assumptions")),
        "failure": bool(typed.get("measured_failures")),
        "boundary": bool(typed.get("boundary_observations")),
    }


def _cross_pair_slots(left: set[str], right: set[str]) -> int:
    # Count distinct unordered pairs with one endpoint in each set. If a ref is
    # in both sets, never count a self-pair and never double count.
    return len({tuple(sorted((a,b))) for a in left for b in right if a!=b})


def build_relation_delta_preflight(
    *,
    storage: StorageSettings | None = None,
    generator_state: dict[str, Any] | None = None,
    relation_state: dict[str, Any] | None = None,
    cache_records: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Deterministically characterize evidence added since the last relation scan.

    This layer never infers lane validity. Pair-slot counts are only upper-bound
    opportunities for later semantic relation review: shared operationalization,
    common failure object, incompatibility, and anomalous-boundary semantics are
    deliberately not inferred here.
    """
    storage=storage or StorageSettings.from_env()
    generator=generator_state if generator_state is not None else load_problem_generator_state()
    relation=relation_state if relation_state is not None else load_global_relation_recall_state()
    receipts=portable_review_receipts(generator)
    last_scan=relation.get("last_completed_scan") or {}
    cutoff=str(last_scan.get("run_id") or "")
    last_digest=str(last_scan.get("relation_universe_digest") or "")
    current_digest=relation_universe_digest(receipts)
    base={
        "schema_version":"1.0",
        "status":"NOT_RUN",
        "policy":{
            "scientific_authority":False,
            "deterministic_typed_evidence_delta_only":True,
            "pair_slots_are_not_lane_valid_pairs":True,
            "shared_operationalization_is_not_inferred":True,
            "common_failure_object_is_not_inferred":True,
            "incompatibility_is_not_inferred":True,
            "boundary_anomaly_semantics_are_not_inferred":True,
            "cannot_reopen_generator":True,
            "cannot_authorize_relation_model_scan":True,
            "cannot_authorize_problem_gate":True,
        },
        "scientific_authority":False,
    }
    if not cutoff or not last_digest:
        base.update({"status":"NO_COMPLETED_RELATION_SCAN","summary":{"current_receipt_runs":len(receipts),"new_reviewed_sources":0,"model_scan_authorized":False,"focused_generator_reopen_authorized":False}})
        return base
    old_receipts=[row for row in receipts if str(row.get("run_id") or "")<=cutoff]
    new_receipts=[row for row in receipts if str(row.get("run_id") or "")>cutoff]
    reconstructed_digest=relation_universe_digest(old_receipts)
    if reconstructed_digest!=last_digest:
        base.update({"status":"HOLD_SCAN_BOUNDARY_NOT_RECONSTRUCTABLE","summary":{"current_receipt_runs":len(receipts),"old_receipt_runs":len(old_receipts),"new_receipt_runs":len(new_receipts),"new_reviewed_sources":0,"model_scan_authorized":False,"focused_generator_reopen_authorized":False},"last_scanned_relation_universe_digest":last_digest,"reconstructed_last_relation_universe_digest":reconstructed_digest,"current_relation_universe_digest":current_digest})
        return base
    old_refs=_refs(old_receipts);current_refs=_refs(receipts);new_refs=current_refs-old_refs
    rows=cache_records if cache_records is not None else reviewed_primary_cache_records(storage,reviewed_refs=current_refs)
    registry={str(row.get("ref") or ""):row for row in rows if str(row.get("ref") or "") in current_refs}
    missing=current_refs-set(registry)
    if missing:
        base.update({"status":"HOLD_RELATION_DELTA_CACHE_INCOMPLETE","summary":{"current_receipt_runs":len(receipts),"old_receipt_runs":len(old_receipts),"new_receipt_runs":len(new_receipts),"old_reviewed_sources":len(old_refs),"current_reviewed_sources":len(current_refs),"new_reviewed_sources":len(new_refs),"cache_missing_sources":len(missing),"model_scan_authorized":False,"focused_generator_reopen_authorized":False},"last_scanned_relation_universe_digest":last_digest,"reconstructed_last_relation_universe_digest":reconstructed_digest,"current_relation_universe_digest":current_digest})
        return base
    flags={ref:_evidence_flags(registry[ref]) for ref in current_refs}
    sets={kind:{ref for ref,v in flags.items() if v[kind]} for kind in ("empirical","assumption","failure","boundary")}
    new_sets={kind:sets[kind]&new_refs for kind in sets}
    old_sets={kind:sets[kind]&old_refs for kind in sets}
    # These are combinatorial search slots only. They intentionally do not
    # assert a lane contract, common measurement, or semantic relation.
    slots={
        "empirical_empirical_slots_touching_new": len({pair for pair in combinations(sorted(sets["empirical"]),2) if pair[0] in new_refs or pair[1] in new_refs}),
        "failure_failure_slots_touching_new": len({pair for pair in combinations(sorted(sets["failure"]),2) if pair[0] in new_refs or pair[1] in new_refs}),
        "assumption_failure_slots_touching_new": len({tuple(sorted((a,b))) for a in sets["assumption"] for b in sets["failure"] if a!=b and (a in new_refs or b in new_refs)}),
        "boundary_empirical_slots_touching_new": len({tuple(sorted((a,b))) for a in sets["boundary"] for b in sets["empirical"] if a!=b and (a in new_refs or b in new_refs)}),
    }
    summary={
        "old_receipt_runs":len(old_receipts),
        "new_receipt_runs":len(new_receipts),
        "old_reviewed_sources":len(old_refs),
        "current_reviewed_sources":len(current_refs),
        "new_reviewed_sources":len(new_refs),
        "new_empirical_sources":len(new_sets["empirical"]),
        "new_assumption_sources":len(new_sets["assumption"]),
        "new_failure_sources":len(new_sets["failure"]),
        "new_boundary_sources":len(new_sets["boundary"]),
        "assumption_break_has_new_assumption_endpoint":bool(new_sets["assumption"]),
        "convergent_failure_has_new_failure_evidence":len(new_sets["failure"])>=1,
        "unexplained_boundary_has_new_boundary_evidence":len(new_sets["boundary"])>=1,
        "contradiction_has_new_empirical_evidence":len(new_sets["empirical"])>=1,
        "cache_missing_sources":0,
        "model_scan_authorized":False,
        "focused_generator_reopen_authorized":False,
    }
    base.update({
        "status":"RELATION_DELTA_TYPED_PREFLIGHT_COMPLETE",
        "summary":summary,
        "pair_slots":slots,
        "interpretation":{
            "assumption_break":"NO_NEW_ASSUMPTION_ENDPOINT" if not new_sets["assumption"] else "NEW_ASSUMPTION_EVIDENCE_PRESENT",
            "convergent_failure":"NEW_FAILURE_EVIDENCE_PRESENT_LANE_VALIDITY_UNKNOWN" if new_sets["failure"] else "NO_NEW_FAILURE_EVIDENCE",
            "unexplained_boundary":"NEW_BOUNDARY_EVIDENCE_PRESENT_LANE_VALIDITY_UNKNOWN" if new_sets["boundary"] else "NO_NEW_BOUNDARY_EVIDENCE",
            "contradiction":"NEW_EMPIRICAL_EVIDENCE_PRESENT_LANE_VALIDITY_UNKNOWN" if new_sets["empirical"] else "NO_NEW_EMPIRICAL_EVIDENCE",
        },
        "last_scanned_relation_universe_digest":last_digest,
        "reconstructed_last_relation_universe_digest":reconstructed_digest,
        "current_relation_universe_digest":current_digest,
        "scientific_authority":False,
    })
    return base


def _default_path(storage: StorageSettings) -> Path:
    return storage.data_root/"paper-first-problem-discovery"/"global-relation-recall"/"relation-delta-preflight.json"


def load_private_relation_delta_preflight(*,storage:StorageSettings|None=None,path:Path|None=None)->dict[str,Any]:
    storage=storage or StorageSettings.from_env();target=path or _default_path(storage)
    try:
        payload=json.loads(target.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError):
        return {"schema_version":"1.0","status":"NOT_RUN","policy":{"scientific_authority":False},"summary":{},"pair_slots":{},"interpretation":{},"scientific_authority":False}
    return payload if isinstance(payload,dict) else {"schema_version":"1.0","status":"STATE_INVALID","policy":{"scientific_authority":False},"summary":{},"pair_slots":{},"interpretation":{},"scientific_authority":False}


def public_relation_delta_preflight_summary(state:dict[str,Any])->dict[str,Any]:
    summary=dict(state.get("summary") or {});slots=dict(state.get("pair_slots") or {});interpretation=dict(state.get("interpretation") or {})
    allowed_summary={
        "old_receipt_runs","new_receipt_runs","old_reviewed_sources","current_reviewed_sources","new_reviewed_sources",
        "new_empirical_sources","new_assumption_sources","new_failure_sources","new_boundary_sources",
        "assumption_break_has_new_assumption_endpoint","convergent_failure_has_new_failure_evidence",
        "unexplained_boundary_has_new_boundary_evidence","contradiction_has_new_empirical_evidence",
        "cache_missing_sources","model_scan_authorized","focused_generator_reopen_authorized",
    }
    allowed_slots={"empirical_empirical_slots_touching_new","failure_failure_slots_touching_new","assumption_failure_slots_touching_new","boundary_empirical_slots_touching_new"}
    allowed_interpretation={"assumption_break","convergent_failure","unexplained_boundary","contradiction"}
    return {
        "schema_version":"1.0","status":str(state.get("status") or "NOT_RUN"),
        "policy":{"scientific_authority":False,"deterministic_typed_evidence_delta_only":True,"pair_slots_are_not_lane_valid_pairs":True,"cannot_reopen_generator":True,"cannot_authorize_relation_model_scan":True,"cannot_authorize_problem_gate":True},
        "summary":{key:summary[key] for key in allowed_summary if key in summary},
        "pair_slots":{key:int(slots.get(key) or 0) for key in allowed_slots if key in slots},
        "interpretation":{key:str(interpretation.get(key) or "") for key in allowed_interpretation if key in interpretation},
        "scientific_authority":False,
    }


def write_private_relation_delta_preflight(*,storage:StorageSettings|None=None,output_path:Path|None=None)->dict[str,Any]:
    storage=storage or StorageSettings.from_env();state=build_relation_delta_preflight(storage=storage)
    target=output_path or _default_path(storage)
    target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return state


if __name__=="__main__":
    print(json.dumps(write_private_relation_delta_preflight(),ensure_ascii=False,indent=2))
