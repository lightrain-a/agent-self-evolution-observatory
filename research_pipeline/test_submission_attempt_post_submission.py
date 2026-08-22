from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from .submission_attempt_lineage import build_attempt_plan, validate_attempt_plan
from .submission_attempt_post_submission import (
    build_attempt_learning_packet,
    build_attempt_rebuttal_preparation,
    build_attempt_rebuttal_skipped_by_venue,
    build_attempt_review_set,
    build_attempt_venue_decision,
    validate_attempt_learning_packet,
    validate_attempt_rebuttal_preparation,
    validate_attempt_rebuttal_skipped,
    validate_attempt_review_set,
    validate_attempt_venue_decision,
)
from .submission_attempt_workflow import (
    append_attempt_workflow_receipt,
    attempt_checklist_items,
    build_attempt_actual_submission,
    build_attempt_human_signoff,
    build_attempt_submission_conflict_guard,
    current_attempt_workflow_summary,
    validate_attempt_workflow_ledger,
)
from .test_submission_attempt_workflow import SubmissionAttemptWorkflowTest


class SubmissionAttemptPostSubmissionTest(unittest.TestCase):
    def submitted_child(self, root: Path):
        helper = SubmissionAttemptWorkflowTest(methodName="test_attempt_human_signoff_and_actual_submission_are_attempt_scoped")
        parent, plan, _, artifacts, _, _, handoff, row = helper.handoff_fixture(root)
        checks = [item["check_id"] for item in attempt_checklist_items(handoff)]
        signoff = build_attempt_human_signoff(
            workflow_ledger=row,
            confirmed_check_ids=checks,
            external_human_confirmation_ref="human:child-review-fixture",
            confirmed_at="2027-01-07T10:00:00+00:00",
            acknowledge_current_artifact_hashes=True,
            acknowledge_actual_submission_not_performed=True,
        )
        row = append_attempt_workflow_receipt(root, signoff)
        guard = build_attempt_submission_conflict_guard(root=root, workflow_ledger=row, signoff_receipt=signoff)
        self.assertTrue(guard["pass"])
        row = append_attempt_workflow_receipt(root, guard)
        submission = build_attempt_actual_submission(
            workflow_ledger=row,
            signoff_receipt=signoff,
            conflict_guard_receipt=guard,
            venue_submission_id="child-review-001",
            venue_forum_ref="venue:child-review-001",
            uploaded_artifact_sha256={item["label"]: item["sha256"] for item in artifacts},
            submitted_at="2027-01-08T11:00:00+00:00",
            external_human_submission_authority_ref="human:child-review-upload",
        )
        row = append_attempt_workflow_receipt(root, submission)
        self.assertEqual(current_attempt_workflow_summary(row)["status"], "ATTEMPT_VENUE_SUBMISSION_CONFIRMED")
        return parent, plan, submission, row

    def reviews(self):
        return [
            {"review_id": "R1", "source_ref": "venue:R1", "received_at": "2027-03-01T12:00:00+00:00", "text": "Clarify how the frozen evidence supports the claim.", "rating": 5, "confidence": 4},
            {"review_id": "R2", "source_ref": "venue:R2", "received_at": "2027-03-01T12:01:00+00:00", "text": "A broader experiment would strengthen the paper.", "rating": 4, "confidence": 3},
        ]

    def normal_rebuttal(self, parent, row, review_set):
        evidence_ref = str((parent.get("contract") or {}).get("evidence_refs", ["artifact:evidence"])[0])
        seg1 = "The frozen evidence already supports the scoped claim."
        seg2 = "We preserve the broader experiment request as a limitation."
        receipt = build_attempt_rebuttal_preparation(
            paper_ledger=parent,
            workflow_ledger=row,
            review_set=review_set,
            objections=[
                {"objection_id": "O1", "review_ids": ["R1"], "category": "clarity", "summary": "Clarify support.", "decision_critical": True, "evidence_state": "EXISTING_EVIDENCE", "claim_ids": []},
                {"objection_id": "O2", "review_ids": ["R2"], "category": "evidence", "summary": "Requests broader experiment.", "decision_critical": True, "evidence_state": "MISSING_DECISIVE_EVIDENCE", "claim_ids": []},
            ],
            resolutions=[
                {"objection_id": "O1", "action": "ANSWER_WITH_EXISTING_EVIDENCE", "response_segment": seg1, "evidence_refs": [evidence_ref]},
                {"objection_id": "O2", "action": "PRESERVE_LIMITATION", "response_segment": seg2, "evidence_refs": []},
            ],
            response_text=seg1 + " " + seg2,
            response_limit_words=500,
        )
        self.assertTrue(receipt["pass"], receipt["blockers"])
        return receipt

    def lessons(self, decision):
        return [
            {"lesson_id": "L1", "category": "PAPER_POSITIONING", "reuse_scope": "WRITING_HEURISTIC", "statement": "Lead with the scoped causal boundary earlier.", "basis_refs": ["attempt-decision:" + decision["attempt_venue_decision_sha256"]], "claim_ids": []},
            {"lesson_id": "L2", "category": "SCIENTIFIC_DIAGNOSTIC", "reuse_scope": "SCIENTIFIC_DIAGNOSTIC_ONLY", "statement": "The reviewer requested broader evidence; treat this as diagnostic until independent scientific evidence exists.", "basis_refs": ["attempt-decision:" + decision["attempt_venue_decision_sha256"]], "claim_ids": []},
        ]

    def completed_child(self, root: Path, decision_name: str = "REJECT"):
        parent, plan, submission, row = self.submitted_child(root)
        review_set = build_attempt_review_set(row, self.reviews())
        row = append_attempt_workflow_receipt(root, review_set)
        rebuttal = self.normal_rebuttal(parent, row, review_set)
        row = append_attempt_workflow_receipt(root, rebuttal)
        decision = build_attempt_venue_decision(
            paper_ledger=parent, workflow_ledger=row, decision_id="D-child", source_ref="venue:decision-child",
            received_at="2027-04-01T12:00:00+00:00", decision=decision_name,
            decision_text=f"Final child attempt decision: {decision_name}.", decision_phase="POST_REBUTTAL", rebuttal_available=True,
        )
        row = append_attempt_workflow_receipt(root, decision)
        learning = build_attempt_learning_packet(paper_ledger=parent, workflow_ledger=row, venue_decision=decision, lessons=self.lessons(decision))
        self.assertTrue(learning["pass"], learning["blockers"])
        row = append_attempt_workflow_receipt(root, learning)
        return parent, plan, submission, review_set, rebuttal, decision, learning, row

    def test_child_review_rebuttal_decision_learning_closes_without_scientific_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            parent, _, _, review_set, rebuttal, decision, learning, row = self.completed_child(root, "REJECT")
            self.assertTrue(validate_attempt_review_set(review_set))
            self.assertTrue(validate_attempt_rebuttal_preparation(rebuttal))
            self.assertTrue(validate_attempt_venue_decision(decision))
            self.assertTrue(validate_attempt_learning_packet(learning))
            self.assertEqual(validate_attempt_workflow_ledger(row), [])
            summary = current_attempt_workflow_summary(row)
            self.assertEqual(summary["status"], "ATTEMPT_POST_DECISION_LEARN_COMPLETE")
            self.assertEqual(summary["review_count"], 2)
            self.assertEqual(summary["rebuttal_missing_decisive_evidence"], 1)
            self.assertEqual(summary["venue_decision"], "REJECT")
            self.assertEqual(summary["learning_lessons"], 2)
            self.assertEqual(summary["learning_scientific_diagnostic_only"], 1)
            self.assertFalse(rebuttal["new_experiment_authorized"])
            self.assertFalse(learning["automatic_reopen_authorized"])
            self.assertEqual(parent["current_state"], "LEARN")

    def test_child_terminal_decision_skips_rebuttal_without_fabricated_reviews(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            parent, _, _, row = self.submitted_child(root)
            decision = build_attempt_venue_decision(
                paper_ledger=parent, workflow_ledger=row, decision_id="desk-child", source_ref="venue:desk-child",
                received_at="2027-02-01T12:00:00+00:00", decision="REJECT", decision_text="Desk reject with no rebuttal window.",
                decision_phase="PRE_REBUTTAL_TERMINAL", rebuttal_available=False,
            )
            row = append_attempt_workflow_receipt(root, decision)
            self.assertEqual(current_attempt_workflow_summary(row)["status"], "ATTEMPT_TERMINAL_DECISION_SKIP_PENDING")
            skip = build_attempt_rebuttal_skipped_by_venue(workflow_ledger=row, venue_decision=decision)
            self.assertTrue(validate_attempt_rebuttal_skipped(skip)); self.assertTrue(skip["review_fabrication_forbidden"])
            row = append_attempt_workflow_receipt(root, skip)
            self.assertEqual(current_attempt_workflow_summary(row)["status"], "ATTEMPT_FINAL_DECISION_LEARNING_PENDING")
            learning = build_attempt_learning_packet(paper_ledger=parent, workflow_ledger=row, venue_decision=decision, lessons=self.lessons(decision))
            row = append_attempt_workflow_receipt(root, learning)
            self.assertEqual(current_attempt_workflow_summary(row)["status"], "ATTEMPT_POST_DECISION_LEARN_COMPLETE")
            counts = {kind: sum(event.get("event_type") == kind for event in row["events"]) for kind in ("attempt-review-set", "attempt-rebuttal-preparation", "attempt-rebuttal-skipped-by-venue")}
            self.assertEqual(counts, {"attempt-review-set": 0, "attempt-rebuttal-preparation": 0, "attempt-rebuttal-skipped-by-venue": 1})
            self.assertEqual(validate_attempt_workflow_ledger(row), [])

    def test_missing_decisive_evidence_cannot_be_disguised_as_existing_evidence_answer(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            parent, _, _, row = self.submitted_child(root)
            review_set = build_attempt_review_set(row, self.reviews()); row = append_attempt_workflow_receipt(root, review_set)
            evidence_ref = str((parent.get("contract") or {}).get("evidence_refs", ["artifact:evidence"])[0])
            bad = build_attempt_rebuttal_preparation(
                paper_ledger=parent, workflow_ledger=row, review_set=review_set,
                objections=[{"objection_id": "O1", "review_ids": ["R2"], "category": "evidence", "summary": "Need experiment", "decision_critical": True, "evidence_state": "MISSING_DECISIVE_EVIDENCE", "claim_ids": []}],
                resolutions=[{"objection_id": "O1", "action": "ANSWER_WITH_EXISTING_EVIDENCE", "response_segment": "Existing evidence resolves it.", "evidence_refs": [evidence_ref]}],
                response_text="Existing evidence resolves it.", response_limit_words=100,
            )
            self.assertFalse(bad["pass"])
            self.assertIn("attempt-rebuttal-missing-evidence-cannot-be-papered-over:O1", bad["blockers"])
            self.assertFalse(bad["new_experiment_authorized"])

    def test_review_text_tampering_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, _, _, row = self.submitted_child(root)
            review = build_attempt_review_set(row, self.reviews())
            bad = copy.deepcopy(review); bad["review_records"][0]["text"] = "tampered reviewer text"
            self.assertFalse(validate_attempt_review_set(bad))

    def test_third_attempt_binds_second_attempt_outcome_not_original_paper_outcome(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            parent, plan, child_submission, _, _, child_decision, child_learning, row = self.completed_child(root, "REJECT")
            third = build_attempt_plan(
                paper_ledger=parent, target_venue="NeurIPS 2027", attempt_type="RESUBMISSION",
                revision_categories=("WRITING",), scientific_contract_unchanged=True,
                parent_attempt=plan, parent_attempt_workflow=row,
            )
            self.assertTrue(validate_attempt_plan(third))
            self.assertEqual(third["parent_attempt_sha256"], plan["attempt_sha256"])
            self.assertEqual(third["parent_submission_receipt_sha256"], child_submission["attempt_submission_receipt_sha256"])
            self.assertEqual(third["parent_venue_decision_sha256"], child_decision["attempt_venue_decision_sha256"])
            self.assertEqual(third["parent_learning_receipt_sha256"], child_learning["attempt_learning_receipt_sha256"])
            original_submission = next(e["receipt"] for e in parent["events"] if e.get("event_type") == "actual-submission")
            self.assertNotEqual(third["parent_submission_receipt_sha256"], original_submission["submission_receipt_sha256"])

    def test_child_accept_can_produce_camera_ready_bound_to_child_venue(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            parent, plan, child_submission, _, _, _, _, row = self.completed_child(root, "ACCEPT")
            camera = build_attempt_plan(
                paper_ledger=parent, target_venue=child_submission["venue"], attempt_type="CAMERA_READY",
                revision_categories=("CAMERA_READY_FORMATTING", "AUTHOR_METADATA"), scientific_contract_unchanged=True,
                parent_attempt=plan, parent_attempt_workflow=row,
            )
            self.assertTrue(camera["machine_preparation_eligible"])
            self.assertEqual(camera["parent_submission_receipt_sha256"], child_submission["attempt_submission_receipt_sha256"])
            with self.assertRaisesRegex(RuntimeError, "camera-ready target venue"):
                build_attempt_plan(
                    paper_ledger=parent, target_venue="Different Venue", attempt_type="CAMERA_READY",
                    revision_categories=("CAMERA_READY_FORMATTING",), scientific_contract_unchanged=True,
                    parent_attempt=plan, parent_attempt_workflow=row,
                )

    def test_incomplete_parent_attempt_workflow_cannot_be_used_as_outcome_parent(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            parent, plan, _, row = self.submitted_child(root)
            self.assertEqual(current_attempt_workflow_summary(row)["status"], "ATTEMPT_VENUE_SUBMISSION_CONFIRMED")
            with self.assertRaisesRegex(RuntimeError, "not post-decision-learn complete"):
                build_attempt_plan(
                    paper_ledger=parent, target_venue="NeurIPS 2027", attempt_type="RESUBMISSION",
                    revision_categories=("WRITING",), scientific_contract_unchanged=True,
                    parent_attempt=plan, parent_attempt_workflow=row,
                )


if __name__ == "__main__":
    unittest.main()
