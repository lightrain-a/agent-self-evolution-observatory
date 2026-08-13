from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT, StorageSettings
from .paper_first_primary_evidence import (
    _paper_lane_keys,
    _source_exposure_state,
    extract_empirical_fact_candidates,
    extract_typed_evidence_candidates,
    parse_arxiv_page,
)

DEFAULT_CONFIG = PROJECT_ROOT / "research_pipeline" / "paper_first_scientific_object_candidates.json"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_scientific_object_config(path: Path = DEFAULT_CONFIG) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload.get("candidates"), dict) or not isinstance(payload.get("support_gate"), dict):
        raise ValueError("scientific-object-config-invalid")
    return payload


def current_lane_axes(lane_keys: list[str] | tuple[str, ...], *, config: dict[str, Any] | None = None) -> dict[str, list[str]]:
    config = config or load_scientific_object_config()
    axes = config.get("current_axes") or {}
    by_axis = {name: set(str(key) for key in axes.get(name) or []) for name in ("object", "context", "property")}
    lanes = [str(key) for key in lane_keys]
    known = set().union(*by_axis.values())
    return {
        "object": [key for key in lanes if key in by_axis["object"]],
        "context": [key for key in lanes if key in by_axis["context"]],
        "property": [key for key in lanes if key in by_axis["property"]],
        "unknown": [key for key in lanes if key not in known],
    }


def _matches_candidate(record: dict[str, Any], spec: dict[str, Any]) -> bool:
    text = f"{record.get('title', '')} {record.get('abstract', '')}".lower()
    positive = tuple(str(value).lower() for value in spec.get("positive_phrases") or [])
    negative = tuple(str(value).lower() for value in spec.get("negative_phrases") or [])
    return bool(positive and any(value in text for value in positive) and not any(value in text for value in negative))


def audit_candidate_object(records: list[dict[str, Any]], candidate_key: str, *, config: dict[str, Any] | None = None) -> dict[str, Any]:
    config = config or load_scientific_object_config()
    spec = config["candidates"][candidate_key]
    gate = config["support_gate"]
    matched = [row for row in records if row.get("primary_source_verified") is True and _matches_candidate(row, spec)]
    collisions: Counter[str] = Counter()
    for row in matched:
        collisions.update(str(key) for key in row.get("lane_keys") or [] if str(key))
    reviewed = len(matched)
    empirical = sum(bool(row.get("empirical_facts")) for row in matched)
    failures = sum(bool((row.get("typed_evidence") or {}).get("measured_failures")) for row in matched)
    boundaries = sum(bool((row.get("typed_evidence") or {}).get("boundary_observations")) for row in matched)
    max_collision = max(collisions.values(), default=0) / reviewed if reviewed else 0.0
    gate_pass = bool(
        reviewed >= int(gate["minimum_reviewed_primary_refs"])
        and empirical >= int(gate["minimum_empirical_fact_supported_refs"])
        and failures >= int(gate["minimum_measured_failure_supported_refs"])
        and max_collision <= float(gate["maximum_single_existing_lane_collision"])
    )
    purity = str(spec.get("object_purity") or "review-required")
    status = "WATCH_INSUFFICIENT_PRIMARY_SUPPORT"
    if gate_pass:
        status = "SHADOW_READY_FOR_PREREGISTRATION" if purity == "clear" else "HOLD_OBJECT_PURITY_REVIEW"
    refs = sorted(str(row.get("ref") or "") for row in matched)
    return {
        "candidate_key": candidate_key,
        "scientific_object": spec["scientific_object"],
        "status": status,
        "object_purity": purity,
        "support_gate": dict(gate),
        "observed": {
            "reviewed_primary_refs": reviewed,
            "empirical_fact_supported_refs": empirical,
            "measured_failure_supported_refs": failures,
            "boundary_supported_refs": boundaries,
            "current_lane_collision_counts": dict(sorted(collisions.items())),
            "maximum_single_existing_lane_collision": round(max_collision, 4),
            "distinct_current_lanes": len(collisions),
        },
        "support_refs": refs,
        "support_ref_digest": hashlib.sha256("\n".join(refs).encode()).hexdigest(),
        "evidence_gate_pass": gate_pass,
        "activation_authorized": False,
        "scientific_authority": False,
    }


def audit_scientific_object_ontology(records: list[dict[str, Any]], *, config: dict[str, Any] | None = None) -> dict[str, Any]:
    config = config or load_scientific_object_config()
    candidates = {key: audit_candidate_object(records, key, config=config) for key in config["candidates"]}
    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "status": "SHADOW_AUDIT_ONLY",
        "policy": {
            "scientific_authority": False,
            "selector_changed": False,
            "prompt_changed": False,
            "generator_call_authorized": False,
            "reviewer_call_authorized": False,
            "automatic_lane_activation": False,
            "lane_preregistration_required_before_activation": True,
            "freshness_and_relevance_must_remain_unchanged": True,
        },
        "current_taxonomy": {
            "axes": config.get("current_axes") or {},
            "finding": "mixed-axis taxonomy: current coverage combines evolving objects, deployment contexts, and reliability properties",
            "implication": "current lane coverage is a breadth-floor fact, not evidence of scientific-object completeness",
        },
        "support_gate": dict(config["support_gate"]),
        "summary": {
            "reviewed_primary_records": len(records),
            "candidate_objects": len(candidates),
            "shadow_ready_for_preregistration": sorted(key for key, row in candidates.items() if row["status"] == "SHADOW_READY_FOR_PREREGISTRATION"),
            "hold_object_purity_review": sorted(key for key, row in candidates.items() if row["status"] == "HOLD_OBJECT_PURITY_REVIEW"),
            "activation_authorized": 0,
        },
        "candidates": candidates,
    }


def reviewed_primary_cache_records(storage: StorageSettings | None = None) -> list[dict[str, Any]]:
    storage = storage or StorageSettings.from_env()
    exposure, _, _, _ = _source_exposure_state(storage)
    source_root = storage.data_root / "paper-first-problem-discovery" / "primary-sources"
    rows: list[dict[str, Any]] = []
    for primary_path in sorted(source_root.glob("arxiv-*.html")):
        if primary_path.name.startswith("arxiv-full-"):
            continue
        match = re.match(r"arxiv-(\d{4}\.\d+)-", primary_path.name)
        if not match or f"arXiv:{match.group(1)}" not in exposure:
            continue
        parsed = parse_arxiv_page(primary_path.read_text(encoding="utf-8", errors="replace"))
        probe = {"title": parsed["title"], "abstract": parsed["abstract"]}
        full_paths = sorted(source_root.glob(f"arxiv-full-{match.group(1)}-*.html"))
        fulltext = full_paths[-1].read_text(encoding="utf-8", errors="replace") if full_paths else ""
        rows.append({
            "ref": f"arXiv:{match.group(1)}",
            "title": parsed["title"],
            "abstract": parsed["abstract"],
            "primary_source_verified": True,
            "lane_keys": list(_paper_lane_keys(probe)),
            "empirical_facts": extract_empirical_fact_candidates(fulltext) if fulltext else [],
            "typed_evidence": extract_typed_evidence_candidates(fulltext) if fulltext else {"operational_assumptions": [], "measured_failures": [], "boundary_observations": []},
        })
    return rows


def write_private_scientific_object_audit(*, storage: StorageSettings | None = None, output_path: Path | None = None) -> dict[str, Any]:
    storage = storage or StorageSettings.from_env()
    state = audit_scientific_object_ontology(reviewed_primary_cache_records(storage))
    target = output_path or storage.data_root / "paper-first-problem-discovery" / "scientific-object-shadow-audit-v2.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return state


if __name__ == "__main__":
    print(json.dumps(write_private_scientific_object_audit()["summary"], ensure_ascii=False))
