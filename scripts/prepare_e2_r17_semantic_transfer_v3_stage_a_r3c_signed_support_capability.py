#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTROL_PLANE_REVISION = "R3C_EXTERNAL_SIGNED_SUPPORT_CAPABILITY"
PARENT_R3B_SHA = "7454608db38e58f2b39b412045e5a2ffe6f2b26db0d012bb2983e37259cb2da9"
PARENT_R3_SHA = "3d0db7078c073613a27bc643675aa8755c7b2f241345ef6371570be48f2dd085"
R3B_REVIEW_VERDICT = "REVISE_R3B_BEFORE_PROVIDER_RECOVERY"
PUBLIC_KEY_SHA256 = "f4b73b89716bee28902feb699d9ab81822a986ac8b89235cf768407c3e01fda0"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def req(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def rel(path: Path) -> str:
    path = path.resolve()
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def bound_code(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": sha(path)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parent-r3b-contract", type=Path, required=True)
    ap.add_argument("--parent-r3-contract", type=Path, required=True)
    ap.add_argument("--r3b-review", type=Path, required=True)
    ap.add_argument("--public-key", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    req(not args.output.exists(), "R3C contract already exists")
    parent = load(args.parent_r3b_contract)
    parent_r3 = load(args.parent_r3_contract)
    review = load(args.r3b_review)
    req(sha(args.parent_r3b_contract) == PARENT_R3B_SHA, "R3B parent contract SHA drift")
    req(sha(args.parent_r3_contract) == PARENT_R3_SHA, "R3 parent contract SHA drift")
    req(parent.get("control_plane_revision") == "R3B_POST_TERMINAL_SUPPORT_GUARD", "R3B parent revision drift")
    req(review.get("verdict") == R3B_REVIEW_VERDICT, "R3B review verdict drift")
    req(review.get("scientific_equivalence_to_parent_r3") == "PASS", "R3B review did not preserve R3 science")
    req(review.get("provider_recovery_authority_affected") is False, "R3B review invalidated provider recovery geometry")
    req(review.get("r3_contract_redesign_required") is False, "R3B review requires scientific redesign")
    req(review.get("new_scientific_experiment_required") is False, "R3B review requires new science")
    req(review.get("stage_b_authority") is False and review.get("scientific_authority") is False, "R3B review grants forbidden authority")
    req(sha(args.public_key) == PUBLIC_KEY_SHA256, "R3C trusted public key SHA drift")

    adjudicator = ROOT / "scripts/adjudicate_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py"
    minter = ROOT / "scripts/authorize_e2_r17_semantic_transfer_v3_stage_a_r3_support_read.py"
    gate = ROOT / "scripts/run_e2_r17_semantic_transfer_v3_stage_a_r3_support_adjudication_gate.py"
    verifier = ROOT / "research_pipeline/e2_r17_r3c_signed_support_capability.py"
    signer = ROOT / "scripts/sign_e2_r17_semantic_transfer_v3_stage_a_r3c_support_capability.py"
    tests = ROOT / "research_pipeline/test_e2_r17_semantic_transfer_v3_r3_support_read_control.py"
    builder = Path(__file__).resolve()
    preflight = ROOT / "scripts/preflight_e2_r17_semantic_transfer_v3_stage_a_r3c_signed_support_capability.py"
    for path in (adjudicator, minter, gate, verifier, signer, tests, builder, preflight):
        req(path.is_file(), f"R3C control file absent: {path}")

    out = copy.deepcopy(parent)
    out["created_at_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    out["control_plane_revision"] = CONTROL_PLANE_REVISION
    out["parent_r3b_contract"] = {
        "path": rel(args.parent_r3b_contract),
        "sha256": PARENT_R3B_SHA,
        "relationship": "control-plane-only successor replacing caller-writable provenance with an externally signed point-of-use capability",
    }
    out["scientific_role"] = (
        "R3C control-plane-only successor to the already-frozen R3 matched-censor recovery; "
        "provider task universe, 158+1+1 geometry, K=8 pools, 7/7/8 opportunities, equal-dose support estimand, and Stage-B boundary are unchanged"
    )
    out["bound_code"]["equal_dose_adjudicator"] = bound_code(adjudicator)
    out["bound_code"]["post_terminal_support_minter"] = bound_code(minter)
    out["bound_code"]["post_terminal_support_gate"] = bound_code(gate)
    out["bound_code"]["post_terminal_support_tests"] = bound_code(tests)
    out["bound_code"]["r3c_signed_capability_verifier"] = bound_code(verifier)
    out["bound_code"]["r3c_external_capability_signer"] = bound_code(signer)
    out["bound_code"]["r3c_contract_builder"] = bound_code(builder)
    out["bound_code"]["r3c_signed_capability_preflight"] = bound_code(preflight)

    reviews = copy.deepcopy(out.get("recovery_reviews") or {})
    reviews["post_terminal_support_control_r3b_v2"] = {
        "path": rel(args.r3b_review),
        "sha256": sha(args.r3b_review),
        "verdict": R3B_REVIEW_VERDICT,
    }
    out["recovery_reviews"] = reviews
    out["post_terminal_support_read_control"] = {
        "required": True,
        "control_plane_revision": CONTROL_PLANE_REVISION,
        "support_authorization_is_structural_request_only": True,
        "external_signed_capability_required": True,
        "point_of_use_signature_verification_in_adjudicator": True,
        "point_of_use_consumption_in_adjudicator": True,
        "gate_origin_is_not_a_trust_anchor": True,
        "direct_adjudicator_invocation_without_valid_signed_capability_forbidden": True,
        "single_use_consumption_required": True,
        "automatic_retry_after_consumption": False,
        "support_read_authorization_may_mint_only_after_terminal_recovery": True,
        "terminal_summary_status_required": "COMPLETED_158_POOLS_PLUS_TWO_FROZEN_EXCEPTIONS_PENDING_R3_EQUAL_DOSE_ADJUDICATION",
        "support_read_authority": "stage_a_support_read_only_with_external_signed_capability",
        "provider_execution_authority": False,
        "updater_authority": False,
        "heldout_authority": False,
        "stage_b_authority": False,
        "paper_claim_authority": False,
        "actual_support_read_authorization_minted": False,
        "actual_signed_capability_minted": False,
        "trusted_external_signer": {
            "algorithm": "Ed25519",
            "signature_context": "E2-R17-R3C-POST-TERMINAL-SUPPORT-CAPABILITY-V1",
            "public_key_path": rel(args.public_key),
            "public_key_sha256": PUBLIC_KEY_SHA256,
            "private_key_in_repository": False,
            "private_key_location_class": "external controller only; root-owned on host52",
            "signer_host_role": "independent Research OS control-plane signer",
        },
    }
    out["authority"] = copy.deepcopy(parent_r3["authority"])
    out["next_gate"] = {
        "before_provider_reset": "FRESH_GPT56_SOL_EXTRA_HIGH_R3C_EXACT_CODE_REVIEW_ONLY_NO_PROVIDER_CALL",
        "after_reset_and_r3c_pass": "EXACTLY_ONE_FRESH_DEEPSEEK_IDENTITY_THEN_LOCAL_ADJUDICATION_THEN_SEPARATE_R3C_RECOVERY_AUTHORIZATION",
        "provider_recovery": "EXECUTE_ONLY_158_ORIGINAL_PROVIDER_TASKS_UNDER_R3C_CONTRACT",
        "post_terminal": "MINT_STRUCTURAL_SUPPORT_REQUEST_THEN_EXTERNAL_CONTROLLER_SIGNS_SINGLE_USE_CAPABILITY_THEN_POINT_OF_USE_VERIFY_AND_CONSUME",
        "stage_b": "SEPARATE_CONTRACT_REVIEW_AND_AUTHORITY_REQUIRED",
    }
    atomic(args.output, out)
    print(json.dumps({
        "status": out["status"],
        "control_plane_revision": CONTROL_PLANE_REVISION,
        "parent_r3b_sha256": PARENT_R3B_SHA,
        "parent_r3_sha256": PARENT_R3_SHA,
        "trusted_public_key_sha256": PUBLIC_KEY_SHA256,
        "output": str(args.output),
        "output_sha256": sha(args.output),
        "provider_calls": 0,
        "scientific_execution": False,
        "stage_b_authority": False,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
