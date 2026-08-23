from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from .human_submission_signoff import (
    SIGNOFF_STATUS,
    append_signoff,
    build_signoff_receipt,
    build_signoff_template,
    validate_signoff_ledger,
    validate_signoff_receipt,
    signoff_identity,
    verify_current_signoff,
)
from .submission_handoff import append_handoff, build_handoff_receipt
from .test_submission_handoff import SubmissionHandoffTest
from .venue_form_consistency import append_venue_form_audit, build_form_contract_template, build_venue_form_audit_receipt


class HumanSubmissionSignoffTest(unittest.TestCase):
    def fixture(self, root: Path):
        helper = SubmissionHandoffTest(methodName="test_handoff_requires_current_freeze_and_is_idempotent")
        paper_ledger, freeze_ledger, policy, paper = helper.ready_fixture(root)
        handoff = build_handoff_receipt(paper_ledger=paper_ledger, freeze_ledger=freeze_ledger, venue_policy=policy)
        handoff_ledger = append_handoff(root, handoff)
        form_contract = build_form_contract_template(
            paper_ledger=paper_ledger,
            freeze_ledger=freeze_ledger,
            handoff_ledger=handoff_ledger,
            venue_policy=policy,
        )
        form_contract["expected_fields"]["keywords"] = ["agents", "memory"]
        form_contract["expected_fields"]["ai_use_disclosure"] = {"used": True, "summary": "AI tools assisted editing."}
        expected = form_contract["expected_fields"]
        form_snapshot = {
            "schema_version": "1.0",
            "paper_id": form_contract["paper_id"],
            "venue": form_contract["venue"],
            "capture_method": "OPENREVIEW_FINAL_FORM_EXPORT",
            "captured_at": "2026-09-24T11:00:00+00:00",
            "fields": {
                "title": expected["title"],
                "abstract": expected["abstract"],
                "keywords": expected["keywords"],
                "author_visibility": expected["author_visibility"],
                "ai_use_disclosure": expected["ai_use_disclosure"],
                "supplement_declared": expected["supplement_declared"],
                "supplement_artifacts": expected["supplement_artifacts"],
            },
        }
        form_receipt = build_venue_form_audit_receipt(form_contract=form_contract, form_snapshot=form_snapshot)
        form_ledger = append_venue_form_audit(root, form_receipt)
        return handoff_ledger, freeze_ledger, form_ledger, paper

    def test_template_requires_explicit_human_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            handoff_ledger, _, form_ledger, _ = self.fixture(root)
            template = build_signoff_template(handoff_ledger, form_ledger)
            self.assertEqual(template["status"], "PENDING_HUMAN_CONFIRMATION")
            self.assertEqual(len(template["required_confirmations"]), 10)
            self.assertFalse(template["submission_authority"])
            self.assertIn("external_human_confirmation_ref", template["required_explicit_inputs"])
            self.assertIn("venue_form_audit_sha256 from a current PASS venue-form audit", template["required_explicit_inputs"])

    def test_complete_human_signoff_is_append_only_but_not_submitted(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            handoff_ledger, freeze_ledger, form_ledger, _ = self.fixture(root)
            template = build_signoff_template(handoff_ledger, form_ledger)
            ids = [row["check_id"] for row in template["required_confirmations"]]
            receipt = build_signoff_receipt(
                handoff_ledger=handoff_ledger,
                freeze_ledger=freeze_ledger,
                venue_form_audit_ledger=form_ledger,
                confirmed_check_ids=ids,
                external_human_confirmation_ref="human-confirmation:test",
                confirmed_at="2026-08-22T12:00:00+00:00",
                acknowledge_current_artifact_hashes=True,
                acknowledge_actual_submission_not_performed=True,
            )
            self.assertEqual(receipt["status"], SIGNOFF_STATUS)
            self.assertEqual(receipt["actual_submission_status"], "NOT_SUBMITTED")
            self.assertFalse(receipt["submission_authority"])
            self.assertTrue(receipt["venue_form_audit_sha256"])
            self.assertTrue(validate_signoff_receipt(receipt))
            row = append_signoff(root, receipt)
            row = append_signoff(root, receipt)
            self.assertEqual(len(row["events"]), 1)
            self.assertEqual(validate_signoff_ledger(row), [])
            self.assertEqual(verify_current_signoff(row, handoff_ledger, freeze_ledger, form_ledger), [])

    def test_missing_confirmation_or_byte_drift_blocks_signoff(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            handoff_ledger, freeze_ledger, form_ledger, paper = self.fixture(root)
            template = build_signoff_template(handoff_ledger, form_ledger)
            ids = [row["check_id"] for row in template["required_confirmations"]]
            with self.assertRaisesRegex(RuntimeError, "missing human confirmations"):
                build_signoff_receipt(
                    handoff_ledger=handoff_ledger,
                    freeze_ledger=freeze_ledger,
                    venue_form_audit_ledger=form_ledger,
                    confirmed_check_ids=ids[:-1],
                    external_human_confirmation_ref="human-confirmation:test",
                    confirmed_at="2026-08-22T12:00:00+00:00",
                    acknowledge_current_artifact_hashes=True,
                    acknowledge_actual_submission_not_performed=True,
                )
            paper.write_bytes(b"changed-after-handoff")
            with self.assertRaisesRegex(RuntimeError, "frozen artifacts are stale"):
                build_signoff_receipt(
                    handoff_ledger=handoff_ledger,
                    freeze_ledger=freeze_ledger,
                    venue_form_audit_ledger=form_ledger,
                    confirmed_check_ids=ids,
                    external_human_confirmation_ref="human-confirmation:test",
                    confirmed_at="2026-08-22T12:00:00+00:00",
                    acknowledge_current_artifact_hashes=True,
                    acknowledge_actual_submission_not_performed=True,
                )

    def test_missing_or_failed_venue_form_audit_blocks_signoff(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            handoff_ledger, freeze_ledger, form_ledger, _ = self.fixture(root)
            template = build_signoff_template(handoff_ledger, form_ledger)
            ids = [row["check_id"] for row in template["required_confirmations"]]
            empty_form_ledger = {"schema_version": "1.0", "paper_id": "FREEZE-PAPER", "events": [], "authority": {"scientific": False, "experiment": False, "gpu": False, "submission": False}}
            with self.assertRaisesRegex(RuntimeError, "venue form audit is missing"):
                build_signoff_receipt(
                    handoff_ledger=handoff_ledger,
                    freeze_ledger=freeze_ledger,
                    venue_form_audit_ledger=empty_form_ledger,
                    confirmed_check_ids=ids,
                    external_human_confirmation_ref="human-confirmation:test",
                    confirmed_at="2026-08-22T12:00:00+00:00",
                    acknowledge_current_artifact_hashes=True,
                    acknowledge_actual_submission_not_performed=True,
                )

    def test_legacy_v1_signoff_receipt_remains_replayable(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            handoff_ledger, freeze_ledger, form_ledger, _ = self.fixture(root)
            template = build_signoff_template(handoff_ledger, form_ledger)
            ids = [row["check_id"] for row in template["required_confirmations"]]
            receipt = build_signoff_receipt(
                handoff_ledger=handoff_ledger,
                freeze_ledger=freeze_ledger,
                venue_form_audit_ledger=form_ledger,
                confirmed_check_ids=ids,
                external_human_confirmation_ref="human-confirmation:legacy-replay",
                confirmed_at="2026-08-22T12:00:00+00:00",
                acknowledge_current_artifact_hashes=True,
                acknowledge_actual_submission_not_performed=True,
            )
            legacy = copy.deepcopy(receipt)
            legacy["schema_version"] = "1.0"
            legacy.pop("venue_form_audit_sha256", None)
            raw = json.dumps(signoff_identity(legacy), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
            legacy["signoff_sha256"] = hashlib.sha256(raw).hexdigest()
            self.assertTrue(validate_signoff_receipt(legacy))

    def test_signoff_tamper_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            handoff_ledger, freeze_ledger, form_ledger, _ = self.fixture(root)
            template = build_signoff_template(handoff_ledger, form_ledger)
            ids = [row["check_id"] for row in template["required_confirmations"]]
            receipt = build_signoff_receipt(
                handoff_ledger=handoff_ledger,
                freeze_ledger=freeze_ledger,
                venue_form_audit_ledger=form_ledger,
                confirmed_check_ids=ids,
                external_human_confirmation_ref="human-confirmation:test",
                confirmed_at="2026-08-22T12:00:00+00:00",
                acknowledge_current_artifact_hashes=True,
                acknowledge_actual_submission_not_performed=True,
            )
            bad = copy.deepcopy(receipt)
            bad["confirmed_check_ids"] = bad["confirmed_check_ids"][:-1]
            self.assertFalse(validate_signoff_receipt(bad))


if __name__ == "__main__":
    unittest.main()
