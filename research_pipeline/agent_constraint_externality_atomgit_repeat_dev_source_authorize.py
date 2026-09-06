from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_atomgit_repeat_dev_build import (
    CONTRACT_OUTPUT as STATIC_CONTRACT,
    OUTPUT_BUNDLE,
    QUAL_OUTPUT as STATIC_QUAL,
    load_dev_spec,
)
from research_pipeline.agent_constraint_externality_atomgit_repeat_dev_source import (
    AUTH_OUTPUT,
    BRIDGE,
    EXEC_CONTRACT,
    MIN_REMAINING,
    MODEL_ID,
    MODEL_PROFILE,
    MODEL_ROUND_CAP,
    PROVIDER,
    Q1_OUTPUT,
    PREFLIGHT_OUTPUT,
    RUN_ROOT,
    TOOL_CALL_CAP,
)
from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
SOURCE_RUNNER = ROOT / "research_pipeline/agent_constraint_externality_atomgit_repeat_dev_source.py"
REVIEW = GENERATED / "agent-constraint-externality-atomgit-repeat-dev-source-exact-review-20260906.json"
G1_CLOSEOUT = ROOT / "consultations/agent-safety-g1-atomgit-q0-r3-closeout-20260906.md"
EXPECTED_REVIEW_STATUS = "ATOMGIT_REPEAT_DEV_SOURCE_EXACT_REVIEW_PASS_2_OF_2"


class AuthorizeStop(RuntimeError):
    pass


def readj(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verified(path: Path, status: str) -> dict[str, Any]:
    payload = readj(path)
    if payload.get("object_id") != OBJECT_ID or payload.get("status") != status:
        raise AuthorizeStop(f"identity/status mismatch: {path}")
    claimed = payload.get("content_sha256")
    if claimed:
        unsigned = dict(payload); unsigned.pop("content_sha256", None)
        if claimed != sha256_value(unsigned):
            raise AuthorizeStop(f"content hash mismatch: {path}")
    return payload


def freeze() -> tuple[dict[str, Any], dict[str, Any]]:
    if AUTH_OUTPUT.exists() or EXEC_CONTRACT.exists():
        raise AuthorizeStop("source authority already exists")
    if RUN_ROOT.exists():
        raise AuthorizeStop("source run root already exists before authority")
    static = verified(STATIC_CONTRACT, "ATOMGIT_REPEAT_DEV_STATIC_DESIGN_READY_ZERO_PROVIDER")
    qual = verified(STATIC_QUAL, "ATOMGIT_REPEAT_DEV_STATIC_QUALIFICATION_PASS_EXECUTION_CLOSED")
    q1 = verified(Q1_OUTPUT, "ATOMGIT_REPEAT_DEV_SOURCE_MCP_PREDISPATCH_PASS")
    preflight = verified(PREFLIGHT_OUTPUT, "ATOMGIT_REPEAT_DEV_SOURCE_PREFLIGHT_PASS_AUTHORITY_CLOSED")
    review = verified(REVIEW, EXPECTED_REVIEW_STATUS)
    if q1.get("codingplan_model_requests") != 0 or preflight.get("provider_requests_created") != 0:
        raise AuthorizeStop("pre-dispatch model-request boundary crossed")
    if review.get("must_fix") != [] or review.get("runner_sha256") != sha256_file(SOURCE_RUNNER) or review.get("bridge_sha256") != sha256_file(BRIDGE):
        raise AuthorizeStop("source runner exact-review binding drift")
    if static["protected_bundle"]["sha256"] != sha256_file(OUTPUT_BUNDLE) or qual["protected_bundle_sha256"] != sha256_file(OUTPUT_BUNDLE):
        raise AuthorizeStop("protected bundle binding drift")
    families = load_dev_spec()["families"]
    family_ids = [row["family_id"] for row in families]
    if len(family_ids) != 6 or len(set(family_ids)) != 6:
        raise AuthorizeStop("source family geometry drift")
    if not G1_CLOSEOUT.is_file():
        raise AuthorizeStop("G1 shared-quota release closeout missing")

    authority: dict[str, Any] = {
        "schema_version": "ace-repeat-dev-source-human-authorization-v1",
        "object_id": OBJECT_ID,
        "status": "USER_AUTHORIZED_ATOMGIT_REPEAT_DEV_SIX_SOURCE_ONLY",
        "authorization_basis": "User message '继续' at 2026-09-06 17:05+08:00 after host69 recovery, following the instruction to continue AtomGit experimental work while sharing the rolling quota with the other paper.",
        "scope": "Exactly one new target-only source episode for each of the six frozen development families. No retry, replacement, top-up, repair generation, topology execution, TO-V, RQ1/RQ2, RQ3, RQ4, or paper claim authority.",
        "family_ids": family_ids,
        "static_contract_content_sha256": static["content_sha256"],
        "static_qualification_content_sha256": qual["content_sha256"],
        "source_preflight_content_sha256": preflight["content_sha256"],
        "source_q1_content_sha256": q1["content_sha256"],
        "source_exact_review_content_sha256": review["content_sha256"],
        "g1_quota_release_closeout_sha256": sha256_file(G1_CLOSEOUT),
        "authority": {
            "source_execution": True,
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

    contract: dict[str, Any] = {
        "schema_version": "ace-repeat-dev-source-execution-contract-v1",
        "object_id": OBJECT_ID,
        "status": "ATOMGIT_REPEAT_DEV_SIX_SOURCE_EXECUTION_AUTHORIZED",
        "execution_id": "ACE-ATOMGIT-REPEAT-DEV-SOURCE-20260906",
        "human_authorization_content_sha256": authority["content_sha256"],
        "source_exact_review_content_sha256": review["content_sha256"],
        "source_preflight_content_sha256": preflight["content_sha256"],
        "source_q1_content_sha256": q1["content_sha256"],
        "static_contract_content_sha256": static["content_sha256"],
        "static_qualification_content_sha256": qual["content_sha256"],
        "protected_bundle_sha256": sha256_file(OUTPUT_BUNDLE),
        "runner_sha256": sha256_file(SOURCE_RUNNER),
        "bridge_sha256": sha256_file(BRIDGE),
        "authorizer_sha256": sha256_file(Path(__file__)),
        "model": {"provider": PROVIDER, "profile": MODEL_PROFILE, "id": MODEL_ID},
        "panel": {
            "family_ids": family_ids,
            "source_count": 6,
            "one_episode_per_family": True,
            "all_six_must_be_semantic_target_failures": True,
            "first_target_success_stops_without_replacement": True,
            "confirmatory_reuse": False,
        },
        "harness": {
            "id": "ATOMCODE_CODINGPLAN_MCP_V1",
            "tool_call_cap": TOOL_CALL_CAP,
            "model_round_cap_per_source": MODEL_ROUND_CAP,
            "minimum_rolling_window_remaining_before_dispatch": MIN_REMAINING,
            "durable_source_dispatch_before_model_request": True,
            "durable_tool_dispatch_before_appworld_tool_execution": True,
            "tool_completion_required_before_repair_eligibility": True,
            "retry_allowed": False,
            "replacement_allowed": False,
            "top_up_allowed": False,
        },
        "quota": {
            "rolling_window_limit": 500,
            "g1_reserved_requests": 0,
            "g1_release_bound_by_closeout_sha256": sha256_file(G1_CLOSEOUT),
            "pre_dispatch_quota_hold_is_resumable": True,
            "post_dispatch_retry_is_forbidden": True,
        },
        "execution_policy": {
            "source_only": True,
            "repair_generation": False,
            "topology_execution": False,
            "partial_source_outcomes_cannot_change_family_order_or_replace_units": True,
            "target_success_is_terminal_support_failure_for_this_six-family development set": True,
        },
        "authority": authority["authority"],
        "scientific_topology_outcomes_observed": 0,
    }
    contract["content_sha256"] = sha256_value(contract)
    return authority, contract


def main() -> None:
    authority, contract = freeze()
    AUTH_OUTPUT.write_text(json.dumps(authority, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    EXEC_CONTRACT.write_text(json.dumps(contract, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "authorization": authority["status"],
        "contract": contract["status"],
        "source_count": 6,
        "repair_generation_authorized": False,
        "topology_execution_authorized": False,
        "provider_requests_created": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
