from __future__ import annotations

import unittest

from .iclr_experiment_audit import build_payload, validate


class IclrExperimentAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_payload()
        cls.papers = cls.payload["papers"]

    def test_target_size_and_validity(self) -> None:
        self.assertEqual(self.payload["target_venue"], "ICLR")
        self.assertGreaterEqual(len(self.papers), 10)
        self.assertEqual(validate(self.payload), [])

    def test_bilingual_execution_fields(self) -> None:
        for paper in self.papers:
            with self.subTest(paper=paper["id"]):
                for key in ("actor", "api_role", "parameter_updates", "data", "hardware", "implication"):
                    self.assertTrue(paper[key]["zh"])
                    self.assertTrue(paper[key]["en"])
                self.assertTrue(paper["source"].startswith("https://"))

    def test_required_iclr_baselines_are_present(self) -> None:
        ids = {paper["id"] for paper in self.papers}
        for required in ("retroformer-2024", "aflow-2025", "web-rl-2025", "score-2025", "self-evolved-reward-2025", "worfbench-2025", "wma-2025"):
            self.assertIn(required, ids)

    def test_primary_recommendation_is_open_weight(self) -> None:
        recommendation = self.payload["summary"]["primary_recommendation"]
        self.assertIn("开放", recommendation["zh"])
        self.assertIn("open", recommendation["en"].lower())


if __name__ == "__main__":
    unittest.main()
