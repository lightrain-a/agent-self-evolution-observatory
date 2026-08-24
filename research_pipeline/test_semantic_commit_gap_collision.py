from __future__ import annotations

import copy
import unittest

from .semantic_commit_gap_collision import build_semantic_commit_gap_collision, validate_semantic_commit_gap_collision


class SemanticCommitGapCollisionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.state = build_semantic_commit_gap_collision(generated_at="2026-08-24T03:00:00+08:00")

    def test_four_lifecycle_stages_are_separated_and_current_formulation_stops(self) -> None:
        self.assertEqual(self.state["status"], "STOP_CURRENT_FORMULATION_MATURE_LIFECYCLE_REDUCTION")
        self.assertEqual([row["name"] for row in self.state["four_stage_decomposition"]], [
            "ACTION_ENDPOINT_REACHED",
            "PERSISTED_STATE_DELTA_VERIFIED",
            "PERSISTED_ARTIFACT_SEMANTICALLY_VALID",
            "FUTURE_ENACTMENT_OR_UPTAKE",
        ])
        self.assertTrue(all(row["scientific_object"] is False for row in self.state["four_stage_decomposition"]))
        self.assertEqual(validate_semantic_commit_gap_collision(self.state), [])

    def test_v19_support_failure_cannot_be_upgraded_to_scientific_positive(self) -> None:
        evidence = self.state["canonical_collision_evidence"]["v19_semantic_observability_failure"]
        self.assertEqual(evidence["source_stop_class"], "SUPPORT_STOP")
        self.assertFalse(evidence["can_authorize_problem_gate"])
        self.assertFalse(evidence["scientific_authority"])
        self.assertTrue(self.state["policy"]["support_stop_cannot_be_promoted_to_problem_evidence"])

    def test_reopen_requires_provenance_only_residual_after_information_matching(self) -> None:
        reopen = self.state["reopen_condition"]
        text = reopen["required_residual"]
        for phrase in (
            "persisted artifact bytes",
            "semantic validity",
            "retrieval/exposure",
            "task state",
            "self-written versus externally installed",
            "same-information uptake/enactability",
        ):
            self.assertIn(phrase, text)
        self.assertEqual(self.state["summary"]["current_scientific_object_survives"], 0)

    def test_manual_promotion_or_v19_consumption_is_rejected(self) -> None:
        broken = copy.deepcopy(self.state)
        broken["summary"]["problem_gate_eligible"] = 1
        self.assertIn("authority-or-consumption-leak:problem_gate_eligible", validate_semantic_commit_gap_collision(broken))
        consumed = copy.deepcopy(self.state)
        consumed["summary"]["sealed_v19_units_consumed"] = 1
        self.assertIn("authority-or-consumption-leak:sealed_v19_units_consumed", validate_semantic_commit_gap_collision(consumed))

    def test_current_closest_work_covers_transition_commit_and_uptake(self) -> None:
        sources = {row["source"] for row in self.state["closest_work"]}
        self.assertTrue({"arXiv:2606.25161", "arXiv:2606.17573", "arXiv:2608.14036", "arXiv:2608.11888"}.issubset(sources))


if __name__ == "__main__":
    unittest.main()
