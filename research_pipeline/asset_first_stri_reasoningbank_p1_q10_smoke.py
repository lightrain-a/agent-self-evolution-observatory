"""One-shot non-scientific Q10 daemon-state reconciliation smoke."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT, sha256_file, utcnow, write_json,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_fault_gate import (
    OUTPUT as FAULT_GATE,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_prepare import (
    CONTRACT, load_payload, verify_history,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_runtime import (
    DaemonReconciledDockerRun, Q10_CONTRACT_SHA256,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q5_core import (
    fixture_by_id, verify_q5_contract,
)

SMOKE = ROOT / "generated/asset-first-stri-reasoningbank-p1-q10-daemon-state-reconciliation-smoke-20260831.json"
RECEIPT_FIELDS = {
    "client_start_invocations",
    "client_returncode",
    "client_timed_out",
    "client_output",
    "reconciliation_invoked",
    "docker_inspect_invoked",
    "container_id",
    "container_name",
    "expected_image",
    "observed_image",
    "expected_image_digest",
    "observed_image_digests",
    "expected_pid_mode",
    "observed_pid_mode",
    "daemon_status",
    "daemon_running",
    "daemon_pid",
    "restart_count",
    "exact_identity_verified",
    "exact_running_state_verified",
    "second_start_invoked",
    "accepted",
    "acceptance_rule",
    "receipt_finalized",
    "contract_sha256",
}


def run_smoke(output: Path = SMOKE) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError(f"refusing to overwrite immutable Q10 smoke: {output}")
    if sha256_file(CONTRACT) != Q10_CONTRACT_SHA256:
        raise RuntimeError("Q10 contract SHA drift")
    contract = load_payload(CONTRACT)
    if contract["authorization"]["q10_live_smoke_authorized"] is not True:
        raise RuntimeError("Q10 live-smoke authority is closed")
    fault = load_payload(FAULT_GATE)
    if not (
        fault["decision"] == "Q10_DETERMINISTIC_FAULT_GATE_PASS"
        and fault["pass"] is True
        and fault["test_count"] == 10
        and all(row["pass"] for row in fault["cases"])
    ):
        raise RuntimeError("Q10 deterministic fault gate is closed")
    history = verify_history()
    q5_verification = verify_q5_contract()
    fixture = fixture_by_id()["sphinx-doc__sphinx-9230"]
    container = DaemonReconciledDockerRun(
        fixture["image_pull_reference"],
        fixture["model_visible"]["base_commit"],
        "q10-nonscientific-daemon-state-reconciliation-smoke",
        fixture["image_amd64_manifest_digest"],
        exact_base=True,
    )
    start: dict[str, Any] | None = None
    exact_base: dict[str, Any] | None = None
    exec_probe: dict[str, Any] | None = None
    failure: dict[str, Any] | None = None
    try:
        start = container.start()
        exact_base = container.exec(
            f'test "$(git rev-parse HEAD)" = "{fixture["model_visible"]["base_commit"]}" '
            '&& test -z "$(git status --porcelain=v1 --untracked-files=all)" '
            "&& git rev-parse HEAD",
            timeout=30,
        )
        exec_probe = container.exec(
            "printf Q10_DAEMON_STATE_RECONCILIATION_EXEC_OK",
            timeout=30,
        )
    except Exception as error:
        failure = {"error_type": type(error).__name__, "message": str(error)}
    finally:
        cleanup = container.close()
    start_receipt = (
        start["q10_start_reconciliation"]
        if start is not None
        else container.start_reconciliation_receipt
    )
    create_receipt = (
        start["q6_create_acknowledgement"] if start is not None else None
    )
    checks = {
        "contract_exact": sha256_file(CONTRACT) == Q10_CONTRACT_SHA256,
        "fault_injection_gate_pass": fault["pass"] is True,
        "q4_q5_q9_history_exact": all(row["pass"] for row in history.values()),
        "q5_source_artifacts_exact": q5_verification["pass"] is True,
        "exact_image_and_digest": bool(
            start_receipt
            and start_receipt["expected_image"] == fixture["image_pull_reference"]
            and start_receipt["expected_image_digest"]
            == fixture["image_amd64_manifest_digest"]
            and start_receipt["exact_identity_verified"] is True
        ),
        "exact_create_configuration": bool(
            create_receipt
            and create_receipt["client_create_invocations"] == 1
            and create_receipt["second_create_invoked"] is False
            and create_receipt["accepted"] is True
        ),
        "start_invoked_exactly_once": bool(
            start_receipt
            and start_receipt["client_start_invocations"] == 1
        ),
        "second_start_forbidden_observed": bool(
            start_receipt
            and start_receipt["second_start_invoked"] is False
        ),
        "normal_or_reconciled_exact_running_state": bool(
            start_receipt
            and start_receipt["accepted"] is True
            and start_receipt["exact_running_state_verified"] is True
        ),
        "exact_base_normalization": bool(
            start
            and start["base_commit_receipt"]["observed_head"]
            == fixture["model_visible"]["base_commit"]
            and exact_base
            and exact_base["returncode"] == 0
            and not exact_base["timed_out"]
            and exact_base["output"].strip()
            == fixture["model_visible"]["base_commit"]
        ),
        "docker_exec_works": bool(
            exec_probe
            and exec_probe["returncode"] == 0
            and not exec_probe["timed_out"]
            and exec_probe["output"] == "Q10_DAEMON_STATE_RECONCILIATION_EXEC_OK"
        ),
        "receipt_complete": bool(
            start_receipt
            and RECEIPT_FIELDS.issubset(start_receipt)
            and start_receipt["receipt_finalized"] is True
        ),
        "cleanup_after_receipt_finalization": bool(
            cleanup["cleanup_invoked"] is True
            and cleanup["reconciliation_receipt_finalized_before_cleanup"] is True
            and cleanup["accepted"] is True
        ),
        "model_provider_calls_zero": True,
        "no_scientific_or_task_outcome_authority": True,
    }
    passed = failure is None and all(checks.values())
    payload = {
        "schema_version": 1,
        "experiment_id": "NON_SCIENTIFIC_Q10_DAEMON_STATE_RECONCILIATION_SMOKE-20260831",
        "created_at_utc": utcnow(),
        "q10_contract_sha256": Q10_CONTRACT_SHA256,
        "fault_gate_sha256": sha256_file(FAULT_GATE),
        "verification": {
            "history": history,
            "q5_sources": q5_verification,
        },
        "fixture": {
            "instance_id": fixture["instance_id"],
            "image": fixture["image_pull_reference"],
            "image_digest": fixture["image_amd64_manifest_digest"],
            "base_commit": fixture["model_visible"]["base_commit"],
            "source_patch_applied": False,
            "test_patch_applied": False,
        },
        "runtime_start": start,
        "start_reconciliation_receipt": start_receipt,
        "exact_base_probe": exact_base,
        "docker_exec_probe": exec_probe,
        "cleanup_receipt": cleanup,
        "checks": checks,
        "pass": passed,
        "decision": (
            "Q10_DAEMON_STATE_RECONCILIATION_SMOKE_PASS"
            if passed else "Q10_DAEMON_STATE_RECONCILIATION_SMOKE_HOLD"
        ),
        "failure": failure,
        "scientific_authority": False,
        "paper_authority": False,
        "mechanism_authority": False,
        "task_outcome_authority": False,
        "model_calls": 0,
        "provider_calls": 0,
        "credential_material_present": False,
    }
    file_sha = write_json(output, payload)
    return {
        "decision": payload["decision"],
        "pass": passed,
        "file_sha256": file_sha,
    }


def main() -> None:
    print(json.dumps(run_smoke(), sort_keys=True))


if __name__ == "__main__":
    main()
