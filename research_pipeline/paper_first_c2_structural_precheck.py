from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .p0_alfworld_adapter import ALFWorldGameRunner, load_config
from .paper_first_c2_contract import build_c2_contract


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _hash_json(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _load_parent(parent_root: Path) -> tuple[dict[str, dict[str, str]], dict[tuple[str, str], dict[str, Any]]]:
    main_rows = list(csv.DictReader((parent_root / "full-support-table" / "main_table.csv").open(encoding="utf-8")))
    main = {str(row["unit_id"]): row for row in main_rows}
    raw: dict[tuple[str, str], dict[str, Any]] = {}
    for line in (parent_root / "full-support-table" / "raw-traces.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        raw[(str(row["unit_id"]), str(row["arm"]))] = row
    return main, raw


def _replay_to_branchpoint(
    runner: ALFWorldGameRunner,
    *,
    task_path: str,
    prefix: list[str],
    forced_actions: tuple[str, str],
    force_one_step: str | None = None,
) -> dict[str, Any]:
    env = runner.build_env("eval_out_of_distribution", [task_path])
    try:
        obs, info = env.reset()
        current_obs = str(obs[0])
        reward = 0.0
        done = False
        prefix_admissible = True
        for action in prefix:
            commands = list((info.get("admissible_commands") or [[]])[0])
            if action not in commands:
                prefix_admissible = False
                break
            obs, scores, dones, info = env.step([action])
            current_obs = str(obs[0])
            reward = float(scores[0])
            done = bool(dones[0])
            if done:
                break
        commands = sorted(str(x) for x in ((info.get("admissible_commands") or [[]])[0] or []))
        snapshot = {
            "observation": current_obs,
            "reward": reward,
            "done": done,
            "admissible_commands": commands,
        }
        both_admissible = bool(not done and all(action in commands for action in forced_actions))
        one_step_support = None
        forced_admissible = None
        if force_one_step is not None:
            forced_admissible = bool(not done and force_one_step in commands)
            if forced_admissible:
                obs, scores, dones, info = env.step([force_one_step])
                done2 = bool(dones[0])
                post_commands = list((info.get("admissible_commands") or [[]])[0])
                one_step_support = bool(done2 or post_commands)
            else:
                one_step_support = False
        return {
            "prefix_admissible": prefix_admissible,
            "branchpoint_sha256": _hash_json(snapshot),
            "branchpoint_done": done,
            "admissible_count": len(commands),
            "both_A0_A1_admissible": both_admissible,
            "forced_action_admissible": forced_admissible,
            "forced_action_one_step_support": one_step_support,
        }
    finally:
        close = getattr(env, "close", None)
        if callable(close):
            close()


def run_structural_precheck(*, parent_root: Path, alfworld_config: Path, output: Path) -> dict[str, Any]:
    contract = build_c2_contract()
    inventory_path = Path(__file__).with_name("paper_first_c2_support_inventory_20260812.json")
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    inv = {str(row["unit_id"]): row for row in inventory["units"]}
    strict_ids = list(contract["strict_units"])
    if len(strict_ids) != 10:
        raise ValueError(f"strict C2 pool must be exactly 10, got {len(strict_ids)}")
    main, raw = _load_parent(parent_root)
    cfg = load_config(alfworld_config)
    cfg.setdefault("general", {})["save_path"] = str(output.parent / "c2-structural-alfworld-runtime")
    runner = ALFWorldGameRunner(cfg)
    allowed_context_fields = ["source_family", "target_family"]
    units: list[dict[str, Any]] = []
    for unit_id in strict_ids:
        row = inv[unit_id]
        parent = main[unit_id]
        retrieved = raw[(unit_id, "retrieved")]
        placebo = raw[(unit_id, "placebo")]
        idx = int(row["divergence_index"])
        r_actions = [str(x) for x in retrieved["actions"]]
        p_actions = [str(x) for x in placebo["actions"]]
        prefix = r_actions[:idx]
        prefix_match = prefix == p_actions[:idx]
        A1 = str(row["retrieved_action"])
        A0 = str(row["placebo_action"])
        frozen_action_match = bool(
            idx < len(r_actions) and idx < len(p_actions) and r_actions[idx] == A1 and p_actions[idx] == A0
        )
        task_path = str(parent["target_task_id"])
        fresh1 = _replay_to_branchpoint(runner, task_path=task_path, prefix=prefix, forced_actions=(A0, A1))
        fresh2 = _replay_to_branchpoint(runner, task_path=task_path, prefix=prefix, forced_actions=(A0, A1))
        a0 = _replay_to_branchpoint(runner, task_path=task_path, prefix=prefix, forced_actions=(A0, A1), force_one_step=A0)
        a1 = _replay_to_branchpoint(runner, task_path=task_path, prefix=prefix, forced_actions=(A0, A1), force_one_step=A1)
        context = {"source_family": str(row["source_family"]), "target_family": str(row["target_family"])}
        context_pre_treatment = set(context) == set(allowed_context_fields) and all(context.values())
        branchpoint_equal = fresh1["branchpoint_sha256"] == fresh2["branchpoint_sha256"] == a0["branchpoint_sha256"] == a1["branchpoint_sha256"]
        valid = bool(
            prefix_match
            and frozen_action_match
            and fresh1["prefix_admissible"]
            and fresh2["prefix_admissible"]
            and branchpoint_equal
            and fresh1["both_A0_A1_admissible"]
            and fresh2["both_A0_A1_admissible"]
            and a0["forced_action_admissible"]
            and a1["forced_action_admissible"]
            and a0["forced_action_one_step_support"]
            and a1["forced_action_one_step_support"]
            and context_pre_treatment
        )
        units.append({
            "unit_id": unit_id,
            "memory_id": str(row["memory_id"]),
            "target_task_id": task_path,
            "divergence_index": idx,
            "A0": A0,
            "A1": A1,
            "context": context,
            "context_fields": allowed_context_fields,
            "prefix_match_between_parent_arms": prefix_match,
            "frozen_action_match": frozen_action_match,
            "fresh_branchpoint_repeat_equal": branchpoint_equal,
            "prefix_admissible": bool(fresh1["prefix_admissible"] and fresh2["prefix_admissible"]),
            "A0_A1_simultaneously_admissible": bool(fresh1["both_A0_A1_admissible"] and fresh2["both_A0_A1_admissible"]),
            "A0_one_step_support": bool(a0["forced_action_one_step_support"]),
            "A1_one_step_support": bool(a1["forced_action_one_step_support"]),
            "context_pre_treatment_external_only": bool(context_pre_treatment),
            "branchpoint_sha256": fresh1["branchpoint_sha256"],
            "valid": valid,
        })
    valid_units = sum(bool(row["valid"]) for row in units)
    result = {
        "schema_version": "1.0",
        "generated_at": _now(),
        "paper_id": contract["paper_id"],
        "stage": "C2-structural-precheck-before-any-branch-outcome",
        "decision": "C2_STRUCTURAL_PRECHECK_PASS" if valid_units == 10 else "C2_STRUCTURAL_PRECHECK_STOP",
        "valid_units": valid_units,
        "required_valid_units": 10,
        "strict_units": 10,
        "outcome_opened": False,
        "tau_A_computed": False,
        "same_action_null_opened": False,
        "pi0_full_continuation_opened": False,
        "allowed_context_fields": allowed_context_fields,
        "units": units,
        "next_gate": "support-aware AI adjudication on whether the 10-unit pool warrants opening same-action null / C2 branch outcomes",
        "C3_locked": True,
        "full_experiment_authorized": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--parent-root", type=Path, required=True)
    parser.add_argument("--alfworld-config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run_structural_precheck(parent_root=args.parent_root, alfworld_config=args.alfworld_config, output=args.output), ensure_ascii=False, indent=2))
