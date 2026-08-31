from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from c1_pacta_v21_first_action_parser import parse_first_action


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_dump(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def journal_provider_response(
    path: Path,
    request_fields: dict[str, Any],
    response: dict[str, Any],
    raw_response: str,
) -> dict[str, Any]:
    row = {key: value for key, value in request_fields.items() if key != "prompt"}
    row.update({
        "schema_version": "1.0",
        "status": "provider_response_persisted_unparsed",
        "response_id": response.get("response_id"),
        "provider_status": response.get("status"),
        "requested_model": response.get("requested_model"),
        "resolved_model": response.get("resolved_model"),
        "thinking_compatibility_fallback": response.get("thinking_compatibility_fallback"),
        "usage": response.get("usage") or {},
        "raw_response": raw_response,
        "raw_response_sha256": sha256_text(raw_response),
        "prompt_sha256": request_fields["prompt_sha256"],
        "provider_returned_at": now(),
    })
    atomic_dump(path, row)
    return row


def parse_journaled_response(path: Path) -> dict[str, Any]:
    row = load(path)
    if row.get("status") != "provider_response_persisted_unparsed":
        raise RuntimeError("response must be journaled exactly once before parsing")
    try:
        parsed = parse_first_action(row["raw_response"])
        row.update({
            "status": "complete",
            "action_signature": parsed.signature,
            "parsed_action": parsed.action_object,
            "canonical_action": parsed.canonical_action,
            "parser_mode": parsed.mode,
            "parsed_at": now(),
        })
    except Exception as exc:
        row.update({
            "status": "failed_first_action_parser",
            "failure_type": type(exc).__name__,
            "failure": str(exc)[:2000],
            "parsed_at": now(),
        })
    atomic_dump(path, row)
    return row
