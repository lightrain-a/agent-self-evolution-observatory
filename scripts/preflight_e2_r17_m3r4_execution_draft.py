#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_m3r4_execution_guard import validate_zero_provider_draft
from research_pipeline.e2_r17_m3r4_execution_plan import sha256_file


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--contract",
        type=Path,
        default=ROOT / "generated/e2-r17-m3r4-execution-draft-contract-20260904.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "generated/e2-r17-m3r4-execution-draft-preflight-20260904.json",
    )
    args = parser.parse_args()

    contract = validate_zero_provider_draft(args.contract)
    contract_sha = sha256_file(args.contract)
    order_path = ROOT / contract["logical_unit_order"]["path"]
    order = json.loads(order_path.read_text(encoding="utf-8"))
    rows = order["logical_units"]
    state_counts = Counter(row["state_id"] for row in rows)
    rep_counts = Counter(int(row["actor_replicate"]) for row in rows)
    round_counts = Counter(int(row["round_index"]) for row in rows)
    combo_by_round: dict[str, dict[str, int]] = {}
    for round_index in range(4):
        subset = [row for row in rows if int(row["round_index"]) == round_index]
        c = Counter(f"{row['state_id']}/actor_rep_{row['actor_replicate']}" for row in subset)
        combo_by_round[str(round_index)] = dict(sorted(c.items()))

    recovery_run = Path(contract["resource_priority"]["recovery_v3_run_root"])
    recovery_lease = Path(contract["resource_priority"]["recovery_v3_lease"])
    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-m3r4-execution-draft-zero-provider-preflight",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "HOLD_FRESH_MODEL_IDENTITY_REQUALIFICATION_REQUIRED_ZERO_PROVIDER_PREFLIGHT_PASS",
        "draft_contract_path": str(args.contract.relative_to(ROOT)),
        "draft_contract_sha256": contract_sha,
        "checks": {
            "draft_zero_authority": True,
            "historical_identity_nonreusable": True,
            "fresh_identity_missing_as_expected": True,
            "state_artifacts_content_addressed": True,
            "updater_receipts_content_addressed": True,
            "suite_manifests_content_addressed": True,
            "mindmemos_commit_bound": True,
            "runtime_freeze_bound": True,
            "m3r4_protocol_review_pass_bound": True,
            "run_root_absent": not Path(contract["run_root"]).exists(),
            "lineage_lease_absent": not Path(contract["lineage_lease_path"]).exists(),
            "recovery_v3_run_root_absent_now": not recovery_run.exists(),
            "recovery_v3_lease_absent_now": not recovery_lease.exists(),
            "scientific_outcomes_read": False,
            "provider_budget_ledger_created": False,
            "provider_calls": 0,
        },
        "logical_unit_order": {
            "path": contract["logical_unit_order"]["path"],
            "sha256": contract["logical_unit_order"]["sha256"],
            "logical_units_sha256": contract["logical_unit_order"]["logical_units_sha256"],
            "logical_units": len(rows),
            "state_counts": dict(sorted(state_counts.items())),
            "actor_replicate_counts": {str(k): v for k, v in sorted(rep_counts.items())},
            "round_counts": {str(k): v for k, v in sorted(round_counts.items())},
            "combo_counts_by_round": combo_by_round,
        },
        "provider_budget": contract["provider_budget"],
        "fresh_model_identity_gate": contract["fresh_model_identity_gate"],
        "authority": {
            "provider_io": False,
            "actor_measurement": False,
            "updater": False,
            "analysis": False,
            "m4_bridge": False,
            "e3": False,
            "paper_promotion": False,
            "submission": False,
        },
        "next_gate": "AFTER_RECOVERY_V3_RESOURCE_PRIORITY_AND_ARK_QUOTA_AVAILABILITY_RUN_FRESH_NONSCIENTIFIC_M3R4_MODEL_IDENTITY_REQUALIFICATION",
        "interpretation_boundary": "Zero-provider draft preflight only. Static execution structure is qualified, but no current identity artifact is eligible for M3R4 scientific execution and no provider/actor authority exists.",
    }
    if not all(value is True for key, value in payload["checks"].items() if key not in {"scientific_outcomes_read", "provider_budget_ledger_created", "provider_calls"}):
        raise RuntimeError("one or more M3R4 zero-provider static preflight checks failed")
    atomic_json(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
