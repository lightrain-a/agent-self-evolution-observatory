from __future__ import annotations

import unittest

from .published_experiment_audit import build_payload, validate


class PublishedExperimentAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_payload()
        cls.papers = cls.payload["papers"]

    def test_audit_is_large_and_valid(self) -> None:
        self.assertGreaterEqual(len(self.papers), 10)
        self.assertEqual(validate(self.payload), [])

    def test_api_and_training_are_separate_fields(self) -> None:
        for paper in self.papers:
            with self.subTest(paper=paper["id"]):
                for field in (
                    "actor", "critic_or_judge", "api_role", "parameter_updates",
                    "data", "hardware", "code", "implication",
                ):
                    self.assertTrue(paper[field]["zh"])
                    self.assertTrue(paper[field]["en"])
                self.assertTrue(paper["verification"])
                self.assertTrue(paper["source"].startswith("https://"))

    def test_unknowns_are_explicit_not_fabricated(self) -> None:
        pending = [
            paper for paper in self.papers
            if "pending" in paper["verification"] or "Unknown" in paper["hardware"]["en"]
        ]
        self.assertTrue(pending)
        self.assertTrue(any(paper["id"] == "clova-2024" for paper in self.papers))
        self.assertTrue(any(paper["id"] == "visplay-2026" for paper in self.papers))


if __name__ == "__main__":
    unittest.main()
