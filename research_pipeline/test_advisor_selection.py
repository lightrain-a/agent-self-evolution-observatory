from __future__ import annotations

import unittest

from .discussion_portfolio import build_discussion_portfolio
from .research_system import build_research_system_state


class DiscussionPoolPolicyTest(unittest.TestCase):
    def test_all_strict_passes_enter_the_senior_discussion_pool(self) -> None:
        portfolio = build_discussion_portfolio()
        self.assertEqual(portfolio["target"], 20)
        self.assertEqual(portfolio["count"], 20)
        self.assertTrue(portfolio["ready"])
        self.assertEqual(len(portfolio["ideas"]), 20)
        self.assertEqual(portfolio["final_summary"]["pass"], 20)
        self.assertEqual(portfolio["final_summary"]["revise"], 0)
        self.assertEqual(portfolio["final_summary"]["block"], 0)
        self.assertTrue(all(item["verdict"] == "pass" and item["reviewed"] and item["collision_gate"] == "pass" for item in portfolio["ideas"]))

    def test_no_comparative_shortlist_is_active(self) -> None:
        state = build_research_system_state()
        self.assertNotIn("advisor_selection", state)
        self.assertNotIn("advisor_priority_first_read", state["summary"])
        self.assertFalse(any("comparative meta-review" in item["source"].lower() for item in state["components"]))


if __name__ == "__main__":
    unittest.main()
