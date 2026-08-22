from __future__ import annotations

from collections import Counter
from typing import Any, Mapping


RESEARCH_ACTION_BY_STATE = {
    "STOPPED": "NO_INTERNAL_ACTION",
    "MERGED": "MERGED_NO_STANDALONE_ACTION",
    "HOLD": "REOPEN_CONDITION_REQUIRED",
    "PAPER_READY": "PAPERSTATE_HANDOFF",
}


def _rows(payload: Mapping[str, Any], key: str) -> list[dict[str, Any]]:
    return [dict(row) for row in payload.get(key) or [] if isinstance(row, Mapping)]


def _paper_key(row: Mapping[str, Any]) -> str:
    return str(row.get("acceptance_paper_id") or row.get("paper_id") or "")


def validate_public_control_plane(
    *,
    research_state: Mapping[str, Any],
    paper_registry: Mapping[str, Any],
    research_system: Mapping[str, Any],
    research_dashboard: Mapping[str, Any],
    research_memory: Mapping[str, Any],
) -> list[str]:
    """Validate read-only public projections against one another without granting authority."""
    errors: list[str] = []

    research_items = _rows(research_state, "research_items")
    research_by_code = {str(row.get("code") or ""): row for row in research_items}
    research_summary = research_state.get("summary") or {}
    research_action_counts = Counter()
    for row in research_items:
        code = str(row.get("code") or "")
        state = str(row.get("scientific_state") or "")
        action = row.get("primary_next_action") or {}
        action_class = str(action.get("action_class") or "")
        research_action_counts[action_class or "UNKNOWN"] += 1
        expected = RESEARCH_ACTION_BY_STATE.get(state, "INTERNAL_REVIEW_REQUIRED")
        if action_class != expected:
            errors.append(f"ResearchItem action mismatch:{code}:{state}->{action_class}")
        if action.get("machine_actionable") is not False or any(action.get(key) is not False for key in ("scientific_authority", "experiment_authority", "p0_authority", "gpu_authority")):
            errors.append(f"ResearchItem action authority leak:{code}")
    if dict(sorted(research_action_counts.items())) != dict(research_summary.get("primary_next_action_counts") or {}):
        errors.append("ResearchItem action summary mismatch")
    if int(research_summary.get("machine_actionable_research_items") or 0) != 0:
        errors.append("ResearchItem machine-actionable count must remain zero")

    papers = _rows(paper_registry, "papers")
    registry_summary = paper_registry.get("summary") or {}
    registry_by_key = {_paper_key(row): row for row in papers}
    derived_registry = {
        "papers": len(papers),
        "submission_ready": sum(row.get("submission_ready") is True for row in papers),
        "gate_clean_submission_ready": sum(row.get("gate_clean_submission_ready") is True for row in papers),
        "paper_preparation_failed": sum(int(((row.get("latest_paper_preparation") or {}).get("required_gates") or 0)) > 0 and (row.get("latest_paper_preparation") or {}).get("pass") is not True for row in papers),
        "immediate_submission_holds": sum(row.get("immediate_submission_hold") is True for row in papers),
        "internal_action_required": sum((row.get("primary_next_action") or {}).get("action_class") != "NO_INTERNAL_ACTION" for row in papers),
        "no_internal_action": sum((row.get("primary_next_action") or {}).get("action_class") == "NO_INTERNAL_ACTION" for row in papers),
    }
    for key, value in derived_registry.items():
        if int(registry_summary.get(key) or 0) != int(value):
            errors.append(f"PaperRegistry summary mismatch:{key}")

    paper_acceptance = research_system.get("paper_acceptance") or {}
    system_paper_summary = paper_acceptance.get("summary") or {}
    ledger_index = paper_acceptance.get("ledger_index") or {}
    ledger_entries = _rows(ledger_index, "entries")
    ledger_by_key = {str(row.get("paper_id") or ""): row for row in ledger_entries}
    expected_system_summary = {
        "registered_papers": registry_summary.get("papers"),
        "ledger_submission_ready_papers": registry_summary.get("submission_ready"),
        "submission_ready_papers": registry_summary.get("submission_ready"),
        "gate_clean_submission_ready_papers": registry_summary.get("gate_clean_submission_ready"),
        "paper_preparation_failed_papers": registry_summary.get("paper_preparation_failed"),
        "immediate_submission_holds": registry_summary.get("immediate_submission_holds"),
        "internal_action_required_papers": registry_summary.get("internal_action_required"),
        "no_internal_action_papers": registry_summary.get("no_internal_action"),
    }
    for key, value in expected_system_summary.items():
        if int(system_paper_summary.get(key) or 0) != int(value or 0):
            errors.append(f"ResearchSystem Paper Acceptance summary mismatch:{key}")
    if set(registry_by_key) != set(ledger_by_key):
        errors.append("PaperRegistry and ResearchSystem ledger IDs differ")
    for paper_id in sorted(set(registry_by_key) & set(ledger_by_key)):
        registry_row = registry_by_key[paper_id]
        ledger_row = ledger_by_key[paper_id]
        for key in ("current_state", "gate_clean_submission_ready", "immediate_submission_hold"):
            if registry_row.get(key) != ledger_row.get(key):
                errors.append(f"Paper row mismatch:{paper_id}:{key}")
        registry_action = registry_row.get("primary_next_action") or {}
        ledger_action = ledger_row.get("primary_next_action") or {}
        for key in ("action_class", "blocking_on"):
            if registry_action.get(key) != ledger_action.get(key):
                errors.append(f"Paper action mismatch:{paper_id}:{key}")
        if (registry_row.get("review_learning") or {}) != (ledger_row.get("review_learning") or {}):
            errors.append(f"Paper review-learning mismatch:{paper_id}")

    dashboard_summary = research_dashboard.get("summary") or {}
    expected_dashboard = {
        "portfolio_objects": research_summary.get("portfolio_objects"),
        "research_items": research_summary.get("research_items"),
        "paper_ready": (research_summary.get("scientific_state_counts") or {}).get("PAPER_READY", 0),
        "holds": (research_summary.get("scientific_state_counts") or {}).get("HOLD", 0),
        "research_handoffs": sum((row.get("primary_next_action") or {}).get("action_class") == "PAPERSTATE_HANDOFF" for row in research_items),
        "research_waiting_reopen": sum((row.get("primary_next_action") or {}).get("action_class") == "REOPEN_CONDITION_REQUIRED" for row in research_items),
        "machine_actionable_attention": 0,
        "papers": registry_summary.get("papers"),
        "submission_ready": registry_summary.get("gate_clean_submission_ready"),
        "ledger_submission_ready": registry_summary.get("submission_ready"),
        "immediate_submission_holds": registry_summary.get("immediate_submission_holds"),
        "paper_internal_action_required": registry_summary.get("internal_action_required"),
        "paper_no_internal_action": registry_summary.get("no_internal_action"),
        "machine_actionable_research_items": research_summary.get("machine_actionable_research_items"),
    }
    for key, value in expected_dashboard.items():
        if int(dashboard_summary.get(key) or 0) != int(value or 0):
            errors.append(f"ResearchDashboard summary mismatch:{key}")
    if dict(dashboard_summary.get("research_primary_next_action_counts") or {}) != dict(research_summary.get("primary_next_action_counts") or {}):
        errors.append("ResearchDashboard ResearchItem action distribution mismatch")
    attention = _rows(research_dashboard, "attention")
    expected_attention_codes = {code for code, row in research_by_code.items() if row.get("scientific_state") in {"PAPER_READY", "HOLD"}}
    if {str(row.get("code") or "") for row in attention} != expected_attention_codes:
        errors.append("ResearchDashboard attention set differs from canonical ResearchItems")
    for row in attention:
        code = str(row.get("code") or "")
        source = research_by_code.get(code) or {}
        if row.get("next_action_class") != (source.get("primary_next_action") or {}).get("action_class"):
            errors.append(f"ResearchDashboard action mismatch:{code}")
        if (row.get("primary_next_action") or {}).get("machine_actionable") is not False:
            errors.append(f"ResearchDashboard action authority leak:{code}")

    dashboard_papers = {str(row.get("paper_id") or ""): row for row in _rows(research_dashboard, "papers")}
    registry_by_public_id = {str(row.get("paper_id") or ""): row for row in papers}
    if set(dashboard_papers) != set(registry_by_public_id):
        errors.append("ResearchDashboard paper IDs differ from PaperRegistry")
    for paper_id in sorted(set(dashboard_papers) & set(registry_by_public_id)):
        if dashboard_papers[paper_id].get("next_action_class") != (registry_by_public_id[paper_id].get("primary_next_action") or {}).get("action_class"):
            errors.append(f"ResearchDashboard paper action mismatch:{paper_id}")

    review_lessons = [row for row in _rows(research_memory, "entries") if row.get("kind") == "REVIEW_LESSON"]
    lessons_by_paper = {str(row.get("candidate_id") or ""): row for row in review_lessons}
    expected_review_papers = {paper_id for paper_id, row in ledger_by_key.items() if int(((row.get("review_learning") or {}).get("review_receipts") or 0)) > 0}
    if set(lessons_by_paper) != expected_review_papers:
        errors.append("ResearchMemory review lessons do not match reviewed PaperStates")
    if int((research_memory.get("summary") or {}).get("review_lessons") or 0) != len(review_lessons):
        errors.append("ResearchMemory review-lesson summary mismatch")
    for paper_id, lesson in lessons_by_paper.items():
        if lesson.get("scientific_authority") is not False or lesson.get("principle_update_allowed") is not False:
            errors.append(f"ResearchMemory review lesson authority leak:{paper_id}")
        if lesson.get("affected_layer") != "paper_review":
            errors.append(f"ResearchMemory review lesson layer mismatch:{paper_id}")

    return sorted(set(errors))
