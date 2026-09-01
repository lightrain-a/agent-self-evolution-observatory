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

from research_pipeline.e2_r17_repair2_manifest import ARMS, validate_quarantine
from research_pipeline.e2_r17_repair2_continuation_v2_manifest import (
    EXPECTED_SOURCE_PAIRS,
    EXPECTED_SOURCE_STATES,
    rows_by,
    validate_valid_rows_v2,
)

CONTRACT_STATUS = "FROZEN_E2_R17_DEEPSEEK_V2_REPAIR2_CONTINUATION_V2"
EXECUTION_AUTH_STATUS = "AUTHORIZED_E2_R17_DEEPSEEK_V2_REPAIR2_CONTINUATION_V2"
SUMMARY_STATUS = "COMPLETED_PENDING_SEPARATE_DEEPSEEK_V2_ADJUDICATION"
AUDIT_STATUS = "PASS_REPAIR2_CONTINUATION_V2_FULL_INTEGRITY_READY_FOR_SEPARATE_ANALYSIS"
SOURCES = tuple(EXPECTED_SOURCE_PAIRS.keys())
PAIR29_RECOVERY_MEASUREMENTS = 7


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
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def source_provenance(contract: dict[str, Any], contract_sha: str, execution_auth_sha: str) -> dict[str, dict[str, Any]]:
    pia_item = contract["pia1"]["canonical_lineage"]
    pia_path = ROOT / pia_item["path"]
    require(pia_path.is_file() and sha_file(pia_path) == pia_item["sha256"], "PIA canonical-lineage artifact drift")
    pia = load_json(pia_path)
    require(pia.get("status") == "PIA1_PASS_V3_RESUME_CANONICAL_LINEAGE", "PIA canonical lineage no longer passing")
    v3_contract_sha = str(pia["canonical_contract_sha256"])
    v3_auth_sha = str(pia["canonical_authorization_sha256"])

    pair29_item = contract["pair29_recovery"]
    pair29_path = ROOT / pair29_item["pass_path"]
    require(pair29_path.is_file() and sha_file(pair29_path) == pair29_item["pass_sha256"], "pair29 recovery PASS drift")
    pair29 = load_json(pair29_path)
    require(pair29.get("status") == "PAIR29_MEASUREMENT_RECOVERY_PASS", "pair29 recovery no longer passing")
    require(pair29.get("partial_effect_read") is False and pair29.get("analyzer_run") is False, "pair29 recovery crossed outcome boundary")
    require(int(pair29.get("new_heldout_evaluations", -1)) == PAIR29_RECOVERY_MEASUREMENTS, "pair29 recovery measurement count drift")
    require(int(pair29.get("unique_429_logical_unit_recoveries", -1)) == 1, "pair29 429 recovery count drift")
    pair29_contract_sha = str(pair29["contract_sha256"])
    pair29_auth_sha = str(pair29["authorization_sha256"])

    return {
        "repair1_inherited": {
            "updater": {(str(contract["repair1_parent"]["contract_sha256"]), str(contract["repair1_parent"]["authorization_sha256"]))},
            "measurement": {(str(contract["repair1_parent"]["contract_sha256"]), str(contract["repair1_parent"]["authorization_sha256"]))},
        },
        "repair2_m1_recovered": {
            "updater": {(str(contract["repair2_stopped_parent"]["contract_sha256"]), str(contract["repair2_stopped_parent"]["authorization_sha256"]))},
            "measurement": {(str(contract["repair2_m1_parent"]["contract_sha256"]), str(contract["repair2_m1_parent"]["authorization_sha256"]))},
        },
        "repair2_v3_fresh": {
            "updater": {(v3_contract_sha, v3_auth_sha)},
            "measurement": {(v3_contract_sha, v3_auth_sha)},
        },
        "repair2_v3_pair29_recovered": {
            "updater": {(v3_contract_sha, v3_auth_sha)},
            "measurement": {(v3_contract_sha, v3_auth_sha), (pair29_contract_sha, pair29_auth_sha)},
            "recovery_measurement": (pair29_contract_sha, pair29_auth_sha),
        },
        "repair2_continuation_v2_fresh": {
            "updater": {(contract_sha, execution_auth_sha)},
            "measurement": {(contract_sha, execution_auth_sha)},
        },
    }


def validate_state_artifacts(
    *,
    source: str,
    unit_id: str,
    arm_name: str,
    arm: dict[str, Any],
    heldout: set[str],
    provenance: dict[str, dict[str, Any]],
) -> tuple[int, dict[str, int], int]:
    state_root = Path(arm["state_root"])
    skill_path = state_root / "update/skill_post/SKILL.md"
    receipt_path = state_root / "update/update_receipt.json"
    require(skill_path.is_file() and sha_file(skill_path) == arm["skill_sha256"], f"skill SHA drift: {unit_id}/{arm_name}")
    require(receipt_path.is_file() and sha_file(receipt_path) == arm["update_receipt_sha256"], f"receipt SHA drift: {unit_id}/{arm_name}")
    receipt = load_json(receipt_path)
    updater_identity = (str(receipt.get("contract_sha256")), str(receipt.get("authorization_sha256")))
    require(updater_identity in provenance[source]["updater"], f"updater provenance drift: {unit_id}/{arm_name}")

    updater_calls = int(arm["updater_calls"])
    require(updater_calls in (10, 11), f"updater calls outside frozen path: {unit_id}/{arm_name}")
    correction_required = bool(arm.get("correction_required"))
    attempt0_success = bool(arm.get("attempt0_success"))
    require((updater_calls == 11) == correction_required, f"correction flag/call mismatch: {unit_id}/{arm_name}")
    require(attempt0_success != correction_required, f"attempt reliability flags invalid: {unit_id}/{arm_name}")

    eval_manifest_path = Path(arm["eval_manifest_path"])
    require(eval_manifest_path.is_file() and sha_file(eval_manifest_path) == arm["eval_manifest_sha256"], f"eval manifest SHA drift: {unit_id}/{arm_name}")
    eval_rows = rows_by(eval_manifest_path, "task_id")
    require(set(eval_rows) == heldout and len(eval_rows) == 18, f"heldout set drift: {unit_id}/{arm_name}")
    recovery_measurements = 0
    for task_id, row in eval_rows.items():
        summary_path = Path(row["summary_path"])
        ref_path = Path(row["trajectory_ref_path"])
        require(summary_path.is_file() and sha_file(summary_path) == row["summary_sha256"], f"eval summary SHA drift: {unit_id}/{arm_name}/{task_id}")
        require(ref_path.is_file() and sha_file(ref_path) == row["trajectory_ref_sha256"], f"trajectory ref SHA drift: {unit_id}/{arm_name}/{task_id}")
        summary = load_json(summary_path)
        require(summary.get("status") == "COMPLETED" and int(summary.get("k")) == 1, f"eval status/K drift: {unit_id}/{arm_name}/{task_id}")
        require(summary.get("skill_pre_sha256") == arm["skill_sha256"], f"eval skill binding drift: {unit_id}/{arm_name}/{task_id}")
        require(summary.get("updater_receipt_sha256") == arm["update_receipt_sha256"], f"eval receipt binding drift: {unit_id}/{arm_name}/{task_id}")
        measurement_identity = (str(summary.get("contract_sha256")), str(summary.get("authorization_sha256")))
        require(measurement_identity in provenance[source]["measurement"], f"measurement provenance drift: {unit_id}/{arm_name}/{task_id}")
        if source == "repair2_v3_pair29_recovered" and measurement_identity == provenance[source]["recovery_measurement"]:
            recovery_measurements += 1
        tasks = summary.get("tasks") or []
        require(len(tasks) == 1 and str(tasks[0].get("task_id")) == task_id, f"eval task drift: {unit_id}/{arm_name}/{task_id}")
        ref = load_json(ref_path)
        trajectory = Path(ref["trajectory_path"])
        require(trajectory.is_file() and sha_file(trajectory) == ref["trajectory_sha256"], f"trajectory SHA drift: {unit_id}/{arm_name}/{task_id}")
        # Outcome-blind boundary: deliberately never access trajectory outcome fields.

    reliability = {
        "attempt0_success": int(attempt0_success),
        "correction_required": int(correction_required),
        "correction_success": int(correction_required),
        "correction_failure": 0,
    }
    return len(eval_rows), reliability, recovery_measurements


def audit_ledger(
    *,
    db: Path,
    state_key: str,
    contract_sha: str,
    authorization_sha: str,
    expected_total_limit: int,
    expected_per_unit_limit: int,
    global_claims: set[tuple[str, str, int]],
) -> int:
    require(db.is_file(), f"missing provider budget ledger: {state_key}")
    connection = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        metadata = {str(k): str(v) for k, v in connection.execute("SELECT key, value FROM metadata")}
        require(metadata.get("contract_sha256") == contract_sha, f"ledger contract drift: {state_key}")
        require(metadata.get("authorization_sha256") == authorization_sha, f"ledger authorization drift: {state_key}")
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


def run_audit(*, contract_path: Path, execution_authorization_path: Path, run_summary_path: Path) -> dict[str, Any]:
    contract = load_json(contract_path)
    execution_auth = load_json(execution_authorization_path)
    summary = load_json(run_summary_path)
    contract_sha = sha_file(contract_path)
    execution_auth_sha = sha_file(execution_authorization_path)

    require(contract.get("status") == CONTRACT_STATUS, "Continuation V2 contract not frozen")
    require(execution_auth.get("status") == EXECUTION_AUTH_STATUS, "Continuation V2 execution authorization status drift")
    require(execution_auth.get("contract_sha256") == contract_sha, "execution authorization contract drift")
    require(execution_auth.get("authority", {}).get("analyzer") is False, "execution authorization must not authorize analyzer")
    require(summary.get("status") == SUMMARY_STATUS, "Continuation V2 run is not complete")
    require(summary.get("contract_sha256") == contract_sha, "summary contract drift")
    require(summary.get("authorization_sha256") == execution_auth_sha, "summary authorization drift")
    require(summary.get("inference_performed") is False, "runner performed scientific inference")
    require(summary.get("mrw_executed") is True and summary.get("primary_control") == "win_c", "treatment/control drift")

    expected_counts = {
        "paired_replicate_units": 48,
        "inherited_paired_units": 29,
        "repair1_inherited_paired_units": 14,
        "repair2_m1_recovered_paired_units": 1,
        "fresh_paired_units": 19,
        "pair29_recovered_paired_units": 1,
        "learned_states": 96,
        "heldout_rollout_units": 1728,
    }
    for key, expected in expected_counts.items():
        require(int(summary.get(key, -1)) == expected, f"summary cardinality drift: {key}")

    lease_path = Path(contract["global_lineage_lease"]["path"])
    require(lease_path.is_file(), "global lineage lease missing at completion")
    lease = load_json(lease_path)
    require(lease.get("status") == "COMPLETED_CONTINUATION_V2", "global lineage lease is not terminal-complete")
    require(lease.get("contract_sha256") == contract_sha and lease.get("authorization_sha256") == execution_auth_sha, "global lineage lease binding drift")
    require(lease.get("exactly_once") is True and lease.get("partial_effect_read") is False, "global lineage lease invariant drift")

    run_root = Path(contract["run_root"])
    require(not (run_root / ".exclusive.lock").exists(), "exclusive run lock still present after completion")
    failure_files = sorted(run_root.rglob("*failure*.json"))
    require(not failure_files, "Continuation V2 contains technical failure artifacts")

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
    validate_valid_rows_v2(valid_rows, streams=contract["streams"], quarantine=quarantine, require_complete=True)
    source_pairs = Counter(str(row["source"]) for row in valid_rows)
    require(source_pairs == EXPECTED_SOURCE_PAIRS, "source provenance cardinality drift")

    provenance = source_provenance(contract, contract_sha, execution_auth_sha)
    heldout = set(map(str, contract["heldout"]["task_ids"]))
    heldout_units = 0
    source_states: Counter[str] = Counter()
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
    pair29_recovery_measurements = 0
    global_claims: set[tuple[str, str, int]] = set()
    provider_claims_by_source: Counter[str] = Counter()
    provider_ledgers_by_source: Counter[str] = Counter()

    for row in valid_rows:
        unit_id = str(row["unit_id"])
        source = str(row["source"])
        pair_summary = Path(row["pair_summary_path"])
        require(pair_summary.is_file() and sha_file(pair_summary) == row["pair_summary_sha256"], f"pair summary SHA drift: {unit_id}")
        for arm_name in ARMS:
            arm = row["arms"][arm_name]
            count, state_reliability, recovered = validate_state_artifacts(
                source=source,
                unit_id=unit_id,
                arm_name=arm_name,
                arm=arm,
                heldout=heldout,
                provenance=provenance,
            )
            heldout_units += count
            source_states[source] += 1
            pair29_recovery_measurements += recovered
            for key, value in state_reliability.items():
                reliability[source][arm_name][f"{key}_count"] += value

            if source in {"repair2_v3_fresh", "repair2_continuation_v2_fresh"}:
                identity = next(iter(provenance[source]["updater"]))
                state_root = Path(arm["state_root"])
                provider_claims_by_source[source] += audit_ledger(
                    db=state_root / "checkpoints/provider_budget.sqlite3",
                    state_key=f"{unit_id}/{arm_name}",
                    contract_sha=identity[0],
                    authorization_sha=identity[1],
                    expected_total_limit=int(contract["budget"]["max_provider_calls_per_state"]),
                    expected_per_unit_limit=int(contract["budget"]["max_provider_calls_per_unit"]),
                    global_claims=global_claims,
                )
                provider_ledgers_by_source[source] += 1

    require(heldout_units == 1728, "heldout artifact cardinality drift")
    require(dict(source_states) == EXPECTED_SOURCE_STATES, "learned-state provenance cardinality drift")
    require(pair29_recovery_measurements == PAIR29_RECOVERY_MEASUREMENTS, "pair29 recovery provenance must account for exactly seven measurements")
    require(provider_ledgers_by_source["repair2_v3_fresh"] == 26, "V3 fresh ledger cardinality drift")
    require(provider_ledgers_by_source["repair2_continuation_v2_fresh"] == 38, "Continuation V2 fresh ledger cardinality drift")

    return {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-deepseek-v2-repair2-continuation-v2-completion-integrity-audit",
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
        "global_lineage_lease_path": str(lease_path),
        "global_lineage_lease_sha256": sha_file(lease_path),
        "paired_replicate_units": 48,
        "learned_states": 96,
        "heldout_rollout_units": heldout_units,
        "source_pair_counts": dict(source_pairs),
        "source_state_counts": dict(source_states),
        "pair29_recovery_measurements": pair29_recovery_measurements,
        "provider_ledgers_by_source": dict(provider_ledgers_by_source),
        "provider_claims_by_source": dict(provider_claims_by_source),
        "provider_claim_uniqueness_pass": True,
        "provider_budget_binding_pass": True,
        "quarantine_exclusion_pass": True,
        "global_lineage_lease_complete_pass": True,
        "runtime_reliability_by_source": reliability,
        "repair1_quarantined_patch_apply_failures": {"win_c": 0, "mrw": 1},
        "scientific_scores_read": False,
        "partial_effect_read": False,
        "analyzer_run": False,
        "authority": {
            "mint_single_use_continuation_v2_analysis_authorization": True,
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
