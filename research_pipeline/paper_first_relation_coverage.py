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


def relation_universe_digest(receipts: list[dict[str, Any]]) -> str:
    material = [{"run_id": row["run_id"], "source_refs": row["source_refs"]} for row in receipts]
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


def coobserved_pairs(receipts: list[dict[str, Any]]) -> set[tuple[str, str]]:
    result: set[tuple[str, str]] = set()
    for row in receipts:
        result.update(combinations(sorted(set(row.get("source_refs") or [])), 2))
    return result
