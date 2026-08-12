from __future__ import annotations

from collections import defaultdict
from typing import Any


POLICY: dict[str, Any] = {
    "schema_version": "1.0",
    "scheduler_is_advisory_only": True,
    "scheduler_cannot_authorize_execution": True,
    "rank_by_information_gain_not_only_expected_score": True,
    "decision_changing_tests_preferred": True,
    "cheap_falsifiers_preferred_before_scale": True,
    "cross_branch_reference_edges_allowed": True,
    "exploration_to_exploitation_shift_is_progressive": True,
}

REFERENCES = [
    {"system": "Ai2 AutoDiscovery", "adopted": "prioritize hypotheses and tests by belief change / information gain rather than only local score improvement"},
    {"system": "MLEvolve", "adopted": "progressive graph search, cross-branch fusion, and time-aware exploration-to-exploitation scheduling"},
    {"system": "AI Scientist-v2", "adopted": "maintain a branching experiment tree instead of greedy best-leaf hill climbing"},
]

OPERATOR_PRIORS = {
    "debug-only": (0.45, 0.40, 0.20),
    "substrate-requalification": (0.90, 0.95, 0.20),
    "target-variation-design": (0.95, 0.95, 0.15),
    "optimization-extension": (0.45, 0.55, 0.55),
    "representation-child": (0.85, 0.80, 0.45),
    "objective-child": (0.85, 0.85, 0.45),
    "disagreement-mining": (0.98, 0.95, 0.15),
    "merge-simplification": (0.90, 0.95, 0.05),
}


def _score(operator: str, principle_linked: bool) -> tuple[float, dict[str, float]]:
    info, decision, cost = OPERATOR_PRIORS.get(operator, (0.60, 0.60, 0.50))
    coverage = 1.0 if principle_linked else 0.5
    replication = 0.7 if operator in {"substrate-requalification", "disagreement-mining"} else 0.4
    utility = 0.35 * info + 0.35 * decision + 0.20 * coverage + 0.10 * replication
    score = utility / (0.5 + cost)
    return round(score, 4), {
        "expected_information_gain": info,
        "decision_relevance": decision,
        "principle_coverage": coverage,
        "replication_value": replication,
        "relative_cost": cost,
    }


def build_experiment_value_scheduler(experiment_iteration: dict[str, Any], meta_trace: dict[str, Any]) -> dict[str, Any]:
    principle_ideas = {str(row.get("idea_id") or "") for row in meta_trace.get("principles") or []}
    candidates: list[dict[str, Any]] = []
    decision_actions: list[dict[str, Any]] = []
    by_operator: dict[str, list[str]] = defaultdict(list)
    for node in experiment_iteration.get("nodes") or []:
        idea_id = str(node.get("idea_id") or "")
        for index, child in enumerate(node.get("repair_children") or []):
            operator = str(child.get("operator") or "unknown")
            score, features = _score(operator, idea_id in principle_ideas)
            candidate_id = f"{idea_id}:{operator}:{index}"
            if operator == "merge-simplification":
                decision_actions.append({"candidate_id": candidate_id, "idea_id": idea_id, "operator": operator, "reason": str(child.get("precondition") or ""), "execution_authorized": False})
                continue
            candidates.append({
                "candidate_id": candidate_id,
                "idea_id": idea_id,
                "operator": operator,
                "child": str(child.get("child") or ""),
                "changed_variable": str(child.get("changed_variable") or ""),
                "precondition": str(child.get("precondition") or ""),
                "value_score": score,
                "features": features,
                "execution_authorized": False,
            })
            by_operator[operator].append(candidate_id)

    candidates.sort(key=lambda row: (-float(row["value_score"]), row["candidate_id"]))
    reference_edges = [
        {"operator": operator, "candidate_ids": sorted(ids)}
        for operator, ids in sorted(by_operator.items())
        if len(ids) >= 2
    ]
    return {
        "schema_version": "1.0",
        "policy": POLICY,
        "references": REFERENCES,
        "summary": {
            "candidates": len(candidates),
            "cross_branch_reference_edges": len(reference_edges),
            "top_candidate": candidates[0]["candidate_id"] if candidates else "",
        },
        "ranking": candidates,
        "decision_actions": decision_actions,
        "cross_branch_reference_edges": reference_edges,
        "search_schedule": {
            "early": "favor cheap falsifiers and broad disagreement/variation discovery",
            "middle": "fuse useful evidence across branches while preserving alternative explanations",
            "late": "exploit only after principle, protocol, support, and matched-baseline uncertainty has narrowed",
        },
    }
