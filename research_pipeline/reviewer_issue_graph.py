from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from typing import Any, Iterable

SCHEMA_VERSION = "1.0"

POLICY: dict[str, Any] = {
    "reviewer_issue_graph_structures_objections_without_granting_reviewer_authority": True,
    "public_projection_exposes_issue_structure_not_reviewer_prose": True,
    "review_issue_priority_is_decision_value_per_repair_cost_not_a_truth_score": True,
    "targeted_experiment_action_is_a_proposal_not_execution_authority": True,
    "claim_expansion_requests_default_to_preserved_limitation": True,
    "meta_review_explains_disagreement_and_missing_evidence_instead_of_voting": True,
    "discovery_lesson_requires_repeated_resolved_pattern_across_papers": True,
    "one_off_reviewer_comment_cannot_auto_mutate_research_memory": True,
}


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(value or "").strip().lower()).strip("-")


def _priority_components(objection: dict[str, Any], action_class: str) -> tuple[int, int, int, float]:
    impact = 3 if objection.get("decision_critical") is True else 1
    evidence_state = _key(objection.get("evidence_state"))
    validity = {
        "missing-decisive-evidence": 3,
        "false-premise-with-evidence": 3,
        "existing-evidence": 2,
        "requires-new-claim": 2,
        "uncertain": 2,
    }.get(evidence_state, 1)
    cost = {
        "narrative-repair": 1,
        "prebuttal": 1,
        "preserve-limitation": 1,
        "human-adjudication": 2,
        "targeted-experiment": 3,
    }.get(action_class, 2)
    score = round((impact * validity) / max(1, cost), 4)
    return impact, validity, cost, score


def build_reviewer_issue_graph(
    *, paper_id: str, review_receipts: Iterable[dict[str, Any]],
    resolutions: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    resolutions = resolutions or {}
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    issue_ids: set[str] = set()
    blockers: list[str] = []

    for receipt in review_receipts:
        if not isinstance(receipt, dict):
            continue
        review_sha = str(receipt.get("review_sha256") or "")
        actions = {
            str(row.get("objection_id")): row
            for row in receipt.get("actions") or [] if isinstance(row, dict) and row.get("objection_id")
        }
        for objection in receipt.get("objections") or []:
            if not isinstance(objection, dict):
                continue
            oid = str(objection.get("objection_id") or "")
            if not oid:
                blockers.append("objection-id-missing")
                continue
            scoped_id = f"{review_sha[:12] or 'review'}:{oid}"
            if scoped_id in issue_ids:
                blockers.append(f"duplicate-reviewer-issue:{scoped_id}")
                continue
            issue_ids.add(scoped_id)
            action = actions.get(oid) or {}
            action_class = _key(action.get("action_class") or "human-adjudication")
            impact, validity, cost, score = _priority_components(objection, action_class)
            resolution = resolutions.get(scoped_id) or resolutions.get(oid) or {}
            resolved = resolution.get("resolved") is True
            evidence_refs = [str(x) for x in resolution.get("evidence_refs") or [] if str(x)]
            manuscript_delta_refs = [str(x) for x in resolution.get("manuscript_delta_refs") or [] if str(x)]
            verification = str(resolution.get("verification") or "")
            if resolved and not (evidence_refs or manuscript_delta_refs or verification):
                blockers.append(f"resolved-issue-without-verification:{scoped_id}")
                resolved = False
            text = str(objection.get("text") or "")
            claim_ids = [str(x) for x in objection.get("claim_ids") or [] if str(x)]
            node = {
                "node_id": f"issue:{scoped_id}",
                "node_type": "REVIEWER_ISSUE",
                "issue_id": scoped_id,
                "source_review_sha256": review_sha,
                "original_comment_sha256": _digest(text) if text else "",
                "reviewer_prose_exposed": False,
                "underlying_concern": str(objection.get("category") or "unknown"),
                "affected_claim_ids": claim_ids,
                "decision_critical": objection.get("decision_critical") is True,
                "evidence_state": _key(objection.get("evidence_state") or "unknown"),
                "action_class": action_class,
                "experiment_required": action_class == "targeted-experiment",
                "experiment_authorized": False,
                "claim_expansion_authorized": action.get("claim_expansion_authorized") is True,
                "priority": {"decision_impact": impact, "scientific_validity": validity, "repair_cost": cost, "value_per_cost": score},
                "status": "RESOLVED" if resolved else "OPEN",
                "resolution": {"evidence_refs": evidence_refs, "manuscript_delta_refs": manuscript_delta_refs, "verification": verification},
                "scientific_authority": False,
            }
            nodes.append(node)
            for cid in claim_ids:
                edges.append({"edge_type": "ISSUE_AFFECTS_CLAIM", "source": node["node_id"], "target": f"claim:{cid}", "scientific_authority": False})
            if action_class == "targeted-experiment":
                edges.append({"edge_type": "ISSUE_PROPOSES_EXPERIMENT", "source": node["node_id"], "target": f"experiment-proposal:{scoped_id}", "execution_authority": False, "scientific_authority": False})

    nodes.sort(key=lambda row: (-float((row.get("priority") or {}).get("value_per_cost") or 0), str(row.get("issue_id") or "")))
    blockers = sorted(set(blockers))
    open_nodes = [row for row in nodes if row.get("status") == "OPEN"]
    return {
        "schema_version": SCHEMA_VERSION,
        "paper_id": str(paper_id),
        "status": "PASS_REVIEWER_ISSUE_GRAPH" if not blockers else "BLOCK_REVIEWER_ISSUE_GRAPH",
        "policy": dict(POLICY),
        "nodes": nodes,
        "edges": edges,
        "blockers": blockers,
        "summary": {
            "issues": len(nodes),
            "open": len(open_nodes),
            "resolved": len(nodes) - len(open_nodes),
            "decision_critical_open": sum(row.get("decision_critical") is True for row in open_nodes),
            "targeted_experiment_proposals": sum(row.get("experiment_required") is True for row in open_nodes),
            "experiment_authorized": 0,
            "blockers": len(blockers),
        },
        "scientific_authority": False,
    }


def build_meta_review(graph: dict[str, Any]) -> dict[str, Any]:
    by_claim: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for node in graph.get("nodes") or []:
        if not isinstance(node, dict) or node.get("node_type") != "REVIEWER_ISSUE":
            continue
        for cid in node.get("affected_claim_ids") or []:
            by_claim[str(cid)].append(node)
    disagreements = []
    for cid, rows in sorted(by_claim.items()):
        evidence_states = sorted({str(row.get("evidence_state") or "") for row in rows})
        action_classes = sorted({str(row.get("action_class") or "") for row in rows})
        if len(evidence_states) > 1 or len(action_classes) > 1:
            disagreements.append({
                "claim_id": cid,
                "issue_ids": [str(row.get("issue_id") or "") for row in rows],
                "evidence_states": evidence_states,
                "action_classes": action_classes,
                "resolution_question": "Which admissible evidence or frozen claim boundary explains the reviewer disagreement?",
            })
    open_nodes = [row for row in graph.get("nodes") or [] if isinstance(row, dict) and row.get("status") == "OPEN"]
    decisive_missing = [row for row in open_nodes if row.get("decision_critical") is True and str(row.get("evidence_state") or "").lower() == "missing-decisive-evidence"]
    return {
        "schema_version": SCHEMA_VERSION,
        "paper_id": graph.get("paper_id"),
        "status": "META_REVIEW_COMPILED",
        "disagreement_clusters": disagreements,
        "highest_priority_open_issue_ids": [str(row.get("issue_id") or "") for row in open_nodes[:5]],
        "decision_critical_missing_evidence_issue_ids": [str(row.get("issue_id") or "") for row in decisive_missing],
        "vote_or_score_is_scientific_authority": False,
        "scientific_authority": False,
        "experiment_authority": False,
    }


def build_review_control_state_from_registry(paper_registry: dict[str, Any]) -> dict[str, Any]:
    rows = []
    global_categories: Counter[str] = Counter()
    global_actions: Counter[str] = Counter()
    for paper in (paper_registry.get("papers") or paper_registry.get("entries") or []):
        if not isinstance(paper, dict):
            continue
        learning = paper.get("review_learning") or {}
        categories = {str(k): int(v or 0) for k, v in (learning.get("category_counts") or {}).items()}
        actions = {str(k): int(v or 0) for k, v in (learning.get("action_class_counts") or {}).items()}
        global_categories.update(categories)
        global_actions.update(actions)
        rows.append({
            "paper_id": str(paper.get("paper_id") or ""),
            "current_state": str(paper.get("current_state") or ""),
            "review_receipts": int(learning.get("review_receipts") or 0),
            "decision_critical_objections": int(learning.get("decision_critical_objections") or 0),
            "targeted_experiment_proposals": int(learning.get("targeted_experiment_proposals") or 0),
            "category_counts": categories,
            "action_class_counts": actions,
            "reviewer_prose_exposed": False,
            "scientific_authority": False,
        })
    repeated = [
        {"pattern": category, "cross_paper_count": sum(int((row.get("category_counts") or {}).get(category) or 0) > 0 for row in rows), "total_objections": count,
         "eligible_for_discovery_lesson_review": sum(int((row.get("category_counts") or {}).get(category) or 0) > 0 for row in rows) >= 2,
         "automatic_memory_promotion": False}
        for category, count in global_categories.most_common()
        if sum(int((row.get("category_counts") or {}).get(category) or 0) > 0 for row in rows) >= 2
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "REVIEW_CONTROL_STATE_COMPILED",
        "policy": dict(POLICY),
        "papers": rows,
        "repeated_issue_patterns": repeated,
        "summary": {
            "papers": len(rows),
            "review_receipts": sum(row["review_receipts"] for row in rows),
            "decision_critical_objections": sum(row["decision_critical_objections"] for row in rows),
            "targeted_experiment_proposals": sum(row["targeted_experiment_proposals"] for row in rows),
            "repeated_cross_paper_patterns": len(repeated),
            "automatic_memory_promotions": 0,
        },
        "scientific_authority": False,
    }
