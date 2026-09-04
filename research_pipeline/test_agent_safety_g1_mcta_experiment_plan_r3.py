from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "generated" / "agent-safety-g1-mcta-experiment-plan-r3-20260904.json"
P1 = ROOT / "generated" / "agent-safety-g1-mcta-p1-conditional-contract-r2-20260904.json"
P2 = ROOT / "generated" / "agent-safety-g1-mcta-length-structure-placebo-contract-20260904.json"
P3 = ROOT / "generated" / "agent-safety-g1-mcta-transport-contract-20260904.json"
MAINLINE = ROOT / "paper_drafts" / "agent-safety-r9-iclr2027" / "MAINLINE_BRIEF.md"
README = ROOT / "paper_drafts" / "agent-safety-r9-iclr2027" / "README.md"
ARCH = ROOT / "paper_drafts" / "agent-safety-r9-iclr2027" / "SKILLZIP_PRECONFIRMATORY_MANUSCRIPT_R2_MCTA.md"
LATEX = ROOT / "paper_drafts" / "agent-safety-r9-iclr2027" / "main_skillzip_preconfirmatory_r2_mcta.tex"


class G1MCTAExperimentPlanR3Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = json.loads(PLAN.read_text(encoding="utf-8"))
        cls.p1 = json.loads(P1.read_text(encoding="utf-8"))
        cls.p2 = json.loads(P2.read_text(encoding="utf-8"))
        cls.p3 = json.loads(P3.read_text(encoding="utf-8"))

    def test_plan_is_zero_provider_and_not_execution_authority(self) -> None:
        self.assertIn("NO_EXECUTION_AUTHORITY", self.plan["status"])
        authority = self.plan["authority"]
        for key in ("provider_calls", "q0_execution", "p0_execution", "p1_execution", "p2_execution", "p3_execution", "harmful_model_calls", "paper_claim_upgrade"):
            self.assertFalse(authority[key])

    def test_mandatory_core_is_exactly_378(self) -> None:
        core = self.plan["mandatory_core"]
        episode_sum = sum(stage["agent_episodes"] for stage in core["stages"])
        self.assertEqual(episode_sum, 378)
        self.assertEqual(core["agent_episode_total"], 378)
        self.assertEqual(self.plan["workload_summary"]["mandatory_core"], 378)
        p1_stage = next(stage for stage in core["stages"] if stage["stage"] == "P1")
        self.assertEqual(p1_stage["agent_episodes"], self.p1["workload"]["agent_episode_count"])

    def test_m0_to_m3_are_required_on_same_rows(self) -> None:
        ladder = self.plan["required_analysis_baselines"]
        self.assertIn("zero extra agent episodes", ladder["provider_cost"])
        self.assertEqual([row["id"] for row in ladder["ordered_ladder"]], [
            "M0_RAW_TEMPORAL",
            "M1_GLOBAL_GATE_ONLY",
            "M2_SAME_SURFACE_TWIN_NO_GRAPH",
            "M3_MCTA_GRAPH_COMPLETE",
        ])
        self.assertIn("must appear together", ladder["main_table_requirement"])

    def test_interpretation_flip_matrix_is_required_and_cost_free(self) -> None:
        flip = self.plan["interpretation_flip_matrix"]
        self.assertTrue(flip["required"])
        self.assertIn("zero extra agent episodes", flip["provider_cost"])
        self.assertIn("M2_GRAPH_OVERADMISSION_RATE", flip["primary_method_necessity_metric"])
        self.assertIn("M2-to-M3 interpretation transition counts", flip["required_outputs"])
        self.assertTrue(flip["post_outcome_definition_change_forbidden"])

    def test_p2_is_claim_triggered_and_matches_frozen_contract(self) -> None:
        p2 = self.plan["conditional_p2_mechanism"]
        self.assertEqual(p2["agent_episodes"], 72)
        self.assertEqual(p2["agent_episodes"], self.p2["execution"]["agent_episode_count"])
        self.assertIn("mandatory", p2["mandatory_if_claimed"].lower())
        self.assertIn("workflow semantics", p2["mandatory_if_claimed"])
        self.assertEqual(p2["cumulative_agent_episodes_if_run"], 450)

    def test_p3_is_scope_triggered_and_matches_frozen_contract(self) -> None:
        p3 = self.plan["conditional_p3_transport"]
        self.assertEqual(p3["agent_episodes"], 178)
        self.assertEqual(p3["agent_episodes"], self.p3["workload"]["total_agent_episodes"])
        self.assertIn("beyond the exact", p3["mandatory_if_claimed"])
        self.assertIn("exact tested backbone", p3["if_not_run"])
        self.assertEqual(p3["cumulative_agent_episodes_if_run_after_p2"], 628)

    def test_extra_budget_prioritizes_independent_support_over_seeds(self) -> None:
        policy = self.plan["information_priority_for_any_extra_budget"]
        priorities = policy["priority_order"]
        self.assertIn("persistent states", priorities[0])
        self.assertIn("task-local pairs", priorities[1])
        self.assertIn("transport backbone", priorities[2])
        self.assertIn("repeated decoding seeds", priorities[3])
        self.assertTrue(any("do not increase only random seeds" in row for row in policy["forbidden"]))

    def test_stop_rules_prevent_workload_inflation_after_null_or_confound(self) -> None:
        rules = {row["condition"]: row["action"] for row in self.plan["stop_and_claim_rules"]}
        self.assertIn("stop before harmful execution", rules["Q0 fails 10/10"])
        self.assertIn("do not weaken C", rules["P0a yields fewer than 6 task-local capability-qualified pair IDs"])
        self.assertIn("raw R1 cannot support", rules["P1 shared-capability support gate fails"])
        self.assertIn("do not run P2", rules["raw R1 positive but shared-capability M3 null or reversed"])

    def test_docs_point_to_claim_aligned_plan_and_flip_matrix(self) -> None:
        mainline = MAINLINE.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        arch = ARCH.read_text(encoding="utf-8")
        latex = LATEX.read_text(encoding="utf-8")
        plan_name = "agent-safety-g1-mcta-experiment-plan-r3-20260904.json"
        self.assertIn(plan_name, mainline)
        self.assertIn(plan_name, readme)
        self.assertIn("Interpretation Flip Matrix", mainline)
        self.assertIn("Interpretation Flip Matrix", readme)
        self.assertIn("Interpretation Flip Matrix", arch)
        self.assertIn("Interpretation Flip Matrix", latex)


if __name__ == "__main__":
    unittest.main()
