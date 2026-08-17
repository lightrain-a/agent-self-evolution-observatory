from __future__ import annotations

import copy
import unittest

from .paper_first_skill_validation_transfer_runtime_audit import (
    build_runtime_audit,
    validate_runtime_audit,
)


class SkillValidationTransferRuntimeAuditTest(unittest.TestCase):
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
                "diagnostic": "",
            },
            gemini_credential_present=True,
        )
        self.assertEqual([], validate_runtime_audit(state))
        self.assertTrue(state["execution_ready"])
        self.assertEqual(["GEMINI_API_KEY"], state["provider_contract"]["required_credentials"])
        self.assertFalse(state["provider_contract"]["bedrock_credential_required"])

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
                "diagnostic": "",
            },
            gemini_credential_present=True,
        )
        broken = copy.deepcopy(state)
        broken["provider_contract"]["bedrock_credential_required"] = True
        self.assertTrue(any("Bedrock" in e for e in validate_runtime_audit(broken)))


if __name__ == "__main__":
    unittest.main()
