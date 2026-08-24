from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

SCHEMA_VERSION = "1.0"

POLICY: dict[str, Any] = {
    "literature_monitoring_produces_structured_delta_not_research_item": True,
    "deep_literature_review_is_routed_only_when_collision_reopen_or_decisive_baseline_requires_it": True,
    "scientific_object_matrix_is_generation_and_collision_surface_not_novelty_authority": True,
    "proximity_agent_finds_nearest_known_objects_but_cannot_decide_novelty": True,
    "analysis_ensemble_is_used_only_when_researcher_degrees_of_freedom_exist": True,
    "deterministic_metrics_do_not_receive_multi_agent_ensemble_by_default": True,
    "meta_review_explains_disagreement_instead_of_majority_voting": True,
    "all_reasoning_components_have_zero_scientific_and_execution_authority": True,
}

REQUIRED_DELTA_FIELDS = (
    "scientific_object", "failure_mode", "intervention", "substrate", "observable", "strongest_baseline", "key_claim", "evidence_type",
)


def build_literature_delta(record: dict[str, Any]) -> dict[str, Any]:
    delta = {
        "schema_version": SCHEMA_VERSION,
        "source_ref": str(record.get("source_ref") or record.get("ref") or ""),
        "scientific_object": str(record.get("scientific_object") or ""),
        "failure_mode": str(record.get("failure_mode") or ""),
        "intervention": str(record.get("intervention") or ""),
        "substrate": str(record.get("substrate") or ""),
        "observable": str(record.get("observable") or ""),
        "strongest_baseline": str(record.get("strongest_baseline") or ""),
        "key_claim": str(record.get("key_claim") or ""),
        "evidence_type": str(record.get("evidence_type") or ""),
        "local_collision": str(record.get("local_collision") or ""),
        "reopen_target": str(record.get("reopen_target") or ""),
        "implementation_decisive": record.get("implementation_decisive") is True,
        "decisive_baseline": record.get("decisive_baseline") is True,
        "scientific_authority": False,
        "research_item_authority": False,
    }
    missing = [key for key in REQUIRED_DELTA_FIELDS if not str(delta.get(key) or "").strip()]
    delta["status"] = "DELTA_COMPLETE" if not missing else "DELTA_INCOMPLETE"
    delta["missing_fields"] = missing
    return delta


def route_literature_depth(delta: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    if str(delta.get("local_collision") or "").strip(): reasons.append("local-collision")
    if str(delta.get("reopen_target") or "").strip(): reasons.append("reopen-target")
    if delta.get("decisive_baseline") is True: reasons.append("decisive-baseline")
    if delta.get("implementation_decisive") is True: reasons.append("implementation-decisive")
    mode = "DEEP_REVIEW" if reasons else "FAST_SCAN"
    return {"schema_version": SCHEMA_VERSION, "source_ref": delta.get("source_ref"), "mode": mode, "reasons": reasons, "scientific_authority": False}


def build_scientific_object_matrix(deltas: Iterable[dict[str, Any]]) -> dict[str, Any]:
    rows = []
    for delta in deltas:
        if not isinstance(delta, dict) or delta.get("status") != "DELTA_COMPLETE":
            continue
        rows.append({
            "source_ref": delta.get("source_ref"),
            "failure_mode": delta.get("failure_mode"),
            "intervention_surface": delta.get("intervention"),
            "substrate": delta.get("substrate"),
            "observable": delta.get("observable"),
            "strongest_reduction": delta.get("strongest_baseline"),
            "local_collision": delta.get("local_collision"),
            "scientific_authority": False,
        })
    signatures = Counter((str(r["failure_mode"]), str(r["intervention_surface"]), str(r["substrate"]), str(r["observable"]), str(r["strongest_reduction"])) for r in rows)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "MATRIX_COMPILED",
        "rows": rows,
        "summary": {"rows": len(rows), "unique_signatures": len(signatures), "duplicate_signatures": sum(max(0, n - 1) for n in signatures.values())},
        "novelty_authority": False,
        "scientific_authority": False,
    }


def build_proximity_projection(candidate_id: str, references: Iterable[dict[str, Any]]) -> dict[str, Any]:
    rows = []
    for ref in references:
        if not isinstance(ref, dict): continue
        distance = ref.get("distance")
        if not isinstance(distance, (int, float)): continue
        rows.append({
            "ref": str(ref.get("ref") or ""), "object_type": str(ref.get("object_type") or "unknown"),
            "distance": float(distance), "basis": str(ref.get("basis") or "precomputed/provenance-audited distance"),
        })
    rows.sort(key=lambda r: (r["distance"], r["ref"]))
    return {
        "schema_version": SCHEMA_VERSION,
        "candidate_id": str(candidate_id),
        "nearest": rows[:5],
        "nearest_prior_work": next((r for r in rows if r["object_type"] == "prior-work"), None),
        "nearest_local_research_item": next((r for r in rows if r["object_type"] == "research-item"), None),
        "nearest_failure_asset": next((r for r in rows if r["object_type"] == "failure-asset"), None),
        "nearest_stop_branch": next((r for r in rows if r["object_type"] == "stop-branch"), None),
        "novelty_verdict": "NOT_AUTHORIZED",
        "scientific_authority": False,
    }


def route_analysis_ambiguity(spec: dict[str, Any]) -> dict[str, Any]:
    deterministic = spec.get("deterministic_metric") is True
    degrees = [str(x) for x in spec.get("researcher_degrees_of_freedom") or [] if str(x)]
    qualitative = spec.get("qualitative_interpretation") is True
    ensemble = (bool(degrees) or qualitative) and not deterministic
    return {
        "schema_version": SCHEMA_VERSION,
        "analysis_id": str(spec.get("analysis_id") or ""),
        "route": "INDEPENDENT_ANALYSIS_ENSEMBLE" if ensemble else "SINGLE_DETERMINISTIC_ANALYSIS",
        "reasons": (["researcher-degrees-of-freedom"] if degrees else []) + (["qualitative-interpretation"] if qualitative else []) + (["deterministic-metric"] if deterministic else []),
        "minimum_independent_trajectories": 3 if ensemble else 1,
        "consensus_is_scientific_authority": False,
        "scientific_authority": False,
    }


def build_research_reasoning_layer_state() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "REASONING_CONTRACTS_INSTALLED",
        "policy": dict(POLICY),
        "contracts": ["LiteratureDelta", "LiteratureDepthRouter", "ScientificObjectMatrix", "ProximityProjection", "AnalysisAmbiguityRouter", "MetaReview"],
        "summary": {"contracts": 6, "automatic_scientific_authority": 0, "automatic_research_item_authority": 0, "automatic_experiment_authority": 0},
        "scientific_authority": False,
    }
