from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from .agent_competence_qualification import DEFAULT_GATE_CONFIG, evaluate_gate


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def aggregate(shard_dirs: list[Path], gate_config_path: Path, output: Path | None = None) -> dict[str, Any]:
    if not shard_dirs:
        raise ValueError("at least one shard directory is required")
    summaries = [load_json(path / "summary.json") for path in shard_dirs]
    first = summaries[0]
    expected_shards = int(first.get("num_shards") or 1)
    seen_indices = {int(row.get("shard_index") or 0) for row in summaries}
    if expected_shards != len(shard_dirs) or seen_indices != set(range(expected_shards)):
        raise ValueError(f"qualification shards incomplete: expected {expected_shards}, got {sorted(seen_indices)}")
    contract_keys = ("model_path", "policy_mode", "split", "seed", "max_steps", "global_num_envs")
    for row in summaries[1:]:
        for key in contract_keys:
            if row.get(key) != first.get(key):
                raise ValueError(f"qualification shard contract mismatch on {key}")

    seen_global: set[int] = set()
    family_stats: dict[str, dict[str, int]] = defaultdict(lambda: {"n": 0, "success": 0})
    total_steps = 0
    successes = 0
    usage = {"input_tokens": 0, "output_tokens": 0, "tokens": 0, "generation_calls": 0}
    for directory, summary in zip(shard_dirs, summaries):
        traces = directory / "qualification-traces.jsonl"
        for line in traces.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            global_index = int(row["global_index"])
            if global_index in seen_global:
                raise ValueError(f"duplicate qualification global_index {global_index}")
            seen_global.add(global_index)
            trace = row["trace"]
            family = str(row["family"])
            success = int(trace.get("success") or 0)
            family_stats[family]["n"] += 1
            family_stats[family]["success"] += success
            successes += success
            total_steps += int(trace.get("steps") or 0)
        for key in usage:
            usage[key] += int((summary.get("usage") or {}).get(key) or 0)

    expected_global = int(first.get("global_num_envs") or 0)
    if len(seen_global) != expected_global or seen_global != set(range(expected_global)):
        raise ValueError(f"qualification global coverage incomplete: {len(seen_global)}/{expected_global}")
    result = {
        "schema_version": "1.0",
        "status": "complete",
        "model_path": first["model_path"],
        "policy_mode": first["policy_mode"],
        "split": first["split"],
        "seed": first["seed"],
        "num_envs": expected_global,
        "max_steps": first["max_steps"],
        "successes": successes,
        "success_rate": successes / max(1, expected_global),
        "mean_steps": total_steps / max(1, expected_global),
        "task_families": dict(sorted(family_stats.items())),
        "task_types_with_success": sum(1 for row in family_stats.values() if row["success"] > 0),
        "usage": usage,
        "source_shards": [str(path) for path in shard_dirs],
    }
    result["gate"] = evaluate_gate(result, load_json(gate_config_path))
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        tmp = output.with_suffix(output.suffix + ".tmp")
        tmp.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        tmp.replace(output)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate deterministic agent-qualification shards.")
    parser.add_argument("shard_dirs", nargs="+", type=Path)
    parser.add_argument("--gate-config", type=Path, default=DEFAULT_GATE_CONFIG)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(json.dumps(aggregate(args.shard_dirs, args.gate_config, args.output), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
