#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.ark_provider import ArkResponseStateError, ArkResponsesClient, ArkSettings
from research_pipeline.config import load_env_file
from research_pipeline.e2_r17_m3r4_execution_guard import FRESH_IDENTITY_STATUS, PLAN_ROUTE
from research_pipeline.e2_r17_m3r4_execution_plan import MAX_OUTPUT_TOKENS, REQUESTED_MODEL, REQUIRED_RESOLVED_MODEL


PROMPT = (
    "This is a non-scientific E2-R17 M3R4 Ark Plan model-identity requalification. "
    "Return exactly M3R4_IDENTITY_OK and nothing else."
)


class ClientLike(Protocol):
    settings: Any

    def respond(self, prompt: str, **kwargs: Any) -> dict[str, Any]: ...


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def sanitize(message: str) -> str:
    text = re.sub(r"resp_[A-Za-z0-9_]+", "resp_[REDACTED]", str(message))
    text = re.sub(r"Request id:\s*[A-Za-z0-9_]+", "Request id: [REDACTED]", text)
    return text[:1200]


def qualify_once(client: ClientLike) -> dict[str, Any]:
    row: dict[str, Any] = {
        "requested_model": REQUESTED_MODEL,
        "required_resolved_model": REQUIRED_RESOLVED_MODEL,
        "prompt_sha256": sha_text(PROMPT),
        "provider_generation_attempts": 1,
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "thinking_requested": "disabled",
        "temperature": 0,
        "provider_retry_limit": int(client.settings.max_retries),
        "hidden_provider_retry_used": False,
        "scientific_outcome": False,
        "benchmark_data_accessed": False,
    }
    try:
        result = client.respond(
            PROMPT,
            model=REQUESTED_MODEL,
            max_output_tokens=MAX_OUTPUT_TOKENS,
            temperature=0,
            thinking="disabled",
            allow_thinking_compatibility_fallback=False,
        )
        text = str(result.get("text") or "")
        resolved = str(result.get("resolved_model") or "")
        checks = {
            "text_exact": text.strip() == "M3R4_IDENTITY_OK",
            "resolved_model_exact": resolved == REQUIRED_RESOLVED_MODEL,
            "provider_status_completed": str(result.get("status") or "") in {"completed", "success", ""},
        }
        row.update(
            {
                "status": "PASS" if all(checks.values()) else "HOLD_IDENTITY_DRIFT",
                "resolved_model": resolved,
                "checks": checks,
                "usage": result.get("usage") or {},
                "provider_status": result.get("status"),
                "response_id_sha256": sha_text(str(result.get("response_id") or "")),
                "raw_text_sha256": sha_text(text),
                "raw_text": text,
            }
        )
    except ArkResponseStateError as exc:
        receipt = exc.receipt()
        row.update(
            {
                "status": "HOLD_PROVIDER_RESPONSE_STATE",
                "resolved_model": receipt.get("resolved_model"),
                "provider_status": receipt.get("status"),
                "incomplete_reason": receipt.get("incomplete_reason"),
                "response_id_sha256": sha_text(str(receipt.get("response_id") or "")),
                "automatic_retry_authorized": False,
            }
        )
    except Exception as exc:  # noqa: BLE001 - fail-closed receipt is required
        message = str(exc)
        quota = "AccountQuotaExceeded" in message or "quota" in message.lower()
        row.update(
            {
                "status": "HOLD_PROVIDER_QUOTA" if quota else "HOLD_PROVIDER_PROTOCOL",
                "error_type": type(exc).__name__,
                "error_message_sanitized": sanitize(message),
                "error_sha256": sha_text(message),
                "automatic_retry_authorized": False,
            }
        )
    return row


def build_payload(*, row: dict[str, Any], route: str, source_default_model: str | None) -> dict[str, Any]:
    pass_row = row.get("status") == "PASS"
    status = FRESH_IDENTITY_STATUS if pass_row else str(row.get("status") or "HOLD")
    return {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-m3r4-scientific-tranche-model-identity-qualification",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": status,
        "scientific_tranche": "E2-R17-M3R4",
        "scientific_experiment": False,
        "route": route,
        "default_model": source_default_model,
        "requested_and_resolved": {
            REQUESTED_MODEL: {
                "requested": REQUESTED_MODEL,
                "resolved": row.get("resolved_model"),
                "thinking_requested": "disabled",
            }
        },
        "provider_retry_limit": int(row.get("provider_retry_limit", 0)),
        "max_output_tokens_smoke": MAX_OUTPUT_TOKENS,
        "qualification_call": row,
        "checks": {
            "route_is_ark_plan": route.rstrip("/") == PLAN_ROUTE,
            "qualification_call_pass": pass_row,
            "requested_model_exact": row.get("requested_model") == REQUESTED_MODEL,
            "resolved_model_exact": row.get("resolved_model") == REQUIRED_RESOLVED_MODEL,
            "provider_retry_zero": int(row.get("provider_retry_limit", -1)) == 0,
            "thinking_disabled": row.get("thinking_requested") == "disabled",
            "max_output_tokens_8192": int(row.get("max_output_tokens", -1)) == MAX_OUTPUT_TOKENS,
        },
        "drift_policy": "Any resolved-model, route, thinking, retry, or 8192-output compatibility drift is HOLD_REVIEW_REQUIRED; no automatic model substitution or repeated qualification until separately authorized.",
        "authority": {
            "preexecution_identity_qualification": pass_row,
            "scientific_experiment": False,
            "provider_scientific_io": False,
            "actor_measurement": False,
            "updater": False,
            "analysis": False,
            "m4": False,
            "e3": False,
            "paper_promotion": False,
            "submission": False,
        },
        "private_credentials_included": False,
        "raw_response_ids_included": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    load_env_file(args.env_file)
    source = ArkSettings.from_env(required=True)
    if source.base_url.rstrip("/") != PLAN_ROUTE:
        raise RuntimeError("M3R4 model identity qualification refuses any non-Ark-Plan route")
    settings = ArkSettings(
        api_key=source.api_key,
        base_url=source.base_url,
        default_model=source.default_model,
        timeout_seconds=300.0,
        max_retries=0,
    )
    row = qualify_once(ArkResponsesClient(settings))
    payload = build_payload(row=row, route=source.base_url, source_default_model=source.default_model)
    atomic_json(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["status"] == FRESH_IDENTITY_STATUS else 2


if __name__ == "__main__":
    raise SystemExit(main())
