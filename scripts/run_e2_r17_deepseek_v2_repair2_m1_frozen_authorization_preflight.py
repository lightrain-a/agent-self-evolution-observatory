#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_provider_budget import ProviderBudgetLedger
import scripts.run_e2_r17_deepseek_v2_repair2_m1_measurement as base


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def validate_gate_bindings(authorization: dict[str, Any]) -> None:
    gates = authorization.get("gate_bindings") or {}
    for path_key, sha_key in (
        ("actual_actor_path_preflight_path", "actual_actor_path_preflight_sha256"),
        ("review_reparse_adjudication_path", "review_reparse_adjudication_sha256"),
    ):
        path = ROOT / str(gates.get(path_key) or "")
        require(path.is_file(), f"missing frozen gate: {path_key}")
        require(base.sha_file(path) == gates.get(sha_key), f"frozen gate SHA drift: {path_key}")
    source_root = ROOT / "generated/e2-r17-deepseek-v2-repair2-m1-review-20260831"
    for model, expected_sha in (gates.get("independent_review_source_sha256") or {}).items():
        path = source_root / f"{model}.json"
        require(path.is_file() and base.sha_file(path) == expected_sha, f"review source drift: {model}")
    require(gates.get("reviewers_pass") == "2/2", "independent review gate is not 2/2 PASS")
    require(gates.get("provider_generation_calls_for_reparse") == 0, "review reparse provider calls drift")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    contract, authorization, contract_sha, authorization_sha = base.validate_contract_authorization(
        args.contract, args.authorization, execution=True
    )
    validate_gate_bindings(authorization)
    require(not args.run_root.exists(), f"frozen authorization preflight root already exists: {args.run_root}")
    formal_root = Path((authorization.get("single_use") or {}).get("run_root") or "")
    require(formal_root.is_absolute() and not formal_root.exists(), "formal M1 execution root must remain absent")
    args.run_root.mkdir(parents=True)
    actor_python, env = base.actor_runtime(contract)
    rows: list[dict[str, Any]] = []

    for state in contract["learned_states"]:
        for task_id in contract["heldout"]["task_ids"]:
            unit_root = args.run_root / state["arm"] / task_id
            output = unit_root / "pre_provider_stop.json"
            ledger = unit_root / "provider_budget.sqlite3"
            result = subprocess.run(
                base.actor_command(
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
                    "status": "FROZEN_ACTUAL_ACTOR_AUTHORIZATION_PATH_PREFLIGHT_FAILURE",
                    "arm": state["arm"],
                    "task_id": task_id,
                    "returncode": result.returncode,
                    "stdout_tail": result.stdout[-4000:],
                    "stderr_tail": result.stderr[-4000:],
                    "provider_calls": 0,
                    "partial_effect_read": False,
                }
                base.atomic_json(args.run_root / "failure.json", failure)
                raise RuntimeError(f"frozen M1 actor preflight failed: {state['arm']}/{task_id}")
            payload = base.load_json(output)
            require(
                payload.get("status") == "STOPPED_IMMEDIATELY_BEFORE_PROVIDER_IO",
                "actor did not stop at provider boundary",
            )
            require(
                payload.get("provider_claims") == 0 and payload.get("provider_calls") == 0,
                "frozen preflight touched provider budget",
            )
            snapshot = ProviderBudgetLedger(
                path=ledger,
                contract_sha256=contract_sha,
                authorization_sha256=authorization_sha,
                total_limit=180,
                per_unit_limit=10,
                allow_create=False,
            ).snapshot()
            require(snapshot.total_claimed == 0, "frozen preflight ledger contains provider claims")
            rows.append({
                "arm": state["arm"],
                "task_id": task_id,
                "status": payload["status"],
                "skill_post_sha256": state["skill_post_sha256"],
                "update_receipt_sha256": state["update_receipt_sha256"],
                "provider_claims": 0,
                "provider_calls": 0,
                "unit_receipt_path": str(output),
                "unit_receipt_sha256": base.sha_file(output),
            })

    require(len(rows) == 36, "frozen M1 preflight cardinality drift")
    require(not formal_root.exists(), "formal M1 execution root appeared during frozen preflight")
    final = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-repair2-m1-frozen-actual-actor-authorization-path-preflight",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "PASS_FROZEN_ACTUAL_ACTOR_AUTHORIZATION_PATH_PREFLIGHT_36_OF_36",
        "contract_sha256": contract_sha,
        "authorization_sha256": authorization_sha,
        "measurement_states": 2,
        "heldout_combinations": 36,
        "provider_claims": 0,
        "provider_calls": 0,
        "new_updater_calls": 0,
        "replayed_updater_calls": 0,
        "analyzer_run": False,
        "partial_effect_read": False,
        "formal_execution_root_absent": True,
        "rows": rows,
    }
    base.atomic_json(args.output, final)
    print(json.dumps(final, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
