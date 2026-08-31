from __future__ import annotations

import inspect
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from research_pipeline.asset_first_stri_reasoningbank_p1_core import sha256_text
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_core import (
    fixture_by_id, replay_one, verify_q10_contract,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_prepare import (
    CONTRACT, EXPECTED_ORDER, load_payload,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_runner import (
    index_payload, run_q10,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_runtime import (
    Q10_CONTRACT_SHA256,
)


class FakeReplayContainer:
    def __init__(self, source: dict, fixture: dict, patch_text: str) -> None:
        self.source = source
        self.fixture = fixture
        self.patch_text = patch_text
        self.exec_count = 0
        self.start_reconciliation_receipt = {
            "client_start_invocations": 1,
            "reconciliation_invoked": True,
            "second_start_invoked": False,
            "receipt_finalized": True,
            "accepted": True,
            "exact_identity_verified": True,
            "exact_running_state_verified": True,
        }

    def start(self) -> dict:
        return {
            "image_inspect": {"output": self.source["image_amd64_manifest_digest"]},
            "base_commit_receipt": {
                "observed_head": self.source["base_commit"],
                "rule": "exact_base_after_preregistered_hard_reset",
            },
            "q10_start_reconciliation": self.start_reconciliation_receipt,
        }

    def exec(self, action: str, *, timeout: int | float) -> dict:
        self.exec_count += 1
        output = "" if self.exec_count == 1 else self.patch_text
        return {"returncode": 0, "timed_out": False, "output": output}

    def close(self) -> dict:
        return {
            "cleanup_invoked": True,
            "reconciliation_receipt_finalized_before_cleanup": True,
            "accepted": True,
        }


class ReasoningBankP1Q10StackTest(unittest.TestCase):
    def test_contract_history_and_all_sources_exact(self) -> None:
        verification = verify_q10_contract()
        self.assertTrue(verification["pass"])
        self.assertEqual(
            verification["contract_sha256"], Q10_CONTRACT_SHA256
        )
        self.assertEqual(len(verification["source_checks"]), 10)
        self.assertTrue(
            all(row["pass"] for row in verification["source_checks"])
        )

    def test_provider_model_path_is_unreachable(self) -> None:
        source = inspect.getsource(replay_one)
        self.assertNotIn("make_client", source)
        self.assertNotIn("execute_agent", source)
        self.assertNotIn("create_response", source)

    @patch(
        "research_pipeline.asset_first_stri_reasoningbank_p1_q10_runner.sha256_file",
        return_value="f" * 64,
    )
    def test_index_freezes_order_zero_calls_and_exactly_once(
        self, _sha256_file
    ) -> None:
        payload = index_payload([], [], False)
        self.assertEqual(
            payload["planned_order"], [list(row) for row in EXPECTED_ORDER]
        )
        self.assertEqual(payload["planned_run_count"], 10)
        self.assertEqual(payload["model_calls"], payload["provider_calls"])
        self.assertEqual(payload["model_calls"], 0)
        self.assertEqual(payload["automatic_retry"], "forbidden")
        self.assertEqual(payload["replacement_sampling"], "forbidden")
        self.assertEqual(payload["second_start"], "forbidden")

    def test_second_runner_invocation_is_refused_before_work(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            index = root / "existing.json"
            index.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "second Q10 invocation"):
                run_q10(root / "runs", index)

    def test_replay_payload_persists_start_evaluator_and_cleanup_receipts(self) -> None:
        contract = load_payload(CONTRACT)
        source = contract["frozen_replay_sources"][0]
        fixture = fixture_by_id()[source["instance_id"]]
        q4 = load_payload(Path(__file__).resolve().parents[1] / source["source_run_path"])
        patch_text = q4["result"]
        expected_cases = (
            fixture["evaluator_only"]["FAIL_TO_PASS"]
            + fixture["evaluator_only"]["PASS_TO_PASS"]
        )
        status_map = {case: "PASSED" for case in expected_cases}
        outcome = {
            "raw_execution": {
                "returncode": 0,
                "timed_out": False,
                "output": "synthetic evaluator output",
            },
            "test_patch_sha256": sha256_text(
                fixture["evaluator_only"]["test_patch"]
            ),
            "status_map": status_map,
            "resolved": True,
        }
        fake = FakeReplayContainer(source, fixture, patch_text)
        with (
            patch(
                "research_pipeline.asset_first_stri_reasoningbank_p1_q10_core."
                "DaemonReconciledDockerRun",
                return_value=fake,
            ),
            patch(
                "research_pipeline.asset_first_stri_reasoningbank_p1_q10_core."
                "evaluate",
                return_value=outcome,
            ),
            patch(
                "research_pipeline.asset_first_stri_reasoningbank_p1_q10_core."
                "official_and_local_maps",
                return_value=(status_map, status_map),
            ),
        ):
            payload = replay_one(source, fixture, "q10-unit")
        self.assertTrue(payload["implementation_valid"])
        self.assertTrue(all(payload["implementation_checks"].values()))
        self.assertEqual(
            payload["start_reconciliation_receipt"]["client_start_invocations"],
            1,
        )
        self.assertFalse(
            payload["start_reconciliation_receipt"]["second_start_invoked"]
        )
        self.assertTrue(payload["cleanup_receipt"]["accepted"])
        self.assertEqual(payload["model_calls"], payload["provider_calls"])
        self.assertEqual(payload["model_calls"], 0)


if __name__ == "__main__":
    unittest.main()
