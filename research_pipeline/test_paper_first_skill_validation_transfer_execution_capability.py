from __future__ import annotations

import copy
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from .experiment_authority import acquire_authority, release_authority
from .paper_first_skill_validation_transfer_execution_capability import (
    build_execution_capability,
    load_execution_capability,
    validate_execution_capability_receipt,
    write_execution_capability,
)
from .paper_first_skill_validation_transfer_f0 import CANDIDATE_ID, CONTRACT_VERSION, SOURCE_COMMIT, build_plan
from .paper_first_skill_validation_transfer_f0_authority import (
    AUTHORITY_TYPE,
    EXPECTED_F0_HARNESS_SHA256,
    EXPECTED_RUNTIME_CONTRACT_SHA256,
    EXPECTED_SOURCE_TREE_SHA256,
    SERVER_ID,
    load_human_authority,
)
from .paper_first_skill_validation_transfer_runtime_audit import DEFAULT_JSON as RUNTIME_AUDIT_JSON, validate_runtime_audit


def _audit_sha(state: dict) -> str:
    raw = json.dumps(
        {k: v for k, v in state.items() if k != "audit_sha256"},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


class SkillValidationTransferExecutionCapabilityTest(unittest.TestCase):
    def authority_payload(self) -> dict:
        return {
            "authority_type": AUTHORITY_TYPE,
            "decision": "approve",
            "reviewed_by": "human-user",
            "reviewed_at": "2026-08-17T16:00:00+08:00",
            "source_message_ref": "conversation-explicit-pa05-f0-approval",
            "source_message_sha256": hashlib.sha256(b"explicit PA-05 F0 approval").hexdigest(),
            "candidate_id": CANDIDATE_ID,
            "contract_version": CONTRACT_VERSION,
            "plan_sha256": build_plan()["plan_sha256"],
            "f0_harness_sha256": EXPECTED_F0_HARNESS_SHA256,
            "runtime_contract_sha256": EXPECTED_RUNTIME_CONTRACT_SHA256,
            "source_tree_sha256": EXPECTED_SOURCE_TREE_SHA256,
            "source_commit": SOURCE_COMMIT,
            "server_id": SERVER_ID,
            "bounded_f0_execution_authorized": True,
            "api_docker_execution_authorized": True,
            "provider_credential_use_authorized": True,
            "gpu_lease_authorized": False,
            "single_attempt": True,
            "provider_price_rechecked_at_review": True,
            "provider_price_source": "official-provider-pricing-checked-at-review",
            "problem_gate_authorized": False,
            "paper_design_authorized": False,
            "method_authorized": False,
            "p0_authorized": False,
            "full_experiment_authorized": False,
        }

    def external_authority(self) -> tuple[Path, dict]:
        root = Path(tempfile.mkdtemp(prefix="pa05-cap-authority-"))
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        path = root / "authority.json"
        path.write_text(json.dumps(self.authority_payload(), indent=2) + "\n", encoding="utf-8")
        return path, load_human_authority(path)

    def control_root(self) -> Path:
        root = Path(tempfile.mkdtemp(prefix="pa05-cap-control-"))
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def runtime(self, *, credential_ready: bool) -> dict:
        state = copy.deepcopy(json.loads(RUNTIME_AUDIT_JSON.read_text(encoding="utf-8")))
        state["credentials"]["GEMINI_API_KEY_present"] = credential_ready
        state["provider_credential_ready"] = credential_ready
        state["execution_ready"] = bool(state["runtime_infrastructure_ready"] and credential_ready)
        state["hold_reason"] = [] if state["execution_ready"] else ["GEMINI_API_KEY not loaded in the current execution environment"]
        state["audit_sha256"] = _audit_sha(state)
        self.assertEqual([], validate_runtime_audit(state))
        return state

    def experiment_authority(self, root: Path, run_id: str) -> dict:
        return acquire_authority(
            root,
            CANDIDATE_ID,
            build_plan()["plan_sha256"],
            "pa05-test-controller",
            "fresh-phenomenon-f0",
            run_id,
        )

    def test_missing_credential_cannot_be_controller_verified(self) -> None:
        _, human = self.external_authority()
        root = self.control_root()
        run_id = "pa05-seed-a-demo"
        experiment = self.experiment_authority(root, run_id)
        try:
            state = build_execution_capability(
                human_authority=human,
                runtime_audit=self.runtime(credential_ready=False),
                run_id=run_id,
                authority_root=root,
                experiment_authority_id=experiment["authority_id"],
            )
            self.assertFalse(state["valid"])
            self.assertFalse(state["controller_verified"])
            self.assertIn("provider-credential-not-ready", state["errors"])
            self.assertEqual([], validate_execution_capability_receipt(state))
        finally:
            release_authority(root, CANDIDATE_ID, experiment["authority_id"], "test-done")

    def test_valid_capability_requires_human_runtime_credential_and_active_controller_authority(self) -> None:
        _, human = self.external_authority()
        root = self.control_root()
        run_id = "pa05-seed-a-demo"
        experiment = self.experiment_authority(root, run_id)
        try:
            state = build_execution_capability(
                human_authority=human,
                runtime_audit=self.runtime(credential_ready=True),
                run_id=run_id,
                authority_root=root,
                experiment_authority_id=experiment["authority_id"],
            )
            self.assertTrue(state["valid"])
            self.assertTrue(state["controller_verified"])
            self.assertEqual(experiment["authority_id"], state["authority_id"])
            self.assertEqual("api_docker", state["execution_kind"])
            self.assertFalse(state["requires_gpu"])
            self.assertEqual([], state["gpu_lease_ids"])
            self.assertEqual([], state["resource_lease_ids"])
            self.assertFalse(state["secret_values_recorded"])
            self.assertEqual([], validate_execution_capability_receipt(state))
        finally:
            release_authority(root, CANDIDATE_ID, experiment["authority_id"], "test-done")

    def test_tampered_capability_fails_hash_validation(self) -> None:
        _, human = self.external_authority()
        root = self.control_root()
        run_id = "pa05-seed-a-demo"
        experiment = self.experiment_authority(root, run_id)
        try:
            state = build_execution_capability(
                human_authority=human,
                runtime_audit=self.runtime(credential_ready=True),
                run_id=run_id,
                authority_root=root,
                experiment_authority_id=experiment["authority_id"],
            )
            state["server_id"] = "69"
            errors = validate_execution_capability_receipt(state)
            self.assertIn("capability-server-drift", errors)
            self.assertIn("execution capability receipt hash mismatch", errors)
        finally:
            release_authority(root, CANDIDATE_ID, experiment["authority_id"], "test-done")

    def test_written_capability_becomes_unloadable_after_experiment_authority_release(self) -> None:
        authority_path, _ = self.external_authority()
        root = self.control_root()
        run_id = "pa05-seed-a-demo"
        experiment = self.experiment_authority(root, run_id)
        runtime_root = Path(tempfile.mkdtemp(prefix="pa05-cap-runtime-"))
        self.addCleanup(lambda: shutil.rmtree(runtime_root, ignore_errors=True))
        runtime_path = runtime_root / "runtime.json"
        runtime_path.write_text(json.dumps(self.runtime(credential_ready=True), indent=2) + "\n", encoding="utf-8")
        output = runtime_root / "capability.json"
        state = write_execution_capability(
            human_authority_path=authority_path,
            run_id=run_id,
            authority_root=root,
            experiment_authority_id=experiment["authority_id"],
            runtime_audit_path=runtime_path,
            output_path=output,
        )
        self.assertTrue(state["valid"])
        loaded = load_execution_capability(output)
        self.assertTrue(loaded["valid"])
        self.assertEqual(state["capability_sha256"], loaded["capability_sha256"])
        release_authority(root, CANDIDATE_ID, experiment["authority_id"], "test-done")
        self.assertEqual({}, load_execution_capability(output))

    def test_human_permit_without_active_experiment_authority_cannot_issue_capability(self) -> None:
        _, human = self.external_authority()
        root = self.control_root()
        state = build_execution_capability(
            human_authority=human,
            runtime_audit=self.runtime(credential_ready=True),
            run_id="pa05-seed-a-demo",
            authority_root=root,
            experiment_authority_id="missing",
        )
        self.assertFalse(state["valid"])
        self.assertIn("active-experiment-authority-required", state["errors"])


if __name__ == "__main__":
    unittest.main()
