from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from research_pipeline.agent_constraint_externality_capability_continue import (
    adjudicate_continuation,
    load_recovery,
    remaining_capability_units,
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
            path.write_text("AA_API_KEY=secret\n", encoding="utf-8")
            os.utime(path, (100, 100))
            contract = {"credential_env_mtime_must_be_gt": 100}
            with self.assertRaises(RunnerError):
                require_rotated_credential(contract, path)
            os.utime(path, (101, 101))
            require_rotated_credential(contract, path)

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
