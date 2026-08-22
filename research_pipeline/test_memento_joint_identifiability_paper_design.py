from __future__ import annotations

import unittest

from .memento_joint_identifiability_paper_design import FROZEN_IDS, f0_contract, paper_design_config, runtime_support
from .paper_design_contract import audit_paper_design_contract


class MementoJointIdentifiabilityPaperDesignTest(unittest.TestCase):
    def test_paper_design_contract_passes_quality_v21(self) -> None:
        audit = audit_paper_design_contract(paper_design_config())
        self.assertTrue(audit["passed"], audit["blockers"])
        quality = audit["paper_quality"]
        self.assertTrue(quality["passed"], quality["blockers"])
        self.assertEqual(quality["summary"]["paper_archetype"], "empirical_analysis")
        self.assertEqual(quality["summary"]["baselines"], 3)
        self.assertEqual(quality["summary"]["main_visualizations"], 4)

    def test_f0_gate_is_exactly_the_problem_gate_contract(self) -> None:
        f0 = f0_contract()
        self.assertEqual(FROZEN_IDS, [str(value) for value in range(10000, 10012)])
        self.assertEqual(f0["units"], 12)
        self.assertEqual(f0["arms_per_unit"], 3)
        self.assertEqual(f0["episodes"], 36)
        self.assertEqual(f0["decision_margin"], -0.05)
        self.assertEqual(f0["go"], "upper_bootstrap95(mean_C_u) <= -0.05")
        self.assertEqual(f0["stop"], "lower_bootstrap95(mean_C_u) >= -0.05")
        self.assertEqual(f0["full_audit_unlock"], "GO only")
        self.assertIn("never shrink", f0["selection_policy"])

    def test_exact_runtime_support_hold_never_becomes_scientific_failure(self) -> None:
        support = runtime_support()
        self.assertEqual(support["status"], "HOLD_EXACT_MEMENTO_RUNTIME_ASSETS_MISSING")
        self.assertFalse(support["observed"]["exact_memento_image_present"])
        self.assertIn("not scientific evidence", support["interpretation"])
        self.assertIn("Do not replace MEMENTO", support["proxy_policy"])


if __name__ == "__main__":
    unittest.main()
