from __future__ import annotations

import unittest

import numpy as np

from .asset_first_stri_certificate import (
    certify,
    dual_global_package_ratio,
    optimal_global_package_ratio,
    robust_interval_package_ratio,
)


class STRICertificateTest(unittest.TestCase):
    def test_global_singleton_overlap_certifies_irreducible_residual(self) -> None:
        rows = [
            {"level": 1, "index": 0, "tool": "a", "accepted_skill_ids": ["s1"]},
            {"level": 1, "index": 1, "tool": "b", "accepted_skill_ids": ["s2"]},
            {"level": 1, "index": 2, "tool": "ab", "accepted_skill_ids": ["s1", "s2"]},
        ]
        out = certify(rows, context_id="positive")
        self.assertEqual(out["decision"], "CERTIFIED_IRREDUCIBLE_PACKAGE_ONLY_REPRESENTATION_RESIDUAL_WITH_CLOSED_FORM_WITNESS")
        self.assertEqual(out["structural_witness"]["witness_count"], 1)
        self.assertAlmostEqual(out["structural_witness"]["global_nonnegative_package_weight_exposure_ratio_lower_bound"], 2.0)
        self.assertAlmostEqual(out["optimal_global_package_weighting"]["ratio"], 2.0)
        self.assertTrue(out["tight_lower_bound"])

    def test_disjoint_support_is_equalizable_negative_control(self) -> None:
        rows = [
            {"level": 3, "index": 0, "tool": "a", "accepted_skill_ids": ["s1"]},
            {"level": 3, "index": 1, "tool": "b", "accepted_skill_ids": ["s2"]},
            {"level": 3, "index": 2, "tool": "c", "accepted_skill_ids": ["s1"]},
        ]
        out = certify(rows, context_id="negative")
        self.assertEqual(out["decision"], "CERTIFIED_PACKAGE_ONLY_EQUALIZABLE_NEGATIVE_CONTROL")
        self.assertEqual(out["negative_control_subtype"], "DISJOINT_SUPPORT")
        self.assertEqual(out["multi_membership_rows"], 0)
        self.assertAlmostEqual(out["optimal_global_package_weighting"]["ratio"], 1.0)

    def test_overlap_can_still_be_globally_equalizable_via_umbrella_skill(self) -> None:
        rows = [
            {"level": 1, "index": 0, "tool": "a", "accepted_skill_ids": ["s1", "umbrella"]},
            {"level": 1, "index": 1, "tool": "b", "accepted_skill_ids": ["s2", "umbrella"]},
            {"level": 1, "index": 2, "tool": "u", "accepted_skill_ids": ["umbrella"]},
        ]
        out = certify(rows, context_id="overlap-equalizable")
        self.assertEqual(out["structural_witness"]["witness_count"], 0)
        self.assertEqual(out["decision"], "CERTIFIED_PACKAGE_ONLY_EQUALIZABLE_NEGATIVE_CONTROL")
        self.assertEqual(out["negative_control_subtype"], "OVERLAP_BUT_GLOBALLY_EQUALIZABLE")
        self.assertAlmostEqual(out["optimal_global_package_weighting"]["ratio"], 1.0)

    def test_lp_can_certify_residual_without_closed_form_witness(self) -> None:
        rows = [
            {"level": 1, "index": 0, "tool": "ab", "accepted_skill_ids": ["s1", "s2"]},
            {"level": 1, "index": 1, "tool": "bc", "accepted_skill_ids": ["s2", "s3"]},
            {"level": 1, "index": 2, "tool": "ac", "accepted_skill_ids": ["s1", "s3"]},
            {"level": 1, "index": 3, "tool": "abc", "accepted_skill_ids": ["s1", "s2", "s3"]},
        ]
        out = certify(rows, context_id="lp-only")
        self.assertEqual(out["structural_witness"]["witness_count"], 0)
        self.assertEqual(out["decision"], "CERTIFIED_IRREDUCIBLE_PACKAGE_ONLY_REPRESENTATION_RESIDUAL_BY_EXACT_LP")
        self.assertGreater(out["optimal_global_package_weighting"]["ratio"], 1.0)
        dual = dual_global_package_ratio(rows)
        self.assertTrue(dual["pass"])
        self.assertAlmostEqual(dual["lower_bound"], out["optimal_global_package_weighting"]["ratio"])
        self.assertGreater(len(dual["alpha_rows"]), 0)
        self.assertGreater(len(dual["beta_rows"]), 0)

    def test_dual_recovers_factor_two_singleton_witness(self) -> None:
        rows = [
            {"level": 1, "index": 0, "tool": "a", "accepted_skill_ids": ["s1"]},
            {"level": 1, "index": 1, "tool": "b", "accepted_skill_ids": ["s2"]},
            {"level": 1, "index": 2, "tool": "ab", "accepted_skill_ids": ["s1", "s2"]},
        ]
        dual = dual_global_package_ratio(rows)
        self.assertAlmostEqual(dual["lower_bound"], 2.0)
        self.assertAlmostEqual(dual["sum_beta"], 1.0)
        self.assertEqual({row["index"] for row in dual["alpha_rows"]}, {0, 1})
        self.assertEqual({row["index"] for row in dual["beta_rows"]}, {2})

    def test_max_share_constraint_can_expose_concentrated_umbrella_equalization(self) -> None:
        rows = [
            {"level": 1, "index": 0, "tool": "a", "accepted_skill_ids": ["s1", "umbrella"]},
            {"level": 1, "index": 1, "tool": "b", "accepted_skill_ids": ["s2", "umbrella"]},
            {"level": 1, "index": 2, "tool": "u", "accepted_skill_ids": ["umbrella"]},
        ]
        unrestricted = optimal_global_package_ratio(rows)
        capped = optimal_global_package_ratio(rows, max_share=0.5)
        self.assertAlmostEqual(unrestricted["ratio"], 1.0)
        self.assertTrue(capped["pass"])
        self.assertGreater(capped["ratio"], 1.0)
        self.assertLessEqual(capped["attained_max_share"], 0.5 + 1e-9)

    def test_box_robust_lp_reduces_to_exact_certificate_for_point_support(self) -> None:
        support = np.asarray([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
        robust = robust_interval_package_ratio(support, support, skills=["s1", "s2"])
        self.assertTrue(robust["pass"])
        self.assertAlmostEqual(robust["ratio"], 2.0)


if __name__ == "__main__":
    unittest.main()
