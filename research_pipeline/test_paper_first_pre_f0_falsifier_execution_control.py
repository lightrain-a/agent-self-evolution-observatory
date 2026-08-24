from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from .paper_first_pre_f0_falsifier_execution_control import (
    AUTHORITY_TYPE,
    build_authorization_request,
    build_current_execution_control,
    claim_external_authority_once,
    load_external_human_authority,
    require_single_use_execution_authority,
    validate_authorization_request,
    validate_public_state,
)


class PreF0FalsifierExecutionControlTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.control = build_current_execution_control()

    def test_current_control_locks_exact_support_qualified_snapshot_only(self) -> None:
        state = copy.deepcopy(self.control)
        self.assertEqual(validate_public_state(state), [])
        self.assertEqual(state["status"], "PRE_F0_FALSIFIER_EXECUTION_CONTROL_LOCKED")
        self.assertEqual(state["summary"]["support_qualified_candidates"], 1)
        self.assertEqual(state["summary"]["qualified_units_cap_total"], 290)
        self.assertEqual(state["summary"]["falsifier_execution_authorized"], 0)
        self.assertEqual(state["summary"]["provider_calls_authorized"], 0)
        self.assertEqual(state["summary"]["gpu_authorized"], 0)
        row = state["candidate_bindings"][0]
        self.assertEqual(row["candidate_snapshot_sha256"], "9b57dbc5728b0f2247917c2f27e3e65b6876f57b3b18ff1026b945e73fb96d3c")
        self.assertEqual(row["unit_manifest_sha256"], "0aa414ad49241a51b169bd8d08c70176f33d204fb85accda41d9e593d7cc8449")
        self.assertEqual(row["qualified_units_cap"], 290)
        self.assertFalse(row["execution_authorized"])
        self.assertFalse(row["terminal_hold_resolution_authorized"])
        self.assertFalse(row["retroactive_historical_execution_authorized"])
        self.assertFalse(row["fresh_out_of_scope_intervention_authorized"])
        public = json.dumps(state, ensure_ascii=False)
        self.assertNotIn('"candidate_id"', public)
        self.assertNotIn('"title"', public)
        self.assertNotIn('/data/', public)
        self.assertNotIn('/home/', public)

    def test_authorization_request_is_zero_authority_and_exact_scope(self) -> None:
        request = build_authorization_request(self.control)
        self.assertEqual(validate_authorization_request(request, control=self.control), [])
        self.assertEqual(request["status"], "AWAITING_EXPLICIT_EXTERNAL_HUMAN_EXECUTION_AUTHORITY")
        self.assertEqual(request["summary"]["requests"], 1)
        row = request["request_entries"][0]
        self.assertEqual(row["requested_execution_route"], "EXACT_SUPPORT_QUALIFIED_CPU_SECONDARY_AUDIT_ONLY")
        self.assertFalse(row["bounded_falsifier_execution_authorized"])
        contract = request["required_authority_contract"]
        self.assertTrue(contract["bounded_falsifier_execution_authorized"])
        self.assertTrue(contract["cpu_execution_authorized"])
        self.assertTrue(contract["single_attempt"])
        for key in (
            "provider_calls_authorized",
            "gpu_calls_authorized",
            "terminal_hold_resolution_authorized",
            "retroactive_historical_execution_authorized",
            "fresh_out_of_scope_intervention_authorized",
            "problem_gate_authorized",
            "paper_design_authorized",
            "method_authorized",
            "experiment_authorized",
            "p0_authorized",
            "scientific_authority",
        ):
            self.assertFalse(contract[key])

    def _permit(self) -> dict:
        row = self.control["candidate_bindings"][0]
        return {
            "authority_type": AUTHORITY_TYPE,
            "decision": "approve",
            "reviewed_by": "human-user",
            "reviewed_at": "2026-08-24T23:00:00+08:00",
            "source_message_ref": "test-fixture-only",
            "source_message_sha256": "f" * 64,
            "control_snapshot_sha256": self.control["control_snapshot_sha256"],
            "discovery_transaction_id": self.control["discovery_transaction_id"],
            "source_generator_run_id": self.control["source_generator_run_id"],
            "candidate_snapshot_sha256": row["candidate_snapshot_sha256"],
            "unit_manifest_sha256": row["unit_manifest_sha256"],
            "support_scope_sha256": row["support_scope_sha256"],
            "bounded_falsifier_execution_authorized": True,
            "cpu_execution_authorized": True,
            "provider_calls_authorized": False,
            "gpu_calls_authorized": False,
            "single_attempt": True,
            "terminal_hold_resolution_authorized": False,
            "retroactive_historical_execution_authorized": False,
            "fresh_out_of_scope_intervention_authorized": False,
            "problem_gate_authorized": False,
            "paper_design_authorized": False,
            "method_authorized": False,
            "experiment_authorized": False,
            "p0_authorized": False,
            "scientific_authority": False,
        }

    def test_missing_or_out_of_scope_permit_fails_closed(self) -> None:
        missing = load_external_human_authority(self.control, "")
        self.assertFalse(missing["bounded_falsifier_execution_authorized"])
        with self.assertRaisesRegex(RuntimeError, "valid explicit external human authority"):
            require_single_use_execution_authority(self.control, authority=missing)
        payload = self._permit()
        payload["unit_manifest_sha256"] = "a" * 64
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "permit.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            invalid = load_external_human_authority(self.control, path)
        self.assertFalse(invalid["bounded_falsifier_execution_authorized"])
        self.assertIn("binding-mismatch:unit_manifest_sha256", invalid["errors"])

    def test_external_exact_scope_permit_is_single_use_but_not_terminal_authority(self) -> None:
        payload = self._permit()
        with tempfile.TemporaryDirectory() as directory:
            permit = Path(directory) / "permit.json"
            permit.write_text(json.dumps(payload), encoding="utf-8")
            authority = load_external_human_authority(self.control, permit)
            self.assertTrue(authority["bounded_falsifier_execution_authorized"])
            self.assertTrue(authority["cpu_execution_authorized"])
            self.assertFalse(authority["terminal_hold_resolution_authorized"])
            self.assertFalse(authority["retroactive_historical_execution_authorized"])
            self.assertFalse(authority["fresh_out_of_scope_intervention_authorized"])
            control_root = Path(directory) / "control"
            first = claim_external_authority_once(control_root, self.control, authority, "unit-test-run-1")
            self.assertTrue(first.is_file())
            with self.assertRaisesRegex(RuntimeError, "single-use"):
                claim_external_authority_once(control_root, self.control, authority, "unit-test-run-2")

    def test_request_tamper_is_detected(self) -> None:
        request = build_authorization_request(self.control)
        request["request_entries"][0]["qualified_units_cap"] += 1
        self.assertTrue(validate_authorization_request(request, control=self.control))


if __name__ == "__main__":
    unittest.main()
