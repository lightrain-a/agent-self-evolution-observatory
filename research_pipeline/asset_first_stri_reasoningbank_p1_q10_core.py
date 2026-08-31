"""Q10 evaluator replay over frozen Q4/Q5 sources with reconciled start receipts."""

from __future__ import annotations

import copy
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT, sha256_file, sha256_text,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_prepare import (
    CONTRACT, EXPECTED_ORDER, Q5_INDEX, load_payload, verify_history,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_eval import evaluate
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_runtime import (
    DaemonReconciledDockerRun, Q10_CONTRACT_SHA256,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q5_core import (
    apply_patch, fixture_by_id, image_digest_visible, official_and_local_maps,
    repaired_fixture, verify_q5_contract,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q5_prepare import (
    CONTRACT as Q5_CONTRACT, FIXTURES, SPHINX_AFTER, SPHINX_BEFORE,
)

ARMS = ("A", "B", "C", "D", "E")


def verify_q10_contract() -> dict[str, Any]:
    if sha256_file(CONTRACT) != Q10_CONTRACT_SHA256:
        raise RuntimeError("Q10 contract SHA-256 drift")
    contract = load_payload(CONTRACT)
    if not (
        contract["decision"]
        == "P1_Q10_DOCKER_START_DAEMON_RECONCILIATION_PREREGISTERED"
        and contract["single_changed_variable"]["variable"]
        == "Docker start acknowledgement acceptance rule"
        and contract["single_changed_variable"]["timeout_duration_changed"] is False
        and contract["exactly_once_invariants"]["client_start_invocations"] == 1
        and contract["exactly_once_invariants"]["second_start_forbidden"] is True
        and contract["authorization"]["q10_replay_execution_authorized"] is False
        and len(contract["frozen_replay_sources"]) == 10
    ):
        raise RuntimeError("Q10 contract semantic drift")
    order = [
        (row["selection_rank"], row["instance_id"], row["arm"])
        for row in contract["frozen_replay_sources"]
    ]
    if order != EXPECTED_ORDER:
        raise RuntimeError("Q10 replay order drift")
    history = verify_history()
    q5 = verify_q5_contract()
    return {
        "contract_sha256": Q10_CONTRACT_SHA256,
        "q5_contract_sha256": q5["contract_sha256"],
        "q5_index_sha256": sha256_file(Q5_INDEX),
        "source_checks": q5["source_checks"],
        "history_checks": history,
        "pass": bool(
            q5["pass"]
            and all(row["pass"] for row in history.values())
            and all(row["pass"] for row in q5["source_checks"])
        ),
    }


def replay_one(
    source: dict[str, Any],
    fixture: dict[str, Any],
    run_id: str,
) -> dict[str, Any]:
    source_path = ROOT / source["source_run_path"]
    source_q4_sha = sha256_file(source_path)
    if source_q4_sha != source["source_run_sha256"]:
        raise RuntimeError("source run SHA drift")
    q4 = load_payload(source_path)
    patch = q4["result"]
    if sha256_text(patch) != source["source_patch_sha256"]:
        raise RuntimeError("source patch SHA drift")
    if q4["task_sha256"] != source["task_sha256"]:
        raise RuntimeError("source task SHA drift")
    if fixture["image_amd64_manifest_digest"] != source["image_amd64_manifest_digest"]:
        raise RuntimeError("image digest drift")
    if fixture["model_visible"]["base_commit"] != source["base_commit"]:
        raise RuntimeError("base commit drift")
    repaired = repaired_fixture(fixture)
    original_script = fixture["evaluator_only"]["eval_script"]
    repaired_script = repaired["evaluator_only"]["eval_script"]
    container = DaemonReconciledDockerRun(
        fixture["image_pull_reference"],
        source["base_commit"],
        run_id,
        source["image_amd64_manifest_digest"],
        exact_base=True,
    )
    start: dict[str, Any] | None = None
    application: dict[str, Any] | None = None
    applied: dict[str, Any] | None = None
    outcome: dict[str, Any] | None = None
    official: dict[str, str] = {}
    local: dict[str, str] = {}
    coverage: dict[str, str] = {}
    failure: dict[str, Any] | None = None
    checks: dict[str, bool] = {}
    try:
        start = container.start()
        application = apply_patch(container, patch)
        if application["returncode"] != 0 or application["timed_out"]:
            raise RuntimeError("frozen Q4 result patch application failed")
        applied = container.exec(
            "git -c core.fileMode=false diff --binary HEAD",
            timeout=60,
        )
        if (
            applied["returncode"] != 0
            or applied["timed_out"]
            or sha256_text(applied["output"]) != sha256_text(patch)
        ):
            raise RuntimeError("applied Q4 patch differs from frozen patch")
        outcome = evaluate(container, repaired)
        official, local = official_and_local_maps(
            fixture["evaluator_only"]["log_parser"],
            outcome["raw_execution"]["output"],
        )
        expected = (
            fixture["evaluator_only"]["FAIL_TO_PASS"]
            + fixture["evaluator_only"]["PASS_TO_PASS"]
        )
        coverage = {case: official.get(case, "MISSING") for case in expected}
        start_receipt = start["q10_start_reconciliation"]
        checks = {
            "source_run_sha_exact": source_q4_sha == source["source_run_sha256"],
            "source_patch_sha_exact": sha256_text(patch) == source["source_patch_sha256"],
            "task_fixture_sha_exact": sha256_file(FIXTURES)
            == load_payload(Q5_CONTRACT)["bindings"]["fixtures_sha256"],
            "image_digest_exact": image_digest_visible(
                start, source["image_amd64_manifest_digest"]
            ),
            "base_commit_exact": (
                start["base_commit_receipt"]["observed_head"] == source["base_commit"]
                and start["base_commit_receipt"]["rule"]
                == "exact_base_after_preregistered_hard_reset"
            ),
            "start_invoked_exactly_once": (
                start_receipt["client_start_invocations"] == 1
            ),
            "second_start_not_invoked": (
                start_receipt["second_start_invoked"] is False
            ),
            "start_receipt_finalized": (
                start_receipt["receipt_finalized"] is True
                and start_receipt["accepted"] is True
            ),
            "exact_container_identity": (
                start_receipt["exact_identity_verified"] is True
            ),
            "exact_daemon_running_state": (
                start_receipt["exact_running_state_verified"] is True
            ),
            "patch_applied_exactly": True,
            "test_patch_sha_exact": outcome["test_patch_sha256"]
            == sha256_text(fixture["evaluator_only"]["test_patch"]),
            "official_status_map_nonempty": len(official) > 0,
            "official_local_parser_exact": official == local == outcome["status_map"],
            "required_case_coverage_sufficient": all(
                value != "MISSING" for value in coverage.values()
            ),
            "evaluator_terminated": (
                not outcome["raw_execution"]["timed_out"]
                and outcome["raw_execution"]["returncode"] == 0
            ),
            "command_change_exact": (
                repaired_script == original_script.replace(SPHINX_BEFORE, SPHINX_AFTER)
                if fixture["instance_id"] == "sphinx-doc__sphinx-9230"
                else repaired_script == original_script
            ),
            "model_provider_calls_zero": True,
        }
    except Exception as error:
        failure = {"error_type": type(error).__name__, "message": str(error)}
    finally:
        cleanup = container.close()
    checks["cleanup_after_reconciliation_receipt"] = bool(
        cleanup["cleanup_invoked"] is True
        and cleanup["reconciliation_receipt_finalized_before_cleanup"] is True
        and cleanup["accepted"] is True
    )
    implementation_valid = bool(
        failure is None and checks and all(checks.values())
    )
    return {
        "schema_version": 1,
        "run_id": run_id,
        "instance_id": source["instance_id"],
        "arm": source["arm"],
        "selection_rank": source["selection_rank"],
        "source_q4": copy.deepcopy(source),
        "source_q4_run_sha256": source_q4_sha,
        "source_q5_contract_sha256": verify_q5_contract()["contract_sha256"],
        "source_q5_index_sha256": sha256_file(Q5_INDEX),
        "q10_contract_sha256": Q10_CONTRACT_SHA256,
        "source_patch_sha256": sha256_text(patch),
        "task_sha256": source["task_sha256"],
        "fixture_sha256": sha256_file(FIXTURES),
        "image": fixture["image_pull_reference"],
        "image_digest": source["image_amd64_manifest_digest"],
        "base_commit": source["base_commit"],
        "runtime_start": start,
        "start_reconciliation_receipt": (
            start["q10_start_reconciliation"]
            if start is not None
            else container.start_reconciliation_receipt
        ),
        "patch_application": application,
        "applied_patch_sha256": (
            sha256_text(applied["output"]) if applied is not None else None
        ),
        "original_eval_script_sha256": sha256_text(original_script),
        "repaired_eval_script_sha256": sha256_text(repaired_script),
        "official_parser_status_map": official,
        "local_parser_status_map": local,
        "required_case_status": coverage,
        "R4_terminal_outcome": outcome,
        "cleanup_receipt": cleanup,
        "implementation_checks": checks,
        "implementation_valid": implementation_valid,
        "failure": failure,
        "resolved": outcome.get("resolved") if outcome is not None else None,
        "task_outcome_affects_qualification": False,
        "attempt_count": 1,
        "model_calls": 0,
        "provider_calls": 0,
        "credential_material_present": False,
    }
