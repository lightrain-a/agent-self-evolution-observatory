from __future__ import annotations

import argparse
import csv
import fcntl
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .alfworld_react_scaffold import extract_task_goal, task_family_from_gamefile
from .config import PROJECT_ROOT
from .paper_first_c2_contract import build_c2_contract
from .p0_alfworld_adapter import ALFWorldGameRunner, HFAdmissiblePolicy, load_config

AUTHORIZATION_PATH = PROJECT_ROOT / "generated" / "paper-first-c2-authorization.json"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _hash_json(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _semantic_contract(value: dict[str, Any]) -> dict[str, Any]:
    normalized = json.loads(json.dumps(value))
    normalized.pop("generated_at", None)
    return normalized


def _append_jsonl(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
        handle.flush()


def _sign(value: int | float) -> int:
    return 1 if value > 0 else (-1 if value < 0 else 0)


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


def _state_snapshot(observation: str, score: float, done: bool, info: dict[str, Any]) -> dict[str, Any]:
    return {
        "observation": str(observation),
        "reward": float(score),
        "done": bool(done),
        "admissible_commands": sorted(str(x) for x in ((info.get("admissible_commands") or [[]])[0] or [])),
    }


def _run_forced_branch(
    runner: ALFWorldGameRunner,
    policy: HFAdmissiblePolicy,
    *,
    task_path: str,
    target_family: str,
    prefix: list[str],
    forced_action: str,
    max_total_steps: int,
) -> dict[str, Any]:
    env = runner.build_env("eval_out_of_distribution", [task_path])
    try:
        obs, info = env.reset()
        current_obs = str(obs[0])
        start_obs = current_obs
        task_goal = extract_task_goal(start_obs)
        gamefile = str((info.get("extra.gamefile") or [task_path])[0])
        inferred_family = task_family_from_gamefile(gamefile)
        history: list[tuple[str, str]] = []
        actions: list[str] = []
        observations: list[str] = [current_obs]
        raw_choices: list[str] = []
        invalid_choice_count = 0
        every_action_admissible = True
        final_score = 0.0
        done = False
        won = False

        for action in prefix:
            commands = list((info.get("admissible_commands") or [[]])[0])
            if action not in commands:
                every_action_admissible = False
                break
            obs, scores, dones, info = env.step([action])
            current_obs = str(obs[0])
            final_score = float(scores[0])
            done = bool(dones[0])
            won = bool((info.get("won") or [False])[0])
            actions.append(str(action))
            observations.append(current_obs)
            history.append((str(action), current_obs))
            if done:
                break

        branchpoint = _state_snapshot(current_obs, final_score, done, info)
        branchpoint_hash = _hash_json(branchpoint)
        forced_admissible = False
        post_forced_has_support = False
        if not done and every_action_admissible:
            commands = list((info.get("admissible_commands") or [[]])[0])
            forced_admissible = forced_action in commands
            if forced_admissible:
                obs, scores, dones, info = env.step([forced_action])
                current_obs = str(obs[0])
                final_score = float(scores[0])
                done = bool(dones[0])
                won = bool((info.get("won") or [False])[0])
                actions.append(str(forced_action))
                observations.append(current_obs)
                history.append((str(forced_action), current_obs))
                post_commands = list((info.get("admissible_commands") or [[]])[0])
                post_forced_has_support = bool(done or post_commands)

        while every_action_admissible and forced_admissible and post_forced_has_support and not done and len(actions) < max_total_steps:
            commands = list((info.get("admissible_commands") or [[]])[0])
            if not commands:
                post_forced_has_support = False
                break
            action, was_invalid, raw = policy.choose(
                current_obs,
                commands,
                history,
                "",
                goal_context=task_goal,
                task_family=target_family or inferred_family,
            )
            every_action_admissible = every_action_admissible and action in commands
            invalid_choice_count += int(was_invalid)
            raw_choices.append(raw)
            obs, scores, dones, info = env.step([action])
            current_obs = str(obs[0])
            final_score = float(scores[0])
            done = bool(dones[0])
            won = bool((info.get("won") or [False])[0])
            actions.append(str(action))
            observations.append(current_obs)
            history.append((str(action), current_obs))

        public_trace = {
            "success": int(won),
            "score": float(final_score),
            "steps": len(actions),
            "terminated": bool(done),
            "every_action_admissible": bool(every_action_admissible),
            "forced_action_admissible": bool(forced_admissible),
            "post_forced_has_support": bool(post_forced_has_support),
            "invalid_choice_count": int(invalid_choice_count),
            "actions": actions,
            "observation_sequence_sha256": _hash_json(observations),
            "action_sequence_sha256": _hash_json(actions),
            "branchpoint_sha256": branchpoint_hash,
        }
        return public_trace
    finally:
        close = getattr(env, "close", None)
        if callable(close):
            close()


def _repeat_equal(left: dict[str, Any], right: dict[str, Any]) -> bool:
    keys = (
        "success",
        "score",
        "steps",
        "terminated",
        "every_action_admissible",
        "forced_action_admissible",
        "post_forced_has_support",
        "invalid_choice_count",
        "action_sequence_sha256",
        "observation_sequence_sha256",
        "branchpoint_sha256",
    )
    return all(left.get(key) == right.get(key) for key in keys)


def _validate_authorization_artifact(path: Path = AUTHORIZATION_PATH) -> dict[str, Any]:
    if not path.exists():
        return {"pass": False, "reason": "authorization-artifact-missing", "path": str(path)}
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"pass": False, "reason": "authorization-artifact-invalid", "path": str(path)}
    passed = bool(
        state.get("decision") == "C2_LOCAL_VALIDATION_AUTHORIZED"
        and state.get("local_validation_authorized") is True
        and state.get("C3_locked") is True
        and state.get("full_experiment_authorized") is False
        and int(state.get("checks_passed") or 0) == int(state.get("checks_total") or -1) == 7
        and state.get("old_b9_formal_method_reopened") is False
    )
    return {
        "pass": passed,
        "reason": "authorized" if passed else "authorization-artifact-does-not-authorize-c2",
        "path": str(path),
        "sha256": _sha(path),
        "decision": state.get("decision"),
        "code_commit": state.get("code_commit"),
    }


def _validate_runtime(contract: dict[str, Any], parent_root: Path, model_path: Path) -> dict[str, Any]:
    import torch
    import transformers
    import textworld

    runtime = contract["runtime"]
    adapter_path = Path(__file__).with_name("p0_alfworld_adapter.py")
    parent_manifest = json.loads((parent_root / "full-support-table" / "manifest.json").read_text(encoding="utf-8"))
    provenance_path = Path(runtime["provenance_authority_path"])
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    provenance_regeneration = provenance.get("deterministic_nonzero_regeneration") or {}
    provenance_gpu = str(provenance_regeneration.get("gpu_uuid") or "")
    provenance_model = str(provenance_regeneration.get("model_path") or "")
    checks = {
        "python_executable": str(Path(sys.executable).resolve()) == str(Path(runtime["python"]).resolve()),
        "python_version": sys.version.split()[0] == runtime["python_version"],
        "torch_version": str(torch.__version__) == runtime["torch_version"],
        "transformers_version": str(transformers.__version__) == runtime["transformers_version"],
        "textworld_version": str(textworld.__version__) == runtime["textworld_version"],
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES", "") == runtime["gpu_uuid"],
        "adapter_sha256": _sha(adapter_path) == runtime["adapter_sha256"],
        "model_config_sha256": _sha(model_path / "config.json") == runtime["model_config_sha256"],
        "model_index_sha256": _sha(model_path / "model.safetensors.index.json") == runtime["model_index_sha256"],
        "parent_main_sha256": _sha(parent_root / "full-support-table" / "main_table.csv") == "eb861663351041e1f1a297b6791c7d31b4ba18285c3a13f0603d5d80c09b324f",
        "parent_raw_sha256": _sha(parent_root / "full-support-table" / "raw-traces.jsonl") == "45d9954a14f370936b5e1129f985130f4b9ef2b742e72a4c6e1e01bc068b1fbf",
        "parent_manifest_gpu_uuid": str(parent_manifest.get("gpu_uuid") or "") == runtime["gpu_uuid"],
        "provenance_authority_sha256": _sha(provenance_path) == runtime["provenance_authority_sha256"],
        "provenance_recovery_gpu_uuid": provenance_gpu == runtime["provenance_authority_expected_gpu_uuid"],
        "provenance_recovery_model_path": provenance_model == runtime["provenance_authority_expected_model_path"],
    }
    return {
        "pass": all(checks.values()),
        "checks": checks,
        "observed": {
            "python": sys.executable,
            "python_version": sys.version.split()[0],
            "torch": str(torch.__version__),
            "transformers": str(transformers.__version__),
            "textworld": str(textworld.__version__),
            "CUDA_VISIBLE_DEVICES": os.environ.get("CUDA_VISIBLE_DEVICES", ""),
            "parent_manifest_gpu_uuid": parent_manifest.get("gpu_uuid"),
            "provenance_authority_path": str(provenance_path),
            "provenance_recovery_gpu_uuid": provenance_gpu,
            "provenance_recovery_model_path": provenance_model,
        },
    }


def adjudicate_c2_outcomes(contract: dict[str, Any], valid_units: int, outcome_rows: list[dict[str, Any]]) -> dict[str, Any]:
    gate = contract["frozen_gate"]["go"]
    nonzero = sum(bool(row["nonzero_tau"]) for row in outcome_rows)
    concordant = sum(bool(row["parent_sign_concordant"]) for row in outcome_rows)
    flip_memory = str(gate["sign_flip_memory_id"])
    expected = {str(k): int(v) for k, v in gate["required_context_parent_signs"].items()}
    flip_rows = [row for row in outcome_rows if row["memory_id"] == flip_memory]
    flip_observed = {row["target_family"]: _sign(int(row["tau_A"])) for row in flip_rows}
    sign_reversal = bool(
        set(flip_observed) == set(expected)
        and all(flip_observed[family] == _sign(delta) for family, delta in expected.items())
    )
    go = bool(
        valid_units == int(gate["valid_units"])
        and nonzero >= int(gate["minimum_nonzero_tau_units"])
        and concordant >= int(gate["minimum_parent_sign_concordant_units"])
        and sign_reversal
    )
    return {
        "decision": "C2_GO_RETURN_TO_PAPER_ADJUDICATION" if go else "C2_STOP_CONTROLLED_ACTION_MECHANISM_NOT_SUPPORTED",
        "metrics": {
            "valid_units": valid_units,
            "nonzero_tau_units": nonzero,
            "parent_sign_concordant_units": concordant,
            "parent_sign_concordance_role": gate.get("parent_sign_concordance_role", "diagnostic-only"),
            "same_memory_cross_context_sign_reversal": sign_reversal,
            "sign_flip_memory_id": flip_memory,
            "sign_flip_expected_parent_signs": {k: _sign(v) for k, v in expected.items()},
            "sign_flip_observed_tau_signs": flip_observed,
        },
    }


def run_c2_local(
    *,
    output_dir: Path,
    model_path: Path,
    parent_root: Path,
    alfworld_config: Path,
) -> dict[str, Any]:
    authorization = _validate_authorization_artifact()
    if not authorization["pass"]:
        raise RuntimeError(f"C2 local validation is locked: {authorization['reason']}")
    contract = build_c2_contract()
    output_dir.mkdir(parents=True, exist_ok=True)
    contract_path = output_dir / "frozen-contract.json"
    if contract_path.exists():
        existing = json.loads(contract_path.read_text(encoding="utf-8"))
        if _semantic_contract(existing) != _semantic_contract(contract):
            raise RuntimeError("refusing to reuse C2 output directory with a changed scientific contract")
        contract = existing
    else:
        _atomic_json(contract_path, contract)

    lock_path = output_dir / ".c2.lock"
    with lock_path.open("a+", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        decision_path = output_dir / "decision.json"
        if decision_path.exists():
            return json.loads(decision_path.read_text(encoding="utf-8"))

        runtime_check = _validate_runtime(contract, parent_root, model_path)
        runtime_check["authorization"] = authorization
        _atomic_json(output_dir / "runtime-check.json", runtime_check)
        if not runtime_check["pass"]:
            result = {
                "schema_version": "1.0",
                "decision": "C2_RUNTIME_BLOCK",
                "runtime_check": runtime_check,
                "C3_locked": True,
                "full_experiment_authorized": False,
            }
            _atomic_json(decision_path, result)
            return result

        main, raw = _load_parent(parent_root)
        inventory = json.loads((Path(__file__).with_name("paper_first_c2_support_inventory_20260812.json")).read_text(encoding="utf-8"))
        inv = {str(row["unit_id"]): row for row in inventory["units"]}
        strict_ids = list(contract["strict_units"])
        config = load_config(alfworld_config)
        config.setdefault("general", {})["save_path"] = str(output_dir / "alfworld-runtime")
        try:
            policy = HFAdmissiblePolicy(model_path, policy_mode="react-family")
        except Exception as error:
            runtime_failure = {
                "schema_version": "1.0",
                "generated_at": _now(),
                "paper_id": contract["paper_id"],
                "stage": "C2-model-load-before-branch-outcomes",
                "error_type": type(error).__name__,
                "error": str(error),
                "scientific_result_available": False,
                "outcome_opened": False,
                "tau_A_computed": False,
                "next_action": "retry the identical frozen contract only when the exact matched-hardware GPU is free",
            }
            _atomic_json(output_dir / "runtime-failure.json", runtime_failure)
            raise
        runner = ALFWorldGameRunner(config)
        max_steps = int(contract["runtime"]["max_total_steps"])
        raw_path = output_dir / "branch-runs.jsonl"
        if raw_path.exists() and raw_path.stat().st_size:
            raise RuntimeError("refusing to append to a partial C2 branch run")

        unit_runs: dict[str, dict[str, Any]] = {}
        for index, unit_id in enumerate(strict_ids, start=1):
            row = inv[unit_id]
            parent = main[unit_id]
            retrieved = raw[(unit_id, "retrieved")]
            placebo = raw[(unit_id, "placebo")]
            idx = int(row["divergence_index"])
            r_actions = [str(x) for x in retrieved["actions"]]
            p_actions = [str(x) for x in placebo["actions"]]
            prefix = r_actions[:idx]
            if prefix != p_actions[:idx]:
                raise RuntimeError(f"{unit_id}: retrieved/placebo prefix mismatch")
            A1 = str(row["retrieved_action"])
            A0 = str(row["placebo_action"])
            if idx >= len(r_actions) or idx >= len(p_actions) or r_actions[idx] != A1 or p_actions[idx] != A0:
                raise RuntimeError(f"{unit_id}: frozen first-divergence action mismatch")
            task_path = str(parent["target_task_id"])
            target_family = str(parent["target_family"])
            runs: dict[str, list[dict[str, Any]]] = {"A0": [], "A1": []}
            for arm, action in (("A0", A0), ("A1", A1)):
                for repeat in (0, 1):
                    trace = _run_forced_branch(
                        runner,
                        policy,
                        task_path=task_path,
                        target_family=target_family,
                        prefix=prefix,
                        forced_action=action,
                        max_total_steps=max_steps,
                    )
                    stored = {
                        "unit_id": unit_id,
                        "unit_index": index,
                        "arm": arm,
                        "repeat": repeat,
                        "memory_id": row["memory_id"],
                        "source_family": row["source_family"],
                        "target_family": target_family,
                        "parent_controlled_delta": int(row["controlled_delta"]),
                        "divergence_index": idx,
                        "forced_action": action,
                        "trace": trace,
                    }
                    runs[arm].append(stored)
                    _append_jsonl(raw_path, stored)
            unit_runs[unit_id] = {
                "inventory": row,
                "parent": parent,
                "A0": runs["A0"],
                "A1": runs["A1"],
            }
            _atomic_json(output_dir / "progress.json", {
                "stage": "collect-repeated-controlled-action-branches",
                "completed_units": index,
                "total_units": len(strict_ids),
                "model_usage": policy.usage_snapshot(),
            })

        precheck_rows: list[dict[str, Any]] = []
        for unit_id in strict_ids:
            bundle = unit_runs[unit_id]
            a0 = [r["trace"] for r in bundle["A0"]]
            a1 = [r["trace"] for r in bundle["A1"]]
            branchpoint_same = len({r["branchpoint_sha256"] for r in a0 + a1}) == 1
            a0_repeat_equal = _repeat_equal(a0[0], a0[1])
            a1_repeat_equal = _repeat_equal(a1[0], a1[1])
            support = all(
                r["every_action_admissible"] and r["forced_action_admissible"] and r["post_forced_has_support"]
                for r in a0 + a1
            )
            valid = bool(branchpoint_same and a0_repeat_equal and a1_repeat_equal and support)
            precheck_rows.append({
                "unit_id": unit_id,
                "branchpoint_same_all_four_runs": branchpoint_same,
                "A0_same_action_null_repeat_equal": a0_repeat_equal,
                "A1_same_action_null_repeat_equal": a1_repeat_equal,
                "pi0_support_all_four_runs": support,
                "valid": valid,
            })
        valid_units = sum(bool(row["valid"]) for row in precheck_rows)
        precheck = {
            "schema_version": "1.0",
            "valid_units": valid_units,
            "required_valid_units": 10,
            "pass": valid_units == 10,
            "units": precheck_rows,
            "scientific_role": "same-action null and pi0 support gate; tau_A aggregation is forbidden unless pass=true",
        }
        _atomic_json(output_dir / "precheck.json", precheck)
        if not precheck["pass"]:
            result = {
                "schema_version": "1.0",
                "generated_at": _now(),
                "paper_id": contract["paper_id"],
                "decision": "C2_STOP_PRECHECK_FAILED",
                "precheck": {"valid_units": valid_units, "required": 10},
                "C3_locked": True,
                "full_experiment_authorized": False,
                "next_action": "stop or redesign the controlled-action estimand; do not inspect a transport certificate",
            }
            _atomic_json(decision_path, result)
            return result

        outcome_rows: list[dict[str, Any]] = []
        for unit_id in strict_ids:
            bundle = unit_runs[unit_id]
            y0 = int(bundle["A0"][0]["trace"]["success"])
            y1 = int(bundle["A1"][0]["trace"]["success"])
            tau = y1 - y0
            parent_delta = int(bundle["inventory"]["controlled_delta"])
            outcome_rows.append({
                "unit_id": unit_id,
                "memory_id": bundle["inventory"]["memory_id"],
                "source_family": bundle["inventory"]["source_family"],
                "target_family": bundle["inventory"]["target_family"],
                "parent_controlled_delta": parent_delta,
                "A0_success": y0,
                "A1_success": y1,
                "tau_A": tau,
                "nonzero_tau": tau != 0,
                "parent_sign_concordant": _sign(tau) == _sign(parent_delta),
            })
        adjudication = adjudicate_c2_outcomes(contract, valid_units, outcome_rows)
        gate = contract["frozen_gate"]["go"]
        result = {
            "schema_version": "1.0",
            "generated_at": _now(),
            "paper_id": contract["paper_id"],
            "decision": adjudication["decision"],
            "metrics": adjudication["metrics"],
            "frozen_gate": gate,
            "outcomes": outcome_rows,
            "model_usage": policy.usage_snapshot(),
            "C3_locked": True,
            "full_experiment_authorized": False,
            "next_action": (
                "return to paper-design/AI adjudication; do not train the C3 certificate yet"
                if adjudication["decision"] == "C2_GO_RETURN_TO_PAPER_ADJUDICATION"
                else "stop or redesign the paper mechanism; no C3/full experiment"
            ),
        }
        _atomic_json(decision_path, result)
        return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Paper-first C2 local controlled-action falsifier.")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--parent-root", type=Path, required=True)
    parser.add_argument("--alfworld-config", type=Path, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(json.dumps(run_c2_local(output_dir=args.output_dir, model_path=args.model_path, parent_root=args.parent_root, alfworld_config=args.alfworld_config), ensure_ascii=False, indent=2))
