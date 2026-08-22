#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "research_pipeline" / "rsi_lockout_c01_matched_reduction_pilot_design.json"


def test_rsi_lockout_matched_reduction_design_is_frozen_zero_authority() -> None:
    state = json.loads(SPEC.read_text(encoding="utf-8"))
    assert state["candidate_id"] == "RSI-LOCKOUT-C01"
    assert state["status"] == "DESIGN_FROZEN_IMPLEMENTATION_AND_AUTHORITY_HOLD"
    assert state["strongest_reduction"]["name"] == "generic persistent tool-failure reachability"
    assert state["strongest_reduction"]["stop_priority"] is True

    assert state["substrate"]["upstream_pin"] == "960656626097b3a4ef56f3e4aff3c25573c1623d"
    assert state["substrate"]["experimental_profile_commit"] == "ca923c03a9c4dcfe1e0d5c6e8b002c4e3ef86f9a"
    assert state["substrate"]["experimental_launcher_commit"] == "ac2b437249d9dbc524d29bd59a1d36874af15fe0"
    assert state["substrate"]["sandbox_scope"] == "conversation"
    assert state["substrate"]["sandbox_networking"] == "disabled"

    assert len(state["frozen_bug_templates"]) == 4
    assert state["replication"]["replicates_per_template"] == 2
    assert state["replication"]["paired_units"] == 8
    assert [arm["id"] for arm in state["arms"]] == [
        "A_RW_NO_FAULT",
        "B_RO_PERSISTENT_LOCKOUT",
        "C_RO_RECREATE_PLACEBO",
        "D_RO_TO_RW_BOUNDED_RESTORE",
    ]
    assert state["episode_protocol"]["turns_per_episode"] == 2
    assert state["episode_protocol"]["turn2_message_identical_across_all_arms_and_target_classes"] is True
    assert state["episode_protocol"]["no_outcome_triggered_restore"] is True
    assert state["verification_and_activation_symmetry"]["status"] == "IMPLEMENTATION_HOLD"

    scope = state["factorial_scope"]
    assert scope["planned_trajectories"] == 64
    assert scope["gpu_required"] is False
    assert scope["provider_calls_required_if_authorized"] is True

    rule = state["decision_rule"]
    assert rule["no_numeric_threshold_tuning"] is True
    assert rule["no_unit_replacement"] is True
    assert rule["no_post_outcome_template_edit"] is True
    assert "same four-arm closure vector" in rule["stop_exact_reduction"]
    assert "at least two distinct bug templates" in rule["advance_provisional"]

    blockers = set(state["pre_run_blockers"])
    assert blockers == {
        "IMPLEMENT_PARAMETERLESS_MATCHED_VALIDATE_AND_ACTIVATE_TARGET",
        "PASS_NO_MODEL_ACTIVATION_SYMMETRY_TEST",
        "PIN_EXACT_MODEL_AND_PROVIDER_BINDING_BEFORE_FIRST_TRAJECTORY",
        "MATERIALIZE_AND_HASH_ALL_8_PAIRED_UNITS_BEFORE_FIRST_TRAJECTORY",
        "VERIFY_CONVERSATION_RECREATE_PLACEBO_AND_RESTORE_SEMANTICS_IN_REAL_EXO_RUNTIME",
        "EXPLICIT_EXPERIMENT_AUTHORITY_REQUIRED",
    }
    assert not any(state["authority"].values())
    assert state["decision"] == "DESIGN_ONLY_NO_EXECUTION_AUTHORITY"

    research_items = json.loads((ROOT / "generated" / "research-items.json").read_text(encoding="utf-8"))
    paper_registry = json.loads((ROOT / "generated" / "paper-registry.json").read_text(encoding="utf-8"))
    pre = json.loads((ROOT / "generated" / "pre-researchitem-candidates.json").read_text(encoding="utf-8"))
    assert len(research_items["research_items"]) == 87
    assert len(paper_registry["papers"]) == 5
    assert [row["candidate_id"] for row in pre["candidates"]] == ["MEMENTO-JOINT-BOUNDARY-CONTROL"]
    assert state["candidate_id"] not in json.dumps(research_items, ensure_ascii=False)
    assert state["candidate_id"] not in json.dumps(paper_registry, ensure_ascii=False)
