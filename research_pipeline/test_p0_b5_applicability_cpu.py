from __future__ import annotations

import json
import unittest

from .config import PROJECT_ROOT


class P0B5ApplicabilityCpuTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state=json.loads((PROJECT_ROOT/"generated"/"p0-b5-applicability-cpu.json").read_text(encoding="utf-8"))

    def test_complexity_matched_ilp_is_exactly_equivalent(self) -> None:
        m=self.state["metrics"]
        self.assertEqual(m["exact_gate_agreement"],1.0)
        self.assertEqual(m["monotone_true_gate_recovery"],m["ilp_true_gate_recovery"])
        self.assertTrue(all(row["monotone_eval"]==row["ilp_eval"] for row in self.state["rows"]))
        self.assertTrue(self.state["matched_simplification"]["equivalent"])
        self.assertEqual(self.state["decision"],"STOP_COMPLEXITY_MATCHED_ILP_EQUIVALENT")
        self.assertTrue(self.state["standalone_claim_stop_authorized"])
        self.assertFalse(self.state["p1_authorized"])


if __name__=="__main__": unittest.main()
