from __future__ import annotations

import unittest

from research_pipeline.e2_r17_state_compiler_bridge_v4_analysis import (
    diagnosis_control_classification,
    excess_state_realization_disagreement,
    first_realization_generator_contrast,
    generator_factorial_main_effect,
    generator_factorial_main_effect_sha_aware,
    generator_factorial_main_effect_sensitivity,
    generator_method_gate,
    realization_averaged_sensitivity,
    realization_localization_gate,
    state_sha_aware_contrast,
    within_source_generator_contrast_sha_aware,
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
        self.assertEqual("FF4_SCOPE_OR_SPARSITY_CANONICALIZATION_ONLY", interpretation.label)

    def test_controls_can_support_typed_diagnosis_without_defining_generator_effect(self) -> None:
        raw = generator_method_gate([-0.05, -0.04, -0.03, 0.01, 0.01, 0.01])
        interpretation = diagnosis_control_classification(
            score_only_advantages=[0.10] * 6,
            scope_matched_advantages=[0.05] * 6,
        )
        self.assertFalse(raw.passed)
        self.assertTrue(interpretation.trajectory_conditioned_diagnosis_supported)

    def test_primary_factorial_generator_effect_uses_both_evidence_sources_and_free_a(self) -> None:
        primary = generator_factorial_main_effect(
            winner_compiled_utility=0.7,
            winner_free_utility=0.5,
            ff4_compiled_utility=0.8,
            ff4_free_a_utility=0.5,
        )
        self.assertAlmostEqual(primary, 0.25)
        self.assertAlmostEqual(first_realization_generator_contrast(0.8, 0.5), 0.3)

    def test_free_b_changes_sensitivity_without_changing_primary_factorial_estimand(self) -> None:
        primary = generator_factorial_main_effect(
            winner_compiled_utility=0.7,
            winner_free_utility=0.5,
            ff4_compiled_utility=0.8,
            ff4_free_a_utility=0.5,
        )
        sensitivity = generator_factorial_main_effect_sensitivity(
            winner_compiled_utility=0.7,
            winner_free_utility=0.5,
            ff4_compiled_utility=0.8,
            ff4_free_a_utility=0.5,
            ff4_free_b_utility=0.9,
        )
        self.assertAlmostEqual(primary, 0.25)
        self.assertAlmostEqual(sensitivity, 0.15)
        self.assertAlmostEqual(realization_averaged_sensitivity(0.8, 0.5, 0.9), 0.1)

    def test_universal_sha_alias_forces_zero_for_free_comp_or_generic_pairs(self) -> None:
        digest = "a" * 64
        self.assertEqual(
            0.0,
            state_sha_aware_contrast(
                left_skill_sha256=digest,
                left_utility=1.0,
                right_skill_sha256=digest,
                right_utility=0.0,
            ),
        )
        self.assertEqual(
            0.0,
            within_source_generator_contrast_sha_aware(
                compiled_skill_sha256=digest,
                compiled_utility=1.0,
                free_skill_sha256=digest,
                free_utility=0.0,
            ),
        )

    def test_primary_factorial_effect_collapses_each_aliased_source_before_average(self) -> None:
        main = generator_factorial_main_effect_sha_aware(
            winner_compiled_skill_sha256="a" * 64,
            winner_compiled_utility=0.9,
            winner_free_skill_sha256="a" * 64,
            winner_free_utility=0.1,
            ff4_compiled_skill_sha256="b" * 64,
            ff4_compiled_utility=0.8,
            ff4_free_a_skill_sha256="c" * 64,
            ff4_free_a_utility=0.4,
        )
        self.assertAlmostEqual(main, 0.2)

    def test_primary_generator_main_effect_can_pass_without_ff4_specific_superiority(self) -> None:
        # Winner-side generator benefit can establish a positive balanced factor
        # effect even when FF4-specific generator contrast is slightly negative.
        main = generator_factorial_main_effect(
            winner_compiled_utility=0.9,
            winner_free_utility=0.5,
            ff4_compiled_utility=0.5,
            ff4_free_a_utility=0.55,
        )
        self.assertGreater(main, 0.0)
        self.assertLess(first_realization_generator_contrast(0.5, 0.55), 0.0)

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
