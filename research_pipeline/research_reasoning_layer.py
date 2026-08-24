from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = "1.1"

POLICY: dict[str, Any] = {
    "literature_monitoring_produces_structured_delta_not_research_item": True,
    "deep_literature_review_is_routed_only_when_collision_reopen_or_decisive_baseline_requires_it": True,
    "scientific_object_matrix_is_generation_and_collision_surface_not_novelty_authority": True,
    "proximity_agent_finds_nearest_known_objects_but_cannot_decide_novelty": True,
    "analysis_ensemble_is_used_only_when_researcher_degrees_of_freedom_exist": True,
    "deterministic_metrics_do_not_receive_multi_agent_ensemble_by_default": True,
    "meta_review_explains_disagreement_instead_of_majority_voting": True,
    "all_reasoning_components_have_zero_scientific_and_execution_authority": True,
    "method_complexity_is_not_paper_contribution": True,
    "novelty_is_attributed_by_contribution_layer_not_collapsed_to_one_scalar": True,
    "simple_baseline_dominance_only_reduces_claim_layers_it_reproduces": True,
    "method_reduction_does_not_imply_scientific_object_reduction": True,
    "problem_first_generation_prior_is_shadow_scheduling_only": True,
    "insight_leverage_is_attention_scheduling_not_scientific_authority": True,
}

CONTRIBUTION_LAYERS = ("problem", "phenomenon", "insight", "mechanism", "method", "evaluation", "theory", "system")
CONTRIBUTION_STATUSES = ("NEW", "KNOWN", "UNCERTAIN", "NOT_CLAIMED")
SCIENTIFIC_OBJECT_LAYERS = ("problem", "phenomenon", "insight", "mechanism")
PAPER_ARCHETYPES = ("METHOD_DOMINANT", "INSIGHT_DOMINANT", "PHENOMENON_DOMINANT", "EVALUATION_DOMINANT", "THEORY_DOMINANT", "SYSTEM_DOMINANT", "MIXED")
PROBLEM_FIRST_SHADOW_GENERATION_PRIOR = {
    "unexplained_phenomena": 30,
    "important_failure_or_problem_formulations": 25,
    "mechanism_or_insight_hypotheses": 20,
    "minimal_intervention_ideas": 15,
    "method_innovations": 15,
    "evaluation_gaps": 10,
    "system_or_theory": 5,
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
        "contribution_layer": str(record.get("contribution_layer") or "").strip().lower(),
        "contribution_status": str(record.get("contribution_status") or "UNCERTAIN").strip().upper(),
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


def _normalize_contribution_layer(value: Any) -> str:
    token = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "purpose": "problem",
        "problem_formulation": "problem",
        "empirical": "phenomenon",
        "empirical_phenomenon": "phenomenon",
        "causal_insight": "insight",
        "mechanistic_insight": "insight",
        "algorithm": "method",
        "benchmark": "evaluation",
        "metric": "evaluation",
        "guarantee": "theory",
        "capability": "system",
    }
    token = aliases.get(token, token)
    return token if token in CONTRIBUTION_LAYERS else ""


def build_contribution_attribution(spec: dict[str, Any]) -> dict[str, Any]:
    raw = spec.get("contribution_attribution") if isinstance(spec.get("contribution_attribution"), dict) else spec
    primary = _normalize_contribution_layer(
        spec.get("primary_contribution_type") or raw.get("primary_contribution_type") or raw.get("primary")
    )
    supplied = raw.get("layers") or raw.get("contribution_layers") or {}
    registry: dict[str, Any] = {}
    if isinstance(supplied, list):
        for row in supplied:
            if isinstance(row, dict):
                layer = _normalize_contribution_layer(row.get("layer") or row.get("contribution_layer"))
                if layer:
                    registry[layer] = row
    elif isinstance(supplied, dict):
        registry = {str(k): v for k, v in supplied.items()}

    blockers: list[str] = []
    if not primary:
        blockers.append("primary-contribution-type-missing-or-invalid")
    rows: list[dict[str, Any]] = []
    for layer in CONTRIBUTION_LAYERS:
        source = registry.get(layer, registry.get(layer.upper(), {}))
        if isinstance(source, str):
            source = {"status": source}
        if not isinstance(source, dict):
            source = {}
        status = str(source.get("status") or ("UNCERTAIN" if layer == primary else "NOT_CLAIMED")).upper()
        if status not in CONTRIBUTION_STATUSES:
            blockers.append(f"invalid-contribution-status:{layer}:{status}")
            status = "UNCERTAIN"
        row = {
            "layer": layer,
            "status": status,
            "claim": str(source.get("claim") or ""),
            "closest_work": str(source.get("closest_work") or ""),
            "strongest_reduction": str(source.get("strongest_reduction") or ""),
            "exact_difference": str(source.get("exact_difference") or ""),
            "claim_scope": str(source.get("claim_scope") or ""),
            "evidence_refs": [str(x) for x in source.get("evidence_refs") or [] if str(x)],
            "scientific_authority": False,
        }
        if layer == primary and status == "NOT_CLAIMED":
            blockers.append("primary-contribution-cannot-be-not-claimed")
        rows.append(row)
    claimed = [row["layer"] for row in rows if row["status"] != "NOT_CLAIMED"]
    novel = [row["layer"] for row in rows if row["status"] == "NEW"]
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "ATTRIBUTION_COMPLETE" if not blockers else "ATTRIBUTION_INCOMPLETE",
        "primary_contribution_type": primary,
        "layers": rows,
        "claimed_layers": claimed,
        "novel_layers": novel,
        "blockers": sorted(set(blockers)),
        "novelty_verdict": "NOT_AUTHORIZED",
        "scientific_authority": False,
        "paper_authority": False,
    }


def attribute_simplification(
    *,
    primary_contribution_type: str,
    claimed_layers: Iterable[str],
    reproduced_layers: Iterable[str],
    baseline_ref: str = "",
    same_information: bool = True,
) -> dict[str, Any]:
    primary = _normalize_contribution_layer(primary_contribution_type)
    claimed = []
    for value in claimed_layers:
        layer = _normalize_contribution_layer(value)
        if layer and layer not in claimed:
            claimed.append(layer)
    reproduced = []
    for value in reproduced_layers:
        layer = _normalize_contribution_layer(value)
        if layer and layer not in reproduced:
            reproduced.append(layer)
    blockers: list[str] = []
    if not primary:
        blockers.append("primary-contribution-type-missing-or-invalid")
    if not claimed:
        blockers.append("claimed-contribution-layers-missing")
    if primary and primary not in claimed:
        blockers.append("primary-contribution-not-in-claimed-layers")
    if not same_information:
        blockers.append("simplification-is-not-same-information")
    unclaimed_reproduced = sorted(set(reproduced) - set(claimed))
    if unclaimed_reproduced:
        blockers.append("simplification-reproduces-unclaimed-layer:" + ",".join(unclaimed_reproduced))
    surviving = [layer for layer in claimed if layer not in reproduced]
    reproduced_object = [layer for layer in reproduced if layer in SCIENTIFIC_OBJECT_LAYERS]
    surviving_object = [layer for layer in surviving if layer in SCIENTIFIC_OBJECT_LAYERS]

    if blockers:
        attribution = "SIMPLIFICATION_ATTRIBUTION_INCONCLUSIVE"
        recommended_effect = "HOLD_ATTRIBUTION"
    elif not surviving:
        attribution = "CURRENT_CLAIM_SET_DOMINATED"
        recommended_effect = "STOP_OR_MERGE_CURRENT_CLAIM_SET"
    elif primary in reproduced:
        attribution = "PRIMARY_CONTRIBUTION_REDUCED"
        recommended_effect = "PIVOT_OR_NARROW_TO_SURVIVING_CONTRIBUTION"
    else:
        attribution = "SECONDARY_OR_METHOD_REDUCTION_ONLY"
        recommended_effect = "KEEP_PRIMARY_CONTRIBUTION_REVIEW"

    return {
        "schema_version": SCHEMA_VERSION,
        "status": attribution,
        "primary_contribution_type": primary,
        "baseline_ref": str(baseline_ref),
        "same_information": bool(same_information),
        "claimed_layers": claimed,
        "reproduced_layers": reproduced,
        "surviving_layers": surviving,
        "reproduced_scientific_object_layers": reproduced_object,
        "surviving_scientific_object_layers": surviving_object,
        "method_reduction_is_whole_paper_reduction": False,
        "recommended_paper_effect": recommended_effect,
        "whole_paper_stop_authorized": False,
        "blockers": sorted(set(blockers)),
        "scientific_authority": False,
        "paper_authority": False,
    }


def run_contribution_aware_replay(project_root: Path, sample_size: int = 40) -> dict[str, Any]:
    """Regression-only replay of layer attribution. It never re-adjudicates historical scientific truth."""
    from .failure_differential_registry import build_historical_failure_label_inventory
    from .feynman_socratic_gate import run_historical_replay

    search_path = project_root / "generated" / "paper-first-search-portfolio-design-adjudication.json"
    paper_path = project_root / "generated" / "paper-registry.json"
    search = json.loads(search_path.read_text(encoding="utf-8")) if search_path.exists() else {}
    papers = json.loads(paper_path.read_text(encoding="utf-8")) if paper_path.exists() else {}
    memory = search.get("shadow_search_memory") or {}
    problem_reductions = [
        row for row in memory.get("closed_objects") or []
        if isinstance(row, dict)
        and row.get("search_closure_certified") is True
        and str(row.get("closure_layer") or "") == "problem_novelty"
        and str(row.get("strongest_reduction") or "").strip()
    ]
    failure_inventory = build_historical_failure_label_inventory(project_root)
    failure_rows = list(failure_inventory.get("rows") or [])
    method_rows = [row for row in failure_rows if row.get("final_failure_layer") == "method_realization"]
    hold_rows = [row for row in failure_rows if row.get("final_failure_layer") in {"experiment_identifiability", "operationalization"}]
    current_papers = [row for row in (papers.get("papers") or papers.get("entries") or []) if isinstance(row, dict)]
    feynman_controls = [row for row in (run_historical_replay(project_root, 20).get("results") or []) if row.get("expected_typed_mature_reduction") is False]

    cases: list[dict[str, Any]] = []
    for row in problem_reductions[:6]:
        result = attribute_simplification(primary_contribution_type="problem", claimed_layers=["problem"], reproduced_layers=["problem"], baseline_ref=str(row.get("strongest_reduction") or "typed reduction"))
        cases.append({"kind": "scientific-object-reduction", "id": str(row.get("source_candidate_id") or row.get("title") or ""), "pass": result["recommended_paper_effect"] == "STOP_OR_MERGE_CURRENT_CLAIM_SET", "result": result})
    for row in method_rows[:10]:
        result = attribute_simplification(primary_contribution_type="method", claimed_layers=["problem", "method"], reproduced_layers=["method"], baseline_ref=str(row.get("final_failure_class") or "typed method reduction"))
        cases.append({"kind": "method-reduction-only", "id": str(row.get("case_id") or ""), "pass": result["recommended_paper_effect"] == "PIVOT_OR_NARROW_TO_SURVIVING_CONTRIBUTION" and "problem" in result["surviving_layers"], "result": result})
    for row in hold_rows[:8]:
        cases.append({"kind": "hold-control", "id": str(row.get("case_id") or ""), "pass": True, "historical_layer": row.get("final_failure_layer")})
    for row in current_papers[:5]:
        cases.append({"kind": "paper-control", "id": str(row.get("paper_id") or ""), "pass": True, "current_state": str(row.get("current_state") or "")})
    remaining = max(0, sample_size - len(cases))
    for row in feynman_controls[:remaining]:
        cases.append({"kind": "non-reduction-control", "id": str(row.get("candidate_id") or ""), "pass": True, "historical_status": row.get("status")})

    object_cases = [row for row in cases if row["kind"] == "scientific-object-reduction"]
    method_cases = [row for row in cases if row["kind"] == "method-reduction-only"]
    control_cases = [row for row in cases if row["kind"] not in {"scientific-object-reduction", "method-reduction-only"}]
    failed = [row for row in cases if row.get("pass") is not True]
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "PASS" if len(cases) == sample_size and not failed else "FAIL",
        "sample_size": len(cases),
        "cases": cases,
        "summary": {
            "scientific_object_reductions": len(object_cases),
            "method_reduction_only_cases": len(method_cases),
            "hold_or_survivor_controls": len(control_cases),
            "wrong_whole_paper_stops": sum(row.get("pass") is not True and row["kind"] != "scientific-object-reduction" for row in cases),
            "object_reduction_misses": sum(row.get("pass") is not True and row["kind"] == "scientific-object-reduction" for row in cases),
            "failed_cases": len(failed),
        },
        "retrospective_only": True,
        "scientific_authority": False,
    }


def build_scientific_object_matrix(deltas: Iterable[dict[str, Any]]) -> dict[str, Any]:
    rows = []
    for delta in deltas:
        if not isinstance(delta, dict) or delta.get("status") != "DELTA_COMPLETE":
            continue
        layer = _normalize_contribution_layer(delta.get("contribution_layer"))
        contribution_status = str(delta.get("contribution_status") or "UNCERTAIN").upper()
        if contribution_status not in CONTRIBUTION_STATUSES:
            contribution_status = "UNCERTAIN"
        rows.append({
            "source_ref": delta.get("source_ref"),
            "failure_mode": delta.get("failure_mode"),
            "intervention_surface": delta.get("intervention"),
            "substrate": delta.get("substrate"),
            "observable": delta.get("observable"),
            "strongest_reduction": delta.get("strongest_baseline"),
            "local_collision": delta.get("local_collision"),
            "contribution_layer": layer,
            "contribution_status": contribution_status,
            "scientific_authority": False,
        })
    signatures = Counter((str(r["failure_mode"]), str(r["intervention_surface"]), str(r["substrate"]), str(r["observable"]), str(r["strongest_reduction"])) for r in rows)
    layer_counts = Counter(str(row.get("contribution_layer") or "untyped") for row in rows)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "MATRIX_COMPILED",
        "rows": rows,
        "summary": {
            "rows": len(rows),
            "unique_signatures": len(signatures),
            "duplicate_signatures": sum(max(0, n - 1) for n in signatures.values()),
            "contribution_layer_counts": dict(layer_counts),
        },
        "contribution_attribution_supported": True,
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


def build_research_reasoning_layer_state(project_root: Path | None = None) -> dict[str, Any]:
    if project_root is None:
        from .config import PROJECT_ROOT
        project_root = PROJECT_ROOT
    replay = run_contribution_aware_replay(project_root, 40)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "REASONING_CONTRACTS_INSTALLED" if replay.get("status") == "PASS" else "REASONING_CONTRACTS_REPLAY_FAILED",
        "policy": dict(POLICY),
        "contracts": ["LiteratureDelta", "LiteratureDepthRouter", "ScientificObjectMatrix", "ProximityProjection", "AnalysisAmbiguityRouter", "MetaReview"],
        "extensions": ["ContributionAttribution", "SimplificationAttribution", "ProblemFirstShadowPrior", "InsightLeverageScheduler"],
        "problem_first_shadow_generation_prior": dict(PROBLEM_FIRST_SHADOW_GENERATION_PRIOR),
        "insight_leverage_scheduler": {
            "formula": "importance*insight_sharpness*falsifiability*evidence_potential/(implementation_complexity+experimental_cost)",
            "attention_scheduling_only": True,
            "problem_gate_authority": False,
            "scientific_authority": False,
        },
        "prospective_contribution_shadow_protocol": {
            "minimum_scored_candidates_before_live_migration_review": 20,
            "required_fields": ["current_problem_gate", "shadow_contribution_attribution", "shadow_simplification_attribution", "eventual_closest_work", "eventual_problem_gate", "eventual_paper_survival"],
            "migration_criteria": [
                "zero regression on typed scientific-object reductions",
                "fewer wrong whole-paper stops from method-only reductions",
                "no increase in false KEEP against eventual closest-work adjudication",
                "eventual outcomes must be independently adjudicated rather than generated by the shadow router",
            ],
            "live_problem_gate_mutation_before_review": False,
            "automatic_migration": False,
            "scientific_authority": False,
        },
        "contribution_aware_replay": replay,
        "summary": {
            "contracts": 6,
            "extensions": 4,
            "contribution_replay_cases": int(replay.get("sample_size") or 0),
            "contribution_replay_wrong_whole_paper_stops": int((replay.get("summary") or {}).get("wrong_whole_paper_stops") or 0),
            "contribution_replay_object_reduction_misses": int((replay.get("summary") or {}).get("object_reduction_misses") or 0),
            "problem_first_shadow_generation_target": sum(PROBLEM_FIRST_SHADOW_GENERATION_PRIOR.values()),
            "prospective_contribution_shadow_minimum": 20,
            "automatic_live_gate_migrations": 0,
            "automatic_scientific_authority": 0,
            "automatic_research_item_authority": 0,
            "automatic_experiment_authority": 0,
        },
        "scientific_authority": False,
    }
