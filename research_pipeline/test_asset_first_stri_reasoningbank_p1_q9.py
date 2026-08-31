from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from research_pipeline.asset_first_stri_reasoningbank_p1_core import sha256_file, write_json
from research_pipeline.asset_first_stri_reasoningbank_p1_q9_prepare import CONTRACT
from research_pipeline.asset_first_stri_reasoningbank_p1_q9_runtime import (
    Q9_CONTRACT_SHA256, ExtendedStartGraceDockerRun,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q9_smoke import generate_authority


class ReasoningBankP1Q9RepairTest(unittest.TestCase):
    def test_q9_contract_and_timeout_are_exact(self) -> None:
        self.assertEqual(sha256_file(CONTRACT), Q9_CONTRACT_SHA256)
        payload = json.loads(CONTRACT.read_text(encoding="utf-8"))
        repair = payload["single_variable_repair"]
        self.assertEqual(repair["before_seconds"], 180)
        self.assertEqual(repair["after_seconds"], 600)
        self.assertTrue(repair["docker_create_and_inspect_unchanged"])
        self.assertEqual(ExtendedStartGraceDockerRun.START_TIMEOUT_SECONDS, 600)
        self.assertEqual(
            ExtendedStartGraceDockerRun.ACK_CONTRACT_SHA256, Q9_CONTRACT_SHA256
        )

    def test_q9_authority_requires_passing_smoke(self) -> None:
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
            smoke = root / "q9-smoke.json"
            authority = root / "q9-authority.json"
            write_json(smoke, {
                "decision": "Q9_RUNTIME_AND_EVALUATOR_SMOKE_PASS",
                "pass": True,
                "checks": checks,
                "runtime_start": {
                    "q6_create_acknowledgement": {
                        "contract_sha256": Q9_CONTRACT_SHA256
                    }
                },
            })
            result = generate_authority(smoke, authority)
            self.assertTrue(result["q5_replay_execution_authorized"])


if __name__ == "__main__":
    unittest.main()
