from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .pilot_registry import build_pilot_registry, validate_result
from .pre_p0_identifiability import CHECKS, audit_contract


PHASES = [{"id": p, "title": {"en": p}, "setup": {"en": "setup"}, "gate": {"en": "gate"}} for p in ("P0", "P1", "P2")]


def idea(idea_id: str) -> dict:
    return {"id": idea_id, "title": {"en": idea_id}, "rank": 1, "experiment_protocol": {"phases": PHASES}}


def passing_pre_p0(idea_id: str) -> dict:
    node = audit_contract(idea_id, {"code":"X","checks":{row["key"]:True for row in CHECKS}})
    return {"schema_version":"1.0","policy":{"p0_execution_requires_pre_p0_pass":True},"summary":{"audited":1,"execution_ready":1,"blocked":0},"nodes":[node]}


def p0_result(idea_id: str, next_action: str = "await-human-approval") -> dict:
    return {
        "schema_version": "1.0", "idea_id": idea_id, "phase": "P0", "result": "pass",
        "code_commit": "abc", "config_hash": "cfg", "datasets": ["ALFWorld"], "models": ["Qwen"],
        "seeds": [1], "metrics": {}, "cost": {}, "diagnosis": "ok", "next_action": next_action,
        "completed_at": "2026-08-09T00:00:00Z",
    }


class PilotRegistryGateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.bank = {"passed_ideas": [
            idea("update-trust-region"),
            idea("outcome-equivalent-trajectory-contrast"),
            idea("regression-gated-self-evolution"),
        ]}

    def test_only_current_ready_p0_is_authorized(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            registry = build_pilot_registry(self.bank, result_dir=root / "results", approval_dir=root / "approvals", pre_p0_audit=passing_pre_p0("update-trust-region"))
        by_id = {row["idea_id"]: row for row in registry["ideas"]}
        self.assertEqual(registry["summary"]["p0_authorized"], 1)
        self.assertEqual(by_id["update-trust-region"]["next_phase"], "P0")
        self.assertIsNone(by_id["outcome-equivalent-trajectory-contrast"]["next_phase"])
        self.assertEqual(by_id["outcome-equivalent-trajectory-contrast"]["p0_gate_status"], "method-redesign")
        self.assertEqual(by_id["regression-gated-self-evolution"]["p0_gate_status"], "not-current-p0-candidate")

    def test_p0_pass_waits_for_explicit_human_approval(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); (root / "results").mkdir()
            (root / "results" / "p0.json").write_text(json.dumps(p0_result("update-trust-region")), encoding="utf-8")
            registry = build_pilot_registry(self.bank, result_dir=root / "results", approval_dir=root / "approvals", pre_p0_audit=passing_pre_p0("update-trust-region"))
            row = next(x for x in registry["ideas"] if x["idea_id"] == "update-trust-region")
            self.assertEqual(row["state"], "awaiting-human-approval")
            self.assertIsNone(row["next_phase"])
            self.assertEqual(row["next_action"], "await-human-approval")
            self.assertEqual(registry["summary"]["p1_authorized"], 0)

            (root / "approvals").mkdir()
            (root / "approvals" / "approve.json").write_text(json.dumps({
                "idea_id": "update-trust-region", "after_phase": "P0", "decision": "approve",
                "reviewed_by": "human", "reviewed_at": "2026-08-09T01:00:00Z", "rationale": "approved",
            }), encoding="utf-8")
            registry = build_pilot_registry(self.bank, result_dir=root / "results", approval_dir=root / "approvals", pre_p0_audit=passing_pre_p0("update-trust-region"))
            row = next(x for x in registry["ideas"] if x["idea_id"] == "update-trust-region")
            self.assertEqual(row["next_phase"], "P1")
            self.assertEqual(registry["summary"]["p1_authorized"], 1)

    def test_p0_result_cannot_request_p1_directly(self) -> None:
        self.assertIn("P0 pass must set next_action=await-human-approval", validate_result(p0_result("update-trust-region", "execute-P1")))


if __name__ == "__main__":
    unittest.main()
