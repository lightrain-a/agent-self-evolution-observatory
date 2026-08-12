from __future__ import annotations

import unittest

from .paper_first_stop_triage import build_paper_first_stop_triage


class PaperFirstStopTriageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state = build_paper_first_stop_triage()
        cls.rows = {row["idea_id"]: row for row in cls.state["rows"]}
        cls.candidate = cls.state["paper_candidates"][0]

    def test_all_current_p0_rows_are_triaged_without_reactivation(self) -> None:
        self.assertEqual(self.state["summary"]["active_p0_rows"], 31)
        self.assertEqual(len(self.state["rows"]), 31)
        self.assertEqual(self.state["summary"]["old_methods_reactivated"], 0)
        self.assertTrue(all(row["execution_authorized"] is False for row in self.state["rows"]))

    def test_only_one_genuinely_new_paper_problem_is_opened(self) -> None:
        self.assertEqual(self.state["summary"]["paper_redesign_candidates"], 1)
        self.assertEqual(self.candidate["paper_id"], "trajectory-mediated-memory-effect-transport")
        self.assertEqual(
            self.candidate["parent_evidence"],
            ["B-8 replicated-effect-memory-gate", "B-9 cross-task-effect-transport-certificate"],
        )
        self.assertIn("Genuinely new research problem", self.candidate["relationship_to_closed_program"])
        self.assertFalse(self.candidate["local_validation_authorized"])
        self.assertFalse(self.candidate["full_experiment_authorized"])

    def test_paper_design_contract_is_structurally_complete_but_not_execution_authority(self) -> None:
        audit = self.candidate["paper_design_audit"]
        self.assertTrue(audit["passed"], audit.get("blockers"))
        self.assertEqual(audit["blockers"], [])
        design = self.candidate["paper_design"]
        self.assertEqual(len(design["experiment_blueprint"]["claim_experiment_matrix"]), 3)
        self.assertTrue(self.candidate["fresh_collision_review_required_before_local_validation"])
        self.assertTrue(self.candidate["fresh_collision_review_complete"])
        self.assertEqual(self.candidate["fresh_collision_review"]["decision"], "PASS_NARROW_TRAJECTORY_MEDIATED_TRANSPORTABILITY")
        self.assertEqual(len(self.candidate["fresh_collision_review"]["sources"]), 7)
        self.assertTrue(self.candidate["ai_premortem_required_before_local_validation"])
        self.assertTrue(self.candidate["environment_feasibility_complete"])
        self.assertEqual(self.candidate["feasibility"]["prefix_replay_smoke"]["status"], "ENVIRONMENT_REPLAY_FEASIBILITY_PASS")
        self.assertTrue(self.candidate["feasibility"]["prefix_replay_smoke"]["all_public_steps_equal"])
        self.assertEqual(self.candidate["feasibility"]["prefix_replay_smoke"]["selected_tasks"], 20)
        self.assertEqual(self.candidate["feasibility"]["prefix_replay_smoke"]["task_families"], 6)

    def test_closed_and_diagnostic_lines_do_not_become_children(self) -> None:
        self.assertEqual(self.rows["self-label-confidence-flow"]["disposition"], "ARCHIVE_PHENOMENON_MERGE_COMPONENT")
        self.assertEqual(self.rows["self-correction-collapse-detector"]["disposition"], "ARCHIVE_PHENOMENON_MERGE_COMPONENT")
        for idea_id in (
            "compositional-update-compatibility",
            "lineage-aware-rollback",
            "active-causal-minimal-rollback",
            "counterfactual-evolution-decision-controller",
            "world-model-error-gated-learning",
            "irreversible-action-counterfactuals",
            "recovery-conditioned-experience",
        ):
            self.assertEqual(self.rows[idea_id]["disposition"], "TERMINATE_OR_MERGE_CURRENT_REALIZATION")

    def test_substrate_stops_cannot_be_rescued_before_paper_novelty(self) -> None:
        for idea_id in (
            "budgeted-evolution-controller",
            "regression-gated-self-evolution",
            "contradiction-preserving-consolidation",
            "retrieval-interference-auditor",
            "workflow-generalization-certificate",
        ):
            self.assertEqual(self.rows[idea_id]["disposition"], "PAPER_NOVELTY_HOLD_NO_SUBSTRATE_RESCUE")

    def test_new_paper_first_p0_rows_remain_non_authoritative(self) -> None:
        for idea_id in ("future-learnability-preserving-self-evolution", "diagnosability-preserving-self-evolution"):
            self.assertEqual(self.rows[idea_id]["disposition"], "NO_ACTION")
            self.assertFalse(self.rows[idea_id]["execution_authorized"])
        for idea_id in ("cross-surface-repair-routing", "failure-mode-transport-under-self-evolution"):
            self.assertEqual(self.rows[idea_id]["disposition"], "PROBLEM_HOLD_NO_METHOD")
            self.assertFalse(self.rows[idea_id]["execution_authorized"])

    def test_b8_b9_are_evidence_only_not_reactivated_methods(self) -> None:
        for idea_id in ("replicated-effect-memory-gate", "cross-task-effect-transport-certificate"):
            self.assertEqual(self.rows[idea_id]["disposition"], "PARENT_EVIDENCE_FOR_NEW_PAPER_PROBLEM")
            self.assertFalse(self.rows[idea_id]["execution_authorized"])


if __name__ == "__main__":
    unittest.main()
