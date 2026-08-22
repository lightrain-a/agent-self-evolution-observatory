from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from .reopened_child_claim_audit import build_child_claim_audit, publish_child_claim_audit
from .reopened_child_claim_expansion_authorization import build_child_claim_expansion_authorization, publish_child_claim_expansion_authorization
from .reopened_child_paper_contract import build_child_paper_contract, publish_child_paper_contract
from .reopened_scientific_evidence_paper_handoff import build_scientific_evidence_paper_handoff, publish_scientific_evidence_paper_handoff
from .reopened_scientific_paper_return import public_scientific_paper_return_state
from .submission_attempt_workflow import append_attempt_workflow_receipt, build_attempt_preparation
from .test_paper_preparation_protocol import passing_packet
from .test_reopened_child_claim_audit import ReopenedChildClaimAuditTest
from .test_reopened_child_paper_contract import ReopenedChildPaperContractTest
from .test_reopened_scientific_evidence_paper_handoff import ReopenedScientificEvidencePaperHandoffTest


class ReopenedScientificPaperReturnTest(unittest.TestCase):
    def source(self, root: Path):
        helper = ReopenedScientificEvidencePaperHandoffTest(methodName="test_method_pass_creates_child_revision_handoff_but_not_claim_or_preparation_authority")
        attempt, contract, result, adjudication = helper.fixture(root)
        handoff = build_scientific_evidence_paper_handoff(
            attempt_plan=attempt,
            reopened_contract=contract,
            p0_result_packet=result,
            p0_adjudication=adjudication,
            revision_spec=helper.revision_spec(),
        )
        return attempt, handoff

    def audited(self, root: Path):
        attempt, handoff = self.source(root)
        publish_scientific_evidence_paper_handoff(root, handoff, recorded_at="2027-04-14T12:00:00+00:00")
        helper = ReopenedChildClaimAuditTest(methodName="test_existing_and_boundary_claims_pass_to_contract_revision_not_claim_update")
        audit = build_child_claim_audit(handoff=handoff, audit_packet=helper.packet(handoff))
        publish_child_claim_audit(root, audit)
        return attempt, handoff, audit

    def contracted(self, root: Path):
        attempt, handoff, audit = self.audited(root)
        helper = ReopenedChildPaperContractTest(methodName="test_contract_freezes_supported_claim_delta_without_parent_update_or_preparation_authority")
        contract = build_child_paper_contract(handoff=handoff, claim_audit=audit, revision_spec=helper.spec(audit))
        publish_child_paper_contract(root, contract)
        return attempt, handoff, audit, contract

    def test_state_requires_evidence_handoff_before_paper_return(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); attempt, _ = self.source(root)
            state = public_scientific_paper_return_state(root, attempt["attempt_sha256"])
            self.assertEqual(state["status"], "SCIENTIFIC_EVIDENCE_PAPER_HANDOFF_REQUIRED")
            self.assertTrue(state["requires_explicit_scientific_reopen"])
            self.assertFalse(state["parent_claim_update_authorized"])

    def test_state_progresses_handoff_to_claim_audit_to_child_contract(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); attempt, handoff = self.source(root)
            publish_scientific_evidence_paper_handoff(root, handoff, recorded_at="2027-04-14T12:00:00+00:00")
            state = public_scientific_paper_return_state(root, attempt["attempt_sha256"])
            self.assertEqual(state["status"], "SCIENTIFIC_REOPEN_EVIDENCE_READY_CHILD_CLAIM_AUDIT_REQUIRED")
            helper = ReopenedChildClaimAuditTest(methodName="test_existing_and_boundary_claims_pass_to_contract_revision_not_claim_update")
            audit = build_child_claim_audit(handoff=handoff, audit_packet=helper.packet(handoff)); publish_child_claim_audit(root, audit)
            state = public_scientific_paper_return_state(root, attempt["attempt_sha256"])
            self.assertEqual(state["status"], "SCIENTIFIC_REOPEN_CHILD_CLAIM_AUDIT_PASS_CONTRACT_REVISION_REQUIRED")
            helper2 = ReopenedChildPaperContractTest(methodName="test_contract_freezes_supported_claim_delta_without_parent_update_or_preparation_authority")
            contract = build_child_paper_contract(handoff=handoff, claim_audit=audit, revision_spec=helper2.spec(audit)); publish_child_paper_contract(root, contract)
            state = public_scientific_paper_return_state(root, attempt["attempt_sha256"])
            self.assertEqual(state["status"], "SCIENTIFIC_REOPEN_CHILD_PAPER_CONTRACT_FROZEN_PREPARATION_REQUIRED")
            self.assertEqual(state["supported_claims"], 2)
            self.assertFalse(state["new_claim_expansion_authorized"])

    def test_human_new_claim_expansion_is_visible_but_still_requires_contract_revision(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            from .test_reopened_scientific_evidence_paper_handoff import ReopenedScientificEvidencePaperHandoffTest
            source = ReopenedScientificEvidencePaperHandoffTest(methodName="test_method_pass_creates_child_revision_handoff_but_not_claim_or_preparation_authority")
            spec = source.revision_spec(); spec["candidate_claims"].append({"claim_id":"C-NEW-RETURN","claim_text":"A new child claim for explicit expansion authority.","evidence_role":"SUPPORTING","claim_relation":"NEW_CHILD_CLAIM"})
            helper = ReopenedChildClaimAuditTest(methodName="test_new_child_claim_is_held_for_human_expansion_authority")
            handoff = helper.handoff(root, spec=spec); publish_scientific_evidence_paper_handoff(root, handoff, recorded_at="2027-04-14T12:00:00+00:00")
            audit = build_child_claim_audit(handoff=handoff, audit_packet=helper.packet(handoff)); publish_child_claim_audit(root, audit)
            auth = build_child_claim_expansion_authorization(claim_audit=audit, approved_new_claim_ids=["C-NEW-RETURN"], external_authority_ref="human:private-expansion", authorized_at="2027-04-16T12:00:00+00:00", scope="Only C-NEW-RETURN within this child paper revision.")
            publish_child_claim_expansion_authorization(root, auth)
            state = public_scientific_paper_return_state(root, handoff["attempt_sha256"])
            self.assertEqual(state["status"], "CHILD_NEW_CLAIM_HUMAN_EXPANSION_AUTHORIZED_CONTRACT_REVISION_REQUIRED")
            self.assertEqual(state["approved_new_claims"], 1)
            self.assertTrue(state["claim_expansion_authorization_sha256"])
            self.assertFalse(state["new_claim_expansion_authorized"])
            self.assertFalse(state["parent_claim_update_authorized"])

    def test_resolved_attempt_workflow_overrides_scientific_reopen_hold_without_parent_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); attempt, _, _, child_contract = self.contracted(root)
            prep = build_attempt_preparation(attempt_plan=attempt, preparation_packet=passing_packet(), scientific_resolution=child_contract)
            append_attempt_workflow_receipt(root, prep)
            state = public_scientific_paper_return_state(root, attempt["attempt_sha256"])
            self.assertEqual(state["status"], "SCIENTIFIC_REOPEN_RESOLVED_RETURNED_TO_ATTEMPT_WORKFLOW")
            self.assertEqual(state["attempt_workflow_status"], "ATTEMPT_PREPARATION_PASS_FREEZE_PENDING")
            self.assertTrue(state["parent_submission_bytes_immutable"])
            self.assertFalse(state["parent_claim_update_authorized"])
            self.assertFalse(state["scientific_authority"])
            self.assertFalse(state["submission_authority"])

    def test_public_state_contains_only_counts_and_hashes_not_claim_text(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); attempt, _, _, _ = self.contracted(root)
            state = public_scientific_paper_return_state(root, attempt["attempt_sha256"])
            raw = str(state)
            self.assertNotIn("The reopened method produces", raw)
            self.assertNotIn("independent-child-claim-auditor", raw)
            self.assertTrue(state["child_paper_contract_sha256"])


if __name__ == "__main__":
    unittest.main()
