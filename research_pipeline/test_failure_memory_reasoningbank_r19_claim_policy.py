import unittest

from research_pipeline.failure_memory_reasoningbank_r19_claim_policy import build


class TestR19ClaimPolicy(unittest.TestCase):
    def test_four_branches_are_frozen(self):
        d = build()
        self.assertEqual(set(d["outcome_branches"]), {
            "A_SUPPORT_GATE_PASS",
            "B_FULL_EXECUTION_GATE_NOT_PASS",
            "C_POST_EXPOSURE_SUPPORT_FAILURE",
            "D_PRE_EXPOSURE_SUPPORT_FAILURE",
        })

    def test_inconclusive_never_becomes_no_effect(self):
        d = build()
        b = d["outcome_branches"]["B_FULL_EXECUTION_GATE_NOT_PASS"]
        self.assertEqual(b["scientific_status"], "INCONCLUSIVE_NO_NO_EFFECT_AUTHORITY")
        self.assertIn("no effect", b["forbidden"])
        self.assertIsNone(d["primary_gate"]["equivalence_margin"])
        self.assertFalse(d["primary_gate"]["no_effect_claim_authorized"])

    def test_r18_cannot_drive_r19_story(self):
        d = build()
        self.assertTrue(d["anti_story_shopping"]["R18_artifacts_cannot_select_R19_story"])
        self.assertTrue(d["anti_story_shopping"]["outcome_branch_selected_by_rules_not_author"])
        self.assertFalse(d["authority"]["experiment"])


if __name__ == "__main__":
    unittest.main()
