from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from .reopened_experiment_lease import (
    ACTIVE_STATUS,
    acquire_reopened_experiment_lease,
    public_reopened_experiment_lease,
    publish_reopened_experiment_lease,
    validate_reopened_experiment_lease,
    validate_reopened_experiment_lease_ledger,
)
from .reopened_experiment_lease_request import build_experiment_lease_request
from .reopened_pre_experiment_adapter import compile_reopened_pre_experiment
from .test_reopened_pre_experiment_adapter import ReopenedPreExperimentAdapterTest


class ReopenedExperimentLeaseTest(unittest.TestCase):
    def fixture(self, root: Path):
        helper = ReopenedPreExperimentAdapterTest(methodName="test_compiler_pass_still_requires_experiment_lease")
        contract, blueprint, blueprint_review, local_auth = helper.fixture(root)
        runtime = helper.runtime()
        runtime["governance"]["substrate_evidence"] = "substrate-evidence.json"
        (root / "substrate-evidence.json").write_text(json.dumps({"pass": True}), encoding="utf-8")
        fake = {
            "status": "pass",
            "execution_authorized": True,
            "passed_gates": 8,
            "gate_count": 8,
            "blockers": [],
            "research_execution_plan": {"plan_hash": "7" * 64},
            "config_hash": "compiler-does-not-own-config-identity",
        }
        with patch("research_pipeline.reopened_pre_experiment_adapter.compile_pre_experiment_card", return_value=fake):
            pre = compile_reopened_pre_experiment(
                contract=contract,
                blueprint=blueprint,
                blueprint_review=blueprint_review,
                local_authorization=local_auth,
                runtime_supplement=runtime,
                data_root=root,
            )
        request = build_experiment_lease_request(pre_experiment_receipt=pre, local_authorization=local_auth)
        return contract, blueprint, blueprint_review, local_auth, runtime, pre, request

    def acquire(self, root: Path, *, run_id: str = "run-001", actor: str = "executor:local-f0"):
        contract, blueprint, review, local_auth, runtime, pre, request = self.fixture(root)
        receipt = acquire_reopened_experiment_lease(
            root=root,
            contract=contract,
            blueprint=blueprint,
            blueprint_review=review,
            local_authorization=local_auth,
            pre_experiment_receipt=pre,
            lease_request=request,
            runtime_supplement=runtime,
            actor=actor,
            run_id=run_id,
            external_execution_authority_ref="human:explicit-local-f0-execution-authority",
        )
        return contract, runtime, receipt

    def test_acquire_rechecks_governance_and_creates_single_writer_lease_without_starting_run(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            contract, _, receipt = self.acquire(root)
            self.assertTrue(validate_reopened_experiment_lease(receipt))
            self.assertEqual(receipt["status"], ACTIVE_STATUS)
            self.assertTrue(receipt["experiment_authority_acquired"])
            self.assertTrue(receipt["execution_authorized"])
            self.assertFalse(receipt["execution_started"])
            self.assertFalse(receipt["model_loaded"])
            self.assertFalse(receipt["gpu_allocated"])
            self.assertEqual(receipt["governance_stage"], "f0-identifiability")
            self.assertTrue((root / "experiment-authority" / f"{contract['contract_id']}.json").exists())
            self.assertFalse((root / "runs").exists())

    def test_runtime_config_drift_after_pre_experiment_is_blocked_before_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            contract, blueprint, review, local_auth, runtime, pre, request = self.fixture(root)
            runtime["scope"]["max_steps"] = 11
            with self.assertRaisesRegex(RuntimeError, "runtime supplement/config drift"):
                acquire_reopened_experiment_lease(
                    root=root,
                    contract=contract,
                    blueprint=blueprint,
                    blueprint_review=review,
                    local_authorization=local_auth,
                    pre_experiment_receipt=pre,
                    lease_request=request,
                    runtime_supplement=runtime,
                    actor="executor",
                    run_id="run-drift",
                    external_execution_authority_ref="human:authority",
                )
            self.assertFalse((root / "experiment-authority").exists())

    def test_governance_recheck_blocks_if_predecessor_evidence_disappears(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            contract, blueprint, review, local_auth, runtime, pre, request = self.fixture(root)
            (root / "substrate-evidence.json").unlink()
            with self.assertRaisesRegex(RuntimeError, "governance stage blocks"):
                acquire_reopened_experiment_lease(
                    root=root,
                    contract=contract,
                    blueprint=blueprint,
                    blueprint_review=review,
                    local_authorization=local_auth,
                    pre_experiment_receipt=pre,
                    lease_request=request,
                    runtime_supplement=runtime,
                    actor="executor",
                    run_id="run-no-predecessor",
                    external_execution_authority_ref="human:authority",
                )
            self.assertFalse((root / "experiment-authority").exists())

    def test_second_run_for_same_contract_is_rejected_by_existing_single_writer_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            contract, blueprint, review, local_auth, runtime, pre, request = self.fixture(root)
            first = acquire_reopened_experiment_lease(
                root=root,
                contract=contract,
                blueprint=blueprint,
                blueprint_review=review,
                local_authorization=local_auth,
                pre_experiment_receipt=pre,
                lease_request=request,
                runtime_supplement=runtime,
                actor="executor-A",
                run_id="run-A",
                external_execution_authority_ref="human:authority-A",
            )
            self.assertTrue(first["experiment_authority_acquired"])
            with self.assertRaisesRegex(RuntimeError, "experiment authority already active"):
                acquire_reopened_experiment_lease(
                    root=root,
                    contract=contract,
                    blueprint=blueprint,
                    blueprint_review=review,
                    local_authorization=local_auth,
                    pre_experiment_receipt=pre,
                    lease_request=request,
                    runtime_supplement=runtime,
                    actor="executor-B",
                    run_id="run-B",
                    external_execution_authority_ref="human:authority-B",
                )

    def test_receipt_tamper_is_detected_and_public_summary_redacts_private_execution_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            contract, _, receipt = self.acquire(root)
            bad = copy.deepcopy(receipt)
            bad["gpu_allocated"] = True
            self.assertFalse(validate_reopened_experiment_lease(bad))
            publish_reopened_experiment_lease(root, receipt)
            public = public_reopened_experiment_lease(root, contract["contract_id"])
            self.assertEqual(public["status"], ACTIVE_STATUS)
            self.assertTrue(public["experiment_authority_acquired"])
            self.assertTrue(public["execution_authorized"])
            self.assertFalse(public["execution_started"])
            self.assertFalse(public["gpu_allocated"])
            text = json.dumps(public, sort_keys=True)
            self.assertNotIn("human:explicit-local-f0-execution-authority", text)
            self.assertNotIn("external_execution_authority_ref", text)

    def test_publish_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, _, receipt = self.acquire(root)
            first = publish_reopened_experiment_lease(root, receipt)
            second = publish_reopened_experiment_lease(root, receipt)
            self.assertEqual(len(first["events"]), 1)
            self.assertEqual(len(second["events"]), 1)
            self.assertEqual(validate_reopened_experiment_lease_ledger(second), [])

    def test_ledger_tamper_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            contract, _, receipt = self.acquire(root)
            ledger = publish_reopened_experiment_lease(root, receipt)
            bad = copy.deepcopy(ledger)
            bad["events"][0]["receipt"]["run_id"] = "tampered-run"
            self.assertIn("experiment-lease-receipt-invalid", validate_reopened_experiment_lease_ledger(bad))
            path = root / "scientific-contract-experiment-leases" / f"{contract['contract_id']}.json"
            path.write_text(json.dumps(bad), encoding="utf-8")
            public = public_reopened_experiment_lease(root, contract["contract_id"])
            self.assertEqual(public["status"], "EXPERIMENT_LEASE_LEDGER_INVALID")


if __name__ == "__main__":
    unittest.main()
