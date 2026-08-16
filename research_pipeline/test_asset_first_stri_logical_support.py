from __future__ import annotations

import unittest

from .asset_first_stri_logical_support import classify_certificate


class STRILogicalSupportTest(unittest.TestCase):
    def test_invalid_units_fail_closed(self) -> None:
        cert = {"multi_membership_rows": 4, "optimal_global_package_weighting": {"ratio": 2.0}}
        self.assertEqual(classify_certificate(all_source_units_valid=False, certificate=cert), "INVALID_FIRST_PARTY_SUBSTRATE")

    def test_overlap_with_lp_residual_is_positive_even_without_simple_witness(self) -> None:
        cert = {"multi_membership_rows": 7, "optimal_global_package_weighting": {"ratio": 1.25}}
        self.assertEqual(classify_certificate(all_source_units_valid=True, certificate=cert), "CROSS_DOMAIN_PACKAGE_ONLY_RESIDUAL")

    def test_equalizable_support_is_negative_boundary(self) -> None:
        cert = {"multi_membership_rows": 0, "optimal_global_package_weighting": {"ratio": 1.0}}
        self.assertEqual(classify_certificate(all_source_units_valid=True, certificate=cert), "DISJOINT_OR_EQUALIZABLE_NEGATIVE_CONTROL")

    def test_missing_lp_is_unresolved(self) -> None:
        cert = {"multi_membership_rows": 2, "optimal_global_package_weighting": {"ratio": None}}
        self.assertEqual(classify_certificate(all_source_units_valid=True, certificate=cert), "UNRESOLVED_SUPPORT_TOPOLOGY")


if __name__ == "__main__":
    unittest.main()
