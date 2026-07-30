from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import StorageSettings

VALID_PHASES = {"P0", "P1", "P2"}
VALID_RESULTS = {"pass", "revise", "fail", "blocked", "running", "planned"}


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
        errors = validate_result(payload)
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
        "next_action": "execute",
    }


def _result_order(item: dict[str, Any]) -> tuple[str, str]:
    return str(item.get("completed_at") or item.get("updated_at") or ""), str(item.get("source_path") or "")


def build_pilot_registry(
    idea_bank: dict[str, Any],
    *,
    result_dir: Path | None = None,
) -> dict[str, Any]:
    storage = StorageSettings.from_env()
    result_dir = result_dir or storage.run_dir / "pilots" / "results"
    valid_results, invalid_results = load_results(result_dir)
    latest: dict[tuple[str, str], dict[str, Any]] = {}
    for result in sorted(valid_results, key=_result_order):
        latest[(str(result["idea_id"]), str(result["phase"]))] = result

    plans: list[dict[str, Any]] = []
    for idea in idea_bank.get("passed_ideas") or []:
        phases = (idea.get("experiment_protocol") or {}).get("phases") or []
        for phase in phases:
            plan = _phase_plan(idea, phase)
            result = latest.get((str(idea["id"]), str(phase.get("id"))))
            if result:
                plan.update({
                    "status": result["result"],
                    "result": result,
                    "next_action": result.get("next_action") or _default_next_action(str(phase.get("id")), str(result["result"])),
                })
            plans.append(plan)

    statuses = Counter(plan["status"] for plan in plans)
    idea_states: list[dict[str, Any]] = []
    by_idea: dict[str, list[dict[str, Any]]] = {}
    for plan in plans:
        by_idea.setdefault(str(plan["idea_id"]), []).append(plan)
    for idea in idea_bank.get("passed_ideas") or []:
        phases = sorted(by_idea.get(str(idea["id"]), []), key=lambda item: item["phase"])
        state = _idea_state(phases)
        idea_states.append({
            "idea_id": idea["id"],
            "title": idea.get("title"),
            "rank": idea.get("rank"),
            "state": state,
            "completed_phases": sum(phase["status"] in {"pass", "revise", "fail", "blocked"} for phase in phases),
            "total_phases": len(phases),
            "next_phase": next((phase["phase"] for phase in phases if phase["status"] in {"planned", "running"}), None),
        })
    idea_states.sort(key=lambda item: (item.get("rank") or 999, item["idea_id"]))

    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "result_dir": str(result_dir),
        "result_schema": pilot_result_schema(),
        "summary": {
            "ideas": len(idea_states),
            "phases": len(plans),
            "status_counts": dict(statuses.most_common()),
            "valid_result_files": len(valid_results),
            "invalid_result_files": len(invalid_results),
            "pilot_ready": sum(item["state"] == "pilot-ready" for item in idea_states),
            "selected_ready": sum(item["state"] == "selected-ready" for item in idea_states),
            "stopped": sum(item["state"] == "stop" for item in idea_states),
        },
        "ideas": idea_states,
        "phases": plans,
        "invalid_results": invalid_results,
    }


def _default_next_action(phase: str, result: str) -> str:
    if result == "pass":
        return {"P0": "execute-P1", "P1": "execute-P2", "P2": "candidate-selection"}.get(phase, "review")
    if result == "revise":
        return "revise-mechanism-and-repeat"
    if result in {"fail", "blocked"}:
        return "stop-or-return-to-gap-mining"
    return "continue"


def _idea_state(phases: list[dict[str, Any]]) -> str:
    statuses = {str(phase["phase"]): str(phase["status"]) for phase in phases}
    if any(status in {"fail", "blocked"} for status in statuses.values()):
        return "stop"
    if statuses.get("P2") == "pass":
        return "selected-ready"
    if statuses.get("P1") == "pass":
        return "pilot-ready"
    if statuses.get("P0") == "pass":
        return "mechanism-pilot"
    if any(status == "revise" for status in statuses.values()):
        return "revise"
    if any(status == "running" for status in statuses.values()):
        return "running"
    return "planned"
