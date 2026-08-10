from __future__ import annotations

import argparse
import json
import math
import random
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .p0_alfworld_adapter import ALFWorldGameRunner, HFAdmissiblePolicy, load_config as load_alfworld_config
from .p0_alfworld_collect import _task_family_order
from .p0_alfworld_contract import build_a2_round


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
        handle.flush()


def _atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _entropy(labels: list[int]) -> float:
    counts = Counter(labels)
    total = len(labels)
    return -sum((count / total) * math.log2(count / total) for count in counts.values()) if total else 0.0


def _check_budget(started: float, episodes: int, *, gpu_hours_cap: float, wall_hours_cap: float, episode_cap: int) -> None:
    elapsed = (time.time() - started) / 3600.0
    if gpu_hours_cap > 0 and elapsed >= gpu_hours_cap:
        raise RuntimeError(f"A2-R1 qualification GPU-hour cap reached: {elapsed:.4f} >= {gpu_hours_cap:.4f}")
    if wall_hours_cap > 0 and elapsed >= wall_hours_cap:
        raise RuntimeError(f"A2-R1 qualification wall-hour cap reached: {elapsed:.4f} >= {wall_hours_cap:.4f}")
    if episode_cap > 0 and episodes >= episode_cap:
        raise RuntimeError(f"A2-R1 qualification episode cap reached: {episodes} >= {episode_cap}")


def _auc(labels: list[int], scores: list[float]) -> float:
    pos = [score for label, score in zip(labels, scores) if label == 1]
    neg = [score for label, score in zip(labels, scores) if label == 0]
    if not pos or not neg:
        return 0.5
    wins = 0.0
    for p in pos:
        for n in neg:
            wins += 1.0 if p > n else 0.5 if p == n else 0.0
    return wins / (len(pos) * len(neg))


def _fit_mean_difference(features: list[list[float]], labels: list[int]) -> dict[str, Any]:
    if len(set(labels)) < 2:
        raise ValueError("sequence qualification controller needs both continue and stop labels")
    dims = len(features[0])
    mu = [_mean([row[j] for row in features]) for j in range(dims)]
    sd = []
    for j in range(dims):
        variance = _mean([(row[j] - mu[j]) ** 2 for row in features])
        value = math.sqrt(variance)
        sd.append(value if value >= 1e-9 else 1.0)
    z = [[(row[j] - mu[j]) / sd[j] for j in range(dims)] for row in features]
    positive = [row for row, label in zip(z, labels) if label == 1]
    negative = [row for row, label in zip(z, labels) if label == 0]
    weights = [
        _mean([row[j] for row in positive]) - _mean([row[j] for row in negative])
        for j in range(dims)
    ]
    return {"mu": mu, "sd": sd, "weights": weights}


def _score(model: dict[str, Any], feature: list[float]) -> float:
    return sum(
        ((feature[j] - model["mu"][j]) / model["sd"][j]) * model["weights"][j]
        for j in range(len(feature))
    )


def _feature(row: dict[str, Any], call_scale: float) -> list[float]:
    return [
        float(row.get("marginal_gain") or 0.0),
        float(row.get("probe_regression") or 0.0),
        float(row.get("disagreement") or 0.0),
        float(row.get("cumulative_calls") or 0.0) / max(call_scale, 1.0),
    ]


def _oracle_round(sequence: dict[str, Any]) -> int:
    """Preserve success first, regression second, calls third."""
    ranked = []
    for index, row in enumerate(sequence["rounds"]):
        ranked.append((
            float(row.get("success") or 0.0),
            -float(row.get("regression") or 0.0),
            -float(row.get("cumulative_calls") or 0.0),
            -(index + 1),
            index + 1,
        ))
    return max(ranked)[-1]


def _tuned_heuristic_round(train: list[dict[str, Any]], test: dict[str, Any]) -> int:
    grid = []
    for min_gain in (0.0, 0.02, 0.05):
        for max_regression in (0.1, 0.25, 0.4):
            for max_disagreement in (0.2, 0.4, 0.6):
                for max_rounds in (1, 2, 3, 4):
                    grid.append((min_gain, max_regression, max_disagreement, max_rounds))

    def choose(sequence: dict[str, Any], params: tuple[float, float, float, int]) -> tuple[int, int]:
        min_gain, max_regression, max_disagreement, max_rounds = params
        selected = 0
        for index, row in enumerate(sequence["rounds"]):
            if index > 0 and (
                float(row["marginal_gain"]) < min_gain
                or float(row["probe_regression"]) > max_regression
                or float(row["disagreement"]) > max_disagreement
                or int(row["round"]) > max_rounds
            ):
                return max(0, index - 1), index
            selected = index
        return selected, selected

    def objective(sequences: list[dict[str, Any]], params: tuple[float, float, float, int]) -> tuple[float, float, float]:
        decisions = [choose(sequence, params) for sequence in sequences]
        selected = [sequence["rounds"][decision[0]] for sequence, decision in zip(sequences, decisions)]
        observed = [sequence["rounds"][decision[1]] for sequence, decision in zip(sequences, decisions)]
        return (
            _mean([float(row["success"]) for row in selected]),
            -_mean([float(row.get("regression") or 0.0) for row in selected]),
            -_mean([float(row["cumulative_calls"]) for row in observed]),
        )

    best = max(grid, key=lambda params: objective(train, params))
    return choose(test, best)[0] + 1


def analyze(sequences: list[dict[str, Any]]) -> dict[str, Any]:
    if len(sequences) < 6:
        return {"pass": False, "decision": "QUALIFICATION-FAIL", "reason": "need-at-least-six-complete-sequences", "sequence_count": len(sequences), "scientific_result_available": False, "pilot_registry_write_forbidden": True}
    oracle = [_oracle_round(sequence) for sequence in sequences]
    oracle_successes = [float(sequence["rounds"][best_round - 1].get("success") or 0.0) for sequence, best_round in zip(sequences, oracle)]
    success_bearing = sum(value > 0.0 for value in oracle_successes)
    minimum_success_bearing = max(3, math.ceil(0.25 * len(sequences)))
    oracle_success_rate = _mean(oracle_successes)
    entropy = _entropy(oracle)
    jackknife_entropy = [_entropy(oracle[:index] + oracle[index + 1:]) for index in range(len(oracle))]
    jackknife_types = [len(set(oracle[:index] + oracle[index + 1:])) for index in range(len(oracle))]
    non_early = sum(round_id > 1 for round_id in oracle)
    rollback_or_harm = sum(
        any(
            float(later.get("success") or 0.0) < float(earlier.get("success") or 0.0)
            or float(later.get("regression") or 0.0) > float(earlier.get("regression") or 0.0)
            for earlier, later in zip(sequence["rounds"], sequence["rounds"][1:])
        )
        for sequence in sequences
    )
    call_scale = _mean([float(sequence["rounds"][0]["cumulative_calls"]) for sequence in sequences])

    labels: list[int] = []
    scores: list[float] = []
    learned_rounds: list[int] = []
    heuristic_rounds: list[int] = []
    for holdout, sequence in enumerate(sequences):
        train = [row for index, row in enumerate(sequences) if index != holdout]
        train_x: list[list[float]] = []
        train_y: list[int] = []
        for train_sequence in train:
            best_round = _oracle_round(train_sequence)
            for row in train_sequence["rounds"][:-1]:
                train_x.append(_feature(row, call_scale))
                train_y.append(1 if best_round > int(row["round"]) else 0)
        if len(set(train_y)) < 2:
            return {
                "pass": False,
                "decision": "QUALIFICATION-FAIL",
                "reason": "leave-one-sequence-out-train-label-collapse",
                "sequence_count": len(sequences),
                "optimal_round_counts": dict(sorted(Counter(oracle).items())),
                "optimal_round_entropy_bits": entropy,
                "scientific_result_available": False,
                "pilot_registry_write_forbidden": True,
            }
        model = _fit_mean_difference(train_x, train_y)
        best_round = oracle[holdout]
        selected = 4
        for row in sequence["rounds"][:-1]:
            value = _score(model, _feature(row, call_scale))
            labels.append(1 if best_round > int(row["round"]) else 0)
            scores.append(value)
            if selected == 4 and value < 0.0:
                selected = int(row["round"])
        learned_rounds.append(selected)
        heuristic_rounds.append(_tuned_heuristic_round(train, sequence))

    continue_stop_auc = _auc(labels, scores)
    disagreements = sum(a != b for a, b in zip(learned_rounds, heuristic_rounds))

    tiny_sequences = sequences[: min(5, len(sequences))]
    tiny_x: list[list[float]] = []
    tiny_y: list[int] = []
    for sequence in tiny_sequences:
        best_round = _oracle_round(sequence)
        for row in sequence["rounds"][:-1]:
            tiny_x.append(_feature(row, call_scale))
            tiny_y.append(1 if best_round > int(row["round"]) else 0)
    if len(set(tiny_y)) >= 2:
        tiny_model = _fit_mean_difference(tiny_x, tiny_y)
        tiny_scores = [_score(tiny_model, feature) for feature in tiny_x]
        tiny_auc = _auc(tiny_y, tiny_scores)
    else:
        tiny_auc = 0.5
    tiny_pass = tiny_auc >= 0.95

    archetype_pass = (
        success_bearing >= minimum_success_bearing
        and oracle_success_rate >= 0.25
        and entropy >= 0.8
        and len(set(oracle)) >= 3
        and min(jackknife_entropy, default=0.0) >= 0.6
        and min(jackknife_types, default=0) >= 2
        and non_early >= 2
        and rollback_or_harm >= 1
    )
    controller_pass = continue_stop_auc >= 0.65 and disagreements >= 1
    return {
        "pass": archetype_pass and controller_pass,
        "sequence_count": len(sequences),
        "optimal_round_counts": dict(sorted(Counter(oracle).items())),
        "optimal_round_entropy_bits": entropy,
        "minimum_entropy_bits": 0.8,
        "oracle_success_bearing_sequences": success_bearing,
        "minimum_oracle_success_bearing_sequences": minimum_success_bearing,
        "oracle_success_rate": oracle_success_rate,
        "minimum_oracle_success_rate": 0.25,
        "jackknife_min_entropy_bits": min(jackknife_entropy, default=0.0),
        "jackknife_min_distinct_rounds": min(jackknife_types, default=0),
        "non_early_optimal_sequences": non_early,
        "rollback_or_harm_sequences": rollback_or_harm,
        "archetype_pass": archetype_pass,
        "leave_one_sequence_out_continue_stop_auc": continue_stop_auc,
        "learned_selected_rounds": learned_rounds,
        "tuned_simple_selected_rounds": heuristic_rounds,
        "controller_baseline_disagreement_sequences": disagreements,
        "controller_disagreement_pass": controller_pass,
        "tiny_real_subset": {
            "sequence_count": len(tiny_sequences),
            "binary_examples": len(tiny_y),
            "continue_labels": sum(tiny_y),
            "training_auc": tiny_auc,
            "pass": tiny_pass,
        },
        "pass": archetype_pass and controller_pass and tiny_pass,
        "decision": "QUALIFICATION-PASS" if archetype_pass and controller_pass and tiny_pass else "QUALIFICATION-FAIL",
        "scientific_result_available": False,
        "pilot_registry_write_forbidden": True,
        "scientific_role": "qualification only; failure cannot be interpreted as an A-2 method failure",
    }


def collect(
    model_path: Path,
    alfworld_config: Path,
    output_dir: Path,
    *,
    num_sequences: int,
    max_rounds: int,
    probe_count: int,
    max_steps: int,
    seed: int,
    gpu_hours_cap: float,
    wall_hours_cap: float,
    episode_cap: int,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    for name in ("raw-traces.jsonl", "fixed-sequences.jsonl"):
        path = output_dir / name
        if path.exists() and path.stat().st_size:
            raise RuntimeError(f"refusing to overwrite non-empty qualification artifact: {path}")
        path.write_text("", encoding="utf-8")

    world = load_alfworld_config(alfworld_config)
    world.setdefault("general", {})["save_path"] = str(output_dir / "alfworld-runtime")
    policy = HFAdmissiblePolicy(model_path, policy_mode="react-family")
    runner = ALFWorldGameRunner(world)
    started = time.time()
    episodes = 0

    def record(role: str, trace: dict[str, Any], **meta: Any) -> None:
        nonlocal episodes
        episodes += 1
        _append_jsonl(output_dir / "raw-traces.jsonl", {"role": role, **meta, "trace": trace})
        usage = policy.usage_snapshot()
        _atomic(output_dir / "progress.json", {
            "stage": role,
            "environment_episodes": episodes,
            "model_calls": int(usage["generation_calls"]),
            "tokens": int(usage["tokens"]),
            "elapsed_hours": round((time.time() - started) / 3600.0, 6),
            "gpu_hours_cap": gpu_hours_cap,
            "wall_hours_cap": wall_hours_cap,
            "episode_cap": episode_cap,
            **meta,
        })
        _check_budget(started, episodes, gpu_hours_cap=gpu_hours_cap, wall_hours_cap=wall_hours_cap, episode_cap=episode_cap)

    probe_pool = _task_family_order(runner.available_game_files("eval_in_distribution"), seed, "a2-r1-probes")
    probe_files = probe_pool[:probe_count]
    probe_baseline: dict[str, dict[str, Any]] = {}
    for probe_file in probe_files:
        trace = runner.run_game_file("eval_in_distribution", probe_file, policy, max_steps=max_steps)
        probe_baseline[probe_file] = trace
        record("a2-r1-probe-baseline", trace)

    base = num_sequences // 3
    remainder = num_sequences % 3
    split_plan = [
        ("train", base + (1 if remainder > 0 else 0)),
        ("eval_in_distribution", base + (1 if remainder > 1 else 0)),
        ("eval_out_of_distribution", base),
    ]
    sequences: list[dict[str, Any]] = []
    patch_generation_calls = 0
    global_index = 0
    for split_index, (env_split, count) in enumerate(split_plan):
        pool = _task_family_order(runner.available_game_files(env_split), seed, f"a2-r1-{env_split}")
        if env_split == "eval_in_distribution":
            pool = [path for path in pool if path not in set(probe_files)]
        for game_file in pool[:count]:
            baseline = runner.run_game_file(env_split, game_file, policy, max_steps=max_steps)
            record("a2-r1-task-baseline", baseline, sequence_index=global_index, env_split=env_split)
            previous = baseline
            persistent_patch = ""
            rounds: list[dict[str, Any]] = []
            logical_calls = 0
            for round_index in range(1, max_rounds + 1):
                patch_piece = policy.propose_patch(
                    previous,
                    seed=seed + 100000 * (split_index + 1) + 1000 * global_index + round_index,
                    previous_patch=persistent_patch,
                    variant=round_index,
                )
                patch_generation_calls += 1
                _check_budget(started, episodes, gpu_hours_cap=gpu_hours_cap, wall_hours_cap=wall_hours_cap, episode_cap=episode_cap)
                if patch_piece and patch_piece.lower() not in persistent_patch.lower():
                    persistent_patch = (persistent_patch + "\n" + patch_piece).strip()
                current = runner.run_game_file(env_split, game_file, policy, persistent_patch, max_steps=max_steps)
                record("a2-r1-task-round", current, sequence_index=global_index, env_split=env_split, round=round_index)
                probe_current: list[dict[str, Any]] = []
                for probe_file in probe_files:
                    trace = runner.run_game_file("eval_in_distribution", probe_file, policy, persistent_patch, max_steps=max_steps)
                    probe_current.append(trace)
                    record("a2-r1-probe-round", trace, sequence_index=global_index, env_split=env_split, round=round_index, task_id=game_file)
                logical_calls += 1 + int(current.get("model_calls", 0)) + sum(int(trace.get("model_calls", 0)) for trace in probe_current)
                row = build_a2_round(round_index, previous, current, probe_baseline.values(), probe_current, logical_calls)
                row["patch"] = persistent_patch
                rounds.append(row)
                previous = current
            sequence = {"task_id": game_file, "split": "qualification", "env_split": env_split, "sequence_index": global_index, "rounds": rounds}
            sequences.append(sequence)
            _append_jsonl(output_dir / "fixed-sequences.jsonl", sequence)
            partial = analyze(sequences)
            _atomic(output_dir / "qualification-partial.json", partial)
            global_index += 1

    usage = policy.usage_snapshot()
    result = analyze(sequences)
    result.update({
        "schema_version": "1.0",
        "generated_at": _now(),
        "artifact_kind": "A2-R1-ALFWorld-sequence-qualification",
        "model_path": str(model_path),
        "policy_mode": "react-family",
        "num_sequences": num_sequences,
        "max_rounds": max_rounds,
        "probe_count": probe_count,
        "max_steps": max_steps,
        "seed": seed,
        "environment_episodes": episodes,
        "patch_generation_calls": patch_generation_calls,
        "model_calls": int(usage["generation_calls"]),
        "tokens": int(usage["tokens"]),
        "gpu_hours": round((time.time() - started) / 3600.0, 6),
        "resource_cap": {"gpu_hours": gpu_hours_cap, "wall_hours": wall_hours_cap, "episodes": episode_cap},
        "split_plan": {name: count for name, count in split_plan},
    })
    _atomic(output_dir / "qualification.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Small A2-R1 ALFWorld sequence-archetype qualification before screening.")
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--alfworld-config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--num-sequences", type=int, default=9)
    parser.add_argument("--max-rounds", type=int, default=4)
    parser.add_argument("--probe-count", type=int, default=2)
    parser.add_argument("--max-steps", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--gpu-hours-cap", type=float, default=1.8)
    parser.add_argument("--wall-hours-cap", type=float, default=2.5)
    parser.add_argument("--episode-cap", type=int, default=125)
    args = parser.parse_args()
    result = collect(args.model_path, args.alfworld_config, args.output_dir, num_sequences=args.num_sequences, max_rounds=args.max_rounds, probe_count=args.probe_count, max_steps=args.max_steps, seed=args.seed, gpu_hours_cap=args.gpu_hours_cap, wall_hours_cap=args.wall_hours_cap, episode_cap=args.episode_cap)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
