from __future__ import annotations

import unittest

from research_pipeline.e2_r17_state_compiler_bridge_v4_analysis import (
    diagnosis_control_classification,
    excess_state_realization_disagreement,
    first_realization_generator_contrast,
    generator_method_gate,
    realization_averaged_sensitivity,
    realization_localization_gate,
)


class StateCompilerBridgeV4AnalysisTest(unittest.TestCase):
    def test_generic_control_failure_does_not_veto_raw_generator_gate(self) -> None:
        raw = generator_method_gate([0.20, 0.10, 0.05, 0.04, -0.01, -0.02])
        interpretation = diagnosis_control_classification(
            score_only_advantages=[0.05] * 6,
            scope_matched_advantages=[-0.01] * 6,
        )
        self.assertTrue(raw.passed)
        self.assertFalse(interpretation.trajectory_conditioned_diagnosis_supported)
        self.assertEqual("SCOPE_OR_SPARSITY_CANONICALIZATION_ONLY", interpretation.label)

    def test_controls_can_support_typed_diagnosis_without_defining_generator_effect(self) -> None:
        raw = generator_method_gate([-0.05, -0.04, -0.03, 0.01, 0.01, 0.01])
        interpretation = diagnosis_control_classification(
            score_only_advantages=[0.10] * 6,
            scope_matched_advantages=[0.05] * 6,
        )
        self.assertFalse(raw.passed)
        self.assertTrue(interpretation.trajectory_conditioned_diagnosis_supported)

    def test_primary_validation_estimand_uses_first_free_realization_only(self) -> None:
        self.assertAlmostEqual(first_realization_generator_contrast(0.8, 0.5), 0.3)
        self.assertAlmostEqual(realization_averaged_sensitivity(0.8, 0.5, 0.9), 0.1)
        # The second draw can change sensitivity without changing the primary estimand.
        self.assertAlmostEqual(first_realization_generator_contrast(0.8, 0.5), 0.3)

    def test_cross_state_excess_detects_stable_state_level_difference(self) -> None:
        excess = excess_state_realization_disagreement(
            free_a_skill_sha256="a" * 64,
            free_b_skill_sha256="b" * 64,
            a1=[1, 1, 1, 1],
            a2=[1, 1, 1, 1],
            b1=[0, 0, 0, 0],
            b2=[0, 0, 0, 0],
        )
        self.assertEqual(1.0, excess)

    def test_identical_free_state_sha_forces_realization_effect_to_zero(self) -> None:
        excess = excess_state_realization_disagreement(
            free_a_skill_sha256="a" * 64,
            free_b_skill_sha256="a" * 64,
            a1=[1, 1, 0, 0],
            a2=[0, 1, 1, 0],
            b1=[0, 0, 1, 1],
            b2=[1, 0, 0, 1],
        )
        self.assertEqual(0.0, excess)

    def test_realization_localization_is_separate_six_stream_gate(self) -> None:
        gate = realization_localization_gate([0.20, 0.10, 0.05, 0.02, -0.01, -0.01])
        self.assertTrue(gate.passed)
        self.assertEqual(4, gate.positive_units)


if __name__ == "__main__":
    unittest.main()
