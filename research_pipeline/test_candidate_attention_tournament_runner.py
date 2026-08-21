from __future__ import annotations

import unittest

from .candidate_attention_tournament import DIMENSIONS, prepare_attention_tournament
from .candidate_attention_tournament_runner import _normalize_orientation, _oriented_prompt, _swap_for
from .test_candidate_attention_tournament import machine


class CandidateAttentionTournamentRunnerTest(unittest.TestCase):
    def test_reviewer_orientation_is_deterministic_and_normalizes_back(self) -> None:
        plan = prepare_attention_tournament(machine(6), comparisons_per_candidate=1, proximity_threshold=0.99)
        pair_ids = [plan["pair_schedule"][0]["pair_id"]]
        prompt_a, orientation_a = _oriented_prompt(plan, pair_ids, "deepseek")
        prompt_b, orientation_b = _oriented_prompt(plan, pair_ids, "deepseek")
        self.assertEqual(prompt_a, prompt_b)
        self.assertEqual(orientation_a, orientation_b)
        self.assertEqual(orientation_a[pair_ids[0]], _swap_for("deepseek", pair_ids[0]))
        payload = {"reviews": [{
            "pair_id": pair_ids[0],
            "dimension_winners": {dimension: "A" for dimension in DIMENSIONS},
            "attention_winner": "A",
            "confidence": "HIGH",
            "reason": "test",
        }]}
        normalized = _normalize_orientation(payload, {pair_ids[0]: True})
        self.assertEqual(normalized["reviews"][0]["attention_winner"], "B")
        self.assertTrue(all(value == "B" for value in normalized["reviews"][0]["dimension_winners"].values()))

    def test_reviewer_labels_do_not_share_forced_orientation_pattern(self) -> None:
        plan = prepare_attention_tournament(machine(8), comparisons_per_candidate=2, proximity_threshold=0.99)
        pair_ids = [row["pair_id"] for row in plan["pair_schedule"]]
        deepseek = [_swap_for("deepseek", pair_id) for pair_id in pair_ids]
        minimax = [_swap_for("minimax", pair_id) for pair_id in pair_ids]
        self.assertNotEqual(deepseek, minimax)


if __name__ == "__main__":
    unittest.main()
