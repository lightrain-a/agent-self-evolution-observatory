from __future__ import annotations

import json
import unittest

from .config import PROJECT_ROOT


class P0B3InterferenceCpuTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state=json.loads((PROJECT_ROOT/"generated"/"p0-b3-interference-cpu.json").read_text(encoding="utf-8"))

    def test_matched_cost_screening_signal_is_not_real_method_result(self) -> None:
        s=self.state; m=s["metrics"]
        self.assertEqual(s["decision"],"SCREENING_SIGNAL_REAL_COINTERACTION_REQUIRED")
        self.assertEqual(m["pathway_audit_calls"],m["simple_audit_calls"])
        self.assertEqual((m["pathway_future_harm"],m["simple_future_harm"]),(0,0))
        self.assertGreater(m["pathway_retained_benefit"],m["simple_retained_benefit"])
        self.assertFalse(s["p1_authorized"])
        self.assertIn("synthetic",s["scientific_role"].lower())

    def test_runtime_was_resolved_without_environment_mutation(self) -> None:
        r=self.state["runtime_preflight_snapshot"]
        self.assertEqual(r["decision"],"RUNTIME_RESOLVED")
        self.assertTrue(r["one_step_qwen_alfworld_smoke_pass"])
        self.assertIn("Python 3.12",r["runtime"])
        self.assertFalse(r["installation_or_environment_mutation_attempted"])


if __name__=="__main__": unittest.main()
