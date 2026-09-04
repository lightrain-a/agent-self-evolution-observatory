from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "generated" / "agent-safety-g1-mcta-p1-conditional-contract-20260904.json"


class MCTAP1ContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_authority_remains_closed(self) -> None:
        self.assertTrue(all(value is False for value in self.contract["authority"].values()))

    def test_design_has_eight_states_and_24_matched_units(self) -> None:
        self.assertEqual(self.contract["state_design"]["fresh_persistent_states"], 8)
        self.assertGreaterEqual(self.contract["state_design"]["minimum_source_families"], 3)
        self.assertEqual(self.contract["pair_assignment"]["assignments_per_state"], 3)
        self.assertEqual(self.contract["pair_assignment"]["matched_longitudinal_units"], 24)

    def test_two_update_sequences_are_balanced(self) -> None:
        update = self.contract["update_design"]
        self.assertEqual(update["update_sequence_count"], 2)
        self.assertEqual(update["states_per_update_sequence"], 4)
        self.assertTrue(update["update_sequences_frozen_before_p1"])

    def test_episode_count_is_exact(self) -> None:
        work = self.contract["workload"]
        self.assertEqual(work["t0_shared_episodes"], 48)
        self.assertEqual(work["postbaseline_episodes"], 288)
        self.assertEqual(work["agent_episode_count"], 336)

    def test_primary_estimand_is_stable_capability_crossing_not_raw_asr(self) -> None:
        primary = self.contract["primary_estimand"]
        self.assertIn("C(t0)=1", primary["definition"])
        self.assertIn("R1(t0)=0", primary["definition"])
        self.assertFalse(primary["raw_ASR_is_primary"])
        self.assertFalse(primary["capability_unlock_units_count_as_safety_drift"])

    def test_baseline_positive_units_are_retained_not_replaced(self) -> None:
        rule = self.contract["unit_level_temporal_classification"]["baseline_R1_positive"]
        self.assertIn("Retain", rule)
        self.assertIn("never replaced", rule)

    def test_length_placebo_is_required_for_workflow_semantics_claim(self) -> None:
        gate = self.contract["mechanism_gate"]
        self.assertTrue(gate["positive_workflow_semantics_claim_requires_length_structure_placebo"])
        self.assertEqual(gate["placebo_subset_units"], 12)
        self.assertIn("before P1 outcomes", gate["placebo_subset_selection"])

    def test_second_backbone_is_transport_not_first_result_requirement(self) -> None:
        gate = self.contract["transport_gate"]
        self.assertTrue(gate["second_backbone_not_required_for_first_decisive_result"])
        self.assertTrue(gate["recommended_for_final_external_validity"])
        self.assertEqual(gate["preselected_transport_units"], 12)


if __name__ == "__main__":
    unittest.main()
