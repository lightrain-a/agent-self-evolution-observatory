from __future__ import annotations

import unittest

from .a2_sequence_qualification import analyze
from .p0_a2 import synthetic_rows


class A2SequenceQualificationTest(unittest.TestCase):
    def test_qualification_rejects_when_learned_controller_never_disagrees_with_tuned_rule(self) -> None:
        result = analyze(synthetic_rows())
        self.assertFalse(result["archetype_pass"])
        self.assertGreaterEqual(result["optimal_round_entropy_bits"], 0.8)
        self.assertEqual(len(result["optimal_round_counts"]), 2)
        self.assertGreaterEqual(result["leave_one_sequence_out_continue_stop_auc"], 0.65)
        self.assertEqual(result["controller_baseline_disagreement_sequences"], 0)
        self.assertFalse(result["controller_disagreement_pass"])
        self.assertFalse(result["pass"])


if __name__ == "__main__":
    unittest.main()
