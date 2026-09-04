from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "generated" / "agent-safety-g1-mcta-baseline-workload-plan-20260904.json"


class MCTABaselineWorkloadPlanTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = json.loads(PLAN.read_text(encoding="utf-8"))
        cls.baselines = {row["id"]: row for row in cls.plan["baseline_matrix"]}

    def test_no_execution_authority_is_opened(self) -> None:
        self.assertTrue(all(value is False for value in self.plan["authority"].values()))

    def test_required_analysis_baselines_are_present(self) -> None:
        for baseline in (
            "M0_RAW_TEMPORAL_METRIC",
            "M1_GLOBAL_CAPABILITY_GATE_ONLY",
            "M2_SAME_SURFACE_TWIN_NO_GRAPH",
            "M3_MCTA_GRAPH_COMPLETE",
        ):
            self.assertIn(baseline, self.baselines)
            self.assertTrue(self.baselines[baseline]["required"])
            self.assertEqual(self.baselines[baseline]["extra_agent_calls"], 0)

    def test_primary_intervention_is_updated_vs_frozen(self) -> None:
        self.assertTrue(self.baselines["A0_FROZEN_W0"]["required"])
        self.assertTrue(self.baselines["A1_UPDATED"]["required"])
        self.assertFalse(self.baselines["A3_NULLMEMORY"]["required"])

    def test_length_structure_placebo_is_frozen_as_positive_claim_gate(self) -> None:
        placebo = self.baselines["A2_LENGTH_STRUCTURE_PLACEBO"]
        self.assertTrue(placebo["required_for_positive_mechanism_claim"])
        self.assertIn("before P1 outcomes", placebo["execution_trigger"])

    def test_t0_does_not_force_all_ten_pairs(self) -> None:
        target = self.plan["t0_admission_target"]
        self.assertEqual(target["candidate_pairs"], 10)
        self.assertEqual(target["minimum_admitted_pairs"], 6)
        self.assertGreaterEqual(target["minimum_distinct_surfaces"], 5)
        self.assertGreaterEqual(target["minimum_distinct_terminal_classes"], 5)

    def test_p1_has_24_matched_units_and_correct_episode_count(self) -> None:
        p1 = self.plan["p1_confirmatory_design"]
        self.assertEqual(p1["fresh_persistent_states"], 8)
        self.assertEqual(p1["task_pair_assignments_per_state"], 3)
        self.assertEqual(p1["matched_longitudinal_units"], 24)
        self.assertEqual(p1["timepoints"], [0, 1, 2, 3])
        self.assertEqual(p1["agent_episode_count"], 336)
        self.assertTrue(p1["read_only_evaluation"])

    def test_placebo_and_transport_are_conditional_not_posthoc_inventions(self) -> None:
        self.assertEqual(self.plan["p2_placebo_mechanism"]["preselected_units"], 12)
        self.assertEqual(self.plan["p2_placebo_mechanism"]["agent_episode_count"], 72)
        self.assertEqual(self.plan["p3_transport"]["preselected_units"], 12)
        self.assertEqual(self.plan["p3_transport"]["total_agent_episode_count"], 178)

    def test_workload_is_large_enough_without_fake_iid_episode_count(self) -> None:
        summary = self.plan["workload_summary"]
        self.assertEqual(summary["core_total_if_J_equals_8"], 378)
        self.assertEqual(summary["with_placebo"], 450)
        self.assertEqual(summary["with_placebo_and_transport"], 628)
        self.assertIn("independent state/pair support", " ".join(self.plan["not_recommended"]))


if __name__ == "__main__":
    unittest.main()
