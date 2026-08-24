from __future__ import annotations

import unittest

from .config import PROJECT_ROOT
from .failure_differential_registry import (
    MIN_PROSPECTIVE_REPLAY_CASES,
    build_failure_hypothesis_set,
    build_historical_failure_label_inventory,
    build_sage_mhfa_shadow_state,
    score_failure_hypothesis_set,
)


class FailureDifferentialRegistryTest(unittest.TestCase):
    def hypotheses(self):
        return [
            {"failure_layer": "experiment_identifiability", "rationale": "support may not expose the contrast", "evidence_refs": ["pre:1"], "repair_route": "repair-substrate"},
            {"failure_layer": "method_realization", "rationale": "matched simplification may absorb the method", "evidence_refs": ["pre:2"], "repair_route": "simplify-or-merge"},
            {"failure_layer": "operationalization", "rationale": "the representation may not implement the principle", "evidence_refs": ["pre:3"], "repair_route": "repair-operationalization"},
        ]

    def test_historical_labels_exceed_count_gate_but_cannot_backfill_hypotheses(self) -> None:
        inventory = build_historical_failure_label_inventory(PROJECT_ROOT)
        summary = inventory["summary"]
        self.assertGreaterEqual(summary["terminalized_failure_labels"], MIN_PROSPECTIVE_REPLAY_CASES)
        self.assertTrue(summary["historical_label_count_sufficient"])
        self.assertEqual(summary["retrospective_hypothesis_generation_allowed"], 0)
        self.assertTrue(all(row["historical_label_only"] for row in inventory["rows"]))
        self.assertTrue(all(row["eligible_to_generate_retrospective_hypotheses"] is False for row in inventory["rows"]))

    def test_hypotheses_freeze_before_final_label_and_have_zero_authority(self) -> None:
        state = build_failure_hypothesis_set(case_id="C1", evidence_refs=["trace:pre"], hypotheses=self.hypotheses())
        self.assertEqual(state["status"], "HYPOTHESIS_SET_FROZEN")
        self.assertTrue(state["frozen_before_final_adjudication"])
        self.assertEqual(len(state["hypotheses"]), 3)
        self.assertFalse(state["scientific_authority"])
        self.assertFalse(state["experiment_authority"])

    def test_final_label_visibility_blocks_hindsight_hypothesis_generation(self) -> None:
        state = build_failure_hypothesis_set(case_id="C1", evidence_refs=["trace:pre"], hypotheses=self.hypotheses(), final_label_visible=True)
        self.assertEqual(state["status"], "HYPOTHESIS_SET_BLOCKED")
        self.assertIn("final-label-visible-before-hypothesis-freeze", state["blockers"])

    def test_scoring_requires_independent_final_adjudication(self) -> None:
        frozen = build_failure_hypothesis_set(case_id="C1", evidence_refs=["trace:pre"], hypotheses=self.hypotheses())
        blocked = score_failure_hypothesis_set(
            frozen, final_failure_layer="method_realization", final_evidence_refs=["final:1"], final_label_independently_adjudicated=False,
        )
        self.assertEqual(blocked["status"], "SCORING_BLOCKED")
        scored = score_failure_hypothesis_set(
            frozen, final_failure_layer="method_realization", final_evidence_refs=["final:1"], final_label_independently_adjudicated=True,
        )
        self.assertEqual(scored["status"], "PROSPECTIVE_CASE_SCORED")
        self.assertFalse(scored["top1_correct"])
        self.assertTrue(scored["topk_contains_truth"])
        self.assertEqual(scored["rank_of_truth"], 2)
        self.assertFalse(scored["scientific_authority"])

    def test_sage_mhfa_remains_shadow_until_prospective_replay_exists(self) -> None:
        state = build_sage_mhfa_shadow_state(PROJECT_ROOT)
        self.assertEqual(state["status"], "SHADOW_REGISTRY_READY_PROSPECTIVE_REPLAY_PENDING")
        self.assertGreaterEqual(state["summary"]["historical_terminalized_labels"], MIN_PROSPECTIVE_REPLAY_CASES)
        self.assertEqual(state["summary"]["prospective_scored_cases"], 0)
        self.assertFalse(state["summary"]["adoption_gap_test_ready"])
        self.assertEqual(state["summary"]["retrospective_label_leakage_allowed"], 0)


if __name__ == "__main__":
    unittest.main()
