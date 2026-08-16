from __future__ import annotations

import unittest

from .asset_first_stri_paper_analysis_suite import perturb, profile


class AssetFirstSTRIPaperAnalysisSuiteTest(unittest.TestCase):
    def test_clone_and_split_quotients_recover_support(self) -> None:
        rows = [
            {"level": 1, "index": 0, "tool": "A", "accepted_skill_ids": ["a"]},
            {"level": 1, "index": 1, "tool": "B", "accepted_skill_ids": ["b"]},
            {"level": 1, "index": 2, "tool": "C", "accepted_skill_ids": ["a", "b"]},
        ]
        base = profile(rows)
        self.assertEqual(base["witness_count"], 1)
        self.assertEqual(base["witness_lb"], 2.0)

        audit = perturb(rows)
        self.assertTrue(audit["identity_rename_pass"])
        self.assertTrue(audit["all_clone_quotients_recover"])
        self.assertTrue(audit["all_split_quotients_recover"])
        self.assertTrue(audit["all_clone_duplicates_detected"])
        self.assertTrue(all(row["quotient_witness_count"] == 1 for row in audit["clone_controls"]))
        self.assertTrue(all(row["quotient_witness_count"] == 1 for row in audit["split_controls"]))

    def test_disjoint_support_is_not_given_a_closed_form_witness(self) -> None:
        rows = [
            {"level": 3, "index": 0, "tool": "A", "accepted_skill_ids": ["a"]},
            {"level": 3, "index": 1, "tool": "B", "accepted_skill_ids": ["b"]},
        ]
        self.assertEqual(profile(rows)["witness_count"], 0)


if __name__ == "__main__":
    unittest.main()
