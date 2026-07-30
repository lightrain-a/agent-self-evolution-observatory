from __future__ import annotations

import unittest

from .cvpr_idea_factory import build_cvpr_idea_bank, validate_bank


class CvprIdeaBankTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_cvpr_idea_bank()
        cls.ideas = cls.payload["passed_ideas"]

    def test_bank_is_large_and_valid(self) -> None:
        self.assertGreaterEqual(len(self.ideas), 40)
        self.assertEqual(validate_bank(self.payload), [])
        self.assertEqual(self.payload["summary"]["raw_candidates"], 61)
        self.assertEqual(self.payload["summary"]["early_rejected"], 18)

    def test_every_passed_idea_has_five_pass_reviews(self) -> None:
        for idea in self.ideas:
            with self.subTest(idea=idea["id"]):
                self.assertEqual(len(idea["reviews"]), 5)
                self.assertTrue(all(review["verdict"] == "pass" for review in idea["reviews"]))
                self.assertTrue(all(review["score"] >= 4 for review in idea["reviews"]))

    def test_resource_policy_is_enforced(self) -> None:
        for idea in self.ideas:
            with self.subTest(idea=idea["id"]):
                self.assertLessEqual(idea["budget"]["max_gpus"], 2)
                self.assertLessEqual(idea["budget"]["gpu_hours"], 48)
                self.assertLessEqual(idea["budget"]["wall_days"], 10)
                self.assertTrue(idea["datasets"])
                self.assertTrue(idea["models"])

    def test_advisor_fields_are_complete(self) -> None:
        fields = self.payload["policy"]["required_fields"]
        for idea in self.ideas:
            with self.subTest(idea=idea["id"]):
                for field in fields:
                    value = idea[field]
                    self.assertTrue(value)
                    if isinstance(value, dict) and "zh" in value:
                        self.assertTrue(value["zh"])
                        self.assertTrue(value["en"])
                self.assertTrue(idea["collision_boundary"]["zh"])
                self.assertTrue(idea["nearest_work"])

    def test_experiment_protocol_is_reproducible_and_api_optional(self) -> None:
        required = {
            "execution_mode", "actor", "cross_model", "critic_or_verifier",
            "tool_models", "commercial_api_role", "parameter_updates",
            "data_protocol", "phases", "controls", "repetitions",
            "call_budget", "compute_budget", "main_table", "ablations",
            "success_gate", "stop_gate", "artifacts_to_log",
        }
        for idea in self.ideas:
            with self.subTest(idea=idea["id"]):
                protocol = idea["experiment_protocol"]
                self.assertTrue(required.issubset(protocol))
                self.assertIn("open-weight-primary", protocol["execution_mode"])
                self.assertEqual([phase["id"] for phase in protocol["phases"]], ["P0", "P1", "P2"])
                self.assertIn("discovery", protocol["data_protocol"])
                self.assertIn("calibration", protocol["data_protocol"])
                self.assertIn("test", protocol["data_protocol"])
                self.assertGreaterEqual(len(protocol["controls"]), 4)
                self.assertGreaterEqual(len(protocol["ablations"]), 4)
                self.assertTrue(protocol["actor"])
                self.assertTrue(protocol["cross_model"])

    def test_ranking_is_monotone(self) -> None:
        self.assertEqual([idea["rank"] for idea in self.ideas], list(range(1, len(self.ideas) + 1)))
        priorities = [idea["priority"] for idea in self.ideas]
        self.assertTrue(all(left >= right for left, right in zip(priorities, priorities[1:])))


if __name__ == "__main__":
    unittest.main()
