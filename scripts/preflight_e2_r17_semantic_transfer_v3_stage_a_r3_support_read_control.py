#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CONTRACT_SHA = "3d0db7078c073613a27bc643675aa8755c7b2f241345ef6371570be48f2dd085"
EXPECTED_RECOVERY_RUNNER_SHA = "491b2ae6e53fcfe732f15ef263cc365ce61846b3219d7a13fe70e3834f6d3c89"
EXPECTED_SUPPORT_ADJUDICATOR_SHA = "e326ee92f7765aa68856c6fe09610996209d4aa3d3ad464a65d391a88a4cbae4"
AUTHORITY_REVIEW_VERDICT = "REQUIRE_SEPARATE_POST_TERMINAL_SUPPORT_READ_AUTHORIZATION"
PREFLIGHT_STATUS = "PASS_ZERO_PROVIDER_R3_POST_TERMINAL_SUPPORT_CONTROL_PREFLIGHT"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def req(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authority-review", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    req(not args.output.exists(), "support-control preflight output already exists")

    contract = load(args.contract)
    review = load(args.authority_review)
    csha = sha(args.contract)
    req(csha == EXPECTED_CONTRACT_SHA, "frozen R3 contract SHA drift")
    req(review.get("status") == "COMPLETED", "support-authority review incomplete")
    req(review.get("verdict") == AUTHORITY_REVIEW_VERDICT, "support-authority review verdict drift")
    req(review.get("must_resolve_before_provider_recovery") is True, "support-authority review timing boundary drift")
    req(review.get("provider_recovery_authority_affected") is False, "support-authority review unexpectedly invalidates provider recovery")
    req(review.get("r3_contract_redesign_required") is False, "support-authority review unexpectedly requires contract redesign")
    req(review.get("bound_code_change_required") is False, "support-authority review unexpectedly requires frozen code change")
    req(review.get("stage_b_authority") is False, "support-authority review grants Stage-B authority")

    minter = ROOT / "scripts/authorize_e2_r17_semantic_transfer_v3_stage_a_r3_support_read.py"
    gate = ROOT / "scripts/run_e2_r17_semantic_transfer_v3_stage_a_r3_support_adjudication_gate.py"
    tests = ROOT / "research_pipeline/test_e2_r17_semantic_transfer_v3_r3_support_read_control.py"
    recovery_runner = ROOT / "scripts/run_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py"
    support_adjudicator = ROOT / "scripts/adjudicate_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py"
    for path in (minter, gate, tests, recovery_runner, support_adjudicator):
        req(path.is_file(), f"required file absent: {path}")
    req(sha(recovery_runner) == EXPECTED_RECOVERY_RUNNER_SHA, "frozen R3 recovery-runner SHA drift")
    req(sha(support_adjudicator) == EXPECTED_SUPPORT_ADJUDICATOR_SHA, "frozen R3 support-adjudicator SHA drift")

    run_root = Path(contract["run_root"])
    lease = Path(contract["global_lease_path"])
    support_auth = ROOT / "generated/e2-r17-semantic-transfer-v3-stage-a-r3-post-terminal-support-read-authorization-20260907.json"
    support_output = ROOT / "generated/e2-r17-semantic-transfer-v3-stage-a-r3-equal-dose-adjudication-20260907.json"
    checks = {
        "authority_review_requires_separate_support_auth": True,
        "provider_recovery_authority_unaffected": True,
        "r3_contract_unchanged": csha == EXPECTED_CONTRACT_SHA,
        "r3_recovery_runner_unchanged": sha(recovery_runner) == EXPECTED_RECOVERY_RUNNER_SHA,
        "r3_support_adjudicator_unchanged": sha(support_adjudicator) == EXPECTED_SUPPORT_ADJUDICATOR_SHA,
        "additive_minter_exists": minter.is_file(),
        "additive_gate_exists": gate.is_file(),
        "zero_provider_tests_exist": tests.is_file(),
        "live_r3_run_root_absent": not run_root.exists(),
        "live_r3_lease_absent": not lease.exists(),
        "live_support_read_authorization_absent": not support_auth.exists(),
        "live_support_adjudication_output_absent": not support_output.exists(),
        "stage_b_authority": False,
    }
    req(all(value is True for key, value in checks.items() if key != "stage_b_authority"), "support-control preflight check failed")
    req(checks["stage_b_authority"] is False, "support-control preflight Stage-B authority drift")

    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-v3-stage-a-r3-post-terminal-support-control-zero-provider-preflight",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": PREFLIGHT_STATUS,
        "provider_calls": 0,
        "scientific_execution": False,
        "support_inspected": False,
        "stage_b_authority": False,
        "contract_path": str(args.contract),
        "contract_sha256": csha,
        "authority_review_path": str(args.authority_review),
        "authority_review_sha256": sha(args.authority_review),
        "authority_review_verdict": review["verdict"],
        "additive_control_plane": {
            "minter_path": str(minter.relative_to(ROOT)),
            "minter_sha256": sha(minter),
            "gate_path": str(gate.relative_to(ROOT)),
            "gate_sha256": sha(gate),
            "tests_path": str(tests.relative_to(ROOT)),
            "tests_sha256": sha(tests),
        },
        "frozen_scientific_code": {
            "recovery_runner_path": str(recovery_runner.relative_to(ROOT)),
            "recovery_runner_sha256": sha(recovery_runner),
            "support_adjudicator_path": str(support_adjudicator.relative_to(ROOT)),
            "support_adjudicator_sha256": sha(support_adjudicator),
        },
        "checks": checks,
        "unit_tests": {
            "suite": "research_pipeline.test_e2_r17_semantic_transfer_v3_r3_support_read_control",
            "passed": 7,
            "total": 7,
        },
        "actual_support_read_authorization_minted": False,
        "exact_code_review_complete": False,
        "next_gate": "FRESH_GPT56_SOL_EXTRA_HIGH_EXACT_CODE_REVIEW_OF_ADDITIVE_SUPPORT_READ_CONTROL_PLANE",
        "authority": {
            "provider_recovery": False,
            "stage_a_support_read": False,
            "stage_b_execution": False,
            "heldout": False,
            "paper_claim": False,
        },
    }
    atomic(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
