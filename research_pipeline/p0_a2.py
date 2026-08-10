from __future__ import annotations

import random
import statistics
from typing import Any, Iterable

from .p0_common import mean, rounded, safe_div


def _decision_utility(seq: dict[str, Any], decision: tuple[int, int], config: dict[str, Any]) -> float:
    analysis = config.get("analysis") or {}
    selected_index, observed_index = decision
    selected = seq["rounds"][selected_index]
    observed = seq["rounds"][observed_index]
    return (
        float(selected["success"])
        - float(analysis.get("regression_lambda", 0.4)) * float(selected.get("regression", 0.0))
        - float(analysis.get("cost_lambda", 0.01)) * float(observed["cumulative_calls"])
    )


def _fixed(seq: dict[str, Any], rounds: int) -> tuple[int, int]:
    index = min(rounds, len(seq["rounds"])) - 1
    return index, index


def _heuristic_grid(config: dict[str, Any]) -> Iterable[tuple[float, float, float, int]]:
    grid = (config.get("analysis") or {}).get("heuristic_grid") or {}
    for min_gain in grid.get("min_gain", [0.0, 0.02, 0.05]):
        for max_reg in grid.get("max_probe_regression", [0.1, 0.25, 0.4]):
            for max_dis in grid.get("max_disagreement", [0.2, 0.4, 0.6]):
                for max_calls in grid.get("max_calls", [4, 8, 12]):
                    yield float(min_gain), float(max_reg), float(max_dis), int(max_calls)


def _heuristic(seq: dict[str, Any], params: tuple[float, float, float, int]) -> tuple[int, int]:
    min_gain, max_reg, max_dis, max_calls = params
    selected = 0
    for index, row in enumerate(seq["rounds"]):
        if index > 0 and (
            float(row["marginal_gain"]) < min_gain
            or float(row["probe_regression"]) > max_reg
            or float(row["disagreement"]) > max_dis
            or int(row["cumulative_calls"]) > max_calls
        ):
            return max(0, index - 1), index
        selected = index
    return selected, selected


def _fit_heuristic(seqs: list[dict[str, Any]], config: dict[str, Any]) -> tuple[float, float, float, int]:
    best: tuple[float, tuple[float, float, float, int]] | None = None
    for params in _heuristic_grid(config):
        score = mean(_decision_utility(seq, _heuristic(seq, params), config) for seq in seqs)
        if best is None or score > best[0]:
            best = (score, params)
    if best is None:
        raise ValueError("empty heuristic grid")
    return best[1]


def _scales(seqs: list[dict[str, Any]]) -> dict[str, tuple[float, float]]:
    keys = ("marginal_gain", "probe_regression", "disagreement", "cumulative_calls")
    values = {key: [float(row[key]) for seq in seqs for row in seq["rounds"]] for key in keys}
    return {key: (mean(vals), statistics.pstdev(vals) or 1.0) for key, vals in values.items()}


def _linear_score(row: dict[str, Any], weights: tuple[float, float, float, float], scales: dict[str, tuple[float, float]]) -> float:
    keys = ("marginal_gain", "probe_regression", "disagreement", "cumulative_calls")
    z = [(float(row[key]) - scales[key][0]) / scales[key][1] for key in keys]
    signed = (z[0], -z[1], -z[2], -z[3])
    return sum(weight * value for weight, value in zip(weights, signed))


def _linear(seq: dict[str, Any], weights: tuple[float, float, float, float], threshold: float, scales: dict[str, tuple[float, float]]) -> tuple[int, int]:
    selected = 0
    for index, row in enumerate(seq["rounds"]):
        if index > 0 and _linear_score(row, weights, scales) < threshold:
            return max(0, index - 1), index
        selected = index
    return selected, selected


def _fit_linear(seqs: list[dict[str, Any]], config: dict[str, Any]):
    scales = _scales(seqs)
    levels = (0.25, 0.5, 1.0, 2.0)
    thresholds = (-1.0, -0.5, 0.0, 0.5, 1.0)
    best = None
    for w0 in levels:
        for w1 in levels:
            for w2 in levels:
                for w3 in levels:
                    weights = (w0, w1, w2, w3)
                    for threshold in thresholds:
                        score = mean(_decision_utility(seq, _linear(seq, weights, threshold, scales), config) for seq in seqs)
                        if best is None or score > best[0]:
                            best = (score, weights, threshold)
    if best is None:
        raise ValueError("empty learned-controller grid")
    return best[1], best[2], scales


def _metrics(name: str, seqs: list[dict[str, Any]], selector) -> dict[str, Any]:
    decisions = [selector(seq) for seq in seqs]
    selected = [seq["rounds"][decision[0]] for seq, decision in zip(seqs, decisions)]
    observed = [seq["rounds"][decision[1]] for seq, decision in zip(seqs, decisions)]
    return {
        "policy": name,
        "tasks": len(seqs),
        "success_rate": rounded(mean(float(row["success"]) for row in selected)),
        "mean_calls": rounded(mean(float(row["cumulative_calls"]) for row in observed)),
        "regression_rate": rounded(mean(float(row.get("regression", 0.0)) for row in selected)),
        "mean_round": rounded(mean(float(row.get("round", 1)) for row in selected)),
        "mean_observed_round": rounded(mean(float(row.get("round", 1)) for row in observed)),
    }


def _evaluate_table(hidden: list[dict[str, Any]], heuristic, weights, threshold, scales) -> list[dict[str, Any]]:
    return [
        _metrics("fixed-1", hidden, lambda seq: _fixed(seq, 1)),
        _metrics("fixed-2", hidden, lambda seq: _fixed(seq, 2)),
        _metrics("fixed-4", hidden, lambda seq: _fixed(seq, 4)),
        _metrics("tuned-heuristic", hidden, lambda seq: _heuristic(seq, heuristic)),
        _metrics("learned-linear-controller", hidden, lambda seq: _linear(seq, weights, threshold, scales)),
    ]


def _comparison(table: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any], float, float]:
    by_name = {row["policy"]: row for row in table}
    proposed = by_name["learned-linear-controller"]
    simple = [by_name[name] for name in ("fixed-1", "fixed-2", "fixed-4", "tuned-heuristic")]
    eligible = [row for row in simple if row["success_rate"] >= proposed["success_rate"] - 0.02]
    strongest = min(eligible or simple, key=lambda row: (row["mean_calls"], -row["success_rate"], row["regression_rate"]))
    saved = safe_div(strongest["mean_calls"] - proposed["mean_calls"], strongest["mean_calls"])
    success_loss = strongest["success_rate"] - proposed["success_rate"]
    return proposed, strongest, saved, success_loss


def _bootstrap_call_saving_interval(hidden: list[dict[str, Any]], heuristic, weights, threshold, scales, confidence: float, seed: int, samples: int = 2000) -> tuple[float, float]:
    rng = random.Random(seed)
    n = len(hidden)
    values: list[float] = []
    for _ in range(samples):
        sampled = [rng.choice(hidden) for _ in range(n)]
        _, _, saved, _ = _comparison(_evaluate_table(sampled, heuristic, weights, threshold, scales))
        values.append(saved)
    values.sort()
    alpha = max(0.0, min(1.0, 1.0 - confidence))
    lo = max(0, min(len(values) - 1, int((alpha / 2) * len(values))))
    hi = max(0, min(len(values) - 1, int((1 - alpha / 2) * len(values)) - 1))
    return rounded(values[lo]), rounded(values[hi])


def analyze(rows: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]:
    discovery = [row for row in rows if row.get("split") in {"discovery", "calibration"}]
    hidden = [row for row in rows if row.get("split") == "hidden"]
    if len(discovery) < 6 or len(hidden) < 6:
        raise ValueError("A-2 requires at least 6 discovery/calibration and 6 hidden sequences")
    if any(not row.get("rounds") for row in rows):
        raise ValueError("every A-2 sequence needs at least one fixed candidate round")

    analysis_cfg = config.get("analysis") or {}
    screening_only = bool(analysis_cfg.get("screening_only"))
    ident = (analysis_cfg.get("identifiability") or {})
    hidden_oracle_success = mean(
        max(float(round_row.get("success", 0.0)) for round_row in seq["rounds"])
        for seq in hidden
    )
    discovery_change_fraction = mean(
        float(len({float(round_row.get("success", 0.0)) for round_row in seq["rounds"]}) > 1)
        for seq in discovery
    )
    min_oracle = float(ident.get("minimum_hidden_oracle_success_rate", 0.0))
    min_change = float(ident.get("minimum_discovery_sequences_with_success_change_fraction", 0.0))
    ident_payload = {
        "hidden_oracle_success_rate": rounded(hidden_oracle_success),
        "discovery_success_change_fraction": rounded(discovery_change_fraction),
    }
    if hidden_oracle_success < min_oracle or discovery_change_fraction < min_change:
        if screening_only:
            return {
                "idea_id": "budgeted-evolution-controller",
                "phase": str(config.get("phase") or "P0-screening"),
                "discovery_sequences": len(discovery),
                "hidden_sequences": len(hidden),
                "identifiability": ident_payload,
                "table": [],
                "decision": "screening-inconclusive",
                "go": None,
                "diagnosis": "Screening lacks sufficient outcome variation; revise the base agent/update sequence or expand screening. This does not reject the idea.",
            }
        raise ValueError(
            "A-2 identifiability gate failed: "
            f"hidden_oracle_success_rate={hidden_oracle_success:.4f} < {min_oracle:.4f} or "
            f"discovery_success_change_fraction={discovery_change_fraction:.4f} < {min_change:.4f}; "
            "this is an inconclusive/floor-effect run, not a scientific method FAIL"
        )

    heuristic = _fit_heuristic(discovery, config)
    weights, threshold, scales = _fit_linear(discovery, config)
    table = _evaluate_table(hidden, heuristic, weights, threshold, scales)
    proposed, strongest, saved, success_loss = _comparison(table)
    common = {
        "idea_id": "budgeted-evolution-controller",
        "phase": "P0",
        "discovery_sequences": len(discovery),
        "hidden_sequences": len(hidden),
        "identifiability": ident_payload,
        "frozen_heuristic": {"min_gain": heuristic[0], "max_probe_regression": heuristic[1], "max_disagreement": heuristic[2], "max_calls": heuristic[3]},
        "frozen_linear_controller": {"weights": list(weights), "threshold": threshold},
        "table": table,
        "strongest_simple_baseline": strongest["policy"],
        "calls_saved_fraction": rounded(saved),
        "success_loss": rounded(success_loss),
    }
    if screening_only:
        screening_success_loss = float(analysis_cfg.get("screening_max_success_loss", 0.05))
        directional = saved > 0 and success_loss <= screening_success_loss and proposed["regression_rate"] <= strongest["regression_rate"]
        return {
            **common,
            "decision": "screening-signal" if directional else "screening-no-signal",
            "go": None,
            "diagnosis": "Screening shows a directional call-saving signal; proceed to confirmatory P0." if directional else "Screening does not show a directional controller signal yet; review or repeat screening, but do not reject the idea.",
        }

    confidence = float(analysis_cfg.get("bootstrap_confidence", 0.95))
    saving_ci = _bootstrap_call_saving_interval(hidden, heuristic, weights, threshold, scales, confidence, int((config.get("seeds") or [42])[0]))
    gate = config.get("go_gate") or {}
    point_go = (
        saved >= float(gate.get("min_call_saving", 0.25))
        and success_loss <= float(gate.get("max_success_loss", 0.02))
        and proposed["regression_rate"] <= strongest["regression_rate"]
    )
    interval_crosses_zero = saving_ci[0] <= 0 <= saving_ci[1]
    if bool(analysis_cfg.get("inconclusive_if_interval_crosses_zero")) and interval_crosses_zero:
        decision, go = "revise", False
        diagnosis = "Confirmatory call-saving uncertainty crosses zero; the result is inconclusive and requires more evidence rather than a method FAIL."
    else:
        decision, go = ("pass", True) if point_go else ("fail", False)
        diagnosis = "The frozen controller clears the preregistered P0 gate." if go else "The frozen controller does not clear the preregistered P0 gate."
    return {
        **common,
        "calls_saved_fraction_ci": {"confidence": confidence, "low": saving_ci[0], "high": saving_ci[1]},
        "decision": decision,
        "go": go,
        "diagnosis": diagnosis,
    }


def synthetic_rows() -> list[dict[str, Any]]:
    rows = []
    for i in range(24):
        split = "hidden" if i >= 12 else ("calibration" if i >= 6 else "discovery")
        optimum = 1 + (i % 2)
        rounds = []
        calls = 0
        for r in range(4):
            calls += 3
            rounds.append({
                "round": r + 1,
                "marginal_gain": 0.22 if r < optimum else (0.01 if r == optimum else -0.04),
                "probe_regression": 0.05 if r <= optimum else 0.45,
                "disagreement": 0.1 if r <= optimum else 0.55,
                "cumulative_calls": calls,
                "success": 1.0 if r >= optimum else 0.0,
                "regression": 0.0 if r <= optimum else 1.0,
            })
        rows.append({"task_id": f"t{i:02d}", "split": split, "rounds": rounds})
    return rows
