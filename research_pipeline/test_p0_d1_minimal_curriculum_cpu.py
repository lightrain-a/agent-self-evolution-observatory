from __future__ import annotations

import json
import unittest

from .config import PROJECT_ROOT


class P0D1MinimalCurriculumCpuTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state=json.loads((PROJECT_ROOT/"generated"/"p0-d1-minimal-curriculum-cpu.json").read_text(encoding="utf-8"))

    def test_one_minimal_and_intersection_have_identical_hidden_boundary_result(self) -> None:
        m=self.state["one_minimal"]
        i=self.state["matched_intersection"]
        self.assertEqual(m["evaluation"]["hidden_boundary_accuracy"],1.0)
        self.assertEqual(i["evaluation"]["hidden_boundary_accuracy"],1.0)
        self.assertEqual(m["compiled_updates"],i["compiled_updates"])
        self.assertEqual(self.state["design"]["final_training_tokens_per_arm"],320)
        self.assertTrue(self.state["design"]["same_final_training_tokens"])

    def test_intersection_baseline_avoids_minimization_calls_and_fires_stop(self) -> None:
        self.assertEqual(self.state["matched_intersection"]["extra_verifier_calls_after_validation"],0)
        self.assertEqual(self.state["one_minimal"]["extra_verifier_calls_for_minimization"],320)
        self.assertTrue(self.state["matched_simplification"]["equivalent"])
        self.assertEqual(self.state["decision"],"STOP_MATCHED_INTERSECTION_FILTER_EQUIVALENT")
        self.assertTrue(self.state["standalone_claim_stop_authorized"])
        self.assertFalse(self.state["p1_authorized"])


if __name__=="__main__": unittest.main()
