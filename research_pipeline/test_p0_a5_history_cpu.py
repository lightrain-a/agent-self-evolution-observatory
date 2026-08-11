from __future__ import annotations

import json
import unittest

from .config import PROJECT_ROOT


class P0A5HistoryCpuTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state=json.loads((PROJECT_ROOT/"generated"/"p0-a5-history-cpu.json").read_text(encoding="utf-8"))

    def test_frozen_long_history_and_rollback_queries(self) -> None:
        d=self.state["design"]
        self.assertEqual(d["updates"],40)
        self.assertEqual(len(d["rollback_queries"]),12)
        self.assertEqual(self.state["semantic_compactor"]["evaluation"]["rollback_fidelity"],1.0)
        self.assertEqual(self.state["generic_state_diff"]["evaluation"]["rollback_fidelity"],1.0)
        self.assertEqual(self.state["periodic_checkpoint"]["rollback_fidelity"],1.0)

    def test_generic_state_diff_dominates_semantic_compaction(self) -> None:
        semantic=self.state["semantic_compactor"]
        generic=self.state["generic_state_diff"]
        self.assertLess(generic["storage_cells"],semantic["storage_cells"])
        self.assertEqual(generic["evaluation"]["mean_segments_from_base"],semantic["evaluation"]["mean_segments_from_base"])
        self.assertTrue(self.state["matched_simplification"]["dominates_or_ties"])
        self.assertEqual(self.state["decision"],"STOP_MATCHED_GENERIC_STATE_DIFF_DOMINATES")
        self.assertTrue(self.state["standalone_claim_stop_authorized"])
        self.assertFalse(self.state["p1_authorized"])


if __name__=="__main__": unittest.main()
