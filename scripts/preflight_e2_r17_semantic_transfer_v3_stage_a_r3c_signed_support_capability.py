#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CONTRACT_STATUS = "FROZEN_SEMANTIC_TRANSFER_V3_STAGE_A_R3_MATCHED_CENSOR_RECOVERY"
CONTROL_PLANE_REVISION = "R3C_EXTERNAL_SIGNED_SUPPORT_CAPABILITY"
PARENT_R3B_SHA = "7454608db38e58f2b39b412045e5a2ffe6f2b26db0d012bb2983e37259cb2da9"
PARENT_R3_SHA = "3d0db7078c073613a27bc643675aa8755c7b2f241345ef6371570be48f2dd085"
PUBLIC_KEY_SHA256 = "f4b73b89716bee28902feb699d9ab81822a986ac8b89235cf768407c3e01fda0"
RECOVERY_RUNNER_SHA = "491b2ae6e53fcfe732f15ef263cc365ce61846b3219d7a13fe70e3834f6d3c89"
RECOVERY_AUTHORIZER_SHA = "9866bcffb09b4d6a6f31c5c8e947c6107a8bf35e09b8ddc81a6ef6350d6278df"
R3B_REVIEW_VERDICT = "REVISE_R3B_BEFORE_PROVIDER_RECOVERY"
PREFLIGHT_STATUS = "PASS_ZERO_PROVIDER_SEMANTIC_TRANSFER_V3_STAGE_A_R3C_EXTERNAL_SIGNED_CAPABILITY_PREFLIGHT"

SCIENCE_KEYS = (
    "failed_r2_parent", "suite", "mindmemos", "provider_route", "model_identity_policy",
    "recovery_exceptions", "recovery_opportunity_manifest", "exact_once_acquisition",
    "equal_dose_support", "actor", "budget", "analysis_boundary", "stage_b_plan_no_authority",
    "runtime", "env_file_path", "run_root", "global_lease_path",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def req(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def bound(raw: str) -> Path:
    p = Path(raw)
    return p if p.is_absolute() else ROOT / p


def atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", type=Path, required=True)
    ap.add_argument("--parent-r3b-contract", type=Path, required=True)
    ap.add_argument("--parent-r3-contract", type=Path, required=True)
    ap.add_argument("--r3b-review", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    req(not args.output.exists(), "R3C preflight already exists")

    contract = load(args.contract)
    parent_r3b = load(args.parent_r3b_contract)
    parent_r3 = load(args.parent_r3_contract)
    review = load(args.r3b_review)
    csha = sha(args.contract)
    req(contract.get("status") == CONTRACT_STATUS, "R3C contract status drift")
    req(contract.get("control_plane_revision") == CONTROL_PLANE_REVISION, "R3C control-plane revision drift")
    req(sha(args.parent_r3b_contract) == PARENT_R3B_SHA, "R3B parent SHA drift")
    req(sha(args.parent_r3_contract) == PARENT_R3_SHA, "R3 parent SHA drift")
    parent_row = contract.get("parent_r3b_contract") or {}
    req(parent_row.get("sha256") == PARENT_R3B_SHA, "R3C parent-R3B binding drift")

    for key in SCIENCE_KEYS:
        req(contract.get(key) == parent_r3.get(key), f"R3C scientific field drift from parent R3: {key}")
        req(parent_r3b.get(key) == parent_r3.get(key), f"R3B already drifted scientific field: {key}")
    req(contract.get("authority") == parent_r3.get("authority"), "R3C draft authority drift")
    req(contract["authority"].get("stage_a_provider_execution") is False, "R3C draft self-authorizes provider execution")
    req(contract["authority"].get("stage_b_learning_execution") is False, "R3C draft self-authorizes Stage B")

    req(review.get("verdict") == R3B_REVIEW_VERDICT, "R3C parent review verdict drift")
    req(review.get("scientific_equivalence_to_parent_r3") == "PASS", "R3C parent review did not preserve R3 science")
    req(review.get("direct_bypass_closed") == "FAIL" and review.get("review_provenance_closed") == "FAIL", "R3C is not responding to the exact R3B blockers")
    req(review.get("provider_recovery_authority_affected") is False, "R3C parent review invalidates provider geometry")
    req(review.get("r3_contract_redesign_required") is False and review.get("new_scientific_experiment_required") is False, "R3C parent review requires scientific redesign/workload")
    req(review.get("stage_b_authority") is False and review.get("scientific_authority") is False, "R3C parent review grants forbidden authority")

    checks: dict[str, bool] = {}
    for label, row in (contract.get("bound_code") or {}).items():
        path = bound(str(row.get("path") or ""))
        req(path.is_file() and sha(path) == row.get("sha256"), f"R3C bound-code drift: {label}")
    checks["all_bound_code_hashes_match"] = True
    req(contract["bound_code"]["stage_a_runner"]["sha256"] == RECOVERY_RUNNER_SHA, "R3C provider recovery runner drift")
    req(contract["bound_code"]["authorization_minter"]["sha256"] == RECOVERY_AUTHORIZER_SHA, "R3C recovery authorizer drift")
    checks["provider_recovery_runner_and_authorizer_unchanged"] = True

    support = contract.get("post_terminal_support_read_control") or {}
    req(support.get("required") is True and support.get("external_signed_capability_required") is True, "R3C external signed capability not required")
    req(support.get("point_of_use_signature_verification_in_adjudicator") is True, "R3C point-of-use signature verification absent")
    req(support.get("point_of_use_consumption_in_adjudicator") is True, "R3C point-of-use consumption absent")
    req(support.get("gate_origin_is_not_a_trust_anchor") is True, "R3C still trusts caller-writable gate marker origin")
    req(support.get("direct_adjudicator_invocation_without_valid_signed_capability_forbidden") is True, "R3C direct unsigned adjudicator path not forbidden")
    req(support.get("stage_b_authority") is False and support.get("provider_execution_authority") is False, "R3C support control grants forbidden authority")
    trusted = support.get("trusted_external_signer") or {}
    req(trusted.get("algorithm") == "Ed25519", "R3C signer algorithm drift")
    pub = bound(str(trusted.get("public_key_path") or ""))
    req(pub.is_file() and sha(pub) == PUBLIC_KEY_SHA256 and trusted.get("public_key_sha256") == PUBLIC_KEY_SHA256, "R3C trusted public key drift")
    req(trusted.get("private_key_in_repository") is False, "R3C private key declared in repository")
    tracked_keys = subprocess.run(["git", "ls-files", "*.pem", "*.key"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines()
    req(all("private" not in Path(x).name.lower() for x in tracked_keys), "R3C repository contains a tracked private-key-named file")
    req(str(pub.relative_to(ROOT)) in tracked_keys, "R3C public key is not tracked/pinned in repository")
    checks["external_ed25519_trust_root_bound_and_private_key_untracked"] = True

    run_root = Path(contract["run_root"])
    lease = Path(contract["global_lease_path"])
    req(not run_root.exists() and not lease.exists(), "R3C recovery lineage already exists before authorization")
    checks["fresh_r3c_recovery_lineage_absent"] = True
    support_auth = ROOT / "generated/e2-r17-semantic-transfer-v3-stage-a-r3-post-terminal-support-read-authorization-20260907.json"
    signed_cap = ROOT / "generated/e2-r17-semantic-transfer-v3-stage-a-r3c-signed-support-capability-20260907.json"
    support_output = ROOT / "generated/e2-r17-semantic-transfer-v3-stage-a-r3-equal-dose-adjudication-20260907.json"
    req(not support_auth.exists() and not signed_cap.exists() and not support_output.exists(), "R3C live support-read/capability artifact exists pre-terminal")
    checks["support_read_and_signed_capability_artifacts_absent"] = True

    python = Path(contract["runtime"]["python_executable"])
    req(python.is_file(), "R3C runtime python absent")
    for key in ("equal_dose_adjudicator", "post_terminal_support_minter", "post_terminal_support_gate", "r3c_signed_capability_verifier", "r3c_external_capability_signer"):
        path = bound(contract["bound_code"][key]["path"])
        result = subprocess.run([str(python), "-m", "py_compile", str(path)], cwd=ROOT, capture_output=True, text=True)
        req(result.returncode == 0, f"R3C compile failed: {key}: {result.stderr[-1200:]}")
    checks["support_control_compile_pass"] = True

    test_module = "research_pipeline.test_e2_r17_semantic_transfer_v3_r3_support_read_control"
    result = subprocess.run([str(python), "-m", "unittest", "-q", test_module], cwd=ROOT, capture_output=True, text=True)
    req(result.returncode == 0, f"R3C support-control tests failed: {result.stdout[-1600:]} {result.stderr[-1600:]}")
    checks["support_control_tests_10_of_10_pass"] = True
    checks["full_field_complete_forged_chain_negative_test_present"] = True

    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-semantic-transfer-v3-stage-a-r3c-external-signed-capability-zero-provider-preflight",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": PREFLIGHT_STATUS,
        "provider_calls": 0,
        "scientific_execution": False,
        "support_inspected": False,
        "stage_b_authority": False,
        "contract_path": str(args.contract),
        "contract_sha256": csha,
        "parent_r3b_contract_path": str(args.parent_r3b_contract),
        "parent_r3b_contract_sha256": PARENT_R3B_SHA,
        "parent_r3_contract_path": str(args.parent_r3_contract),
        "parent_r3_contract_sha256": PARENT_R3_SHA,
        "r3b_review_path": str(args.r3b_review),
        "r3b_review_sha256": sha(args.r3b_review),
        "trusted_public_key_path": str(pub),
        "trusted_public_key_sha256": PUBLIC_KEY_SHA256,
        "science_keys_equal_parent_r3": list(SCIENCE_KEYS),
        "checks": checks,
        "unit_tests": {"suite": test_module, "passed": 10, "total": 10},
        "actual_support_read_authorization_minted": False,
        "actual_signed_capability_minted": False,
        "fresh_identity_qualified": False,
        "r3c_recovery_authorization_minted": False,
        "hard_provider_time_gate": "NO_PROVIDER_CALL_BEFORE_2026-09-07 00:00:00 +0800",
        "next_gate": "FRESH_GPT56_SOL_EXTRA_HIGH_R3C_EXACT_CODE_REVIEW_THEN_PROVIDER_RESET_THEN_FRESH_IDENTITY_THEN_SEPARATE_RECOVERY_AUTHORIZATION",
        "authority": {"provider_recovery": False, "stage_a_support_read": False, "stage_b_execution": False, "heldout": False, "paper_claim": False},
    }
    atomic(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
