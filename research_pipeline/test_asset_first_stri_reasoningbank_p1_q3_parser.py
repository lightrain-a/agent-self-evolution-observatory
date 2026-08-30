from __future__ import annotations

import json
import unittest

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    canonical_json,
    sha256_text,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_eval import (
    evaluate,
    parse_django,
    parse_pytest_v2,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q3_parser_qualification import (
    OUTPUT,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q3_prepare import CONTRACT


class FakeContainer:
    def __init__(self, output: str) -> None:
        self.output = output

    def exec(self, command: str, *, timeout: int) -> dict:
        return {
            "command": command,
            "output": self.output,
            "returncode": 0,
            "timed_out": False,
        }


class ReasoningBankP1Q3ParserTest(unittest.TestCase):
    def test_django_matches_official_status_forms(self) -> None:
        log = """--version is equivalent to version
pkg.TestCase.test_ok ... ok
pkg.TestCase.test_upper ... OK
pkg.TestCase.test_spaced ...  OK
pkg.TestCase.test_skip ... skipped 'reason'
pkg.TestCase.test_fail ... FAIL
FAIL: pkg.TestCase.test_fail_header (pkg.TestCase)
pkg.TestCase.test_error ... ERROR
ERROR: pkg.TestCase.test_error_header (pkg.TestCase)
pkg.TestCase.test_multiline ... Internal Server Error: /example/
ok
"""
        self.assertEqual(
            parse_django(log),
            {
                "--version is equivalent to version": "PASSED",
                "pkg.TestCase.test_ok": "PASSED",
                "pkg.TestCase.test_upper": "PASSED",
                "pkg.TestCase.test_spaced": "PASSED",
                "pkg.TestCase.test_skip": "SKIPPED",
                "pkg.TestCase.test_fail": "FAILED",
                "pkg.TestCase.test_fail_header": "FAILED",
                "pkg.TestCase.test_error": "ERROR",
                "pkg.TestCase.test_error_header": "ERROR",
                "pkg.TestCase.test_multiline": "PASSED",
            },
        )

    def test_sphinx_matches_official_pytest_v2_forms(self) -> None:
        log = """\x1b[32mPASSED\x1b[0m docs/test_build.py::test_new
FAILED docs/test_build.py::test_fail - AssertionError: details
SKIPPED [2] docs/test_build.py:12: optional
docs/test_old.py::test_legacy PASSED
docs/test_old.py::test_skip SKIPPED
"""
        self.assertEqual(
            parse_pytest_v2(log),
            {
                "docs/test_build.py::test_new": "PASSED",
                "docs/test_build.py::test_fail": "FAILED",
                "docs/test_old.py::test_legacy": "PASSED",
                "docs/test_old.py::test_skip": "SKIPPED",
            },
        )

    def test_frozen_official_conformance_receipt_is_valid(self) -> None:
        receipt = json.loads(OUTPUT.read_text(encoding="utf-8"))
        expected_payload_sha = receipt.pop("payload_sha256")
        self.assertEqual(expected_payload_sha, sha256_text(canonical_json(receipt)))
        self.assertEqual(receipt["decision"], "P1_Q3_PARSERS_QUALIFIED")
        self.assertTrue(receipt["all_cases_exact"])
        self.assertEqual(receipt["case_count"], 14)
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual(
            receipt["source"]["wheel_sha256"],
            contract["bindings"]["swebench_wheel_sha256"],
        )
        self.assertEqual(
            receipt["source"]["function_source_sha256"],
            {
                row["official_callable"]: row["source_sha256"]
                for row in contract["bindings"]["official_parser_source"].values()
            },
        )

    def test_evaluate_dispatches_django_and_sphinx(self) -> None:
        cases = (
            (
                "parse_log_django",
                "pkg.TestCase.test_fix ... ok",
                "pkg.TestCase.test_fix",
            ),
            (
                "parse_log_sphinx",
                "PASSED docs/test_build.py::test_fix",
                "docs/test_build.py::test_fix",
            ),
        )
        for parser_name, line, test_name in cases:
            with self.subTest(parser=parser_name):
                output = (
                    ">>>>> Start Test Output\n"
                    + line
                    + "\n>>>>> End Test Output\n"
                )
                fixture = {
                    "evaluator_only": {
                        "eval_script": "run frozen evaluator",
                        "log_parser": parser_name,
                        "FAIL_TO_PASS": [test_name],
                        "PASS_TO_PASS": [],
                        "test_patch": "frozen patch",
                    }
                }
                result = evaluate(FakeContainer(output), fixture)
                self.assertTrue(result["valid"])
                self.assertTrue(result["resolved"])
                self.assertEqual(result["status_map"][test_name], "PASSED")


if __name__ == "__main__":
    unittest.main()
