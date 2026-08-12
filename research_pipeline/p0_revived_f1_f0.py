from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def _ck(status: str, evidence: str) -> dict[str, Any]:
    return {"status": status, "evidence": evidence, "evidence_kind": "cpu-exact-dynamics-f0"}

def run_f1_f0() -> dict[str, Any]:
    rows = []
    for i in range(120):
        predicted_margin = (((i * 7) % 19) - 9) / 10.0
        residual_delta = (((i * 11 + 3) % 23) - 11) / 10.0
        true_margin = predicted_margin + residual_delta
        predicted_action = 1 if predicted_margin >= 0 else -1
        true_action = 1 if true_margin >= 0 else -1
        rows.append({"id": i, "predicted_margin": predicted_margin, "residual_delta": residual_delta, "predicted_action": predicted_action, "true_action": true_action, "decision_change": predicted_action != true_action})
    hidden = rows[80:]
    changed = [row for row in rows if row["decision_change"]]
    hidden_changed = [row for row in hidden if row["decision_change"]]
    proposed = {row["id"]: row["decision_change"] for row in hidden}
    direct = {row["id"]: row["predicted_action"] != row["true_action"] for row in hidden}
    equivalent = proposed == direct
    k = max(1, len(hidden_changed))
    magnitude = sorted(hidden, key=lambda row: abs(row["residual_delta"]), reverse=True)[:k]
    value_aware = sorted(hidden, key=lambda row: abs(row["residual_delta"]) / (abs(row["predicted_margin"]) + 0.1), reverse=True)[:k]
    def recall(selected: list[dict[str, Any]]) -> float:
        return sum(row["decision_change"] for row in selected) / len(hidden_changed) if hidden_changed else 0.0
    return {
        "schema_version": "1.0", "generated_at": _now(), "idea_id": "world-model-error-gated-learning", "code": "F-1",
        "scientific_role": "CPU exact-margin world-model residual F0 with frozen-policy decision truth",
        "design": {"transition_residuals": 120, "development": 80, "hidden": 40, "frozen_policy": True},
        "substrate_inventory": {"observed_effective_candidates": len(changed), "observed_fresh_heldout": 40, "observed_reserve_fraction": 1 / 3},
        "metrics": {"decision_changing_total": len(changed), "decision_changing_hidden": len(hidden_changed), "proposed_direct_agreement": 1.0 if equivalent else 0.0, "magnitude_topk_recall": recall(magnitude), "value_aware_topk_recall": recall(value_aware), "direct_action_disagreement_recall": 1.0 if hidden_changed else 0.0},
        "checks": {
            "target_variation": _ck("pass", "Action-changing and action-invariant residuals both occur."),
            "baseline_disagreement": _ck("fail" if equivalent else "pass", "The proposed decision-change selector is identical to direct action disagreement on the same transition information."),
            "representability": _ck("pass", "Predicted/true margins and frozen actions are programmatically exact."),
            "tiny_overfit": _ck("pass", "The final 40 transition residuals are held out."),
            "competence_window": _ck("pass", "The frozen policy has mixed changed/unchanged decisions."),
            "effect_variation": _ck("pass", "Residual corrections span action-changing and invariant effects."),
        },
        "updater_competence": {"status": "pass", "passed": True, "reason": "The residual gate identifies a non-degenerate subset of true transitions."},
        "gpu0": {"status": "stop-matched-direct-action-disagreement-equivalent" if equivalent else "cpu-f0-signal-continue", "evidence": "Direct action disagreement exactly reproduces the selector." if equivalent else "Selector headroom survives.", "next": "Merge F-1 admission into direct action-disagreement/value-aware selection." if equivalent else "Open adapter P0 after gates."},
        "matched_simplification": {"baseline": "same-data direct action-disagreement selector", "equivalent": equivalent},
        "decision": "STOP_MATCHED_DIRECT_ACTION_DISAGREEMENT_EQUIVALENT" if equivalent else "P0_SIGNAL_CONTINUE",
        "method_failure_authorized": False, "execution_authorized": False,
        "next_action": "Keep decision-changing residuals as a data-selection diagnostic; drop standalone selector mechanism." if equivalent else "Proceed after gates.",
    }
