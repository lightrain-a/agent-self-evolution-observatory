from __future__ import annotations

import unittest

from .idea_discovery_v3 import build_idea_discovery_v3, validate


class IdeaDiscoveryV3Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bank = build_idea_discovery_v3()

    def test_size_and_internal_status(self) -> None:
        self.assertFalse(validate(self.bank))
        self.assertEqual(self.bank["summary"]["workflow_stages"], 9)
        self.assertEqual(self.bank["summary"]["mechanism_gates"], 5)
        self.assertEqual(self.bank["summary"]["raw_children"], 14)
        self.assertEqual(self.bank["summary"]["internal_shortlist"], 10)
        self.assertEqual(self.bank["summary"]["repair"], 4)
        self.assertEqual(self.bank["summary"]["external_reviewed"], 10)
        self.assertEqual(self.bank["summary"]["external_pass"], 0)
        self.assertEqual(self.bank["summary"]["external_revise"], 6)
        self.assertEqual(self.bank["summary"]["external_block"], 4)
        self.assertTrue(self.bank["policy"]["main_bank_unchanged"])
        self.assertTrue(self.bank["policy"]["external_review_required_before_merge"])

    def test_solution_fields_are_concrete(self) -> None:
        ids = set()
        for idea in self.bank["all_children"]:
            with self.subTest(idea=idea["id"]):
                self.assertNotIn(idea["id"], ids)
                ids.add(idea["id"])
                self.assertTrue(idea["parent_id"])
                self.assertTrue(idea["update_surface"])
                self.assertTrue(idea["public_assets"])
                self.assertGreaterEqual(len(idea["generation_mechanisms"]), 2)
                for field in (
                    "changed_assumption",
                    "exact_mechanism",
                    "learning_signal",
                    "independent_ground_truth",
                    "strongest_baseline",
                    "decisive_pilot",
                    "stop_condition",
                ):
                    self.assertTrue(idea[field]["en"])
                    self.assertTrue(idea[field]["zh"])
                self.assertEqual(set(idea["scores"]), {
                    "novelty", "specificity", "identifiability",
                    "feasibility", "transfer", "cost_efficiency",
                })

    def test_repository_patterns_use_official_github_urls(self) -> None:
        self.assertEqual(len(self.bank["repository_patterns"]), 7)
        for item in self.bank["repository_patterns"]:
            self.assertTrue(item["official_repo"].startswith("https://github.com/"))
            self.assertTrue(item["adopted_as"])

    def test_pareto_front_contains_solution_first_leaders(self) -> None:
        front = set(self.bank["pareto_front_ids"])
        self.assertTrue({
            "active-causal-minimal-rollback",
            "future-reuse-harm-predictor",
            "replicated-effect-memory-gate",
            "version-differential-active-diagnosis",
            "cross-task-effect-transport-certificate",
        }.issubset(front))


if __name__ == "__main__":
    unittest.main()
