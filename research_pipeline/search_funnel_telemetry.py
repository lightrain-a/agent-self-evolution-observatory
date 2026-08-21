from __future__ import annotations

from collections import Counter
from typing import Any


SCHEMA_VERSION = "1.0"

POLICY: dict[str, Any] = {
    "schema_version": SCHEMA_VERSION,
    "telemetry_is_observability_not_scientific_authority": True,
    "bottleneck_labels_describe_pipeline_state_not_scientific_truth": True,
    "portfolio_capacity_pressure_cannot_relax_gates": True,
    "zero_candidates_and_support_holds_are_distinct_bottlenecks": True,
    "typed_reduction_or_support_holds_must_not_be_reported_as_idea_generation_failure": True,
    "support_availability_adapts_future_search_allocation_not_scientific_rank": True,
    "support_hold_cannot_eliminate_or_scientifically_downgrade_a_candidate": True,
    "new_provider_fanout_requires_a_new_receipted_source_or_operator_frame": True,
    "telemetry_cannot_authorize_provider_calls_problem_gate_method_experiment_p0_or_gpu": True,
}


def _int(mapping: dict[str, Any], key: str) -> int:
    try:
        return int(mapping.get(key) or 0)
    except (TypeError, ValueError):
        return 0


def _blocker_key(value: Any) -> str:
    text = str(value or "").strip()
    return text.split(":", 1)[0] if text else "unknown"


def build_search_funnel_telemetry(
    *,
    primary_state: dict[str, Any],
    generator_state: dict[str, Any],
    pre_f0_state: dict[str, Any],
    pre_f0_support_state: dict[str, Any],
    problem_gate_state: dict[str, Any],
    discovery_frontier_state: dict[str, Any],
    candidate_portfolio_state: dict[str, Any],
) -> dict[str, Any]:
    ps = primary_state.get("summary") or {}
    gs = generator_state.get("summary") or {}
    fs = pre_f0_state.get("summary") or {}
    ss = pre_f0_support_state.get("summary") or {}
    qs = problem_gate_state.get("summary") or {}
    cs = candidate_portfolio_state.get("summary") or {}

    blocker_counts: Counter[str] = Counter()
    for row in pre_f0_state.get("rows") or []:
        if not isinstance(row, dict):
            continue
        for value in row.get("reduction_blockers") or []:
            blocker_counts[_blocker_key(value)] += 1

    stage_counts = {
        "primary_verified": _int(ps, "verified"),
        "primary_selected": _int(ps, "selected"),
        "raw_seeds": _int(gs, "raw_seeds"),
        "semantic_unique_seeds": _int(gs, "semantic_unique_seeds"),
        "breadth_archive": _int(gs, "breadth_archive"),
        "reviewer_attacks": _int(gs, "reviewer_attacks"),
        "repair_children": _int(gs, "repair_children"),
        "pre_f0_eligible": _int(gs, "pre_f0_eligible"),
        "pre_f0_queued": _int(fs, "queued"),
        "pre_f0_support_qualified": _int(ss, "support_qualified"),
        "pre_f0_support_hold": _int(ss, "hold_support_unavailable"),
        "semantic_clear": _int(gs, "semantic_clear"),
        "problem_gate_submitted": _int(qs, "submitted"),
        "problem_gate_passed": _int(qs, "passed_problem_gate"),
        "paper_design_eligible": _int(qs, "paper_design_eligible"),
    }

    generator_status = str(generator_state.get("status") or "")
    pre_f0_queued = stage_counts["pre_f0_queued"]
    support_ready = stage_counts["pre_f0_support_qualified"]
    raw_seeds = stage_counts["raw_seeds"]
    semantic_unique = stage_counts["semantic_unique_seeds"]
    semantic_clear = stage_counts["semantic_clear"]
    submitted = stage_counts["problem_gate_submitted"]
    passed = stage_counts["problem_gate_passed"]

    all_pre_f0_support_held = bool(
        pre_f0_queued > 0
        and support_ready == 0
        and stage_counts["pre_f0_support_hold"] == pre_f0_queued
    )
    if all_pre_f0_support_held:
        bottleneck = "PRE_F0_SUPPORT_PROVENANCE"
        explanation = "Candidate problems exist, but every retained Pre-F0 falsifier lacks qualified first-party support. This is a support-provenance bottleneck, not an idea-generation or scientific failure."
        next_action = "Preserve the held candidates and adapt the next receipted API search frame toward independently resolvable first-party evidence surfaces; do not rerun the same content-addressed pool/operator frame."
    elif pre_f0_queued > 0 and support_ready == 0:
        bottleneck = "PRE_F0_REDUCTION_OR_SUPPORT_EVIDENCE"
        explanation = "Candidate problems exist, but exact-reduction/support evidence is not yet qualified; this is not an idea-generation failure."
        next_action = "Resolve the cheapest discriminating reduction/support contracts for the retained Pre-F0 candidates, then rerun exact same-information reduction before Problem Gate."
    elif raw_seeds == 0 and _int(ps, "verified") > 0:
        bottleneck = "BREADTH_SEARCH"
        explanation = "Primary evidence exists but breadth search produced no raw candidate seed."
        next_action = "Increase or redirect breadth search across the registered search primitives without relaxing later scientific gates."
    elif raw_seeds > 0 and semantic_unique == 0:
        bottleneck = "MECHANICAL_DEDUP_OR_SCHEMA"
        explanation = "Raw seeds exist but none survives deterministic normalization/deduplication."
        next_action = "Audit duplicate/schema loss before spending reviewer calls."
    elif semantic_unique > 0 and pre_f0_queued == 0 and semantic_clear == 0 and generator_status.startswith("GENERATED"):
        bottleneck = "FORMULATION_OR_EXACT_REDUCTION"
        explanation = "Breadth candidates exist but none reaches a reviewable or bounded Pre-F0 route."
        next_action = "Inspect formulation and exact-reduction loss reasons; do not interpret this as a scientific dead end without a typed principle closure."
    elif semantic_clear > 0 and submitted == 0:
        bottleneck = "PROBLEM_GATE_HANDOFF"
        explanation = "Independent semantic review is clear but candidates are not yet represented in Problem Gate."
        next_action = "Repair the deterministic handoff/provenance contract without changing scientific thresholds."
    elif submitted > 0 and passed == 0:
        bottleneck = "PROBLEM_GATE"
        explanation = "Candidates reached Problem Gate but none currently passes the frozen problem contract."
        next_action = "Inspect typed Problem-Gate blockers and distinguish scientific reduction from support/protocol/realization holds."
    elif passed > 0:
        bottleneck = "PAPER_DESIGN_OR_METHOD_BOUNDARY"
        explanation = "At least one problem survives Problem Gate; the next bottleneck is paper design/method boundary rather than discovery."
        next_action = "Maintain the active portfolio while independently reviewing paper novelty, claim boundary, and method necessity."
    else:
        bottleneck = str(discovery_frontier_state.get("status") or "NO_SINGLE_BOTTLENECK")
        explanation = "No more specific funnel diagnosis dominates the current trigger-driven discovery frontier."
        next_action = "Follow the current zero-authority discovery frontier trigger without promoting a control-plane state into scientific evidence."

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "SEARCH_FUNNEL_OBSERVED",
        "policy": dict(POLICY),
        "summary": {
            "bottleneck": bottleneck,
            "primary_verified": stage_counts["primary_verified"],
            "raw_seeds": stage_counts["raw_seeds"],
            "pre_f0_queued": stage_counts["pre_f0_queued"],
            "pre_f0_support_qualified": stage_counts["pre_f0_support_qualified"],
            "problem_gate_passed": stage_counts["problem_gate_passed"],
            "visible_candidates": _int(cs, "visible_candidates"),
        },
        "stage_counts": stage_counts,
        "loss_reason_counts": dict(sorted(blocker_counts.items())),
        "bottleneck": {
            "key": bottleneck,
            "explanation": explanation,
            "next_action": next_action,
            "scientific_authority": False,
        },
        "search_adaptation": {
            "status": (
                "PROPOSE_SUPPORT_AWARE_NEW_SEARCH_FRAME"
                if all_pre_f0_support_held
                else "NO_SUPPORT_SATURATION_PIVOT"
            ),
            "trigger": {
                "pre_f0_queued": pre_f0_queued,
                "support_qualified": support_ready,
                "support_holds": stage_counts["pre_f0_support_hold"],
                "all_retained_candidates_support_held": all_pre_f0_support_held,
            },
            "allowed_effects": (
                [
                    "allocate_future_generation_budget_toward_verified_first_party_asset_surfaces",
                    "retain_current_candidates_as_support_holds",
                    "require_new_source_set_or_discovery_operator_receipt_before_provider_fanout",
                ]
                if all_pre_f0_support_held
                else []
            ),
            "forbidden_effects": [
                "scientifically_downgrade_held_candidate",
                "convert_support_hold_to_scientific_failure",
                "relax_exact_reduction_or_problem_gate",
                "authorize_provider_calls",
            ],
            "provider_calls_authorized": False,
            "scientific_authority": False,
        },
        "portfolio": {
            "visible_candidates": _int(cs, "visible_candidates"),
            "active_problem_lines": _int(cs, "active_problem_lines"),
            "search_holds": _int(cs, "search_holds"),
            "active_shortfall": _int(cs, "active_shortfall"),
            "search_hold_shortfall": _int(cs, "search_hold_shortfall"),
            "capacity_targets_are_advisory": True,
        },
        "frontier_status": str(discovery_frontier_state.get("status") or ""),
        "scientific_authority": False,
        "authority": {
            "provider_calls": False,
            "problem_gate": False,
            "paper_design": False,
            "method": False,
            "experiment": False,
            "p0": False,
            "gpu": False,
        },
    }
