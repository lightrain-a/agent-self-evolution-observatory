from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from .reopened_scientific_contract import build_reopened_scientific_contract, publish_reopened_scientific_contract
from .reopened_scientific_problem_gate import (
    BLOCK_STATUS,
    PASS_STATUS,
    REQUIRED_CHECKS,
    REVIEWER_ROLE,
    build_reopen_problem_gate_receipt,
    load_latest_reopen_problem_gate,
    normalize_problem_gate_packet,
    public_reopen_problem_gate_summary,
    publish_reopen_problem_gate_receipt,
    validate_reopen_problem_gate_ledger,
    validate_reopen_problem_gate_receipt,
)
from .test_reopened_scientific_contract import ReopenedScientificContractTest


class ReopenedScientificProblemGateTest(unittest.TestCase):
    def contract(self, root: Path) -> dict:
        helper = ReopenedScientificContractTest(methodName="test_valid_contract_is_content_addressed_immutable_and_problem_gate_required")
        _, _, handoff = helper.handoff(root)
        contract = build_reopened_scientific_contract(handoff=handoff, spec=helper.spec(handoff))
        publish_reopened_scientific_contract(root, contract)
        return contract

    def packet(self, contract: dict, *, fail: str = "") -> dict:
        checks = {key: True for key in REQUIRED_CHECKS}
        if fail:
            checks[fail] = False
        return {
            "audit_id": "reopen-problem-audit-001",
            "reviewer_role": REVIEWER_ROLE,
            "reviewer_ref": "independent-reviewer:private-ref",
            "reviewed_at": "2027-04-02T12:00:00+00:00",
            "contract_sha256": contract["contract_sha256"],
            "checks": checks,
            "decision_critical_question": "Does the newly specified intervention define a scientifically adjudicable problem that cannot be answered by the parent contract alone?",
            "strongest_parent_reduction": "The parent contract may already explain the reviewer concern without a new intervention if the requested delta is only presentational.",
            "why_reopen_survives_parent_reduction": "The child freezes a new intervention/control contrast that the parent contract never adjudicated, so the requested delta cannot be settled by parent prose alone.",
            "failure_if_false": "If the matched-control falsifier rejects the intervention effect, the reopened child object stops without changing the parent claim states.",
            "scientific_authority": False,
            "paper_design_authority": False,
            "method_design_authority": False,
            "experiment_authority": False,
            "p0_authority": False,
            "gpu_authority": False,
            "claim_expansion_authority": False,
        }

    def test_packet_requires_independent_reviewer_and_exact_check_set(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); contract = self.contract(root)
            bad = self.packet(contract); bad["reviewer_ref"] = ""
            with self.assertRaisesRegex(RuntimeError, "reviewer reference"):
                normalize_problem_gate_packet(contract, bad)
            bad = self.packet(contract); bad["checks"]["EXTRA"] = True
            with self.assertRaisesRegex(RuntimeError, "required check set exactly"):
                normalize_problem_gate_packet(contract, bad)

    def test_passing_gate_only_grants_process_eligibility_not_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); contract=self.contract(root)
            receipt=build_reopen_problem_gate_receipt(contract=contract,packet=self.packet(contract))
            self.assertTrue(validate_reopen_problem_gate_receipt(receipt))
            self.assertEqual(receipt["status"],PASS_STATUS)
            self.assertTrue(receipt["paper_design_eligible"])
            self.assertTrue(receipt["method_design_review_eligible"])
            self.assertFalse(receipt["problem_gate_authority"])
            self.assertFalse(receipt["paper_design_authority"])
            self.assertFalse(receipt["method_design_authority"])
            self.assertFalse(receipt["experiment_authority"])
            self.assertFalse(receipt["p0_authority"])
            self.assertFalse(receipt["gpu_authority"])
            row=publish_reopen_problem_gate_receipt(root,receipt)
            row2=publish_reopen_problem_gate_receipt(root,receipt)
            self.assertEqual(len(row["events"]),1)
            self.assertEqual(len(row2["events"]),1)
            self.assertEqual(validate_reopen_problem_gate_ledger(row2),[])
            self.assertFalse((root/"experiment-authority").exists())

    def test_single_failed_check_blocks_all_downstream_eligibility(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); contract=self.contract(root)
            fail="strongest_parent_reduction_checked"
            receipt=build_reopen_problem_gate_receipt(contract=contract,packet=self.packet(contract,fail=fail))
            self.assertEqual(receipt["status"],BLOCK_STATUS)
            self.assertFalse(receipt["pass"])
            self.assertEqual(receipt["failed_checks"],[fail])
            self.assertFalse(receipt["paper_design_eligible"])
            self.assertFalse(receipt["method_design_review_eligible"])

    def test_authority_request_in_packet_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); contract=self.contract(root)
            packet=self.packet(contract); packet["experiment_authority"]=True
            with self.assertRaisesRegex(RuntimeError,"may not grant authority"):
                build_reopen_problem_gate_receipt(contract=contract,packet=packet)

    def test_contract_sha_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); contract=self.contract(root)
            packet=self.packet(contract); packet["contract_sha256"]="0"*64
            with self.assertRaisesRegex(RuntimeError,"contract SHA mismatch"):
                build_reopen_problem_gate_receipt(contract=contract,packet=packet)

    def test_receipt_tamper_and_ledger_authority_leak_are_detected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); contract=self.contract(root)
            receipt=build_reopen_problem_gate_receipt(contract=contract,packet=self.packet(contract))
            bad=copy.deepcopy(receipt); bad["method_design_authority"]=True
            self.assertFalse(validate_reopen_problem_gate_receipt(bad))
            row=publish_reopen_problem_gate_receipt(root,receipt)
            row["authority"]["experiment"]=True
            self.assertIn("reopen-problem-gate-ledger-authority-leak",validate_reopen_problem_gate_ledger(row))

    def test_public_summary_redacts_private_reviewer_reference(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); contract=self.contract(root)
            receipt=build_reopen_problem_gate_receipt(contract=contract,packet=self.packet(contract))
            publish_reopen_problem_gate_receipt(root,receipt)
            loaded=load_latest_reopen_problem_gate(root,contract["contract_id"])
            public=public_reopen_problem_gate_summary(loaded)
            self.assertEqual(public["status"],PASS_STATUS)
            text=json.dumps(public,sort_keys=True)
            self.assertNotIn("independent-reviewer:private-ref",text)
            self.assertNotIn('"reviewer_ref"',text)
            self.assertTrue(public["reviewer_ref_sha256"])

    def test_parent_contract_and_child_contract_are_not_mutated(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); contract=self.contract(root)
            path=root/"scientific-contracts"/f"{contract['contract_id']}.json"
            before=path.read_bytes()
            receipt=build_reopen_problem_gate_receipt(contract=contract,packet=self.packet(contract))
            publish_reopen_problem_gate_receipt(root,receipt)
            self.assertEqual(path.read_bytes(),before)
            self.assertEqual(contract["status"],"NEW_SCIENTIFIC_CONTRACT_CREATED_PROBLEM_GATE_REQUIRED")
            self.assertFalse(contract["experiment_authorized"])
            self.assertFalse(contract["gpu_execution_authorized"])


if __name__=="__main__":
    unittest.main()
