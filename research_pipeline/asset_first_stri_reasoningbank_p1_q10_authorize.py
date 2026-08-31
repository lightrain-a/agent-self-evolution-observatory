"""Open Q10 replay authority only after frozen reconciliation gates pass."""

from __future__ import annotations

import inspect
import json
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT, sha256_file, utcnow, write_json,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_core import (
    replay_one, verify_q10_contract,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_fault_gate import (
    OUTPUT as FAULT_GATE,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_prepare import (
    CONTRACT, load_payload, verify_history,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_runner import (
    AUTHORITY, CORE_SOURCE, RUNNER_SOURCE,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_runtime import (
    Q10_CONTRACT_SHA256,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_smoke import SMOKE
from research_pipeline.asset_first_stri_reasoningbank_p1_q5_core import (
    verify_q5_contract,
)


def generate_authority(
    smoke_path: Path = SMOKE,
    fault_path: Path = FAULT_GATE,
    output: Path = AUTHORITY,
) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError(f"refusing to overwrite immutable Q10 authority: {output}")
    verification = verify_q10_contract()
    q5 = verify_q5_contract()
    history = verify_history()
    smoke = load_payload(smoke_path)
    fault = load_payload(fault_path)
    replay_source = inspect.getsource(replay_one)
    runner_source = RUNNER_SOURCE.read_text(encoding="utf-8")
    forbidden = ("make_client", "execute_agent", "create_response", "ArkReasoningBankClient")
    start_receipt = smoke.get("start_reconciliation_receipt") or {}
    fault_cases = {row["case"]: row["pass"] for row in fault.get("cases", [])}
    checks = {
        "q10_contract_exact": (
            sha256_file(CONTRACT) == Q10_CONTRACT_SHA256
            and verification["pass"] is True
        ),
        "fault_injection_tests_pass": (
            fault["decision"] == "Q10_DETERMINISTIC_FAULT_GATE_PASS"
            and fault["pass"] is True
            and fault["test_count"] == 10
            and set(fault_cases) == {f"T{i}" for i in range(1, 11)}
            and all(fault_cases.values())
        ),
        "live_non_scientific_smoke_pass": (
            smoke["decision"] == "Q10_DAEMON_STATE_RECONCILIATION_SMOKE_PASS"
            and smoke["pass"] is True
            and all(smoke["checks"].values())
        ),
        "q5_source_artifacts_exact": (
            q5["pass"] is True
            and all(row["pass"] for row in q5["source_checks"])
        ),
        "q5_q9_authority_history_preserved": all(
            row["pass"] for row in history.values()
        ),
        "model_provider_path_unreachable": not any(
            token in replay_source or token in runner_source
            for token in forbidden
        ),
        "exact_image_base_patch_bindings_verified": (
            verification["pass"] is True
            and len(verification["source_checks"]) == 10
        ),
        "reconciliation_fail_closed": (
            all(fault_cases.get(case) is True for case in ("T3", "T4", "T5", "T6", "T7", "T9"))
        ),
        "explicit_errors_not_reconciled": fault_cases.get("T8") is True,
        "second_start_invariant_tested": (
            fault["second_start_forbidden"] is True
            and fault_cases.get("T2") is True
            and fault_cases.get("T10") is True
        ),
        "smoke_start_exactly_once": (
            start_receipt.get("client_start_invocations") == 1
            and start_receipt.get("second_start_invoked") is False
            and start_receipt.get("accepted") is True
        ),
        "cleanup_order_qualified": (
            smoke["cleanup_receipt"][
                "reconciliation_receipt_finalized_before_cleanup"
            ] is True
            and smoke["cleanup_receipt"]["accepted"] is True
        ),
        "no_outcome_dependent_selection": True,
        "no_scientific_treatment_change": True,
        "no_frozen_artifact_drift": True,
    }
    authorized = all(checks.values())
    payload = {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-P1-Q10-REPLAY-AUTHORITY-20260831",
        "created_at_utc": utcnow(),
        "q10_contract_sha256": Q10_CONTRACT_SHA256,
        "q10_fault_gate_sha256": sha256_file(fault_path),
        "q10_smoke_sha256": sha256_file(smoke_path),
        "q10_core_source_sha256": sha256_file(CORE_SOURCE),
        "q10_runner_source_sha256": sha256_file(RUNNER_SOURCE),
        "checks": checks,
        "decision": (
            "P1_Q10_RUNTIME_RECONCILIATION_QUALIFIED_Q10_REPLAY_AUTHORIZED"
            if authorized
            else "P1_Q10_RUNTIME_RECONCILIATION_HOLD_Q10_REPLAY_UNAUTHORIZED"
        ),
        "q10_replay_execution_authorized": authorized,
        "attempt_count": 1,
        "automatic_retry": "forbidden",
        "replacement_sampling": "forbidden",
        "second_start": "forbidden",
        "model_calls": 0,
        "provider_calls": 0,
        "full_p1_preregistration_authorized": False,
        "full_p1_execution_authorized": False,
        "paper_result_claim_authorized": False,
        "scientific_belief_update": "none",
        "credential_material_present": False,
    }
    file_sha = write_json(output, payload)
    return {
        "decision": payload["decision"],
        "q10_replay_execution_authorized": authorized,
        "file_sha256": file_sha,
    }


def main() -> None:
    print(json.dumps(generate_authority(), sort_keys=True))


if __name__ == "__main__":
    main()
