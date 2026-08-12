from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from .paper_first_c2_contract import build_c2_contract
from .paper_first_post_c2_adjudication import (
    SOURCE,
    build_post_c2_adjudication,
    evaluate_post_c2_adjudication,
)


class PaperFirstPostC2AdjudicationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.authority = json.loads(Path(SOURCE).read_text(encoding="utf-8"))
        cls.latest_contract = build_c2_contract()
        cls.state = build_post_c2_adjudication()

    def test_real_c2_terminalizes_current_mechanism_only(self) -> None:
        self.assertEqual(self.state["decision"], "STOP_CURRENT_CONTROLLED_MEDIATOR_PAPER_MECHANISM")
        self.assertEqual(self.state["current_paper_formulation_status"], "STOP")
        self.assertEqual(self.state["current_method_status"], "local-falsifier-triggered")
        self.assertEqual(self.state["broad_parent_phenomenon_status"], "SURVIVES_AS_ARCHIVED_PARENT_EVIDENCE")
        self.assertTrue(self.state["authority"]["clean_mechanism_stop"])

    def test_stop_is_invariant_to_later_gate_tightening(self) -> None:
        gate = self.state["gate_provenance"]
        self.assertTrue(gate["executed_gate_stops_observed_result"])
        self.assertTrue(gate["latest_source_gate_stops_observed_result"])
        self.assertTrue(gate["decision_invariant_to_later_gate_tightening"])
        self.assertEqual(gate["executed_gate"]["minimum_nonzero_tau_units"], 3)
        self.assertEqual(gate["latest_source_gate"]["minimum_nonzero_tau_units"], 9)
        self.assertEqual(gate["latest_source_gate"]["minimum_parent_sign_concordant_units"], 9)

    def test_c3_full_and_rescue_remain_locked(self) -> None:
        authority = self.state["authority"]
        self.assertTrue(authority["C3_locked"])
        self.assertFalse(authority["full_experiment_authorized"])
        self.assertFalse(authority["second_backbone_authorized"])
        self.assertFalse(authority["new_method_auto_authorized"])
        self.assertFalse(authority["new_paper_problem_auto_authorized"])
        self.assertFalse(authority["threshold_relaxation_authorized"])
        self.assertFalse(authority["unit_replacement_authorized"])
        self.assertFalse(authority["retrospective_principle_certificate_authorized"])

    def test_decision_context_failure_blocks_mechanism_falsifier_authority(self) -> None:
        authority = copy.deepcopy(self.authority)
        authority["decision_context_validity"]["decision"] = "POSTHOC_DECISION_CONTEXT_VALIDITY_FAIL"
        authority["decision_context_validity"]["valid_units"] = 9
        result = evaluate_post_c2_adjudication(authority, self.latest_contract)
        self.assertEqual(result["decision"], "C2_NEGATIVE_VALIDITY_INCONCLUSIVE_REDESIGN_REQUIRED")
        self.assertFalse(result["authority"]["clean_mechanism_stop"])
        self.assertTrue(result["authority"]["C3_locked"])
        self.assertFalse(result["authority"]["full_experiment_authorized"])

    def test_scienceworld_scope_lesson_cannot_rescue_or_falsify_principle(self) -> None:
        scienceworld = self.state["scienceworld_scope_evidence"]
        self.assertEqual(scienceworld["f0_decision"], "SYMMETRIC_F0_HOLD")
        self.assertFalse(scienceworld["auto_rescues_current_paper"])
        self.assertIn("No retrospective principle certificate", scienceworld["principle_authority"])
        self.assertFalse(self.state["authority"]["retrospective_principle_certificate_authorized"])

    def test_recorded_stop_must_match_executed_frozen_gate(self) -> None:
        authority = copy.deepcopy(self.authority)
        authority["historical_frozen_contract"]["go"]["minimum_nonzero_tau_units"] = 2
        authority["historical_frozen_contract"]["go"]["same_memory_cross_context_sign_reversal_required"] = False
        result = evaluate_post_c2_adjudication(authority, self.latest_contract)
        self.assertEqual(result["decision"], "C2_PROVENANCE_INCONSISTENT_HOLD")
        self.assertFalse(result["authority"]["clean_mechanism_stop"])


if __name__ == "__main__":
    unittest.main()
