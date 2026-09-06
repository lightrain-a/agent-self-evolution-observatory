#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_bridge_v4r2_stage_a_capability import (
    CONTROL_PLANE_REVISION,
    PRODUCTION_PUBLIC_KEY_SHA256,
)

CONTRACT_STATUS = "FROZEN_E2_R17_BRIDGE_V4R2_STAGE_A_SCREEN_SEARCH_SUPPORT"
PREFLIGHT_STATUS = "PASS_ZERO_PROVIDER_BRIDGE_V4R2_STAGE_A_CONTRACT_PREFLIGHT"
REVIEW_VERDICT = "PASS_TO_SEPARATE_BRIDGE_V4R2_STAGE_A_AUTHORIZATION"
AUTH_STATUS = "AUTHORIZED_E2_R17_BRIDGE_V4R2_STAGE_A_STRUCTURAL_REQUIRES_SIGNED_CAPABILITY"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def atomic_exclusive(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        os.write(fd, raw)
        os.fsync(fd)
    finally:
        os.close(fd)


def build_authorization(
    *,
    contract_path: Path,
    preflight_path: Path,
    review_path: Path,
) -> dict[str, Any]:
    contract = load_json(contract_path)
    preflight = load_json(preflight_path)
    review = load_json(review_path)
    contract_sha = sha256_file(contract_path)
    preflight_sha = sha256_file(preflight_path)
    review_sha = sha256_file(review_path)

    require(contract.get("status") == CONTRACT_STATUS, "Bridge Stage-A contract status drift")
    require(not any((contract.get("authority") or {}).values()), "Bridge Stage-A contract must remain zero-authority")
    require(preflight.get("status") == PREFLIGHT_STATUS, "Bridge Stage-A preflight status drift")
    require(preflight.get("contract_sha256") == contract_sha, "Bridge Stage-A preflight/contract SHA drift")
    require(preflight.get("provider_calls") == 0 and preflight.get("provider_claims") == 0, "Bridge Stage-A preflight touched provider")
    require(preflight.get("scientific_outcomes_read") is False and preflight.get("method_effect_read") is False, "Bridge Stage-A preflight outcome boundary drift")
    require(preflight.get("updater_calls") == 0 and preflight.get("heldout_actor_calls") == 0, "Bridge Stage-A preflight stage separation drift")

    require(review.get("status") == "COMPLETED", "Bridge Stage-A independent review receipt incomplete")
    require(review.get("surface") == "ChatGPT web", "Bridge Stage-A independent review surface drift")
    require(review.get("model") == "GPT-6 Pro", "Bridge Stage-A independent review model drift")
    require(review.get("verdict") == REVIEW_VERDICT, "Bridge Stage-A independent review did not PASS")
    require(review.get("control_plane_revision") == CONTROL_PLANE_REVISION, "Bridge Stage-A independent review control-plane revision drift")
    require(review.get("contract_sha256_acknowledged") == contract_sha, "Bridge Stage-A review contract acknowledgement drift")
    require(review.get("preflight_sha256_acknowledged") == preflight_sha, "Bridge Stage-A review preflight acknowledgement drift")
    require(review.get("scientific_authority_now") is False, "Bridge Stage-A review improperly grants authority directly")
    require(review.get("stage_a_execution_recommendation") == "ALLOW_SEPARATE_AUTHORIZATION", "Bridge Stage-A review recommendation drift")
    require(list(review.get("remaining_blockers") or []) == [], "Bridge Stage-A review retains blockers")
    for key in (
        "scientific_geometry",
        "stage_separation",
        "support_gate",
        "identity_runtime_budget",
        "exactly_once_fail_closed",
        "causal_integrity",
        "m3r4_dependency",
        "r1_supersession_clean",
        "r2_supersession_clean",
        "authority_provenance",
    ):
        require(review.get(key) == "PASS", f"Bridge Stage-A review field not PASS: {key}")

    run_root = Path(contract["run_root"])
    lease_path = Path(contract["lineage_lease_path"])
    consumption_path = Path(contract["signed_capability_control"]["consumption_marker_path"])
    require(not run_root.exists() and not lease_path.exists(), "Bridge Stage-A run root/lease no longer fresh")
    require(not consumption_path.exists(), "Bridge Stage-A capability already consumed")
    require(contract["signed_capability_control"]["production_public_key_sha256"] == PRODUCTION_PUBLIC_KEY_SHA256, "Bridge Stage-A contract trust-root drift")

    expected_authority = {
        "scientific_experiment": True,
        "provider_io": True,
        "search_pool_acquisition": True,
        "support_inspection": True,
        "free_updater": False,
        "deterministic_state_materialization": False,
        "actor_evaluation": False,
        "screen_outcome_opening": False,
        "validation_opening": False,
        "analysis": False,
        "paper_promotion": False,
    }
    scope = {
        "contract_sha256": contract_sha,
        "allowed_unit_ids": contract["search"]["unit_ids"],
        "allowed_task_ids": contract["search"]["task_ids"],
        "exact_k": 8,
        "required_resolved_model": contract["actor"]["required_resolved_model"],
        "identity_artifact_sha256": contract["model_identity"]["sha256"],
        "required_skill_pre_sha256": contract["initial_skill"]["sha256"],
        "max_turns": contract["actor"]["max_turns"],
        "max_output_tokens": contract["actor"]["max_output_tokens"],
        "automatic_retry": False,
        "run_root": contract["run_root"],
        "lineage_lease_path": contract["lineage_lease_path"],
        "consumption_marker_path": str(consumption_path),
        "provider_budget": {
            "required": True,
            "total_limit": contract["budget"]["search_provider_call_ceiling"],
            "per_unit_limit": contract["budget"]["per_search_unit_call_ceiling"],
        },
    }
    return {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-bridge-v4r2-stage-a-structural-authorization",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": AUTH_STATUS,
        "single_use": True,
        "control_plane_revision": CONTROL_PLANE_REVISION,
        "contract_path": str(contract_path.resolve()),
        "contract_sha256": contract_sha,
        "preflight_path": str(preflight_path.resolve()),
        "preflight_sha256": preflight_sha,
        "independent_review": {
            "path": str(review_path.resolve()),
            "sha256": review_sha,
            "verdict": REVIEW_VERDICT,
        },
        "authority_requires_external_signed_capability": True,
        "production_public_key_sha256": PRODUCTION_PUBLIC_KEY_SHA256,
        "authority": expected_authority,
        "execution_scope": scope,
        "interpretation_boundary": "This structural authorization is not sufficient authority by itself. Actual Stage-A provider execution additionally requires an externally Ed25519-signed single-use capability from the hard-pinned host52 controller trust root, verified and consumed at runner point of use before provider I/O.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--preflight", type=Path, required=True)
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), "Bridge Stage-A structural authorization already exists")
    payload = build_authorization(contract_path=args.contract, preflight_path=args.preflight, review_path=args.review)
    atomic_exclusive(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
