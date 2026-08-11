from __future__ import annotations

import json
import unittest

from .config import PROJECT_ROOT


class P0C2EvaluatorCpuTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state=json.loads((PROJECT_ROOT/"generated"/"p0-c2-evaluator-cpu.json").read_text(encoding="utf-8"))

    def test_cross_version_attribution_is_tied_by_anchor_residual(self) -> None:
        a=self.state["attribution"]
        self.assertEqual(a["cross_accuracy"],1.0)
        self.assertEqual(a["simple_accuracy"],1.0)
        self.assertEqual(a["cross_version"],a["simple_anchor_residual"])

    def test_simple_anchor_calibration_exactly_matches_causal_repair(self) -> None:
        p=self.state["cross_version_causal_repair"]
        s=self.state["simple_anchor_residual_repair"]
        self.assertEqual(p["params"],s["params"])
        self.assertEqual(p["evaluation"],s["evaluation"])
        self.assertGreater(p["extra_intervention_calls"],s["extra_intervention_calls"])
        self.assertTrue(self.state["matched_simplification"]["parameters_identical"])
        self.assertEqual(self.state["decision"],"STOP_SIMPLE_ANCHOR_RESIDUAL_CALIBRATION_EQUIVALENT")
        self.assertTrue(self.state["standalone_claim_stop_authorized"])
        self.assertFalse(self.state["p1_authorized"])


if __name__=="__main__": unittest.main()
