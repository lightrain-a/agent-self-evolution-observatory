from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from .experiment_authority import acquire_authority, release_authority
from .resource_lease import acquire_gpu_lease, release_gpu_lease
from .reopened_experiment_lease import acquire_reopened_experiment_lease
from .reopened_local_f0_run import (
    ACTIVE_STATUS,
    STALE_STATUS,
    public_reopened_local_f0_run,
    start_and_publish_reopened_local_f0_run,
    start_reopened_local_f0_run,
    validate_reopened_local_f0_run_start,
    validate_run_start_ledger,
)
from .test_reopened_experiment_lease import ReopenedExperimentLeaseTest


class ReopenedLocalF0RunTest(unittest.TestCase):
    def fixture(self, root: Path, *, run_id: str = "run-f0-001"):
        helper = ReopenedExperimentLeaseTest(methodName="test_acquire_rechecks_governance_and_creates_single_writer_lease_without_starting_run")
        contract, blueprint, review, local_auth, runtime, pre, request = helper.fixture(root)
        lease = acquire_reopened_experiment_lease(
            root=root,
            contract=contract,
            blueprint=blueprint,
            blueprint_review=review,
            local_authorization=local_auth,
            pre_experiment_receipt=pre,
            lease_request=request,
            runtime_supplement=runtime,
            actor="executor:test-local-f0",
            run_id=run_id,
            external_execution_authority_ref="human:private-run-authority",
        )
        return contract, local_auth, pre, request, lease

    def start_kwargs(self, root: Path, *, run_root: Path | None = None, gpu_uuid: str = "GPU-TEST-001") -> dict:
        contract, local_auth, pre, request, lease = self.fixture(root)
        return {
            "root": root,
            "experiment_lease": lease,
            "lease_request": request,
            "pre_experiment_receipt": pre,
            "local_authorization": local_auth,
            "server_id": "server-test",
            "gpu_uuid": gpu_uuid,
            "owner": "executor:test-local-f0",
            "ttl_minutes": 30,
            "run_root": run_root or (root / "runs" / "run-f0-001"),
            "model_name": "Qwen-Test",
            "model_revision": "test-revision-001",
        }

    def test_start_acquires_resource_lease_and_creates_run_root_without_scientific_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            kwargs = self.start_kwargs(root)
            receipt, ledger = start_and_publish_reopened_local_f0_run(**kwargs)
            self.assertTrue(validate_reopened_local_f0_run_start(receipt))
            self.assertEqual(validate_run_start_ledger(ledger), [])
            self.assertEqual(receipt["status"], ACTIVE_STATUS)
            self.assertTrue(receipt["execution_started"])
            self.assertTrue(receipt["gpu_allocated"])
            self.assertTrue(receipt["model_load_authorized"])
            self.assertFalse(receipt["model_loaded"])
            self.assertFalse(receipt["scientific_authority"])
            self.assertFalse(receipt["p0_authority"])
            self.assertFalse(receipt["full_experiment_authority"])
            marker = Path(receipt["run_root"]) / "run-start.json"
            self.assertTrue(marker.is_file())
            public = public_reopened_local_f0_run(root, receipt["contract_id"])
            self.assertEqual(public["status"], ACTIVE_STATUS)
            self.assertTrue(public["experiment_authority_active"])
            self.assertTrue(public["resource_lease_active"])
            self.assertTrue(public["execution_started"])
            self.assertFalse(public["model_loaded"])

    def test_same_start_is_idempotent_but_same_experiment_lease_cannot_change_run_surface(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            kwargs = self.start_kwargs(root)
            first, ledger1 = start_and_publish_reopened_local_f0_run(**kwargs)
            second, ledger2 = start_and_publish_reopened_local_f0_run(**kwargs)
            self.assertEqual(first["run_start_sha256"], second["run_start_sha256"])
            self.assertEqual(len(ledger1["events"]), 1)
            self.assertEqual(len(ledger2["events"]), 1)
            changed = dict(kwargs); changed["run_root"] = root / "runs" / "different-root"
            with self.assertRaisesRegex(RuntimeError, "different formal run start"):
                start_and_publish_reopened_local_f0_run(**changed)

    def test_ttl_cannot_exceed_human_authorized_gpu_hour_cap(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); kwargs = self.start_kwargs(root); kwargs["ttl_minutes"] = 121
            with self.assertRaisesRegex(RuntimeError, "TTL exceeds"):
                start_reopened_local_f0_run(**kwargs)
            self.assertFalse((root / "resource-leases").exists())

    def test_model_mismatch_is_blocked_before_resource_lease(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); kwargs = self.start_kwargs(root); kwargs["model_name"] = "Wrong-Model"
            with self.assertRaisesRegex(RuntimeError, "model does not match"):
                start_reopened_local_f0_run(**kwargs)
            self.assertFalse((root / "resource-leases").exists())

    def test_nonempty_or_git_nested_run_root_is_blocked_before_resource_lease(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); nonempty = root / "runs" / "nonempty"; nonempty.mkdir(parents=True); (nonempty / "x").write_text("x")
            kwargs = self.start_kwargs(root, run_root=nonempty)
            with self.assertRaisesRegex(RuntimeError, "must be new"):
                start_reopened_local_f0_run(**kwargs)
            self.assertFalse((root / "resource-leases").exists())
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); checkout = root / "checkout"; checkout.mkdir(); (checkout / ".git").write_text("gitdir: elsewhere")
            kwargs = self.start_kwargs(root, run_root=checkout / "nested" / "run")
            with self.assertRaisesRegex(RuntimeError, "outside every git checkout"):
                start_reopened_local_f0_run(**kwargs)

    def test_gpu_resource_conflict_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); kwargs = self.start_kwargs(root)
            other = acquire_authority(root, "other-idea", "o" * 64, "other-executor", "local-f0", "other-run")
            acquire_gpu_lease(root, "server-test", "GPU-TEST-001", "other-run", "other-executor", idea_id="other-idea", authority_id=other["authority_id"], plan_hash="o" * 64, ttl_minutes=30)
            with self.assertRaisesRegex(RuntimeError, "GPU lease already active"):
                start_reopened_local_f0_run(**kwargs)

    def test_releasing_gpu_or_experiment_lease_makes_public_run_stale(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); kwargs = self.start_kwargs(root); receipt, _ = start_and_publish_reopened_local_f0_run(**kwargs)
            release_gpu_lease(root, receipt["server_id"], receipt["gpu_uuid"], receipt["gpu_lease_id"], idea_id=receipt["contract_id"], authority_id=receipt["experiment_authority_id"], plan_hash=receipt["plan_hash"], outcome="test-release")
            public = public_reopened_local_f0_run(root, receipt["contract_id"])
            self.assertEqual(public["status"], STALE_STATUS)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); kwargs = self.start_kwargs(root); receipt, _ = start_and_publish_reopened_local_f0_run(**kwargs)
            release_authority(root, receipt["contract_id"], receipt["experiment_authority_id"], "test-release")
            public = public_reopened_local_f0_run(root, receipt["contract_id"])
            self.assertEqual(public["status"], STALE_STATUS)

    def test_tamper_and_public_redaction(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); kwargs = self.start_kwargs(root); receipt, ledger = start_and_publish_reopened_local_f0_run(**kwargs)
            bad = copy.deepcopy(receipt); bad["gpu_uuid"] = "GPU-TAMPER"
            self.assertFalse(validate_reopened_local_f0_run_start(bad))
            bad_ledger = copy.deepcopy(ledger); bad_ledger["events"][0]["receipt"]["model_revision"] = "tampered"
            self.assertIn("run-start-receipt-invalid", validate_run_start_ledger(bad_ledger))
            public = public_reopened_local_f0_run(root, receipt["contract_id"])
            text = json.dumps(public, sort_keys=True)
            for private in ("server-test", "GPU-TEST-001", str(receipt["run_root"]), "human:private-run-authority"):
                self.assertNotIn(private, text)
            self.assertTrue(public["server_gpu_binding_sha256"])


if __name__ == "__main__":
    unittest.main()
