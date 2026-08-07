from __future__ import annotations

import unittest
from .discussion_portfolio import TARGET, build_discussion_portfolio


class DiscussionPortfolioTest(unittest.TestCase):
    def test_strict_pass_accounting(self) -> None:
        p=build_discussion_portfolio()
        self.assertEqual(p["target"],TARGET)
        self.assertEqual(p["remaining"],max(0,TARGET-p["count"]))
        self.assertEqual(p["count"],22)
        self.assertTrue(p["ready"])
        self.assertTrue(p["policy"]["strict_external_pass_only"])
        self.assertTrue(p["policy"]["supplementary_machine_school_not_counted"])
        self.assertTrue(all(x["verdict"]=="pass" for x in p["ideas"]))
        self.assertEqual(len({(x["source"],x["id"]) for x in p["ideas"]}),len(p["ideas"]))


if __name__=="__main__":unittest.main()
