from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from research_pipeline.asset_first_stri_reasoningbank_p1_core import sha256_file, write_json
from research_pipeline.asset_first_stri_reasoningbank_p1_q8_prepare import CONTRACT
from research_pipeline.asset_first_stri_reasoningbank_p1_q8_runtime import (
    Q8_CONTRACT_SHA256, StartGraceDockerRun,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q8_smoke import generate_authority


class ReasoningBankP1Q8RepairTest(unittest.TestCase):
    def test_q8_contract_and_timeout_are_exact(self) -> None:
        self.assertEqual(sha256_file(CONTRACT), Q8_CONTRACT_SHA256)
        payload = json.loads(CONTRACT.read_text(encoding="utf-8"))
        repair = payload["single_variable_repair"]
        self.assertEqual(repair["before_seconds"], 60)
        self.assertEqual(repair["after_seconds"], 180)
        self.assertTrue(repair["docker_create_and_inspect_unchanged"])
        self.assertEqual(StartGraceDockerRun.START_TIMEOUT_SECONDS, 180)
        self.assertEqual(
            StartGraceDockerRun.ACK_CONTRACT_SHA256, Q8_CONTRACT_SHA256
        )

    def test_q8_authority_requires_passing_smoke(self) -> None:
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
            smoke = root / "q8-smoke.json"
            authority = root / "q8-authority.json"
            write_json(smoke, {
                "decision": "Q8_RUNTIME_AND_EVALUATOR_SMOKE_PASS",
                "pass": True,
                "checks": checks,
                "runtime_start": {
                    "q6_create_acknowledgement": {
                        "contract_sha256": Q8_CONTRACT_SHA256
                    }
                },
            })
            result = generate_authority(smoke, authority)
            self.assertTrue(result["q5_replay_execution_authorized"])


if __name__ == "__main__":
    unittest.main()
