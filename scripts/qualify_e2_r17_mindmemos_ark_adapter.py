#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.ark_provider import ArkSettings
from research_pipeline.e2_r17_mindmemos_ark_adapter import (
    MindMemOSArkPlanChatAdapter,
    PLAN_BASE_URL,
    REQUESTED_MODEL,
    REQUIRED_RESOLVED_MODEL,
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


async def run_smoke() -> dict:
    raw = ArkSettings.from_env(required=True)
    adapter = MindMemOSArkPlanChatAdapter(settings=raw, max_parse_attempts=3)
    base = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-mindmemos-ark-plan-adapter-qualification",
        "scientific_outcome": False,
        "benchmark_data_accessed": False,
        "provider_request_is_protocol_smoke_only": True,
        "model_identity": {
            "requested": REQUESTED_MODEL,
            "required_resolved": REQUIRED_RESOLVED_MODEL,
            "route": raw.base_url,
        },
        "adapter_sha256": sha(ROOT / "research_pipeline/e2_r17_mindmemos_ark_adapter.py"),
        "scientific_authority": False,
        "submission_authority": False,
    }
    try:
        response = await adapter.chat(
            task="r17_adapter_protocol_smoke",
            messages=[
                {"role": "system", "content": "This is a transport protocol smoke test. Return exactly the token PLAN_OK."},
                {"role": "user", "content": "Return PLAN_OK and nothing else."},
            ],
            temperature=0,
            max_tokens=32,
        )
    except Exception as exc:
        text = str(exc)
        subscription = "InvalidSubscription" in text or "does not have a valid AgentPlan subscription" in text
        return {
            **base,
            "status": "HOLD_PROVIDER_SUBSCRIPTION" if subscription else "FAIL_PROVIDER_PROTOCOL",
            "provider_error_type": type(exc).__name__,
            "provider_error_class": "ARK_PLAN_SUBSCRIPTION" if subscription else "OTHER",
            "provider_error_message_sanitized": "Ark Plan subscription unavailable" if subscription else text[:500],
            "call_receipts": adapter.public_receipts(),
            "provider_retry_disabled": adapter.settings.max_retries == 0,
            "f1_execution_authorized": False,
        }
    receipts = adapter.public_receipts()
    checks = {
        "plan_route": raw.base_url.rstrip("/") == PLAN_BASE_URL,
        "one_generation_receipt": len(receipts) == 1,
        "requested_model": receipts[0]["requested_model"] == REQUESTED_MODEL if receipts else False,
        "resolved_model_exact": response.model == REQUIRED_RESOLVED_MODEL,
        "content_exact": response.content.strip() == "PLAN_OK",
        "response_id_not_public_raw": bool(receipts and len(receipts[0]["response_id_sha256"]) == 64),
        "provider_retry_disabled": adapter.settings.max_retries == 0,
    }
    return {
        **base,
        "status": "PASS" if all(checks.values()) else "FAIL",
        "model_identity": {**base["model_identity"], "observed_resolved": response.model},
        "checks": checks,
        "usage": response.usage.__dict__,
        "call_receipts": receipts,
        "f1_execution_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "generated/e2-r17-mindmemos-ark-adapter-qualification-20260825.json")
    args = parser.parse_args()
    payload = asyncio.run(run_smoke())
    atomic(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
