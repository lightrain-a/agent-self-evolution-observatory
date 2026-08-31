"""Persist the deterministic Q10 T1-T10 fault-injection gate."""

from __future__ import annotations

import io
import json
import unittest
from pathlib import Path
from typing import Iterable

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT, sha256_file, utcnow, write_json,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_prepare import CONTRACT
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_runtime import (
    Q10_CONTRACT_SHA256,
)

OUTPUT = ROOT / "generated/asset-first-stri-reasoningbank-p1-q10-fault-tests-20260831.json"
MODULE = "research_pipeline.test_asset_first_stri_reasoningbank_p1_q10_runtime"
EXPECTED_TESTS = {
    "test_t1_normal_success": "T1",
    "test_t2_timeout_daemon_running": "T2",
    "test_t3_timeout_daemon_created_holds": "T3",
    "test_t4_timeout_daemon_exited_holds": "T4",
    "test_t5_timeout_daemon_restarting_holds": "T5",
    "test_t6_wrong_container_identity_holds": "T6",
    "test_t7_wrong_image_pid_or_command_holds": "T7",
    "test_t8_explicit_error_is_hard_failure_without_reconciliation": "T8",
    "test_t9_reconciliation_inspect_timeout_holds_without_retry": "T9",
    "test_t10_cleanup_after_receipt_finalization": "T10",
}


def flatten(suite: unittest.TestSuite) -> Iterable[unittest.TestCase]:
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


def run_fault_gate(output: Path = OUTPUT) -> dict:
    if output.exists():
        raise RuntimeError(f"refusing to overwrite immutable Q10 fault gate: {output}")
    if sha256_file(CONTRACT) != Q10_CONTRACT_SHA256:
        raise RuntimeError("Q10 contract SHA drift")
    suite = unittest.defaultTestLoader.loadTestsFromName(MODULE)
    test_ids = [test.id().rsplit(".", 1)[-1] for test in flatten(suite)]
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromName(MODULE)
    )
    expected_exact = set(test_ids) == set(EXPECTED_TESTS)
    passed = bool(
        result.wasSuccessful()
        and result.testsRun == 10
        and expected_exact
    )
    payload = {
        "schema_version": 1,
        "experiment_id": "NON_SCIENTIFIC_Q10_DETERMINISTIC_FAULT_GATE-20260831",
        "created_at_utc": utcnow(),
        "q10_contract_sha256": Q10_CONTRACT_SHA256,
        "test_module": MODULE,
        "test_count": result.testsRun,
        "expected_test_ids_exact": expected_exact,
        "cases": [
            {"case": EXPECTED_TESTS[test_id], "test_id": test_id, "pass": passed}
            for test_id in sorted(test_ids, key=lambda name: int(EXPECTED_TESTS[name][1:]))
        ],
        "failures": [test.id() for test, _ in result.failures],
        "errors": [test.id() for test, _ in result.errors],
        "start_invocation_invariant": 1,
        "second_start_forbidden": True,
        "cleanup_after_receipt_finalization_tested": True,
        "model_calls": 0,
        "provider_calls": 0,
        "scientific_authority": False,
        "task_outcome_authority": False,
        "pass": passed,
        "decision": (
            "Q10_DETERMINISTIC_FAULT_GATE_PASS"
            if passed else "Q10_DETERMINISTIC_FAULT_GATE_HOLD"
        ),
        "credential_material_present": False,
    }
    file_sha = write_json(output, payload)
    return {
        "decision": payload["decision"],
        "pass": passed,
        "file_sha256": file_sha,
    }


def main() -> None:
    print(json.dumps(run_fault_gate(), sort_keys=True))


if __name__ == "__main__":
    main()
