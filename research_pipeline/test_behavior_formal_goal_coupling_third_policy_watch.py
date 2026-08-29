from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from .behavior_formal_goal_coupling_third_policy_watch import evaluate_change


class ThirdPolicyWatchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.baseline = json.loads(
            Path("generated/behavior-formal-goal-coupling-third-policy-source-baseline-20260828.json").read_text()
        )
        cls.current = copy.deepcopy(cls.baseline["surfaces"])

    def test_stable_surfaces_do_not_trigger(self) -> None:
        result = evaluate_change(self.baseline, copy.deepcopy(self.current))
        self.assertEqual(result["status"], "WATCH_STABLE_NO_THIRD_POLICY_SOURCE_CHANGE")
        self.assertFalse(result["triggered"])
        self.assertFalse(result["scientific_authority"])
        self.assertFalse(result["execution_authority"])
        self.assertFalse(result["gpu_authority"])
        self.assertFalse(result["policy_outcomes_read"])

    def test_transport_failure_is_incomplete_hold_not_false_stable(self) -> None:
        current = copy.deepcopy(self.current)
        current.pop("openral_vla_compatibility")
        result = evaluate_change(
            self.baseline,
            current,
            [{"surface": "openral_vla_compatibility", "error": "timeout"}],
        )
        self.assertEqual(result["status"], "WATCH_INCOMPLETE_SOURCE_TRANSPORT_HOLD")
        self.assertFalse(result["triggered"])
        self.assertFalse(result["recheck_required"])
        self.assertFalse(result["watch_complete"])
        self.assertEqual(result["transport_errors"][0]["surface"], "openral_vla_compatibility")
        self.assertFalse(result["execution_authority"])
        self.assertFalse(result["policy_outcomes_read"])

    def test_detected_change_still_rechecks_if_another_surface_transport_fails(self) -> None:
        current = copy.deepcopy(self.current)
        current["openeta_readme"]["sha256"] = "0" * 64
        current.pop("openral_vla_compatibility")
        result = evaluate_change(
            self.baseline,
            current,
            [{"surface": "openral_vla_compatibility", "error": "timeout"}],
        )
        self.assertEqual(result["status"], "RECHECK_REQUIRED_THIRD_POLICY_SOURCE_CHANGE")
        self.assertTrue(result["triggered"])
        self.assertFalse(result["watch_complete"])
        self.assertFalse(result["execution_authority"])

    def test_content_hash_change_triggers_recheck_only(self) -> None:
        current = copy.deepcopy(self.current)
        current["openeta_readme"]["sha256"] = "0" * 64
        result = evaluate_change(self.baseline, current)
        self.assertEqual(result["status"], "RECHECK_REQUIRED_THIRD_POLICY_SOURCE_CHANGE")
        self.assertTrue(result["triggered"])
        self.assertEqual(result["changed_surfaces"][0]["surface"], "openeta_readme")
        self.assertFalse(result["execution_authority"])
        self.assertFalse(result["policy_training_authorized"])

    def test_issue_state_or_timestamp_change_triggers(self) -> None:
        current = copy.deepcopy(self.current)
        current["allenai_behavior2026_bridge_issue"]["state"] = "closed"
        current["allenai_behavior2026_bridge_issue"]["updated_at"] = "2026-08-29T00:00:00Z"
        result = evaluate_change(self.baseline, current)
        self.assertTrue(result["triggered"])
        surfaces = {row["surface"] for row in result["changed_surfaces"]}
        self.assertIn("allenai_behavior2026_bridge_issue", surfaces)
        self.assertFalse(result["gpu_authority"])
        self.assertFalse(result["policy_rollouts_authorized"])


if __name__ == "__main__":
    unittest.main()
