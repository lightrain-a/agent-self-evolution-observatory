from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from research_pipeline.paper_first_agent_safety_r9_f0_browser import verify_services
from research_pipeline.paper_first_agent_safety_r9_f0_journal import (
    acquire_lock,
    load_journal,
    release_lock,
)
from research_pipeline.paper_first_agent_safety_r9_f0_runtime import run_episode


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected object: {path}")
    return value


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def sha_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def validate_plan_hash(plan: dict[str, Any]) -> None:
    expected = sha_bytes(canonical({k: v for k, v in plan.items() if k != "plan_sha256"}))
    require(plan["plan_sha256"] == expected, "control plan hash drift")


def summarize_no_update(journal: dict[str, Any]) -> dict[str, Any]:
    completed = [row for row in journal["episodes"].values() if row.get("status") == "completed"]
    by_key = {
        (row["state_id"], int(row["branch_seed"]), int(row["future_step"])): row
        for row in completed
    }
    states = sorted({row["state_id"] for row in completed})
    seeds = sorted({int(row["branch_seed"]) for row in completed})
    survival: dict[str, Any] = {}
    first_counts: Counter[str] = Counter()
    for state_id in states:
        survival[state_id] = {}
        for seed in seeds:
            rows = [by_key[(state_id, seed, step)] for step in (1, 2, 3)]
            predictions = [int(row["harmbench_prediction"]) for row in rows]
            first = next((i + 1 for i, value in enumerate(predictions) if value == 1), None)
            first_counts["censored" if first is None else str(first)] += 1
            survival[state_id][str(seed)] = {
                "predictions_by_step": predictions,
                "first_violation_step": first,
                "event_observed": first is not None,
                "censored_at_step3": first is None,
                "episode_ids": [row["episode_id"] for row in rows],
            }
    return {
        "survival": survival,
        "future_violation_episodes": sum(int(row["harmbench_prediction"]) for row in completed),
        "branches": len(states) * len(seeds),
        "branches_with_first_violation": sum(
            branch["event_observed"]
            for state in survival.values()
            for branch in state.values()
        ),
        "first_violation_step_counts": {
            "step1": first_counts["1"],
            "step2": first_counts["2"],
            "step3": first_counts["3"],
            "censored_at_step3": first_counts["censored"],
        },
    }


def summarize_fixed(journal: dict[str, Any], prereg: dict[str, Any]) -> dict[str, Any]:
    completed = [row for row in journal["episodes"].values() if row.get("status") == "completed"]
    by_key = {
        (row["state_id"], int(row["behavior_id"]), int(row["future_step"])): row
        for row in completed
    }
    step0 = prereg["step0_qualification_rows"]
    trajectories: dict[str, Any] = {}
    first_counts: Counter[str] = Counter()
    violations_by_exposure = {0: 0, 1: 0, 2: 0, 3: 0}
    for state_id, baseline_rows in step0.items():
        trajectories[state_id] = {}
        for baseline in baseline_rows:
            behavior_id = int(baseline["behavior_id"])
            rows = [by_key[(state_id, behavior_id, step)] for step in (1, 2, 3)]
            predictions = [0] + [int(row["harmbench_prediction"]) for row in rows]
            first = next((step for step, value in enumerate(predictions) if value == 1), None)
            first_counts["censored" if first is None else str(first)] += 1
            for step, value in enumerate(predictions):
                violations_by_exposure[step] += value
            trajectories[state_id][str(behavior_id)] = {
                "predictions_by_exposure_step": predictions,
                "first_violation_exposure_step": first,
                "event_observed": first is not None,
                "censored_at_step3": first is None,
                "step0_episode_id": baseline["episode_id"],
                "new_episode_ids": [row["episode_id"] for row in rows],
            }
    return {
        "trajectories": trajectories,
        "violations_by_exposure_step": {str(k): v for k, v in violations_by_exposure.items()},
        "trajectories_with_first_violation": sum(
            row["event_observed"]
            for state in trajectories.values()
            for row in state.values()
        ),
        "trajectory_count": len(step0) * 3,
        "first_violation_exposure_step_counts": {
            "step1": first_counts["1"],
            "step2": first_counts["2"],
            "step3": first_counts["3"],
            "censored_at_step3": first_counts["censored"],
        },
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.experiment_root)
    prereg = load(root / "preregistration.json")
    review = load(root / "protocol-review.json")
    gate = load(root / "execution-gate.json")
    auth = load(root / "human-execution-authorization.json")
    require(gate["status"] == "READY_R23_CONTROLLED_LONGITUDINAL_EXECUTION", "execution gate not ready")
    require(gate["execution_authorized"] is True and gate["gpu_authorized"] is True, "execution authority missing")
    require(gate["preregistration_sha256"] == prereg["preregistration_sha256"], "gate/preregistration drift")
    require(gate["review_sha256"] == review["review_sha256"], "gate/review drift")
    require(gate["human_authorization_sha256"] == auth["authorization_sha256"], "gate/human authority drift")
    require(review["status"] == "PASS_EXACT_MATCHED_CONTROL_PROTOCOL_REVIEW", "protocol review not PASS")

    arm_dir_name = "no-update" if args.arm == "no-update" else "fixed-probe"
    execution_name = "no-update-execution" if args.arm == "no-update" else "fixed-probe-execution"
    arm_root = root / arm_dir_name
    plan = load(arm_root / "control-plan.json")
    validate_plan_hash(plan)
    expected_plan_hash = gate["no_update_plan_sha256"] if args.arm == "no-update" else gate["fixed_probe_plan_sha256"]
    require(plan["plan_sha256"] == expected_plan_hash, "gate/plan drift")
    require(len(plan["episodes"]) == 36, "arm episode cardinality drift")

    out = root / execution_name
    lock = acquire_lock(out, plan)
    try:
        journal = load_journal(out, plan)
        require(not any(row.get("status") == "protocol_inconclusive" for row in journal["episodes"].values()),
                "protocol-inconclusive episode forbids continuation")
        services = verify_services()
        require(services["qwen"]["id"] == "Qwen3-8B", "Qwen service identity drift")
        require(services["harmbench"]["revision"] == "0cd31cdc8b53209dd5b153b20026ff085901bb14",
                "HarmBench service identity drift")

        rows = json.loads((Path(args.browserart_root) / "src/datasets/behaviors/hbb.json").read_text(encoding="utf-8"))
        by_id = {int(row["id"]): row for row in rows}
        behavior_ids = sorted({int(row["behavior_id"]) for row in plan["episodes"]})
        behaviors = {}
        for behavior_id in behavior_ids:
            row = by_id.get(behavior_id)
            require(row is not None and row.get("evaluation_category") == "closed-ended",
                    f"behavior identity drift: {behavior_id}")
            require(row.get("website") in {"local:email", "local:twitter", "local:review"},
                    f"behavior website drift: {behavior_id}")
            behaviors[str(behavior_id)] = row
        bundle = {"behaviors": behaviors}
        episode_args = SimpleNamespace(
            output_dir=str(out),
            browserart_root=args.browserart_root,
            awm_root=args.awm_root,
            states_dir=args.states_dir,
            preflight_dir=str(arm_root),
        )

        new = 0
        for spec in plan["episodes"]:
            prior = journal["episodes"].get(spec["episode_id"])
            if prior is not None:
                require(prior.get("status") == "completed", f"non-completed episode blocks: {spec['episode_id']}")
                continue
            run_episode(spec, bundle, journal, episode_args)
            new += 1
            if args.max_new_episodes and new >= args.max_new_episodes:
                break

        completed = journal["counters"]["completed_episodes"]
        result: dict[str, Any] = {
            "schema_version": "1.0",
            "status": "R23_CONTROL_ARM_PARTIAL" if completed < 36 else "READY_R23_CONTROL_ARM_OUTCOMES",
            "arm": args.arm,
            "plan_sha256": plan["plan_sha256"],
            "new_episodes_completed": new,
            "total_completed": completed,
            "counters": dict(journal["counters"]),
            "scientific_authority": False,
        }
        if completed == 36:
            result["outcomes"] = (
                summarize_no_update(journal)
                if args.arm == "no-update"
                else summarize_fixed(journal, prereg)
            )
            summary_path = out / "arm-outcomes-summary.json"
            summary_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return result
    finally:
        release_lock(lock)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment-root", required=True)
    parser.add_argument("--arm", choices=("no-update", "fixed-probe"), required=True)
    parser.add_argument("--awm-root", required=True)
    parser.add_argument("--browserart-root", required=True)
    parser.add_argument("--states-dir", required=True)
    parser.add_argument("--max-new-episodes", type=int, default=0)
    result = run(parser.parse_args())
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
