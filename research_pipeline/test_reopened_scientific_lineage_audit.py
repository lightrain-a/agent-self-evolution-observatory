from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .reopened_child_claim_audit import build_child_claim_audit, publish_child_claim_audit
from .reopened_child_paper_contract import build_child_paper_contract, publish_child_paper_contract
from .reopened_p0_principle_handoff import build_p0_principle_handoff, publish_p0_principle_handoff
from .reopened_p0_principle_memory_authorization import (
    build_principle_memory_authorization,
    build_principle_memory_handoff,
    publish_principle_memory_receipt,
)
from .reopened_p0_result_adjudication import build_p0_adjudication, build_p0_result_packet, publish_p0_result_receipt
from .reopened_principle_memory_closure import build_principle_scientific_closure, publish_principle_scientific_closure
from .reopened_scientific_evidence_paper_handoff import build_scientific_evidence_paper_handoff, publish_scientific_evidence_paper_handoff
from .reopened_scientific_lineage_audit import audit_reopened_scientific_attempt, audit_reopened_scientific_portfolio
from .test_reopened_child_claim_audit import ReopenedChildClaimAuditTest
from .test_reopened_child_paper_contract import ReopenedChildPaperContractTest
from .test_reopened_p0_principle_handoff import ReopenedP0PrincipleHandoffTest
from .test_reopened_p0_principle_memory_authorization import ReopenedP0PrincipleMemoryAuthorizationTest
from .test_reopened_p0_result_adjudication import ReopenedP0ResultAdjudicationTest
from .test_reopened_scientific_evidence_paper_handoff import ReopenedScientificEvidencePaperHandoffTest


class ReopenedScientificLineageAuditTest(unittest.TestCase):
    def paper_branch(self, root: Path):
        helper = ReopenedScientificEvidencePaperHandoffTest(methodName="test_method_pass_creates_child_revision_handoff_but_not_claim_or_preparation_authority")
        attempt, contract, result, adjudication = helper.fixture(root)
        publish_p0_result_receipt(root, result, recorded_at="2027-04-10T11:00:00+00:00")
        publish_p0_result_receipt(root, adjudication, recorded_at="2027-04-10T12:00:00+00:00")
        handoff = build_scientific_evidence_paper_handoff(
            attempt_plan=attempt,
            reopened_contract=contract,
            p0_result_packet=result,
            p0_adjudication=adjudication,
            revision_spec=helper.revision_spec(),
        )
        publish_scientific_evidence_paper_handoff(root, handoff, recorded_at="2027-04-14T12:00:00+00:00")
        audit_helper = ReopenedChildClaimAuditTest(methodName="test_existing_and_boundary_claims_pass_to_contract_revision_not_claim_update")
        claim_audit = build_child_claim_audit(handoff=handoff, audit_packet=audit_helper.packet(handoff))
        publish_child_claim_audit(root, claim_audit)
        contract_helper = ReopenedChildPaperContractTest(methodName="test_contract_freezes_supported_claim_delta_without_parent_update_or_preparation_authority")
        child_contract = build_child_paper_contract(handoff=handoff, claim_audit=claim_audit, revision_spec=contract_helper.spec(claim_audit))
        publish_child_paper_contract(root, child_contract)
        return attempt, contract, result, adjudication, handoff, claim_audit, child_contract

    def principle_branch(self, root: Path):
        result_helper = ReopenedP0ResultAdjudicationTest(methodName="test_method_fail_is_current_realization_only_and_cannot_falsify_principle")
        plan = result_helper.plan(root)
        result = build_p0_result_packet(p0_plan=plan, packet=result_helper.result_input(plan, "METHOD-FAIL"))
        adjudication = build_p0_adjudication(p0_plan=plan, result_packet=result, packet=result_helper.adjudication_packet())
        publish_p0_result_receipt(root, result, recorded_at="2027-04-10T11:00:00+00:00")
        publish_p0_result_receipt(root, adjudication, recorded_at="2027-04-10T12:00:00+00:00")
        contract = json.loads((root / "scientific-contracts" / f"{plan['contract_id']}.json").read_text())
        attempt_sha = contract["source_attempt_sha256"]
        principle_helper = ReopenedP0PrincipleHandoffTest(methodName="test_positive_counter_explanation_only_creates_human_review_dead_end_candidate")
        ph = build_p0_principle_handoff(
            p0_adjudication=adjudication,
            principle_certificate=principle_helper.principle_certificate(),
            principle_evidence=principle_helper.true_negative_evidence(with_counter=True),
        )
        publish_p0_principle_handoff(root, ph, recorded_at="2027-04-11T12:00:00+00:00")
        memory_helper = ReopenedP0PrincipleMemoryAuthorizationTest(methodName="test_memory_handoff_is_scoped_core_principle_closure_but_not_automatic_write")
        auth = build_principle_memory_authorization(principle_handoff=ph, external_authority_ref="pi:private-memory-authority", authorized_at="2027-04-12T12:00:00+00:00")
        publish_principle_memory_receipt(root, auth, recorded_at="2027-04-12T12:00:00+00:00")
        memory = build_principle_memory_handoff(principle_handoff=ph, authorization=auth, memory_spec=memory_helper.memory_spec(ph))
        publish_principle_memory_receipt(root, memory, recorded_at="2027-04-12T13:00:00+00:00")
        closure = build_principle_scientific_closure(memory_handoff=memory, persisted_at="2027-04-13T12:00:00+00:00")
        publish_principle_scientific_closure(root, closure)
        return attempt_sha, ph, auth, memory, closure

    def test_complete_positive_paper_return_branch_reconciles(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); attempt, _, _, _, _, audit, child = self.paper_branch(root)
            state = audit_reopened_scientific_attempt(root, attempt["attempt_sha256"])
            self.assertEqual(state["status"], "REOPENED_SCIENTIFIC_LINEAGE_RECONCILED")
            self.assertEqual(state["errors"], [])
            self.assertEqual(state["paper_branch"]["child_claim_audit_sha256"], audit["child_claim_audit_sha256"])
            self.assertEqual(state["paper_branch"]["child_paper_contract_sha256"], child["child_paper_contract_sha256"])
            self.assertFalse(state["parent_claim_update_authorized"])
            self.assertFalse(state["submission_authority"])

    def test_method_fail_principle_memory_branch_reconciles_without_positive_paper_handoff(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); attempt_sha, _, _, memory, closure = self.principle_branch(root)
            state = audit_reopened_scientific_attempt(root, attempt_sha)
            self.assertEqual(state["status"], "REOPENED_SCIENTIFIC_LINEAGE_RECONCILED")
            self.assertEqual(state["errors"], [])
            self.assertEqual(state["paper_branch"]["status"], "SCIENTIFIC_EVIDENCE_PAPER_HANDOFF_REQUIRED")
            self.assertEqual(state["principle_branch"]["principle_memory_handoff_sha256"], memory["principle_memory_handoff_sha256"])
            self.assertEqual(state["principle_branch"]["principle_closure_sha256"], closure["principle_closure_sha256"])
            self.assertFalse(state["automatic_principle_update_authorized"])
            self.assertFalse(state["automatic_memory_write_authorized"])

    def test_orphan_child_contract_is_invalid_not_a_next_required_state(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); attempt, _, _, _, _, _, _ = self.paper_branch(root)
            (root / "paper-scientific-revision-handoffs" / f"{attempt['attempt_sha256']}.json").unlink()
            state = audit_reopened_scientific_attempt(root, attempt["attempt_sha256"])
            self.assertEqual(state["status"], "REOPENED_SCIENTIFIC_LINEAGE_INVALID")
            self.assertIn("child-paper-contract-without-paper-handoff", state["errors"])
            self.assertIn("child-claim-audit-without-paper-handoff", state["errors"])

    def test_tampered_child_contract_or_handoff_is_detected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); attempt, _, _, _, _, _, _ = self.paper_branch(root)
            path = root / "paper-scientific-child-contracts" / f"{attempt['attempt_sha256']}.json"
            row = json.loads(path.read_text()); row["child_claim_audit_sha256"] = "0" * 64; path.write_text(json.dumps(row))
            state = audit_reopened_scientific_attempt(root, attempt["attempt_sha256"])
            self.assertIn("child-paper-contract-invalid", state["errors"])

    def test_corrupted_principle_closure_file_is_invalid_not_silently_missing(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); attempt_sha, ph, _, _, _ = self.principle_branch(root)
            path = root / "research-memory-principle-closures" / f"{ph['principle_id']}.json"
            row = json.loads(path.read_text()); row["authority"]["scientific"] = True; path.write_text(json.dumps(row))
            state = audit_reopened_scientific_attempt(root, attempt_sha)
            self.assertEqual(state["status"], "REOPENED_SCIENTIFIC_LINEAGE_INVALID")
            self.assertIn("principle-closure:principle-closure-ledger-authority-leak", state["errors"])

    def test_portfolio_summary_counts_only_scientific_reopen_attempts_and_redacts_private_refs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); attempt, *_ = self.paper_branch(root)
            state = audit_reopened_scientific_portfolio(root)
            self.assertGreaterEqual(state["summary"]["scientific_reopen_attempts"], 1)
            self.assertEqual(state["summary"]["invalid"], 0)
            raw = json.dumps(state)
            for private in ("independent-p0-adjudicator:private-ref", "pi:private-memory-authority"):
                self.assertNotIn(private, raw)
            self.assertFalse(state["authority"]["scientific"])


if __name__ == "__main__":
    unittest.main()
