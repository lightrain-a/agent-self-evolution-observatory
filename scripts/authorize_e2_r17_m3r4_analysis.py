#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AUDIT_STATUS = "PASS_M3R4_COMPLETION_INTEGRITY_READY_FOR_SEPARATE_ANALYSIS_AUTHORIZATION"
ANALYSIS_AUTH_STATUS = "AUTHORIZED_E2_R17_M3R4_ANALYSIS_ONLY"


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--measurement-authorization", type=Path, required=True)
    parser.add_argument("--completion-audit", type=Path, required=True)
    parser.add_argument("--analyzer", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    require(not args.output.exists(), "M3R4 analysis authorization already exists")
    contract = load_json(args.contract)
    measurement_auth = load_json(args.measurement_authorization)
    audit = load_json(args.completion_audit)
    contract_sha = sha256_file(args.contract)
    measurement_auth_sha = sha256_file(args.measurement_authorization)
    audit_sha = sha256_file(args.completion_audit)

    require(contract.get("status") == "FROZEN_E2_R17_M3R4_EXECUTION", "M3R4 contract status drift")
    require(measurement_auth.get("status") == "AUTHORIZED_E2_R17_M3R4_ACTOR_MEASUREMENT_ONLY", "M3R4 measurement auth drift")
    require(measurement_auth.get("contract_sha256") == contract_sha, "M3R4 measurement auth/contract drift")
    require(audit.get("status") == AUDIT_STATUS, "M3R4 completion audit is not PASS")
    require(audit.get("contract_sha256") == contract_sha, "M3R4 audit contract drift")
    require(audit.get("measurement_authorization_sha256") == measurement_auth_sha, "M3R4 audit measurement-auth drift")
    require(audit.get("scientific_outcomes_read") is False and audit.get("scores_read") is False, "M3R4 audit already read outcomes")
    require(audit.get("partial_effect_read") is False and audit.get("analysis_run") is False, "M3R4 audit analysis boundary drift")
    require(int(audit.get("logical_units", -1)) == 72 and int(audit.get("technical_failures", -1)) == 0, "M3R4 audit geometry/failure drift")
    require(type(audit.get("within_task_iid_stationarity_qualified")) is bool, "M3R4 within-task qualification missing")
    require(type(audit.get("cross_task_factorization_qualified")) is bool, "M3R4 cross-task qualification missing")

    analyzer = args.analyzer.resolve()
    require(analyzer.is_file(), "M3R4 analyzer missing")
    metric = ROOT / contract["bound_code"]["analysis_metric"]["path"]
    require(metric.is_file(), "M3R4 frozen metric missing")
    require(sha256_file(metric) == contract["bound_code"]["analysis_metric"]["sha256"], "M3R4 metric SHA drift")

    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-m3r4-analysis-authorization",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": ANALYSIS_AUTH_STATUS,
        "single_use": True,
        "contract_path": str(args.contract.resolve()),
        "contract_sha256": contract_sha,
        "measurement_authorization_path": str(args.measurement_authorization.resolve()),
        "measurement_authorization_sha256": measurement_auth_sha,
        "completion_audit_path": str(args.completion_audit.resolve()),
        "completion_audit_sha256": audit_sha,
        "run_summary_path": audit["run_summary_path"],
        "run_summary_sha256": audit["run_summary_sha256"],
        "completed_manifest_path": audit["completed_manifest_path"],
        "completed_manifest_sha256": audit["completed_manifest_sha256"],
        "analysis_code": {
            "path": str(analyzer),
            "sha256": sha256_file(analyzer),
        },
        "frozen_metric": {
            "path": str(metric),
            "sha256": sha256_file(metric),
        },
        "inference_assumptions": {
            "within_task_iid_stationarity_qualified": audit["within_task_iid_stationarity_qualified"],
            "cross_task_factorization_qualified": audit["cross_task_factorization_qualified"],
            "qualification_boundary": audit["qualification_boundary"],
        },
        "authority": {
            "scientific_experiment": False,
            "provider_io": False,
            "actor_measurement": False,
            "updater": False,
            "analysis": True,
            "bridge": False,
            "e3": False,
            "paper_promotion": False,
            "submission": False,
        },
        "forbidden": {
            "provider_io": True,
            "new_actor_measurement": True,
            "updater": True,
            "historical_actor_outcomes_in_gate": True,
            "historical_ff_hist_in_gate": True,
            "historical_win_common_in_gate": True,
            "automatic_rerun": True,
            "bridge_execution": True,
            "paper_promotion": True,
        },
        "scientific_outcomes_read_before_authorization": False,
        "partial_effect_read_before_authorization": False,
        "next_gate": "RUN_EXACT_M3R4_ANALYZER_ONCE_ON_THE_72_SEALED_POST_FREEZE_SCORES",
    }
    atomic_json(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
