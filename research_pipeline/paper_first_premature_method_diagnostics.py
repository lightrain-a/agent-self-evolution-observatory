from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT, StorageSettings, resolve_experiment_data_root

DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-premature-method-diagnostics.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "paper-first-premature-method-diagnostics.js"

RUN_RELATIVE = Path("runs") / "paper-first-p0-method-20260812"

AUTHORITY = {
    "authority_type": "premature-paper-first-method-diagnostic-only",
    "scientific_authority": False,
    "p0_lifecycle_authority": False,
    "local_validation_authority": False,
    "method_authority": False,
    "principle_authority": False,
    "full_experiment_authority": False,
    "cannot_retroactively_authorize": True,
    "cannot_override_problem_or_design_adjudication": True,
    "can_only_supply_reducibility_or_failure_asset_evidence": True,
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _sha(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _pf4_design_row(design: dict[str, Any]) -> dict[str, Any]:
    return next((row for row in design.get("rows") or [] if row.get("id") == "PF-4"), {})


def build_premature_method_diagnostics(data_root: Path | None = None) -> dict[str, Any]:
    root = data_root or resolve_experiment_data_root(StorageSettings.from_env())
    run_root = root / RUN_RELATIVE
    # Historical authority must come from the versioned generated artifacts, not a
    # fresh builder invocation whose volatile generated_at would rewrite ordering.
    pf1_authority = _load(PROJECT_ROOT / "generated" / "paper-first-pf1-problem-adjudication.json")
    design_authority = _load(PROJECT_ROOT / "generated" / "paper-first-design-adjudication.json")
    pf4_authority = _pf4_design_row(design_authority)

    a8_v1_path = run_root / "a8" / "result.json"
    a8_v1_trace = run_root / "a8" / "raw-traces.jsonl"
    a8_v2_path = run_root / "a8-v2" / "result.json"
    a8_v2_freeze_path = run_root / "a8-v2" / "decision-freeze.json"
    a8_v2_trace = run_root / "a8-v2" / "raw-traces.jsonl"
    c7_path = run_root / "c7" / "method-precheck.json"

    a8_v1 = _load(a8_v1_path)
    a8_v2 = _load(a8_v2_path)
    a8_freeze = _load(a8_v2_freeze_path) or (a8_v2.get("decision_freeze") or {})
    c7 = _load(c7_path)

    selected = a8_freeze.get("selected") or {}
    selected_id = str(selected.get("proposed_future_learnability") or "")
    selected_metrics = (a8_freeze.get("metrics") or {}).get(selected_id) or {}
    a8 = {
        "incubation_id": "PF-1",
        "historical_code": "A-8",
        "idea_id": "future-learnability-preserving-self-evolution",
        "status": "complete-diagnostic-quarantined" if a8_v2.get("status") == "complete" else "diagnostic-artifact-incomplete",
        "authority": dict(AUTHORITY),
        "v1_design_diagnosis": {
            "decision": a8_v1.get("decision"),
            "diagnosis": a8_v1.get("diagnosis"),
            "current_baseline": a8_v1.get("observed_baseline", {}).get("current_rate"),
            "retention_baseline": a8_v1.get("observed_baseline", {}).get("retention_rate"),
            "raw_trace_rows": a8_v1.get("provenance", {}).get("raw_trace_rows"),
            "hidden_executed": bool(a8_v1.get("hidden_executed")),
            "artifact_sha256": _sha(a8_v1_path),
            "raw_trace_sha256": _sha(a8_v1_trace) or a8_v1.get("provenance", {}).get("raw_trace_sha256"),
        },
        "v2_observed_method_diagnostic": {
            "decision": a8_v2.get("decision"),
            "baseline_reverification": a8_v2.get("baseline_reverification") or {},
            "eligible_candidates": len(a8_freeze.get("eligible") or []),
            "selected_proposed": selected.get("proposed_future_learnability"),
            "selected_same_information_post_only": selected.get("strongest_same_information_post_only"),
            "same_information_decision_disagreement": bool(a8_freeze.get("method_post_only_disagreement")),
            "selected_probe_adaptation_gain": selected_metrics.get("probe_adaptation_gain"),
            "hidden_authorized": bool(a8_freeze.get("hidden_authorized")),
            "hidden_executed": bool(a8_v2.get("hidden_executed")),
            "artifact_sha256": _sha(a8_v2_path),
            "decision_freeze_sha256": _sha(a8_v2_freeze_path),
            "raw_trace_sha256": _sha(a8_v2_trace),
            "completed_at": a8_v2.get("completed_at"),
        },
        "dominant_problem_authority": {
            "decision": pf1_authority.get("decision"),
            "paper_problem_status": pf1_authority.get("paper_problem_status"),
            "artifact_generated_at": pf1_authority.get("generated_at"),
            "artifact_sha256": _sha(PROJECT_ROOT / "generated" / "paper-first-pf1-problem-adjudication.json"),
            "timestamp_is_not_authority": True,
            "problem_stop_dominates_diagnostic_regardless_of_rebuild_timestamp": True,
            "p0_authorized": bool((pf1_authority.get("authority") or {}).get("p0_authorized")),
            "gpu_authorized": bool((pf1_authority.get("authority") or {}).get("gpu_authorized")),
        },
        "diagnostic_interpretation": (
            "The v1 retention floor is evidence of an experiment-design failure, not a method negative. "
            "After repairing only the mastered-task substrate, v2 reverified current/retention at 4/4 and 4/4, "
            "but the Future-Learnability selector and the strongest same-information post-adaptation-success baseline "
            "both selected c2. This corroborates reducibility of the historical gate, but cannot reopen or override the "
            "already-terminal PF-1 paper-problem adjudication."
        ),
        "surviving_asset": "future-update-responsiveness may remain a cross-cutting audit dimension; the standalone gate/paper thesis remains closed",
    }

    c7 = {
        "incubation_id": "PF-4",
        "historical_code": "C-7",
        "idea_id": "diagnosability-preserving-self-evolution",
        "status": "complete-diagnostic-quarantined" if c7.get("decision") else "diagnostic-artifact-incomplete",
        "authority": dict(AUTHORITY),
        "observed_method_diagnostic": {
            "decision": c7.get("decision"),
            "same_information_decision_disagreement": c7.get("same_information_decision_disagreement"),
            "proposed_selection": (c7.get("decisions") or {}).get("proposed_diagnosability_constraint"),
            "same_information_soft_scalar_selection": (c7.get("decisions") or {}).get("strongest_same_information_soft_scalar"),
            "fresh_gpu_authorized": bool(c7.get("fresh_gpu_authorized")),
            "baseline_no_repair_diagnostic_accuracy": c7.get("baseline_no_repair_diagnostic_accuracy"),
            "surface_metrics_development_only": c7.get("surface_metrics_development_only") or {},
            "artifact_sha256": _sha(c7_path),
            "source_trace_sha256": c7.get("trace_sha256"),
        },
        "dominant_design_authority": {
            "verdict": pf4_authority.get("verdict"),
            "current_method_disposition": pf4_authority.get("current_method_disposition"),
            "merge_target": pf4_authority.get("merge_target"),
            "merge_role": pf4_authority.get("merge_role"),
            "local_validation_authorized": bool(pf4_authority.get("local_validation_authorized")),
            "full_experiment_authorized": bool(pf4_authority.get("full_experiment_authorized")),
        },
        "diagnostic_interpretation": (
            "The historical hard diagnosability constraint and a same-information utility+diagnosability scalarization "
            "both selected workflow, with no fresh GPU authorized. This corroborates the latest Paper Design decision to "
            "treat diagnosability preservation as a cross-cutting invariant rather than an irreducible standalone method."
        ),
        "surviving_asset": "diagnosability preservation remains a cross-cutting commit/verification invariant merged into the repair-surface problem",
    }

    cards = [a8, c7]
    completed = sum(row.get("status") == "complete-diagnostic-quarantined" for row in cards)
    same_information_stops = sum(
        str((row.get("v2_observed_method_diagnostic") or row.get("observed_method_diagnostic") or {}).get("decision") or "").startswith("STOP_MATCHED_")
        for row in cards
    )
    hidden = sum(bool((row.get("v2_observed_method_diagnostic") or {}).get("hidden_executed")) for row in cards)
    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "run_root": str(run_root),
        "authority": dict(AUTHORITY),
        "policy": {
            "preserve_machine_artifacts_even_when_execution_lacked_authority": True,
            "diagnostic_results_cannot_create_or_restore_p0_lifecycle": True,
            "diagnostic_results_cannot_override_problem_or_design_adjudication": True,
            "same_information_reducibility_can_be_reused_as_failure_asset": True,
            "no_additional_gpu_or_hidden_execution_is_authorized": True,
        },
        "summary": {
            "directions": len(cards),
            "completed_diagnostics": completed,
            "design_holds": int(a8_v1.get("diagnosis") == "design-nonidentifiable"),
            "same_information_reducibility_findings": same_information_stops,
            "hidden_executions": hidden,
            "scientifically_authorized": 0,
            "p0_lifecycle_mutations": 0,
            "full_experiment_authorized": 0,
        },
        "cards": cards,
    }


def _is_complete_frozen_snapshot(state: dict[str, Any]) -> bool:
    summary = state.get("summary") or {}
    cards = state.get("cards") or []
    return bool(
        summary.get("directions") == 2
        and summary.get("completed_diagnostics") == 2
        and summary.get("same_information_reducibility_findings") == 2
        and summary.get("hidden_executions") == 0
        and summary.get("scientifically_authorized") == 0
        and summary.get("p0_lifecycle_mutations") == 0
        and summary.get("full_experiment_authorized") == 0
        and len(cards) == 2
        and all((row.get("status") == "complete-diagnostic-quarantined") for row in cards if isinstance(row, dict))
        and len([row for row in cards if isinstance(row, dict)]) == 2
    )


def resolve_premature_method_diagnostics(
    data_root: Path | None = None,
    *,
    snapshot_path: Path = DEFAULT_JSON,
) -> dict[str, Any]:
    """Resolve host-local evidence without degrading a validated frozen artifact.

    Historical PF-1/PF-4 diagnostics may live on a different execution host. A
    host that cannot see those raw runs must consume the last complete,
    non-authoritative generated snapshot rather than reinterpret missing files as
    new scientific evidence. If neither source is complete, fail closed.
    """
    local = build_premature_method_diagnostics(data_root)
    if _is_complete_frozen_snapshot(local):
        return local
    frozen = _load(snapshot_path)
    if _is_complete_frozen_snapshot(frozen):
        return frozen
    raise RuntimeError("premature method diagnostic source is incomplete and no valid frozen snapshot is available")


def write_premature_method_diagnostics(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    state = resolve_premature_method_diagnostics(snapshot_path=json_path)
    # If the resolver returned the existing frozen snapshot, avoid rewriting it
    # solely because this host lacks the historical raw run tree.
    existing = _load(json_path)
    if existing == state and json_path.exists():
        if not js_path.exists():
            js_path.parent.mkdir(parents=True, exist_ok=True)
            js_path.write_text(
                "window.PAPER_FIRST_PREMATURE_METHOD_DIAGNOSTICS = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n",
                encoding="utf-8",
            )
        return state
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text(
        "window.PAPER_FIRST_PREMATURE_METHOD_DIAGNOSTICS = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    return state


if __name__ == "__main__":
    print(json.dumps(write_premature_method_diagnostics(), ensure_ascii=False, indent=2))
