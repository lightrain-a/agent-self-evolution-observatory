from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from .paper_first_skill_validation_transfer_f0 import CANDIDATE_ID, CONTRACT_VERSION, SOURCE_COMMIT, build_plan
from .paper_first_skill_validation_transfer_f0_authority import (
    AUTHORITY_TYPE,
    EXPECTED_F0_HARNESS_SHA256,
    EXPECTED_RUNTIME_CONTRACT_SHA256,
    EXPECTED_SOURCE_TREE_SHA256,
    SERVER_ID,
    load_human_authority,
    require_bounded_f0_execution_authority,
)


class SkillValidationTransferF0AuthorityTest(unittest.TestCase):
    def payload(self) -> dict:
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

    def write_external(self, payload: dict) -> Path:
        root = Path(tempfile.mkdtemp(prefix="pa05-authority-"))
        path = root / "authority.json"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        self.addCleanup(lambda: __import__("shutil").rmtree(root, ignore_errors=True))
        return path

    def test_missing_authority_fails_closed(self) -> None:
        state = load_human_authority("")
        self.assertFalse(state["bounded_f0_execution_authorized"])
        with self.assertRaisesRegex(RuntimeError, "valid external human execution authority"):
            require_bounded_f0_execution_authority(authority=state)

    def test_valid_external_authority_is_non_gpu_and_bounded(self) -> None:
        state = load_human_authority(self.write_external(self.payload()))
        self.assertEqual([], state["errors"])
        self.assertTrue(state["bounded_f0_execution_authorized"])
        self.assertTrue(state["api_docker_execution_authorized"])
        self.assertTrue(state["provider_credential_use_authorized"])
        self.assertFalse(state["gpu_lease_authorized"])
        self.assertEqual(SERVER_ID, state["server_id"])
        self.assertIs(state, require_bounded_f0_execution_authority(authority=state))
        for key in (
            "problem_gate_authorized",
            "paper_design_authorized",
            "method_authorized",
            "p0_authorized",
            "full_experiment_authorized",
        ):
            self.assertFalse(state[key])

    def test_gpu_authorization_is_rejected(self) -> None:
        payload = self.payload()
        payload["gpu_lease_authorized"] = True
        state = load_human_authority(self.write_external(payload))
        self.assertFalse(state["bounded_f0_execution_authorized"])
        self.assertIn("gpu-lease-must-remain-unauthorized", state["errors"])

    def test_runtime_contract_drift_is_rejected(self) -> None:
        payload = self.payload()
        payload["runtime_contract_sha256"] = "0" * 64
        state = load_human_authority(self.write_external(payload))
        self.assertFalse(state["bounded_f0_execution_authorized"])
        self.assertIn("binding-mismatch:runtime_contract_sha256", state["errors"])

    def test_provider_price_recheck_is_required_by_human_permit(self) -> None:
        payload = self.payload()
        payload["provider_price_rechecked_at_review"] = False
        state = load_human_authority(self.write_external(payload))
        self.assertFalse(state["bounded_f0_execution_authorized"])
        self.assertIn("provider-price-recheck-required-at-human-review", state["errors"])


if __name__ == "__main__":
    unittest.main()
