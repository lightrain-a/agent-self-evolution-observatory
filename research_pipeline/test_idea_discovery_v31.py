from __future__ import annotations

import unittest

from .idea_discovery_v31 import build_idea_discovery_v31, validate


class IdeaDiscoveryV31Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bank = build_idea_discovery_v31()

    def test_six_reviewer_repaired_children(self) -> None:
        self.assertFalse(validate(self.bank))
        self.assertEqual(self.bank["summary"]["children"], 6)
        self.assertEqual(self.bank["summary"]["external_reviewed"], 6)
        self.assertEqual(self.bank["summary"]["external_pass"], 0)
        self.assertEqual(self.bank["summary"]["external_revise"], 2)
        self.assertEqual(self.bank["summary"]["external_block"], 4)
        self.assertTrue(self.bank["policy"]["parents_only_from_v3_revise"])
        self.assertTrue(self.bank["policy"]["blocked_parents_stopped"])
        self.assertTrue(self.bank["policy"]["main_bank_unchanged"])

    def test_algorithms_are_more_specific_than_v3(self) -> None:
        for idea in self.bank["children"]:
            with self.subTest(idea=idea["id"]):
                self.assertGreater(len(idea["exact_mechanism"]["en"]), 240)
                self.assertTrue(idea["update_surface"])
                self.assertTrue(idea["learning_signal"]["zh"])
                self.assertTrue(idea["independent_ground_truth"]["en"])
                self.assertGreaterEqual(len(idea["generation_mechanisms"]), 2)
                self.assertNotEqual(idea["external_verdict"], "pass")

    def test_only_two_children_survive_as_revise(self) -> None:
        revised = {idea["id"] for idea in self.bank["children"] if idea["external_verdict"] == "revise"}
        self.assertEqual(revised, {"restoration-clause-learning", "conformal-effect-transport-gate"})

    def test_blocked_v3_parents_do_not_reappear(self) -> None:
        stopped = {
            "version-differential-active-diagnosis",
            "precommit-workflow-transfer-certificate",
            "actor-evaluator-residual-gate",
            "asset-level-model-swap-certificate",
        }
        self.assertFalse(stopped & {idea["parent_id"] for idea in self.bank["children"]})


if __name__ == "__main__":
    unittest.main()
