from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import StorageSettings, resolve_experiment_data_root
from .pre_experiment_compiler import compile_from_path as compile_pre_experiment_from_path
from .pre_p0_identifiability import build_pre_p0_identifiability_audit

VALID_PHASES = {"P0", "P1", "P2"}
VALID_RESULTS = {"pass", "revise", "fail", "blocked", "running", "planned"}
VALID_APPROVAL_DECISIONS = {"approve", "hold", "reject"}
FORMAL_P0_CONFIGS = {
    "update-trust-region": Path(__file__).with_name("p0_a1_confirm_config.json"),
    "budgeted-evolution-controller": Path(__file__).with_name("p0_a2_confirm_config.json"),
}

CURRENT_P0_GATE = {
    "update-trust-region": "ready",
    "budgeted-evolution-controller": "ready",
    "outcome-equivalent-trajectory-contrast": "method-redesign",
    "workflow-generalization-certificate": "method-redesign",
    "world-model-error-gated-learning": "scenario-check",
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def pilot_result_schema() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "required": [
            "idea_id", "phase", "result", "code_commit", "config_hash", "datasets",
            "models", "seeds", "metrics", "cost", "diagnosis", "next_action",
        ],
        "result_values": sorted(VALID_RESULTS - {"planned"}),
        "phase_values": sorted(VALID_PHASES),
    }


def validate_result(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = pilot_result_schema()["required"]
    for key in required:
        if key not in payload:
            errors.append(f"missing {key}")
    if payload.get("phase") not in VALID_PHASES:
        errors.append(f"invalid phase: {payload.get('phase')}")
    if payload.get("result") not in VALID_RESULTS - {"planned"}:
        errors.append(f"invalid result: {payload.get('result')}")
    if not isinstance(payload.get("metrics"), dict):
        errors.append("metrics must be an object")
    if not isinstance(payload.get("cost"), dict):
        errors.append("cost must be an object")
    if payload.get("phase") == "P0" and payload.get("result") == "pass" and payload.get("next_action") != "await-human-approval":
        errors.append("P0 pass must set next_action=await-human-approval")
    return errors


def pilot_approval_schema() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "required": ["idea_id", "after_phase", "decision", "reviewed_by", "reviewed_at", "rationale"],
        "after_phase_values": ["P0"],
        "decision_values": sorted(VALID_APPROVAL_DECISIONS),
    }


def validate_approval(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in pilot_approval_schema()["required"]:
        if key not in payload:
            errors.append(f"missing {key}")
    if payload.get("after_phase") != "P0":
        errors.append("pilot approval is only valid after P0")
    if payload.get("decision") not in VALID_APPROVAL_DECISIONS:
        errors.append(f"invalid decision: {payload.get('decision')}")
    return errors


def load_results(result_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    valid: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []
    if not result_dir.exists():
        return valid, invalid
    for path in sorted(result_dir.rglob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            invalid.append({"path": str(path), "errors": [str(error)]})
            continue
        if not isinstance(payload, dict):
            invalid.append({"path": str(path), "errors": ["root must be an object"]})
            continue
        if payload.get("invalidated") is True:
            invalid.append({
                "path": str(path),
                "errors": ["scientifically invalidated: " + str(payload.get("invalidation_reason") or "unspecified")],
                "invalidated": True,
            })
            continue
        errors = validate_result(payload)
        if errors:
            invalid.append({"path": str(path), "errors": errors})
            continue
        payload = dict(payload)
        payload["source_path"] = str(path)
        valid.append(payload)
    return valid, invalid


def load_approvals(approval_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    valid: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []
    if not approval_dir.exists():
        return valid, invalid
    for path in sorted(approval_dir.rglob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            invalid.append({"path": str(path), "errors": [str(error)]})
            continue
        if not isinstance(payload, dict):
            invalid.append({"path": str(path), "errors": ["root must be an object"]})
            continue
        errors = validate_approval(payload)
        if errors:
            invalid.append({"path": str(path), "errors": errors})
            continue
        payload = dict(payload)
        payload["source_path"] = str(path)
        valid.append(payload)
    return valid, invalid


def _phase_plan(idea: dict[str, Any], phase: dict[str, Any]) -> dict[str, Any]:
    return {
        "idea_id": idea["id"],
        "idea_title": idea.get("title"),
        "rank": idea.get("rank"),
        "phase": phase.get("id"),
        "title": phase.get("title"),
        "setup": phase.get("setup"),
        "gate": phase.get("gate"),
        "status": "planned",
        "result": None,
        "execution_authorized": False,
        "blocked_by": None,
        "next_action": "wait",
    }


def _result_order(item: dict[str, Any]) -> tuple[str, str]:
    return str(item.get("completed_at") or item.get("updated_at") or ""), str(item.get("source_path") or "")


def build_pilot_registry(
    idea_bank: dict[str, Any],
    *,
    result_dir: Path | None = None,
    approval_dir: Path | None = None,
    pre_p0_audit: dict[str, Any] | None = None,
    pre_experiment_cards: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    storage = StorageSettings.from_env()
    experiment_data_root = resolve_experiment_data_root(storage)
    result_dir = result_dir or experiment_data_root / "runs" / "pilots" / "results"
    approval_dir = approval_dir or result_dir.parent / "approvals"
    valid_results, invalid_results = load_results(result_dir)
    valid_approvals, invalid_approvals = load_approvals(approval_dir)
    pre_p0_audit = pre_p0_audit or build_pre_p0_identifiability_audit(idea_bank)
    pre_p0_by_id = {str(node.get("idea_id")): node for node in pre_p0_audit.get("nodes") or []}
    if pre_experiment_cards is None:
        pre_experiment_cards = {}
        for idea_id, config_file in FORMAL_P0_CONFIGS.items():
            try:
                pre_experiment_cards[idea_id] = compile_pre_experiment_from_path(idea_id, config_file, experiment_data_root)
            except Exception as error:
                pre_experiment_cards[idea_id] = {
                    "idea_id": idea_id,
                    "phase": "P0",
                    "execution_authorized": False,
                    "status": "blocked",
                    "passed_gates": 0,
                    "gate_count": 8,
                    "blockers": [f"pre-experiment-compile-error:{type(error).__name__}"],
                }
    latest: dict[tuple[str, str], dict[str, Any]] = {}
    for result in sorted(valid_results, key=_result_order):
        latest[(str(result["idea_id"]), str(result["phase"]))] = result

    latest_approvals: dict[str, dict[str, Any]] = {}
    for approval in sorted(valid_approvals, key=lambda item: (str(item.get("reviewed_at") or ""), str(item.get("source_path") or ""))):
        latest_approvals[str(approval["idea_id"])] = approval

    plans: list[dict[str, Any]] = []
    for idea in idea_bank.get("passed_ideas") or []:
        idea_id = str(idea["id"])
        phases = (idea.get("experiment_protocol") or {}).get("phases") or []
        phase_statuses = {
            phase_id: str(latest[(idea_id, phase_id)]["result"])
            for phase_id in VALID_PHASES
            if (idea_id, phase_id) in latest
        }
        approval = latest_approvals.get(idea_id)
        approval_decision = str((approval or {}).get("decision") or "")
        p0_gate_status = CURRENT_P0_GATE.get(idea_id, "not-current-p0-candidate")
        pre_p0 = pre_p0_by_id.get(idea_id) or {"execution_ready": False, "status": "missing-contract", "blockers": ["missing-pre-p0-contract"]}
        pre_p0_status = "pass" if pre_p0.get("execution_ready") else str(pre_p0.get("status") or "repair-required")
        pre_experiment = pre_experiment_cards.get(idea_id) or {"execution_authorized": False, "status": "missing-card", "blockers": ["missing-pre-experiment-card"]}
        pre_experiment_status = "pass" if pre_experiment.get("execution_authorized") else str(pre_experiment.get("status") or "blocked")
        for phase in phases:
            phase_id = str(phase.get("id"))
            plan = _phase_plan(idea, phase)
            authorized, blocked_by = _phase_authorization(phase_id, phase_statuses, approval_decision, p0_gate_status, pre_p0_status, pre_experiment_status)
            plan["execution_authorized"] = authorized
            plan["blocked_by"] = blocked_by
            plan["next_action"] = f"execute-{phase_id}" if authorized else _blocked_next_action(blocked_by)
            result = latest.get((idea_id, phase_id))
            if result:
                plan.update({
                    "status": result["result"],
                    "result": result,
                    "reported_next_action": result.get("next_action"),
                    "execution_authorized": False,
                    "blocked_by": None,
                    "next_action": _default_next_action(phase_id, str(result["result"])),
                })
            plans.append(plan)

    statuses = Counter(plan["status"] for plan in plans)
    idea_states: list[dict[str, Any]] = []
    by_idea: dict[str, list[dict[str, Any]]] = {}
    for plan in plans:
        by_idea.setdefault(str(plan["idea_id"]), []).append(plan)
    for idea in idea_bank.get("passed_ideas") or []:
        idea_id = str(idea["id"])
        phases = sorted(by_idea.get(idea_id, []), key=lambda item: item["phase"])
        approval = latest_approvals.get(idea_id)
        state = _idea_state(phases, approval)
        idea_states.append({
            "idea_id": idea["id"],
            "title": idea.get("title"),
            "rank": idea.get("rank"),
            "state": state,
            "p0_gate_status": CURRENT_P0_GATE.get(idea_id, "not-current-p0-candidate"),
            "pre_p0_gate_status": "pass" if (pre_p0_by_id.get(idea_id) or {}).get("execution_ready") else str((pre_p0_by_id.get(idea_id) or {}).get("status") or "missing-contract"),
            "pre_p0_audit": pre_p0_by_id.get(idea_id),
            "pre_experiment_gate_status": "pass" if (pre_experiment_cards.get(idea_id) or {}).get("execution_authorized") else str((pre_experiment_cards.get(idea_id) or {}).get("status") or "missing-card"),
            "pre_experiment_card": pre_experiment_cards.get(idea_id),
            "p0_human_approval": approval,
            "completed_phases": sum(phase["status"] in {"pass", "revise", "fail", "blocked"} for phase in phases),
            "total_phases": len(phases),
            "next_phase": next((phase["phase"] for phase in phases if phase["status"] in {"planned", "running"} and phase.get("execution_authorized")), None),
            "next_action": next((phase["next_action"] for phase in phases if phase["status"] in {"planned", "running"} and phase.get("execution_authorized")), "await-human-approval" if state == "awaiting-human-approval" else next((phase["next_action"] for phase in phases if phase["phase"] == "P0" and phase["status"] in {"planned", "running"}), None)),
        })
    idea_states.sort(key=lambda item: (item.get("rank") or 999, item["idea_id"]))

    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "result_dir": str(result_dir),
        "approval_dir": str(approval_dir),
        "result_schema": pilot_result_schema(),
        "approval_schema": pilot_approval_schema(),
        "policy": {
            "p0_only_before_human_review": True,
            "p0_pass_requires_explicit_human_approval_before_p1": True,
            "approval_artifact_required": True,
            "automatic_p0_to_p1_forbidden": True,
            "p0_execution_requires_pre_p0_pass": True,
            "p0_execution_requires_pre_experiment_8_of_8": True,
        },
        "summary": {
            "ideas": len(idea_states),
            "phases": len(plans),
            "status_counts": dict(statuses.most_common()),
            "valid_result_files": len(valid_results),
            "invalid_result_files": sum(not bool(item.get("invalidated")) for item in invalid_results),
            "invalidated_result_files": sum(bool(item.get("invalidated")) for item in invalid_results),
            "valid_approval_files": len(valid_approvals),
            "invalid_approval_files": len(invalid_approvals),
            "awaiting_human_approval": sum(item["state"] == "awaiting-human-approval" for item in idea_states),
            "p0_authorized": sum(any(phase["phase"] == "P0" and phase["status"] in {"planned", "running"} and phase.get("execution_authorized") for phase in by_idea.get(str(item["idea_id"]), [])) for item in idea_states),
            "pre_p0_ready": sum(str(item.get("pre_p0_gate_status")) == "pass" for item in idea_states),
            "pre_experiment_ready": sum(str(item.get("pre_experiment_gate_status")) == "pass" for item in idea_states),
            "p1_authorized": sum(any(phase["phase"] == "P1" and phase["status"] in {"planned", "running"} and phase.get("execution_authorized") for phase in by_idea.get(str(item["idea_id"]), [])) for item in idea_states),
            "pilot_ready": sum(item["state"] == "pilot-ready" for item in idea_states),
            "selected_ready": sum(item["state"] == "selected-ready" for item in idea_states),
            "stopped": sum(item["state"] == "stop" for item in idea_states),
        },
        "ideas": idea_states,
        "phases": plans,
        "invalid_results": invalid_results,
        "invalid_approvals": invalid_approvals,
    }


def _phase_authorization(phase: str, statuses: dict[str, str], approval_decision: str, p0_gate_status: str, pre_p0_status: str = "repair-required", pre_experiment_status: str = "blocked") -> tuple[bool, str | None]:
    if phase == "P0":
        if p0_gate_status != "ready":
            return False, p0_gate_status
        if pre_p0_status != "pass":
            return False, "pre-p0-identifiability"
        if pre_experiment_status != "pass":
            return False, "pre-experiment-8-gate"
        return True, None
    if phase == "P1":
        if statuses.get("P0") != "pass":
            return False, "P0-pass-required"
        if approval_decision != "approve":
            return False, "human-approval-after-P0-required"
        return True, None
    if phase == "P2":
        if statuses.get("P1") != "pass":
            return False, "P1-pass-required"
        if approval_decision != "approve":
            return False, "human-approval-after-P0-required"
        return True, None
    return False, "unknown-phase"


def _blocked_next_action(blocked_by: str | None) -> str:
    if blocked_by == "human-approval-after-P0-required":
        return "await-human-approval"
    if blocked_by == "P0-pass-required":
        return "await-P0-result"
    if blocked_by == "P1-pass-required":
        return "await-P1-result"
    if blocked_by == "collision-recheck":
        return "complete-collision-recheck"
    if blocked_by == "method-redesign":
        return "redesign-method-before-P0"
    if blocked_by == "scenario-check":
        return "confirm-scenario-before-P0"
    if blocked_by == "pre-p0-identifiability":
        return "repair-pre-p0-identifiability-before-P0"
    if blocked_by == "pre-experiment-8-gate":
        return "repair-pre-experiment-card-before-P0"
    if blocked_by == "not-current-p0-candidate":
        return "not-authorized-by-current-human-review"
    return "wait"


def _default_next_action(phase: str, result: str) -> str:
    if result == "pass":
        return {"P0": "await-human-approval", "P1": "execute-P2", "P2": "candidate-selection"}.get(phase, "review")
    if result == "revise":
        return "revise-mechanism-and-repeat"
    if result in {"fail", "blocked"}:
        return "stop-or-return-to-gap-mining"
    return "continue"


def _idea_state(phases: list[dict[str, Any]], approval: dict[str, Any] | None = None) -> str:
    statuses = {str(phase["phase"]): str(phase["status"]) for phase in phases}
    if any(status in {"fail", "blocked"} for status in statuses.values()):
        return "stop"
    if statuses.get("P2") == "pass":
        return "selected-ready"
    if statuses.get("P1") == "pass":
        return "pilot-ready"
    if statuses.get("P0") == "pass":
        if str((approval or {}).get("decision") or "") != "approve":
            return "awaiting-human-approval"
        return "mechanism-pilot"
    if any(status == "revise" for status in statuses.values()):
        return "revise"
    if any(status == "running" for status in statuses.values()):
        return "running"
    return "planned"
