from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from .paper_acceptance import PaperState
from .paper_acceptance_ledger import (
    advance_frozen_paper_to_learn,
    record_frozen_contract_post_decision_learning,
    record_frozen_contract_venue_decision,
    validate_paper_ledger,
)
from .post_decision_learning import build_learning_packet
from .submission_attempt_lineage import (
    build_attempt_plan,
    public_attempt_summary,
    publish_attempt_plan,
    validate_attempt_ledger,
    validate_attempt_plan,
)
from .test_post_decision_learning import PostDecisionLearningTest


class SubmissionAttemptLineageTest(unittest.TestCase):
    def learned_fixture(self, root: Path, decision_name: str):
        helper = PostDecisionLearningTest(methodName="test_reject_decision_and_learning_enter_learn_without_rewriting_science")
        _, rebuttal_ledger, _ = helper.rebuttal_fixture(root)
        decision = helper.decision(rebuttal_ledger, decision_name)
        record_frozen_contract_venue_decision(root, rebuttal_ledger["paper_id"], decision)
        current = json.loads((root / "paper-acceptance" / f"{rebuttal_ledger['paper_id']}.json").read_text())
        learning = build_learning_packet(paper_ledger=current, venue_decision=decision, lessons=helper.lessons(decision))
        self.assertTrue(learning["pass"])
        record_frozen_contract_post_decision_learning(root, rebuttal_ledger["paper_id"], learning)
        learned = advance_frozen_paper_to_learn(root, rebuttal_ledger["paper_id"])
        self.assertTrue(learned["receipt"]["allowed"])
        self.assertEqual(learned["ledger"]["current_state"], PaperState.LEARN.value)
        self.assertEqual(validate_paper_ledger(learned["ledger"]), [])
        return learned["ledger"], decision, learning

    def test_rejected_paper_can_plan_paper_side_resubmission_without_rewriting_parent(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ledger, decision, learning = self.learned_fixture(root, "REJECT")
            submission = next(e["receipt"] for e in ledger["events"] if e.get("event_type") == "actual-submission")
            plan = build_attempt_plan(
                paper_ledger=ledger,
                target_venue="ICML 2027",
                attempt_type="RESUBMISSION",
                revision_categories=("WRITING", "PAPER_POSITIONING", "CITATION"),
                scientific_contract_unchanged=True,
            )
            self.assertTrue(validate_attempt_plan(plan))
            self.assertEqual(plan["status"], "RESUBMISSION_PAPER_SIDE_ONLY")
            self.assertTrue(plan["machine_preparation_eligible"])
            self.assertFalse(plan["requires_explicit_scientific_reopen"])
            self.assertEqual(plan["parent_submission_receipt_sha256"], submission["submission_receipt_sha256"])
            self.assertEqual(plan["parent_venue_decision_sha256"], decision["venue_decision_sha256"])
            self.assertEqual(plan["parent_learning_receipt_sha256"], learning["learning_receipt_sha256"])
            self.assertTrue(plan["parent_submission_bytes_immutable"])
            self.assertFalse(plan["new_experiment_authorized"])

            row = publish_attempt_plan(plan, root)
            row2 = publish_attempt_plan(plan, root)
            self.assertEqual(len(row["events"]), 1)
            self.assertEqual(len(row2["events"]), 1)
            self.assertEqual(validate_attempt_ledger(row2), [])
            self.assertEqual(json.loads((root / "paper-acceptance" / f"{ledger['paper_id']}.json").read_text())["current_state"], "LEARN")

    def test_scientific_change_requires_explicit_reopen_and_never_grants_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ledger, _, _ = self.learned_fixture(root, "REJECT")
            cases = [
                {"scientific_contract_unchanged": False},
                {"scientific_contract_unchanged": True, "new_claim_requested": True},
                {"scientific_contract_unchanged": True, "new_experiment_requested": True},
                {"scientific_contract_unchanged": True, "new_scientific_evidence_requested": True},
                {"scientific_contract_unchanged": True, "scientific_interpretation_change_requested": True},
            ]
            for index, flags in enumerate(cases):
                with self.subTest(index=index):
                    plan = build_attempt_plan(
                        paper_ledger=ledger,
                        target_venue="ICML 2027",
                        attempt_type="RESUBMISSION",
                        revision_categories=("WRITING",),
                        **flags,
                    )
                    self.assertTrue(validate_attempt_plan(plan))
                    self.assertEqual(plan["status"], "RESUBMISSION_REQUIRES_EXPLICIT_SCIENTIFIC_REOPEN")
                    self.assertFalse(plan["machine_preparation_eligible"])
                    self.assertTrue(plan["requires_explicit_scientific_reopen"])
                    self.assertFalse(plan["automatic_reopen_authorized"])
                    self.assertFalse(plan["scientific_authority"])
                    self.assertFalse(plan["experiment_authority"])
                    self.assertFalse(plan["gpu_authority"])

            category_only = build_attempt_plan(
                paper_ledger=ledger,
                target_venue="ICML 2027",
                attempt_type="RESUBMISSION",
                revision_categories=("SCIENTIFIC_EVIDENCE",),
                scientific_contract_unchanged=True,
            )
            self.assertTrue(category_only["requires_explicit_scientific_reopen"])
            self.assertFalse(category_only["machine_preparation_eligible"])

    def test_accepted_paper_camera_ready_is_separate_child_and_keeps_anonymous_parent_immutable(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ledger, _, _ = self.learned_fixture(root, "ACCEPT")
            submission = next(e["receipt"] for e in ledger["events"] if e.get("event_type") == "actual-submission")
            plan = build_attempt_plan(
                paper_ledger=ledger,
                target_venue=submission["venue"],
                attempt_type="CAMERA_READY",
                revision_categories=("CAMERA_READY_FORMATTING", "AUTHOR_METADATA", "ACKNOWLEDGEMENTS"),
                scientific_contract_unchanged=True,
            )
            self.assertTrue(validate_attempt_plan(plan))
            self.assertEqual(plan["status"], "CAMERA_READY_PAPER_SIDE_ONLY")
            self.assertTrue(plan["machine_preparation_eligible"])
            self.assertTrue(plan["parent_submission_bytes_immutable"])
            self.assertEqual(plan["parent_submission_receipt_sha256"], submission["submission_receipt_sha256"])
            publish_attempt_plan(plan, root)
            canonical = json.loads((root / "paper-acceptance" / f"{ledger['paper_id']}.json").read_text())
            parent_submission_after = next(e["receipt"] for e in canonical["events"] if e.get("event_type") == "actual-submission")
            self.assertEqual(parent_submission_after["submission_receipt_sha256"], submission["submission_receipt_sha256"])

    def test_attempt_type_must_match_parent_venue_decision(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            reject_root = Path(td) / "reject"; reject_root.mkdir()
            rejected, _, _ = self.learned_fixture(reject_root, "REJECT")
            submission = next(e["receipt"] for e in rejected["events"] if e.get("event_type") == "actual-submission")
            with self.assertRaisesRegex(RuntimeError, "camera-ready requires ACCEPT"):
                build_attempt_plan(
                    paper_ledger=rejected,
                    target_venue=submission["venue"],
                    attempt_type="CAMERA_READY",
                    revision_categories=("CAMERA_READY_FORMATTING",),
                    scientific_contract_unchanged=True,
                )

            accept_root = Path(td) / "accept"; accept_root.mkdir()
            accepted, _, _ = self.learned_fixture(accept_root, "ACCEPT")
            with self.assertRaisesRegex(RuntimeError, "resubmission requires rejected"):
                build_attempt_plan(
                    paper_ledger=accepted,
                    target_venue="ICML 2027",
                    attempt_type="RESUBMISSION",
                    revision_categories=("WRITING",),
                    scientific_contract_unchanged=True,
                )
            accepted_submission = next(e["receipt"] for e in accepted["events"] if e.get("event_type") == "actual-submission")
            with self.assertRaisesRegex(RuntimeError, "camera-ready target venue"):
                build_attempt_plan(
                    paper_ledger=accepted,
                    target_venue=accepted_submission["venue"] + "-different",
                    attempt_type="CAMERA_READY",
                    revision_categories=("CAMERA_READY_FORMATTING",),
                    scientific_contract_unchanged=True,
                )

    def test_child_attempt_must_reference_prior_immutable_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ledger, _, _ = self.learned_fixture(root, "REJECT")
            parent = build_attempt_plan(
                paper_ledger=ledger,
                target_venue="ICML 2027",
                attempt_type="RESUBMISSION",
                revision_categories=("WRITING",),
                scientific_contract_unchanged=True,
            )
            child = build_attempt_plan(
                paper_ledger=ledger,
                target_venue="NeurIPS 2027",
                attempt_type="RESUBMISSION",
                revision_categories=("PAPER_POSITIONING",),
                scientific_contract_unchanged=True,
                parent_attempt=parent,
            )
            with self.assertRaisesRegex(RuntimeError, "parent attempt is not present"):
                publish_attempt_plan(child, root)
            publish_attempt_plan(parent, root)
            row = publish_attempt_plan(child, root)
            self.assertEqual(len(row["events"]), 2)
            self.assertEqual(row["events"][1]["receipt"]["parent_attempt_sha256"], parent["attempt_sha256"])
            self.assertEqual(validate_attempt_ledger(row), [])
            public = public_attempt_summary(row)
            self.assertEqual(public["attempts"], 2)
            self.assertEqual(public["latest_attempt_sha256"], child["attempt_sha256"])
            self.assertTrue(public["parent_submission_bytes_immutable"])

    def test_tampering_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ledger, _, _ = self.learned_fixture(root, "REJECT")
            plan = build_attempt_plan(
                paper_ledger=ledger,
                target_venue="ICML 2027",
                attempt_type="RESUBMISSION",
                revision_categories=("WRITING",),
                scientific_contract_unchanged=True,
            )
            bad = copy.deepcopy(plan)
            bad["target_venue"] = "Tampered Venue"
            self.assertFalse(validate_attempt_plan(bad))
            row = publish_attempt_plan(plan, root)
            tampered = copy.deepcopy(row)
            tampered["events"][0]["receipt"]["status"] = "RESUBMISSION_REQUIRES_EXPLICIT_SCIENTIFIC_REOPEN"
            self.assertIn("attempt-receipt-invalid", validate_attempt_ledger(tampered))


if __name__ == "__main__":
    unittest.main()
