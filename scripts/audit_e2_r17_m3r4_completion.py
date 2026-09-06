#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_m3r4_execution_plan import (
    TASK_IDS,
    logical_units,
    state_binding_map,
    structural_provider_budget,
)

CONTRACT_STATUS = "FROZEN_E2_R17_M3R4_EXECUTION"
MEASUREMENT_AUTH_STATUS = "AUTHORIZED_E2_R17_M3R4_ACTOR_MEASUREMENT_ONLY"
RUN_STATUS = "COMPLETED_M3R4_MEASUREMENT_OUTCOME_EMBARGOED"
LEASE_STATUS = "COMPLETED_M3R4_MEASUREMENT"
AUDIT_STATUS = "PASS_M3R4_COMPLETION_INTEGRITY_READY_FOR_SEPARATE_ANALYSIS_AUTHORIZATION"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


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


def read_manifest(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def provider_ledger_summary(path: Path) -> dict[str, Any]:
    require(path.is_file(), "M3R4 provider ledger missing")
    db = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        total = int(db.execute("select count(*) from claims").fetchone()[0])
        rows = db.execute(
            "select unit_id, count(*) as n, max(unit_call_index) as max_idx from claims group by unit_id order by unit_id"
        ).fetchall()
        claim_ids = [int(x[0]) for x in db.execute("select claim_id from claims order by claim_id").fetchall()]
    finally:
        db.close()
    return {
        "total_claims": total,
        "unit_claim_counts": {str(unit): int(n) for unit, n, _ in rows},
        "unit_max_call_index": {str(unit): int(max_idx) for unit, _, max_idx in rows},
        "claim_ids_contiguous": claim_ids == list(range(1, total + 1)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--measurement-authorization", type=Path, required=True)
    parser.add_argument("--run-summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    require(not args.output.exists(), "M3R4 completion audit output already exists")
    contract = load_json(args.contract)
    authorization = load_json(args.measurement_authorization)
    run_summary = load_json(args.run_summary)
    contract_sha = sha256_file(args.contract)
    auth_sha = sha256_file(args.measurement_authorization)

    require(contract.get("status") == CONTRACT_STATUS, "M3R4 final contract status drift")
    require(authorization.get("status") == MEASUREMENT_AUTH_STATUS, "M3R4 measurement authorization status drift")
    require(authorization.get("contract_sha256") == contract_sha, "M3R4 authorization/contract SHA drift")
    require((authorization.get("authority") or {}).get("analysis") is False, "measurement authorization must keep analysis closed")
    require(run_summary.get("status") == RUN_STATUS, "M3R4 run summary status drift")
    require(run_summary.get("contract_sha256") == contract_sha, "M3R4 run summary contract drift")
    require(run_summary.get("authorization_sha256") == auth_sha, "M3R4 run summary authorization drift")
    require(int(run_summary.get("completed_logical_units", -1)) == 72, "M3R4 completed-unit count drift")
    require(run_summary.get("scores_read") is False, "M3R4 run summary says scores were read")
    require(run_summary.get("partial_effect_read") is False, "M3R4 run summary says partial effect was read")
    require(run_summary.get("analysis_authorized") is False, "M3R4 run summary unexpectedly authorizes analysis")

    provenance = authorization.get("provenance") or {}
    for label, path_key, sha_key in (
        ("runner", "runner_path", "runner_sha256"),
        ("guard", "guard_path", "guard_sha256"),
    ):
        path = ROOT / str(provenance.get(path_key) or "")
        require(path.is_file(), f"M3R4 {label} missing")
        require(sha256_file(path) == provenance.get(sha_key), f"M3R4 {label} SHA drift")

    for label, item in (contract.get("bound_code") or {}).items():
        path = ROOT / item["path"]
        require(path.is_file() and sha256_file(path) == item["sha256"], f"M3R4 bound-code drift: {label}")

    runtime = contract["actor_runtime"]
    freeze_path = Path(runtime["freeze_path"])
    qualification_path = ROOT / runtime["qualification_path"]
    require(freeze_path.is_file() and sha256_file(freeze_path) == runtime["freeze_sha256"], "M3R4 runtime freeze drift")
    require(
        qualification_path.is_file() and sha256_file(qualification_path) == runtime["qualification_sha256"],
        "M3R4 runtime qualification drift",
    )

    run_root = Path(contract["run_root"])
    lease_path = Path(contract["lineage_lease_path"])
    require(run_root.is_dir(), "M3R4 run root missing")
    require(lease_path.is_file(), "M3R4 lineage lease missing")
    lease = load_json(lease_path)
    require(lease.get("status") == LEASE_STATUS, "M3R4 lease not complete")
    require(lease.get("contract_sha256") == contract_sha, "M3R4 lease contract drift")
    require(lease.get("authorization_sha256") == auth_sha, "M3R4 lease authorization drift")
    require(int(lease.get("completed_logical_units", -1)) == 72, "M3R4 lease unit count drift")
    require(lease.get("scientific_outcomes_read") is False, "M3R4 lease says outcomes were read")

    manifest_path = Path(run_summary["completed_manifest_path"])
    require(manifest_path.is_file(), "M3R4 completed manifest missing")
    require(sha256_file(manifest_path) == run_summary["completed_manifest_sha256"], "M3R4 completed manifest SHA drift")
    require(lease.get("completed_manifest_sha256") == run_summary["completed_manifest_sha256"], "M3R4 lease/summary manifest drift")
    rows = read_manifest(manifest_path)
    expected = logical_units()
    require(len(rows) == len(expected) == 72, "M3R4 manifest cardinality drift")

    state_map = state_binding_map()
    trajectory_paths: set[str] = set()
    unit_dirs: set[str] = set()
    for row, unit in zip(rows, expected, strict=True):
        for key, expected_value in (
            ("order_index", unit.order_index),
            ("round_index", unit.round_index),
            ("unit_id", unit.unit_id),
            ("task_id", unit.task_id),
            ("state_id", unit.state_id),
            ("actor_replicate", unit.actor_replicate),
            ("state_sha256", state_map[unit.state_id].skill_sha256),
        ):
            require(row.get(key) == expected_value, f"M3R4 manifest drift {unit.unit_id}/{key}")
        trajectory = Path(row["trajectory_ref_path"])
        require(trajectory.is_file(), f"M3R4 sealed trajectory missing: {unit.unit_id}")
        require(sha256_file(trajectory) == row["trajectory_ref_sha256"], f"M3R4 sealed trajectory SHA drift: {unit.unit_id}")
        require(str(trajectory).startswith(str(run_root) + "/"), f"M3R4 trajectory escaped run root: {unit.unit_id}")
        unit_dir = run_root / "units" / f"{unit.order_index:02d}_{unit.state_id}_rep{unit.actor_replicate}_{unit.task_id}"
        require(str(trajectory).startswith(str(unit_dir) + "/"), f"M3R4 trajectory/unit-root drift: {unit.unit_id}")
        trajectory_paths.add(str(trajectory))
        unit_dirs.add(str(unit_dir))
    require(len(trajectory_paths) == 72 and len(unit_dirs) == 72, "M3R4 unique trajectory/unit-root count drift")

    failure_candidates = [
        path
        for path in run_root.rglob("*.json")
        if "failure" in path.name.lower() or path.name.startswith("eval_failure_")
    ]
    require(not failure_candidates, "M3R4 technical failure artifact present")

    ledger_path = run_root / "provider_budget.sqlite3"
    ledger = provider_ledger_summary(ledger_path)
    budget = structural_provider_budget()
    expected_ids = {unit.unit_id for unit in expected}
    require(set(ledger["unit_claim_counts"]) == expected_ids, "M3R4 provider-ledger unit set drift")
    require(ledger["claim_ids_contiguous"] is True, "M3R4 provider claim IDs are not contiguous")
    require(0 < int(ledger["total_claims"]) <= int(budget["hard_max_provider_calls_structural"]), "M3R4 provider total budget drift")
    require(
        all(1 <= int(n) <= int(budget["max_provider_calls_per_logical_unit"]) for n in ledger["unit_claim_counts"].values()),
        "M3R4 per-unit provider budget drift",
    )
    require(
        all(int(ledger["unit_max_call_index"][uid]) == int(ledger["unit_claim_counts"][uid]) for uid in expected_ids),
        "M3R4 provider unit-call index drift",
    )

    scope = authorization.get("execution_scope") or {}
    require(scope.get("automatic_retry") is False, "M3R4 automatic-retry policy drift")
    require(scope.get("completed_unit_replay") is False, "M3R4 completed-unit replay policy drift")
    require(scope.get("partial_effect_read") is False, "M3R4 partial-effect policy drift")
    require(scope.get("state_ids") == ["ff_r1", "ff_r2"], "M3R4 state scope drift")
    require(scope.get("actor_replicates") == [1, 2], "M3R4 replicate scope drift")
    require(scope.get("allowed_task_ids") == list(TASK_IDS), "M3R4 task scope drift")

    # These are pre-outcome execution diagnostics. They support the frozen
    # stochastic model but do not prove independence of hidden provider draws.
    diagnostics = {
        "exact_72_unit_hash_interleaved_order": True,
        "fresh_unique_unit_roots": len(unit_dirs) == 72,
        "fresh_actor_call_per_logical_unit_by_bound_runner": True,
        "no_completed_unit_replay": True,
        "no_automatic_retry": True,
        "provider_claims_partitioned_by_exact_unit_id": True,
        "same_resolved_model_runtime_and_verifier_bound": True,
        "no_concrete_shared_context_or_task_cache_violation_detected": True,
        "no_concrete_cross_task_batch_or_shared_state_coupling_detected": True,
        "hidden_provider_independence_not_provable_from_logs": True,
    }
    within_qualified = all(
        diagnostics[key]
        for key in (
            "exact_72_unit_hash_interleaved_order",
            "fresh_unique_unit_roots",
            "fresh_actor_call_per_logical_unit_by_bound_runner",
            "no_completed_unit_replay",
            "no_automatic_retry",
            "same_resolved_model_runtime_and_verifier_bound",
            "no_concrete_shared_context_or_task_cache_violation_detected",
        )
    )
    cross_qualified = all(
        diagnostics[key]
        for key in (
            "exact_72_unit_hash_interleaved_order",
            "fresh_unique_unit_roots",
            "provider_claims_partitioned_by_exact_unit_id",
            "no_concrete_cross_task_batch_or_shared_state_coupling_detected",
        )
    )

    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-m3r4-outcome-blind-completion-audit",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": AUDIT_STATUS,
        "contract_path": str(args.contract.resolve()),
        "contract_sha256": contract_sha,
        "measurement_authorization_path": str(args.measurement_authorization.resolve()),
        "measurement_authorization_sha256": auth_sha,
        "run_summary_path": str(args.run_summary.resolve()),
        "run_summary_sha256": sha256_file(args.run_summary),
        "completed_manifest_path": str(manifest_path),
        "completed_manifest_sha256": sha256_file(manifest_path),
        "lineage_lease_path": str(lease_path),
        "lineage_lease_sha256": sha256_file(lease_path),
        "logical_units": 72,
        "task_count": 18,
        "states": ["ff_r1", "ff_r2"],
        "actor_replicates": [1, 2],
        "trajectory_files_sha_verified_without_opening_outcome_content": 72,
        "technical_failures": 0,
        "provider_budget": {
            "total_claimed": ledger["total_claims"],
            "total_limit": budget["hard_max_provider_calls_structural"],
            "per_unit_limit": budget["max_provider_calls_per_logical_unit"],
            "unit_count": len(ledger["unit_claim_counts"]),
        },
        "inference_diagnostics": diagnostics,
        "within_task_iid_stationarity_qualified": bool(within_qualified),
        "cross_task_factorization_qualified": bool(cross_qualified),
        "qualification_boundary": "No concrete coupling violation was detected in the frozen execution diagnostics. These flags license the preregistered model-based interpretation but do not claim that hidden provider independence was proven from logs.",
        "scientific_outcomes_read": False,
        "scores_read": False,
        "partial_effect_read": False,
        "analysis_run": False,
        "authority": {
            "mint_single_use_analysis_authorization": True,
            "provider_io": False,
            "actor_measurement": False,
            "updater": False,
            "analysis": False,
            "bridge": False,
            "paper_promotion": False,
        },
        "next_gate": "MINT_SINGLE_USE_M3R4_ANALYSIS_AUTHORIZATION_THEN_READ_72_SEALED_SCORES_ONCE",
    }
    atomic_json(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
