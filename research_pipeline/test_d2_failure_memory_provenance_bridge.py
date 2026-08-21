from __future__ import annotations

import json
import unittest
from pathlib import Path

from .d2_failure_memory_provenance_bridge import FROZEN_TASKS, build_support


ROOT = Path(__file__).resolve().parent.parent


class FailureMemoryProvenanceBridgeTest(unittest.TestCase):
    def test_support_pool_is_frozen_and_qualified(self) -> None:
        support = build_support()
        self.assertEqual(support["status"], "SUPPORT_QUALIFIED")
        self.assertEqual(tuple(row["task_id"] for row in support["tasks"]), FROZEN_TASKS)
        self.assertEqual(len({row["intent_template_id"] for row in support["tasks"]}), 3)
        for row in support["tasks"]:
            self.assertTrue(row["qualified"])
            self.assertEqual(row["blockers"], [])
            self.assertTrue(all(item["visible"] for item in row["reference_visibility"]))

    def test_current_bridge_is_complete_and_inconclusive_without_negative_authority(self) -> None:
        result = json.loads((ROOT / "generated/d2-failure-memory-provenance-bridge.json").read_text(encoding="utf-8"))
        summary = result["summary"]
        self.assertEqual(result["status"], "BRIDGE_COMPLETE")
        self.assertEqual(summary["requested_calls"], 144)
        self.assertEqual(summary["complete_calls"], 144)
        self.assertEqual(summary["provider_failures"], 0)
        self.assertEqual(summary["mean_success_minus_failure_terminal_rate"], 0.0)
        self.assertEqual(summary["permutation_p_success_greater"], 1.0)
        self.assertFalse(summary["support_gate_pass"])
        self.assertFalse(summary["counterevidence_gate_pass"])
        self.assertEqual(result["decision"], "INCONCLUSIVE_NO_NEGATIVE_AUTHORITY")
        self.assertFalse(result["scientific_authority"])

    def test_success_and_failure_provenance_outputs_are_identical_per_task(self) -> None:
        result = json.loads((ROOT / "generated/d2-failure-memory-provenance-bridge.json").read_text(encoding="utf-8"))
        for task_id in FROZEN_TASKS:
            success = {row["answer_sha256"] for row in result["rollouts"] if row["task_id"] == task_id and row["provenance"] == "SUCCESS"}
            failure = {row["answer_sha256"] for row in result["rollouts"] if row["task_id"] == task_id and row["provenance"] == "FAILURE"}
            self.assertEqual(success, failure)


if __name__ == "__main__":
    unittest.main()
