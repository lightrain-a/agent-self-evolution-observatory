from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from .reopened_scientific_method_design import (
    DESIGN_STATUS,
    REVIEW_BLOCK,
    REVIEW_PASS,
    REQUIRED_REVIEW_CHECKS,
    REVIEWER_ROLE,
    build_reopen_method_design,
    build_reopen_method_review,
    public_reopen_method_summary,
    publish_reopen_method_receipt,
    validate_reopen_method_design,
    validate_reopen_method_ledger,
    validate_reopen_method_review,
)
from .reopened_scientific_problem_gate import build_reopen_problem_gate_receipt, publish_reopen_problem_gate_receipt
from .test_reopened_scientific_problem_gate import ReopenedScientificProblemGateTest


class ReopenedScientificMethodDesignTest(unittest.TestCase):
    def fixture(self, root: Path):
        helper = ReopenedScientificProblemGateTest(methodName="test_passing_gate_only_grants_process_eligibility_not_authority")
        contract = helper.contract(root)
        gate = build_reopen_problem_gate_receipt(contract=contract, packet=helper.packet(contract))
        publish_reopen_problem_gate_receipt(root, gate)
        return contract, gate

    def spec(self):
        return {
            "method_name": "Scoped Reopen Certificate",
            "method_thesis": "Estimate the newly requested scientific delta under matched information and abstain when the child contract is not identified.",
            "formal_objects": {"treatment": "frozen child intervention", "outcome": "external task utility", "context": "pre-treatment task family"},
            "mechanism": "Compare matched intervention/control branches under the child contract and report only contract-valid contrasts.",
            "identifiability_boundary": "No causal claim is emitted when treatment support or matched continuation is unavailable.",
            "strongest_same_information_reduction": "A generic matched-effect estimator with identical treatment, controls, contexts, and budget.",
            "cheapest_local_falsifier": "Run the smallest preregistered matched unit set and stop if the generic reduction is equivalent or the effect is absent.",
            "resource_budget": {"max_local_units": 24, "max_provider_calls": 96, "max_gpu_hours": 4.0},
            "stop_rules": ["STOP if the generic same-information baseline is equivalent.", "STOP if the preregistered local falsifier fails."],
            "experiment_blueprint_outline": "Only after independent method review, design a local F0 followed by bounded P0; no execution is authorized here.",
            "same_information_baselines": [
                {"name": "generic-matched-effect", "same_information_access": "same units, treatment, controls, contexts, budget", "reduction_test": "compare decisions and confidence intervals"},
                {"name": "simple-stratified-delta", "same_information_access": "same units and context labels", "reduction_test": "test whether stratification alone reproduces the claimed method advantage"},
            ],
            "method_freeze_requirements": ["freeze treatment/control semantics", "freeze estimator and stop rules"],
        }

    def review(self, fail: str = ""):
        checks = {key: True for key in REQUIRED_REVIEW_CHECKS}
        if fail:
            checks[fail] = False
        return {
            "reviewer_role": REVIEWER_ROLE,
            "reviewer_ref": "independent-method-reviewer:private-ref",
            "reviewed_at": "2027-04-03T12:00:00+00:00",
            "checks": checks,
            "reduction_analysis": "The design survives the strongest frozen generic reduction because its decision object remains distinct under identical information.",
            "failure_if_blocked": "Return to the child scientific contract and revise or stop the method realization; do not execute experiments.",
        }

    def test_problem_gate_pass_required(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); contract, gate = self.fixture(root); gate = dict(gate); gate["status"] = "REOPEN_PROBLEM_GATE_BLOCKED"
            with self.assertRaisesRegex(RuntimeError, "Problem Gate PASS"):
                build_reopen_method_design(contract=contract, problem_gate_receipt=gate, method_spec=self.spec())

    def test_method_design_is_frozen_but_grants_no_execution_authority(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); contract, gate = self.fixture(root)
            design = build_reopen_method_design(contract=contract, problem_gate_receipt=gate, method_spec=self.spec())
            self.assertTrue(validate_reopen_method_design(design)); self.assertEqual(design["status"], DESIGN_STATUS)
            self.assertTrue(design["method_frozen"]); self.assertFalse(design["experiment_blueprint_design_eligible"])
            self.assertFalse(design["experiment_authority"]); self.assertFalse(design["gpu_authority"])
            row = publish_reopen_method_receipt(root, design); row2 = publish_reopen_method_receipt(root, design)
            self.assertEqual(len(row["events"]), 1); self.assertEqual(len(row2["events"]), 1); self.assertEqual(validate_reopen_method_ledger(row2), [])

    def test_spec_requires_matched_baselines_budget_and_stop_rules(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); contract, gate=self.fixture(root)
            for mutate, regex in [
                (lambda s: s.update({"same_information_baselines": s["same_information_baselines"][:1]}), "at least two"),
                (lambda s: s.update({"stop_rules": ["one"]}), "at least two"),
                (lambda s: s.update({"resource_budget": {"max_local_units": 0, "max_provider_calls": 1, "max_gpu_hours": 1}}), "resource budget"),
            ]:
                spec=self.spec(); mutate(spec)
                with self.assertRaisesRegex(RuntimeError, regex): build_reopen_method_design(contract=contract, problem_gate_receipt=gate, method_spec=spec)

    def test_independent_review_pass_only_unlocks_blueprint_design_eligibility(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); contract, gate=self.fixture(root); design=build_reopen_method_design(contract=contract, problem_gate_receipt=gate, method_spec=self.spec())
            publish_reopen_method_receipt(root, design)
            review=build_reopen_method_review(method_design=design, review_packet=self.review())
            self.assertTrue(validate_reopen_method_review(review)); self.assertEqual(review["status"], REVIEW_PASS)
            self.assertTrue(review["experiment_blueprint_design_eligible"]); self.assertFalse(review["local_validation_eligible"])
            self.assertFalse(review["experiment_blueprint_authority"]); self.assertFalse(review["experiment_authority"]); self.assertFalse(review["gpu_authority"])
            row=publish_reopen_method_receipt(root, review); self.assertEqual(validate_reopen_method_ledger(row), [])
            public=public_reopen_method_summary(root, contract["contract_id"]); self.assertEqual(public["status"], REVIEW_PASS)

    def test_single_failed_review_check_blocks_blueprint(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); contract, gate=self.fixture(root); design=build_reopen_method_design(contract=contract, problem_gate_receipt=gate, method_spec=self.spec())
            fail="method_not_generic_relabeling_pass"; review=build_reopen_method_review(method_design=design, review_packet=self.review(fail))
            self.assertEqual(review["status"], REVIEW_BLOCK); self.assertEqual(review["failed_checks"], [fail]); self.assertFalse(review["experiment_blueprint_design_eligible"])

    def test_review_must_follow_published_design_and_private_ref_is_redacted(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); contract, gate=self.fixture(root); design=build_reopen_method_design(contract=contract, problem_gate_receipt=gate, method_spec=self.spec()); review=build_reopen_method_review(method_design=design, review_packet=self.review())
            with self.assertRaisesRegex(RuntimeError, "prior frozen method design"): publish_reopen_method_receipt(root, review)
            publish_reopen_method_receipt(root, design); publish_reopen_method_receipt(root, review)
            public=public_reopen_method_summary(root, contract["contract_id"]); text=json.dumps(public, sort_keys=True)
            self.assertNotIn("independent-method-reviewer:private-ref", text); self.assertNotIn('"reviewer_ref"', text); self.assertTrue(public["reviewer_ref_sha256"])

    def test_tamper_and_authority_leak_are_detected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); contract, gate=self.fixture(root); design=build_reopen_method_design(contract=contract, problem_gate_receipt=gate, method_spec=self.spec())
            bad=copy.deepcopy(design); bad["experiment_authority"]=True; self.assertFalse(validate_reopen_method_design(bad))
            publish_reopen_method_receipt(root, design); review=build_reopen_method_review(method_design=design, review_packet=self.review()); badr=copy.deepcopy(review); badr["gpu_authority"]=True; self.assertFalse(validate_reopen_method_review(badr))


if __name__ == "__main__":
    unittest.main()
