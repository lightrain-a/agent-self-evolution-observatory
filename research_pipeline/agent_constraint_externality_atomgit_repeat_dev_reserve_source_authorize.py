from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from research_pipeline import agent_constraint_externality_atomgit_repeat_dev_reserve_source_common as c
from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value

AUTHORIZATION_TIME = "2026-09-06T19:05:00+08:00"
AUTHORIZATION_BASIS = (
    "Current-session user message '继续' at 2026-09-06 19:05+08:00, continuing the already-directed AtomGit "
    "Constraint experiment. After discovering the old fixed-six source authority had already terminated, the continuation "
    "was narrowed to the repaired pre-topology reserve source-acquisition stage only."
)


class AuthorizeError(RuntimeError):
    pass


def git_head() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()


def require_clean() -> None:
    status = subprocess.run(["git", "status", "--porcelain"], check=True, capture_output=True, text=True).stdout.strip()
    if status:
        raise AuthorizeError("authorization requires a clean committed readiness checkpoint")


def freeze() -> tuple[dict[str, Any], dict[str, Any]]:
    require_clean()
    if c.AUTH_OUTPUT.exists() or c.EXEC_CONTRACT.exists():
        raise AuthorizeError("reserve source authority already exists")
    readiness = c.verified(c.READINESS_OUTPUT, "ATOMGIT_REPEAT_DEV_RESERVE_SOURCE_READY_AWAITING_SEPARATE_HUMAN_AUTHORITY")
    preflight = c.verified(c.PREFLIGHT_OUTPUT, "ATOMGIT_REPEAT_DEV_RESERVE_SOURCE_PREFLIGHT_PASS_AUTHORITY_CLOSED")
    q1 = c.verified(c.Q1_OUTPUT, "ATOMGIT_REPEAT_DEV_RESERVE_SOURCE_MCP_PREDISPATCH_PASS")
    reserve = c.reserve_contract()
    if readiness["preflight_content_sha256"] != preflight["content_sha256"]:
        raise AuthorizeError("readiness/preflight binding drift")
    if preflight["q1_content_sha256"] != q1["content_sha256"]:
        raise AuthorizeError("preflight/Q1 binding drift")
    if readiness["bundle_sha256"] != sha256_file(c.OUTPUT_BUNDLE):
        raise AuthorizeError("bundle binding drift")
    if readiness["executor_sha256"] != sha256_file(c.ROOT / "research_pipeline/agent_constraint_externality_atomgit_repeat_dev_reserve_source.py"):
        raise AuthorizeError("executor binding drift")
    if readiness["common_sha256"] != sha256_file(Path(c.__file__)) or readiness["bridge_sha256"] != sha256_file(c.BRIDGE):
        raise AuthorizeError("common/bridge binding drift")

    authority: dict[str, Any] = {
        "schema_version": "ace-repeat-dev-reserve-source-human-authorization-v1",
        "object_id": OBJECT_ID,
        "status": "USER_AUTHORIZED_ATOMGIT_REPEAT_DEV_RESERVE_SOURCE_ONLY",
        "authorized_at": AUTHORIZATION_TIME,
        "authorization_basis": AUTHORIZATION_BASIS,
        "scope": "Only fresh target-only source acquisition inside the frozen 8-FG + 8-TNF development reserve until the first 3 semantic target failures per category are frozen, or a frozen stop/hold occurs.",
        "readiness_content_sha256": readiness["content_sha256"],
        "preflight_content_sha256": preflight["content_sha256"],
        "q1_content_sha256": q1["content_sha256"],
        "reserve_contract_content_sha256": reserve["content_sha256"],
        "authority": {
            "reserve_source_execution": True,
            "repair_generation": False,
            "development_repeat_qualification": False,
            "target_only_verification": False,
            "rq1_rq2": False,
            "rq3": False,
            "rq4": False,
            "paper_claim": False,
        },
        "scientific_topology_outcomes_observed": 0,
    }
    authority["content_sha256"] = sha256_value(authority)
    c.writej(c.AUTH_OUTPUT, authority)

    contract: dict[str, Any] = {
        "schema_version": "ace-repeat-dev-reserve-source-execution-contract-v1",
        "object_id": OBJECT_ID,
        "execution_id": c.EXECUTION_ID,
        "status": "ATOMGIT_REPEAT_DEV_RESERVE_SOURCE_EXECUTION_AUTHORIZED",
        "code_parent_git_sha": git_head(),
        "human_authorization_content_sha256": authority["content_sha256"],
        "readiness_content_sha256": readiness["content_sha256"],
        "preflight_content_sha256": preflight["content_sha256"],
        "q1_content_sha256": q1["content_sha256"],
        "protected_bundle_sha256": sha256_file(c.OUTPUT_BUNDLE),
        "executor_sha256": readiness["executor_sha256"],
        "common_sha256": readiness["common_sha256"],
        "bridge_sha256": readiness["bridge_sha256"],
        "model": {"provider": c.PROVIDER, "profile": c.MODEL_PROFILE, "id": c.MODEL_ID},
        "ranked_family_ids": c.ranked_ids(),
        "selection": {
            "needed_per_category": 3,
            "target_success": "pre-topology eligibility attrition; continue within frozen reserve",
            "semantic_failure": "eligible; select first three per category",
            "technical_invalidity_after_dispatch": "hard stop no replay no skip",
            "maximum_source_dispatches": 16,
            "outside_reserve_replacement": False,
        },
        "harness": {
            "id": "ATOMCODE_CODINGPLAN_MCP_V1",
            "model_round_cap_per_source": c.MODEL_ROUND_CAP,
            "tool_call_cap": c.TOOL_CALL_CAP,
            "durable_source_dispatch_before_model_request": True,
            "durable_tool_dispatch_before_appworld_tool_execution": True,
            "retry_allowed": False,
            "replacement_allowed": False,
        },
        "quota": {
            "rolling_window_limit": 500,
            "shared_reserve": c.SHARED_RESERVE,
            "minimum_remaining_before_each_dispatch": c.MIN_REMAINING,
            "pre_dispatch_hold_resumable": True,
            "post_dispatch_retry_allowed": False,
        },
        "authority": authority["authority"],
        "scientific_topology_outcomes_observed": 0,
    }
    contract["content_sha256"] = sha256_value(contract)
    c.writej(c.EXEC_CONTRACT, contract)
    return authority, contract


def main() -> None:
    authority, contract = freeze()
    print(json.dumps({
        "authorization": authority["status"],
        "contract": contract["status"],
        "code_parent_git_sha": contract["code_parent_git_sha"],
        "reserve_source_execution": True,
        "repair_generation": False,
        "development_repeat_qualification": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
