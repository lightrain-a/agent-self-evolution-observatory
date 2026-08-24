from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = "1.0"
DEFAULT_JSON_NAME = "research-control-plane.json"
DEFAULT_JS_NAME = "research-control-plane.js"

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
    failure_differential_registry: dict[str, Any] | None = None,
    research_skill_registry: dict[str, Any] | None = None,
    manuscript_integrity_layer: dict[str, Any] | None = None,
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
    skill_summary = dict((research_skill_registry or {}).get("summary") or {})
    internal_skill_library = (research_skill_registry or {}).get("internal_skill_library") or {}
    skill_summary["internal_skill_ids"] = [str(row.get("skill_id") or "") for row in internal_skill_library.get("skills") or [] if str(row.get("skill_id") or "")]
    skill_summary["external_distillation"] = [
        {
            "source_pack": str(row.get("source_pack") or ""),
            "decision": str(row.get("decision") or ""),
            "kept": list(row.get("kept") or []),
            "discarded": list(row.get("discarded") or []),
            "internal_skills": list(row.get("internal_skills") or []),
        }
        for row in internal_skill_library.get("external_distillation") or [] if isinstance(row, dict)
    ]
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
        "component_snapshots": {
            "execution_kernel": dict(research_execution_kernel.get("summary") or {}),
            "reasoning_layer": dict(research_reasoning_layer.get("summary") or {}),
            "feynman_socratic_gate": dict(feynman_socratic_gate.get("summary") or {}),
            "reproduction_gate": dict(reproduction_gate.get("summary") or {}),
            "review_control": dict(review_control.get("summary") or {}),
            "figure_claim_graph": dict(figure_claim_graph.get("summary") or {}),
            "failure_differential_registry": dict((failure_differential_registry or {}).get("summary") or {}),
            "research_skill_registry": skill_summary,
            "manuscript_integrity_layer": dict((manuscript_integrity_layer or {}).get("summary") or {}),
        },
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
            "catalogued_skill_packs": int(((research_skill_registry or {}).get("summary") or {}).get("skill_packs_catalogued_not_installed") or 0),
            "external_skill_packs_distilled": int(((research_skill_registry or {}).get("summary") or {}).get("external_skill_packs_distilled") or 0),
            "canonical_internal_skills": int(((research_skill_registry or {}).get("summary") or {}).get("canonical_internal_skills") or 0),
            "external_skill_runtime_dependencies": int(((research_skill_registry or {}).get("summary") or {}).get("external_skill_runtime_dependencies") or 0),
            "post_draft_integrity_surfaces": int(((manuscript_integrity_layer or {}).get("summary") or {}).get("audit_surfaces") or 0),
            "automatic_scientific_authority": 0,
            "automatic_experiment_authority": 0,
            "automatic_gpu_authority": 0,
        },
        "scientific_authority": False,
    }


def _load_public_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _artifact_sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return ""


def build_public_research_control_plane_projection(project_root: Path) -> dict[str, Any]:
    """Build the control plane only from committed/public artifacts plus deterministic contracts.

    This deliberately avoids rebuilding the whole research-system projection, so publishing the
    control plane cannot accidentally absorb unrelated paper, corpus, or experiment deltas owned
    by another canonical writer.
    """
    root = project_root.resolve()
    generated = root / "generated"
    system_path = generated / "research-system-state.json"
    paper_path = generated / "paper-registry.json"
    governance_path = generated / "research-governance-v2.json"
    quality_path = generated / "asset-first-stri-paper-quality-v2-20260816.json"
    system_state = _load_public_json(system_path)
    paper_registry = _load_public_json(paper_path)
    governance = _load_public_json(governance_path)
    paper_quality = _load_public_json(quality_path)

    from .failure_differential_registry import build_sage_mhfa_shadow_state
    from .manuscript_integrity_audit import build_manuscript_integrity_layer_state
    from .feynman_socratic_gate import build_feynman_socratic_gate_state
    from .figure_claim_graph import build_figure_claim_graph
    from .reproduction_gate import build_reproduction_gate_state
    from .research_execution_kernel import build_research_execution_kernel_state
    from .research_capability_registry import build_research_capability_registry
    from .research_reasoning_layer import build_research_reasoning_layer_state
    from .reviewer_issue_graph import build_review_control_state_from_registry

    execution_kernel = build_research_execution_kernel_state(root / "research_pipeline")
    reasoning_layer = build_research_reasoning_layer_state()
    feynman = build_feynman_socratic_gate_state(root)
    reproduction = build_reproduction_gate_state(root)
    review_control = build_review_control_state_from_registry(paper_registry)
    figure_claim = build_figure_claim_graph(paper_quality)
    failure_differential = build_sage_mhfa_shadow_state(root)
    research_skill_registry = build_research_capability_registry()
    manuscript_integrity = build_manuscript_integrity_layer_state()
    experiment_nodes = ((system_state.get("experiment_iteration") or {}).get("nodes") or [])
    failure_assets = system_state.get("failure_asset_library") or {}

    state = build_research_control_plane_state(
        research_execution_kernel=execution_kernel,
        research_reasoning_layer=reasoning_layer,
        feynman_socratic_gate=feynman,
        reproduction_gate=reproduction,
        review_control=review_control,
        figure_claim_graph=figure_claim,
        failure_differential_registry=failure_differential,
        research_skill_registry=research_skill_registry,
        manuscript_integrity_layer=manuscript_integrity,
        experiment_nodes=experiment_nodes,
        research_states=(),
        governance_state=governance,
        failure_asset_library=failure_assets,
        paper_registry_summary=paper_registry.get("summary") or {},
    )
    state["shadow_extensions"] = {
        "failure_differential_registry": failure_differential,
        "shadow_extension_grants_scientific_authority": False,
        "shadow_extension_grants_experiment_authority": False,
    }
    sources = {
        str(path.relative_to(root)): _artifact_sha256(path)
        for path in (system_path, paper_path, governance_path, quality_path)
    }
    projection = {
        **state,
        "projection_policy": {
            "selective_projection_only": True,
            "full_research_system_rebuild_forbidden": True,
            "public_committed_artifacts_are_inputs": True,
            "projection_cannot_mutate_source_artifacts": True,
        },
        "source_artifact_sha256": sources,
    }
    projection["projection_sha256"] = hashlib.sha256(
        json.dumps(projection, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return projection


def write_public_research_control_plane_projection(project_root: Path) -> dict[str, Any]:
    root = project_root.resolve()
    state = build_public_research_control_plane_projection(root)
    generated = root / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    json_path = generated / DEFAULT_JSON_NAME
    js_path = generated / DEFAULT_JS_NAME
    json_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text(
        "window.RESEARCH_CONTROL_PLANE = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    return state
