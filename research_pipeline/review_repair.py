from __future__ import annotations

import re
from collections import Counter
from typing import Any

from .human_terminal_state import repair_allowed


RULES: tuple[dict[str, Any], ...] = (
    {
        "key": "instrumentation-cost",
        "patterns": (r"instrument", r"expensive", r"cost", r"annotation", r"label"),
        "operator": "assumption-removal",
        "action": "Replace exhaustive or oracle supervision with matched replay, weak labels, or an observable proxy; rerun feasibility and attribution review.",
    },
    {
        "key": "non-identifiable-disagreement",
        "patterns": (r"style", r"format", r"disagreement", r"distinct error", r"identif"),
        "operator": "contradiction-resolution",
        "action": "Separate stylistic disagreement from error-mechanism disagreement using controlled formatting and label-shuffled critics.",
    },
    {
        "key": "oracle-exhaustive-search",
        "patterns": (r"oracle", r"exhaustive", r"all update", r"all surface"),
        "operator": "assumption-removal",
        "action": "Use partial-information routing, bandit feedback, or retrospective labels instead of executing every candidate update surface.",
    },
    {
        "key": "novelty-collision",
        "patterns": (r"collision", r"duplicate", r"same mechanism", r"near-duplicate"),
        "operator": "limitation-inversion",
        "action": "State the exact boundary where the nearest method fails; otherwise merge with the higher-priority parent.",
    },
    {
        "key": "weak-main-table",
        "patterns": (r"metric", r"main table", r"surrogate", r"evaluation"),
        "operator": "objective-evaluation-mismatch",
        "action": "Replace the aggregate metric with a direct persistent-gain, regression, attribution, or out-of-loop measurement.",
    },
    {
        "key": "limited-generality",
        "patterns": (r"single domain", r"generality", r"transfer", r"one model"),
        "operator": "cross-domain-analogy",
        "action": "Add a structurally matched second domain and freeze the update rule before transfer.",
    },
    {
        "key": "resource-overrun",
        "patterns": (r"gpu", r"budget", r"resource", r"too large", r"high-resource"),
        "operator": "assumption-removal",
        "action": "Contract the update surface to prompts, memory, routing, or a sub-50M module and define a P0 phenomenon-only gate.",
    },
)


def _combined_text(idea: dict[str, Any]) -> str:
    parts = [
        str(item) for item in idea.get("blocking_reasons") or []
    ]
    structured = idea.get("structured_block") or {}
    if isinstance(structured, dict):
        parts.extend(str(value) for value in structured.values())
    for review in idea.get("external_reviews") or []:
        parts.extend(str(review.get(key) or "") for key in ("finding", "required_action"))
    for review in idea.get("reviews") or []:
        if review.get("verdict") != "pass":
            parts.extend(str(review.get(key) or "") for key in ("finding", "required_action", "label"))
    return " ".join(parts).lower()


def _rule_matches(text: str) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for rule in RULES:
        score = sum(bool(re.search(pattern, text, flags=re.I)) for pattern in rule["patterns"])
        if score:
            results.append({**rule, "match_score": score})
    results.sort(key=lambda item: (-item["match_score"], item["key"]))
    return results


def build_repair_queue(idea_bank: dict[str, Any], collisions: dict[str, Any], pilot_registry: dict[str, Any], experiment_iteration: dict[str, Any] | None = None) -> dict[str, Any]:
    queue: list[dict[str, Any]] = []
    by_id = {
        str(idea["id"]): idea
        for idea in list(idea_bank.get("passed_ideas") or []) + list(idea_bank.get("blocked_ideas") or [])
    }
    collision_flags: dict[str, list[dict[str, Any]]] = {}
    for pair in collisions.get("pairs") or []:
        if pair.get("relation") not in {"duplicate", "near-duplicate", "merge-candidate"}:
            continue
        collision_flags.setdefault(str(pair["left_id"]), []).append(pair)
        collision_flags.setdefault(str(pair["right_id"]), []).append(pair)

    for idea in idea_bank.get("blocked_ideas") or []:
        text = _combined_text(idea)
        rules = _rule_matches(text)
        selected = rules[:2] or [{
            "key": "manual-diagnosis", "operator": "limitation-inversion",
            "action": "Request a project-scoped strict review to identify the single decisive blocker.", "match_score": 0,
        }]
        queue.append({
            "idea_id": idea["id"],
            "title": idea.get("title"),
            "source": "structured-block",
            "priority": 100 + float(idea.get("priority") or 0),
            "current_status": idea.get("status"),
            "recommended_repairs": selected,
            "max_children": 2,
            "rerun_reviewers": ["novelty", "attribution", "feasibility"],
            "automatic_execution": "project-web-gpt-optional",
        })

    for idea_id, pairs in collision_flags.items():
        idea = by_id.get(idea_id)
        if not idea or idea.get("status") == "block":
            continue
        strongest = max(pairs, key=lambda item: float((item.get("scores") or {}).get("hybrid") or 0))
        queue.append({
            "idea_id": idea_id,
            "title": idea.get("title"),
            "source": "collision-engine",
            "priority": 50 + 10 * float((strongest.get("scores") or {}).get("hybrid") or 0),
            "current_status": idea.get("status"),
            "recommended_repairs": [{
                "key": "novelty-collision",
                "operator": "limitation-inversion",
                "action": f"Compare against {strongest.get('right_id') if strongest.get('left_id') == idea_id else strongest.get('left_id')}; merge unless the exact problem-mechanism-experiment boundary survives.",
                "match_score": 1,
            }],
            "max_children": 1,
            "rerun_reviewers": ["novelty", "learning_problem", "generality"],
            "automatic_execution": "project-web-gpt-optional",
        })

    for node in (experiment_iteration or {}).get("nodes") or []:
        children = list(node.get("repair_children") or [])
        if not children:
            continue
        idea = by_id.get(str(node.get("idea_id")))
        if not idea:
            continue
        queue.append({
            "idea_id": node["idea_id"],
            "title": idea.get("title"),
            "source": "experiment-diagnosis",
            "priority": 250 if not node.get("experiment_identifiable") else 225,
            "current_status": node.get("diagnosis"),
            "diagnosis_layer": node.get("diagnosis_layer"),
            "scientific_belief_update_allowed": bool(node.get("scientific_belief_update_allowed")),
            "recommended_repairs": [
                {
                    "key": str(child.get("operator") or "atomic-repair"),
                    "operator": str(child.get("operator") or "atomic-repair"),
                    "action": str(child.get("changed_variable") or child.get("precondition") or "Create one atomic repair child."),
                    "child": child.get("child"),
                    "precondition": child.get("precondition"),
                    "match_score": 1,
                }
                for child in children[:2]
            ],
            "max_children": min(2, len(children)),
            "rerun_reviewers": ["experiment-identifiability", "attribution", "simplification"],
            "automatic_execution": "forbidden-until-child-readiness-gate",
        })

    for item in pilot_registry.get("ideas") or []:
        if item.get("state") != "revise":
            continue
        idea = by_id.get(str(item["idea_id"]))
        if not idea:
            continue
        queue.append({
            "idea_id": item["idea_id"],
            "title": idea.get("title"),
            "source": "pilot-result",
            "priority": 200 - 5 * int(item.get("rank") or 99),
            "current_status": item.get("state"),
            "recommended_repairs": [{
                "key": "pilot-revision",
                "operator": "objective-evaluation-mismatch",
                "action": "Use the failed metric or diagnosis to revise only the mechanism or evaluation boundary, then repeat the same phase under the frozen budget.",
                "match_score": 1,
            }],
            "max_children": 2,
            "rerun_reviewers": ["attribution", "stability", "feasibility"],
            "automatic_execution": "project-web-gpt-optional",
        })

    queue = [item for item in queue if repair_allowed(str(item.get("idea_id") or ""))]
    queue.sort(key=lambda item: (-float(item["priority"]), str(item["idea_id"])))
    source_counts = Counter(item["source"] for item in queue)
    operator_counts = Counter(
        repair["operator"]
        for item in queue
        for repair in item.get("recommended_repairs") or []
    )
    return {
        "schema_version": "1.0",
        "policy": {
            "max_revision_rounds": 2,
            "max_children_per_round": 2,
            "reviewer_cannot_self_approve": True,
            "preserve_parent_branch": True,
            "automatic_selection_forbidden": False,
            "automatic_selection_scope": "idea-lifecycle repair only; stop at P0 or merge",
            "stop_automatic_idea_iteration_at_p0": True,
            "experiment_diagnosis_precedes_pilot_revision": True,
            "nonidentifiable_pilot_cannot_trigger_scientific_stop": True,
            "terminal_human_parent_repair_forbidden": False,
            "terminal_parent_repair_allowed_only_before_p0_or_merge": True,
            "absorbed_child_repair_forbidden": True,
        },
        "summary": {
            "queued_ideas": len(queue),
            "source_counts": dict(source_counts.most_common()),
            "operator_counts": dict(operator_counts.most_common()),
        },
        "queue": queue,
    }


def build_web_review_prompt(item: dict[str, Any], idea: dict[str, Any]) -> str:
    repairs = "\n".join(
        f"- {repair['operator']}: {repair['action']}"
        for repair in item.get("recommended_repairs") or []
    )
    return (
        "Act as a strict ICLR reviewer and repair planner. Work only on the supplied idea. "
        "Do not reward wording. Produce at most two materially distinct revised children, or recommend merge/stop. "
        "Each child must state the changed assumption, mechanism, decisive experiment, and what remains inherited from the parent.\n\n"
        f"Idea ID: {idea.get('id')}\n"
        f"Title: {idea.get('title')}\n"
        f"Problem: {idea.get('purpose')}\n"
        f"Mechanism: {idea.get('core_idea')}\n"
        f"Collision boundary: {idea.get('collision_boundary')}\n"
        f"Current blockers: {idea.get('blocking_reasons')}\n"
        f"Suggested repair operators:\n{repairs}\n\n"
        "Return JSON with keys verdict, merge_target, children, required_evidence."
    )
