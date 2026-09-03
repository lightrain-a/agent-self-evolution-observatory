from __future__ import annotations

import itertools
import unittest

from research_pipeline.e2_r17_regeneration_metrics_v2 import compute_regeneration_metrics_v2


SHA_A = "a" * 64
SHA_B = "b" * 64
TASK = "r17-b4-tsr-p0"


def _scores(ff_r1: int, ff_r2: int) -> dict[str, dict[str, int]]:
    return {
        "ff_hist": {TASK: 1},
        "ff_r1": {TASK: ff_r1},
        "ff_r2": {TASK: ff_r2},
        "win_common": {TASK: 0},
    }


class RegenerationMetricsV2Test(unittest.TestCase):
    def test_stable_distinct_states_give_positive_excess(self) -> None:
        m = compute_regeneration_metrics_v2(
            original_ff_r1={TASK: 1},
            original_ff_r2={TASK: 0},
            new_scores=_scores(1, 0),
            ff_r1_sha256=SHA_A,
            ff_r2_sha256=SHA_B,
        )
        self.assertEqual(m.d_cross_state, 1.0)
        self.assertEqual(m.d_within_actor, 0.0)
        self.assertEqual(m.e_real, 1.0)
        self.assertTrue(m.regeneration_localization_support)

    def test_actor_flip_noise_does_not_masquerade_as_state_separation(self) -> None:
        m = compute_regeneration_metrics_v2(
            original_ff_r1={TASK: 1},
            original_ff_r2={TASK: 1},
            new_scores=_scores(0, 0),
            ff_r1_sha256=SHA_A,
            ff_r2_sha256=SHA_B,
        )
        self.assertEqual(m.d_cross_state, 0.5)
        self.assertEqual(m.d_within_actor, 1.0)
        self.assertEqual(m.e_real, -0.5)
        self.assertFalse(m.regeneration_localization_support)

    def test_identical_state_sha_forces_zero_realization_contrast(self) -> None:
        m = compute_regeneration_metrics_v2(
            original_ff_r1={TASK: 1},
            original_ff_r2={TASK: 0},
            new_scores=_scores(1, 0),
            ff_r1_sha256=SHA_A,
            ff_r2_sha256=SHA_A,
        )
        self.assertTrue(m.state_sha_alias)
        self.assertEqual(m.e_real, 0.0)
        self.assertFalse(m.regeneration_localization_support)

    def test_expected_excess_equals_squared_probability_difference(self) -> None:
        # Exhaustively average the four binary actor outcomes under fixed
        # Bernoulli p_A/p_B. This locks the prospective interpretation:
        # E[D_X-D_A] = (p_A-p_B)^2 for one task.
        for p_a, p_b in ((0.2, 0.8), (0.4, 0.6), (0.6, 0.9), (0.5, 0.5)):
            expected = 0.0
            for a1, a2, b1, b2 in itertools.product((0, 1), repeat=4):
                prob = (
                    (p_a if a1 else 1 - p_a)
                    * (p_a if a2 else 1 - p_a)
                    * (p_b if b1 else 1 - p_b)
                    * (p_b if b2 else 1 - p_b)
                )
                m = compute_regeneration_metrics_v2(
                    original_ff_r1={TASK: a1},
                    original_ff_r2={TASK: b1},
                    new_scores=_scores(a2, b2),
                    ff_r1_sha256=SHA_A,
                    ff_r2_sha256=SHA_B,
                )
                expected += prob * m.e_real
            self.assertAlmostEqual(expected, (p_a - p_b) ** 2, places=12)

    def test_task_set_drift_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            compute_regeneration_metrics_v2(
                original_ff_r1={TASK: 1},
                original_ff_r2={"r17-b4-tsr-p6": 0},
                new_scores=_scores(1, 0),
                ff_r1_sha256=SHA_A,
                ff_r2_sha256=SHA_B,
            )

    def test_common_win_and_historical_state_remain_descriptive_outputs(self) -> None:
        m = compute_regeneration_metrics_v2(
            original_ff_r1={TASK: 1},
            original_ff_r2={TASK: 0},
            new_scores=_scores(1, 0),
            ff_r1_sha256=SHA_A,
            ff_r2_sha256=SHA_B,
        )
        self.assertEqual(m.new_success_rates["ff_hist"], 1.0)
        self.assertEqual(m.new_success_rates["win_common"], 0.0)
        self.assertEqual(m.new_ff_minus_common_win["ff_hist"], 1.0)


if __name__ == "__main__":
    unittest.main()
