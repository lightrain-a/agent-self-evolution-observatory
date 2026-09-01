from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_capability_execute import (
    enumerate_capability_units,
)
from research_pipeline.agent_constraint_externality_runner_core import (
    OBJECT_ID,
    AppendOnlyLedger,
    RunnerError,
    sha256_file,
    sha256_value,
)

VERDICT = "CAPABILITY_CALIBRATION_FAIL_INTERFACE_STOP"
FAILURE_CLASSIFICATION = "RUNNER_EVALUATOR_INTERFACE_FAILURE"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _evaluator_failure_evidence(
    *,
    source_db_path: Path,
    output_db_path: Path,
    expected_table: str,
    failure_message: str,
) -> dict[str, Any]:
    if not source_db_path.is_file() or not output_db_path.is_file():
        raise RunnerError("Evaluator audit database path is missing.")
    with sqlite3.connect(source_db_path) as connection:
        source_tables = {
            str(row[0])
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
    source_has_expected_table = expected_table in source_tables
    output_bytes = output_db_path.stat().st_size
    message_matches = failure_message == f"no such table: {expected_table}"
    if not source_has_expected_table or output_bytes != 0 or not message_matches:
        raise RunnerError(
            "Observed databases do not prove the frozen evaluator interface failure."
        )
    return {
        "classification": FAILURE_CLASSIFICATION,
        "failure_message_matches_expected_table": message_matches,
        "source_db_path": str(source_db_path),
        "source_db_bytes": source_db_path.stat().st_size,
        "source_db_table_count": len(source_tables),
        "source_has_expected_table": source_has_expected_table,
        "expected_table": expected_table,
        "evaluator_output_db_path": str(output_db_path),
        "evaluator_output_db_bytes": output_bytes,
        "inference": (
            "The source task database contains the required table, while the "
            "database handed to evaluation is an empty file."
        ),
    }


def build_failure_adjudication(
    *,
    ledger_path: Path,
    snapshot_path: Path,
    source_db_path: Path,
    output_db_path: Path,
    expected_table: str,
) -> dict[str, Any]:
    model_snapshot = _read_json(snapshot_path)
    if model_snapshot.get("object_id") != OBJECT_ID:
        raise RunnerError("Provider snapshot object identity mismatch.")

    ledger = AppendOnlyLedger(ledger_path)
    states = ledger.states()
    if any(state == "UNKNOWN_AFTER_DISPATCH" for state in states.values()):
        raise RunnerError(
            "Capability contains UNKNOWN_AFTER_DISPATCH; manual adjudication required."
        )
    rows = ledger.rows()
    if any(row.get("object_id") != OBJECT_ID for row in rows):
        raise RunnerError("Ledger object identity mismatch.")

    dispatch_rows = [row for row in rows if row["event"] == "DISPATCH"]
    terminal_rows = [
        row for row in rows if row["event"] in {"COMPLETION", "FAILURE"}
    ]
    failure_rows = [row for row in rows if row["event"] == "FAILURE"]
    if len(failure_rows) != 1 or not rows or rows[-1]["event"] != "FAILURE":
        raise RunnerError(
            "Read-only failure adjudication requires one terminal stopping failure."
        )
    if len(dispatch_rows) != len(terminal_rows):
        raise RunnerError("Every dispatched capability unit must be terminal.")
    if any(
        row.get("attempt") != 1 or row.get("max_retries") != 0
        for row in dispatch_rows
    ):
        raise RunnerError("Capability dispatch violated the no-retry contract.")
    if failure_rows[0].get("retry_attempted") is not False:
        raise RunnerError("Capability failure indicates a retry attempt.")

    provider_receipts = [
        receipt
        for row in terminal_rows
        for receipt in row.get("provider_receipts", [])
    ]
    resolved_models = {
        receipt.get("resolved_model") for receipt in provider_receipts
    }
    resolved_model = model_snapshot.get("resolved_request_model")
    if resolved_models != {resolved_model}:
        raise RunnerError("Provider resolved-model identity drifted.")

    failure = failure_rows[0]
    evidence = _evaluator_failure_evidence(
        source_db_path=source_db_path,
        output_db_path=output_db_path,
        expected_table=expected_table,
        failure_message=str(failure.get("message", "")),
    )
    catalog_requests = int(
        model_snapshot.get("catalog_provider_request_count", 0)
    )
    agent_requests = len(provider_receipts)
    scheduled_units = len(enumerate_capability_units(str(resolved_model)))
    authority = {
        "f0": False,
        "second_model": False,
        "toolsandbox": False,
        "appworld_ul": False,
        "p1": False,
        "method": False,
        "paper_claim": False,
    }
    gate = {
        "object_id": OBJECT_ID,
        "verdict": VERDICT,
        "failure_units": [failure["unit_id"]],
        "failure_classes": [str(failure.get("failure_class", ""))],
        "failure_messages": [str(failure.get("message", ""))],
        "failure_classification": FAILURE_CLASSIFICATION,
        "agent_model_request_count": agent_requests,
        "resolved_model_identities": sorted(str(item) for item in resolved_models),
        "scientific_outcome_available": False,
        "evaluator_failure_evidence": evidence,
    }
    result = {
        "schema_version": "ace-qwen-capability-failure-adjudication-v1",
        "object_id": OBJECT_ID,
        "status": VERDICT,
        "adjudication_mode": "POST_OUTCOME_READ_ONLY",
        "gate": gate,
        "provider_snapshot": model_snapshot,
        "scheduled_agent_episode_count": scheduled_units,
        "agent_episode_count": len(dispatch_rows),
        "terminal_agent_episode_count": len(terminal_rows),
        "catalog_provider_request_count": catalog_requests,
        "updater_model_request_count": 0,
        "provider_request_total": catalog_requests + agent_requests,
        "temperature": 0,
        "provider_max_retries": 0,
        "application_retry": False,
        "replacement": False,
        "measurement_only_recovery": False,
        "scientific_unit_replayed": False,
        "provider_calls_initiated_by_adjudicator": 0,
        "provider_side_deterministic_replay_guaranteed": False,
        "ledger_sha256": sha256_file(ledger_path),
        "scientific_outcomes_observed": 0,
        "partial_scientific_effects_reported": False,
        "f0_backbone": None,
        "authority": authority,
    }
    result["content_sha256"] = sha256_value(result)
    return result


def write_failure_artifacts(
    result: dict[str, Any],
    *,
    result_path: Path,
    snapshot_path: Path,
    manifest_path: Path,
) -> None:
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    manifest = {
        "schema_version": "ace-qwen-capability-failure-manifest-v1",
        "object_id": OBJECT_ID,
        "status": result["status"],
        "adjudication_mode": result["adjudication_mode"],
        "files": {
            str(path): {
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
            }
            for path in (snapshot_path, result_path)
        },
        "ledger_sha256": result["ledger_sha256"],
        "scheduled_agent_episode_count": result[
            "scheduled_agent_episode_count"
        ],
        "agent_episode_count": result["agent_episode_count"],
        "terminal_agent_episode_count": result[
            "terminal_agent_episode_count"
        ],
        "provider_request_total": result["provider_request_total"],
        "updater_model_request_count": 0,
        "scientific_outcomes_observed": 0,
        "scientific_unit_replayed": False,
        "provider_calls_initiated_by_adjudicator": 0,
        "authority": result["authority"],
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--source-db", type=Path, required=True)
    parser.add_argument("--output-db", type=Path, required=True)
    parser.add_argument("--expected-table", default="emails")
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()

    result = build_failure_adjudication(
        ledger_path=args.ledger,
        snapshot_path=args.snapshot,
        source_db_path=args.source_db,
        output_db_path=args.output_db,
        expected_table=args.expected_table,
    )
    write_failure_artifacts(
        result,
        result_path=args.result,
        snapshot_path=args.snapshot,
        manifest_path=args.manifest,
    )
    print(
        json.dumps(
            {
                "status": result["status"],
                "provider_request_total": result["provider_request_total"],
                "scientific_outcomes_observed": 0,
                "f0_authorized": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
