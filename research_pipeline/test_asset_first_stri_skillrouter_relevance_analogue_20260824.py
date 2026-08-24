from __future__ import annotations

import json
import unittest
from pathlib import Path
from .asset_first_stri_skillrouter_relevance_analogue_20260824 import DEFAULT_JSON, DEFAULT_REPO, build


class SkillRouterRelevanceAnalogueTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.x = build() if DEFAULT_REPO.exists() else json.loads(Path(DEFAULT_JSON).read_text(encoding="utf-8"))

    def test_release_inventory(self) -> None:
        self.assertTrue(all(self.x["preflight"].values()))
        self.assertEqual(self.x["task_inventory"]["released_rows"], 87)
        self.assertEqual(self.x["headline"]["core_rows"], 75)
        self.assertEqual((self.x["headline"]["core_single"], self.x["headline"]["core_multi"]), (24, 51))

    def test_gold_graph_is_external_equalizable_negative(self) -> None:
        self.assertAlmostEqual(self.x["headline"]["core_uniform_ratio"], 7.0, places=8)
        self.assertAlmostEqual(self.x["headline"]["core_R_star"], 1.0, places=8)
        self.assertAlmostEqual(self.x["headline"]["all_gt_uniform_ratio"], 7.0, places=8)
        self.assertAlmostEqual(self.x["headline"]["all_gt_R_star"], 1.0, places=8)

    def test_graded_relevance_stress_is_still_equalizable(self) -> None:
        self.assertAlmostEqual(self.x["headline"]["graded_ge_1_uniform_ratio"], 21.0, places=8)
        self.assertAlmostEqual(self.x["headline"]["graded_ge_1_R_star"], 1.0, places=8)

    def test_scope_is_relevance_not_support(self) -> None:
        self.assertIn("retrieval acceptability", self.x["scientific_boundary"])
        self.assertEqual(self.x["new_model_calls"], 0)
        self.assertEqual(self.x["new_gpu_runs"], 0)
        self.assertFalse(self.x["claim_expansion"])


if __name__ == "__main__": unittest.main()
