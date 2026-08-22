from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from .reopened_p0_result_adjudication import build_p0_adjudication, build_p0_result_packet
from .reopened_scientific_evidence_paper_handoff import (
    STATUS,
    build_scientific_evidence_paper_handoff,
    public_scientific_evidence_paper_handoff,
    publish_scientific_evidence_paper_handoff,
    validate_paper_revision_handoff_ledger,
    validate_scientific_evidence_paper_handoff,
)
from .test_reopened_p0_result_adjudication import ReopenedP0ResultAdjudicationTest


class ReopenedScientificEvidencePaperHandoffTest(unittest.TestCase):
    def fixture(self, root: Path, outcome: str = "METHOD-PASS"):
        helper = ReopenedP0ResultAdjudicationTest(methodName="test_method_pass_is_current_realization_only_and_does_not_prove_principle")
        plan = helper.plan(root)
        contract_path = root / "scientific-contracts" / f"{plan['contract_id']}.json"
        contract = json.loads(contract_path.read_text())
        attempt = None
        for path in (root / "paper-submission-attempts").glob("*.json"):
            ledger = json.loads(path.read_text())
            for event in ledger.get("events") or []:
                receipt = event.get("receipt") or {}
                if receipt.get("attempt_sha256") == contract.get("source_attempt_sha256"):
                    attempt = receipt
        if not attempt:
            raise RuntimeError("fixture attempt missing")
        result = build_p0_result_packet(p0_plan=plan, packet=helper.result_input(plan, outcome))
        adjudication = build_p0_adjudication(p0_plan=plan, result_packet=result, packet=helper.adjudication_packet())
        return attempt, contract, result, adjudication

    def revision_spec(self) -> dict:
        return {
            "revision_summary": "Use the fresh confirmatory P0 evidence to revise the child manuscript, then rerun Claim Audit before any claim upgrade or paper preparation.",
            "candidate_claims": [
                {"claim_id": "C-REOPEN-METHOD", "claim_text": "The reopened method produces the preregistered effect on fresh held-out confirmatory units.", "evidence_role": "PRIMARY", "claim_relation": "EXISTING_PARENT_CLAIM"},
                {"claim_id": "C-REOPEN-BOUNDARY", "claim_text": "The observed effect remains scoped to the frozen child scientific contract and same-information comparison.", "evidence_role": "BOUNDARY", "claim_relation": "BOUNDARY_CLARIFICATION"},
            ],
            "parent_submitted_bytes_will_be_modified": False,
            "automatic_claim_upgrade_requested": False,
            "outcome_driven_claim_selection_used": False,
        }

    def test_method_pass_creates_child_revision_handoff_but_not_claim_or_preparation_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); attempt, contract, result, adjudication = self.fixture(root)
            receipt = build_scientific_evidence_paper_handoff(attempt_plan=attempt, reopened_contract=contract, p0_result_packet=result, p0_adjudication=adjudication, revision_spec=self.revision_spec())
            self.assertTrue(validate_scientific_evidence_paper_handoff(receipt))
            self.assertEqual(receipt["status"], STATUS)
            self.assertTrue(receipt["child_manuscript_revision_eligible"])
            self.assertTrue(receipt["child_claim_audit_required"])
            self.assertFalse(receipt["child_claim_audit_passed"])
            self.assertFalse(receipt["claim_upgrade_authorized"])
            self.assertFalse(receipt["claim_expansion_authorized"])
            self.assertFalse(receipt["paper_preparation_eligible"])
            self.assertFalse(receipt["submission_eligible"])
            self.assertTrue(receipt["parent_submitted_bytes_immutable"])
            self.assertTrue(receipt["parent_paper_claim_status_unchanged"])
            self.assertEqual(receipt["attempt_sha256"], contract["source_attempt_sha256"])
            self.assertEqual(receipt["evidence_bundle"]["method_verdict"], "METHOD-PASS")
            self.assertFalse(receipt["evidence_bundle"]["principle_proven"])

    def test_method_fail_or_typed_stop_cannot_be_promoted_as_positive_child_paper_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); attempt, contract, result, adjudication = self.fixture(root, "METHOD-FAIL")
            with self.assertRaisesRegex(RuntimeError, "P0 METHOD-PASS"):
                build_scientific_evidence_paper_handoff(attempt_plan=attempt, reopened_contract=contract, p0_result_packet=result, p0_adjudication=adjudication, revision_spec=self.revision_spec())

    def test_attempt_contract_and_result_lineage_are_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); attempt, contract, result, adjudication = self.fixture(root)
            bad_contract = copy.deepcopy(contract); bad_contract["source_attempt_sha256"] = "0" * 64
            with self.assertRaisesRegex(RuntimeError, "valid reopened scientific contract"):
                build_scientific_evidence_paper_handoff(attempt_plan=attempt, reopened_contract=bad_contract, p0_result_packet=result, p0_adjudication=adjudication, revision_spec=self.revision_spec())
            bad_result = copy.deepcopy(result); bad_result["contract_id"] = "wrong-contract"
            with self.assertRaisesRegex(RuntimeError, "valid confirmatory P0 result"):
                build_scientific_evidence_paper_handoff(attempt_plan=attempt, reopened_contract=contract, p0_result_packet=bad_result, p0_adjudication=adjudication, revision_spec=self.revision_spec())

    def test_revision_spec_forbids_parent_mutation_automatic_upgrade_and_outcome_selection(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); attempt, contract, result, adjudication = self.fixture(root)
            for key, regex in (
                ("parent_submitted_bytes_will_be_modified", "parent submitted bytes"),
                ("automatic_claim_upgrade_requested", "automatic claim upgrade"),
                ("outcome_driven_claim_selection_used", "outcome-driven claim selection"),
            ):
                spec = self.revision_spec(); spec[key] = True
                with self.assertRaisesRegex(RuntimeError, regex):
                    build_scientific_evidence_paper_handoff(attempt_plan=attempt, reopened_contract=contract, p0_result_packet=result, p0_adjudication=adjudication, revision_spec=spec)

    def test_candidate_claims_are_inputs_to_claim_audit_not_authorized_claims(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); attempt, contract, result, adjudication = self.fixture(root)
            spec = self.revision_spec(); spec["candidate_claims"] = []
            with self.assertRaisesRegex(RuntimeError, "at least one candidate claim"):
                build_scientific_evidence_paper_handoff(attempt_plan=attempt, reopened_contract=contract, p0_result_packet=result, p0_adjudication=adjudication, revision_spec=spec)
            spec = self.revision_spec(); spec["candidate_claims"][1]["claim_id"] = spec["candidate_claims"][0]["claim_id"]
            with self.assertRaisesRegex(RuntimeError, "unique"):
                build_scientific_evidence_paper_handoff(attempt_plan=attempt, reopened_contract=contract, p0_result_packet=result, p0_adjudication=adjudication, revision_spec=spec)

    def test_append_only_idempotence_public_summary_and_tamper_detection(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); attempt, contract, result, adjudication = self.fixture(root)
            receipt = build_scientific_evidence_paper_handoff(attempt_plan=attempt, reopened_contract=contract, p0_result_packet=result, p0_adjudication=adjudication, revision_spec=self.revision_spec())
            first = publish_scientific_evidence_paper_handoff(root, receipt, recorded_at="2027-04-14T12:00:00+00:00")
            second = publish_scientific_evidence_paper_handoff(root, receipt, recorded_at="2027-04-14T12:00:00+00:00")
            self.assertEqual(len(first["events"]), 1)
            self.assertEqual(len(second["events"]), 1)
            self.assertEqual(validate_paper_revision_handoff_ledger(second), [])
            public = public_scientific_evidence_paper_handoff(root, attempt["attempt_sha256"])
            self.assertEqual(public["status"], STATUS)
            self.assertEqual(public["candidate_claims"], 2)
            self.assertTrue(public["child_manuscript_revision_eligible"])
            self.assertTrue(public["child_claim_audit_required"])
            self.assertFalse(public["claim_upgrade_authorized"])
            self.assertFalse(public["paper_preparation_eligible"])
            self.assertFalse(public["submission_eligible"])
            bad = copy.deepcopy(receipt); bad["claim_upgrade_authorized"] = True
            self.assertFalse(validate_scientific_evidence_paper_handoff(bad))
            raw = json.dumps(public)
            self.assertNotIn("artifact_manifest", raw)
            self.assertNotIn("primary_metric_value", raw)


if __name__ == "__main__":
    unittest.main()
