from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .presubmission_freeze import artifact
from .reopened_child_claim_audit import build_child_claim_audit
from .reopened_child_paper_contract import build_child_paper_contract
from .submission_attempt_workflow import (
    append_attempt_workflow_receipt,
    build_attempt_freeze,
    build_attempt_handoff,
    build_attempt_preparation,
    current_attempt_workflow_summary,
    preparation_identity,
    validate_attempt_freeze,
    validate_attempt_handoff,
    validate_attempt_preparation,
    validate_attempt_workflow_ledger,
)
from .test_paper_preparation_protocol import passing_packet
from .test_reopened_child_claim_audit import ReopenedChildClaimAuditTest
from .test_reopened_child_paper_contract import ReopenedChildPaperContractTest
from .test_submission_attempt_workflow import SubmissionAttemptWorkflowTest, policy


class ReopenedAttemptScientificResolutionTest(unittest.TestCase):
    def resolved_fixture(self, root: Path):
        audit_helper = ReopenedChildClaimAuditTest(methodName="test_existing_and_boundary_claims_pass_to_contract_revision_not_claim_update")
        handoff = audit_helper.handoff(root)
        audit = build_child_claim_audit(handoff=handoff, audit_packet=audit_helper.packet(handoff))
        contract_helper = ReopenedChildPaperContractTest(methodName="test_contract_freezes_supported_claim_delta_without_parent_update_or_preparation_authority")
        child_contract = build_child_paper_contract(handoff=handoff, claim_audit=audit, revision_spec=contract_helper.spec(audit))
        attempt = None
        for path in (root / "paper-submission-attempts").glob("*.json"):
            ledger = json.loads(path.read_text())
            for event in ledger.get("events") or []:
                receipt = event.get("receipt") or {}
                if receipt.get("attempt_sha256") == handoff["attempt_sha256"]:
                    attempt = receipt
        if not attempt:
            raise RuntimeError("scientific attempt fixture missing")
        return attempt, handoff, audit, child_contract

    def artifacts(self, root: Path):
        package = root / "resolved-child-package"; package.mkdir(parents=True, exist_ok=True)
        pdf = package / "main.pdf"; pdf.write_bytes(b"resolved-child-pdf")
        source = package / "source.zip"; source.write_bytes(b"resolved-source")
        return pdf, [artifact("paper_pdf", pdf), artifact("source_zip", source)]

    def test_scientific_attempt_remains_blocked_without_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); attempt, _, _, _ = self.resolved_fixture(root)
            self.assertTrue(attempt["requires_explicit_scientific_reopen"])
            self.assertFalse(attempt["machine_preparation_eligible"])
            with self.assertRaisesRegex(RuntimeError, "explicit scientific reopen"):
                build_attempt_preparation(attempt_plan=attempt, preparation_packet=passing_packet())

    def test_resolved_scientific_attempt_prepares_against_child_contract_sha(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); attempt, _, audit, child_contract = self.resolved_fixture(root)
            prep = build_attempt_preparation(attempt_plan=attempt, preparation_packet=passing_packet(), scientific_resolution=child_contract)
            self.assertTrue(validate_attempt_preparation(prep))
            self.assertTrue(prep["scientific_reopen_resolved"])
            self.assertFalse(prep["scientific_contract_unchanged"])
            self.assertTrue(prep["child_claim_revision_frozen"])
            self.assertEqual(prep["resolved_child_paper_contract_sha256"], child_contract["child_paper_contract_sha256"])
            self.assertEqual(prep["child_claim_audit_sha256"], audit["child_claim_audit_sha256"])
            self.assertEqual(prep["parent_contract_sha256"], attempt["contract_sha256"])
            self.assertEqual(prep["paper_preparation_receipt"]["contract_sha256"], child_contract["child_paper_contract_sha256"])
            self.assertFalse(prep["claim_expansion_authorized"])
            self.assertFalse(prep["new_experiment_authorized"])

    def test_resolved_preparation_freeze_handoff_remain_attempt_scoped_and_parent_immutable(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); attempt, _, _, child_contract = self.resolved_fixture(root)
            parent_path = root / "paper-acceptance" / f"{attempt['paper_id']}.json"
            parent_before = parent_path.read_bytes()
            prep = build_attempt_preparation(attempt_plan=attempt, preparation_packet=passing_packet(), scientific_resolution=child_contract)
            _, artifacts = self.artifacts(root); venue_policy = policy(attempt["target_venue"])
            freeze = build_attempt_freeze(attempt_plan=attempt, preparation_receipt=prep, artifacts=artifacts, venue_policy=venue_policy)
            handoff = build_attempt_handoff(attempt_plan=attempt, preparation_receipt=prep, freeze_receipt=freeze, venue_policy=venue_policy)
            self.assertTrue(validate_attempt_freeze(freeze)); self.assertTrue(validate_attempt_handoff(handoff))
            row = append_attempt_workflow_receipt(root, prep)
            row = append_attempt_workflow_receipt(root, freeze)
            row = append_attempt_workflow_receipt(root, handoff)
            self.assertEqual(validate_attempt_workflow_ledger(row), [])
            summary = current_attempt_workflow_summary(row)
            self.assertEqual(summary["status"], "ATTEMPT_MACHINE_HANDOFF_READY_HUMAN_CONFIRMATION_REQUIRED")
            self.assertEqual(row["attempt_sha256"], attempt["attempt_sha256"])
            self.assertEqual(parent_path.read_bytes(), parent_before)
            self.assertTrue(handoff["parent_submission_bytes_immutable"])

    def test_normal_paper_side_attempt_identity_has_no_resolution_fields(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); helper = SubmissionAttemptWorkflowTest(methodName="test_attempt_scoped_preparation_freeze_handoff_is_append_only_and_ready")
            _, attempt = helper.safe_attempt(root)
            prep = build_attempt_preparation(attempt_plan=attempt, preparation_packet=passing_packet())
            self.assertTrue(validate_attempt_preparation(prep))
            self.assertNotIn("scientific_reopen_resolved", prep)
            self.assertNotIn("resolved_child_paper_contract_sha256", prep)
            identity = preparation_identity(prep)
            self.assertEqual(set(identity), {"paper_id", "contract_sha256", "attempt_sha256", "parent_submission_receipt_sha256", "paper_preparation_receipt_sha256", "status"})
            self.assertTrue(prep["scientific_contract_unchanged"])

    def test_paper_side_attempt_rejects_injected_scientific_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); _, _, _, child_contract = self.resolved_fixture(root)
            helper = SubmissionAttemptWorkflowTest(methodName="test_attempt_scoped_preparation_freeze_handoff_is_append_only_and_ready")
            normal_root = root / "normal-paper-side-fixture"
            normal_root.mkdir()
            _, normal_attempt = helper.safe_attempt(normal_root, venue="NeurIPS 2027")
            with self.assertRaisesRegex(RuntimeError, "must not inject"):
                build_attempt_preparation(attempt_plan=normal_attempt, preparation_packet=passing_packet(), scientific_resolution=child_contract)


if __name__ == "__main__":
    unittest.main()
