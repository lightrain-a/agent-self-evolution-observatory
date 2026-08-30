from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from research_pipeline.ark_provider import ArkResponsesClient, ArkSettings, extract_json_object
from research_pipeline.config import load_env_file

RUN = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-p0-20260830-pilot-v1")
ENV = Path("/home/wyt/code/agent-self-evolution-observatory/.env")
MODEL = "doubao-seed-2.0-mini"
RESOLVED = "doubao-seed-2-0-mini-260215"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def shat(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def validate_schema(text: str):
    payload = extract_json_object(text)
    require(isinstance(payload, dict), "probe output is not an object")
    action = payload.get("action")
    require(isinstance(action, list) and len(action) == 1, "probe action must contain one item")
    require(isinstance(action[0], dict) and len(action[0]) == 1, "probe action object invalid")
    require(isinstance(payload.get("next_goal"), str), "probe next_goal missing")
    return payload


def main() -> int:
    contract = json.loads((RUN / "contract.json").read_text(encoding="utf-8"))
    require(contract["status"] == "FROZEN_BEFORE_PROVIDER_SUPPORT_AND_SCIENTIFIC_CALLS", "contract is not frozen")
    prompt = """This is a non-scientific provider support probe. Do not use experimental data.
Return exactly one JSON object and no prose using this schema:
{
  "action": [
    {
      "click_element": {
        "index": 1
      }
    }
  ],
  "next_goal": "Open the example item"
}
The toy state contains a visible example item at index 1. Select it."""
    artifact = {
        "schema_version": "1.0",
        "artifact_kind": "C1_PACTA_NON_SCIENTIFIC_SUPPORT_PROBE",
        "status": "STOP_SUPPORT",
        "requested_model": MODEL,
        "expected_resolved_model": RESOLVED,
        "thinking": "disabled",
        "temperature": 0.0,
        "retries": 0,
        "substitution": False,
        "prompt_sha256": shat(prompt),
        "scientific_data_used": False,
        "completed_at": now(),
    }
    try:
        load_env_file(ENV)
        raw = ArkSettings.from_env()
        settings = ArkSettings(api_key=raw.api_key, base_url=raw.base_url, default_model=raw.default_model, timeout_seconds=180, max_retries=0)
        client = ArkResponsesClient(settings)
        response = client.respond(
            prompt,
            model=MODEL,
            max_output_tokens=160,
            temperature=0.0,
            thinking="disabled",
            store=True,
            allow_thinking_compatibility_fallback=False,
        )
        text = str(response.get("text") or "")
        payload = validate_schema(text)
        require(response.get("requested_model") == MODEL, "requested model drift")
        require(response.get("resolved_model") == RESOLVED, "resolved model drift")
        require(response.get("thinking_compatibility_fallback") is False, "thinking fallback occurred")
        artifact.update({
            "status": "SUPPORT_PASS",
            "resolved_model": response.get("resolved_model"),
            "response_id": response.get("response_id"),
            "provider_status": response.get("status"),
            "raw_text": text,
            "raw_text_sha256": shat(text),
            "parsed": payload,
            "usage": response.get("usage") or {},
            "provider_summary": settings.safe_summary(),
        })
    except Exception as exc:
        artifact.update({"failure_type": type(exc).__name__, "failure": str(exc)[:2000]})
    dump(RUN / "model-support.json", artifact)
    print(json.dumps({"status": artifact["status"], "requested": MODEL, "resolved": artifact.get("resolved_model"), "failure": artifact.get("failure")}))
    return 0 if artifact["status"] == "SUPPORT_PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
