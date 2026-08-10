from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from .alfworld_react_scaffold import task_family_from_gamefile
from .p0_alfworld_adapter import ALFWorldGameRunner, HFAdmissiblePolicy, load_config


DEFAULT_GATE_CONFIG = Path(__file__).with_name("p0_agent_qualification_config.json")


def evaluate_gate(summary: dict[str, Any], gate_config: dict[str, Any]) -> dict[str, Any]:
    split = str(summary.get("split") or "")
    calibration = gate_config.get("calibration") or {}
    full = gate_config.get("full_qualification") or {}
    if split == str(calibration.get("split") or "eval_in_distribution"):
        success_threshold = float(calibration.get("minimum_success_rate_to_full_qualification", 0.20))
        type_threshold = int(calibration.get("minimum_task_types_with_success_to_full_qualification", 3))
        passed = float(summary.get("success_rate") or 0.0) >= success_threshold and int(summary.get("task_types_with_success") or 0) >= type_threshold
        return {
            "stage": "calibration",
            "passed": passed,
            "decision": "advance-full-qualification" if passed else "revise-base-agent",
            "minimum_success_rate": success_threshold,
            "minimum_task_types_with_success": type_threshold,
        }
    if split == str(full.get("split") or "eval_out_of_distribution"):
        success_threshold = float(full.get("minimum_success_rate", 0.30))
        successes_threshold = int(full.get("minimum_successful_tasks", 41))
        type_threshold = int(full.get("minimum_task_types_with_success", 5))
        passed = (
            float(summary.get("success_rate") or 0.0) >= success_threshold
            and int(summary.get("successes") or 0) >= successes_threshold
            and int(summary.get("task_types_with_success") or 0) >= type_threshold
        )
        return {
            "stage": "full-qualification",
            "passed": passed,
            "decision": "qualified" if passed else "revise-base-agent",
            "minimum_success_rate": success_threshold,
            "minimum_successful_tasks": successes_threshold,
            "minimum_task_types_with_success": type_threshold,
        }
    return {"stage": "unknown", "passed": False, "decision": "unsupported-split"}


def stratified_select(files: list[str], count: int, seed: int) -> list[str]:
    if count <= 0 or count >= len(files):
        return sorted(files)
    groups: dict[str, list[str]] = defaultdict(list)
    for path in files:
        groups[task_family_from_gamefile(path)].append(path)
    for family in groups:
        groups[family].sort(key=lambda p: hashlib.sha256(f"{seed}|{family}|{p}".encode()).hexdigest())
    families = sorted(groups)
    chosen: list[str] = []
    cursor = 0
    while len(chosen) < count and families:
        family = families[cursor % len(families)]
        if groups[family]:
            chosen.append(groups[family].pop(0))
        else:
            families.remove(family)
            if not families:
                break
            cursor -= 1
        cursor += 1
    return chosen


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        handle.flush()


def run(args: argparse.Namespace) -> dict[str, Any]:
    world = load_config(args.alfworld_config)
    world.setdefault("general", {})["save_path"] = str(args.output_dir / "alfworld-runtime")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    traces_path = args.output_dir / "qualification-traces.jsonl"
    if traces_path.exists() and traces_path.stat().st_size:
        raise RuntimeError(f"refusing to overwrite non-empty qualification output: {traces_path}")
    traces_path.write_text("", encoding="utf-8")

    policy = HFAdmissiblePolicy(args.model_path, policy_mode=args.policy_mode)
    runner = ALFWorldGameRunner(world)
    files = runner.available_game_files(args.split)
    full_selected = stratified_select(files, args.num_envs, args.seed)
    if args.num_shards < 1 or not (0 <= args.shard_index < args.num_shards):
        raise ValueError("qualification shard requires num_shards>=1 and 0<=shard_index<num_shards")
    selected_pairs = [(global_index, path) for global_index, path in enumerate(full_selected) if global_index % args.num_shards == args.shard_index]
    selected = [path for _, path in selected_pairs]
    family_stats: dict[str, dict[str, int]] = defaultdict(lambda: {"n": 0, "success": 0})
    success = 0
    total_steps = 0
    for local_index, (global_index, game_file) in enumerate(selected_pairs, 1):
        trace = runner.run_game_file(args.split, game_file, policy, max_steps=args.max_steps)
        family = task_family_from_gamefile(game_file)
        family_stats[family]["n"] += 1
        family_stats[family]["success"] += int(trace["success"])
        success += int(trace["success"])
        total_steps += int(trace["steps"])
        append_jsonl(traces_path, {"index": local_index, "global_index": global_index, "family": family, "trace": trace})
        progress = {
            "status": "running",
            "completed": local_index,
            "total": len(selected),
            "global_total": len(full_selected),
            "shard_index": args.shard_index,
            "num_shards": args.num_shards,
            "success": success,
            "success_rate": success / local_index,
            "model_calls": policy.usage_snapshot()["generation_calls"],
        }
        (args.output_dir / "progress.json").write_text(json.dumps(progress, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    usage = policy.usage_snapshot()
    summary = {
        "schema_version": "1.0",
        "status": "complete",
        "model_path": str(args.model_path),
        "policy_mode": args.policy_mode,
        "split": args.split,
        "seed": args.seed,
        "num_envs": len(selected),
        "global_num_envs": len(full_selected),
        "shard_index": args.shard_index,
        "num_shards": args.num_shards,
        "max_steps": args.max_steps,
        "successes": success,
        "success_rate": success / max(1, len(selected)),
        "mean_steps": total_steps / max(1, len(selected)),
        "task_families": dict(sorted(family_stats.items())),
        "task_types_with_success": sum(1 for row in family_stats.values() if row["success"] > 0),
        "usage": usage,
    }
    gate_config = json.loads(args.gate_config.read_text(encoding="utf-8"))
    summary["gate"] = evaluate_gate(summary, gate_config) if args.num_shards == 1 else {
        "stage": "shard",
        "passed": None,
        "decision": "aggregate-shards-before-gating",
    }
    (args.output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Qualify ALFWorld base-agent competence before update experiments.")
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--alfworld-config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--split", default="eval_in_distribution")
    parser.add_argument("--num-envs", type=int, default=24)
    parser.add_argument("--max-steps", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--policy-mode", choices=["direct", "react-lite", "react-family"], default="react-family")
    parser.add_argument("--gate-config", type=Path, default=DEFAULT_GATE_CONFIG)
    parser.add_argument("--num-shards", type=int, default=1)
    parser.add_argument("--shard-index", type=int, default=0)
    return parser.parse_args()


def main() -> None:
    print(json.dumps(run(parse_args()), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
