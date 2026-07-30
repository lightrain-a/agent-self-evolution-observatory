from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_lineage(idea_bank: dict[str, Any], collisions: dict[str, Any]) -> dict[str, Any]:
    ideas = list(idea_bank.get("passed_ideas") or []) + list(idea_bank.get("blocked_ideas") or [])
    by_id = {str(idea["id"]): idea for idea in ideas}
    track_roots: dict[str, str] = {}
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    for track_id, label in (idea_bank.get("tracks") or {}).items():
        root_id = f"track-root:{track_id}"
        track_roots[str(track_id)] = root_id
        nodes.append({
            "id": root_id,
            "kind": "track-root",
            "track_id": track_id,
            "title": label,
            "created_at": idea_bank.get("generated_at"),
        })

    cluster_parent: dict[str, str] = {}
    for cluster in collisions.get("clusters") or []:
        members = [by_id[item] for item in cluster.get("idea_ids") or [] if item in by_id]
        if not members:
            continue
        members.sort(key=lambda item: (-(float(item.get("priority") or 0)), item.get("id")))
        parent = str(members[0]["id"])
        for child in members[1:]:
            cluster_parent[str(child["id"])] = parent

    for idea in ideas:
        idea_id = str(idea["id"])
        node = {
            "id": idea_id,
            "kind": "idea",
            "title": idea.get("title"),
            "track_id": idea.get("track_id"),
            "operator": idea.get("operator"),
            "status": idea.get("status"),
            "rank": idea.get("rank"),
            "priority": idea.get("priority"),
            "nearest_work": list(idea.get("nearest_work") or []),
            "review_count": len(idea.get("reviews") or []),
            "external_review_count": len(idea.get("external_reviews") or []),
            "blocking_reasons": list(idea.get("blocking_reasons") or []),
            "created_at": idea_bank.get("generated_at"),
        }
        nodes.append(node)
        parent = cluster_parent.get(idea_id) or track_roots.get(str(idea.get("track_id")))
        if parent:
            edges.append({
                "source": parent,
                "target": idea_id,
                "relation": "near-duplicate-child" if idea_id in cluster_parent else "generated-under-track",
                "operator": idea.get("operator"),
            })
        for index, review in enumerate(idea.get("external_reviews") or []):
            review_id = f"review:{idea_id}:{index + 1}"
            nodes.append({
                "id": review_id,
                "kind": "external-review",
                "verdict": review.get("verdict"),
                "reviewer": review.get("reviewer"),
                "finding": review.get("finding"),
                "required_action": review.get("required_action"),
                "source_artifact": review.get("source_artifact"),
            })
            edges.append({"source": idea_id, "target": review_id, "relation": "reviewed-by"})
        for index, review in enumerate(idea.get("reviews") or []):
            review_id = f"programmatic-review:{idea_id}:{index + 1}"
            nodes.append({
                "id": review_id,
                "kind": "programmatic-review",
                "verdict": review.get("verdict"),
                "reviewer": review.get("reviewer"),
                "label": review.get("label"),
                "score": review.get("score"),
            })
            edges.append({"source": idea_id, "target": review_id, "relation": "reviewed-by"})

    for item in idea_bank.get("early_rejected") or []:
        title = str(item.get("title") or "")
        identifier = f"early-rejected:{len(nodes) + 1}"
        nodes.append({
            "id": identifier,
            "kind": "early-rejected",
            "title": title,
            "reason": item.get("reason"),
            "created_at": idea_bank.get("generated_at"),
        })

    kind_counts = Counter(node["kind"] for node in nodes)
    relation_counts = Counter(edge["relation"] for edge in edges)
    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "summary": {
            "nodes": len(nodes),
            "edges": len(edges),
            "idea_nodes": len(ideas),
            "track_roots": len(track_roots),
            "external_reviews": sum(len(idea.get("external_reviews") or []) for idea in ideas),
            "programmatic_reviews": sum(len(idea.get("reviews") or []) for idea in ideas),
            "node_kinds": dict(kind_counts.most_common()),
            "relations": dict(relation_counts.most_common()),
        },
        "nodes": nodes,
        "edges": edges,
    }
