from __future__ import annotations

import unittest

from .d2_active_paper_reopen_scheduler import PRIORITY, build_scheduler


class D2ActivePaperReopenSchedulerTest(unittest.TestCase):
    def test_current_scheduler_is_support_bound_and_preserves_mock_pc_priority(self) -> None:
        state = build_scheduler()
        self.assertEqual(state["status"], "ALL_THREE_TARGETED_REPAIRS_EXTERNALLY_BLOCKED")
        self.assertEqual([row["paper_id"] for row in state["entries"]], list(PRIORITY))
        self.assertEqual(state["summary"], {"papers": 3, "reopen_now": 0, "hold_environment": 1, "hold_support": 2})
        self.assertEqual(state["entries"][0]["scheduler_state"], "HOLD_ENVIRONMENT")
        self.assertEqual(state["entries"][1]["scheduler_state"], "HOLD_SUPPORT")
        self.assertEqual(state["entries"][2]["scheduler_state"], "HOLD_SUPPORT")

    def test_scheduler_forbids_more_surrogate_spend_before_decisive_dependencies_reopen(self) -> None:
        state = build_scheduler()
        c02, c06, c01 = state["entries"]
        self.assertTrue(any("first-action" in item for item in c02["forbid_before_reopen"]))
        self.assertTrue(any("synthetic TimeSage" in item for item in c06["forbid_before_reopen"]))
        self.assertTrue(any("explicit SUCCESS/FAILURE" in item for item in c01["forbid_before_reopen"]))
        for row in state["entries"]:
            self.assertFalse(row["scientific_authority"])
            self.assertFalse(row["experiment_authority"])


if __name__ == "__main__":
    unittest.main()
