from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .principle_adjudication import FAILURE_LAYER_SPECS

DEFAULT_JSON = PROJECT_ROOT / "generated" / "p0-decision-ledger.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "p0-decision-ledger.js"

DIAGNOSIS_REQUIRED_STATES = frozenset({
    "experiment-stop-await-human-review",
    "method-development-stop",
    "experiment-merge",
    "upstream-hold",
})

FAILURE_CLASS_TO_LAYER = {
    "IMPLEMENTATION_ERROR": "execution",
    "RUNTIME_ERROR": "execution",
    "PROVENANCE_INCONCLUSIVE": "execution",
    "BUDGET_STOP": "execution",
    "FAIL_SUBSTRATE": "experiment_identifiability",
    "FAIL_TARGET_DEGENERACY": "experiment_identifiability",
    "SUPPORT_INSUFFICIENT": "experiment_identifiability",
    "FAIL_REPRESENTATION": "operationalization",
    "FAIL_BASELINE_CEILING": "method_realization",
    "METHOD_FAIL": "method_realization",
    "FAIL_PROBLEM": "assumption_scope",
    "PRINCIPLE_DEAD_END": "core_principle",
}

LAYER_TO_MIGRATED_FAILURE_CLASS = {
    "execution": "HISTORICAL_EXECUTION_FAILURE",
    "experiment_identifiability": "HISTORICAL_IDENTIFIABILITY_OR_SUPPORT_FAILURE",
    "optimization": "HISTORICAL_OPTIMIZATION_FAILURE",
    "operationalization": "HISTORICAL_OPERATIONALIZATION_FAILURE",
    "method_realization": "HISTORICAL_METHOD_OR_REDUCTION_FAILURE",
    "assumption_scope": "HISTORICAL_ASSUMPTION_OR_SCOPE_FAILURE",
    "core_principle": "HISTORICAL_PRINCIPLE_FAILURE",
}

POLICY = {
    "schema_version": "1.2",
    "one_current_row_per_active_p0": True,
    "lifecycle_and_execution_decision_are_separate": True,
    "economy_stop_overrides_planned_registry_display": True,
    "execution_artifact_overrides_plan": True,
    "human_terminal_state_remains_lifecycle_authority": True,
    "scientific_stop_does_not_rewrite_p0_lifecycle": True,
    "failed_or_held_experiment_requires_failure_layer": True,
    "failure_layer_schema": tuple(FAILURE_LAYER_SPECS),
    "failure_layer_requires_evidence_next_action_and_principle_authority": True,
    "unknown_failure_layer_blocks_ledger_build_and_publication": True,
    "historical_rows_are_migrated_from_existing_typed_artifacts_not_reinterpreted_as_new_evidence": True,
    "only_core_principle_layer_may_allow_principle_update": True,
    "principle_update_requires_explicit_dead_end_certificate": True,
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _terminal_rows(human_state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {**(human_state.get("parents") or {}), **(human_state.get("independent_methods") or {})}


def _token(value: Any) -> str:
    return str(value or "").strip().upper().replace("-", "_").replace(" ", "_")


def _infer_failure_layer(
    override: dict[str, Any],
    primary_stop: str,
    gpu0_status: str,
    p0_decision: str,
    current_state: str,
) -> tuple[str | None, str]:
    explicit_layer = str(override.get("failure_layer") or "").strip()
    if explicit_layer:
        if explicit_layer not in FAILURE_LAYER_SPECS:
            raise ValueError(f"unknown explicit failure_layer: {explicit_layer}")
        return explicit_layer, "explicit-failure-layer"

    failure_class = _token(override.get("failure_class"))
    if failure_class:
        layer = FAILURE_CLASS_TO_LAYER.get(failure_class)
        if layer is None:
            raise ValueError(f"unmapped failure_class: {failure_class}")
        return layer, f"explicit-failure-class:{failure_class}"

    stop = _token(primary_stop)
    if stop == "SUBSTRATE":
        return "experiment_identifiability", "economy-stop:substrate"
    if stop == "MATCHED_SIMPLIFICATION":
        return "method_realization", "economy-stop:matched-simplification"
    if stop == "VOI":
        return "experiment_identifiability", "economy-stop:voi"

    status = _token(gpu0_status)
    if status:
        if any(part in status for part in ("RUNTIME", "IMPLEMENTATION_ERROR", "PROVENANCE", "BUDGET")):
            return "execution", f"offline-gpu0:{status}"
        if any(part in status for part in ("REPRESENTATION", "OBJECTIVE_CLAIM", "MEASUREMENT", "OPERATIONALIZATION")):
            return "operationalization", f"offline-gpu0:{status}"
        if any(part in status for part in ("UNDERFIT", "OPTIMIZATION", "CAPACITY")):
            return "optimization", f"offline-gpu0:{status}"
        if any(part in status for part in ("SUBSTRATE", "SUPPORT_INSUFFICIENT", "DEGENERATE", "INSUFFICIENT")):
            return "experiment_identifiability", f"offline-gpu0:{status}"
        if any(part in status for part in ("MATCHED", "EQUIVALENT", "DOMINATES", "NO_HEADROOM", "CEILING")):
            return "method_realization", f"offline-gpu0:{status}"

    decision = _token(p0_decision)
    if decision:
        if "PRINCIPLE_DEAD_END" in decision:
            return "core_principle", f"terminal-decision:{decision}"
        if any(part in decision for part in ("ASSUMPTION", "SCOPE_REFIN", "SCOPE_VIOLATION")):
            return "assumption_scope", f"terminal-decision:{decision}"
        if any(part in decision for part in ("REPRESENTATION", "OBJECTIVE", "OPERATIONALIZATION")):
            return "operationalization", f"terminal-decision:{decision}"
        if any(part in decision for part in ("UNDERFIT", "OPTIMIZATION", "CAPACITY")):
            return "optimization", f"terminal-decision:{decision}"
        if any(part in decision for part in ("SUBSTRATE", "SUPPORT_INSUFFICIENT", "DEGENERATE", "NO_R1_VOI")):
            return "experiment_identifiability", f"terminal-decision:{decision}"
        if any(part in decision for part in ("MATCHED", "EQUIVALENT", "DOMINATES", "SIMPLE", "ARCHIVE_AS_SECONDARY", "MERGE_DIAGNOSTIC")):
            return "method_realization", f"terminal-decision:{decision}"

    if current_state in DIAGNOSIS_REQUIRED_STATES:
        raise ValueError(
            f"state {current_state} requires a failure layer, but no typed evidence maps "
            f"failure_class={failure_class or '--'} primary_stop={primary_stop or '--'} "
            f"gpu0={gpu0_status or '--'} decision={p0_decision or '--'}"
        )
    return None, "not-required"


def _failure_evidence(
    override: dict[str, Any],
    gpu0: dict[str, Any],
    economy: dict[str, Any],
    term: dict[str, Any],
    p0_decision: str,
) -> dict[str, Any]:
    if override:
        return {
            "source": "four-direction-iteration",
            "evidence_sha256": str(override.get("evidence_sha256") or ""),
            "metrics": override.get("final_method_metrics") or override.get("support_metrics") or override.get("metrics") or {},
            "decision": str(override.get("decision") or ""),
        }
    gpu_status = str(gpu0.get("status") or gpu0.get("phenomenon") or "")
    gpu_statement = str(gpu0.get("evidence") or "")
    gpu_source = str(gpu0.get("source") or "")
    gpu_kind = str(gpu0.get("evidence_kind") or "")
    gpu_has_negative_detail = bool(gpu_statement or gpu_source or gpu_kind) or _token(gpu_status) not in {"", "PASS", "QUALIFIED"}
    if gpu0 and gpu_has_negative_detail:
        return {
            "source": gpu_source or "offline-qualification",
            "status": gpu_status,
            "evidence_kind": gpu_kind,
            "statement": gpu_statement,
        }
    economy_stop = str(economy.get("primary_stop_class") or "")
    if economy and economy_stop:
        return {
            "source": "economy-gate",
            "status": str(economy.get("status") or ""),
            "primary_stop_class": economy_stop,
        }
    current_fact = term.get("current_fact") or {}
    statement = str(current_fact.get("en") or current_fact.get("zh") or "") if isinstance(current_fact, dict) else str(current_fact or "")
    return {"source": "human-terminal/current-fact", "decision": p0_decision, "statement": statement}


def audit_failure_diagnosis(row: dict[str, Any]) -> dict[str, Any]:
    required = str(row.get("current_state") or "") in DIAGNOSIS_REQUIRED_STATES
    if not required:
        return {"required": False, "complete": True, "blockers": []}
    blockers: list[str] = []
    layer = str(row.get("failure_layer") or "")
    if layer not in FAILURE_LAYER_SPECS:
        blockers.append("failure-layer-missing-or-invalid")
    evidence = row.get("failure_evidence")
    if not isinstance(evidence, dict) or not evidence or not str(evidence.get("source") or "").strip():
        blockers.append("failure-evidence-missing")
    elif not any((
        str(evidence.get("evidence_sha256") or "").strip(),
        str(evidence.get("statement") or "").strip(),
        str(evidence.get("decision") or "").strip(),
        str(evidence.get("primary_stop_class") or "").strip(),
        bool(evidence.get("metrics")),
    )):
        blockers.append("failure-evidence-detail-missing")
    if not str(row.get("failure_layer_basis") or "").strip():
        blockers.append("failure-layer-basis-missing")
    if not str(row.get("next_action") or "").strip():
        blockers.append("failure-next-action-missing")
    if not isinstance(row.get("principle_update_allowed"), bool):
        blockers.append("principle-update-authority-missing")
    elif row.get("principle_update_allowed") is True and layer != "core_principle":
        blockers.append("non-principle-layer-cannot-update-principle")
    if row.get("principle_update_allowed") is True:
        if row.get("principle_dead_end_certified") is not True:
            blockers.append("principle-update-without-dead-end-certificate")
        counter = row.get("counter_explanation")
        if not isinstance(counter, dict) or not counter:
            blockers.append("principle-update-without-counter-explanation")
    return {"required": True, "complete": not blockers, "blockers": blockers}


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
        updater_status = str(((preflight.get("updater_competence") or {}).get("status") or ""))
        gpu0_status = str(gpu0.get("status") or gpu0.get("phenomenon") or "")
        support_hold = gpu0_status.startswith("hold-f0-support-insufficient") or updater_status.startswith("hold-support-insufficient")
        if override:
            current_state = str(override.get("current_state") or "experiment-stop-await-human-review")
            next_action = str(override.get("next_action") or "review-latest-experiment-decision")
        elif p0_decision:
            current_state = "experiment-stop-await-human-review"
            next_action = str(gpu0.get("next") or "human-merge-drop-or-pivot-review")
        elif support_hold:
            current_state = "upstream-hold"
            next_action = str(gpu0.get("next") or "repair-or-expand-local-support-substrate-before-method-admission")
        elif primary_stop == "matched-simplification":
            current_state = "experiment-stop-await-human-review"
            next_action = str(gpu0.get("next") or "human-merge-drop-or-pivot-review")
        elif primary_stop == "substrate":
            current_state = "upstream-hold"
            next_action = str(gpu0.get("next") or "collect-or-qualify-required-substrate")
        elif primary_stop == "voi":
            current_state = "method-development-stop"
            next_action = str(gpu0.get("next") or "repair-decision-changing-value-before-more-compute")
        elif preflight.get("execution_authorized") is True:
            current_state = "launchable"
            next_action = "launch-under-single-writer-authority"
        elif economy.get("execution_compilation_authorized") is not True:
            current_state = "economy-blocked"
            next_action = "repair-economy-contract-before-pre-experiment"
        else:
            current_state = "method-admission-blocked"
            next_action = "complete-post-support-method-admission-and-runtime-gates"

        failure_layer, failure_layer_basis = _infer_failure_layer(
            override, primary_stop, gpu0_status, p0_decision, current_state
        )
        explicit_failure_class = str(override.get("failure_class") or "").strip()
        failure_class = explicit_failure_class or (LAYER_TO_MIGRATED_FAILURE_CLASS.get(failure_layer or "") if failure_layer else None)
        principle_dead_end_certified = bool(override.get("principle_dead_end_certified") or term.get("principle_dead_end_certified"))
        counter_explanation = override.get("counter_explanation") or term.get("counter_explanation") or None
        principle_update_allowed = bool(
            failure_layer == "core_principle" and principle_dead_end_certified and isinstance(counter_explanation, dict) and counter_explanation
        )
        row = {
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
            "failure_class": failure_class,
            "failure_layer": failure_layer,
            "failure_layer_basis": failure_layer_basis,
            "failure_evidence": _failure_evidence(override, gpu0, economy, term, p0_decision) if failure_layer else None,
            "principle_update_allowed": principle_update_allowed,
            "principle_dead_end_certified": principle_dead_end_certified,
            "counter_explanation": counter_explanation,
            "latest_metrics": override.get("final_method_metrics") or override.get("support_metrics") or override.get("metrics") or {},
            "source_priority": (["four-direction-iteration"] if override else []) + ["human-terminal", "economy-gate", "offline-qualification", "execution-preflight"],
        }
        audit = audit_failure_diagnosis(row)
        row["failure_diagnosis_complete"] = audit["complete"]
        row["failure_diagnosis_blockers"] = audit["blockers"]
        if audit["required"] and not audit["complete"]:
            raise ValueError(f"incomplete failure diagnosis for {idea_id}: {audit['blockers']}")
        rows.append(row)

    counts = Counter(str(row["current_state"]) for row in rows)
    required_rows = [row for row in rows if str(row.get("current_state") or "") in DIAGNOSIS_REQUIRED_STATES]
    failure_layers = Counter(str(row.get("failure_layer")) for row in required_rows if row.get("failure_layer"))
    diagnosis_complete = sum(bool(row.get("failure_diagnosis_complete")) for row in required_rows)
    return {
        "schema_version": "1.1",
        "generated_at": _now(),
        "policy": POLICY,
        "failure_layer_specs": FAILURE_LAYER_SPECS,
        "summary": {
            "active_p0": len(rows),
            "state_counts": dict(counts),
            "experiment_stopped": counts.get("experiment-stop-await-human-review", 0) + counts.get("method-development-stop", 0),
            "experiment_merged": counts.get("experiment-merge", 0),
            "upstream_hold": counts.get("upstream-hold", 0),
            "method_development_stop": counts.get("method-development-stop", 0),
            "latest_iteration_overrides": sum(row.get("decision_source") == "four-direction-iteration" for row in rows),
            "economy_blocked": counts.get("economy-blocked", 0),
            "compile_blocked": counts.get("compile-blocked", 0),
            "method_admission_blocked": counts.get("method-admission-blocked", 0),
            "launchable": counts.get("launchable", 0),
            "execution_authorized": sum(bool(row["execution_authorized"]) for row in rows),
            "failure_diagnosis_required": len(required_rows),
            "failure_diagnosis_complete": diagnosis_complete,
            "failure_diagnosis_incomplete": len(required_rows) - diagnosis_complete,
            "failure_layer_counts": dict(failure_layers),
            "principle_updates_allowed": sum(bool(row.get("principle_update_allowed")) for row in required_rows),
        },
        "rows": rows,
    }


def write_p0_decision_ledger(ledger: dict[str, Any], json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    errors: list[str] = []
    for row in ledger.get("rows") or []:
        audit = audit_failure_diagnosis(row)
        if audit["required"] and not audit["complete"]:
            errors.append(f"{row.get('idea_id')}: {','.join(audit['blockers'])}")
    if errors:
        raise ValueError("P0 decision ledger contains untyped terminal/hold rows: " + "; ".join(errors))
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.P0_DECISION_LEDGER = " + json.dumps(ledger, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return ledger
