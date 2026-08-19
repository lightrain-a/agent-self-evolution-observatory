from __future__ import annotations

import unittest

from .asset_first_stri_reviewer_extensions import analyze_context, single_edge_support_stability


class STRIReviewerExtensionsTest(unittest.TestCase):
    def test_singleton_overlap_dual_and_support_stability(self) -> None:
        rows = [
            {"level": 1, "index": 0, "tool": "a", "accepted_skill_ids": ["s1"]},
            {"level": 1, "index": 1, "tool": "b", "accepted_skill_ids": ["s2"]},
            {"level": 1, "index": 2, "tool": "ab", "accepted_skill_ids": ["s1", "s2"]},
        ]
        out = analyze_context(rows, context_id="positive")
        self.assertAlmostEqual(out["R_star"], 2.0)
        self.assertAlmostEqual(out["dual"]["lower_bound"], 2.0)
        self.assertLessEqual(out["dual"]["primal_dual_gap"], 1e-8)
        self.assertEqual({row["index"] for row in out["dual"]["alpha_rows"]}, {0, 1})
        self.assertEqual({row["index"] for row in out["dual"]["beta_rows"]}, {2})
        semantic = out["semantic_first_neutral_construction"]
        self.assertAlmostEqual(semantic["maximum_semantic_marginal_error"], 0.0)
        self.assertAlmostEqual(semantic["support_violation_mass"], 0.0)
        self.assertAlmostEqual(semantic["kernel_row_sum_min"], 1.0)
        self.assertAlmostEqual(semantic["kernel_row_sum_max"], 1.0)

        stability = out["single_edge_support_stability"]
        self.assertEqual(stability["support_additions"]["perturbations"], 2)
        self.assertEqual(stability["support_deletions_that_keep_row_covered"]["perturbations"], 2)
        self.assertEqual(stability["support_deletions_that_would_uncover_row"], 2)

    def test_umbrella_equalization_can_be_fragile_under_mass_cap(self) -> None:
        rows = [
            {"level": 1, "index": 0, "tool": "a", "accepted_skill_ids": ["s1", "umbrella"]},
            {"level": 1, "index": 1, "tool": "b", "accepted_skill_ids": ["s2", "umbrella"]},
            {"level": 1, "index": 2, "tool": "u", "accepted_skill_ids": ["umbrella"]},
        ]
        out = analyze_context(rows, context_id="umbrella")
        self.assertAlmostEqual(out["R_star"], 1.0)
        self.assertGreater(out["max_share_scan"]["0.750"]["R_star_rho"], 1.0)
        self.assertGreater(out["max_share_scan"]["0.500"]["R_star_rho"], 1.0)

    def test_equalizable_disjoint_support_is_sensitive_to_cross_support_addition(self) -> None:
        rows = [
            {"level": 3, "index": 0, "tool": "a0", "accepted_skill_ids": ["s1"]},
            {"level": 3, "index": 1, "tool": "a1", "accepted_skill_ids": ["s1"]},
            {"level": 3, "index": 2, "tool": "b0", "accepted_skill_ids": ["s2"]},
            {"level": 3, "index": 3, "tool": "b1", "accepted_skill_ids": ["s2"]},
        ]
        out = single_edge_support_stability(rows)
        self.assertAlmostEqual(out["base_R_star"], 1.0)
        self.assertEqual(out["support_additions"]["residual_count"], 4)
        self.assertEqual(out["support_additions"]["same_original_class_count"], 0)


if __name__ == "__main__":
    unittest.main()
