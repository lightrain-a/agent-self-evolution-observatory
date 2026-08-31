from __future__ import annotations

import inspect
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from research_pipeline.asset_first_stri_reasoningbank_p1_core import write_json
from research_pipeline.asset_first_stri_reasoningbank_p1_q5_core import (
    CONTRACT_SHA256,
    EXPECTED_ORDER,
    fixture_by_id,
    official_and_local_maps,
    repaired_fixture,
    replay_one,
    verify_q5_contract,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q5_prepare import (
    SPHINX_AFTER,
    SPHINX_BEFORE,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q5_runner import (
    index_payload,
    run_q5,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q5_smoke import (
    generate_authority,
    run_smoke,
)


class ReasoningBankP1Q5StackTest(unittest.TestCase):
    def test_contract_and_all_source_hashes_are_exact(self) -> None:
        result = verify_q5_contract()
        self.assertTrue(result["pass"])
        self.assertEqual(result["contract_sha256"], CONTRACT_SHA256)
        self.assertEqual(len(result["source_checks"]), 10)
        self.assertTrue(all(row["pass"] for row in result["source_checks"]))

    def test_single_variable_repair_and_django_identity(self) -> None:
        fixtures = fixture_by_id()
        sphinx = fixtures["sphinx-doc__sphinx-9230"]
        django = fixtures["django__django-11880"]
        repaired_sphinx = repaired_fixture(sphinx)
        repaired_django = repaired_fixture(django)
        before = sphinx["evaluator_only"]["eval_script"]
        after = repaired_sphinx["evaluator_only"]["eval_script"]
        self.assertEqual(before.count(SPHINX_BEFORE), 1)
        self.assertEqual(after, before.replace(SPHINX_BEFORE, SPHINX_AFTER))
        self.assertEqual(
            repaired_django["evaluator_only"]["eval_script"],
            django["evaluator_only"]["eval_script"],
        )

    def test_official_and_local_parser_equivalence(self) -> None:
        raw = (
            "tests/test_domain_py.py::test_pass PASSED\n"
            "FAILED tests/test_domain_py.py::test_fail - details\n"
        )
        official, local = official_and_local_maps("parse_log_sphinx", raw)
        self.assertEqual(official, local)
        self.assertEqual(len(official), 2)

    def test_provider_model_path_is_unreachable(self) -> None:
        source = inspect.getsource(replay_one)
        self.assertNotIn("make_client", source)
        self.assertNotIn("execute_agent", source)
        self.assertNotIn("create_response", source)

    @patch(
        "research_pipeline.asset_first_stri_reasoningbank_p1_q5_runner.sha256_file",
        return_value="f" * 64,
    )
    def test_index_freezes_order_zero_calls_and_no_retry(self, _sha256_file) -> None:
        payload = index_payload([], [], False)
        self.assertEqual(payload["planned_order"], [list(row) for row in EXPECTED_ORDER])
        self.assertEqual(payload["planned_run_count"], 10)
        self.assertEqual(payload["model_calls"], payload["provider_calls"])
        self.assertEqual(payload["model_calls"], 0)
        self.assertEqual(payload["automatic_retry"], "forbidden")
        self.assertEqual(payload["replacement_sampling"], "forbidden")

    def test_second_runner_invocation_is_refused_before_work(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            index = root / "existing.json"
            index.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "second Q5 invocation"):
                run_q5(root / "runs", index)

    @patch(
        "research_pipeline.asset_first_stri_reasoningbank_p1_q5_smoke.DockerRun"
    )
    def test_failed_smoke_is_frozen_as_hold(self, docker_run) -> None:
        docker_run.return_value.start.side_effect = RuntimeError("synthetic")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "smoke.json"
            result = run_smoke(output)
            self.assertFalse(result["pass"])
            self.assertEqual(result["decision"], "Q5_EVALUATOR_VERBOSITY_SMOKE_HOLD")
            self.assertTrue(output.exists())

    def test_authority_opens_only_after_passing_smoke(self) -> None:
        checks = {
            "S1_per_test_result_lines": True,
            "S2_official_status_map_nonempty": True,
            "S3_official_local_parser_exact": True,
            "S4_only_reporting_verbosity_changed": True,
            "S5_no_model_or_provider_call": True,
            "S6_evaluator_terminated_normally": True,
            "fresh_exact_digest_container": True,
            "exact_base_normalization": True,
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            smoke = root / "smoke.json"
            authority = root / "authority.json"
            write_json(smoke, {
                "decision": "Q5_EVALUATOR_VERBOSITY_SMOKE_PASS",
                "pass": True,
                "checks": checks,
            })
            result = generate_authority(smoke, authority)
            self.assertTrue(result["q5_replay_execution_authorized"])
            self.assertTrue(authority.exists())


if __name__ == "__main__":
    unittest.main()
