from __future__ import annotations

import copy
import unittest

from .paper_first_skill_validation_transfer_runtime_audit import (
    build_runtime_audit,
    validate_runtime_audit,
)


class SkillValidationTransferRuntimeAuditTest(unittest.TestCase):
    def exact_preflight_pass(self) -> dict:
        return {
            "status": "PASS",
            "source_commit": "9e3daa339987c3cfa624121e1be442593a53d43c",
            "strict_exit_code": 0,
            "asset_pass": True,
            "config_pass": True,
            "harbor_importable": True,
            "runtime_image_present": True,
            "n_asset_errors": 0,
            "n_config_errors": 0,
        }

    def test_permission_denied_image_is_unobservable_not_absent(self) -> None:
        state = build_runtime_audit(
            harbor_importable=False,
            benchmark_python_ready=True,
            runtime_image_probe={
                "tag": "agent-runtime:latest",
                "builder": "docker",
                "status": "UNOBSERVABLE_PERMISSION_DENIED",
                "observable": False,
                "present": False,
                "probe_returncode": 1,
                "diagnostic": "permission denied while trying to connect to docker.sock",
            },
            gemini_credential_present=False,
        )
        self.assertEqual([], validate_runtime_audit(state))
        self.assertFalse(state["execution_ready"])
        self.assertEqual(
            "UNOBSERVABLE_PERMISSION_DENIED",
            state["runtime_image"]["status"],
        )
        self.assertIn(
            "agent-runtime:latest:UNOBSERVABLE_PERMISSION_DENIED",
            state["hold_reason"],
        )

    def test_gemini_f0_does_not_require_bedrock(self) -> None:
        state = build_runtime_audit(
            harbor_importable=True,
            benchmark_python_ready=True,
            runtime_image_probe={
                "tag": "agent-runtime:latest",
                "builder": "docker",
                "status": "PRESENT",
                "observable": True,
                "present": True,
                "probe_returncode": 0,
                "image_id": "sha256:test",
                "repo_tags": ["agent-runtime:latest"],
            },
            exact_preflight_probe=self.exact_preflight_pass(),
            gemini_credential_present=True,
        )
        self.assertEqual([], validate_runtime_audit(state))
        self.assertTrue(state["runtime_infrastructure_ready"])
        self.assertTrue(state["execution_ready"])
        self.assertEqual(["GEMINI_API_KEY"], state["provider_contract"]["required_credentials"])
        self.assertFalse(state["provider_contract"]["bedrock_credential_required"])

    def test_runtime_infrastructure_requires_exact_first_party_preflight(self) -> None:
        state = build_runtime_audit(
            harbor_importable=True,
            benchmark_python_ready=True,
            runtime_image_probe={
                "tag": "agent-runtime:latest",
                "builder": "docker",
                "status": "PRESENT",
                "observable": True,
                "present": True,
                "probe_returncode": 0,
                "image_id": "sha256:test",
                "repo_tags": ["agent-runtime:latest"],
            },
            gemini_credential_present=True,
        )
        self.assertEqual([], validate_runtime_audit(state))
        self.assertFalse(state["runtime_infrastructure_ready"])
        self.assertFalse(state["execution_ready"])
        self.assertIn("exact first-party strict preflight not passed:NOT_RUN", state["hold_reason"])

    def test_present_image_receipt_rejects_raw_inspect_diagnostic(self) -> None:
        state = build_runtime_audit(
            harbor_importable=True,
            benchmark_python_ready=True,
            runtime_image_probe={
                "tag": "agent-runtime:latest",
                "builder": "docker",
                "status": "PRESENT",
                "observable": True,
                "present": True,
                "probe_returncode": 0,
                "diagnostic": "raw docker inspect output must never be published",
            },
            exact_preflight_probe=self.exact_preflight_pass(),
            gemini_credential_present=True,
        )
        self.assertTrue(any("docker-inspect" in e for e in validate_runtime_audit(state)))

    def test_bedrock_gate_drift_fails_closed(self) -> None:
        state = build_runtime_audit(
            harbor_importable=True,
            benchmark_python_ready=True,
            runtime_image_probe={
                "tag": "agent-runtime:latest",
                "builder": "docker",
                "status": "PRESENT",
                "observable": True,
                "present": True,
                "probe_returncode": 0,
                "image_id": "sha256:test",
                "repo_tags": ["agent-runtime:latest"],
            },
            exact_preflight_probe=self.exact_preflight_pass(),
            gemini_credential_present=True,
        )
        broken = copy.deepcopy(state)
        broken["provider_contract"]["bedrock_credential_required"] = True
        self.assertTrue(any("Bedrock" in e for e in validate_runtime_audit(broken)))


if __name__ == "__main__":
    unittest.main()
