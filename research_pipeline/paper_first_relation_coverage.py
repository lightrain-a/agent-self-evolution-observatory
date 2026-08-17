from __future__ import annotations

import hashlib
import json
from itertools import combinations
from typing import Any


def portable_review_receipts(generator_state: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in ((generator_state.get("saturation_memory") or {}).get("portable_review_receipts") or []):
        if not isinstance(row, dict) or row.get("scientific_authority") is not False:
            continue
        refs = sorted({str(ref).strip() for ref in row.get("source_refs") or [] if str(ref).strip().startswith("arXiv:")})
        run_id = str(row.get("run_id") or "").strip()
        if run_id and len(refs) >= 2:
            rows.append({"run_id": run_id, "source_refs": refs, "scientific_authority": False})
    return rows


def source_universe_digest(receipts: list[dict[str, Any]]) -> str:
    """Content-address the reviewed source set independently of scheduler history."""
    source_refs=sorted({ref for row in receipts for ref in row.get("source_refs") or []})
    return hashlib.sha256(json.dumps(source_refs,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()


def relation_universe_digest(receipts: list[dict[str, Any]]) -> str:
    # The relation universe is defined by which sources exist and which source
    # pairs have ever co-occurred. Run IDs and repeated identical receipts are
    # scheduler history, not a change in the relation search space.
    source_refs = sorted({ref for row in receipts for ref in row.get("source_refs") or []})
    pairs = sorted(coobserved_pairs(receipts))
    material = {"source_refs": source_refs, "coobserved_source_pairs": [list(pair) for pair in pairs]}
    return hashlib.sha256(json.dumps(material, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def source_pair_coverage(receipts: list[dict[str, Any]]) -> dict[str, Any]:
    exposure: dict[str, int] = {}
    coobserved: set[tuple[str, str]] = set()
    for row in receipts:
        refs = sorted(set(row.get("source_refs") or []))
        for ref in refs:
            exposure[ref] = exposure.get(ref, 0) + 1
        coobserved.update(combinations(refs, 2))
    refs = sorted(exposure)
    possible = len(refs) * (len(refs) - 1) // 2
    neighbors = {ref: set() for ref in refs}
    for a, b in coobserved:
        neighbors[a].add(b)
        neighbors[b].add(a)
    degrees = sorted(len(neighbors[ref]) for ref in refs)
    median = degrees[(len(degrees) - 1) // 2] if degrees else 0
    complete = bool(possible == 0 or len(coobserved) == possible)
    return {
        "receipt_runs": len(receipts),
        "reviewed_receipt_sources": len(refs),
        "possible_source_pairs": possible,
        "coobserved_source_pairs": len(coobserved),
        "pair_coverage_fraction": round(len(coobserved) / possible, 4) if possible else 1.0,
        "single_exposure_sources": sum(count == 1 for count in exposure.values()),
        "minimum_coobserved_neighbors": degrees[0] if degrees else 0,
        "median_coobserved_neighbors": median,
        "maximum_coobserved_neighbors": degrees[-1] if degrees else 0,
        "pairwise_coobservation_complete": complete,
        "relation_blind_spot_detected": bool(len(refs) >= 2 and not complete),
        "relation_universe_digest": relation_universe_digest(receipts),
        "search_control_only": True,
        "scientific_authority": False,
    }


def relation_recall_freshness(generator_state: dict[str, Any], relation_state: dict[str, Any]) -> dict[str, Any]:
    """Compare the current semantic source universe with the last completed scan.

    Portable review receipts are scheduler metadata.  Their co-observation topology
    may change when the same reviewed sources are regrouped into later tranches, but
    the global relation model already searched all supplied source cards.  Therefore
    a topology-only digest drift is recorded deterministically and never triggers a
    redundant model rescan.  A changed source set (or an unreconstructable historical
    boundary) remains stale/unknown exactly as before.
    """
    receipts=portable_review_receipts(generator_state)
    current=source_pair_coverage(receipts)
    last=relation_state.get("last_completed_scan") or {}
    last_summary=last.get("summary") or relation_state.get("summary") or {}
    last_coverage=last.get("relation_coverage") or {}
    last_digest=str(last.get("relation_universe_digest") or last_summary.get("relation_universe_digest") or "")
    current_digest=str(current.get("relation_universe_digest") or "")
    current_source_digest=source_universe_digest(receipts) if receipts else ""
    has_completed_scan=bool(last_digest)
    raw_digest_changed=bool(has_completed_scan and current_digest and current_digest!=last_digest)
    cutoff=str(last.get("run_id") or "").strip()
    source_boundary_reconstructable=False;last_source_digest=""
    if has_completed_scan and cutoff:
        old_receipts=[row for row in receipts if str(row.get("run_id") or "")<=cutoff]
        if old_receipts and relation_universe_digest(old_receipts)==last_digest:
            source_boundary_reconstructable=True
            last_source_digest=source_universe_digest(old_receipts)
    scheduler_topology_only_drift=bool(raw_digest_changed and source_boundary_reconstructable and current_source_digest==last_source_digest)
    semantic_stale=bool(raw_digest_changed and not scheduler_topology_only_drift)
    if not has_completed_scan:
        status="NO_COMPLETED_RELATION_SCAN"
    elif semantic_stale:
        status="STALE_RELATION_UNIVERSE"
    else:
        status="CURRENT_RELATION_UNIVERSE"
    current_blind_spot=bool(current.get("relation_blind_spot_detected"))
    return {
        "schema_version":"1.1",
        "status":status,
        "policy":{
            "scientific_authority":False,
            "deterministic_digest_comparison_only":True,
            "stale_scan_is_historical_not_current_negative_evidence":True,
            "stale_scan_cannot_reopen_focused_generator":True,
            "model_scan_deferred_is_not_relation_exhaustion":True,
            "portable_review_receipts_are_scheduler_metadata_only":True,
            "scheduler_topology_only_drift_does_not_require_model_rescan":True,
            "source_set_change_or_unreconstructable_boundary_remains_stale":True,
        },
        "summary":{
            "current_reviewed_sources":int(current.get("reviewed_receipt_sources") or 0),
            "last_scanned_sources":int(last_coverage.get("reviewed_receipt_sources") or last_summary.get("reviewed_receipt_sources") or 0),
            "current_possible_pairs":int(current.get("possible_source_pairs") or 0),
            "current_coobserved_pairs":int(current.get("coobserved_source_pairs") or 0),
            "current_pair_coverage_fraction":float(current.get("pair_coverage_fraction") or 0.0),
            "last_pair_coverage_fraction":float(last_coverage.get("pair_coverage_fraction") or last_summary.get("pair_coverage_fraction") or 0.0),
            "current_relation_blind_spot":current_blind_spot,
            "raw_topology_digest_changed":raw_digest_changed,
            "source_boundary_reconstructable":source_boundary_reconstructable,
            "scheduler_topology_only_drift":scheduler_topology_only_drift,
            "universe_stale":semantic_stale,
            "current_not_reduced_unknown":semantic_stale or not has_completed_scan,
            "model_scan_deferred":bool(semantic_stale and current_blind_spot),
            "focused_problem_generator_reopen_allowed":False if semantic_stale or not has_completed_scan else bool(last_summary.get("focused_problem_generator_reopen_required")),
        },
        "current_relation_universe_digest":current_digest,
        "last_scanned_relation_universe_digest":last_digest,
        "current_source_universe_digest":current_source_digest,
        "last_scanned_source_universe_digest":last_source_digest,
        "scientific_authority":False,
    }


def coobserved_pairs(receipts: list[dict[str, Any]]) -> set[tuple[str, str]]:
    result: set[tuple[str, str]] = set()
    for row in receipts:
        result.update(combinations(sorted(set(row.get("source_refs") or [])), 2))
    return result
