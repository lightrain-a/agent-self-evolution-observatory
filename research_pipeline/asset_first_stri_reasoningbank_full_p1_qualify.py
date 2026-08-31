"""Qualify Full-P1 runtime, parser families, and frozen provider without task behavior."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_ark_provider import (
    ArkReasoningBankSettings,
    CANONICAL_SECRET_FILE,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    BASE_URL,
    MAX_RETRIES,
    MODEL,
    ROOT,
    sha256_file,
    utcnow,
    write_json,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_runtime import (
    DaemonReconciledDockerRun,
)

POPULATION = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-population-and-image-freeze-20260831.json"
PREREGISTRATION = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-behavioral-propagation-preregistration-20260831.json"
ACQUISITION = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-runtime-acquisition-repair-result-20260831.json"
Q10_FAULTS = ROOT / "generated/asset-first-stri-reasoningbank-p1-q10-fault-tests-20260831.json"
Q10_ADJUDICATION = ROOT / "generated/asset-first-stri-reasoningbank-p1-q10-adjudication-20260831.json"
Q10_INDEX = ROOT / "generated/asset-first-stri-reasoningbank-p1-q10-index-20260831.json"
Q10_RUN_DIR = ROOT / "generated/asset-first-stri-reasoningbank-p1-q10-runs-20260831"
SOURCE_RUN = ROOT / "generated/asset-first-stri-reasoningbank-p1-runs-20260829/source-sympy__sympy-13798/run.json"
OUTPUT = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-runtime-provider-evaluator-qualification-20260831.json"
EXPECTED = {
    POPULATION: "6ca2a6831e01db63961db3d5c337c17ee790755046c68bbcb6c056e136d8bbe8",
    PREREGISTRATION: "af8e9efb53ad5df5e846329b289ce791bc8ffe7c581f810c0ade1067d09fe7dd",
    Q10_FAULTS: "21deda0aaa883d11a58d7553f4f3217d7694c461ef23e7be48da897e9cf83554",
    Q10_ADJUDICATION: "a92d394ee90ee6d1b5c65ca3deb17c9311649757a1e053ed94cc7c025b0f89c9",
    Q10_INDEX: "faf047da587b7daa0be16c703dabe01d14c7149441c62d2279be26cd75cf8a72",
    SOURCE_RUN: "8de287a4c64437186e9f92856248c7aed95a1e162f90a8e1c9da9b380d73cbf7",
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_static() -> dict[str, Any]:
    checks = {}
    for path, expected in EXPECTED.items():
        actual = sha256_file(path)
        checks[str(path.relative_to(ROOT))] = {
            "expected": expected,
            "actual": actual,
            "pass": actual == expected,
        }
    if not all(row["pass"] for row in checks.values()):
        raise RuntimeError("Full-P1 qualification prerequisite SHA drift")
    return checks


def provider_qualification() -> dict[str, Any]:
    settings = ArkReasoningBankSettings.from_env_file(CANONICAL_SECRET_FILE)
    source = load(SOURCE_RUN)
    responses = source.get("model_responses", [])
    resolved = sorted({row.get("resolved_model") for row in responses})
    passed = bool(
        settings.api_key
        and settings.base_url.rstrip("/") == BASE_URL
        and responses
        and resolved == [MODEL]
    )
    return {
        "configured": bool(settings.api_key),
        "base_url": settings.base_url,
        "frozen_model": MODEL,
        "request_timeout_seconds": 120.0,
        "max_retries": MAX_RETRIES,
        "historical_exact_provider_receipt_path": str(SOURCE_RUN.relative_to(ROOT)),
        "historical_exact_provider_receipt_sha256": sha256_file(SOURCE_RUN),
        "historical_response_count": len(responses),
        "historical_resolved_models": resolved,
        "live_model_call_for_qualification": False,
        "secret_value_exported": False,
        "pass": passed,
    }


def parser_qualification() -> dict[str, Any]:
    index = load(Q10_INDEX)
    run_rows = []
    for receipt in index["completed_runs"]:
        run = load(ROOT / receipt["path"])
        outcome = run["R4_terminal_outcome"]
        run_rows.append({
            "instance_id": run["instance_id"],
            "arm": run["arm"],
            "attempt_count": run["attempt_count"],
            "parser": outcome["log_parser"],
            "evaluator_valid": outcome["valid"],
            "implementation_valid": run["implementation_valid"],
        })
    parsers = sorted({row["parser"] for row in run_rows})
    passed = bool(
        index["execution_complete"] is True
        and len(index["run_journal"]) == len(run_rows) == 10
        and all(row["attempt_count"] == 1 for row in run_rows)
        and all(row["evaluator_valid"] and row["implementation_valid"] for row in run_rows)
        and parsers == ["parse_log_django", "parse_log_sphinx"]
    )
    return {
        "q10_index_sha256": sha256_file(Q10_INDEX),
        "qualified_run_count": len(run_rows),
        "parser_families": parsers,
        "every_attempt_count_one": all(row["attempt_count"] == 1 for row in run_rows),
        "every_evaluator_valid": all(row["evaluator_valid"] for row in run_rows),
        "every_implementation_valid": all(row["implementation_valid"] for row in run_rows),
        "negative_or_positive_task_outcome_ignored": True,
        "pass": passed,
    }


def qualify(output: Path = OUTPUT) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError("refusing duplicate Full-P1 qualification")
    static = verify_static()
    acquisition = load(ACQUISITION)
    if not (
        acquisition["decision"]
        == "FULL_P1_EXACT_IMAGES_READY_AFTER_SINGLE_CHANNEL_REPAIR"
        and acquisition["all_blobs_sha256_verified"] is True
        and acquisition["all_images_imported_by_exact_digest"] is True
    ):
        raise RuntimeError("Full-P1 exact image acquisition gate is closed")
    faults = load(Q10_FAULTS)
    adjudication = load(Q10_ADJUDICATION)
    population = load(POPULATION)["population"]
    provider = provider_qualification()
    parser = parser_qualification()
    runtime_rows = []
    failures = []
    for fixture in population:
        run_id = f"full-p1-preflight-rank-{fixture['selection_rank']:03d}"
        container = DaemonReconciledDockerRun(
            image=fixture["image_pull_reference"],
            base_commit=fixture["model_visible"]["base_commit"],
            run_id=run_id,
            expected_image_digest=fixture["image_amd64_manifest_digest"],
            exact_base=True,
        )
        start = None
        try:
            start = container.start()
            row = {
                "selection_rank": fixture["selection_rank"],
                "instance_id": fixture["instance_id"],
                "image_amd64_manifest_digest": fixture["image_amd64_manifest_digest"],
                "attempt_count": 1,
                "client_start_invocations": start["q10_start_reconciliation"]["client_start_invocations"],
                "reconciliation_invoked": start["q10_start_reconciliation"]["reconciliation_invoked"],
                "second_start_invoked": start["q10_start_reconciliation"]["second_start_invoked"],
                "start_accepted": start["q10_start_reconciliation"]["accepted"],
                "base_state_rule": start["base_commit_receipt"]["rule"],
                "observed_head": start["base_commit_receipt"]["observed_head"],
                "model_calls": 0,
                "evaluator_calls": 0,
            }
            runtime_rows.append(row)
        except Exception as error:
            failures.append({
                "selection_rank": fixture["selection_rank"],
                "instance_id": fixture["instance_id"],
                "error_type": type(error).__name__,
                "message": str(error),
                "start_reconciliation_receipt": container.start_reconciliation_receipt,
            })
        finally:
            cleanup = container.close()
            if runtime_rows and runtime_rows[-1]["instance_id"] == fixture["instance_id"]:
                runtime_rows[-1]["cleanup_receipt"] = cleanup
            elif failures and failures[-1]["instance_id"] == fixture["instance_id"]:
                failures[-1]["cleanup_receipt"] = cleanup
    runtime_pass = bool(
        not failures
        and len(runtime_rows) == 8
        and all(row["attempt_count"] == 1 for row in runtime_rows)
        and all(row["client_start_invocations"] == 1 for row in runtime_rows)
        and all(row["second_start_invoked"] is False for row in runtime_rows)
        and all(row["start_accepted"] is True for row in runtime_rows)
        and all(row["cleanup_receipt"]["accepted"] is True for row in runtime_rows)
    )
    qualified = bool(
        runtime_pass
        and provider["pass"]
        and parser["pass"]
        and faults["decision"] == "Q10_DETERMINISTIC_FAULT_GATE_PASS"
        and faults["pass"] is True
        and adjudication["implementation_qualified"] is True
    )
    payload = {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-FULL-P1-RUNTIME-PROVIDER-EVALUATOR-QUALIFICATION-20260831",
        "created_at_utc": utcnow(),
        "decision": (
            "FULL_P1_RUNTIME_PROVIDER_EVALUATOR_QUALIFIED"
            if qualified
            else "FULL_P1_EXECUTION_QUALIFICATION_HOLD"
        ),
        "static_input_checks": static,
        "acquisition_sha256": sha256_file(ACQUISITION),
        "q10_fault_gate": {
            "sha256": sha256_file(Q10_FAULTS),
            "decision": faults["decision"],
            "test_count": faults["test_count"],
            "pass": faults["pass"],
        },
        "q10_adjudication": {
            "sha256": sha256_file(Q10_ADJUDICATION),
            "decision": adjudication["decision"],
            "implementation_qualified": adjudication["implementation_qualified"],
        },
        "provider_qualification": provider,
        "parser_evaluator_qualification": parser,
        "runtime_preflight": {
            "policy": "one non-scientific start per frozen image; no model or evaluator calls",
            "row_count": len(runtime_rows),
            "rows": runtime_rows,
            "failures": failures,
            "pass": runtime_pass,
        },
        "execution_authorized": False,
        "scientific_boundary": {
            "task_problem_statements_rendered": False,
            "task_outcomes_observed": False,
            "model_calls": 0,
            "evaluator_calls": 0,
            "qualification_is_not_scientific_evidence": True,
        },
        "credential_material_present": False,
    }
    return {
        "decision": payload["decision"],
        "file_sha256": write_json(output, payload),
        "runtime_count": len(runtime_rows),
        "failure_count": len(failures),
    }


def main() -> None:
    print(json.dumps(qualify(), sort_keys=True))


if __name__ == "__main__":
    main()
