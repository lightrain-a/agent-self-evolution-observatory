from __future__ import annotations

from typing import Any


SCHEMA_VERSION = "1.0"

SOFT_CAPACITY_TARGETS = {
    "active_problem_lines": 3,
    "search_hold_min": 5,
    "search_hold_max": 10,
}

POLICY: dict[str, Any] = {
    "schema_version": SCHEMA_VERSION,
    "portfolio_is_a_persistence_and_capacity_view_not_a_scientific_gate": True,
    "portfolio_cannot_promote_candidate_stage": True,
    "portfolio_cannot_authorize_problem_method_experiment_p0_or_gpu": True,
    "pre_f0_hold_is_not_problem_gate_pass": True,
    "problem_gate_pass_is_only_paper_design_eligibility": True,
    "soft_capacity_targets_do_not_relax_scientific_thresholds": True,
    "multiple_candidates_may_remain_visible_while_one_line_is_blocked": True,
    "pre_f0_adjudication_can_close_current_formulation_without_promotion": True,
}

_STAGE_PRIORITY = {
    "GENERATOR_REVIEW": 10,
    "PRE_F0_EVIDENCE_ACQUISITION": 20,
    "PRE_F0_ADJUDICATION": 25,
    "PROBLEM_GATE": 30,
    "PAPER_DESIGN_BACKLOG": 40,
}


def _rows(value: Any) -> list[dict[str, Any]]:
    return [row for row in (value or []) if isinstance(row, dict)] if isinstance(value, list) else []


def _text(value: Any) -> str:
    return str(value or "").strip()


def _candidate_id(row: dict[str, Any]) -> str:
    return _text(row.get("candidate_id") or row.get("id") or row.get("idea_id"))


def _put(index: dict[str, dict[str, Any]], row: dict[str, Any]) -> None:
    cid = _candidate_id(row)
    if not cid:
        return
    old = index.get(cid)
    if old is None or _STAGE_PRIORITY.get(str(row.get("stage") or ""), 0) >= _STAGE_PRIORITY.get(str(old.get("stage") or ""), 0):
        index[cid] = row


def build_research_candidate_portfolio(
    *,
    generator_state: dict[str, Any],
    pre_f0_state: dict[str, Any],
    problem_gate_state: dict[str, Any],
    paper_design_backlog_state: dict[str, Any],
    pre_f0_adjudication_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compile existing candidate surfaces into one zero-authority persistent portfolio.

    The compiler never changes a source candidate's scientific status.  It only keeps
    simultaneous lines visible and reports capacity pressure so a blocked main line does
    not erase adjacent candidates from the operator's view.
    """
    index: dict[str, dict[str, Any]] = {}

    for row in _rows(generator_state.get("candidates")):
        _put(index, {
            "candidate_id": _candidate_id(row),
            "title": _text(row.get("title")),
            "stage": "GENERATOR_REVIEW",
            "portfolio_state": "SEARCH_REVIEW",
            "source_status": _text(generator_state.get("status")),
            "discovery_lane": _text(row.get("discovery_lane")),
            "scientific_authority": False,
        })

    for row in _rows(pre_f0_state.get("rows")):
        _put(index, {
            "candidate_id": _candidate_id(row),
            "title": _text(row.get("title")),
            "stage": "PRE_F0_EVIDENCE_ACQUISITION",
            "portfolio_state": "SEARCH_HOLD",
            "source_status": _text(pre_f0_state.get("status")),
            "discovery_lane": _text(row.get("discovery_lane")),
            "reduction_blockers": [str(value) for value in row.get("reduction_blockers") or [] if str(value)],
            "route_reason": _text(row.get("route_reason")),
            "scientific_authority": False,
        })

    for row in _rows((pre_f0_adjudication_state or {}).get("entries")):
        if row.get("scientific_authority") is not False:
            continue
        portfolio_state = _text(row.get("portfolio_state"))
        if portfolio_state not in {"SEARCH_STOP_CURRENT_FORMULATION", "SEARCH_REVIEW", "SEARCH_HOLD"}:
            continue
        _put(index, {
            "candidate_id": _candidate_id(row),
            "candidate_identity_version": _text(row.get("candidate_identity_version")),
            "candidate_snapshot_sha256": _text(row.get("candidate_snapshot_sha256")),
            "title": _text(row.get("title")),
            "stage": "PRE_F0_ADJUDICATION",
            "portfolio_state": portfolio_state,
            "source_status": _text(row.get("status")),
            "discovery_lane": _text(row.get("discovery_lane")),
            "reopen_only_if": _text(row.get("reopen_only_if")),
            "paper_design_eligible": False,
            "scientific_authority": False,
        })

    for key, portfolio_state in (("audited", "PROBLEM_GATE_AUDITED"), ("passed", "ACTIVE_PAPER_PROBLEM"), ("blocked", "PROBLEM_GATE_BLOCKED")):
        for row in _rows(problem_gate_state.get(key)):
            _put(index, {
                "candidate_id": _candidate_id(row),
                "title": _text(row.get("title")),
                "stage": "PROBLEM_GATE",
                "portfolio_state": portfolio_state,
                "source_status": _text(row.get("status") or row.get("decision")),
                "discovery_lane": _text(row.get("discovery_lane")),
                "paper_design_eligible": portfolio_state == "ACTIVE_PAPER_PROBLEM",
                "scientific_authority": False,
            })

    for row in _rows(paper_design_backlog_state.get("entries")):
        _put(index, {
            "candidate_id": _candidate_id(row),
            "title": _text(row.get("title")),
            "stage": "PAPER_DESIGN_BACKLOG",
            "portfolio_state": "ACTIVE_PAPER_DESIGN_REVIEW",
            "source_status": _text(row.get("status")),
            "paper_design_eligible": True,
            "scientific_authority": False,
        })

    rows = sorted(index.values(), key=lambda row: (-_STAGE_PRIORITY.get(str(row.get("stage") or ""), 0), str(row.get("candidate_id") or "")))
    active = sum(str(row.get("portfolio_state") or "").startswith("ACTIVE_") for row in rows)
    search_holds = sum(row.get("portfolio_state") in {"SEARCH_HOLD", "SEARCH_REVIEW"} for row in rows)
    blocked = sum(row.get("portfolio_state") == "PROBLEM_GATE_BLOCKED" for row in rows)
    stopped_current = sum(row.get("portfolio_state") == "SEARCH_STOP_CURRENT_FORMULATION" for row in rows)
    targets = dict(SOFT_CAPACITY_TARGETS)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "PORTFOLIO_ACTIVE" if rows else "PORTFOLIO_EMPTY",
        "policy": dict(POLICY),
        "soft_capacity_targets": targets,
        "summary": {
            "visible_candidates": len(rows),
            "active_problem_lines": active,
            "search_holds": search_holds,
            "problem_gate_blocked": blocked,
            "search_stopped_current_formulation": stopped_current,
            "active_target": targets["active_problem_lines"],
            "active_shortfall": max(0, targets["active_problem_lines"] - active),
            "search_hold_min_target": targets["search_hold_min"],
            "search_hold_shortfall": max(0, targets["search_hold_min"] - search_holds),
            "automatic_promotions": 0,
        },
        "rows": rows,
        "scientific_authority": False,
        "authority": {
            "problem_gate": False,
            "paper_design": False,
            "method": False,
            "experiment": False,
            "p0": False,
            "gpu": False,
        },
    }
