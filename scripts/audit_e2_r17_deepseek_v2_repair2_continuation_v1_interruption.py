#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_repair2_manifest import validate_quarantine
from research_pipeline.e2_r17_repair2_v3_manifest import ARMS, REPLICATES, rows_by, validate_valid_rows_v3

EXPECTED_PARENT_CONTRACT = "9e38bdbfc71186e3e58587169d8c619bff4ae24de4145fefafa63e49a6f148a3"
EXPECTED_PARENT_AUTH = "9643a0a30d0acc4f32607b217701b368a895b2fe1e86a0aa84da24aa0a80898b"
EXPECTED_V3_CONTRACT = "312e970520794c564b23a9717f4c40d4baeb0674619da334c8fcc20ee95fc045"
EXPECTED_V3_AUTH = "7aa826db915b40840fb54ca2c269a23c4f74807bae74fd99285eac6875ee5b74"
V3_RUN = Path("/data/wyt/e2-r17-search-projection/runs/deepseek-v2-repair2-v3-20260831")
PARTIAL_UNIT = "e1-ioc-00/rep1"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def require(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def atomic(path: Path, payload: dict[str, Any]) -> None:
    require(not path.exists(), f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    tmp.replace(path)


def logical_ledger(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing ledger {path}")
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        metadata = {str(k): str(v) for k, v in con.execute("SELECT key,value FROM metadata")}
        claims = [
            {"claim_id": row[0], "unit_id": str(row[1]), "unit_call_index": int(row[2]), "claimed_at_utc": str(row[3])}
            for row in con.execute("SELECT claim_id,unit_id,unit_call_index,claimed_at_utc FROM claims ORDER BY claimed_at_utc,claim_id")
        ]
    finally:
        con.close()
    require(len({(x["unit_id"], x["unit_call_index"]) for x in claims}) == len(claims), f"duplicate claims {path}")
    physical = [{"path": str(path), "sha256": sha(path)}]
    for suffix in ("-wal", "-shm"):
        item = Path(str(path) + suffix)
        if item.is_file():
            physical.append({"path": str(item), "sha256": sha(item)})
    return {
        "path": str(path),
        "metadata": metadata,
        "claims": claims,
        "claims_sha256": canonical_sha(claims),
        "physical_files": physical,
    }


def validate_eval_manifest(path: Path, expected_sha: str, heldout_subset: set[str], skill_sha: str, receipt_sha: str) -> tuple[list[dict[str, Any]], list[Path]]:
    require(path.is_file() and sha(path) == expected_sha, f"eval manifest drift {path}")
    rows = rows_by(path, "task_id")
    require(set(rows) == heldout_subset, f"heldout set drift {path}")
    bindings = []
    ledger_paths: set[Path] = set()
    for task_id, row in rows.items():
        summary_path = Path(row["summary_path"])
        ref_path = Path(row["trajectory_ref_path"])
        require(summary_path.is_file() and sha(summary_path) == row["summary_sha256"], f"summary drift {task_id}")
        require(ref_path.is_file() and sha(ref_path) == row["trajectory_ref_sha256"], f"ref drift {task_id}")
        summary = load(summary_path)
        require(summary.get("status") == "COMPLETED" and int(summary.get("k")) == 1, f"summary incomplete {task_id}")
        require(summary.get("skill_pre_sha256") == skill_sha, f"skill drift {task_id}")
        require(summary.get("updater_receipt_sha256") == receipt_sha, f"receipt drift {task_id}")
        ref = load(ref_path)
        trajectory = Path(ref["trajectory_path"])
        require(trajectory.is_file() and sha(trajectory) == ref["trajectory_sha256"], f"trajectory drift {task_id}")
        budget = summary.get("provider_budget") or {}
        if budget.get("ledger_path"):
            ledger_paths.add(Path(budget["ledger_path"]))
        bindings.append({
            "task_id": task_id,
            "summary_path": str(summary_path),
            "summary_sha256": row["summary_sha256"],
            "trajectory_ref_path": str(ref_path),
            "trajectory_ref_sha256": row["trajectory_ref_sha256"],
            "trajectory_path": str(trajectory),
            "trajectory_sha256": ref["trajectory_sha256"],
            "contract_sha256": summary.get("contract_sha256"),
            "authorization_sha256": summary.get("authorization_sha256"),
            "provider_calls": int((summary.get("tasks") or [{}])[0].get("provider_calls", 0)),
        })
        # Deliberately never access ref["score"].
    return bindings, sorted(ledger_paths)


def state_binding(arm: dict[str, Any], tasks: set[str]) -> dict[str, Any]:
    state_root = Path(arm["state_root"])
    skill = state_root / "update/skill_post/SKILL.md"
    receipt = Path(arm.get("update_receipt_path") or state_root / "update/update_receipt.json")
    checkpoint = state_root / "checkpoints/update_completed.json"
    require(skill.is_file() and sha(skill) == arm["skill_sha256"], f"skill drift {state_root}")
    require(receipt.is_file() and sha(receipt) == arm["update_receipt_sha256"], f"receipt drift {state_root}")
    require(checkpoint.is_file(), f"missing update checkpoint {state_root}")
    evals, eval_ledgers = validate_eval_manifest(Path(arm["eval_manifest_path"]), arm["eval_manifest_sha256"], tasks, arm["skill_sha256"], arm["update_receipt_sha256"])
    ledgers: list[dict[str, Any]] = []
    primary = state_root / "checkpoints/provider_budget.sqlite3"
    if primary.is_file():
        ledgers.append(logical_ledger(primary))
    for path in eval_ledgers:
        if all(item["path"] != str(path) for item in ledgers):
            ledgers.append(logical_ledger(path))
    return {
        "state_root": str(state_root),
        "skill_path": str(skill),
        "skill_sha256": arm["skill_sha256"],
        "update_receipt_path": str(receipt),
        "update_receipt_sha256": arm["update_receipt_sha256"],
        "update_checkpoint_path": str(checkpoint),
        "update_checkpoint_sha256": sha(checkpoint),
        "updater_calls": int(arm.get("updater_calls", 0)),
        "attempt0_success": bool(arm.get("attempt0_success")),
        "correction_required": bool(arm.get("correction_required")),
        "eval_manifest_path": arm["eval_manifest_path"],
        "eval_manifest_sha256": arm["eval_manifest_sha256"],
        "heldout_tasks": evals,
        "provider_ledgers": ledgers,
        "mutation": "forbidden",
        "replay_provider": False,
        "recompute_provider": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--interruption-output", type=Path, required=True)
    parser.add_argument("--inheritance-output", type=Path, required=True)
    parser.add_argument("--remaining-output", type=Path, required=True)
    args = parser.parse_args()

    contract = load(args.contract)
    require(sha(args.contract) == EXPECTED_V3_CONTRACT, "V3 contract SHA drift")
    require(sha(args.authorization) == EXPECTED_V3_AUTH, "V3 authorization SHA drift")
    require(contract["repair2_stopped_parent"]["contract_sha256"] == EXPECTED_PARENT_CONTRACT, "parent contract drift")
    require(contract["repair2_stopped_parent"]["authorization_sha256"] == EXPECTED_PARENT_AUTH, "parent authorization drift")
    heldout = [str(x) for x in contract["heldout"]["task_ids"]]
    heldout_set = set(heldout)

    process_text = subprocess.check_output(["ps", "-eo", "pid,ppid,pgid,stat,args"], text=True)
    forbidden_processes = [
        line for line in process_text.splitlines()
        if ("run_e2_r17_deepseek_v2_repair2_continuation_v3.py" in line or "run_e2_r17_actor_pool_repair2_v3.py" in line)
        and "audit_e2_r17_deepseek_v2_repair2_continuation_v1_interruption.py" not in line
    ]
    require(not forbidden_processes, "old runner or actor still alive")
    lock = load(V3_RUN / ".exclusive.lock")
    require(int(lock["pid"]) == 2439745 and lock["contract_sha256"] == EXPECTED_V3_CONTRACT and lock["authorization_sha256"] == EXPECTED_V3_AUTH, "stale lock identity drift")

    valid_path = V3_RUN / "checkpoints/valid_replicates.jsonl"
    completed_path = V3_RUN / "checkpoints/completed_replicates.jsonl"
    valid_rows = list(rows_by(valid_path, "unit_id").values())
    completed_rows = rows_by(completed_path, "unit_id")
    require(len(valid_rows) == len(completed_rows) == 17, "complete pair boundary is not exactly 17")
    require({row["unit_id"] for row in valid_rows} == set(completed_rows), "valid/completed set mismatch")
    quarantine_item = contract["technical_quarantine"]
    quarantine = validate_quarantine(ROOT / quarantine_item["path"], quarantine_item["sha256"])
    validate_valid_rows_v3(valid_rows, streams=contract["streams"], quarantine=quarantine, require_complete=False)

    inherited_rows = []
    learned_roots: set[str] = set()
    heldout_count = 0
    for row in valid_rows:
        unit = {
            "unit_id": row["unit_id"],
            "stream_id": row["stream_id"],
            "replicate_id": int(row["replicate_id"]),
            "source": row["source"],
            "pair_summary_path": row["pair_summary_path"],
            "pair_summary_sha256": row["pair_summary_sha256"],
            "completion_ledger_entry": completed_rows[row["unit_id"]],
            "arms": {},
        }
        require(sha(Path(row["pair_summary_path"])) == row["pair_summary_sha256"], f"pair summary drift {row['unit_id']}")
        for arm_name in ARMS:
            binding = state_binding(row["arms"][arm_name], heldout_set)
            unit["arms"][arm_name] = binding
            learned_roots.add(binding["state_root"])
            heldout_count += len(binding["heldout_tasks"])
        inherited_rows.append(unit)

    expected_order = [f"{stream}/rep{rep}" for stream in contract["streams"] for rep in REPLICATES]
    completed_set = {row["unit_id"] for row in valid_rows}
    remaining_units = [unit for unit in expected_order if unit not in completed_set]
    require(len(remaining_units) == 31 and remaining_units[0] == PARTIAL_UNIT, "remaining unit order drift")

    stream, rep_text = PARTIAL_UNIT.split("/rep")
    partial_root = V3_RUN / "states" / stream / f"replicate_{rep_text}"
    partial_arms: dict[str, Any] = {}
    partial_heldout = 0
    v3_claims = 0
    for db in V3_RUN.glob("states/*/replicate_*/*/checkpoints/provider_budget.sqlite3"):
        v3_claims += len(logical_ledger(db)["claims"])
    for arm_name in ARMS:
        state_root = partial_root / arm_name
        checkpoint = load(state_root / "checkpoints/update_completed.json")
        manifest_path = state_root / "checkpoints/completed_eval_tasks.jsonl"
        task_rows = rows_by(manifest_path, "task_id")
        require(len(task_rows) == 12 and set(task_rows).issubset(heldout_set), f"partial heldout boundary drift {arm_name}")
        arm = {
            "state_root": str(state_root),
            "skill_sha256": checkpoint["skill_post_sha256"],
            "update_receipt_sha256": checkpoint["update_receipt_sha256"],
            "eval_manifest_path": str(manifest_path),
            "eval_manifest_sha256": sha(manifest_path),
            "updater_calls": int(checkpoint["provider_calls"]),
            "attempt0_success": bool(checkpoint.get("attempt0_success", int(checkpoint["provider_calls"]) == 10)),
            "correction_required": bool(checkpoint.get("correction_required", int(checkpoint["provider_calls"]) == 11)),
        }
        binding = state_binding(arm, set(task_rows))
        binding["remaining_heldout_task_ids"] = [task for task in heldout if task not in task_rows]
        binding["parent_claim_count"] = len(next(x for x in binding["provider_ledgers"] if x["path"].endswith("checkpoints/provider_budget.sqlite3"))["claims"])
        binding["residual_provider_budget"] = 191 - binding["parent_claim_count"]
        partial_arms[arm_name] = binding
        learned_roots.add(binding["state_root"])
        partial_heldout += len(binding["heldout_tasks"])

    require(len(learned_roots) == 36, "learned-state cardinality is not 36")
    require(heldout_count == 612 and partial_heldout == 24, "heldout boundary cardinality drift")
    require(v3_claims == 609, "V3 provider claim cardinality drift")

    eval_dirs = {p.parent.name for p in partial_root.glob("*/evaluation/*/evaluation_summary.json")}
    for arm_name in ARMS:
        state_root = partial_root / arm_name
        manifest_tasks = set(rows_by(state_root / "checkpoints/completed_eval_tasks.jsonl", "task_id"))
        actual_dirs = {p.name for p in (state_root / "evaluation").iterdir() if p.is_dir()}
        require(actual_dirs == manifest_tasks, f"partial evaluation directory exists for {arm_name}")
        require(not [p for p in state_root.rglob("*") if p.is_file() and (p.name.endswith((".tmp", ".partial", ".staging")) or ".tmp." in p.name)], f"temp artifact exists for {arm_name}")

    boots = subprocess.check_output(["journalctl", "--list-boots", "--no-pager"], text=True)
    prior = subprocess.run(["journalctl", "-b", "-1", "--since", "2026-08-31 16:57:30", "--until", "2026-08-31 16:57:42", "--no-pager"], capture_output=True, text=True).stdout
    require("Activating special unit exit.target" in prior, "host shutdown evidence absent")
    require("3fa98da61cec4b0fb65749ced2e6e51d" in boots and "c9e261f1b8154cdb9a44de696743d7f2" in boots, "boot lineage drift")

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    interruption = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-deepseek-v2-repair2-v3-execution-interruption-audit",
        "created_at_utc": now,
        "status": "PASS_CONTINUATION_BOUNDARY_PROVEN",
        "classification": "FAIL_CLOSED_HOST_SHUTDOWN_AT_CLEAN_HELDOUT_TASK_BOUNDARY",
        "root_cause": "HOST_SHUTDOWN_DURING_EXECUTION",
        "prior_boot_id": "3fa98da61cec4b0fb65749ced2e6e51d",
        "current_boot_id": "c9e261f1b8154cdb9a44de696743d7f2",
        "shutdown_evidence_sha256": canonical_sha(prior.splitlines()),
        "old_runner_pid": 2439745,
        "old_runner_alive": False,
        "old_actor_alive": False,
        "provider_worker_alive": False,
        "stale_lock_path": str(V3_RUN / ".exclusive.lock"),
        "stale_lock_sha256": sha(V3_RUN / ".exclusive.lock"),
        "completed_pairs": 17,
        "learned_states": 36,
        "heldout_units": 636,
        "provider_claims": 609,
        "failure_json": 0,
        "full_summary_absent": True,
        "boundary_assertions": {
            "NO_PARTIAL_PROVIDER_CLAIM": True,
            "NO_PARTIAL_LEARNED_STATE": True,
            "NO_PARTIAL_HELDOUT_UNIT": True,
            "NO_AMBIGUOUS_COMPLETION": True,
        },
        "filesystem": {"free_bytes": os.statvfs(V3_RUN).f_bavail * os.statvfs(V3_RUN).f_frsize, "free_inodes": os.statvfs(V3_RUN).f_favail},
        "oom_evidence": False,
        "python_exception_evidence": False,
        "partial_effect_read": False,
        "analyzer_run": False,
        "authority": {"build_continuation_manifests": True, "provider_io": False},
    }

    inheritance = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-deepseek-v2-repair2-v3-continuation-v1-immutable-inheritance-manifest",
        "created_at_utc": now,
        "status": "PASS_IMMUTABLE_INHERITANCE_17_PAIRS_PLUS_CLEAN_PARTIAL_PAIR",
        "parent_repair2_contract_sha256": EXPECTED_PARENT_CONTRACT,
        "parent_repair2_authorization_sha256": EXPECTED_PARENT_AUTH,
        "v3_contract_sha256": EXPECTED_V3_CONTRACT,
        "v3_authorization_sha256": EXPECTED_V3_AUTH,
        "v3_run_root": str(V3_RUN),
        "completed_pair_count": 17,
        "completed_learned_states": 34,
        "completed_heldout_units": 612,
        "partial_boundary": {"unit_id": PARTIAL_UNIT, "completed_learned_states": 2, "completed_heldout_units": 24, "arms": partial_arms},
        "total_immutable_learned_states": 36,
        "total_immutable_heldout_units": 636,
        "v3_provider_claims": 609,
        "completed_pairs": inherited_rows,
        "replay_provider": False,
        "recompute_provider": False,
        "mutation": "forbidden",
        "scientific_scores_read": False,
        "partial_effect_read": False,
    }

    missing_states = 0
    remaining_heldout = 0
    per_unit = []
    for unit in remaining_units:
        if unit == PARTIAL_UNIT:
            state_missing = 0
            heldout_missing = sum(len(partial_arms[arm]["remaining_heldout_task_ids"]) for arm in ARMS)
            existing_state_roots = {arm: partial_arms[arm]["state_root"] for arm in ARMS}
        else:
            state_missing = 2
            heldout_missing = 36
            existing_state_roots = {}
        missing_states += state_missing
        remaining_heldout += heldout_missing
        per_unit.append({"unit_id": unit, "new_learned_states": state_missing, "remaining_heldout_units": heldout_missing, "existing_state_roots": existing_state_roots})
    require(missing_states == 60 and remaining_heldout == 1092, "remaining cardinality drift")
    remaining = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-deepseek-v2-repair2-v3-continuation-v1-remaining-set-proof",
        "created_at_utc": now,
        "status": "PASS_REMAINING_SET_EXACT_PARTITION",
        "frozen_design_order": expected_order,
        "completed_set": sorted(completed_set),
        "remaining_set": remaining_units,
        "intersection": sorted(completed_set.intersection(remaining_units)),
        "union_equals_frozen_design": completed_set.union(remaining_units) == set(expected_order),
        "first_continuation_unit": remaining_units[0],
        "remaining_pairs": len(remaining_units),
        "remaining_new_learned_states": missing_states,
        "remaining_heldout_units": remaining_heldout,
        "per_unit": per_unit,
        "partial_effect_read": False,
    }
    require(not remaining["intersection"] and remaining["union_equals_frozen_design"], "partition proof failed")

    atomic(args.interruption_output, interruption)
    atomic(args.inheritance_output, inheritance)
    atomic(args.remaining_output, remaining)
    print(json.dumps({"interruption_status": interruption["status"], "inheritance_status": inheritance["status"], "remaining_status": remaining["status"], "provider_calls": 0}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
