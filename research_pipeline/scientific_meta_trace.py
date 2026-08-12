from __future__ import annotations

from collections import defaultdict
from typing import Any


POLICY: dict[str, Any] = {
    "schema_version": "1.0",
    "raw_execution_trace_is_not_scientific_state": True,
    "scientific_state_is_compact_and_branch_aware": True,
    "failed_branches_remain_retrievable": True,
    "cross_branch_reference_edges_allowed": True,
    "one_experiment_updates_only_explicit_belief_targets": True,
    "every_belief_update_requires_artifact_or_primary_source_provenance": True,
    "unresolved_uncertainty_must_be_named_before_next_experiment": True,
    "active_scientific_state_is_separate_from_institutional_memory": True,
    "active_scientific_state_never_time_decays": True,
    "institutional_memory_requires_scope_and_effectiveness_tracking": True,
}

REFERENCES = [
    {"system": "Qiushi Discovery Engine", "adopted": "Meta-Trace memory and nonlinear research phases for long-horizon coherence"},
    {"system": "Kosmos", "adopted": "structured world model shared across literature and analysis agents"},
    {"system": "MLEvolve", "adopted": "cross-branch reference edges and retrospective global memory"},
    {"system": "AutoResearchClaw", "adopted": "cross-run failures become reusable safeguards rather than disappearing with one run"},
    {"system": "AutoSci", "adopted": "separate Active Research Memory from Long-Term Knowledge Memory and evolve memory/skills/workflows through versioned updates"},
]


def _unique_principle_cards(pre_experiment: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for card in pre_experiment.get("cards") or []:
        audit = card.get("principle_certificate_prerequisite") or {}
        pid = str(audit.get("principle_id") or "")
        if pid and pid not in out:
            out[pid] = {"idea_id": str(card.get("idea_id") or ""), "audit": audit}
    return out


def build_scientific_meta_trace(
    pre_experiment: dict[str, Any],
    principle_layer: dict[str, Any],
    experiment_iteration: dict[str, Any],
    decision_ledger: dict[str, Any] | None = None,
    historical_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    principles = _unique_principle_cards(pre_experiment)
    cards_by_idea: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for card in pre_experiment.get("cards") or []:
        cards_by_idea[str(card.get("idea_id") or "")].append(card)

    adjudications_by_principle: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in principle_layer.get("adjudications") or []:
        adjudications_by_principle[str(row.get("principle_id") or "")].append(row)

    nodes_by_idea = {str(node.get("idea_id") or ""): node for node in experiment_iteration.get("nodes") or []}
    traces: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    for pid, item in principles.items():
        idea_id = item["idea_id"]
        audit = item["audit"]
        contract = audit.get("contract") or {}
        blockers = sorted({str(blocker) for card in cards_by_idea.get(idea_id, []) for blocker in card.get("blockers") or []})
        adjudications = adjudications_by_principle.get(pid, [])
        if any(row.get("principle_falsified") for row in adjudications):
            belief_state = "falsified"
        elif any(row.get("verdict") == "PRINCIPLE_SUPPORTED_NOT_PROVEN" for row in adjudications):
            belief_state = "supported-not-proven"
        else:
            belief_state = "unresolved"
        node = nodes_by_idea.get(idea_id) or {}
        next_uncertainty = blockers[0] if blockers else str(node.get("diagnosis") or "no-current-blocker")
        traces.append({
            "principle_id": pid,
            "idea_id": idea_id,
            "mechanism": str(contract.get("mechanism") or ""),
            "belief_state": belief_state,
            "registered_predictions": [str(row.get("id") or "") for row in contract.get("predictions") or []],
            "current_blockers": blockers,
            "latest_diagnosis": str(node.get("diagnosis") or ""),
            "latest_belief_targets": sorted({str(row.get("scientific_belief_target") or "none") for row in adjudications}),
            "evidence_refs": sorted({ref for ref in [str(node.get("artifact_dir") or "")] + [str(card.get("qualification_evidence_path") or "") for card in cards_by_idea.get(idea_id, [])] if ref}),
            "next_uncertainty": next_uncertainty,
        })
        if belief_state == "unresolved":
            unresolved.append({"principle_id": pid, "idea_id": idea_id, "uncertainty": next_uncertainty})

    by_diagnosis: dict[str, list[str]] = defaultdict(list)
    by_operator: dict[str, list[str]] = defaultdict(list)
    for node in experiment_iteration.get("nodes") or []:
        idea = str(node.get("idea_id") or "")
        by_diagnosis[str(node.get("diagnosis") or "unknown")].append(idea)
        for child in node.get("repair_children") or []:
            by_operator[str(child.get("operator") or "unknown")].append(idea)

    reference_edges: list[dict[str, Any]] = []
    for relation, groups in (("shared-diagnosis", by_diagnosis), ("shared-repair-operator", by_operator)):
        for key, ideas in groups.items():
            unique = sorted(set(ideas))
            if len(unique) >= 2:
                reference_edges.append({"relation": relation, "key": key, "ideas": unique})

    historical_boundary_evidence: list[dict[str, Any]] = []
    for record in (historical_evidence or {}).get("records") or []:
        historical_boundary_evidence.append({
            "evidence_id": str(record.get("evidence_id") or ""),
            "domain": str(record.get("domain") or ""),
            "phase": str(record.get("phase") or ""),
            "original_decision": str(record.get("original_decision") or ""),
            "original_decision_preserved": bool(record.get("original_decision_preserved")),
            "evidence_timing": str(record.get("evidence_timing") or "historical"),
            "evidence_class": str(record.get("evidence_class") or "historical"),
            "diagnosis": str(record.get("diagnosis") or ""),
            "affected_scientific_layer": str(record.get("affected_scientific_layer") or ""),
            "scope_refinement": str(record.get("scope_refinement") or ""),
            "active_principle_belief_update_allowed": bool(record.get("active_principle_belief_update_allowed")),
            "principle_falsified": bool(record.get("principle_falsified")),
            "execution_authorized": bool(record.get("execution_authorized")),
            "reusable_precheck": str(record.get("reusable_precheck") or ""),
            "paper_relationship": record.get("paper_relationship") or {},
            "provenance": record.get("provenance") or {},
        })

    ledger_summary = (decision_ledger or {}).get("summary") or {}
    return {
        "schema_version": "1.0",
        "policy": POLICY,
        "references": REFERENCES,
        "summary": {
            "principles": len(traces),
            "unresolved_principles": len(unresolved),
            "cross_branch_reference_edges": len(reference_edges),
            "current_launchable": int(ledger_summary.get("launchable") or 0),
            "historical_boundary_evidence": len(historical_boundary_evidence),
            "historical_active_principle_belief_updates": sum(bool(row.get("active_principle_belief_update_allowed")) for row in historical_boundary_evidence),
            "historical_execution_authorized": sum(bool(row.get("execution_authorized")) for row in historical_boundary_evidence),
        },
        "principles": traces,
        "historical_boundary_evidence": historical_boundary_evidence,
        "unresolved_questions": unresolved,
        "cross_branch_reference_edges": reference_edges,
        "memory_scopes": {
            "active_scientific_state": {
                "contains": ["current principle certificates", "current predictions", "current experiment state", "current decision authority"],
                "time_decay_allowed": False,
                "rule": "Current-project scientific truth is authority-bound state and cannot be weakened or rewritten by memory aging.",
            },
            "institutional_research_memory": {
                "contains": ["reusable failure assets", "post-hoc boundary evidence", "validated workflow lessons", "retrieval/tool effectiveness", "cross-project safeguards"],
                "time_decay_allowed": True,
                "rule": "Reusable cross-project memory must carry scope, validation age, and observed helpful/harmful reuse before affecting future planning.",
            },
        },
    }
