from __future__ import annotations

import unittest

from .discussion_portfolio import TARGET, build_discussion_portfolio


class DiscussionPortfolioTest(unittest.TestCase):
    def test_strict_final_pass_accounting(self) -> None:
        payload = build_discussion_portfolio()
        self.assertEqual(payload["target"], TARGET)
        self.assertEqual(payload["count"], TARGET)
        self.assertEqual(payload["remaining"], 0)
        self.assertTrue(payload["ready"])
        self.assertEqual(payload["final_summary"]["pass"], TARGET)
        self.assertEqual(payload["final_summary"]["revise"], 0)
        self.assertEqual(payload["final_summary"]["block"], 0)
        self.assertTrue(payload["policy"]["strict_final_pass_only"])
        self.assertTrue(payload["policy"]["two_model_unanimous_pass_required"])
        self.assertTrue(payload["policy"]["fresh_primary_source_collision_gate_required"])
        self.assertTrue(payload["policy"]["no_portfolio_shortlist"])
        self.assertTrue(all(row["verdict"] == "pass" and row["final_verdict"] == "pass" for row in payload["ideas"]))
        self.assertTrue(all(row["collision_gate"] == "pass" for row in payload["ideas"]))
        self.assertEqual(len({row["id"] for row in payload["ideas"]}), TARGET)

    def test_historical_blocks_are_absent_from_current_pool(self) -> None:
        ids = {row["id"] for row in build_discussion_portfolio()["ideas"]}
        self.assertNotIn("regression-gated-self-evolution", ids)
        self.assertNotIn("effect-transport-lesson-specializer-v5", ids)


if __name__ == "__main__":
    unittest.main()
