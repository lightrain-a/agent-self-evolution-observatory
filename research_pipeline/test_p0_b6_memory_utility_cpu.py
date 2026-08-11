from __future__ import annotations

import json
import unittest

from .config import PROJECT_ROOT


class P0B6MemoryUtilityCpuTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state=json.loads((PROJECT_ROOT/"generated"/"p0-b6-memory-utility-cpu.json").read_text(encoding="utf-8"))

    def test_frozen_twenty_percent_audit(self) -> None:
        d=self.state["design"]
        self.assertAlmostEqual(d["audit_fraction"],0.2)
        self.assertEqual((d["audited_activations"],d["future_activations"]),(60,240))
        self.assertTrue(d["same_audit_labels"])

    def test_simple_recency_frequency_policy_dominates_hazard(self) -> None:
        learned=self.state["utility_hazard"]["future"]
        simple=self.state["recency_frequency"]["future"]
        self.assertGreater(learned["retained_harm"],simple["retained_harm"])
        self.assertEqual(simple["retained_harm"],0)
        self.assertEqual(simple["quarantined_benefit"],0)
        self.assertEqual(simple["retained_benefit"],learned["retained_benefit"])
        self.assertTrue(self.state["matched_simplification"]["simple_dominates"])
        self.assertEqual(self.state["decision"],"STOP_RECENCY_FREQUENCY_POLICY_DOMINATES")
        self.assertTrue(self.state["standalone_claim_stop_authorized"])
        self.assertFalse(self.state["p1_authorized"])


if __name__=="__main__": unittest.main()
