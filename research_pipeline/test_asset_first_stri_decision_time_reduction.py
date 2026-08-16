from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from .asset_first_stri_decision_time_reduction import analyze


class DecisionTimeReductionTest(unittest.TestCase):
    def test_reduces_precontext_single_package_controller_to_global_weights(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "question_generate").mkdir()
            (root / "skill_library").mkdir()
            (root / "question_generate" / "question_generate.py").write_text(
                "skill = sample_skill(skills)\nchat = build_questioner_messages(expanded_skill)\n", encoding="utf-8"
            )
            (root / "skill_library" / "library.py").write_text(
                "weight *= quality_multiplier(skill)\nweight *= exploration_multiplier(skill)\nweights.append(weight)\n"
                "return generator.choices(list(skills), weights=weights, k=1)\n", encoding="utf-8"
            )
            witness = root / "witness.json"
            witness.write_text(json.dumps({"witness_count": 2, "tight_global_package_exposure_ratio_lower_bound": 2.0}), encoding="utf-8")
            with patch("research_pipeline.asset_first_stri_decision_time_reduction.subprocess.check_output", return_value="a" * 40):
                result = analyze(author_repo=root, structural_witness=witness)
        self.assertEqual(result["strongest_reduction_verdict"], "PRE_CONTEXT_SINGLE_PACKAGE_CONTROLLER_CLASS_REDUCED_TO_GLOBAL_WEIGHTS")
        self.assertIn(">= 2.0", result["theorem"]["consequence"])
        self.assertFalse(result["p0_authorized"])

    def test_rejects_posttask_call_order(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "question_generate").mkdir()
            (root / "skill_library").mkdir()
            (root / "question_generate" / "question_generate.py").write_text(
                "chat = build_questioner_messages(expanded_skill)\nskill = sample_skill(skills)\n", encoding="utf-8"
            )
            (root / "skill_library" / "library.py").write_text(
                "weight *= quality_multiplier(skill)\nweight *= exploration_multiplier(skill)\nweights.append(weight)\n"
                "return generator.choices(list(skills), weights=weights, k=1)\n", encoding="utf-8"
            )
            witness = root / "witness.json"
            witness.write_text(json.dumps({"witness_count": 1, "tight_global_package_exposure_ratio_lower_bound": 2.0}), encoding="utf-8")
            with patch("research_pipeline.asset_first_stri_decision_time_reduction.subprocess.check_output", return_value="a" * 40):
                with self.assertRaises(RuntimeError):
                    analyze(author_repo=root, structural_witness=witness)


if __name__ == "__main__":
    unittest.main()
