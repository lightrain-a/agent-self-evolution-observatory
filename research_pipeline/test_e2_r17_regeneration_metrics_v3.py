from __future__ import annotations

import inspect
import itertools
import math
import unittest

from research_pipeline.e2_r17_regeneration_metrics_v3 import (
    compute_prospective_regeneration_metrics,
    exact_conditional_randomization_p,
)


SHA_A = "a" * 64
SHA_B = "b" * 64


def task(i: int) -> str:
    return f"r17-b4-tsr-p{i}"


class RegenerationMetricsV3Test(unittest.TestCase):
    def test_interface_accepts_only_fully_prospective_replicates(self) -> None:
        params = set(inspect.signature(compute_prospective_regeneration_metrics).parameters)
        self.assertEqual(
            params,
            {
                "ff_r1_rep1",
                "ff_r1_rep2",
                "ff_r2_rep1",
                "ff_r2_rep2",
                "ff_r1_sha256",
                "ff_r2_sha256",
                "alpha",
            },
        )
        self.assertNotIn("original_ff_r1", params)
        self.assertNotIn("original_ff_r2", params)

    def test_stable_separation_has_e_real_one(self) -> None:
        ids = [task(i) for i in range(3)]
        a1 = {q: 1 for q in ids}
        a2 = {q: 1 for q in ids}
        b1 = {q: 0 for q in ids}
        b2 = {q: 0 for q in ids}
        m = compute_prospective_regeneration_metrics(
            ff_r1_rep1=a1,
            ff_r1_rep2=a2,
            ff_r2_rep1=b1,
            ff_r2_rep2=b2,
            ff_r1_sha256=SHA_A,
            ff_r2_sha256=SHA_B,
        )
        self.assertEqual(m.d_cross_state, 1.0)
        self.assertEqual(m.d_within_actor, 0.0)
        self.assertEqual(m.e_real, 1.0)
        self.assertEqual(m.informative_two_success_tasks, 3)
        self.assertEqual(m.same_state_separation_tasks, 3)

    def test_exact_randomization_tail_matches_binomial_one_third(self) -> None:
        n, x = 8, 6
        expected = sum(
            math.comb(n, k) * (1 / 3) ** k * (2 / 3) ** (n - k)
            for k in range(x, n + 1)
        )
        self.assertAlmostEqual(
            exact_conditional_randomization_p(informative_tasks=n, separation_tasks=x),
            expected,
            places=15,
        )

    def test_exact_p_is_one_with_no_informative_tasks(self) -> None:
        self.assertEqual(
            1.0,
            exact_conditional_randomization_p(informative_tasks=0, separation_tasks=0),
        )

    def test_positive_effect_alone_does_not_pass_without_uncertainty_gate(self) -> None:
        # Three separated tasks yield E_REAL=1, but P(X>=3 | Binom(3,1/3))=1/27
        # actually passes at .05. Use two separated tasks instead: p=1/9 > .05.
        ids = [task(0), task(1)]
        m = compute_prospective_regeneration_metrics(
            ff_r1_rep1={q: 1 for q in ids},
            ff_r1_rep2={q: 1 for q in ids},
            ff_r2_rep1={q: 0 for q in ids},
            ff_r2_rep2={q: 0 for q in ids},
            ff_r1_sha256=SHA_A,
            ff_r2_sha256=SHA_B,
        )
        self.assertGreater(m.e_real, 0.0)
        self.assertAlmostEqual(m.exact_one_sided_p, 1 / 9)
        self.assertFalse(m.randomization_pass)
        self.assertFalse(m.bounded_localization_pass)

    def test_three_clean_separation_tasks_pass_alpha_point_zero_five(self) -> None:
        ids = [task(i) for i in range(3)]
        m = compute_prospective_regeneration_metrics(
            ff_r1_rep1={q: 1 for q in ids},
            ff_r1_rep2={q: 1 for q in ids},
            ff_r2_rep1={q: 0 for q in ids},
            ff_r2_rep2={q: 0 for q in ids},
            ff_r1_sha256=SHA_A,
            ff_r2_sha256=SHA_B,
        )
        self.assertAlmostEqual(m.exact_one_sided_p, 1 / 27)
        self.assertTrue(m.bounded_localization_pass)

    def test_identical_state_sha_forces_zero_and_p_one(self) -> None:
        ids = [task(i) for i in range(4)]
        m = compute_prospective_regeneration_metrics(
            ff_r1_rep1={q: 1 for q in ids},
            ff_r1_rep2={q: 1 for q in ids},
            ff_r2_rep1={q: 0 for q in ids},
            ff_r2_rep2={q: 0 for q in ids},
            ff_r1_sha256=SHA_A,
            ff_r2_sha256=SHA_A,
        )
        self.assertTrue(m.state_sha_alias)
        self.assertEqual(m.e_real, 0.0)
        self.assertEqual(m.exact_one_sided_p, 1.0)
        self.assertFalse(m.bounded_localization_pass)

    def test_task_contribution_identity_exhaustive(self) -> None:
        # Across all four fresh binary outcomes, E_REAL(q) is 1 when both
        # successes belong to one state, -1/2 when two successes split across
        # states, and 0 otherwise.
        q = task(0)
        for a1, a2, b1, b2 in itertools.product((0, 1), repeat=4):
            m = compute_prospective_regeneration_metrics(
                ff_r1_rep1={q: a1},
                ff_r1_rep2={q: a2},
                ff_r2_rep1={q: b1},
                ff_r2_rep2={q: b2},
                ff_r1_sha256=SHA_A,
                ff_r2_sha256=SHA_B,
                alpha=0.05,
            )
            total = a1 + a2 + b1 + b2
            if total == 2 and a1 == a2 and b1 == b2:
                expected = 1.0
            elif total == 2:
                expected = -0.5
            else:
                expected = 0.0
            self.assertEqual(m.task_contributions[q], expected)

    def test_task_set_drift_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            compute_prospective_regeneration_metrics(
                ff_r1_rep1={task(0): 1},
                ff_r1_rep2={task(1): 1},
                ff_r2_rep1={task(0): 0},
                ff_r2_rep2={task(0): 0},
                ff_r1_sha256=SHA_A,
                ff_r2_sha256=SHA_B,
            )


if __name__ == "__main__":
    unittest.main()
