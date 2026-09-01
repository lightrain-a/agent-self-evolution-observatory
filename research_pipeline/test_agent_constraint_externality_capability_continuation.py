from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from research_pipeline.agent_constraint_externality_capability_continue import (
    CREDENTIAL_REUSE_AUTHORIZATION_PATH,
    adjudicate_continuation,
    load_recovery,
    remaining_capability_units,
    require_credential_authorization,
    require_rotated_credential,
)
from research_pipeline.agent_constraint_externality_capability_measurement_recover import (
    HISTORICAL_UNIT_ID,
)
from research_pipeline.agent_constraint_externality_runner_core import (
    ALLOWED_ALIAS,
    OBJECT_ID,
    RunnerError,
    sha256_value,
)

ROOT = Path(__file__).resolve().parents[1]
RECOVERY = ROOT / "generated/agent-constraint-externality-capability-measurement-recovery-r1-20260901.json"
CONTRACT = ROOT / "generated/agent-constraint-externality-capability-continuation-r1-contract-20260901.json"


class CapabilityContinuationTests(unittest.TestCase):
    def test_recovery_artifact_is_measurement_only_and_content_addressed(self) -> None:
        payload = load_recovery(RECOVERY)
        self.assertEqual(payload["status"], "HISTORICAL_MEASUREMENT_RECOVERY_PASS")
        self.assertEqual(payload["provider_requests_added_by_recovery"], 0)
        self.assertFalse(payload["agent_reexecution"])
        self.assertTrue(payload["tool_loop_completed"])
        claimed = payload["content_sha256"]
        unsigned = dict(payload)
        unsigned.pop("content_sha256")
        self.assertEqual(claimed, sha256_value(unsigned))

    def test_remaining_units_are_exactly_the_seven_never_dispatched_units(self) -> None:
        units = remaining_capability_units()
        self.assertEqual(len(units), 7)
        self.assertEqual(len({unit.unit_id for unit in units}), 7)
        self.assertNotIn(HISTORICAL_UNIT_ID, {unit.unit_id for unit in units})

    def test_contract_keeps_f0_closed_and_forbids_recovered_replay(self) -> None:
        payload = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["remaining_units"], 7)
        self.assertFalse(payload["replay_recovered_unit"])
        self.assertFalse(payload["f0_authorized"])
        self.assertEqual(payload["model"], ALLOWED_ALIAS)
        claimed = payload["content_sha256"]
        unsigned = dict(payload)
        unsigned.pop("content_sha256")
        self.assertEqual(claimed, sha256_value(unsigned))

    def test_credential_rotation_gate_is_objective_and_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".env"
            path.write_text("PLACEHOLDER_ROTATION_MARKER=updated\n", encoding="utf-8")
            os.utime(path, (100, 100))
            contract = {"credential_env_mtime_must_be_gt": 100}
            with self.assertRaises(RunnerError):
                require_rotated_credential(contract, path)
            os.utime(path, (101, 101))
            require_rotated_credential(contract, path)

    def test_existing_credential_reuse_override_is_content_addressed_and_non_scientific(self) -> None:
        payload = json.loads(CREDENTIAL_REUSE_AUTHORIZATION_PATH.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "EXISTING_CREDENTIAL_REUSE_USER_AUTHORIZED")
        self.assertTrue(payload["existing_credential_reuse_authorized"])
        self.assertFalse(payload["credential_value_persisted"])
        self.assertFalse(payload["scientific_protocol_changed"])
        self.assertFalse(payload["model_changed"])
        self.assertFalse(payload["thresholds_changed"])
        self.assertFalse(payload["replay_recovered_unit_authorized"])
        self.assertFalse(payload["f0_authorized"])
        claimed = payload["content_sha256"]
        unsigned = dict(payload)
        unsigned.pop("content_sha256")
        self.assertEqual(claimed, sha256_value(unsigned))

    def test_existing_credential_reuse_authorization_can_replace_rotation_gate(self) -> None:
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".env"
            path.write_text("PLACEHOLDER_CREDENTIAL_MARKER=existing\n", encoding="utf-8")
            old_time = int(contract["credential_env_mtime_must_be_gt"])
            os.utime(path, (old_time, old_time))
            mode = require_credential_authorization(
                contract,
                env_path=path,
                reuse_authorization_path=CREDENTIAL_REUSE_AUTHORIZATION_PATH,
            )
            self.assertEqual(mode, "EXISTING_CREDENTIAL_USER_AUTHORIZED")

    def test_toolcap_failure_counts_as_incomplete_capability_measurement_not_interface(self) -> None:
        units = remaining_capability_units()
        with tempfile.TemporaryDirectory() as directory:
            ledger = Path(directory) / "continuation-ledger.jsonl"
            measurements = Path(directory) / "toolcap-measurements.jsonl"
            rows = []
            for index, unit in enumerate(units):
                rows.append({
                    "schema_version": "ace-exactly-once-ledger-v1",
                    "object_id": OBJECT_ID,
                    "event": "DISPATCH",
                    "unit_id": unit.unit_id,
                })
                if index == 0:
                    rows.append({
                        "schema_version": "ace-exactly-once-ledger-v1",
                        "object_id": OBJECT_ID,
                        "event": "FAILURE",
                        "unit_id": unit.unit_id,
                        "failure_class": "RunnerError",
                        "message": "Tool-call cap exceeded.",
                        "retry_attempted": False,
                        "provider_receipts": [{"resolved_model": ALLOWED_ALIAS}],
                    })
                    measurement = {
                        "schema_version": "ace-capability-toolcap-measurement-v1",
                        "object_id": OBJECT_ID,
                        "continuation_id": "CAPABILITY-INTERFACE-RECOVERY-CONTINUATION-R1",
                        "unit_id": unit.unit_id,
                        "family_id": unit.family_id,
                        "classification": "CAPABILITY_TOOL_LOOP_INCOMPLETE_AT_FROZEN_CAP",
                        "tool_loop_completed": False,
                        "executed_tool_call_cap": 12,
                        "provider_receipt_count": 1,
                        "provider_reexecution": False,
                        "retry": False,
                        "replacement": False,
                        "recovery_mode": "TEST",
                        "evaluation": {"target_success": False, "non_target_preservation": 1.0},
                    }
                    measurement["content_sha256"] = sha256_value(measurement)
                    measurements.write_text(json.dumps(measurement, sort_keys=True) + "\n", encoding="utf-8")
                else:
                    rows.append({
                        "schema_version": "ace-exactly-once-ledger-v1",
                        "object_id": OBJECT_ID,
                        "event": "COMPLETION",
                        "unit_id": unit.unit_id,
                        "provider_receipts": [{"resolved_model": ALLOWED_ALIAS}],
                        "result": {
                            "tool_call_count": 1,
                            "evaluation": {"target_success": True, "non_target_preservation": 1.0},
                        },
                    })
            ledger.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
            result = adjudicate_continuation(
                recovery_path=RECOVERY,
                continuation_ledger_path=ledger,
                toolcap_measurement_ledger_path=measurements,
            )
            self.assertEqual(result["tool_cap_incomplete_measurements"], 1)
            self.assertEqual(result["status"], "CAPABILITY_CALIBRATION_PASS")
            self.assertEqual(result["gate"]["tool_loop_completion_rate"], 0.875)

    def test_combined_adjudication_uses_one_recovery_plus_seven_new_units(self) -> None:
        units = remaining_capability_units()
        with tempfile.TemporaryDirectory() as directory:
            ledger = Path(directory) / "continuation-ledger.jsonl"
            rows = []
            for index, unit in enumerate(units):
                rows.append({
                    "schema_version": "ace-exactly-once-ledger-v1",
                    "object_id": OBJECT_ID,
                    "event": "DISPATCH",
                    "unit_id": unit.unit_id,
                })
                rows.append({
                    "schema_version": "ace-exactly-once-ledger-v1",
                    "object_id": OBJECT_ID,
                    "event": "COMPLETION",
                    "unit_id": unit.unit_id,
                    "provider_receipts": [{"resolved_model": ALLOWED_ALIAS}],
                    "result": {
                        "tool_call_count": 1,
                        "evaluation": {
                            "target_success": index < 6,
                            "non_target_preservation": 1.0,
                        },
                    },
                })
            ledger.write_text(
                "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
                encoding="utf-8",
            )
            result = adjudicate_continuation(
                recovery_path=RECOVERY,
                continuation_ledger_path=ledger,
            )
            self.assertEqual(result["valid_capability_measurements"], 8)
            self.assertEqual(result["recovered_measurements"], 1)
            self.assertEqual(result["newly_executed_measurements"], 7)
            self.assertEqual(result["status"], "CAPABILITY_CALIBRATION_PASS")
            self.assertEqual(result["f0_backbone"], ALLOWED_ALIAS)
            self.assertFalse(result["authority"]["f0"])


if __name__ == "__main__":
    unittest.main()
