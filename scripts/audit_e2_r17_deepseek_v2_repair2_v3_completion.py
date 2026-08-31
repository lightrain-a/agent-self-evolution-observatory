#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_repair2_manifest import validate_quarantine
from research_pipeline.e2_r17_repair2_v3_manifest import (
    ARMS,
    rows_by,
    validate_valid_rows_v3,
)

CONTRACT_STATUS = "FROZEN_E2_R17_DEEPSEEK_V2_REPAIR2_CONTINUATION_V3"
EXECUTION_AUTH_STATUS = "AUTHORIZED_E2_R17_DEEPSEEK_V2_REPAIR2_V3"
SUMMARY_STATUS = "COMPLETED_PENDING_SEPARATE_DEEPSEEK_V2_ADJUDICATION"
AUDIT_STATUS = "PASS_REPAIR2_V3_FULL_INTEGRITY_READY_FOR_SEPARATE_ANALYSIS"
SOURCES = ("repair1_inherited", "repair2_m1_recovered", "repair2_v3_fresh")
EXPECTED_SOURCE_PAIRS = Counter(
    {"repair1_inherited": 14, "repair2_m1_recovered": 1, "repair2_v3_fresh": 33}
)
EXPECTED_SOURCE_STATES = {
    "repair1_inherited": 28,
    "repair2_m1_recovered": 2,
    "repair2_v3_fresh": 66,
}


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    tmp.replace(path)


def receipt_path(state_root: Path, arm: dict[str, Any]) -> Path:
    return Path(arm.get("update_receipt_path") or state_root / "update/update_receipt.json")


def validate_state_artifacts(
    *,
    source: str,
    unit_id: str,
    arm_name: str,
    arm: dict[str, Any],
    heldout: set[str],
    contract: dict[str, Any],
    contract_sha: str,
    execution_auth_sha: str,
) -> tuple[int, dict[str, int]]:
    state_root = Path(arm["state_root"])
    skill_path = state_root / "update/skill_post/SKILL.md"
    receipt = receipt_path(state_root, arm)
    require(skill_path.is_file() and sha_file(skill_path) == arm["skill_sha256"], f"skill SHA drift: {unit_id}/{arm_name}")
    require(receipt.is_file() and sha_file(receipt) == arm["update_receipt_sha256"], f"receipt SHA drift: {unit_id}/{arm_name}")
    receipt_payload = load_json(receipt)

    if source == "repair1_inherited":
        updater_contract = contract["repair1_parent"]["contract_sha256"]
        updater_auth = contract["repair1_parent"]["authorization_sha256"]
        measurement_contract = updater_contract
        measurement_auth = updater_auth
    elif source == "repair2_m1_recovered":
        updater_contract = contract["repair2_stopped_parent"]["contract_sha256"]
        updater_auth = contract["repair2_stopped_parent"]["authorization_sha256"]
        measurement_contract = contract["repair2_m1_parent"]["contract_sha256"]
        measurement_auth = contract["repair2_m1_parent"]["authorization_sha256"]
    else:
        updater_contract = contract_sha
        updater_auth = execution_auth_sha
        measurement_contract = contract_sha
        measurement_auth = execution_auth_sha
    require(receipt_payload.get("contract_sha256") == updater_contract, f"updater contract provenance drift: {unit_id}/{arm_name}")
    require(receipt_payload.get("authorization_sha256") == updater_auth, f"updater authorization provenance drift: {unit_id}/{arm_name}")

    updater_calls = int(arm["updater_calls"])
    require(updater_calls in (10, 11), f"updater calls outside frozen path: {unit_id}/{arm_name}")
    correction_required = bool(arm.get("correction_required"))
    attempt0_success = bool(arm.get("attempt0_success"))
    require((updater_calls == 11) == correction_required, f"correction flag/call mismatch: {unit_id}/{arm_name}")
    require(attempt0_success != correction_required, f"attempt reliability flags invalid: {unit_id}/{arm_name}")

    eval_manifest_path = Path(arm["eval_manifest_path"])
    require(
        eval_manifest_path.is_file() and sha_file(eval_manifest_path) == arm["eval_manifest_sha256"],
        f"eval manifest SHA drift: {unit_id}/{arm_name}",
    )
    eval_rows = rows_by(eval_manifest_path, "task_id")
    require(set(eval_rows) == heldout and len(eval_rows) == 18, f"heldout set drift: {unit_id}/{arm_name}")
    for task_id, row in eval_rows.items():
        summary_path = Path(row["summary_path"])
        ref_path = Path(row["trajectory_ref_path"])
        require(summary_path.is_file() and sha_file(summary_path) == row["summary_sha256"], f"eval summary SHA drift: {unit_id}/{arm_name}/{task_id}")
        require(ref_path.is_file() and sha_file(ref_path) == row["trajectory_ref_sha256"], f"trajectory ref SHA drift: {unit_id}/{arm_name}/{task_id}")
        summary = load_json(summary_path)
        require(summary.get("status") == "COMPLETED" and int(summary.get("k")) == 1, f"eval status/K drift: {unit_id}/{arm_name}/{task_id}")
        require(summary.get("skill_pre_sha256") == arm["skill_sha256"], f"eval skill binding drift: {unit_id}/{arm_name}/{task_id}")
        require(summary.get("updater_receipt_sha256") == arm["update_receipt_sha256"], f"eval receipt binding drift: {unit_id}/{arm_name}/{task_id}")
        require(summary.get("contract_sha256") == measurement_contract, f"measurement contract provenance drift: {unit_id}/{arm_name}/{task_id}")
        require(summary.get("authorization_sha256") == measurement_auth, f"measurement authorization provenance drift: {unit_id}/{arm_name}/{task_id}")
        tasks = summary.get("tasks") or []
        require(len(tasks) == 1 and str(tasks[0].get("task_id")) == task_id, f"eval task drift: {unit_id}/{arm_name}/{task_id}")
        ref = load_json(ref_path)
        trajectory = Path(ref["trajectory_path"])
        require(trajectory.is_file() and sha_file(trajectory) == ref["trajectory_sha256"], f"trajectory SHA drift: {unit_id}/{arm_name}/{task_id}")
        # Outcome-blind boundary: never access the trajectory ref score here.

    reliability = {
        "attempt0_success": int(attempt0_success),
        "correction_required": int(correction_required),
        "correction_success": int(correction_required),
        "correction_failure": 0,
    }
    return len(eval_rows), reliability


def audit_ledger(
    *,
    db: Path,
    state_key: str,
    contract_sha: str,
    execution_auth_sha: str,
    expected_total_limit: int,
    expected_per_unit_limit: int,
    global_claims: set[tuple[str, str, int]],
) -> int:
    require(db.is_file(), f"missing provider budget ledger: {state_key}")
    connection = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        metadata = {str(k): str(v) for k, v in connection.execute("SELECT key, value FROM metadata")}
        require(metadata.get("contract_sha256") == contract_sha, f"ledger contract drift: {state_key}")
        require(metadata.get("authorization_sha256") == execution_auth_sha, f"ledger authorization drift: {state_key}")
        require(int(metadata.get("total_limit", -1)) == expected_total_limit, f"ledger total limit drift: {state_key}")
        require(int(metadata.get("per_unit_limit", -1)) == expected_per_unit_limit, f"ledger unit limit drift: {state_key}")
        claims = [(str(unit), int(index)) for unit, index in connection.execute("SELECT unit_id, unit_call_index FROM claims")]
    finally:
        connection.close()
    require(len(claims) <= expected_total_limit, f"provider budget breach: {state_key}")
    require(len(claims) == len(set(claims)), f"duplicate local provider claim: {state_key}")
    unit_counts = Counter(unit for unit, _ in claims)
    require(all(count <= expected_per_unit_limit for count in unit_counts.values()), f"per-unit provider budget breach: {state_key}")
    for unit, count in unit_counts.items():
        indices = sorted(index for claim_unit, index in claims if claim_unit == unit)
        require(indices == list(range(1, count + 1)), f"non-contiguous provider claim sequence: {state_key}/{unit}")
    for unit, index in claims:
        key = (state_key, unit, index)
        require(key not in global_claims, f"duplicate global provider claim: {key}")
        global_claims.add(key)
    return len(claims)


def run_audit(
    *,
    contract_path: Path,
    execution_authorization_path: Path,
    run_summary_path: Path,
) -> dict[str, Any]:
    contract = load_json(contract_path)
    execution_auth = load_json(execution_authorization_path)
    summary = load_json(run_summary_path)
    contract_sha = sha_file(contract_path)
    execution_auth_sha = sha_file(execution_authorization_path)

    require(contract.get("status") == CONTRACT_STATUS, "V3 contract not frozen")
    require(execution_auth.get("status") == EXECUTION_AUTH_STATUS, "V3 execution authorization status drift")
    require(execution_auth.get("contract_sha256") == contract_sha, "V3 execution authorization contract drift")
    require(execution_auth.get("authority", {}).get("analyzer") is False, "execution authorization must not authorize analyzer")
    require(summary.get("status") == SUMMARY_STATUS, "V3 run is not complete")
    require(summary.get("contract_sha256") == contract_sha, "summary contract drift")
    require(summary.get("authorization_sha256") == execution_auth_sha, "summary authorization drift")
    require(summary.get("inference_performed") is False, "runner performed inference")
    require(summary.get("mrw_executed") is True and summary.get("primary_control") == "win_c", "treatment/control drift")
    expected_counts = {
        "paired_replicate_units": 48,
        "inherited_paired_units": 15,
        "repair1_inherited_paired_units": 14,
        "repair2_m1_recovered_paired_units": 1,
        "fresh_paired_units": 33,
        "learned_states": 96,
        "heldout_rollout_units": 1728,
    }
    for key, expected in expected_counts.items():
        require(int(summary.get(key, -1)) == expected, f"summary cardinality drift: {key}")

    run_root = Path(contract["run_root"])
    failure_files = sorted(run_root.rglob("*failure*.json"))
    require(not failure_files, "V3 contains technical failure artifacts")
    valid_path = Path(summary["valid_replicate_manifest"])
    completed_path = Path(summary["completed_replicate_manifest"])
    require(valid_path == Path(contract["valid_replicate_manifest"]["path"]), "valid manifest path drift")
    require(valid_path.is_file() and sha_file(valid_path) == summary["valid_replicate_manifest_sha256"], "valid manifest SHA drift")
    require(completed_path.is_file() and sha_file(completed_path) == summary["completed_replicate_manifest_sha256"], "completed manifest SHA drift")
    valid_rows = list(rows_by(valid_path, "unit_id").values())
    completed_rows = rows_by(completed_path, "unit_id")
    require(len(completed_rows) == 48 and set(completed_rows) == {str(row["unit_id"]) for row in valid_rows}, "completed/valid manifest mismatch")

    quarantine_item = contract["technical_quarantine"]
    quarantine = validate_quarantine(ROOT / quarantine_item["path"], quarantine_item["sha256"])
    validate_valid_rows_v3(valid_rows, streams=contract["streams"], quarantine=quarantine, require_complete=True)

    heldout = set(map(str, contract["heldout"]["task_ids"]))
    source_pairs = Counter(str(row["source"]) for row in valid_rows)
    require(source_pairs == EXPECTED_SOURCE_PAIRS, "source provenance cardinality drift")
    heldout_units = 0
    source_states = Counter()
    reliability = {
        source: {
            arm: {
                "attempt0_success_count": 0,
                "correction_required_count": 0,
                "correction_success_count": 0,
                "correction_failure_count": 0,
            }
            for arm in ARMS
        }
        for source in SOURCES
    }
    global_claims: set[tuple[str, str, int]] = set()
    provider_claims = 0
    fresh_ledgers = 0

    for row in valid_rows:
        unit_id = str(row["unit_id"])
        source = str(row["source"])
        pair_summary = Path(row["pair_summary_path"])
        require(pair_summary.is_file() and sha_file(pair_summary) == row["pair_summary_sha256"], f"pair summary SHA drift: {unit_id}")
        for arm_name in ARMS:
            arm = row["arms"][arm_name]
            count, state_reliability = validate_state_artifacts(
                source=source,
                unit_id=unit_id,
                arm_name=arm_name,
                arm=arm,
                heldout=heldout,
                contract=contract,
                contract_sha=contract_sha,
                execution_auth_sha=execution_auth_sha,
            )
            heldout_units += count
            source_states[source] += 1
            for key, value in state_reliability.items():
                reliability[source][arm_name][f"{key}_count" if not key.endswith("_count") else key] += value
            if source == "repair2_v3_fresh":
                state_root = Path(arm["state_root"])
                provider_claims += audit_ledger(
                    db=state_root / "checkpoints/provider_budget.sqlite3",
                    state_key=f"{unit_id}/{arm_name}",
                    contract_sha=contract_sha,
                    execution_auth_sha=execution_auth_sha,
                    expected_total_limit=int(contract["budget"]["max_provider_calls_per_state"]),
                    expected_per_unit_limit=int(contract["budget"]["max_provider_calls_per_unit"]),
                    global_claims=global_claims,
                )
                fresh_ledgers += 1

    require(heldout_units == 1728, "heldout artifact cardinality drift")
    require(dict(source_states) == EXPECTED_SOURCE_STATES, "learned-state provenance cardinality drift")
    require(fresh_ledgers == 66, "V3 fresh ledger cardinality drift")

    return {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-deepseek-v2-repair2-v3-completion-integrity-audit",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": AUDIT_STATUS,
        "contract_path": str(contract_path),
        "contract_sha256": contract_sha,
        "execution_authorization_path": str(execution_authorization_path),
        "execution_authorization_sha256": execution_auth_sha,
        "run_summary_path": str(run_summary_path),
        "run_summary_sha256": sha_file(run_summary_path),
        "valid_replicate_manifest_path": str(valid_path),
        "valid_replicate_manifest_sha256": sha_file(valid_path),
        "completed_replicate_manifest_path": str(completed_path),
        "completed_replicate_manifest_sha256": sha_file(completed_path),
        "paired_replicate_units": 48,
        "learned_states": 96,
        "heldout_rollout_units": heldout_units,
        "source_pair_counts": dict(source_pairs),
        "source_state_counts": dict(source_states),
        "v3_fresh_provider_ledgers": fresh_ledgers,
        "v3_fresh_provider_claims": provider_claims,
        "provider_claim_uniqueness_pass": True,
        "provider_budget_binding_pass": True,
        "quarantine_exclusion_pass": True,
        "runtime_reliability_by_source": reliability,
        "repair1_quarantined_patch_apply_failures": {"win_c": 0, "mrw": 1},
        "scientific_scores_read": False,
        "partial_effect_read": False,
        "analyzer_run": False,
        "authority": {
            "mint_single_use_v3_analysis_authorization": True,
            "scientific_execution": False,
            "provider_io": False,
            "public_benchmark": False,
            "second_backbone": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--execution-authorization", type=Path, required=True)
    parser.add_argument("--run-summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--analysis-output", type=Path)
    args = parser.parse_args()
    require(not args.output.exists(), "completion audit already exists; exactly-once closeout required")
    if args.analysis_output is not None:
        require(not args.analysis_output.exists(), "analysis output exists before completion audit")
    payload = run_audit(
        contract_path=args.contract,
        execution_authorization_path=args.execution_authorization,
        run_summary_path=args.run_summary,
    )
    atomic_json(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
