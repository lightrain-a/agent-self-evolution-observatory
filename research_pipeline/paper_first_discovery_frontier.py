from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SCHEMA_VERSION = "1.0"


def _now(value: datetime | None = None) -> str:
    return (value or datetime.now(timezone.utc)).astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _int(mapping: dict[str, Any], key: str) -> int:
    try:
        return int(mapping.get(key) or 0)
    except (TypeError, ValueError):
        return 0


def build_paper_first_discovery_frontier(
    *,
    primary_state: dict[str, Any],
    generator_state: dict[str, Any],
    queue_state: dict[str, Any],
    relation_freshness_state: dict[str, Any],
    relation_admission_state: dict[str, Any],
    shadow_admission_state: dict[str, Any],
    object_candidate_state: dict[str, Any],
    support_release_watch_state: dict[str, Any],
    support_asset_recheck_state: dict[str, Any],
    shadow_portfolio_state: dict[str, Any] | None = None,
    evidence_migration_state: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Compile zero-authority discovery-control states into one trigger-driven frontier.

    This state never replaces any scientific gate. It only says which already-existing
    control plane is currently actionable and which external events may change that fact.
    """
    ps = primary_state.get("summary") or {}
    gs = generator_state.get("summary") or {}
    qs = queue_state.get("summary") or {}
    rf = relation_freshness_state.get("summary") or {}
    ra = relation_admission_state.get("summary") or {}
    sa = shadow_admission_state.get("summary") or {}
    oc = object_candidate_state.get("summary") or {}
    rw = support_release_watch_state.get("summary") or {}
    aq = support_asset_recheck_state.get("summary") or {}
    shadow_latest = ((shadow_portfolio_state or {}).get("latest_run") or {}) if isinstance(shadow_portfolio_state, dict) else {}
    es = shadow_latest.get("summary") or {}
    ms = (evidence_migration_state or {}).get("summary") or {}

    live_source_closed = bool(
        primary_state.get("status") == "READY"
        and ps.get("source_retrieval_complete") is True
        and ps.get("source_coverage_exhausted") is True
        and _int(ps, "unreviewed_lane_linked_sources") == 0
        and _int(ps, "carrier_probe_pending") == 0
        and ps.get("carrier_probe_complete") is True
    )
    live_generator_closed = bool(
        generator_state.get("status") in {"SKIPPED_SOURCE_COVERAGE_SATURATED", "GENERATED_ZERO_CANDIDATES"}
        and _int(gs, "generated") == 0
        and _int(gs, "written_to_auto_inbox") == 0
    )
    live_queue_closed = bool(
        _int(qs, "submitted") == 0
        and _int(qs, "passed_problem_gate") == 0
        and _int(qs, "paper_design_eligible") == 0
    )
    relation_current_closed = bool(
        relation_freshness_state.get("status") == "CURRENT_RELATION_UNIVERSE"
        and rf.get("universe_stale") is False
        and rf.get("current_not_reduced_unknown") is False
        and rf.get("focused_problem_generator_reopen_allowed") is False
        and relation_admission_state.get("status") == "HOLD_MANUAL_RELATION_SCAN"
        and ra.get("manual_scan_eligible") is False
        and ra.get("automatic_model_scan_authorized") is False
    )
    shadow_closed = bool(
        shadow_admission_state.get("status") == "SKIPPED_SHADOW_SOURCE_TRANSACTION_ALREADY_TERMINAL"
        and sa.get("same_source_transaction") is True
        and sa.get("qualification_allowed") is False
        and _int(sa, "automatic_provider_calls_authorized") == 0
    )
    object_closed = bool(
        _int(oc, "activation_authorized") == 0
        and _int(oc, "pending_cache") == 0
    )
    shadow_evidence_open = sum(_int(es, key) for key in (
        "evidence_design_pending", "evidence_operationalization_recompile_pending", "evidence_review_pending", "evidence_substrate_preflight_pending", "evidence_harness_implementation_pending", "evidence_execution_ready", "evidence_residual_survives", "evidence_branch_repair_ready"
    ))
    migration_evidence_open = sum(_int(ms, key) for key in (
        "evidence_design_pending", "evidence_operationalization_recompile_pending", "evidence_review_pending", "evidence_substrate_preflight_pending", "evidence_harness_implementation_pending", "evidence_execution_ready", "evidence_residual_survives", "evidence_branch_repair_ready"
    )) if str((evidence_migration_state or {}).get("status") or "") == "LEGACY_REDUCTION_EVIDENCE_MIGRATION_READY" else 0
    evidence_internal_open = shadow_evidence_open + migration_evidence_open
    evidence_loop_closed = evidence_internal_open == 0
    support_closed = bool(
        _int(rw, "recheck_required") == 0
        and _int(rw, "support_qualified") == 0
        and _int(rw, "generator_reopen_authorized") == 0
        and _int(rw, "problem_gate_authorized") == 0
        and _int(aq, "queued") == 0
        and _int(aq, "support_qualified") == 0
        and _int(aq, "generator_reopen_authorized") == 0
        and _int(aq, "problem_gate_authorized") == 0
    )

    triggers = [
        {
            "trigger": "NEW_FRESHNESS_RELEVANCE_QUALIFIED_LANE_GROUNDED_PRIMARY_SOURCE",
            "detector": "canonical-live-primary-retrieval",
            "effect": "may-open-a-new-content-addressed-primary-transaction",
            "automatic_model_call_authorized": False,
            "scientific_authority": False,
        },
        {
            "trigger": "NEW_CANONICAL_SOURCE_TRANSACTION_AFTER_LIVE_CLOSURE",
            "detector": "shadow-search-admission",
            "effect": "may-permit-zero-provider-qualification-freeze-before-shadow-execution",
            "automatic_model_call_authorized": False,
            "scientific_authority": False,
        },
        {
            "trigger": "AUTHOR_RELEASE_SURFACE_CHANGE_FOR_CURRENT_SUPPORT_HOLD",
            "detector": "support-release-watch",
            "effect": "creates-or-refreshes-asset-recheck-task-only",
            "automatic_model_call_authorized": False,
            "scientific_authority": False,
        },
        {
            "trigger": "NEW_AUTHOR_RELEASE_DECLARATION_ON_NO_ENDPOINT_PRIMARY",
            "detector": "bounded-primary-declaration-refresh",
            "effect": "adds-author-declared-release-watch-target-only",
            "automatic_model_call_authorized": False,
            "scientific_authority": False,
        },
        {
            "trigger": "NEW_PRIMARY_VERIFIED_SUPPORT_FOR_SHADOW_SCIENTIFIC_OBJECT",
            "detector": "shadow-scientific-object-maintenance",
            "effect": "may-request-human-lane-preregistration-review-only-after-existing-support-purity-ownership-gates",
            "automatic_model_call_authorized": False,
            "scientific_authority": False,
        },
    ]

    blockers: list[str] = []
    if not live_source_closed:
        blockers.append("live-source-frontier-open")
    if not live_generator_closed:
        blockers.append("live-generator-frontier-open")
    if not live_queue_closed:
        blockers.append("live-problem-queue-open")
    if not relation_current_closed:
        blockers.append("relation-frontier-open-or-stale")
    if not shadow_closed:
        blockers.append("shadow-qualification-or-search-open")
    if not object_closed:
        blockers.append("scientific-object-candidate-work-open")
    if not support_closed:
        blockers.append("support-release-or-asset-recheck-open")
    if not evidence_loop_closed:
        blockers.append("bounded-evidence-acquisition-open")

    if not live_queue_closed:
        status = "LIVE_PROBLEM_REVIEW_PENDING"
    elif not live_source_closed or not live_generator_closed:
        status = "LIVE_SOURCE_DISCOVERY_PENDING"
    elif not evidence_loop_closed:
        status = "EVIDENCE_ACQUISITION_PENDING"
    elif not support_closed:
        status = "SUPPORT_ASSET_RECHECK_PENDING"
    elif not shadow_closed:
        status = "SHADOW_QUALIFICATION_PENDING"
    elif not relation_current_closed:
        status = "RELATION_CONTROL_PENDING"
    elif not object_closed:
        status = "SCIENTIFIC_OBJECT_REVIEW_PENDING"
    else:
        status = "WAIT_EXTERNAL_EVIDENCE_TRIGGERS"

    summary = {
        "live_source_closed": live_source_closed,
        "live_generator_closed": live_generator_closed,
        "live_queue_closed": live_queue_closed,
        "relation_current_closed": relation_current_closed,
        "shadow_closed": shadow_closed,
        "scientific_object_closed": object_closed,
        "support_release_closed": support_closed,
        "evidence_acquisition_closed": evidence_loop_closed,
        "evidence_internal_open": evidence_internal_open,
        "shadow_evidence_internal_open": shadow_evidence_open,
        "migration_evidence_internal_open": migration_evidence_open,
        "evidence_design_pending": _int(es, "evidence_design_pending") + (_int(ms, "evidence_design_pending") if migration_evidence_open else 0),
        "evidence_operationalization_recompile_pending": _int(es, "evidence_operationalization_recompile_pending") + (_int(ms, "evidence_operationalization_recompile_pending") if migration_evidence_open else 0),
        "evidence_review_pending": _int(es, "evidence_review_pending") + (_int(ms, "evidence_review_pending") if migration_evidence_open else 0),
        "evidence_substrate_preflight_pending": _int(es, "evidence_substrate_preflight_pending") + (_int(ms, "evidence_substrate_preflight_pending") if migration_evidence_open else 0),
        "evidence_harness_implementation_pending": _int(es, "evidence_harness_implementation_pending") + (_int(ms, "evidence_harness_implementation_pending") if migration_evidence_open else 0),
        "evidence_execution_ready": _int(es, "evidence_execution_ready") + (_int(ms, "evidence_execution_ready") if migration_evidence_open else 0),
        "evidence_residual_survives": _int(es, "evidence_residual_survives") + (_int(ms, "evidence_residual_survives") if migration_evidence_open else 0),
        "evidence_branch_repair_ready": _int(es, "evidence_branch_repair_ready") + (_int(ms, "evidence_branch_repair_ready") if migration_evidence_open else 0),
        "open_internal_frontiers": len(blockers),
        "external_triggers": len(triggers),
        "automatic_model_calls_authorized": 0,
        "automatic_problem_gate_authorized": 0,
        "automatic_method_authorized": 0,
        "automatic_experiment_authorized": 0,
        "automatic_p0_authorized": 0,
        "automatic_gpu_authorized": 0,
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": _now(now),
        "status": status,
        "policy": {
            "scientific_authority": False,
            "frontier_is_deterministic_compute_control_only": True,
            "frontier_does_not_replace_primary_generator_problem_gate_or_relation_controls": True,
            "frontier_cannot_authorize_model_calls": True,
            "frontier_cannot_authorize_problem_gate_method_experiment_p0_gpu": True,
            "wait_external_status_is_not_scientific_exhaustion": True,
            "external_trigger_detection_may_use_existing_bounded_source_release_checks": True,
            "trigger_detection_never_counts_as_trigger_satisfaction": True,
            "trigger_satisfaction_must_reenter_original_control_plane": True,
        },
        "summary": summary,
        "blockers": blockers,
        "triggers": triggers,
        "scientific_authority": False,
    }


def validate_paper_first_discovery_frontier(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    policy = state.get("policy") or {}
    summary = state.get("summary") or {}
    allowed_statuses = {
        "WAIT_EXTERNAL_EVIDENCE_TRIGGERS",
        "LIVE_PROBLEM_REVIEW_PENDING",
        "LIVE_SOURCE_DISCOVERY_PENDING",
        "SUPPORT_ASSET_RECHECK_PENDING",
        "EVIDENCE_ACQUISITION_PENDING",
        "SHADOW_QUALIFICATION_PENDING",
        "RELATION_CONTROL_PENDING",
        "SCIENTIFIC_OBJECT_REVIEW_PENDING",
    }
    if state.get("scientific_authority") is not False:
        errors.append("discovery frontier cannot carry scientific authority")
    if state.get("status") not in allowed_statuses:
        errors.append("discovery frontier status invalid")
    if (
        policy.get("scientific_authority") is not False
        or policy.get("frontier_is_deterministic_compute_control_only") is not True
        or policy.get("frontier_does_not_replace_primary_generator_problem_gate_or_relation_controls") is not True
        or policy.get("frontier_cannot_authorize_model_calls") is not True
        or policy.get("frontier_cannot_authorize_problem_gate_method_experiment_p0_gpu") is not True
        or policy.get("wait_external_status_is_not_scientific_exhaustion") is not True
        or policy.get("trigger_detection_never_counts_as_trigger_satisfaction") is not True
        or policy.get("trigger_satisfaction_must_reenter_original_control_plane") is not True
    ):
        errors.append("discovery frontier policy must remain deterministic zero-authority orchestration")
    for key in (
        "automatic_model_calls_authorized",
        "automatic_problem_gate_authorized",
        "automatic_method_authorized",
        "automatic_experiment_authorized",
        "automatic_p0_authorized",
        "automatic_gpu_authorized",
    ):
        if _int(summary, key) != 0:
            errors.append("discovery frontier cannot authorize models or downstream scientific execution")
            break
    triggers = [row for row in state.get("triggers") or [] if isinstance(row, dict)]
    if len(triggers) != _int(summary, "external_triggers") or any(row.get("scientific_authority") is not False or row.get("automatic_model_call_authorized") is not False for row in triggers):
        errors.append("discovery frontier external triggers must be bounded zero-authority detectors")
    if state.get("status") == "WAIT_EXTERNAL_EVIDENCE_TRIGGERS":
        if _int(summary, "open_internal_frontiers") != 0 or not all(summary.get(key) is True for key in (
            "live_source_closed", "live_generator_closed", "live_queue_closed", "relation_current_closed", "shadow_closed", "scientific_object_closed", "support_release_closed", "evidence_acquisition_closed"
        )):
            errors.append("wait-external frontier requires every internal discovery frontier to be closed")
    return sorted(set(errors))
