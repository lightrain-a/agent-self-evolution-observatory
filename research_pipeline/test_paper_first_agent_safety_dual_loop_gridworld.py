from __future__ import annotations

import math
import unittest

from .paper_first_agent_safety_dual_loop_gridworld import (
    GridConfig,
    GridWorld,
    RHO_LEVELS,
    baseline_visitation_profile,
    candidate_regime,
    coupled_dynamics_baseline,
    eval_starts,
    mask_pair,
    periods_for_tau,
    smoke_probe,
    support_matched_mask_pair,
    train_starts,
    update_counts,
)


class AgentSafetyDualLoopGridWorldTest(unittest.TestCase):
    def test_rho_changes_only_mask_overlap_with_fixed_cardinality(self) -> None:
        env = GridWorld(GridConfig())
        counts = []
        actual = []
        for rho in RHO_LEVELS:
            a, b, observed = mask_pair(env.preference_dim, rho, env.cfg.edit_fraction)
            counts.append((sum(a), sum(b)))
            actual.append(observed)
        self.assertEqual(len(set(counts)), 1)
        self.assertEqual(actual[0], 0.0)
        self.assertEqual(actual[-1], 1.0)
        self.assertTrue(all(x <= y for x, y in zip(actual, actual[1:])))

    def test_support_matched_rho_preserves_per_stratum_marginals(self) -> None:
        env = GridWorld(GridConfig())
        profile = baseline_visitation_profile(env, episodes=64)
        audits = []
        for rho in RHO_LEVELS:
            _a, _b, actual, audit = support_matched_mask_pair(env, rho, profile, seed=12345)
            audits.append((actual, audit))
        keys = sorted(profile["strata"])
        for key in keys:
            self.assertEqual(len({audit["strata"][key]["a_count"] for _rho, audit in audits}), 1)
            self.assertEqual(len({audit["strata"][key]["b_count"] for _rho, audit in audits}), 1)
        self.assertTrue(all(row["intersection"] == 0 for row in audits[0][1]["strata"].values()))
        self.assertTrue(all(row["intersection"] == row["a_count"] == row["b_count"] for row in audits[-1][1]["strata"].values()))
        actual = [value for value, _audit in audits]
        self.assertTrue(all(left <= right for left, right in zip(actual, actual[1:])))

    def test_support_profile_is_no_loop_and_deterministic(self) -> None:
        env = GridWorld(GridConfig())
        first = baseline_visitation_profile(env, episodes=32)
        second = baseline_visitation_profile(env, episodes=32)
        self.assertEqual(first["source"], "frozen-no-loop-base-policy")
        self.assertEqual(first["counts"], second["counts"])
        self.assertEqual(first["strata"], second["strata"])

    def test_same_mask_seed_preserves_marginal_signature_for_all_rho(self) -> None:
        env = GridWorld(GridConfig())
        profile = baseline_visitation_profile(env, episodes=64)
        signatures = []
        for rho in RHO_LEVELS:
            _a, _b, _actual, audit = support_matched_mask_pair(env, rho, profile, seed=271828)
            signatures.append(tuple((key, row["a_count"], row["b_count"]) for key, row in sorted(audit["strata"].items())))
        self.assertEqual(len(set(signatures)), 1)

    def test_tau_changes_only_preregistered_cadence(self) -> None:
        self.assertEqual(periods_for_tau(0.25), (4, 1))
        self.assertEqual(periods_for_tau(1.0), (1, 1))
        self.assertEqual(periods_for_tau(4.0), (1, 4))

    def test_train_eval_starts_are_disjoint(self) -> None:
        cfg = GridConfig()
        self.assertTrue(set(train_starts(cfg)).isdisjoint(set(eval_starts(cfg))))

    def test_competence_floor_is_120_updates_at_extreme_tau(self) -> None:
        cfg = GridConfig()
        self.assertEqual(cfg.train_episodes, 480)
        self.assertGreaterEqual(min(update_counts(0.25, cfg.train_episodes)), 120)
        self.assertGreaterEqual(min(update_counts(4.0, cfg.train_episodes)), 120)

    def test_candidate_predictor_is_precomposition_and_finite(self) -> None:
        label, critical = candidate_regime(0.12, 0.10, 0.75, 1.0, 480)
        self.assertIn(label, {"additive", "dominance", "mutual-degradation"})
        self.assertGreaterEqual(critical, 0.0)
        self.assertLessEqual(critical, 1.0)

    def test_generic_baseline_is_finite(self) -> None:
        label, ra, rb = coupled_dynamics_baseline(0.1, 0.12, 0.5, 1.0)
        self.assertIn(label, {"additive", "dominance", "mutual-degradation"})
        self.assertTrue(math.isfinite(ra))
        self.assertTrue(math.isfinite(rb))

    def test_smoke_has_no_scientific_outcome(self) -> None:
        state = smoke_probe()
        self.assertEqual(state["status"], "SMOKE_PASS")
        self.assertTrue(state["train_eval_disjoint"])
        self.assertTrue(state["support_marginals_invariant_across_rho"])
        self.assertTrue(state["rho0_disjoint_within_every_stratum"])
        self.assertTrue(state["rho1_identical_within_every_stratum"])
        self.assertTrue(state["actual_rho_monotone"])
        self.assertTrue(state["sample_exec_finite"])
        self.assertFalse(state["scientific_outcome_inferred"])
        self.assertFalse(state["scientific_authority"])


if __name__ == "__main__":
    unittest.main()
