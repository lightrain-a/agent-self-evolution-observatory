from __future__ import annotations

from dataclasses import dataclass, replace
import random
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


def _harmful_rate(rows: list[Candidate]) -> float:
    return safe_div(sum(row.harmful for row in rows), len(rows))


def _ranked_policies(candidates: list[Candidate], k: int) -> dict[str, list[Candidate]]:
    return {
        "current-task-gain": sorted(candidates, key=lambda x: (-x.current_task_gain, x.candidate_id))[:k],
        "prompt-edit-size": sorted(candidates, key=lambda x: (x.edit_size, x.candidate_id))[:k],
        "behavior-drift": sorted(candidates, key=lambda x: (x.behavior_drift, -x.current_task_gain, x.candidate_id))[:k],
        "gain+behavior-drift": sorted(candidates, key=lambda x: (x.current_task_gain <= 0, x.behavior_drift, -x.current_task_gain, x.candidate_id))[:k],
        "accept-all": list(candidates),
    }


def _bootstrap_reduction_interval(candidates: list[Candidate], acceptance_rate: float, confidence: float, seed: int, samples: int = 2000) -> tuple[float, float]:
    rng = random.Random(seed)
    n = len(candidates)
    values: list[float] = []
    for draw in range(samples):
        sampled = [replace(rng.choice(candidates), candidate_id=f"b{draw}-{i}") for i in range(n)]
        k = max(1, min(n, round(n * acceptance_rate)))
        policies = _ranked_policies(sampled, k)
        current = policies["current-task-gain"]
        edit = policies["prompt-edit-size"]
        current_rate, edit_rate = _harmful_rate(current), _harmful_rate(edit)
        current_gain = mean(row.current_task_gain for row in current)
        edit_gain = mean(row.current_task_gain for row in edit)
        if (current_rate, -current_gain) <= (edit_rate, -edit_gain):
            strongest = current
        else:
            strongest = edit
        baseline_rate = _harmful_rate(strongest)
        proposed_rate = _harmful_rate(policies["gain+behavior-drift"])
        if baseline_rate > 0:
            values.append((baseline_rate - proposed_rate) / baseline_rate)
        else:
            values.append(0.0 if proposed_rate == 0 else -1.0)
    values.sort()
    alpha = max(0.0, min(1.0, 1.0 - confidence))
    lo_index = max(0, min(len(values) - 1, int((alpha / 2) * len(values))))
    hi_index = max(0, min(len(values) - 1, int((1 - alpha / 2) * len(values)) - 1))
    return rounded(values[lo_index]), rounded(values[hi_index])


def analyze(rows: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]:
    candidates = [_candidate(row, config) for row in rows]
    if len(candidates) < 8:
        raise ValueError("A-1 requires at least 8 candidate updates even for a dry run")
    acceptance_rate = float((config.get("analysis") or {}).get("acceptance_rate", 0.5))
    k = max(1, min(len(candidates), round(len(candidates) * acceptance_rate)))
    policies = _ranked_policies(candidates, k)
    table = [_metrics(name, chosen, candidates) for name, chosen in policies.items()]
    by_name = {row["policy"]: row for row in table}
    strongest = min(
        (by_name["current-task-gain"], by_name["prompt-edit-size"]),
        key=lambda row: (row["harmful_rate"], -row["mean_current_task_gain"]),
    )
    proposed = by_name["gain+behavior-drift"]
    harmful_candidates = sum(row.harmful for row in candidates)
    analysis_cfg = config.get("analysis") or {}
    screening_only = bool(analysis_cfg.get("screening_only"))
    min_harmful = int(analysis_cfg.get("minimum_harmful_candidates_for_decision", 0))
    if min_harmful and harmful_candidates < min_harmful:
        raise ValueError(
            "A-1 identifiability gate failed: "
            f"only {harmful_candidates} harmful candidates observed, fewer than required {min_harmful}; "
            "this run is inconclusive and must not be interpreted as a scientific method FAIL"
        )
    if strongest["harmful_rate"] > 0:
        reduction = (strongest["harmful_rate"] - proposed["harmful_rate"]) / strongest["harmful_rate"]
    else:
        reduction = 0.0 if proposed["harmful_rate"] == 0 else -1.0
    gain_loss = strongest["mean_current_task_gain"] - proposed["mean_current_task_gain"]
    common = {
        "idea_id": "update-trust-region",
        "phase": str(config.get("phase") or "P0"),
        "candidate_count": len(candidates),
        "matched_acceptance_count": k,
        "harmful_candidate_count": harmful_candidates,
        "table": table,
        "strongest_simple_baseline": strongest["policy"],
        "harmful_update_reduction": rounded(reduction),
        "target_gain_loss": rounded(gain_loss),
    }
    if screening_only:
        required = int(analysis_cfg.get("minimum_harmful_candidates_for_interpretation", 4))
        if harmful_candidates < required:
            return {**common, "decision": "screening-inconclusive", "go": None, "diagnosis": f"Only {harmful_candidates} harmful candidates were observed; expand or repeat screening. This does not reject the idea."}
        screening_gain_loss = float(analysis_cfg.get("screening_max_target_gain_loss", 0.05))
        directional = reduction > 0 and gain_loss <= screening_gain_loss
        return {
            **common,
            "decision": "screening-signal" if directional else "screening-no-signal",
            "go": None,
            "diagnosis": "Screening shows a directional signal; confirmatory P0 remains blocked until independent Pre-Experiment identifiability and probe-fidelity gates pass." if directional else "Screening does not show a directional signal yet; review or repeat screening, but do not reject the idea.",
        }

    confidence = float(analysis_cfg.get("bootstrap_confidence", 0.95))
    reduction_ci = _bootstrap_reduction_interval(candidates, acceptance_rate, confidence, int((config.get("seeds") or [42])[0]))
    gate = config.get("go_gate") or {}
    threshold = float(gate.get("min_harmful_reduction", 0.25))
    gain_ok = gain_loss <= float(gate.get("max_target_gain_loss", 0.02))
    interval_crosses_zero = reduction_ci[0] <= 0 <= reduction_ci[1]
    if bool(analysis_cfg.get("inconclusive_if_interval_crosses_zero")) and interval_crosses_zero:
        decision, go = "revise", False
        diagnosis = "Confirmatory harmful-reduction uncertainty crosses zero; the result is inconclusive and requires more evidence rather than a method FAIL."
    else:
        go = reduction >= threshold and gain_ok
        decision = "pass" if go else "fail"
        diagnosis = "Current-task gain plus behavioral drift clears the preregistered P0 gate." if go else "Current-task gain plus behavioral drift does not clear the preregistered P0 gate."
    return {
        **common,
        "harmful_update_reduction_ci": {"confidence": confidence, "low": reduction_ci[0], "high": reduction_ci[1]},
        "decision": decision,
        "go": go,
        "diagnosis": diagnosis,
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
