from __future__ import annotations

import unittest

from research_pipeline.asset_first_stri_structural_witness import structural_lower_bound


class StructuralWitnessTest(unittest.TestCase):
    def test_mandatory_overlap_implies_ratio_two(self) -> None:
        rows = [
            {"accepted_skill_ids": ["a"], "level": 1, "index": 0, "tool": "ua"},
            {"accepted_skill_ids": ["b"], "level": 1, "index": 1, "tool": "ub"},
            {"accepted_skill_ids": ["a", "b"], "level": 1, "index": 2, "tool": "ab"},
        ]
        out = structural_lower_bound(rows, {"a", "b"})
        self.assertEqual(out["witness_count"], 1)
        self.assertEqual(out["global_nonnegative_package_weight_exposure_ratio_lower_bound"], 2.0)

    def test_overlap_without_two_unique_regions_does_not_certify(self) -> None:
        rows = [
            {"accepted_skill_ids": ["a"], "level": 1, "index": 0, "tool": "ua"},
            {"accepted_skill_ids": ["a", "b"], "level": 1, "index": 1, "tool": "ab"},
        ]
        out = structural_lower_bound(rows, {"a", "b"})
        self.assertEqual(out["witness_count"], 0)
        self.assertIsNone(out["global_nonnegative_package_weight_exposure_ratio_lower_bound"])


if __name__ == "__main__":
    unittest.main()
