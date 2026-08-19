from __future__ import annotations

import hashlib
from collections import Counter
from typing import Any


SCHEMA_VERSION = "1.1"

POLICY: dict[str, Any] = {
    "schema_version": SCHEMA_VERSION,
    "graph_is_a_derived_traceability_view_not_scientific_authority": True,
    "existing_evidence_graph_is_referenced_not_duplicated": True,
    "paper_idea_claim_experiment_principle_failure_and_closure_are_distinct_node_kinds": True,
    "experiment_failure_edge_cannot_close_core_principle": True,
    "only_certified_principle_dead_end_may_emit_principle_closure_edge": True,
    "search_closure_and_scientific_dead_end_are_distinct": True,
    "failure_assets_preserve_affected_layer_and_does_not_imply_scope": True,
    "candidate_portfolio_stage_does_not_promote_scientific_status": True,
}


def _text(value: Any) -> str:
    return str(value or "").strip()


def _short_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def _idea_node_id(idea_id: str) -> str:
    return f"idea:{idea_id}"


def build_scientific_research_graph(
    *,
    evidence_graph: dict[str, Any],
    candidate_portfolio: dict[str, Any],
    scientific_meta_trace: dict[str, Any],
    failure_asset_library: dict[str, Any],
    pilot_registry: dict[str, Any],
) -> dict[str, Any]:
    """Compile a typed overlay over the existing evidence graph.

    The large literature/evidence graph is already canonical state.  Re-copying every
    paper/claim/idea node into a second graph makes public snapshots large and creates a
    needless second source of truth.  This compiler therefore stores only the scientific
    overlay (candidate stage, principles, experiment phases, failure assets, and certified
    closures) and references the existing graph by identity.  Summary counts are computed
    over the conceptual union for observability.
    """
    base_nodes = [row for row in evidence_graph.get("nodes") or [] if isinstance(row, dict) and _text(row.get("id"))]
    base_edges = [row for row in evidence_graph.get("edges") or [] if isinstance(row, dict)]
    base_ids = {_text(row.get("id")) for row in base_nodes}
    base_node_kinds = Counter(_text(row.get("kind")) or "evidence_object" for row in base_nodes)
    base_relations = Counter(_text(row.get("relation")) or "related" for row in base_edges)

    overlay_nodes: dict[str, dict[str, Any]] = {}
    overlay_edges: list[dict[str, Any]] = []

    def ensure_idea(idea_id: str, source: str) -> str:
        node_id = _idea_node_id(idea_id)
        if node_id not in base_ids:
            overlay_nodes.setdefault(node_id, {"id": node_id, "kind": "idea", "label": idea_id, "source": source})
        return node_id

    for row in candidate_portfolio.get("rows") or []:
        if not isinstance(row, dict):
            continue
        cid = _text(row.get("candidate_id"))
        if not cid:
            continue
        node_id = f"candidate:{cid}"
        overlay_nodes[node_id] = {
            "id": node_id,
            "kind": "candidate_problem",
            "label": _text(row.get("title")) or cid,
            "candidate_id": cid,
            "stage": _text(row.get("stage")),
            "portfolio_state": _text(row.get("portfolio_state")),
            "source": "research_candidate_portfolio",
            "scientific_authority": False,
        }

    for row in scientific_meta_trace.get("principles") or []:
        if not isinstance(row, dict):
            continue
        pid, idea_id = _text(row.get("principle_id")), _text(row.get("idea_id"))
        if not pid:
            continue
        node_id = f"principle:{pid}"
        overlay_nodes[node_id] = {
            "id": node_id,
            "kind": "core_principle",
            "label": _text(row.get("mechanism")) or pid,
            "belief_state": _text(row.get("belief_state")),
            "source": "scientific_meta_trace",
        }
        if idea_id:
            target = ensure_idea(idea_id, "scientific_meta_trace")
            overlay_edges.append({"source": node_id, "target": target, "relation": "principle_for"})

    for row in pilot_registry.get("phases") or []:
        if not isinstance(row, dict):
            continue
        idea_id, phase = _text(row.get("idea_id")), _text(row.get("phase"))
        if not idea_id or not phase:
            continue
        node_id = f"experiment:{idea_id}:{phase}"
        overlay_nodes[node_id] = {
            "id": node_id,
            "kind": "experiment",
            "label": _text(row.get("title")) or f"{idea_id} {phase}",
            "phase": phase,
            "status": _text(row.get("status")),
            "source": "pilot_registry",
        }
        target = ensure_idea(idea_id, "pilot_registry")
        overlay_edges.append({"source": target, "target": node_id, "relation": "tested_by"})

    for idx, row in enumerate(failure_asset_library.get("assets") or []):
        if not isinstance(row, dict):
            continue
        idea_id = _text(row.get("idea_id"))
        signature = _text(row.get("signature")) or f"failure-{idx}"
        node_id = f"failure:{_short_hash(f'{idea_id}|{signature}|{idx}')}"
        overlay_nodes[node_id] = {
            "id": node_id,
            "kind": "failure_asset",
            "label": signature,
            "affected_layer": _text(row.get("affected_layer")),
            "does_not_imply": _text(row.get("does_not_imply")),
            "source": "failure_asset_library",
            "scientific_authority": False,
        }
        if idea_id:
            target = ensure_idea(idea_id, "failure_asset_library")
            overlay_edges.append({"source": node_id, "target": target, "relation": "diagnoses"})

    dead_end_registry = failure_asset_library.get("dead_end_registry") or {}
    for idx, row in enumerate(dead_end_registry.get("certified_principle_dead_ends") or []):
        if not isinstance(row, dict) or row.get("principle_dead_end_certified") is not True:
            continue
        principle_id = _text(row.get("principle_id") or row.get("id"))
        closure_key = _text(row.get("closure_id") or row.get("counter_explanation") or principle_id or str(idx))
        node_id = f"closure:{_short_hash(closure_key)}"
        overlay_nodes[node_id] = {
            "id": node_id,
            "kind": "scientific_closure",
            "label": _text(row.get("counter_explanation") or row.get("reason")) or closure_key,
            "closure_layer": "core_principle",
            "source": "failure_asset_library",
            "principle_dead_end_certified": True,
        }
        if principle_id:
            target = f"principle:{principle_id}"
            overlay_nodes.setdefault(target, {"id": target, "kind": "core_principle", "label": principle_id, "source": "failure_asset_library"})
            overlay_edges.append({"source": node_id, "target": target, "relation": "closes_principle"})

    overlay_kinds = Counter(str(row.get("kind") or "unknown") for row in overlay_nodes.values())
    overlay_relations = Counter(str(row.get("relation") or "unknown") for row in overlay_edges)
    unified_kinds = base_node_kinds + overlay_kinds
    unified_relations = base_relations + overlay_relations
    new_overlay_ids = {node_id for node_id in overlay_nodes if node_id not in base_ids}
    closure_edges = sum(row.get("relation") == "closes_principle" for row in overlay_edges)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "RESEARCH_GRAPH_COMPILED",
        "policy": dict(POLICY),
        "base_graph": {
            "state_key": "evidence_graph",
            "nodes": len(base_nodes),
            "edges": len(base_edges),
            "referenced_not_duplicated": True,
        },
        "summary": {
            "nodes": len(base_ids | set(overlay_nodes)),
            "edges": len(base_edges) + len(overlay_edges),
            "node_kinds": dict(sorted(unified_kinds.items())),
            "relations": dict(sorted(unified_relations.items())),
            "base_nodes": len(base_nodes),
            "base_edges": len(base_edges),
            "overlay_nodes": len(overlay_nodes),
            "new_overlay_nodes": len(new_overlay_ids),
            "overlay_edges": len(overlay_edges),
            "candidate_nodes": overlay_kinds.get("candidate_problem", 0),
            "experiment_nodes": overlay_kinds.get("experiment", 0),
            "principle_nodes": overlay_kinds.get("core_principle", 0),
            "failure_asset_nodes": overlay_kinds.get("failure_asset", 0),
            "scientific_closure_nodes": overlay_kinds.get("scientific_closure", 0),
            "principle_closure_edges": closure_edges,
        },
        "overlay_nodes": sorted(overlay_nodes.values(), key=lambda row: str(row.get("id") or "")),
        "overlay_edges": overlay_edges,
        "scientific_authority": False,
    }
