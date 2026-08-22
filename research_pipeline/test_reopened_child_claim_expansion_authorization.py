from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from .reopened_child_claim_audit import build_child_claim_audit
from .reopened_child_claim_expansion_authorization import (
    STATUS,
    build_child_claim_expansion_authorization,
    public_child_claim_expansion_authorization,
    publish_child_claim_expansion_authorization,
    validate_child_claim_expansion_authorization,
    validate_claim_expansion_authority_ledger,
)
from .reopened_child_paper_contract import build_child_paper_contract, validate_child_paper_contract
from .test_reopened_child_claim_audit import ReopenedChildClaimAuditTest
from .test_reopened_child_paper_contract import ReopenedChildPaperContractTest
from .test_reopened_scientific_evidence_paper_handoff import ReopenedScientificEvidencePaperHandoffTest


class ReopenedChildClaimExpansionAuthorizationTest(unittest.TestCase):
    def fixture(self, root: Path, *, two_new: bool = False):
        source = ReopenedScientificEvidencePaperHandoffTest(methodName="test_method_pass_creates_child_revision_handoff_but_not_claim_or_preparation_authority")
        spec = source.revision_spec()
        spec["candidate_claims"].append({"claim_id":"C-NEW-ONE","claim_text":"A first new child claim.","evidence_role":"SUPPORTING","claim_relation":"NEW_CHILD_CLAIM"})
        if two_new:
            spec["candidate_claims"].append({"claim_id":"C-NEW-TWO","claim_text":"A second new child claim.","evidence_role":"MECHANISM","claim_relation":"NEW_CHILD_CLAIM"})
        helper = ReopenedChildClaimAuditTest(methodName="test_new_child_claim_is_held_for_human_expansion_authority")
        handoff = helper.handoff(root, spec=spec)
        audit = build_child_claim_audit(handoff=handoff, audit_packet=helper.packet(handoff))
        return handoff, audit

    def authorize(self, audit: dict, ids=None):
        return build_child_claim_expansion_authorization(
            claim_audit=audit,
            approved_new_claim_ids=ids or [audit["held_new_claim_ids"][0]],
            external_authority_ref="human:private-child-claim-expansion",
            authorized_at="2027-04-16T12:00:00+00:00",
            scope="Authorize only the explicitly listed new child claim(s) within the reopened scientific contract and audited evidence bundle.",
        )

    def test_only_audit_held_new_claims_can_be_authorized(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); _,audit=self.fixture(root)
            with self.assertRaisesRegex(RuntimeError,"only audit-held"):
                self.authorize(audit,["C-NOT-HELD"])
            auth=self.authorize(audit)
            self.assertTrue(validate_child_claim_expansion_authorization(auth))
            self.assertEqual(auth["status"],STATUS)
            self.assertEqual(auth["approved_new_claim_ids"],["C-NEW-ONE"])
            self.assertTrue(auth["child_claim_expansion_authorized"])
            self.assertTrue(auth["authorization_applies_only_to_listed_claim_ids"])
            self.assertFalse(auth["future_claim_expansion_authorized"])
            self.assertFalse(auth["parent_claim_update_authorized"])
            self.assertFalse(auth["paper_preparation_authorized"])

    def test_claim_audit_without_held_new_claims_cannot_create_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); helper=ReopenedChildClaimAuditTest(methodName="test_existing_and_boundary_claims_pass_to_contract_revision_not_claim_update");handoff=helper.handoff(root);audit=build_child_claim_audit(handoff=handoff,audit_packet=helper.packet(handoff))
            with self.assertRaisesRegex(RuntimeError,"no held new claims"):
                build_child_claim_expansion_authorization(claim_audit=audit,approved_new_claim_ids=["X"],external_authority_ref="human:x",authorized_at="2027-04-16T12:00:00+00:00",scope="x")

    def test_authorized_new_claim_enters_child_contract_while_unapproved_new_claim_remains_held(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);handoff,audit=self.fixture(root,two_new=True);auth=self.authorize(audit,["C-NEW-ONE"])
            base=ReopenedChildPaperContractTest(methodName="test_held_new_claims_are_excluded_from_child_contract");spec=base.spec(audit);spec["claim_wording"]["C-NEW-ONE"]="The human-authorized new child claim remains bounded to the reopened P0 evidence and child scientific scope."
            contract=build_child_paper_contract(handoff=handoff,claim_audit=audit,revision_spec=spec,claim_expansion_authorization=auth)
            self.assertTrue(validate_child_paper_contract(contract))
            self.assertTrue(contract["new_claim_expansion_authorized"])
            self.assertTrue(contract["human_claim_expansion_authority_confirmed"])
            self.assertEqual(contract["approved_new_claim_ids"],["C-NEW-ONE"])
            self.assertEqual(contract["held_new_claim_ids"],["C-NEW-TWO"])
            ids=[row["claim_id"] for row in contract["supported_claims"]]
            self.assertIn("C-NEW-ONE",ids);self.assertNotIn("C-NEW-TWO",ids)
            self.assertFalse(contract["future_claim_expansion_authorized"])
            self.assertFalse(contract["parent_claim_update_authorized"])

    def test_contract_cannot_include_unauthorized_new_claim_wording(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);handoff,audit=self.fixture(root);base=ReopenedChildPaperContractTest(methodName="test_held_new_claims_are_excluded_from_child_contract");spec=base.spec(audit);spec["claim_wording"]["C-NEW-ONE"]="unauthorized"
            with self.assertRaisesRegex(RuntimeError,"cover exactly"):
                build_child_paper_contract(handoff=handoff,claim_audit=audit,revision_spec=spec)

    def test_append_only_public_redaction_and_tamper(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);_,audit=self.fixture(root);auth=self.authorize(audit);row=publish_child_claim_expansion_authorization(root,auth);row2=publish_child_claim_expansion_authorization(root,auth);self.assertEqual(len(row["events"]),1);self.assertEqual(len(row2["events"]),1);self.assertEqual(validate_claim_expansion_authority_ledger(row2),[]);public=public_child_claim_expansion_authorization(root,audit["attempt_sha256"]);self.assertEqual(public["status"],STATUS);self.assertEqual(public["approved_new_claims"],1);self.assertFalse(public["future_claim_expansion_authorized"]);self.assertFalse(public["parent_claim_update_authorized"]);self.assertNotIn("human:private-child-claim-expansion",json.dumps(public));bad=copy.deepcopy(auth);bad["future_claim_expansion_authorized"]=True;self.assertFalse(validate_child_claim_expansion_authorization(bad))


if __name__=="__main__":unittest.main()
