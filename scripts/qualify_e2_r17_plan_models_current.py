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
REQUESTED_MODELS = ("deepseek-v4-pro", "kimi-k3")


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def sanitize_error(message: str) -> str:
    text = re.sub(r"resp_[A-Za-z0-9_]+", "resp_[REDACTED]", str(message))
    text = re.sub(r"Request id:\s*[A-Za-z0-9_]+", "Request id: [REDACTED]", text)
    return text[:1000]


def family_match(requested: str, resolved: str) -> bool:
    if requested == "deepseek-v4-pro":
        return resolved == requested or resolved.startswith("deepseek-v4-pro-")
    if requested == "kimi-k3":
        return resolved == requested or resolved.startswith("kimi-k3-")
    return False


def call_once(
    client: ArkResponsesClient,
    requested_model: str,
    *,
    max_output_tokens: int,
    thinking: str | None,
) -> dict[str, Any]:
    prompt = (
        "This is a zero-authority Ark Plan route and model-identity qualification. "
        "Return exactly PLAN_OK and nothing else."
    )
    row: dict[str, Any] = {
        "requested_model": requested_model,
        "prompt_sha256": sha_text(prompt),
        "provider_generation_attempts": 1,
        "max_output_tokens": max_output_tokens,
        "thinking_requested": thinking,
        "provider_retry_limit": client.settings.max_retries,
        "hidden_provider_retry_used": False,
        "scientific_outcome": False,
        "benchmark_data_accessed": False,
    }
    try:
        try:
            result = client.respond(
                prompt,
                model=requested_model,
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
                "response_id_sha256": sha_text(str(state.get("response_id") or "")),
            }
            if state.get("status") == "incomplete" and state.get("incomplete_reason") == "length":
                row.update(
                    {
                        "status": "HOLD_OUTPUT_BUDGET",
                        "resolved_model": state.get("resolved_model"),
                        "diagnosis": "qualification output budget exhausted before PLAN_OK; no GET recovery attempted",
                    }
                )
                return row
            if not exc.response_id:
                raise
            polled = client.poll_response(exc.response_id, max_polls=4, interval_seconds=1.0)
            if not polled.get("text"):
                return {
                    **row,
                    "status": "HOLD_PROVIDER_RESPONSE_STATE",
                    "polled_status": polled.get("status"),
                    "poll_count": polled.get("poll_count"),
                }
            result = {
                "requested_model": requested_model,
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
            "resolved_model_matches_requested_family": family_match(requested_model, resolved),
        }
        row.update(
            {
                "status": "PASS" if all(checks.values()) else "FAIL",
                "resolved_model": resolved,
                "checks": checks,
                "usage": result.get("usage") or {},
                "provider_status": result.get("status"),
                "response_id_sha256": sha_text(str(result.get("response_id") or "")),
                "raw_text": text,
                "raw_text_sha256": sha_text(text),
                "get_poll_recovery": bool(result.get("get_poll_recovery", False)),
                "poll_count": result.get("poll_count", 0),
            }
        )
    except Exception as exc:  # noqa: BLE001 - receipt must survive provider failures
        message = str(exc)
        subscription = "InvalidSubscription" in message or "valid AgentPlan subscription" in message
        row.update(
            {
                "status": "HOLD_PROVIDER_SUBSCRIPTION" if subscription else "FAIL_PROVIDER_PROTOCOL",
                "error_type": type(exc).__name__,
                "error_message_sanitized": "Ark Plan subscription unavailable" if subscription else sanitize_error(message),
                "error_sha256": sha_text(message),
            }
        )
    return row


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--models", nargs="+", choices=REQUESTED_MODELS, default=list(REQUESTED_MODELS))
    parser.add_argument("--max-output-tokens", type=int, default=256)
    parser.add_argument("--compatibility-parent", type=Path)
    parser.add_argument("--thinking", choices=("disabled", "enabled", "none"), default="disabled")
    args = parser.parse_args()

    load_env_file(args.env_file)
    source = ArkSettings.from_env(required=True)
    if source.base_url.rstrip("/") != PLAN_BASE_URL:
        raise RuntimeError("E2-R17 qualification refuses any non-Ark-Plan route")
    settings = ArkSettings(
        api_key=source.api_key,
        base_url=source.base_url,
        default_model=source.default_model,
        timeout_seconds=300.0,
        max_retries=0,
    )
    client = ArkResponsesClient(settings)
    thinking = None if args.thinking == "none" else args.thinking
    rows = [
        call_once(client, model, max_output_tokens=args.max_output_tokens, thinking=thinking)
        for model in args.models
    ]
    resolved = [str(row.get("resolved_model") or "") for row in rows]
    checks = {
        "all_protocol_calls_pass": all(row.get("status") == "PASS" for row in rows),
        "resolved_identities_distinct": len(set(resolved)) == len(resolved) and all(resolved),
        "route_is_ark_plan": source.base_url.rstrip("/") == PLAN_BASE_URL,
        "provider_retry_zero": settings.max_retries == 0,
    }
    status = "PASS" if all(checks.values()) else (
        "HOLD_PROVIDER_SUBSCRIPTION"
        if any(row.get("status") == "HOLD_PROVIDER_SUBSCRIPTION" for row in rows)
        else "HOLD_OR_FAIL"
    )
    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-current-ark-plan-model-identity-qualification",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": status,
        "route": source.base_url,
        "default_model": source.default_model,
        "models": rows,
        "checks": checks,
        "compatibility_parent": (
            {
                "path": str(args.compatibility_parent.relative_to(ROOT) if args.compatibility_parent.is_relative_to(ROOT) else args.compatibility_parent),
                "sha256": hashlib.sha256(args.compatibility_parent.read_bytes()).hexdigest(),
                "separate_generation_calls_declared": True,
            }
            if args.compatibility_parent is not None
            else None
        ),
        "release_drift_policy": (
            "Observed resolved identities are frozen for this review tranche. Historical exact suffixes are not reused as authority. "
            "Any later execution tranche must requalify and bind its own observed identities."
        ),
        "authority": {
            "preexecution_consultation": status == "PASS",
            "scientific_experiment": False,
            "gpu": False,
            "paper_promotion": False,
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
