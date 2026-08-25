from __future__ import annotations

import unittest

from .asset_first_stri_r2_partition_geometry_20260825 import build, stars_bars, weak_composition_count_dp


class StriR2PartitionGeometryTest(unittest.TestCase):
    def test_dp_matches_closed_form_on_small_counts(self) -> None:
        for k in range(2, 5):
            for n in range(0, 15):
                for m in range(0, 4):
                    self.assertEqual(weak_composition_count_dp(n, k, m), stars_bars(n, k, m))

    def test_guaranteed_fragmentation_region_is_universal(self) -> None:
        result = build()
        self.assertTrue(result["pass_gate"])
        self.assertEqual(result["decision"], "PASS_ARBITRARY_PARTITION_GEOMETRY")
        for row in result["rows"]:
            if row["region"] == "GUARANTEED_FRAGMENTATION":
                self.assertEqual(row["fragmentation_fraction"], 1.0)

    def test_tail_is_partition_dependent(self) -> None:
        result = build()
        tail = [row for row in result["rows"] if row["region"] == "PARTITION_DEPENDENT_TAIL"]
        self.assertTrue(any(0.0 < row["fragmentation_fraction"] < 1.0 for row in tail))
        self.assertEqual(result["headline"]["formula_mismatches"], 0)
        self.assertEqual(result["headline"]["guaranteed_region_failures"], 0)


if __name__ == "__main__":
    unittest.main()
