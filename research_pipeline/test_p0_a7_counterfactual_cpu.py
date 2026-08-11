from __future__ import annotations

import json
import unittest

from .config import PROJECT_ROOT


class P0A7CounterfactualCpuTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state=json.loads((PROJECT_ROOT/"generated"/"p0-a7-counterfactual-cpu.json").read_text(encoding="utf-8"))

    def test_same_state_four_action_support_is_non_degenerate(self) -> None:
        d=self.state["design"]
        self.assertTrue(d["all_actions_supported_hidden"])
        self.assertEqual(set(d["hidden_action_truth"]),{"continue","commit","rollback","stop"})
        self.assertTrue(all(v>0 for v in d["hidden_action_truth"].values()))
        self.assertFalse(d["candidate_regeneration"])

    def test_shallow_cart_reproduces_controller_and_fires_stop(self) -> None:
        linear=self.state["linear_controller"]["hidden"]
        tree=self.state["matched_cart"]["hidden"]
        self.assertEqual(linear["action_accuracy"],1.0)
        self.assertEqual(tree["action_accuracy"],1.0)
        self.assertEqual((linear["mean_regret"],tree["mean_regret"]),(0.0,0.0))
        self.assertLessEqual(self.state["matched_cart"]["selected_depth"],3)
        self.assertTrue(self.state["matched_simplification"]["equivalent_or_better"])
        self.assertEqual(self.state["decision"],"STOP_MATCHED_SHALLOW_RULE_EQUIVALENT")
        self.assertTrue(self.state["standalone_claim_stop_authorized"])
        self.assertFalse(self.state["p1_authorized"])


if __name__=="__main__": unittest.main()
