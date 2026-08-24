from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from .p0_decision_ledger import build_p0_decision_ledger
from .principle_adjudication import FAILURE_LAYER_SPECS

SCHEMA_VERSION = "1.0"
MIN_PROSPECTIVE_REPLAY_CASES = 15
MAX_HYPOTHESES = 3

POLICY: dict[str, Any] = {
    "schema_version": SCHEMA_VERSION,
    "hypotheses_must_be_frozen_before_final_failure_layer_is_visible": True,
    "historical_final_labels_cannot_be_used_to_retroactively_generate_hypotheses": True,
    "final_failure_layer_must_be_independently_adjudicated": True,
    "top_k_is_diagnostic_not_scientific_authority": True,
    "hypothesis_rank_cannot_authorize_repair_experiment_or_gpu": True,
    "registry_merges_into_existing_post_screen_differential_diagnosis_checkpoint": True,
    "prospective_replay_required_before_any_claim_of_improved_failure_attribution": True,
}


def _sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def build_historical_failure_label_inventory(project_root: Path) -> dict[str, Any]:
    """Inventory independently terminalized labels without turning them into prospective hypotheses."""
    root = project_root.resolve()
    generated = root / "generated"
    admission = _load(generated / "p0-admission-state.json")
    offline = _load(generated / "p0-offline-qualification.json")
    human = _load(generated / "human-terminal-idea-state.json")
    iteration = _load(generated / "p0-four-direction-iteration.json")
    ledger = build_p0_decision_ledger(admission, offline, human, iteration)
    rows = []
    for row in ledger.get("rows") or []:
        if not isinstance(row, dict) or row.get("failure_diagnosis_complete") is not True:
            continue
        layer = str(row.get("failure_layer") or "")
        if layer not in FAILURE_LAYER_SPECS:
            continue
        rows.append({
            "case_id": str(row.get("idea_id") or row.get("code") or ""),
            "code": str(row.get("code") or ""),
            "final_failure_layer": layer,
            "final_failure_class": str(row.get("failure_class") or ""),
            "current_state": str(row.get("current_state") or ""),
            "historical_label_only": True,
            "eligible_to_generate_retrospective_hypotheses": False,
            "scientific_authority": False,
        })
    counts = {layer: sum(r["final_failure_layer"] == layer for r in rows) for layer in FAILURE_LAYER_SPECS}
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "HISTORICAL_FAILURE_LABEL_INVENTORY_READY",
        "rows": rows,
        "summary": {
            "terminalized_failure_labels": len(rows),
            "minimum_replay_cases": MIN_PROSPECTIVE_REPLAY_CASES,
            "historical_label_count_sufficient": len(rows) >= MIN_PROSPECTIVE_REPLAY_CASES,
            "failure_layer_counts": counts,
            "retrospective_hypothesis_generation_allowed": 0,
        },
        "scientific_authority": False,
    }


def build_failure_hypothesis_set(
    *, case_id: str, evidence_refs: Iterable[str], hypotheses: Iterable[dict[str, Any]],
    final_label_visible: bool = False,
) -> dict[str, Any]:
    blockers: list[str] = []
    refs = [str(value) for value in evidence_refs if str(value)]
    if not case_id:
        blockers.append("case-id-missing")
    if not refs:
        blockers.append("pre-adjudication-evidence-refs-required")
    if final_label_visible:
        blockers.append("final-label-visible-before-hypothesis-freeze")
    rows = []
    for index, raw in enumerate(hypotheses, start=1):
        if not isinstance(raw, dict):
            continue
        layer = str(raw.get("failure_layer") or "")
        rationale = str(raw.get("rationale") or "").strip()
        hrefs = [str(value) for value in raw.get("evidence_refs") or [] if str(value)]
        route = str(raw.get("repair_route") or "").strip()
        if layer not in FAILURE_LAYER_SPECS:
            blockers.append(f"invalid-failure-layer:{index}:{layer}")
        if not rationale:
            blockers.append(f"hypothesis-rationale-missing:{index}")
        if not hrefs:
            blockers.append(f"hypothesis-evidence-missing:{index}")
        if not route:
            blockers.append(f"repair-route-missing:{index}")
        rows.append({
            "rank": index,
            "failure_layer": layer,
            "rationale": rationale,
            "evidence_refs": hrefs,
            "repair_route": route,
            "scientific_authority": False,
            "experiment_authority": False,
        })
    if not rows:
        blockers.append("hypothesis-set-empty")
    if len(rows) > MAX_HYPOTHESES:
        blockers.append("too-many-hypotheses")
    layers = [row["failure_layer"] for row in rows]
    if len(layers) != len(set(layers)):
        blockers.append("duplicate-failure-layers")
    identity = {
        "case_id": str(case_id),
        "evidence_refs": refs,
        "hypotheses": rows,
        "final_label_visible_at_freeze": bool(final_label_visible),
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "HYPOTHESIS_SET_FROZEN" if not blockers else "HYPOTHESIS_SET_BLOCKED",
        **identity,
        "hypothesis_set_sha256": _sha(identity),
        "frozen_before_final_adjudication": not final_label_visible and not blockers,
        "blockers": sorted(set(blockers)),
        "scientific_authority": False,
        "experiment_authority": False,
        "p0_authority": False,
        "gpu_authority": False,
    }


def score_failure_hypothesis_set(
    hypothesis_set: dict[str, Any], *, final_failure_layer: str,
    final_evidence_refs: Iterable[str], final_label_independently_adjudicated: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    if hypothesis_set.get("status") != "HYPOTHESIS_SET_FROZEN":
        blockers.append("hypothesis-set-not-validly-frozen")
    if hypothesis_set.get("frozen_before_final_adjudication") is not True:
        blockers.append("hypothesis-set-not-prospective")
    if final_failure_layer not in FAILURE_LAYER_SPECS:
        blockers.append("invalid-final-failure-layer")
    refs = [str(value) for value in final_evidence_refs if str(value)]
    if not refs:
        blockers.append("final-adjudication-evidence-required")
    if not final_label_independently_adjudicated:
        blockers.append("final-label-must-be-independently-adjudicated")
    layers = [str(row.get("failure_layer") or "") for row in hypothesis_set.get("hypotheses") or [] if isinstance(row, dict)]
    return {
        "schema_version": SCHEMA_VERSION,
        "case_id": hypothesis_set.get("case_id"),
        "hypothesis_set_sha256": hypothesis_set.get("hypothesis_set_sha256"),
        "status": "PROSPECTIVE_CASE_SCORED" if not blockers else "SCORING_BLOCKED",
        "final_failure_layer": str(final_failure_layer),
        "final_evidence_refs": refs,
        "top1_correct": bool(layers and layers[0] == final_failure_layer) if not blockers else False,
        "topk_contains_truth": final_failure_layer in layers if not blockers else False,
        "rank_of_truth": (layers.index(final_failure_layer) + 1) if not blockers and final_failure_layer in layers else None,
        "blockers": blockers,
        "scientific_authority": False,
        "experiment_authority": False,
    }


def build_sage_mhfa_shadow_state(project_root: Path, prospective_scores: Iterable[dict[str, Any]] = ()) -> dict[str, Any]:
    inventory = build_historical_failure_label_inventory(project_root)
    supplied_scores = list(prospective_scores)
    scores = [dict(row) for row in supplied_scores if isinstance(row, dict) and row.get("status") == "PROSPECTIVE_CASE_SCORED"]
    automation_summary = ((_load(project_root.resolve() / "generated" / "ai-consultation-automation.json").get("summary") or {}) if not supplied_scores else {})
    prospective_n = len(scores) if supplied_scores else int(automation_summary.get("failure_differential_scored") or 0)
    frozen_n = len(scores) if supplied_scores else int(automation_summary.get("failure_differential_frozen") or 0)
    waiting_final_n = 0 if supplied_scores else int(automation_summary.get("failure_differential_waiting_new_final") or 0)
    top1 = sum(row.get("top1_correct") is True for row in scores) if supplied_scores else int(automation_summary.get("failure_differential_top1_correct") or 0)
    topk = sum(row.get("topk_contains_truth") is True for row in scores) if supplied_scores else int(automation_summary.get("failure_differential_topk_contains_truth") or 0)
    single = sum(row.get("single_diagnosis_correct") is True for row in scores) if supplied_scores else int(automation_summary.get("failure_differential_single_diagnosis_correct") or 0)
    single_evaluable = sum(row.get("single_diagnosis_correct") in {True, False} for row in scores) if supplied_scores else int(automation_summary.get("failure_differential_single_diagnosis_evaluable") or 0)
    ready = prospective_n >= MIN_PROSPECTIVE_REPLAY_CASES
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "READY_FOR_SAGE_MHFA_GAP_TEST" if ready else "SHADOW_REGISTRY_READY_PROSPECTIVE_REPLAY_PENDING",
        "policy": dict(POLICY),
        "integration_target": "existing post_screen_differential_diagnosis checkpoint + Failure Asset Library",
        "historical_label_inventory": inventory,
        "prospective_scores": scores,
        "summary": {
            "historical_terminalized_labels": int((inventory.get("summary") or {}).get("terminalized_failure_labels") or 0),
            "historical_label_count_sufficient": bool((inventory.get("summary") or {}).get("historical_label_count_sufficient")),
            "prospective_frozen_cases": frozen_n,
            "prospective_scored_cases": prospective_n,
            "prospective_cases_waiting_new_final_evidence": waiting_final_n,
            "minimum_prospective_replay_cases": MIN_PROSPECTIVE_REPLAY_CASES,
            "top1_correct": top1,
            "topk_contains_truth": topk,
            "single_diagnosis_evaluable": single_evaluable,
            "single_diagnosis_correct": single,
            "top1_accuracy": (top1 / prospective_n) if prospective_n else None,
            "topk_recall": (topk / prospective_n) if prospective_n else None,
            "single_diagnosis_accuracy": (single / single_evaluable) if single_evaluable else None,
            "adoption_gap_test_ready": ready,
            "retrospective_label_leakage_allowed": 0,
            "automatic_repair_authority": 0,
        },
        "next_action": (
            "Compare top-1 versus top-k attribution and unnecessary-pivot rate against the existing single diagnosis at identical evidence/reviewer budget."
            if ready else
            "Freeze competing hypotheses before final adjudication on future post-screen failures; historical final labels are inventory only and cannot be backfilled into prospective replay."
        ),
        "scientific_authority": False,
        "experiment_authority": False,
    }
