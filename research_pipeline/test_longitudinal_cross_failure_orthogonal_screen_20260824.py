from __future__ import annotations

import copy
import unittest

from .longitudinal_cross_failure_orthogonal_screen_20260824 import (
    build_cross_failure_orthogonal_screen,
    validate_cross_failure_orthogonal_screen,
)


class LongitudinalCrossFailureOrthogonalScreenTest(unittest.TestCase):
    def setUp(self) -> None:
        self.state = build_cross_failure_orthogonal_screen(generated_at="2026-08-24T10:25:00+08:00")

    def test_three_orthogonal_carriers_are_reduced_before_debate(self) -> None:
        self.assertEqual(validate_cross_failure_orthogonal_screen(self.state), [])
        self.assertEqual(
            {row["carrier_id"] for row in self.state["carriers"]},
            {
                "revision-authority-topology",
                "feedback-to-write-coupling-topology",
                "executable-composition-invariant-witness",
            },
        )
        self.assertEqual(self.state["summary"]["survivors"], 0)
        self.assertEqual(self.state["summary"]["debate_eligible"], 0)
        self.assertEqual(self.state["summary"]["problem_gate_eligible"], 0)
        self.assertEqual(self.state["summary"]["provider_calls_authorized"], 0)
        self.assertEqual(self.state["summary"]["gpu_authorized"], 0)
        self.assertTrue(all(row["decision"].startswith("STOP_") for row in self.state["carriers"]))

    def test_p15_closure_and_pathbench_budget_are_preserved(self) -> None:
        policy = self.state["policy"]
        self.assertTrue(policy["p15_remains_closed"])
        self.assertTrue(policy["pathbench_experiment_budget_remains_do_not_run"])
        self.assertTrue(policy["same_task_ranking_reversal_probe_trajectory_and_seu_remain_closure_support_only"])

    def test_same_information_reducer_must_receive_full_pre_outcome_support(self) -> None:
        broken = copy.deepcopy(self.state)
        broken["carriers"][1]["strongest_same_information_reduction"]["same_information"] = ""
        self.assertIn(
            "carrier-reduction-incomplete:feedback-to-write-coupling-topology",
            validate_cross_failure_orthogonal_screen(broken),
        )
        self.assertTrue(self.state["policy"]["baseline_receives_full_pre_outcome_observable_and_action_support"])

    def test_manual_promotion_or_execution_authority_is_rejected(self) -> None:
        promoted = copy.deepcopy(self.state)
        promoted["carriers"][0]["debate_eligible"] = True
        self.assertIn(
            "carrier-promotion:revision-authority-topology",
            validate_cross_failure_orthogonal_screen(promoted),
        )
        executed = copy.deepcopy(self.state)
        executed["summary"]["provider_calls_authorized"] = 1
        self.assertIn("authority-or-claim-leak:provider_calls_authorized", validate_cross_failure_orthogonal_screen(executed))

    def test_zero_survivor_moves_to_fresh_source_not_more_local_relabeling(self) -> None:
        self.assertIn("bounded fresh-source discovery", self.state["next_action"])
        self.assertEqual(self.state["summary"]["new_external_claims"], 0)
        self.assertTrue(self.state["policy"]["fresh_primary_search_required_before_any_survivor_promotion"])


if __name__ == "__main__":
    unittest.main()
