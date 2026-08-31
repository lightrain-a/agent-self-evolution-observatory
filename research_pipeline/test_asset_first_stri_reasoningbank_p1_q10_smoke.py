from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from research_pipeline.asset_first_stri_reasoningbank_p1_q10_runtime import (
    Q10_CONTRACT_SHA256,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_smoke import (
    RECEIPT_FIELDS, run_smoke,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q5_core import fixture_by_id
from research_pipeline.asset_first_stri_reasoningbank_p1_q5_prepare import load_payload


class FakeContainer:
    def __init__(self, cleanup_ok: bool = True) -> None:
        self.fixture = fixture_by_id()["sphinx-doc__sphinx-9230"]
        self.exec_count = 0
        self.cleanup_ok = cleanup_ok
        self.start_reconciliation_receipt = {
            key: None for key in RECEIPT_FIELDS
        }
        self.start_reconciliation_receipt.update({
            "client_start_invocations": 1,
            "client_returncode": 0,
            "client_timed_out": False,
            "client_output": "name",
            "reconciliation_invoked": False,
            "docker_inspect_invoked": True,
            "container_id": "b" * 64,
            "container_name": "/q10-smoke",
            "expected_image": self.fixture["image_pull_reference"],
            "observed_image": self.fixture["image_pull_reference"],
            "expected_image_digest": self.fixture["image_amd64_manifest_digest"],
            "observed_image_digests": [
                "image@" + self.fixture["image_amd64_manifest_digest"]
            ],
            "expected_pid_mode": "host",
            "observed_pid_mode": "host",
            "daemon_status": "running",
            "daemon_running": True,
            "daemon_pid": 42,
            "restart_count": 0,
            "exact_identity_verified": True,
            "exact_running_state_verified": True,
            "second_start_invoked": False,
            "accepted": True,
            "acceptance_rule": "normal_client_acknowledgement_with_exact_post_start_state",
            "receipt_finalized": True,
            "contract_sha256": Q10_CONTRACT_SHA256,
        })

    def start(self) -> dict:
        return {
            "image_inspect": {"output": self.fixture["image_amd64_manifest_digest"]},
            "base_commit_receipt": {
                "observed_head": self.fixture["model_visible"]["base_commit"],
                "rule": "exact_base_after_preregistered_hard_reset",
            },
            "q6_create_acknowledgement": {
                "client_create_invocations": 1,
                "second_create_invoked": False,
                "accepted": True,
            },
            "q10_start_reconciliation": self.start_reconciliation_receipt,
        }

    def exec(self, action: str, *, timeout: int | float) -> dict:
        self.exec_count += 1
        output = (
            self.fixture["model_visible"]["base_commit"] + "\n"
            if self.exec_count == 1
            else "Q10_DAEMON_STATE_RECONCILIATION_EXEC_OK"
        )
        return {"returncode": 0, "timed_out": False, "output": output}

    def close(self) -> dict:
        return {
            "cleanup_invoked": True,
            "reconciliation_receipt_finalized_before_cleanup": True,
            "accepted": self.cleanup_ok,
        }


class ReasoningBankP1Q10SmokeTest(unittest.TestCase):
    def run_with_fake(self, fake: FakeContainer) -> dict:
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "smoke.json"
            with patch(
                "research_pipeline.asset_first_stri_reasoningbank_p1_q10_smoke."
                "DaemonReconciledDockerRun",
                return_value=fake,
            ):
                run_smoke(output)
            return load_payload(output)

    def test_smoke_pass_requires_complete_exact_receipts(self) -> None:
        payload = self.run_with_fake(FakeContainer())
        self.assertEqual(payload["decision"], "Q10_DAEMON_STATE_RECONCILIATION_SMOKE_PASS")
        self.assertTrue(payload["pass"])
        self.assertTrue(all(payload["checks"].values()))
        self.assertEqual(payload["model_calls"], payload["provider_calls"])
        self.assertEqual(payload["model_calls"], 0)

    def test_cleanup_failure_holds(self) -> None:
        payload = self.run_with_fake(FakeContainer(cleanup_ok=False))
        self.assertEqual(payload["decision"], "Q10_DAEMON_STATE_RECONCILIATION_SMOKE_HOLD")
        self.assertFalse(payload["pass"])
        self.assertFalse(payload["checks"]["cleanup_after_receipt_finalization"])


if __name__ == "__main__":
    unittest.main()
