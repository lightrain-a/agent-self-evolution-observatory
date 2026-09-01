#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_provider_budget import ProviderBudgetLedger
from scripts.run_e2_r17_e1_a_pool_support import validate_runtime as validate_actor_runtime

ARMS = ("win_c", "mrw")
PREFLIGHT_STATUS = "PREFLIGHT_ONLY_E2_R17_DEEPSEEK_V2_REPAIR2_M1"
AUTHORIZED_STATUS = "AUTHORIZED_E2_R17_DEEPSEEK_V2_REPAIR2_M1_MEASUREMENT_ONLY"
CONTRACT_STATUS = "FROZEN_E2_R17_DEEPSEEK_V2_REPAIR2_M1_MEASUREMENT_ONLY"


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with temp.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def validate_contract_authorization(
    contract_path: Path,
    authorization_path: Path,
    *,
    execution: bool,
) -> tuple[dict[str, Any], dict[str, Any], str, str]:
    contract = load_json(contract_path)
    authorization = load_json(authorization_path)
    contract_sha = sha_file(contract_path)
    authorization_sha = sha_file(authorization_path)
    require(contract.get("status") == CONTRACT_STATUS, "M1 contract is not frozen")
    expected_status = AUTHORIZED_STATUS if execution else {PREFLIGHT_STATUS, AUTHORIZED_STATUS}
    if execution:
        require(authorization.get("status") == expected_status, "M1 execution authorization invalid")
    else:
        require(authorization.get("status") in expected_status, "M1 preflight authorization invalid")
    require(authorization.get("contract_sha256") == contract_sha, "M1 authorization/contract SHA mismatch")
    require(Path(str(authorization.get("contract_path") or "")).resolve() == contract_path.resolve(), "M1 contract path drift")

    authority = authorization.get("authority") or {}
    require(authority.get("measurement_only") is True, "measurement-only authority absent")
    require(authority.get("updater") is False, "M1 updater authority must be false")
    require(authority.get("analyzer") is False, "M1 analyzer authority must be false")
    require(authority.get("paper_promotion") is False, "M1 paper authority must be false")
    require(authority.get("public_benchmark") is False, "M1 public benchmark authority must be false")
    require(authority.get("scientific_experiment") is execution, "M1 scientific authority/status mismatch")

    scope = authorization.get("execution_scope") or {}
    tasks = [str(value) for value in contract["heldout"]["task_ids"]]
    require(len(tasks) == 18 and scope.get("allowed_task_ids") == tasks, "M1 exact 18-task scope drift")
    require(scope.get("allowed_modes") == ["e1"] and int(scope.get("exact_k")) == 1, "M1 mode/K drift")
    require(scope.get("required_resolved_model") == contract["actor"]["resolved_model"], "M1 model binding drift")
    require(scope.get("identity_artifact_sha256") == contract["model_identity"]["sha256"], "M1 identity binding drift")
    require(scope.get("learned_states") == contract["learned_states"], "M1 learned-state scope drift")
    budget = scope.get("provider_budget") or {}
    require(budget.get("required") is True, "M1 provider budget required")
    require(int(budget.get("total_limit")) == 180 and int(budget.get("per_unit_limit")) == 10, "M1 actor-only budget drift")

    require(contract["authority"]["updater"] is False and contract["authority"]["analyzer"] is False, "M1 contract authority drift")
    require(contract["measurement"]["new_updater_calls"] == 0, "M1 new updater calls must be zero")
    require(contract["measurement"]["replayed_updater_calls"] == 0, "M1 replayed updater calls must be zero")
    require(contract["measurement"]["measurement_states"] == 2, "M1 must bind exactly two measurement states")
    require(contract["measurement"]["heldout_evaluations"] == 36, "M1 must bind exactly 36 heldout evaluations")
    require(contract["measurement"]["partial_effect_read"] is False, "M1 partial effect must remain sealed")
    require(len(contract["learned_states"]) == 2, "M1 must bind exactly two learned states")

    parent = authorization.get("parent_repair2_provenance") or {}
    require(parent == contract["parent_repair2_provenance"], "M1 parent provenance drift")
    for key in ("contract", "authorization"):
        path = Path(parent[f"{key}_path"])
        require(path.is_file() and sha_file(path) == parent[f"{key}_sha256"], f"parent Repair2 {key} drift")

    for row in contract["learned_states"]:
        skill = Path(row["skill_post_path"])
        receipt = Path(row["update_receipt_path"])
        require(skill.is_file() and sha_file(skill) == row["skill_post_sha256"], f"learned skill drift: {row['arm']}")
        require(receipt.is_file() and sha_file(receipt) == row["update_receipt_sha256"], f"updater receipt drift: {row['arm']}")
        completed = Path(row["update_completed_path"])
        require(completed.is_file() and sha_file(completed) == row["update_completed_sha256"], f"update checkpoint drift: {row['arm']}")
        completed_payload = load_json(completed)
        require(completed_payload.get("status") == "COMPLETED", f"update checkpoint incomplete: {row['arm']}")
        require(completed_payload.get("arm") == row["arm"], f"update checkpoint arm drift: {row['arm']}")
        require(completed_payload.get("skill_post_sha256") == row["skill_post_sha256"], f"update checkpoint skill drift: {row['arm']}")
        require(completed_payload.get("update_receipt_sha256") == row["update_receipt_sha256"], f"update checkpoint receipt drift: {row['arm']}")
        payload = load_json(receipt)
        require(payload.get("status") == "COMPLETED", f"updater receipt incomplete: {row['arm']}")
        require(Path(payload["skill_post_path"]).resolve() == skill.resolve(), f"receipt skill path drift: {row['arm']}")
        require(payload.get("skill_post_sha256") == row["skill_post_sha256"], f"receipt skill SHA drift: {row['arm']}")
        require(payload.get("contract_sha256") == parent["contract_sha256"], f"receipt parent contract drift: {row['arm']}")
        require(payload.get("authorization_sha256") == parent["authorization_sha256"], f"receipt parent auth drift: {row['arm']}")

    for label, binding in contract["bound_code"].items():
        path = ROOT / binding["path"]
        require(path.is_file() and sha_file(path) == binding["sha256"], f"bound code drift: {label}")
    return contract, authorization, contract_sha, authorization_sha


def actor_command(
    *,
    contract: dict[str, Any],
    authorization_path: Path,
    state: dict[str, Any],
    task_id: str,
    run_root: Path,
    ledger_path: Path,
    output_path: Path,
    actor_python: Path,
    preflight: bool,
) -> list[str]:
    command = [
        str(actor_python),
        str(ROOT / contract["bound_code"]["measurement_actor"]["path"]),
        "--env-file", contract["env_file"],
        "--suite-root", contract["suite"]["root"],
        "--mindmemos-root", contract["mindmemos"]["root"],
        "--run-root", str(run_root),
        "--identity", str(ROOT / contract["model_identity"]["path"]),
        "--authorization", str(authorization_path),
        "--skill-source", str(Path(state["skill_post_path"]).parent),
        "--updater-receipt", state["update_receipt_path"],
        "--mode", "e1",
        "--model", contract["actor"]["requested_model"],
        "--task-id", task_id,
        "--k", "1",
        "--prefix-ks", "1",
        "--max-turns", str(contract["actor"]["max_turns"]),
        "--max-output-tokens", str(contract["actor"]["max_output_tokens"]),
        "--concurrency", "1",
        "--provider-budget-ledger", str(ledger_path),
        "--provider-total-call-limit", "180",
        "--provider-per-unit-call-limit", "10",
        "--output", str(output_path),
    ]
    if preflight:
        command.append("--stop-before-provider-io")
    return command


def actor_runtime(contract: dict[str, Any]) -> tuple[Path, dict[str, str]]:
    python, env = validate_actor_runtime({"runtime": contract["actor_runtime"]})
    env["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
    return python, env


def run_preflight(args: argparse.Namespace) -> dict[str, Any]:
    contract, authorization, contract_sha, authorization_sha = validate_contract_authorization(
        args.contract, args.authorization, execution=False
    )
    require(not args.run_root.exists(), f"M1 preflight root already exists: {args.run_root}")
    args.run_root.mkdir(parents=True)
    actor_python, env = actor_runtime(contract)
    rows: list[dict[str, Any]] = []
    for state in contract["learned_states"]:
        for task_id in contract["heldout"]["task_ids"]:
            unit_root = args.run_root / state["arm"] / task_id
            output = unit_root / "pre_provider_stop.json"
            ledger = unit_root / "provider_budget.sqlite3"
            result = subprocess.run(
                actor_command(
                    contract=contract,
                    authorization_path=args.authorization,
                    state=state,
                    task_id=task_id,
                    run_root=unit_root / "actor",
                    ledger_path=ledger,
                    output_path=output,
                    actor_python=actor_python,
                    preflight=True,
                ),
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
            )
            if result.returncode != 0:
                failure = {
                    "status": "ACTUAL_ACTOR_AUTHORIZATION_PATH_PREFLIGHT_FAILURE",
                    "arm": state["arm"],
                    "task_id": task_id,
                    "returncode": result.returncode,
                    "stdout_tail": result.stdout[-4000:],
                    "stderr_tail": result.stderr[-4000:],
                    "provider_calls": 0,
                }
                atomic_json(args.run_root / "failure.json", failure)
                raise RuntimeError(f"M1 actual-path preflight failed: {state['arm']}/{task_id}")
            payload = load_json(output)
            require(payload.get("status") == "STOPPED_IMMEDIATELY_BEFORE_PROVIDER_IO", "actor did not stop at provider boundary")
            require(payload.get("provider_claims") == 0 and payload.get("provider_calls") == 0, "preflight touched provider budget")
            snapshot = ProviderBudgetLedger(
                path=ledger,
                contract_sha256=contract_sha,
                authorization_sha256=authorization_sha,
                total_limit=180,
                per_unit_limit=10,
                allow_create=False,
            ).snapshot()
            require(snapshot.total_claimed == 0, "preflight ledger contains provider claims")
            rows.append({
                "arm": state["arm"],
                "task_id": task_id,
                "status": payload["status"],
                "skill_post_sha256": state["skill_post_sha256"],
                "update_receipt_sha256": state["update_receipt_sha256"],
                "provider_claims": 0,
                "provider_calls": 0,
                "unit_receipt_path": str(output),
                "unit_receipt_sha256": sha_file(output),
            })
    require(len(rows) == 36, "M1 preflight cardinality drift")
    final = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-repair2-m1-actual-actor-authorization-path-preflight",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "PASS_ACTUAL_ACTOR_AUTHORIZATION_PATH_PREFLIGHT_36_OF_36",
        "contract_sha256": contract_sha,
        "authorization_sha256": authorization_sha,
        "measurement_states": 2,
        "heldout_combinations": 36,
        "provider_claims": 0,
        "provider_calls": 0,
        "partial_effect_read": False,
        "units": rows,
    }
    atomic_json(args.output, final)
    return final


def acquire_lock(path: Path, contract_sha: str, authorization_sha: str) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.write(fd, (json.dumps({
        "pid": os.getpid(),
        "pgid": os.getpgrp(),
        "contract_sha256": contract_sha,
        "authorization_sha256": authorization_sha,
        "exactly_once": True,
    }, sort_keys=True) + "\n").encode())
    os.fsync(fd)
    return fd


def run_execution(args: argparse.Namespace) -> dict[str, Any]:
    contract, authorization, contract_sha, authorization_sha = validate_contract_authorization(
        args.contract, args.authorization, execution=True
    )
    require(not args.run_root.exists(), f"M1 run root already exists: {args.run_root}")
    args.run_root.mkdir(parents=True)
    lock_fd = acquire_lock(args.run_root / ".exclusive.lock", contract_sha, authorization_sha)
    actor_python, env = actor_runtime(contract)
    start = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-repair2-m1-run-start-receipt",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "M1_RUN_START_WRITTEN_BEFORE_PROVIDER_IO",
        "pid": os.getpid(),
        "pgid": os.getpgrp(),
        "contract_sha256": contract_sha,
        "authorization_sha256": authorization_sha,
        "new_updater_calls": 0,
        "replayed_updater_calls": 0,
        "sealed_parent_updater_calls": 20,
        "measurement_states": 2,
        "heldout_evaluations": 36,
        "provider_claims_before_start": 0,
        "provider_calls_before_start": 0,
        "partial_effect_read": False,
        "analyzer_forbidden": True,
        "exactly_once": True,
    }
    atomic_json(args.run_root / "run-start-receipt.json", start)
    manifest = args.run_root / "checkpoints" / "completed_measurements.jsonl"
    completed = 0
    try:
        for state in contract["learned_states"]:
            state_root = args.run_root / "states" / state["arm"]
            ledger_path = state_root / "provider_budget.sqlite3"
            ledger = ProviderBudgetLedger(
                path=ledger_path,
                contract_sha256=contract_sha,
                authorization_sha256=authorization_sha,
                total_limit=180,
                per_unit_limit=10,
                allow_create=True,
            )
            for task_id in contract["heldout"]["task_ids"]:
                before = ledger.snapshot().total_claimed
                unit_root = state_root / "evaluation" / task_id
                output = unit_root / "evaluation_summary.json"
                result = subprocess.run(
                    actor_command(
                        contract=contract,
                        authorization_path=args.authorization,
                        state=state,
                        task_id=task_id,
                        run_root=unit_root,
                        ledger_path=ledger_path,
                        output_path=output,
                        actor_python=actor_python,
                        preflight=False,
                    ),
                    cwd=ROOT,
                    env=env,
                    text=True,
                    capture_output=True,
                )
                after = ledger.snapshot().total_claimed
                if result.returncode != 0:
                    classification = (
                        "AMBIGUOUS_PROVIDER_UNIT_NO_RETRY"
                        if after > before
                        else "PRE_PROVIDER_LOCAL_IMPLEMENTATION_FAILURE"
                    )
                    failure = {
                        "status": "STOP_AND_ADJUDICATE_REPAIR2_M1",
                        "classification": classification,
                        "arm": state["arm"],
                        "task_id": task_id,
                        "provider_claims_before": before,
                        "provider_claims_after": after,
                        "returncode": result.returncode,
                        "stdout_tail": result.stdout[-4000:],
                        "stderr_tail": result.stderr[-4000:],
                        "automatic_retry": False,
                        "partial_effect_read": False,
                    }
                    atomic_json(args.run_root / "failure.json", failure)
                    raise RuntimeError(f"M1 measurement stopped: {state['arm']}/{task_id}/{classification}")
                require(output.is_file(), "actor completed without sealed measurement summary")
                summary = load_json(output)
                require(summary.get("status") == "COMPLETED", "actor summary incomplete")
                require(summary.get("k") == 1, "actor summary K drift")
                require(summary.get("skill_pre_sha256") == state["skill_post_sha256"], "actor learned-state drift")
                require(summary.get("updater_receipt_sha256") == state["update_receipt_sha256"], "actor receipt drift")
                require(summary.get("tasks") == [{
                    "task_id": task_id,
                    "failure_family": summary["tasks"][0]["failure_family"],
                    "scores_withheld_from_measurement_summary": True,
                    "provider_calls": summary["tasks"][0]["provider_calls"],
                    "pools": summary["tasks"][0]["pools"],
                }], "measurement summary exposed or drifted task payload")
                row = {
                    "arm": state["arm"],
                    "task_id": task_id,
                    "summary_path": str(output),
                    "summary_sha256": sha_file(output),
                    "skill_post_sha256": state["skill_post_sha256"],
                    "update_receipt_sha256": state["update_receipt_sha256"],
                    "provider_claims_before": before,
                    "provider_claims_after": after,
                    "partial_effect_read": False,
                }
                append_jsonl(manifest, row)
                completed += 1
        require(completed == 36, "M1 completion cardinality drift")
        final = {
            "schema_version": "1.0",
            "artifact_type": "e2-r17-repair2-m1-measurement-recovery-summary",
            "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "status": "REPAIR2_M1_MEASUREMENT_RECOVERY_PASS",
            "contract_sha256": contract_sha,
            "authorization_sha256": authorization_sha,
            "new_updater_calls": 0,
            "replayed_updater_calls": 0,
            "measurement_states": 2,
            "heldout_evaluations": 36,
            "paired_units_after_recovery": 15,
            "learned_states_after_recovery": 30,
            "heldout_units_after_recovery": 540,
            "partial_effect_read": False,
            "analyzer_run": False,
            "next_state": "REPAIR2_CONTINUATION_V3_REQUIRED",
            "completed_measurement_manifest": str(manifest),
            "completed_measurement_manifest_sha256": sha_file(manifest),
        }
        atomic_json(args.output, final)
        return final
    finally:
        os.close(lock_fd)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--stage", choices=("actual-path-preflight", "execute"), required=True)
    args = parser.parse_args()
    result = run_preflight(args) if args.stage == "actual-path-preflight" else run_execution(args)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
