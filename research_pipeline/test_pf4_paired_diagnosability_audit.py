from __future__ import annotations

import unittest

from .pf4_paired_diagnosability_audit import decompose_drop


class PF4PairedDiagnosabilityAuditTest(unittest.TestCase):
    def test_unpaired_drop_decomposes_into_composition_and_paired_change(self) -> None:
        row = decompose_drop(2 / 3, 1 / 2, 1 / 2)
        self.assertAlmostEqual(row["legacy_unpaired_drop"], 1 / 6)
        self.assertAlmostEqual(row["cohort_composition_term"], 1 / 6)
        self.assertAlmostEqual(row["paired_causal_drop"], 0.0)
        self.assertAlmostEqual(row["legacy_unpaired_drop"], row["reconstructed_drop"])

    def test_paired_improvement_cannot_be_called_diagnostic_degradation(self) -> None:
        row = decompose_drop(2 / 3, 4 / 5, 1.0)
        self.assertLess(row["paired_causal_drop"], 0.0)
        self.assertAlmostEqual(row["legacy_unpaired_drop"], row["cohort_composition_term"] + row["paired_causal_drop"])


if __name__ == "__main__":
    unittest.main()
