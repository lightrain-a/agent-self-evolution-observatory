from __future__ import annotations

import json
import unittest
from pathlib import Path

from .asset_first_stri_r2_credit_fragmentation_theory_20260825 import (
    EvidenceStats,
    arbitrary_partition_fragmented,
    balanced_eligible_partition,
    balanced_full_retirement_threshold,
    balanced_retirement_lag,
    lifecycle_homomorphism_holds,
    native_class_decision,
    quotient_class_decision,
    threshold_fragmentation_window,
    theorem_summary,
)

ROOT = Path(__file__).resolve().parents[1]
PHASE = ROOT / "generated/asset-first-stri-r2-credit-fragmentation-phase-result-20260825.json"
P0 = ROOT / "generated/asset-first-stri-r2-credit-fragmentation-result-20260825.json"


class CreditFragmentationTheoryTest(unittest.TestCase):
    def test_single_identity_always_commutes_for_threshold_gate(self) -> None:
        for n in range(0, 40):
            parts = balanced_eligible_partition(n, 1)
            self.assertTrue(lifecycle_homomorphism_holds(parts, min_attempts=8))

    def test_balanced_threshold_fragmentation_window(self) -> None:
        for k in range(2, 7):
            window = threshold_fragmentation_window(multiplicity=k, min_attempts=8)
            self.assertEqual(window, (8, 8 * k - 1))
            for n in range(0, 8 * k + 3):
                parts = balanced_eligible_partition(n, k)
                q = quotient_class_decision(parts, min_attempts=8)
                native = native_class_decision(parts, min_attempts=8)
                self.assertEqual(q and not native, 8 <= n < 8 * k)
            self.assertEqual(balanced_full_retirement_threshold(multiplicity=k, min_attempts=8), 8 * k)
            self.assertEqual(balanced_retirement_lag(multiplicity=k, min_attempts=8), 8 * (k - 1))

    def test_arbitrary_partition_condition(self) -> None:
        self.assertTrue(arbitrary_partition_fragmented((EvidenceStats(7, 7), EvidenceStats(1, 1)), min_attempts=8))
        self.assertTrue(arbitrary_partition_fragmented((EvidenceStats(8, 8), EvidenceStats(7, 7)), min_attempts=8))
        self.assertFalse(arbitrary_partition_fragmented((EvidenceStats(8, 8), EvidenceStats(8, 8)), min_attempts=8))
        self.assertFalse(arbitrary_partition_fragmented((EvidenceStats(4, 4), EvidenceStats(3, 3)), min_attempts=8))

    def test_phase_grid_matches_theorem_exactly(self) -> None:
        phase = json.loads(PHASE.read_text(encoding="utf-8"))
        self.assertEqual(phase["decision"], "PASS_CREDIT_FRAGMENTATION_PHASE_DIAGRAM")
        self.assertEqual(phase["headline"]["analytic_mismatches"], 0)
        self.assertEqual(phase["grid"]["cells"], 882)
        for row in phase["rows"]:
            if float(row["p_hat"]) != 0.90:
                continue
            k, n = int(row["k"]), int(row["N"])
            parts = balanced_eligible_partition(n, k)
            self.assertEqual(row["native_class_active"], not native_class_decision(parts, min_attempts=8))
            self.assertEqual(row["quotient_credit_class_active"], not quotient_class_decision(parts, min_attempts=8))

    def test_released_p0_is_one_point_in_the_phase_theorem(self) -> None:
        p0 = json.loads(P0.read_text(encoding="utf-8"))
        self.assertEqual(p0["decision"], "PASS_RELEASED_CREDIT_FRAGMENTATION_MECHANISM")
        parts = balanced_eligible_partition(8, 2)
        self.assertTrue(quotient_class_decision(parts, min_attempts=8))
        self.assertFalse(native_class_decision(parts, min_attempts=8))
        self.assertFalse(p0["arms"]["A_canonical_native"]["focal_semantic_class_active"])
        self.assertTrue(p0["arms"]["B_split2_native"]["focal_semantic_class_active"])
        self.assertFalse(p0["arms"]["C_split2_quotient_credit"]["focal_semantic_class_active"])

    def test_theorem_boundary_is_explicit(self) -> None:
        summary = theorem_summary()
        self.assertIn("nonlinear lifecycle decision", summary["important_boundary"])
        self.assertIn("does not assert endogenous prevalence", summary["claim_scope"])
        self.assertFalse(summary["scientific_authority"])


if __name__ == "__main__":
    unittest.main()
