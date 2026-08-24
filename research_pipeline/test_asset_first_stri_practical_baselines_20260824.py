from __future__ import annotations

import math
import unittest

from .asset_first_stri_practical_baselines_20260824 import build


class PracticalBaselineSuiteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build()

    def test_regime_inventory(self) -> None:
        regimes = self.payload["regimes"]
        self.assertEqual(set(regimes), {"skillsp_l1_full", "skillsp_l1_calibration", "skillsp_l1_heldout", "skillsp_l3", "logical_compiler"})
        self.assertEqual(regimes["skillsp_l1_full"]["covered_rows"], 314)
        self.assertEqual(regimes["skillsp_l1_calibration"]["covered_rows"], 47)
        self.assertEqual(regimes["skillsp_l1_heldout"]["covered_rows"], 52)
        self.assertEqual(regimes["skillsp_l3"]["covered_rows"], 34)
        self.assertEqual(regimes["logical_compiler"]["covered_rows"], 128)

    def test_level1_headline(self) -> None:
        h = self.payload["headline"]
        self.assertAlmostEqual(h["level1_exact_R_star"], 2.0, places=8)
        self.assertAlmostEqual(h["level1_uniform_ratio"], 2.0, places=8)
        self.assertGreater(h["level1_inverse_support_ratio"], 90.0)
        self.assertGreater(h["level1_inverse_sqrt_ratio"], 10.0)
        self.assertGreater(h["level1_nnls_ratio"], 5.0)
        self.assertLess(h["level1_nnls_cv"], h["level1_uniform_cv"])

    def test_negative_regimes_are_equalizable(self) -> None:
        for regime in ("skillsp_l3", "logical_compiler"):
            rows = {x["baseline"]: x for x in self.payload["regimes"][regime]["baselines"]}
            self.assertAlmostEqual(rows["exact_rstar"]["metrics"]["distortion_ratio"], 1.0, places=8)
            self.assertAlmostEqual(rows["semantic_first_upper_bound"]["metrics"]["distortion_ratio"], 1.0, places=8)

    def test_calibration_to_heldout_is_no_refit(self) -> None:
        transfer = self.payload["calibration_to_heldout"]
        self.assertTrue(transfer["no_heldout_refit"])
        rows = {x["baseline"]: x for x in transfer["results"]}
        self.assertAlmostEqual(rows["released_uniform"]["heldout_metrics"]["distortion_ratio"], 2.0, places=8)
        self.assertAlmostEqual(rows["exact_rstar"]["heldout_metrics"]["distortion_ratio"], 2.0, places=8)
        self.assertEqual(transfer["train_skills"], transfer["test_skills"])

    def test_no_model_or_gpu_calls(self) -> None:
        self.assertEqual(self.payload["new_model_calls"], 0)
        self.assertEqual(self.payload["new_gpu_runs"], 0)
        self.assertFalse(self.payload["claim_expansion"])


if __name__ == "__main__":
    unittest.main()
