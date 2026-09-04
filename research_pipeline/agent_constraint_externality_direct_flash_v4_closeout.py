from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_direct_flash_v4 import (
    AUTH_OUTPUT,
    CATALOG_OUTPUT,
    CONTRACT_OUTPUT,
    EXECUTION_ID,
    MODEL_ID,
)
from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
RUNTIME = ROOT / "runtimes/agent-constraint-externality-direct-qwen37flash-capability-v4-r1-20260903"
LEDGER = RUNTIME / "ledger.jsonl"
OUTPUT = GENERATED / "agent-constraint-externality-direct-qwen37flash-capability-v4-r1-credit-stop-20260903.json"


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
    contract = verified(CONTRACT_OUTPUT, "DIRECT_QWEN37FLASH_CAPABILITY_V4_R1_AUTHORIZED")
    catalog = verified(CATALOG_OUTPUT, "DIRECT_QWEN37FLASH_CATALOG_V4_R1_PASS")
    auth = verified(AUTH_OUTPUT, "USER_CONTINUE_AUTHORIZED_DIRECT_QWEN37FLASH_V4_REQUALIFICATION")
    rows = [json.loads(line) for line in LEDGER.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(rows) != 2 or [row.get("event") for row in rows] != ["DISPATCH", "FAILURE"]:
        raise RuntimeError("Expected exactly one dispatch plus one terminal provider failure.")
    dispatch, failure = rows
    expected_unit = f"capability:{MODEL_ID}|ACE-FG-05|1"
    if dispatch.get("unit_id") != expected_unit or failure.get("unit_id") != expected_unit:
        raise RuntimeError("Credit-stop unit identity drifted.")
    if failure.get("failure_class") != "ProviderCallError" or failure.get("retry_attempted") is not False:
        raise RuntimeError("Credit-stop ledger failure classification drifted.")
    payload: dict[str, Any] = {
        "schema_version": "ace-direct-qwen37flash-v4-r1-credit-stop-v1",
        "object_id": OBJECT_ID,
        "execution_id": EXECUTION_ID,
        "status": "DIRECT_QWEN37FLASH_V4_R1_PROVIDER_CREDIT_EXHAUSTED_STOP",
        "classification": "PROVIDER_ACCOUNT_CREDIT_BLOCKER_NOT_MODEL_CAPABILITY_OUTCOME",
        "provider": contract["provider"],
        "base_url": contract["base_url"],
        "model_id": MODEL_ID,
        "harness": contract["harness"],
        "catalog_content_sha256": catalog["content_sha256"],
        "authorization_content_sha256": auth["content_sha256"],
        "contract_content_sha256": contract["content_sha256"],
        "ledger_sha256": sha256_file(LEDGER),
        "scientific_dispatch_count": 1,
        "terminal_failure_count": 1,
        "valid_capability_measurements": 0,
        "never_dispatched_unit_count": 7,
        "failed_unit_id": expected_unit,
        "provider_error_evidence": {
            "http_status": 400,
            "provider_error_code": "insufficient_credit",
            "provider_error_type": "invalid_request_error",
            "provider_error_message_class": "USER_CREDIT_NOT_ENOUGH",
            "synthetic_no_tools_diagnostic_confirmed_same_error": True,
            "model_or_function_schema_incompatibility_inferred": False,
        },
        "retry": False,
        "replacement": False,
        "replay_current_failed_unit": False,
        "scientific_outcomes_observed": 0,
        "interpretation_boundary": (
            "The first qwen3.7-flash V4 capability unit never produced a model response or AppWorld scientific measurement. "
            "The provider returned account-level insufficient_credit; no statement about Flash capability is permitted."
        ),
        "recovery_rule": (
            "Do not replay or continue this execution ID. If provider credit becomes available, freeze a new prospective recovery execution "
            "with explicit disposition for the already-dispatched unit and no outcome reuse."
        ),
        "authority": {
            "continue_execution_id": False,
            "replay_failed_unit": False,
            "source_failure_qualification": False,
            "f0_r1": False,
            "p1": False,
            "paper_claim": False,
            "static_design_work": True,
        },
        "next_authorized_action": "STATICALLY_QUALIFY_FRESH_DIRECT_SOURCE_FAILURE_CASES_WHILE_PROVIDER_CREDIT_BLOCKED",
    }
    payload["content_sha256"] = sha256_value(payload)
    return payload


def main() -> None:
    payload = build()
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "valid_capability_measurements": 0,
        "never_dispatched_unit_count": payload["never_dispatched_unit_count"],
        "scientific_outcomes_observed": 0,
        "next_authorized_action": payload["next_authorized_action"],
        "content_sha256": payload["content_sha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
