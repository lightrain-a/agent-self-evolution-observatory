from __future__ import annotations

import copy
import unittest

from .paper_first_skill_validation_transfer_runtime_audit import build_runtime_audit
from .paper_first_skill_validation_transfer_scout import (
    build_skill_validation_transfer_scout,
    validate_skill_validation_transfer_scout,
)


class SkillValidationTransferScoutTest(unittest.TestCase):
    def test_default_scout_is_design_ready_but_execution_held(self) -> None:
        state = build_skill_validation_transfer_scout()
        self.assertEqual([], validate_skill_validation_transfer_scout(state))
        self.assertEqual("DESIGN_READY_EXECUTION_ENV_HOLD", state["status"])
        self.assertTrue(state["f0"]["design_ready"])
        self.assertFalse(state["execution_environment"]["execution_ready"])
        self.assertFalse(state["execution_environment"]["direct_execution_authorized"])
        self.assertEqual(0, state["f0"]["model_calls_executed"])
        self.assertEqual(0, state["f0"]["task_trials_executed"])

    def test_environment_presence_does_not_grant_scientific_authority(self) -> None:
        state = build_skill_validation_transfer_scout(
            harbor_importable=True,
            runtime_image_present=True,
            gemini_credential_present=True,
            benchmark_python_ready=True,
            bedrock_credential_present=False,
        )
        self.assertEqual([], validate_skill_validation_transfer_scout(state))
        self.assertEqual("DESIGN_READY_EXECUTION_ENV_PRESENT", state["status"])
        self.assertTrue(state["execution_environment"]["execution_ready"])
        self.assertFalse(state["execution_environment"]["bedrock_required_for_f0"])
        self.assertEqual(["GEMINI_API_KEY"], state["execution_environment"]["required_provider_credentials"])
        self.assertEqual("GEMINI_API_KEY", state["execution_environment"]["provider_routing"]["host_litellm_api_key_env"])
        self.assertTrue(state["execution_environment"]["provider_routing"]["skill_author_uses_run_model_when_model_yaml_active"])
        self.assertFalse(state["execution_environment"]["direct_execution_authorized"])
        self.assertTrue(all(v is False for v in state["authority"].values()))

    def test_bedrock_presence_cannot_substitute_for_missing_gemini_credential(self) -> None:
        state = build_skill_validation_transfer_scout(
            harbor_importable=True,
            runtime_image_present=True,
            gemini_credential_present=False,
            bedrock_credential_present=True,
        )
        self.assertEqual([], validate_skill_validation_transfer_scout(state))
        self.assertFalse(state["execution_environment"]["execution_ready"])
        self.assertIn("Gemini credential for agent + host-side SkillAuthor", state["execution_environment"]["hold_reason"])
        self.assertFalse(any("Bedrock" in reason for reason in state["execution_environment"]["hold_reason"]))

    def test_host_specific_runtime_receipt_can_move_execution_host_without_changing_f0(self) -> None:
        runtime = build_runtime_audit(
            host="52",
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
            exact_preflight_probe={
                "status": "PASS",
                "source_commit": "9e3daa339987c3cfa624121e1be442593a53d43c",
                "strict_exit_code": 0,
                "asset_pass": True,
                "config_pass": True,
                "harbor_importable": True,
                "runtime_image_present": True,
                "n_asset_errors": 0,
                "n_config_errors": 0,
            },
            gemini_credential_present=False,
        )
        state = build_skill_validation_transfer_scout(runtime_audit=runtime)
        self.assertEqual([], validate_skill_validation_transfer_scout(state))
        env = state["execution_environment"]
        self.assertEqual("52", env["host"])
        self.assertTrue(env["runtime_infrastructure_ready"])
        self.assertFalse(env["provider_credential_ready"])
        self.assertFalse(env["execution_ready"])
        self.assertEqual(
            "7756cb19d009b410df23a289a331e74719d0f372c5d4be84d3ec13a974a68a8c",
            state["f0"]["plan_sha256"],
        )

    def test_source_drift_fails_closed(self) -> None:
        state = build_skill_validation_transfer_scout()
        broken = copy.deepcopy(state)
        broken["source"]["commit_sha"] = "0" * 40
        self.assertTrue(any("source identity" in e for e in validate_skill_validation_transfer_scout(broken)))


if __name__ == "__main__":
    unittest.main()
