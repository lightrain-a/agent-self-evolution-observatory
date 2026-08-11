from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .emerging_niche import COMPONENTS, score_emerging_niche, write_emerging_niche_policy


class EmergingNicheTest(unittest.TestCase):
    def test_weights_sum_to_one(self) -> None:
        self.assertAlmostEqual(sum(float(row["weight"]) for row in COMPONENTS.values()), 1.0)

    def test_high_evidence_scores_priority(self) -> None:
        result = score_emerging_niche({key: 5 for key in COMPONENTS}, evidence_fresh=True)
        self.assertEqual(result["score"], 100.0)
        self.assertEqual(result["band"], "priority")
        self.assertTrue(result["priority_eligible"])

    def test_stale_or_missing_evidence_never_defaults_high(self) -> None:
        stale = score_emerging_niche({key: 5 for key in COMPONENTS}, evidence_fresh=False)
        missing = score_emerging_niche({"exact_problem_sparsity": 5}, evidence_fresh=True)
        self.assertIsNone(stale["score"])
        self.assertIsNone(missing["score"])
        self.assertEqual(stale["status"], "pending")
        self.assertEqual(missing["status"], "pending")

    def test_dead_niche_and_low_importance_are_capped(self) -> None:
        dead = {key: 5 for key in COMPONENTS}; dead["emerging_signal"] = 1
        trivial = {key: 5 for key in COMPONENTS}; trivial["importance_floor"] = 2
        self.assertLessEqual(score_emerging_niche(dead, evidence_fresh=True)["score"], 64)
        self.assertLessEqual(score_emerging_niche(trivial, evidence_fresh=True)["score"], 64)

    def test_authoritative_stop_blocks_priority_without_rewriting_score(self) -> None:
        result = score_emerging_niche({key: 5 for key in COMPONENTS}, evidence_fresh=True,
                                      authoritative_blocks={"experiment_stop": True})
        self.assertEqual(result["score"], 100.0)
        self.assertFalse(result["priority_eligible"])
        self.assertIn("experiment_stop", result["authoritative_blocks"])

    def test_policy_artifacts_are_written(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); json_path = root / "policy.json"; js_path = root / "policy.js"
            write_emerging_niche_policy(json_path, js_path)
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["short_name"], "ENS")
            self.assertIn("experiment_stop", payload["hard_policy"]["never_overrides"])
            self.assertIn("window.EMERGING_NICHE_POLICY", js_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
