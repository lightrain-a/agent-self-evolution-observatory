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

    def test_real_gate_is_blocked_by_runtime_drift_not_gpu_capacity(self) -> None:
        r=self.state["runtime_preflight_snapshot"]
        self.assertEqual(r["decision"],"HOLD_RUNTIME_ENVIRONMENT_DRIFT")
        self.assertIn("idle",r["gpu_state"].lower())
        self.assertFalse(r["installation_or_environment_mutation_attempted"])


if __name__=="__main__": unittest.main()
