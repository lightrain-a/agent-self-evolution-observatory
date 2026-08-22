from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from .reopened_child_claim_audit import (
    AUDITOR_ROLE,
    BLOCK_STATUS,
    CHECKS,
    HOLD_STATUS,
    PASS_STATUS,
    build_child_claim_audit,
    public_child_claim_audit,
    publish_child_claim_audit,
    validate_child_claim_audit,
    validate_child_claim_audit_ledger,
)
from .reopened_scientific_evidence_paper_handoff import build_scientific_evidence_paper_handoff
from .test_reopened_scientific_evidence_paper_handoff import ReopenedScientificEvidencePaperHandoffTest


class ReopenedChildClaimAuditTest(unittest.TestCase):
    def handoff(self, root: Path, *, spec: dict | None = None) -> dict:
        helper = ReopenedScientificEvidencePaperHandoffTest(methodName="test_method_pass_creates_child_revision_handoff_but_not_claim_or_preparation_authority")
        attempt, contract, result, adjudication = helper.fixture(root)
        return build_scientific_evidence_paper_handoff(
            attempt_plan=attempt,
            reopened_contract=contract,
            p0_result_packet=result,
            p0_adjudication=adjudication,
            revision_spec=spec or helper.revision_spec(),
        )

    def packet(self, handoff: dict, *, fail_claim: str = "", fail_check: str = "") -> dict:
        rows = []
        for claim in handoff["candidate_claims"]:
            checks = {key: True for key in CHECKS}
            if claim["claim_id"] == fail_claim and fail_check:
                checks[fail_check] = False
            rows.append({"claim_id": claim["claim_id"], "checks": checks})
        return {
            "auditor_role": AUDITOR_ROLE,
            "auditor_ref": "independent-child-claim-auditor:private-ref",
            "audited_at": "2027-04-15T12:00:00+00:00",
            "claim_checks": rows,
        }

    def test_existing_and_boundary_claims_pass_to_contract_revision_not_claim_update(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); handoff = self.handoff(root)
            receipt = build_child_claim_audit(handoff=handoff, audit_packet=self.packet(handoff))
            self.assertTrue(validate_child_claim_audit(receipt))
            self.assertEqual(receipt["status"], PASS_STATUS)
            self.assertTrue(receipt["claim_audit_passed"])
            self.assertTrue(receipt["paper_contract_revision_eligible"])
            self.assertEqual(receipt["supported_claim_ids"], ["C-REOPEN-METHOD", "C-REOPEN-BOUNDARY"])
            self.assertFalse(receipt["claim_update_authorized"])
            self.assertFalse(receipt["paper_preparation_eligible"])
            self.assertFalse(receipt["submission_eligible"])
            self.assertTrue(receipt["parent_submitted_bytes_immutable"])
            self.assertTrue(receipt["principle_proof_from_method_pass_forbidden"])

    def test_new_child_claim_is_held_for_human_expansion_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); helper = ReopenedScientificEvidencePaperHandoffTest(methodName="test_method_pass_creates_child_revision_handoff_but_not_claim_or_preparation_authority")
            spec = helper.revision_spec()
            spec["candidate_claims"].append({
                "claim_id": "C-NEW-CHILD",
                "claim_text": "A new broader child claim that was absent from the parent contract.",
                "evidence_role": "SUPPORTING",
                "claim_relation": "NEW_CHILD_CLAIM",
            })
            handoff = self.handoff(root, spec=spec)
            receipt = build_child_claim_audit(handoff=handoff, audit_packet=self.packet(handoff))
            self.assertEqual(receipt["status"], PASS_STATUS)
            self.assertTrue(receipt["human_claim_expansion_authority_required"])
            self.assertEqual(receipt["held_new_claim_ids"], ["C-NEW-CHILD"])
            self.assertNotIn("C-NEW-CHILD", receipt["supported_claim_ids"])
            self.assertFalse(receipt["new_claim_expansion_authorized"])
            self.assertTrue(receipt["paper_contract_revision_eligible"])

    def test_only_new_claims_hold_entire_audit_until_human_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); helper = ReopenedScientificEvidencePaperHandoffTest(methodName="test_method_pass_creates_child_revision_handoff_but_not_claim_or_preparation_authority")
            spec = helper.revision_spec(); spec["candidate_claims"] = [{
                "claim_id": "C-NEW-ONLY",
                "claim_text": "A wholly new child claim.",
                "evidence_role": "PRIMARY",
                "claim_relation": "NEW_CHILD_CLAIM",
            }]
            handoff = self.handoff(root, spec=spec)
            receipt = build_child_claim_audit(handoff=handoff, audit_packet=self.packet(handoff))
            self.assertEqual(receipt["status"], HOLD_STATUS)
            self.assertFalse(receipt["claim_audit_passed"])
            self.assertFalse(receipt["paper_contract_revision_eligible"])
            self.assertEqual(receipt["held_new_claim_ids"], ["C-NEW-ONLY"])

    def test_failed_evidence_or_scope_check_blocks_contract_revision(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); handoff = self.handoff(root)
            receipt = build_child_claim_audit(handoff=handoff, audit_packet=self.packet(handoff, fail_claim="C-REOPEN-METHOD", fail_check="scope_within_reopened_contract_pass"))
            self.assertEqual(receipt["status"], BLOCK_STATUS)
            self.assertFalse(receipt["claim_audit_passed"])
            self.assertFalse(receipt["paper_contract_revision_eligible"])
            self.assertEqual(receipt["failed_claim_ids"], ["C-REOPEN-METHOD"])
            self.assertFalse(receipt["claim_update_authorized"])

    def test_audit_requires_exact_candidate_coverage_and_exact_checks(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); handoff = self.handoff(root); packet = self.packet(handoff)
            packet["claim_checks"].pop()
            with self.assertRaisesRegex(RuntimeError, "every candidate claim"):
                build_child_claim_audit(handoff=handoff, audit_packet=packet)
            packet = self.packet(handoff); packet["claim_checks"][0]["checks"].pop("method_principle_boundary_pass")
            with self.assertRaisesRegex(RuntimeError, "required set exactly"):
                build_child_claim_audit(handoff=handoff, audit_packet=packet)

    def test_append_only_public_redaction_and_tamper_detection(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); handoff = self.handoff(root); receipt = build_child_claim_audit(handoff=handoff, audit_packet=self.packet(handoff))
            first = publish_child_claim_audit(root, receipt)
            second = publish_child_claim_audit(root, receipt)
            self.assertEqual(len(first["events"]), 1)
            self.assertEqual(len(second["events"]), 1)
            self.assertEqual(validate_child_claim_audit_ledger(second), [])
            public = public_child_claim_audit(root, handoff["attempt_sha256"])
            self.assertEqual(public["status"], PASS_STATUS)
            self.assertEqual(public["supported_claims"], 2)
            self.assertFalse(public["claim_update_authorized"])
            self.assertFalse(public["paper_preparation_eligible"])
            text = json.dumps(public)
            self.assertNotIn("independent-child-claim-auditor:private-ref", text)
            self.assertNotIn("claim_text", text)
            bad = copy.deepcopy(receipt); bad["paper_preparation_eligible"] = True
            self.assertFalse(validate_child_claim_audit(bad))


if __name__ == "__main__":
    unittest.main()
