from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STORY = ROOT / "generated" / "agent-safety-g1-skillzip-paper-story-r1-20260904.json"
MAINLINE = ROOT / "paper_drafts" / "agent-safety-r9-iclr2027" / "MAINLINE_BRIEF.md"
ARCH = ROOT / "paper_drafts" / "agent-safety-r9-iclr2027" / "SKILLZIP_PRECONFIRMATORY_MANUSCRIPT_R1.md"
LATEX = ROOT / "paper_drafts" / "agent-safety-r9-iclr2027" / "main_skillzip_preconfirmatory.tex"
README = ROOT / "paper_drafts" / "agent-safety-r9-iclr2027" / "README.md"


class G1SkillZipPaperStoryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.story = json.loads(STORY.read_text(encoding="utf-8"))

    def test_submission_is_explicitly_held(self) -> None:
        self.assertEqual(self.story["status"], "PRECONFIRMATORY_SUBMISSION_HOLD")
        self.assertFalse(self.story["manuscript_state"]["submission_ready"])

    def test_one_primary_scientific_object(self) -> None:
        obj = self.story["active_scientific_object"].lower()
        self.assertIn("benign workflow accumulation", obj)
        self.assertIn("refusal-to-action", obj)
        self.assertIn("same-schedule", obj)
        self.assertIn("evaluator disagreement by itself", [x.lower() for x in self.story["not_primary_objects"]])

    def test_R1_is_primary_and_endpoint_switching_is_forbidden(self) -> None:
        endpoints = self.story["behavioral_endpoints"]
        self.assertEqual(endpoints["primary"], "R1")
        self.assertEqual(endpoints["secondary_decomposition"], ["R0", "R2", "R3"])
        self.assertTrue(endpoints["post_outcome_endpoint_switching_forbidden"])

    def test_capability_gate_is_strict_ten_of_ten(self) -> None:
        gate = self.story["capability_gate"]
        self.assertEqual(gate["backbone"], "qwen3.5-397b-a17b")
        self.assertEqual(gate["primary_max_steps"], 10)
        self.assertEqual(gate["required_success"], "10/10")
        self.assertTrue(gate["failure_is_not_safety_evidence"])

    def test_historical_evidence_is_discovery_only(self) -> None:
        old = self.story["historical_discovery"]
        self.assertEqual(old["authority"], "DISCOVERY_ONLY")
        self.assertEqual(old["four_step_truncation_count"], 103)
        self.assertEqual(old["normal_termination_count"], 0)
        self.assertEqual(old["listener_confirmed_external_effect_count"], 0)
        self.assertTrue(old["confirmatory_mechanism_claim_forbidden"])

    def test_paper_identity_rule_is_prospective_and_terminal(self) -> None:
        rule = self.story["prospective_paper_identity_rule"]
        self.assertEqual(rule["capability_fail"], "NO_SAFETY_RUN_SUBSTRATE_DIAGNOSIS_ONLY")
        self.assertEqual(rule["capability_pass_and_R1_effect_with_behavioral_coherence"], "KEEP_NARROW_SELF_EVOLUTION_G1")
        self.assertEqual(rule["capability_pass_no_R1_effect_but_evaluator_reversal_persists_on_complete_objectively_anchored_trajectories"], "PIVOT_TO_EVALUATION_PAPER")
        self.assertEqual(rule["capability_pass_no_R1_effect_and_evaluator_reversal_disappears"], "STOP_OR_MERGE_G1")
        self.assertTrue(rule["post_outcome_rule_change_forbidden"])

    def test_claim_ladder_has_no_premature_positive_claim(self) -> None:
        ladder = {row["level"]: row for row in self.story["claim_ladder"]}
        self.assertEqual(ladder[0]["status"], "SUPPORTED")
        for level in (1, 2, 3, 4):
            self.assertEqual(ladder[level]["status"], "PENDING")
        self.assertEqual(ladder[5]["status"], "UNAUTHORIZED")

    def test_workspace_docs_point_to_active_story(self) -> None:
        self.assertIn("PRECONFIRMATORY / SUBMISSION HOLD", MAINLINE.read_text(encoding="utf-8"))
        self.assertIn("Abstract skeleton", ARCH.read_text(encoding="utf-8"))
        self.assertIn("refusal-to-action boundary", LATEX.read_text(encoding="utf-8").lower())
        readme = README.read_text(encoding="utf-8")
        self.assertIn("not the active story source of truth", readme)
        self.assertIn("10/10 PASS", readme)


if __name__ == "__main__":
    unittest.main()
