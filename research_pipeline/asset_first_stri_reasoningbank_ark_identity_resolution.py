#!/usr/bin/env python3
"""Single-variable Ark model-alias resolution qualification."""

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


EXPERIMENT_ID = "E1-STRI-REASONINGBANK-ARK-Q0B-20260829"
DIRECT_MODEL = "doubao-seed-evolving"
DEFAULT_OUTPUT = Path(
    "generated/asset-first-stri-reasoningbank-ark-provider-identity-resolution-result-20260829.json"
)
TOOL = {
    "type": "function",
    "name": "record_probe",
    "description": "Record the requested integer.",
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


def receipt(label: str, result: dict[str, Any]) -> dict[str, Any]:
    text = str(result.get("text") or "")
    calls = [
        {
            "name": call.get("name"),
            "arguments": str(call.get("arguments") or ""),
            "call_id_sha256": sha(str(call.get("call_id") or "")),
        }
        for call in result.get("function_calls") or []
    ]
    return {
        "label": label,
        "ok": True,
        "requested_model": result.get("requested_model"),
        "resolved_model": result.get("resolved_model"),
        "status": result.get("status"),
        "text": text,
        "text_sha256": sha(text),
        "function_calls": calls,
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
    live: dict[str, dict[str, Any]] = {}

    specs = [
        (
            "basic_direct",
            {
                "input_items": "Reply exactly DIRECT_MODEL_OK.",
                "instructions": "Follow the exact output instruction.",
                "temperature": 0,
                "thinking": "disabled",
                "max_output_tokens": 256,
            },
        ),
        (
            "multiturn_direct",
            {
                "input_items": [
                    {"role": "user", "content": "The nonce is DIRECT_731."},
                    {"role": "assistant", "content": "Acknowledged."},
                    {"role": "user", "content": "Return only the nonce."},
                ],
                "instructions": "Use prior messages and obey the last request.",
                "temperature": 0,
                "thinking": "disabled",
                "max_output_tokens": 256,
            },
        ),
        (
            "tool_direct",
            {
                "input_items": "Call record_probe with value 731.",
                "instructions": "You must make exactly one record_probe call.",
                "tools": [TOOL],
                "tool_choice": "required",
                "temperature": 0,
                "thinking": "disabled",
                "max_output_tokens": 512,
                "store": True,
            },
        ),
    ]
    for label, kwargs in specs:
        try:
            result = client.create_response(**kwargs)
            rows.append(receipt(label, result))
            live[label] = result
        except ArkCompatibilityError as error:
            rows.append({"label": label, "ok": False, **error.safe_receipt()})

    tool = live.get("tool_direct")
    if tool and tool.get("function_calls"):
        call = tool["function_calls"][0]
        try:
            result = client.continue_function_call(
                previous_response_id=str(tool["response_id"]),
                call_id=str(call.get("call_id") or ""),
                output=json.dumps({"recorded": 731}),
                instructions="Reply exactly DIRECT_TOOL_CONTINUATION_OK.",
                model=DIRECT_MODEL,
                max_output_tokens=256,
            )
            rows.append(receipt("tool_continuation_direct", result))
        except ArkCompatibilityError as error:
            rows.append(
                {
                    "label": "tool_continuation_direct",
                    "ok": False,
                    **error.safe_receipt(),
                }
            )
    else:
        rows.append(
            {
                "label": "tool_continuation_direct",
                "ok": False,
                "error_type": "PREREQUISITE_TOOL_CALL_MISSING",
                "credential_material_present": False,
            }
        )

    by = {row["label"]: row for row in rows}
    checks = {
        "all_requests_succeeded": all(row.get("ok") for row in rows),
        "all_requested_model_direct": all(
            row.get("requested_model") == DIRECT_MODEL for row in rows if row.get("ok")
        ),
        "all_resolved_model_direct": all(
            row.get("resolved_model") == DIRECT_MODEL for row in rows if row.get("ok")
        ),
        "basic_exact": by["basic_direct"].get("text", "").strip() == "DIRECT_MODEL_OK",
        "multiturn_exact": by["multiturn_direct"].get("text", "").strip() == "DIRECT_731",
        "tool_exact": (
            len(by["tool_direct"].get("function_calls") or []) == 1
            and (by["tool_direct"].get("function_calls") or [{}])[0].get("name")
            == "record_probe"
        ),
        "continuation_exact": by["tool_continuation_direct"].get("text", "").strip()
        == "DIRECT_TOOL_CONTINUATION_OK",
        "usage_present": all(bool(row.get("usage")) for row in rows if row.get("ok")),
    }
    decision = (
        "ARK_DIRECT_MODEL_QUALIFIED_FOR_REASONINGBANK_AGENT_SEMANTICS"
        if all(checks.values())
        else "ARK_DIRECT_MODEL_NOT_QUALIFIED"
    )
    output = {
        "schema_version": 1,
        "experiment_id": EXPERIMENT_ID,
        "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "contract": "generated/asset-first-stri-reasoningbank-ark-provider-identity-resolution-contract-20260829.json",
        "single_variable_repair": "Pin provider-resolved model directly; all other adapter and probe semantics unchanged.",
        "provider_role": "ReasoningBank architecture + compatibility-adapted Ark backend",
        "settings": settings.safe_summary(),
        "receipts": rows,
        "checks": checks,
        "decision": decision,
        "sampling_contract": {
            "temperature": 0,
            "seed": None,
            "repeats": "paired same-backend repeated executions",
            "independent_seeded_repeats": False,
        },
        "resource_accounting": {
            "provider_requests_attempted": len(rows),
            "gpu_seconds": 0,
        },
        "scientific_boundary": {
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
