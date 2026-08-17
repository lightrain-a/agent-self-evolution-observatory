from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from research_pipeline.paper_first_fresh_phenomenon_portfolio import (
    build_fresh_phenomenon_portfolio,
    validate_fresh_phenomenon_portfolio,
)
from research_pipeline.principle_adjudication import audit_dead_end_counter_explanation


ROOT = Path(__file__).resolve().parents[1]
READJUDICATION = ROOT / "generated" / "skill-validation-transfer-distribution-shift-principle-readjudication-20260817.json"


class SkillValidationTransferPrincipleReadjudicationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.row = json.loads(READJUDICATION.read_text(encoding="utf-8"))

    def test_scoped_same_information_reduction_is_auditable(self) -> None:
        self.assertEqual("PA-05-SKILL-VALIDATION-TRANSFER", self.row["candidate_id"])
        self.assertTrue(self.row["principle_dead_end_certified"])
        self.assertFalse(self.row["experiment_run_for_this_readjudication"])
        counter = self.row["principle_diagnosis"]["counter_explanation"]
        audit = audit_dead_end_counter_explanation(counter)
        self.assertTrue(audit["passed"], audit["blockers"])
        self.assertEqual("SAME_INFORMATION_REDUCTION", audit["type"])
        self.assertTrue(counter["same_information_reduction_verified"])
        self.assertIn("distribution-shift", self.row["scientific_interpretation"]["new_search_basin"])

    def test_closure_is_narrow_and_preserves_substrate_reuse(self) -> None:
        closure = self.row["fresh_phenomenon_closure"]
        self.assertEqual("arXiv:2605.24117", closure["source_ref"])
        self.assertEqual(3, len(closure["closed_evidence_sha256"]))
        self.assertIn("ranking inversion", closure["closure_scope"])
        self.assertIn("remains a strong first-party executable substrate", self.row["scientific_interpretation"]["safe_claim"])
        self.assertFalse(closure["scientific_authority"])

    def test_invalid_reduction_fails_closed_back_to_execution_hold(self) -> None:
        broken = copy.deepcopy(self.row)
        broken["principle_diagnosis"]["counter_explanation"]["same_information_reduction_verified"] = False
        state = build_fresh_phenomenon_portfolio(skill_validation_readjudication=broken)
        row = next(r for r in state["candidates"] if r["candidate_id"] == "PA-05-SKILL-VALIDATION-TRANSFER")
        self.assertEqual("HOLD_EXECUTION", row["status"])
        self.assertEqual("PROVENANCE_AUDITED_FIRST_PARTY_EXECUTABLE_SUBSTRATE", row["support_status"])
        self.assertTrue(row["f0_design_ready"])
        self.assertFalse(row["scientific_authority"])
        self.assertEqual([], validate_fresh_phenomenon_portfolio(state))


if __name__ == "__main__":
    unittest.main()
