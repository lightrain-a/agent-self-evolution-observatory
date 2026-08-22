from __future__ import annotations

import unittest

from .d2_active_paper_reopen_scheduler import PRIORITY, build_scheduler


CURRENT_CANONICAL = {
    "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE": "SUBMISSION_READY",
    "D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK": "SUBMISSION_READY",
    "D2-PAPER-FAILURE-MEMORY-PROVENANCE": "TARGETED_REPAIR",
}


class D2ActivePaperReopenSchedulerTest(unittest.TestCase):
    def test_canonical_submission_ready_state_overrides_old_repair_blockers(self) -> None:
        state = build_scheduler(paper_acceptance_states=CURRENT_CANONICAL)
        self.assertEqual(state["status"], "PORTFOLIO_HAS_SUBMISSION_READY_WITH_HELD_TARGETED_REPAIR")
        self.assertEqual([row["paper_id"] for row in state["entries"]], list(PRIORITY))
        self.assertEqual(
            state["summary"],
            {
                "papers": 3,
                "submission_ready": 2,
                "reopen_now": 0,
                "hold_environment": 0,
                "hold_support": 0,
                "hold_support_and_identification": 1,
            },
        )
        self.assertEqual(state["entries"][0]["scheduler_state"], "DONE_SUBMISSION_READY")
        self.assertEqual(state["entries"][1]["scheduler_state"], "DONE_SUBMISSION_READY")
        self.assertEqual(state["entries"][2]["scheduler_state"], "HOLD_SUPPORT_AND_IDENTIFICATION")

    def test_c01_reopen_gate_tracks_power_and_identification_debt(self) -> None:
        state = build_scheduler(paper_acceptance_states=CURRENT_CANONICAL)
        c01 = state["entries"][2]
        evidence = c01["current_evidence"]
        self.assertEqual(evidence["r4_verdict"], "INCONCLUSIVE_NO_THRESHOLD_CHANGE")
        self.assertEqual(evidence["r4_mean_success_minus_failure_terminal_rate"], 0.166667)
        self.assertAlmostEqual(evidence["r4_permutation_p_success_greater"], 0.07853921460785392)
        self.assertEqual(evidence["approx_independent_pairs_for_80pct_power_range"], [18, 22])
        self.assertEqual(evidence["original_verifier_primary_strict_pass"], 4)
        self.assertEqual(evidence["deepseek_primary_strict_pass"], 0)
        self.assertEqual(evidence["kimi_primary_strict_pass"], 1)
        self.assertEqual(evidence["three_reviewer_unanimous_primary_strict_pass"], 0)
        self.assertEqual(evidence["fresh_same_release_confirmation_tasks"], 0)

    def test_scheduler_forbids_obsolete_or_outcome_driven_spend(self) -> None:
        state = build_scheduler(paper_acceptance_states=CURRENT_CANONICAL)
        c02, c06, c01 = state["entries"]
        self.assertTrue(any("obsolete targeted-repair" in item for item in c02["forbid_before_reopen"]))
        self.assertTrue(any("obsolete targeted-repair" in item for item in c06["forbid_before_reopen"]))
        self.assertTrue(any("same four R4 pairs" in item for item in c01["forbid_before_reopen"]))
        self.assertTrue(any("drop or replace R4 pairs" in item for item in c01["forbid_before_reopen"]))
        for row in state["entries"]:
            self.assertFalse(row["scientific_authority"])
            self.assertFalse(row["experiment_authority"])


if __name__ == "__main__":
    unittest.main()
