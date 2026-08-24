from __future__ import annotations

from collections import Counter
from typing import Any

from .research_reasoning_layer import CONTRIBUTION_LAYERS

SCHEMA_VERSION = "1.0"

POLICY: dict[str, Any] = {
    "figure_claim_graph_is_compiled_from_registered_claim_evidence_and_visual_receipts": True,
    "writer_consumes_claim_graph_but_cannot_create_evidence": True,
    "affirmative_prose_requires_supported_or_supported_narrowly_claim_with_complete_evidence_trace": True,
    "headline_claim_requires_at_least_one_completed_visual_or_table_surface": True,
    "quantitative_visual_uncertainty_requirement_must_be_visible_when_declared": True,
    "negative_refuted_or_inconclusive_evidence_cannot_be_hidden_by_affirmative_prose": True,
    "graph_has_zero_scientific_authority": True,
    "claim_nodes_may_bind_contribution_layer_without_changing_claim_authority": True,
    "insight_dominant_visual_story_prefers_phenomenon_prediction_intervention_alternative_and_boundary_evidence": True,
}


def build_figure_claim_graph(paper_quality_state: dict[str, Any]) -> dict[str, Any]:
    contract = paper_quality_state.get("quality_contract") or {}
    completion = paper_quality_state.get("completion") or {}
    audit = paper_quality_state.get("audit") or {}
    claim_ledger = audit.get("claim_ledger") or []

    evidence_completion = {
        str(row.get("id")): row for row in completion.get("evidence") or [] if isinstance(row, dict) and row.get("id")
    }
    visual_completion = {
        str(row.get("id")): row for row in completion.get("visualizations") or [] if isinstance(row, dict) and row.get("id")
    }
    visual_plans = {
        str(row.get("id")): row for row in contract.get("visualizations") or [] if isinstance(row, dict) and row.get("id")
    }

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    blockers: list[str] = []

    for row in evidence_completion.values():
        nodes.append({
            "node_id": f"evidence:{row['id']}", "node_type": "EVIDENCE", "evidence_id": row["id"],
            "status": str(row.get("status") or ""), "artifact_refs": list(row.get("artifact_refs") or []),
            "scientific_authority": False,
        })

    claim_ids: set[str] = set()
    for row in claim_ledger:
        if not isinstance(row, dict):
            continue
        cid = str(row.get("claim_id") or "")
        if not cid:
            continue
        claim_ids.add(cid)
        adjudication = str(row.get("adjudication_status") or "")
        trace_complete = row.get("trace_complete") is True
        prose_allowed = adjudication in {"SUPPORTED", "SUPPORTED_NARROWLY"} and trace_complete
        contribution_layer = str(row.get("contribution_layer") or row.get("claim_contribution_layer") or "").strip().lower()
        if contribution_layer not in CONTRIBUTION_LAYERS:
            contribution_layer = ""
        nodes.append({
            "node_id": f"claim:{cid}", "node_type": "CLAIM", "claim_id": cid,
            "claim_type": str(row.get("claim_type") or ""), "claim_text": str(row.get("claim_text") or ""),
            "contribution_layer": contribution_layer,
            "adjudication_status": adjudication, "trace_complete": trace_complete,
            "affirmative_prose_allowed": prose_allowed,
            "must_preserve_negative_or_inconclusive": row.get("must_preserve_negative_or_inconclusive") is True,
            "scientific_authority": False,
        })
        evidence_ids = [str(x) for x in row.get("evidence_ids") or [] if str(x)]
        if not evidence_ids:
            blockers.append(f"claim-without-evidence:{cid}")
        for eid in evidence_ids:
            evidence = evidence_completion.get(eid)
            if evidence is None:
                blockers.append(f"claim-evidence-unregistered:{cid}:{eid}")
            elif str(evidence.get("status") or "") not in {"PASS", "FAIL", "INCONCLUSIVE", "NOT_APPLICABLE"}:
                blockers.append(f"claim-evidence-not-completed:{cid}:{eid}")
            edges.append({"edge_type": "CLAIM_SUPPORTED_BY_EVIDENCE", "source": f"claim:{cid}", "target": f"evidence:{eid}", "scientific_authority": False})

    visual_targets: Counter[str] = Counter()
    for vid, plan in visual_plans.items():
        done = visual_completion.get(vid) or {}
        status = str(done.get("status") or "")
        review = done.get("visual_review") or {}
        targets = [str(x) for x in plan.get("target_claim_ids") or [] if str(x)]
        sources = [str(x) for x in plan.get("source_evidence_ids") or [] if str(x)]
        nodes.append({
            "node_id": f"visual:{vid}", "node_type": "VISUAL", "visual_id": vid,
            "placement": str(plan.get("placement") or ""), "visual_type": str(plan.get("visual_type") or ""),
            "reviewer_question": str(plan.get("reviewer_question") or ""), "takeaway": str(plan.get("takeaway") or ""),
            "quantitative": plan.get("quantitative") is True,
            "uncertainty_required": plan.get("uncertainty_required") is True,
            "negative_or_failure_required": plan.get("negative_or_failure_visible") is True,
            "completion_status": status, "artifact_refs": list(done.get("artifact_refs") or []),
            "script_refs": list(done.get("script_refs") or []), "caption_ref": str(done.get("caption_ref") or ""),
            "visual_review": dict(review), "scientific_authority": False,
        })
        if status != "PASS":
            blockers.append(f"visual-not-complete:{vid}")
        if not str(done.get("caption_ref") or ""):
            blockers.append(f"visual-caption-missing:{vid}")
        if plan.get("quantitative") is True and review.get("source_data_versioned") is not True:
            blockers.append(f"quantitative-visual-data-not-versioned:{vid}")
        if plan.get("uncertainty_required") is True and review.get("uncertainty_visible") is not True:
            blockers.append(f"required-uncertainty-not-visible:{vid}")
        if plan.get("negative_or_failure_visible") is True and review.get("negative_or_failure_visible") is not True:
            blockers.append(f"required-negative-failure-not-visible:{vid}")
        for cid in targets:
            visual_targets[cid] += int(status == "PASS")
            if cid not in claim_ids:
                blockers.append(f"visual-target-claim-unregistered:{vid}:{cid}")
            edges.append({"edge_type": "VISUAL_ADDRESSES_CLAIM", "source": f"visual:{vid}", "target": f"claim:{cid}", "scientific_authority": False})
        for eid in sources:
            if eid not in evidence_completion:
                blockers.append(f"visual-evidence-unregistered:{vid}:{eid}")
            edges.append({"edge_type": "VISUAL_DISPLAYS_EVIDENCE", "source": f"visual:{vid}", "target": f"evidence:{eid}", "scientific_authority": False})

    for cid in claim_ids:
        if visual_targets[cid] == 0:
            blockers.append(f"claim-without-completed-visual-surface:{cid}")

    blockers = sorted(set(blockers))
    contribution_counts = Counter(
        str(node.get("contribution_layer") or "untyped")
        for node in nodes if node.get("node_type") == "CLAIM"
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "paper_id": str(paper_quality_state.get("paper_id") or ""),
        "status": "PASS_FIGURE_CLAIM_GRAPH" if not blockers else "BLOCK_FIGURE_CLAIM_GRAPH",
        "policy": dict(POLICY),
        "nodes": nodes,
        "edges": edges,
        "blockers": blockers,
        "summary": {
            "claims": sum(n.get("node_type") == "CLAIM" for n in nodes),
            "evidence": sum(n.get("node_type") == "EVIDENCE" for n in nodes),
            "visuals": sum(n.get("node_type") == "VISUAL" for n in nodes),
            "edges": len(edges),
            "affirmative_prose_claims": sum(n.get("node_type") == "CLAIM" and n.get("affirmative_prose_allowed") is True for n in nodes),
            "negative_or_inconclusive_claims": sum(n.get("node_type") == "CLAIM" and n.get("must_preserve_negative_or_inconclusive") is True for n in nodes),
            "contribution_layer_counts": dict(contribution_counts),
            "typed_contribution_claims": sum(count for key, count in contribution_counts.items() if key != "untyped"),
            "blockers": len(blockers),
        },
        "scientific_authority": False,
    }


def writer_claim_surface(graph: dict[str, Any]) -> dict[str, Any]:
    allowed = []
    preserved = []
    for node in graph.get("nodes") or []:
        if not isinstance(node, dict) or node.get("node_type") != "CLAIM":
            continue
        row = {"claim_id": node.get("claim_id"), "claim_text": node.get("claim_text"), "adjudication_status": node.get("adjudication_status"), "contribution_layer": node.get("contribution_layer")}
        if node.get("affirmative_prose_allowed") is True:
            allowed.append(row)
        if node.get("must_preserve_negative_or_inconclusive") is True:
            preserved.append(row)
    return {
        "schema_version": SCHEMA_VERSION,
        "affirmative_claims": allowed,
        "must_preserve_negative_or_inconclusive": preserved,
        "writer_can_create_evidence": False,
        "scientific_authority": False,
    }
