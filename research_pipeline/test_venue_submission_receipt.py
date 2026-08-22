from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from .human_submission_signoff import append_signoff, build_signoff_receipt, build_signoff_template
from .paper_acceptance import PaperState
from .paper_acceptance_ledger import (
    advance_frozen_paper_to_submitted,
    advance_paper_ledger,
    record_actual_submission,
    record_frozen_contract_actual_submission,
    validate_paper_ledger,
)
from .presubmission_freeze import artifact, build_freeze, digest, publish_freeze
from .submission_handoff import append_handoff, build_handoff_receipt
from .test_presubmission_freeze import PreSubmissionFreezeTest
from .venue_submission_receipt import (
    build_submission_receipt,
    external_transition_authority_ref,
    validate_submission_receipt,
)


class VenueSubmissionReceiptTest(unittest.TestCase):
    def fixture(self, root: Path):
        helper = PreSubmissionFreezeTest(methodName="test_artifact_hash_changes_when_bytes_change")
        contract = helper.ready(root)
        paper = root / "paper.pdf"
        source = root / "source.zip"
        paper.write_bytes(b"paper-bytes")
        source.write_bytes(b"source-bytes")
        policy = {
            "schema_version": "1.0",
            "venue": "TEST 2027",
            "deadlines_aoe": {"abstract": "2026-09-18", "full_paper": "2026-09-25"},
            "human_only_confirmation_required": True,
            "scientific_authority": False,
            "submission_authority": False,
        }
        policy["snapshot_sha256"] = digest(policy)
        freeze_receipt = build_freeze(
            contract.paper_id,
            [artifact("paper_pdf", paper), artifact("source_zip", source)],
            policy,
            root,
        )
        freeze_ledger = publish_freeze(freeze_receipt, root)
        paper_ledger = json.loads((root / "paper-acceptance" / f"{contract.paper_id}.json").read_text())
        handoff_receipt = build_handoff_receipt(
            paper_ledger=paper_ledger,
            freeze_ledger=freeze_ledger,
            venue_policy=policy,
        )
        handoff_ledger = append_handoff(root, handoff_receipt)
        template = build_signoff_template(handoff_ledger)
        ids = [row["check_id"] for row in template["required_confirmations"]]
        signoff_receipt = build_signoff_receipt(
            handoff_ledger=handoff_ledger,
            freeze_ledger=freeze_ledger,
            confirmed_check_ids=ids,
            external_human_confirmation_ref="human-confirmation:test-only",
            confirmed_at="2026-08-22T12:00:00+00:00",
            acknowledge_current_artifact_hashes=True,
            acknowledge_actual_submission_not_performed=True,
        )
        signoff_ledger = append_signoff(root, signoff_receipt)
        uploaded = {
            str(row["label"]): str(row["sha256"])
            for row in freeze_receipt["frozen_artifacts"]
        }
        return contract, paper_ledger, freeze_ledger, handoff_ledger, signoff_ledger, uploaded, paper

    def test_actual_receipt_is_required_and_exactly_binds_submitted_transition(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            contract, paper_ledger, freeze_ledger, handoff_ledger, signoff_ledger, uploaded, _ = self.fixture(root)

            arbitrary = advance_paper_ledger(
                root,
                contract,
                PaperState.SUBMITTED,
                external_submission_authority_ref="human:submit-approval",
            )
            self.assertFalse(arbitrary["receipt"]["allowed"])
            self.assertIn("actual-submission-receipt-required", arbitrary["receipt"]["blockers"])

            receipt = build_submission_receipt(
                paper_ledger=paper_ledger,
                freeze_ledger=freeze_ledger,
                handoff_ledger=handoff_ledger,
                signoff_ledger=signoff_ledger,
                venue_submission_id="TEST-2027-0042",
                venue_forum_ref="forum:test-0042",
                uploaded_artifact_sha256=uploaded,
                submitted_at="2026-08-22T12:05:00+00:00",
                external_human_submission_authority_ref="human-submit:test-only",
            )
            self.assertTrue(validate_submission_receipt(receipt))
            self.assertFalse(receipt["submission_authority"])
            row = record_actual_submission(root, contract, receipt)
            self.assertEqual(row["summary"]["actual_submission_receipts"], 1)

            wrong_ref = advance_paper_ledger(
                root,
                contract,
                PaperState.SUBMITTED,
                external_submission_authority_ref="human-submit:test-only",
            )
            self.assertFalse(wrong_ref["receipt"]["allowed"])
            self.assertIn("external-submission-authority-ref-must-bind-receipt", wrong_ref["receipt"]["blockers"])

            authority_ref = external_transition_authority_ref(receipt)
            submitted = advance_paper_ledger(
                root,
                contract,
                PaperState.SUBMITTED,
                external_submission_authority_ref=authority_ref,
            )
            self.assertTrue(submitted["receipt"]["allowed"])
            self.assertEqual(submitted["ledger"]["current_state"], PaperState.SUBMITTED.value)
            self.assertEqual(
                submitted["receipt"]["gate_receipts"]["actual_submission_receipt_sha256"],
                receipt["submission_receipt_sha256"],
            )
            self.assertEqual(validate_paper_ledger(submitted["ledger"]), [])
            self.assertFalse(submitted["receipt"]["submission_authority"])
            tampered_ledger = copy.deepcopy(submitted["ledger"])
            actual_event = next(event for event in tampered_ledger["events"] if event.get("event_type") == "actual-submission")
            actual_event["receipt"]["venue_submission_id"] = "TAMPERED-IN-LEDGER"
            self.assertIn("invalid-content-addressed-receipt:actual-submission", validate_paper_ledger(tampered_ledger))

    def test_legacy_frozen_contract_submission_path_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            contract, paper_ledger, freeze_ledger, handoff_ledger, signoff_ledger, uploaded, _ = self.fixture(root)
            receipt = build_submission_receipt(
                paper_ledger=paper_ledger,
                freeze_ledger=freeze_ledger,
                handoff_ledger=handoff_ledger,
                signoff_ledger=signoff_ledger,
                venue_submission_id="TEST-2027-0043",
                venue_forum_ref="forum:test-0043",
                uploaded_artifact_sha256=uploaded,
                submitted_at="2026-08-22T12:06:00+00:00",
                external_human_submission_authority_ref="human-submit:test-only-legacy",
            )
            first = record_frozen_contract_actual_submission(root, contract.paper_id, receipt)
            second = record_frozen_contract_actual_submission(root, contract.paper_id, receipt)
            self.assertEqual(first["summary"]["actual_submission_receipts"], 1)
            self.assertEqual(second["summary"]["actual_submission_receipts"], 1)
            authority_ref = external_transition_authority_ref(receipt)
            submitted = advance_frozen_paper_to_submitted(
                root,
                contract.paper_id,
                external_submission_authority_ref=authority_ref,
            )
            repeated = advance_frozen_paper_to_submitted(
                root,
                contract.paper_id,
                external_submission_authority_ref=authority_ref,
            )
            self.assertTrue(submitted["receipt"]["allowed"])
            self.assertEqual(repeated["receipt"]["event_id"], submitted["receipt"]["event_id"])
            self.assertEqual(validate_paper_ledger(repeated["ledger"]), [])

    def test_hash_mismatch_or_stale_bytes_block_actual_submission_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, paper_ledger, freeze_ledger, handoff_ledger, signoff_ledger, uploaded, paper = self.fixture(root)
            bad_uploaded = dict(uploaded)
            bad_uploaded["paper_pdf"] = "0" * 64
            with self.assertRaisesRegex(RuntimeError, "uploaded artifact hashes do not exactly match current freeze"):
                build_submission_receipt(
                    paper_ledger=paper_ledger,
                    freeze_ledger=freeze_ledger,
                    handoff_ledger=handoff_ledger,
                    signoff_ledger=signoff_ledger,
                    venue_submission_id="TEST-2027-0042",
                    venue_forum_ref="forum:test-0042",
                    uploaded_artifact_sha256=bad_uploaded,
                    submitted_at="2026-08-22T12:05:00+00:00",
                    external_human_submission_authority_ref="human-submit:test-only",
                )
            paper.write_bytes(b"drift-after-human-signoff")
            with self.assertRaisesRegex(RuntimeError, "frozen artifacts are stale"):
                build_submission_receipt(
                    paper_ledger=paper_ledger,
                    freeze_ledger=freeze_ledger,
                    handoff_ledger=handoff_ledger,
                    signoff_ledger=signoff_ledger,
                    venue_submission_id="TEST-2027-0042",
                    venue_forum_ref="forum:test-0042",
                    uploaded_artifact_sha256=uploaded,
                    submitted_at="2026-08-22T12:05:00+00:00",
                    external_human_submission_authority_ref="human-submit:test-only",
                )

    def test_missing_or_stale_human_signoff_blocks_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, paper_ledger, freeze_ledger, handoff_ledger, _, uploaded, _ = self.fixture(root)
            empty_signoff = {"schema_version": "1.0", "paper_id": "FREEZE-PAPER", "events": [], "authority": {"scientific": False, "experiment": False, "gpu": False, "submission": False}}
            with self.assertRaisesRegex(RuntimeError, "human signoff is missing or stale"):
                build_submission_receipt(
                    paper_ledger=paper_ledger,
                    freeze_ledger=freeze_ledger,
                    handoff_ledger=handoff_ledger,
                    signoff_ledger=empty_signoff,
                    venue_submission_id="TEST-2027-0042",
                    venue_forum_ref="forum:test-0042",
                    uploaded_artifact_sha256=uploaded,
                    submitted_at="2026-08-22T12:05:00+00:00",
                    external_human_submission_authority_ref="human-submit:test-only",
                )

    def test_submission_receipt_tamper_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, paper_ledger, freeze_ledger, handoff_ledger, signoff_ledger, uploaded, _ = self.fixture(root)
            receipt = build_submission_receipt(
                paper_ledger=paper_ledger,
                freeze_ledger=freeze_ledger,
                handoff_ledger=handoff_ledger,
                signoff_ledger=signoff_ledger,
                venue_submission_id="TEST-2027-0042",
                venue_forum_ref="forum:test-0042",
                uploaded_artifact_sha256=uploaded,
                submitted_at="2026-08-22T12:05:00+00:00",
                external_human_submission_authority_ref="human-submit:test-only",
            )
            bad = copy.deepcopy(receipt)
            bad["venue_submission_id"] = "TAMPERED"
            self.assertFalse(validate_submission_receipt(bad))


if __name__ == "__main__":
    unittest.main()
