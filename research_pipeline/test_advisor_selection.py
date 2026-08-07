from __future__ import annotations

import unittest

from .advisor_selection import build_advisor_selection


class AdvisorSelectionTest(unittest.TestCase):
    def test_comparative_shortlist_covers_all_strict_passes(self) -> None:
        payload = build_advisor_selection()
        self.assertEqual(payload["source_count"], 22)
        self.assertEqual(len(payload["ranked_ideas"]), 22)
        self.assertEqual(len(payload["primary_shortlist"]), 8)
        self.assertEqual(payload["meta_review_status"], {"reviewed": 22, "complete": True})
        self.assertEqual(len({x["cluster"] for x in payload["primary_shortlist"]}), 8)
        self.assertTrue(all(x["first_pilot_priority"] in {"high", "medium", "low"} for x in payload["ranked_ideas"]))
        self.assertEqual(payload["primary_shortlist"][0]["id"], "correction-action-causal-compiler")


if __name__ == "__main__":
    unittest.main()
