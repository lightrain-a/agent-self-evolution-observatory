from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from .paper_preparation_protocol import PAPER_PREPARATION_PROTOCOL_VERSION
from .scientific_reopen_protocol import (
    AUTHORIZATION_SCOPE,
    AUTHORIZED_STATUS,
    HANDOFF_DESTINATION,
    HANDOFF_STATUS,
    PROPOSAL_STATUS,
    build_research_os_scientific_reopen_handoff,
    build_scientific_reopen_authorization,
    build_scientific_reopen_proposal,
    public_scientific_reopen_summary,
    publish_scientific_reopen_receipt,
    validate_research_os_scientific_reopen_handoff,
    validate_scientific_reopen_authorization,
    validate_scientific_reopen_ledger,
    validate_scientific_reopen_proposal,
)
from .submission_attempt_lineage import build_attempt_plan, publish_attempt_plan
from .submission_attempt_workflow import build_attempt_preparation
from .test_paper_preparation_protocol import passing_packet
from .test_submission_attempt_lineage import SubmissionAttemptLineageTest


class ScientificReopenProtocolTest(unittest.TestCase):
    def parent(self, root: Path) -> dict:
        helper = SubmissionAttemptLineageTest(methodName="test_scientific_change_requires_explicit_reopen_and_never_grants_authority")
        ledger, _, _ = helper.learned_fixture(root, "REJECT")
        return ledger

    def scientific_plan(self, root: Path) -> dict:
        parent = self.parent(root)
        plan = build_attempt_plan(
            paper_ledger=parent,
            target_venue="ICML 2027",
            attempt_type="RESUBMISSION",
            revision_categories=("EXPERIMENT", "SCIENTIFIC_EVIDENCE"),
            scientific_contract_unchanged=True,
            new_experiment_requested=True,
            new_scientific_evidence_requested=True,
        )
        publish_attempt_plan(plan, root)
        return plan

    def paper_side_plan(self, root: Path) -> dict:
        parent = self.parent(root)
        return build_attempt_plan(
            paper_ledger=parent,
            target_venue="ICML 2027",
            attempt_type="RESUBMISSION",
            revision_categories=("WRITING", "PAPER_POSITIONING"),
            scientific_contract_unchanged=True,
        )

    def test_paper_side_attempt_cannot_create_scientific_reopen_proposal(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaisesRegex(RuntimeError, "paper-side-only"):
                build_scientific_reopen_proposal(self.paper_side_plan(root))

    def test_scientific_change_creates_proposal_without_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            plan = self.scientific_plan(root)
            proposal = build_scientific_reopen_proposal(plan)
            self.assertTrue(validate_scientific_reopen_proposal(proposal))
            self.assertEqual(proposal["status"], PROPOSAL_STATUS)
            self.assertTrue(proposal["new_scientific_contract_required"])
            self.assertTrue(proposal["existing_scientific_contract_immutable"])
            self.assertFalse(proposal["new_experiment_authorized"])
            self.assertFalse(proposal["gpu_authority"])
            row = publish_scientific_reopen_receipt(root, proposal)
            row2 = publish_scientific_reopen_receipt(root, proposal)
            self.assertEqual(len(row["events"]), 1)
            self.assertEqual(len(row2["events"]), 1)
            self.assertEqual(validate_scientific_reopen_ledger(row2), [])

    def test_external_authorization_requires_published_proposal_and_remains_zero_execution_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            plan = self.scientific_plan(root)
            proposal = build_scientific_reopen_proposal(plan)
            auth = build_scientific_reopen_authorization(
                proposal=proposal,
                external_scientific_authority_ref="pi:explicit-scientific-reopen-approval",
                authorized_at="2027-04-01T12:00:00+00:00",
            )
            self.assertTrue(validate_scientific_reopen_authorization(auth))
            self.assertEqual(auth["authorization_scope"], AUTHORIZATION_SCOPE)
            with self.assertRaisesRegex(RuntimeError, "previously published proposal"):
                publish_scientific_reopen_receipt(root, auth)
            publish_scientific_reopen_receipt(root, proposal)
            row = publish_scientific_reopen_receipt(root, auth)
            row2 = publish_scientific_reopen_receipt(root, auth)
            self.assertEqual(len(row["events"]), 2)
            self.assertEqual(len(row2["events"]), 2)
            self.assertEqual(validate_scientific_reopen_ledger(row2), [])
            self.assertEqual(auth["status"], AUTHORIZED_STATUS)
            self.assertTrue(auth["external_scientific_authority_confirmed"])
            self.assertTrue(auth["new_scientific_contract_required"])
            self.assertFalse(auth["automatic_contract_creation_authorized"])
            self.assertFalse(auth["new_experiment_authorized"])
            self.assertFalse(auth["gpu_execution_authorized"])
            self.assertFalse(auth["claim_expansion_authorized"])
            self.assertFalse(auth["scientific_authority"])
            self.assertFalse(auth["experiment_authority"])
            self.assertFalse(auth["gpu_authority"])

    def test_authorization_does_not_unlock_old_attempt_preparation(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            plan = self.scientific_plan(root)
            proposal = build_scientific_reopen_proposal(plan)
            publish_scientific_reopen_receipt(root, proposal)
            auth = build_scientific_reopen_authorization(
                proposal=proposal,
                external_scientific_authority_ref="pi:approval",
                authorized_at="2027-04-01T12:00:00+00:00",
            )
            publish_scientific_reopen_receipt(root, auth)
            with self.assertRaisesRegex(RuntimeError, "explicit scientific reopen"):
                build_attempt_preparation(attempt_plan=plan, preparation_packet=passing_packet())

    def test_authorization_requires_explicit_external_reference_and_timestamp(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            proposal = build_scientific_reopen_proposal(self.scientific_plan(root))
            with self.assertRaisesRegex(RuntimeError, "authority reference"):
                build_scientific_reopen_authorization(proposal=proposal, external_scientific_authority_ref="", authorized_at="2027-04-01T12:00:00+00:00")
            with self.assertRaisesRegex(RuntimeError, "timestamp"):
                build_scientific_reopen_authorization(proposal=proposal, external_scientific_authority_ref="pi:approval", authorized_at="")

    def test_tampering_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            proposal = build_scientific_reopen_proposal(self.scientific_plan(root))
            bad_proposal = copy.deepcopy(proposal)
            bad_proposal["new_experiment_authorized"] = True
            self.assertFalse(validate_scientific_reopen_proposal(bad_proposal))
            auth = build_scientific_reopen_authorization(proposal=proposal, external_scientific_authority_ref="pi:approval", authorized_at="2027-04-01T12:00:00+00:00")
            bad_auth = copy.deepcopy(auth)
            bad_auth["authorization_scope"] = "RUN_EXPERIMENT"
            self.assertFalse(validate_scientific_reopen_authorization(bad_auth))

    def test_research_os_handoff_requires_authorization_and_grants_no_execution_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            plan = self.scientific_plan(root)
            paper = json.loads((root / "paper-acceptance" / f"{plan['paper_id']}.json").read_text())
            proposal = build_scientific_reopen_proposal(plan)
            auth = build_scientific_reopen_authorization(
                proposal=proposal,
                external_scientific_authority_ref="pi:approval",
                authorized_at="2027-04-01T12:00:00+00:00",
            )
            handoff = build_research_os_scientific_reopen_handoff(
                paper_ledger=paper,
                attempt_plan=plan,
                proposal=proposal,
                authorization=auth,
            )
            self.assertTrue(validate_research_os_scientific_reopen_handoff(handoff))
            self.assertEqual(handoff["status"], HANDOFF_STATUS)
            self.assertEqual(handoff["destination_gate"], HANDOFF_DESTINATION)
            self.assertTrue(handoff["new_contract_creation_eligible"])
            self.assertTrue(handoff["new_scientific_contract_required"])
            self.assertTrue(handoff["existing_scientific_contract_immutable"])
            self.assertTrue(handoff["reviewer_feedback_is_diagnostic_context_not_scientific_evidence"])
            self.assertFalse(handoff["automatic_contract_creation_authorized"])
            self.assertFalse(handoff["problem_gate_authorized"])
            self.assertFalse(handoff["method_design_authorized"])
            self.assertFalse(handoff["experiment_blueprint_authorized"])
            self.assertFalse(handoff["new_experiment_authorized"])
            self.assertFalse(handoff["p0_authorized"])
            self.assertFalse(handoff["gpu_execution_authorized"])
            self.assertFalse(handoff["scientific_authority"])
            self.assertFalse(handoff["experiment_authority"])
            self.assertFalse(handoff["gpu_authority"])
            self.assertEqual(handoff["requested_scientific_deltas"]["scientific_revision_categories"], ["EXPERIMENT", "SCIENTIFIC_EVIDENCE"])
            self.assertTrue(handoff["requested_scientific_deltas"]["new_experiment_requested"])
            self.assertTrue(handoff["requested_scientific_deltas"]["new_scientific_evidence_requested"])
            with self.assertRaisesRegex(RuntimeError, "previously published scientific authorization"):
                publish_scientific_reopen_receipt(root, handoff)
            publish_scientific_reopen_receipt(root, proposal)
            publish_scientific_reopen_receipt(root, auth)
            row = publish_scientific_reopen_receipt(root, handoff)
            row2 = publish_scientific_reopen_receipt(root, handoff)
            self.assertEqual(len(row["events"]), 3)
            self.assertEqual(len(row2["events"]), 3)
            self.assertEqual(validate_scientific_reopen_ledger(row2), [])
            self.assertFalse((root / "experiment-authority").exists())

    def test_research_os_handoff_preserves_parent_contract_and_claim_state(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            plan = self.scientific_plan(root)
            path = root / "paper-acceptance" / f"{plan['paper_id']}.json"
            paper_before = json.loads(path.read_text())
            proposal = build_scientific_reopen_proposal(plan)
            publish_scientific_reopen_receipt(root, proposal)
            auth = build_scientific_reopen_authorization(proposal=proposal, external_scientific_authority_ref="pi:approval", authorized_at="2027-04-01T12:00:00+00:00")
            publish_scientific_reopen_receipt(root, auth)
            handoff = build_research_os_scientific_reopen_handoff(paper_ledger=paper_before, attempt_plan=plan, proposal=proposal, authorization=auth)
            publish_scientific_reopen_receipt(root, handoff)
            paper_after = json.loads(path.read_text())
            self.assertEqual(paper_after["current_state"], "LEARN")
            self.assertEqual(paper_after["contract_sha256"], paper_before["contract_sha256"])
            self.assertEqual(paper_after["contract"], paper_before["contract"])
            self.assertEqual(handoff["source_contract_sha256"], paper_before["contract_sha256"])

    def test_research_os_handoff_tamper_or_lineage_mismatch_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            plan = self.scientific_plan(root)
            paper = json.loads((root / "paper-acceptance" / f"{plan['paper_id']}.json").read_text())
            proposal = build_scientific_reopen_proposal(plan)
            auth = build_scientific_reopen_authorization(proposal=proposal, external_scientific_authority_ref="pi:approval", authorized_at="2027-04-01T12:00:00+00:00")
            handoff = build_research_os_scientific_reopen_handoff(paper_ledger=paper, attempt_plan=plan, proposal=proposal, authorization=auth)
            bad = copy.deepcopy(handoff)
            bad["experiment_blueprint_authorized"] = True
            self.assertFalse(validate_research_os_scientific_reopen_handoff(bad))
            bad_auth = copy.deepcopy(auth)
            bad_auth["attempt_sha256"] = "0" * 64
            with self.assertRaisesRegex(RuntimeError, "authorization"):
                build_research_os_scientific_reopen_handoff(paper_ledger=paper, attempt_plan=plan, proposal=proposal, authorization=bad_auth)

    def test_public_summary_exposes_handoff_seed_without_private_authority_reference(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            plan = self.scientific_plan(root)
            paper = json.loads((root / "paper-acceptance" / f"{plan['paper_id']}.json").read_text())
            proposal = build_scientific_reopen_proposal(plan)
            row = publish_scientific_reopen_receipt(root, proposal)
            auth = build_scientific_reopen_authorization(
                proposal=proposal,
                external_scientific_authority_ref="pi:private-authority-reference",
                authorized_at="2027-04-01T12:00:00+00:00",
            )
            row = publish_scientific_reopen_receipt(root, auth)
            handoff = build_research_os_scientific_reopen_handoff(paper_ledger=paper, attempt_plan=plan, proposal=proposal, authorization=auth)
            row = publish_scientific_reopen_receipt(root, handoff)
            public = public_scientific_reopen_summary(row, plan["attempt_sha256"])
            self.assertEqual(public["status"], HANDOFF_STATUS)
            self.assertEqual(public["destination_gate"], HANDOFF_DESTINATION)
            self.assertTrue(public["new_contract_creation_eligible"])
            self.assertTrue(public["new_contract_seed_id"].startswith("scientific-reopen-"))
            self.assertTrue(public["research_os_handoff_sha256"])
            text = json.dumps(public, sort_keys=True)
            self.assertNotIn("pi:private-authority-reference", text)
            self.assertNotIn("external_scientific_authority_ref\"", text)

    def test_public_summary_redacts_external_authority_reference(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            plan = self.scientific_plan(root)
            proposal = build_scientific_reopen_proposal(plan)
            row = publish_scientific_reopen_receipt(root, proposal)
            auth = build_scientific_reopen_authorization(
                proposal=proposal,
                external_scientific_authority_ref="pi:private-authority-reference",
                authorized_at="2027-04-01T12:00:00+00:00",
            )
            row = publish_scientific_reopen_receipt(root, auth)
            public = public_scientific_reopen_summary(row, plan["attempt_sha256"])
            self.assertEqual(public["status"], AUTHORIZED_STATUS)
            self.assertTrue(public["external_scientific_authority_confirmed"])
            self.assertTrue(public["new_scientific_contract_required"])
            self.assertFalse(public["new_experiment_authorized"])
            self.assertFalse(public["gpu_execution_authorized"])
            text = json.dumps(public, sort_keys=True)
            self.assertNotIn("pi:private-authority-reference", text)
            self.assertNotIn("external_scientific_authority_ref\"", text)


if __name__ == "__main__":
    unittest.main()
