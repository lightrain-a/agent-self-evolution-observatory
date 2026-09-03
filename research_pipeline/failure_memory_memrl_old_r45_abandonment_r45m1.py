"""Permanently quarantine the unreachable original R45 lineage.

This receipt records the user's infrastructure-replacement authorization without
reclassifying the old unknown remote state as NOT_STARTED.  It reads no old
scientific output and grants no authority to inspect or pool a recovered effect.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
R43 = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-r43-memrl-g8-execution-manifest.json"
R44 = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-r44-human-execution-authorization.json"
CONTINUATION = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-continuation-status-20260831.json"
OUT = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-r45m1-old-r45-infrastructure-abandonment.json"

EXPECTED_FILE_SHA256 = {
    R43: "dbd810dce063f5bdaaf7c40038a3329166f8ad11441dd11b49034491bf753de2",
    R44: "155ff75eadbc286527a43cc54026f651832413a15eb79f5fd994bc4345a33ba3",
    CONTINUATION: "75892ee200d640c1dcac7f2a57392b740aaba06961262357f8764ace7bdcfaf5",
}
EXPECTED_R43_RECEIPT = "ed496819814765359a85f190c71de04f7c19c9788da27784b7c588b1ab5f2fce"
EXPECTED_R44_RECEIPT = "58de2e81e998db7c8f5321e6985fa477be9037247a0fffc197f943533dafc3cf"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object:{path}")
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _receipt_valid(value: dict[str, Any]) -> bool:
    observed = value.get("receipt_sha256")
    return isinstance(observed, str) and observed == _digest(
        {key: row for key, row in value.items() if key != "receipt_sha256"}
    )


def verify_frozen_evidence() -> dict[str, Any]:
    observed = {path: _sha(path) for path in EXPECTED_FILE_SHA256}
    drift = [
        str(path.relative_to(PROJECT_ROOT))
        for path, expected in EXPECTED_FILE_SHA256.items()
        if observed[path] != expected
    ]
    if drift:
        raise ValueError("STOP_FROZEN_EVIDENCE_DRIFT:" + ",".join(drift))

    r43 = _load(R43)
    r44 = _load(R44)
    if not _receipt_valid(r43) or r43.get("receipt_sha256") != EXPECTED_R43_RECEIPT:
        raise ValueError("STOP_FROZEN_EVIDENCE_DRIFT:r43-internal-receipt")
    if not _receipt_valid(r44) or r44.get("receipt_sha256") != EXPECTED_R44_RECEIPT:
        raise ValueError("STOP_FROZEN_EVIDENCE_DRIFT:r44-internal-receipt")
    bound = (r44.get("bindings") or {}).get("g8_manifest") or {}
    if bound.get("sha256") != observed[R43] or bound.get("receipt_sha256") != EXPECTED_R43_RECEIPT:
        raise ValueError("STOP_FROZEN_EVIDENCE_DRIFT:r43-r44-binding")
    return {
        "r43": r43,
        "r44": r44,
        "file_sha256": {
            str(path.relative_to(PROJECT_ROOT)): observed[path]
            for path in EXPECTED_FILE_SHA256
        },
    }


def build() -> dict[str, Any]:
    frozen = verify_frozen_evidence()
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-R45M1-OLD-R45-INFRASTRUCTURE-ABANDONMENT",
        "recorded_date": "2026-09-01",
        "role": "USER_AUTHORIZED_INFRASTRUCTURE_ONLY_REPLACEMENT_PRECONDITION",
        "status": "OLD_R45_PERMANENTLY_QUARANTINED_REMOTE_STATE_UNKNOWN",
        "explicit_user_directive": "直接开始重新跑",
        "adjudication": {
            "old_host": "yutong@222.20.126.60",
            "old_lineage": "R45",
            "old_state": "UNKNOWN_REMOTE_STATE",
            "reason": "host/network route unavailable",
            "pid_verified": False,
            "completed_ledger_verified": False,
            "checkpoint_verified": False,
            "old_scientific_outputs_read": False,
            "old_effect_inspected": False,
            "old_lineage_admissible_in_new_analysis": False,
            "future_recovery_of_old_artifacts": "QUARANTINE_ONLY",
            "unknown_reclassified_as_not_started": False,
        },
        "replacement": {
            "authorized": True,
            "classification": "USER_AUTHORIZED_INFRASTRUCTURE_ONLY_REPLACEMENT_RUN",
            "is_resume_of_old_r45": False,
            "fresh_lineage": "R45-M1",
            "preferred_host": "wyt@222.20.126.231",
            "fallback_host_before_first_scientific_source_exposure_only": "wyt@222.20.126.232",
            "old_artifact_pooling": False,
            "old_artifact_task_selection": False,
            "old_artifact_threshold_adjustment": False,
            "old_artifact_claim_adjustment": False,
        },
        "bindings": {
            "r43": {
                "path": str(R43.relative_to(PROJECT_ROOT)),
                "sha256": frozen["file_sha256"][str(R43.relative_to(PROJECT_ROOT))],
                "receipt_sha256": frozen["r43"]["receipt_sha256"],
            },
            "r44": {
                "path": str(R44.relative_to(PROJECT_ROOT)),
                "sha256": frozen["file_sha256"][str(R44.relative_to(PROJECT_ROOT))],
                "receipt_sha256": frozen["r44"]["receipt_sha256"],
            },
            "continuation": {
                "path": str(CONTINUATION.relative_to(PROJECT_ROOT)),
                "sha256": frozen["file_sha256"][str(CONTINUATION.relative_to(PROJECT_ROOT))],
            },
        },
        "authority": {
            "abandon_old_lineage": True,
            "resume_old_lineage": False,
            "inspect_old_scientific_effect": False,
            "pool_old_artifacts": False,
            "start_replacement_before_migration_qualification": False,
            "scientific_claim_change": False,
        },
        "confirmatory_outcomes_observed_by_this_receipt": 0,
    }
    payload["receipt_sha256"] = _digest(payload)
    return payload


def validate(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("status") != "OLD_R45_PERMANENTLY_QUARANTINED_REMOTE_STATE_UNKNOWN":
        errors.append("status")
    adj = payload.get("adjudication") or {}
    required_false = (
        "pid_verified",
        "completed_ledger_verified",
        "checkpoint_verified",
        "old_scientific_outputs_read",
        "old_effect_inspected",
        "old_lineage_admissible_in_new_analysis",
        "unknown_reclassified_as_not_started",
    )
    if any(adj.get(key) is not False for key in required_false):
        errors.append("old-state-overreach")
    if adj.get("future_recovery_of_old_artifacts") != "QUARANTINE_ONLY":
        errors.append("future-recovery")
    replacement = payload.get("replacement") or {}
    if replacement.get("fresh_lineage") != "R45-M1" or replacement.get("is_resume_of_old_r45") is not False:
        errors.append("replacement-lineage")
    authority = payload.get("authority") or {}
    if authority.get("abandon_old_lineage") is not True:
        errors.append("abandonment-authority")
    if any(authority.get(key) is not False for key in authority if key != "abandon_old_lineage"):
        errors.append("authority-leak")
    expected = _digest({key: row for key, row in payload.items() if key != "receipt_sha256"})
    if payload.get("receipt_sha256") != expected:
        errors.append("receipt-hash")
    return errors


def write(path: Path = OUT) -> dict[str, Any]:
    row = build()
    errors = validate(row)
    if errors:
        raise ValueError("invalid old-R45 abandonment receipt:" + ";".join(errors))
    path.write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return row


if __name__ == "__main__":
    row = write()
    print(json.dumps({
        "status": row["status"],
        "receipt_sha256": row["receipt_sha256"],
        "confirmatory_outcomes_observed": row["confirmatory_outcomes_observed_by_this_receipt"],
    }, ensure_ascii=False, sort_keys=True))
