from __future__ import annotations

import json
import unittest
from pathlib import Path
from .asset_first_stri_skillrl_budget_baselines_20260824 import DEFAULT_CONTRACT, DEFAULT_JSON, build


class SkillRLBudgetBaselinesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        contract = json.loads(Path(DEFAULT_CONTRACT).read_text(encoding="utf-8"))
        repo = Path((contract.get("author_asset") or {}).get("repo") or "")
        cls.x = build() if repo.exists() else json.loads(Path(DEFAULT_JSON).read_text(encoding="utf-8"))
        cls.by = {row["top_k"]: row for row in cls.x["budgets"]}

    def test_frozen_inventory_and_preflight(self) -> None:
        self.assertEqual(self.x["tasks"], 223)
        self.assertEqual(self.x["general_skill_targets"], 12)
        self.assertTrue(all(self.x["preflight"].values()))

    def test_top_k6_reproduces_existing_phenotype(self) -> None:
        c = self.by[6]["controls"]["official_dynamic_priority"]
        self.assertEqual(c["targets_with_semantic_set_change"], 11)
        self.assertEqual(c["targets_with_unique_count_reduction"], 5)
        self.assertGreater(c["prompt_changed_fraction"], 0.9)

    def test_non_dynamic_clone_and_quotient_controls(self) -> None:
        for k in self.x["top_k_values"]:
            self.assertEqual(self.by[k]["controls"]["non_dynamic_clone_placebo"]["semantic_set_changed"], 0)
            self.assertEqual(self.by[k]["controls"]["exact_semantic_quotient"]["semantic_set_changed"], 0)

    def test_budget_boundary(self) -> None:
        for k in (1,2,3,4,6,8,12):
            self.assertEqual(self.by[k]["controls"]["official_dynamic_priority"]["targets_with_semantic_set_change"], 11)
            self.assertEqual(self.by[k]["controls"]["official_dynamic_priority"]["targets_with_unique_count_reduction"], k-1)
        self.assertEqual(self.by[13]["controls"]["official_dynamic_priority"]["semantic_set_changed"], 0)
        self.assertEqual(self.by[12]["controls"]["capacity_plus_one"]["semantic_set_changed"], 0)

    def test_zero_new_execution_authority(self) -> None:
        self.assertEqual(self.x["new_model_calls"], 0)
        self.assertEqual(self.x["new_gpu_runs"], 0)
        self.assertFalse(self.x["claim_expansion"])


if __name__ == "__main__":
    unittest.main()
