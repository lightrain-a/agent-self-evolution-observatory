from __future__ import annotations

import json
import unittest

from .config import PROJECT_ROOT


class P0A4CompositionCpuTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state=json.loads((PROJECT_ROOT/"generated"/"p0-a4-composition-cpu.json").read_text(encoding="utf-8"))

    def test_hidden_identity_and_triple_split_is_real(self) -> None:
        d=self.state["design"]
        self.assertTrue(d["hidden_update_identities_disjoint"])
        self.assertTrue(d["triples_absent_from_training"])
        self.assertEqual(d["pair_intervention_rows"],15)
        self.assertEqual(d["hidden_triples"],20)

    def test_direct_order_risk_and_repair_exactly_tie_registry(self) -> None:
        m=self.state["metrics"]
        self.assertEqual((m["registry_prediction_accuracy"],m["direct_prediction_accuracy"]),(1.0,1.0))
        self.assertEqual((m["registry_repair_success"],m["direct_repair_success"]),(1.0,1.0))
        self.assertEqual(m["repair_exact_agreement"],1.0)
        self.assertEqual(m["registry_candidate_checks"],m["direct_candidate_checks"])
        self.assertTrue(self.state["matched_simplification"]["equivalent"])
        self.assertEqual(self.state["decision"],"STOP_DIRECT_ORDER_AWARE_RISK_EQUIVALENT")
        self.assertTrue(self.state["standalone_claim_stop_authorized"])
        self.assertFalse(self.state["p1_authorized"])


if __name__=="__main__": unittest.main()
