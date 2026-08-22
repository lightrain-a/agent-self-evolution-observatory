#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "research_pipeline" / "rsi_c01_shadow_substrate_gate.json"


def test_rsi_c01_is_terminal_historical_alias_for_rsi_lockout() -> None:
    state = json.loads(SPEC.read_text(encoding="utf-8"))
    assert state["schema_version"] == "1.2"
    assert state["candidate_id"] == "RSI-C01"
    assert state["portfolio_class"] == "HISTORICAL_SHADOW_ALIAS_SUPERSEDED_NOT_PROJECTED"
    assert state["status"] == "SUPERSEDED_BY_RSI_LOCKOUT_C01"
    assert state["scientific_object"]["broad_claim_status"] == "NOVELTY_FAIL"
    assert state["scientific_object"]["narrow_claim_status"] == "REBIND_COMPLETE_AS_DISTINCT_ZERO_AUTHORITY_OBJECT"
    assert state["scientific_object"]["promotion_status"] == "MOVED_TO_RSI_LOCKOUT_C01_ZERO_AUTHORITY"

    identity = state["canonical_object_qualification"]
    assert identity["status"] == "RESOLVED_BY_DISTINCT_CANDIDATE_ID"
    assert identity["identity_match"] is False
    assert identity["current_object_found_in_canonical_data_root"] is True
    assert identity["resolved_candidate_id"] == "RSI-LOCKOUT-C01"
    assert identity["resolved_contract_sha256"] == "6b123f5a092b594500d7dd554f69bd20e62032f92dde6f9913229b1a8aba30d2"
    assert identity["canonical_candidate_with_conflicting_identity"]["candidate_id"] == "SHADOW-RSI-C01"
    assert identity["canonical_candidate_with_conflicting_identity"]["terminal_status"] == "STOP_EXACT_REDUCTION_SUPPORTED"

    closest = state["closest_work_boundary"]
    assert closest["decision"] == "MOVED_TO_RSI_LOCKOUT_C01"
    assert closest["strict_closest_work_completed"] is True
    assert closest["same_information_reduction_completed"] is True
    assert closest["novelty_authority"] is False
    assert closest["resolved_review_sha256"] == "b98d42e14eb9a8e0c55c9d7c9890e0afc26357b1c169b6cf721348fdeb75f38f"

    assert state["substrate"]["qualification"] == "MOVED_TO_RSI_LOCKOUT_C01_W_ENGINEERING_QUALIFIED"
    assert state["substrate"]["same_substrate_qualification"] == "MOVED_TO_RSI_LOCKOUT_C01"
    assert state["substrate"]["source_scan"]["exact_main_sha"] == "960656626097b3a4ef56f3e4aff3c25573c1623d"
    assert state["dry_run"]["results"]["rw_equivalent_write_paths_mutating"] == 7
    assert state["dry_run"]["results"]["ro_equivalent_write_paths_mutating"] == 0
    assert state["dry_run"]["results"]["full_rwv_lockout_qualified"] is False

    assert [row["status"] for row in state["promotion_gates"]] == [
        "RESOLVED_BY_SUPERSESSION",
        "MOVED_TO_RSI_LOCKOUT_C01",
        "MOVED_TO_RSI_LOCKOUT_C01",
        "MOVED_TO_RSI_LOCKOUT_C01",
    ]
    assert state["next_gate"]["name"] == "NONE_HISTORICAL_ALIAS_TERMINAL"
    assert state["next_gate"]["successor_candidate_id"] == "RSI-LOCKOUT-C01"
    assert state["next_gate"]["execution_authorized"] is False
    assert not any(state["authority"].values())
    assert not any(
        state["projection_policy"][key]
        for key in ("generated_frontend", "research_item", "paper_state", "canonical_consumer_surface")
    )

    research_items = json.loads((ROOT / "generated" / "research-items.json").read_text(encoding="utf-8"))
    paper_registry = json.loads((ROOT / "generated" / "paper-registry.json").read_text(encoding="utf-8"))
    assert "RSI-C01" not in json.dumps(research_items, ensure_ascii=False)
    assert "RSI-C01" not in json.dumps(paper_registry, ensure_ascii=False)
    assert "RSI-C01" not in (ROOT / "paper-ideas.html").read_text(encoding="utf-8")
    assert "RSI-C01" not in (ROOT / "app.js").read_text(encoding="utf-8")
