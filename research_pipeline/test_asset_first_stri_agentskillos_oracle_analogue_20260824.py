from __future__ import annotations

import unittest

from .asset_first_stri_agentskillos_oracle_analogue_20260824 import build


class AgentSkillOSOracleAnalogueTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build()

    def test_preflight_and_boundary(self) -> None:
        self.assertTrue(all(self.payload["preflight"].values()))
        self.assertEqual(self.payload["decision"], "QUALIFY_AUTHOR_ORACLE_SET_ANALOGUE_ONLY")
        self.assertIn("not a complete executable semantic-support relation", self.payload["scientific_boundary"])
        self.assertFalse(self.payload["claim_expansion"])
        self.assertEqual(self.payload["new_model_calls"], 0)
        self.assertEqual(self.payload["new_gpu_runs"], 0)

    def test_full_graph(self) -> None:
        head = self.payload["headline"]
        self.assertEqual((head["tasks"], head["categories"], head["unique_oracle_skills"]), (30, 5, 19))
        self.assertEqual(head["multi_skill_tasks"], 20)
        self.assertAlmostEqual(head["full_uniform_exposure_ratio"], 4.0)
        self.assertAlmostEqual(head["full_oracle_set_R_star_analogue"], 2.5)

    def test_category_boundary(self) -> None:
        rows = {row["regime"]: row for row in self.payload["regimes"]}
        self.assertAlmostEqual(rows["data_computation"]["oracle_set_R_star_analogue"], 2.0)
        self.assertAlmostEqual(rows["document_creation"]["oracle_set_R_star_analogue"], 2.0)
        for name in ("motion_video", "visual_creation", "web_interaction"):
            self.assertAlmostEqual(rows[name]["oracle_set_R_star_analogue"], 1.0)
        self.assertEqual(set(self.payload["headline"]["residual_categories"]), {"data_computation", "document_creation"})
        self.assertEqual(set(self.payload["headline"]["equalizable_categories"]), {"motion_video", "visual_creation", "web_interaction"})


if __name__ == "__main__":
    unittest.main()
