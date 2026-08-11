from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT, StorageSettings, resolve_experiment_data_root

DEFAULT_JSON = PROJECT_ROOT / "generated" / "p0-a3-substrate-stop.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "p0-a3-substrate-stop.js"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_state() -> dict[str, Any]:
    root = resolve_experiment_data_root(StorageSettings.from_env())
    updater = _load(root / "pre-experiment" / "evidence" / "updater-competence" / "a1-localized-updater-qualification-v1.json")
    panel = _load(root / "pre-gpu" / "a3-mastered-probe-panel-v1.json")
    screening = _load(root / "pre-experiment-a1-screening-review-20260810.json")
    repair = _load(PROJECT_ROOT / "research_pipeline" / "p0_a3_probe_repair_config.json")
    metrics = updater.get("metrics") or {}
    thresholds = updater.get("thresholds") or {}
    fidelity = screening.get("probe_fidelity") or {}
    competence_pass = bool((updater.get("gate") or {}).get("passed"))
    fresh_outputs = [root / name for name in repair.get("outputs") or []]
    fresh_present = any(path.exists() for path in fresh_outputs)
    hard_stop = (not competence_pass) and not bool(repair.get("execution_authorized")) and not fresh_present
    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "idea_id": "regression-gated-self-evolution",
        "code": "A-3",
        "scientific_scope": "current Qwen2.5-7B-Instruct + ALFWorld persistent-prompt-patch P0 substrate only",
        "updater_competence": {
            "passed": competence_pass,
            "candidate_count": metrics.get("candidate_count"),
            "positive_target_gain_candidates": metrics.get("positive_target_gain_candidates"),
            "effective_candidate_fraction": metrics.get("effective_candidate_fraction"),
            "required_positive_target_gain_candidates": thresholds.get("positive_target_gain_candidates"),
            "required_effective_candidate_fraction": thresholds.get("effective_candidate_fraction"),
            "authorization_effect": updater.get("authorization_effect"),
        },
        "mastered_panel": {
            "passed": bool(panel.get("pass")),
            "panel_size": panel.get("panel_size"),
            "mastered_candidates": panel.get("mastered_candidates"),
            "task_family_coverage": repair.get("scope", {}).get("mastered_probe_panel", {}).get("task_family_coverage"),
        },
        "legacy_probe_fidelity": {
            "aggregate_panel_loo_auc": fidelity.get("aggregate_panel_leave_one_candidate_out_auc"),
            "best_single_probe_auc": fidelity.get("best_single_probe_action_auc"),
            "minimum_required_auc": fidelity.get("minimum_fidelity_auc"),
            "passed": bool(fidelity.get("fidelity_pass")),
            "role": "supporting negative evidence only; not the final A-3 marginal-probe-value test",
        },
        "fresh_final_a3_test": {
            "execution_authorized": bool(repair.get("execution_authorized")),
            "blocked_by": repair.get("blocked_by") or [],
            "fresh_candidate_validation_required": bool(repair.get("analysis", {}).get("fresh_candidate_validation_required")),
            "fresh_outputs_present": fresh_present,
            "hidden_original_opened": False,
            "method_result_available": False,
        },
        "decision": "STOP_CURRENT_SUBSTRATE_UPDATER_INCOMPETENT" if hard_stop else "HOLD_A3_SUBSTRATE_REVIEW",
        "current_substrate_stop_authorized": hard_stop,
        "method_failure_authorized": False,
        "exact_method_stop_fired": False,
        "interpretation": "The current prompt-patch updater fails a block-only competence prerequisite, so fresh A-3 collection is forbidden. The final marginal-probe-value versus hidden-original-fidelity claim was never legally tested and must not be called a method failure.",
        "next_action": "Stop GPU work on this prompt-patch P0 instance. Reopen A-3 only with a newly qualified update substrate/action stream and a newly frozen fresh-candidate validation; otherwise send the direction to human pivot/drop review.",
    }


def write_state(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    state = build_state()
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.P0_A3_SUBSTRATE_STOP = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return state


if __name__ == "__main__":
    print(json.dumps(write_state(), ensure_ascii=False, indent=2))
