#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.ark_provider import ArkResponseStateError, ArkResponsesClient, ArkSettings
from research_pipeline.config import load_env_file

PLAN_BASE_URL = "https://ark.cn-beijing.volces.com/api/plan/v3"
MODELS = ("deepseek-v4-pro", "kimi-k3")
DEEPSEEK_REQUIRED_RESOLVED = "deepseek-v4-pro-260425"


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sanitize_error(message: str) -> str:
    text = re.sub(r"resp_[A-Za-z0-9_]+", "resp_[REDACTED]", str(message))
    text = re.sub(r"Request id:\s*[A-Za-z0-9_]+", "Request id: [REDACTED]", text)
    return text[:500]


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(path)


def call_once(
    client: ArkResponsesClient,
    model: str,
    *,
    max_output_tokens: int,
    thinking: str | None,
    call_kind: str,
) -> dict[str, Any]:
    prompt = (
        "This is a zero-authority provider/model-identity protocol smoke for an internal research debate. "
        "Return exactly PLAN_OK and nothing else."
    )
    row: dict[str, Any] = {
        "call_kind": call_kind,
        "requested_model": model,
        "prompt_sha256": sha(prompt),
        "max_output_tokens": max_output_tokens,
        "thinking_requested": thinking,
        "provider_generation_attempts": 1,
        "provider_retry_limit": client.settings.max_retries,
        "hidden_provider_retry_used": False,
        "automatic_thinking_compatibility_fallback_allowed": False,
        "scientific_outcome": False,
    }
    try:
        try:
            result = client.respond(
                prompt,
                model=model,
                max_output_tokens=max_output_tokens,
                temperature=0,
                thinking=thinking,
                allow_thinking_compatibility_fallback=False,
            )
        except ArkResponseStateError as exc:
            state = exc.receipt()
            row["initial_response_state"] = {
                "status": state.get("status"),
                "requested_model": state.get("requested_model"),
                "resolved_model": state.get("resolved_model"),
                "incomplete_reason": state.get("incomplete_reason"),
                "response_id_sha256": sha(str(state.get("response_id") or "")),
            }
            if not exc.response_id:
                raise
            try:
                polled = client.poll_response(exc.response_id, max_polls=4, interval_seconds=1.0)
            except Exception as poll_error:
                row.update(
                    {
                        "status": "HOLD_PROVIDER_RESPONSE_RETRIEVAL",
                        "poll_error_type": type(poll_error).__name__,
                        "poll_error_message_sanitized": sanitize_error(str(poll_error)),
                        "poll_error_sha256": sha(str(poll_error)),
                    }
                )
                return row
            if not polled.get("text"):
                row.update(
                    {
                        "status": "HOLD_PROVIDER_RESPONSE_STATE",
                        "polled_status": polled.get("status"),
                        "poll_count": polled.get("poll_count"),
                    }
                )
                return row
            result = {
                "requested_model": model,
                "resolved_model": polled.get("resolved_model"),
                "text": polled.get("text"),
                "usage": polled.get("usage") or {},
                "response_id": polled.get("response_id") or exc.response_id,
                "status": polled.get("status"),
                "get_poll_recovery": True,
                "poll_count": polled.get("poll_count"),
            }
        text = str(result.get("text") or "")
        resolved = str(result.get("resolved_model") or "")
        checks = {
            "text_exact": text.strip() == "PLAN_OK",
            "resolved_model_present": bool(resolved),
            "deepseek_resolved_exact": (
                resolved == DEEPSEEK_REQUIRED_RESOLVED if model == "deepseek-v4-pro" else True
            ),
        }
        row.update(
            {
                "status": "PASS" if all(checks.values()) else "FAIL",
                "resolved_model": resolved,
                "checks": checks,
                "usage": result.get("usage") or {},
                "response_id_sha256": sha(str(result.get("response_id") or "")),
                "raw_text": text,
                "raw_text_sha256": sha(text),
                "provider_status": result.get("status"),
                "get_poll_recovery": bool(result.get("get_poll_recovery", False)),
                "poll_count": result.get("poll_count", 0),
            }
        )
    except Exception as exc:
        message = str(exc)
        subscription = "InvalidSubscription" in message or "valid AgentPlan subscription" in message
        row.update(
            {
                "status": "HOLD_PROVIDER_SUBSCRIPTION" if subscription else "FAIL_PROVIDER_PROTOCOL",
                "error_type": type(exc).__name__,
                "error_class": "ARK_PLAN_SUBSCRIPTION" if subscription else "OTHER",
                "error_message_sanitized": "Ark Plan subscription unavailable" if subscription else sanitize_error(message),
                "error_sha256": sha(message),
            }
        )
    return row


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--call-kind", default="INITIAL_PROTOCOL_SMOKE")
    parser.add_argument("--max-output-tokens", type=int, default=32)
    parser.add_argument("--thinking", choices=("disabled", "enabled", "none"), default="none")
    parser.add_argument("--compatibility-parent", type=Path)
    args = parser.parse_args()

    load_env_file(args.env_file)
    source = ArkSettings.from_env(required=True)
    if source.base_url.rstrip("/") != PLAN_BASE_URL:
        raise RuntimeError("R17 debate qualifier refuses non-Plan Ark route")
    settings = ArkSettings(
        api_key=source.api_key,
        base_url=source.base_url,
        default_model=source.default_model,
        timeout_seconds=240.0,
        max_retries=0,
    )
    client = ArkResponsesClient(settings)
    thinking = None if args.thinking == "none" else args.thinking
    rows = [
        call_once(
            client,
            model,
            max_output_tokens=args.max_output_tokens,
            thinking=thinking,
            call_kind=args.call_kind,
        )
        for model in MODELS
    ]
    status = "PASS" if all(row.get("status") == "PASS" for row in rows) else (
        "HOLD_PROVIDER_SUBSCRIPTION"
        if any(row.get("status") == "HOLD_PROVIDER_SUBSCRIPTION" for row in rows)
        else "HOLD_OR_FAIL"
    )
    parent = None
    if args.compatibility_parent:
        parent = {
            "path": str(args.compatibility_parent),
            "sha256": hashlib.sha256(args.compatibility_parent.read_bytes()).hexdigest(),
            "separate_generation_calls_declared": True,
        }
    payload = {
        "schema_version": "1.1",
        "artifact_type": "e2-r17-search-projection-debate-model-qualification",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": status,
        "call_kind": args.call_kind,
        "compatibility_parent": parent,
        "route": source.base_url,
        "route_is_ark_plan": source.base_url.rstrip("/") == PLAN_BASE_URL,
        "provider_retry_limit": settings.max_retries,
        "models": rows,
        "k3_requested_identity_is_not_assumed_resolved_identity": True,
        "scientific_provider_calls": 0,
        "protocol_smoke_calls": len(rows),
        "benchmark_data_accessed": False,
        "authority": {
            "debate_completed": False,
            "f0_r4_frozen": False,
            "experiment": False,
            "gpu": False,
            "submission": False,
        },
        "private_credentials_included": False,
        "raw_response_ids_included": False,
    }
    atomic_json(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if status == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
