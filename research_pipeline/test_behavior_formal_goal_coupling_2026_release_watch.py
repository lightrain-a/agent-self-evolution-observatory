from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path
from unittest import mock

from .behavior_formal_goal_coupling_2026_release_watch import (
    EMPTY_GIT_BLOB_OID,
    EMPTY_SHA256,
    SCHEMA_FILE,
    TARGET_FILES,
    _git_blob_oid,
    _verify_fixed_revision_mirror,
    evaluate_release_change,
)


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

    def test_git_blob_oid_matches_git_empty_blob(self) -> None:
        self.assertEqual(_git_blob_oid(b""), EMPTY_GIT_BLOB_OID)
        self.assertEqual(EMPTY_SHA256, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")

    def test_fixed_revision_verification_does_not_download_nonempty_outcomes(self) -> None:
        schema = b"schema bytes\n"
        files = {
            SCHEMA_FILE: {"exists": True, "size": len(schema), "oid": _git_blob_oid(schema)},
            TARGET_FILES[0]: {"exists": True, "size": 7, "oid": "a" * 40},
            TARGET_FILES[1]: {"exists": True, "size": 0, "oid": EMPTY_GIT_BLOB_OID},
            TARGET_FILES[2]: {"exists": True, "size": 0, "oid": EMPTY_GIT_BLOB_OID},
        }
        downloads: list[str] = []

        def fake_download(url: str) -> bytes:
            downloads.append(url)
            if SCHEMA_FILE in url:
                return schema
            return b""

        with mock.patch(
            "research_pipeline.behavior_formal_goal_coupling_2026_release_watch._download_bytes",
            side_effect=fake_download,
        ):
            verified = _verify_fixed_revision_mirror("b" * 40, files)

        self.assertFalse(verified[TARGET_FILES[0]]["content_downloaded"])
        self.assertEqual(
            verified[TARGET_FILES[0]]["verification"],
            "deferred_nonempty_outcome_content_recheck_required",
        )
        self.assertFalse(verified[TARGET_FILES[0]]["outcome_values_read"])
        self.assertEqual(sum(TARGET_FILES[0] in url for url in downloads), 0)
        self.assertEqual(verified[TARGET_FILES[1]]["sha256"], EMPTY_SHA256)
        self.assertTrue(verified[SCHEMA_FILE]["tree_oid_match"])


if __name__ == "__main__":
    unittest.main()
