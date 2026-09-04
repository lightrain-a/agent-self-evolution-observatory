from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_direct_flash_v4_closeout import OUTPUT as CREDIT_STOP
from research_pipeline.agent_constraint_externality_direct_sfq_a0_build import (
    CONTRACT_OUTPUT as SFQ_CONTRACT,
    QUAL_OUTPUT as SFQ_QUAL,
)
from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_value

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
OUTPUT = GENERATED / "agent-constraint-externality-direct-qwen37flash-v4-r2-recovery-proposal-20260903.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verified(path: Path, status: str | None = None) -> dict[str, Any]:
    payload = read_json(path)
    if payload.get("object_id") != OBJECT_ID:
        raise RuntimeError(f"Object mismatch: {path}")
    claimed = payload.get("content_sha256")
    unsigned = dict(payload); unsigned.pop("content_sha256", None)
    if claimed != sha256_value(unsigned):
        raise RuntimeError(f"Content hash mismatch: {path}")
    if status is not None and payload.get("status") != status:
        raise RuntimeError(f"Status mismatch: {path}: {payload.get('status')}")
    return payload


def build() -> dict[str, Any]:
    stop = verified(CREDIT_STOP, "DIRECT_QWEN37FLASH_V4_R1_PROVIDER_CREDIT_EXHAUSTED_STOP")
    sfq = verified(SFQ_CONTRACT, "DIRECT_SFQ_A0_STATIC_DESIGN_READY_PROVIDER_CREDIT_BLOCKED")
    qual = verified(
        SFQ_QUAL,
        "DIRECT_SFQ_A0_PUBLIC_REACHABILITY_AND_FRESHNESS_PASS_EXECUTION_BLOCKED",
    )
    payload: dict[str, Any] = {
        "schema_version": "ace-direct-qwen37flash-v4-r2-recovery-proposal-v1",
        "object_id": OBJECT_ID,
        "status": "DIRECT_QWEN37FLASH_V4_R2_RECOVERY_PROPOSAL_WAIT_PROVIDER_CREDIT",
        "prior_execution_id": stop["execution_id"],
        "prior_stop_content_sha256": stop["content_sha256"],
        "prior_valid_capability_measurements": 0,
        "prior_scientific_model_responses": 0,
        "prior_appworld_actions_after_dispatch": 0,
        "prior_failure_class": "ACCOUNT_LEVEL_INSUFFICIENT_CREDIT_BEFORE_MODEL_RESPONSE",
        "candidate": {
            "model_id": "qwen3.7-flash",
            "provider": "TYPICAL_TOKEN_OPENAI_RESPONSES_API",
            "base_url": "https://api.aa.com.cn/api/v1",
            "harness": "APPWORLD_DIRECT_FUNCTION_CALLING_V4",
        },
        "recovery_execution": {
            "execution_id": "DIRECT-QWEN37FLASH-CAPABILITY-V4-R2-CREDIT-RECOVERY",
            "new_ledger_required": True,
            "old_r1_ledger_is_read_only_failure_evidence": True,
            "same_eight_capability_units": True,
            "clean_snapshot_each_unit": True,
            "reexecute_r1_failed_logical_unit": (
                "ONLY_UNDER_FUTURE_EXPLICIT_R2_EXECUTION_AUTHORITY_BECAUSE_R1_RECEIVED_NO_MODEL_RESPONSE_AND_EXECUTED_NO_APPWORLD_ACTION"
            ),
            "historical_invalid_flash_measurements_reused": False,
            "r1_credit_failure_used_as_model_selection_evidence": False,
            "tool_call_cap": 16,
            "temperature": 0,
            "provider_max_retries": 0,
            "application_retry": False,
            "replacement": False,
        },
        "credit_readiness_gate": {
            "required_before_execution_contract": True,
            "test_type": "NON_SCIENTIFIC_SYNTHETIC_RESPONSES_REQUEST",
            "model": "qwen3.7-flash",
            "tools": 0,
            "max_retries": 0,
            "pass_condition": "HTTP_2XX_WITH_COMPLETED_MODEL_RESPONSE",
            "fail_condition": "ANY_HTTP_OR_PROVIDER_ERROR",
            "credit_check_outcome_must_be_frozen_before_R2_SCIENTIFIC_DISPATCH": True,
        },
        "downstream_static_design": {
            "direct_sfq_a0_contract_content_sha256": sfq["content_sha256"],
            "direct_sfq_a0_qualification_content_sha256": qual["content_sha256"],
            "direct_sfq_a0_execution_requires_R2_capability_pass": True,
        },
        "scientific_outcomes_observed": 0,
        "authority": {
            "credit_readiness_check": False,
            "direct_flash_v4_r2_execution": False,
            "direct_sfq_a0_execution": False,
            "f0_r1": False,
            "p1": False,
            "paper_claim": False,
            "design_only": True,
        },
        "next_authorized_action": "WAIT_FOR_OR_RESTORE_DIRECT_PROVIDER_CREDIT_THEN_RUN_SEPARATELY_AUTHORIZED_NON_SCIENTIFIC_CREDIT_READINESS_CHECK",
    }
    payload["content_sha256"] = sha256_value(payload)
    return payload


def main() -> None:
    payload = build()
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "execution_authorized": payload["authority"]["direct_flash_v4_r2_execution"],
        "direct_sfq_a0_execution_authorized": payload["authority"]["direct_sfq_a0_execution"],
        "next_authorized_action": payload["next_authorized_action"],
        "content_sha256": payload["content_sha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
