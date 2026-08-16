from __future__ import annotations

import unittest

from research_pipeline.b3_minteval_support import (
    build_matched_stale_pair_candidates,
    score_factorial_outcome,
    select_source_disjoint_candidates,
)


class B3MintevalSupportTest(unittest.TestCase):
    def fixture(self, row_id="001"):
        return {
            "id": row_id,
            "contexts": [
                {"content": "Daniel went to the office.", "timestamp": ""},
                {"content": "Mary went to the garden.", "timestamp": ""},
                {"content": "Daniel journeyed to the hallway.", "timestamp": ""},
                {"content": "John travelled to the kitchen.", "timestamp": ""},
                {"content": "Daniel moved to the bedroom.", "timestamp": ""},
                {"content": "Sandra went to the bathroom.", "timestamp": ""},
            ],
            "questions": [
                {"answer": "bedroom", "metadata": "{}", "question": "Where is Daniel?", "question_type": "simple"}
            ],
        }

    def test_builds_matched_stale_pair_without_model_output(self):
        rows = [self.fixture()]
        out = build_matched_stale_pair_candidates(rows)
        self.assertEqual(len(out), 1)
        row = out[0]
        self.assertEqual(row["support_memory"]["location"], "bedroom")
        self.assertEqual(row["stale_memory_A"]["location"], "hallway")
        self.assertEqual(row["stale_memory_B"]["location"], "office")
        self.assertNotEqual(row["neutral_memory_N1"]["who"], "Daniel")
        self.assertNotEqual(row["neutral_memory_N2"]["who"], "Daniel")
        self.assertFalse(row["selection_used_model_outputs"])
        self.assertEqual(len(row["arms"]["none"]), 3)
        self.assertEqual(len(row["arms"]["A"]), 3)
        self.assertEqual(len(row["arms"]["B"]), 3)
        self.assertEqual(len(row["arms"]["AB"]), 3)

    def test_gold_inconsistent_latest_fact_is_rejected(self):
        row = self.fixture()
        row["questions"][0]["answer"] = "garden"
        self.assertEqual(build_matched_stale_pair_candidates([row]), [])

    def test_source_disjoint_freeze_keeps_one_candidate_per_history(self):
        a = build_matched_stale_pair_candidates([self.fixture("001")])[0]
        b = dict(a); b["candidate_id"] = "other-same-history"
        c = build_matched_stale_pair_candidates([self.fixture("002")])[0]
        frozen = select_source_disjoint_candidates([a, b, c], limit=10)
        self.assertEqual([row["history_id"] for row in frozen], ["001", "002"])

    def test_only_joint_only_harm_counts_as_mechanism_support(self):
        yes = score_factorial_outcome({"none": 1, "A": 1, "B": 1, "AB": 0})
        self.assertTrue(yes["mechanism_support"])
        self.assertEqual(yes["interaction_contrast"], -1)

        complementarity = score_factorial_outcome({"none": 0, "A": 0, "B": 0, "AB": 1})
        self.assertFalse(complementarity["mechanism_support"])
        self.assertTrue(complementarity["ordinary_complementarity_excluded"])

        single_harm = score_factorial_outcome({"none": 1, "A": 0, "B": 1, "AB": 0})
        self.assertFalse(single_harm["mechanism_support"])
        self.assertTrue(single_harm["single_memory_harm_excluded"])


if __name__ == "__main__":
    unittest.main()
