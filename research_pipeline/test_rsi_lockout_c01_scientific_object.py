#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "research_pipeline" / "rsi_lockout_c01_scientific_object.json"


def test_rsi_lockout_has_unique_zero_authority_identity() -> None:
    state = json.loads(SPEC.read_text(encoding="utf-8"))
    assert state["candidate_id"] == "RSI-LOCKOUT-C01"
    assert state["status"] == "CANONICAL_SCIENTIFIC_OBJECT_IDENTITY_FROZEN_ZERO_AUTHORITY"
    assert state["canonical_object_qualification"]["status"] == "PASS_UNIQUE_IDENTITY_FROZEN"
    assert state["lineage"]["conflicting_canonical_id"] == "SHADOW-RSI-C01"
    assert state["lineage"]["identity_relation"] == "DISTINCT_SCIENTIFIC_OBJECT_NO_AUTHORITY_INHERITANCE"
    assert state["scientific_object"]["fault_object"].startswith("a complete functional-equivalence class")
    assert state["next_gate"]["name"] == "STRICT_CLOSEST_WORK_AND_SAME_INFORMATION_REDUCTION"
    assert state["next_gate"]["execution_authorized"] is False
    assert not any(state["authority"].values())
    assert not any(state["projection_policy"].values())

    q = state["canonical_object_qualification"]
    contract = Path(q["contract_path"])
    receipt = Path(q["receipt_path"])
    assert contract.exists() and receipt.exists()
    assert hashlib.sha256(contract.read_bytes()).hexdigest() == q["contract_sha256"]
    assert hashlib.sha256(receipt.read_bytes()).hexdigest() == q["receipt_sha256"]
    canonical = json.loads(contract.read_text(encoding="utf-8"))
    assert canonical["candidate_id"] == state["candidate_id"]
    assert canonical["scientific_object"] == state["scientific_object"]

    research_items = json.loads((ROOT / "generated" / "research-items.json").read_text(encoding="utf-8"))
    paper_registry = json.loads((ROOT / "generated" / "paper-registry.json").read_text(encoding="utf-8"))
    assert state["candidate_id"] not in json.dumps(research_items, ensure_ascii=False)
    assert state["candidate_id"] not in json.dumps(paper_registry, ensure_ascii=False)
    assert state["candidate_id"] not in (ROOT / "paper-ideas.html").read_text(encoding="utf-8")
    assert state["candidate_id"] not in (ROOT / "app.js").read_text(encoding="utf-8")
