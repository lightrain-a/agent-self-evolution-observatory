from __future__ import annotations

import hashlib
import json
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

from .alfworld_react_scaffold import task_family_from_gamefile
from .p0_alfworld_adapter import ALFWorldGameRunner, HFAdmissiblePolicy, load_config as load_alfworld_config
from .p0_alfworld_contract import build_a1_row, build_a2_round, estimate_a1_episodes, estimate_a2_episodes
from .p0_common import balanced_assignments, config_hash, load_json


def _task_key(value: str) -> str:
    normalized = str(value).replace("\\", "/")
    marker = "/json_2.1.1/"
    return normalized.split(marker, 1)[1] if marker in normalized else normalized


def _ordered(values: list[str], seed: int, label: str) -> list[str]:
    return sorted(values, key=lambda value: hashlib.sha256(f"{seed}|{label}|{value}".encode()).hexdigest())


def _task_family_order(values: list[str], seed: int, label: str) -> list[str]:
    """Round-robin task families while keeping deterministic within-family order."""
    groups: dict[str, list[str]] = defaultdict(list)
    for value in values:
        groups[task_family_from_gamefile(value)].append(value)
    for family, rows in groups.items():
        groups[family] = _ordered(rows, seed, f"{label}|{family}")
    families = sorted(groups, key=lambda family: hashlib.sha256(f"{seed}|{label}|family|{family}".encode()).hexdigest())
    output: list[str] = []
    while families:
        remaining: list[str] = []
        for family in families:
            rows = groups[family]
            if rows:
                output.append(rows.pop(0))
            if rows:
                remaining.append(family)
        families = remaining
    return output


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)
    path.write_text(text, encoding="utf-8")


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        handle.flush()


def _reset_stream_files(output_dir: Path, names: tuple[str, ...]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for name in names:
        path = output_dir / name
        if path.exists() and path.stat().st_size:
            raise RuntimeError(f"refusing to overwrite non-empty incremental P0 artifact: {path}")
        path.write_text("", encoding="utf-8")


def _check_live_budget(experiment: dict[str, Any], started: float, environment_episodes: int) -> None:
    cap = experiment.get("resource_cap") or {}
    elapsed_hours = (time.time() - started) / 3600.0
    if cap.get("gpu_hours") is not None and elapsed_hours >= float(cap["gpu_hours"]):
        raise RuntimeError(f"live GPU-hour cap reached: {elapsed_hours:.4f} >= {float(cap['gpu_hours']):.4f}")
    if cap.get("wall_hours") is not None and elapsed_hours >= float(cap["wall_hours"]):
        raise RuntimeError(f"live wall-hour cap reached: {elapsed_hours:.4f} >= {float(cap['wall_hours']):.4f}")
    if cap.get("episodes") is not None and environment_episodes >= int(cap["episodes"]):
        raise RuntimeError(f"live environment-episode cap reached: {environment_episodes} >= {int(cap['episodes'])}")


def _emit_progress(
    output_dir: Path,
    progress_callback: Callable[[dict[str, Any]], None] | None,
    policy: HFAdmissiblePolicy,
    started: float,
    environment_episodes: int,
    *,
    stage: str,
    **extra: Any,
) -> None:
    usage = policy.usage_snapshot()
    payload = {
        "stage": stage,
        "environment_episodes": int(environment_episodes),
        "model_calls": int(usage["generation_calls"]),
        "tokens": int(usage["tokens"]),
        "elapsed_hours": round((time.time() - started) / 3600.0, 6),
        **extra,
    }
    _write_json(output_dir / "progress.json", payload)
    if progress_callback is not None:
        progress_callback(payload)


def _trace_record(role: str, trace: dict[str, Any], **meta: Any) -> dict[str, Any]:
    return {"role": role, **meta, "trace": trace}


def _record_incremental(
    output_dir: Path,
    raw_records: list[dict[str, Any]],
    experiment: dict[str, Any],
    policy: HFAdmissiblePolicy,
    started: float,
    progress_callback: Callable[[dict[str, Any]], None] | None,
    stage: str,
    role: str,
    trace: dict[str, Any],
    **meta: Any,
) -> None:
    row = _trace_record(role, trace, **meta)
    raw_records.append(row)
    _append_jsonl(output_dir / "raw-traces.jsonl", row)
    _emit_progress(
        output_dir,
        progress_callback,
        policy,
        started,
        len(raw_records),
        stage=stage,
        **meta,
    )
    _check_live_budget(experiment, started, len(raw_records))


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
    *,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    experiment = load_json(experiment_config_path)
    world = load_alfworld_config(alfworld_config_path)
    world.setdefault("general", {})["save_path"] = str(output_dir / "alfworld-runtime")
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

    _reset_stream_files(output_dir, ("raw-traces.jsonl", "candidate-patches.jsonl", "candidate-evaluation.jsonl"))
    policy_mode = str(scope.get("policy_mode") or "direct")
    policy = HFAdmissiblePolicy(model_path, policy_mode=policy_mode)
    runner = ALFWorldGameRunner(world)
    raw_records: list[dict[str, Any]] = []
    started = time.time()
    _emit_progress(output_dir, progress_callback, policy, started, 0, stage="discovery")

    stratify = bool(scope.get("stratify_by_task_type") or scope.get("stratify_probes_and_hidden_by_task_type"))
    discovery_pool = runner.available_game_files(str(split_cfg["discovery"]))
    discovery_files = (_task_family_order if stratify else _ordered)(discovery_pool, seed, "a1-discovery")
    failure_traces: list[dict[str, Any]] = []
    for game_file in discovery_files[:discovery_cap]:
        trace = runner.run_game_file(str(split_cfg["discovery"]), game_file, policy, max_steps=max_steps)
        _record_incremental(output_dir, raw_records, experiment, policy, started, progress_callback, "discovery", "discovery-baseline", trace)
        if not trace["success"]:
            failure_traces.append(trace)
        if len(failure_traces) >= failure_target:
            break
    if not failure_traces:
        raise RuntimeError("A-1 found no baseline failures; candidate prompt updates cannot be generated")

    candidates, attempts = generate_a1_candidates(policy, failure_traces, list(target_range), seed)
    for candidate in candidates:
        _append_jsonl(output_dir / "candidate-patches.jsonl", candidate)
    _emit_progress(output_dir, progress_callback, policy, started, len(raw_records), stage="candidate-generation-complete", candidates_completed=len(candidates), candidates_total=candidate_target)
    _check_live_budget(experiment, started, len(raw_records))

    probe_pool = runner.available_game_files(str(split_cfg["behavior_probes"]))
    hidden_pool = runner.available_game_files(str(split_cfg["hidden"]))
    probe_files = (_task_family_order if stratify else _ordered)(probe_pool, seed, "a1-probes")[:probe_count]
    hidden_files = (_task_family_order if stratify else _ordered)(hidden_pool, seed, "a1-hidden")[:hidden_pool_count]
    probe_baseline: dict[str, dict[str, Any]] = {}
    hidden_baseline: dict[str, dict[str, Any]] = {}
    for game_file in probe_files:
        trace = runner.run_game_file(str(split_cfg["behavior_probes"]), game_file, policy, max_steps=max_steps)
        probe_baseline[game_file] = trace
        _record_incremental(output_dir, raw_records, experiment, policy, started, progress_callback, "probe-baseline", "behavior-probe-baseline", trace)
    for game_file in hidden_files:
        trace = runner.run_game_file(str(split_cfg["hidden"]), game_file, policy, max_steps=max_steps)
        hidden_baseline[game_file] = trace
        _record_incremental(output_dir, raw_records, experiment, policy, started, progress_callback, "hidden-baseline", "hidden-baseline", trace)

    failure_by_id = {str(trace["task_id"]): trace for trace in failure_traces}
    assignments = balanced_assignments([c["candidate_id"] for c in candidates], hidden_files, hidden_each, seed)
    rows: list[dict[str, Any]] = []
    for candidate_index, candidate in enumerate(candidates, 1):
        candidate_id = str(candidate["candidate_id"])
        patch = str(candidate["patch"])
        source_id = str(candidate["source_task_id"])
        current_before = failure_by_id[source_id]
        current_after = runner.run_game_file(str(split_cfg["discovery"]), source_id, policy, patch, max_steps=max_steps)
        _record_incremental(output_dir, raw_records, experiment, policy, started, progress_callback, "candidate-evaluation", "candidate-current", current_after, candidate_id=candidate_id, candidate_index=candidate_index, candidates_total=len(candidates))
        probe_after: list[dict[str, Any]] = []
        for game_file in probe_files:
            trace = runner.run_game_file(str(split_cfg["behavior_probes"]), game_file, policy, patch, max_steps=max_steps)
            probe_after.append(trace)
            _record_incremental(output_dir, raw_records, experiment, policy, started, progress_callback, "candidate-evaluation", "candidate-probe", trace, candidate_id=candidate_id, candidate_index=candidate_index, candidates_total=len(candidates))
        hidden_after: list[dict[str, Any]] = []
        assigned_hidden = assignments[candidate_id]
        for game_file in assigned_hidden:
            trace = runner.run_game_file(str(split_cfg["hidden"]), game_file, policy, patch, max_steps=max_steps)
            hidden_after.append(trace)
            _record_incremental(output_dir, raw_records, experiment, policy, started, progress_callback, "candidate-evaluation", "candidate-hidden", trace, candidate_id=candidate_id, candidate_index=candidate_index, candidates_total=len(candidates))
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
        _append_jsonl(output_dir / "candidate-evaluation.jsonl", row)
        _emit_progress(output_dir, progress_callback, policy, started, len(raw_records), stage="candidate-complete", candidate_id=candidate_id, candidates_completed=candidate_index, candidates_total=len(candidates))

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
        "phase": str(experiment.get("phase") or "P0"),
        "experiment_config_hash": config_hash(experiment),
        "experiment_config": str(experiment_config_path),
        "alfworld_config": str(alfworld_config_path),
        "model_path": str(model_path),
        "seed": seed,
        "policy_mode": policy_mode,
        "stratified_by_task_type": stratify,
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
    _write_json(output_dir / "cost.json", cost)
    _write_json(output_dir / "manifest.json", manifest)
    return manifest


def collect_a2(
    experiment_config_path: Path,
    alfworld_config_path: Path,
    model_path: Path,
    output_dir: Path,
    *,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    experiment = load_json(experiment_config_path)
    world = load_alfworld_config(alfworld_config_path)
    world.setdefault("general", {})["save_path"] = str(output_dir / "alfworld-runtime")
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

    _reset_stream_files(output_dir, ("raw-traces.jsonl", "fixed-sequences.jsonl"))
    policy_mode = str(scope.get("policy_mode") or "direct")
    policy = HFAdmissiblePolicy(model_path, policy_mode=policy_mode)
    runner = ALFWorldGameRunner(world)
    raw_records: list[dict[str, Any]] = []
    started = time.time()
    _emit_progress(output_dir, progress_callback, policy, started, 0, stage="probe-baseline")
    stratify = bool(scope.get("stratify_by_task_type"))
    excluded_task_keys = {str(value) for value in (scope.get("excluded_qualification_task_keys") or []) if str(value)}
    probe_pool = [path for path in runner.available_game_files("eval_in_distribution") if _task_key(path) not in excluded_task_keys]
    probe_source = (_task_family_order if stratify else _ordered)(probe_pool, seed, "a2-probes")
    probe_files = probe_source[:probe_count]
    probe_baseline: dict[str, dict[str, Any]] = {}
    for game_file in probe_files:
        trace = runner.run_game_file("eval_in_distribution", game_file, policy, max_steps=max_steps)
        probe_baseline[game_file] = trace
        _record_incremental(output_dir, raw_records, experiment, policy, started, progress_callback, "probe-baseline", "a2-probe-baseline", trace)

    sequences: list[dict[str, Any]] = []
    patch_generation_calls = 0
    split_items = (("discovery", splits["discovery"]), ("calibration", splits["calibration"]), ("hidden", splits["hidden"]))
    for split_index, (split_label, count_value) in enumerate(split_items):
        count = int(count_value)
        env_split = str(split_names[split_label])
        raw_pool = [path for path in runner.available_game_files(env_split) if _task_key(path) not in excluded_task_keys]
        pool = (_task_family_order if stratify else _ordered)(raw_pool, seed, f"a2-{split_label}")
        if env_split == "eval_in_distribution":
            pool = [path for path in pool if path not in set(probe_files)]
        selected = pool[:count]
        if len(selected) < count:
            raise RuntimeError(f"not enough ALFWorld tasks for A-2 {split_label}: {len(selected)} < {count}")
        for task_offset, game_file in enumerate(selected):
            baseline = runner.run_game_file(env_split, game_file, policy, max_steps=max_steps)
            _record_incremental(output_dir, raw_records, experiment, policy, started, progress_callback, "sequence-baseline", "a2-task-baseline", baseline, split=split_label, task_index=task_offset + 1, tasks_total=count)
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
                _check_live_budget(experiment, started, len(raw_records))
                current = runner.run_game_file(env_split, game_file, policy, persistent_patch, max_steps=max_steps)
                _record_incremental(output_dir, raw_records, experiment, policy, started, progress_callback, "sequence-round", "a2-task-round", current, split=split_label, round=round_index, task_index=task_offset + 1, tasks_total=count)
                probe_current: list[dict[str, Any]] = []
                for probe_file in probe_files:
                    trace = runner.run_game_file("eval_in_distribution", probe_file, policy, persistent_patch, max_steps=max_steps)
                    probe_current.append(trace)
                    _record_incremental(output_dir, raw_records, experiment, policy, started, progress_callback, "sequence-probe", "a2-probe-round", trace, split=split_label, round=round_index, task_id=game_file, task_index=task_offset + 1, tasks_total=count)
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
            sequence = {"task_id": game_file, "split": split_label, "rounds": rounds}
            sequences.append(sequence)
            _append_jsonl(output_dir / "fixed-sequences.jsonl", sequence)
            _emit_progress(output_dir, progress_callback, policy, started, len(raw_records), stage="sequence-complete", split=split_label, task_index=task_offset + 1, tasks_total=count)

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
        "phase": str(experiment.get("phase") or "P0"),
        "experiment_config_hash": config_hash(experiment),
        "experiment_config": str(experiment_config_path),
        "alfworld_config": str(alfworld_config_path),
        "model_path": str(model_path),
        "seed": seed,
        "policy_mode": policy_mode,
        "stratified_by_task_type": stratify,
        "sequence_splits": splits,
        "excluded_qualification_task_keys": sorted(excluded_task_keys),
        "excluded_qualification_task_count": len(excluded_task_keys),
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
    _write_json(output_dir / "cost.json", cost)
    _write_json(output_dir / "manifest.json", manifest)
    return manifest
