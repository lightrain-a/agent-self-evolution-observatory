from __future__ import annotations

from typing import Any


SCHEMA_VERSION = "1.0"


def build_shadow_continuation_frontier(
    *,
    admission: dict[str, Any],
    support_watch: dict[str, Any],
    asset_queue: dict[str, Any],
    support_handoff: dict[str, Any],
) -> dict[str, Any]:
    a = admission.get("summary") or {}
    w = support_watch.get("summary") or {}
    q = asset_queue.get("summary") or {}
    h = support_handoff.get("summary") or {}

    qualification_ready = admission.get("status") == "READY_FOR_SHADOW_QUALIFICATION" and a.get("qualification_allowed") is True
    release_recheck = int(w.get("recheck_required") or 0)
    queued = int(q.get("queued") or 0)
    handoff_ready = int(h.get("support_inventory_recheck_ready") or 0)
    provenance_hold = int(h.get("provenance_incomplete") or 0)
    support_holds = int(w.get("support_holds") or q.get("support_holds") or 0)

    if provenance_hold > 0:
        status = "HOLD_SUPPORT_RECHECK_PROVENANCE"
        next_action = "repair-support-recheck-provenance"
    elif handoff_ready > 0:
        status = "READY_FOR_SUPPORT_INVENTORY_RECHECK"
        next_action = "support-inventory-recheck"
    elif release_recheck > 0 and queued == 0:
        status = "READY_FOR_ASSET_RECHECK_QUEUE_COMPILE"
        next_action = "compile-durable-asset-recheck-queue"
    elif queued > 0:
        status = "HOLD_ASSET_RECHECK_HANDOFF_NOT_READY"
        next_action = "compile-support-inventory-handoff"
    elif qualification_ready:
        status = "READY_FOR_ZERO_PROVIDER_SHADOW_QUALIFICATION"
        next_action = "canonical-private-pool-shadow-qualification"
    elif admission.get("status") == "HOLD_PRIOR_SHADOW_RUN_INCOMPLETE":
        status = "HOLD_PRIOR_SHADOW_RUN_INCOMPLETE"
        next_action = "finish-or-stop-prior-shadow-run"
    elif admission.get("status") == "HOLD_CANONICAL_DISCOVERY_TRANSACTION_OPEN":
        status = "HOLD_CANONICAL_DISCOVERY_TRANSACTION_OPEN"
        next_action = "wait-canonical-discovery-close"
    elif admission.get("status") in {"HOLD_PREVIOUS_SHADOW_SOURCE_IDENTITY_UNAVAILABLE", "HOLD_SHADOW_SOURCE_IDENTITY_CONFLICT"}:
        status = str(admission.get("status"))
        next_action = "repair-shadow-source-provenance"
    elif admission.get("status") == "SKIPPED_SHADOW_SOURCE_TRANSACTION_ALREADY_TERMINAL":
        status = "WAIT_EXTERNAL_PRIMARY_OR_SUPPORT_RELEASE_CHANGE" if support_holds > 0 else "WAIT_EXTERNAL_PRIMARY_CONTENT_CHANGE"
        next_action = "wait-external-change"
    else:
        status = "HOLD_SHADOW_CONTINUATION_STATE_INCOMPLETE"
        next_action = "repair-shadow-continuation-state"

    active_control_actions = int(status.startswith("READY_FOR_"))
    external_wait = int(status.startswith("WAIT_EXTERNAL_"))
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "next_control_action": next_action,
        "policy": {
            "scientific_authority": False,
            "frontier_is_deterministic_control_projection_only": True,
            "frontier_cannot_create_shadow_run": True,
            "frontier_cannot_call_model_provider": True,
            "frontier_cannot_qualify_support": True,
            "frontier_cannot_reopen_generator_or_problem_gate": True,
            "frontier_cannot_authorize_method_experiment_p0_gpu": True,
            "zero_active_action_is_valid_external_wait": True,
        },
        "summary": {
            "shadow_qualification_ready": int(qualification_ready),
            "release_recheck_required": release_recheck,
            "asset_recheck_queued": queued,
            "support_inventory_handoff_ready": handoff_ready,
            "support_handoff_provenance_hold": provenance_hold,
            "support_holds": support_holds,
            "active_control_actions": active_control_actions,
            "external_wait": external_wait,
            "automatic_provider_calls_authorized": 0,
            "scientific_authority": 0,
            "generator_reopen_authorized": 0,
            "problem_gate_authorized": 0,
            "method_authorized": 0,
            "experiment_authorized": 0,
            "p0_authorized": 0,
            "gpu_authorized": 0,
        },
        "source_status": {
            "shadow_admission": str(admission.get("status") or "NOT_RUN"),
            "support_release_watch": str(support_watch.get("status") or "NOT_RUN"),
            "support_asset_queue": str(asset_queue.get("status") or "NOT_RUN"),
            "support_inventory_handoff": str(support_handoff.get("status") or "NOT_RUN"),
        },
        "scientific_authority": False,
    }


def validate_shadow_continuation_frontier(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    policy = state.get("policy") or {}
    summary = state.get("summary") or {}
    allowed = {
        "WAIT_EXTERNAL_PRIMARY_OR_SUPPORT_RELEASE_CHANGE",
        "WAIT_EXTERNAL_PRIMARY_CONTENT_CHANGE",
        "READY_FOR_ZERO_PROVIDER_SHADOW_QUALIFICATION",
        "READY_FOR_ASSET_RECHECK_QUEUE_COMPILE",
        "READY_FOR_SUPPORT_INVENTORY_RECHECK",
        "HOLD_SUPPORT_RECHECK_PROVENANCE",
        "HOLD_ASSET_RECHECK_HANDOFF_NOT_READY",
        "HOLD_PRIOR_SHADOW_RUN_INCOMPLETE",
        "HOLD_CANONICAL_DISCOVERY_TRANSACTION_OPEN",
        "HOLD_PREVIOUS_SHADOW_SOURCE_IDENTITY_UNAVAILABLE",
        "HOLD_SHADOW_SOURCE_IDENTITY_CONFLICT",
        "HOLD_SHADOW_CONTINUATION_STATE_INCOMPLETE",
    }
    if state.get("status") not in allowed:
        errors.append("shadow continuation frontier status invalid")
    if state.get("scientific_authority") is not False or policy.get("scientific_authority") is not False:
        errors.append("shadow continuation frontier cannot carry scientific authority")
    if policy.get("frontier_is_deterministic_control_projection_only") is not True or policy.get("frontier_cannot_create_shadow_run") is not True or policy.get("frontier_cannot_call_model_provider") is not True or policy.get("frontier_cannot_qualify_support") is not True or policy.get("frontier_cannot_reopen_generator_or_problem_gate") is not True or policy.get("frontier_cannot_authorize_method_experiment_p0_gpu") is not True:
        errors.append("shadow continuation frontier must remain zero-authority control projection")
    if any(int(summary.get(key) or 0) != 0 for key in ("automatic_provider_calls_authorized", "provider_calls_authorized", "scientific_authority", "generator_reopen_authorized", "problem_gate_authorized", "method_authorized", "experiment_authorized", "p0_authorized", "gpu_authorized")):
        errors.append("shadow continuation frontier cannot authorize provider or downstream work")
    status = str(state.get("status") or "")
    ready = int(summary.get("active_control_actions") or 0)
    external_wait = int(summary.get("external_wait") or 0)
    if ready != int(status.startswith("READY_FOR_")):
        errors.append("shadow continuation active-action accounting mismatch")
    if external_wait != int(status.startswith("WAIT_EXTERNAL_")):
        errors.append("shadow continuation external-wait accounting mismatch")
    if status == "READY_FOR_SUPPORT_INVENTORY_RECHECK" and int(summary.get("support_inventory_handoff_ready") or 0) <= 0:
        errors.append("support-inventory ready frontier requires ready handoff")
    if status == "READY_FOR_ZERO_PROVIDER_SHADOW_QUALIFICATION" and int(summary.get("shadow_qualification_ready") or 0) != 1:
        errors.append("shadow qualification frontier requires qualification-ready admission")
    if status.startswith("WAIT_EXTERNAL_") and ready != 0:
        errors.append("external-wait frontier cannot contain active control action")
    return sorted(set(errors))
