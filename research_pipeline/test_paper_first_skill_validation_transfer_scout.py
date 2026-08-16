from __future__ import annotations

import copy
import unittest

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
            bedrock_credential_present=True,
        )
        self.assertEqual([], validate_skill_validation_transfer_scout(state))
        self.assertEqual("DESIGN_READY_EXECUTION_ENV_PRESENT", state["status"])
        self.assertTrue(state["execution_environment"]["execution_ready"])
        self.assertFalse(state["execution_environment"]["direct_execution_authorized"])
        self.assertTrue(all(v is False for v in state["authority"].values()))

    def test_source_drift_fails_closed(self) -> None:
        state = build_skill_validation_transfer_scout()
        broken = copy.deepcopy(state)
        broken["source"]["commit_sha"] = "0" * 40
        self.assertTrue(any("source identity" in e for e in validate_skill_validation_transfer_scout(broken)))


if __name__ == "__main__":
    unittest.main()
