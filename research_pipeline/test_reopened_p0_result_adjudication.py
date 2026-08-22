from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from .reopened_p0_plan import build_p0_plan
from .reopened_p0_result_adjudication import (
    ADJUDICATOR_ROLE,
    BASELINE_BOUNDARY,
    BUDGET_STOP,
    IMPLEMENTATION_STOP,
    INCONCLUSIVE,
    METHOD_FAIL,
    METHOD_PASS,
    PACKET_STATUS,
    PROTOCOL_STOP,
    REQUIRED_CHECKS,
    RUNTIME_STOP,
    SUPPORT_STOP,
    build_p0_adjudication,
    build_p0_result_packet,
    public_p0_result,
    publish_p0_result_receipt,
    validate_p0_adjudication,
    validate_p0_result_ledger,
    validate_p0_result_packet,
)
from .test_reopened_p0_plan import ReopenedP0PlanTest


class ReopenedP0ResultAdjudicationTest(unittest.TestCase):
    def plan(self, root: Path):
        helper = ReopenedP0PlanTest(methodName="test_plan_requires_p0_authority_and_is_frozen_without_execution")
        authority, adjudication = helper.fixture(root)
        return build_p0_plan(p0_authorization=authority, adjudication=adjudication, spec=helper.spec())

    def result_input(self, plan: dict, outcome: str = "METHOD-PASS") -> dict:
        manifest = [
            {"role": "raw-trace", "sha256": "1" * 64, "bytes": 1024},
            {"role": "analysis-table", "sha256": "2" * 64, "bytes": 2048},
            {"role": "execution-summary", "sha256": "3" * 64, "bytes": 512},
        ]
        baseline = {
            "strongest_baseline": "generic matched effect",
            "same_information": True,
            "primary_effect": 0.04,
            "candidate_effect": 0.18,
        }
        return {
            "run_id": "p0-run-001",
            "typed_execution_outcome": outcome,
            "artifact_manifest": manifest,
            "artifact_manifest_sha256": hashlib.sha256(json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
            "analysis_receipt_sha256": "4" * 64,
            "recompute_receipt_sha256": "5" * 64,
            "completed_units": 48,
            "provider_calls": 188,
            "gpu_hours_used": 5.7,
            "evaluation_split": plan["plan_spec"]["evaluation_split"],
            "local_f0_data_excluded_from_confirmatory_statistic": True,
            "outcome_driven_selection_used": False,
            "primary_metric_name": "paired effect on held-out units",
            "primary_metric_value": 0.18 if outcome == "METHOD-PASS" else -0.01 if outcome == "METHOD-FAIL" else None,
            "primary_test_p_value": 0.01 if outcome == "METHOD-PASS" else 0.63 if outcome == "METHOD-FAIL" else None,
            "same_information_baseline_summary": baseline,
            "same_information_baseline_summary_sha256": hashlib.sha256(json.dumps(baseline, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        }

    def adjudication_packet(self, fail: str = "") -> dict:
        checks = {key: True for key in REQUIRED_CHECKS}
        if fail:
            checks[fail] = False
        return {
            "adjudicator_role": ADJUDICATOR_ROLE,
            "adjudicator_ref": "independent-p0-adjudicator:private-ref",
            "adjudicated_at": "2027-04-10T12:00:00+00:00",
            "checks": checks,
        }

    def test_result_packet_is_frozen_but_has_no_method_or_principle_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); plan = self.plan(root)
            packet = build_p0_result_packet(p0_plan=plan, packet=self.result_input(plan))
            self.assertTrue(validate_p0_result_packet(packet))
            self.assertEqual(packet["status"], PACKET_STATUS)
            self.assertFalse(packet["method_verdict_authorized"])
            self.assertFalse(packet["principle_update_allowed"])
            self.assertFalse(packet["claim_update_authorized"])

    def test_result_packet_rejects_screening_outcome_split_drift_and_local_f0_reuse(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); plan = self.plan(root)
            data = self.result_input(plan, "SCREENING-SIGNAL")
            with self.assertRaisesRegex(RuntimeError, "screening-only"):
                build_p0_result_packet(p0_plan=plan, packet=data)
            data = self.result_input(plan); data["evaluation_split"] = "local-f0"
            with self.assertRaisesRegex(RuntimeError, "evaluation split"):
                build_p0_result_packet(p0_plan=plan, packet=data)
            data = self.result_input(plan); data["local_f0_data_excluded_from_confirmatory_statistic"] = False
            with self.assertRaisesRegex(RuntimeError, "exclude local-F0"):
                build_p0_result_packet(p0_plan=plan, packet=data)

    def test_method_pass_is_current_realization_only_and_does_not_prove_principle(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); plan = self.plan(root); result = build_p0_result_packet(p0_plan=plan, packet=self.result_input(plan, "METHOD-PASS"))
            receipt = build_p0_adjudication(p0_plan=plan, result_packet=result, packet=self.adjudication_packet())
            self.assertTrue(validate_p0_adjudication(receipt))
            self.assertEqual(receipt["status"], METHOD_PASS)
            self.assertTrue(receipt["method_verdict_authorized"])
            self.assertEqual(receipt["method_verdict"], "METHOD-PASS")
            self.assertFalse(receipt["principle_update_allowed"])
            self.assertFalse(receipt["claim_update_authorized"])
            self.assertTrue(receipt["positive_method_evidence_does_not_prove_principle"])

    def test_method_fail_is_current_realization_only_and_cannot_falsify_principle(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); plan = self.plan(root); result = build_p0_result_packet(p0_plan=plan, packet=self.result_input(plan, "METHOD-FAIL"))
            receipt = build_p0_adjudication(p0_plan=plan, result_packet=result, packet=self.adjudication_packet())
            self.assertEqual(receipt["status"], METHOD_FAIL)
            self.assertEqual(receipt["failure_layer"], "method_realization")
            self.assertTrue(receipt["method_verdict_authorized"])
            self.assertFalse(receipt["principle_falsified"])
            self.assertFalse(receipt["principle_update_allowed"])
            self.assertTrue(receipt["principle_adjudication_required_for_any_principle_update"])

    def test_non_method_failures_are_typed_and_never_emit_method_verdict(self) -> None:
        cases = [
            ("METHOD-PASS", "protocol_validity_pass", PROTOCOL_STOP, "experiment_identifiability"),
            ("METHOD-PASS", "support_qualification_pass", SUPPORT_STOP, "assumption_scope"),
            ("RUNTIME-ERROR", "", RUNTIME_STOP, "execution"),
            ("IMPLEMENTATION-ERROR", "", IMPLEMENTATION_STOP, "execution"),
            ("BUDGET-STOP", "", BUDGET_STOP, "optimization"),
            ("BASELINE-FLOOR", "", BASELINE_BOUNDARY, "method_realization"),
        ]
        for outcome, fail, expected_status, expected_layer in cases:
            with self.subTest(expected_status=expected_status), tempfile.TemporaryDirectory() as td:
                root = Path(td); plan = self.plan(root); result = build_p0_result_packet(p0_plan=plan, packet=self.result_input(plan, outcome))
                receipt = build_p0_adjudication(p0_plan=plan, result_packet=result, packet=self.adjudication_packet(fail))
                self.assertEqual(receipt["status"], expected_status)
                self.assertEqual(receipt["failure_layer"], expected_layer)
                self.assertFalse(receipt["method_verdict_authorized"])
                self.assertEqual(receipt["method_verdict"], "NO_METHOD_VERDICT")
                self.assertFalse(receipt["principle_update_allowed"])

    def test_statistical_plan_failure_is_inconclusive_not_method_fail(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); plan = self.plan(root); result = build_p0_result_packet(p0_plan=plan, packet=self.result_input(plan, "METHOD-FAIL"))
            receipt = build_p0_adjudication(p0_plan=plan, result_packet=result, packet=self.adjudication_packet("statistical_plan_followed_pass"))
            self.assertEqual(receipt["status"], INCONCLUSIVE)
            self.assertFalse(receipt["method_verdict_authorized"])
            self.assertFalse(receipt["principle_update_allowed"])

    def test_append_only_order_idempotence_and_public_redaction(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); plan = self.plan(root); result = build_p0_result_packet(p0_plan=plan, packet=self.result_input(plan)); adjudication = build_p0_adjudication(p0_plan=plan, result_packet=result, packet=self.adjudication_packet())
            with self.assertRaisesRegex(RuntimeError, "published result packet"):
                publish_p0_result_receipt(root, adjudication, recorded_at="2027-04-10T12:00:00+00:00")
            first = publish_p0_result_receipt(root, result, recorded_at="2027-04-10T11:00:00+00:00")
            row = publish_p0_result_receipt(root, adjudication, recorded_at="2027-04-10T12:00:00+00:00")
            row2 = publish_p0_result_receipt(root, adjudication, recorded_at="2027-04-10T12:00:00+00:00")
            self.assertEqual(len(first["events"]), 1)
            self.assertEqual(len(row["events"]), 2)
            self.assertEqual(len(row2["events"]), 2)
            self.assertEqual(validate_p0_result_ledger(row2), [])
            public = public_p0_result(root, plan["contract_id"])
            self.assertEqual(public["status"], METHOD_PASS)
            self.assertTrue(public["method_verdict_authorized"])
            self.assertFalse(public["principle_update_allowed"])
            self.assertNotIn("independent-p0-adjudicator:private-ref", json.dumps(public))

    def test_tamper_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); plan = self.plan(root); result = build_p0_result_packet(p0_plan=plan, packet=self.result_input(plan)); adjudication = build_p0_adjudication(p0_plan=plan, result_packet=result, packet=self.adjudication_packet())
            bad = copy.deepcopy(result); bad["primary_metric_value"] = 999
            self.assertFalse(validate_p0_result_packet(bad))
            bad2 = copy.deepcopy(adjudication); bad2["principle_update_allowed"] = True
            self.assertFalse(validate_p0_adjudication(bad2))


if __name__ == "__main__":
    unittest.main()
