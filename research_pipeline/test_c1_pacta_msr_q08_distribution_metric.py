from __future__ import annotations

import math
import unittest

from research_pipeline.c1_pacta_msr_q08_distribution_metric import (
    calibrate_threshold,
    exact_match_mmd2_unbiased,
)


class C1PactaMsrQ08DistributionMetricTest(unittest.TestCase):
    def test_mmd2_is_zero_for_identical_deterministic_samples(self):
        x = ["git status"] * 6
        self.assertAlmostEqual(exact_match_mmd2_unbiased(x, x), 0.0)

    def test_mmd2_is_two_for_disjoint_deterministic_samples(self):
        x = ["git status"] * 6
        y = ["pytest -q"] * 6
        self.assertAlmostEqual(exact_match_mmd2_unbiased(x, y), 2.0)

    def test_mmd2_can_be_negative_finite_sample_and_is_not_clipped(self):
        # Unbiased U-statistics can be negative at finite n; clipping would
        # reintroduce positive null bias and is therefore forbidden.
        x = ["a", "a", "a", "b", "b", "b"]
        y = ["a", "a", "a", "b", "b", "b"]
        self.assertLess(exact_match_mmd2_unbiased(x, y), 0.0)

    def test_q08_synthetic_calibration_refreezes_threshold_without_provider_calls(self):
        result = calibrate_threshold()
        self.assertEqual(result["status"], "Q08_UNBIASED_MMD2_SYNTHETIC_CALIBRATION_PASS")
        self.assertAlmostEqual(result["selected_mean_D_select_threshold"], 0.20)
        self.assertEqual(result["scientific_provider_calls"], 0)
        self.assertEqual(result["scientific_outcomes_read"], 0)
        selected = next(row for row in result["rows"] if math.isclose(row["threshold"], 0.20))
        self.assertTrue(selected["passes"])
        self.assertLessEqual(selected["worst_null_gate_rate"], 0.05)
        self.assertGreaterEqual(selected["canonical_alt_gate_rate"], 0.45)
        lower = next(row for row in result["rows"] if math.isclose(row["threshold"], 0.15))
        self.assertFalse(lower["passes"])


if __name__ == "__main__":
    unittest.main()
