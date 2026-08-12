from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .p0_alfworld_adapter import ALFWorldGameRunner, HFAdmissiblePolicy, load_config
from .p0_c_shared_core import check_gpu_free, write_json
from .p0_c_shared_future_resume import _local_task, _rows


def audit(plan_path: Path, baseline_file: Path, model_path: Path, alfworld_config: Path, output_path: Path) -> dict[str, Any]:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    rows = _rows(baseline_file)
    frozen = {
        (row.get("role"), row.get("task")): row.get("trace") or {}
        for row in rows
        if row.get("role") in {"probe-baseline", "hidden-baseline"}
    }
    expected = len(plan["probe_tasks"]) + len(plan["hidden_tasks"])
    if len(frozen) != expected:
        raise RuntimeError(f"frozen baseline table incomplete: {len(frozen)}/{expected}")
    gpu = check_gpu_free()
    config = load_config(alfworld_config)
    config.setdefault("general", {})["save_path"] = str(output_path.parent / "runtime-portability-alfworld")
    policy = HFAdmissiblePolicy(model_path, policy_mode="react-family")
    runner = ALFWorldGameRunner(config)
    details = []
    for role, split, tasks in (
        ("probe-baseline", "eval_in_distribution", plan["probe_tasks"]),
        ("hidden-baseline", "eval_out_of_distribution", plan["hidden_tasks"]),
    ):
        for task in tasks:
            trace = runner.run_game_file(split, _local_task(task), policy, max_steps=int(plan["max_steps"]))
            prior = frozen[(role, task)]
            details.append({
                "role": role,
                "task": task,
                "frozen_success": int(prior.get("success", 0)),
                "runtime_success": int(trace.get("success", 0)),
                "success_match": int(prior.get("success", 0)) == int(trace.get("success", 0)),
                "first_action_match": (prior.get("actions") or [None])[0] == (trace.get("actions") or [None])[0],
                "action_sequence_match": list(prior.get("actions") or []) == list(trace.get("actions") or []),
            })
    success_matches = sum(row["success_match"] for row in details)
    result = {
        "schema_version": "1.0",
        "decision": "PORTABILITY_PASS" if success_matches == expected else "PORTABILITY_FAIL_REANCHOR_REQUIRED",
        "tasks": expected,
        "success_matches": success_matches,
        "success_match_rate": success_matches / expected,
        "first_action_matches": sum(row["first_action_match"] for row in details),
        "action_sequence_matches": sum(row["action_sequence_match"] for row in details),
        "f0_authority": success_matches == expected,
        "failure_action": "If any success truth differs, do not interpret cross-server candidate deltas; recompute against a runtime-matched 60 baseline before F0.",
        "gpu_preflight": gpu,
        "usage": policy.usage_snapshot(),
        "details": details,
    }
    write_json(output_path, result)
    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--baseline-file", type=Path, required=True)
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--alfworld-config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(audit(args.plan, args.baseline_file, args.model_path, args.alfworld_config, args.output), ensure_ascii=False, indent=2))
