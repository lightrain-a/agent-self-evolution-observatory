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
    PROPOSAL_STATUS,
    build_scientific_reopen_authorization,
    build_scientific_reopen_proposal,
    public_scientific_reopen_summary,
    publish_scientific_reopen_receipt,
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
            self.assertEqual(len(row["events"]), 2)
            self.assertEqual(validate_scientific_reopen_ledger(row), [])
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
