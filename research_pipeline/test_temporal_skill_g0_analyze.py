from __future__ import annotations

import copy
import unittest

from research_pipeline import temporal_skill_g0_analyze as analyze
from research_pipeline import temporal_skill_g0_reopen_preflight as preflight


class TemporalSkillG0AnalyzeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.receipt, cls.plan = preflight.build_receipt()

    def make_results(self, *, n_success: bool, g0_success: bool, t_success: bool) -> dict:
        rows = []
        values = {
            "N_FRESH": n_success,
            "G0_NOOP": g0_success,
            "T_FROZEN": t_success,
        }
        for row in self.plan["rows"]:
            rows.append(
                {
                    **row,
                    "runtime_valid": True,
                    "resolved_model": self.plan["model_identity"]["required_resolved_model"],
                    "family_success": bool(values[row["arm"]]),
                }
            )
        return {
            "schema_version": "1.0",
            "plan_body_sha256": self.plan["plan_body_sha256"],
            "runner_sha256": self.receipt["frozen_execution_code"]["runner_sha256"],
            "rows": rows,
        }

    def test_neutral_noop_reaches_neutrality_go(self) -> None:
        results = self.make_results(n_success=False, g0_success=False, t_success=True)
        out = analyze.analyze(self.plan, self.receipt, results, bootstrap_draws=200)
        self.assertTrue(out["integrity"]["pass"])
        self.assertEqual(out["status"], "NEUTRALITY_GO")
        self.assertTrue(out["neutrality_go"])
        self.assertEqual(out["neutrality"]["point"], 0.0)
        self.assertEqual(out["neutrality"]["bootstrap_90_ci"], [0.0, 0.0])
        self.assertTrue(out["operation_specificity"]["stage_a_primary_track_survives_directional_gate"])
        self.assertEqual(out["operation_specificity"]["load_bearing_cell_downgrades"], [])
        self.assertFalse(out["claim_upgrade_authorized"])

    def test_nonneutral_noop_stops(self) -> None:
        results = self.make_results(n_success=False, g0_success=True, t_success=True)
        out = analyze.analyze(self.plan, self.receipt, results, bootstrap_draws=200)
        self.assertTrue(out["integrity"]["pass"])
        self.assertEqual(out["status"], "G0_NONNEUTRAL_STOP")
        self.assertFalse(out["neutrality_go"])
        self.assertEqual(out["neutrality"]["point"], 1.0)
        self.assertTrue(out["neutrality"]["global_nonneutral_trigger"])
        self.assertFalse(out["operation_specificity_evaluated"])

    def test_missing_planned_unit_holds(self) -> None:
        results = self.make_results(n_success=False, g0_success=False, t_success=True)
        results["rows"] = results["rows"][:-1]
        out = analyze.analyze(self.plan, self.receipt, results, bootstrap_draws=50)
        self.assertEqual(out["status"], "HOLD_INCOMPLETE_OR_MODEL_DRIFT")
        self.assertFalse(out["integrity"]["pass"])
        self.assertIn("missing-planned-units:1", out["integrity"]["errors"])
        self.assertFalse(out["operation_specificity_evaluated"])

    def test_model_drift_holds(self) -> None:
        results = self.make_results(n_success=False, g0_success=False, t_success=True)
        results = copy.deepcopy(results)
        results["rows"][0]["resolved_model"] = "some-new-model-version"
        out = analyze.analyze(self.plan, self.receipt, results, bootstrap_draws=50)
        self.assertEqual(out["status"], "HOLD_INCOMPLETE_OR_MODEL_DRIFT")
        self.assertFalse(out["integrity"]["pass"])
        self.assertIn("invalid-planned-rows:1", out["integrity"]["errors"])

    def test_sign_test_is_exact(self) -> None:
        self.assertAlmostEqual(analyze.one_sided_sign_p(5, 0, "positive"), 1 / 32)
        self.assertAlmostEqual(analyze.one_sided_sign_p(0, 5, "negative"), 1 / 32)
        self.assertEqual(analyze.one_sided_sign_p(0, 0, "positive"), 1.0)


if __name__ == "__main__":
    unittest.main()
