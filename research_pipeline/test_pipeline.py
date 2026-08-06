from __future__ import annotations

import unittest

from .pipeline import build_snapshot


class PipelineSnapshotTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.snapshot = build_snapshot()

    def test_expected_portfolio_and_architecture(self) -> None:
        self.assertEqual(len(self.snapshot.ideas), 34)
        self.assertEqual(len(self.snapshot.funnel), 4)
        self.assertEqual(len(self.snapshot.generation_operators), 14)
        self.assertEqual(len(self.snapshot.reviewer_roles), 5)
        self.assertEqual(self.snapshot.architecture_version, "2.1-s2-connected")

    def test_exactly_one_selected_idea(self) -> None:
        selected = [idea for idea in self.snapshot.ideas if idea.stage == "selected"]
        self.assertEqual([idea.name for idea in selected], ["GroundEvo-Admission"])
        self.assertEqual(selected[0].decision, "advance")
        self.assertIsNotNone(selected[0].pilot)

    def test_every_idea_has_advisor_fields(self) -> None:
        for idea in self.snapshot.ideas:
            with self.subTest(idea=idea.name):
                self.assertFalse(idea.validate())
                for field_name in (
                    "purpose",
                    "core_idea",
                    "rationale",
                    "method_logic",
                    "importance",
                    "comparative_advantage",
                    "thesis",
                ):
                    value = getattr(idea, field_name)
                    self.assertTrue(value.get("en"))
                    self.assertTrue(value.get("zh"))
                self.assertEqual(len(idea.scorecard), 7)
                self.assertEqual(len(idea.reviews), 5)
                self.assertIsNotNone(idea.pilot)

    def test_funnel_is_monotone(self) -> None:
        counts = [stage.count for stage in self.snapshot.funnel]
        self.assertTrue(all(left >= right for left, right in zip(counts, counts[1:])), counts)


if __name__ == "__main__":
    unittest.main()
