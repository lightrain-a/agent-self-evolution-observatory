from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .paper_first_p0_f0 import build_paper_first_p0_f0_state


class PaperFirstP0F0StateTest(unittest.TestCase):
    def test_support_pass_and_hold_never_emit_method_fail(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            run = root / "runs" / "paper-first-p0-20260812"
            future = run / "future-learnability"
            shared = run / "shared-surface"
            future.mkdir(parents=True); shared.mkdir(parents=True)
            (future / "result.json").write_text(json.dumps({"status":"complete","analysis":{"support_pass":True,"matched_candidates":3,"nonzero_matched_candidates":1,"future_learnability_range":0.25,"baseline":{}}}))
            (shared / "result.json").write_text(json.dumps({"status":"complete","analysis":{
                "pf2":{"support_pass":False,"heldout_oracle_repair_rate":.889,"best_fixed_surface_rate":.778,"ownership_accuracy":.778,"distinct_best_surfaces":3},
                "pf4":{"support_pass":True,"baseline_diagnostic_accuracy":.667,"post_update_wrong_surface_accuracy":{"workflow":.5},"diagnostic_drop":{"workflow":.167}},
                "pf6":{"support_pass":False,"failure_modes":["success","loop-timeout","missing-required-transform"],"non_diagonal_transitions":5,"repair_summaries":{},"decision_relevant_pair":None},
            }}))
            state = build_paper_first_p0_f0_state(root)
        self.assertEqual(state["summary"], {"ideas":4,"running":0,"support_pass":2,"support_hold":2,"method_fail_authorized":0})
        by = {row["idea_id"]: row for row in state["cards"]}
        self.assertEqual(by["future-learnability-preserving-self-evolution"]["decision"], "F0_SUPPORT_PASS")
        self.assertEqual(by["diagnosability-preserving-self-evolution"]["decision"], "F0_SUPPORT_PASS")
        self.assertEqual(by["cross-surface-repair-routing"]["decision"], "HOLD_F0_SUPPORT_INSUFFICIENT")
        self.assertEqual(by["failure-mode-transport-under-self-evolution"]["decision"], "HOLD_F0_SUPPORT_INSUFFICIENT")
        self.assertTrue(all(row["method_failure_authorized"] is False for row in state["cards"]))


if __name__ == "__main__":
    unittest.main()
