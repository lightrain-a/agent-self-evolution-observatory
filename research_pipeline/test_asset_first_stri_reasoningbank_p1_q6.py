from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from research_pipeline.asset_first_stri_reasoningbank_p1_core import DockerRun, write_json
from research_pipeline.asset_first_stri_reasoningbank_p1_q6_prepare import CONTRACT
from research_pipeline.asset_first_stri_reasoningbank_p1_q6_runtime import (
    Q6_CONTRACT_SHA256, ReconciledDockerRun,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q6_smoke import (
    generate_authority,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_core import sha256_file


class ReasoningBankP1Q6RepairTest(unittest.TestCase):
    def test_q6_contract_is_exact_and_single_variable(self) -> None:
        self.assertEqual(sha256_file(CONTRACT), Q6_CONTRACT_SHA256)
        payload = json.loads(CONTRACT.read_text(encoding="utf-8"))
        repair = payload["single_variable_repair"]
        self.assertEqual(repair["variable"], "Docker create acknowledgement reconciliation")
        self.assertTrue(repair["docker_create_command_unchanged"])
        self.assertTrue(repair["evaluator_command_unchanged_from_q5"])
        self.assertEqual(repair["model_calls"], repair["provider_calls"])
        self.assertEqual(repair["model_calls"], 0)

    @patch.object(DockerRun, "start")
    def test_normal_create_receipt_remains_valid(self, parent_start: Mock) -> None:
        parent_start.return_value = {
            "image_inspect": {"returncode": 0, "output": "digest amd64"},
            "base_commit_receipt": {"observed_head": "a" * 40},
        }
        run = ReconciledDockerRun("image", "a" * 40, "normal", exact_base=True)
        receipt = run.start()["q6_create_acknowledgement"]
        self.assertFalse(receipt["repair_invoked"])
        self.assertTrue(receipt["normal_create_receipt_accepted"])

    @patch.object(DockerRun, "start", side_effect=RuntimeError("docker create failed: "))
    @patch(
        "research_pipeline.asset_first_stri_reasoningbank_p1_q6_runtime.run_host"
    )
    def test_timeout_accepts_only_exact_created_side_effect(
        self, run_host: Mock, _parent_start: Mock,
    ) -> None:
        image = "image@sha256:digest"
        run_host.side_effect = [
            {"returncode": 0, "output": "digest amd64", "timed_out": False},
            {
                "returncode": 0,
                "output": json.dumps([{
                    "Id": "f" * 64,
                    "Name": "/e1-rb-timeout-fixed",
                    "State": {"Status": "created", "Running": False},
                    "Config": {
                        "Image": image,
                        "Entrypoint": ["sleep"],
                        "Cmd": ["infinity"],
                    },
                    "HostConfig": {"PidMode": "host"},
                }]),
                "timed_out": False,
            },
            {"returncode": 0, "output": "started", "timed_out": False},
        ]
        run = ReconciledDockerRun(image, "a" * 40, "timeout", exact_base=True)
        run.name = "e1-rb-timeout-fixed"
        run.exec = Mock(side_effect=[
            {"returncode": 0, "output": "b" * 40},
            {"returncode": 0, "output": "HEAD reset"},
            {"returncode": 0, "output": "a" * 40},
        ])
        receipt = run.start()
        self.assertTrue(receipt["q6_create_acknowledgement"]["repair_invoked"])
        self.assertTrue(
            receipt["q6_create_acknowledgement"]["exact_side_effect_verified"]
        )
        self.assertTrue(run.created)
        run.created = False

    def test_q6_authority_requires_passing_smoke(self) -> None:
        checks = {
            "S1_per_test_result_lines": True,
            "S2_official_status_map_nonempty": True,
            "S3_official_local_parser_exact": True,
            "S4_only_reporting_verbosity_changed": True,
            "S5_no_model_or_provider_call": True,
            "S6_evaluator_terminated_normally": True,
            "S7_container_create_receipt_qualified": True,
            "fresh_exact_digest_container": True,
            "exact_base_normalization": True,
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            smoke = root / "q6-smoke.json"
            authority = root / "q6-authority.json"
            write_json(smoke, {
                "decision": "Q6_RUNTIME_AND_EVALUATOR_SMOKE_PASS",
                "pass": True,
                "checks": checks,
                "runtime_start": {
                    "q6_create_acknowledgement": {
                        "contract_sha256": Q6_CONTRACT_SHA256
                    }
                },
            })
            result = generate_authority(smoke, authority)
            self.assertTrue(result["q5_replay_execution_authorized"])
            self.assertTrue(authority.exists())


if __name__ == "__main__":
    unittest.main()
