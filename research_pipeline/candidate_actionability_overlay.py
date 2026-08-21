from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any

SCHEMA_VERSION = "1.0"
AUTHORITY = {
    "scientific_claim": False,
    "candidate_elimination": False,
    "problem_gate": False,
    "paper_design": False,
    "method": False,
    "experiment": False,
    "p0": False,
    "gpu": False,
}


def _canon(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha(value: Any) -> str:
    return hashlib.sha256(_canon(value).encode()).hexdigest()


def _correction_status(disposition: str) -> tuple[str, str]:
    value = str(disposition or "").upper()
    if value == "BUDGET_INFEASIBLE":
        return "HOLD_SUBSTRATE_BUDGET_INFEASIBLE", "HOLD_BUDGET"
    if value == "SOURCE_SPECIFIC_REQUIRED":
        return "WAIT_PRIMARY_ASSET_RELEASE", "WAIT_EXTERNAL_ASSET"
    if value == "PROTOCOL_REPAIR_REQUIRED":
        return "NEEDS_BOUNDED_EVIDENCE_DESIGN", "REPAIR_PROTOCOL"
    if value == "SUBSTRATE_UNAVAILABLE":
        return "HOLD_SUBSTRATE_UNAVAILABLE", "HOLD_SUPPORT"
    return "", ""


def _lane(status: str) -> str:
    status = str(status or "")
    if status == "READY_FOR_BOUNDED_EVIDENCE_ACQUISITION":
        return "CONTINUE_BOUNDED_EVIDENCE"
    if status == "READY_FOR_BOUNDED_SUBSTRATE_PREFLIGHT":
        return "CONTINUE_SUBSTRATE_PREFLIGHT"
    if status == "NEEDS_MINIMAL_HARNESS_IMPLEMENTATION":
        return "CONTINUE_HARNESS_IMPLEMENTATION"
    if status in {"NEEDS_BOUNDED_EVIDENCE_DESIGN", "DEFERRED_BY_ACTIVE_PORTFOLIO_BUDGET"}:
        return "NEXT_BOUNDED_EVIDENCE_DESIGN"
    if status == "WAIT_PRIMARY_ASSET_RELEASE":
        return "WAIT_EXTERNAL_ASSET"
    if status == "HOLD_HARNESS_RUNTIME_SUPPORT":
        return "HOLD_RUNTIME_SUPPORT"
    if status == "HOLD_SUBSTRATE_BUDGET_INFEASIBLE":
        return "HOLD_BUDGET"
    if status == "HOLD_SUBSTRATE_UNAVAILABLE":
        return "HOLD_SUPPORT"
    if status == "HOLD_EVIDENCE_REVIEW_BLOCKED":
        return "HOLD_SCIENTIFIC_REVIEW"
    if status == "HOLD_EVIDENCE_DESIGN_INVALID":
        return "HOLD_DESIGN_INVALID"
    if status == "NEEDS_INDEPENDENT_EVIDENCE_REVIEW":
        return "CONTINUE_INDEPENDENT_REVIEW"
    if status == "NEEDS_OPERATIONALIZATION_RECOMPILE":
        return "CONTINUE_PROTOCOL_REPAIR"
    return "OBSERVE_ONLY"


def compile_actionability_overlay(
    tournament: dict[str, Any],
    evidence_plan: dict[str, Any],
    *,
    substrate_receipts: list[dict[str, Any]] | None = None,
    runtime_revocations: list[dict[str, Any]] | None = None,
    next_slots: int = 4,
) -> dict[str, Any]:
    if tournament.get("scientific_authority") is not False:
        raise ValueError("tournament must be zero-authority")
    ranking = [dict(row) for row in tournament.get("ranking") or [] if isinstance(row, dict)]
    rank_by = {str(row.get("candidate_id") or ""): row for row in ranking}
    entries = {str(row.get("candidate_id") or ""): deepcopy(row) for row in evidence_plan.get("entries") or [] if isinstance(row, dict)}
    if set(rank_by) != set(entries):
        raise ValueError("tournament/evidence candidate sets differ")

    corrections: dict[str, dict[str, Any]] = {}
    for receipt in substrate_receipts or []:
        cid = str(receipt.get("candidate_id") or "")
        if cid not in entries:
            continue
        corrected_status, lane_hint = _correction_status(str(receipt.get("disposition") or ""))
        if corrected_status:
            corrections[cid] = {
                "source": "substrate_receipt",
                "disposition": str(receipt.get("disposition") or ""),
                "corrected_status": corrected_status,
                "lane_hint": lane_hint,
                "reason": str(receipt.get("reason") or "")[:1800],
                "scientific_authority": False,
            }
    for receipt in runtime_revocations or []:
        cid = str(receipt.get("candidate_id") or "")
        if cid not in entries:
            continue
        if receipt.get("execution_authorized") is False:
            corrections[cid] = {
                "source": "runtime_revocation",
                "disposition": str(receipt.get("status") or "EXECUTION_AUTHORIZATION_REVOKED_ZERO_AUTHORITY"),
                "corrected_status": "HOLD_HARNESS_RUNTIME_SUPPORT",
                "lane_hint": "HOLD_RUNTIME_SUPPORT",
                "reason": str(receipt.get("reason") or "")[:1800],
                "scientific_authority": False,
            }

    rows = []
    for cid, attention in rank_by.items():
        base = entries[cid]
        base_status = str(base.get("status") or "")
        correction = corrections.get(cid)
        effective_status = str((correction or {}).get("corrected_status") or base_status)
        lane = _lane(effective_status)
        rows.append({
            "candidate_id": cid,
            "scientific_attention_rank": int(attention.get("attention_rank") or 10**9),
            "scientific_attention_score": float(attention.get("attention_score") or 0.0),
            "dimension_scores": deepcopy(attention.get("dimension_scores") or {}),
            "proximity_family": str(attention.get("proximity_family") or ""),
            "base_evidence_status": base_status,
            "effective_operational_status": effective_status,
            "action_lane": lane,
            "correction": deepcopy(correction) if correction else None,
            "scientific_rank_changed_by_overlay": False,
            "scientific_authority": False,
        })
    rows.sort(key=lambda row: row["scientific_attention_rank"])

    actionable_lanes = {
        "CONTINUE_BOUNDED_EVIDENCE": 0,
        "CONTINUE_SUBSTRATE_PREFLIGHT": 1,
        "CONTINUE_HARNESS_IMPLEMENTATION": 2,
        "CONTINUE_INDEPENDENT_REVIEW": 3,
        "CONTINUE_PROTOCOL_REPAIR": 4,
        "NEXT_BOUNDED_EVIDENCE_DESIGN": 5,
    }
    action_queue = sorted(
        [row for row in rows if row["action_lane"] in actionable_lanes],
        key=lambda row: (actionable_lanes[row["action_lane"]], row["scientific_attention_rank"], row["candidate_id"]),
    )
    recommended = []
    used_families = set()
    for row in action_queue:
        family = row["proximity_family"]
        if family and family in used_families:
            continue
        recommended.append(row["candidate_id"])
        if family:
            used_families.add(family)
        if len(recommended) >= max(0, int(next_slots)):
            break
    for row in action_queue:
        if len(recommended) >= max(0, int(next_slots)):
            break
        if row["candidate_id"] not in recommended:
            recommended.append(row["candidate_id"])

    core = {
        "schema_version": SCHEMA_VERSION,
        "status": "ACTIONABILITY_OVERLAY_COMPILED",
        "tournament_result_sha256": tournament.get("tournament_result_sha256"),
        "rows": rows,
        "recommended_next_attention": recommended,
        "lane_counts": {lane: sum(row["action_lane"] == lane for row in rows) for lane in sorted({row["action_lane"] for row in rows})},
        "policy": {
            "scientific_attention_rank_is_never_overwritten": True,
            "operational_holds_only_change_action_lane": True,
            "budget_support_runtime_failures_have_zero_belief_authority": True,
            "overlay_cannot_authorize_or_eliminate_candidates": True,
            "formal_evidence_state_machine_remains_authoritative": True,
        },
        "scientific_authority": False,
        "authority": dict(AUTHORITY),
    }
    core["overlay_sha256"] = _sha(core)
    return core


def reschedule_freshly_promoted_deferred(
    original_plan: dict[str, Any],
    updated_plan: dict[str, Any],
    overlay: dict[str, Any],
    *,
    max_active: int = 4,
) -> dict[str, Any]:
    """Use attention rank only to fill newly freed, never-started evidence slots."""
    from .paper_first_evidence_acquisition import _plan_status, _summary

    original = {str(row.get("candidate_id") or ""): row for row in original_plan.get("entries") or [] if isinstance(row, dict)}
    entries = [deepcopy(row) for row in updated_plan.get("entries") or [] if isinstance(row, dict)]
    by_id = {str(row.get("candidate_id") or ""): row for row in entries}
    if set(original) != set(by_id):
        raise ValueError("original/updated evidence candidate sets differ")

    fresh: list[str] = []
    for cid, row in by_id.items():
        if str(original[cid].get("status") or "") != "DEFERRED_BY_ACTIVE_PORTFOLIO_BUDGET":
            continue
        status = str(row.get("status") or "")
        if status == "NEEDS_BOUNDED_EVIDENCE_DESIGN" and row.get("design_selected") is True:
            if any(row.get(key) for key in ("design", "evidence_review", "substrate_preflight", "harness_implementation", "evidence_receipt")):
                raise ValueError(f"fresh-slot scheduler cannot touch progressed deferred candidate:{cid}")
            fresh.append(cid)
        elif status not in {"DEFERRED_BY_ACTIVE_PORTFOLIO_BUDGET", "NEEDS_BOUNDED_EVIDENCE_DESIGN"}:
            raise ValueError(f"originally deferred candidate progressed beyond reschedulable boundary:{cid}")

    active_statuses = {
        "NEEDS_BOUNDED_EVIDENCE_DESIGN", "NEEDS_OPERATIONALIZATION_RECOMPILE",
        "NEEDS_INDEPENDENT_EVIDENCE_REVIEW", "READY_FOR_BOUNDED_SUBSTRATE_PREFLIGHT",
        "NEEDS_MINIMAL_HARNESS_IMPLEMENTATION", "READY_FOR_BOUNDED_EVIDENCE_ACQUISITION",
        "BRANCH_REPAIR_READY", "RETURN_TO_SEMANTIC_CURRENT_SOURCE_REVIEW",
    }
    for cid in fresh:
        row = by_id[cid]
        row["design_selected"] = False
        row["status"] = "DEFERRED_BY_ACTIVE_PORTFOLIO_BUDGET"
        for key in ("attention_rank", "attention_overlay_sha256", "selection_basis"):
            row.pop(key, None)

    active = sum(row.get("design_selected") is True and str(row.get("status") or "") in active_statuses for row in entries)
    free = max(0, int(max_active) - active)
    rank = {str(row.get("candidate_id") or ""): int(row.get("scientific_attention_rank") or 10**9) for row in overlay.get("rows") or [] if isinstance(row, dict)}
    original_deferred = {cid for cid, row in original.items() if str(row.get("status") or "") == "DEFERRED_BY_ACTIVE_PORTFOLIO_BUDGET"}
    order = [str(cid) for cid in overlay.get("recommended_next_attention") or [] if str(cid) in original_deferred]
    order.extend(cid for cid in sorted(original_deferred, key=lambda value: (rank.get(value, 10**9), value)) if cid not in order)
    selected = order[:free]
    for cid in selected:
        row = by_id[cid]
        if str(row.get("status") or "") != "DEFERRED_BY_ACTIVE_PORTFOLIO_BUDGET":
            raise ValueError(f"attention fill target is not deferred:{cid}")
        row["design_selected"] = True
        row["status"] = "NEEDS_BOUNDED_EVIDENCE_DESIGN"
        row["selection_basis"] = "ATTENTION_TOURNAMENT_FREED_SLOT_ZERO_AUTHORITY"
        row["attention_rank"] = rank.get(cid, 10**9)
        row["attention_overlay_sha256"] = overlay.get("overlay_sha256")
        row["execution_authorized"] = False

    out = deepcopy(updated_plan)
    out["entries"] = entries
    out["summary"] = _summary(entries)
    out["status"] = _plan_status(entries)
    out["portfolio"] = {
        **dict(out.get("portfolio") or {}),
        "freed_slot_scheduler": "attention-tournament-zero-authority",
        "attention_overlay_sha256": overlay.get("overlay_sha256"),
        "newly_selected_candidates": selected,
        "active_candidates": sum(row.get("design_selected") is True and str(row.get("status") or "") in active_statuses for row in entries),
    }
    out["scientific_authority"] = False
    out["authority"] = dict(AUTHORITY)
    return out
