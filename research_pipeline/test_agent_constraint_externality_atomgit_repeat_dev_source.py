from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from research_pipeline.agent_constraint_externality_atomgit_repeat_dev_source import (
    AUTH_OUTPUT,
    EXEC_CONTRACT,
    RESULT_OUTPUT,
    families,
    trajectory_audit,
    unit_id,
)


class AtomGitRepeatDevSourceTest(unittest.TestCase):
    def test_six_new_source_units_are_unique_and_target_only(self) -> None:
        rows = families()
        self.assertEqual(len(rows), 6)
        ids = [unit_id(row["family_id"]) for row in rows]
        self.assertEqual(len(set(ids)), 6)
        for family in rows:
            case = family["source_case"]
            self.assertEqual(case["task_instruction"], family["target_instruction"])
            self.assertTrue(case["case_id"].startswith("ACE-DEV-"))
            self.assertTrue(case["case_id"].endswith("-SOURCE"))
            self.assertNotIn(" Preserve ", case["task_instruction"])

    def test_execution_artifacts_do_not_preexist_in_clean_freeze(self) -> None:
        self.assertFalse(AUTH_OUTPUT.exists())
        self.assertFalse(EXEC_CONTRACT.exists())
        self.assertFalse(RESULT_OUTPUT.exists())

    def test_trajectory_audit_accepts_closed_exactly_once_tools(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "trajectory.jsonl"
            rows = [
                {"event":"TOOL_DISPATCH","tool_id":"x:1","index":1,"tool_name":"a","arguments":{}},
                {"event":"TOOL_COMPLETION","tool_id":"x:1","index":1,"tool_name":"a","result":"ok"},
                {"event":"TOOL_DISPATCH","tool_id":"x:2","index":2,"tool_name":"b","arguments":{}},
                {"event":"TOOL_COMPLETION","tool_id":"x:2","index":2,"tool_name":"b","result":"ok"},
            ]
            path.write_text("".join(json.dumps(row)+"\n" for row in rows), encoding="utf-8")
            audit = trajectory_audit(path, 2)
            self.assertTrue(audit["all_tool_dispatches_closed"])
            self.assertEqual(audit["tool_call_count"], 2)

    def test_trajectory_audit_rejects_dangling_dispatch(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "trajectory.jsonl"
            path.write_text(json.dumps({"event":"TOOL_DISPATCH","tool_id":"x:1","index":1,"tool_name":"a","arguments":{}})+"\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "trajectory"):
                trajectory_audit(path, 1)

    def test_trajectory_audit_rejects_cap_rejection(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "trajectory.jsonl"
            rows = [
                {"event":"TOOL_DISPATCH","tool_id":"x:1","index":1,"tool_name":"a","arguments":{}},
                {"event":"TOOL_REJECTED","tool_id":"x:1","index":1,"reason":"TOOL_CALL_CAP_EXCEEDED"},
            ]
            path.write_text("".join(json.dumps(row)+"\n" for row in rows), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "trajectory"):
                trajectory_audit(path, 1)


if __name__ == "__main__":
    unittest.main()
