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

import scripts.run_e2_r17_v31_provider_runtime_pilot_review as review_harness
import scripts.run_e2_r17_v3_1_review as base

DRAFT = ROOT / "generated/e2-r17-v31-provider-runtime-pilot-draft-contract-20260828.json"
SOURCE_ROOT = ROOT / "generated/e2-r17-v31-provider-runtime-pilot-review-20260828"
DEFAULT_OUTPUT = ROOT / "generated/e2-r17-v31-provider-runtime-pilot-review-reparsed-20260829.json"
MODELS = ("deepseek-v4-pro", "kimi-k3")


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    draft_sha = sha_file(DRAFT)
    rows: dict[str, Any] = {}
    all_valid = True
    for model in MODELS:
        path = SOURCE_ROOT / f"{model}.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        review = payload.get("review") or {}
        missing = base.validate_review_schema(review, draft_sha)
        resolved_ok = bool(payload.get("resolved_model_matches_qualification"))
        pass_semantics = (
            review.get("verdict") == "PASS_TO_SEPARATELY_AUTHORIZED_PROVIDER_RUNTIME_PILOT"
            and review.get("provider_runtime_pilot_recommendation")
            == "ALLOW_SEPARATE_FROZEN_PROVIDER_RUNTIME_PILOT_AUTHORIZATION"
            and review.get("e1_b_recommendation") == "HOLD"
            and review.get("paper_claim_authority") is False
            and not review.get("remaining_blockers")
        )
        valid = not missing and resolved_ok and pass_semantics
        all_valid = all_valid and valid
        rows[model] = {
            "source_path": str(path.relative_to(ROOT)),
            "source_sha256": sha_file(path),
            "original_status": payload.get("status"),
            "original_missing_required_fields": payload.get("missing_required_fields") or [],
            "raw_text_sha256": payload.get("raw_text_sha256"),
            "resolved_model": payload.get("resolved_model"),
            "resolved_model_matches_qualification": resolved_ok,
            "reparsed_missing_required_fields": missing,
            "verdict": review.get("verdict"),
            "provider_runtime_pilot_recommendation": review.get("provider_runtime_pilot_recommendation"),
            "e1_b_recommendation": review.get("e1_b_recommendation"),
            "paper_claim_authority": review.get("paper_claim_authority"),
            "remaining_blockers": review.get("remaining_blockers") or [],
            "single_sentence_verdict": review.get("single_sentence_verdict"),
            "valid_after_harness_repair": valid,
        }

    result = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-v31-provider-runtime-pilot-review-reparse-adjudication",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "PASS_REPARSED_EXISTING_REVIEWS" if all_valid else "HOLD_REPARSE",
        "draft_contract_path": str(DRAFT.relative_to(ROOT)),
        "draft_contract_sha256": draft_sha,
        "review_harness_path": "scripts/run_e2_r17_v3_1_review.py",
        "review_harness_sha256": sha_file(ROOT / "scripts/run_e2_r17_v3_1_review.py"),
        "provider_review_harness_path": "scripts/run_e2_r17_v31_provider_runtime_pilot_review.py",
        "provider_review_harness_sha256": sha_file(ROOT / "scripts/run_e2_r17_v31_provider_runtime_pilot_review.py"),
        "provider_generation_calls": 0,
        "reused_exact_model_outputs": True,
        "original_fail_schema_preserved": True,
        "failure_classification": "IMPLEMENTATION/REVIEW_HARNESS_SCHEMA_VALIDATION",
        "scientific_belief_update": "NONE; the original model content was valid and the failure was local schema validation only.",
        "rows": rows,
        "authority": {
            "prepare_provider_runtime_pilot_authorization": all_valid,
            "execute_e1_b": False,
            "paper_promotion": False,
            "submission": False,
        },
    }
    atomic_json(args.output, result)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if all_valid else 2


if __name__ == "__main__":
    raise SystemExit(main())
