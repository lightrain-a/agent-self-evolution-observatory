from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = "1.0"

POLICY: dict[str, Any] = {
    "control_plane_is_distinct_from_runtime_execution_plane": True,
    "research_mode_never_grants_scientific_or_execution_authority_by_itself": True,
    "experiment_tree_scores_schedule_attention_not_scientific_evidence": True,
    "best_branch_cannot_hide_or_discard_completed_scientific_results": True,
    "artifact_inspector_is_read_only_and_content_addressed": True,
    "paper_mode_consumes_validated_evidence_and_cannot_manufacture_evidence": True,
    "reproduction_mode_still_requires_external_execution_authority": True,
    "zero_active_research_states_is_valid": True,
}

MODE_ACTIONS = {
    "DISCOVERY": {"draft-candidate", "propose-falsifier", "read-literature", "read-memory"},
    "DEBATE": {"draft-objection", "propose-falsifier", "read-evidence", "read-memory"},
    "REPRODUCTION": {"read-source", "inspect-artifact", "propose-reproduction", "execute-reproduction", "write-execution-receipt"},
    "PAPER": {"read-validated-evidence", "write-manuscript", "write-figure", "write-review-response"},
}

FORBIDDEN_DIRECT_ACTIONS = {"write-validated-evidence", "grant-scientific-authority", "grant-experiment-authority", "grant-p0-authority", "grant-gpu-authority"}


def evaluate_mode_action(mode: str, action: str, *, execution_authority: bool = False) -> dict[str, Any]:
    mode = str(mode or "").upper()
    action = str(action or "").lower()
    blockers: list[str] = []
    if mode not in MODE_ACTIONS:
        blockers.append("unknown-research-mode")
    if action in FORBIDDEN_DIRECT_ACTIONS:
        blockers.append("mode-cannot-directly-perform-authority-or-evidence-write")
    elif mode in MODE_ACTIONS and action not in MODE_ACTIONS[mode]:
        blockers.append("action-not-allowed-in-mode")
    if mode == "REPRODUCTION" and action == "execute-reproduction" and not execution_authority:
        blockers.append("external-execution-authority-required")
    return {
        "schema_version": SCHEMA_VERSION,
        "mode": mode,
        "action": action,
        "allowed": not blockers,
        "blockers": blockers,
        "mode_grants_scientific_authority": False,
        "mode_grants_execution_authority": False,
        "scientific_authority": False,
    }


def build_experiment_tree(nodes: Iterable[dict[str, Any]]) -> dict[str, Any]:
    registry: dict[str, dict[str, Any]] = {}
    blockers: list[str] = []
    for raw in nodes:
        if not isinstance(raw, dict):
            continue
        eid = str(raw.get("experiment_id") or raw.get("node_id") or raw.get("id") or raw.get("idea_id") or "")
        if not eid:
            continue
        if eid in registry:
            blockers.append(f"duplicate-experiment-node:{eid}")
            continue
        registry[eid] = {
            "experiment_id": eid,
            "parent_experiment_id": str(raw.get("parent_experiment_id") or raw.get("parent_id") or ""),
            "phase": str(raw.get("phase") or raw.get("stage") or ""),
            "status": str(raw.get("status") or raw.get("decision") or ""),
            "scheduling_score": raw.get("scheduling_score", raw.get("priority_score")),
            "evidence_selected_by_score": False,
            "scientific_authority": False,
        }
    for eid, row in registry.items():
        parent = row["parent_experiment_id"]
        if parent and parent not in registry:
            blockers.append(f"missing-parent:{eid}:{parent}")
    # Detect cycles independently of scheduling score.
    for eid in registry:
        seen: set[str] = set()
        cursor = eid
        while cursor and cursor in registry:
            if cursor in seen:
                blockers.append(f"experiment-tree-cycle:{eid}")
                break
            seen.add(cursor)
            cursor = registry[cursor]["parent_experiment_id"]
    children: dict[str, list[str]] = {eid: [] for eid in registry}
    roots: list[str] = []
    for eid, row in registry.items():
        parent = row["parent_experiment_id"]
        if parent in children:
            children[parent].append(eid)
        elif not parent:
            roots.append(eid)
    rows = []
    for eid, row in registry.items():
        rows.append({**row, "child_experiment_ids": sorted(children[eid])})
    blockers = sorted(set(blockers))
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "EXPERIMENT_TREE_VALID" if not blockers else "EXPERIMENT_TREE_INVALID",
        "nodes": sorted(rows, key=lambda r: r["experiment_id"]),
        "roots": sorted(roots),
        "blockers": blockers,
        "selection_score_is_scheduling_only": True,
        "completed_results_remain_visible": True,
        "scientific_authority": False,
    }


def inspect_artifact(project_root: Path, relative_path: str, *, expected_sha256: str = "") -> dict[str, Any]:
    root = project_root.resolve()
    raw = Path(str(relative_path))
    blockers: list[str] = []
    if raw.is_absolute():
        blockers.append("absolute-path-forbidden")
        path = root
    else:
        path = (root / raw).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            blockers.append("path-traversal-forbidden")
    exists = path.is_file() if not blockers else False
    digest = ""
    size = 0
    if exists:
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        size = len(data)
    else:
        blockers.append("artifact-missing")
    if expected_sha256 and digest and digest != expected_sha256:
        blockers.append("artifact-sha256-mismatch")
    return {
        "schema_version": SCHEMA_VERSION,
        "relative_path": str(relative_path),
        "exists": exists,
        "sha256": digest,
        "size_bytes": size,
        "expected_sha256": str(expected_sha256),
        "status": "PASS" if not blockers else "BLOCK",
        "blockers": sorted(set(blockers)),
        "read_only": True,
        "scientific_authority": False,
    }


def build_research_control_plane_state(
    *, research_execution_kernel: dict[str, Any], research_reasoning_layer: dict[str, Any],
    feynman_socratic_gate: dict[str, Any], reproduction_gate: dict[str, Any],
    review_control: dict[str, Any], figure_claim_graph: dict[str, Any],
    experiment_nodes: Iterable[dict[str, Any]] = (), research_states: Iterable[dict[str, Any]] = (),
    governance_state: dict[str, Any] | None = None, failure_asset_library: dict[str, Any] | None = None,
    paper_registry_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    tree = build_experiment_tree(experiment_nodes)
    states = [dict(row) for row in research_states if isinstance(row, dict)]
    governance = governance_state or {}
    runtime = governance.get("runtime") or {}
    failures = failure_asset_library or {}
    paper_summary = paper_registry_summary or {}
    checks = {
        "execution_kernel": research_execution_kernel.get("status") == "KERNEL_CONTRACTS_INSTALLED",
        "reasoning_layer": research_reasoning_layer.get("status") == "REASONING_CONTRACTS_INSTALLED",
        "feynman_socratic": str(feynman_socratic_gate.get("status") or "").endswith("GATE_INSTALLED"),
        "reproduction_gate": reproduction_gate.get("status") == "REPRODUCTION_GATE_INSTALLED",
        "review_control": review_control.get("status") == "REVIEW_CONTROL_STATE_COMPILED",
        "figure_claim_graph": figure_claim_graph.get("status") == "PASS_FIGURE_CLAIM_GRAPH",
        "experiment_tree": tree.get("status") == "EXPERIMENT_TREE_VALID",
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "CONTROL_PLANE_READY" if all(checks.values()) else "CONTROL_PLANE_HOLD",
        "policy": dict(POLICY),
        "research_modes": {mode: {"allowed_actions": sorted(actions), "scientific_authority": False, "execution_authority": False} for mode, actions in MODE_ACTIONS.items()},
        "component_checks": checks,
        "research_states": states,
        "experiment_tree": tree,
        "resource_snapshot": {
            "active_gpu_leases": int(runtime.get("active_gpu_leases") or 0),
            "resource_authority_source": "research-governance-v2",
            "control_plane_can_grant_gpu": False,
        },
        "failure_snapshot": dict(failures.get("summary") or {}),
        "review_snapshot": dict(review_control.get("summary") or {}),
        "paper_readiness": dict(paper_summary),
        "summary": {
            "component_checks_passed": sum(checks.values()),
            "component_checks_total": len(checks),
            "active_research_states": len(states),
            "experiment_tree_nodes": len(tree.get("nodes") or []),
            "reviewer_issue_papers": int((review_control.get("summary") or {}).get("papers") or 0),
            "registered_papers": int(paper_summary.get("papers") or 0),
            "submission_ready_papers": int(paper_summary.get("submission_ready") or 0),
            "automatic_scientific_authority": 0,
            "automatic_experiment_authority": 0,
            "automatic_gpu_authority": 0,
        },
        "scientific_authority": False,
    }
