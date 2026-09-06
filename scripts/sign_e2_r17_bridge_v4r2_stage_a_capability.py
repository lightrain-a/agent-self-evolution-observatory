#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_bridge_v4r2_stage_a_capability import (
    CONTROL_PLANE_REVISION,
    PRODUCTION_PUBLIC_KEY_PATH,
    PRODUCTION_PUBLIC_KEY_SHA256,
    sha256_file,
    sign_document,
)
from scripts.authorize_e2_r17_bridge_v4r2_stage_a import AUTH_STATUS, REVIEW_VERDICT


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


def build_payload(
    *,
    contract_path: Path,
    preflight_path: Path,
    review_path: Path,
    authorization_path: Path,
    issued_at_utc: str | None = None,
    capability_id: str | None = None,
) -> dict[str, Any]:
    contract = load_json(contract_path)
    preflight = load_json(preflight_path)
    review = load_json(review_path)
    authorization = load_json(authorization_path)
    contract_sha = sha256_file(contract_path)
    preflight_sha = sha256_file(preflight_path)
    review_sha = sha256_file(review_path)
    auth_sha = sha256_file(authorization_path)

    require(authorization.get("status") == AUTH_STATUS, "Bridge Stage-A structural authorization status drift")
    require(authorization.get("control_plane_revision") == CONTROL_PLANE_REVISION, "Bridge Stage-A structural authorization revision drift")
    require(authorization.get("contract_sha256") == contract_sha, "Bridge Stage-A structural authorization contract drift")
    require(authorization.get("preflight_sha256") == preflight_sha, "Bridge Stage-A structural authorization preflight drift")
    require((authorization.get("independent_review") or {}).get("sha256") == review_sha, "Bridge Stage-A structural authorization review drift")
    require((authorization.get("independent_review") or {}).get("verdict") == REVIEW_VERDICT, "Bridge Stage-A structural authorization review verdict drift")
    require(authorization.get("authority_requires_external_signed_capability") is True, "Bridge Stage-A structural authorization does not require signed capability")
    require(authorization.get("production_public_key_sha256") == PRODUCTION_PUBLIC_KEY_SHA256, "Bridge Stage-A structural authorization trust-root drift")
    require(review.get("status") == "COMPLETED" and review.get("verdict") == REVIEW_VERDICT, "Bridge Stage-A accepted review receipt drift")
    require(review.get("control_plane_revision") == CONTROL_PLANE_REVISION, "Bridge Stage-A accepted review revision drift")
    require(review.get("contract_sha256_acknowledged") == contract_sha, "Bridge Stage-A review contract acknowledgement drift")
    require(review.get("preflight_sha256_acknowledged") == preflight_sha, "Bridge Stage-A review preflight acknowledgement drift")
    require(preflight.get("contract_sha256") == contract_sha and preflight.get("provider_calls") == 0, "Bridge Stage-A preflight binding drift")
    require(PRODUCTION_PUBLIC_KEY_PATH.is_file() and sha256_file(PRODUCTION_PUBLIC_KEY_PATH) == PRODUCTION_PUBLIC_KEY_SHA256, "Bridge Stage-A production public key drift")

    scope = authorization["execution_scope"]
    expected_authority = authorization["authority"]
    return {
        "capability_id": capability_id or secrets.token_hex(32),
        "issued_at_utc": issued_at_utc or datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "control_plane_revision": CONTROL_PLANE_REVISION,
        "contract_sha256": contract_sha,
        "preflight_sha256": preflight_sha,
        "review_receipt_sha256": review_sha,
        "structural_authorization_sha256": auth_sha,
        "runner_sha256": contract["bound_code"]["runner"]["sha256"],
        "runtime_sha256": contract["bound_code"]["runtime"]["sha256"],
        "support_sha256": contract["bound_code"]["support"]["sha256"],
        "identity_sha256": contract["model_identity"]["sha256"],
        "run_root": scope["run_root"],
        "lineage_lease_path": scope["lineage_lease_path"],
        "consumption_marker_path": scope["consumption_marker_path"],
        "single_use": True,
        "authority": expected_authority,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--private-key", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--preflight", type=Path, required=True)
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), "Bridge Stage-A signed capability already exists")
    payload = build_payload(
        contract_path=args.contract,
        preflight_path=args.preflight,
        review_path=args.review,
        authorization_path=args.authorization,
    )
    document = sign_document(
        payload=payload,
        private_key_path=args.private_key,
        public_key_path=PRODUCTION_PUBLIC_KEY_PATH,
    )
    atomic_exclusive(args.output, document)
    print(
        json.dumps(
            {
                "status": "SIGNED_E2_R17_BRIDGE_V4R2_STAGE_A_CAPABILITY",
                "capability_id": payload["capability_id"],
                "public_key_sha256": PRODUCTION_PUBLIC_KEY_SHA256,
                "provider_calls": 0,
                "scientific_execution": False,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
