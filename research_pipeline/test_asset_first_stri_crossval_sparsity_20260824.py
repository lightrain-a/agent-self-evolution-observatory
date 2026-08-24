from __future__ import annotations

import unittest

from .asset_first_stri_crossval_sparsity_20260824 import exact_sparsity_frontier


class STRICrossvalSparsityTest(unittest.TestCase):
    def test_sparsity_frontier_detects_minimum_cover_and_optimum(self) -> None:
        rows = [
            {"level": 1, "index": 0, "tool": "a", "accepted_skill_ids": ["s1"]},
            {"level": 1, "index": 1, "tool": "b", "accepted_skill_ids": ["s2"]},
            {"level": 1, "index": 2, "tool": "c", "accepted_skill_ids": ["s1", "s2"]},
        ]
        result = exact_sparsity_frontier(rows)
        self.assertEqual(result["minimum_feasible_active_packages"], 2)
        self.assertEqual(result["minimum_active_packages_attaining_unrestricted_R_star"], 2)
        self.assertAlmostEqual(float(result["unrestricted_R_star"]), 2.0)
        self.assertFalse(result["frontier"][0]["feasible"])
        self.assertTrue(result["frontier"][1]["feasible"])

    def test_single_universal_package_is_exact(self) -> None:
        rows = [
            {"level": 0, "index": 0, "tool": "a", "accepted_skill_ids": ["universal", "x"]},
            {"level": 0, "index": 1, "tool": "b", "accepted_skill_ids": ["universal", "y"]},
            {"level": 0, "index": 2, "tool": "c", "accepted_skill_ids": ["universal"]},
        ]
        result = exact_sparsity_frontier(rows)
        self.assertEqual(result["minimum_feasible_active_packages"], 1)
        self.assertEqual(result["minimum_active_packages_attaining_unrestricted_R_star"], 1)
        self.assertAlmostEqual(float(result["unrestricted_R_star"]), 1.0)
        self.assertEqual(result["frontier"][0]["best_subset"], ["universal"])


if __name__ == "__main__":
    unittest.main()
