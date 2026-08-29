#!/usr/bin/env python3
"""Causal tool-result continuation probe for the direct Ark backend."""

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


EXPERIMENT_ID = "E1-STRI-REASONINGBANK-ARK-Q0C-20260829"
DIRECT_MODEL = "doubao-seed-evolving"
NONCE = "TOOL_ONLY_NONCE_913"
DEFAULT_OUTPUT = Path(
    "generated/asset-first-stri-reasoningbank-ark-tool-continuation-causal-result-20260829.json"
)
TOOL = {
    "type": "function",
    "name": "record_probe",
    "description": "Record the requested integer and return an environment receipt.",
    "parameters": {
        "type": "object",
        "properties": {"value": {"type": "integer"}},
        "required": ["value"],
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
    instructions = (
        "First call record_probe exactly once. After its result arrives, output the "
        "continuation_nonce value from that result. The nonce is not present yet."
    )
    try:
        live_first = client.create_response(
            input_items="Call record_probe with value 731.",
            instructions=instructions,
            tools=[TOOL],
            tool_choice="required",
            temperature=0,
            thinking="disabled",
            max_output_tokens=512,
            store=True,
        )
        rows.append(safe_row("tool_call", live_first))
    except ArkCompatibilityError as error:
        rows.append({"label": "tool_call", "ok": False, **error.safe_receipt()})

    if live_first and live_first.get("function_calls"):
        call = live_first["function_calls"][0]
        try:
            continued = client.continue_function_call(
                previous_response_id=str(live_first["response_id"]),
                call_id=str(call.get("call_id") or ""),
                output=json.dumps({"recorded": 731, "continuation_nonce": NONCE}),
                model=DIRECT_MODEL,
                max_output_tokens=256,
            )
            rows.append(safe_row("tool_result_continuation", continued))
        except ArkCompatibilityError as error:
            rows.append(
                {
                    "label": "tool_result_continuation",
                    "ok": False,
                    **error.safe_receipt(),
                }
            )
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
    continuation_text = str(by["tool_result_continuation"].get("text") or "")
    checks = {
        "all_requests_succeeded": all(row.get("ok") for row in rows),
        "direct_model_identity": all(
            row.get("requested_model") == DIRECT_MODEL
            and row.get("resolved_model") == DIRECT_MODEL
            for row in rows
            if row.get("ok")
        ),
        "single_tool_call": (
            len(by["tool_call"].get("function_calls") or []) == 1
            and (by["tool_call"].get("function_calls") or [{}])[0].get("name")
            == "record_probe"
        ),
        "nonce_absent_before_tool_result": NONCE not in str(by["tool_call"].get("text") or "")
        and NONCE
        not in str((by["tool_call"].get("function_calls") or [{}])[0].get("arguments") or ""),
        "post_call_nonce_recovered": NONCE in continuation_text,
        "usage_present": all(bool(row.get("usage")) for row in rows if row.get("ok")),
    }
    decision = (
        "ARK_CAUSAL_TOOL_CONTINUATION_QUALIFIED"
        if all(checks.values())
        else "ARK_CAUSAL_TOOL_CONTINUATION_NOT_QUALIFIED"
    )
    output = {
        "schema_version": 1,
        "experiment_id": EXPERIMENT_ID,
        "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "contract": "generated/asset-first-stri-reasoningbank-ark-tool-continuation-causal-contract-20260829.json",
        "provider_role": "ReasoningBank architecture + compatibility-adapted Ark backend",
        "causal_observable": "Recover a nonce that first becomes model-visible in function_call_output.",
        "nonce_sha256": sha(NONCE),
        "nonce_is_harmless_public_probe": True,
        "receipts": rows,
        "checks": checks,
        "decision": decision,
        "resource_accounting": {"provider_requests_attempted": len(rows), "gpu_seconds": 0},
        "scientific_boundary": {
            "provider_semantics_only": True,
            "p1_outcome_observed": False,
            "memory_induction_executed": False,
            "behavioral_claim_authorized": False,
            "full_p1_authorized": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"decision": decision, "output": str(args.output)}, sort_keys=True))


if __name__ == "__main__":
    main()
