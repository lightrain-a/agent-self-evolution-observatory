#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "research_pipeline" / "rsi_c01_shadow_substrate_gate.json"


def test_rsi_c01_remains_shadow_hold_and_unprojected() -> None:
    state = json.loads(SPEC.read_text(encoding="utf-8"))
    assert state["candidate_id"] == "RSI-C01"
    assert state["portfolio_class"] == "SHADOW_HOLD_NOT_PROJECTED"
    assert state["status"] == "HOLD_CANONICAL_SCIENTIFIC_OBJECT_IDENTITY_MISMATCH"
    assert state["scientific_object"]["broad_claim_status"] == "NOVELTY_FAIL"
    assert state["scientific_object"]["narrow_claim_status"] == "UNQUALIFIED_SHADOW_OBJECT_NO_CANONICAL_MATCH"
    identity = state["canonical_object_qualification"]
    assert identity["status"] == "FAIL_OBJECT_IDENTITY_MISMATCH"
    assert identity["identity_match"] is False
    assert identity["current_object_found_in_canonical_data_root"] is False
    assert identity["canonical_candidate_with_conflicting_identity"]["candidate_id"] == "SHADOW-RSI-C01"
    assert identity["canonical_candidate_with_conflicting_identity"]["terminal_status"] == "STOP_EXACT_REDUCTION_SUPPORTED"
    assert state["closest_work_boundary"]["decision"] == "NOT_RUN_CANONICAL_OBJECT_IDENTITY_MISMATCH"
    assert state["closest_work_boundary"]["strict_closest_work_completed"] is False
    assert state["substrate"]["qualification"] == "ENGINEERING_FEASIBILITY_ONLY_NOT_SCIENTIFICALLY_QUALIFIED"
    assert state["substrate"]["same_substrate_qualification"] == "NOT_RUN_CANONICAL_OBJECT_IDENTITY_MISMATCH"
    assert state["dry_run"]["results"]["rw_equivalent_write_paths_mutating"] == 7
    assert state["dry_run"]["results"]["ro_equivalent_write_paths_mutating"] == 0
    assert state["dry_run"]["results"]["same_owner_mode_bits_bypassed"] is True
    assert state["dry_run"]["results"]["full_rwv_lockout_qualified"] is False
    assert [row["status"] for row in state["promotion_gates"]] == ["FAIL_OBJECT_IDENTITY_MISMATCH", "ENGINEERING_PARTIAL_W_ONLY_BLOCKED_BY_G0", "BLOCKED_BY_G0", "BLOCKED_BY_G0"]
    assert state["next_gate"]["name"] == "CANONICAL_OBJECT_REBIND_OR_DISTINCT_CANDIDATE_ID"
    assert state["next_gate"]["execution_authorized"] is False
    assert not any(state["authority"].values())
    assert not any(state["projection_policy"][key] for key in ("generated_frontend", "research_item", "paper_state", "canonical_consumer_surface"))

    research_items = json.loads((ROOT / "generated" / "research-items.json").read_text(encoding="utf-8"))
    paper_registry = json.loads((ROOT / "generated" / "paper-registry.json").read_text(encoding="utf-8"))
    assert "RSI-C01" not in json.dumps(research_items, ensure_ascii=False)
    assert "RSI-C01" not in json.dumps(paper_registry, ensure_ascii=False)
    assert "RSI-C01" not in (ROOT / "paper-ideas.html").read_text(encoding="utf-8")
    assert "RSI-C01" not in (ROOT / "app.js").read_text(encoding="utf-8")
