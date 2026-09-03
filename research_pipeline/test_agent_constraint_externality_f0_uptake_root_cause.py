from __future__ import annotations

import json
import unittest

from research_pipeline.agent_constraint_externality_f0_uptake_root_cause import OUTPUT
from research_pipeline.agent_constraint_externality_runner_core import sha256_value


class F0UptakeRootCauseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(OUTPUT.read_text(encoding="utf-8"))

    def test_artifact_is_content_addressed_and_zero_request(self) -> None:
        claimed = self.payload["content_sha256"]
        unsigned = dict(self.payload)
        unsigned.pop("content_sha256")
        self.assertEqual(claimed, sha256_value(unsigned))
        self.assertEqual(self.payload["provider_requests_added_by_diagnosis"], 0)
        self.assertEqual(self.payload["scientific_outcomes_added_by_diagnosis"], 0)

    def test_capability_gate_cannot_guarantee_six_source_failures(self) -> None:
        mismatch = self.payload["arithmetic_mismatch"]
        self.assertEqual(mismatch["maximum_target_failures_when_only_meeting_capability_success_min_if_same_panel"], 4)
        self.assertEqual(mismatch["f0_minimum_eligible_repair_families"], 6)
        self.assertEqual(mismatch["failure_shortfall_even_at_capability_success_floor"], 2)

    def test_source_task_is_structurally_simpler_than_capability_task(self) -> None:
        cap = self.payload["structural_comparison"]["capability_means"]
        source = self.payload["structural_comparison"]["f0_source_means"]
        self.assertEqual(cap["constraint_count"], 3.0)
        self.assertEqual(source["constraint_count"], 1.0)
        self.assertEqual(cap["non_target_constraint_count"], 2.0)
        self.assertEqual(source["non_target_constraint_count"], 0.0)
        self.assertEqual(cap["tool_call_cap"], source["tool_call_cap"])
        self.assertLess(source["instruction_word_count"], cap["instruction_word_count"])

    def test_current_run_stops_and_only_prospective_redesign_is_open(self) -> None:
        self.assertEqual(self.payload["status"], "CAPABILITY_GATE_DOES_NOT_IDENTIFY_SOURCE_FAILURE_AVAILABILITY")
        self.assertEqual(self.payload["classification"], "SOURCE_FAILURE_OPPORTUNITY_DESIGN_MISMATCH")
        self.assertTrue(self.payload["prospective_repair_design_requirements"]["current_f0_mandatory_stop"])
        self.assertTrue(self.payload["prospective_repair_design_requirements"]["current_f0_source_families_may_not_be_rewritten_and_replayed"])
        self.assertTrue(self.payload["authority"]["prospective_redesign_only"])
        self.assertFalse(self.payload["authority"]["current_f0"])
        self.assertFalse(self.payload["authority"]["probe"])
        self.assertFalse(self.payload["authority"]["p1"])


if __name__ == "__main__":
    unittest.main()
