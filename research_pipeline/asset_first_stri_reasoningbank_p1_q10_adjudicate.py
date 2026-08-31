"""Outcome-blind Q10 adjudicator and immutable evidence packager."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT, sha256_file, utcnow, write_json,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_core import verify_q10_contract
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_fault_gate import OUTPUT as FAULT_GATE
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_prepare import (
    CONTRACT, EXPECTED_ORDER, Q5_ADJUDICATION, SCIENTIFIC_MEMORY as Q5_MEMORY,
    load_payload,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_runner import AUTHORITY, INDEX
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_runtime import Q10_CONTRACT_SHA256
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_smoke import SMOKE

OUTPUT = ROOT / "generated/asset-first-stri-reasoningbank-p1-q10-adjudication-20260831.json"
MANIFEST = ROOT / "generated/asset-first-stri-reasoningbank-p1-q10-artifact-manifest-20260831.json"
FAILURE_DIFFERENTIAL = ROOT / "generated/asset-first-stri-reasoningbank-p1-q10-failure-differential-20260831.json"
MEMORY = ROOT / "generated/asset-first-stri-reasoningbank-p1-q2-q3-q4-q5-q10-scientific-memory-20260831.json"
PASS_DECISION = "P1_Q10_RUNTIME_RECONCILIATION_QUALIFIED_FULL_P1_PLANNING_GATE_OPEN_EXECUTION_UNAUTHORIZED"
FAIL_DECISION = "P1_Q10_RUNTIME_RECONCILIATION_UNQUALIFIED_FULL_P1_HOLD"
CANONICAL_LESSON = (
    "implementation/operationalization failure -> no scientific belief update -> "
    "prospective repaired qualification"
)
RECONCILIATION_LESSON = (
    "A remote/container operation may have completed even when the client "
    "acknowledgement fails. Exactly-once scientific execution therefore requires "
    "side-effect reconciliation, not blind retries."
)


def _artifact_rows(index: dict[str, Any]) -> list[dict[str, Any]]:
    paths = [CONTRACT, FAULT_GATE, SMOKE, AUTHORITY, INDEX]
    paths.extend(ROOT / row["path"] for row in index["completed_runs"])
    expected = {
        str((ROOT / row["path"]).resolve()): row["file_sha256"]
        for row in index["completed_runs"]
    }
    rows = []
    for path in paths:
        actual = sha256_file(path)
        expected_sha = expected.get(str(path.resolve()))
        rows.append({
            "path": str(path.relative_to(ROOT)),
            "sha256": actual,
            "bytes": path.stat().st_size,
            "index_expected_sha256": expected_sha,
            "hash_matches": expected_sha is None or expected_sha == actual,
        })
    return rows


def adjudicate(
    index_path: Path = INDEX,
    output: Path = OUTPUT,
    manifest: Path = MANIFEST,
    differential: Path = FAILURE_DIFFERENTIAL,
    memory: Path = MEMORY,
) -> dict[str, Any]:
    for path in (output, manifest, differential, memory):
        if path.exists():
            raise RuntimeError(f"refusing to overwrite immutable Q10 evidence: {path}")
    verification = verify_q10_contract()
    index = load_payload(index_path)
    authority = load_payload(AUTHORITY)
    smoke = load_payload(SMOKE)
    q5 = load_payload(Q5_ADJUDICATION)
    completed = index["completed_runs"]
    journal = index["run_journal"]
    actual_order = [
        (row["selection_rank"], row["instance_id"], row["arm"])
        for row in completed
    ]
    journal_order = [
        (row["selection_rank"], row["instance_id"], row["arm"])
        for row in journal
    ]
    summaries, artifact_checks = [], []
    for receipt in completed:
        path = (ROOT / receipt["path"]).resolve()
        if not path.is_relative_to(ROOT.resolve()):
            raise RuntimeError("Q10 run path escapes repository")
        actual_sha = sha256_file(path)
        run = load_payload(path)
        hash_pass = actual_sha == receipt["file_sha256"]
        artifact_checks.append({
            "run_id": receipt["run_id"],
            "expected_sha256": receipt["file_sha256"],
            "actual_sha256": actual_sha,
            "pass": hash_pass,
        })
        implementation_checks = run.get("implementation_checks") or {}
        start = run.get("start_reconciliation_receipt") or {}
        cleanup = run.get("cleanup_receipt") or {}
        summaries.append({
            "ordinal": receipt["ordinal"],
            "selection_rank": receipt["selection_rank"],
            "instance_id": receipt["instance_id"],
            "arm": receipt["arm"],
            "run_id": receipt["run_id"],
            "run_file_sha256": actual_sha,
            "implementation_checks": implementation_checks,
            "implementation_valid": bool(
                hash_pass
                and run.get("implementation_valid") is True
                and implementation_checks
                and all(implementation_checks.values())
            ),
            "official_status_count": len(run.get("official_parser_status_map") or {}),
            "official_local_parser_exact": (
                run.get("official_parser_status_map")
                == run.get("local_parser_status_map")
            ),
            "client_start_invocations": start.get("client_start_invocations"),
            "reconciliation_invoked": start.get("reconciliation_invoked"),
            "exact_running_state_verified": start.get("exact_running_state_verified"),
            "second_start_invoked": start.get("second_start_invoked"),
            "cleanup_accepted": cleanup.get("accepted"),
            "cleanup_after_finalized_receipt": cleanup.get(
                "reconciliation_receipt_finalized_before_cleanup"
            ),
            "resolved": run.get("resolved"),
            "task_outcome_affects_qualification": False,
            "model_calls": run.get("model_calls"),
            "provider_calls": run.get("provider_calls"),
            "failure": run.get("failure"),
        })
    checks = {
        "contract_exact": (
            index["contract_sha256"] == Q10_CONTRACT_SHA256
            and verification["pass"] is True
        ),
        "smoke_and_authority_exact": (
            index["smoke_sha256"] == sha256_file(SMOKE)
            and index["execution_authority_sha256"] == sha256_file(AUTHORITY)
            and authority["q10_replay_execution_authorized"] is True
            and smoke["pass"] is True
        ),
        "all_ten_started_once_in_frozen_order": (
            len(journal) == 10
            and journal_order == EXPECTED_ORDER
            and all(
                row["attempt_count"] == 1 and row["status"] == "persisted"
                for row in journal
            )
        ),
        "all_ten_persisted_once_in_frozen_order": (
            index["execution_complete"] is True
            and len(completed) == 10
            and actual_order == EXPECTED_ORDER
            and len({row["run_id"] for row in completed}) == 10
            and all(row["attempt_count"] == 1 for row in completed)
        ),
        "all_artifact_hashes_valid": (
            len(artifact_checks) == 10 and all(row["pass"] for row in artifact_checks)
        ),
        "all_ten_implementation_valid": (
            len(summaries) == 10 and all(row["implementation_valid"] for row in summaries)
        ),
        "all_start_invocation_counts_one": all(
            row["client_start_invocations"] == 1 for row in summaries
        ),
        "all_second_start_counts_zero": all(
            row["second_start_invoked"] is False for row in summaries
        ),
        "all_reconciliation_events_fail_closed": all(
            row["exact_running_state_verified"] is True
            for row in summaries
            if row["reconciliation_invoked"] is True
        ),
        "all_cleanup_receipts_valid": all(
            row["cleanup_accepted"] is True
            and row["cleanup_after_finalized_receipt"] is True
            for row in summaries
        ),
        "all_official_parser_maps_valid_and_exact": all(
            row["official_status_count"] > 0
            and row["official_local_parser_exact"] is True
            for row in summaries
        ),
        "no_model_or_provider_calls": (
            index["model_calls"] == index["provider_calls"] == 0
            and all(
                row["model_calls"] == row["provider_calls"] == 0 for row in summaries
            )
        ),
        "no_retry_replacement_or_second_start": (
            index["automatic_retry"] == "forbidden"
            and index["replacement_sampling"] == "forbidden"
            and index["second_start"] == "forbidden"
        ),
        "task_outcomes_excluded_from_qualification": True,
        "q4_q5_immutable_history_preserved": (
            q5["decision"] == "P1_Q5_EVALUATOR_REPAIR_UNQUALIFIED_FULL_P1_HOLD"
            and q5["implementation_qualified"] is False
            and q5["scientific_boundary"]["scientific_belief_update"] == "none"
        ),
    }
    qualified = all(checks.values())
    decision = PASS_DECISION if qualified else FAIL_DECISION
    reconciled = [
        row["run_id"] for row in summaries if row["reconciliation_invoked"] is True
    ]
    payload = {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-P1-Q10-ADJUDICATION-20260831",
        "created_at_utc": utcnow(),
        "contract_sha256": Q10_CONTRACT_SHA256,
        "index_sha256": sha256_file(index_path),
        "smoke_sha256": sha256_file(SMOKE),
        "execution_authority_sha256": sha256_file(AUTHORITY),
        "artifact_checks": artifact_checks,
        "run_summaries": summaries,
        "qualification_checks": checks,
        "implementation_qualified": qualified,
        "reconciliation_events": {
            "count": len(reconciled),
            "run_ids": reconciled,
            "all_fail_closed": checks["all_reconciliation_events_fail_closed"],
        },
        "descriptive_task_outcomes": {
            "resolved_count": sum(row["resolved"] is True for row in summaries),
            "unresolved_count": sum(row["resolved"] is False for row in summaries),
            "missing_or_invalid_count": sum(row["resolved"] is None for row in summaries),
            "sphinx": {
                row["arm"]: row["resolved"] for row in summaries
                if row["instance_id"] == "sphinx-doc__sphinx-9230"
            },
            "django": {
                row["arm"]: row["resolved"] for row in summaries
                if row["instance_id"] == "django__django-11880"
            },
            "used_for_implementation_qualification": False,
        },
        "decision": decision,
        "authorization": {
            "full_p1_preregistration_authorized": qualified,
            "full_p1_execution_authorized": False,
            "paper_result_claim_authorized": False,
            "q4_q5_reclassified": False,
        },
        "scientific_boundary": {
            "q10_is_runtime_implementation_qualification_only": True,
            "r0_r1_r2_r3_behavioral_claim_authorized": False,
            "r4_performance_claim_authorized": False,
            "scientific_belief_update": "none",
        },
        "credential_material_present": False,
    }
    adjudication_sha = write_json(output, payload)
    manifest_rows = _artifact_rows(index)
    manifest_sha = write_json(manifest, {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-P1-Q10-ARTIFACT-MANIFEST-20260831",
        "created_at_utc": utcnow(),
        "artifact_count": len(manifest_rows),
        "artifacts": manifest_rows,
        "all_artifacts_sha256_verified": all(
            row["hash_matches"] for row in manifest_rows
        ),
        "adjudication_sha256": adjudication_sha,
        "credential_material_present": False,
    })
    failed_runs = [
        {
            "run_id": row["run_id"],
            "failed_checks": [
                key for key, value in row["implementation_checks"].items() if not value
            ],
            "failure": row["failure"],
        }
        for row in summaries if not row["implementation_valid"]
    ]
    differential_sha = write_json(differential, {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-P1-Q10-FAILURE-DIFFERENTIAL-20260831",
        "created_at_utc": utcnow(),
        "q10_adjudication_sha256": adjudication_sha,
        "q10_artifact_manifest_sha256": manifest_sha,
        "implementation_qualified": qualified,
        "failed_runs": failed_runs,
        "classification": (
            {"failure_present": False, "primary_failure_layer": None}
            if qualified else {
                "failure_present": True,
                "primary_failure_layer": (
                    "execution substrate / Docker daemon transport instability"
                    if not checks["all_reconciliation_events_fail_closed"]
                    else "implementation/runtime"
                ),
            }
        ),
        "scientific_belief_update": "none",
        "task_outcomes_used_for_classification": False,
        "q4_q5_preserved_unchanged": True,
        "credential_material_present": False,
    })
    memory_sha = write_json(memory, {
        "schema_version": 1,
        "memory_id": "E1-STRI-REASONINGBANK-Q2-Q3-Q4-Q5-Q10-FAILURE-DIFFERENTIAL-20260831",
        "created_at_utc": utcnow(),
        "canonical_lesson": CANONICAL_LESSON,
        "reconciliation_lesson": RECONCILIATION_LESSON,
        "bindings": {
            "q5_scientific_memory_sha256": sha256_file(Q5_MEMORY),
            "q10_contract_sha256": Q10_CONTRACT_SHA256,
            "q10_fault_gate_sha256": sha256_file(FAULT_GATE),
            "q10_smoke_sha256": sha256_file(SMOKE),
            "q10_authority_sha256": sha256_file(AUTHORITY),
            "q10_index_sha256": sha256_file(index_path),
            "q10_adjudication_sha256": adjudication_sha,
            "q10_failure_differential_sha256": differential_sha,
        },
        "sequence": [
            {
                "stage": "Q4",
                "disposition": "evaluator observability failure; no scientific belief update",
            },
            {
                "stage": "Q5",
                "disposition": (
                    "observability repaired; one Docker start acknowledgement "
                    "failure; no scientific belief update"
                ),
            },
            {
                "stage": "Q6-Q9",
                "disposition": (
                    "bounded acknowledgement-window qualification history; "
                    "timeout magnitude alone was insufficient"
                ),
            },
            {
                "stage": "Q10",
                "disposition": (
                    "prospective daemon-side start reconciliation qualified"
                    if qualified
                    else "prospective reconciliation failed; no scientific conclusion"
                ),
            },
        ],
        "scientific_authority": False,
        "experiment_authority": False,
        "credential_material_present": False,
    })
    return {
        "decision": decision,
        "implementation_qualified": qualified,
        "file_sha256": adjudication_sha,
        "manifest_sha256": manifest_sha,
        "failure_differential_sha256": differential_sha,
        "scientific_memory_sha256": memory_sha,
        "resolved_count": payload["descriptive_task_outcomes"]["resolved_count"],
        "reconciliation_event_count": len(reconciled),
    }


def main() -> None:
    print(json.dumps(adjudicate(), sort_keys=True))


if __name__ == "__main__":
    main()
