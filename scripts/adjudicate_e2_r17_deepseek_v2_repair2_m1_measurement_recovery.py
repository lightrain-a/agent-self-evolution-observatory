#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.run_e2_r17_deepseek_v2_repair2_m1_measurement as m1

CONTRACT = ROOT / "generated/e2-r17-deepseek-v2-repair2-m1-measurement-contract-v2-20260831.json"
AUTHORIZATION = ROOT / "generated/e2-r17-deepseek-v2-repair2-m1-single-use-authorization-20260831.json"
RECOVERY_SUMMARY = ROOT / "generated/e2-r17-deepseek-v2-repair2-m1-measurement-recovery-summary-20260831.json"
RUN_ROOT = Path("/data/wyt/e2-r17-search-projection/runs/deepseek-v2-repair2-m1-measurement-20260831")
DEFAULT_OUTPUT = ROOT / "generated/e2-r17-deepseek-v2-repair2-m1-measurement-recovery-pass-adjudication-20260831.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    m1.atomic_json(path, payload)


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def forbidden_summary_paths(value: Any, prefix: tuple[str, ...] = ()) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            current = prefix + (str(key),)
            lower = str(key).lower()
            if any(token in lower for token in ("effect", "p_value", "pvalue", "treatment_difference")):
                found.append(".".join(current))
            if "score" in lower and key != "scores_withheld_from_measurement_summary":
                found.append(".".join(current))
            found.extend(forbidden_summary_paths(child, current))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(forbidden_summary_paths(child, prefix + (str(index),)))
    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    contract, authorization, contract_sha, authorization_sha = m1.validate_contract_authorization(
        CONTRACT, AUTHORIZATION, execution=True
    )
    recovery = m1.load_json(RECOVERY_SUMMARY)
    require(recovery.get("status") == "REPAIR2_M1_MEASUREMENT_RECOVERY_PASS", "M1 recovery summary is not PASS")
    require(recovery.get("contract_sha256") == contract_sha, "recovery contract SHA drift")
    require(recovery.get("authorization_sha256") == authorization_sha, "recovery authorization SHA drift")
    require(recovery.get("new_updater_calls") == 0, "new updater calls drift")
    require(recovery.get("replayed_updater_calls") == 0, "replayed updater calls drift")
    require(recovery.get("measurement_states") == 2, "measurement state count drift")
    require(recovery.get("heldout_evaluations") == 36, "heldout count drift")
    require(recovery.get("partial_effect_read") is False, "partial effect boundary violated")
    require(recovery.get("analyzer_run") is False, "analyzer boundary violated")
    require(recovery.get("paired_units_after_recovery") == 15, "paired-unit state drift")
    require(recovery.get("learned_states_after_recovery") == 30, "learned-state state drift")
    require(recovery.get("heldout_units_after_recovery") == 540, "heldout-unit state drift")

    manifest = Path(str(recovery.get("completed_measurement_manifest") or ""))
    require(manifest == RUN_ROOT / "checkpoints/completed_measurements.jsonl", "manifest path drift")
    require(manifest.is_file(), "measurement manifest missing")
    require(sha_file(manifest) == recovery.get("completed_measurement_manifest_sha256"), "manifest SHA drift")
    rows = [json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    require(len(rows) == 36, "manifest does not contain exactly 36 rows")

    expected_tasks = list(contract["heldout"]["task_ids"])
    expected_pairs = {(arm, task) for arm in ("win_c", "mrw") for task in expected_tasks}
    actual_pairs = [(str(row.get("arm")), str(row.get("task_id"))) for row in rows]
    require(set(actual_pairs) == expected_pairs, "manifest arm/task coverage drift")
    require(len(actual_pairs) == len(set(actual_pairs)), "duplicate manifest arm/task row")
    require(Counter(arm for arm, _ in actual_pairs) == Counter({"win_c": 18, "mrw": 18}), "arm cardinality drift")

    state_by_arm = {str(row["arm"]): row for row in contract["learned_states"]}
    summary_provider_calls: dict[str, int] = defaultdict(int)
    summary_hashes: list[str] = []
    for row in rows:
        arm = str(row["arm"])
        task_id = str(row["task_id"])
        state = state_by_arm[arm]
        require(row.get("partial_effect_read") is False, f"manifest partial effect flag drift: {arm}/{task_id}")
        require(row.get("skill_post_sha256") == state["skill_post_sha256"], f"manifest skill drift: {arm}/{task_id}")
        require(row.get("update_receipt_sha256") == state["update_receipt_sha256"], f"manifest receipt drift: {arm}/{task_id}")
        summary_path = Path(str(row.get("summary_path") or ""))
        require(summary_path.is_file(), f"missing summary: {arm}/{task_id}")
        require(summary_path.resolve().is_relative_to(RUN_ROOT.resolve()), f"summary escaped M1 root: {arm}/{task_id}")
        summary_sha = sha_file(summary_path)
        require(summary_sha == row.get("summary_sha256"), f"summary SHA drift: {arm}/{task_id}")
        summary_hashes.append(summary_sha)
        summary = m1.load_json(summary_path)
        require(not forbidden_summary_paths(summary), f"summary exposed score/effect key: {arm}/{task_id}")
        require(summary.get("status") == "COMPLETED", f"summary incomplete: {arm}/{task_id}")
        require(summary.get("contract_sha256") == contract_sha, f"summary contract drift: {arm}/{task_id}")
        require(summary.get("authorization_sha256") == authorization_sha, f"summary auth drift: {arm}/{task_id}")
        require(summary.get("mode") == "e1" and summary.get("k") == 1, f"summary mode/K drift: {arm}/{task_id}")
        require(summary.get("resolved_model") == contract["actor"]["resolved_model"], f"summary model drift: {arm}/{task_id}")
        require(summary.get("skill_pre_sha256") == state["skill_post_sha256"], f"summary skill drift: {arm}/{task_id}")
        require(summary.get("updater_receipt_sha256") == state["update_receipt_sha256"], f"summary receipt drift: {arm}/{task_id}")
        require(summary.get("provider_retry_limit") == 0, f"provider retry drift: {arm}/{task_id}")
        require(summary.get("private_credentials_included") is False, f"credential leak flag: {arm}/{task_id}")
        require(summary.get("raw_response_ids_included") is False, f"raw response id flag: {arm}/{task_id}")
        tasks = summary.get("tasks") or []
        require(len(tasks) == 1 and tasks[0].get("task_id") == task_id, f"summary task drift: {arm}/{task_id}")
        require(tasks[0].get("scores_withheld_from_measurement_summary") is True, f"scores not withheld: {arm}/{task_id}")
        calls = int(tasks[0].get("provider_calls"))
        require(1 <= calls <= 10, f"provider calls outside unit budget: {arm}/{task_id}")
        summary_provider_calls[arm] += calls

    require(len(summary_hashes) == len(set(summary_hashes)), "duplicate measurement summary SHA")
    require(not (RUN_ROOT / "failure.json").exists(), "M1 failure artifact present")
    require(not list(RUN_ROOT.rglob("*analy*")), "analyzer artifact present")
    require(not list(RUN_ROOT.rglob("*effect*")), "effect artifact present")

    ledger_audit: dict[str, Any] = {}
    for arm in ("win_c", "mrw"):
        ledger = RUN_ROOT / "states" / arm / "provider_budget.sqlite3"
        require(ledger.is_file(), f"missing provider ledger: {arm}")
        with sqlite3.connect(f"file:{ledger}?mode=ro", uri=True) as cx:
            metadata = dict(cx.execute("select key,value from metadata"))
            claims = list(cx.execute(
                "select claim_id,unit_id,unit_call_index,claimed_at_utc from claims order by claim_id"
            ))
        require(metadata.get("contract_sha256") == contract_sha, f"ledger contract drift: {arm}")
        require(metadata.get("authorization_sha256") == authorization_sha, f"ledger auth drift: {arm}")
        require(int(metadata.get("total_limit", "-1")) == 180, f"ledger total limit drift: {arm}")
        require(int(metadata.get("per_unit_limit", "-1")) == 10, f"ledger unit limit drift: {arm}")
        require(len(claims) == len({row[0] for row in claims}), f"duplicate claim id: {arm}")
        pairs = [(str(row[1]), int(row[2])) for row in claims]
        require(len(pairs) == len(set(pairs)), f"duplicate provider unit call: {arm}")
        by_unit: dict[str, list[int]] = defaultdict(list)
        for _, unit_id, index, _ in claims:
            by_unit[str(unit_id)].append(int(index))
        require(len(by_unit) == 18, f"provider unit cardinality drift: {arm}")
        for unit_id, indexes in by_unit.items():
            require(sorted(indexes) == list(range(1, len(indexes) + 1)), f"non-contiguous calls: {arm}/{unit_id}")
            require(len(indexes) <= 10, f"provider unit budget breach: {arm}/{unit_id}")
        require(len(claims) == summary_provider_calls[arm], f"summary/ledger provider count mismatch: {arm}")
        ledger_audit[arm] = {
            "ledger_path": str(ledger),
            "ledger_sha256": sha_file(ledger),
            "provider_claims": len(claims),
            "unique_provider_units": len(by_unit),
            "duplicate_provider_unit_calls": 0,
            "max_claims_per_unit": max(map(len, by_unit.values())),
            "total_limit": 180,
            "per_unit_limit": 10,
        }

    start = RUN_ROOT / "run-start-receipt.json"
    lock = RUN_ROOT / ".exclusive.lock"
    require(start.is_file() and lock.is_file(), "start receipt or exclusive lock missing")
    result = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-deepseek-v2-repair2-m1-measurement-recovery-pass-adjudication",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "REPAIR2_M1_MEASUREMENT_RECOVERY_PASS_INTEGRITY_AUDITED",
        "contract_path": str(CONTRACT.relative_to(ROOT)),
        "contract_sha256": contract_sha,
        "authorization_path": str(AUTHORIZATION.relative_to(ROOT)),
        "authorization_sha256": authorization_sha,
        "run_root": str(RUN_ROOT),
        "run_start_receipt_sha256": sha_file(start),
        "exclusive_lock_sha256": sha_file(lock),
        "recovery_summary_path": str(RECOVERY_SUMMARY.relative_to(ROOT)),
        "recovery_summary_sha256": sha_file(RECOVERY_SUMMARY),
        "measurement_manifest_path": str(manifest),
        "measurement_manifest_sha256": sha_file(manifest),
        "manifest_rows": 36,
        "unique_arm_task_rows": 36,
        "arm_cardinality": {"win_c": 18, "mrw": 18},
        "measurement_summary_sha256_count": 36,
        "measurement_summary_sha256_unique": 36,
        "new_updater_calls": 0,
        "replayed_updater_calls": 0,
        "new_learned_states": 0,
        "sealed_parent_updater_calls": 20,
        "measurement_states": 2,
        "heldout_evaluations": 36,
        "failure_artifacts": 0,
        "provider_retry_limit": 0,
        "ledger_audit": ledger_audit,
        "paired_units_after_recovery": 15,
        "learned_states_after_recovery": 30,
        "heldout_units_after_recovery": 540,
        "partial_effect_read": False,
        "analyzer_run": False,
        "scientific_belief_update": "NONE_AT_M1; complete effect remains sealed until the full 48/48 closeout.",
        "next_state": "PREPARE_REPAIR2_CONTINUATION_V3",
        "authority": {
            "reexecute_m1": False,
            "run_analyzer": False,
            "read_partial_effect": False,
            "prepare_repair2_continuation_v3": True,
            "execute_v3": False,
            "paper_promotion": False,
            "submission": False,
        },
    }
    atomic_json(args.output, result)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
