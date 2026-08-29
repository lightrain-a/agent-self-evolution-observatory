#!/usr/bin/env python3
"""Direct-identity and causal tool-result probe for Ark DeepSeek-Pro."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_ark_provider import (
    ArkCompatibilityError,
    ArkReasoningBankClient,
    ArkReasoningBankSettings,
    CANONICAL_SECRET_FILE,
)


EXPERIMENT_ID = "E1-STRI-REASONINGBANK-ARK-DEEPSEEK-Q1B-20260829"
DIRECT_MODEL = "deepseek-v4-pro-ga-260813"
FROZEN_VALUE = "DEEPSEEK_TOOL_ONLY_VALUE_8429"
DEFAULT_OUTPUT = Path(
    "generated/asset-first-stri-reasoningbank-deepseek-direct-causal-result-20260829.json"
)
TOOL = {
    "type": "function",
    "name": "fetch_frozen_value",
    "description": "Fetch a value held only by the external environment.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    },
    "strict": True,
}


def sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def safe_row(label: str, result: dict[str, Any]) -> dict[str, Any]:
    text = str(result.get("text") or "")
    return {
        "label": label,
        "ok": True,
        "requested_model": result.get("requested_model"),
        "resolved_model": result.get("resolved_model"),
        "status": result.get("status"),
        "text": text,
        "text_sha256": sha(text),
        "function_calls": [
            {
                "name": call.get("name"),
                "arguments": str(call.get("arguments") or ""),
                "call_id_sha256": sha(str(call.get("call_id") or "")),
            }
            for call in result.get("function_calls") or []
        ],
        "usage": result.get("usage") or {},
        "response_id_sha256": sha(str(result.get("response_id") or "")),
        "credential_material_present": False,
    }


def failed_row(label: str, error: ArkCompatibilityError) -> dict[str, Any]:
    return {
        "label": label,
        "ok": False,
        **error.safe_receipt(),
        "credential_material_present": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, default=CANONICAL_SECRET_FILE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    base = ArkReasoningBankSettings.from_env_file(args.env_file)
    settings = ArkReasoningBankSettings(
        api_key=base.api_key,
        base_url=base.base_url,
        model=DIRECT_MODEL,
        timeout_seconds=base.timeout_seconds,
        max_retries=base.max_retries,
    )
    client = ArkReasoningBankClient(settings)
    rows: list[dict[str, Any]] = []
    live_first: dict[str, Any] | None = None

    try:
        live_first = client.create_response(
            input_items=(
                "Use fetch_frozen_value to obtain the external frozen value. "
                "After the tool result arrives, answer: What is frozen_value?"
            ),
            instructions=(
                "Call fetch_frozen_value exactly once. The frozen value is unavailable "
                "until the tool result arrives. Include the complete frozen_value in the answer."
            ),
            tools=[TOOL],
            tool_choice="required",
            temperature=0.0,
            max_output_tokens=None,
            store=True,
        )
        rows.append(safe_row("tool_call", live_first))
    except ArkCompatibilityError as error:
        rows.append(failed_row("tool_call", error))

    if live_first and live_first.get("function_calls"):
        call = live_first["function_calls"][0]
        try:
            continued = client.continue_function_call(
                previous_response_id=str(live_first["response_id"]),
                call_id=str(call.get("call_id") or ""),
                output=json.dumps(
                    {"frozen_value": FROZEN_VALUE, "source": "qualification_environment"}
                ),
                model=DIRECT_MODEL,
                max_output_tokens=None,
            )
            rows.append(safe_row("tool_result_continuation", continued))
        except ArkCompatibilityError as error:
            rows.append(failed_row("tool_result_continuation", error))
    else:
        rows.append(
            {
                "label": "tool_result_continuation",
                "ok": False,
                "error_type": "PREREQUISITE_TOOL_CALL_MISSING",
                "credential_material_present": False,
            }
        )

    by = {row["label"]: row for row in rows}
    call_row = by["tool_call"]
    continuation = str(by["tool_result_continuation"].get("text") or "")
    pre_call_material = (
        str(call_row.get("text") or "")
        + json.dumps(call_row.get("function_calls") or [], sort_keys=True)
    )
    checks = {
        "all_requests_succeeded": all(row.get("ok") for row in rows),
        "direct_model_identity": all(
            row.get("requested_model") == DIRECT_MODEL
            and row.get("resolved_model") == DIRECT_MODEL
            for row in rows
            if row.get("ok")
        ),
        "single_zero_argument_tool_call": (
            len(call_row.get("function_calls") or []) == 1
            and (call_row.get("function_calls") or [{}])[0].get("name")
            == "fetch_frozen_value"
            and json.loads(
                str((call_row.get("function_calls") or [{}])[0].get("arguments") or "{}")
            )
            == {}
        ),
        "frozen_value_absent_before_tool_result": FROZEN_VALUE not in pre_call_material,
        "post_call_frozen_value_recovered": FROZEN_VALUE in continuation,
        "usage_present": all(bool(row.get("usage")) for row in rows if row.get("ok")),
    }
    decision = (
        "ARK_DEEPSEEK_PRO_DIRECT_CAUSAL_QUALIFIED"
        if all(checks.values())
        else "ARK_DEEPSEEK_PRO_DIRECT_CAUSAL_NOT_QUALIFIED"
    )
    output = {
        "schema_version": 1,
        "experiment_id": EXPERIMENT_ID,
        "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "contract": (
            "generated/asset-first-stri-reasoningbank-deepseek-direct-causal-contract-"
            "20260829.json"
        ),
        "provider_role": "ReasoningBank architecture + Ark DeepSeek-Pro compatibility backend",
        "causal_observable": (
            "Recover a frozen value that first becomes model-visible in the "
            "function_call_output of a zero-argument tool."
        ),
        "frozen_value_sha256": sha(FROZEN_VALUE),
        "receipts": rows,
        "checks": checks,
        "decision": decision,
        "resource_accounting": {
            "provider_requests_attempted": len(rows),
            "gpu_seconds": 0,
        },
        "scientific_boundary": {
            "provider_semantics_only": True,
            "p1_outcome_observed": False,
            "memory_induction_executed": False,
            "behavioral_claim_authorized": False,
            "full_p1_authorized": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"decision": decision, "output": str(args.output)}, sort_keys=True))


if __name__ == "__main__":
    main()
