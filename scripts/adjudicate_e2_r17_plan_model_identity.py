#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PLAN_BASE_URL = "https://ark.cn-beijing.volces.com/api/plan/v3"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def select_pass(payloads: list[tuple[Path, dict[str, Any]]], requested: str) -> tuple[Path, dict[str, Any]]:
    matches: list[tuple[Path, dict[str, Any]]] = []
    for path, payload in payloads:
        for row in payload.get("models") or []:
            if row.get("requested_model") == requested and row.get("status") == "PASS":
                matches.append((path, row))
    if not matches:
        raise RuntimeError(f"no passing qualification for {requested}")
    return matches[-1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qualification", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    loaded = [(path, json.loads(path.read_text(encoding="utf-8"))) for path in args.qualification]
    for path, payload in loaded:
        if payload.get("route") != PLAN_BASE_URL:
            raise RuntimeError(f"non-Plan qualification forbidden: {path}")
        if payload.get("private_credentials_included"):
            raise RuntimeError(f"credential leakage flag in {path}")
    deep_path, deep = select_pass(loaded, "deepseek-v4-pro")
    kimi_path, kimi = select_pass(loaded, "kimi-k3")
    resolved = {deep["resolved_model"], kimi["resolved_model"]}
    checks = {
        "deepseek_pass": deep.get("status") == "PASS",
        "kimi_pass": kimi.get("status") == "PASS",
        "resolved_identities_distinct": len(resolved) == 2,
        "provider_retry_zero": deep.get("provider_retry_limit") == 0 and kimi.get("provider_retry_limit") == 0,
        "no_hidden_provider_retry": not deep.get("hidden_provider_retry_used") and not kimi.get("hidden_provider_retry_used"),
        "route_is_ark_plan": True,
    }
    status = "PASS_CURRENT_REVIEW_TRANCHE" if all(checks.values()) else "HOLD"
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-current-plan-model-identity-adjudication",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": status,
        "route": PLAN_BASE_URL,
        "requested_and_resolved": {
            "deepseek-v4-pro": {
                "requested": "deepseek-v4-pro",
                "resolved": deep["resolved_model"],
                "source_artifact": str(deep_path),
                "source_artifact_sha256": sha256(deep_path),
                "thinking_requested": deep.get("thinking_requested"),
            },
            "kimi-k3": {
                "requested": "kimi-k3",
                "resolved": kimi["resolved_model"],
                "source_artifact": str(kimi_path),
                "source_artifact_sha256": sha256(kimi_path),
                "thinking_requested": kimi.get("thinking_requested"),
            },
        },
        "checks": checks,
        "compatibility_history": [
            {
                "path": str(path),
                "sha256": sha256(path),
                "status": item.get("status"),
            }
            for path, item in loaded
        ],
        "adjudication": (
            "The initial Kimi Auto/default-thinking smokes are retained as explicit incomplete-length protocol failures. "
            "The passing Kimi qualification is a separately declared compatibility call with thinking disabled. "
            "DeepSeek resolves to the current GA release rather than the historical 260425 suffix. These observed identities "
            "are frozen only for the current pre-execution review tranche and must be requalified before any later scientific tranche."
        ),
        "authority": {
            "preexecution_consultation": status == "PASS_CURRENT_REVIEW_TRANCHE",
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
    return 0 if status == "PASS_CURRENT_REVIEW_TRANCHE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
