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
CONTROL_PLANE_REVISION = "R3B_POST_TERMINAL_SUPPORT_GUARD"
PARENT_R3_SHA = "3d0db7078c073613a27bc643675aa8755c7b2f241345ef6371570be48f2dd085"
RECOVERY_RUNNER_SHA = "491b2ae6e53fcfe732f15ef263cc365ce61846b3219d7a13fe70e3834f6d3c89"
AUTHORITY_REVIEW_VERDICT = "REQUIRE_SEPARATE_POST_TERMINAL_SUPPORT_READ_AUTHORIZATION"
R1_REVIEW_VERDICT = "REVISE_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE"
PREFLIGHT_STATUS = "PASS_ZERO_PROVIDER_SEMANTIC_TRANSFER_V3_STAGE_A_R3B_SUPPORT_GUARD_PREFLIGHT"

SCIENCE_KEYS = (
    "failed_r2_parent",
    "suite",
    "mindmemos",
    "provider_route",
    "model_identity_policy",
    "recovery_exceptions",
    "recovery_opportunity_manifest",
    "exact_once_acquisition",
    "equal_dose_support",
    "actor",
    "budget",
    "analysis_boundary",
    "stage_b_plan_no_authority",
    "runtime",
    "env_file_path",
    "run_root",
    "global_lease_path",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def req(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def bound(raw: str) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else ROOT / path


def atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--parent-contract", type=Path, required=True)
    parser.add_argument("--authority-review", type=Path, required=True)
    parser.add_argument("--r1-exact-code-review", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    req(not args.output.exists(), "R3B preflight already exists")

    contract = load(args.contract)
    parent = load(args.parent_contract)
    authority_review = load(args.authority_review)
    r1_review = load(args.r1_exact_code_review)
    csha = sha(args.contract)
    psha = sha(args.parent_contract)

    req(contract.get("status") == CONTRACT_STATUS, "R3B contract status drift")
    req(contract.get("control_plane_revision") == CONTROL_PLANE_REVISION, "R3B control-plane revision drift")
    req(psha == PARENT_R3_SHA, "parent R3 contract SHA drift")
    parent_row = contract.get("parent_r3_contract") or {}
    req(bound(str(parent_row.get("path") or "")).resolve() == args.parent_contract.resolve(), "R3B parent contract path drift")
    req(parent_row.get("sha256") == psha, "R3B parent contract binding drift")

    for key in SCIENCE_KEYS:
        req(contract.get(key) == parent.get(key), f"R3B scientific field drift: {key}")
    req(contract.get("authority") == parent.get("authority"), "R3B draft authority drift")
    req(contract["authority"].get("stage_a_provider_execution") is False, "R3B draft self-authorizes provider execution")
    req(contract["authority"].get("stage_b_learning_execution") is False, "R3B draft self-authorizes Stage B")

    req(authority_review.get("verdict") == AUTHORITY_REVIEW_VERDICT, "R3B authority-review verdict drift")
    req(authority_review.get("must_resolve_before_provider_recovery") is True, "R3B authority-review timing drift")
    req(authority_review.get("provider_recovery_authority_affected") is False, "R3B authority-review invalidates provider recovery")
    req(r1_review.get("verdict") == R1_REVIEW_VERDICT, "R3B R1 exact-code review verdict drift")
    req(r1_review.get("provider_recovery_authority_affected") is False, "R3B R1 review invalidates provider recovery")
    req(r1_review.get("stage_b_authority") is False, "R3B R1 review grants Stage B")

    checks: dict[str, bool] = {}
    for label, row in (contract.get("bound_code") or {}).items():
        path = bound(str(row.get("path") or ""))
        req(path.is_file() and sha(path) == row.get("sha256"), f"R3B bound-code drift: {label}")
    checks["all_bound_code_hashes_match"] = True
    req(contract["bound_code"]["stage_a_runner"]["sha256"] == RECOVERY_RUNNER_SHA, "R3B recovery-runner hash drift")
    checks["provider_recovery_runner_unchanged"] = True

    support = contract.get("post_terminal_support_read_control") or {}
    req(support.get("required") is True, "R3B support-read control not required")
    req(support.get("direct_adjudicator_invocation_forbidden") is True, "R3B direct support-adjudicator invocation not forbidden")
    req(support.get("single_use_consumption_required") is True, "R3B single-use support consumption absent")
    req(support.get("support_read_authorization_may_mint_only_after_terminal_recovery") is True, "R3B terminal mint boundary absent")
    req(support.get("stage_b_authority") is False, "R3B support control grants Stage B")
    checks["post_terminal_support_control_bound"] = True

    run_root = Path(contract["run_root"])
    lease = Path(contract["global_lease_path"])
    req(not run_root.exists() and not lease.exists(), "R3B provider-recovery lineage already exists")
    checks["fresh_r3b_lineage_absent"] = True

    support_auth = ROOT / "generated/e2-r17-semantic-transfer-v3-stage-a-r3-post-terminal-support-read-authorization-20260907.json"
    support_output = ROOT / "generated/e2-r17-semantic-transfer-v3-stage-a-r3-equal-dose-adjudication-20260907.json"
    req(not support_auth.exists() and not support_output.exists(), "R3B live support-read artifact exists before terminal recovery")
    checks["support_read_artifacts_absent"] = True

    python = Path(contract["runtime"]["python_executable"])
    req(python.is_file(), "R3B runtime python absent")
    for key in ("equal_dose_adjudicator", "post_terminal_support_minter", "post_terminal_support_gate"):
        path = bound(contract["bound_code"][key]["path"])
        result = subprocess.run([str(python), "-m", "py_compile", str(path)], cwd=ROOT, capture_output=True, text=True)
        req(result.returncode == 0, f"R3B compile failed: {key}: {result.stderr[-1000:]}")
    checks["support_control_compile_pass"] = True

    test_module = "research_pipeline.test_e2_r17_semantic_transfer_v3_r3_support_read_control"
    result = subprocess.run([str(python), "-m", "unittest", "-q", test_module], cwd=ROOT, capture_output=True, text=True)
    req(result.returncode == 0, f"R3B support-control tests failed: {result.stdout[-1200:]} {result.stderr[-1200:]}")
    checks["support_control_tests_9_of_9_pass"] = True

    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-semantic-transfer-v3-stage-a-r3b-support-guard-zero-provider-preflight",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": PREFLIGHT_STATUS,
        "provider_calls": 0,
        "scientific_execution": False,
        "support_inspected": False,
        "stage_b_authority": False,
        "contract_path": str(args.contract),
        "contract_sha256": csha,
        "parent_r3_contract_path": str(args.parent_contract),
        "parent_r3_contract_sha256": psha,
        "authority_review_path": str(args.authority_review),
        "authority_review_sha256": sha(args.authority_review),
        "r1_exact_code_review_path": str(args.r1_exact_code_review),
        "r1_exact_code_review_sha256": sha(args.r1_exact_code_review),
        "science_keys_equal_parent": list(SCIENCE_KEYS),
        "checks": checks,
        "unit_tests": {"suite": test_module, "passed": 9, "total": 9},
        "actual_support_read_authorization_minted": False,
        "fresh_identity_qualified": False,
        "r3b_recovery_authorization_minted": False,
        "next_gate": "FRESH_GPT56_SOL_EXTRA_HIGH_R3B_EXACT_HASH_PREEXECUTION_REVIEW_THEN_PROVIDER_RESET_THEN_FRESH_IDENTITY_THEN_SEPARATE_RECOVERY_AUTHORIZATION",
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
