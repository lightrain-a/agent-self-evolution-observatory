from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from .paper_acceptance import PaperState
from .paper_acceptance_ledger import (
    advance_frozen_paper_to_learn,
    advance_paper_ledger,
    record_frozen_contract_post_decision_learning,
    record_frozen_contract_venue_decision,
    record_rebuttal_preparation,
    validate_paper_ledger,
)
from .post_decision_learning import (
    build_learning_packet,
    build_venue_decision_receipt,
    validate_learning_receipt,
    validate_venue_decision_receipt,
)
from .rebuttal_protocol import build_review_set
from .test_rebuttal_protocol import RebuttalProtocolTest


class PostDecisionLearningTest(unittest.TestCase):
    def rebuttal_fixture(self, root: Path):
        helper = RebuttalProtocolTest(methodName="test_review_intake_and_rebuttal_gate_are_content_addressed")
        contract, submitted, _ = helper.submitted_fixture(root)
        reviews = helper.review_set(submitted)
        receipt = helper.passing_rebuttal(submitted, reviews)
        record_rebuttal_preparation(root, contract, receipt)
        advanced = advance_paper_ledger(root, contract, PaperState.REBUTTAL)
        self.assertTrue(advanced["receipt"]["allowed"])
        self.assertEqual(validate_paper_ledger(advanced["ledger"]), [])
        return contract, advanced["ledger"], receipt

    def decision(self, ledger, decision="REJECT"):
        return build_venue_decision_receipt(
            paper_ledger=ledger,
            decision_id=f"decision-{decision.lower()}",
            source_ref=f"venue-decision:{decision.lower()}",
            received_at="2026-11-15T12:00:00+00:00",
            decision=decision,
            decision_text=f"Final venue decision: {decision}.",
        )

    def lessons(self, decision_receipt):
        dref = "venue-decision:" + decision_receipt["venue_decision_sha256"]
        return [
            {
                "lesson_id": "L1",
                "category": "PAPER_POSITIONING",
                "reuse_scope": "PAPER_PREPARATION_HEURISTIC",
                "statement": "State the strongest matched baseline earlier in the introduction.",
                "basis_refs": [dref],
                "claim_ids": [],
            },
            {
                "lesson_id": "L2",
                "category": "SCIENTIFIC_DIAGNOSTIC",
                "reuse_scope": "SCIENTIFIC_DIAGNOSTIC_ONLY",
                "statement": "Reviewer disagreement around C1 should be treated as a diagnostic signal, not scientific counterevidence.",
                "basis_refs": [dref],
                "claim_ids": ["C1"],
            },
        ]

    def test_reject_decision_and_learning_enter_learn_without_rewriting_science(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, ledger, _ = self.rebuttal_fixture(root)
            blocked = advance_frozen_paper_to_learn(root, ledger["paper_id"])
            self.assertFalse(blocked["receipt"]["allowed"])
            self.assertIn("venue-final-decision-receipt-required", blocked["receipt"]["blockers"])

            decision = self.decision(ledger, "REJECT")
            self.assertTrue(validate_venue_decision_receipt(decision))
            self.assertTrue(decision["scientific_claim_status_unchanged"])
            self.assertTrue(decision["rejection_does_not_refute_scientific_claims"])
            record_frozen_contract_venue_decision(root, ledger["paper_id"], decision)

            current = __import__("json").loads((root / "paper-acceptance" / f"{ledger['paper_id']}.json").read_text())
            learning = build_learning_packet(paper_ledger=current, venue_decision=decision, lessons=self.lessons(decision))
            self.assertTrue(learning["pass"])
            self.assertTrue(validate_learning_receipt(learning))
            self.assertFalse(learning["claim_expansion_authorized"])
            self.assertFalse(learning["new_experiment_authorized"])
            self.assertFalse(learning["automatic_reopen_authorized"])
            record_frozen_contract_post_decision_learning(root, ledger["paper_id"], learning)

            advanced = advance_frozen_paper_to_learn(root, ledger["paper_id"])
            self.assertTrue(advanced["receipt"]["allowed"])
            self.assertEqual(advanced["ledger"]["current_state"], PaperState.LEARN.value)
            self.assertEqual(advanced["receipt"]["gate_receipts"]["venue_decision_sha256"], decision["venue_decision_sha256"])
            self.assertEqual(advanced["receipt"]["gate_receipts"]["learning_receipt_sha256"], learning["learning_receipt_sha256"])
            self.assertEqual(validate_paper_ledger(advanced["ledger"]), [])

    def test_accept_does_not_prove_scientific_truth(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, ledger, _ = self.rebuttal_fixture(root)
            decision = self.decision(ledger, "ACCEPT")
            self.assertTrue(validate_venue_decision_receipt(decision))
            self.assertTrue(decision["acceptance_does_not_prove_scientific_truth"])
            self.assertTrue(decision["scientific_claim_status_unchanged"])
            self.assertFalse(decision["scientific_authority"])

    def test_scientific_lesson_cannot_escape_diagnostic_scope(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, ledger, _ = self.rebuttal_fixture(root)
            decision = self.decision(ledger, "REJECT")
            bad = [{
                "lesson_id": "L-science",
                "category": "SCIENTIFIC_DIAGNOSTIC",
                "reuse_scope": "EXPERIMENT_DESIGN_PRIOR",
                "statement": "Treat the rejection as proof that C1 is false.",
                "basis_refs": ["venue-decision:" + decision["venue_decision_sha256"]],
                "claim_ids": ["C1"],
            }]
            learning = build_learning_packet(paper_ledger=ledger, venue_decision=decision, lessons=bad)
            self.assertFalse(learning["pass"])
            self.assertIn("learning-scientific-lesson-must-remain-diagnostic:L-science", learning["blockers"])
            self.assertFalse(learning["automatic_reopen_authorized"])

    def test_decision_and_learning_tamper_are_detected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, ledger, _ = self.rebuttal_fixture(root)
            decision = self.decision(ledger, "REJECT")
            bad_decision = copy.deepcopy(decision)
            bad_decision["decision"] = "ACCEPT"
            self.assertFalse(validate_venue_decision_receipt(bad_decision))
            learning = build_learning_packet(paper_ledger=ledger, venue_decision=decision, lessons=self.lessons(decision))
            self.assertTrue(validate_learning_receipt(learning))
            bad_learning = copy.deepcopy(learning)
            bad_learning["lessons"][0]["statement_sha256"] = "0" * 64
            self.assertFalse(validate_learning_receipt(bad_learning))


if __name__ == "__main__":
    unittest.main()
