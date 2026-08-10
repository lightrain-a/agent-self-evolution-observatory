from __future__ import annotations

import argparse
import json
import math
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .p0_a1 import _candidate
from .p0_alfworld_adapter import ALFWorldGameRunner, HFAdmissiblePolicy, load_config as load_alfworld_config, normalized_edit_distance
from .p0_common import load_json


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


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
        raise ValueError("probe fidelity classifier requires both harmful and non-harmful candidates")
    dims = len(features[0])
    mu = [_mean([row[j] for row in features]) for j in range(dims)]
    sd: list[float] = []
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


def _loo_auc(features: list[list[float]], labels: list[int]) -> float:
    predictions: list[float] = []
    for holdout in range(len(features)):
        train_x = [row for index, row in enumerate(features) if index != holdout]
        train_y = [label for index, label in enumerate(labels) if index != holdout]
        if len(set(train_y)) < 2:
            return 0.5
        model = _fit_mean_difference(train_x, train_y)
        predictions.append(_score(model, features[holdout]))
    return _auc(labels, predictions)


def _check_budget(started: float, episodes: int, *, gpu_hours_cap: float, wall_hours_cap: float, episode_cap: int) -> None:
    elapsed = (time.time() - started) / 3600.0
    if gpu_hours_cap > 0 and elapsed >= gpu_hours_cap:
        raise RuntimeError(f"mastered-probe replay GPU-hour cap reached: {elapsed:.4f} >= {gpu_hours_cap:.4f}")
    if wall_hours_cap > 0 and elapsed >= wall_hours_cap:
        raise RuntimeError(f"mastered-probe replay wall-hour cap reached: {elapsed:.4f} >= {wall_hours_cap:.4f}")
    if episode_cap > 0 and episodes >= episode_cap:
        raise RuntimeError(f"mastered-probe replay episode cap reached: {episodes} >= {episode_cap}")


def _baseline_traces(panel: dict[str, Any]) -> dict[str, dict[str, Any]]:
    source = Path(str(panel["source"]))
    rows = _read_jsonl(source)
    selected = {str(row["task_id"]) for row in panel.get("selected") or []}
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        trace = row.get("trace") or {}
        task_id = str(trace.get("task_id") or "")
        if task_id in selected:
            result[task_id] = trace
    missing = sorted(selected - set(result))
    if missing:
        raise ValueError(f"mastered probe baseline traces missing: {missing}")
    if any(int(trace.get("success") or 0) != 1 for trace in result.values()):
        raise ValueError("mastered probe panel contains a baseline-unsuccessful task")
    return result


def analyze_replays(config: dict[str, Any], candidate_eval_rows: list[dict[str, Any]], panel: dict[str, Any], baseline: dict[str, dict[str, Any]], replay_rows: list[dict[str, Any]]) -> dict[str, Any]:
    candidates = [_candidate(row, config) for row in candidate_eval_rows]
    candidate_ids = [row.candidate_id for row in candidates]
    labels = [int(row.harmful) for row in candidates]
    by_candidate: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in replay_rows:
        candidate_id = str(row.get("candidate_id") or "")
        trace = row.get("trace") or {}
        if candidate_id in set(candidate_ids):
            by_candidate[candidate_id][str(trace.get("task_id") or "")] = trace

    task_ids = [str(row["task_id"]) for row in panel.get("selected") or []]
    probe_rows: list[dict[str, Any]] = []
    candidate_features: dict[str, dict[str, Any]] = {candidate_id: {"success_losses": [], "action_distances": [], "length_changes": [], "invalid_changes": []} for candidate_id in candidate_ids}
    for task_id in task_ids:
        before = baseline[task_id]
        success_loss_scores: list[float] = []
        action_scores: list[float] = []
        length_scores: list[float] = []
        invalid_scores: list[float] = []
        for candidate_id in candidate_ids:
            after = by_candidate[candidate_id].get(task_id)
            if after is None:
                raise ValueError(f"candidate {candidate_id} missing mastered probe replay {task_id}")
            success_loss = float(int(before.get("success") or 0) == 1 and int(after.get("success") or 0) == 0)
            action = normalized_edit_distance(list(before.get("actions") or []), list(after.get("actions") or []))
            length = abs(float(after.get("steps") or 0) - float(before.get("steps") or 0)) / 50.0
            invalid = float(after.get("invalid_choice_rate") or 0.0) - float(before.get("invalid_choice_rate") or 0.0)
            success_loss_scores.append(success_loss); action_scores.append(action); length_scores.append(length); invalid_scores.append(invalid)
            features = candidate_features[candidate_id]
            features["success_losses"].append(success_loss); features["action_distances"].append(action); features["length_changes"].append(length); features["invalid_changes"].append(invalid)
        probe_rows.append({"task_id": task_id, "task_family": str(before.get("task_family") or "unknown"), "baseline_steps": int(before.get("steps") or 0), "success_loss_events": int(sum(success_loss_scores)), "success_loss_auc": _auc(labels, success_loss_scores), "action_distance_auc": _auc(labels, action_scores), "length_change_auc": _auc(labels, length_scores), "invalid_change_auc": _auc(labels, invalid_scores)})

    probe_only: list[list[float]] = []
    gain_plus_probe: list[list[float]] = []
    success_loss_rate: list[float] = []
    for candidate in candidates:
        features = candidate_features[candidate.candidate_id]
        row = [_mean(features["success_losses"]), _mean(features["action_distances"]), max(features["action_distances"]), _mean(features["length_changes"]), _mean(features["invalid_changes"])]
        probe_only.append(row); gain_plus_probe.append([float(candidate.current_task_gain), *row]); success_loss_rate.append(row[0])
    probe_only_auc = _loo_auc(probe_only, labels)
    combined_auc = _loo_auc(gain_plus_probe, labels)
    success_loss_auc = _auc(labels, success_loss_rate)
    total_success_losses = sum(int(row["success_loss_events"]) for row in probe_rows)
    minimum_auc = 0.65
    development_pass = probe_only_auc >= minimum_auc and total_success_losses >= 3
    return {"candidate_count": len(candidates), "harmful_candidates": int(sum(labels)), "panel_size": len(task_ids), "panel_family_coverage": len({row["task_family"] for row in probe_rows}), "probe_rows": probe_rows, "total_probe_success_loss_events": total_success_losses, "success_loss_rate_auc": success_loss_auc, "probe_only_leave_one_candidate_out_auc": probe_only_auc, "gain_plus_probe_leave_one_candidate_out_auc": combined_auc, "minimum_fidelity_auc": minimum_auc, "development_fidelity_pass": development_pass, "diagnosis": "Mastered-task probes produce a development fidelity signal. Freeze the panel-selection rule and validate it on a fresh candidate batch before any formal P0." if development_pass else "Even mastered-task probes do not predict hidden harmful regression strongly enough on the development batch; revise the probe signal/panel before fresh validation."}


def collect(model_path: Path, alfworld_config: Path, a1_run_dir: Path, panel_path: Path, output_dir: Path, *, max_steps: int, gpu_hours_cap: float, wall_hours_cap: float, episode_cap: int) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    replay_path = output_dir / "probe-replays.jsonl"
    if replay_path.exists() and replay_path.stat().st_size:
        raise RuntimeError(f"refusing to overwrite non-empty mastered-probe replay artifact: {replay_path}")
    replay_path.write_text("", encoding="utf-8")
    config = load_json(Path(__file__).with_name("p0_a1_screening_config.json"))
    candidate_eval_rows = _read_jsonl(a1_run_dir / "candidate-evaluation.jsonl")
    candidate_patches = _read_jsonl(a1_run_dir / "candidate-patches.jsonl")
    panel = load_json(panel_path)
    if panel.get("pass") is not True:
        raise ValueError("mastered probe panel is not qualified")
    baseline = _baseline_traces(panel)
    patch_by_id = {str(row["candidate_id"]): str(row.get("patch") or "") for row in candidate_patches}
    candidate_ids = [str(row["candidate_id"]) for row in candidate_eval_rows]
    if set(candidate_ids) - set(patch_by_id):
        raise ValueError("candidate patch file does not cover the frozen A-1 candidate set")
    world = load_alfworld_config(alfworld_config); world.setdefault("general", {})["save_path"] = str(output_dir / "alfworld-runtime")
    policy = HFAdmissiblePolicy(model_path, policy_mode="react-family"); runner = ALFWorldGameRunner(world); started = time.time(); episodes = 0
    task_ids = [str(row["task_id"]) for row in panel.get("selected") or []]
    for candidate_index, candidate_id in enumerate(candidate_ids, 1):
        patch = patch_by_id[candidate_id]
        for probe_index, task_id in enumerate(task_ids, 1):
            trace = runner.run_game_file("eval_in_distribution", task_id, policy, patch, max_steps=max_steps); episodes += 1
            _append_jsonl(replay_path, {"candidate_id": candidate_id, "candidate_index": candidate_index, "candidates_total": len(candidate_ids), "probe_index": probe_index, "probes_total": len(task_ids), "trace": trace})
            usage = policy.usage_snapshot(); _atomic(output_dir / "progress.json", {"stage": "mastered-probe-replay", "candidate_id": candidate_id, "candidate_index": candidate_index, "candidates_total": len(candidate_ids), "probe_index": probe_index, "probes_total": len(task_ids), "environment_episodes": episodes, "model_calls": int(usage["generation_calls"]), "tokens": int(usage["tokens"]), "elapsed_hours": round((time.time() - started) / 3600.0, 6)})
            _check_budget(started, episodes, gpu_hours_cap=gpu_hours_cap, wall_hours_cap=wall_hours_cap, episode_cap=episode_cap)
    result = analyze_replays(config, candidate_eval_rows, panel, baseline, _read_jsonl(replay_path)); usage = policy.usage_snapshot()
    result.update({"schema_version": "1.0", "generated_at": _now(), "artifact_kind": "mastered-probe-panel-development-replay", "source_a1_run": str(a1_run_dir), "panel_path": str(panel_path), "model_path": str(model_path), "policy_mode": "react-family", "max_steps": max_steps, "environment_episodes": episodes, "model_calls": int(usage["generation_calls"]), "tokens": int(usage["tokens"]), "gpu_hours": round((time.time() - started) / 3600.0, 6), "resource_cap": {"gpu_hours": gpu_hours_cap, "wall_hours": wall_hours_cap, "episodes": episode_cap}, "scientific_result_available": False, "pilot_registry_write_forbidden": True, "scientific_role": "development repair only; current hidden labels may diagnose the panel, but a fresh candidate batch is required for validation"})
    _atomic(output_dir / "qualification.json", result); return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay frozen A-1 development candidates on a mastered-task probe panel.")
    parser.add_argument("--model-path", type=Path, required=True); parser.add_argument("--alfworld-config", type=Path, required=True); parser.add_argument("--a1-run-dir", type=Path, required=True); parser.add_argument("--panel", type=Path, required=True); parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--max-steps", type=int, default=50); parser.add_argument("--gpu-hours-cap", type=float, default=1.4); parser.add_argument("--wall-hours-cap", type=float, default=2.0); parser.add_argument("--episode-cap", type=int, default=100)
    args = parser.parse_args(); result = collect(args.model_path, args.alfworld_config, args.a1_run_dir, args.panel, args.output_dir, max_steps=args.max_steps, gpu_hours_cap=args.gpu_hours_cap, wall_hours_cap=args.wall_hours_cap, episode_cap=args.episode_cap); print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
