from __future__ import annotations

import json
import unittest
from pathlib import Path

from .asset_first_stri_skillsbench_support_qualification_20260824 import DEFAULT_JSON, DEFAULT_REPO, build


class SkillsBenchSupportQualificationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.x = build() if DEFAULT_REPO.exists() else json.loads(Path(DEFAULT_JSON).read_text(encoding="utf-8"))

    def test_inventory(self) -> None:
        s = self.x["summary"]
        self.assertEqual(s["tasks"], 87)
        self.assertEqual(s["required_skills_empty_tasks"], 75)
        self.assertEqual(s["task_local_skills_empty_tasks"], 0)
        self.assertEqual(s["required_vs_task_local_mismatch_tasks"], 79)
        self.assertEqual(s["task_local_skill_files"], 232)
        self.assertEqual(s["unique_task_local_skill_names"], 195)

    def test_fail_closed_as_exact_support(self) -> None:
        self.assertEqual(self.x["decision"], "STOP_AS_EXACT_SUPPORT_SUBSTRATE")
        self.assertIn("invent negative support labels", self.x["reason"])
        self.assertIn("task-local availability", self.x["reopen_condition"])

    def test_zero_execution_authority(self) -> None:
        self.assertEqual(self.x["new_model_calls"], 0)
        self.assertEqual(self.x["new_gpu_runs"], 0)
        self.assertFalse(self.x["claim_expansion"])
        self.assertFalse(self.x["scientific_authority"])


if __name__ == "__main__":
    unittest.main()
