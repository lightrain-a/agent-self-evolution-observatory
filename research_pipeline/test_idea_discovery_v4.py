from __future__ import annotations

import unittest

from .idea_discovery_v4 import build_idea_discovery_v4, validate


class IdeaDiscoveryV4Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_idea_discovery_v4()

    def test_size_and_status_groups(self) -> None:
        summary = self.payload["summary"]
        self.assertEqual(summary["raw_candidates"], 28)
        self.assertEqual(summary["discussion"], 14)
        self.assertEqual(summary["revival"], 8)
        self.assertEqual(summary["repair"], 4)
        self.assertEqual(summary["component"], 2)
        self.assertEqual(summary["tournament_finalists"], 16)
        self.assertFalse(validate(self.payload))

    def test_combinations_are_structured(self) -> None:
        for idea in self.payload["all_candidates"]:
            with self.subTest(idea=idea["id"]):
                self.assertGreaterEqual(len(idea["mechanism_atoms"]), 1)
                self.assertLessEqual(len(idea["mechanism_atoms"]), 3)
                self.assertTrue(idea["persistent_update_object"])
                self.assertTrue(idea["composition_logic"]["zh"])
                self.assertTrue(idea["composition_logic"]["en"])
                self.assertTrue(idea["strongest_baseline"]["zh"])
                self.assertTrue(idea["decisive_pilot"]["en"])

    def test_revivals_have_material_conditions(self) -> None:
        revived = self.payload["revival"]
        self.assertEqual(len(revived), 8)
        for idea in revived:
            with self.subTest(idea=idea["id"]):
                self.assertEqual(idea["lineage_type"], "revived")
                self.assertTrue(idea["revival_condition"]["zh"])
                self.assertTrue(idea["revival_condition"]["en"])
                self.assertTrue(idea["parent_ids"])

    def test_tournament_and_pareto_preserve_diversity(self) -> None:
        finalists = self.payload["tournament_finalists"]
        self.assertEqual(len(finalists), 16)
        self.assertGreaterEqual(len({idea["persistent_update_object"] for idea in finalists}), 8)
        self.assertGreaterEqual(len(self.payload["pareto_front_ids"]), 8)
        self.assertIn("memory-interaction-clause-learner", self.payload["pareto_front_ids"])
        self.assertIn("update-composition-repair-compiler", self.payload["pareto_front_ids"])

    def test_external_review_is_complete_and_preserves_combination_audit(self) -> None:
        summary = self.payload["summary"]
        self.assertEqual((summary["external_reviewed"], summary["external_pending"]), (16, 0))
        self.assertEqual((summary["external_pass"], summary["external_revise"], summary["external_block"]), (5, 8, 3))
        for idea in self.payload["tournament_finalists"]:
            with self.subTest(idea=idea["id"]):
                self.assertEqual(idea["external_review_status"], "reviewed")
                self.assertTrue(idea["external_reviews"][-1].get("combination_audit"))

    def test_repository_patterns_are_official_github_urls(self) -> None:
        patterns = self.payload["repository_patterns"]
        self.assertGreaterEqual(len(patterns), 10)
        for item in patterns:
            with self.subTest(system=item["system"]):
                self.assertTrue(item["official_repo"].startswith("https://github.com/"))
                self.assertTrue(item["adopted_as"])


if __name__ == "__main__":
    unittest.main()
