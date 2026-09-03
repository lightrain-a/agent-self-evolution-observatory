from __future__ import annotations

import json
import unittest
from pathlib import Path

from research_pipeline.e2_r17_regeneration_metrics import compute_regeneration_metrics


ROOT = Path(__file__).resolve().parents[1]
FROZEN_REPLAY_ANALYSIS = ROOT / "generated/e2-r17-single-case-first-fail-exact-replay-measurement-analysis-20260902.json"


class RegenerationMetricsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.replay = json.loads(FROZEN_REPLAY_ANALYSIS.read_text(encoding="utf-8"))
        cls.a1 = cls.replay["task_level_scores"]["1"]["first_fail"]
        cls.b1 = cls.replay["task_level_scores"]["2"]["first_fail"]

    def test_frozen_original_task_sets_are_identical_18(self) -> None:
        self.assertEqual(set(self.a1), set(self.b1))
        self.assertEqual(len(self.a1), 18)

    def test_zero_between_state_when_new_measurements_make_states_identical(self) -> None:
        # If both new frozen states exactly equal their respective original states
        # and A/B originals are still different, the statistic captures persistent
        # between-state disagreement rather than creating it from an extra draw.
        new = {
            "ff_hist": dict(self.a1),
            "ff_r1": dict(self.a1),
            "ff_r2": dict(self.b1),
            "win_common": dict(self.a1),
        }
        result = compute_regeneration_metrics(
            original_ff_r1=self.a1,
            original_ff_r2=self.b1,
            new_scores=new,
        )
        self.assertGreaterEqual(result.d_between_state, 0.0)
        self.assertEqual(result.d_within_actor, 0.0)
        self.assertEqual(result.d_regeneration_minus_actor, result.d_between_state)
        self.assertEqual(len(result.task_ids), 18)
        self.assertEqual(set(result.family_diagnostics), {"agj", "fmv", "ioc", "msp", "ska", "tsr"})

    def test_actor_flip_noise_can_dominate_regeneration(self) -> None:
        # Make each new FF measurement the complement of its original. Then both
        # actor-averaged states are 0.5 on every task while within-state actor
        # disagreement is maximal, so the regeneration diagnostic must fail.
        flip_a = {task: 1 - value for task, value in self.a1.items()}
        flip_b = {task: 1 - value for task, value in self.b1.items()}
        new = {
            "ff_hist": dict(self.a1),
            "ff_r1": flip_a,
            "ff_r2": flip_b,
            "win_common": dict(self.a1),
        }
        result = compute_regeneration_metrics(
            original_ff_r1=self.a1,
            original_ff_r2=self.b1,
            new_scores=new,
        )
        self.assertEqual(result.d_between_state, 0.0)
        self.assertEqual(result.d_within_actor, 1.0)
        self.assertEqual(result.d_regeneration_minus_actor, -1.0)
        self.assertFalse(result.regeneration_support)

    def test_new_common_win_contrasts_are_contemporaneous(self) -> None:
        all_zero = {task: 0 for task in self.a1}
        all_one = {task: 1 for task in self.a1}
        new = {
            "ff_hist": all_one,
            "ff_r1": all_one,
            "ff_r2": all_zero,
            "win_common": all_zero,
        }
        result = compute_regeneration_metrics(
            original_ff_r1=self.a1,
            original_ff_r2=self.b1,
            new_scores=new,
        )
        self.assertEqual(result.new_ff_minus_common_win["ff_hist"], 1.0)
        self.assertEqual(result.new_ff_minus_common_win["ff_r1"], 1.0)
        self.assertEqual(result.new_ff_minus_common_win["ff_r2"], 0.0)
        self.assertTrue(result.new_ff_r1_gt_ff_r2)

    def test_task_set_drift_fails_closed(self) -> None:
        bad = dict(self.a1)
        bad.pop(next(iter(bad)))
        new = {
            "ff_hist": dict(self.a1),
            "ff_r1": bad,
            "ff_r2": dict(self.b1),
            "win_common": dict(self.a1),
        }
        with self.assertRaises(ValueError):
            compute_regeneration_metrics(
                original_ff_r1=self.a1,
                original_ff_r2=self.b1,
                new_scores=new,
            )


if __name__ == "__main__":
    unittest.main()
