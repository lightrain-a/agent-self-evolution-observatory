from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .submission_attempt_history import build_attempt_history
from .submission_attempt_lineage import build_attempt_plan, publish_attempt_plan
from .test_submission_attempt_post_submission import SubmissionAttemptPostSubmissionTest


class SubmissionAttemptHistoryTest(unittest.TestCase):
    def test_history_preserves_closed_child_when_new_attempt_is_planned(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            helper = SubmissionAttemptPostSubmissionTest(methodName="test_third_attempt_binds_second_attempt_outcome_not_original_paper_outcome")
            parent, first, _, _, _, _, _, workflow = helper.completed_child(root, "REJECT")
            third = build_attempt_plan(
                paper_ledger=parent,
                target_venue="NeurIPS 2027",
                attempt_type="RESUBMISSION",
                revision_categories=("WRITING",),
                scientific_contract_unchanged=True,
                parent_attempt=first,
                parent_attempt_workflow=workflow,
            )
            publish_attempt_plan(third, root)
            history = build_attempt_history(parent["paper_id"], root / "paper-submission-attempts", root / "paper-submission-attempt-workflows")
            self.assertEqual(history["summary"]["attempts"], 2)
            self.assertEqual(history["summary"]["venue_submissions"], 1)
            self.assertEqual(history["summary"]["review_sets"], 1)
            self.assertEqual(history["summary"]["final_decisions"], 1)
            self.assertEqual(history["summary"]["post_decision_learn_complete"], 1)
            self.assertEqual(history["latest_attempt_sha256"], third["attempt_sha256"])
            self.assertEqual(history["attempts"][0]["workflow_status"], "ATTEMPT_POST_DECISION_LEARN_COMPLETE")
            self.assertEqual(history["attempts"][1]["workflow_status"], "ATTEMPT_WORKFLOW_NOT_STARTED")
            self.assertEqual(history["attempts"][1]["parent_attempt_id"], first["attempt_id"])
            self.assertTrue(history["attempts"][0]["parent_submission_bytes_immutable"])

    def test_history_is_public_safe_and_does_not_expose_reviewer_text_or_paths(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            helper = SubmissionAttemptPostSubmissionTest(methodName="test_child_review_rebuttal_decision_learning_closes_without_scientific_authority")
            parent, _, _, _, _, _, _, _ = helper.completed_child(root, "REJECT")
            history = build_attempt_history(parent["paper_id"], root / "paper-submission-attempts", root / "paper-submission-attempt-workflows")
            raw = json.dumps(history, ensure_ascii=False)
            self.assertNotIn(str(root), raw)
            self.assertNotIn("Clarify how the frozen evidence supports the claim", raw)
            self.assertNotIn("A broader experiment would strengthen the paper", raw)
            self.assertFalse(history["authority"]["scientific"])
            self.assertFalse(history["authority"]["submission"])

    def test_history_digest_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            helper = SubmissionAttemptPostSubmissionTest(methodName="test_child_review_rebuttal_decision_learning_closes_without_scientific_authority")
            parent, _, _, _, _, _, _, _ = helper.completed_child(root, "REJECT")
            first = build_attempt_history(parent["paper_id"], root / "paper-submission-attempts", root / "paper-submission-attempt-workflows")
            second = build_attempt_history(parent["paper_id"], root / "paper-submission-attempts", root / "paper-submission-attempt-workflows")
            self.assertEqual(first, second)
            self.assertEqual(first["history_sha256"], second["history_sha256"])

    def test_invalid_historical_workflow_is_visible_not_dropped(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            helper = SubmissionAttemptPostSubmissionTest(methodName="test_child_review_rebuttal_decision_learning_closes_without_scientific_authority")
            parent, plan, _, _, _, _, _, _ = helper.completed_child(root, "REJECT")
            path = root / "paper-submission-attempt-workflows" / f"{plan['attempt_id']}.json"
            row = json.loads(path.read_text())
            row["events"][0]["receipt"]["status"] = "TAMPERED"
            path.write_text(json.dumps(row), encoding="utf-8")
            history = build_attempt_history(parent["paper_id"], root / "paper-submission-attempts", root / "paper-submission-attempt-workflows")
            self.assertEqual(history["summary"]["attempts"], 1)
            self.assertEqual(history["summary"]["invalid_attempts"], 1)
            self.assertEqual(history["attempts"][0]["workflow_status"], "ATTEMPT_WORKFLOW_INVALID")
            self.assertTrue(history["attempts"][0]["workflow_validation_errors"])

    def test_empty_history_is_stable(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            history = build_attempt_history("NONE", root / "paper-submission-attempts", root / "paper-submission-attempt-workflows")
            self.assertEqual(history["summary"]["attempts"], 0)
            self.assertEqual(history["attempts"], [])
            self.assertTrue(history["history_sha256"])


if __name__ == "__main__":
    unittest.main()
