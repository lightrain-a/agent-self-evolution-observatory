from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from research_pipeline.ark_provider import ArkResponseStateError, ArkResponsesClient, ArkSettings
from research_pipeline.config import load_env_file

AUTH = HERE / "c1-tgrp-pilot-human-authorization-20260829.json"
OUTPUT = HERE / "c1-tgrp-provider-support-requalification-20260829.json"
CANONICAL_ENV = Path("/home/wyt/code/agent-self-evolution-observatory/.env")

MODEL = "doubao-seed-2.0-mini"
EXPECTED_RESOLVED = "doubao-seed-2-0-mini-260215"
PROMPT = (
    "This is a non-scientific service-availability probe. "
    "Return a short plain-text acknowledgement. Do not use tools and do not discuss any task data."
)


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def main() -> int:
    auth = json.loads(AUTH.read_text(encoding="utf-8"))
    if not auth["authorized"]["one_current_provider_model_support_requalification"]:
        raise RuntimeError("support requalification not authorized")
    if auth["frozen_model"]["requested"] != MODEL or auth["frozen_model"]["expected_resolved"] != EXPECTED_RESOLVED:
        raise RuntimeError("authorization model drift")

    if not CANONICAL_ENV.is_file():
        raise RuntimeError("frozen canonical provider env path is unavailable")
    load_env_file(CANONICAL_ENV)
    raw = ArkSettings.from_env()
    settings = ArkSettings(
        api_key=raw.api_key,
        base_url=raw.base_url,
        default_model=raw.default_model,
        timeout_seconds=180.0,
        max_retries=0,
    )
    client = ArkResponsesClient(settings)
    base = {
        "schema_version": "1.0",
        "artifact_kind": "C1_TGRP_PROVIDER_SUPPORT_REQUALIFICATION",
        "paper_id": auth["paper_id"],
        "experiment_id": auth["experiment_id"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "execution_base": auth["execution_base"],
        "experiment_branch": auth["experiment_branch"],
        "probe_is_scientific_task": False,
        "probe_prompt_sha256": sha_text(PROMPT),
        "requested_model": MODEL,
        "expected_resolved_model": EXPECTED_RESOLVED,
        "temperature": 0.0,
        "max_output_tokens": 64,
        "thinking": "disabled",
        "provider_retries": 0,
        "substitution_allowed": False,
        "provider": settings.safe_summary(),
        "authority_ref": AUTH.name,
    }

    post_attempted = False
    try:
        post_attempted = True
        response = client.respond(
            PROMPT,
            model=MODEL,
            max_output_tokens=64,
            temperature=0.0,
            thinking="disabled",
            store=True,
            allow_thinking_compatibility_fallback=False,
        )
        resolved = str(response.get("resolved_model") or "")
        fallback = bool(response.get("thinking_compatibility_fallback"))
        text = str(response.get("text") or "")
        checks = {
            "provider_configured": bool(settings.api_key),
            "response_object_returned": True,
            "assistant_text_present": bool(text.strip()),
            "requested_model_exact": str(response.get("requested_model") or "") == MODEL,
            "resolved_model_exact": resolved == EXPECTED_RESOLVED,
            "thinking_fallback_absent": not fallback,
            "status_present": bool(str(response.get("status") or "").strip()),
        }
        passed = all(checks.values())
        payload = {
            **base,
            "status": "SUPPORT_PASS" if passed else "SUPPORT_HOLD_RESPONSE_OR_MODEL_DRIFT",
            "provider_post_attempted": post_attempted,
            "provider_posts": 1,
            "checks": checks,
            "response": {
                "response_id": response.get("response_id"),
                "status": response.get("status"),
                "requested_model": response.get("requested_model"),
                "resolved_model": resolved,
                "thinking_requested": response.get("thinking_requested"),
                "thinking_effective": response.get("thinking_effective"),
                "thinking_compatibility_fallback": fallback,
                "text_sha256": sha_text(text) if text else "",
                "text_chars": len(text),
                "usage": response.get("usage") or {},
            },
            "scientific_outcomes": 0,
            "next_gate": "Pilot execution allowed only if status=SUPPORT_PASS; confirmatory full remains locked.",
        }
    except ArkResponseStateError as error:
        payload = {
            **base,
            "status": "SUPPORT_HOLD_PROVIDER_RESPONSE_STATE",
            "provider_post_attempted": post_attempted,
            "provider_posts": 1 if post_attempted else 0,
            "failure": error.receipt(),
            "scientific_outcomes": 0,
            "next_gate": "STOP_SUPPORT; do not substitute model/provider or execute pilot.",
        }
    except Exception as error:
        payload = {
            **base,
            "status": "SUPPORT_HOLD_RUNTIME_OR_PROVIDER",
            "provider_post_attempted": post_attempted,
            "provider_posts": 1 if post_attempted else 0,
            "failure": {"type": type(error).__name__, "message": str(error)[:1600]},
            "scientific_outcomes": 0,
            "next_gate": "STOP_SUPPORT; diagnose without substituting model/provider or executing pilot.",
        }

    write_json(OUTPUT, payload)
    print(json.dumps({
        "status": payload["status"],
        "provider_posts": payload.get("provider_posts", 0),
        "resolved_model": (payload.get("response") or {}).get("resolved_model"),
        "scientific_outcomes": 0,
    }, ensure_ascii=False))
    return 0 if payload["status"] == "SUPPORT_PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
