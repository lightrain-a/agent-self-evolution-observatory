#!/usr/bin/env python3
"""Live, sanitized Ark semantic qualification for ReasoningBank P1."""

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


EXPERIMENT_ID = "E1-STRI-REASONINGBANK-ARK-Q0-20260829"
DEFAULT_OUTPUT = Path("generated/asset-first-stri-reasoningbank-ark-provider-qualification-result-20260829.json")
EXPECTED_BASE_URL = "https://ark.cn-beijing.volces.com/api/plan/v3"
EXPECTED_MODEL = "ark-code-latest"
TOOL = {
    "type": "function",
    "name": "record_probe",
    "description": "Record the exact integer requested by the user.",
    "parameters": {
        "type": "object",
        "properties": {"value": {"type": "integer"}},
        "required": ["value"],
        "additionalProperties": False,
    },
    "strict": True,
}


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def safe_call_receipt(label: str, result: dict[str, Any]) -> dict[str, Any]:
    calls = []
    for call in result.get("function_calls") or []:
        arguments = str(call.get("arguments") or "")
        calls.append(
            {
                "type": call.get("type"),
                "name": call.get("name"),
                "arguments": arguments,
                "arguments_sha256": sha256_text(arguments),
                "call_id_sha256": sha256_text(str(call.get("call_id") or "")),
            }
        )
    text = str(result.get("text") or "")
    response_id = str(result.get("response_id") or "")
    return {
        "label": label,
        "ok": True,
        "status": result.get("status"),
        "requested_model": result.get("requested_model"),
        "resolved_model": result.get("resolved_model"),
        "text": text,
        "text_sha256": sha256_text(text),
        "function_calls": calls,
        "usage": result.get("usage") or {},
        "response_id_sha256": sha256_text(response_id),
        "credential_material_present": False,
    }


def run_probe(
    client: ArkReasoningBankClient,
    label: str,
    **kwargs: Any,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    try:
        result = client.create_response(**kwargs)
        return safe_call_receipt(label, result), result
    except ArkCompatibilityError as error:
        return {
            "label": label,
            "ok": False,
            **error.safe_receipt(),
        }, None


def classify_parameter(receipt: dict[str, Any]) -> str:
    if receipt.get("ok"):
        return "accepted_by_provider"
    if receipt.get("status_code") in {400, 422}:
        return "unsupported_or_rejected"
    return "unresolved_transport_or_provider_failure"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, default=CANONICAL_SECRET_FILE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    settings = ArkReasoningBankSettings.from_env_file(args.env_file)
    if settings.base_url.rstrip("/") != EXPECTED_BASE_URL:
        raise RuntimeError("outcome-independent Ark base URL freeze violated")
    if settings.model != EXPECTED_MODEL:
        raise RuntimeError("outcome-independent Ark model freeze violated")
    client = ArkReasoningBankClient(settings)
    receipts: list[dict[str, Any]] = []
    live_results: dict[str, dict[str, Any] | None] = {}

    probes = [
        (
            "basic_chat",
            {
                "input_items": "Reply exactly BASIC_OK.",
                "max_output_tokens": 256,
                "temperature": 0,
                "thinking": "disabled",
            },
        ),
        (
            "system_user",
            {
                "instructions": "Follow the user's exact output instruction. Do not add punctuation.",
                "input_items": [{"role": "user", "content": "Reply exactly SYSTEM_USER_OK"}],
                "max_output_tokens": 256,
                "temperature": 0,
                "thinking": "disabled",
            },
        ),
        (
            "multi_turn_history",
            {
                "instructions": "Answer the last user request using the prior messages.",
                "input_items": [
                    {"role": "user", "content": "The frozen nonce is MULTI_TURN_731."},
                    {"role": "assistant", "content": "Acknowledged."},
                    {"role": "user", "content": "Reply with only the frozen nonce."},
                ],
                "max_output_tokens": 256,
                "temperature": 0,
                "thinking": "disabled",
            },
        ),
        (
            "tool_call",
            {
                "instructions": "You must call record_probe once with the integer requested.",
                "input_items": [{"role": "user", "content": "Use the tool to record 731."}],
                "tools": [TOOL],
                "tool_choice": "required",
                "max_output_tokens": 512,
                "temperature": 0,
                "thinking": "disabled",
                "store": True,
            },
        ),
        (
            "temperature",
            {
                "input_items": "Reply exactly TEMPERATURE_OK.",
                "max_output_tokens": 256,
                "temperature": 0.2,
                "thinking": "disabled",
            },
        ),
        (
            "top_p",
            {
                "input_items": "Reply exactly TOP_P_OK.",
                "max_output_tokens": 256,
                "top_p": 0.8,
                "thinking": "disabled",
            },
        ),
        (
            "seed_42_a",
            {
                "input_items": "Choose one word from alpha, beta, gamma. Output one word.",
                "max_output_tokens": 256,
                "temperature": 0.8,
                "seed": 42,
                "thinking": "disabled",
            },
        ),
        (
            "seed_42_b",
            {
                "input_items": "Choose one word from alpha, beta, gamma. Output one word.",
                "max_output_tokens": 256,
                "temperature": 0.8,
                "seed": 42,
                "thinking": "disabled",
            },
        ),
        (
            "seed_43",
            {
                "input_items": "Choose one word from alpha, beta, gamma. Output one word.",
                "max_output_tokens": 256,
                "temperature": 0.8,
                "seed": 43,
                "thinking": "disabled",
            },
        ),
        (
            "repeat_no_seed_a",
            {
                "input_items": "Choose one word from red, green, blue. Output one word.",
                "max_output_tokens": 256,
                "temperature": 0,
                "thinking": "disabled",
            },
        ),
        (
            "repeat_no_seed_b",
            {
                "input_items": "Choose one word from red, green, blue. Output one word.",
                "max_output_tokens": 256,
                "temperature": 0,
                "thinking": "disabled",
            },
        ),
        (
            "stop",
            {
                "input_items": "Output STOP_PREFIX then <END> then forbidden suffix.",
                "max_output_tokens": 256,
                "temperature": 0,
                "stop": ["<END>"],
                "thinking": "disabled",
            },
        ),
        (
            "structured_json",
            {
                "input_items": "Return an object with ok=true and value=731.",
                "max_output_tokens": 256,
                "temperature": 0,
                "thinking": "disabled",
                "text": {
                    "format": {
                        "type": "json_schema",
                        "name": "qualification_probe",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "ok": {"type": "boolean"},
                                "value": {"type": "integer"},
                            },
                            "required": ["ok", "value"],
                            "additionalProperties": False,
                        },
                        "strict": True,
                    }
                },
            },
        ),
    ]

    for label, kwargs in probes:
        receipt, live = run_probe(client, label, **kwargs)
        receipts.append(receipt)
        live_results[label] = live
        print(json.dumps({"label": label, "ok": receipt["ok"]}, sort_keys=True))

    tool_live = live_results.get("tool_call")
    tool_continuation_receipt: dict[str, Any]
    if tool_live and tool_live.get("function_calls"):
        call = tool_live["function_calls"][0]
        try:
            continuation = client.continue_function_call(
                previous_response_id=str(tool_live["response_id"]),
                call_id=str(call.get("call_id") or ""),
                output=json.dumps({"recorded": 731}),
                instructions="After the tool result, reply exactly TOOL_CONTINUATION_OK.",
                max_output_tokens=256,
            )
            tool_continuation_receipt = safe_call_receipt("tool_result_continuation", continuation)
        except ArkCompatibilityError as error:
            tool_continuation_receipt = {
                "label": "tool_result_continuation",
                "ok": False,
                **error.safe_receipt(),
            }
    else:
        tool_continuation_receipt = {
            "label": "tool_result_continuation",
            "ok": False,
            "error_type": "PREREQUISITE_TOOL_CALL_MISSING",
            "credential_material_present": False,
        }
    receipts.append(tool_continuation_receipt)

    by_label = {row["label"]: row for row in receipts}
    required_semantics = {
        "endpoint_reachable": any(row.get("ok") for row in receipts),
        "exact_model_frozen": settings.model == EXPECTED_MODEL,
        "basic_chat": by_label["basic_chat"].get("ok")
        and by_label["basic_chat"].get("text", "").strip() == "BASIC_OK",
        "system_user": by_label["system_user"].get("ok")
        and by_label["system_user"].get("text", "").strip() == "SYSTEM_USER_OK",
        "multi_turn_history": by_label["multi_turn_history"].get("ok")
        and by_label["multi_turn_history"].get("text", "").strip() == "MULTI_TURN_731",
        "tool_call_parsing": by_label["tool_call"].get("ok")
        and len(by_label["tool_call"].get("function_calls") or []) == 1
        and (by_label["tool_call"].get("function_calls") or [{}])[0].get("name") == "record_probe",
        "tool_result_continuation": tool_continuation_receipt.get("ok")
        and tool_continuation_receipt.get("text", "").strip() == "TOOL_CONTINUATION_OK",
        "usage_metadata": all(
            isinstance(row.get("usage"), dict) and bool(row.get("usage"))
            for row in receipts
            if row.get("ok")
        ),
        "provider_model_identifier": all(
            row.get("resolved_model") == EXPECTED_MODEL
            for row in receipts
            if row.get("ok")
        ),
        "max_output_tokens": by_label["basic_chat"].get("ok"),
        "timeout_configured": settings.timeout_seconds > 0,
        "retry_configured": settings.max_retries >= 0,
    }
    parameter_semantics = {
        name: classify_parameter(by_label[name])
        for name in ("temperature", "top_p", "seed_42_a", "stop", "structured_json")
    }
    seed_a = by_label["seed_42_a"]
    seed_b = by_label["seed_42_b"]
    seed_c = by_label["seed_43"]
    if all(row.get("ok") for row in (seed_a, seed_b, seed_c)):
        seed_semantics = {
            "classification": "accepted_empirically_unresolved",
            "same_seed_equal": seed_a.get("text_sha256") == seed_b.get("text_sha256"),
            "different_seed_differs": seed_a.get("text_sha256") != seed_c.get("text_sha256"),
            "claim_independent_seeded_repeats_authorized": False,
        }
    else:
        seed_semantics = {
            "classification": "unsupported_or_rejected",
            "same_seed_equal": None,
            "different_seed_differs": None,
            "claim_independent_seeded_repeats_authorized": False,
        }
    no_seed_a = by_label["repeat_no_seed_a"]
    no_seed_b = by_label["repeat_no_seed_b"]
    repeat_semantics = {
        "classification": "paired_same_backend_repeated_execution",
        "temperature_zero_outputs_equal": (
            no_seed_a.get("ok")
            and no_seed_b.get("ok")
            and no_seed_a.get("text_sha256") == no_seed_b.get("text_sha256")
        ),
        "determinism_claim_authorized": False,
    }
    all_required = all(required_semantics.values())
    decision = (
        "ARK_BACKEND_QUALIFIED_FOR_REASONINGBANK_AGENT_SEMANTICS"
        if all_required
        else "ARK_BACKEND_NOT_YET_QUALIFIED_LOCALIZE_AND_REPAIR"
    )
    output = {
        "schema_version": 1,
        "experiment_id": EXPERIMENT_ID,
        "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "contract": "generated/asset-first-stri-reasoningbank-ark-provider-qualification-contract-20260829.json",
        "provider_role": "ReasoningBank architecture + compatibility-adapted Ark backend",
        "settings": settings.safe_summary(),
        "model_selection_rule": "Project-default authorized coding/agent model frozen before P1 outcome.",
        "receipts": receipts,
        "required_semantics": required_semantics,
        "parameter_semantics": parameter_semantics,
        "seed_semantics": seed_semantics,
        "repeat_semantics": repeat_semantics,
        "decision": decision,
        "resource_accounting": {
            "provider_requests_attempted": len(probes) + (1 if tool_live and tool_live.get("function_calls") else 0),
            "gpu_seconds": 0,
        },
        "scientific_boundary": {
            "original_reasoningbank_reproduction": False,
            "p1_treatment_outcome_observed": False,
            "memory_or_retrieval_semantics_changed": False,
            "behavioral_claim_authorized": False,
            "full_p1_authorized": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"decision": decision, "output": str(args.output)}, sort_keys=True))


if __name__ == "__main__":
    main()
