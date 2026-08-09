from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

from .p0_alfworld_adapter import ALFWorldGameRunner, HFAdmissiblePolicy, load_config as load_alfworld_config
from .p0_alfworld_contract import build_a1_row, build_a2_round, estimate_a1_episodes, estimate_a2_episodes
from .p0_common import balanced_assignments, config_hash, load_json


def _ordered(values: list[str], seed: int, label: str) -> list[str]:
    return sorted(values, key=lambda value: hashlib.sha256(f"{seed}|{label}|{value}".encode()).hexdigest())


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)
    path.write_text(text, encoding="utf-8")


def _trace_record(role: str, trace: dict[str, Any], **meta: Any) -> dict[str, Any]:
    return {"role": role, **meta, "trace": trace}


def _model_call_cost(raw_records: list[dict[str, Any]], patch_generation_calls: int) -> int:
    return patch_generation_calls + sum(int((record.get("trace") or {}).get("model_calls", 0)) for record in raw_records)


def generate_a1_candidates(
    policy: HFAdmissiblePolicy,
    failure_traces: list[dict[str, Any]],
    target_range: list[int],
    seed: int,
) -> tuple[list[dict[str, Any]], int]:
    if not failure_traces:
        raise RuntimeError("A-1 candidate generation requires discovery failure traces")
    candidate_target = int(max(target_range))
    candidates: list[dict[str, Any]] = []
    seen_patches: set[str] = set()
    attempts = 0
    while len(candidates) < candidate_target and attempts < candidate_target * 6:
        source = failure_traces[attempts % len(failure_traces)]
        patch = policy.propose_patch(source, seed=seed + 1000 + attempts, variant=attempts)
        normalized = " ".join(patch.lower().split())
        attempts += 1
        if not normalized or normalized in seen_patches:
            continue
        seen_patches.add(normalized)
        candidate_id = f"u{len(candidates):03d}"
        candidates.append({
            "candidate_id": candidate_id,
            "source_task_id": source["task_id"],
            "patch": patch,
            "edit_size": policy.token_count(patch),
        })
    if len(candidates) < int(min(target_range)):
        raise RuntimeError(f"A-1 generated only {len(candidates)} unique updates; minimum is {min(target_range)}")
    return candidates, attempts


def collect_a1(
    experiment_config_path: Path,
    alfworld_config_path: Path,
    model_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    experiment = load_json(experiment_config_path)
    world = load_alfworld_config(alfworld_config_path)
    seed = int((experiment.get("seeds") or [42])[0])
    scope = experiment.get("scope") or {}
    split_cfg = scope.get("splits") or {
        "discovery": "train",
        "behavior_probes": "eval_in_distribution",
        "hidden": "eval_out_of_distribution",
    }
    target_range = scope.get("candidate_updates_target") or [20, 24]
    candidate_target = int(max(target_range))
    failure_target = int(scope.get("discovery_failures_target", 20))
    discovery_cap = int(scope.get("discovery_episode_cap", max(failure_target, 32)))
    probe_count = int(scope.get("behavior_probes", 8))
    hidden_pool_count = int(scope.get("hidden_original_tasks_target", 24))
    hidden_each = int(scope.get("hidden_tasks_per_candidate", 8))
    max_steps = int(scope.get("max_steps", 50))

    estimate = estimate_a1_episodes(experiment, candidate_target)
    cap = int((experiment.get("resource_cap") or {}).get("episodes", 0))
    if cap and estimate["worst_case_total"] > cap:
        raise ValueError(f"A-1 frozen collection plan can use {estimate['worst_case_total']} episodes, above cap {cap}")

    policy = HFAdmissiblePolicy(model_path)
    runner = ALFWorldGameRunner(world)
    raw_records: list[dict[str, Any]] = []
    started = time.time()

    discovery_files = _ordered(runner.available_game_files(str(split_cfg["discovery"])), seed, "a1-discovery")
    failure_traces: list[dict[str, Any]] = []
    for game_file in discovery_files[:discovery_cap]:
        trace = runner.run_game_file(str(split_cfg["discovery"]), game_file, policy, max_steps=max_steps)
        raw_records.append(_trace_record("discovery-baseline", trace))
        if not trace["success"]:
            failure_traces.append(trace)
        if len(failure_traces) >= failure_target:
            break
    if not failure_traces:
        raise RuntimeError("A-1 found no baseline failures; candidate prompt updates cannot be generated")

    candidates, attempts = generate_a1_candidates(policy, failure_traces, list(target_range), seed)

    probe_files = _ordered(runner.available_game_files(str(split_cfg["behavior_probes"])), seed, "a1-probes")[:probe_count]
    hidden_files = _ordered(runner.available_game_files(str(split_cfg["hidden"])), seed, "a1-hidden")[:hidden_pool_count]
    probe_baseline: dict[str, dict[str, Any]] = {}
    hidden_baseline: dict[str, dict[str, Any]] = {}
    for game_file in probe_files:
        trace = runner.run_game_file(str(split_cfg["behavior_probes"]), game_file, policy, max_steps=max_steps)
        probe_baseline[game_file] = trace
        raw_records.append(_trace_record("behavior-probe-baseline", trace))
    for game_file in hidden_files:
        trace = runner.run_game_file(str(split_cfg["hidden"]), game_file, policy, max_steps=max_steps)
        hidden_baseline[game_file] = trace
        raw_records.append(_trace_record("hidden-baseline", trace))

    failure_by_id = {str(trace["task_id"]): trace for trace in failure_traces}
    assignments = balanced_assignments([c["candidate_id"] for c in candidates], hidden_files, hidden_each, seed)
    rows: list[dict[str, Any]] = []
    for candidate in candidates:
        candidate_id = str(candidate["candidate_id"])
        patch = str(candidate["patch"])
        source_id = str(candidate["source_task_id"])
        current_before = failure_by_id[source_id]
        current_after = runner.run_game_file(str(split_cfg["discovery"]), source_id, policy, patch, max_steps=max_steps)
        raw_records.append(_trace_record("candidate-current", current_after, candidate_id=candidate_id))
        probe_after: list[dict[str, Any]] = []
        for game_file in probe_files:
            trace = runner.run_game_file(str(split_cfg["behavior_probes"]), game_file, policy, patch, max_steps=max_steps)
            probe_after.append(trace)
            raw_records.append(_trace_record("candidate-probe", trace, candidate_id=candidate_id))
        hidden_after: list[dict[str, Any]] = []
        assigned_hidden = assignments[candidate_id]
        for game_file in assigned_hidden:
            trace = runner.run_game_file(str(split_cfg["hidden"]), game_file, policy, patch, max_steps=max_steps)
            hidden_after.append(trace)
            raw_records.append(_trace_record("candidate-hidden", trace, candidate_id=candidate_id))
        row = build_a1_row(
            candidate_id,
            current_before,
            current_after,
            float(candidate["edit_size"]),
            probe_baseline.values(),
            probe_after,
            [hidden_baseline[path] for path in assigned_hidden],
            hidden_after,
        )
        rows.append(row)

    patch_generation_calls = attempts
    elapsed_hours = round((time.time() - started) / 3600.0, 6)
    usage = policy.usage_snapshot()
    independently_counted_calls = _model_call_cost(raw_records, patch_generation_calls)
    if usage["generation_calls"] != independently_counted_calls:
        raise RuntimeError(f"A-1 model-call accounting mismatch: tokenizer={usage['generation_calls']} trace={independently_counted_calls}")
    cost = {
        "gpu_hours": elapsed_hours,
        "model_calls": usage["generation_calls"],
        "tokens": usage["tokens"],
        "input_tokens": usage["input_tokens"],
        "output_tokens": usage["output_tokens"],
        "wall_clock_hours": elapsed_hours,
        "environment_episodes": len(raw_records),
        "patch_generation_calls": patch_generation_calls,
        "accounting_consistent": True,
    }
    manifest = {
        "schema_version": "1.0",
        "idea_id": "update-trust-region",
        "phase": "P0",
        "experiment_config_hash": config_hash(experiment),
        "experiment_config": str(experiment_config_path),
        "alfworld_config": str(alfworld_config_path),
        "model_path": str(model_path),
        "seed": seed,
        "splits": split_cfg,
        "candidate_count": len(candidates),
        "candidate_generation_contract": {
            "allowed_inputs": ["discovery-baseline-failure-traces"],
            "forbidden_inputs": ["behavior-probe-results", "hidden-original-task-results"],
            "generation_completed_before_probe_and_hidden_execution": True,
        },
        "resource_estimate": estimate,
        "actual_environment_episodes": len(raw_records),
        "environment_wrapper_reuse": True,
        "environment_wrapper_builds": runner.wrapper_build_count,
        "hidden_assignment": assignments,
        "analysis_input": "candidate-evaluation.jsonl",
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_jsonl(output_dir / "candidate-patches.jsonl", candidates)
    _write_jsonl(output_dir / "candidate-evaluation.jsonl", rows)
    _write_jsonl(output_dir / "raw-traces.jsonl", raw_records)
    _write_json(output_dir / "cost.json", cost)
    _write_json(output_dir / "manifest.json", manifest)
    return manifest


def collect_a2(
    experiment_config_path: Path,
    alfworld_config_path: Path,
    model_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    experiment = load_json(experiment_config_path)
    world = load_alfworld_config(alfworld_config_path)
    seed = int((experiment.get("seeds") or [42])[0])
    scope = experiment.get("scope") or {}
    splits = scope.get("sequence_splits") or {"discovery": 8, "calibration": 8, "hidden": 12}
    split_names = scope.get("alfworld_splits") or {
        "discovery": "train",
        "calibration": "eval_in_distribution",
        "hidden": "eval_out_of_distribution",
    }
    max_rounds = int(scope.get("max_update_rounds", 4))
    probe_count = int(scope.get("behavior_probes", 2))
    max_steps = int(scope.get("max_steps", 50))
    estimate = estimate_a2_episodes(experiment)
    estimated_episodes = int(estimate["total"])
    cap = int((experiment.get("resource_cap") or {}).get("episodes", 0))
    if cap and estimated_episodes > cap:
        raise ValueError(f"A-2 frozen collection plan uses {estimated_episodes} episodes, above cap {cap}")

    policy = HFAdmissiblePolicy(model_path)
    runner = ALFWorldGameRunner(world)
    raw_records: list[dict[str, Any]] = []
    started = time.time()
    probe_source = _ordered(runner.available_game_files("eval_in_distribution"), seed, "a2-probes")
    probe_files = probe_source[:probe_count]
    probe_baseline: dict[str, dict[str, Any]] = {}
    for game_file in probe_files:
        trace = runner.run_game_file("eval_in_distribution", game_file, policy, max_steps=max_steps)
        probe_baseline[game_file] = trace
        raw_records.append(_trace_record("a2-probe-baseline", trace))

    sequences: list[dict[str, Any]] = []
    patch_generation_calls = 0
    split_items = (("discovery", splits["discovery"]), ("calibration", splits["calibration"]), ("hidden", splits["hidden"]))
    for split_index, (split_label, count_value) in enumerate(split_items):
        count = int(count_value)
        env_split = str(split_names[split_label])
        pool = _ordered(runner.available_game_files(env_split), seed, f"a2-{split_label}")
        if env_split == "eval_in_distribution":
            pool = [path for path in pool if path not in set(probe_files)]
        selected = pool[:count]
        if len(selected) < count:
            raise RuntimeError(f"not enough ALFWorld tasks for A-2 {split_label}: {len(selected)} < {count}")
        for task_offset, game_file in enumerate(selected):
            baseline = runner.run_game_file(env_split, game_file, policy, max_steps=max_steps)
            raw_records.append(_trace_record("a2-task-baseline", baseline, split=split_label))
            previous = baseline
            persistent_patch = ""
            rounds: list[dict[str, Any]] = []
            logical_calls = 0
            for round_index in range(1, max_rounds + 1):
                patch_piece = policy.propose_patch(
                    previous,
                    seed=seed + 100000 * (split_index + 1) + 1000 * task_offset + round_index,
                    previous_patch=persistent_patch,
                    variant=round_index,
                )
                patch_generation_calls += 1
                if patch_piece and patch_piece.lower() not in persistent_patch.lower():
                    persistent_patch = (persistent_patch + "\n" + patch_piece).strip()
                current = runner.run_game_file(env_split, game_file, policy, persistent_patch, max_steps=max_steps)
                raw_records.append(_trace_record("a2-task-round", current, split=split_label, round=round_index))
                probe_current: list[dict[str, Any]] = []
                for probe_file in probe_files:
                    trace = runner.run_game_file("eval_in_distribution", probe_file, policy, persistent_patch, max_steps=max_steps)
                    probe_current.append(trace)
                    raw_records.append(_trace_record("a2-probe-round", trace, split=split_label, round=round_index, task_id=game_file))
                logical_calls += 1 + int(current.get("model_calls", 0)) + sum(int(trace.get("model_calls", 0)) for trace in probe_current)
                row = build_a2_round(
                    round_index,
                    previous,
                    current,
                    probe_baseline.values(),
                    probe_current,
                    logical_calls,
                )
                row["patch"] = persistent_patch
                rounds.append(row)
                previous = current
            sequences.append({"task_id": game_file, "split": split_label, "rounds": rounds})

    elapsed_hours = round((time.time() - started) / 3600.0, 6)
    usage = policy.usage_snapshot()
    independently_counted_calls = _model_call_cost(raw_records, patch_generation_calls)
    if usage["generation_calls"] != independently_counted_calls:
        raise RuntimeError(f"A-2 model-call accounting mismatch: tokenizer={usage['generation_calls']} trace={independently_counted_calls}")
    cost = {
        "gpu_hours": elapsed_hours,
        "model_calls": usage["generation_calls"],
        "tokens": usage["tokens"],
        "input_tokens": usage["input_tokens"],
        "output_tokens": usage["output_tokens"],
        "wall_clock_hours": elapsed_hours,
        "environment_episodes": len(raw_records),
        "patch_generation_calls": patch_generation_calls,
        "accounting_consistent": True,
    }
    manifest = {
        "schema_version": "1.0",
        "idea_id": "budgeted-evolution-controller",
        "phase": "P0",
        "experiment_config_hash": config_hash(experiment),
        "experiment_config": str(experiment_config_path),
        "alfworld_config": str(alfworld_config_path),
        "model_path": str(model_path),
        "seed": seed,
        "sequence_splits": splits,
        "alfworld_splits": split_names,
        "resource_estimate": estimate,
        "estimated_environment_episodes": estimated_episodes,
        "actual_environment_episodes": len(raw_records),
        "environment_wrapper_reuse": True,
        "environment_wrapper_builds": runner.wrapper_build_count,
        "sequence_generation_contract": {
            "mode": "full-policy-conditioned-rollout-then-freeze",
            "controller_access_during_generation": False,
            "controller_fit_splits": ["discovery", "calibration"],
            "controller_test_split": "hidden",
            "all_controllers_reuse_identical_saved_sequences": True,
        },
        "analysis_input": "fixed-sequences.jsonl",
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_jsonl(output_dir / "fixed-sequences.jsonl", sequences)
    _write_jsonl(output_dir / "raw-traces.jsonl", raw_records)
    _write_json(output_dir / "cost.json", cost)
    _write_json(output_dir / "manifest.json", manifest)
    return manifest
