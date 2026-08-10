from __future__ import annotations

import math
from typing import Any

from .pre_experiment_science import gate
from .pre_experiment_specs import TYPED_OUTCOMES


def _estimate_a1_episodes(config: dict[str, Any], candidate_count: int) -> dict[str, int]:
    scope = config.get("scope") or {}
    discovery = int(scope.get("discovery_failures_target", 20))
    discovery_cap = int(scope.get("discovery_episode_cap", discovery))
    probes = int(scope.get("behavior_probes", 8))
    hidden_pool = int(scope.get("hidden_original_tasks_target", 24))
    hidden_each = int(scope.get("hidden_tasks_per_candidate", 8))
    baseline = discovery + probes + hidden_pool
    candidate_eval = candidate_count * (1 + probes + hidden_each)
    return {"baseline": baseline, "candidate_evaluation": candidate_eval, "total": baseline + candidate_eval, "worst_case_total": discovery_cap + probes + hidden_pool + candidate_eval}


def _estimate_a2_episodes(config: dict[str, Any]) -> dict[str, int]:
    scope = config.get("scope") or {}
    splits = scope.get("sequence_splits") or {"discovery": 8, "calibration": 8, "hidden": 12}
    sequences = sum(int(value) for value in splits.values())
    rounds = int(scope.get("max_update_rounds", 4))
    probes = int(scope.get("behavior_probes", 2))
    per_sequence = 1 + rounds * (1 + probes)
    return {"sequences": sequences, "per_sequence": per_sequence, "baseline_probes": probes, "total": probes + sequences * per_sequence}


def compute_estimate(idea_id: str, config: dict[str, Any]) -> dict[str, Any]:
    scope = config.get("scope") or {}
    throughput = (config.get("pre_experiment") or {}).get("throughput") or config.get("throughput_basis") or {}
    mean_steps = float(throughput.get("mean_steps_per_episode") or 0.0)
    calls_per_gpu_hour = float(throughput.get("calls_per_gpu_hour") or 0.0)
    if idea_id == "update-trust-region":
        candidate_count = int(max(scope.get("candidate_updates_target") or [0]))
        episodes = _estimate_a1_episodes(config, candidate_count)
        expected_episodes = int(episodes.get("total") or episodes.get("worst_case_total") or 0)
        worst_episodes = int(episodes.get("worst_case_total") or expected_episodes)
        extra_calls = candidate_count * 6
    elif idea_id == "budgeted-evolution-controller":
        episodes = _estimate_a2_episodes(config)
        expected_episodes = int(episodes.get("total") or 0)
        worst_episodes = expected_episodes
        extra_calls = int(episodes.get("sequences") or 0) * int(scope.get("max_update_rounds", 4))
    else:
        expected_episodes = int(scope.get("expected_environment_episodes") or 0)
        worst_episodes = int(scope.get("worst_case_environment_episodes") or expected_episodes)
        extra_calls = int(scope.get("expected_extra_model_calls") or 0)
        episodes = {"total": expected_episodes, "worst_case_total": worst_episodes}
    max_steps = int(scope.get("max_steps", 0))
    expected_calls = int(math.ceil(expected_episodes * mean_steps + extra_calls)) if mean_steps > 0 else 0
    worst_calls = int(worst_episodes * max_steps + extra_calls) if max_steps > 0 else 0
    return {
        "episode_estimate": episodes,
        "expected_environment_episodes": expected_episodes,
        "worst_case_environment_episodes": worst_episodes,
        "mean_steps_per_episode": mean_steps,
        "max_steps": max_steps,
        "extra_model_calls_upper_bound": extra_calls,
        "expected_model_calls": expected_calls,
        "worst_case_model_calls": worst_calls,
        "calls_per_gpu_hour": calls_per_gpu_hour,
        "expected_gpu_hours": expected_calls / calls_per_gpu_hour if calls_per_gpu_hour > 0 else None,
        "worst_case_gpu_hours": worst_calls / calls_per_gpu_hour if calls_per_gpu_hour > 0 else None,
    }


def compute_graph(idea_id: str, config: dict[str, Any]) -> dict[str, Any]:
    detail = compute_estimate(idea_id, config)
    cap = config.get("resource_cap") or {}
    blockers: list[str] = []
    episode_cap = int(cap.get("episodes") or 0)
    gpu_cap = float(cap.get("gpu_hours") or 0.0)
    if detail["worst_case_environment_episodes"] <= 0:
        blockers.append("compute-episode-estimate-missing")
    if episode_cap < detail["worst_case_environment_episodes"]:
        blockers.append("episode-cap-below-worst-case-plan")
    worst_gpu = detail.get("worst_case_gpu_hours")
    if worst_gpu is None:
        blockers.append("gpu-hour-estimate-missing-throughput")
    else:
        margin = float(((config.get("pre_experiment") or {}).get("compute") or {}).get("minimum_gpu_hour_margin", 1.05))
        required = float(worst_gpu) * margin
        detail["minimum_gpu_hour_margin"] = margin
        detail["required_gpu_hour_cap"] = required
        if gpu_cap + 1e-12 < required:
            blockers.append("gpu-hour-cap-below-worst-case-plus-margin")
    return gate("compute_graph", not blockers, blockers=blockers, detail={**detail, "resource_cap": cap})


def measured_throughput(config: dict[str, Any]) -> dict[str, Any]:
    throughput = (config.get("pre_experiment") or {}).get("throughput") or config.get("throughput_basis") or {}
    blockers: list[str] = []
    episodes = int(throughput.get("calibration_episodes") or 0)
    calls = int(throughput.get("calibration_model_calls") or 0)
    hours = float(throughput.get("calibration_gpu_hours") or 0.0)
    declared = float(throughput.get("calls_per_gpu_hour") or 0.0)
    recomputed = calls / hours if calls > 0 and hours > 0 else 0.0
    if episodes < 3:
        blockers.append("throughput-calibration-needs-at-least-three-full-episodes")
    if calls <= 0 or hours <= 0:
        blockers.append("throughput-measurement-missing")
    if declared <= 0:
        blockers.append("calls-per-gpu-hour-missing")
    if recomputed > 0 and declared > 0 and abs(declared - recomputed) / recomputed > 0.05:
        blockers.append("declared-throughput-disagrees-with-measurement")
    if not str(throughput.get("measurement_id") or "").strip():
        blockers.append("throughput-measurement-id-missing")
    return gate("measured_throughput", not blockers, blockers=blockers, detail={**throughput, "recomputed_calls_per_gpu_hour": recomputed})


def observability_recovery(config: dict[str, Any]) -> dict[str, Any]:
    recovery = (config.get("pre_experiment") or {}).get("recovery") or {}
    required = ("incremental_trace", "atomic_progress", "heartbeat_state", "online_budget_watchdog", "per_run_lock", "gpu_uuid_binding")
    blockers = [f"recovery-capability-missing:{key}" for key in required if recovery.get(key) is not True]
    if not str(recovery.get("restart_policy") or "").strip():
        blockers.append("restart-or-resume-policy-missing")
    if not str(recovery.get("partial_artifact_policy") or "").strip():
        blockers.append("partial-artifact-policy-missing")
    return gate("observability_recovery", not blockers, blockers=blockers, detail=recovery)


def outcome_semantics(config: dict[str, Any]) -> dict[str, Any]:
    semantics = (config.get("pre_experiment") or {}).get("outcomes") or {}
    allowed = set(semantics.get("allowed") or [])
    phase = str(config.get("phase") or "P0")
    blockers: list[str] = []
    unknown = sorted(allowed - TYPED_OUTCOMES)
    blockers.extend(f"unknown-outcome:{name}" for name in unknown)
    required_common = {"INCONCLUSIVE", "BASELINE-FLOOR", "RUNTIME-ERROR", "IMPLEMENTATION-ERROR", "BUDGET-STOP"}
    if not required_common.issubset(allowed):
        blockers.append("common-non-method-outcomes-incomplete")
    if phase != "P0":
        if "METHOD-FAIL" in allowed:
            blockers.append("screening-must-not-allow-method-fail")
        if not {"SCREENING-SIGNAL", "SCREENING-NO-SIGNAL"}.issubset(allowed):
            blockers.append("screening-signal-outcomes-missing")
    elif not {"METHOD-PASS", "METHOD-FAIL"}.issubset(allowed):
        blockers.append("confirmatory-method-outcomes-missing")
    if semantics.get("budget_stop_registers_scientific_result") is not False:
        blockers.append("budget-stop-registration-policy-invalid")
    if semantics.get("floor_or_ceiling_counts_as_method_fail") is not False:
        blockers.append("floor-ceiling-interpretation-policy-invalid")
    return gate("outcome_semantics", not blockers, blockers=blockers, detail=semantics)
