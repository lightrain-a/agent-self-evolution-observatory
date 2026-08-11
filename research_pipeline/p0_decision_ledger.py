from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from .config import PROJECT_ROOT

DEFAULT_JSON = PROJECT_ROOT / "generated" / "p0-decision-ledger.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "p0-decision-ledger.js"

POLICY = {
    "schema_version": "1.0",
    "one_current_row_per_active_p0": True,
    "lifecycle_and_execution_decision_are_separate": True,
    "economy_stop_overrides_planned_registry_display": True,
    "execution_artifact_overrides_plan": True,
    "human_terminal_state_remains_lifecycle_authority": True,
    "scientific_stop_does_not_rewrite_p0_lifecycle": True,
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _terminal_rows(human_state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {**(human_state.get("parents") or {}), **(human_state.get("independent_methods") or {})}


def build_p0_decision_ledger(
    admission_state: dict[str, Any],
    offline_state: dict[str, Any],
    human_state: dict[str, Any],
    experiment_overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    offline = {str(row.get("idea_id")): row for row in offline_state.get("cards") or []}
    terminal = _terminal_rows(human_state)
    overrides = (experiment_overrides or {}).get("ideas") or {}
    rows: list[dict[str, Any]] = []
    for card in admission_state.get("cards") or []:
        idea_id = str(card.get("idea_id") or "")
        term = terminal.get(idea_id) or {}
        preflight = card.get("execution_preflight") or {}
        economy = preflight.get("economy_gate") or {}
        off = offline.get(idea_id) or {}
        gpu0 = off.get("gpu0") or preflight.get("gpu0") or {}
        override = overrides.get(idea_id) or {}
        p0_decision = str(override.get("decision") or term.get("p0_decision") or term.get("p0_screening_decision") or "")
        primary_stop = str(economy.get("primary_stop_class") or "")
        if override:
            current_state = str(override.get("current_state") or "experiment-stop-await-human-review")
            next_action = str(override.get("next_action") or "review-latest-experiment-decision")
        elif p0_decision or primary_stop:
            current_state = "experiment-stop-await-human-review"
            next_action = "human-merge-drop-or-pivot-review"
        elif preflight.get("execution_authorized") is True:
            current_state = "launchable"
            next_action = "launch-under-single-writer-authority"
        elif economy.get("execution_compilation_authorized") is not True:
            current_state = "economy-blocked"
            next_action = "repair-economy-contract-before-pre-experiment"
        else:
            current_state = "compile-blocked"
            next_action = "complete-pre-experiment-and-runtime-gates"
        rows.append({
            "idea_id": idea_id,
            "code": card.get("code"),
            "group": card.get("group"),
            "lifecycle": str(term.get("terminal_state") or card.get("lifecycle") or ""),
            "p0_decision": p0_decision or None,
            "economy_status": economy.get("status"),
            "economy_stop_class": primary_stop or None,
            "offline_gpu0_status": gpu0.get("status") or gpu0.get("phenomenon"),
            "execution_authorized": bool(override.get("execution_authorized")) if override else bool(preflight.get("execution_authorized")),
            "current_state": current_state,
            "next_action": next_action,
            "decision_source": "four-direction-iteration" if override else "human/economy/offline/preflight",
            "failure_class": override.get("failure_class") if override else None,
            "latest_metrics": override.get("final_method_metrics") or override.get("support_metrics") or override.get("metrics") or {},
            "source_priority": (["four-direction-iteration"] if override else []) + ["human-terminal", "economy-gate", "offline-qualification", "execution-preflight"],
        })
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["current_state"]] = counts.get(row["current_state"], 0) + 1
    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "policy": POLICY,
        "summary": {
            "active_p0": len(rows),
            "state_counts": counts,
            "experiment_stopped": counts.get("experiment-stop-await-human-review", 0) + counts.get("method-development-stop", 0),
            "experiment_merged": counts.get("experiment-merge", 0),
            "upstream_hold": counts.get("upstream-hold", 0),
            "method_development_stop": counts.get("method-development-stop", 0),
            "latest_iteration_overrides": sum(row.get("decision_source") == "four-direction-iteration" for row in rows),
            "economy_blocked": counts.get("economy-blocked", 0),
            "compile_blocked": counts.get("compile-blocked", 0),
            "launchable": counts.get("launchable", 0),
            "execution_authorized": sum(bool(row["execution_authorized"]) for row in rows),
        },
        "rows": rows,
    }


def write_p0_decision_ledger(ledger: dict[str, Any], json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.P0_DECISION_LEDGER = " + json.dumps(ledger, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return ledger
