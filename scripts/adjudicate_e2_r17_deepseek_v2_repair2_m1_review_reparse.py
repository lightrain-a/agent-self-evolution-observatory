#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.run_e2_r17_deepseek_v2_repair2_m1_review as m1_review

CONTRACT = ROOT / "generated/e2-r17-deepseek-v2-repair2-m1-measurement-contract-v2-20260831.json"
PREFLIGHT = ROOT / "generated/e2-r17-deepseek-v2-repair2-m1-actual-actor-path-preflight-v2-20260831.json"
SOURCE_ROOT = ROOT / "generated/e2-r17-deepseek-v2-repair2-m1-review-20260831"
DEFAULT_OUTPUT = ROOT / "generated/e2-r17-deepseek-v2-repair2-m1-review-reparse-adjudication-20260831.json"
MODELS = ("deepseek-v4-pro", "kimi-k3")


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def sha_text(text: str) -> str:
    return sha_bytes(text.encode("utf-8"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    tmp.replace(path)


def validate_review(review: dict[str, Any], contract_sha: str, preflight_sha: str) -> list[str]:
    missing = [field for field in m1_review.schema() if field not in review]
    if review.get("contract_sha256_acknowledged") != contract_sha:
        missing.append("contract_sha256_acknowledged_exact")
    if review.get("preflight_sha256_acknowledged") != preflight_sha:
        missing.append("preflight_sha256_acknowledged_exact")
    if review.get("paper_claim_authority") is not False:
        missing.append("paper_claim_authority_false")
    return sorted(set(missing))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    contract_sha = sha_file(CONTRACT)
    preflight_sha = sha_file(PREFLIGHT)
    rows: dict[str, Any] = {}
    all_valid = True

    for model in MODELS:
        path = SOURCE_ROOT / f"{model}.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        review = payload.get("review") or {}
        missing = validate_review(review, contract_sha, preflight_sha)
        raw_text = str(payload.get("raw_text") or "")
        provider_integrity = (
            payload.get("provider_status") == "completed"
            and payload.get("provider_generation_attempts") == 1
            and payload.get("provider_retry_limit") == 0
            and payload.get("hidden_provider_retry_used") is False
            and payload.get("get_poll_recovery") is False
            and payload.get("raw_text_sha256") == sha_text(raw_text)
        )
        identity_ok = bool(payload.get("resolved_model_matches_qualification"))
        pass_semantics = (
            review.get("verdict") == "PASS_TO_SINGLE_USE_M1_AUTHORIZATION"
            and review.get("execution_recommendation") == "ALLOW_SINGLE_USE_M1_AUTHORIZATION"
            and review.get("paper_claim_authority") is False
            and not review.get("remaining_blockers")
        )
        valid = not missing and provider_integrity and identity_ok and pass_semantics
        all_valid = all_valid and valid
        rows[model] = {
            "source_path": str(path.relative_to(ROOT)),
            "source_sha256": sha_file(path),
            "original_status": payload.get("status"),
            "original_parse_valid": payload.get("parse_valid"),
            "original_missing_required_fields": payload.get("missing_required_fields") or [],
            "raw_text_sha256": payload.get("raw_text_sha256"),
            "provider_integrity": provider_integrity,
            "resolved_model": payload.get("resolved_model"),
            "resolved_model_matches_qualification": identity_ok,
            "reparsed_missing_required_fields": missing,
            "contract_sha256_acknowledged": review.get("contract_sha256_acknowledged"),
            "preflight_sha256_acknowledged": review.get("preflight_sha256_acknowledged"),
            "verdict": review.get("verdict"),
            "execution_recommendation": review.get("execution_recommendation"),
            "paper_claim_authority": review.get("paper_claim_authority"),
            "remaining_blockers": review.get("remaining_blockers") or [],
            "single_sentence_verdict": review.get("single_sentence_verdict"),
            "valid_after_local_schema_repair": valid,
        }

    result = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-deepseek-v2-repair2-m1-review-reparse-adjudication",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "PASS_REPARSED_EXISTING_M1_REVIEWS_2_OF_2" if all_valid else "HOLD_M1_REPARSE",
        "contract_path": str(CONTRACT.relative_to(ROOT)),
        "contract_sha256": contract_sha,
        "actual_actor_path_preflight_path": str(PREFLIGHT.relative_to(ROOT)),
        "actual_actor_path_preflight_sha256": preflight_sha,
        "source_review_root": str(SOURCE_ROOT.relative_to(ROOT)),
        "provider_generation_calls": 0,
        "provider_claims": 0,
        "reused_exact_model_outputs": True,
        "original_fail_schema_artifacts_preserved": True,
        "failure_classification": "IMPLEMENTATION/REUSED_BASE_REVIEW_SCHEMA_SHA_BINDING",
        "failure_detail": (
            "The reused V3.1 helper compared every *_sha256_acknowledged field to the "
            "contract SHA. M1 correctly has distinct contract and preflight SHA fields."
        ),
        "scientific_belief_update": "NONE",
        "partial_effect_read": False,
        "rows": rows,
        "authority": {
            "prepare_single_use_m1_authorization": all_valid,
            "execute_m1_measurement": False,
            "execute_updater": False,
            "run_analyzer": False,
            "prepare_v3": False,
            "paper_promotion": False,
            "submission": False,
        },
    }
    atomic_json(args.output, result)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if all_valid else 2


if __name__ == "__main__":
    raise SystemExit(main())
