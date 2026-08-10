from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from .pilot_registry import build_pilot_registry
from .p0_runner import collect_real_p0
from .pre_p0_identifiability import CHECKS, CURRENT_CONTRACTS, audit_contract, build_pre_p0_identifiability_audit


PHASES=[{"id":p,"title":{"en":p},"setup":{"en":"setup"},"gate":{"en":"gate"}} for p in ("P0","P1","P2")]


def idea(idea_id: str) -> dict:
    return {"id":idea_id,"title":{"en":idea_id},"rank":1,"experiment_protocol":{"phases":PHASES}}


def passing_audit(idea_id: str) -> dict:
    contract={
        "code":"X-1","claim":"claim","objective":"objective","primary_metric":"metric",
        "checks":{row["key"]:True for row in CHECKS},"required_next":"execute bounded P0",
    }
    node=audit_contract(idea_id,contract)
    return {"schema_version":"1.0","policy":{"p0_execution_requires_pre_p0_pass":True},"summary":{"audited":1,"execution_ready":1,"blocked":0},"nodes":[node]}


def passing_pre_experiment_card(idea_id: str) -> dict:
    return {"idea_id": idea_id, "status": "pass", "execution_authorized": True, "passed_gates": 8, "gate_count": 8, "blockers": []}


class PreP0IdentifiabilityTest(unittest.TestCase):
    def test_current_round1_failures_are_blocked_before_gpu(self) -> None:
        audit=build_pre_p0_identifiability_audit({"passed_ideas":[idea(k) for k in CURRENT_CONTRACTS]})
        by_id={row["idea_id"]:row for row in audit["nodes"]}
        self.assertEqual(audit["summary"]["execution_ready"],0)
        self.assertIn("representability",by_id["update-trust-region"]["blockers"])
        self.assertIn("target_variation",by_id["budgeted-evolution-controller"]["blockers"])
        self.assertIn("baseline_disagreement",by_id["outcome-equivalent-trajectory-contrast"]["blockers"])
        self.assertIn("claim_alignment",by_id["workflow-generalization-certificate"]["blockers"])
        self.assertTrue(all(row["estimated_voi"]=="near-zero-before-repair" for row in audit["nodes"]))

    def test_all_ten_checks_are_hard_requirements(self) -> None:
        self.assertEqual(len(CHECKS),10)
        contract={"code":"X","checks":{row["key"]:True for row in CHECKS}}
        self.assertTrue(audit_contract("x",contract)["execution_ready"])
        for row in CHECKS:
            broken={**contract,"checks":dict(contract["checks"])}
            broken["checks"][row["key"]]=False
            self.assertFalse(audit_contract("x",broken)["execution_ready"],row["key"])

    def test_real_p0_runner_cannot_bypass_pre_p0_gate(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "explicit frozen --config and 8/8 Pre-Experiment Card"):
            collect_real_p0(
                "update-trust-region", None, Path("missing-alfworld.yaml"), Path("missing-model"),
                Path("missing-data"), Path("missing-site"), Path("missing-alfworld"), Path("missing-output"),
            )

    def test_pilot_registry_requires_human_and_pre_p0_gates(self) -> None:
        bank={"passed_ideas":[idea("update-trust-region")]}
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            blocked=build_pilot_registry(bank,result_dir=root/"results",approval_dir=root/"approvals")
            self.assertEqual(blocked["summary"]["p0_authorized"],0)
            row=blocked["ideas"][0]
            self.assertEqual(row["p0_gate_status"],"ready")
            self.assertEqual(row["pre_p0_gate_status"],"repair-required")
            self.assertEqual(row["next_action"],"repair-pre-p0-identifiability-before-P0")

            ready=build_pilot_registry(bank,result_dir=root/"results",approval_dir=root/"approvals",pre_p0_audit=passing_audit("update-trust-region"),pre_experiment_cards={"update-trust-region":passing_pre_experiment_card("update-trust-region")})
            self.assertEqual(ready["summary"]["p0_authorized"],1)
            self.assertEqual(ready["ideas"][0]["next_phase"],"P0")


if __name__=="__main__":
    unittest.main()
