#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_repair2_manifest import validate_quarantine
from research_pipeline.e2_r17_repair2_v3_manifest import (
    validate_v3_compatibility_manifest,
    validate_valid_rows_v3,
)
from scripts.run_e2_r17_deepseek_v2_repair2_continuation_v3 import (
    validate_contract_auth,
)
from scripts.run_e2_r17_e1_a_pool_support import validate_runtime as validate_actor_runtime
from scripts.run_e2_r17_e1_b_transition_runtime_pilot import atomic_json, load_json, require, sha_file


def process_matches() -> list[str]:
    result = subprocess.run(
        ["ps", "-eo", "pid=,comm=,args="],
        capture_output=True,
        text=True,
        check=True,
    )
    matches = []
    for line in result.stdout.splitlines():
        fields = line.strip().split(None, 2)
        if len(fields) != 3:
            continue
        pid, command, arguments = fields
        if not command.startswith("python"):
            continue
        if pid == str(os.getpid()):
            continue
        if (
            "run_e2_r17_deepseek_v2_repair2_continuation_v3.py" in arguments
            or "run_e2_r17_actor_pool_repair2_v3.py" in arguments
        ):
            matches.append(line)
    return matches


def make_fixture(
    root: Path,
    *,
    arm: str,
    initial_skill: Path,
    contract_sha: str,
    authorization_sha: str,
) -> tuple[Path, Path]:
    skill_dir = root / "fixtures" / arm / "skill_post"
    skill_dir.mkdir(parents=True, exist_ok=False)
    skill_path = skill_dir / "SKILL.md"
    shutil.copyfile(initial_skill, skill_path)
    receipt_path = root / "fixtures" / arm / "update_receipt.json"
    atomic_json(
        receipt_path,
        {
            "schema_version": "1.0",
            "artifact_type": "repair2-v3-preflight-only-updater-receipt-fixture",
            "status": "COMPLETED",
            "contract_sha256": contract_sha,
            "authorization_sha256": authorization_sha,
            "skill_post_path": str(skill_path),
            "skill_post_sha256": sha_file(skill_path),
            "provider_calls": 0,
            "provider_io": False,
            "scientific_learned_state": False,
        },
    )
    return skill_dir, receipt_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), f"refusing to overwrite preflight: {args.output}")

    contract, authorization = validate_contract_auth(args.contract, args.authorization)
    contract_sha = sha_file(args.contract)
    authorization_sha = sha_file(args.authorization)
    run_root = Path(contract["run_root"])
    require(not run_root.exists(), "V3 formal run root must not exist before authorization preflight")
    require(process_matches() == [], "V3 runner/actor process already active")

    repair1 = contract["repair1_parent"]
    m1 = contract["repair2_m1_parent"]
    compatibility = contract["compatibility_manifest"]
    rows = validate_v3_compatibility_manifest(
        path=ROOT / compatibility["path"],
        expected_sha=compatibility["sha256"],
        repair1_contract_sha=repair1["contract_sha256"],
        repair1_authorization_sha=repair1["authorization_sha256"],
        m1_contract_sha=m1["contract_sha256"],
        m1_authorization_sha=m1["authorization_sha256"],
        m1_pass_path=ROOT / m1["pass_path"],
        m1_pass_sha=m1["pass_sha256"],
        heldout_task_ids=contract["heldout"]["task_ids"],
    )
    quarantine_item = contract["technical_quarantine"]
    quarantine = validate_quarantine(ROOT / quarantine_item["path"], quarantine_item["sha256"])
    validate_valid_rows_v3(
        rows,
        streams=contract["streams"],
        quarantine=quarantine,
        require_complete=False,
    )
    require(len(rows) == 15, "V3 inherited prefix is not exactly 15 pairs")
    require(sum(row["source"] == "repair1_inherited" for row in rows) == 14, "Repair1 prefix count drift")
    require(sum(row["source"] == "repair2_m1_recovered" for row in rows) == 1, "M1 recovered count drift")
    require(authorization.get("partial_effect_read") is False, "authorization outcome boundary drift")

    actor_python, actor_env = validate_actor_runtime({"runtime": contract["actor_runtime"]})
    actor_env["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
    initial_skill = Path(contract["initial_skill"]["path"])
    require(initial_skill.is_file() and sha_file(initial_skill) == contract["initial_skill"]["sha256"], "initial skill drift")

    results: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="e2-r17-repair2-v3-preflight-") as temp_name:
        temp_root = Path(temp_name)
        fixtures = {
            arm: make_fixture(
                temp_root,
                arm=arm,
                initial_skill=initial_skill,
                contract_sha=contract_sha,
                authorization_sha=authorization_sha,
            )
            for arm in ("win_c", "mrw")
        }
        for arm in ("win_c", "mrw"):
            skill_dir, receipt_path = fixtures[arm]
            for task_id in contract["heldout"]["task_ids"]:
                unit_root = temp_root / "actor_units" / arm / task_id
                output = unit_root / "pre_provider_stop.json"
                ledger = unit_root / "provider_budget.sqlite3"
                command = [
                    str(actor_python),
                    str(ROOT / "scripts/run_e2_r17_actor_pool_repair2_v3.py"),
                    "--env-file", contract["env_file"],
                    "--suite-root", contract["suite"]["root"],
                    "--mindmemos-root", contract["mindmemos"]["root"],
                    "--run-root", str(unit_root / "run"),
                    "--identity", str(ROOT / contract["model_identity"]["path"]),
                    "--authorization", str(args.authorization),
                    "--skill-source", str(skill_dir),
                    "--updater-receipt", str(receipt_path),
                    "--mode", "e1",
                    "--model", contract["actor"]["requested_model"],
                    "--task-id", task_id,
                    "--k", "1",
                    "--prefix-ks", "1",
                    "--max-turns", str(contract["actor"]["max_turns"]),
                    "--max-output-tokens", str(contract["actor"]["max_output_tokens"]),
                    "--concurrency", "1",
                    "--provider-budget-ledger", str(ledger),
                    "--provider-total-call-limit", str(contract["budget"]["max_provider_calls_per_state"]),
                    "--provider-per-unit-call-limit", str(contract["budget"]["max_provider_calls_per_unit"]),
                    "--stop-before-provider-io",
                    "--output", str(output),
                ]
                completed = subprocess.run(command, cwd=ROOT, env=actor_env, capture_output=True, text=True)
                require(
                    completed.returncode == 0,
                    f"actual V3 actor authorization path failed: {arm}/{task_id}: {completed.stderr[-2000:]}",
                )
                payload = load_json(output)
                require(payload.get("status") == "STOPPED_IMMEDIATELY_BEFORE_PROVIDER_IO", "actor did not stop at provider boundary")
                require(payload.get("provider_claims") == 0 and payload.get("provider_calls") == 0, "preflight touched provider")
                require(payload.get("contract_sha256") == contract_sha, "actor preflight contract binding drift")
                require(payload.get("authorization_sha256") == authorization_sha, "actor preflight authorization binding drift")
                results.append(
                    {
                        "arm": arm,
                        "task_id": task_id,
                        "status": "PASS",
                        "provider_claims": 0,
                        "provider_calls": 0,
                    }
                )

    require(len(results) == 36, "V3 actor-path preflight cardinality drift")
    require(not run_root.exists(), "V3 formal run root appeared during preflight")
    require(process_matches() == [], "V3 process remained after preflight")
    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-deepseek-v2-repair2-v3-frozen-preflight-adjudication",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "PREFLIGHT_PASS_REPAIR2_CONTINUATION_V3",
        "contract_sha256": contract_sha,
        "authorization_sha256": authorization_sha,
        "inherited_pairs": 15,
        "repair1_inherited_pairs": 14,
        "repair2_m1_recovered_pairs": 1,
        "remaining_fresh_pairs": 33,
        "remaining_new_learned_states": 66,
        "remaining_heldout_units": 1188,
        "actual_actor_authorization_path": {
            "passed": len(results),
            "expected": 36,
            "results": results,
            "provider_claims": 0,
            "provider_calls": 0,
        },
        "run_root_absent": True,
        "active_v3_processes": 0,
        "partial_effect_read": False,
        "analyzer_run": False,
        "provider_io": False,
        "authority": {
            "launch_v3": False,
            "read_partial_effect": False,
            "run_analyzer": False,
        },
    }
    atomic_json(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
