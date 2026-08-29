#!/usr/bin/env python3
"""Role-aligned Ark DeepSeek-Pro qualification for ReasoningBank P1."""

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


EXPERIMENT_ID = "E1-STRI-REASONINGBANK-ARK-DEEPSEEK-Q1-20260829"
REQUESTED_MODEL = "deepseek-v4-pro"
NONCE = "DEEPSEEK_TOOL_NONCE_617"
DEFAULT_OUTPUT = Path(
    "generated/asset-first-stri-reasoningbank-deepseek-provider-qualification-result-20260829.json"
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


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def safe_receipt(label: str, result: dict[str, Any], *, role: str) -> dict[str, Any]:
    text = str(result.get("text") or "")
    return {
        "label": label,
        "role": role,
        "ok": True,
        "requested_model": result.get("requested_model"),
        "resolved_model": result.get("resolved_model"),
        "status": result.get("status"),
        "text": text,
        "text_sha256": digest(text),
        "function_calls": [
            {
                "name": call.get("name"),
                "arguments": str(call.get("arguments") or ""),
                "call_id_sha256": digest(str(call.get("call_id") or "")),
            }
            for call in result.get("function_calls") or []
        ],
        "usage": result.get("usage") or {},
        "response_id_sha256": digest(str(result.get("response_id") or "")),
        "credential_material_present": False,
    }


def failed_receipt(label: str, role: str, error: ArkCompatibilityError) -> dict[str, Any]:
    return {"label": label, "role": role, "ok": False, **error.safe_receipt()}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, default=CANONICAL_SECRET_FILE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    base = ArkReasoningBankSettings.from_env_file(args.env_file)
    settings = ArkReasoningBankSettings(
        api_key=base.api_key,
        base_url=base.base_url,
        model=REQUESTED_MODEL,
        timeout_seconds=base.timeout_seconds,
        max_retries=base.max_retries,
    )
    client = ArkReasoningBankClient(settings)
    rows: list[dict[str, Any]] = []
    live: dict[str, dict[str, Any]] = {}

    probes = [
        (
            "behavior_basic",
            "behavior",
            {
                "instructions": "Follow the exact user output instruction.",
                "input_items": [{"role": "user", "content": "Reply exactly DEEPSEEK_BEHAVIOR_OK"}],
                "temperature": 0.0,
                "max_output_tokens": None,
                "store": True,
            },
        ),
        (
            "behavior_multiturn",
            "behavior",
            {
                "instructions": "Use prior messages and return only the requested value.",
                "input_items": [
                    {"role": "user", "content": "The frozen value is DEEPSEEK_MULTI_617."},
                    {"role": "assistant", "content": "Acknowledged."},
                    {"role": "user", "content": "Return only the frozen value."},
                ],
                "temperature": 0.0,
                "max_output_tokens": None,
                "store": True,
            },
        ),
        (
            "tool_call",
            "behavior",
            {
                "instructions": (
                    "Call record_probe exactly once. After its result arrives, output the "
                    "continuation_nonce from that result."
                ),
                "input_items": "Call record_probe with value 617.",
                "tools": [TOOL],
                "tool_choice": "required",
                "temperature": 0.0,
                "max_output_tokens": None,
                "store": True,
            },
        ),
        (
            "memory_induction",
            "memory_induction",
            {
                "instructions": "Return only the requested qualification marker.",
                "input_items": "Reply exactly DEEPSEEK_INDUCTION_TEMP1_OK",
                "temperature": 1.0,
                "max_output_tokens": 65536,
                "store": True,
            },
        ),
        (
            "judge",
            "judge",
            {
                "instructions": "Return a JSON object matching the schema.",
                "input_items": "The qualification case succeeded. Set success=true.",
                "temperature": 0.0,
                "max_output_tokens": 65536,
                "text": {
                    "format": {
                        "type": "json_schema",
                        "name": "judge_probe",
                        "schema": {
                            "type": "object",
                            "properties": {"success": {"type": "boolean"}},
                            "required": ["success"],
                            "additionalProperties": False,
                        },
                        "strict": True,
                    }
                },
                "store": True,
            },
        ),
        (
            "behavior_repeat_a",
            "behavior_repeat",
            {
                "input_items": "Choose one word from red, green, blue. Output one word.",
                "temperature": 0.0,
                "max_output_tokens": None,
                "store": True,
            },
        ),
        (
            "behavior_repeat_b",
            "behavior_repeat",
            {
                "input_items": "Choose one word from red, green, blue. Output one word.",
                "temperature": 0.0,
                "max_output_tokens": None,
                "store": True,
            },
        ),
    ]
    for label, role, kwargs in probes:
        try:
            result = client.create_response(**kwargs)
            rows.append(safe_receipt(label, result, role=role))
            live[label] = result
        except ArkCompatibilityError as error:
            rows.append(failed_receipt(label, role, error))

    tool = live.get("tool_call")
    if tool and tool.get("function_calls"):
        call = tool["function_calls"][0]
        try:
            result = client.continue_function_call(
                previous_response_id=str(tool["response_id"]),
                call_id=str(call.get("call_id") or ""),
                output=json.dumps({"recorded": 617, "continuation_nonce": NONCE}),
                model=REQUESTED_MODEL,
                max_output_tokens=65536,
            )
            rows.append(safe_receipt("tool_continuation", result, role="behavior"))
        except ArkCompatibilityError as error:
            rows.append(failed_receipt("tool_continuation", "behavior", error))
    else:
        rows.append(
            {
                "label": "tool_continuation",
                "role": "behavior",
                "ok": False,
                "error_type": "PREREQUISITE_TOOL_CALL_MISSING",
                "credential_material_present": False,
            }
        )

    by = {row["label"]: row for row in rows}
    successful = [row for row in rows if row.get("ok")]
    resolved = sorted({str(row.get("resolved_model") or "") for row in successful})
    try:
        judge_payload = json.loads(str(by["judge"].get("text") or ""))
    except Exception:
        judge_payload = {}
    continuation = str(by["tool_continuation"].get("text") or "")
    checks = {
        "all_requests_succeeded": all(row.get("ok") for row in rows),
        "all_requested_deepseek_pro": all(
            row.get("requested_model") == REQUESTED_MODEL for row in successful
        ),
        "stable_nonempty_resolved_model": len(resolved) == 1 and bool(resolved[0]),
        "behavior_system_user_exact": by["behavior_basic"].get("text", "").strip()
        == "DEEPSEEK_BEHAVIOR_OK",
        "behavior_multiturn_exact": by["behavior_multiturn"].get("text", "").strip()
        == "DEEPSEEK_MULTI_617",
        "single_tool_call": (
            len(by["tool_call"].get("function_calls") or []) == 1
            and (by["tool_call"].get("function_calls") or [{}])[0].get("name")
            == "record_probe"
        ),
        "nonce_absent_before_tool_result": NONCE
        not in str(by["tool_call"].get("text") or "")
        and NONCE
        not in str((by["tool_call"].get("function_calls") or [{}])[0].get("arguments") or ""),
        "causal_tool_result_consumed": NONCE in continuation,
        "memory_induction_temperature_one": by["memory_induction"].get("text", "").strip()
        == "DEEPSEEK_INDUCTION_TEMP1_OK",
        "judge_temperature_zero_json_schema": judge_payload == {"success": True},
        "usage_present": all(bool(row.get("usage")) for row in successful),
    }
    core_pass = all(checks.values())
    exact_identity = resolved == [REQUESTED_MODEL]
    if core_pass and exact_identity:
        decision = "ARK_DEEPSEEK_PRO_BACKEND_QUALIFIED"
    elif core_pass:
        decision = "ARK_DEEPSEEK_PRO_ALIAS_QUALIFIED_DIRECT_IDENTITY_CONFIRMATION_REQUIRED"
    else:
        decision = "ARK_DEEPSEEK_PRO_BACKEND_NOT_QUALIFIED"
    repeat_equal = (
        by["behavior_repeat_a"].get("ok")
        and by["behavior_repeat_b"].get("ok")
        and by["behavior_repeat_a"].get("text_sha256")
        == by["behavior_repeat_b"].get("text_sha256")
    )
    output = {
        "schema_version": 1,
        "experiment_id": EXPERIMENT_ID,
        "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "contract": "generated/asset-first-stri-reasoningbank-deepseek-provider-qualification-contract-20260829.json",
        "alignment": "generated/asset-first-stri-reasoningbank-deepseek-paper-alignment-20260829.json",
        "provider_role": "ReasoningBank architecture + Ark DeepSeek-Pro compatibility backend",
        "settings": settings.safe_summary(),
        "resolved_models": resolved,
        "receipts": rows,
        "checks": checks,
        "sampling": {
            "behavior_temperature": 0.0,
            "memory_induction_temperature": 1.0,
            "judge_temperature": 0.0,
            "seed": "omitted",
            "top_p": "omitted",
            "behavior_repeat_outputs_equal": bool(repeat_equal),
            "determinism_claim_authorized": False,
            "repeat_label": "paired same-backend repeated execution",
        },
        "decision": decision,
        "resource_accounting": {
            "provider_requests_attempted": len(rows),
            "gpu_seconds": 0,
        },
        "scientific_boundary": {
            "p1_task_outcome_observed": False,
            "memory_induction_executed": False,
            "reasoningbank_original_provider_reproduction": False,
            "behavioral_claim_authorized": False,
            "full_p1_authorized": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"decision": decision, "resolved_models": resolved}, sort_keys=True))


if __name__ == "__main__":
    main()
