from __future__ import annotations

import unittest

from .failure_memory_memrl_current_gate_r42 import build, validate


class MemRLCurrentGateR42Test(unittest.TestCase):
    def setUp(self) -> None:
        self.d = build()

    def test_current_gate_recompile_passes_g1_through_g7_only(self) -> None:
        g = self.d["current_gate_adjudication"]
        self.assertTrue(all(g[k]["pass"] is True for k in ("G1", "G2", "G3", "G4", "G5", "G6", "G7")))
        self.assertFalse(g["G8"]["pass"])
        self.assertEqual(self.d["summary"]["passed"], 7)
        self.assertEqual(self.d["summary"]["blocking_gates"], ["G8"])

    def test_no_confirmatory_outcome_or_authority_is_created(self) -> None:
        self.assertEqual(self.d["summary"]["confirmatory_validation_outcomes_observed"], 0)
        self.assertFalse(any(self.d["authority"].values()))
        self.assertFalse(self.d["runtime_candidate"]["final_confirmatory_image_frozen"])

    def test_gate_is_structurally_valid(self) -> None:
        self.assertEqual(validate(self.d), [])
        self.assertEqual(self.d["summary"]["total"], 8)


if __name__ == "__main__":
    unittest.main()
