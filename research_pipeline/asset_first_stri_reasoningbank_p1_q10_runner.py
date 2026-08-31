"""Exactly-once Q10 evaluator replay over ten frozen qualification units."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT, sha256_file, utcnow, write_json,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_core import (
    fixture_by_id, replay_one, verify_q10_contract,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_prepare import (
    CONTRACT, EXPECTED_ORDER, load_payload,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_runtime import (
    Q10_CONTRACT_SHA256,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_smoke import SMOKE

RUN_DIR = ROOT / "generated/asset-first-stri-reasoningbank-p1-q10-runs-20260831"
INDEX = ROOT / "generated/asset-first-stri-reasoningbank-p1-q10-index-20260831.json"
AUTHORITY = ROOT / "generated/asset-first-stri-reasoningbank-p1-q10-replay-execution-authority-20260831.json"
CORE_SOURCE = ROOT / "research_pipeline/asset_first_stri_reasoningbank_p1_q10_core.py"
RUNNER_SOURCE = ROOT / "research_pipeline/asset_first_stri_reasoningbank_p1_q10_runner.py"


def index_payload(
    journal: list[dict[str, Any]],
    completed: list[dict[str, Any]],
    execution_complete: bool,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-P1-Q10-REPLAY-20260831",
        "created_at_utc": utcnow(),
        "contract_sha256": Q10_CONTRACT_SHA256,
        "smoke_sha256": sha256_file(SMOKE),
        "execution_authority_sha256": sha256_file(AUTHORITY),
        "planned_order": [list(row) for row in EXPECTED_ORDER],
        "planned_run_count": 10,
        "run_journal": copy.deepcopy(journal),
        "completed_runs": copy.deepcopy(completed),
        "started_run_count": len(journal),
        "completed_run_count": len(completed),
        "execution_complete": execution_complete,
        "attempt_count": 1,
        "automatic_retry": "forbidden",
        "replacement_sampling": "forbidden",
        "second_start": "forbidden",
        "model_calls": 0,
        "provider_calls": 0,
        "full_p1_execution_authorized": False,
        "credential_material_present": False,
    }


def verify_authority() -> dict[str, Any]:
    authority = load_payload(AUTHORITY)
    if not (
        authority["decision"]
        == "P1_Q10_RUNTIME_RECONCILIATION_QUALIFIED_Q10_REPLAY_AUTHORIZED"
        and authority["q10_replay_execution_authorized"] is True
        and authority["q10_contract_sha256"] == Q10_CONTRACT_SHA256
        and authority["q10_smoke_sha256"] == sha256_file(SMOKE)
        and authority["q10_core_source_sha256"] == sha256_file(CORE_SOURCE)
        and authority["q10_runner_source_sha256"] == sha256_file(RUNNER_SOURCE)
        and all(authority["checks"].values())
        and authority["model_calls"] == authority["provider_calls"] == 0
        and authority["full_p1_execution_authorized"] is False
    ):
        raise RuntimeError("Q10 replay execution authority is closed")
    return authority


def run_q10(
    output_dir: Path = RUN_DIR,
    index_path: Path = INDEX,
) -> dict[str, Any]:
    if output_dir.exists() or index_path.exists():
        raise RuntimeError("refusing a second Q10 invocation or replacement replay")
    verification = verify_q10_contract()
    if not verification["pass"]:
        raise RuntimeError("Q10 frozen contract/source verification failed")
    verify_authority()
    contract = load_payload(CONTRACT)
    fixtures = fixture_by_id()
    journal: list[dict[str, Any]] = []
    completed: list[dict[str, Any]] = []
    write_json(index_path, index_payload(journal, completed, False))
    for source in contract["frozen_replay_sources"]:
        run_id = f"q10-{source['instance_id']}-{source['arm']}"
        started = {
            "ordinal": len(journal) + 1,
            "selection_rank": source["selection_rank"],
            "instance_id": source["instance_id"],
            "arm": source["arm"],
            "run_id": run_id,
            "source_run_sha256": source["source_run_sha256"],
            "attempt_count": 1,
            "started_at_utc": utcnow(),
            "status": "started_once",
        }
        journal.append(started)
        write_json(index_path, index_payload(journal, completed, False))
        out_path = output_dir / run_id / "run.json"
        try:
            payload = replay_one(
                source,
                fixtures[source["instance_id"]],
                run_id,
            )
            payload["created_at_utc"] = utcnow()
        except Exception as error:
            payload = {
                "schema_version": 1,
                "run_id": run_id,
                "created_at_utc": utcnow(),
                "instance_id": source["instance_id"],
                "arm": source["arm"],
                "selection_rank": source["selection_rank"],
                "source_q4": copy.deepcopy(source),
                "q10_contract_sha256": Q10_CONTRACT_SHA256,
                "implementation_checks": {},
                "implementation_valid": False,
                "failure": {
                    "error_type": type(error).__name__,
                    "message": str(error),
                },
                "task_outcome_affects_qualification": False,
                "attempt_count": 1,
                "model_calls": 0,
                "provider_calls": 0,
                "credential_material_present": False,
            }
        file_sha = write_json(out_path, payload)
        start_receipt = payload.get("start_reconciliation_receipt") or {}
        cleanup = payload.get("cleanup_receipt") or {}
        receipt = {
            "ordinal": started["ordinal"],
            "selection_rank": source["selection_rank"],
            "instance_id": source["instance_id"],
            "arm": source["arm"],
            "run_id": run_id,
            "path": str(out_path.relative_to(ROOT)),
            "file_sha256": file_sha,
            "attempt_count": 1,
            "implementation_valid": payload["implementation_valid"],
            "resolved": payload.get("resolved"),
            "client_start_invocations": start_receipt.get(
                "client_start_invocations"
            ),
            "reconciliation_invoked": start_receipt.get(
                "reconciliation_invoked"
            ),
            "second_start_invoked": start_receipt.get(
                "second_start_invoked"
            ),
            "cleanup_accepted": cleanup.get("accepted"),
        }
        completed.append(receipt)
        journal[-1].update({
            "status": "persisted",
            "completed_at_utc": utcnow(),
            "run_file_sha256": file_sha,
        })
        write_json(index_path, index_payload(journal, completed, False))
    write_json(index_path, index_payload(journal, completed, True))
    return {
        "decision": "P1_Q10_REPLAY_EXECUTION_COMPLETE",
        "run_count": len(completed),
        "index_sha256": sha256_file(index_path),
        "model_calls": 0,
        "provider_calls": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=RUN_DIR)
    parser.add_argument("--index", type=Path, default=INDEX)
    args = parser.parse_args()
    print(json.dumps(run_q10(args.output_dir, args.index), sort_keys=True))


if __name__ == "__main__":
    main()
