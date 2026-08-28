from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from .behavior_formal_goal_coupling_2026_release_watch import TARGET_FILES, evaluate_release_change


class BehaviorFormalGoalCoupling2026ReleaseWatchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.baseline = json.loads(
            Path("generated/behavior-formal-goal-coupling-2026-release-baseline-20260828.json").read_text(encoding="utf-8")
        )

    def current_from_baseline(self):
        space = self.baseline["leaderboard_space"]
        files = {}
        for path, row in space["data_files"].items():
            files[path] = {"exists": True, "oid": row["oid"], "size": row["size"]}
        return {"sha": space["sha"], "last_modified": "x", "data_files": files}

    def test_stable_target_files_do_not_trigger(self) -> None:
        result = evaluate_release_change(self.baseline, self.current_from_baseline())
        self.assertFalse(result["triggered"])
        self.assertEqual(result["changed_2026_target_files"], [])
        self.assertFalse(result["policy_outcome_values_read"])

    def test_each_2026_target_file_change_triggers(self) -> None:
        for path in TARGET_FILES:
            with self.subTest(path=path):
                current = self.current_from_baseline()
                current["data_files"][path]["oid"] = "f" * 40
                current["data_files"][path]["size"] = 1
                result = evaluate_release_change(self.baseline, current)
                self.assertTrue(result["triggered"])
                self.assertEqual([row["path"] for row in result["changed_2026_target_files"]], [path])
                self.assertFalse(result["analysis_authority"])

    def test_2025_history_file_change_is_ignored_for_trigger(self) -> None:
        current = self.current_from_baseline()
        current["data_files"]["data/2025_results.jsonl"]["oid"] = "e" * 40
        current["data_files"]["data/2025_results.jsonl"]["size"] += 10
        result = evaluate_release_change(self.baseline, current)
        self.assertFalse(result["triggered"])
        self.assertTrue(result["ignored_2025_results_changed"])

    def test_public_schema_change_requires_recheck_without_result_release(self) -> None:
        current = self.current_from_baseline()
        current["data_files"]["data/README.md"]["oid"] = "b" * 40
        current["data_files"]["data/README.md"]["size"] += 1
        result = evaluate_release_change(self.baseline, current)
        self.assertFalse(result["triggered"])
        self.assertTrue(result["public_schema_changed"])
        self.assertTrue(result["recheck_required"])
        self.assertEqual(result["status"], "RECHECK_REQUIRED_2026_PUBLIC_SCHEMA_CHANGE")

    def test_portal_or_space_revision_change_without_target_or_schema_change_does_not_trigger(self) -> None:
        current = self.current_from_baseline()
        current["sha"] = "a" * 40
        result = evaluate_release_change(self.baseline, current)
        self.assertFalse(result["triggered"])
        self.assertFalse(result["recheck_required"])
        self.assertEqual(result["current_space_sha"], "a" * 40)


if __name__ == "__main__":
    unittest.main()
