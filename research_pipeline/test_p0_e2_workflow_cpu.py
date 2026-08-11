from __future__ import annotations

import json
import unittest

from .config import PROJECT_ROOT
from .p0_e2_workflow_cpu import _freeze_hash


class P0E2WorkflowCpuTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state=json.loads((PROJECT_ROOT/"generated"/"p0-e2-workflow-cpu.json").read_text(encoding="utf-8"))

    def test_frozen_identity_disjoint_zero_search_contract(self) -> None:
        s=self.state
        self.assertEqual(_freeze_hash(s["frozen_registry"]),s["freeze_sha256_before_hidden"])
        self.assertTrue(s["design"]["hidden_api_identity_disjoint"])
        self.assertTrue(s["baseline_fairness"]["same_source_call_budget"])
        self.assertTrue(s["baseline_fairness"]["both_zero_search_on_hidden"])
        self.assertFalse(s["baseline_fairness"]["hidden_outcomes_used_before_freeze"])
        self.assertEqual(s["design"]["rewrite_rule_capacity"],4)

    def test_matched_e1_direct_edit_fires_stop(self) -> None:
        m=self.state["metrics"]
        self.assertEqual(m["grammar_source_calls"],m["direct_source_calls"])
        self.assertEqual(m["grammar_hidden_success"],1.0)
        self.assertEqual(m["direct_edit_hidden_success"],1.0)
        self.assertEqual(m["hidden_rewrite_agreement"],1.0)
        self.assertEqual(m["grammar_harmful_rewrites"],0)
        self.assertEqual(m["direct_harmful_rewrites"],0)
        self.assertTrue(self.state["matched_simplification"]["equivalent"])
        self.assertEqual(self.state["decision"],"STOP_MATCHED_E1_DIRECT_EDIT_EQUIVALENT")
        self.assertTrue(self.state["standalone_claim_stop_authorized"])
        self.assertFalse(self.state["p1_authorized"])


if __name__=="__main__": unittest.main()
