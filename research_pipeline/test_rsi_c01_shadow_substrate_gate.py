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
    assert state["status"] == "HOLD_SUBSTRATE_NOT_YET_QUALIFIED"
    assert state["scientific_object"]["broad_claim_status"] == "NOVELTY_FAIL"
    assert state["scientific_object"]["narrow_claim_status"] == "PASS_PROVISIONAL_CLOSEST_WORK_ONLY"
    assert state["substrate"]["qualification"] == "PARTIAL_W_BOUNDARY_FEASIBILITY_ONLY"
    assert state["dry_run"]["results"]["rw_equivalent_write_paths_mutating"] == 7
    assert state["dry_run"]["results"]["ro_equivalent_write_paths_mutating"] == 0
    assert state["dry_run"]["results"]["same_owner_mode_bits_bypassed"] is True
    assert state["dry_run"]["results"]["full_rwv_lockout_qualified"] is False
    assert [row["status"] for row in state["promotion_gates"]] == ["PARTIAL_W_ONLY", "PENDING", "PENDING"]
    assert not any(state["authority"].values())
    assert not any(state["projection_policy"][key] for key in ("generated_frontend", "research_item", "paper_state", "canonical_consumer_surface"))

    research_items = json.loads((ROOT / "generated" / "research-items.json").read_text(encoding="utf-8"))
    paper_registry = json.loads((ROOT / "generated" / "paper-registry.json").read_text(encoding="utf-8"))
    assert "RSI-C01" not in json.dumps(research_items, ensure_ascii=False)
    assert "RSI-C01" not in json.dumps(paper_registry, ensure_ascii=False)
    assert "RSI-C01" not in (ROOT / "paper-ideas.html").read_text(encoding="utf-8")
    assert "RSI-C01" not in (ROOT / "app.js").read_text(encoding="utf-8")
