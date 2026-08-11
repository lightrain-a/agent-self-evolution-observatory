from __future__ import annotations

import unittest

from .p0_realizability_suite import build_p0_realizability_suite


class P0RealizabilitySuiteTest(unittest.TestCase):
    def test_synthetic_suite_is_representability_only(self) -> None:
        state=build_p0_realizability_suite()
        self.assertEqual(state["summary"]["audited"],14)
        self.assertEqual(state["summary"]["synthetic_pass"],14)
        self.assertEqual(state["summary"]["synthetic_fail"],0)
        self.assertTrue(state["policy"]["representability_only"])
        self.assertTrue(state["policy"]["cannot_unblock_reality_or_effect_variation"])
        self.assertTrue(state["policy"]["cannot_emit_method_result"])
        self.assertTrue(all(row["evidence_kind"]=="synthetic-realizability-only" for row in state["rows"]))

    def test_key_mechanisms_are_not_trivial_constant_outputs(self) -> None:
        by_id={row["idea_id"]:row for row in build_p0_realizability_suite()["rows"]}
        self.assertEqual(by_id["active-causal-minimal-rollback"]["evidence"]["minimal_fault_set"],["b","c"])
        self.assertEqual(len(by_id["counterfactual-evolution-decision-controller"]["evidence"]["action_coverage"]),4)
        self.assertEqual(by_id["constraint-complete-typed-memory-order-logic"]["evidence"]["legal"],3)
        self.assertEqual(by_id["constraint-complete-typed-memory-order-logic"]["evidence"]["violations"],3)
        self.assertFalse(by_id["interventional-permission-triage-under-ceiling"]["evidence"]["new_request_executable"])


if __name__=="__main__":
    unittest.main()
