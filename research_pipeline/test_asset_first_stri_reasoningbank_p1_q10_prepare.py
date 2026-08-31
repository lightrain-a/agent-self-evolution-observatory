from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from research_pipeline.asset_first_stri_reasoningbank_p1_core import sha256_file
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_prepare import (
    CONTRACT, EXPECTED_ORDER, prepare, verify_history,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q5_prepare import load_payload


class ReasoningBankP1Q10PrepareTest(unittest.TestCase):
    def test_frozen_contract_and_history(self) -> None:
        checks = verify_history()
        self.assertTrue(all(row["pass"] for row in checks.values()))
        payload = load_payload(CONTRACT)
        self.assertEqual(
            payload["decision"],
            "P1_Q10_DOCKER_START_DAEMON_RECONCILIATION_PREREGISTERED",
        )
        self.assertEqual(
            payload["single_changed_variable"]["variable"],
            "Docker start acknowledgement acceptance rule",
        )
        self.assertFalse(
            payload["single_changed_variable"]["timeout_duration_changed"]
        )
        self.assertTrue(
            payload["exactly_once_invariants"]["second_start_forbidden"]
        )
        self.assertEqual(
            payload["exactly_once_invariants"]["client_start_invocations"], 1
        )
        self.assertFalse(
            payload["authorization"]["q10_replay_execution_authorized"]
        )
        order = [
            (row["selection_rank"], row["instance_id"], row["arm"])
            for row in payload["frozen_replay_sources"]
        ]
        self.assertEqual(order, EXPECTED_ORDER)

    def test_prepare_is_deterministic_except_timestamp(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "contract.json"
            result = prepare(output)
            self.assertEqual(result["file_sha256"], sha256_file(output))
            payload = load_payload(output)
            payload.pop("created_at_utc")
            frozen = load_payload(CONTRACT)
            frozen.pop("created_at_utc")
            self.assertEqual(payload, frozen)


if __name__ == "__main__":
    unittest.main()
