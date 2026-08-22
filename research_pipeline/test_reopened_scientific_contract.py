from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from .reopened_scientific_contract import (
    CONTRACT_STATUS,
    build_reopened_scientific_contract,
    evaluate_new_contract_spec,
    find_contract_by_handoff,
    public_reopened_contract_summary,
    publish_reopened_scientific_contract,
    required_delta_keys,
    validate_reopened_scientific_contract,
)
from .scientific_reopen_protocol import (
    build_research_os_scientific_reopen_handoff,
    build_scientific_reopen_authorization,
    build_scientific_reopen_proposal,
)
from .test_scientific_reopen_protocol import ScientificReopenProtocolTest


class ReopenedScientificContractTest(unittest.TestCase):
    def handoff(self, root: Path):
        helper = ScientificReopenProtocolTest(methodName="test_research_os_handoff_requires_authorization_and_grants_no_execution_authority")
        plan = helper.scientific_plan(root)
        paper = json.loads((root / "paper-acceptance" / f"{plan['paper_id']}.json").read_text())
        proposal = build_scientific_reopen_proposal(plan)
        auth = build_scientific_reopen_authorization(
            proposal=proposal,
            external_scientific_authority_ref="pi:private-contract-authority",
            authorized_at="2027-04-01T12:00:00+00:00",
        )
        handoff = build_research_os_scientific_reopen_handoff(
            paper_ledger=paper,
            attempt_plan=plan,
            proposal=proposal,
            authorization=auth,
        )
        return paper, plan, handoff

    def spec(self, handoff: dict) -> dict:
        mapping = {key: f"This child contract explicitly addresses {key}." for key in required_delta_keys(handoff)}
        return {
            "scientific_question": "Does the reviewer-requested intervention expose a reproducible effect under a newly frozen contract?",
            "hypothesis": "The requested intervention produces a measurable effect that survives the newly defined control.",
            "falsifiable_prediction": "Under the frozen control, the intervention effect exceeds the preregistered zero-effect boundary on held-out units.",
            "cheapest_falsifier": "Run the smallest preregistered matched-control pilot that can reject the claimed effect direction.",
            "scope": "Only the reviewer-triggered intervention and the frozen matched-control regime described in this child contract.",
            "stop_condition": "Stop the child scientific object if the preregistered falsifier rules out the effect within the frozen scope.",
            "difference_from_parent": "Adds a reviewer-triggered intervention/evidence question without changing the parent paper contract or its adjudicated claim states.",
            "limitations_boundary": "No inference outside the frozen intervention/control scope; support failures remain non-scientific negatives.",
            "evidence_plan": [
                "Freeze the new intervention and matched-control construction before outcomes.",
                "Run the cheapest falsifier before any broader replication.",
            ],
            "requested_delta_mapping": mapping,
            "reviewer_feedback_used_as": "DIAGNOSTIC_CONTEXT_ONLY",
            "existing_evidence_used_as": "CONTEXT_PENDING_NEW_CONTRACT_READJUDICATION",
            "new_evidence_required_before_claim_upgrade": True,
            "outcome_driven_selection_forbidden": True,
            "support_failure_not_scientific_negative": True,
            "inherit_parent_claim_status": False,
        }

    def test_incomplete_spec_is_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, _, handoff = self.handoff(root)
            audit = evaluate_new_contract_spec(handoff, {})
            self.assertFalse(audit["pass"])
            self.assertIn("new-contract-spec-missing:scientific_question", audit["blockers"])
            with self.assertRaisesRegex(RuntimeError, "invalid reopened scientific contract spec"):
                build_reopened_scientific_contract(handoff=handoff, spec={})

    def test_delta_mapping_must_match_requested_scientific_deltas_exactly(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, _, handoff = self.handoff(root)
            spec = self.spec(handoff)
            required = required_delta_keys(handoff)
            self.assertEqual(required, ["EXPERIMENT", "NEW_EXPERIMENT", "NEW_SCIENTIFIC_EVIDENCE", "SCIENTIFIC_EVIDENCE"])
            missing = copy.deepcopy(spec)
            missing["requested_delta_mapping"].pop(required[0])
            self.assertIn("new-contract-spec-delta-mapping-must-match-requested-deltas-exactly", evaluate_new_contract_spec(handoff, missing)["blockers"])
            extra = copy.deepcopy(spec)
            extra["requested_delta_mapping"]["UNREQUESTED_SCOPE_EXPANSION"] = "should fail"
            self.assertIn("new-contract-spec-delta-mapping-must-match-requested-deltas-exactly", evaluate_new_contract_spec(handoff, extra)["blockers"])

    def test_valid_contract_is_content_addressed_immutable_and_problem_gate_required(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paper, _, handoff = self.handoff(root)
            contract = build_reopened_scientific_contract(handoff=handoff, spec=self.spec(handoff))
            self.assertTrue(validate_reopened_scientific_contract(contract))
            self.assertEqual(contract["status"], CONTRACT_STATUS)
            self.assertEqual(contract["scientific_stage"], "problem")
            self.assertTrue(contract["problem_gate_required"])
            self.assertFalse(contract["problem_gate_authorized"])
            self.assertFalse(contract["paper_design_authorized"])
            self.assertFalse(contract["method_design_authorized"])
            self.assertFalse(contract["experiment_authorized"])
            self.assertFalse(contract["p0_authorized"])
            self.assertFalse(contract["gpu_execution_authorized"])
            self.assertFalse(contract["inherit_parent_claim_status"])
            self.assertEqual(contract["parent_contract_sha256"], paper["contract_sha256"])
            first = publish_reopened_scientific_contract(root, contract)
            second = publish_reopened_scientific_contract(root, contract)
            self.assertEqual(first["contract_sha256"], second["contract_sha256"])
            self.assertEqual(len(list((root / "scientific-contracts").glob("reopen-contract-*.json"))), 1)
            self.assertFalse((root / "experiment-authority").exists())

    def test_contract_file_contains_no_private_scientific_authority_reference(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, _, handoff = self.handoff(root)
            contract = build_reopened_scientific_contract(handoff=handoff, spec=self.spec(handoff))
            publish_reopened_scientific_contract(root, contract)
            text = (root / "scientific-contracts" / f"{contract['contract_id']}.json").read_text()
            self.assertNotIn("pi:private-contract-authority", text)
            self.assertNotIn("external_scientific_authority_ref", text)

    def test_contract_tamper_or_authority_leak_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, _, handoff = self.handoff(root)
            contract = build_reopened_scientific_contract(handoff=handoff, spec=self.spec(handoff))
            bad = copy.deepcopy(contract)
            bad["experiment_authorized"] = True
            self.assertFalse(validate_reopened_scientific_contract(bad))
            bad2 = copy.deepcopy(contract)
            bad2["scientific_question"] = "Tampered question"
            self.assertFalse(validate_reopened_scientific_contract(bad2))

    def test_reviewer_feedback_cannot_be_promoted_to_scientific_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, _, handoff = self.handoff(root)
            spec = self.spec(handoff)
            spec["reviewer_feedback_used_as"] = "SCIENTIFIC_EVIDENCE"
            audit = evaluate_new_contract_spec(handoff, spec)
            self.assertFalse(audit["pass"])
            self.assertIn("reviewer-feedback-must-remain-diagnostic-context", audit["blockers"])

    def test_find_by_handoff_and_public_summary_preserve_zero_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, _, handoff = self.handoff(root)
            contract = build_reopened_scientific_contract(handoff=handoff, spec=self.spec(handoff))
            publish_reopened_scientific_contract(root, contract)
            found = find_contract_by_handoff(root, handoff["research_os_handoff_sha256"])
            self.assertEqual(found["contract_id"], contract["contract_id"])
            public = public_reopened_contract_summary(found)
            self.assertEqual(public["status"], CONTRACT_STATUS)
            self.assertTrue(public["problem_gate_required"])
            self.assertFalse(public["problem_gate_authorized"])
            self.assertFalse(public["method_design_authorized"])
            self.assertFalse(public["experiment_authorized"])
            self.assertFalse(public["p0_authorized"])
            self.assertFalse(public["gpu_execution_authorized"])

    def test_existing_evidence_cannot_be_inherited_as_authoritative(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, _, handoff = self.handoff(root)
            spec = self.spec(handoff)
            spec["existing_evidence_used_as"] = "SUPPORTED"
            audit = evaluate_new_contract_spec(handoff, spec)
            self.assertFalse(audit["pass"])
            self.assertIn("existing-evidence-must-await-new-contract-readjudication", audit["blockers"])


if __name__ == "__main__":
    unittest.main()
