from __future__ import annotations

import unittest

import numpy as np

import behavior_formal_goal_coupling_shared26_fast_norm as fast_norm


class FastNormTest(unittest.TestCase):
    def test_episode_moments_match_bruteforce_with_padding(self) -> None:
        rng = np.random.default_rng(7)
        raw_state = rng.normal(size=(41, fast_norm.STATE_WIDTH_RAW)).astype(np.float32)
        raw_actions = rng.normal(size=(41, fast_norm.ACTION_WIDTH)).astype(np.float32)
        start_count = 37

        state_m = fast_norm.Moments.empty(fast_norm.STATE_WIDTH)
        action_m = fast_norm.Moments.empty(fast_norm.ACTION_WIDTH)
        fast_norm.accumulate_episode(raw_state, raw_actions, start_count, state_m, action_m)
        brute_state, brute_actions = fast_norm.brute_force_episode(raw_state, raw_actions, start_count)

        self.assertEqual(state_m.count, start_count)
        self.assertEqual(action_m.count, start_count * fast_norm.ACTION_HORIZON)
        np.testing.assert_allclose(state_m.sum, brute_state.astype(np.float64).sum(axis=0), rtol=0, atol=1e-10)
        np.testing.assert_allclose(
            state_m.sumsq,
            np.square(brute_state.astype(np.float64)).sum(axis=0),
            rtol=0,
            atol=1e-10,
        )
        flat_actions = brute_actions.astype(np.float64).reshape(-1, fast_norm.ACTION_WIDTH)
        np.testing.assert_allclose(action_m.sum, flat_actions.sum(axis=0), rtol=0, atol=1e-9)
        np.testing.assert_allclose(action_m.sumsq, np.square(flat_actions).sum(axis=0), rtol=0, atol=1e-8)

    def test_state_mapping_is_exact_r1pro_contract(self) -> None:
        raw = np.arange(2 * fast_norm.STATE_WIDTH_RAW, dtype=np.float32).reshape(2, fast_norm.STATE_WIDTH_RAW)
        state = fast_norm.transform_state(raw)
        expected0 = np.concatenate(
            [
                raw[0, 0:3],
                raw[0, 53:57],
                raw[0, 3:10],
                np.array([raw[0, 24:26].sum()], dtype=np.float32),
                raw[0, 28:35],
                np.array([raw[0, 49:51].sum()], dtype=np.float32),
            ]
        )
        self.assertEqual(state.shape, (2, 23))
        np.testing.assert_array_equal(state[0], expected0)


if __name__ == "__main__":
    unittest.main()
