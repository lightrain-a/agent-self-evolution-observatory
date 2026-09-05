from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable

from research_pipeline.agent_constraint_externality_runner_core import (
    OBJECT_ID,
    ensure_no_secret,
    sha256_value,
)
from research_pipeline.config import DEFAULT_ENV_FILE, load_env_file

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
READINESS_V2 = GENERATED / "agent-constraint-externality-confirmatory-execution-readiness-v2-20260905.json"
RECOVERY_PROPOSAL = GENERATED / "agent-constraint-externality-direct-qwen37flash-v4-r2-recovery-proposal-20260903.json"
AUTH_OUTPUT = GENERATED / "agent-constraint-externality-provider-readiness-human-authorization-r1-20260905.json"
RESULT_OUTPUT = GENERATED / "agent-constraint-externality-provider-readiness-r1-20260905.json"

BASE_URL = "https://api.aa.com.cn/api/v1"
MODEL_ID = "qwen3.7-flash"
AUTHORIZED_AT = "2026-09-05T13:10:00+08:00"
AUTHORIZATION_SOURCE = "CURRENT_SESSION_USER_MESSAGE_CONTINUE_AFTER_EXPLICIT_PROVIDER_READINESS_ONLY_GATE"
SYNTHETIC_INSTRUCTIONS = (
    "This is a non-scientific provider readiness check. Do not use tools. "
    "Reply with the single token READY."
)
SYNTHETIC_INPUT = "READY"


class ProviderReadinessError(RuntimeError):
    pass


def read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ProviderReadinessError(f"missing required artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def verified_content(path: Path) -> dict[str, Any]:
    payload = read_json(path)
    claimed = payload.get("content_sha256")
    unsigned = dict(payload)
    unsigned.pop("content_sha256", None)
    if claimed != sha256_value(unsigned):
        raise ProviderReadinessError(f"content hash mismatch: {path}")
    return payload


def _downstream_authority_false() -> dict[str, bool]:
    return {
        "provider_execution": False,
        "gate0": False,
        "gate1": False,
        "development_repeat_qualification": False,
        "confirmatory_source_and_repair": False,
        "target_only_verification": False,
        "rq1_rq2_execution": False,
        "rq1_analysis": False,
        "rq2_analysis": False,
        "rq3": False,
        "rq4": False,
        "secondary_actor": False,
        "external_updater": False,
        "paper_claim": False,
    }


def _verify_parent_contracts() -> tuple[dict[str, Any], dict[str, Any]]:
    readiness = verified_content(READINESS_V2)
    recovery = verified_content(RECOVERY_PROPOSAL)
    if readiness.get("status") != "EXECUTION_SEQUENCE_MECHANICALLY_CLOSED_AUTHORITY_FALSE":
        raise ProviderReadinessError("confirmatory readiness V2 is not mechanically closed")
    if readiness.get("scientific_object") != OBJECT_ID:
        raise ProviderReadinessError("confirmatory readiness scientific object drifted")
    if any(bool(v) for v in readiness.get("authority", {}).values()):
        raise ProviderReadinessError("confirmatory readiness unexpectedly grants authority")
    if recovery.get("object_id") != OBJECT_ID:
        raise ProviderReadinessError("R2 recovery proposal object drifted")
    if recovery.get("status") != "DIRECT_QWEN37FLASH_V4_R2_RECOVERY_PROPOSAL_WAIT_PROVIDER_CREDIT":
        raise ProviderReadinessError("R2 recovery proposal status drifted")
    gate = recovery.get("credit_readiness_gate", {})
    expected = {
        "required_before_execution_contract": True,
        "test_type": "NON_SCIENTIFIC_SYNTHETIC_RESPONSES_REQUEST",
        "model": MODEL_ID,
        "tools": 0,
        "max_retries": 0,
        "pass_condition": "HTTP_2XX_WITH_COMPLETED_MODEL_RESPONSE",
        "fail_condition": "ANY_HTTP_OR_PROVIDER_ERROR",
        "credit_check_outcome_must_be_frozen_before_R2_SCIENTIFIC_DISPATCH": True,
    }
    if gate != expected:
        raise ProviderReadinessError(f"credit-readiness gate drifted: {gate}")
    candidate = recovery.get("candidate", {})
    if candidate.get("model_id") != MODEL_ID or candidate.get("base_url") != BASE_URL:
        raise ProviderReadinessError("frozen provider candidate drifted")
    return readiness, recovery


def build_authorization() -> dict[str, Any]:
    readiness, recovery = _verify_parent_contracts()
    payload: dict[str, Any] = {
        "schema_version": "ace-provider-readiness-human-authorization-r1-v1",
        "object_id": OBJECT_ID,
        "status": "USER_AUTHORIZED_NON_SCIENTIFIC_PROVIDER_READINESS_R1_ONLY",
        "authorized_at": AUTHORIZED_AT,
        "authorization_source": AUTHORIZATION_SOURCE,
        "scope": "ONE_NON_SCIENTIFIC_QWEN37FLASH_RESPONSES_READINESS_ATTEMPT_ZERO_TOOLS_ZERO_RETRIES",
        "provider": recovery["candidate"]["provider"],
        "base_url": BASE_URL,
        "model_id": MODEL_ID,
        "request_contract": {
            "endpoint": "/responses",
            "tools": 0,
            "temperature": 0,
            "store": False,
            "max_retries": 0,
            "contains_scientific_case": False,
            "contains_appworld_state": False,
            "contains_repair_artifact": False,
        },
        "parent_readiness_content_sha256": readiness["content_sha256"],
        "r2_recovery_proposal_content_sha256": recovery["content_sha256"],
        "authority": {
            "provider_readiness_check": True,
            **_downstream_authority_false(),
        },
        "non_scientific_provider_requests_authorized": 1,
        "scientific_provider_calls_authorized": 0,
        "scientific_outcomes_observed": 0,
        "forbidden": [
            "Gate 0 dispatch",
            "AppWorld scientific case dispatch",
            "provider/model substitution",
            "retry after any dispatched readiness request",
            "scientific outcome interpretation",
        ],
    }
    payload["content_sha256"] = sha256_value(payload)
    ensure_no_secret(payload)
    return payload


def verify_authorization(payload: dict[str, Any]) -> None:
    claimed = payload.get("content_sha256")
    unsigned = dict(payload)
    unsigned.pop("content_sha256", None)
    if claimed != sha256_value(unsigned):
        raise ProviderReadinessError("authorization content hash mismatch")
    if payload.get("status") != "USER_AUTHORIZED_NON_SCIENTIFIC_PROVIDER_READINESS_R1_ONLY":
        raise ProviderReadinessError("authorization status mismatch")
    authority = payload.get("authority", {})
    if authority.get("provider_readiness_check") is not True:
        raise ProviderReadinessError("provider-readiness authority is not open")
    bad = [k for k, v in authority.items() if k != "provider_readiness_check" and bool(v)]
    if bad:
        raise ProviderReadinessError(f"authorization leaks downstream authority: {bad}")
    if payload.get("non_scientific_provider_requests_authorized") != 1:
        raise ProviderReadinessError("authorization request count drifted")
    if payload.get("scientific_provider_calls_authorized") != 0:
        raise ProviderReadinessError("authorization unexpectedly permits scientific provider calls")


def _request_body() -> dict[str, Any]:
    return {
        "model": MODEL_ID,
        "instructions": SYNTHETIC_INSTRUCTIONS,
        "input": SYNTHETIC_INPUT,
        "tools": [],
        "temperature": 0,
        "store": False,
    }


def _base_result(auth: dict[str, Any]) -> dict[str, Any]:
    body = _request_body()
    return {
        "schema_version": "ace-provider-readiness-r1-v1",
        "object_id": OBJECT_ID,
        "execution_id": "ACE-PROVIDER-READINESS-R1-20260905",
        "provider": auth["provider"],
        "base_url": BASE_URL,
        "model_id": MODEL_ID,
        "test_type": "NON_SCIENTIFIC_SYNTHETIC_RESPONSES_REQUEST",
        "request_contract": {
            "endpoint": "/responses",
            "tools": 0,
            "temperature": 0,
            "store": False,
            "max_retries": 0,
            "request_body_sha256": sha256_value(body),
            "contains_scientific_case": False,
            "contains_appworld_state": False,
            "contains_repair_artifact": False,
        },
        "authorization_content_sha256": auth["content_sha256"],
        "readiness_content_sha256": auth["parent_readiness_content_sha256"],
        "r2_recovery_proposal_content_sha256": auth["r2_recovery_proposal_content_sha256"],
        "authority": _downstream_authority_false(),
        "scientific_provider_calls_created": 0,
        "scientific_outcomes_created": 0,
        "secrets_persisted": False,
        "retry_attempted": False,
    }


def _error_fields(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    error = payload.get("error")
    if not isinstance(error, dict):
        return {}
    out: dict[str, Any] = {}
    for key in ("type", "code"):
        value = error.get(key)
        if isinstance(value, (str, int, float, bool)) or value is None:
            out[key] = value
    return out


def _read_http_error(exc: urllib.error.HTTPError) -> dict[str, Any]:
    try:
        raw = exc.read()
        payload = json.loads(raw.decode("utf-8")) if raw else {}
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        payload = {}
    return _error_fields(payload)


def run_readiness(
    auth: dict[str, Any],
    *,
    api_key: str | None = None,
    base_url: str | None = None,
    opener: Callable[..., Any] = urllib.request.urlopen,
) -> dict[str, Any]:
    _verify_parent_contracts()
    verify_authorization(auth)
    result = _base_result(auth)

    if api_key is None:
        load_env_file(DEFAULT_ENV_FILE)
        api_key = os.getenv("AA_API_KEY", "").strip()
    else:
        api_key = api_key.strip()
    if base_url is None:
        base_url = os.getenv("AA_BASE_URL", BASE_URL).rstrip("/")
    else:
        base_url = base_url.rstrip("/")
    if base_url != BASE_URL:
        raise ProviderReadinessError("AA_BASE_URL drifted from frozen provider base URL")

    if not api_key:
        result.update({
            "status": "PROVIDER_READINESS_R1_NOT_DISPATCHED_CREDENTIAL_UNAVAILABLE_STOP",
            "classification": "LOCAL_APPROVED_SECRET_NOT_CONFIGURED",
            "provider_request_count": 0,
            "http_status": None,
            "completed_model_response": False,
            "resolved_model": None,
            "readiness_pass": False,
            "next_legal_action": (
                "RESTORE_APPROVED_AA_API_KEY_SECRET_THEN_REQUIRE_NEW_EXPLICIT_PROVIDER_READINESS_AUTHORITY; "
                "GATE0_AND_ALL_SCIENTIFIC_DISPATCH_REMAIN_CLOSED"
            ),
        })
        result["content_sha256"] = sha256_value(result)
        ensure_no_secret(result)
        return result

    body = _request_body()
    request = urllib.request.Request(
        BASE_URL + "/responses",
        data=json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"),
        headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"},
        method="POST",
    )
    provider_request_count = 1
    try:
        response = opener(request, timeout=60)
        try:
            http_status = int(getattr(response, "status", response.getcode()))
            raw = response.read()
        finally:
            close = getattr(response, "close", None)
            if callable(close):
                close()
    except urllib.error.HTTPError as exc:
        result.update({
            "status": "PROVIDER_READINESS_R1_PROVIDER_ERROR_STOP",
            "classification": "HTTP_OR_PROVIDER_ERROR",
            "provider_request_count": provider_request_count,
            "http_status": int(exc.code),
            "provider_error": _read_http_error(exc),
            "completed_model_response": False,
            "resolved_model": None,
            "readiness_pass": False,
            "next_legal_action": (
                "STOP_NO_SCIENTIFIC_DISPATCH; RESTORE_PROVIDER_CREDIT_OR_INTERFACE_THEN_REQUIRE_NEW_EXPLICIT_PROVIDER_READINESS_AUTHORITY"
            ),
        })
        result["content_sha256"] = sha256_value(result)
        ensure_no_secret(result)
        return result
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        result.update({
            "status": "PROVIDER_READINESS_R1_TRANSPORT_ERROR_STOP",
            "classification": type(exc).__name__,
            "provider_request_count": provider_request_count,
            "http_status": None,
            "completed_model_response": False,
            "resolved_model": None,
            "readiness_pass": False,
            "next_legal_action": (
                "STOP_NO_SCIENTIFIC_DISPATCH; RESTORE_PROVIDER_TRANSPORT_THEN_REQUIRE_NEW_EXPLICIT_PROVIDER_READINESS_AUTHORITY"
            ),
        })
        result["content_sha256"] = sha256_value(result)
        ensure_no_secret(result)
        return result

    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        payload = None
    completed = isinstance(payload, dict) and payload.get("status") == "completed"
    resolved_model = payload.get("model") if isinstance(payload, dict) else None
    output = payload.get("output") if isinstance(payload, dict) else None
    output_present = isinstance(output, list) and len(output) > 0
    pass_check = 200 <= http_status < 300 and completed and resolved_model == MODEL_ID and output_present
    if pass_check:
        status = "PROVIDER_READINESS_R1_PASS_GATE0_AUTHORITY_STILL_CLOSED"
        classification = "CREDIT_INTERFACE_AND_FROZEN_MODEL_BINDING_READY"
        next_legal_action = (
            "EXPLICIT_SEPARATE_HUMAN_AUTHORITY_FOR_GATE0_ONLY; GATE0_AND_ALL_SCIENTIFIC_DISPATCH_REMAIN_CLOSED_UNTIL_THEN"
        )
    else:
        status = "PROVIDER_READINESS_R1_INTERFACE_OR_MODEL_BINDING_FAIL_STOP"
        classification = "COMPLETION_OR_MODEL_BINDING_CONTRACT_NOT_MET"
        next_legal_action = "STOP_NO_SCIENTIFIC_DISPATCH; ADJUDICATE_PROVIDER_INTERFACE_BEFORE_ANY_NEW_AUTHORITY"
    result.update({
        "status": status,
        "classification": classification,
        "provider_request_count": provider_request_count,
        "http_status": http_status,
        "completed_model_response": bool(completed),
        "output_present": bool(output_present),
        "resolved_model": resolved_model if isinstance(resolved_model, str) else None,
        "readiness_pass": bool(pass_check),
        "next_legal_action": next_legal_action,
    })
    result["content_sha256"] = sha256_value(result)
    ensure_no_secret(result)
    return result


def verify_result(payload: dict[str, Any]) -> None:
    claimed = payload.get("content_sha256")
    unsigned = dict(payload)
    unsigned.pop("content_sha256", None)
    if claimed != sha256_value(unsigned):
        raise ProviderReadinessError("provider-readiness result content hash mismatch")
    if payload.get("scientific_provider_calls_created") != 0 or payload.get("scientific_outcomes_created") != 0:
        raise ProviderReadinessError("provider readiness created scientific work")
    if any(bool(v) for v in payload.get("authority", {}).values()):
        raise ProviderReadinessError("provider-readiness result leaks downstream authority")
    count = payload.get("provider_request_count")
    if count not in {0, 1}:
        raise ProviderReadinessError("provider readiness request count must be 0 or 1")
    if payload.get("retry_attempted") is not False:
        raise ProviderReadinessError("provider readiness must never retry")
    if payload.get("readiness_pass"):
        if count != 1 or payload.get("status") != "PROVIDER_READINESS_R1_PASS_GATE0_AUTHORITY_STILL_CLOSED":
            raise ProviderReadinessError("invalid provider-readiness PASS state")
        if payload.get("resolved_model") != MODEL_ID or payload.get("completed_model_response") is not True:
            raise ProviderReadinessError("provider-readiness PASS lacks exact frozen model completion")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authorize", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    selected = sum(bool(x) for x in (args.authorize, args.run, args.check))
    if selected != 1:
        raise SystemExit("choose exactly one of --authorize, --run, --check")

    if args.authorize:
        if AUTH_OUTPUT.exists():
            raise ProviderReadinessError(f"refusing overwrite of authorization artifact: {AUTH_OUTPUT}")
        payload = build_authorization()
        AUTH_OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif args.run:
        if RESULT_OUTPUT.exists():
            raise ProviderReadinessError(f"refusing overwrite of provider-readiness result: {RESULT_OUTPUT}")
        auth = verified_content(AUTH_OUTPUT)
        payload = run_readiness(auth)
        verify_result(payload)
        RESULT_OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        auth = verified_content(AUTH_OUTPUT)
        verify_authorization(auth)
        payload = verified_content(RESULT_OUTPUT)
        verify_result(payload)

    print(json.dumps({
        "status": payload["status"],
        "content_sha256": payload["content_sha256"],
        "provider_request_count": payload.get("provider_request_count", 0),
        "readiness_pass": payload.get("readiness_pass", False),
        "gate0_authority": payload.get("authority", {}).get("gate0", False),
        "scientific_provider_calls_created": payload.get("scientific_provider_calls_created", 0),
        "scientific_outcomes_created": payload.get("scientific_outcomes_created", 0),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
