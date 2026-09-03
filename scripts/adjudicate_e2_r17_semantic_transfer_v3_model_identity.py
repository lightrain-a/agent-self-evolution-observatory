#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PLAN_BASE_URL = "https://ark.cn-beijing.volces.com/api/plan/v3"
REQUESTED_MODEL = "deepseek-v4-pro"
REQUIRED_RESOLVED_MODEL = "deepseek-v4-pro-ga-260813"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def build_identity(
    *,
    contract_path: Path,
    qualification_path: Path,
    created_at_utc: str | None = None,
) -> dict[str, Any]:
    contract = load(contract_path)
    qualification = load(qualification_path)

    require(contract.get("artifact_type") == "e2-r17-semantic-transfer-v3-stage-a-contract-r2", "wrong R2 contract type")
    require((contract.get("model_identity_policy") or {}).get("requested_model") == REQUESTED_MODEL, "contract requested model drift")
    require((contract.get("model_identity_policy") or {}).get("required_resolved_model") == REQUIRED_RESOLVED_MODEL, "contract resolved model drift")
    require((contract.get("model_identity_policy") or {}).get("thinking") == "disabled", "contract thinking policy drift")
    require((contract.get("model_identity_policy") or {}).get("provider_retry_limit") == 0, "contract provider retry policy drift")

    require(qualification.get("artifact_type") == "e2-r17-current-ark-plan-model-identity-qualification", "wrong qualification artifact type")
    require(qualification.get("status") == "PASS", "fresh qualification is not PASS")
    require(qualification.get("route") == PLAN_BASE_URL, "fresh qualification route drift")
    require(qualification.get("private_credentials_included") is False, "qualification credential-leakage flag")
    require(qualification.get("raw_response_ids_included") is False, "qualification raw response IDs are not allowed")

    rows = [row for row in (qualification.get("models") or []) if row.get("requested_model") == REQUESTED_MODEL]
    require(len(rows) == 1, "fresh qualification must contain exactly one DeepSeek V4-Pro row")
    row = rows[0]
    require(row.get("status") == "PASS", "fresh DeepSeek identity row is not PASS")
    require(row.get("resolved_model") == REQUIRED_RESOLVED_MODEL, "fresh DeepSeek exact resolved identity drift")
    require(row.get("thinking_requested") == "disabled", "fresh DeepSeek thinking mode drift")
    require(row.get("provider_retry_limit") == 0, "fresh DeepSeek provider retry limit drift")
    require(row.get("hidden_provider_retry_used") is False, "fresh DeepSeek hidden provider retry detected")
    require(row.get("scientific_outcome") is False, "identity qualification must not access scientific outcome")
    require(row.get("benchmark_data_accessed") is False, "identity qualification must not access benchmark data")
    require((row.get("checks") or {}).get("text_exact") is True, "identity qualification PLAN_OK text check failed")
    require((row.get("checks") or {}).get("resolved_model_present") is True, "identity qualification resolved model missing")
    require((row.get("checks") or {}).get("resolved_model_matches_requested_family") is True, "identity qualification family check failed")

    contract_created = datetime.fromisoformat(str(contract["created_at_utc"]))
    qualification_created = datetime.fromisoformat(str(qualification["created_at_utc"]))
    require(qualification_created > contract_created, "fresh identity qualification must occur after R2 contract freeze")

    timestamp = created_at_utc or datetime.now(timezone.utc).isoformat(timespec="seconds")
    adjudication_created = datetime.fromisoformat(timestamp)
    require(adjudication_created >= qualification_created, "identity adjudication timestamp precedes qualification")

    return {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-semantic-transfer-v3-fresh-model-identity-adjudication",
        "created_at_utc": timestamp,
        "status": "PASS_CURRENT_REVIEW_TRANCHE",
        "contract_path": str(contract_path.relative_to(ROOT) if contract_path.is_relative_to(ROOT) else contract_path),
        "contract_sha256": sha256(contract_path),
        "qualification_path": str(qualification_path.relative_to(ROOT) if qualification_path.is_relative_to(ROOT) else qualification_path),
        "qualification_sha256": sha256(qualification_path),
        "route": PLAN_BASE_URL,
        "requested_and_resolved": {
            REQUESTED_MODEL: {
                "requested": REQUESTED_MODEL,
                "resolved": REQUIRED_RESOLVED_MODEL,
                "thinking": "disabled",
                "provider_retry_limit": 0,
                "qualification_scientific_outcome": False,
                "qualification_benchmark_data_accessed": False,
                "source_qualification_sha256": sha256(qualification_path),
            }
        },
        "checks": {
            "qualification_after_contract_freeze": True,
            "qualification_pass": True,
            "exact_resolved_identity": True,
            "thinking_disabled": True,
            "provider_retry_zero": True,
            "hidden_provider_retry_unused": True,
            "scientific_outcome_unread": True,
            "benchmark_data_unread": True,
            "single_deepseek_identity_call_only": True,
        },
        "authority": {
            "preexecution_identity_evidence": True,
            "mint_stage_a_authorization": False,
            "stage_a_provider_execution": False,
            "stage_b_learning_execution": False,
            "paper_promotion": False,
        },
        "scientific_execution": False,
        "private_credentials_included": False,
        "raw_response_ids_included": False,
        "note": "This artifact normalizes one fresh DeepSeek-only Ark Plan identity qualification into the exact schema consumed by the frozen V3 Stage-A authorizer. It grants no provider authority by itself.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--qualification", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build_identity(contract_path=args.contract, qualification_path=args.qualification)
    atomic_json(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
