from __future__ import annotations

import unittest

from .failure_memory_memrl_g5_runtime_adjudication_r41 import build, validate


class MemRLG5RuntimeAdjudicationR41Test(unittest.TestCase):
    def setUp(self) -> None:
        self.d = build()

    def test_runtime_support_closes_historical_g5_without_execution_authority(self) -> None:
        g = self.d["historical_r39_r40_gate_adjudication"]
        self.assertTrue(g["G5_SUPPORT_AND_PREREGISTRATION"])
        self.assertFalse(g["G6_AUTHORITY"])
        self.assertTrue(self.d["runtime_support"]["native_osinteraction_container_lifecycle_pass"])
        self.assertTrue(self.d["runtime_support"]["training_support_evaluator_replay_pass"])
        self.assertFalse(self.d["runtime_support"]["validation_split_executed"])
        self.assertFalse(self.d["runtime_support"]["confirmatory_outcome_observed"])

    def test_support_image_cannot_be_promoted_to_confirmatory_image(self) -> None:
        r = self.d["runtime_support"]
        self.assertFalse(r["support_image_is_final_confirmatory_image"])
        self.assertFalse(r["source_faithful_confirmatory_image_frozen"])
        self.assertTrue(self.d["current_program_boundary"]["confirmatory_image_must_be_frozen_before_first_validation_treatment_outcome"])

    def test_no_scientific_or_execution_authority_leaks(self) -> None:
        self.assertFalse(any(self.d["authority"].values()))
        self.assertEqual(self.d["access_accounting"]["confirmatory_validation_tasks_executed"], 0)
        self.assertEqual(self.d["access_accounting"]["confirmatory_treatment_outcomes_observed"], 0)
        self.assertEqual(validate(self.d), [])


if __name__ == "__main__":
    unittest.main()
