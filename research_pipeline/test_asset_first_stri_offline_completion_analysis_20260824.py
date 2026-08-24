from __future__ import annotations

import unittest

import numpy as np

from .asset_first_stri_offline_completion_analysis_20260824 import (
    classify_ratio,
    package_wide_biases,
    signature_block_relabels,
    synthetic_support_matrix,
    tool_block_package_biases,
)


class STRIOfflineCompletionAnalysisTest(unittest.TestCase):
    def test_classification_is_certificate_based(self) -> None:
        self.assertEqual(classify_ratio(1.0), "EQUALIZABLE")
        self.assertEqual(classify_ratio(2.0), "RESIDUAL")
        self.assertEqual(classify_ratio(None), "FAIL_CLOSED_INVALID_SUPPORT")

    def test_structured_perturbation_families_are_deterministic(self) -> None:
        rows = [
            {"tool": "A"},
            {"tool": "A"},
            {"tool": "B"},
            {"tool": "B"},
        ]
        skills = ["s1", "s2", "s3"]
        A = np.asarray(
            [
                [1.0, 0.0, 0.0],
                [1.0, 1.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 1.0, 1.0],
            ]
        )
        sig1 = signature_block_relabels(A)
        sig2 = signature_block_relabels(A)
        self.assertEqual(sig1, sig2)
        self.assertEqual(len(sig1), 12)  # four observed signatures, ordered pairs
        pkg = package_wide_biases(A, skills)
        self.assertTrue(pkg)
        self.assertTrue(all(row["changed_cells"] > 0 for row in pkg))
        tool = tool_block_package_biases(rows, A, skills)
        self.assertTrue(tool)
        self.assertTrue(all(row["changed_cells"] > 0 for row in tool))

    def test_synthetic_scalability_matrix_is_covered_and_reproducible(self) -> None:
        A1 = synthetic_support_matrix(128, 8, 20260824)
        A2 = synthetic_support_matrix(128, 8, 20260824)
        self.assertTrue(np.array_equal(A1, A2))
        self.assertEqual(A1.shape, (128, 8))
        self.assertTrue(np.all(A1.sum(axis=1) >= 1))
        self.assertTrue(np.all(A1.sum(axis=0) >= 1))
        self.assertTrue(set(np.unique(A1)).issubset({0.0, 1.0}))


if __name__ == "__main__":
    unittest.main()
