from __future__ import annotations

import unittest

from .iclr_idea_factory import build_iclr_idea_bank, validate_bank


class IclrIdeaBankTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_iclr_idea_bank()
        cls.ideas = cls.payload["passed_ideas"]

    def test_target_and_size(self) -> None:
        self.assertEqual(self.payload["target_venue"], "ICLR")
        self.assertGreaterEqual(len(self.ideas), 24)
        self.assertEqual(validate_bank(self.payload), [])
        self.assertEqual(self.payload["summary"]["tracks"], 8)

    def test_seven_review_gates(self) -> None:
        for idea in self.ideas:
            with self.subTest(idea=idea["id"]):
                self.assertEqual(len(idea["reviews"]), 7)
                self.assertTrue(all(review["verdict"] == "pass" for review in idea["reviews"]))
                self.assertTrue(all(review["score"] >= 4 for review in idea["reviews"]))

    def test_generality_and_resource_policy(self) -> None:
        for idea in self.ideas:
            with self.subTest(idea=idea["id"]):
                self.assertGreaterEqual(len(idea["domains"]), 2)
                self.assertLessEqual(idea["budget"]["max_gpus"], 2)
                self.assertLessEqual(idea["budget"]["gpu_hours"], 48)
                self.assertTrue(idea["experiment_protocol"])
                self.assertTrue(idea["models"])
                self.assertTrue(idea["datasets"])

    def test_primary_open_weight_and_api_policy(self) -> None:
        policy = self.payload["policy"]
        self.assertTrue(policy["primary_open_weight_required"])
        self.assertTrue(policy["commercial_api_optional_only"])
        for idea in self.ideas:
            role = idea["experiment_protocol"]["commercial_api_role"]
            self.assertIn("optional", role["en"].lower())
            self.assertIn("核心", role["zh"])

    def test_ranking_and_web_review(self) -> None:
        self.assertEqual([idea["rank"] for idea in self.ideas], list(range(1, len(self.ideas) + 1)))
        self.assertEqual(sorted(idea["programmatic_rank"] for idea in self.ideas), list(range(1, len(self.ideas) + 1)))
        verdict_order = {"pass": 0, "revise": 1, "pending": 2, "block": 3}
        verdicts = [verdict_order[idea["external_verdict"]] for idea in self.ideas]
        self.assertTrue(all(left <= right for left, right in zip(verdicts, verdicts[1:])))
        for verdict in verdict_order:
            priorities = [idea["priority"] for idea in self.ideas if idea["external_verdict"] == verdict]
            self.assertTrue(all(left >= right for left, right in zip(priorities, priorities[1:])))
        reviewed = [idea for idea in self.ideas if idea["external_reviews"]]
        self.assertTrue(any(idea["id"] == "regression-gated-self-evolution" for idea in reviewed))
        summary = self.payload["summary"]
        self.assertEqual(summary["project_web_gpt_reviewed"], len(reviewed))
        self.assertEqual(summary["project_web_gpt_pending"], len(self.ideas) - len(reviewed))
        self.assertEqual(summary["project_web_gpt_complete"], len(reviewed) == len(self.ideas))
        counts = summary["external_verdict_counts"]
        for verdict in ("pass", "revise", "block", "pending"):
            self.assertEqual(counts[verdict], sum(idea["external_verdict"] == verdict for idea in self.ideas))


if __name__ == "__main__":
    unittest.main()
