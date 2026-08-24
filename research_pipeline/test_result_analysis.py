from __future__ import annotations

import copy
import unittest

from .failure_asset_library import build_failure_asset_library
from .result_analysis import (
    build_result_analysis_state,
    load_result_analysis_ledger,
    result_analysis_discovery_lessons,
    result_analysis_failure_assets,
    result_analysis_paper_guidance,
    validate_result_analysis_ledger,
)


class ResultAnalysisTest(unittest.TestCase):
    def setUp(self) -> None:
        self.ledger = load_result_analysis_ledger()
        self.state = build_result_analysis_state(self.ledger)

    def test_c1_result_is_analyzed_before_terminal_distillation(self) -> None:
        self.assertEqual(self.state["status"], "RESULT_ANALYSIS_DISTILLED", self.state["errors"])
        self.assertEqual(self.state["summary"]["analyses"], 1)
        self.assertEqual(self.state["summary"]["terminal_results_analyzed"], 1)
        self.assertEqual(self.state["summary"]["discovery_lessons"], 3)
        self.assertEqual(self.state["summary"]["failure_assets"], 1)
        self.assertEqual(self.state["summary"]["paper_guidance_records"], 1)
        self.assertEqual(self.state["summary"]["errors"], 0)
        self.assertFalse(self.state["scientific_authority"])
        self.assertFalse(any(self.state["authority"].values()))

        row = self.state["analyses"][0]
        analysis = row["analysis"]
        self.assertEqual(analysis["failure_layer"], "method_realization")
        self.assertEqual(analysis["failure_type"], "evidence-authority-qualification-unavailable")
        self.assertIn("does not reliably propagate", row["observed"][2]["statement"])
        self.assertIn("does not prove", analysis["negative_boundaries"][3])
        self.assertIn("never received scientific execution authority", analysis["negative_boundaries"][2])
        self.assertIn("filtered by later exposure and uptake stages", analysis["mechanism_interpretation"])
        self.assertIn("Paper-only strengthening", analysis["next_scientific_action"])

    def test_analysis_contract_rejects_numbers_without_interpretation(self) -> None:
        broken = copy.deepcopy(self.ledger)
        analysis = broken["analyses"][0]["analysis"]
        analysis["negative_boundaries"] = []
        analysis["strongest_alternative_explanations"] = []
        analysis["does_not_imply"] = ""
        errors = validate_result_analysis_ledger(broken)
        self.assertTrue(any("negative_boundaries" in error for error in errors))
        self.assertTrue(any("strongest_alternative_explanations" in error for error in errors))
        self.assertTrue(any("does_not_imply" in error for error in errors))

    def test_failure_layer_cannot_be_promoted_to_method_effect_failure(self) -> None:
        broken = copy.deepcopy(self.ledger)
        broken["analyses"][0]["analysis"]["failure_layer"] = "method_effect"
        errors = validate_result_analysis_ledger(broken)
        self.assertTrue(any("failure layer is not canonical" in error for error in errors))

    def test_result_analysis_projects_zero_authority_failure_asset_and_lessons(self) -> None:
        assets = result_analysis_failure_assets(self.state)
        lessons = result_analysis_discovery_lessons(self.state)
        guidance = result_analysis_paper_guidance(self.state)
        self.assertEqual(len(assets), 1)
        self.assertEqual(len(lessons), 3)
        self.assertEqual(len(guidance), 1)
        self.assertEqual(assets[0]["signature"], "method_realization:evidence-authority-qualification-unavailable")
        self.assertEqual(assets[0]["affected_layer"], "method_realization")
        self.assertFalse(assets[0]["scientific_authority"])
        self.assertEqual(
            {row["lesson_id"] for row in lessons},
            {
                "LS-RESULT-STAGEWISE-TRANSPORT-NOT-STATE-DIVERGENCE",
                "LS-RESULT-LOCATOR-VALIDITY-AUTHORITY-SEPARATION",
                "LS-RESULT-QUALIFICATION-STOP-NOT-METHOD-FAIL",
            },
        )
        self.assertEqual(guidance[0]["active_archetype"], "IDENTIFICATION_MEASUREMENT")
        self.assertFalse(guidance[0]["scientific_authority"])
        self.assertFalse(guidance[0]["experiment_authority"])

        library = build_failure_asset_library({"nodes": []}, additional_assets=assets)
        self.assertIn(
            "method_realization:evidence-authority-qualification-unavailable",
            {row["signature"] for row in library["assets"]},
        )
        self.assertEqual(library["summary"]["principle_dead_ends"], 0)


if __name__ == "__main__":
    unittest.main()
