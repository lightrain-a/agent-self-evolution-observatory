from __future__ import annotations

from dataclasses import dataclass, field
import unittest

from research_pipeline.e2_r17_compute_shielding_runner import (
    Arm,
    ComputePolicy,
    route_feedback,
    select_best_of_k,
    summarize_packets,
)


@dataclass
class R:
    case_id: str = "case"
    score: float = 0.0
    rollout: int = 0
    messages: list[dict] = field(default_factory=list)


class ComputeShieldingRunnerTest(unittest.TestCase):
    def setUp(self):
        self.policy = ComputePolicy(low_k=1, high_k=4, hardmine_replay_multiplier=2)

    def test_best_of_k_tie_break_is_rollout_index(self):
        rows = [R(score=0, rollout=3), R(score=1, rollout=2), R(score=1, rollout=1), R(score=0, rollout=0)]
        selected = select_best_of_k(rows, 4)
        self.assertEqual(selected.selected.rollout, 1)

    def test_hh_hides_rescued_failures(self):
        rows = [R(score=0, rollout=0), R(score=0, rollout=1), R(score=1, rollout=2), R(score=0, rollout=3)]
        dep = select_best_of_k(rows, 4)
        packet = route_feedback(arm=Arm.HH, deployment=dep, shadow=None, policy=self.policy)
        self.assertEqual(tuple(x.rollout for x in packet.updater_cases), (2,))
        self.assertEqual(packet.rescued_failure_count_hidden_from_updater, 3)

    def test_shadow_is_only_counterfactual_failure_channel(self):
        rows = [R(score=0, rollout=0), R(score=1, rollout=1), R(score=0, rollout=2), R(score=0, rollout=3)]
        dep = select_best_of_k(rows, 4)
        shadow = R(score=0, rollout=100)
        packet = route_feedback(arm=Arm.HL_SHADOW, deployment=dep, shadow=shadow, policy=self.policy)
        self.assertIs(packet.updater_cases[0], shadow)
        self.assertEqual(packet.deployed.rollout, 1)
        self.assertEqual(packet.rescued_failure_count_hidden_from_updater, 3)

    def test_hardmine_cannot_mine_rescued_subrun_failures(self):
        rows = [R(score=0, rollout=0), R(score=0, rollout=1), R(score=1, rollout=2), R(score=0, rollout=3)]
        dep = select_best_of_k(rows, 4)
        packet = route_feedback(arm=Arm.HH_HARDMINE, deployment=dep, shadow=None, policy=self.policy)
        self.assertEqual(len(packet.updater_cases), 1)
        self.assertEqual(packet.updater_cases[0].score, 1)

    def test_hardmine_replays_only_selected_high_compute_failure(self):
        rows = [R(score=0, rollout=i) for i in range(4)]
        dep = select_best_of_k(rows, 4)
        packet = route_feedback(arm=Arm.HH_HARDMINE, deployment=dep, shadow=None, policy=self.policy)
        self.assertEqual(len(packet.updater_cases), 2)
        self.assertTrue(all(x is dep.selected for x in packet.updater_cases))

    def test_low_arm_requires_k1(self):
        dep = select_best_of_k([R(score=0, rollout=0)], 1)
        packet = route_feedback(arm=Arm.LL, deployment=dep, shadow=None, policy=self.policy)
        self.assertEqual(len(packet.updater_cases), 1)

    def test_summary_separates_online_success_and_learning_signal(self):
        high = select_best_of_k([R(score=0, rollout=0), R(score=1, rollout=1), R(score=0, rollout=2), R(score=0, rollout=3)], 4)
        hh = route_feedback(arm=Arm.HH, deployment=high, shadow=None, policy=self.policy)
        hs = route_feedback(arm=Arm.HL_SHADOW, deployment=high, shadow=R(score=0, rollout=100), policy=self.policy)
        a = summarize_packets([hh])
        b = summarize_packets([hs])
        self.assertEqual(a["online_successes"], b["online_successes"])
        self.assertEqual(a["updater_visible_failures"], 0)
        self.assertEqual(b["updater_visible_failures"], 1)


if __name__ == "__main__":
    unittest.main()
