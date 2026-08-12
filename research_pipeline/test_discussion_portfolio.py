from __future__ import annotations

import unittest

from .discussion_portfolio import TARGET, build_discussion_portfolio


class DiscussionPortfolioTest(unittest.TestCase):
    def test_terminal_active_pool_accounting(self) -> None:
        payload = build_discussion_portfolio()
        self.assertEqual(payload["target"], TARGET)
        self.assertEqual(payload["count"], 27)
        self.assertGreaterEqual(payload["count"], TARGET)
        self.assertEqual(payload["remaining"], 0)
        self.assertTrue(payload["ready"])
        self.assertEqual(payload["final_summary"]["pass"], TARGET)
        self.assertEqual(payload["final_summary"]["revise"], 0)
        self.assertEqual(payload["final_summary"]["block"], 0)
        self.assertTrue(payload["policy"]["terminal_human_state_is_active_source_of_truth"])
        self.assertTrue(payload["policy"]["absorbed_children_excluded_from_advisor_pool"])
        self.assertTrue(payload["policy"]["target_is_minimum_not_exact_cap"])
        self.assertTrue(payload["policy"]["no_portfolio_shortlist"])
        self.assertTrue(all(row["terminal_state"] in {"p0", "p0-ready"} for row in payload["ideas"]))
        self.assertEqual(sum(row["source"] == "human-terminal-parent" for row in payload["ideas"]), 20)
        self.assertEqual(sum(row["source"] == "terminal-independent-method" for row in payload["ideas"]), 7)
        self.assertEqual(len({row["id"] for row in payload["ideas"]}), 27)

    def test_merged_dropped_and_absorbed_methods_are_absent_from_active_pool(self) -> None:
        ids = {row["id"] for row in build_discussion_portfolio()["ideas"]}
        self.assertIn("regression-gated-self-evolution", ids)
        self.assertNotIn("outcome-equivalent-trajectory-contrast", ids)
        self.assertNotIn("causally-verified-experience-admission", ids)
        self.assertNotIn("probe-mutation-retirement-policy", ids)
        self.assertNotIn("failure-localization-before-reflection", ids)


if __name__ == "__main__":
    unittest.main()
