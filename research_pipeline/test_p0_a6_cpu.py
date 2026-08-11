from __future__ import annotations

import unittest

from .p0_a6_cpu import run_a6_cpu_p0


class P0A6CpuTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state=run_a6_cpu_p0()

    def test_matched_group_testing_kills_standalone_claim(self) -> None:
        s=self.state["summary"]; m=self.state["matched_simplification"]
        self.assertEqual(s["active-causal"]["exact_recovery"],1.0)
        self.assertEqual(s["binary-group-testing"]["exact_recovery"],1.0)
        self.assertEqual(s["active-causal"]["mean_tests"],s["binary-group-testing"]["mean_tests"])
        self.assertTrue(m["per_case_test_counts_identical"])
        self.assertEqual(m["relative_mean_test_saving"],0.0)
        self.assertEqual(m["paired_sign_p"],1.0)
        self.assertTrue(m["equivalent"])
        self.assertEqual(self.state["decision"],"STOP_MATCHED_GROUP_TESTING_EQUIVALENT")
        self.assertTrue(self.state["standalone_claim_stop_authorized"])
        self.assertFalse(self.state["real_sequence_gate_required"])

    def test_ddmin_advantage_is_not_mistaken_for_method_novelty(self) -> None:
        p=self.state["paired_active_vs_ddmin"]
        self.assertGreater(p["relative_mean_test_saving"],0.15)
        self.assertLess(p["paired_sign_p"],0.05)
        self.assertGreater(self.state["summary"]["delta-debugging"]["mean_tests"],self.state["summary"]["active-causal"]["mean_tests"])


if __name__=="__main__":
    unittest.main()
