from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .p0_common import mean, rounded, safe_div


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    current_task_gain: float
    edit_size: float
    behavior_drift: float
    hidden_delta: float
    hidden_before: tuple[float, ...]
    hidden_after: tuple[float, ...]

    @property
    def harmful(self) -> bool:
        return self.hidden_delta < -0.02

    @property
    def useful(self) -> bool:
        return self.current_task_gain > 0 and not self.harmful


def _candidate(row: dict[str, Any], config: dict[str, Any]) -> Candidate:
    before = row.get("probe_features_before") or {}
    after = row.get("probe_features_after") or {}
    analysis = config.get("analysis") or {}
    weights = analysis.get("drift_weights") or {
        "action_sequence_distance": 0.35,
        "invalid_action_rate": 0.25,
        "instruction_choice_shift": 0.25,
        "plan_length": 0.15,
    }
    scales = analysis.get("feature_scales") or {}
    drift = 0.0
    total_weight = 0.0
    for key, weight in weights.items():
        if key not in before or key not in after:
            raise ValueError(f"candidate {row.get('candidate_id')} missing probe feature {key}")
        scale = float(scales.get(key, 1.0)) or 1.0
        drift += float(weight) * abs(float(after[key]) - float(before[key])) / scale
        total_weight += float(weight)
    hidden_before = tuple(float(x) for x in row.get("hidden_before") or [])
    hidden_after = tuple(float(x) for x in row.get("hidden_after") or [])
    if not hidden_before or len(hidden_before) != len(hidden_after):
        raise ValueError(f"candidate {row.get('candidate_id')} hidden_before/after must be non-empty and matched")
    return Candidate(
        candidate_id=str(row["candidate_id"]),
        current_task_gain=float(row["current_task_gain"]),
        edit_size=float(row["edit_size"]),
        behavior_drift=drift / total_weight if total_weight else drift,
        hidden_delta=mean(a - b for a, b in zip(hidden_after, hidden_before)),
        hidden_before=hidden_before,
        hidden_after=hidden_after,
    )


def _metrics(name: str, chosen: list[Candidate], all_rows: list[Candidate]) -> dict[str, Any]:
    accepted = {row.candidate_id for row in chosen}
    useful_total = sum(row.useful for row in all_rows)
    rejected_useful = sum(row.useful and row.candidate_id not in accepted for row in all_rows)
    task_deltas = [a - b for row in chosen for a, b in zip(row.hidden_after, row.hidden_before)]
    return {
        "policy": name,
        "accepted": len(chosen),
        "harmful_updates": sum(row.harmful for row in chosen),
        "harmful_rate": rounded(safe_div(sum(row.harmful for row in chosen), len(chosen))),
        "worst_hidden_task_regression": rounded(min(task_deltas) if task_deltas else 0.0),
        "mean_hidden_delta": rounded(mean(row.hidden_delta for row in chosen)),
        "mean_current_task_gain": rounded(mean(row.current_task_gain for row in chosen)),
        "useful_update_false_rejection_rate": rounded(safe_div(rejected_useful, useful_total)),
    }


def analyze(rows: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]:
    candidates = [_candidate(row, config) for row in rows]
    if len(candidates) < 8:
        raise ValueError("A-1 requires at least 8 candidate updates even for a dry run")
    acceptance_rate = float((config.get("analysis") or {}).get("acceptance_rate", 0.5))
    k = max(1, min(len(candidates), round(len(candidates) * acceptance_rate)))
    policies = {
        "current-task-gain": sorted(candidates, key=lambda x: (-x.current_task_gain, x.candidate_id))[:k],
        "prompt-edit-size": sorted(candidates, key=lambda x: (x.edit_size, x.candidate_id))[:k],
        "behavior-drift": sorted(candidates, key=lambda x: (x.behavior_drift, -x.current_task_gain, x.candidate_id))[:k],
        "gain+behavior-drift": sorted(candidates, key=lambda x: (x.current_task_gain <= 0, x.behavior_drift, -x.current_task_gain, x.candidate_id))[:k],
        "accept-all": list(candidates),
    }
    table = [_metrics(name, chosen, candidates) for name, chosen in policies.items()]
    by_name = {row["policy"]: row for row in table}
    strongest = min(
        (by_name["current-task-gain"], by_name["prompt-edit-size"]),
        key=lambda row: (row["harmful_rate"], -row["mean_current_task_gain"]),
    )
    proposed = by_name["gain+behavior-drift"]
    if strongest["harmful_rate"] > 0:
        reduction = (strongest["harmful_rate"] - proposed["harmful_rate"]) / strongest["harmful_rate"]
    else:
        reduction = 0.0 if proposed["harmful_rate"] == 0 else -1.0
    gain_loss = strongest["mean_current_task_gain"] - proposed["mean_current_task_gain"]
    gate = config.get("go_gate") or {}
    go = reduction >= float(gate.get("min_harmful_reduction", 0.25)) and gain_loss <= float(gate.get("max_target_gain_loss", 0.02))
    return {
        "idea_id": "update-trust-region",
        "phase": "P0",
        "candidate_count": len(candidates),
        "matched_acceptance_count": k,
        "table": table,
        "strongest_simple_baseline": strongest["policy"],
        "harmful_update_reduction": rounded(reduction),
        "target_gain_loss": rounded(gain_loss),
        "decision": "pass" if go else "fail",
        "go": go,
        "diagnosis": "Current-task gain plus behavioral drift clears the preregistered P0 gate." if go else "Current-task gain plus behavioral drift does not clear the preregistered P0 gate.",
    }


def synthetic_rows() -> list[dict[str, Any]]:
    rows = []
    for i in range(12):
        harmful = i in {1, 4, 7, 10}
        drift = 0.65 if harmful else 0.08 + (i % 3) * 0.03
        gain = 0.08 - (i % 4) * 0.01 + (0.03 if harmful else 0.0)
        rows.append({
            "candidate_id": f"u{i:02d}",
            "current_task_gain": gain,
            "edit_size": 0.1 + (i % 5) * 0.08,
            "probe_features_before": {"action_sequence_distance": 0.0, "invalid_action_rate": 0.05, "instruction_choice_shift": 0.0, "plan_length": 8.0},
            "probe_features_after": {"action_sequence_distance": drift, "invalid_action_rate": 0.05 + drift * 0.2, "instruction_choice_shift": drift * 0.8, "plan_length": 8.0 + drift * 4},
            "hidden_before": [1, 1, 1, 1, 1, 1],
            "hidden_after": [0, 0, 1, 1, 1, 1] if harmful else [1, 1, 1, 1, 1, 1],
        })
    return rows
