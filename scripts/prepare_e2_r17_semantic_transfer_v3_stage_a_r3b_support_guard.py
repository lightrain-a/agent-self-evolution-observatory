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
CONTROL_PLANE_REVISION = "R3B_POST_TERMINAL_SUPPORT_GUARD"
PARENT_R3_SHA = "3d0db7078c073613a27bc643675aa8755c7b2f241345ef6371570be48f2dd085"
AUTHORITY_REVIEW_VERDICT = "REQUIRE_SEPARATE_POST_TERMINAL_SUPPORT_READ_AUTHORIZATION"
R1_REVIEW_VERDICT = "REVISE_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def req(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def bound_code_row(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": sha(path)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parent-contract", type=Path, required=True)
    parser.add_argument("--authority-review", type=Path, required=True)
    parser.add_argument("--r1-exact-code-review", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    req(not args.output.exists(), "R3B contract already exists")
    parent = load(args.parent_contract)
    authority_review = load(args.authority_review)
    r1_review = load(args.r1_exact_code_review)
    psha = sha(args.parent_contract)
    req(psha == PARENT_R3_SHA, "parent R3 contract SHA drift")
    req(parent.get("status") == "FROZEN_SEMANTIC_TRANSFER_V3_STAGE_A_R3_MATCHED_CENSOR_RECOVERY", "parent R3 contract status drift")
    req(authority_review.get("verdict") == AUTHORITY_REVIEW_VERDICT, "support-authority review verdict drift")
    req(authority_review.get("must_resolve_before_provider_recovery") is True, "support-authority review timing drift")
    req(r1_review.get("verdict") == R1_REVIEW_VERDICT, "R1 exact-code review verdict drift")
    req(r1_review.get("provider_recovery_authority_affected") is False, "R1 exact-code review unexpectedly invalidates provider recovery")
    req(r1_review.get("stage_b_authority") is False, "R1 exact-code review grants Stage B")

    adjudicator = ROOT / "scripts/adjudicate_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py"
    minter = ROOT / "scripts/authorize_e2_r17_semantic_transfer_v3_stage_a_r3_support_read.py"
    gate = ROOT / "scripts/run_e2_r17_semantic_transfer_v3_stage_a_r3_support_adjudication_gate.py"
    tests = ROOT / "research_pipeline/test_e2_r17_semantic_transfer_v3_r3_support_read_control.py"
    preflight = ROOT / "scripts/preflight_e2_r17_semantic_transfer_v3_stage_a_r3b_support_guard.py"
    builder = Path(__file__).resolve()
    for path in (adjudicator, minter, gate, tests, preflight, builder):
        req(path.is_file(), f"R3B control file absent: {path}")

    out = copy.deepcopy(parent)
    out["created_at_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    out["control_plane_revision"] = CONTROL_PLANE_REVISION
    out["parent_r3_contract"] = {
        "path": rel(args.parent_contract.resolve()),
        "sha256": psha,
        "status": parent["status"],
        "relationship": "control-plane-only successor; scientific geometry, provider task universe, and support estimand unchanged",
    }
    out["scientific_role"] = (
        "versioned fail-closed Stage-A R3 matched-censor recovery with R3B post-terminal support-read authority guard; "
        "scientific recovery geometry and support semantics unchanged from parent R3"
    )
    out["bound_code"]["equal_dose_adjudicator"] = bound_code_row(adjudicator)
    out["bound_code"]["post_terminal_support_minter"] = bound_code_row(minter)
    out["bound_code"]["post_terminal_support_gate"] = bound_code_row(gate)
    out["bound_code"]["post_terminal_support_tests"] = bound_code_row(tests)
    out["bound_code"]["r3b_support_guard_preflight"] = bound_code_row(preflight)
    out["bound_code"]["r3b_contract_builder"] = bound_code_row(builder)

    recovery_reviews = copy.deepcopy(out.get("recovery_reviews") or {})
    recovery_reviews["post_terminal_support_authority"] = {
        "path": rel(args.authority_review.resolve()),
        "sha256": sha(args.authority_review),
        "verdict": AUTHORITY_REVIEW_VERDICT,
    }
    recovery_reviews["post_terminal_support_control_r1"] = {
        "path": rel(args.r1_exact_code_review.resolve()),
        "sha256": sha(args.r1_exact_code_review),
        "verdict": R1_REVIEW_VERDICT,
    }
    out["recovery_reviews"] = recovery_reviews
    out["post_terminal_support_read_control"] = {
        "required": True,
        "control_plane_revision": CONTROL_PLANE_REVISION,
        "direct_adjudicator_invocation_forbidden": True,
        "support_adjudicator_requires_support_authorization": True,
        "support_adjudicator_requires_gate_consumption_marker": True,
        "single_use_consumption_required": True,
        "automatic_retry_after_consumption": False,
        "support_read_authorization_may_mint_only_after_terminal_recovery": True,
        "terminal_summary_status_required": "COMPLETED_158_POOLS_PLUS_TWO_FROZEN_EXCEPTIONS_PENDING_R3_EQUAL_DOSE_ADJUDICATION",
        "support_read_authority": "stage_a_support_read_only",
        "provider_execution_authority": False,
        "updater_authority": False,
        "heldout_authority": False,
        "stage_b_authority": False,
        "paper_claim_authority": False,
        "exact_code_review_required_before_provider_recovery": True,
        "actual_support_read_authorization_minted": False,
    }
    out["authority"] = copy.deepcopy(parent["authority"])
    out["next_gate"] = {
        "before_provider_reset": "FRESH_GPT56_SOL_EXTRA_HIGH_R3B_EXACT_HASH_PREEXECUTION_REVIEW_ONLY_NO_PROVIDER_CALL",
        "after_reset_and_exact_hash_pass": "EXACTLY_ONE_FRESH_DEEPSEEK_IDENTITY_THEN_LOCAL_ADJUDICATION_THEN_SEPARATE_R3B_RECOVERY_AUTHORIZATION",
        "provider_recovery": "EXECUTE_ONLY_158_ORIGINAL_PROVIDER_TASKS_UNDER_R3B_CONTRACT",
        "post_terminal": "MINT_SINGLE_USE_SUPPORT_READ_AUTHORIZATION_THEN_CONSUME_THROUGH_GUARDED_ONE_SHOT_GATE",
        "stage_b": "SEPARATE_CONTRACT_REVIEW_AND_AUTHORITY_REQUIRED",
    }
    atomic(args.output, out)
    print(json.dumps({
        "status": out["status"],
        "control_plane_revision": out["control_plane_revision"],
        "parent_r3_contract_sha256": psha,
        "output": str(args.output),
        "output_sha256": sha(args.output),
        "provider_calls": 0,
        "scientific_execution": False,
        "stage_b_authority": False,
    }, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
