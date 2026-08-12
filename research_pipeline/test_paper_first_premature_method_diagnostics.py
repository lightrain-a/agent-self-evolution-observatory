from __future__ import annotations

import unittest
from pathlib import Path

from .paper_first_premature_method_diagnostics import build_premature_method_diagnostics


class PrematurePaperFirstMethodDiagnosticsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        root = Path("/data/wyt/agent-self-evolution-observatory")
        if not (root / "runs" / "paper-first-p0-method-20260812" / "a8-v2" / "result.json").exists():
            raise unittest.SkipTest("premature method diagnostic artifacts are not mounted")
        cls.state = build_premature_method_diagnostics(root)
        cls.by = {row["incubation_id"]: row for row in cls.state["cards"]}

    def test_archive_has_zero_scientific_or_lifecycle_authority(self) -> None:
        summary = self.state["summary"]
        self.assertEqual((summary["directions"], summary["completed_diagnostics"]), (2, 2))
        self.assertEqual(summary["scientifically_authorized"], 0)
        self.assertEqual(summary["p0_lifecycle_mutations"], 0)
        self.assertEqual(summary["full_experiment_authorized"], 0)
        self.assertTrue(self.state["authority"]["cannot_retroactively_authorize"])
        self.assertTrue(self.state["authority"]["cannot_override_problem_or_design_adjudication"])
        for row in self.state["cards"]:
            self.assertFalse(row["authority"]["scientific_authority"])
            self.assertFalse(row["authority"]["p0_lifecycle_authority"])
            self.assertFalse(row["authority"]["method_authority"])
            self.assertFalse(row["authority"]["principle_authority"])

    def test_pf1_preserves_design_hold_then_same_information_reducibility(self) -> None:
        row = self.by["PF-1"]
        v1 = row["v1_design_diagnosis"]
        v2 = row["v2_observed_method_diagnostic"]
        self.assertEqual(v1["decision"], "HOLD_METHOD_NONIDENTIFIABLE_RETENTION_FLOOR")
        self.assertEqual(v1["diagnosis"], "design-nonidentifiable")
        self.assertEqual((v1["current_baseline"], v1["retention_baseline"]), (0.5, 0.0))
        self.assertFalse(v1["hidden_executed"])
        self.assertEqual(v2["decision"], "STOP_MATCHED_POST_ONLY_EQUIVALENT")
        self.assertEqual((v2["baseline_reverification"]["current_success"], v2["baseline_reverification"]["retention_success"]), (4, 4))
        self.assertEqual(v2["eligible_candidates"], 6)
        self.assertEqual(v2["selected_proposed"], "c2")
        self.assertEqual(v2["selected_same_information_post_only"], "c2")
        self.assertEqual(v2["selected_probe_adaptation_gain"], 0.5)
        self.assertFalse(v2["same_information_decision_disagreement"])
        self.assertFalse(v2["hidden_authorized"])
        self.assertFalse(v2["hidden_executed"])
        dominant = row["dominant_problem_authority"]
        self.assertEqual(dominant["decision"], "STOP_PF1_STANDALONE_PROBLEM_MERGE_EVOLVABILITY_AUDIT")
        self.assertFalse(dominant["p0_authorized"])
        self.assertFalse(dominant["gpu_authorized"])
        self.assertTrue(dominant["timestamp_is_not_authority"])
        self.assertTrue(dominant["problem_stop_dominates_diagnostic_regardless_of_rebuild_timestamp"])

    def test_pf4_diagnostic_corroborates_cross_cutting_merge_without_gpu(self) -> None:
        row = self.by["PF-4"]
        obs = row["observed_method_diagnostic"]
        self.assertEqual(obs["decision"], "STOP_MATCHED_SOFT_SCALAR_EQUIVALENT")
        self.assertEqual(obs["proposed_selection"], "workflow")
        self.assertEqual(obs["same_information_soft_scalar_selection"], "workflow")
        self.assertFalse(obs["same_information_decision_disagreement"])
        self.assertFalse(obs["fresh_gpu_authorized"])
        dominant = row["dominant_design_authority"]
        self.assertEqual(dominant["verdict"], "MERGE_AS_CROSS_CUTTING_INVARIANT")
        self.assertEqual(dominant["merge_target"], "PF-2 repair-surface-identifiability-under-persistent-agent-updates")
        self.assertFalse(dominant["local_validation_authorized"])
        self.assertFalse(dominant["full_experiment_authorized"])

    def test_same_information_findings_are_failure_assets_not_method_authority(self) -> None:
        self.assertEqual(self.state["summary"]["design_holds"], 1)
        self.assertEqual(self.state["summary"]["same_information_reducibility_findings"], 2)
        self.assertEqual(self.state["summary"]["hidden_executions"], 0)
        self.assertTrue(self.state["policy"]["same_information_reducibility_can_be_reused_as_failure_asset"])
        self.assertTrue(self.state["policy"]["no_additional_gpu_or_hidden_execution_is_authorized"])


if __name__ == "__main__":
    unittest.main()
