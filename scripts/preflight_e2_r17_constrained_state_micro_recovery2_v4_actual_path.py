#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_e2_r17_constrained_state_micro_recovery2 import create_state_receipt
from scripts.run_e2_r17_e1_a_pool_support import validate_runtime as validate_actor_runtime

STATUS = "PASS_RECOVERY2_V4_ACTUAL_ACTOR_PATH_4_OF_4_ZERO_PROVIDER"
ARMS = ("g0_base", "g1_verify", "g2_complete", "g3_complete_recover")
TASK_ID = "r17-b4-ska-p4"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def req(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--preflight-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    req(not args.output.exists(), "actual-path preflight output already exists")
    req(not args.preflight_root.exists(), "actual-path preflight root already exists")
    contract = load(args.contract)
    authorization = load(args.authorization)
    contract_sha = sha(args.contract)
    authorization_sha = sha(args.authorization)
    req(authorization.get("contract_sha256") == contract_sha, "authorization/contract drift")
    raw_gate = str((contract.get("recovery2") or {}).get("quota_reset_not_before") or "")
    gate = datetime.fromisoformat(raw_gate)
    req(gate.tzinfo is not None, "quota reset gate must be timezone-aware")
    now = datetime.now(gate.tzinfo)
    req(now >= gate, f"actual-path preflight cannot run before {raw_gate}")
    req((authorization.get("execution_scope") or {}).get("execution_not_before") == raw_gate, "authorization not-before drift")

    actor_python, actor_env = validate_actor_runtime({"runtime": contract["actor_runtime"]})
    actor_env["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
    states = {row["arm"]: row for row in contract["states"]}
    req(tuple(states) == ARMS, "state order drift")
    identity = ROOT / contract["model_identity"]["path"]
    args.preflight_root.mkdir(parents=True, exist_ok=False)
    rows: list[dict[str, Any]] = []

    for arm in ARMS:
        arm_root = args.preflight_root / arm
        receipt = None
        if arm != "g0_base":
            receipt = create_state_receipt(args.preflight_root, arm, states[arm], contract_sha, authorization_sha)
        skill_path = Path(states[arm]["skill_path"])
        skill_dir = str(skill_path.parent if arm == "g0_base" else (ROOT / skill_path).resolve().parent)
        output = arm_root / "pre-provider-stop.json"
        ledger = arm_root / "provider_budget.sqlite3"
        command = [
            str(actor_python),
            str(ROOT / "scripts/run_e2_r17_actor_pool_constrained_state_micro.py"),
            "--env-file", contract["env_file"],
            "--suite-root", contract["suite"]["root"],
            "--mindmemos-root", contract["mindmemos"]["root"],
            "--run-root", str(arm_root / "actor"),
            "--identity", str(identity),
            "--authorization", str(args.authorization.resolve()),
            "--skill-source", skill_dir,
            "--mode", "e1",
            "--model", contract["actor"]["requested_model"],
            "--task-id", TASK_ID,
            "--k", "1",
            "--prefix-ks", "1",
            "--max-turns", str(contract["actor"]["max_turns"]),
            "--max-output-tokens", str(contract["actor"]["max_output_tokens"]),
            "--concurrency", "1",
            "--provider-budget-ledger", str(ledger),
            "--provider-total-call-limit", "123",
            "--provider-per-unit-call-limit", "11",
            "--output", str(output),
            "--stop-before-provider-io",
        ]
        if receipt is not None:
            command += ["--updater-receipt", str(receipt)]
        completed = subprocess.run(command, cwd=ROOT, env=actor_env, text=True, capture_output=True, check=False)
        req(completed.returncode == 0, f"actual-path actor preflight failed {arm}: {completed.stderr[-1600:]}")
        req(output.is_file(), f"actual-path output missing {arm}")
        payload = load(output)
        req(payload.get("status") == "STOPPED_IMMEDIATELY_BEFORE_PROVIDER_IO", f"actor did not stop before provider I/O {arm}")
        req(payload.get("provider_calls") == 0 and payload.get("provider_claims") == 0, f"preflight touched provider {arm}")
        rows.append({
            "arm": arm,
            "status": payload["status"],
            "provider_calls": 0,
            "provider_claims": 0,
            "receipt_mode": "none_initial_skill" if receipt is None else "deterministic_bound_receipt",
            "skill_pre_sha256": states[arm]["skill_sha256"],
            "artifact_path": str(output),
            "artifact_sha256": sha(output),
        })

    result = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-constrained-state-micro-recovery2-v4-actual-path-preflight",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": STATUS,
        "contract_sha256": contract_sha,
        "authorization_sha256": authorization_sha,
        "task_id": TASK_ID,
        "arms": rows,
        "provider_calls": 0,
        "provider_claims": 0,
        "scientific_outcomes_read": False,
        "partial_effect_read": False,
        "remaining_execution_order_sha256": contract["recovery2"]["remaining_execution_order_sha256"],
        "execution_not_before": raw_gate,
        "next_gate": "EXECUTE_RECOVERY2_V4_EXACT_27_UNIT_SEQUENCE",
    }
    atomic(args.output, result)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
