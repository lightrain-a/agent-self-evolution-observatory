from __future__ import annotations

import unittest

import numpy as np

from .asset_first_stri_certificate import (
    certify,
    dual_global_package_ratio,
    dual_target_package_ratio,
    optimal_global_package_ratio,
    optimal_target_package_ratio,
    robust_interval_package_ratio,
    semantic_first_construction,
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

    def test_nonuniform_target_is_exact_when_target_lies_in_support_cone(self) -> None:
        rows = [
            {"level": 1, "index": 0, "tool": "a", "accepted_skill_ids": ["s1"]},
            {"level": 1, "index": 1, "tool": "b", "accepted_skill_ids": ["s2"]},
            {"level": 1, "index": 2, "tool": "ab", "accepted_skill_ids": ["s1", "s2"]},
        ]
        target = [1.0, 2.0, 3.0]
        primal = optimal_target_package_ratio(rows, target_exposure=target)
        dual = dual_target_package_ratio(rows, target_exposure=target)
        self.assertAlmostEqual(primal["ratio"], 1.0)
        self.assertAlmostEqual(dual["lower_bound"], 1.0)
        self.assertAlmostEqual(primal["weights"]["s1"], 1.0)
        self.assertAlmostEqual(primal["weights"]["s2"], 2.0)
        self.assertFalse(primal["neutral_target"])

    def test_nonuniform_target_outside_support_cone_has_irreducible_distortion(self) -> None:
        rows = [
            {"level": 1, "index": 0, "tool": "a", "accepted_skill_ids": ["s1"]},
            {"level": 1, "index": 1, "tool": "b", "accepted_skill_ids": ["s2"]},
            {"level": 1, "index": 2, "tool": "ab", "accepted_skill_ids": ["s1", "s2"]},
        ]
        target = [1.0, 1.0, 1.5]
        primal = optimal_target_package_ratio(rows, target_exposure=target)
        dual = dual_target_package_ratio(rows, target_exposure=target)
        self.assertGreater(primal["ratio"], 1.0)
        self.assertAlmostEqual(primal["ratio"], dual["lower_bound"])

    def test_duplicate_support_column_preserves_nonuniform_target_certificate(self) -> None:
        base = [
            {"level": 1, "index": 0, "tool": "a", "accepted_skill_ids": ["s1"]},
            {"level": 1, "index": 1, "tool": "b", "accepted_skill_ids": ["s2"]},
            {"level": 1, "index": 2, "tool": "ab", "accepted_skill_ids": ["s1", "s2"]},
        ]
        cloned = [
            {**row, "accepted_skill_ids": list(row["accepted_skill_ids"]) + (["s1_clone"] if "s1" in row["accepted_skill_ids"] else [])}
            for row in base
        ]
        target = [1.0, 1.0, 1.5]
        original = optimal_target_package_ratio(base, target_exposure=target)
        duplicate = optimal_target_package_ratio(cloned, target_exposure=target)
        self.assertAlmostEqual(original["ratio"], duplicate["ratio"])

    def test_box_robust_target_conditioning_reduces_to_nonuniform_point_certificate(self) -> None:
        support = np.asarray([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
        target = [1.0, 2.0, 3.0]
        robust = robust_interval_package_ratio(support, support, skills=["s1", "s2"], target_exposure=target)
        self.assertTrue(robust["pass"])
        self.assertAlmostEqual(robust["ratio"], 1.0)
        self.assertFalse(robust["neutral_target"])

    def test_semantic_first_construction_realizes_arbitrary_target_under_overlap(self) -> None:
        rows = [
            {"level": 1, "index": 0, "tool": "a", "accepted_skill_ids": ["s1"]},
            {"level": 1, "index": 1, "tool": "b", "accepted_skill_ids": ["s2"]},
            {"level": 1, "index": 2, "tool": "ab", "accepted_skill_ids": ["s1", "s2"]},
        ]
        target = [1.0, 2.0, 7.0]
        out = semantic_first_construction(rows, target_exposure=target)
        self.assertTrue(out["pass"])
        self.assertAlmostEqual(out["maximum_semantic_marginal_error"], 0.0)
        self.assertAlmostEqual(out["support_violation_mass"], 0.0)
        self.assertAlmostEqual(out["kernel_row_sum_min"], 1.0)
        self.assertAlmostEqual(out["kernel_row_sum_max"], 1.0)
        self.assertEqual(out["target_distribution"], [0.1, 0.2, 0.7])
        self.assertEqual(out["semantic_marginal"], [0.1, 0.2, 0.7])

    def test_semantic_first_target_survives_exact_support_clone(self) -> None:
        base = [
            {"level": 1, "index": 0, "tool": "a", "accepted_skill_ids": ["s1"]},
            {"level": 1, "index": 1, "tool": "b", "accepted_skill_ids": ["s2"]},
            {"level": 1, "index": 2, "tool": "ab", "accepted_skill_ids": ["s1", "s2"]},
        ]
        cloned = [
            {**row, "accepted_skill_ids": list(row["accepted_skill_ids"]) + (["s1_clone"] if "s1" in row["accepted_skill_ids"] else [])}
            for row in base
        ]
        target = [1.0, 1.0, 1.0]
        before = semantic_first_construction(base, target_exposure=target)
        after = semantic_first_construction(cloned, target_exposure=target)
        self.assertEqual(before["semantic_marginal"], after["semantic_marginal"])
        self.assertAlmostEqual(after["maximum_semantic_marginal_error"], 0.0)
        self.assertIn("s1_clone", after["package_marginal"])


if __name__ == "__main__":
    unittest.main()
