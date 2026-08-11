from __future__ import annotations

import unittest

from .p0_b10_cpu import run_b10_cpu_p0


class P0B10CpuTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state=run_b10_cpu_p0()

    def test_binding_held_out_split_and_fair_baseline(self) -> None:
        self.assertEqual(self.state["design"]["held_out_combinations"],32)
        self.assertTrue(all(row["active_truth_constraints"]>=1 for row in self.state["rows"]))
        self.assertEqual(sum(row["active_truth_constraints"]>=2 for row in self.state["rows"]),4)
        fairness=self.state["baseline_fairness"]
        self.assertTrue(fairness["same_typed_variables"] and fairness["same_training_records"] and fairness["same_held_out_combinations"] and fairness["same_exact_candidate_enumeration"] and fairness["compiled_edge_budget_matched"])
        self.assertFalse(fairness["test_outcomes_used_for_decoding"])

    def test_matched_nary_control_falsifies_both_b10_subclaims(self) -> None:
        m=self.state["metrics"]; g=self.state["gates"]
        self.assertEqual(m["symbolic_exact_accuracy"],1.0)
        self.assertEqual(m["factor_exact_accuracy"],1.0)
        self.assertEqual(m["symbolic_representation_advantage"],0.0)
        self.assertEqual(m["symbolic_compiled_accuracy"],1.0)
        self.assertEqual(m["factor_budgeted_compiled_accuracy"],1.0)
        self.assertEqual(m["symbolic_compiled_edge_checks_mean"],m["factor_budgeted_edge_checks_mean"])
        self.assertFalse(g["representation_claim_pass"])
        self.assertTrue(g["matched_edge_budget_factor_matches"])
        self.assertEqual(self.state["decision"],"STOP_MATCHED_NARY_EQUIVALENT")
        self.assertTrue(self.state["standalone_claim_stop_authorized"])
        self.assertTrue(self.state["real_agent_generalization_not_tested"])


if __name__=="__main__":
    unittest.main()
