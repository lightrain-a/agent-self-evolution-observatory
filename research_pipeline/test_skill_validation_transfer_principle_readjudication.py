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
from research_pipeline.paper_first_skill_validation_transfer_f0 import (
    ARMS,
    SOURCE_DEPLOYMENT_ROLES,
    SOURCE_LEARNING_ROLES,
)


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

    def test_exact_reduction_witness_matches_frozen_f0_and_does_not_rely_on_generic_veto(self) -> None:
        counter = self.row["principle_diagnosis"]["counter_explanation"]
        witness = counter["exact_reduction_witness"]
        self.assertEqual("ALGEBRAIC_REPARAMETERIZATION", witness["witness_type"])
        self.assertFalse(witness["requires_experiment_outcome"])
        self.assertFalse(witness["depends_on_observed_inversion_rate"])
        self.assertEqual(list(ARMS), witness["candidate_arms"])
        self.assertEqual(list(SOURCE_LEARNING_ROLES), witness["source_roles"])
        self.assertEqual(list(SOURCE_DEPLOYMENT_ROLES), witness["target_roles"])
        self.assertIn("argmax_a L_a", witness["mapping"]["local_selector"])
        self.assertIn("argmax_a D_a", witness["mapping"]["deployment_oracle"])
        self.assertIn("sign(local_delta) != sign(deployment_delta)", witness["mapping"]["ranking_inversion"])
        self.assertIn("D_deployment_oracle", witness["mapping"]["selector_regret"])
        refs = counter["evidence_refs"]
        self.assertIn("arXiv:2409.19774", refs)
        self.assertIn("arXiv:2209.00652", refs)
        self.assertIn("arXiv:2007.03511", refs)
        self.assertFalse(any("paper_first_fresh_saturation.py#" in ref for ref in refs))
        self.assertTrue(all("TOO_GENERIC_TO_VETO" in ref or "SOFT_COLLISION" in ref for ref in counter["non_authoritative_context_refs"]))

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
