from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from .reopened_p0_principle_handoff import (
    DEAD_END_CANDIDATE_STATUS,
    PREDICTION_REJECTED_STATUS,
    SUPPORT_STATUS,
    UNRESOLVED_STATUS,
    build_p0_principle_handoff,
    public_p0_principle_handoff,
    publish_p0_principle_handoff,
    validate_p0_principle_handoff,
    validate_p0_principle_handoff_ledger,
)
from .reopened_p0_result_adjudication import build_p0_adjudication, build_p0_result_packet
from .test_reopened_p0_result_adjudication import ReopenedP0ResultAdjudicationTest
from .test_reopened_pre_experiment_adapter import ReopenedPreExperimentAdapterTest


class ReopenedP0PrincipleHandoffTest(unittest.TestCase):
    def principle_certificate(self) -> dict:
        runtime = ReopenedPreExperimentAdapterTest(methodName="test_compiler_pass_still_requires_experiment_lease").runtime()
        contract = runtime["pre_experiment"]["principle_certificate"]
        return {"passed": True, "contract": contract}

    def p0_adjudication(self, root: Path, outcome: str):
        helper = ReopenedP0ResultAdjudicationTest(methodName="test_method_fail_is_current_realization_only_and_cannot_falsify_principle")
        plan = helper.plan(root)
        result = build_p0_result_packet(p0_plan=plan, packet=helper.result_input(plan, outcome))
        return build_p0_adjudication(p0_plan=plan, result_packet=result, packet=helper.adjudication_packet())

    def true_negative_evidence(self, *, with_counter: bool = False) -> dict:
        evidence = {
            "registered_prediction_id": "P1",
            "assumptions_hold": True,
            "scope_conditions_hold": True,
            "operationalization_valid": True,
            "experiment_identifiable": True,
            "optimization_adequate": True,
            "independent_truth": True,
            "matched_baseline": True,
            "protocol_validity": True,
            "falsifier_triggered": True,
        }
        if with_counter:
            evidence["counter_explanation"] = {
                "type": "SAME_INFORMATION_REDUCTION",
                "statement": "The matched generic estimator explains the same observable decisions without the reopened method mechanism.",
                "opposite_prediction": "The generic matched estimator remains equivalent on fresh held-out confirmatory units.",
                "opposite_principle": "The extra reopened method mechanism is unnecessary within this frozen scope.",
                "opposite_search_seed": "Search for the smallest same-information invariant explanation.",
                "scope": "Only the frozen child-contract confirmatory scope.",
                "reopen_condition": "Reopen if a fresh same-information setting produces stable decision disagreement.",
                "same_information_or_scope_matched": True,
                "evidence_refs": ["sha256:counter-evidence"],
                "alternative_explanations_ruled_out": ["runtime failure", "support failure", "protocol mismatch"],
                "same_information_reduction_verified": True,
                "positive_support": True,
            }
        return evidence

    def test_method_pass_only_supports_principle_without_proof_or_update_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); adjudication = self.p0_adjudication(root, "METHOD-PASS")
            receipt = build_p0_principle_handoff(p0_adjudication=adjudication, principle_certificate=self.principle_certificate())
            self.assertTrue(validate_p0_principle_handoff(receipt))
            self.assertEqual(receipt["status"], SUPPORT_STATUS)
            self.assertEqual(receipt["underlying_verdict"], "PRINCIPLE_SUPPORTED_NOT_PROVEN")
            self.assertFalse(receipt["registered_prediction_rejected"])
            self.assertFalse(receipt["dead_end_candidate"])
            self.assertFalse(receipt["automatic_principle_update_authorized"])
            self.assertTrue(receipt["positive_method_evidence_does_not_prove_principle"])

    def test_method_fail_with_missing_falsification_preconditions_remains_unresolved(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); adjudication = self.p0_adjudication(root, "METHOD-FAIL")
            evidence = self.true_negative_evidence(); evidence["protocol_validity"] = False
            receipt = build_p0_principle_handoff(p0_adjudication=adjudication, principle_certificate=self.principle_certificate(), principle_evidence=evidence)
            self.assertEqual(receipt["status"], UNRESOLVED_STATUS)
            self.assertEqual(receipt["underlying_verdict"], "METHOD_NEGATIVE_PRINCIPLE_UNRESOLVED")
            self.assertIn("protocol_validity", receipt["missing_preconditions"])
            self.assertFalse(receipt["registered_prediction_rejected"])
            self.assertFalse(receipt["automatic_principle_update_authorized"])

    def test_all_preconditions_without_counter_explanation_rejects_prediction_only(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); adjudication = self.p0_adjudication(root, "METHOD-FAIL")
            receipt = build_p0_principle_handoff(p0_adjudication=adjudication, principle_certificate=self.principle_certificate(), principle_evidence=self.true_negative_evidence())
            self.assertEqual(receipt["status"], PREDICTION_REJECTED_STATUS)
            self.assertEqual(receipt["underlying_verdict"], "REGISTERED_PREDICTION_REJECTED_COUNTEREXPLANATION_REQUIRED")
            self.assertTrue(receipt["registered_prediction_rejected"])
            self.assertFalse(receipt["dead_end_candidate"])
            self.assertFalse(receipt["persistent_dead_end_memory_write_authorized"])

    def test_positive_counter_explanation_only_creates_human_review_dead_end_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); adjudication = self.p0_adjudication(root, "METHOD-FAIL")
            receipt = build_p0_principle_handoff(p0_adjudication=adjudication, principle_certificate=self.principle_certificate(), principle_evidence=self.true_negative_evidence(with_counter=True))
            self.assertEqual(receipt["status"], DEAD_END_CANDIDATE_STATUS)
            self.assertEqual(receipt["underlying_verdict"], "PRINCIPLE_DEAD_END_CERTIFIED")
            self.assertTrue(receipt["dead_end_candidate"])
            self.assertTrue(receipt["external_human_principle_review_required"])
            self.assertFalse(receipt["automatic_principle_update_authorized"])
            self.assertFalse(receipt["persistent_dead_end_memory_write_authorized"])
            self.assertFalse(receipt["claim_update_authorized"])

    def test_non_method_p0_outcome_cannot_enter_principle_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            helper = ReopenedP0ResultAdjudicationTest(methodName="test_non_method_failures_are_typed_and_never_emit_method_verdict")
            plan = helper.plan(root)
            result = build_p0_result_packet(p0_plan=plan, packet=helper.result_input(plan, "RUNTIME-ERROR"))
            adjudication = build_p0_adjudication(p0_plan=plan, result_packet=result, packet=helper.adjudication_packet())
            with self.assertRaisesRegex(RuntimeError, "authorized P0 method verdict"):
                build_p0_principle_handoff(p0_adjudication=adjudication, principle_certificate=self.principle_certificate())

    def test_append_only_public_summary_and_tamper_detection(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); adjudication = self.p0_adjudication(root, "METHOD-FAIL")
            receipt = build_p0_principle_handoff(p0_adjudication=adjudication, principle_certificate=self.principle_certificate(), principle_evidence=self.true_negative_evidence(with_counter=True))
            row = publish_p0_principle_handoff(root, receipt, recorded_at="2027-04-11T12:00:00+00:00")
            row2 = publish_p0_principle_handoff(root, receipt, recorded_at="2027-04-11T12:00:00+00:00")
            self.assertEqual(len(row["events"]), 1)
            self.assertEqual(len(row2["events"]), 1)
            self.assertEqual(validate_p0_principle_handoff_ledger(row2), [])
            public = public_p0_principle_handoff(root, adjudication["contract_id"])
            self.assertEqual(public["status"], DEAD_END_CANDIDATE_STATUS)
            self.assertTrue(public["dead_end_candidate"])
            self.assertFalse(public["automatic_principle_update_authorized"])
            bad = copy.deepcopy(receipt); bad["persistent_dead_end_memory_write_authorized"] = True
            self.assertFalse(validate_p0_principle_handoff(bad))
            self.assertNotIn("counter_explanation", json.dumps(public))


if __name__ == "__main__":
    unittest.main()
