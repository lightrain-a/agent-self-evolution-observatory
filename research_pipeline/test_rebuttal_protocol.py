from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from .paper_acceptance import PaperState
from .paper_acceptance_ledger import (
    advance_paper_ledger,
    record_actual_submission,
    record_rebuttal_preparation,
    validate_paper_ledger,
)
from .rebuttal_protocol import (
    append_review_set,
    build_rebuttal_preparation,
    build_review_set,
    validate_rebuttal_receipt,
    validate_review_set,
)
from .test_venue_submission_receipt import VenueSubmissionReceiptTest
from .venue_submission_receipt import build_submission_receipt, external_transition_authority_ref


class RebuttalProtocolTest(unittest.TestCase):
    def submitted_fixture(self, root: Path):
        helper = VenueSubmissionReceiptTest(methodName="test_submission_receipt_tamper_is_detected")
        contract, paper_ledger, freeze_ledger, handoff_ledger, signoff_ledger, uploaded, _ = helper.fixture(root)
        actual = build_submission_receipt(
            paper_ledger=paper_ledger,
            freeze_ledger=freeze_ledger,
            handoff_ledger=handoff_ledger,
            signoff_ledger=signoff_ledger,
            venue_submission_id="TEST-2027-REBUTTAL",
            venue_forum_ref="forum:test-rebuttal",
            uploaded_artifact_sha256=uploaded,
            submitted_at="2026-08-22T12:20:00+00:00",
            external_human_submission_authority_ref="human-submit:rebuttal-test",
        )
        record_actual_submission(root, contract, actual)
        submitted = advance_paper_ledger(
            root,
            contract,
            PaperState.SUBMITTED,
            external_submission_authority_ref=external_transition_authority_ref(actual),
        )
        self.assertTrue(submitted["receipt"]["allowed"])
        return contract, submitted["ledger"], actual

    def review_set(self, paper_ledger):
        reviews = [
            {
                "review_id": "R1",
                "source_ref": "venue-review:R1",
                "received_at": "2026-11-01T10:00:00+00:00",
                "text": "Please explain the strongest baseline and why the existing evidence supports C1.",
                "rating": 6,
                "confidence": 4,
            },
            {
                "review_id": "R2",
                "source_ref": "venue-review:R2",
                "received_at": "2026-11-01T10:05:00+00:00",
                "text": "Please add a second-model claim and a new decisive experiment.",
                "rating": 5,
                "confidence": 3,
            },
        ]
        return build_review_set(paper_ledger, reviews)

    def passing_rebuttal(self, paper_ledger, review_set):
        objections = [
            {
                "objection_id": "O1",
                "review_ids": ["R1"],
                "category": "baseline",
                "summary": "The strongest baseline is unclear.",
                "decision_critical": True,
                "evidence_state": "EXISTING_EVIDENCE",
                "claim_ids": ["C1"],
            },
            {
                "objection_id": "O2",
                "review_ids": ["R2"],
                "category": "scope",
                "summary": "Reviewer requests a second-model extension outside the frozen claim.",
                "decision_critical": True,
                "evidence_state": "REQUIRES_NEW_CLAIM",
                "claim_ids": [],
            },
        ]
        segment1 = "The frozen evidence already supports C1 and the rebuttal points directly to that comparison."
        segment2 = "A second-model extension is outside the frozen claim scope and remains a limitation."
        resolutions = [
            {"objection_id": "O1", "action": "ANSWER_WITH_EXISTING_EVIDENCE", "response_segment": segment1, "evidence_refs": ["artifact:evidence"]},
            {"objection_id": "O2", "action": "PRESERVE_LIMITATION", "response_segment": segment2, "evidence_refs": []},
        ]
        return build_rebuttal_preparation(
            paper_ledger=paper_ledger,
            review_set=review_set,
            objections=objections,
            resolutions=resolutions,
            response_text=segment1 + "\n\n" + segment2,
            response_limit_words=200,
        )

    def test_review_intake_and_rebuttal_gate_are_content_addressed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            contract, paper_ledger, _ = self.submitted_fixture(root)
            blocked = advance_paper_ledger(root, contract, PaperState.REBUTTAL)
            self.assertFalse(blocked["receipt"]["allowed"])
            self.assertIn("rebuttal-preparation-pass-receipt-required", blocked["receipt"]["blockers"])

            reviews = self.review_set(paper_ledger)
            self.assertTrue(validate_review_set(reviews))
            intake = append_review_set(root, reviews)
            intake = append_review_set(root, reviews)
            self.assertEqual(len(intake["events"]), 1)

            receipt = self.passing_rebuttal(paper_ledger, reviews)
            self.assertTrue(receipt["pass"])
            self.assertTrue(validate_rebuttal_receipt(receipt))
            self.assertFalse(receipt["claim_expansion_authorized"])
            self.assertFalse(receipt["new_experiment_authorized"])
            record_rebuttal_preparation(root, contract, receipt)
            advanced = advance_paper_ledger(root, contract, PaperState.REBUTTAL)
            self.assertTrue(advanced["receipt"]["allowed"])
            self.assertEqual(advanced["ledger"]["current_state"], PaperState.REBUTTAL.value)
            self.assertEqual(advanced["receipt"]["gate_receipts"]["rebuttal_preparation_receipt_sha256"], receipt["rebuttal_receipt_sha256"])
            self.assertEqual(validate_paper_ledger(advanced["ledger"]), [])

            tampered = copy.deepcopy(advanced["ledger"])
            event = next(e for e in tampered["events"] if e.get("event_type") == "rebuttal-preparation")
            event["receipt"]["response_words"] += 1
            self.assertIn("invalid-content-addressed-receipt:rebuttal-preparation", validate_paper_ledger(tampered))

    def test_missing_decisive_evidence_cannot_be_papered_over(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, paper_ledger, _ = self.submitted_fixture(root)
            reviews = self.review_set(paper_ledger)
            segment = "The current evidence already proves the requested new experiment is unnecessary."
            receipt = build_rebuttal_preparation(
                paper_ledger=paper_ledger,
                review_set=reviews,
                objections=[{
                    "objection_id": "O3",
                    "review_ids": ["R2"],
                    "category": "evidence",
                    "summary": "Reviewer requests a decisive missing intervention.",
                    "decision_critical": True,
                    "evidence_state": "MISSING_DECISIVE_EVIDENCE",
                    "claim_ids": ["C1"],
                }],
                resolutions=[{
                    "objection_id": "O3",
                    "action": "ANSWER_WITH_EXISTING_EVIDENCE",
                    "response_segment": segment,
                    "evidence_refs": ["artifact:evidence"],
                }],
                response_text=segment,
                response_limit_words=100,
            )
            self.assertFalse(receipt["pass"])
            self.assertIn("rebuttal-missing-evidence-cannot-be-papered-over:O3", receipt["blockers"])
            self.assertFalse(receipt["new_experiment_authorized"])

    def test_new_claim_request_must_preserve_frozen_scope(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, paper_ledger, _ = self.submitted_fixture(root)
            reviews = self.review_set(paper_ledger)
            segment = "We extend the paper to a new model family and now claim generality."
            receipt = build_rebuttal_preparation(
                paper_ledger=paper_ledger,
                review_set=reviews,
                objections=[{
                    "objection_id": "O4",
                    "review_ids": ["R2"],
                    "category": "scope",
                    "summary": "Reviewer requests a new generalization claim.",
                    "decision_critical": True,
                    "evidence_state": "REQUIRES_NEW_CLAIM",
                    "claim_ids": [],
                }],
                resolutions=[{
                    "objection_id": "O4",
                    "action": "CLARIFY_SCOPE",
                    "response_segment": segment,
                    "evidence_refs": [],
                }],
                response_text=segment,
                response_limit_words=100,
            )
            self.assertFalse(receipt["pass"])
            self.assertIn("rebuttal-new-claim-request-must-preserve-scope:O4", receipt["blockers"])
            self.assertFalse(receipt["claim_expansion_authorized"])

    def test_rebuttal_budget_is_hard_and_review_ids_are_unique(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, paper_ledger, _ = self.submitted_fixture(root)
            with self.assertRaisesRegex(RuntimeError, "review ids must be nonempty and unique"):
                build_review_set(paper_ledger, [
                    {"review_id": "R1", "source_ref": "a", "received_at": "2026-11-01", "text": "one"},
                    {"review_id": "R1", "source_ref": "b", "received_at": "2026-11-02", "text": "two"},
                ])
            reviews = self.review_set(paper_ledger)
            receipt = self.passing_rebuttal(paper_ledger, reviews)
            receipt2 = build_rebuttal_preparation(
                paper_ledger=paper_ledger,
                review_set=reviews,
                objections=[{
                    "objection_id": "O5",
                    "review_ids": ["R1"],
                    "category": "clarity",
                    "summary": "Clarify scope.",
                    "decision_critical": True,
                    "evidence_state": "CLARIFICATION_ONLY",
                    "claim_ids": ["C1"],
                }],
                resolutions=[{
                    "objection_id": "O5",
                    "action": "CLARIFY_SCOPE",
                    "response_segment": "one two three four five",
                    "evidence_refs": [],
                }],
                response_text="one two three four five",
                response_limit_words=4,
            )
            self.assertTrue(receipt["pass"])
            self.assertFalse(receipt2["pass"])
            self.assertIn("rebuttal-response-over-budget", receipt2["blockers"])


if __name__ == "__main__":
    unittest.main()
