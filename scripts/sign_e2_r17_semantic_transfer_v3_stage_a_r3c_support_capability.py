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

from research_pipeline.e2_r17_r3c_signed_support_capability import (
    CONTROL_PLANE_REVISION,
    HARD_PROVIDER_NOT_BEFORE,
    public_key_fingerprint,
    sign_document,
)
EXPECTED_PUBLIC_KEY_SHA256 = "f4b73b89716bee28902feb699d9ab81822a986ac8b89235cf768407c3e01fda0"
SUPPORT_AUTH_STATUS = "AUTHORIZED_E2_R17_V3_R3_POST_TERMINAL_SUPPORT_READ"
CONTROL_REVIEW_VERDICT = "PASS_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def req(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def atomic(path: Path, payload: dict[str, Any]) -> None:
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
    recovery_authorization_path: Path,
    summary_path: Path,
    support_authorization_path: Path,
    control_review_path: Path,
    public_key_path: Path,
    adjudication_output_path: Path,
    issued_at_utc: str | None = None,
    nonce: str | None = None,
) -> dict[str, Any]:
    contract = load(contract_path)
    support_auth = load(support_authorization_path)
    review = load(control_review_path)
    req(contract.get("control_plane_revision") == CONTROL_PLANE_REVISION, "R3C contract revision drift")
    signer = ((contract.get("post_terminal_support_read_control") or {}).get("trusted_external_signer") or {})
    req(signer.get("algorithm") == "Ed25519", "R3C contract signer algorithm drift")
    req(signer.get("public_key_sha256") == EXPECTED_PUBLIC_KEY_SHA256, "R3C contract signer public-key SHA drift")
    req(public_key_fingerprint(public_key_path) == EXPECTED_PUBLIC_KEY_SHA256, "R3C signer public key drift")
    req(support_auth.get("status") == SUPPORT_AUTH_STATUS, "R3C support authorization status drift")
    req(support_auth.get("contract_sha256") == sha(contract_path), "R3C support authorization contract SHA drift")
    req(support_auth.get("recovery_authorization_sha256") == sha(recovery_authorization_path), "R3C support authorization recovery-auth SHA drift")
    req(support_auth.get("terminal_summary_sha256") == sha(summary_path), "R3C support authorization terminal-summary SHA drift")
    review_row = support_auth.get("control_review") or {}
    req(review_row.get("sha256") == sha(control_review_path), "R3C support authorization/control-review SHA drift")
    req(review.get("status") == "COMPLETED" and review.get("surface") == "ChatGPT web" and review.get("model") == "GPT-5.6 Sol", "R3C control-review provenance drift")
    req(review.get("verdict") == CONTROL_REVIEW_VERDICT, "R3C control review did not PASS")
    req(review.get("control_plane_revision") == CONTROL_PLANE_REVISION, "R3C control-review revision drift")
    control = support_auth.get("bound_control_plane") or {}
    scope = support_auth.get("execution_scope") or {}
    req(Path(str(scope.get("required_adjudication_output") or "")).resolve() == adjudication_output_path.resolve(), "R3C adjudication output path drift")
    authority = support_auth.get("authority") or {}
    req(authority.get("stage_a_support_read") is True, "R3C support authorization lacks support-read authority")
    for key in ("stage_a_provider_execution", "stage_b_learning_execution", "updater", "heldout_evaluation", "analyzer", "second_backbone", "public_benchmark", "paper_promotion", "submission"):
        req(authority.get(key) is False, f"R3C support authorization overbroad: {key}")
    return {
        "capability_id": nonce or secrets.token_hex(32),
        "issued_at_utc": issued_at_utc or datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "control_plane_revision": CONTROL_PLANE_REVISION,
        "hard_provider_not_before": HARD_PROVIDER_NOT_BEFORE,
        "contract_sha256": sha(contract_path),
        "recovery_authorization_sha256": sha(recovery_authorization_path),
        "terminal_summary_sha256": sha(summary_path),
        "support_authorization_sha256": sha(support_authorization_path),
        "control_review_sha256": sha(control_review_path),
        "minter_sha256": str(control.get("minter_sha256") or ""),
        "gate_sha256": str(control.get("gate_sha256") or ""),
        "support_adjudicator_sha256": str(control.get("support_adjudicator_sha256") or ""),
        "required_adjudication_output": str(adjudication_output_path.resolve()),
        "required_run_root": str(Path(str(scope.get("required_run_root") or "")).resolve()),
        "single_use": True,
        "stage_a_support_read": True,
        "stage_a_provider_execution": False,
        "stage_b_learning_execution": False,
        "updater": False,
        "heldout_evaluation": False,
        "analyzer": False,
        "second_backbone": False,
        "public_benchmark": False,
        "paper_promotion": False,
        "submission": False,
        "scientific_authority": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--private-key", type=Path, required=True)
    ap.add_argument("--public-key", type=Path, required=True)
    ap.add_argument("--contract", type=Path, required=True)
    ap.add_argument("--recovery-authorization", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    ap.add_argument("--support-authorization", type=Path, required=True)
    ap.add_argument("--control-review", type=Path, required=True)
    ap.add_argument("--adjudication-output", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    req(not args.output.exists(), "R3C signed support capability already exists")
    payload = build_payload(
        contract_path=args.contract,
        recovery_authorization_path=args.recovery_authorization,
        summary_path=args.summary,
        support_authorization_path=args.support_authorization,
        control_review_path=args.control_review,
        public_key_path=args.public_key,
        adjudication_output_path=args.adjudication_output,
    )
    document = sign_document(payload=payload, private_key_path=args.private_key, public_key_path=args.public_key)
    atomic(args.output, document)
    print(json.dumps({"status": "SIGNED_R3C_SUPPORT_CAPABILITY", "capability_id": payload["capability_id"], "public_key_sha256": public_key_fingerprint(args.public_key), "provider_calls": 0, "scientific_authority": False}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
