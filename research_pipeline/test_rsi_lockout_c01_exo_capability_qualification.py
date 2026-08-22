#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "research_pipeline" / "rsi_lockout_c01_exo_capability_qualification.json"


def test_rsi_lockout_exo_w_qualification_stays_zero_authority_and_unprojected() -> None:
    state = json.loads(SPEC.read_text(encoding="utf-8"))
    assert state["candidate_id"] == "RSI-LOCKOUT-C01"
    assert state["status"] == "W_LOCKOUT_ENGINEERING_QUALIFIED_NOVELTY_REDUCTION_GATE_HOLD"
    assert state["identity_binding"]["identity_status"] == "PASS_UNIQUE_IDENTITY_FROZEN"
    assert state["closest_work_binding"]["novelty_authority"] is False
    assert state["closest_work_binding"]["matched_ordinary_tool_control_required"] is True

    substrate = state["substrate"]
    assert substrate["exact_pin"] == "960656626097b3a4ef56f3e4aff3c25573c1623d"
    assert substrate["experimental_profile_commit"] == "ca923c03a9c4dcfe1e0d5c6e8b002c4e3ef86f9a"
    assert substrate["experimental_worktree_only"] is True
    assert state["capability_map"]["W"]["qualified"] is True
    assert state["capability_map"]["R"]["full_class_lockout_qualified"] is False
    assert state["capability_map"]["V"]["full_class_lockout_qualified"] is False

    profile = state["experimental_profile"]
    assert profile["built_in_allowlist"] == ["shell", "inspect_tools"]
    assert profile["registered_allowlist"] == [
        "list_adapter_events",
        "list_conversation_events",
        "rebuild_and_restart_exo",
    ]
    assert set(profile["forbidden_persistent_mutators"]) == {
        "manage_tool",
        "install_agent_tool",
        "uninstall_agent_tool",
        "install_skill",
        "uninstall_skill",
        "snapshot_sandbox",
        "rewind_sandbox",
    }
    assert state["profile_unit_test"]["result"] == "PASS"
    assert (state["profile_unit_test"]["tests_passed"], state["profile_unit_test"]["tests_total"]) == (6, 6)

    dry = state["paired_mount_dry_run"]
    assert dry["checked_host"] == "root@10.42.8.52"
    assert dry["cross_host_evidence"] is True
    assert len(dry["result_sha256"]) == 64
    assert dry["model_calls"] == 0 and dry["gpu_calls"] == 0
    assert dry["results"] == {
        "self_rw_mutating": "7/7",
        "self_ro_mutating": "0/7",
        "ordinary_rw_mutating": "7/7",
        "ordinary_ro_mutating": "0/7",
        "self_after_access_only_restore_mutating": "7/7",
        "ordinary_after_access_only_restore_mutating": "7/7",
    }

    gates = {row["id"]: row["status"] for row in state["promotion_gates"]}
    assert gates == {
        "G0_CANONICAL_SCIENTIFIC_OBJECT_IDENTITY": "PASS",
        "G1_W_CAPABILITY_LEVEL_LOCKOUT": "PASS_ENGINEERING_QUALIFICATION_ONLY",
        "G1B_SAME_INFORMATION_REDUCTION_CONTROL": "DESIGN_FROZEN_NOT_RUN",
        "G2_RECURSIVE_OBJECT_EXTERNAL_SUPERVISION_SEPARATION": "DESIGN_PASS_RUNTIME_PILOT_NOT_RUN",
        "G3_PRINCIPAL_INTERACTION_PILOT": "NOT_RUN",
    }
    assert state["decision"]["overall"] == "HOLD_BEFORE_DYNAMIC_PILOT"
    assert not any(state["authority"].values())
    assert state["decision"]["research_item_promotion"] is False
    assert state["decision"]["paper_state_entry"] is False
    assert state["decision"]["frontend_projection"] is False

    research_items = json.loads((ROOT / "generated" / "research-items.json").read_text(encoding="utf-8"))
    paper_registry = json.loads((ROOT / "generated" / "paper-registry.json").read_text(encoding="utf-8"))
    pre = json.loads((ROOT / "generated" / "pre-researchitem-candidates.json").read_text(encoding="utf-8"))
    assert len(research_items["research_items"]) == 87
    assert len(paper_registry["papers"]) == 5
    assert pre["summary"]["pre_researchitem_candidates"] == 1
    assert [row["candidate_id"] for row in pre["candidates"]] == ["MEMENTO-JOINT-BOUNDARY-CONTROL"]
    assert state["candidate_id"] not in json.dumps(research_items, ensure_ascii=False)
    assert state["candidate_id"] not in json.dumps(paper_registry, ensure_ascii=False)
