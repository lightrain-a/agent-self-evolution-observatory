"""Preregister and run Qwen3-Coder-Next provider qualification (Q0)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_ark_provider import (
    ArkCompatibilityError,
    ArkReasoningBankClient,
    ArkReasoningBankSettings,
    CANONICAL_SECRET_FILE,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    BASE_URL,
    FORMAT_RE,
    ROOT,
    canonical_json,
    sha256_file,
    sha256_text,
    utcnow,
    write_json,
)

EXPERIMENT_ID = "E1-STRI-REASONINGBANK-QWEN-DISTRIBUTION-V3-20260901"
MODEL = "qwen3-coder-next"
D0_INDEX = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-d0-evaluator-index-20260901.json"
CONTRACT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-q0-contract-20260901.json"
OUTPUT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-q0-result-20260901.json"
EXPECTED_CONTRACT_SHA256 = "PENDING"
TIMEOUT_SECONDS = 120.0
MAX_RETRIES = 0
RECOMMENDED_TEMPERATURE = 1.0
RECOMMENDED_TOP_P = 0.95
RECOMMENDED_TOP_K = 40
SCIENTIFIC_MAX_OUTPUT_TOKENS = 32768
OFFICIAL_MODEL_CARD = "https://huggingface.co/Qwen/Qwen3-Coder-Next"


def probe_plan() -> list[dict[str, Any]]:
    return [
        {
            "ordinal": 1,
            "name": "identity_messages_sampling",
            "goal": "model identity, system/user semantics, recommended temperature/top_p",
            "attempt_count": 1,
        },
        {
            "ordinal": 2,
            "name": "instructions_semantics",
            "goal": "Responses instructions/system priority",
            "attempt_count": 1,
        },
        {
            "ordinal": 3,
            "name": "multi_turn_history",
            "goal": "system/user/assistant/user history semantics",
            "attempt_count": 1,
        },
        {
            "ordinal": 4,
            "name": "recommended_top_k",
            "goal": "recommended top_k=40 acceptance and evidence of honoring",
            "attempt_count": 1,
        },
        {
            "ordinal": 5,
            "name": "seed_acceptance",
            "goal": "seed field acceptance without assuming it is honored",
            "attempt_count": 1,
        },
        {
            "ordinal": 6,
            "name": "stop_semantics",
            "goal": "stop field acceptance and visible truncation",
            "attempt_count": 1,
        },
        {
            "ordinal": 7,
            "name": "tool_call",
            "goal": "function tool/action compatibility",
            "attempt_count": 1,
        },
        {
            "ordinal": 8,
            "name": "text_action_parser",
            "goal": "exact mini-SWE-agent bash action format compatibility",
            "attempt_count": 1,
        },
        {
            "ordinal": 9,
            "name": "max_output_tokens",
            "goal": "small output cap behavior and incomplete metadata",
            "attempt_count": 1,
        },
        {
            "ordinal": 10,
            "name": "previous_response",
            "goal": "stored response identity and continuation semantics",
            "attempt_count": 1,
        },
    ]


def load_d0_terminal() -> dict[str, Any]:
    if not D0_INDEX.is_file():
        raise RuntimeError("D0 evaluator index absent")
    document = json.loads(D0_INDEX.read_text(encoding="utf-8"))
    if document["execution_complete"] is not True:
        raise RuntimeError("D0 evaluator qualification is not terminal")
    if document["decision"] not in {
        "D0_PRIMARY_FOUR_REPOSITORY_EVALUATOR_FEASIBILITY_PASS",
        "D0_FALLBACK_THREE_REPOSITORY_EVALUATOR_FEASIBILITY_PASS",
    }:
        raise RuntimeError("D0 did not open Q0 provider qualification")
    return document


def contract_payload() -> dict[str, Any]:
    d0 = load_d0_terminal()
    plan = probe_plan()
    return {
        "schema_version": 1,
        "experiment_id": EXPERIMENT_ID,
        "stage": "Q0_QWEN_PROVIDER_QUALIFICATION",
        "created_at_utc": utcnow(),
        "decision": "Q0_QWEN3_CODER_NEXT_PROVIDER_QUALIFICATION_AUTHORIZED",
        "d0_index_path": str(D0_INDEX.relative_to(ROOT)),
        "d0_index_sha256": sha256_file(D0_INDEX),
        "d0_decision": d0["decision"],
        "provider": {
            "route_family": "domestic OpenAI-compatible Responses API",
            "base_url": BASE_URL,
            "requested_model": MODEL,
            "resolved_model_requirement": MODEL,
            "timeout_seconds": TIMEOUT_SECONDS,
            "max_retries": MAX_RETRIES,
            "streaming": False,
            "store": True,
            "credential_source": "pre-existing mode-0600 server secret file",
            "credential_value_persisted": False,
        },
        "official_configuration_basis": {
            "model_card": OFFICIAL_MODEL_CARD,
            "model_card_statement": "non-thinking-only; temperature=1.0; top_p=0.95; top_k=40",
            "temperature": RECOMMENDED_TEMPERATURE,
            "top_p": RECOMMENDED_TOP_P,
            "top_k": RECOMMENDED_TOP_K,
            "scientific_max_output_tokens": SCIENTIFIC_MAX_OUTPUT_TOKENS,
            "unsupported_recommended_parameter_policy": "freeze unavailable/omitted; do not substitute a model or provider based on outcomes",
        },
        "probe_plan": plan,
        "probe_plan_sha256": sha256_text(canonical_json(plan)),
        "classification_vocabulary": [
            "honored",
            "ignored",
            "unsupported",
            "server-fixed",
            "unresolved",
        ],
        "qualification_gate": {
            "model_identity_exact_required": True,
            "system_user_semantics_required": True,
            "multi_turn_required": True,
            "response_parser_required": True,
            "text_action_compatibility_required": True,
            "usage_metadata_required": True,
            "response_identity_metadata_required": True,
            "tool_function_call_required_for_scientific_agent": False,
            "recommended_top_k_support_required": False,
            "no_hidden_retries": True,
        },
        "scientific_boundary": {
            "benchmark_calls_authorized": False,
            "source_generation_authorized": False,
            "confirmatory_execution_authorized": False,
        },
        "credential_material_present": False,
    }


def freeze_contract(output: Path = CONTRACT) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError("refusing to overwrite immutable Q0 contract")
    payload = contract_payload()
    return {
        "decision": payload["decision"],
        "file_sha256": write_json(output, payload),
        "probe_count": len(payload["probe_plan"]),
    }


def make_client() -> ArkReasoningBankClient:
    base = ArkReasoningBankSettings.from_env_file(CANONICAL_SECRET_FILE)
    if base.base_url.rstrip("/") != BASE_URL:
        raise RuntimeError("Q0 provider base URL drift")
    settings = ArkReasoningBankSettings(
        api_key=base.api_key,
        base_url=BASE_URL,
        model=MODEL,
        timeout_seconds=TIMEOUT_SECONDS,
        max_retries=MAX_RETRIES,
    )
    return ArkReasoningBankClient(settings)


def public_success(name: str, value: dict[str, Any], elapsed: float) -> dict[str, Any]:
    response_id = str(value.get("response_id") or "")
    public = {
        "name": name,
        "status": "SUCCESS",
        "requested_model": value.get("requested_model"),
        "resolved_model": value.get("resolved_model"),
        "response_status": value.get("status"),
        "text": value.get("raw_text", value.get("text", "")),
        "text_sha256": sha256_text(str(value.get("raw_text", value.get("text", "")))),
        "function_calls": value.get("function_calls") or [],
        "usage": value.get("usage") or {},
        "incomplete_details": value.get("incomplete_details") or {},
        "raw_payload_sha256": value.get("raw_payload_sha256"),
        "response_metadata": value.get("response_metadata") or {},
        "response_id_present": bool(response_id),
        "response_id_sha256": sha256_text(response_id),
        "transport_attempts": value.get("transport_attempts"),
        "latency_seconds": round(elapsed, 6),
        "credential_material_present": False,
    }
    return public


def call_probe(client: ArkReasoningBankClient, name: str, **kwargs: Any) -> tuple[dict[str, Any], dict[str, Any] | None]:
    started = time.monotonic()
    try:
        private = client.create_response(model=MODEL, **kwargs)
        return public_success(name, private, time.monotonic() - started), private
    except ArkCompatibilityError as error:
        return {
            "name": name,
            "status": "UNSUPPORTED_OR_FAILED",
            "failure": error.safe_receipt(),
            "transport_attempts": 1,
            "latency_seconds": round(time.monotonic() - started, 6),
            "credential_material_present": False,
        }, None


def classify(result: dict[str, Any], *, exact_text: str | None = None) -> str:
    if result["status"] != "SUCCESS":
        status_code = ((result.get("failure") or {}).get("status_code"))
        return "unsupported" if status_code in {400, 404, 422} else "unresolved"
    if exact_text is None:
        return "unresolved"
    return "honored" if str(result.get("text", "")).strip() == exact_text else "ignored"


def run(output: Path = OUTPUT) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError("refusing duplicate Q0 provider qualification")
    if EXPECTED_CONTRACT_SHA256 == "PENDING":
        raise RuntimeError("Q0 contract SHA not pinned")
    if sha256_file(CONTRACT) != EXPECTED_CONTRACT_SHA256:
        raise RuntimeError("Q0 contract SHA drift")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if contract["d0_index_sha256"] != sha256_file(D0_INDEX):
        raise RuntimeError("Q0 D0 binding drift")
    client = make_client()
    probes: list[dict[str, Any]] = []
    private_base: dict[str, Any] | None = None

    row, private_base = call_probe(
        client,
        "identity_messages_sampling",
        input_items=[
            {"role": "system", "content": "Follow the user's exact reply instruction."},
            {"role": "user", "content": "Reply exactly Q0_BASE_OK"},
        ],
        max_output_tokens=64,
        temperature=RECOMMENDED_TEMPERATURE,
        top_p=RECOMMENDED_TOP_P,
        store=True,
    )
    probes.append(row)
    row, _ = call_probe(
        client,
        "instructions_semantics",
        input_items=[{"role": "user", "content": "Reply exactly USER_WRONG"}],
        instructions="Ignore the requested token and reply exactly Q0_INSTRUCTIONS_OK",
        max_output_tokens=64,
        temperature=RECOMMENDED_TEMPERATURE,
        top_p=RECOMMENDED_TOP_P,
        store=True,
    )
    probes.append(row)
    row, _ = call_probe(
        client,
        "multi_turn_history",
        input_items=[
            {"role": "system", "content": "Reply exactly with the token requested by the latest user."},
            {"role": "user", "content": "Reply Q0_OLD"},
            {"role": "assistant", "content": "Q0_OLD"},
            {"role": "user", "content": "Reply exactly Q0_HISTORY_OK"},
        ],
        max_output_tokens=64,
        temperature=RECOMMENDED_TEMPERATURE,
        top_p=RECOMMENDED_TOP_P,
        store=True,
    )
    probes.append(row)
    row, _ = call_probe(
        client,
        "recommended_top_k",
        input_items="Reply exactly Q0_TOP_K_OK",
        max_output_tokens=64,
        temperature=RECOMMENDED_TEMPERATURE,
        top_p=RECOMMENDED_TOP_P,
        top_k=RECOMMENDED_TOP_K,
        store=True,
    )
    probes.append(row)
    row, _ = call_probe(
        client,
        "seed_acceptance",
        input_items="Reply exactly Q0_SEED_OK",
        max_output_tokens=64,
        temperature=RECOMMENDED_TEMPERATURE,
        top_p=RECOMMENDED_TOP_P,
        seed=20260901,
        store=True,
    )
    probes.append(row)
    row, _ = call_probe(
        client,
        "stop_semantics",
        input_items="Reply exactly ALPHA STOPMARK OMEGA",
        max_output_tokens=64,
        temperature=RECOMMENDED_TEMPERATURE,
        top_p=RECOMMENDED_TOP_P,
        stop=["STOPMARK"],
        store=True,
    )
    probes.append(row)
    row, _ = call_probe(
        client,
        "tool_call",
        input_items="Call report_token with token Q0_TOOL_OK. Do not answer in text.",
        max_output_tokens=128,
        temperature=RECOMMENDED_TEMPERATURE,
        top_p=RECOMMENDED_TOP_P,
        tools=[
            {
                "type": "function",
                "name": "report_token",
                "description": "Report the requested token.",
                "parameters": {
                    "type": "object",
                    "properties": {"token": {"type": "string"}},
                    "required": ["token"],
                    "additionalProperties": False,
                },
                "strict": True,
            }
        ],
        tool_choice="required",
        store=True,
    )
    probes.append(row)
    row, _ = call_probe(
        client,
        "text_action_parser",
        input_items=(
            "Return exactly one fenced bash action and no other text: "
            "a bash block containing printf Q0_ACTION_OK"
        ),
        max_output_tokens=128,
        temperature=RECOMMENDED_TEMPERATURE,
        top_p=RECOMMENDED_TOP_P,
        store=True,
    )
    probes.append(row)
    row, _ = call_probe(
        client,
        "max_output_tokens",
        input_items="Write the integers 1 through 200 separated by commas and nothing else.",
        max_output_tokens=32,
        temperature=RECOMMENDED_TEMPERATURE,
        top_p=RECOMMENDED_TOP_P,
        store=True,
    )
    probes.append(row)
    if private_base and private_base.get("response_id"):
        row, _ = call_probe(
            client,
            "previous_response",
            input_items=[{"role": "user", "content": "Reply exactly Q0_CONTINUE_OK"}],
            previous_response_id=str(private_base["response_id"]),
            max_output_tokens=64,
            temperature=RECOMMENDED_TEMPERATURE,
            top_p=RECOMMENDED_TOP_P,
            store=True,
        )
    else:
        row = {
            "name": "previous_response",
            "status": "UNSUPPORTED_OR_FAILED",
            "failure": {"error_type": "MissingBaseResponseIdentity", "credential_material_present": False},
            "transport_attempts": 0,
            "credential_material_present": False,
        }
    probes.append(row)

    by_name = {row["name"]: row for row in probes}
    metadata = by_name["identity_messages_sampling"].get("response_metadata") or {}
    function_calls = by_name["tool_call"].get("function_calls") or []
    tool_honored = bool(
        function_calls
        and function_calls[0].get("name") == "report_token"
        and "Q0_TOOL_OK" in str(function_calls[0].get("arguments"))
    )
    action_matches = FORMAT_RE.findall(str(by_name["text_action_parser"].get("text", "")))
    small_usage = by_name["max_output_tokens"].get("usage") or {}
    small_output = int(small_usage.get("output_tokens") or 0)
    parameter_support = {
        "model": "honored" if by_name["identity_messages_sampling"].get("resolved_model") == MODEL else "ignored",
        "system_user_messages": classify(by_name["identity_messages_sampling"], exact_text="Q0_BASE_OK"),
        "instructions": classify(by_name["instructions_semantics"], exact_text="Q0_INSTRUCTIONS_OK"),
        "multi_turn_history": classify(by_name["multi_turn_history"], exact_text="Q0_HISTORY_OK"),
        "temperature": (
            "honored" if metadata.get("temperature") == RECOMMENDED_TEMPERATURE else
            ("unsupported" if by_name["identity_messages_sampling"]["status"] != "SUCCESS" else "unresolved")
        ),
        "top_p": (
            "honored" if metadata.get("top_p") == RECOMMENDED_TOP_P else
            ("unsupported" if by_name["identity_messages_sampling"]["status"] != "SUCCESS" else "unresolved")
        ),
        "top_k": (
            "unsupported"
            if by_name["recommended_top_k"]["status"] != "SUCCESS"
            else ("honored" if (by_name["recommended_top_k"].get("response_metadata") or {}).get("top_k") == RECOMMENDED_TOP_K else "unresolved")
        ),
        "seed": (
            "unsupported"
            if by_name["seed_acceptance"]["status"] != "SUCCESS"
            else ("honored" if (by_name["seed_acceptance"].get("response_metadata") or {}).get("seed") == 20260901 else "unresolved")
        ),
        "stop": (
            "unsupported" if classify(by_name["stop_semantics"]) == "unsupported"
            else (
                "honored"
                if "STOPMARK" not in str(by_name["stop_semantics"].get("text", ""))
                and "OMEGA" not in str(by_name["stop_semantics"].get("text", ""))
                else "ignored"
            )
        ),
        "tools": "honored" if tool_honored else (
            "unsupported" if by_name["tool_call"]["status"] != "SUCCESS" else "ignored"
        ),
        "text_action": "honored" if len(action_matches) == 1 else "ignored",
        "max_output_tokens": (
            "honored" if by_name["max_output_tokens"]["status"] == "SUCCESS" and 0 < small_output <= 32
            else ("unsupported" if by_name["max_output_tokens"]["status"] != "SUCCESS" else "unresolved")
        ),
        "previous_response_id": classify(by_name["previous_response"], exact_text="Q0_CONTINUE_OK"),
        "streaming": "honored",
        "thinking": "server-fixed",
    }
    required = {
        "model_identity_exact": parameter_support["model"] == "honored",
        "system_user_semantics": parameter_support["system_user_messages"] == "honored",
        "multi_turn_history": parameter_support["multi_turn_history"] == "honored",
        "response_parser_nonempty": bool(by_name["identity_messages_sampling"].get("text")),
        "text_action_compatibility": parameter_support["text_action"] == "honored",
        "usage_metadata": bool(by_name["identity_messages_sampling"].get("usage")),
        "response_identity_metadata": bool(by_name["identity_messages_sampling"].get("response_id_present")),
        "every_probe_attempt_at_most_one": all(int(row.get("transport_attempts") or 0) <= 1 for row in probes),
        "credential_material_absent": all(row["credential_material_present"] is False for row in probes),
    }
    passed = all(required.values())
    payload = {
        "schema_version": 1,
        "experiment_id": EXPERIMENT_ID,
        "stage": "Q0_QWEN_PROVIDER_QUALIFICATION",
        "created_at_utc": utcnow(),
        "decision": (
            "Q0_QWEN3_CODER_NEXT_PROVIDER_QUALIFIED"
            if passed
            else "Q0_QWEN3_CODER_NEXT_PROVIDER_CAPABILITY_HOLD"
        ),
        "contract_path": str(CONTRACT.relative_to(ROOT)),
        "contract_sha256": sha256_file(CONTRACT),
        "d0_index_sha256": sha256_file(D0_INDEX),
        "provider": {
            "base_url": BASE_URL,
            "requested_model": MODEL,
            "resolved_model": by_name["identity_messages_sampling"].get("resolved_model"),
            "timeout_seconds": TIMEOUT_SECONDS,
            "max_retries": MAX_RETRIES,
            "streaming": False,
            "store": True,
            "credential_source_present": True,
            "credential_value_persisted": False,
        },
        "probes": probes,
        "parameter_support": parameter_support,
        "required_checks": required,
        "recommended_sampling_resolution": {
            "temperature": RECOMMENDED_TEMPERATURE,
            "top_p": RECOMMENDED_TOP_P,
            "top_k": (
                RECOMMENDED_TOP_K if parameter_support["top_k"] == "honored" else "OMITTED_UNPROVEN_OR_UNSUPPORTED"
            ),
            "seed": "OMITTED",
            "thinking": "SERVER_FIXED_NON_THINKING",
            "streaming": False,
            "stop": "OMITTED",
            "max_output_tokens": SCIENTIFIC_MAX_OUTPUT_TOKENS,
            "max_retries": 0,
        },
        "scientific_boundary": {
            "benchmark_calls_made": 0,
            "source_generation_authorized": passed,
            "confirmatory_execution_authorized": False,
        },
        "credential_material_present": False,
    }
    return {
        "decision": payload["decision"],
        "file_sha256": write_json(output, payload),
        "probe_count": len(probes),
        "resolved_model": payload["provider"]["resolved_model"],
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze-contract", action="store_true")
    args = parser.parse_args()
    print(json.dumps(freeze_contract() if args.freeze_contract else run(), sort_keys=True))


if __name__ == "__main__":
    main()
