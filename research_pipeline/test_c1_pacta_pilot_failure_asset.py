from __future__ import annotations
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper_drafts" / "c1-manuscript-strengthening-20260825"


class TestC1PactaPilotClosure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.closure = json.loads(
            (PAPER / "c1-pacta-pilot-closure-20260830.json").read_text()
        )
        cls.failure = json.loads(
            (ROOT / "research_pipeline" / "c1_pacta_pilot_failure_asset_20260830.json").read_text()
        )["asset"]
        cls.audit = json.loads(
            (PAPER / "c1-pacta-claim-audit-20260830.json").read_text()
        )
        cls.registry = json.loads(
            (ROOT / "research_pipeline" / "external_failure_assets.json").read_text()
        )

    def test_execution_identity_and_split(self):
        self.assertEqual(
            self.closure["provenance"]["execution_git_sha"],
            "70e29a40ad252c3fbe85c48bc93a717b1e638785",
        )
        self.assertEqual(self.closure["split"]["pilot"], [313, 376, 368, 512, 300, 191])
        self.assertEqual(len(self.closure["split"]["confirmatory"]), 13)
        self.assertEqual(self.closure["split"]["confirmatory_outcomes_observed"], 0)

    def test_irreversible_pilot_failure(self):
        pilot = self.closure["pilot"]
        self.assertEqual(pilot["projection_calls"], 24)
        self.assertEqual(pilot["projection_exact_schema_successes"], 0)
        self.assertEqual(pilot["projection_failure_states"], 6)
        self.assertEqual(pilot["gate_open"], 0)
        self.assertEqual(pilot["gate_closed"], 6)
        self.assertEqual(pilot["status"], "PILOT_HOLD_OR_STOP")
        self.assertTrue(all(value is None for key, value in pilot["U"].items() if key != "reason"))

    def test_downstream_stays_locked(self):
        self.assertFalse(self.closure["confirmatory"]["executed"])
        self.assertFalse(self.closure["terminal"]["executed"])
        self.assertEqual(self.closure["claim_authority"]["active_manuscript"], "R9")
        self.assertFalse(self.closure["claim_authority"]["R10_created"])

    def test_failure_is_layer_typed(self):
        diff = self.closure["failure_differential"]
        self.assertTrue(diff["projection_schema_failure"])
        self.assertTrue(diff["gate_degeneracy"])
        self.assertFalse(diff["provider_failure"])
        self.assertEqual(diff["counterfactual_gate_mechanism"], "not qualified")
        self.assertEqual(self.failure["scientific_authority"], False)

    def test_claim_audit_preserves_negative_boundary(self):
        self.assertEqual(self.audit["status"], "PASS")
        self.assertEqual(self.audit["summary"], {
            "claims_total": 10,
            "claims_passed": 10,
            "claims_failed": 0,
        })
        self.assertTrue(all(row["pass"] for row in self.audit["checks"]))
        self.assertFalse(any(self.audit["authority"].values()))
        claims = "\n".join(row["claim"] for row in self.audit["checks"]).lower()
        self.assertIn("no u or a3-minus-a2 estimate is authorized", claims)
        self.assertIn("counterfactual gate mechanism was not qualified", claims)
        self.assertIn("r9 remains the active manuscript", claims)

    def test_institutional_lesson_and_registry(self):
        expected = (
            "An existing method adapted from problem A must not be relabeled as novelty for "
            "problem B. Novelty must reside in the additional mechanism required by the "
            "adaptation failure."
        )
        self.assertEqual(self.failure["institutional_lesson"], expected)
        entry = {
            "source_path": "research_pipeline/c1_pacta_pilot_failure_asset_20260830.json",
            "source_key": "asset",
        }
        self.assertEqual(self.registry["assets"].count(entry), 1)
        self.assertFalse(self.registry["scientific_authority"])


if __name__ == "__main__":
    unittest.main()
