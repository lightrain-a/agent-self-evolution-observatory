from __future__ import annotations

import unittest

from research_pipeline.d5_state_sufficiency_f0 import ARMS, MEMORY_IDS
from research_pipeline.d5_state_sufficiency_gemma import analyze_a


class D5StateSufficiencyGemmaTest(unittest.TestCase):
    @staticmethod
    def _contract() -> dict:
        tasks = [
            {"target_family": "f1", "task_relpath": "task-1"},
            {"target_family": "f2", "task_relpath": "task-2"},
            {"target_family": "f3", "task_relpath": "task-3"},
        ]
        return {"contract_sha256": "abc", "stage_a": {"episodes": 27, "tasks": tasks}}

    @staticmethod
    def _task_rows(task: str, triples: dict[str, tuple[int, int, int]]) -> list[dict]:
        rows = []
        for mid in MEMORY_IDS:
            retrieved, placebo, no_memory = triples[mid]
            values = {"retrieved": retrieved, "placebo": placebo, "no-memory": no_memory}
            for arm in ARMS:
                rows.append({
                    "memory_id": mid,
                    "task_relpath": task,
                    "arm": arm,
                    "success": values[arm],
                    "actions": ["look"] if arm == "no-memory" else [f"{arm}-{mid}"],
                })
        return rows

    def test_incomplete_but_still_qualified_prefix_remains_incomplete(self) -> None:
        same = {mid: (1, 1, 1) for mid in MEMORY_IDS}
        result = analyze_a(self._task_rows("task-1", same), self._contract())
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertEqual(result["completed_tasks"], 1)
        self.assertNotIn("decision", result)

    def test_one_completed_equivalence_violation_is_monotone_early_stop(self) -> None:
        same = {mid: (1, 1, 1) for mid in MEMORY_IDS}
        mismatch = {mid: (0, 0, 0) for mid in MEMORY_IDS}
        mismatch[MEMORY_IDS[1]] = (0, 1, 0)
        rows = self._task_rows("task-1", same) + self._task_rows("task-2", mismatch)
        result = analyze_a(rows, self._contract())
        self.assertEqual(result["status"], "EARLY_STOP_QUALIFICATION_FAILED")
        self.assertEqual(result["decision"], "STOP_GEMMA_SUBSTRATE_NO_CURRENT_EQUIVALENCE")
        self.assertFalse(result["stage_b_authorized_by_this_gate"])
        self.assertEqual(result["remaining_stage_a_rows_not_required"], 9)

    def test_complete_common_panel_pass_opens_stage_b(self) -> None:
        rows = []
        for task, value in [("task-1", 1), ("task-2", 0), ("task-3", 1)]:
            same = {mid: (value, value, value) for mid in MEMORY_IDS}
            rows.extend(self._task_rows(task, same))
        result = analyze_a(rows, self._contract())
        self.assertEqual(result["status"], "COMPLETE")
        self.assertEqual(result["decision"], "PASS_OPEN_SEALED_STAGE_B")
        self.assertTrue(result["stage_b_authorized_by_this_gate"])


if __name__ == "__main__":
    unittest.main()
