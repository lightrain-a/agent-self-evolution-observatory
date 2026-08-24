from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

try:
    from research_pipeline.failure_memory_reasoningbank_r19_partial_checkpoint_r28 import RECEIPT_ID, build
    from research_pipeline.failure_memory_reasoningbank_r19_csv_checkpoint_r28 import RECEIPT_ID as CSV_RECEIPT_ID
except ModuleNotFoundError:
    from failure_memory_reasoningbank_r19_partial_checkpoint_r28 import RECEIPT_ID, build
    from failure_memory_reasoningbank_r19_csv_checkpoint_r28 import RECEIPT_ID as CSV_RECEIPT_ID


class TestR19CheckpointR28(unittest.TestCase):
    def _root(self, *, inflight: bool = False) -> Path:
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        attempts = []
        progress = []
        arms = [("STATUS_S", 0), ("STATUS_F", 0), ("STATUS_F", 1), ("STATUS_S", 1)]
        for i, (arm, rep) in enumerate(arms):
            attempts.append({"sequence_index": i, "status": "STARTED"})
            progress.append({
                "sequence_index": i,
                "task_id": "271",
                "arm": arm,
                "repeat_id": rep,
                "agent_completion_count": 1,
                "fuzzy_evaluator_completion_count": 0,
                "status": "COMPLETE",
            })
        if inflight:
            attempts.append({"sequence_index": 4, "status": "STARTED"})
        (root / "attempts.jsonl").write_text("".join(json.dumps(x) + "\n" for x in attempts), encoding="utf-8")
        (root / "progress.jsonl").write_text("".join(json.dumps(x) + "\n" for x in progress), encoding="utf-8")
        (root / "run-contract.json").write_text("{}\n", encoding="utf-8")
        (root / "summary.json").write_text("{}\n", encoding="utf-8")
        return root

    def test_r28_identity_and_no_interim_boundary(self) -> None:
        out = build(self._root())
        self.assertEqual(out["receipt_id"], RECEIPT_ID)
        self.assertEqual(CSV_RECEIPT_ID, "D2-FAILURE-MEMORY-PROVENANCE-L2B-R19-CSV-DURABILITY-R28")
        self.assertEqual(out["execution"]["episodes_complete"], 4)
        self.assertEqual(out["execution"]["complete_independent_tasks"], 1)
        self.assertEqual(out["execution"]["next_sequence_index"], 4)
        self.assertFalse(out["interim_policy"]["task_deltas_computed"])
        self.assertFalse(out["interim_policy"]["effect_mean_computed"])
        self.assertFalse(out["interim_policy"]["claim_update_allowed"])

    def test_inflight_episode_fails_closed(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "no in-flight STARTED"):
            build(self._root(inflight=True))


if __name__ == "__main__":
    unittest.main()
