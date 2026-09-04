from __future__ import annotations

import inspect
import itertools
import math
import unittest

from research_pipeline.e2_r17_regeneration_metrics_v4 import (
    compute_prospective_regeneration_metrics_v4,
    exact_conditional_randomization_p,
)


SHA_A = "a" * 64
SHA_B = "b" * 64


def task(i: int) -> str:
    return f"r17-b4-tsr-p{i}"


def clean_separation(ids: list[str], *, within_ok: bool = True, across_ok: bool = True):
    return compute_prospective_regeneration_metrics_v4(
        ff_r1_rep1={q: 1 for q in ids},
        ff_r1_rep2={q: 1 for q in ids},
        ff_r2_rep1={q: 0 for q in ids},
        ff_r2_rep2={q: 0 for q in ids},
        ff_r1_sha256=SHA_A,
        ff_r2_sha256=SHA_B,
        within_task_iid_stationarity_qualified=within_ok,
        cross_task_factorization_qualified=across_ok,
    )


class RegenerationMetricsV4Test(unittest.TestCase):
    def test_interface_requires_fully_prospective_replicates_and_two_assumption_flags(self) -> None:
        params = set(inspect.signature(compute_prospective_regeneration_metrics_v4).parameters)
        self.assertEqual(
            params,
            {
                "ff_r1_rep1",
                "ff_r1_rep2",
                "ff_r2_rep1",
                "ff_r2_rep2",
                "ff_r1_sha256",
                "ff_r2_sha256",
                "within_task_iid_stationarity_qualified",
                "cross_task_factorization_qualified",
                "alpha",
            },
        )
        self.assertNotIn("original_ff_r1", params)
        self.assertNotIn("original_ff_r2", params)

    def test_stable_separation_passes_only_when_both_inference_assumptions_are_qualified(self) -> None:
        ids = [task(i) for i in range(3)]
        passed = clean_separation(ids, within_ok=True, across_ok=True)
        self.assertEqual(passed.e_real, 1.0)
        self.assertAlmostEqual(passed.exact_one_sided_p, 1 / 27)
        self.assertTrue(passed.raw_randomization_pass)
        self.assertTrue(passed.inference_assumptions_qualified)
        self.assertTrue(passed.bounded_localization_pass)

        no_across = clean_separation(ids, within_ok=True, across_ok=False)
        self.assertEqual(no_across.e_real, 1.0)
        self.assertAlmostEqual(no_across.exact_one_sided_p, 1 / 27)
        self.assertTrue(no_across.raw_randomization_pass)
        self.assertFalse(no_across.inference_assumptions_qualified)
        self.assertFalse(no_across.bounded_localization_pass)

        no_within = clean_separation(ids, within_ok=False, across_ok=True)
        self.assertTrue(no_within.raw_randomization_pass)
        self.assertFalse(no_within.inference_assumptions_qualified)
        self.assertFalse(no_within.bounded_localization_pass)

    def test_cross_task_equal_propensity_or_exchangeability_is_not_an_input(self) -> None:
        params = set(inspect.signature(compute_prospective_regeneration_metrics_v4).parameters)
        self.assertNotIn("common_task_probability", params)
        self.assertNotIn("cross_task_exchangeability", params)
        self.assertIn("cross_task_factorization_qualified", params)

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

    def test_taskwise_conditional_probability_is_one_third(self) -> None:
        assignments = list(itertools.combinations(range(4), 2))
        same_state = 0
        # Slots 0,1 belong to A; 2,3 belong to B.
        for successes in assignments:
            if set(successes) in ({0, 1}, {2, 3}):
                same_state += 1
        self.assertEqual(len(assignments), 6)
        self.assertEqual(same_state, 2)
        self.assertEqual(same_state / len(assignments), 1 / 3)

    def test_positive_effect_alone_does_not_pass_uncertainty_gate(self) -> None:
        ids = [task(0), task(1)]
        m = clean_separation(ids)
        self.assertGreater(m.e_real, 0.0)
        self.assertAlmostEqual(m.exact_one_sided_p, 1 / 9)
        self.assertFalse(m.raw_randomization_pass)
        self.assertFalse(m.bounded_localization_pass)

    def test_identical_state_sha_forces_zero_and_p_one(self) -> None:
        ids = [task(i) for i in range(4)]
        m = compute_prospective_regeneration_metrics_v4(
            ff_r1_rep1={q: 1 for q in ids},
            ff_r1_rep2={q: 1 for q in ids},
            ff_r2_rep1={q: 0 for q in ids},
            ff_r2_rep2={q: 0 for q in ids},
            ff_r1_sha256=SHA_A,
            ff_r2_sha256=SHA_A,
            within_task_iid_stationarity_qualified=True,
            cross_task_factorization_qualified=True,
        )
        self.assertTrue(m.state_sha_alias)
        self.assertEqual(m.e_real, 0.0)
        self.assertEqual(m.exact_one_sided_p, 1.0)
        self.assertFalse(m.bounded_localization_pass)

    def test_task_contribution_identity_exhaustive(self) -> None:
        q = task(0)
        for a1, a2, b1, b2 in itertools.product((0, 1), repeat=4):
            m = compute_prospective_regeneration_metrics_v4(
                ff_r1_rep1={q: a1},
                ff_r1_rep2={q: a2},
                ff_r2_rep1={q: b1},
                ff_r2_rep2={q: b2},
                ff_r1_sha256=SHA_A,
                ff_r2_sha256=SHA_B,
                within_task_iid_stationarity_qualified=True,
                cross_task_factorization_qualified=True,
            )
            total = a1 + a2 + b1 + b2
            if total == 2 and a1 == a2 and b1 == b2:
                expected = 1.0
            elif total == 2:
                expected = -0.5
            else:
                expected = 0.0
            self.assertEqual(m.task_contributions[q], expected)

    def test_assumption_flags_must_be_real_booleans(self) -> None:
        ids = [task(0)]
        kwargs = dict(
            ff_r1_rep1={ids[0]: 1},
            ff_r1_rep2={ids[0]: 1},
            ff_r2_rep1={ids[0]: 0},
            ff_r2_rep2={ids[0]: 0},
            ff_r1_sha256=SHA_A,
            ff_r2_sha256=SHA_B,
        )
        with self.assertRaises(ValueError):
            compute_prospective_regeneration_metrics_v4(
                **kwargs,
                within_task_iid_stationarity_qualified=1,  # type: ignore[arg-type]
                cross_task_factorization_qualified=True,
            )
        with self.assertRaises(ValueError):
            compute_prospective_regeneration_metrics_v4(
                **kwargs,
                within_task_iid_stationarity_qualified=True,
                cross_task_factorization_qualified="yes",  # type: ignore[arg-type]
            )

    def test_task_set_drift_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            compute_prospective_regeneration_metrics_v4(
                ff_r1_rep1={task(0): 1},
                ff_r1_rep2={task(1): 1},
                ff_r2_rep1={task(0): 0},
                ff_r2_rep2={task(0): 0},
                ff_r1_sha256=SHA_A,
                ff_r2_sha256=SHA_B,
                within_task_iid_stationarity_qualified=True,
                cross_task_factorization_qualified=True,
            )


if __name__ == "__main__":
    unittest.main()
