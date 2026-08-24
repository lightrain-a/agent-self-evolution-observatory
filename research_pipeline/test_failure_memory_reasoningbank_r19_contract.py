from __future__ import annotations

import unittest

from research_pipeline.failure_memory_reasoningbank_r19_contract import build_schedule


class TestR19Contract(unittest.TestCase):
    def _cohort(self):
        return [
            {"template_id": str(1000 + i), "source_task_id": str(2000 + i), "r19_downstream_task_id": str(3000 + i)}
            for i in range(35)
        ]

    def test_schedule_has_140_episodes(self):
        rows = build_schedule(self._cohort())
        self.assertEqual(len(rows), 140)
        self.assertEqual([r["sequence_index"] for r in rows], list(range(140)))

    def test_every_task_has_two_repeats_per_arm_and_counterbalanced_order(self):
        rows = build_schedule(self._cohort())
        for idx in range(35):
            unit = [r for r in rows if r["cohort_index"] == idx]
            self.assertEqual(len(unit), 4)
            self.assertEqual(sum(r["arm"] == "STATUS_S" for r in unit), 2)
            self.assertEqual(sum(r["arm"] == "STATUS_F" for r in unit), 2)
            rep0 = [r["arm"] for r in unit if r["repeat_id"] == 0]
            rep1 = [r["arm"] for r in unit if r["repeat_id"] == 1]
            self.assertEqual(rep1, list(reversed(rep0)))

    def test_invalid_cohort_size_fails_closed(self):
        with self.assertRaises(RuntimeError):
            build_schedule(self._cohort()[:-1])


if __name__ == "__main__":
    unittest.main()
