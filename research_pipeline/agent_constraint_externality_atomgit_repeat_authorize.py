from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline import agent_constraint_externality_atomgit_repeat_common as c
from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value

ROOT = Path(__file__).resolve().parents[1]
G = ROOT / "generated"
READINESS = G / "agent-constraint-externality-atomgit-repeat-r2-readiness-20260906.json"
PREFLIGHT = G / "agent-constraint-externality-atomgit-repeat-r2-preflight-20260906.json"
RUNNER = ROOT / "research_pipeline/agent_constraint_externality_atomgit_repeat_execute.py"
BRIDGE = ROOT / "research_pipeline/agent_constraint_externality_atomgit_repeat_mcp_bridge.py"
COMMON = ROOT / "research_pipeline/agent_constraint_externality_atomgit_repeat_common.py"
ADJUDICATOR = ROOT / "research_pipeline/agent_constraint_externality_atomgit_repeat_adjudicate.py"


class AuthorizeError(RuntimeError):
    pass


def readj(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verified(path: Path, status: str) -> dict[str, Any]:
    payload = readj(path)
    if payload.get("object_id") != OBJECT_ID or payload.get("status") != status:
        raise AuthorizeError(f"identity/status mismatch: {path}")
    claimed = payload.get("content_sha256")
    unsigned = dict(payload); unsigned.pop("content_sha256", None)
    if claimed != sha256_value(unsigned):
        raise AuthorizeError(f"content hash mismatch: {path}")
    return payload


def writej(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    if c.AUTH.exists() or c.CONTRACT.exists():
        raise AuthorizeError("repeat authority/contract already exists")
    readiness = verified(READINESS, "ATOMGIT_REPEAT_DEV_R2_ZERO_PROVIDER_READY_AWAITING_SEPARATE_HUMAN_AUTHORITY")
    preflight = verified(PREFLIGHT, "ATOMGIT_REPEAT_DEV_R2_PREFLIGHT_PASS_AUTHORITY_CLOSED")
    close, manifest, freeze = c.parents()
    if readiness["repair_closeout_content_sha256"] != close["content_sha256"]:
        raise AuthorizeError("repair closeout binding drift")
    if readiness["repair_manifest_content_sha256"] != manifest["content_sha256"]:
        raise AuthorizeError("repair manifest binding drift")
    if readiness["preexec_freeze_content_sha256"] != freeze["content_sha256"]:
        raise AuthorizeError("preexec freeze binding drift")
    if readiness["runner_sha256"] != sha256_file(RUNNER):
        raise AuthorizeError("runner SHA drift")
    if readiness["bridge_sha256"] != sha256_file(BRIDGE):
        raise AuthorizeError("bridge SHA drift")
    if readiness["common_sha256"] != sha256_file(COMMON):
        raise AuthorizeError("common SHA drift")
    if readiness["r2_panel"]["episode_count"] != 72 or readiness["r2_panel"]["condition_cell_count"] != 36:
        raise AuthorizeError("R2 panel geometry drift")
    if readiness["q1_model_requests"] != 0 or preflight["q1_model_requests"] != 0:
        raise AuthorizeError("predispatch Q1 consumed model requests")
    if any(readiness["authority"].values()) or any(preflight["authority"].values()):
        raise AuthorizeError("readiness/preflight authority must remain closed")

    authority: dict[str, Any] = {
        "schema_version": "ace-repeat-dev-r2-human-authorization-v1",
        "object_id": OBJECT_ID,
        "status": "USER_AUTHORIZED_ATOMGIT_REPEAT_DEV_R2_ONLY",
        "authorized_at": "2026-09-06T22:34:00+08:00",
        "authorization_source": "CURRENT_SESSION_USER_MESSAGE_CONTINUE_AFTER_R2_ZERO_PROVIDER_READINESS",
        "scope": "Exactly the frozen 72-episode development-only R*=2 repeat-qualification panel: 6 families x 3 topology arms x 2 branches x 2 repeats. No TARGET_ONLY_VERIFICATION or confirmatory RQ authority.",
        "readiness_content_sha256": readiness["content_sha256"],
        "preflight_content_sha256": preflight["content_sha256"],
        "repair_closeout_content_sha256": close["content_sha256"],
        "repair_manifest_content_sha256": manifest["content_sha256"],
        "preexec_freeze_content_sha256": freeze["content_sha256"],
        "authority": {
            "development_repeat_qualification": True,
            "target_only_verification": False,
            "rq1_rq2": False,
            "rq3": False,
            "rq4": False,
            "paper_claim": False,
        },
        "scientific_externality_claim_authority": False,
    }
    authority["content_sha256"] = sha256_value(authority)

    contract: dict[str, Any] = {
        "schema_version": "ace-repeat-dev-r2-execution-contract-v1",
        "object_id": OBJECT_ID,
        "execution_id": c.EXECUTION_ID,
        "status": "ATOMGIT_REPEAT_DEV_R2_EXECUTION_AUTHORIZED",
        "human_authorization_content_sha256": authority["content_sha256"],
        "readiness_content_sha256": readiness["content_sha256"],
        "preflight_content_sha256": preflight["content_sha256"],
        "repair_closeout_content_sha256": close["content_sha256"],
        "repair_manifest_content_sha256": manifest["content_sha256"],
        "preexec_freeze_content_sha256": freeze["content_sha256"],
        "model": {"provider": c.PROVIDER, "profile": c.MODEL_PROFILE, "id": c.MODEL_ID},
        "panel": {
            "family_ids": readiness["family_ids"],
            "arms": readiness["r2_panel"]["arms"],
            "branches": readiness["r2_panel"]["branches"],
            "repeats": readiness["r2_panel"]["repeats"],
            "repeat_seeds": readiness["r2_panel"]["repeat_seeds"],
            "episode_count": 72,
            "condition_cell_count": 36,
            "unit_ids_sha256": readiness["r2_panel"]["unit_ids_sha256"],
            "branch_order_salt": readiness["r2_panel"]["branch_order_salt"],
        },
        "execution_policy": {
            "exactly_once": True,
            "retry_after_dispatch": False,
            "replacement": False,
            "pair_start_min_remaining": c.MIN_REMAINING_PAIR,
            "unit_start_min_remaining": c.MIN_REMAINING_UNIT,
            "pre_dispatch_quota_hold_resumable": True,
            "full_panel_may_span_quota_windows": True,
            "pair_scientific_state_sha_must_match": True,
            "real_repair_exact_frozen_bytes": True,
            "no_update_no_repair": True,
            "crr_definition": "newly failed initially-satisfied non-target constraints divided by 2",
        },
        # Duplicate the three fields below at top level because the already-frozen
        # executor consumes this minimal legacy binding interface. runtime_bindings
        # remains the richer audit record.
        "runner_sha256": sha256_file(RUNNER),
        "bridge_sha256": sha256_file(BRIDGE),
        "unit_ids_sha256": readiness["r2_panel"]["unit_ids_sha256"],
        "runtime_bindings": {
            "runner_sha256": sha256_file(RUNNER),
            "bridge_sha256": sha256_file(BRIDGE),
            "common_sha256": sha256_file(COMMON),
            "adjudicator_sha256": sha256_file(ADJUDICATOR),
            "reserve_bundle_sha256": readiness["reserve_bundle_sha256"],
        },
        "analysis_policy": {
            "direction_blind_repeat_decision_only": True,
            "R2_pass_thresholds": {"target_disagreement_rate_max": 0.10, "mean_absolute_crr_repeat_difference_max": 0.10},
            "R3_trigger_ceiling": 0.20,
            "R_gt_3_forbidden": True,
            "effect_mean_or_sign_not_used_for_repeat_count": True,
            "target_only_verification_opens_automatically": False,
            "rq1_rq2_opens_automatically": False,
        },
        "authority": authority["authority"],
        "scientific_externality_claim_authority": False,
    }
    contract["content_sha256"] = sha256_value(contract)
    return authority, contract


def main() -> None:
    authority, contract = build()
    writej(c.AUTH, authority); writej(c.CONTRACT, contract)
    print(json.dumps({
        "authorization": authority["status"],
        "contract": contract["status"],
        "episode_count": contract["panel"]["episode_count"],
        "authority": authority["authority"],
        "scientific_externality_claim_authority": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
