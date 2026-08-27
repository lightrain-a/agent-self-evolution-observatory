from __future__ import annotations

import itertools
import math
import random
import unittest

from research_pipeline.e2_r17_search_projection_theory import (
    binary_projection_stats,
    continuous_projection_stats,
    gamma_iid,
    gated_projection_factorization,
    p_star,
)


class SearchProjectionTheoryTest(unittest.TestCase):
    def test_binary_identity_for_arbitrary_correlated_joint_laws(self) -> None:
        rng = random.Random(20260827)
        for k in range(2, 7):
            atoms = list(itertools.product((0, 1), repeat=k))
            for _ in range(50):
                weights = [rng.expovariate(1.0) for _ in atoms]
                total = sum(weights)
                joint = {atom: weight / total for atom, weight in zip(atoms, weights)}
                stats = binary_projection_stats(joint)
                self.assertAlmostEqual(stats.acting_gain, stats.rescue_censoring_mass, places=12)
                self.assertAlmostEqual(stats.visibility_gap, stats.rescue_censoring_mass, places=12)

    def test_iid_closed_form(self) -> None:
        for k in (2, 4, 8):
            for p in (0.05, 0.2, 0.5, 0.9):
                atoms = list(itertools.product((0, 1), repeat=k))
                joint = {
                    atom: math.prod(p if value else 1 - p for value in atom)
                    for atom in atoms
                }
                stats = binary_projection_stats(joint)
                self.assertAlmostEqual(stats.rescue_censoring_mass, gamma_iid(p, k), places=12)

    def test_p_star_is_interior_maximum(self) -> None:
        for k in (2, 3, 4, 8, 16):
            peak = p_star(k)
            self.assertGreater(peak, 0.0)
            self.assertLess(peak, 1.0)
            center = gamma_iid(peak, k)
            self.assertGreaterEqual(center, gamma_iid(max(0.0, peak - 1e-4), k))
            self.assertGreaterEqual(center, gamma_iid(min(1.0, peak + 1e-4), k))

    def test_continuous_layer_cake_identity(self) -> None:
        support = {
            (0.10, 0.80, 0.30): 0.25,
            (0.75, 0.20, 0.40): 0.35,
            (0.40, 0.40, 0.40): 0.15,
            (0.20, 0.35, 0.90): 0.25,
        }
        stats = continuous_projection_stats(support)
        self.assertAlmostEqual(stats.acting_gain, stats.integrated_threshold_censoring, places=12)

    def test_exact_gated_gamma_delta_factorization(self) -> None:
        ate, mass, delta = gated_projection_factorization(
            [
                (True, 0.20, 0.40),
                (True, 0.15, -0.10),
                (False, 0.65, 0.0),
            ]
        )
        self.assertAlmostEqual(ate, mass * delta, places=12)

    def test_factorization_rejects_off_event_projection_change(self) -> None:
        with self.assertRaises(ValueError):
            gated_projection_factorization([(True, 0.2, 0.5), (False, 0.8, 0.1)])


if __name__ == "__main__":
    unittest.main()
