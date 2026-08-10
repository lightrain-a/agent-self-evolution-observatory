from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .pre_experiment_specs import ALLOWED_PROVENANCE_TYPES, GATES
from .pre_p0_identifiability import CURRENT_CONTRACTS, audit_contract


def _spec(key: str) -> dict[str, str]:
    return next(row for row in GATES if row["key"] == key)


def gate(key: str, passed: bool, *, blockers: list[str] | None = None, evidence: Any = None, detail: Any = None) -> dict[str, Any]:
    return {**_spec(key), "pass": bool(passed), "blockers": list(blockers or []), "evidence": evidence, "detail": detail}


def get_path(payload: dict[str, Any], dotted: str) -> Any:
    value: Any = payload
    for part in dotted.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def parameter_provenance(config: dict[str, Any]) -> dict[str, Any]:
    contract = (config.get("pre_experiment") or {}).get("parameter_provenance") or {}
    critical = list(contract.get("critical_parameters") or [])
    entries = {str(row.get("parameter")): row for row in contract.get("entries") or [] if isinstance(row, dict)}
    blockers: list[str] = []
    rows: list[dict[str, Any]] = []
    if not critical:
        blockers.append("critical-parameter-list-missing")
    for parameter in critical:
        row = entries.get(str(parameter)) or {}
        actual = get_path(config, str(parameter))
        source_type = str(row.get("source_type") or "")
        basis = str(row.get("basis") or "").strip()
        declared = row.get("value")
        ok = actual is not None and source_type in ALLOWED_PROVENANCE_TYPES and bool(basis)
        if declared is not None and declared != actual:
            blockers.append(f"parameter-value-mismatch:{parameter}")
            ok = False
        if actual is None:
            blockers.append(f"parameter-missing:{parameter}")
        if source_type not in ALLOWED_PROVENANCE_TYPES:
            blockers.append(f"parameter-source-invalid:{parameter}")
        if not basis:
            blockers.append(f"parameter-basis-missing:{parameter}")
        if str(parameter) not in entries:
            blockers.append(f"parameter-provenance-missing:{parameter}")
        rows.append({"parameter": parameter, "value": actual, "source_type": source_type, "basis": basis, "pass": ok})
    return gate("parameter_provenance", not blockers, blockers=sorted(set(blockers)), evidence=rows)


def qualification_path(data_root: Path, config: dict[str, Any]) -> Path | None:
    competence = (config.get("pre_experiment") or {}).get("competence") or {}
    evidence_id = str(competence.get("evidence_id") or "").strip()
    if not evidence_id:
        return None
    canonical = data_root / "pre-experiment" / "evidence" / "qualifications" / f"{evidence_id}.json"
    flat = data_root / f"pre-experiment-qualification-{evidence_id}.json"
    return canonical if canonical.exists() or not flat.exists() else flat


def baseline_competence(config: dict[str, Any], data_root: Path) -> dict[str, Any]:
    contract = (config.get("pre_experiment") or {}).get("competence") or {}
    path = qualification_path(data_root, config)
    blockers: list[str] = []
    summary: dict[str, Any] = {}
    if path is None:
        blockers.append("competence-evidence-id-missing")
    elif not path.exists():
        blockers.append("competence-evidence-file-missing")
    else:
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                summary = loaded
            else:
                blockers.append("competence-evidence-invalid-root")
        except (OSError, json.JSONDecodeError):
            blockers.append("competence-evidence-invalid-json")
    if summary:
        source_gate = summary.get("gate") or {}
        minimum_rate = float(contract.get("minimum_success_rate", 0.0))
        maximum_rate = float(contract.get("maximum_success_rate", 1.0))
        minimum_types = int(contract.get("minimum_task_types_with_success", 1))
        rate = float(summary.get("success_rate") or 0.0)
        task_types = int(summary.get("task_types_with_success") or 0)
        if source_gate.get("passed") is not True:
            blockers.append("competence-source-gate-not-passed")
        if rate < minimum_rate:
            blockers.append("baseline-floor")
        if rate > maximum_rate:
            blockers.append("baseline-ceiling")
        if task_types < minimum_types:
            blockers.append("competence-task-family-coverage-insufficient")
        expected_policy = str(contract.get("policy_mode") or "")
        if expected_policy and str(summary.get("policy_mode") or "") != expected_policy:
            blockers.append("competence-policy-mode-mismatch")
        expected_model = str(contract.get("model_name") or "")
        if expected_model and expected_model.lower() not in str(summary.get("model_path") or "").lower():
            blockers.append("competence-model-mismatch")
    return gate("baseline_competence", not blockers, blockers=blockers, evidence={"path": str(path) if path else "", "summary": summary})


def mechanism_identifiability(idea_id: str, config: dict[str, Any]) -> dict[str, Any]:
    contract = (config.get("pre_experiment") or {}).get("identifiability") or {}
    scope = config.get("scope") or {}
    analysis = config.get("analysis") or {}
    blockers: list[str] = []
    retrospective = audit_contract(idea_id, CURRENT_CONTRACTS.get(idea_id))
    required_retrospective = {
        "claim_alignment", "target_variation", "baseline_disagreement",
        "representability", "tiny_overfit", "competence_window", "effect_variation",
    }
    retrospective_checks = {row["key"]: row for row in retrospective.get("checks") or []}
    for key in sorted(required_retrospective):
        if key in retrospective_checks and retrospective_checks[key].get("pass") is not True:
            blockers.append(f"retrospective-{key}")
    if idea_id == "update-trust-region":
        candidate_count = int(max(scope.get("candidate_updates_target") or [0]))
        accepted = max(1, round(candidate_count * float(analysis.get("acceptance_rate", 0.5)))) if candidate_count else 0
        minimum_harmful = int(analysis.get("minimum_harmful_candidates_for_decision") or analysis.get("minimum_harmful_candidates_for_interpretation") or 0)
        prevalence = float(contract.get("expected_harmful_prevalence", 0.25))
        expected_harmful = candidate_count * prevalence
        detail = {"candidate_count": candidate_count, "accepted_count": accepted, "expected_harmful_prevalence": prevalence, "expected_harmful_candidates": expected_harmful, "minimum_harmful_candidates": minimum_harmful, "true_false_design_separation": "high-drift harmful updates versus null/no-harmful regime", "retrospective_pre_p0": retrospective}
        if candidate_count < 8:
            blockers.append("too-few-candidates-for-identifiability")
        if minimum_harmful and expected_harmful < minimum_harmful:
            blockers.append("expected-harmful-count-below-identifiability-minimum")
        if accepted < 4:
            blockers.append("too-few-accepted-candidates")
    elif idea_id == "budgeted-evolution-controller":
        splits = scope.get("sequence_splits") or {}
        archetypes = list(contract.get("required_sequence_archetypes") or [])
        detail = {"sequence_splits": splits, "required_sequence_archetypes": archetypes, "controller_features": list(scope.get("controller_features") or []), "identifiability_thresholds": analysis.get("identifiability") or {}, "retrospective_pre_p0": retrospective}
        if int(splits.get("discovery", 0)) + int(splits.get("calibration", 0)) < 12:
            blockers.append("too-few-fit-sequences")
        if int(splits.get("hidden", 0)) < 8:
            blockers.append("too-few-hidden-sequences")
        if not {"early-stop", "late-stop", "rollback-or-harm"}.issubset(set(archetypes)):
            blockers.append("sequence-archetype-contract-incomplete")
        if len(scope.get("controller_features") or []) < 3:
            blockers.append("controller-feature-set-too-small")
    else:
        detail = {**contract, "retrospective_pre_p0": retrospective}
        if contract.get("synthetic_true_false_separation") is not True:
            blockers.append("synthetic-true-false-separation-not-demonstrated")
    return gate("mechanism_identifiability", not blockers, blockers=blockers, detail=detail)


def statistical_resolution(idea_id: str, config: dict[str, Any]) -> dict[str, Any]:
    scope = config.get("scope") or {}
    analysis = config.get("analysis") or {}
    phase = str(config.get("phase") or "P0")
    blockers: list[str] = []
    detail: dict[str, Any] = {"phase": phase}
    if idea_id == "update-trust-region":
        candidate_count = int(max(scope.get("candidate_updates_target") or [0]))
        accepted = max(1, round(candidate_count * float(analysis.get("acceptance_rate", 0.5)))) if candidate_count else 0
        hidden_each = int(scope.get("hidden_tasks_per_candidate", 0))
        accepted_resolution = 1.0 / accepted if accepted else 1.0
        hidden_resolution = 1.0 / hidden_each if hidden_each else 1.0
        detail.update({"accepted_count": accepted, "accepted_rate_resolution": accepted_resolution, "hidden_delta_resolution": hidden_resolution})
        if phase == "P0":
            go = config.get("go_gate") or {}
            max_loss = float(go.get("max_target_gain_loss", 1.0))
            detail.update({"max_target_gain_loss": max_loss, "min_harmful_reduction": float(go.get("min_harmful_reduction", 0.0))})
            if max_loss + 1e-12 < accepted_resolution:
                blockers.append("target-gain-threshold-finer-than-observable-resolution")
            if analysis.get("bootstrap_confidence") is None:
                blockers.append("confirmatory-confidence-interval-missing")
        else:
            max_loss = float(analysis.get("screening_max_target_gain_loss", accepted_resolution))
            detail["screening_max_target_gain_loss"] = max_loss
            if max_loss + 1e-12 < accepted_resolution:
                blockers.append("screening-gain-threshold-finer-than-observable-resolution")
    elif idea_id == "budgeted-evolution-controller":
        hidden = int((scope.get("sequence_splits") or {}).get("hidden", 0))
        resolution = 1.0 / hidden if hidden else 1.0
        detail.update({"hidden_sequences": hidden, "success_rate_resolution": resolution})
        if phase == "P0":
            max_loss = float((config.get("go_gate") or {}).get("max_success_loss", 1.0))
            detail["max_success_loss"] = max_loss
            if max_loss + 1e-12 < resolution:
                blockers.append("success-loss-threshold-finer-than-observable-resolution")
            if analysis.get("bootstrap_confidence") is None:
                blockers.append("confirmatory-confidence-interval-missing")
    statistics = (config.get("pre_experiment") or {}).get("statistics") or {}
    if phase != "P0" and statistics.get("screening_cannot_reject_idea") is not True:
        blockers.append("screening-rejection-policy-missing")
    return gate("statistical_resolution", not blockers, blockers=blockers, detail=detail)
